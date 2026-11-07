"""Stages 1–4: ingest texts, extract claims, map conditions, cluster names."""

from __future__ import annotations

import json

import pandas as pd

from pharmakon import llm
from pharmakon.common import (
    GOLD,
    INTERIM,
    PROCESSED,
    RAW,
    add_provenance,
    get_logger,
    load_yaml,
    now_iso,
    pilot,
    write_stage_report,
    write_table,
)
from pharmakon.corpus.first1k import chapters_to_frames, parse_tei
from pharmakon.extract.claims import extract, prefilter_pilot
from pharmakon.extract.lexicon import pilot_stems
from pharmakon.identify import gold
from pharmakon.link.disease import build_condition_map, mesh_details
from pharmakon.names.normalize import match_key

DMM_CTS = "urn:cts:greekLit:tlg0656.tlg001.1st1K-grc1"


def ingest_texts() -> dict:
    log = get_logger("ingest-texts")
    src = RAW / "dmm_wellmann" / "tlg0656.tlg001.1st1K-grc1.xml"
    meta = json.loads((RAW / "dmm_wellmann" / "SOURCE.json").read_text()) if (RAW / "dmm_wellmann" / "SOURCE.json").exists() else {}
    chapters = parse_tei(src)
    passages, chs = chapters_to_frames(chapters, DMM_CTS, work="dmm", century=1)
    ts = meta.get("retrieved_at", now_iso())
    passages = add_provenance(passages, "dmm_wellmann", "first1k_tei_parse_v1", ts)
    chs = add_provenance(chs, "dmm_wellmann", "first1k_tei_parse_v1", ts)
    write_table(passages, INTERIM / "passages.parquet")
    write_table(passages, PROCESSED / "passages.parquet")
    write_table(chs, PROCESSED / "dmm_chapters.parquet")
    per_book = chs.groupby("book").size().to_dict()
    resid = passages["residue_flags"].map(len).gt(0)
    summary = {
        "passages": int(len(passages)),
        "chapters": int(len(chs)),
        "chapters_per_book": {int(k): int(v) for k, v in per_book.items()},
        "books_present": sorted(int(b) for b in per_book),
        "headword_parsed_rate": round(float(chs["headword_grc"].notna().mean()), 4),
        "chapters_with_synonym_lists": int(chs["synonyms"].map(len).gt(0).sum()),
        "synonyms_total": int(chs["synonyms"].map(len).sum()),
        "residual_apparatus_flag_rate": round(float(resid.mean()), 4),
        "residual_flag_counts": pd.Series([f for fl in passages["residue_flags"] for f in fl]).value_counts().to_dict(),
        "duplicate_chapter_numbers_disambiguated": int(chs["chapter"].astype(str).str.contains("dup").sum()),
        "source_commit": meta.get("last_commit_touching_file"),
    }
    log.info(json.dumps(summary, ensure_ascii=False))
    write_stage_report("ingest-texts", summary)
    return summary


def extract_claims(use_llm: bool = False) -> dict:
    log = get_logger("extract-claims")
    if use_llm and not llm.available():
        raise SystemExit("--llm requested but ANTHROPIC_API_KEY is not set")
    passages = pd.read_parquet(PROCESSED / "passages.parquet")
    gold_ch = set(pd.read_parquet(GOLD / "lardos_gold.parquet")["dmm_chapter_id"].dropna()) if (GOLD / "lardos_gold.parquet").exists() else set()
    scope = prefilter_pilot(passages, pilot()["dmm_books_plants"], gold_ch)
    claims, stats = extract(scope, use_llm=use_llm)
    kept = claims[claims.status != "span_mismatch"]
    archived = claims[claims.status == "span_mismatch"]
    write_table(kept, PROCESSED / "claims_dmm.parquet")
    write_table(archived if len(archived) else kept.head(0), INTERIM / "claims_archived.parquet")
    stems = set(pilot_stems())
    pilot_mask = kept["condition_stem"].isin(stems)
    summary = {
        **stats,
        "claims_total": int(len(claims)),
        "claims_kept": int(len(kept)),
        "archived_span_mismatch": int(len(archived)),
        "exact_span_verified_rate_kept": round(float(kept["span_verified"].mean()), 4) if len(kept) else None,
        "status_counts": kept["status"].value_counts().to_dict(),
        "icpc2_counts": kept["icpc2_chapter"].value_counts().to_dict(),
        "pilot_skin_claims": int(pilot_mask.sum()),
        "pilot_skin_chapters": int(kept.loc[pilot_mask, "chapter_id"].nunique()),
        "substance_type_counts": kept["substance_type"].value_counts().to_dict(),
        "plant_part_known_rate": round(float(kept["plant_part"].notna().mean()), 4),
        "route_known_rate": round(float(kept["route"].notna().mean()), 4),
    }
    log.info(json.dumps(summary, ensure_ascii=False))
    write_stage_report("extract-claims", summary)
    # Audit sheet: 50 random kept claims, blinded, for a human auditor (spec/07 §2).
    audit = kept.sample(min(50, len(kept)), random_state=pilot()["seed"])[
        ["claim_id", "passage_id", "substance_name_grc", "plant_part", "route", "condition_text_grc", "condition_en", "evidence_span_grc"]
    ].assign(substance_ok="", part_ok="", condition_ok="", notes="")
    (GOLD / "audits").mkdir(parents=True, exist_ok=True)
    audit.to_csv(GOLD / "audits" / "extraction_audit_50.csv", index=False)
    return summary


def map_conditions() -> dict:
    log = get_logger("map-conditions")
    cmap = build_condition_map()
    write_table(cmap, PROCESSED / "condition_map.parquet")
    claims = pd.read_parquet(PROCESSED / "claims_dmm.parquet")
    m = cmap.set_index("condition_stem")
    claims["mesh_ids"] = claims["condition_stem"].map(lambda s: list(m.loc[s, "mesh_ids"]) if s in m.index else [])
    claims["no_modern_equivalent"] = claims["condition_stem"].map(lambda s: bool(m.loc[s, "no_modern_equivalent"]) if s in m.index else True)
    ug = load_yaml("use_groups.yaml")
    icpc_to_ug = {ic: g for g, v in ug["use_groups"].items() for ic in v["icpc2"]}
    claims["use_group"] = [ug["stem_overrides"].get(s, icpc_to_ug.get(c, "XY")) for s, c in zip(claims["condition_stem"], claims["icpc2_chapter"], strict=False)]
    write_table(claims, PROCESSED / "claims_dmm.parquet")
    all_ids = sorted({i for ids in cmap["mesh_ids"] for i in ids})
    details = mesh_details(all_ids)
    write_table(details, PROCESSED / "mesh_terms.parquet")
    unverified = sorted({u for us in cmap["mesh_unverified"] for u in us})
    audit = cmap[cmap["mesh_ids"].map(len) > 0].explode("mesh_labels")[["condition_stem", "condition_en", "icpc2_chapter", "mesh_labels"]].assign(mapping_ok="", notes="")
    audit.head(50).to_csv(GOLD / "audits" / "condition_mesh_audit_50.csv", index=False)
    summary = {
        "lexicon_conditions": int(len(cmap)),
        "with_verified_mesh": int(cmap["mesh_ids"].map(len).gt(0).sum()),
        "no_modern_equivalent": int(cmap["no_modern_equivalent"].sum()),
        "mesh_labels_failed_verification": unverified,
        "claims_with_verified_mesh_rate": round(float(claims["mesh_ids"].map(len).gt(0).mean()), 4),
        "distinct_mesh_ids": len(all_ids),
        "use_group_counts": claims["use_group"].value_counts().to_dict(),
    }
    log.info(json.dumps(summary, ensure_ascii=False))
    write_stage_report("map-conditions", summary)
    return summary


def build_gold() -> dict:
    """Phase 3 gold set from Lardos et al. (data/gold/lardos_*.parquet)."""
    log = get_logger("gold")
    out = {
        "lardos_gold": gold.parse_final_results(),
        "lardos_candidates": gold.parse_candidates(),
        "lardos_reports": gold.parse_reports(),
        "lardos_oracle": gold.parse_oracle(),
        "lardos_dmm_link": gold.parse_dmm_link(),
        "lardos_uses": gold.parse_uses(),
    }
    gm = gold.gold_chapter_map(out["lardos_gold"], out["lardos_dmm_link"])
    out["lardos_gold"] = out["lardos_gold"].merge(gm, on="gold_id", how="left")
    for name, df in out.items():
        write_table(df, GOLD / f"{name}.parquet")
    g = out["lardos_gold"]
    summary = {
        "gold_names": int(g["gold_id"].nunique()),
        "jc_lemmas": int(g["jc_lemma_tag"].nunique()),
        "candidates": int(len(g)),
        "expert_confidence_counts": g.groupby("gold_id")["expert_confidence"].first().value_counts().to_dict(),
        "expert_unidentified_names": int(g.groupby("gold_id")["expert_unidentified"].first().sum()),
        "gold_names_linked_to_dmm_chapter": int(gm["dmm_chapter_id"].notna().sum()),
        "reports": int(len(out["lardos_reports"])),
        "uses_rows": out["lardos_uses"]["node"].value_counts().to_dict(),
    }
    log.info(json.dumps(summary, ensure_ascii=False))
    write_stage_report("gold", summary)
    return summary


def cluster_names() -> dict:
    """Stage 4: name clusters = Dioscorides chapter headword + flagged synonym-list variants,
    joined to JC names through Lardos Data file 2 (explicit crosswalk)."""
    log = get_logger("cluster-names")
    chs = pd.read_parquet(PROCESSED / "dmm_chapters.parquet")
    gold_df = pd.read_parquet(GOLD / "lardos_gold.parquet")
    gold_ch = gold_df.groupby("dmm_chapter_id")["gold_id"].apply(lambda s: sorted(set(s))).to_dict()
    chs = chs[(chs["book"].isin(pilot()["dmm_books_plants"]) | chs["chapter_id"].isin(gold_ch)) & chs["headword_grc"].notna()]
    link = pd.read_parquet(GOLD / "lardos_dmm_link.parquet")
    rows = []
    for c in chs.to_dict("records"):
        variants = [{"variant": c["headword_grc"], "variant_source": "headword", "work": "dmm"}]
        variants += [{"variant": s, "variant_source": "synonym_list", "work": "dmm"} for s in c["synonyms"]]
        rows.append({"cluster_id": f"cl:{c['chapter_id']}", "chapter_id": c["chapter_id"], "lemma": c["headword_grc"],
                     "lemma_key": match_key(c["headword_grc"]), "variants": variants})
    clusters = pd.DataFrame(rows)
    # Crosswalk to JC names: Lardos explicit chapter link, else accent-insensitive fuzzy headword match ≥ 90.
    link = link[link["dmm_chapter_id"].notna()]
    jc_by_ch: dict[str, list[dict]] = {}
    for r in link.to_dict("records"):
        jc_by_ch.setdefault(r["dmm_chapter_id"], []).append(r)
    crosswalk, gold_ids, conf = [], [], []
    for c in clusters.to_dict("records"):
        hits = jc_by_ch.get(c["chapter_id"], [])
        crosswalk.append([{"jc_name_grc": h["jc_name_grc"], "jc_lemma_tag": h["jc_lemma_tag"], "connection": h["connection"], "method": "lardos_file2_chapter_link"} for h in hits])
        gold_ids.append(gold_ch.get(c["chapter_id"], []))
        conf.append(1.0 if hits else 0.5)
    clusters["jc_crosswalk"] = crosswalk
    clusters["gold_ids"] = gold_ids
    clusters["works"] = [["dmm", *(["jc"] if x else [])] for x in crosswalk]
    clusters["crosswalk_method"] = ["lardos_file2_chapter_link" if x else "dmm_only" for x in crosswalk]
    clusters["confidence"] = conf
    clusters = add_provenance(clusters, "dmm_wellmann", "headword_synonym_cluster_v1")
    write_table(clusters, PROCESSED / "name_clusters.parquet")
    # Merge-precision audit sheet (synonym variants), for a human check (spec/05 Stage 4).
    ex = clusters.explode("variants").dropna(subset=["variants"])
    ex = ex[ex["variants"].map(lambda v: v["variant_source"] == "synonym_list")]
    ex.assign(variant=ex["variants"].map(lambda v: v["variant"]))[["cluster_id", "lemma", "variant"]].sample(
        min(100, len(ex)), random_state=pilot()["seed"]).assign(same_drug="").to_csv(GOLD / "audits" / "cluster_merge_audit_100.csv", index=False)
    summary = {
        "clusters": int(len(clusters)),
        "clusters_with_jc_crosswalk": int(sum(bool(x) for x in crosswalk)),
        "clusters_linked_to_gold": int(clusters["gold_ids"].map(len).gt(0).sum()),
        "gold_names_covered": int(len({g for gs in clusters["gold_ids"] for g in gs})),
        "synonym_variants": int(len(ex)),
    }
    log.info(json.dumps(summary, ensure_ascii=False))
    write_stage_report("cluster-names", summary)
    return summary
