# 02 — Literature Review and Gap Analysis

The review was compiled from searches across SciSpace, alphaXiv and the open web on 7 November 2026. Full citations are in `REFERENCES.md`.

## A. Identification of plants in historical texts

**Lardos et al. 2024, *J. Ethnopharmacology* 322:117622 [verified].**
- **What they did:**
  - Developed a six-stage interdisciplinary methodology to assess the identity of plants named in John the Physician's *Therapeutics* (13th c. Byzantine).
  - Applied it to 50 plant names (corresponding to 61 Dioscorides plants) and 130 candidate species.
  - Compared Dioscorides' morphological descriptions with modern descriptions; compared historical with modern medicinal uses; added statistical evaluation.
  - Each suggested identity gets a measure of confidence.
- **Licence:** CC BY 4.0 paper.
- **Data:** research data on Royal Holloway figshare (doi:10.17637/rh.23736189.v1). It includes:
  - plant names in John the Physician and Dioscorides;
  - Dioscorides plant descriptions;
  - candidate lists with MPNS validation;
  - modern plant descriptions;
  - PubMed and clinical-trial data;
  - botanical and medicinal comparative analyses;
  - statistical evaluation.
- **Gap:** fully manual and expert-intensive; does not scale; uncertainty is not carried into downstream chemistry.
- **How we use it:** as the **gold standard** for evaluating the automated identification model (`07_EVALUATION_PLAN.md`), and as a design template for features.

**Zipser, Lardos, Lazarou et al. 2023, *Wellcome Open Research*.**
- Multi-layer tagging of pharmaceutical terms with confidence factors for translations (Ioannes Archiatrus).
- **Use:** model for representing confidence per term.

**Zipser et al. 2023, *Studia Ceranea* — "Pharmaceutical terminology… andrachne, chrysocolla".**
- Argues most ancient plant and mineral names cannot be identified with high certainty.
- **Use:** motivation for reporting distributions, not single answers.

**Fillies et al. 2025 — "Historic to FAIR: LLMs for historic term identification".**
- GPT-4 achieved high detection and identification rates for historical biodiversity terms.
- **Gap:** general biodiversity records, not ancient Greek pharmacology; no calibration.

**El Haff et al. 2024 — NER resource for ancient (Abbasid) pharmacopeias.** Works on English translations; shows NER transfer issues across translators.

**Sharma et al. 2017 (AMIA); Sharma et al. 2019 (Solr-Plant, *BMC Bioinformatics*).** Plant-name extraction and fuzzy resolution from historical/biomedical text.

## B. Quantitative studies of Dioscorides and the Greek tradition

**Staub, Casu & Leonti 2016, *Phytomedicine* 23(10):1043–52, PMID 27444350 [verified].**
- Line-by-line survey of *De materia medica* (Matthioli 1568 version).
- Database of **5,314 unique therapeutic uses of 536 plant taxa and 924 herbal drugs**.
- Fields: chapter, putative botanical identity, plant part, symptom/disease, mode of administration, biomedical interpretation, organ/symptom category.
- **Use:** an independent comparison set for extraction recall and for candidate identities, if obtainable from the paper's supplement or the authors **[VERIFY availability]**.

**Leonti et al. 2015, *Frontiers in Pharmacology* — "From cumulative cultural transmission to evidence-based medicine".**
- Southern Italy: relates the classical written record to contemporary use and evidence.
- **Use:** closest conceptual precedent for RQ3. We differ by automation, a multi-text chain, identification uncertainty and a strict temporal split.

**Leonti et al. 2024, *eLife* — "Taste shaped the use of botanical drugs".** Chemosensory qualities predict Graeco-Roman therapeutic uses (phylogenetic GLMMs). **Use:** optional covariate and discussion point.

**Leonti et al. 2026, *J. Ethnopharmacology* — systemic vs topical use by plant organ and chemosensory properties in *De materia medica*.** **Use:** supports our plant-part field and topical pilot domain.

**Mir et al. 2026; Smaili et al. 2026, *Ethnobotany Research and Applications*.**
- Diachronic comparisons from Dioscorides via Ibn al-Baytar (and Ibn Sina) to modern Northeastern Morocco (Apiaceae; *Prunus dulcis*).
- Show selective erosion of knowledge.
- **Use:** methodological precedent for persistence categories (persisted / modified / lost).

**Lardos, Prieto-Garcia & Heinrich 2011, *Frontiers in Pharmacology*.** Resins and gums in Cypriot iatrosophia; the relationship of the iatrosophia to Dioscorides. **Use:** optional post-Byzantine link.

**Yarnell & Touwaide 2019, *J. Altern. Complement. Med.*.** Dioscorides' diuretic claims were largely accurate. **Use:** anecdotal precedent that ancient claims can be tested.

**Connelly et al. 2018 (arXiv; medieval *Lylye of Medicynes*).** Network analysis of a medieval text reveals non-random ingredient patterns related to antimicrobial activity. **Use:** precedent for computational mining of pre-modern texts.

## C. LLM and knowledge-graph systems for historical and traditional medicine

**DeepRoot (Ma et al., ICML 2026 GenBio workshop; arXiv:2606.15931) [verified].**
- Multi-agent LLM system that builds a verified Neo4j knowledge graph from the *Shen Nong Ben Cao Jing*.
- Grounding: COCONUT, PubChem, ChEMBL, Open Targets, MeSH/ICD-10/SNOMED.
- Recovers 10 of 21 held-out compound–disease pairs at R@20.
- Reduces hallucinated evidence (7–10% vs 87% for tool-calling LLMs).
- **Stated limitations:** a single corpus; N=21 held-out pairs without CIs; flat, uncalibrated priors.
- Its own examples show failures when the historical source is misidentified (e.g. an Arisaema/knotweed confusion).
- **Use:** we adopt its best practices:
  - verbatim-span auditing;
  - generate-then-verify ontology mapping;
  - InChIKey identity;
  - weakest-link path tiers.
- **We add:** probabilistic identification, a multi-text chain, calibrated confidence and temporal validation.
- Code: github.com/CarlisleMa/deeprootv1.

**OpenTCM (He et al. 2025, arXiv:2504.20118).** GraphRAG for TCM retrieval and diagnosis.

**LingShu (2026), TCMaster (2026), TCMScience (2026), DeepTCM (2026).** TCM-focused knowledge graphs and agents. They show the field is active but centred on Chinese medicine.

**LLM-H2G (2026, *BMC Bioinformatics*); RWR disease–plant (2026, *AgriEngineering*).**
- Herb–disease association prediction with random splits.
- The RWR paper reports ROC-AUC 0.9987, which suggests leakage.
- **Use:** as a cautionary contrast in our evaluation design.

## D. Phylogeny, cross-cultural convergence and research effort

**Saslis-Lagoudakis et al. 2012, *PNAS*.**
- Cross-cultural phylogenetic "hot nodes" are richer in bioactive plants (Nepal, New Zealand, Cape of South Africa).
- **Use:** optional feature (genus/family-level use clustering).

**Domingo-Fernández et al. 2023, *iScience*.**
- Large-scale cross-cultural analysis: congeneric plants share indications; taxonomically related plants share phytochemical space.
- **Use:** justification for genus-level smoothing; relevant to the Fraunhofer SCAI judge.

**de Souza et al. 2018, *Frontiers in Plant Science*.** Research effort is unevenly distributed across ethnomedicinal lineages. **Use:** motivates the popularity baseline.

**Cámara-Leret & Bascompte 2021, *PNAS*.** Over 75% of 12,495 medicinal plant uses studied are known in only one language. **Use:** framing for knowledge loss.

## E. Temporal validation and discovery forecasting

- **Abo-Dahab et al. 2026 — pharmacology knowledge graph (ChEMBL 36) with strict temporal split** (train ≤2022, test 2023–25) and hard negatives. **Use:** template for our temporal design.
- **Dyport (2023, arXiv:2312.03303):** importance-based time-sliced benchmarking of hypothesis generation.
- **Hakken (2026, arXiv:2609.04494); "Learning Scientific Trajectories" (2026, arXiv:2610.38719); BioDisco (2025, arXiv:2508.01285):** forecasting future discoveries with temporal evaluation.

## F. Modern Greek ethnobotany (endpoint data)

All of the following are open access:
- **Axiotis, Halabalaki & Skaltsounis 2018, *Frontiers in Pharmacology* 9:409 [verified].** North Aegean islands; 109 wild species from 52 families; supplementary tables; informant consensus factor.
- **Tsioutsiou, Cheilari & Aligiannis 2023, *Frontiers in Pharmacology* 14:1225580 [verified].** Plants used against skin ailments on Mount Pelion. Two of the authors are EthnoHack judges. Directly matches our pilot domain.
- **Perouli & Bareka 2022, *Mediterranean Botany* 43:e75357 [verified].** Milos island; covers 16th–21st c. changes. Cites earlier Greek studies (Crete: Skoula et al. 2009, 2010; Zagori/Epirus: Vokou et al. 1993; Malamas & Marselos 1992).

## G. The gap, stated precisely

To our knowledge no published system:
1. automates **probabilistic, calibrated** identification of plants named in ancient Greek pharmacological texts and validates it against an expert gold set;
2. **propagates identification uncertainty** through compound → target → disease evidence paths;
3. aligns claims across a **multi-text chain spanning about 2,000 years** to modern ethnobotany;
4. tests the forecasting value of that persistence with a **strict temporal split** and a popularity baseline.

This is a claim about the literature found, not proof of absence. The README and pitch should say "to our knowledge".
