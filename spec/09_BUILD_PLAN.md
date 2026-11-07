# 09 — Build Plan (phases, tasks, acceptance criteria)

Work strictly phase by phase. At each gate:
1. run the acceptance checks;
2. write `reports/phase_N.md` (what was done, numbers, failures, open questions);
3. stop for human review.

Rough effort assumes a team of 2–4. Phases 1–3 and 5 can run in parallel by different people once Phase 0 is done.

---

## Phase 0 — Setup and source verification
**Tasks**
- Initialise the repo:
  - `uv init`; dependencies from `04_ARCHITECTURE.md` §5; `ruff`, `pytest`, `pre-commit`;
  - `Makefile`, `config/`, `.env.example`, `docs/`.
- Implement `http.py` (cache, retries, rate limits) and `llm.py` (Anthropic client, JSON-schema output, cache, prompt versioning).
- Work through the `03_DATA_SOURCES.md` download checklist. Resolve every **[VERIFY]** item needed for the pilot.
- Write `docs/source_verification.md`.

**Acceptance**
- `make setup && make test` passes on a clean machine.
- Dioscorides TEI present (commit hash recorded).
- Lardos files downloaded, licence recorded.
- COCONUT dump present.
- Test calls to GBIF, ChEMBL, Open Targets, PubMed, Wikidata SPARQL and LOTUS succeed and are cached.
- Decision recorded for Galen and Paul: digital text found, or the fallback chosen.

---

## Phase 1 — Corpus ingestion (Stage 1)
**Tasks:** TEI parser with apparatus stripping, segmenter, `passages.parquet`, unit tests on 3 fixture chapters.

**Acceptance:** criteria from `05_PIPELINE_SPEC.md` Stage 1; `reports/eval_ingest.md`.

---

## Phase 2 — Claim extraction and condition mapping (Stages 2–3)
**Tasks**
- Pydantic schemas; prompt `extract_v1`; span verifier; pilot prefilter.
- Run on the pilot scope (~books 1–4, skin/wound chapters first).
- Condition mapping with MeSH verification.
- Generate audit sheets. A human audits them.

**Acceptance**
- ≥98% exact span verification among kept claims.
- Audit precision ≥0.85 on substance/part/condition (or a documented diagnosis plus prompt v2).
- `reports/eval_extraction.md`, `reports/eval_conditions.md`.

---

## Phase 3 — Gold set and identification model (Stages 4–5)
**Tasks**
- Parse Lardos files 2, 3, 5, 6, 9, 10, 11 into `data/gold/lardos_*.parquet`. Map candidates to GBIF keys.
- Name clustering and crosswalk.
- Candidate generation (LSJ parser, Lardos, optional Staub, LLM proposals) with GBIF verification.
- Features f1–f4, f6. Trait-schema prompt `traits_v1` for both ancient and modern descriptions.
- Conditional logit with ∅ alternative; LONO CV; calibration; baselines; bootstrap.
- Apply to all pilot names → `id_posterior.parquet`.

**Acceptance**
- `reports/eval_identification.md` with a metrics table, reliability diagram and ablations.
- The success criterion from `07_EVALUATION_PLAN.md` §3 is met, or the shortfall is explained.
- 10 example identification cards rendered as Markdown.

---

## Phase 4 — Linking chemistry, targets, diseases (Stage 6)
**Tasks**
- COCONUT/LOTUS linkers (with reference years); ChEMBL linker (with doc years); Open Targets linker.
- Path assembly and tiering.
- Unit tests with 3 well-known taxa (e.g. *Hypericum perforatum*, *Salvia officinalis*, *Pistacia lentiscus*) to sanity-check counts.

**Acceptance**
- The coverage table is reported (share of taxa with ≥1 compound; share of compounds with ≥1 target; share of paths that close the loop).
- No identifiers are written without an API/file origin (a test asserts provenance columns are non-null).

---

## Phase 5 — Later texts, modern studies, persistence (Stages 7–8)
**Tasks**
- Ingest Galen (books 6–8) and Paul (book 7), or their fallbacks, through Stages 1–3.
- Ingest Lardos JC uses.
- Ingest modern Greek studies (Pelion, North Aegean, Milos at minimum) with a human-checked 10% sample.
- Copy detection (Greek n-gram overlap) to down-weight Galen/Paul passages that copy Dioscorides.
- Persistence table and patterns; permutation null.

**Acceptance**
- `reports/eval_persistence.md` with counts by pattern and ICPC chapter, the permutation test result and 5 worked examples (with Greek spans).

---

## Phase 6 — Evidence labels and temporal backtest (Stages 9–10)
**Tasks**
- PubMed query builder; per-year counts; first_support_year; label audit (100+/50−).
- Forecast dataset per cutoff with strict ≤ *T* features.
- Models, baselines, rolling-origin evaluation, bootstrap, DeLong; shuffled-history control.

**Acceptance**
- `reports/eval_labels.md` (label precision with CI).
- `reports/eval_forecast.md` with all cutoffs, all baselines, CIs and leakage controls.
- Figures 5–6 from `07_EVALUATION_PLAN.md` §5.

---

## Phase 7 — Leads and uncertainty analysis (Stage 11)
**Tasks:** current ranking; P(species) weighting; conservation and toxicity flags; rank-sensitivity analysis.

**Acceptance:** `reports/leads_top50.md`; `reports/eval_uncertainty.md` (Kendall τ, count of top-20 changes).

---

## Phase 8 — Explorer app (Stage 12)
**Tasks:** pages 1–6 from `08_APP_SPEC.md`; sample dataset; deployment.

**Acceptance**
- The app runs from a fresh clone with the sample data via `make app`.
- The deployed URL works on desktop and phone.
- Every number on the Home page comes from report JSON.

---

## Phase 9 — Documentation and submission
**Tasks**
- `README.md`: problem, data, method, results, limitations, how to reproduce, licences, citation.
- `docs/limitations.md` final pass.
- Slides and video per `11_SUBMISSION_KIT.md`.
- Devpost page.

**Acceptance**
- A teammate reproduces all figures with `make reproduce` from cached raw data.
- The submission checklist in `11_SUBMISSION_KIT.md` is fully ticked.

---

## Scope tiers (if time is short, cut from the bottom)

| Tier | Includes |
|---|---|
| **MVP** | Dioscorides only + Lardos JC + 2 modern studies; identification model with gold evaluation; persistence (DMM→JC→modern); chemistry links; explorer pages 2, 3, 6 |
| **Core** | + PubMed labels + temporal backtest + leads + pages 4, 5 |
| **Full** | + Galen + Paul + copy detection + Bayesian identification + conservation layer |
| **Stretch** | + second domain (gastrointestinal) + Neo4j export + Arabic transmission via GlossGA metadata |
