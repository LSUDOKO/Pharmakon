# Phase 10 — LLM layer and all-body-system scope

Done after the pilot (phases 0–9). Every number below is in `reports/stages/*.json`; the pilot's stage files are archived in `reports/scope_pilot/`.

## What was added
- **LLM backends.** Groq (`openai/gpt-oss-120b`, temperature 0, JSON schema, hash-keyed cache) and an interactive Claude session (`claude-opus-5-5`) whose outputs are committed under `data/llm/` with prompt version and model, and re-verified by `python -m pharmakon.llm_session check …`.
- **LLM claim extraction** for all 1,158 in-scope Dioscorides passages, merged with `rule_extract_v1` under a verify-first policy (`extract/merge_llm.py`).
- **LLM-proposed lexicon extension** (`config/conditions_lexicon_llm.yaml`): stems from frequent out-of-lexicon LLM conditions, MeSH verified by exact lookup.
- **f1 morphology feature** (spec/06): Dioscorides trait records (Claude session, candidates hidden) vs English Wikipedia species descriptions (Groq for 121 species, Claude session for the rest); spans verified on both sides.
- **LLM-judge baseline** (spec/06 Option C): Claude session, Greek chapter + candidate list, no access to gold or model outputs.
- **All body systems** (`PHARMAKON_SCOPE=all`): chemistry for 300 taxa, PubMed labels for 1,999 pairs.

## Integrity controls
- The temporal backtest uses only `rule_extract_v1` claims with their pre-LLM status, pairs flagged `from_rule_claims`, and the frozen non-LLM posterior `id_posterior_nollm.parquet` (CLAUDE.md rule 6). Tested in `tests/test_llm_layer.py`.
- Every LLM span was re-verified: 0 span mismatches in claims, Greek traits and species traits.
- POWO refuses automated clients (HTTP 403); not circumvented, recorded in `docs/source_verification.md`.
- Human audits remain pending and were not done by a model.

## Acceptance checks
- `make test`: 27 tests pass (3 new). `ruff` clean.
- `mypy --strict` on `identify/` reports 28 errors (24 pre-existing); not yet fixed.
- Live site, JSON API and MCP server redeployed and checked (6 tools, JSON-RPC over HTTP).

## Results in one line each
- Identification: f1 lowers calibration error from 0.21 to 0.14 (main model) and lifts transfer-model top-1 from 0.56 to 0.59; the LLM judge reaches top-1 0.59 (comparison only).
- Backtest (all body systems, 3× more positives): popularity dominates; adding history never helps and at the 2005 cutoff hurts (ΔAUPRC CI below zero).
- Leads: 1,781 untested pairs; 16 of the top 20 now have a closed compound → target → disease path.
