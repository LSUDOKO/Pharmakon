# 01 — Project Overview

## 1. The problem

Greek and Byzantine pharmacological texts are among the largest and longest-running written records of plant medicine. *De materia medica* (Dioscorides, 1st c. CE) describes roughly 600 plants. It was used and rewritten for more than 1,500 years. Turning these texts into drug-discovery hypotheses is blocked by three problems.

1. **Identification uncertainty.** An ancient name such as *ἀψίνθιον* or *πάνακες* does not map cleanly to one modern species.
   - Most studies take a single identification from a dictionary.
   - Lardos et al. (2024) showed such identifications are often questionable. They proposed a manual, confidence-scored method instead.
   - No automated system propagates that uncertainty downstream.
2. **No diachronic view at scale.**
   - Whether a remedy persisted from antiquity to modern folk medicine has been studied manually: single families or single species, or curated tables (Leonti et al. 2015; Mir et al. 2026; Smaili et al. 2026).
   - It has not been studied computationally across a chain of texts.
3. **No honest test of predictive value.**
   - Computational "herb–disease" models are usually evaluated with random splits, which leak information.
   - Strict temporal validation is now standard in drug-repurposing knowledge graphs (Abo-Dahab et al. 2026) and in discovery forecasting (Hakken 2026; Dyport 2023).
   - It has not been applied to historical materia medica.

## 2. What Pharmakon does

| Layer | Output |
|---|---|
| Corpus | Public-domain Greek editions, segmented to chapter and passage level with CTS URNs |
| Extraction | Structured claims (substance, part, preparation, route, condition) with verbatim Greek spans |
| Identification | For each ancient plant name, a calibrated probability distribution over modern species |
| Linking | Species → compounds (COCONUT/LOTUS) → targets (ChEMBL) → diseases (Open Targets/MeSH) |
| Persistence | For each (plant, condition-category) claim, whether it survives, changes or disappears across texts up to modern Greek ethnobotany |
| Backtest | Does persistence (plus chemistry) predict which claims later gained pharmacological support? Tested with a strict time split |
| Leads | Ranked hypotheses whose scores are weighted by identification probability, shown with uncertainty and conservation status |
| Explorer | An app for historians and pharmacognosists to inspect every step, from Greek passage to evidence path |

## 3. Research questions and hypotheses

- **RQ1 — Identification.** Can an automated, evidence-combining model reproduce expert plant identifications for a Byzantine text, with calibrated confidence?
  - **H1:** It beats a single-dictionary baseline and a zero-shot LLM baseline on top-1 accuracy and calibration (Brier score, ECE) against the Lardos et al. gold set.
- **RQ2 — Persistence.** Which ancient plant–use claims persist into modern Greek folk medicine, and does persistence depend on plant part, condition category or chemosensory properties?
- **RQ3 — Forecasting.** With a cutoff year *T*, do persistence and pre-*T* chemistry predict which plant–condition pairs first receive pharmacological support after *T*?
  - **H3:** They add predictive value beyond a research-popularity baseline (PubMed volume before *T*).
  - A null result is reported as honestly as a positive one.
- **RQ4 — Uncertainty matters.** Does weighting leads by identification probability change the ranking materially? How many "top leads" rest on low-confidence identifications?

## 4. Pilot scope (recommended)

Do not try to cover all of medicine at once. Pilot domain: **skin conditions and wounds** (dermatological uses). Reasons:
- Staub et al. (2016) note that dermatological uses (e.g. Fabaceae seeds) are prominent in *De materia medica*.
- Judges Tsioutsiou, Cheilari & Aligiannis (2023) published an ethnopharmacological study of plants used against skin ailments on Mount Pelion. It gives a modern Greek endpoint in exactly this domain.
- Topical uses are more plausible pharmacologically and easier to map to MeSH (wounds, eczema, burns, ulcers, infections).

Then expand to a second domain (e.g. gastrointestinal) only once the pilot is complete.

## 5. Text chain (diachronic backbone)

| Period | Source | Role |
|---|---|---|
| 1st c. CE | Dioscorides, *De materia medica* (Wellmann ed.) | Anchor text, richest morphology |
| 2nd c. CE | Galen, *De simplicium medicamentorum temperamentis ac facultatibus*, books 6–8 (plants; Kühn ed.) | Early transmission |
| 7th c. CE | Paul of Aegina, *Epitome*, book 7 (simples; Heiberg ed., CMG IX) | Byzantine compilation |
| 13th c. CE | John the Physician, *Therapeutics* (via Lardos et al. 2024 data) | Late Byzantine; also the identification gold set |
| 16th–20th c. | Cypriot iatrosophia (Lardos et al. 2011), optional | Post-Byzantine |
| 1990s–2020s | Modern Greek ethnobotanical field studies (Axiotis et al. 2018; Tsioutsiou et al. 2023; Perouli & Bareka 2022; others) | Modern endpoint |

## 6. Why this fits EthnoHack

**Track 1 match.** The organisers describe Track 1 as using NLP to extract medicinal knowledge from historical texts, mapping plant names across eras, and connecting ancient knowledge to modern pharmacology. Pharmakon is that description, implemented.

**Judging criteria mapping**

| Criterion | How Pharmakon addresses it |
|---|---|
| Scientific relevance | A recognised open problem (plant identity in historical texts) plus a falsifiable forecasting hypothesis |
| Innovation | First automated probabilistic identification with uncertainty carried downstream, across a multi-text Greek chain |
| Technical implementation | Reproducible CLI pipeline, cached, tested, documented, with open data only |
| Data science quality | Expert gold set, calibration metrics, strict temporal split, popularity baseline, bootstrap CIs, label audit |
| Feasibility | Pilot domain; modular design that extends to Arabic, Latin and Ayurvedic corpora |
| Impact | Prioritises candidates for lab screening; supports traditional-use dossiers; flags conservation risk for Greek flora |
| Presentation | Explorer app shows every step from Greek passage to evidence path |

**Judge expertise alignment (useful for framing, not flattery).**
- A historian of Byzantine pharmacology (Bouras-Vallianatos): text chain, philology.
- Pharmacognosists (Aligiannis, Cheilari): natural-product layer, modern Greek ethnobotany.
- A data-management and mining expert (Gunopulos): pipeline, data quality.
- A biomedical data intelligence researcher at Fraunhofer SCAI (Ay): knowledge graph, validation.

**Prize targets:** Track 1 first prize; Best Scientific Rigor; Best AI Solution; Best Student Team (if eligible).

## 7. Non-goals

- No clinical recommendations, dosing or self-treatment guidance.
- No claims that an ancient identification is "solved". We report probabilities and evidence.
- No new critical edition of any Greek text.
