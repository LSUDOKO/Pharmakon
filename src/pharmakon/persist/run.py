"""Stages 7–8 — Byzantine (JC) and modern nodes, then persistence of (name, use group) claims.

Persistence is computed on the Lardos et al. medicinal use groups (config/use_groups.yaml), which
both the Dioscorides ICPC-2 claims and the JC / modern records map to. Species-level matching uses
the identification posterior:  E[modern] = Σ_s P(s|n) · 1[s or its genus attested with that group].
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from pharmakon.common import (
    GOLD,
    PROCESSED,
    get_logger,
    now_iso,
    pilot,
    write_stage_report,
    write_table,
)
from pharmakon.persist import modern as M

NONE = "__unidentified__"


def modern_records() -> pd.DataFrame:
    """All modern attestations: Lardos ethnobotany/herbal references + Pelion + North Aegean."""
    studies = M.build()
    write_table(studies, PROCESSED / "modern_studies.parquet")
    st = studies[studies["taxon_verified"]].explode("use_groups").dropna(subset=["use_groups"])
    a = pd.DataFrame({"taxon_key": st["taxon_key"], "genus": st["genus"], "use_group": st["use_groups"],
                      "source": st["study"], "year": st["study_year"].astype(int)})
    uses = pd.read_parquet(GOLD / "lardos_uses.parquet")
    mod = uses[uses["node"] == "modern"].copy()
    cand = pd.read_parquet(PROCESSED / "id_candidates.parquet")[["taxon_key", "genus", "candidate_keys"]].explode("candidate_keys")
    k2t = cand.drop_duplicates("candidate_keys").set_index("candidate_keys")
    mod["taxon_key"] = mod["candidate_key"].map(k2t["taxon_key"])
    mod["genus"] = mod["candidate_key"].map(k2t["genus"])
    mod = mod.dropna(subset=["taxon_key"])
    b = pd.DataFrame({"taxon_key": mod["taxon_key"], "genus": mod["genus"], "use_group": mod["use_group"],
                      "source": "lardos:" + mod["reference"].astype(str), "year": mod["ref_year"]})
    out = pd.concat([a, b], ignore_index=True)
    out["source_id"], out["retrieved_at"], out["method"] = "modern_endpoint", now_iso(), "union_v1"
    return out


def jc_records() -> pd.DataFrame:
    """JC (13th c.) use groups per Dioscorides cluster, via the Lardos JC↔DMM crosswalk."""
    uses = pd.read_parquet(GOLD / "lardos_uses.parquet")
    jc = uses[uses["node"] == "jc"]
    gold = pd.read_parquet(GOLD / "lardos_gold.parquet")
    cands = pd.read_parquet(GOLD / "lardos_candidates.parquet")
    name2lemma = {}
    for r in gold.drop_duplicates("gold_id").itertuples():
        name2lemma[str(r.jc_name_translit).lower().strip()] = r.jc_lemma_tag
    for r in cands.drop_duplicates("jc_lemma_tag").itertuples():
        name2lemma.setdefault(str(r.dmm_name_beck).lower().strip(), r.jc_lemma_tag)
    jc = jc.assign(jc_lemma_tag=jc["dmm_name_beck"].str.lower().str.strip().map(name2lemma)).dropna(subset=["jc_lemma_tag"])
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    lemma2cl = gold.dropna(subset=["dmm_chapter_id"]).drop_duplicates(["jc_lemma_tag", "dmm_chapter_id"])
    ch2cl = dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=True))
    lemma2cl = lemma2cl.assign(cluster_id=lemma2cl["dmm_chapter_id"].map(ch2cl)).dropna(subset=["cluster_id"])
    out = jc.merge(lemma2cl[["jc_lemma_tag", "cluster_id"]], on="jc_lemma_tag")
    return out[["cluster_id", "use_group", "jc_lemma_tag", "plant_part"]].drop_duplicates(["cluster_id", "use_group"])


def _expected(post_n: pd.DataFrame, modern_sp: set, modern_gen: set, g: str | None) -> tuple[float, float]:
    """(E[species-or-genus attested], E[species attested]) for use group g (None = any group)."""
    e_any, e_sp = 0.0, 0.0
    for r in post_n.itertuples():
        if r.taxon_key == NONE:
            continue
        sp = (r.taxon_key, g) in modern_sp
        ge = (r.genus, g) in modern_gen
        e_sp += r.p * sp
        e_any += r.p * (sp or ge)
    return e_any, e_sp


def galen_records() -> dict[tuple[str, str], float]:
    """(cluster, use group) attested in Galen books 6–8 → weight (0.5 if the entry copies Dioscorides, else 1)."""
    gp = PROCESSED / "claims_galen.parquet"
    if not gp.exists():
        return {}
    gc = pd.read_parquet(gp)
    gc = gc[gc["status"] == "ok"]
    xw = pd.read_parquet(PROCESSED / "galen_crosswalk.parquet")
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    ch2cl = dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=True))
    m = gc.merge(xw, left_on="chapter_id", right_on="entry_id")
    m["cluster_id"] = m["dmm_chapter_id"].map(ch2cl)
    out: dict[tuple[str, str], float] = {}
    for r in m.dropna(subset=["cluster_id"]).itertuples():
        w = 0.5 if r.copy_containment > COPY_THRESHOLD else 1.0
        out[(r.cluster_id, r.use_group)] = max(out.get((r.cluster_id, r.use_group), 0.0), w)
    return out


COPY_THRESHOLD = 0.15


def persistence_table(claims: pd.DataFrame, post: pd.DataFrame, jc: pd.DataFrame, modern: pd.DataFrame,
                      galen: dict[tuple[str, str], float] | None = None) -> pd.DataFrame:
    galen = galen or {}
    galen_clusters = {c for c, _ in galen}
    modern_sp = set(zip(modern["taxon_key"], modern["use_group"], strict=True)) | {(t, None) for t in modern["taxon_key"]}
    modern_gen = set(zip(modern["genus"], modern["use_group"], strict=True)) | {(gname, None) for gname in modern["genus"]}
    jc_set = set(zip(jc["cluster_id"], jc["use_group"], strict=True))
    jc_linked = set(jc["cluster_id"])
    by_unit = {u: d for u, d in post.groupby("unit_id")}
    dmm = claims.groupby(["cluster_id", "use_group"]).agg(
        n_claims=("claim_id", "size"), example_span=("evidence_span_grc", "first"), example_passage=("passage_id", "first"),
        plant_parts=("plant_part", lambda s: sorted({x for x in s if isinstance(x, str)}))).reset_index()
    rows = []
    groups_all = sorted(set(dmm["use_group"]) | set(modern["use_group"]))
    for cl in sorted(set(dmm["cluster_id"])):
        pn = by_unit.get(cl)
        if pn is None or pn.loc[pn["taxon_key"] != NONE, "p"].sum() == 0:
            continue
        p_id = float(pn.loc[pn["taxon_key"] != NONE, "p"].sum())
        e_plant_modern, _ = _expected(pn, modern_sp, modern_gen, None)
        dm = dmm[dmm["cluster_id"] == cl].set_index("use_group")
        for g in groups_all:
            in_dmm = g in dm.index
            e_mod, e_mod_sp = _expected(pn, modern_sp, modern_gen, g)
            in_jc = (cl, g) in jc_set if cl in jc_linked else None
            in_galen = (cl, g) in galen if cl in galen_clusters else None
            if not in_dmm and e_mod < 0.5:
                continue
            later = [e_mod] + ([float(in_jc)] if in_jc is not None else []) + ([galen.get((cl, g), 0.0)] if in_galen is not None else [])
            if in_dmm and e_mod >= 0.5:
                pat = "persisted"
            elif in_dmm and e_plant_modern >= 0.5:
                pat = "modified"
            elif in_dmm:
                pat = "persisted_to_byzantine_only" if in_jc else ("persisted_to_galen_only" if in_galen else "lost")
            else:
                pat = "novel"
            rows.append({
                "cluster_id": cl, "use_group": g, "present_dmm": in_dmm, "present_galen": in_galen, "galen_linked": cl in galen_clusters,
                "galen_weight": galen.get((cl, g)), "present_jc": in_jc, "jc_linked": cl in jc_linked,
                "expected_modern": round(e_mod, 4), "expected_modern_species_only": round(e_mod_sp, 4),
                "p_identified": round(p_id, 4), "expected_plant_in_modern": round(e_plant_modern, 4),
                "persistence_score": round(float(np.mean(later)), 4) if in_dmm else None,
                "n_texts_attesting": int(in_dmm) + int(bool(in_galen)) + int(bool(in_jc)) + int(e_mod >= 0.5),
                "pattern": pat,
                "n_dmm_claims": int(dm.loc[g, "n_claims"]) if in_dmm else 0,
                "example_span_grc": dm.loc[g, "example_span"] if in_dmm else None,
                "example_passage_id": dm.loc[g, "example_passage"] if in_dmm else None,
                "plant_parts": list(dm.loc[g, "plant_parts"]) if in_dmm else [],
            })
    out = pd.DataFrame(rows)
    out["first_attested_century"] = np.where(out["present_dmm"], 1, np.where(out["present_galen"].fillna(False).astype(bool), 2,
                                             np.where(out["present_jc"].fillna(False).astype(bool), 13, 20)))
    return out


def permutation_null(tab: pd.DataFrame, post: pd.DataFrame, modern: pd.DataFrame, n: int, seed: int) -> dict:
    """Shuffle modern use-group labels across records (taxa fixed): is persistence above chance?

    Denominator: DMM (name, use group) rows whose plant is attested in the modern record (E ≥ 0.5).
    """
    rows = tab[tab["present_dmm"] & (tab["expected_plant_in_modern"] >= 0.5)][["cluster_id", "use_group", "pattern"]]
    observed = float((rows["pattern"] == "persisted").mean())
    pp = post[post["taxon_key"] != NONE]
    cand = {u: list(zip(d["taxon_key"], d["genus"], d["p"], strict=True)) for u, d in pp.groupby("unit_id")}
    taxa = modern["taxon_key"].to_numpy()
    genera = modern["genus"].to_numpy()
    groups = modern["use_group"].to_numpy()
    rng = np.random.default_rng(seed)
    pairs = list(zip(rows["cluster_id"], rows["use_group"], strict=True))
    null = []
    for _ in range(n):
        g = rng.permutation(groups)
        sp = set(zip(taxa, g, strict=True))
        ge = set(zip(genera, g, strict=True))
        hits = 0
        for cl, ug in pairs:
            e = sum(p for t, gn, p in cand.get(cl, []) if (t, ug) in sp or (gn, ug) in ge)
            hits += e >= 0.5
        null.append(hits / max(len(pairs), 1))
    null_a = np.array(null)
    return {"observed_persisted_share": round(observed, 4), "null_mean": round(float(null_a.mean()), 4),
            "null_95pct": round(float(np.percentile(null_a, 95)), 4),
            "p_value": round(float((np.sum(null_a >= observed) + 1) / (n + 1)), 4),
            "n_permutations": n, "n_rows": len(pairs),
            "denominator": "DMM (name, use group) rows whose plant is attested in the modern record (E>=0.5)"}


def run() -> dict:
    log = get_logger("persistence")
    cfg = pilot()
    claims = pd.read_parquet(PROCESSED / "claims_dmm.parquet")
    claims = claims[(claims["status"] == "ok") & (claims["substance_type"] == "plant")]
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    claims = claims.assign(cluster_id=claims["chapter_id"].map(dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=True)))).dropna(subset=["cluster_id"])
    post = pd.read_parquet(PROCESSED / "id_posterior.parquet")
    post = post[post["unit_kind"] == "cluster"]
    modern = modern_records()
    write_table(modern, PROCESSED / "modern_attestations.parquet")
    jc = jc_records()
    galen = galen_records()
    tab = persistence_table(claims, post, jc, modern, galen)
    tab_no_galen = persistence_table(claims, post, jc, modern, {})
    tab["source_id"], tab["retrieved_at"], tab["method"] = "pharmakon_persistence", now_iso(), "expected_attestation_v1"
    write_table(tab, PROCESSED / "persistence.parquet")
    perm = permutation_null(tab, post, modern, n=1000, seed=cfg["seed"])
    d = tab[tab["present_dmm"]]
    by_group = d.groupby("use_group")["pattern"].value_counts().unstack(fill_value=0)
    ex = tab[(tab["pattern"] == "persisted") & (tab["use_group"] == "DE")].sort_values(["persistence_score", "n_dmm_claims"], ascending=False).head(5)
    examples = ex[["cluster_id", "use_group", "persistence_score", "expected_modern", "present_galen", "present_jc", "example_passage_id", "example_span_grc"]].to_dict("records")
    summary = {
        "clusters_with_identified_taxa": int(tab["cluster_id"].nunique()),
        "rows": int(len(tab)),
        "pattern_counts": tab["pattern"].value_counts().to_dict(),
        "pattern_counts_dermatology": tab[tab["use_group"] == "DE"]["pattern"].value_counts().to_dict(),
        "by_use_group": {g: {k: int(v) for k, v in r.items()} for g, r in by_group.iterrows()},
        "jc_linked_clusters": int(tab.loc[tab["jc_linked"], "cluster_id"].nunique()),
        "galen_linked_clusters": int(tab.loc[tab["galen_linked"], "cluster_id"].nunique()),
        "galen_agreement_rate": round(float(d.loc[d["galen_linked"], "present_galen"].astype(bool).mean()), 4) if d["galen_linked"].any() else None,
        "mean_persistence_score_with_galen": round(float(d["persistence_score"].mean()), 4),
        "mean_persistence_score_without_galen": round(float(tab_no_galen.loc[tab_no_galen["present_dmm"], "persistence_score"].mean()), 4),
        "galen_copy_threshold_4gram_containment": COPY_THRESHOLD,
        "jc_agreement_rate": round(float(d.loc[d["jc_linked"], "present_jc"].astype(bool).mean()), 4) if d["jc_linked"].any() else None,
        "modern_records": int(len(modern)),
        "modern_sources": modern["source"].str.split(":").str[0].value_counts().to_dict(),
        "permutation_test": perm,
        "worked_examples": examples,
        "copy_detection": "Galen entries down-weighted to 0.5 when word-4-gram containment in the matched Dioscorides chapter > 0.15; Paul of Aegina not ingested",
    }
    log.info(json.dumps({k: summary[k] for k in ("rows", "pattern_counts", "permutation_test")}, ensure_ascii=False))
    write_stage_report("persistence", summary)
    return summary
