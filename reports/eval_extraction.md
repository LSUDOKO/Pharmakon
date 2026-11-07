# Claim extraction

Extractor: `rule_extract_v1` (deterministic; the LLM path `llm_extract_v1` is implemented but was not run — no API key).

| metric | Dioscorides | Galen 6–8 |
|---|---|---|
| claims kept | 3696 | 1033 |
| exact span verification among kept | 1.0 | 1.0 |
| archived span mismatches | 0 | 0 |
| status counts | {'ok': 3550, 'ambiguous': 146} | ok=799 |
| pilot skin/wound claims | 1417 in 413 chapters | DE=448 |
| plant part known | 0.6347 | |
| route known | 0.6475 | |

`ambiguous` = a condition word in a clause without any therapeutic cue (e.g. a side effect: κεφαλαλγὲς ὄν). Ambiguous claims are kept for inspection but excluded from persistence, labels and leads.

**Human audit: pending.** The blinded audit sheet is in `data/gold/audits/`. No precision figure is claimed until a person fills it in; numbers below are automatic checks only.
Recall on fully annotated passages: pending (needs a human annotator).
