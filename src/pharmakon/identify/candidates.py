"""Candidate generation (union of sources) followed by GBIF verification (spec/05 Stage 5.1)."""

from __future__ import annotations

import pandas as pd

from pharmakon.common import GOLD, INTERIM, PROCESSED, now_iso
from pharmakon.link.taxonomy import verify_many
from pharmakon.names.normalize import match_key, strip_accents


def _lsj_index() -> dict[str, list[tuple[str, bool]]]:
    lsj = pd.read_parquet(INTERIM / "lsj_plants.parquet")
    idx: dict[str, list[tuple[str, bool]]] = {}
    for r in lsj.itertuples():
        for b, h in zip(r.binomials, r.hedged, strict=False):
            idx.setdefault(r.lemma_key, []).append((str(b), bool(h)))
    return idx


def lsj_lookup(idx: dict, greek: str) -> tuple[list[tuple[str, bool]], str]:
    """LSJ binomials for a Greek name: exact lemma, else first word (flagged)."""
    k = strip_accents(greek).replace("ς", "σ")
    k = " ".join(match_key(k).split())
    if k in idx:
        return idx[k], "exact"
    first = k.split()[0] if k.split() else ""
    if first in idx:
        return idx[first], "first_word"
    return [], "none"


def build_units() -> pd.DataFrame:
    """Identification units: every gold name, plus every pilot cluster.

    Columns: unit_id, unit_kind (gold|cluster), cluster_id, names_grc (list), jc_lemma_tag, group."""
    gold = pd.read_parquet(GOLD / "lardos_gold.parquet")
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    ch2cl = dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=False))
    rows = []
    for g in gold.drop_duplicates("gold_id").to_dict("records"):
        names = [g["dmm_name_grc"].split(":")[0].split(",")[0].strip(), g["jc_name_grc"]]
        rows.append({
            "unit_id": g["gold_id"], "unit_kind": "gold", "cluster_id": ch2cl.get(g["dmm_chapter_id"]),
            "names_grc": [n for n in dict.fromkeys(names) if isinstance(n, str) and n],
            "jc_lemma_tag": g["jc_lemma_tag"], "jc_id": g["jc_id"], "group": g["jc_lemma_tag"],
        })
    for c in clusters.to_dict("records"):
        rows.append({
            "unit_id": c["cluster_id"], "unit_kind": "cluster", "cluster_id": c["cluster_id"],
            "names_grc": [c["lemma"]], "jc_lemma_tag": None, "jc_id": None, "group": c["cluster_id"],
            "gold_ids": list(c["gold_ids"]),
        })
    return pd.DataFrame(rows)


def build_candidates(units: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (candidates per unit, GBIF verification log). Unverifiable candidates are dropped and logged."""
    gold = pd.read_parquet(GOLD / "lardos_gold.parquet")
    reports = pd.read_parquet(GOLD / "lardos_reports.parquet")
    idx = _lsj_index()
    raw = []
    lardos_by_unit = gold.groupby("gold_id")["candidate_name"].apply(list).to_dict()
    for u in units.to_dict("records"):
        lardos: list[str] = []
        if u["unit_kind"] == "gold":
            lardos = lardos_by_unit.get(u["unit_id"], [])
        else:
            for gid in u.get("gold_ids") or []:
                lardos += lardos_by_unit.get(gid, [])
        for n in lardos:
            raw.append({"unit_id": u["unit_id"], "name": n, "src": "lardos", "hedged": False, "lsj_match": None})
        seen_lsj = set()
        for g in u["names_grc"]:
            hits, how = lsj_lookup(idx, g)
            for b, hedged in hits:
                if b in seen_lsj:
                    continue
                seen_lsj.add(b)
                raw.append({"unit_id": u["unit_id"], "name": b, "src": "lsj", "hedged": hedged, "lsj_match": how})
    raw = pd.DataFrame(raw)
    ver = verify_many(raw["name"].tolist())
    ok = ver[ver["verified"]].set_index("input_name")
    raw = raw[raw["name"].isin(ok.index)].copy()
    for col in ["taxon_key", "accepted_name", "family", "genus", "taxon_rank", "species_key", "match_type", "confidence"]:
        raw[col] = raw["name"].map(ok[col])
    # Literature reports per (jc_id, candidate) from Lardos Data file 5.
    rep = reports.copy()
    rep["candidate_key"] = rep["candidate_key"].astype(str)
    unit_jc = units.set_index("unit_id")["jc_id"].to_dict()
    raw["jc_id"] = raw["unit_id"].map(unit_jc)
    from pharmakon.identify.gold import name_key

    raw["candidate_key"] = raw["name"].map(name_key)
    agg = []
    for (uid, tk), grp in raw.groupby(["unit_id", "taxon_key"]):
        jc = grp["jc_id"].iloc[0]
        keys = set(grp["candidate_key"])
        r = rep[(rep["jc_id"] == jc) & rep["candidate_key"].isin(keys)] if isinstance(jc, str) else rep.head(0)
        lsj = grp[grp["src"] == "lsj"]
        agg.append({
            "unit_id": uid, "taxon_key": tk, "accepted_name": grp["accepted_name"].iloc[0],
            "family": grp["family"].iloc[0], "genus": grp["genus"].iloc[0], "taxon_rank": grp["taxon_rank"].iloc[0],
            "species_key": grp["species_key"].iloc[0], "input_names": sorted(set(grp["name"])),
            "candidate_sources": sorted(set(grp["src"])),
            "in_lardos": bool((grp["src"] == "lardos").any()),
            "lsj_asserts": bool((~lsj["hedged"]).any()) if len(lsj) else False,
            "lsj_hedged_only": bool(len(lsj) and lsj["hedged"].all()),
            "lit_refs_dmm_texts": int(r[r["study_type"] == "DMMBotanicalTexts"]["reference"].nunique()),
            "lit_refs_ethnobot": int(r[r["study_type"] == "EthnobotStudies"]["reference"].nunique()),
            "lit_ref_years": sorted({int(y) for y in r["ref_year"].dropna()}),
            "candidate_keys": sorted(keys),
        })
    cand = pd.DataFrame(agg)
    cand["source_id"] = "gbif_backbone"
    cand["retrieved_at"] = now_iso()
    cand["method"] = "candidate_union_v1+gbif_verify"
    return cand, ver
