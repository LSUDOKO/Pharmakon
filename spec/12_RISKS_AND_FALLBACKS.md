# 12 — Risks and Fallbacks

| # | Risk | Likelihood | Impact | Detection | Fallback |
|---|---|---|---|---|---|
| R1 | Galen *De simpl. med.* not available as clean digital Greek | Medium | Medium | Phase 0 check | Use Kühn scans + Greek OCR on books 6–8 only, with spot-checks; or drop Galen and keep DMM → JC → modern |
| R2 | Paul of Aegina book 7 not digitised | Medium | Low | Phase 0 | Use Lardos JC as the Byzantine node; mention Paul as future work |
| R3 | First1KGreek TEI contains apparatus residue | High | Medium | Stage 1 residue flag | Regex cleaning + a manual sample; extraction prompt told to ignore sigla; span verification still uses the stored text |
| R4 | LLM misreads rare Greek vocabulary | Medium | High | Extraction audit | Prompt v2 with glossary hints (LSJ glosses injected for headwords); restrict to chapters with audit precision ≥0.85; report residual error |
| R5 | Lardos data licence unclear or files differ from description | Low | High | Phase 0 | Contact the authors; meanwhile use their open-access paper tables (CC BY) for the gold names and identities |
| R6 | Gold set too small (50 names) for a stable model | Medium | Medium | Wide CIs | Keep the model low-parameter (conditional logit); report CIs; add Staub identities as a secondary agreement check; use a Bayesian version for uncertainty |
| R7 | GBIF fuzzy matches create wrong taxa | Medium | Medium | Unit tests on known names | Require EXACT or FUZZY ≥90 confidence plus kingdom Plantae plus a rank check; manual review list for FUZZY |
| R8 | PubMed proxy labels are noisy | High | High | Label audit | Report precision; use the stricter label variant; include MeSH-restricted queries; frame results with the audit numbers |
| R9 | Too few positive labels per cutoff | Medium | High | Dataset stats | Pool cutoffs; widen to 2 domains; use AUPRC with CIs; switch to a survival-style model (time to first support) |
| R10 | Open Targets lacks historical versions → temporal leakage | High | Medium | Design review | Sensitivity analysis without OT-dependent features; use ChEMBL doc year and LOTUS reference year (which are dated) as main chemistry features |
| R11 | LOTUS SPARQL timeouts | Medium | Low | Phase 0 | Use the LOTUS frozen dump (Zenodo, via lotus.naturalproducts.net) **[VERIFY]**, or batch queries per genus |
| R12 | Flora of Greece no bulk export | Medium | Low | Phase 0 | Polite per-taxon queries for candidates only; or GBIF country=GR as a presence proxy |
| R13 | Modern study tables are in PDF only | Medium | Low | Phase 5 | Camelot/pdfplumber + manual correction + 10% double-check |
| R14 | Copy dependence between texts inflates persistence | High | Medium | n-gram overlap | Down-weight copies; report persistence with and without Galen/Paul |
| R15 | Results are null | Possible | Low (if framed well) | Phase 6 | Present as a scientific finding with diagnostics; identification and persistence results still stand |
| R16 | Cost/latency of LLM calls | Low | Low | Token logs | Cache everything; use a small model for prefiltering and a larger model for extraction on the pilot only |
| R17 | Toxic plants surface as top leads | High | Medium | Toxicity flag | Badge plus explicit discussion; never present as recommendations |

## Decision log
Record every fallback taken in `docs/decisions.md` with date, reason and consequence for claims.
