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
- **No LLM.** No `ANTHROPIC_API_KEY` was available, so extraction is the deterministic `rule_extract_v1`: Greek condition lexicon × clause segmentation. This gives exact spans (100% verified), with two costs:
  - recall is limited to the lexicon;
  - plant part and route are inherited from the preceding clause when the current clause lacks them (flagged in `uncertain_fields`).
- **Ambiguous clauses.** A condition word with no therapeutic cue is marked `ambiguous` rather than `ok`. Some real uses expressed with unlisted verbs are therefore under-counted.
- **Glosses.** The condition glosses are deliberately cautious. Ancient categories such as λέπρα, ἕρπης and γλαύκωμα have no modern equivalent and carry `mesh_ids=[]`.
- **Human audit pending.** The extraction, condition, merge and label audits are generated as blinded CSV sheets but have **not yet been filled in by a human**. No audited precision figure is claimed.

## Identification
- **Gold standard.** The gold is the expert judgement of Lardos et al. (61 Dioscorides names / 50 JC lemmas), not ground truth. The confidence intervals are wide.
- **No morphology feature.** Morphology (f1) is not computed, because the Greek trait extractor needs an LLM. The expert-coded trait congruence appears only in a labelled ORACLE ablation, since the gold verdict was derived from it.
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
- **Scope of the backtest.** The backtest pairs are capped at 400 (skin/wound pilot, highest P(species) first), and the positives per cutoff are few. Results are reported for every cutoff with cluster-bootstrap CIs.

## Leads
- **Conservation status.** Conservation status is Wikidata P141 (no IUCN token).
- **Toxicity flags.** Each toxicity flag cites a PubChem GHS record for a marker compound. That record supports "known toxic constituent", not a clinical toxicity assessment of the plant.
