"""Export processed tables + stage reports to static JSON for the web frontend (web/public/data)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from pharmakon import http
from pharmakon.common import GOLD, PROCESSED, ROOT, read_stage_report
from pharmakon.names.normalize import match_key, transliterate

OUT = ROOT / "web" / "public" / "data"
NONE = "__unidentified__"


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list | tuple | np.ndarray):
        return [_clean(v) for v in o]
    if isinstance(o, float | np.floating):
        return None if np.isnan(o) else round(float(o), 4)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if o is pd.NA or o is pd.NaT:
        return None
    return o


def _dump(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_clean(obj), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def safe(cid: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", cid.replace("cl:", "").lower()).strip("-")


def plant_images(qids: list[str]) -> dict[str, dict]:
    """Wikidata P18 image per taxon item → Wikimedia Commons thumbnail URL + file page (for attribution)."""
    out = {}
    for i in range(0, len(qids), 80):
        vals = " ".join(f"wd:{q}" for q in qids[i : i + 80])
        for b in http.sparql(f"SELECT ?t ?img WHERE {{ VALUES ?t {{ {vals} }} ?t wdt:P18 ?img }}"):
            q = b["t"].rsplit("/", 1)[-1]
            fname = b["img"].rsplit("/", 1)[-1]
            out.setdefault(q, {"thumb": f"https://commons.wikimedia.org/wiki/Special:FilePath/{fname}?width=640",
                               "page": f"https://commons.wikimedia.org/wiki/File:{fname}"})
    return out


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    passages = pd.read_parquet(PROCESSED / "passages.parquet")
    claims = pd.read_parquet(PROCESSED / "claims_dmm.parquet")
    post = pd.read_parquet(PROCESSED / "id_posterior.parquet")
    expl = pd.read_parquet(PROCESSED / "id_explanations.parquet")
    pers = pd.read_parquet(PROCESSED / "persistence.parquet")
    modern = pd.read_parquet(PROCESSED / "modern_studies.parquet")
    taxa = pd.read_parquet(PROCESSED / "taxa.parquet")
    cand = pd.read_parquet(PROCESSED / "id_candidates.parquet")[["taxon_key", "species_key"]].drop_duplicates("taxon_key")
    gal_p = pd.read_parquet(PROCESSED / "passages_galen.parquet")
    gal_c = pd.read_parquet(PROCESSED / "claims_galen.parquet")
    gal_x = pd.read_parquet(PROCESSED / "galen_crosswalk.parquet")
    leads = pd.read_parquet(PROCESSED / "leads.parquet")
    paths = pd.read_parquet(PROCESSED / "evidence_paths.parquet")
    morph_p = PROCESSED / "id_morphology.parquet"
    morph = pd.read_parquet(morph_p) if morph_p.exists() else pd.DataFrame(columns=["unit_id", "taxon_key", "matches"])
    mmap = {(r.unit_id, r.taxon_key): list(r.matches) for r in morph.itertuples()}

    tk2qid = cand.merge(taxa[["species_key", "wikidata", "iucn_status", "vernacular_el"]], on="species_key", how="left").set_index("taxon_key")
    pc = post[post["unit_kind"] == "cluster"]
    want = set(pc[(pc["taxon_key"] != NONE) & (pc["p"] >= 0.15)]["taxon_key"]) | set(leads["taxon_key"])
    qids = sorted({tk2qid.loc[t, "wikidata"] for t in want if t in tk2qid.index and isinstance(tk2qid.loc[t, "wikidata"], str)})
    imgs = plant_images(qids)
    def img(tk):
        q = tk2qid.loc[tk, "wikidata"] if tk in tk2qid.index else None
        return imgs.get(q) if isinstance(q, str) else None

    # ---- names index + per-name detail ---------------------------------------------------
    by_post = {u: d.sort_values("p", ascending=False) for u, d in pc.groupby("unit_id")}
    n_claims = claims[claims["status"] == "ok"].groupby("chapter_id").size()
    index = []
    gx = gal_x.merge(gal_p.groupby("entry_id").agg(heading=("entry_heading", "first"), text=("text_grc", " ".join), cts=("cts_urn", "first")).reset_index(), on="entry_id")
    for c in clusters.itertuples():
        pp = by_post.get(c.cluster_id, pd.DataFrame())
        top = pp.iloc[0] if len(pp) else None
        index.append({"id": safe(c.cluster_id), "lemma": c.lemma, "translit": transliterate(c.lemma), "key": match_key(c.lemma),
                      "chapter": c.chapter_id, "top": (top["accepted_name"] if top is not None and top["taxon_key"] != NONE else None),
                      "p": float(top["p"]) if top is not None else None, "claims": int(n_claims.get(c.chapter_id, 0)), "gold": bool(len(c.gold_ids)),
                      "species": [x for x in pp["accepted_name"].dropna().tolist()] if len(pp) else []})
        ch_pass = passages[passages["chapter_id"] == c.chapter_id]
        ch_claims = claims[claims["chapter_id"] == c.chapter_id]
        ex = expl[expl["unit_id"] == c.cluster_id]
        wcols = [k for k in ex.columns if k.startswith("w_")]
        cand_rows = []
        for r in pp.itertuples():
            e = ex[ex["taxon_key"] == r.taxon_key]
            cand_rows.append({"taxon": r.taxon_key, "name": r.accepted_name, "family": r.family, "p": r.p, "lo": r.p_lo, "hi": r.p_hi,
                              "image": img(r.taxon_key) if r.taxon_key != NONE else None,
                              "iucn": tk2qid.loc[r.taxon_key, "iucn_status"] if r.taxon_key in tk2qid.index else None,
                              "vernacular_el": list(tk2qid.loc[r.taxon_key, "vernacular_el"]) if r.taxon_key in tk2qid.index and isinstance(tk2qid.loc[r.taxon_key, "vernacular_el"], list | np.ndarray) else [],
                              "sources": list(e["candidate_sources"].iloc[0]) if len(e) else [],
                              "contrib": {k[2:]: float(e[k].iloc[0]) for k in wcols} if len(e) else {},
                              "morph": mmap.get((c.cluster_id, r.taxon_key), [])})
        g = gx[gx["dmm_chapter_id"] == c.chapter_id]
        galen = [{"heading": r.heading, "text": r.text[:900], "cts": r.cts, "copy": r.copy_containment,
                  "spans": gal_c[gal_c["chapter_id"] == r.entry_id]["evidence_span_grc"].tolist()} for r in g.drop_duplicates("entry_id").itertuples()]
        tks = set(pp["taxon_key"]) if len(pp) else set()
        mm = modern[modern["taxon_key"].isin(tks)]
        detail = {
            "id": safe(c.cluster_id), "lemma": c.lemma, "chapter": c.chapter_id, "translit": transliterate(c.lemma),
            "synonyms": [v["variant"] for v in c.variants if v["variant_source"] == "synonym_list"][:20],
            "jc": sorted({x["jc_name_grc"] for x in c.jc_crosswalk}),
            "passages": [{"id": p.passage_id, "cts": p.cts_urn, "text": p.text_grc,
                          "spans": ch_claims[ch_claims["passage_id"] == p.passage_id]["evidence_span_grc"].tolist()} for p in ch_pass.itertuples()],
            "claims": ch_claims[["condition_text_grc", "condition_en", "plant_part", "route", "use_group", "status"]].assign(
                llm=ch_claims["extractor_version"].astype(str).str.contains("llm") if "extractor_version" in ch_claims else False).to_dict("records"),
            "candidates": cand_rows,
            "model": pp["method"].iloc[0] if len(pp) else None,
            "persistence": pers[pers["cluster_id"] == c.cluster_id][["use_group", "present_dmm", "present_galen", "present_jc", "expected_modern", "pattern"]].to_dict("records"),
            "galen": galen,
            "modern": mm[["study", "accepted_name", "local_name", "plant_part", "ailment_text"]].head(12).to_dict("records"),
        }
        _dump(detail, OUT / "names" / f"{safe(c.cluster_id)}.json")
    _dump(index, OUT / "names.json")

    # ---- leads + evidence paths ------------------------------------------------------------
    pid = {(r.taxon_key, r.mesh_id) for r in paths.itertuples()}
    lrows = []
    for r in leads.itertuples():
        lrows.append({"rank": r.rank_weighted, "rank_top1": r.rank_top1_only, "species": r.accepted_name, "family": r.family, "condition": r.mesh_label,
                      "p": r.p_species, "score": r.score_weighted, "path": r.path_strength, "iucn": r.conservation_status,
                      "toxic": bool(r.toxicity_flag), "tox_url": r.toxicity_citation, "names": [safe(x) for x in r.clusters],
                      "jc": bool(r.h_present_jc), "modern": bool(r.h_modern_attested), "query": r.query_string,
                      "image": img(r.taxon_key), "has_paths": (r.taxon_key, r.mesh_id) in pid, "taxon": r.taxon_key, "mesh": r.mesh_id})
    _dump(lrows, OUT / "leads.json")
    sp = paths.merge(leads[["taxon_key", "accepted_name"]].drop_duplicates("taxon_key"), on="taxon_key", how="left")
    sp = sp.sort_values("path_strength", ascending=False).groupby(["taxon_key", "mesh_id"]).head(12)
    _dump(sp[["taxon_key", "accepted_name", "mesh_id", "inchikey", "molecule_chembl_id", "target_chembl_id", "disease_name", "ct_tier", "td_tier",
              "pchembl", "ot_score", "compound_ref_year", "activity_doc_year", "path_strength"]].to_dict("records"), OUT / "paths.json")

    # ---- results ----------------------------------------------------------------------------
    st = {k: read_stage_report(k) for k in ("ingest-texts", "extract-claims", "map-conditions", "gold", "identify", "link-chemistry", "ingest-galen",
                                             "persistence", "evidence-labels", "forecast", "leads", "build-kg")}
    hits = pd.read_parquet(PROCESSED / "forecast_hits.parquet")
    st["forecast_hits"] = hits[["cutoff", "accepted_name", "mesh_label", "score_histpop", "label", "first_support_year"]].to_dict("records")
    d = pers[pers["present_dmm"]]
    def lab(v, linked):
        return "no record" if not linked else ("attested" if v else "absent")
    flows = d.assign(galen=[lab(v, ln) for v, ln in zip(d["present_galen"], d["galen_linked"], strict=True)],
                     jc=[lab(v, ln) for v, ln in zip(d["present_jc"], d["jc_linked"], strict=True)],
                     modern=np.where(d["expected_modern"] >= 0.5, "attested", "absent"))
    st["flows"] = flows.groupby(["use_group", "galen", "jc", "modern"]).size().rename("n").reset_index().to_dict("records")
    gold = pd.read_parquet(GOLD / "lardos_gold.parquet")
    st["gold_counts"] = {"names": int(gold["gold_id"].nunique()), "candidates": int(len(gold))}
    _dump(st, OUT / "results.json")
    return {"names": len(index), "leads": len(lrows), "images": len(imgs), "out": str(OUT)}


if __name__ == "__main__":
    print(run())
