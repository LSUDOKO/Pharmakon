"""Stage 11 — leads: currently-unsupported (taxon, condition) pairs ranked by model score × P(species).

Also answers RQ4: how much does carrying identification uncertainty change the ranking?
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

from pharmakon.common import (
    PROCESSED,
    REPORTS,
    get_logger,
    now_iso,
    write_stage_report,
    write_table,
)
from pharmakon.forecast.run import final_model_scores
from pharmakon.leads.toxicity import build as build_toxic

NONE = "__unidentified__"


def run() -> dict:
    log = get_logger("leads")
    tox = build_toxic()
    write_table(tox, PROCESSED / "toxic_taxa.parquet")
    now = final_model_scores()
    post = pd.read_parquet(PROCESSED / "id_posterior.parquet")
    post = post[post["unit_kind"] == "cluster"]
    top1 = post.sort_values("p", ascending=False).groupby("unit_id").head(1)
    top1_taxa = {(r.unit_id, r.taxon_key) for r in top1.itertuples() if r.taxon_key != NONE}
    now["is_top1_identity"] = [any((c, t) in top1_taxa for c in cl) for t, cl in zip(now["taxon_key"], now["clusters"], strict=True)]
    paths = pd.read_parquet(PROCESSED / "evidence_paths.parquet")
    ps = paths.groupby(["taxon_key", "mesh_id"]).agg(path_strength=("path_strength", "max"), n_paths=("path_strength", "size"),
                                                     example_target=("target_chembl_id", "first"), example_compound=("molecule_chembl_id", "first")).reset_index() if len(paths) else pd.DataFrame(columns=["taxon_key", "mesh_id", "path_strength", "n_paths"])
    taxa = pd.read_parquet(PROCESSED / "taxa.parquet")
    cand = pd.read_parquet(PROCESSED / "id_candidates.parquet")[["taxon_key", "species_key", "genus", "family"]].drop_duplicates("taxon_key")
    cons = cand.merge(taxa[["species_key", "iucn_status"]], on="species_key", how="left").set_index("taxon_key")
    toxg = tox.set_index("genus")
    now = now.merge(ps, on=["taxon_key", "mesh_id"], how="left")
    now["path_strength"] = now["path_strength"].fillna(0.0)
    now["p_species"] = now["h_p_species"]
    now["lead_score"] = now["model_score"]
    now["score_weighted"] = now["model_score"] * now["p_species"]
    now["score_top1_only"] = now["model_score"] * now["is_top1_identity"].astype(float)
    now["genus"] = now["taxon_key"].map(cons["genus"])
    now["family"] = now["taxon_key"].map(cons["family"])
    now["conservation_status"] = now["taxon_key"].map(cons["iucn_status"])
    now["toxicity_flag"] = now["genus"].isin(toxg.index)
    now["toxicity_citation"] = now["genus"].map(lambda g: toxg.loc[g, "pubchem_url"] if g in toxg.index else None)
    leads = now[~now["supported_today"]].sort_values("score_weighted", ascending=False).reset_index(drop=True)
    leads["rank_weighted"] = np.arange(1, len(leads) + 1)
    leads["rank_top1_only"] = leads["score_top1_only"].rank(ascending=False, method="min").astype(int)
    keep = ["taxon_key", "accepted_name", "family", "genus", "mesh_id", "mesh_label", "clusters", "p_species", "lead_score", "score_weighted",
            "score_top1_only", "rank_weighted", "rank_top1_only", "is_top1_identity", "path_strength", "n_paths", "conservation_status",
            "toxicity_flag", "toxicity_citation", "h_present_jc", "h_modern_attested", "h_n_dmm_claims", "query_string"]
    out = leads[keep].copy()
    out["source_id"], out["retrieved_at"], out["method"] = "pharmakon_leads", now_iso(), "logistic_full@T=2015 × P(species)"
    write_table(out, PROCESSED / "leads.parquet")
    tau = kendalltau(out["score_weighted"], out["score_top1_only"]).statistic if len(out) > 2 else float("nan")
    top20_w = set(out.head(20).index)
    top20_t = set(out.sort_values("score_top1_only", ascending=False).head(20).index)
    low_conf = int((out.head(20)["p_species"] < 0.5).sum())
    summary = {
        "candidate_pairs_scored": int(len(now)),
        "unsupported_today": int(len(out)),
        "kendall_tau_weighted_vs_top1": round(float(tau), 4),
        "top20_changed_when_using_top1_identity": len(top20_w - top20_t),
        "top20_resting_on_p_species_below_0.5": low_conf,
        "top20_with_toxicity_flag": int(out.head(20)["toxicity_flag"].sum()),
        "top20_with_closed_evidence_path": int((out.head(20)["path_strength"] > 0).sum()),
        "toxic_genera_verified_in_pubchem": int(tox["verified"].sum()),
    }
    write_md(out)
    log.info(json.dumps(summary))
    write_stage_report("leads", summary)
    return summary


def write_md(out: pd.DataFrame) -> None:
    lines = ["# Top 50 research leads (hypotheses, NOT medical advice)", "",
             "Pairs with **no PubMed support to date** (co-mention proxy), ranked by forecast score × P(species).",
             "P(species) is the identification probability (90% bootstrap intervals in `id_posterior`). ⚠ = known toxic constituent (PubChem GHS link).",
             "Evidence path: weakest-link tier of a closed taxon→compound→target→disease path (— = none found within the pilot caps).", "",
             "| # | Species | Condition (MeSH) | P(species) | score×P | evidence path | IUCN | toxicity |", "|---|---|---|---|---|---|---|---|"]
    for r in out.head(50).itertuples():
        tox = f"⚠ [PubChem]({r.toxicity_citation})" if r.toxicity_flag else ""
        lines.append(f"| {r.rank_weighted} | *{r.accepted_name}* | {r.mesh_label} | {r.p_species:.2f} | {r.score_weighted:.3f} | "
                     f"{'tier ' + format(r.path_strength, '.2f') if r.path_strength > 0 else '—'} | {r.conservation_status if isinstance(r.conservation_status, str) else '—'} | {tox} |")
    (REPORTS / "leads_top50.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
