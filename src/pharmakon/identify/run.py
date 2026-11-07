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


def baseline_llm_judge(feats: pd.DataFrame, units_df: pd.DataFrame, units: list[Unit]) -> tuple[dict[str, np.ndarray], dict]:
    """spec/06 Option C: the LLM sees the Greek chapter and the candidate list, returns probabilities.

    Comparison only: it cannot be validated independently and may have memorised published identifications.
    """
    from pharmakon import llm
    from pharmakon.schemas import JudgeOutput

    ch = pd.read_parquet(PROCESSED / "dmm_chapters.parquet").set_index("chapter_id")
    cl = units_df.set_index("unit_id")["cluster_id"].to_dict()
    preds, meta, fails = {}, {}, []
    session = PROCESSED.parent / "llm" / "judge_session.jsonl"
    if session.exists():  # Claude-session judge (committed; prompt judge_v1)
        got_all = {(d := json.loads(x))["unit_id"]: d for x in session.read_text(encoding="utf-8").splitlines() if x.strip()}
        for u in units:
            names = feats.loc[feats["unit_id"] == u.uid, "accepted_name"].tolist()
            d = got_all.get(u.uid)
            if d is None:
                fails.append(u.uid)
                continue
            got = {c["candidate"].strip(): max(0.0, float(c["p"])) for c in d.get("probabilities", [])}
            p = np.array([got.get(n, 0.0) for n in names] + [max(0.0, float(d.get("p_none_of_these", 0)))], dtype=float) + 1e-6
            preds[u.uid] = p / p.sum()
        method = next(iter(got_all.values()), {}).get("method", "judge_v1:claude-session")
        return preds, {"provider": "claude-session", "model": method, "prompt_version": "judge_v1", "failed_units": fails}
    for u in units:
        names = feats.loc[feats["unit_id"] == u.uid, "accepted_name"].tolist()
        cid = str(cl.get(u.uid, "")).removeprefix("cl:")
        if cid not in ch.index:
            fails.append(u.uid)
            continue
        text = str(ch.loc[cid, "text_grc"])[:2500]  # Greek is token-dense; keep request + reply under Groq's 8k tokens/min
        user = (f"Dioscorides, De materia medica {cid.removeprefix('dmm:')}:\n\n{text}\n\nCandidates:\n"
                + "\n".join(f"- {n}" for n in names))
        try:
            res, meta = llm.structured("judge_v1", user, JudgeOutput, max_tokens=2000, effort="medium")
        except Exception:  # noqa: BLE001 — counted below, never silently dropped
            fails.append(u.uid)
            continue
        got = {c.candidate.strip(): max(0.0, c.p) for c in res.probabilities}
        p = np.array([got.get(n, 0.0) for n in names] + [max(0.0, res.p_none_of_these)], dtype=float) + 1e-6
        preds[u.uid] = p / p.sum()
    return preds, {"provider": meta.get("provider"), "model": meta.get("model"), "prompt_version": "judge_v1", "failed_units": fails}


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
    # f1 morphology (LLM-extracted traits, spans verified). Only used when Greek traits exist.
    from pharmakon.identify import morphology as M

    morph_stats: dict = {"status": "not_run", "reason": f"{M.GREEK_OUT} missing"}
    if M.GREEK_OUT.exists():
        f1, morph_stats = M.build_f1(feats, units)
        feats["f1_morph"] = f1.to_numpy()
    use_f1 = "f1_morph" in feats and bool(cfg.get("identify_use_morphology", False))
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
    from pharmakon import llm

    if llm.available() or (PROCESSED.parent / "llm" / "judge_session.jsonl").exists():
        jp, jmeta = baseline_llm_judge(feats, units, gold_units)
        ju = [u for u in gold_units if u.uid in jp]
        results["baseline_llm_judge"] = summarise(jp, ju, seed, n_boot) | {"meta": jmeta}
    else:
        results["baseline_llm_judge"] = {"status": "not_run", "reason": "no LLM key (spec/06 Option C is comparison-only)"}
    if "f1_morph" in feats:
        u_f1 = _units(feats, ys, MAIN + ["f1_morph"])
        results["model_plus_f1_morphology"] = summarise(lono(u_f1, groups), u_f1, seed, n_boot)
        u_tf1 = _units(feats, ys, TRANSFER + ["f1_morph"])
        results["transfer_plus_f1_morphology"] = summarise(lono(u_tf1, groups), u_tf1, seed, n_boot)
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

    kinds = units.set_index("unit_id")["unit_kind"].to_dict()

    def posterior(main_cols: list[str], transfer_cols: list[str], tag: str) -> tuple[pd.DataFrame, list[dict], CLogit, CLogit]:
        final, boots = fit_final(_units(feats, ys, main_cols), groups, seed)
        final_tr, boots_tr = fit_final(_units(feats, ys, transfer_cols), groups, seed)
        mv, tv = MODEL_VERSION + tag, TRANSFER_VERSION + tag
        post_rows, expl_rows = [], []
        for uid, grp in feats.groupby("unit_id", sort=False):
            gold_unit = kinds.get(uid) == "gold"
            cols, mdl, bts = (main_cols, final, boots) if gold_unit else (transfer_cols, final_tr, boots_tr)
            X = grp[cols].to_numpy(float)
            p = mdl.predict(X)
            bs = np.array([b.predict(X) for b in bts])
            lo, hi = np.percentile(bs, 5, axis=0), np.percentile(bs, 95, axis=0)
            contrib = mdl.contributions(X)
            version = mv if gold_unit else tv
            low_cov = len(grp) < 2
            for j, r in enumerate(grp.itertuples()):
                post_rows.append({"unit_id": uid, "taxon_key": r.taxon_key, "accepted_name": r.accepted_name, "family": r.family, "genus": r.genus,
                                  "p": float(p[j]), "p_lo": float(min(lo[j], p[j])), "p_hi": float(max(hi[j], p[j])),
                                  "low_candidate_coverage": low_cov, "model_version": version})
                expl_rows.append({"unit_id": uid, "taxon_key": r.taxon_key, "model_version": version,
                                  **{f"w_{c}": (float(contrib[j, cols.index(c)]) if c in cols else 0.0) for c in ALLF},
                                  **{c: float(getattr(r, c)) for c in ALLF if hasattr(r, c)}, "candidate_sources": list(r.candidate_sources),
                                  "input_names": list(r.input_names), "lit_ref_years": list(r.lit_ref_years)})
            post_rows.append({"unit_id": uid, "taxon_key": NONE, "accepted_name": None, "family": None, "genus": None,
                              "p": float(p[-1]), "p_lo": float(min(lo[-1], p[-1])), "p_hi": float(max(hi[-1], p[-1])),
                              "low_candidate_coverage": low_cov, "model_version": version})
        have = set(feats["unit_id"])
        for u in units.to_dict("records"):
            if u["unit_id"] not in have:
                post_rows.append({"unit_id": u["unit_id"], "taxon_key": NONE, "accepted_name": None, "family": None, "genus": None,
                                  "p": 1.0, "p_lo": 1.0, "p_hi": 1.0, "low_candidate_coverage": True, "model_version": "no_verified_candidates"})
        post = pd.DataFrame(post_rows)
        post = post.merge(units[["unit_id", "unit_kind", "cluster_id"]], on="unit_id", how="left")
        post["calibrated"] = post["model_version"] != "no_verified_candidates"
        post["source_id"], post["retrieved_at"] = "pharmakon_identify", ts
        post["method"] = post["model_version"].map({mv: f"{mv}:T={final.T:.3f}", tv: f"{tv}:T={final_tr.T:.3f}"}).fillna("no_verified_candidates")
        return post, expl_rows, final, final_tr

    ts = now_iso()
    ALLF = MAIN + (["f1_morph"] if "f1_morph" in feats else [])
    # Frozen non-LLM posterior: the only one the temporal backtest may use (CLAUDE.md rule 6).
    post_nollm, expl_nollm, final0, final0_tr = posterior(MAIN, TRANSFER, "")
    write_table(post_nollm, PROCESSED / "id_posterior_nollm.parquet")
    if use_f1:
        post, expl_rows, final, final_tr = posterior(MAIN + ["f1_morph"], TRANSFER + ["f1_morph"], "+f1")
        main_used, tr_used = MAIN + ["f1_morph"], TRANSFER + ["f1_morph"]
    else:
        post, expl_rows, final, final_tr = post_nollm, expl_nollm, final0, final0_tr
        main_used, tr_used = MAIN, TRANSFER
    write_table(post, PROCESSED / "id_posterior.parquet")
    expl = pd.DataFrame(expl_rows)
    expl["source_id"], expl["retrieved_at"], expl["method"] = "pharmakon_identify", ts, MODEL_VERSION
    write_table(expl, PROCESSED / "id_explanations.parquet")
    cand_out = feats.drop(columns=["vernacular_el"]).copy()
    write_table(cand_out, PROCESSED / "id_candidates.parquet")

    cl = post[post["unit_kind"] == "cluster"]
    top = cl.sort_values("p", ascending=False).groupby("unit_id").head(1)
    summary = {
        "model_version": MODEL_VERSION + ("+f1" if use_f1 else ""),
        "features": {c: (F.FEATURES[c] if c in F.FEATURES else "morphological agreement: Dioscorides' description vs the species' Wikipedia description (LLM-extracted traits, spans verified)") for c in main_used},
        "weights": {c: round(float(w), 4) for c, w in zip(main_used, final.w, strict=True)},
        "none_utility_b": round(final.b, 4),
        "temperature": round(final.T, 4),
        "uses_morphology": use_f1,
        "morphology": morph_stats,
        "frozen_non_llm_model": {"weights": {c: round(float(w), 4) for c, w in zip(MAIN, final0.w, strict=True)}, "temperature": round(final0.T, 4),
                                 "note": "id_posterior_nollm.parquet; the only posterior the temporal backtest uses"},
        "transfer_model": {"features": tr_used, "weights": {c: round(float(w), 4) for c, w in zip(tr_used, final_tr.w, strict=True)},
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
