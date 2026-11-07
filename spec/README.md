# Pharmakon — Project Specification Pack

**Pharmakon** is an uncertainty-aware, 2,000-year map of Greek and Byzantine pharmacology. It is built for the EthnoHack 2026 data hackathon (Track 1: Traditional knowledge).

This folder is a complete specification for an AI coding agent (Claude Code) or a human team to build the project end to end. It contains no code. It explains *what* to build, *why*, *from which real data*, and *how to prove it works*.

## One-sentence pitch

An AI system that:
1. reads ancient Greek and Byzantine pharmacological texts;
2. works out which modern plant each ancient name most likely refers to, **with a calibrated probability**;
3. traces each remedy across 2,000 years (Dioscorides → Galen → Paul of Aegina → Byzantine texts → modern Greek folk medicine);
4. tests, with a strict time split, whether remedies that persisted are the ones modern science later supported;
5. carries identification uncertainty into every drug-discovery lead it proposes.

## How to use this pack with Claude Code

1. Create an empty repository (e.g. `pharmakon/`) and copy this whole folder into it as `spec/`.
2. Copy `spec/CLAUDE.md` to the repository root as `CLAUDE.md`. Claude Code reads it automatically.
3. Start Claude Code in the repo and say:
   > Read every file in `spec/` in numeric order. Then execute `spec/09_BUILD_PLAN.md` phase by phase. Stop at the end of each phase, show me the acceptance-check results, and wait for my go-ahead.
4. Keep the human in the loop at every phase gate. The gates exist because some data sources must be checked by a person (licences, downloads, expert audit samples).

## File index (read in this order)

| File | What it covers |
|---|---|
| `CLAUDE.md` | Operating rules for the coding agent: no fabrication, provenance, testing, style |
| `01_PROJECT_OVERVIEW.md` | Problem, hypotheses, novelty, hackathon fit, judging-criteria mapping |
| `02_LITERATURE_REVIEW.md` | What prior work did, what it lacks, how we build on it (with links) |
| `03_DATA_SOURCES.md` | Every dataset and API: URL, licence, access method, fields, caveats |
| `04_ARCHITECTURE.md` | System design, repository layout, data model and knowledge-graph schema |
| `05_PIPELINE_SPEC.md` | Stage-by-stage specification with inputs, outputs, algorithms, prompts |
| `06_IDENTIFICATION_MODEL.md` | The core novelty: probabilistic plant identification and calibration |
| `07_EVALUATION_PLAN.md` | Gold sets, metrics, the temporal backtest, baselines, statistics, audits |
| `08_APP_SPEC.md` | The interactive explorer (screens, components, behaviour) |
| `09_BUILD_PLAN.md` | Phased plan with tasks and acceptance criteria for every phase |
| `10_RESPONSIBLE_RESEARCH.md` | Ethics, licences, disclaimers, safety, attribution |
| `11_SUBMISSION_KIT.md` | Devpost page, 10-slide outline, pitch-video script, README skeleton |
| `12_RISKS_AND_FALLBACKS.md` | What can go wrong and the fallback for each risk |
| `REFERENCES.md` | Consolidated reference list with links and DOIs |

## Verification status of facts in this pack

Facts were checked against live sources on 7 November 2026 where marked **[verified]**. Items marked **[VERIFY]** are plausible but were not confirmed. The agent must confirm them before relying on them (see `CLAUDE.md`, rule 3).
