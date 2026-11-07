# CLAUDE.md — Operating rules for building Pharmakon

You are building **Pharmakon**, a research-grade data pipeline and explorer app (see `spec/01_PROJECT_OVERVIEW.md`). The output will be judged by pharmacognosists, a historian of Byzantine pharmacology and data scientists. Scientific integrity matters more than features.

## Non-negotiable rules

1. **Never fabricate data, identifiers or citations.**
   - Do not invent species names, PubMed IDs, ChEMBL IDs, InChIKeys, DOIs, URNs, page numbers or Greek text.
   - Every identifier written to disk must come from an API response, a downloaded file or a verified lookup, and must carry provenance.
2. **Every extracted claim needs a verbatim evidence span.**
   - A claim extracted from a historical text must include the exact Greek substring and its CTS URN / passage reference.
   - Run a substring check (Unicode NFC, whitespace-normalised) against the source passage. Claims that fail are archived with `status="span_mismatch"`, never silently kept.
3. **Unverified sources.** When a spec file marks something **[VERIFY]**, confirm it before you build on it:
   - Check that the URL resolves, the licence permits use, and the data has the stated fields.
   - Record the result in `docs/source_verification.md`.
   - If a source cannot be confirmed, stop and tell the human. Propose the fallback from `spec/12_RISKS_AND_FALLBACKS.md`.
4. **Provenance on everything.** Each row in each processed table carries:
   - `source_id` (from `spec/03_DATA_SOURCES.md`)
   - `retrieved_at` (ISO timestamp)
   - `method` (e.g. `llm_extract_v1`, `gbif_match`, `manual_gold`)
   - `confidence` where applicable
5. **LLMs propose; databases and humans verify.** LLMs may extract, normalise and propose candidates. They must not be the final authority for:
   - taxonomic names (verify against GBIF/WFO);
   - disease codes (verify against MeSH/MONDO by exact or synonym match);
   - compound identities (verify via InChIKey from COCONUT/LOTUS/PubChem).
   Use the "generate-then-verify" pattern (see `spec/05_PIPELINE_SPEC.md`).
6. **No outcome leakage into the temporal backtest.**
   - Features used in the backtest may only use information dated on or before the cutoff year.
   - LLM outputs must never be used as a plausibility score in the backtest: modern LLMs have read the modern literature.
   - See `spec/07_EVALUATION_PLAN.md` §4.
7. **No medical claims.**
   - The app and README must state that outputs are research hypotheses, not medical advice.
   - Flag toxic taxa (see `spec/10_RESPONSIBLE_RESEARCH.md`).
8. **Respect licences.**
   - Do not copy copyrighted modern translations (e.g. Beck 2005/2017, Osbaldeston 2000) into the repo.
   - Use the public-domain Greek editions and our own machine translations, clearly labelled.
9. **Phase gates.** Work through `spec/09_BUILD_PLAN.md` one phase at a time. At the end of each phase:
   - run its acceptance checks;
   - write `reports/phase_N.md` with the results;
   - stop for human review.

## Engineering conventions

- **Language:** Python 3.11+. Package manager: `uv` (fallback: `pip` + `venv`).
- **Layout:** `src/pharmakon/...` as defined in `spec/04_ARCHITECTURE.md`.
- **Storage:** Parquet files plus a DuckDB catalogue (`data/pharmakon.duckdb`). Graph views are built with NetworkX. Neo4j export is optional.
- **Config:** `config/*.yaml`. Secrets in `.env`: `ANTHROPIC_API_KEY`, `NCBI_API_KEY`, `NCBI_EMAIL`, `IUCN_TOKEN`. Never commit `.env`.
- **HTTP:**
  - one shared client with on-disk caching (`requests-cache` or `hishel`), retries with exponential backoff, and polite rate limits;
  - NCBI: ≤10 req/s with an API key, ≤3 without;
  - Wikidata SPARQL: set a descriptive User-Agent.
- **LLM calls:**
  - temperature 0;
  - JSON-schema-constrained output (Pydantic models in `src/pharmakon/schemas.py`);
  - cache every request/response pair by hash in `data/cache/llm/`;
  - log the model name and prompt version.
- **Determinism:** fixed random seeds. Every pipeline stage is a CLI command (`python -m pharmakon <stage>`) and is idempotent and resumable.
- **Tests:** `pytest`. Each stage has unit tests on small fixtures in `tests/fixtures/`. Run tests before closing a phase.
- **Quality:** `ruff` for lint and format; type hints throughout; `mypy --strict` on `schemas.py` and `identify/`.
- **Notebooks:** only for exploration and figures, in `notebooks/`. Logic lives in `src/`.
- **Logging:** structured logs (JSON lines) in `logs/`. Every stage prints a summary of counts in, counts out, failures and reasons.

## Definition of done for any stage

- The CLI command runs from a clean checkout after `make data` (or the documented download step).
- Output tables have documented schemas in `docs/data_dictionary.md`.
- Tests pass and failure cases are counted and reported, not hidden.
- Limitations are written down in `docs/limitations.md` as they are discovered.

## When unsure

Ask the human. Prefer a smaller, verified result over a larger, unverified one.
