# 10 — Responsible Research

EthnoHack requires respect for licences, intellectual property, privacy, traditional knowledge, scientific integrity and appropriate interpretation of computational predictions. It also requires that unvalidated findings are never presented as medical facts. This file turns those requirements into concrete rules.

## 1. Medical safety
- **Disclaimer** (README, app banner, slides, video): *"Pharmakon generates research hypotheses from historical texts and open databases. Nothing here is medical advice, a recommendation to use any plant, or evidence of safety or efficacy."*
- **No dosing.** Do not extract or display doses as recommendations. If quantities appear in a Greek span, they appear only inside the quoted historical text.
- **Toxicity flags.** Maintain `config/toxic_taxa.yaml`: a curated list of genera/species with well-known serious toxicity that occur in Dioscorides, e.g. *Aconitum, Conium, Hyoscyamus, Mandragora, Atropa, Datura, Colchicum, Veratrum, Helleborus, Euphorbia* (latex), *Nerium, Digitalis, Ricinus, Aristolochia* (aristolochic acids), *Papaver somniferum*. Cite a source per entry (e.g. a toxicology reference or Wikidata/PubChem hazard statements).
  - Flagged leads show a red "Known toxicity" badge and cannot be sorted to the top without the badge visible.
- **Language discipline.** Use "associated with", "candidate", "hypothesis", "supported in the literature (proxy)". Never use "cures", "treats" or "proven".

## 2. Interpretation of predictions
- Every probability shown has an explanation and an uncertainty band.
- Evidence labels are a **PubMed co-mention proxy**. Report audited label precision next to every forecasting result.
- Report negative and null results with equal prominence.

## 3. Cultural and traditional knowledge
- The historical corpus is public-domain written heritage. No community-held Indigenous knowledge is extracted from living informants by this project.
- Modern Greek field studies are published, peer-reviewed works. Use their published tables only, cite them, and do not re-identify informants. Aggregate to species/use level.
- Acknowledge that modern folk knowledge belongs to the communities documented. Include a statement that any future commercial development based on leads derived from modern community knowledge should follow access-and-benefit-sharing principles (Nagoya Protocol) and engage the documenting researchers and communities.

## 4. Licences and attribution
- Keep a `docs/licences.md` table: source, licence, attribution text, what we redistribute (raw / derived / none).
- Redistribution policy:
  - **CC0** (COCONUT, LOTUS, Wikidata): derived tables may be redistributed.
  - **CC BY / CC BY-SA** (First1KGreek, Lardos data — verify): attribute; derived Greek text tables inherit share-alike if applicable.
  - **ChEMBL (CC BY-SA)**: derived target tables inherit share-alike.
  - **GBIF occurrences**: redistribute counts only, not records.
  - **IUCN**: do not redistribute raw data; show status only, with attribution, under their terms.
  - **Copyrighted translations**: never stored.
- Machine translations of Greek are our own outputs. Label them "machine translation — check against a scholarly edition".

## 5. Responsible use of AI
- Log model name, version, prompt version and temperature for every LLM output.
- Cache and publish (in the repo) the prompts used.
- LLMs never generate identifiers (codes, IDs, DOIs). All such values are verified by lookup.
- Discuss known LLM limitations with ancient Greek (rare words, apparatus noise, anachronistic glosses) in `docs/limitations.md`.

## 6. Privacy
- No personal data is processed. Modern studies are used at an aggregate level.

## 7. Scientific integrity checklist (tick before submission)
- [ ] Every headline number traces to a report file.
- [ ] Gold-set caveat (expert judgement ≠ ground truth) stated.
- [ ] Label-precision audit reported.
- [ ] Leakage controls documented and the shuffled control reported.
- [ ] All cutoffs reported; no cherry-picking.
- [ ] Limitations section written.
- [ ] Toxicity flags present in the app and leads table.
- [ ] Licences table complete.
