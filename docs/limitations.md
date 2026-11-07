# Limitations

Written as they were discovered during the build (CLAUDE.md, definition of done).

## Data and texts
- **Edition and encoding.** The Dioscorides text is the First1KGreek encoding of Wellmann. 207 chapter divs are wrongly nested and 8 chapter numbers are reused in the TEI. Both are handled (nested chapters are parsed on their own, and duplicates are disambiguated as `NdupK`), but the chapter boundaries still inherit OCR and encoding errors.
- **Residual apparatus.** About 1.2% of passages still carry possible apparatus residue (sigla, Latin runs, editorial brackets). These passages are flagged, not deleted.
- **Synonym lists.** The `RV:` synonym lists are later additions (Popa 2010). They are stored as flagged variants and are never used as identification evidence.
- **Text chain.** Galen (*De simpl. med.* books 6–8) is included. Paul of Aegina is not, because no TEI was found (fallback R2). The 13th-century node is John the Physician, taken only through the 50 plants that Lardos et al. analysed.
- **Galen crosswalk.** Galen's genitive headings are matched to Dioscorides headwords by stem. Homonymous drug names can be mismatched, and 137 of 476 Galen entries are unmapped.
- **Modern endpoint coverage.** The modern endpoint combines the Lardos herbal/ethnobotanical references for their candidate plants with two field studies. The Mount Pelion study covers skin ailments only, which inflates modern attestation of dermatological uses (DE).

## Extraction
- **Two extractors.** `rule_extract_v1` (Greek condition lexicon × clause segmentation, exact spans) is merged with LLM extraction done in an interactive Claude session (`llm_extract_v1:claude-opus-5-5-session`, prompt `extract_v1`, committed as `data/llm/claims_session*.jsonl`). Session outputs are not temperature-0 API calls and cannot be regenerated bit-for-bit; they are committed instead, and the pipeline re-verifies every span on every run.
- **Merge policy.** LLM claims only enter the tables through the lexicon: their condition words must match a lexicon stem, so MeSH codes still come only from the NLM-verified map. LLM claims outside the lexicon are archived in `interim/claims_llm_out_of_lexicon.parquet`. Rule claims without a therapeutic cue (`ambiguous`) become `ok` only when the LLM reads the same passage and condition as a use (`llm_confirmed`).
- **LLM-proposed lexicon extension.** `config/conditions_lexicon_llm.yaml` adds stems proposed from frequent out-of-lexicon LLM conditions (bites of scorpions, spiders, dogs and snakes; achores; burns; sprains; haemorrhage; epilepsy spellings …). Every MeSH label was verified by exact lookup, but the stems and glosses are an LLM proposal awaiting the human condition-mapping audit. Ambiguous single-word stems (κοιλι-, φλεγμ-, καθαιρ-, ῥευματ-, φακ-) were deliberately not added.
- **Judgement calls inside LLM extraction.** The annotators kept deliberate abortifacient, contraceptive and some veterinary uses, and a few uses Dioscorides reports as hearsay; they excluded cosmetic, culinary and pest-repellent uses. A few amulet uses stated as remedies were kept in one batch and excluded in others. Headword errors in the TEI were corrected from the passage text and flagged in `uncertain_fields`.
- **Backtest isolation.** None of the above reaches the temporal backtest: it reads only `rule_extract_v1` claims with their original status (`forecast.run.rule_claims`) and pairs flagged `from_rule_claims`.
- **Glosses.** The condition glosses are deliberately cautious. Ancient categories such as λέπρα, ἕρπης and γλαύκωμα have no modern equivalent and carry `mesh_ids=[]`.
- **Human audit pending.** The extraction, condition, merge and label audits are generated as blinded CSV sheets but have **not yet been filled in by a human**. No audited precision figure is claimed, for either extractor.

## Identification
- **Gold standard.** The gold is the expert judgement of Lardos et al. (61 Dioscorides names / 50 JC lemmas), not ground truth. The confidence intervals are wide.
- **Morphology feature (f1).** Dioscorides' description is turned into a 14-trait record in a Claude session (prompt `morph_greek_v1`, candidate species never shown), and each candidate species' English Wikipedia description into the same record with Groq `openai/gpt-oss-120b` (prompt `morph_species_v1`). Every trait keeps a verbatim span that is re-verified. Coverage is thin: Dioscorides often describes only uses, many species pages are stubs, and some leaf shapes are read from similes ("leaves like the olive's"), which uses the annotator's knowledge of the comparison plant. Kew POWO, the preferred modern source, refuses automated clients (HTTP 403) and was not used. The expert-coded trait congruence still appears only in a labelled ORACLE ablation.
- **LLM judge.** The spec/06 Option C baseline (Groq, Greek chapter + candidate list) is comparison-only: a modern LLM may have memorised published identifications, so its agreement with experts is not evidence of independent skill.
- **Calibration.** Calibration is below target: ECE 0.21 after temperature scaling, against a target of ≤ 0.10. The model clearly beats the LSJ dictionary baseline on top-1 and Brier.
- **Two models.** The full model uses Lardos literature counts, which exist only for gold names. All other Dioscorides names are scored with the *transfer* model, which drops those features (top-1 0.56 vs 0.62).
- **Unverifiable candidates.** 146 candidate names could not be verified in the GBIF backbone and were dropped (rule R7): 144 LSJ regex hits (old synonyms such as *Quercus aegilops* or *Statice limonium*, plus non-plant English word pairs) and 2 Lardos names. Names whose only candidates were dropped fall entirely on ∅.
- **Distribution data.** Geographic plausibility uses GBIF occurrence counts for GR/CY/TR (aggregated counts only), as a proxy for Flora of Greece.

## Chemistry and disease
- **Compounds.** Compounds come from LOTUS on Wikidata, not the COCONUT dump (disk budget). Reference years come from the Wikidata scholarly subgraph.
- **Pilot caps.** Activity look-ups are capped at 15 compounds per taxon (the earliest documented) and 120 taxa.
- **Targets.** Only human single-protein targets are linked. Antimicrobial (organism) targets are not mapped to infections.
- **Open Targets dates.** Open Targets associations are current, not historical. The backtest therefore reports a sensitivity model without the OT-dependent feature.

## Labels and backtest
- **Proxy labels.** Evidence labels are a **PubMed co-mention proxy** (species in title/abstract + MeSH condition + pharmacology filter):
  - GBIF synonyms are not added to the query;
  - the stricter in-vivo/clinical label variant is not implemented; a ≥2-paper variant is.
- **Scope of the backtest.** Two scopes are reported. The skin/wound pilot (default `config/pilot.yaml`, 400 pairs; archived in `reports/scope_pilot/`) and all body systems (`PHARMAKON_SCOPE=all`, `config/scope_all.yaml`). Both use only pairs supported by deterministic pre-LLM claims and the frozen non-LLM identification (`id_posterior_nollm.parquet`). Positives per cutoff stay small; results are reported for every cutoff with cluster-bootstrap CIs.

## Leads
- **What leads use.** Leads may use LLM-derived evidence (merged claims, the f1 morphology feature in P(species)); the scoring model is the backtest's logistic model refitted at the last cutoff. Each lead also keeps its frozen, non-LLM P(species) (`p_species_frozen`) for comparison.
- **Conservation status.** Conservation status is Wikidata P141 (no IUCN token).
- **Toxicity flags.** Each toxicity flag cites a PubChem GHS record for a marker compound. That record supports "known toxic constituent", not a clinical toxicity assessment of the plant.
