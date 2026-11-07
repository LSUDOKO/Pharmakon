"""Stage 9 — PubMed evidence labels (a co-mention PROXY for pharmacological support).

For each (taxon, MeSH disease) pair arising from a Dioscorides claim, the exact query string is
stored with the row. Cumulative record counts at each cutoff come from ESearch with
``datetype=pdat`` and ``maxdate``; the first year with ≥1 record is found by bisection.
"""

from __future__ import annotations

import json

import pandas as pd

from pharmakon import http
from pharmakon.common import (
    GOLD,
    PROCESSED,
    env,
    get_logger,
    now_iso,
    pilot,
    write_stage_report,
    write_table,
)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PHARM = '("Plant Extracts"[MeSH Terms] OR "Phytochemicals"[MeSH Terms] OR pharmacology[Subheading] OR "drug effects"[Subheading])'
MIN_YEAR = 1900


def _params(extra: dict) -> dict:
    p = {"db": "pubmed", "retmode": "json", "tool": "pharmakon", **extra}
    if env("NCBI_EMAIL"):
        p["email"] = env("NCBI_EMAIL")
    if env("NCBI_API_KEY"):
        p["api_key"] = env("NCBI_API_KEY")
    return p


def count(term: str, maxyear: int | None = None, minyear: int | None = None, retmax: int = 0) -> tuple[int, list[str]]:
    extra: dict = {"term": term, "retmax": retmax}
    if maxyear is not None or minyear is not None:
        extra.update({"datetype": "pdat", "mindate": str(minyear or MIN_YEAR), "maxdate": str(maxyear or 3000)})
    js = http.get_json(f"{EUTILS}/esearch.fcgi", params=_params(extra)) or {}
    r = js.get("esearchresult", {})
    return int(r.get("count", 0)), list(r.get("idlist", []))


def pair_query(species: str, mesh_label: str, entry_terms: list[str]) -> str:
    dis = " OR ".join([f'"{mesh_label}"[MeSH Terms]', *[f'"{t}"[tiab]' for t in entry_terms[:5]]])
    return f'("{species}"[tiab]) AND ({dis}) AND {PHARM}'


def first_year(term: str, lo: int, hi: int) -> int:
    """Smallest year y in [lo, hi] with ≥1 record up to y (cum(hi) > 0 is assumed)."""
    while lo < hi:
        mid = (lo + hi) // 2
        if count(term, maxyear=mid)[0] > 0:
            hi = mid
        else:
            lo = mid + 1
    return lo


def cumulative(term: str, years: list[int]) -> dict[int, int]:
    return {y: count(term, maxyear=y)[0] for y in years}


def build_pairs(max_pairs: int) -> pd.DataFrame:
    claims = pd.read_parquet(PROCESSED / "claims_dmm.parquet")
    claims = claims[(claims["status"] == "ok") & (claims["substance_type"] == "plant")]
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    claims = claims.assign(cluster_id=claims["chapter_id"].map(dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=True))))
    cm = claims.explode("mesh_ids").dropna(subset=["mesh_ids"])[["cluster_id", "mesh_ids", "use_group"]].drop_duplicates()
    post = pd.read_parquet(PROCESSED / "id_posterior.parquet")
    post = post[(post["unit_kind"] == "cluster") & (post["taxon_key"] != "__unidentified__") & (post["p"] >= pilot()["id_min_p_for_backtest"])]
    cand = pd.read_parquet(PROCESSED / "id_candidates.parquet")[["taxon_key", "taxon_rank"]].drop_duplicates("taxon_key")
    post = post.merge(cand, on="taxon_key")
    post = post[post["taxon_rank"] == "SPECIES"]
    pairs = post.merge(cm, left_on="unit_id", right_on="cluster_id")
    pairs = pairs.rename(columns={"mesh_ids": "mesh_id"})
    agg = pairs.groupby(["taxon_key", "mesh_id"]).agg(
        accepted_name=("accepted_name", "first"), p_species=("p", "max"), clusters=("cluster_id", lambda s: sorted(set(s))),
        use_group=("use_group", "first"), skin=("use_group", lambda s: bool((s == "DE").any()))).reset_index()
    agg = agg.sort_values(["skin", "p_species"], ascending=[False, False]).head(max_pairs).reset_index(drop=True)
    return agg


def run() -> dict:
    log = get_logger("evidence-labels")
    cfg = pilot()
    cut = sorted(cfg["cutoffs"])
    t_end = cfg["t_end"]
    years = sorted({cut[0] - 5, *cut, t_end})
    pairs = build_pairs(cfg["pubmed_max_pairs"])
    mesh = pd.read_parquet(PROCESSED / "mesh_terms.parquet").set_index("mesh_id")
    rows = []
    for r in pairs.itertuples():
        label = mesh.loc[r.mesh_id, "mesh_label"] if r.mesh_id in mesh.index else r.mesh_id
        terms = [t for t in (mesh.loc[r.mesh_id, "entry_terms"] if r.mesh_id in mesh.index else []) if t != label]
        q = pair_query(r.accepted_name, label, list(terms))
        total, _ = count(q, maxyear=t_end)
        cum = cumulative(q, years) if total else dict.fromkeys(years, 0)
        fy = None
        if total:
            prev = MIN_YEAR
            for y in years:
                if cum[y] > 0:
                    fy = first_year(q, prev, y)
                    break
                prev = y + 1
        rows.append({"taxon_key": r.taxon_key, "accepted_name": r.accepted_name, "mesh_id": r.mesh_id, "mesh_label": label,
                     "p_species": r.p_species, "clusters": r.clusters, "use_group": r.use_group, "query_string": q,
                     "n_total_to_t_end": cum[t_end], **{f"cum_{y}": cum[y] for y in years}, "first_support_year": fy})
    lab = pd.DataFrame(rows)
    # Popularity confounders: papers on the species (any topic) and on the disease, up to each cutoff.
    pop_sp = {}
    for sp in sorted(lab["accepted_name"].unique()):
        pop_sp[sp] = cumulative(f'"{sp}"[tiab]', years)
    pop_d = {}
    for mid in sorted(lab["mesh_id"].unique()):
        lbl = mesh.loc[mid, "mesh_label"] if mid in mesh.index else mid
        pop_d[mid] = cumulative(f'"{lbl}"[MeSH Terms]', years)
    for y in years:
        lab[f"pop_species_{y}"] = lab["accepted_name"].map(lambda s, y=y: pop_sp[s][y])
        lab[f"pop_disease_{y}"] = lab["mesh_id"].map(lambda m, y=y: pop_d[m][y])
    lab["audited"] = False
    lab["audit_label"] = None
    lab["source_id"], lab["retrieved_at"], lab["method"] = "pubmed", now_iso(), "esearch_pdat_cumulative_v1"
    write_table(lab, PROCESSED / "evidence_labels.parquet")
    # Blinded audit sheets: 100 positive PMIDs and 50 negative pairs (spec/07 §2).
    pos = lab[lab["n_total_to_t_end"] > 0].sample(min(100, int((lab["n_total_to_t_end"] > 0).sum())), random_state=cfg["seed"])
    audit = []
    for r in pos.itertuples():
        _, ids = count(r.query_string, maxyear=t_end, retmax=1)
        audit.append({"taxon": r.accepted_name, "condition": r.mesh_label, "pmid": ids[0] if ids else None,
                      "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{ids[0]}/" if ids else None,
                      "tests_plant_for_condition": ""})
    pd.DataFrame(audit).to_csv(GOLD / "audits" / "label_audit_positive_100.csv", index=False)
    neg = lab[lab["n_total_to_t_end"] == 0]
    neg.sample(min(50, len(neg)), random_state=cfg["seed"])[["accepted_name", "mesh_label", "query_string"]].assign(
        support_exists_anyway="").to_csv(GOLD / "audits" / "label_audit_negative_50.csv", index=False)
    summary = {
        "pairs": int(len(lab)),
        "pairs_skin": int((lab["use_group"] == "DE").sum()),
        "taxa": int(lab["taxon_key"].nunique()),
        "mesh_terms": int(lab["mesh_id"].nunique()),
        "pairs_with_any_support_to_t_end": int((lab["n_total_to_t_end"] > 0).sum()),
        "positive_rate": round(float((lab["n_total_to_t_end"] > 0).mean()), 4),
        "first_support_year_quantiles": lab["first_support_year"].dropna().quantile([0.1, 0.5, 0.9]).round(0).to_dict(),
        "eligible_and_positive_by_cutoff": {T: {"eligible": int((lab[f"cum_{T}"] == 0).sum()),
                                               "positive": int(((lab[f"cum_{T}"] == 0) & (lab[f"cum_{t_end}"] > 0)).sum())} for T in cut},
        "label_audit": "pending human audit (data/gold/audits/label_audit_*.csv)",
        "t_end": t_end,
    }
    log.info(json.dumps(summary))
    write_stage_report("evidence-labels", summary)
    return summary
