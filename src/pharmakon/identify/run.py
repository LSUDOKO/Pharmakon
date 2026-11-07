"""Stage 5 — identify: candidates → features → conditional logit → LONO evaluation → posteriors."""

from __future__ import annotations

import json
from collections import Counter

import numpy as np
import pandas as pd

from pharmakon.common import (
    GOLD,
    INTERIM,
    PROCESSED,
    REPORTS,
    get_logger,
    now_iso,
    pilot,
    write_stage_report,
    write_table,
)
from pharmakon.identify import features as F
from pharmakon.identify.candidates import build_candidates, build_units
from pharmakon.identify.model import CLogit, Unit, bootstrap_ci, ece, unit_metrics

MODEL_VERSION = "clogit_v1"
TRANSFER_VERSION = "clogit_transfer_v1"
NONE = "__unidentified__"
MAIN = [f for g in ("f2", "f3", "f4", "f6") for f in F.GROUPS[g]]
# Lardos literature counts exist only for the 61 gold names; the transferable model omits them so it
# can score every Dioscorides name without a train/apply distribution shift.
TRANSFER = [c for c in MAIN if c not in {"f4_lit_dmm", "f4_lit_ethno"}]


def _targets(feats: pd.DataFrame, gold: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict]:
    """Expert-correct indicator per gold unit over [candidates..., ∅]."""
    top = gold[gold["is_expert_top"]].groupby("gold_id")["candidate_key"].apply(set).to_dict()
    unid = gold.groupby("gold_id")["expert_unidentified"].first().to_dict()
    ys, dropped = {}, {"all_expert_top_failed_gbif": []}
    for uid, grp in feats.groupby("unit_id", sort=False):
        if uid not in unid:
            continue
        if unid[uid]:
            y = np.zeros(len(grp) + 1)
            y[-1] = 1.0
        else:
            hit = np.array([bool(set(ks) & top.get(uid, set())) for ks in grp["candidate_keys"]] + [False], dtype=float)
            if hit.sum() == 0:
                dropped["all_expert_top_failed_gbif"].append(uid)
                continue
            y = hit / hit.sum()
        ys[uid] = y
    return ys, dropped


def _units(feats: pd.DataFrame, ys: dict, cols: list[str]) -> list[Unit]:
    out = []
    for uid, grp in feats.groupby("unit_id", sort=False):
        if uid in ys:
            out.append(Unit(uid=uid, X=grp[cols].to_numpy(float), y=ys[uid], taxa=grp["taxon_key"].tolist()))
    return out


def lono(units: list[Unit], groups: dict[str, str], l2: float = 1.0, calibrate: bool = True) -> dict[str, np.ndarray]:
    """Leave-one-name-out (grouped by JC lemma). Temperature fitted on inner LONO of the training fold."""
    preds: dict[str, np.ndarray] = {}
    gids = sorted({groups[u.uid] for u in units})
    for g in gids:
        train = [u for u in units if groups[u.uid] != g]
        test = [u for u in units if groups[u.uid] == g]
        m = CLogit(l2=l2).fit(train)
        if calibrate:
            inner_logits, inner_units = [], []
            for h in sorted({groups[u.uid] for u in train}):
                tr2 = [u for u in train if groups[u.uid] != h]
                te2 = [u for u in train if groups[u.uid] == h]
                m2 = CLogit(l2=l2).fit(tr2)
                for u in te2:
                    inner_logits.append(m2.utilities(u.X))
                    inner_units.append(u)
            m.fit_temperature(inner_units, inner_logits)
        for u in test:
            preds[u.uid] = m.predict(u.X)
    return preds


def summarise(preds: dict[str, np.ndarray], units: list[Unit], seed: int, n_boot: int) -> dict:
    by = {u.uid: u for u in units}
    rows = [unit_metrics(preds[uid], by[uid].y) | {"uid": uid} for uid in preds]
    df = pd.DataFrame(rows)
    out = {"n_names": int(len(df))}
    for m in ["top1", "top3", "rr", "logloss", "brier"]:
        v = df[m].to_numpy()
        lo, hi = bootstrap_ci(v, n=n_boot, seed=seed)
        out[m] = {"mean": round(float(v.mean()), 4), "ci95": [round(lo, 4), round(hi, 4)]}
    e, rel = ece(df["conf"].to_numpy(), df["top1"].to_numpy())
    out["ece"] = round(e, 4)
    out["reliability"] = rel
    out["per_name"] = df.round(4).to_dict("records")
    return out


def baseline_lsj(feats: pd.DataFrame, units: list[Unit]) -> dict[str, np.ndarray]:
    """Dictionary baseline: all mass on LSJ's asserted binomial when it is a candidate, else ∅."""
    preds = {}
    for u in units:
        grp = feats[feats["unit_id"] == u.uid]
        lsj = grp["f4_lsj"].to_numpy()
        p = np.zeros(len(grp) + 1)
        if (lsj == 1.0).any():
            p[int(np.argmax(lsj == 1.0))] = 1.0
        elif (lsj > 0).any():
            p[int(np.argmax(lsj))] = 1.0
        else:
            p[-1] = 1.0
        preds[u.uid] = np.clip(p, 1e-6, 1)  # avoid log(0); renormalised below
        preds[u.uid] /= preds[u.uid].sum()
    return preds


def baseline_uniform(units: list[Unit]) -> dict[str, np.ndarray]:
    return {u.uid: np.full(len(u.X) + 1, 1.0 / (len(u.X) + 1)) for u in units}


def baseline_genus(feats: pd.DataFrame, units: list[Unit], groups: dict[str, str]) -> dict[str, np.ndarray]:
    """Most-frequent-genus prior learned from expert top identifications of the OTHER names."""
    preds = {}
    genera = feats.groupby("unit_id", sort=False)["genus"].apply(list).to_dict()
    for u in units:
        train = [v for v in units if groups[v.uid] != groups[u.uid]]
        genus_ct: Counter = Counter()
        n_none = 0
        for v in train:
            g = genera[v.uid]
            if v.y[-1] > 0:
                n_none += 1
            for gi, yi in zip(g, v.y[:-1], strict=True):
                if yi > 0:
                    genus_ct[gi] += 1
        s = np.array([genus_ct.get(g, 0) + 1.0 for g in genera[u.uid]])
        p_none = n_none / max(len(train), 1)
        p = np.append((1 - p_none) * s / s.sum(), p_none)
        preds[u.uid] = p
    return preds


def fit_final(units_: list[Unit], groups: dict[str, str], seed: int, n_boot: int = 200) -> tuple[CLogit, list[CLogit]]:
    """Fit on all gold names; temperature from LONO utilities; bootstrap refits give 90% intervals."""
    final = CLogit().fit(units_)
    lg, uu = [], []
    for g in sorted({groups[u.uid] for u in units_}):
        m2 = CLogit().fit([u for u in units_ if groups[u.uid] != g])
        for u in units_:
            if groups[u.uid] == g:
                lg.append(m2.utilities(u.X))
                uu.append(u)
    final.fit_temperature(uu, lg)
    rng = np.random.default_rng(seed)
    gids = sorted({groups[u.uid] for u in units_})
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(gids, size=len(gids), replace=True)
        b = CLogit().fit([u for g in pick for u in units_ if groups[u.uid] == g])
        b.T = final.T
        boots.append(b)
    return final, boots


def run() -> dict:
    log = get_logger("identify")
    cfg = pilot()
    seed, n_boot = cfg["seed"], cfg["bootstrap_n"]
    units = build_units()
    cand, ver = build_candidates(units)
    write_table(ver, INTERIM / "gbif_verification.parquet")
    taxa = F.enrich_taxa(cand)
    taxa["source_id"], taxa["retrieved_at"], taxa["method"] = "gbif_occ+wikidata_taxa", now_iso(), "gbif_facet+wikidata_sparql"
    write_table(taxa, PROCESSED / "taxa.parquet")
    feats = F.compute(cand, units, taxa)
    oracle = pd.read_parquet(GOLD / "lardos_oracle.parquet")
    okey = {(r.gold_id, r.candidate_key): float(r.oracle_bot_score) for r in oracle.itertuples()}
    feats["oracle_bot"] = [max((okey.get((u, k), 0.0) for k in ks), default=0.0) for u, ks in zip(feats["unit_id"], feats["candidate_keys"], strict=True)]
    gold = pd.read_parquet(GOLD / "lardos_gold.parquet")
    ys, dropped = _targets(feats, gold)
    groups = units.set_index("unit_id")["group"].to_dict()

    gold_units = _units(feats, ys, MAIN)
    results: dict[str, dict] = {}
    preds_main = lono(gold_units, groups)
    results["model_calibrated"] = summarise(preds_main, gold_units, seed, n_boot)
    results["model_uncalibrated"] = summarise(lono(gold_units, groups, calibrate=False), gold_units, seed, n_boot)
    results["baseline_lsj"] = summarise(baseline_lsj(feats, gold_units), gold_units, seed, n_boot)
    results["baseline_genus_prior"] = summarise(baseline_genus(feats, gold_units, groups), gold_units, seed, n_boot)
    results["baseline_uniform"] = summarise(baseline_uniform(gold_units), gold_units, seed, n_boot)
    results["baseline_llm_judge"] = {"status": "not_run", "reason": "ANTHROPIC_API_KEY not set (spec/06 Option C is comparison-only)"}
    for g in ("f2", "f3", "f4", "f6"):
        cols = [c for c in MAIN if c not in F.GROUPS[g]]
        u2 = _units(feats, ys, cols)
        results[f"ablation_without_{g}"] = summarise(lono(u2, groups), u2, seed, n_boot)
    # Circularity check: the gold tie-break (uses score) draws on modern ethnobotanical records, which
    # f4_lit_ethno also counts. Report the model without it.
    u_ne = _units(feats, ys, [c for c in MAIN if c != "f4_lit_ethno"])
    results["ablation_without_f4_lit_ethno"] = summarise(lono(u_ne, groups), u_ne, seed, n_boot)
    u_tr = _units(feats, ys, TRANSFER)
    results["transfer_model_calibrated"] = summarise(lono(u_tr, groups), u_tr, seed, n_boot)
    u_or = _units(feats, ys, MAIN + ["oracle_bot"])
    results["ablation_plus_ORACLE_expert_traits"] = summarise(lono(u_or, groups), u_or, seed, n_boot)

    # Stratified accuracy by expert confidence.
    conf = gold.groupby("gold_id")["expert_confidence"].first()
    pn = pd.DataFrame(results["model_calibrated"]["per_name"])
    pn["expert_confidence"] = pn["uid"].map(conf)
    strat = pn.groupby("expert_confidence")["top1"].agg(["mean", "count"]).round(3).reset_index().to_dict("records")

    final, boots = fit_final(_units(feats, ys, MAIN), groups, seed)
    final_tr, boots_tr = fit_final(u_tr, groups, seed)
    kinds = units.set_index("unit_id")["unit_kind"].to_dict()

    post_rows, expl_rows = [], []
    ts = now_iso()
    for uid, grp in feats.groupby("unit_id", sort=False):
        gold_unit = kinds.get(uid) == "gold"
        cols, mdl, bts = (MAIN, final, boots) if gold_unit else (TRANSFER, final_tr, boots_tr)
        X = grp[cols].to_numpy(float)
        p = mdl.predict(X)
        bs = np.array([b.predict(X) for b in bts])
        lo, hi = np.percentile(bs, 5, axis=0), np.percentile(bs, 95, axis=0)
        contrib = mdl.contributions(X)
        version = MODEL_VERSION if gold_unit else TRANSFER_VERSION
        low_cov = len(grp) < 2
        for j, r in enumerate(grp.itertuples()):
            post_rows.append({"unit_id": uid, "taxon_key": r.taxon_key, "accepted_name": r.accepted_name, "family": r.family, "genus": r.genus,
                              "p": float(p[j]), "p_lo": float(min(lo[j], p[j])), "p_hi": float(max(hi[j], p[j])),
                              "low_candidate_coverage": low_cov, "model_version": version})
            expl_rows.append({"unit_id": uid, "taxon_key": r.taxon_key, "model_version": version,
                              **{f"w_{c}": (float(contrib[j, cols.index(c)]) if c in cols else 0.0) for c in MAIN},
                              **{c: float(getattr(r, c)) for c in MAIN}, "candidate_sources": list(r.candidate_sources),
                              "input_names": list(r.input_names), "lit_ref_years": list(r.lit_ref_years)})
        post_rows.append({"unit_id": uid, "taxon_key": NONE, "accepted_name": None, "family": None, "genus": None,
                          "p": float(p[-1]), "p_lo": float(min(lo[-1], p[-1])), "p_hi": float(max(hi[-1], p[-1])),
                          "low_candidate_coverage": low_cov, "model_version": version})
    # Units with no verified candidate at all: everything on ∅.
    have = set(feats["unit_id"])
    for u in units.to_dict("records"):
        if u["unit_id"] not in have:
            post_rows.append({"unit_id": u["unit_id"], "taxon_key": NONE, "accepted_name": None, "family": None, "genus": None,
                              "p": 1.0, "p_lo": 1.0, "p_hi": 1.0, "low_candidate_coverage": True, "model_version": "no_verified_candidates"})
    post = pd.DataFrame(post_rows)
    post = post.merge(units[["unit_id", "unit_kind", "cluster_id"]], on="unit_id", how="left")
    post["calibrated"] = post["model_version"] != "no_verified_candidates"
    post["source_id"], post["retrieved_at"] = "pharmakon_identify", ts
    post["method"] = post["model_version"].map({MODEL_VERSION: f"{MODEL_VERSION}:T={final.T:.3f}", TRANSFER_VERSION: f"{TRANSFER_VERSION}:T={final_tr.T:.3f}"}).fillna("no_verified_candidates")
    write_table(post, PROCESSED / "id_posterior.parquet")
    expl = pd.DataFrame(expl_rows)
    expl["source_id"], expl["retrieved_at"], expl["method"] = "pharmakon_identify", ts, MODEL_VERSION
    write_table(expl, PROCESSED / "id_explanations.parquet")
    cand_out = feats.drop(columns=["vernacular_el"]).copy()
    write_table(cand_out, PROCESSED / "id_candidates.parquet")

    cl = post[post["unit_kind"] == "cluster"]
    top = cl.sort_values("p", ascending=False).groupby("unit_id").head(1)
    summary = {
        "model_version": MODEL_VERSION,
        "features": {c: F.FEATURES[c] for c in MAIN},
        "weights": {c: round(float(w), 4) for c, w in zip(MAIN, final.w, strict=True)},
        "none_utility_b": round(final.b, 4),
        "temperature": round(final.T, 4),
        "transfer_model": {"features": TRANSFER, "weights": {c: round(float(w), 4) for c, w in zip(TRANSFER, final_tr.w, strict=True)},
                           "none_utility_b": round(final_tr.b, 4), "temperature": round(final_tr.T, 4)},
        "gold_names_evaluated": len(gold_units),
        "gold_names_dropped": dropped,
        "candidates_total": int(len(feats)),
        "gbif_verification": {"inputs": int(len(ver)), "verified": int(ver["verified"].sum()),
                              "fail_reasons": ver.loc[~ver["verified"], "reason"].value_counts().head(10).to_dict()},
        "results": {k: {kk: vv for kk, vv in v.items() if kk not in {"per_name"}} for k, v in results.items()},
        "accuracy_by_expert_confidence": strat,
        "clusters_scored": int(cl["unit_id"].nunique()),
        "clusters_top1_is_taxon": int((top["taxon_key"] != NONE).sum()),
        "mean_top1_probability_clusters": round(float(top["p"].mean()), 4),
        "clusters_low_candidate_coverage": int(cl.groupby("unit_id")["low_candidate_coverage"].first().sum()),
    }
    log.info(json.dumps({k: summary[k] for k in ("gold_names_evaluated", "temperature", "clusters_scored")}))
    write_stage_report("identify", summary)
    (REPORTS / "stages" / "identify_per_name.json").write_text(
        json.dumps({k: v.get("per_name") for k, v in results.items() if "per_name" in v}, ensure_ascii=False, indent=1), encoding="utf-8")
    return {k: summary[k] for k in summary if k not in {"results"}} | {
        "headline": {k: {m: results[k][m] for m in ("top1", "brier", "ece") if m in results[k]} for k in results if "top1" in results[k]}}
