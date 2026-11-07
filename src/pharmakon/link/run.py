"""Stage 6 orchestration: link-chemistry → link-targets → link-diseases → evidence paths."""

from __future__ import annotations

import json

import pandas as pd

from pharmakon.common import (
    PROCESSED,
    frozen_posterior,
    get_logger,
    now_iso,
    pilot,
    write_stage_report,
    write_table,
)
from pharmakon.link import chemistry as C

TIER_SCORE = {"T1": 1.0, "T2": 0.75, "T3": 0.5, "T4": 0.25}


def ot_tier(score: float) -> str:
    return "T1" if score >= 0.7 else "T2" if score >= 0.4 else "T3"


def select_taxa(max_taxa: int) -> pd.DataFrame:
    """Species with P(s|n) ≥ 0.2 for at least one pilot name, highest probability first."""
    post = pd.read_parquet(frozen_posterior())
    taxa = pd.read_parquet(PROCESSED / "taxa.parquet")
    cand = pd.read_parquet(PROCESSED / "id_candidates.parquet")[["taxon_key", "species_key", "taxon_rank"]].drop_duplicates("taxon_key")
    p = post[(post["taxon_key"] != "__unidentified__") & (post["p"] >= pilot()["id_min_p_for_backtest"])]
    best = p.groupby("taxon_key")["p"].max().sort_values(ascending=False).reset_index()
    best = best.merge(cand, on="taxon_key").merge(taxa[["species_key", "wikidata"]], on="species_key", how="left")
    best = best[(best["taxon_rank"] == "SPECIES") & best["wikidata"].notna()]
    return best.head(max_taxa)


def run_chemistry() -> dict:
    log = get_logger("link")
    cfg = pilot()
    sel = select_taxa(cfg["lotus_max_taxa"])
    lotus = C.lotus_compounds(sel["wikidata"].tolist())
    tc = lotus.merge(sel[["wikidata", "taxon_key"]], on="wikidata", how="inner")
    tc["inchikey14"] = tc["inchikey"].str[:14]
    tc["organism_part"] = None  # LOTUS on Wikidata does not record the organ
    write_table(tc, PROCESSED / "taxon_compounds.parquet")

    ids = C.chembl_ids(sorted(tc["inchikey"].unique()))
    tc2 = tc.merge(ids, on="inchikey", how="inner")
    # Cap per taxon for the pilot: earliest-documented compounds first (deterministic).
    tc2 = tc2.sort_values(["taxon_key", "reference_year", "inchikey"], na_position="last")
    capped = tc2.groupby("taxon_key").head(cfg["chembl_max_compounds_per_taxon"])
    mols = sorted(capped["molecule_chembl_id"].unique())
    acts = C.chembl_activities(mols)
    mech = C.chembl_mechanisms(mols)
    tgt = C.chembl_targets(sorted(set(acts["target_chembl_id"]) | set(mech["target_chembl_id"]))) if len(acts) else pd.DataFrame()
    human = tgt[(tgt["organism"] == "Homo sapiens") & (tgt["target_type"] == "SINGLE PROTEIN")]
    ct = acts[acts["target_chembl_id"].isin(human["target_chembl_id"])].copy()
    mech_pairs = set(zip(mech["molecule_chembl_id"], mech["target_chembl_id"], strict=False))
    ct["tier"] = [("T1" if (m, t) in mech_pairs else tr) for m, t, tr in zip(ct["molecule_chembl_id"], ct["target_chembl_id"], ct["tier"], strict=True)]
    ct = ct.merge(ids, on="molecule_chembl_id", how="left")
    ct = ct.rename(columns={"document_year": "doc_year"})
    ct["source_id"], ct["retrieved_at"], ct["method"] = "chembl", now_iso(), "chembl_rest_activity_pchembl>=5"
    write_table(ct, PROCESSED / "compound_targets.parquet")

    # Target → disease via Open Targets (UniProt → Ensembl → associations with MeSH xrefs).
    human = human[human["target_chembl_id"].isin(ct["target_chembl_id"])].copy()
    human["uniprot1"] = human["uniprot"].map(lambda a: a[0] if len(a) else None)
    ens = {u: C.ot_ensembl(u) for u in human["uniprot1"].dropna().unique()}
    human["ensembl_id"] = human["uniprot1"].map(ens)
    rows = []
    for e in sorted({x for x in human["ensembl_id"] if x}):
        rows.extend(C.ot_associations(e))
    td = pd.DataFrame(rows).merge(human[["target_chembl_id", "ensembl_id", "pref_name"]], on="ensembl_id", how="left")
    td["tier"] = td["ot_score"].map(ot_tier)
    td["source_id"], td["retrieved_at"], td["method"] = "opentargets", now_iso(), "ot_graphql_associatedDiseases>=0.2"
    write_table(td, PROCESSED / "target_disease.parquet")

    paths = build_paths(capped, ct, td)
    write_table(paths, PROCESSED / "evidence_paths.parquet")
    taxa_with_cmp = tc["taxon_key"].nunique()
    summary = {
        "taxa_selected": int(len(sel)),
        "taxa_with_compounds": int(taxa_with_cmp),
        "share_taxa_with_compound": round(taxa_with_cmp / max(len(sel), 1), 4),
        "taxon_compound_pairs": int(len(tc)),
        "distinct_compounds": int(tc["inchikey"].nunique()),
        "compound_pairs_with_reference_year": round(float(tc["reference_year"].notna().mean()), 4),
        "compounds_in_chembl": int(ids["inchikey"].nunique()),
        "compounds_queried_for_activity": len(mols),
        "share_queried_compounds_with_human_target": round(ct["molecule_chembl_id"].nunique() / max(len(mols), 1), 4),
        "compound_target_rows": int(len(ct)),
        "human_targets": int(ct["target_chembl_id"].nunique()),
        "target_disease_rows": int(len(td)),
        "opentargets_gaps": len(C.OT_ERRORS),
        "paths_closing_loop": int(paths["closes_loop"].sum()) if len(paths) else 0,
        "taxon_disease_pairs_with_path": int(paths.loc[paths["closes_loop"], ["taxon_key", "mesh_id"]].drop_duplicates().shape[0]) if len(paths) else 0,
    }
    log.info(json.dumps(summary))
    write_stage_report("link-chemistry", summary)
    return summary


def build_paths(tc: pd.DataFrame, ct: pd.DataFrame, td: pd.DataFrame) -> pd.DataFrame:
    """Taxon → Compound → Target → Disease paths whose disease maps to a MeSH ID claimed for that taxon's names.

    path_strength = weakest-link tier score (DeepRoot-style); weighting by P(species) happens downstream.
    """
    claims = pd.read_parquet(PROCESSED / "claims_dmm.parquet")
    post = pd.read_parquet(frozen_posterior())
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    ch2cl = dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=True))
    claims["cluster_id"] = claims["chapter_id"].map(ch2cl)
    cl_mesh = claims[claims["status"] == "ok"].explode("mesh_ids").dropna(subset=["mesh_ids"]).groupby("cluster_id")["mesh_ids"].apply(set).to_dict()
    claimed = sorted({m for s in cl_mesh.values() for m in s})
    desc = C.mesh_descendants(claimed)
    expand = {m: {m, *desc.get(m, [])} for m in claimed}
    cl_post = post[post["unit_id"].str.startswith("cl:")]
    taxon_mesh: dict[str, set[str]] = {}
    for r in cl_post.itertuples():
        if r.taxon_key == "__unidentified__" or r.p < pilot()["id_min_p_for_backtest"]:
            continue
        taxon_mesh.setdefault(r.taxon_key, set()).update(cl_mesh.get(r.unit_id, set()))
    if ct.empty or td.empty:
        return pd.DataFrame(columns=["taxon_key", "mesh_id", "closes_loop"])
    m = tc[["taxon_key", "inchikey", "molecule_chembl_id", "reference_year"]].merge(
        ct[["molecule_chembl_id", "target_chembl_id", "pchembl_value", "tier", "doc_year"]].rename(columns={"tier": "ct_tier"}), on="molecule_chembl_id")
    best_ct = m.sort_values("pchembl_value", ascending=False).drop_duplicates(["taxon_key", "molecule_chembl_id", "target_chembl_id"])
    tdx = td.explode("mesh_xrefs").dropna(subset=["mesh_xrefs"])[["target_chembl_id", "disease_id", "disease_name", "ot_score", "tier", "mesh_xrefs"]].rename(columns={"tier": "td_tier"})
    p = best_ct.merge(tdx, on="target_chembl_id")
    rows = []
    for r in p.itertuples():
        claimed_here = taxon_mesh.get(r.taxon_key, set())
        hit = [cm for cm in claimed_here if r.mesh_xrefs in expand.get(cm, {cm})]
        for cm in hit or [None]:
            rows.append({"taxon_key": r.taxon_key, "inchikey": r.inchikey, "molecule_chembl_id": r.molecule_chembl_id,
                         "target_chembl_id": r.target_chembl_id, "disease_id": r.disease_id, "disease_name": r.disease_name,
                         "disease_mesh": r.mesh_xrefs, "mesh_id": cm, "closes_loop": cm is not None,
                         "ct_tier": r.ct_tier, "td_tier": r.td_tier, "pchembl": r.pchembl_value, "ot_score": r.ot_score,
                         "compound_ref_year": r.reference_year, "activity_doc_year": r.doc_year,
                         "path_strength": min(TIER_SCORE[r.ct_tier], TIER_SCORE[r.td_tier])})
    out = pd.DataFrame(rows)
    out = out[out["closes_loop"]].copy() if len(out) else out
    if len(out):
        out["compound_ref_year"] = out["compound_ref_year"].astype("Float64")
        out["path_strength"] = out["path_strength"].astype(float)
    out["source_id"], out["retrieved_at"], out["method"] = "lotus+chembl+opentargets", now_iso(), "weakest_link_path_v1"
    return out.reset_index(drop=True) if len(out) else out


def path_strength_table(paths: pd.DataFrame) -> pd.DataFrame:
    """Max path strength per (taxon, claimed MeSH)."""
    if paths.empty:
        return pd.DataFrame(columns=["taxon_key", "mesh_id", "path_strength", "n_paths"])
    return paths.groupby(["taxon_key", "mesh_id"]).agg(path_strength=("path_strength", "max"), n_paths=("path_strength", "size"),
                                                         first_activity_year=("activity_doc_year", "min")).reset_index()


