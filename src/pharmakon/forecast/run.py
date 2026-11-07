"""Stage 10 — the temporal backtest ("time machine"), spec/07 §4.

Rows: (taxon s, MeSH disease d) pairs from Dioscorides claims with P(s|n) ≥ 0.2.
At cutoff T a row is eligible iff it had no PubMed support up to T; label = support appears in (T, T_end].
Rolling origin: train on rows eligible at T−5 (labels in (T−5, T]); test on rows eligible at T.
Every feature uses information dated ≤ the cutoff of its row. No LLM output is used anywhere.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from pharmakon.common import (
    PROCESSED,
    REPORTS,
    get_logger,
    now_iso,
    pilot,
    write_stage_report,
    write_table,
)

HISTORY = ["h_p_species", "h_n_dmm_claims", "h_present_jc", "h_modern_attested", "h_topical_share", "h_n_texts"]
CHEM = ["c_n_compounds", "c_n_compounds_active_on_assoc_targets"]
POP = ["pop_species", "pop_disease"]
SETS = {
    "popularity": POP,
    "history": HISTORY,
    "chemistry": CHEM,
    "history+popularity": HISTORY + POP,
    "chemistry+popularity": CHEM + POP,
    "full": HISTORY + CHEM + POP,
    "full_without_OT_dependent": HISTORY + ["c_n_compounds"] + POP,
}


def _history_static() -> pd.DataFrame:
    """Per-pair history that is dated ≤ every cutoff (1st and 13th c.): claims, JC attestation, routes."""
    claims = pd.read_parquet(PROCESSED / "claims_dmm.parquet")
    claims = claims[(claims["status"] == "ok") & (claims["substance_type"] == "plant")]
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    claims = claims.assign(cluster_id=claims["chapter_id"].map(dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=True))))
    ex = claims.explode("mesh_ids").dropna(subset=["mesh_ids"])
    per = ex.groupby(["cluster_id", "mesh_ids"]).agg(n_claims=("claim_id", "size"), topical=("route", lambda s: float((s == "topical").mean())),
                                                    use_group=("use_group", "first")).reset_index().rename(columns={"mesh_ids": "mesh_id"})
    pers = pd.read_parquet(PROCESSED / "persistence.parquet")[["cluster_id", "use_group", "present_jc"]]
    per = per.merge(pers, on=["cluster_id", "use_group"], how="left")
    per["present_jc"] = per["present_jc"].fillna(False).astype(bool).astype(float)
    return per


def _modern_attested_by(labels: pd.DataFrame, T: int) -> np.ndarray:
    """1 if the species or its genus is attested in a modern record published ≤ T for the pair's use group."""
    mod = pd.read_parquet(PROCESSED / "modern_attestations.parquet")
    mod = mod[pd.to_numeric(mod["year"], errors="coerce") <= T]
    cand = pd.read_parquet(PROCESSED / "id_candidates.parquet")[["taxon_key", "genus"]].drop_duplicates("taxon_key").set_index("taxon_key")["genus"]
    sp = set(zip(mod["taxon_key"], mod["use_group"], strict=True))
    ge = set(zip(mod["genus"], mod["use_group"], strict=True))
    return np.array([float((t, g) in sp or (cand.get(t), g) in ge) for t, g in zip(labels["taxon_key"], labels["use_group"], strict=True)])


def _chem_by(labels: pd.DataFrame, T: int) -> tuple[np.ndarray, np.ndarray]:
    tc = pd.read_parquet(PROCESSED / "taxon_compounds.parquet")
    tc = tc[pd.to_numeric(tc["reference_year"], errors="coerce") <= T]
    n_c = tc.groupby("taxon_key")["inchikey"].nunique()
    paths = pd.read_parquet(PROCESSED / "evidence_paths.parquet")
    if len(paths):
        paths = paths[(pd.to_numeric(paths["compound_ref_year"], errors="coerce") <= T) & (pd.to_numeric(paths["activity_doc_year"], errors="coerce") <= T)]
        n_a = paths.groupby(["taxon_key", "mesh_id"])["inchikey"].nunique()
    else:
        n_a = pd.Series(dtype=float)
    a = labels["taxon_key"].map(n_c).fillna(0).to_numpy(float)
    b = np.array([float(n_a.get((t, m), 0)) for t, m in zip(labels["taxon_key"], labels["mesh_id"], strict=True)])
    return np.log1p(a), np.log1p(b)


def features_at(labels: pd.DataFrame, hist: pd.DataFrame, T: int) -> pd.DataFrame:
    """Feature matrix for every pair using information dated ≤ T only."""
    df = labels[["taxon_key", "mesh_id", "accepted_name", "mesh_label", "p_species", "clusters", "use_group", "query_string"]].copy()
    h = df.explode("clusters").merge(hist.drop(columns=["use_group"]), left_on=["clusters", "mesh_id"], right_on=["cluster_id", "mesh_id"], how="left")
    agg = h.groupby(["taxon_key", "mesh_id"]).agg(n_claims=("n_claims", "sum"), topical=("topical", "mean"), present_jc=("present_jc", "max")).reset_index()
    df = df.merge(agg, on=["taxon_key", "mesh_id"], how="left")
    df["h_p_species"] = df["p_species"]
    df["h_n_dmm_claims"] = np.log1p(df["n_claims"].fillna(0))
    df["h_present_jc"] = df["present_jc"].fillna(0.0)
    df["h_modern_attested"] = _modern_attested_by(df, T)
    df["h_topical_share"] = df["topical"].fillna(0.0)
    df["h_n_texts"] = 1 + df["h_present_jc"] + df["h_modern_attested"]
    df["c_n_compounds"], df["c_n_compounds_active_on_assoc_targets"] = _chem_by(df, T)
    df["pop_species"] = np.log1p(labels[f"pop_species_{T}"].to_numpy(float))
    df["pop_disease"] = np.log1p(labels[f"pop_disease_{T}"].to_numpy(float))
    df["group"] = df["clusters"].map(lambda c: c[0] if len(c) else "none")
    return df


def precision_at(y: np.ndarray, s: np.ndarray, k: int) -> float:
    k = min(k, len(y))
    return float(y[np.argsort(-s)][:k].mean()) if k else float("nan")


def metrics(y: np.ndarray, s: np.ndarray) -> dict:
    out = {"n": int(len(y)), "positives": int(y.sum()), "base_rate": round(float(y.mean()), 4) if len(y) else None}
    if 0 < y.sum() < len(y):
        out["auroc"] = round(float(roc_auc_score(y, s)), 4)
        out["auprc"] = round(float(average_precision_score(y, s)), 4)
        out["auprc_lift"] = round(out["auprc"] / max(out["base_rate"], 1e-9), 3)
    for k in (20, 50, 100):
        out[f"p_at_{k}"] = round(precision_at(y, s, k), 4)
    return out


def bootstrap(y: np.ndarray, scores: dict[str, np.ndarray], groups: np.ndarray, n: int, seed: int) -> dict:
    """Cluster bootstrap (resampling ancient names) for AUPRC/AUROC and ΔAUPRC(history+pop − pop)."""
    rng = np.random.default_rng(seed)
    ug = np.unique(groups)
    idx_by = {g: np.where(groups == g)[0] for g in ug}
    res: dict[str, list] = {k: [] for k in scores} | {"delta_auprc_histpop_minus_pop": [], "delta_auroc_histpop_minus_pop": []}
    auroc: dict[str, list] = {k: [] for k in scores}
    for _ in range(n):
        idx = np.concatenate([idx_by[g] for g in rng.choice(ug, size=len(ug), replace=True)])
        yy = y[idx]
        if yy.sum() == 0 or yy.sum() == len(yy):
            continue
        for k, s in scores.items():
            res[k].append(average_precision_score(yy, s[idx]))
            auroc[k].append(roc_auc_score(yy, s[idx]))
        if "history+popularity" in scores and "popularity" in scores:
            res["delta_auprc_histpop_minus_pop"].append(res["history+popularity"][-1] - res["popularity"][-1])
            res["delta_auroc_histpop_minus_pop"].append(auroc["history+popularity"][-1] - auroc["popularity"][-1])
    ci = {}
    for k, v in res.items():
        if v:
            ci[k] = [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
    for k, v in auroc.items():
        if v:
            ci[f"{k}_auroc"] = [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
    d = res.get("delta_auprc_histpop_minus_pop", [])
    if d:
        ci["p_delta_auprc_le_0"] = round(float(np.mean(np.array(d) <= 0)), 4)
    return ci


def _fit_score(kind: str, Xtr: np.ndarray, ytr: np.ndarray, Xte: np.ndarray, seed: int) -> np.ndarray:
    if ytr.sum() == 0 or ytr.sum() == len(ytr):
        return np.zeros(len(Xte))
    if kind == "logistic":
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))
    else:
        m = HistGradientBoostingClassifier(max_depth=3, max_iter=150, learning_rate=0.05, random_state=seed)
    m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


def run() -> dict:
    log = get_logger("forecast")
    cfg = pilot()
    seed, t_end = cfg["seed"], cfg["t_end"]
    labels = pd.read_parquet(PROCESSED / "evidence_labels.parquet")
    hist = _history_static()
    results, datasets, hits = {}, [], []
    rng = np.random.default_rng(seed)
    for T in sorted(cfg["cutoffs"]):
        T0 = T - 5
        tr_mask = (labels[f"cum_{T0}"] == 0).to_numpy()
        te_mask = (labels[f"cum_{T}"] == 0).to_numpy()
        ftr = features_at(labels, hist, T0)[tr_mask].reset_index(drop=True)
        fte = features_at(labels, hist, T)[te_mask].reset_index(drop=True)
        ytr = (labels.loc[tr_mask, f"cum_{T}"].to_numpy() > 0).astype(int)
        yte = (labels.loc[te_mask, f"cum_{t_end}"].to_numpy() > 0).astype(int)
        yte_strict = ((labels.loc[te_mask, f"cum_{T}"].to_numpy() < 2) & (labels.loc[te_mask, f"cum_{t_end}"].to_numpy() >= 2)).astype(int)
        scores: dict[str, np.ndarray] = {"random": rng.random(len(fte)), "popularity_raw": fte["pop_species"].to_numpy()}
        for name, cols in SETS.items():
            scores[name] = _fit_score("logistic", ftr[cols].to_numpy(float), ytr, fte[cols].to_numpy(float), seed)
        scores["full_gbm"] = _fit_score("gbm", ftr[SETS["full"]].to_numpy(float), ytr, fte[SETS["full"]].to_numpy(float), seed)
        # Leakage control: permute history features across rows (train and test) — should fall to baseline.
        sh_tr, sh_te = ftr.copy(), fte.copy()
        for c in HISTORY:
            sh_tr[c] = rng.permutation(sh_tr[c].to_numpy())
            sh_te[c] = rng.permutation(sh_te[c].to_numpy())
        scores["shuffled_history+popularity"] = _fit_score("logistic", sh_tr[HISTORY + POP].to_numpy(float), ytr, sh_te[HISTORY + POP].to_numpy(float), seed)
        res = {"train_rows": int(len(ftr)), "train_positives": int(ytr.sum()), "test": {k: metrics(yte, s) for k, s in scores.items()},
               "test_strict_label": {k: metrics(yte_strict, s) for k, s in scores.items() if k in {"popularity", "history+popularity", "full"}}}
        res["bootstrap_ci"] = bootstrap(yte, {k: scores[k] for k in ("popularity", "history+popularity", "full", "history")}, fte["group"].to_numpy(), cfg["bootstrap_n"], seed)
        if len(ftr) and ytr.sum() and ytr.sum() < len(ytr):
            lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(ftr[SETS["full"]].to_numpy(float), ytr)
            res["full_logistic_coefficients"] = {c: round(float(w), 4) for c, w in zip(SETS["full"], lr[-1].coef_[0], strict=True)}
        results[T] = res
        fte = fte.assign(cutoff=T, label=yte, label_strict=yte_strict, score_full=scores["full"], score_histpop=scores["history+popularity"],
                         score_pop=scores["popularity"])
        datasets.append(fte)
        firsts = labels.loc[te_mask, "first_support_year"].to_numpy()
        top = fte.assign(first_support_year=firsts).sort_values("score_histpop", ascending=False).head(25)
        hits.append(top.assign(outcome=np.where(top["label"] == 1, "hit", "no support found (yet)")))
    ds = pd.concat(datasets, ignore_index=True)
    ds["source_id"], ds["retrieved_at"], ds["method"] = "pharmakon_forecast", now_iso(), "rolling_origin_v1"
    write_table(ds.drop(columns=["clusters"]), PROCESSED / "forecast_dataset.parquet")
    hit = pd.concat(hits, ignore_index=True)[["cutoff", "accepted_name", "mesh_label", "score_histpop", "label", "first_support_year", "outcome", "query_string"]]
    hit["source_id"], hit["retrieved_at"], hit["method"] = "pharmakon_forecast", now_iso(), "rolling_origin_v1"
    write_table(hit, PROCESSED / "forecast_hits.parquet")
    summary = {"cutoffs": sorted(cfg["cutoffs"]), "t_end": t_end, "feature_sets": SETS, "results": {str(k): v for k, v in results.items()},
               "leakage_controls": ["no LLM features", "identification uses no pharmacology", "modern studies gated by publication year ≤ T",
                                    "LOTUS reference year and ChEMBL document year ≤ T", "shuffled-history control reported",
                                    "Open Targets associations are current (not historical): see full_without_OT_dependent"],
               "label_note": "PubMed co-mention proxy; label precision pending human audit"}
    log.info(json.dumps({T: {k: v["test"]["history+popularity"].get("auprc") for k, v in [(T, results[T])]} for T in results}))
    write_stage_report("forecast", summary)
    (REPORTS / "stages").mkdir(parents=True, exist_ok=True)
    return {str(T): {m: results[T]["test"][m].get("auprc") for m in ("random", "popularity", "history", "history+popularity", "full", "shuffled_history+popularity")}
            | {"positives": results[T]["test"]["full"]["positives"], "n": results[T]["test"]["full"]["n"]} for T in results}


def final_model_scores() -> pd.DataFrame:
    """Score every currently-unsupported pair (features ≤ T_end) with the model trained at the last cutoff."""
    cfg = pilot()
    T, t_end = max(cfg["cutoffs"]), cfg["t_end"]
    labels = pd.read_parquet(PROCESSED / "evidence_labels.parquet")
    hist = _history_static()
    tr_mask = (labels[f"cum_{T}"] == 0).to_numpy()
    ftr = features_at(labels, hist, T)[tr_mask]
    ytr = (labels.loc[tr_mask, f"cum_{t_end}"].to_numpy() > 0).astype(int)
    now = features_at(labels, hist, t_end)
    cols = SETS["full"]
    now["model_score"] = _fit_score("logistic", ftr[cols].to_numpy(float), ytr, now[cols].to_numpy(float), cfg["seed"])
    now["supported_today"] = labels[f"cum_{t_end}"].to_numpy() > 0
    return now
