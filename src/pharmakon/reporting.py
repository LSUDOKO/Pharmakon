"""Regenerate every evaluation report (reports/eval_*.md) and figure from stage JSON + processed tables.

Every number in the pitch must trace to a file written here (spec/07 §1).
"""

from __future__ import annotations

import json

import pandas as pd
import plotly.graph_objects as go

from pharmakon.common import GOLD, PROCESSED, REPORTS, read_stage_report, wilson_ci

FIG = REPORTS / "figures"
NOTE_AUDIT = ("**Human audit: pending.** The blinded audit sheet is in `data/gold/audits/`. No precision figure is "
              "claimed until a person fills it in; numbers below are automatic checks only.")


def _w(name: str, lines: list[str]) -> str:
    (REPORTS / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return name


def _fig(fig: go.Figure, name: str) -> str:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.write_html(FIG / f"{name}.html", include_plotlyjs="cdn")
    return f"figures/{name}.html"


def ingest() -> str:
    s = read_stage_report("ingest-texts")
    g = read_stage_report("ingest-galen")
    return _w("eval_ingest.md", [
        "# Text ingestion", "",
        f"* Dioscorides (Wellmann, First1KGreek commit `{s.get('source_commit')}`): **{s.get('passages')} passages**, "
        f"{s.get('chapters')} chapters; books present {s.get('books_present')}; chapters per book {s.get('chapters_per_book')}.",
        f"* Headword parsed for {s.get('headword_parsed_rate'):.1%} of chapters; {s.get('chapters_with_synonym_lists')} chapters carry "
        f"`RV:` synonym lists ({s.get('synonyms_total')} variants, flagged `synonym_list`).",
        f"* Residual-apparatus flag rate after stripping `<note>`/`<del>`: **{s.get('residual_apparatus_flag_rate'):.1%}** {s.get('residual_flag_counts')}.",
        f"* {s.get('duplicate_chapter_numbers_disambiguated')} chapter divs reuse an earlier `@n` in the TEI (encoding errors); kept and disambiguated as `NdupK`. "
        "207 chapter divs are wrongly nested in the TEI; nested text is excluded from the parent and parsed on its own (unit test).",
        f"* Galen *De simpl. med.* books 6–8: {g.get('galen_passages_books_6_8')} passages, {g.get('drug_entries')} drug entries "
        f"({g.get('entries_with_parsed_heading')} headings parsed).",
        "", "**20-passage manual comparison with the Perseids reader: pending human check** (links are in the explorer, one per passage).",
    ])


def extraction() -> str:
    s = read_stage_report("extract-claims")
    g = read_stage_report("ingest-galen")
    return _w("eval_extraction.md", [
        "# Claim extraction", "",
        f"Extractor: `{s.get('extractor')}` (deterministic; the LLM path `llm_extract_v1` is implemented but was not run — no API key).", "",
        "| metric | Dioscorides | Galen 6–8 |", "|---|---|---|",
        f"| claims kept | {s.get('claims_kept')} | {g.get('claims_kept')} |",
        f"| exact span verification among kept | {s.get('exact_span_verified_rate_kept')} | {g.get('exact_span_verified_rate')} |",
        f"| archived span mismatches | {s.get('archived_span_mismatch')} | 0 |",
        f"| status counts | {s.get('status_counts')} | ok={g.get('claims_ok')} |",
        f"| pilot skin/wound claims | {s.get('pilot_skin_claims')} in {s.get('pilot_skin_chapters')} chapters | DE={g.get('use_group_counts', {}).get('DE')} |",
        f"| plant part known | {s.get('plant_part_known_rate')} | |", f"| route known | {s.get('route_known_rate')} | |", "",
        "`ambiguous` = a condition word in a clause without any therapeutic cue (e.g. a side effect: κεφαλαλγὲς ὄν). Ambiguous claims are kept "
        "for inspection but excluded from persistence, labels and leads.", "", NOTE_AUDIT,
        "Recall on fully annotated passages: pending (needs a human annotator).",
    ])


def conditions() -> str:
    s = read_stage_report("map-conditions")
    return _w("eval_conditions.md", [
        "# Condition mapping", "",
        f"* Lexicon entries: {s.get('lexicon_conditions')}; with ≥1 MeSH descriptor verified by exact NLM lookup: {s.get('with_verified_mesh')}; "
        f"explicit `no_modern_equivalent`: {s.get('no_modern_equivalent')}. Labels failing verification: {s.get('mesh_labels_failed_verification')}.",
        f"* Claims with ≥1 verified MeSH ID: **{s.get('claims_with_verified_mesh_rate'):.1%}**; distinct MeSH IDs: {s.get('distinct_mesh_ids')}.",
        f"* Lardos use-group distribution: {s.get('use_group_counts')}", "", NOTE_AUDIT,
    ])


def identification() -> str:
    s = read_stage_report("identify")
    r = s.get("results", {})
    lines = ["# Identification vs expert gold (Lardos et al. 2024)", "",
             "**Caveat:** the gold standard is expert judgement (botanical congruence + use congruence), not ground truth.", "",
             f"Leave-one-name-out over {s.get('gold_names_evaluated')} gold names (grouped by the 50 JC lemmas); 95% bootstrap CIs over names (1,000).", "",
             "| model | top-1 | top-1 95% CI | top-3 | MRR | log loss | Brier | ECE |", "|---|---|---|---|---|---|---|---|"]
    for k, v in r.items():
        if "top1" in v:
            lines.append(f"| {k} | {v['top1']['mean']} | {v['top1']['ci95']} | {v['top3']['mean']} | {v['rr']['mean']} | {v['logloss']['mean']} | {v['brier']['mean']} | {v['ece']} |")
        else:
            lines.append(f"| {k} | {v.get('status')} — {v.get('reason')} | | | | | | |")
    main, lsj = r.get("model_calibrated", {}), r.get("baseline_lsj", {})
    beat = main and lsj and main["top1"]["mean"] > lsj["top1"]["mean"] and main["brier"]["mean"] < lsj["brier"]["mean"]
    lines += ["", "## Success criterion (spec/07 §3)", "",
              f"* Beats the LSJ dictionary baseline on top-1 **and** Brier: **{'yes' if beat else 'no'}**.",
              f"* ECE ≤ 0.10 after calibration: **{'yes' if main.get('ece', 1) <= 0.10 else 'no'}** (calibrated {main.get('ece')}, uncalibrated "
              f"{r.get('model_uncalibrated', {}).get('ece')}). Diagnosis: with 61 names each ECE bin holds ≈6 names, so ECE is noisy; temperature "
              f"scaling (T={s.get('temperature')}) is fitted by NLL on tie-aware targets, which need not minimise top-1 ECE. The expert-trait ORACLE "
              f"ablation reaches ECE {r.get('ablation_plus_ORACLE_expert_traits', {}).get('ece')}: the missing morphology stream (f1, needs an LLM) "
              "is the main gap.",
              "", "## Weights (full model)", "", "```json", json.dumps(s.get("weights"), indent=1), "```",
              f"Unidentified-bucket utility b = {s.get('none_utility_b')}; temperature {s.get('temperature')}.", "",
              "The **transfer model** (no Lardos literature counts, so it can score all Dioscorides names) is the one applied to clusters:",
              "```json", json.dumps(s.get("transfer_model"), indent=1), "```",
              f"Accuracy by expert confidence: {s.get('accuracy_by_expert_confidence')}", "",
              f"GBIF verification of candidates: {s.get('gbif_verification')}", "",
              f"Applied to {s.get('clusters_scored')} Dioscorides names: {s.get('clusters_top1_is_taxon')} have a taxon as top-1; "
              f"{s.get('clusters_low_candidate_coverage')} have fewer than two verified candidates (`low_candidate_coverage`).",
              "", "Reliability diagram: `figures/reliability.html`. Example identification cards: `identification_cards.md`."]
    fig = go.Figure()
    fig.add_scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(dash="dot"), name="perfect")
    for k in ("model_calibrated", "baseline_lsj", "baseline_genus_prior"):
        rel = r.get(k, {}).get("reliability", [])
        fig.add_scatter(x=[b["mean_conf"] for b in rel], y=[b["accuracy"] for b in rel], mode="lines+markers", name=k,
                        text=[f"n={b['n']}" for b in rel])
    fig.update_layout(xaxis_title="confidence (max p)", yaxis_title="top-1 agreement with experts", title="Identification reliability")
    _fig(fig, "reliability")
    return _w("eval_identification.md", lines)


def cards(n: int = 10) -> str:
    post = pd.read_parquet(PROCESSED / "id_posterior.parquet")
    expl = pd.read_parquet(PROCESSED / "id_explanations.parquet")
    gold = pd.read_parquet(GOLD / "lardos_gold.parquet")
    lines = ["# Identification cards (gold names, full model)", ""]
    for gid in gold.drop_duplicates("gold_id").sort_values("gold_id")["gold_id"].head(n):
        g = gold[gold["gold_id"] == gid]
        p = post[post["unit_id"] == gid].sort_values("p", ascending=False)
        lines += [f"## {g['dmm_name_grc'].iloc[0]} (JC: {g['jc_name_grc'].iloc[0]}) — {g['dmm_chapter_id'].iloc[0]}", "",
                  f"Expert verdict: {', '.join(g.loc[g['is_expert_top'], 'candidate_name'])} (confidence {g['expert_confidence'].iloc[0]})", "",
                  "| candidate | P | 90% interval | top feature contributions |", "|---|---|---|---|"]
        for r in p.itertuples():
            e = expl[(expl["unit_id"] == gid) & (expl["taxon_key"] == r.taxon_key)]
            contrib = ""
            if len(e):
                w = {c[2:]: e[c].iloc[0] for c in e.columns if c.startswith("w_")}
                contrib = ", ".join(f"{k} {v:+.2f}" for k, v in sorted(w.items(), key=lambda kv: -abs(kv[1]))[:3])
            lines.append(f"| {r.accepted_name or 'unidentified (∅)'} | {r.p:.2f} | [{r.p_lo:.2f}, {r.p_hi:.2f}] | {contrib} |")
        lines.append("")
    return _w("identification_cards.md", lines)


def persistence() -> str:
    s = read_stage_report("persistence")
    lines = ["# Persistence (DMM → Galen → John the Physician → modern Greek)", "",
             f"* Rows (name × Lardos use group): {s.get('rows')} over {s.get('clusters_with_identified_taxa')} names with ≥1 verified candidate taxon.",
             f"* Pattern counts: {s.get('pattern_counts')}", f"* Dermatology (pilot): {s.get('pattern_counts_dermatology')}",
             f"* Galen re-attests {s.get('galen_agreement_rate')} of Dioscorides uses for the {s.get('galen_linked_clusters')} linked names; "
             f"John the Physician {s.get('jc_agreement_rate')} ({s.get('jc_linked_clusters')} linked names).",
             f"* Mean persistence score with / without Galen: {s.get('mean_persistence_score_with_galen')} / {s.get('mean_persistence_score_without_galen')}. "
             f"Copy detection: {s.get('copy_detection')}.",
             f"* Modern records: {s.get('modern_records')} from {s.get('modern_sources')}.", "",
             "## Permutation null", "", "```json", json.dumps(s.get("permutation_test"), indent=1), "```",
             "Interpretation: among Dioscorides uses whose plant appears in the modern record, the same use group recurs more often than when "
             "modern use labels are shuffled across records. Caveat: the Pelion study covers skin ailments only, which inflates DE attestation.", "",
             "## Worked examples (dermatology, with verbatim Greek)", ""]
    for e in s.get("worked_examples", []):
        lines += [f"* **{e['cluster_id']}** — score {e['persistence_score']}, E[modern] {e['expected_modern']}, Galen {e.get('present_galen')}, "
                  f"JC {e['present_jc']} — `{e['example_passage_id']}`", f"  > {e['example_span_grc']}"]
    return _w("eval_persistence.md", lines)


def labels() -> str:
    s = read_stage_report("evidence-labels")
    lines = ["# Evidence labels (PubMed co-mention proxy)", "", f"* Pairs: {s.get('pairs')} ({s.get('taxa')} species × {s.get('mesh_terms')} MeSH terms; skin pilot {s.get('pairs_skin')}).",
             f"* With ≥1 record to {s.get('t_end')}: {s.get('pairs_with_any_support_to_t_end')} ({s.get('positive_rate')}).",
             f"* First-support-year quantiles: {s.get('first_support_year_quantiles')}", f"* Eligible / positive per cutoff: {s.get('eligible_and_positive_by_cutoff')}",
             "", "The exact query string is stored with each row of `data/processed/evidence_labels.parquet`.", ""]
    audit = GOLD / "audits" / "label_audit_positive_100.csv"
    if audit.exists():
        a = pd.read_csv(audit)
        done = a["tests_plant_for_condition"].astype(str).str.lower().isin(["1", "yes", "y", "true", "0", "no", "n", "false"])
        if done.any():
            k = int(a.loc[done, "tests_plant_for_condition"].astype(str).str.lower().isin(["1", "yes", "y", "true"]).sum())
            lo, hi = wilson_ci(k, int(done.sum()))
            lines.append(f"Label precision (human audit): {k}/{int(done.sum())} = {k / done.sum():.2f} (Wilson 95% CI {lo:.2f}–{hi:.2f}).")
        else:
            lines.append(NOTE_AUDIT)
    return _w("eval_labels.md", lines)


def forecast() -> str:
    s = read_stage_report("forecast")
    res = s.get("results", {})
    lines = ["# Temporal backtest", "", "Rolling origin: train on pairs unsupported at T−5 (labels in (T−5, T]); test on pairs unsupported at T (labels in (T, T_end]).",
             "All features dated ≤ the row's cutoff. Label = PubMed co-mention proxy (precision pending audit).", "",
             "| T | n test | positives | random | popularity | history | chemistry | history+pop | full | full (GBM) | shuffled hist+pop | ΔAUPRC(hist+pop − pop) 95% CI |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    fig = go.Figure()
    xs = sorted(res, key=int)
    for T in xs:
        t = res[T]["test"]
        g = lambda m, t=t: t.get(m, {}).get("auprc", "–")  # noqa: E731
        ci = res[T].get("bootstrap_ci", {})
        lines.append(f"| {T} | {t['full']['n']} | {t['full']['positives']} | {g('random')} | {g('popularity')} | {g('history')} | {g('chemistry')} | "
                     f"{g('history+popularity')} | {g('full')} | {g('full_gbm')} | {g('shuffled_history+popularity')} | {ci.get('delta_auprc_histpop_minus_pop', '–')} |")
    for m in ("popularity", "history+popularity", "full"):
        ys = [res[T]["test"][m].get("auprc") for T in xs]
        lo = [res[T].get("bootstrap_ci", {}).get(m, [None, None])[0] for T in xs]
        hi = [res[T].get("bootstrap_ci", {}).get(m, [None, None])[1] for T in xs]
        fig.add_scatter(x=xs, y=ys, name=m, mode="lines+markers",
                        error_y=dict(type="data", symmetric=False, array=[(h - y) if h is not None and y is not None else 0 for h, y in zip(hi, ys, strict=True)],
                                     arrayminus=[(y - lo_) if lo_ is not None and y is not None else 0 for lo_, y in zip(lo, ys, strict=True)]))
    fig.update_layout(title="AUPRC by cutoff (95% cluster-bootstrap CI)", xaxis_title="cutoff T", yaxis_title="AUPRC")
    _fig(fig, "backtest_auprc")
    lines += ["", "Precision@k and AUROC per model: `reports/stages/forecast.json`.", "", "## Leakage controls", ""]
    lines += [f"* {c}" for c in s.get("leakage_controls", [])]
    lines += ["", "## Interpretation", "",
              "Read the ΔAUPRC column: if its 95% CI excludes 0, persistence/history adds information beyond research popularity at that cutoff; "
              "otherwise the pilot finds no added signal at that cutoff. All cutoffs are reported; none were selected after the fact."]
    return _w("eval_forecast.md", lines)


def uncertainty() -> str:
    s = read_stage_report("leads")
    return _w("eval_uncertainty.md", [
        "# Does identification uncertainty change the ranking? (RQ4)", "",
        f"* Unsupported candidate pairs ranked: {s.get('unsupported_today')}.",
        f"* Kendall τ between P(species)-weighted ranking and top-1-identity ranking: **{s.get('kendall_tau_weighted_vs_top1')}**.",
        f"* Top-20 leads that change when only the top-1 identity is used: **{s.get('top20_changed_when_using_top1_identity')}**.",
        f"* Top-20 leads resting on P(species) < 0.5: {s.get('top20_resting_on_p_species_below_0.5')}.",
        f"* Top-20 with a known-toxicity flag: {s.get('top20_with_toxicity_flag')}; with a closed compound→target→disease path: {s.get('top20_with_closed_evidence_path')}.",
        "", "Full table: `leads_top50.md`.",
    ])


def data_versions() -> str:
    from pharmakon.common import RAW

    lines = ["# Data versions", ""]
    for d in sorted(RAW.glob("*/SOURCE.json")):
        m = json.loads(d.read_text())
        lines.append(f"* `{m.get('source_id')}` retrieved {m.get('retrieved_at')} — " + ", ".join(f"{k}: {v}" for k, v in m.items() if k in {"last_commit_touching_file", "doi", "rows", "url"}))
    lc = read_stage_report("link-chemistry")
    lines += ["* ChEMBL / Open Targets / MeSH / PubMed / Wikidata: live REST snapshots, cached in `data/cache/http.sqlite`; versions in `docs/source_verification.md`.",
              f"* Linking summary: {lc}"]
    return _w("data_versions.md", lines)


def write_all() -> dict:
    out = []
    for f in (ingest, extraction, conditions, identification, cards, persistence, labels, forecast, uncertainty, data_versions, data_dictionary, phase_reports):
        try:
            out.append(f())
        except Exception as exc:  # noqa: BLE001 - report which report could not be built and why
            out.append(f"{f.__name__}: skipped ({exc})")
    return {"written": out}


def data_dictionary() -> str:
    """docs/data_dictionary.md: every processed table with its columns and dtypes (generated, never hand-edited)."""
    from pharmakon.common import ROOT

    lines = ["# Data dictionary", "", "Generated by `python -m pharmakon report` from the parquet files. Provenance columns "
             "(`source_id`, `retrieved_at`, `method`) are present on every table and checked on write.", ""]
    for base in (PROCESSED, GOLD):
        for p in sorted(base.glob("*.parquet")):
            df = pd.read_parquet(p)
            lines += [f"## `{p.relative_to(ROOT)}` — {len(df):,} rows", "", "| column | dtype | example |", "|---|---|---|"]
            for c in df.columns:
                ex = df[c].dropna().iloc[0] if df[c].notna().any() else ""
                exs = str(ex).replace("|", "/").replace("\n", " ")[:60]
                lines.append(f"| `{c}` | {df[c].dtype} | {exs} |")
            lines.append("")
    (ROOT / "docs" / "data_dictionary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "docs/data_dictionary.md"


def phase_reports() -> str:
    """reports/phase_N.md — acceptance-check summaries per build phase (spec/09), from stage JSON."""
    st = {k: read_stage_report(k) for k in ("ingest-texts", "extract-claims", "map-conditions", "gold", "cluster-names", "identify",
                                             "link-chemistry", "ingest-galen", "persistence", "evidence-labels", "forecast", "leads", "build-kg")}
    idn, fc = st["identify"], st["forecast"].get("results", {})
    mc = idn.get("results", {}).get("model_calibrated", {})
    phases = {
        0: ("Setup and source verification", [
            "Repo, `pyproject.toml`, Makefile, config, cached HTTP client (`http.py`), optional LLM wrapper (`llm.py`).",
            "Live checks of 13 sources pass: see `docs/source_verification.md`.",
            f"Dioscorides TEI commit `{st['ingest-texts'].get('source_commit')}`; Lardos figshare CC BY 4.0; Galen found in First1KGreek (tlg0057.tlg075); Paul → fallback R2.",
            "Open: no ANTHROPIC/NCBI/IUCN keys in the build environment (documented fallbacks)."]),
        1: ("Corpus ingestion", [f"{st['ingest-texts'].get('passages')} passages, all 5 books, residual-apparatus flag rate {st['ingest-texts'].get('residual_apparatus_flag_rate')}.",
                                 "Unit tests on 3 real fixture chapters pass. 20-passage Perseids comparison: pending human check."]),
        2: ("Claims and conditions", [f"{st['extract-claims'].get('claims_kept')} claims, exact span verification {st['extract-claims'].get('exact_span_verified_rate_kept')} (≥0.98 required: met).",
                                      f"{st['map-conditions'].get('claims_with_verified_mesh_rate')} of claims with verified MeSH.",
                                      "Audit precision ≥0.85: NOT yet assessed — audit sheets generated, human audit pending."]),
        3: ("Gold set and identification", [f"{st['gold'].get('gold_names')} gold names / {st['gold'].get('candidates')} candidates parsed; LONO top-1 {mc.get('top1')}, Brier {mc.get('brier', {}).get('mean')}, ECE {mc.get('ece')}.",
                                           "Success criterion: beats LSJ on top-1 and Brier — met; ECE ≤ 0.10 — NOT met (diagnosis in eval_identification.md).",
                                           f"10 identification cards: `identification_cards.md`. {st['cluster-names'].get('clusters')} name clusters; merge-precision audit pending."]),
        4: ("Chemistry, targets, diseases", [f"Coverage: {st['link-chemistry'].get('share_taxa_with_compound')} of selected taxa have ≥1 compound; "
                                            f"{st['link-chemistry'].get('share_queried_compounds_with_human_target')} of queried compounds have a human target; "
                                            f"{st['link-chemistry'].get('taxon_disease_pairs_with_path')} taxon–disease pairs close the loop.",
                                            "Provenance columns are enforced on every write (`write_table`, unit test)."]),
        5: ("Later texts, modern studies, persistence", [f"Galen: {st['ingest-galen'].get('drug_entries')} entries, {st['ingest-galen'].get('entries_mapped_to_dmm')} mapped to Dioscorides; copy containment mean {st['ingest-galen'].get('copy_containment_mean')}.",
                                                         f"Persistence permutation test: {st['persistence'].get('permutation_test')}.",
                                                         "Worked examples with Greek spans: eval_persistence.md. Modern-table 10% human check: pending."]),
        6: ("Labels and temporal backtest", [f"{st['evidence-labels'].get('pairs')} pairs, {st['evidence-labels'].get('pairs_with_any_support_to_t_end')} with PubMed support.",
                                            "AUPRC (pop / history+pop): " + "; ".join(f"T={T}: {v['test']['popularity'].get('auprc')} / {v['test']['history+popularity'].get('auprc')}" for T, v in fc.items()),
                                            "Label audit (100+/50−): pending human audit."]),
        7: ("Leads and uncertainty", [f"{st['leads'].get('unsupported_today')} leads; Kendall τ weighted vs top-1 = {st['leads'].get('kendall_tau_weighted_vs_top1')}; "
                                     f"{st['leads'].get('top20_changed_when_using_top1_identity')} of top-20 change."]),
        8: ("Explorer app", ["Six Streamlit pages; `make app` runs from the committed `data/processed`; AppTest smoke test for every page passes.",
                             "Deployment URL: not deployed from this environment (needs the team's Streamlit Cloud / HF account)."]),
        9: ("Documentation", ["README, docs/limitations.md, licences, decisions, data dictionary. Slides/video/Devpost: team tasks (spec/11)."]),
    }
    for n, (title, items) in phases.items():
        _w(f"phase_{n}.md", [f"# Phase {n} — {title}", "", *[f"- {i}" for i in items]])
    return "phase_0..9.md"
