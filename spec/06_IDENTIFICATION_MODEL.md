# 06 — Probabilistic Plant Identification (core novelty)

## 1. Task definition

For each ancient name cluster *n*, estimate a probability distribution
P(s | n), with s ∈ C_n ∪ {∅}, where C_n is a verified candidate set of modern taxa and ∅ = "none of the candidates / unidentifiable".

Output: calibrated probabilities, top-k list, credible interval per probability, and human-readable reasons (which features drove the result).

## 2. Evidence streams (features)

Each feature is computed per (n, s). All features have documented provenance.

| # | Feature | How computed | Source |
|---|---|---|---|
| f1 | **Morphological agreement** | LLM converts the Dioscorides description of *n* into a structured trait record. Traits: habit, height class, stem, leaf shape/size/arrangement/hairiness, flower colour/shape, fruit/seed, root, smell, taste, habitat. The same schema is filled from a modern description of *s* (POWO / Flora of Greece / Lardos file 6). Score = weighted agreement over traits present in both, with "unknown" ignored. | `dmm_wellmann`, `powo`, `jc_lardos` file 3/6 |
| f2 | **Geographic plausibility** | log(1 + GBIF occurrence count of *s* in GR+CY+TR+eastern Med polygon) plus native-range flag (POWO) plus presence in the Flora of Greece checklist | `gbif_occ`, `powo`, `flora_greece` |
| f3 | **Name continuity** | Max similarity between the ancient lemma (transliterated, accent-stripped) and (a) modern Greek vernacular names of *s* (Wikidata P1843 `el`, Flora of Greece common names); (b) the genus/species epithet of *s* (many Linnaean names derive from Greek, e.g. *Artemisia absinthium* ← ἀψίνθιον). Features are kept separate because (b) can encode later scholarly guesses. | `wikidata_taxa`, `flora_greece` |
| f4 | **Scholarly agreement** | Number of independent sources proposing *s* (LSJ, Lardos candidates, Staub 2016), and whether the source asserts it or hedges ("prob.", "perh."; LSJ hedges are parsed) | `lsj`, `jc_lardos`, `dmm_staub` |
| f5 | **Use–part coherence** (ablation only) | Whether the plant part and use pattern of *n* match the modern documented uses of *s* (modern ethnobotany only, **no pharmacology**). Excluded from the backtest model to avoid circularity. | modern studies |
| f6 | **Taxonomic prior** | Genus-level prior from how often the genus is used medicinally in the Eastern Mediterranean (modern studies) | modern studies |

**Important:** no feature uses pharmacological evidence (PubMed/ChEMBL). Identification must be independent of the outcome we later test.

## 3. Model options

### Option A (default): conditional logit with a "none" alternative
- Utility U(n,s) = wᵀ f(n,s); U(n,∅) = b (a learned constant).
- P(s | n) = softmax over C_n ∪ {∅}.
- Fit w and b on the gold set (Section 4) by maximum likelihood with L2 regularisation (statsmodels `ConditionalLogit` or a small PyTorch/NumPy implementation).
- Few parameters (≈7), so it is suitable for a small gold set.

### Option B: Bayesian version (stretch)
- Same likelihood, with weakly informative priors on w (Normal(0,1)), in PyMC.
- Gives posterior predictive intervals for P(s|n), which become the uncertainty bars in the app.

### Option C: LLM-judge baseline (comparison only)
- Give the LLM the Greek description plus the candidate list and ask for probabilities.
- Report it as a baseline, not as the method. It cannot be validated independently and may have memorised scholarly identifications.

## 4. Gold standard and training data

- **Primary gold:** Lardos et al. 2024, 50 John-the-Physician plant names ↔ 61 Dioscorides plants, 130 candidate species. The expert confidence from their statistical evaluation (file 11) and comparative analyses (files 9–10) gives:
  - the top expert identification per name (for top-1 accuracy);
  - the expert confidence level (for calibration analysis).
- Map their candidates to GBIF keys. Record any failures.
- **Interpretation caveat:** the gold standard is expert judgement, not ground truth. Report agreement with experts and say so explicitly.
- **Secondary check (if available):** Staub 2016 putative identities for overlapping chapters. Measure agreement only (not training).

## 5. Training and evaluation protocol

- **Cross-validation:** leave-one-name-out (LONO) over the 50 gold names, so no name contributes to both training and testing.
- **Metrics:**
  - top-1 and top-3 accuracy vs expert top identification;
  - mean reciprocal rank;
  - log loss, Brier score, Expected Calibration Error (10 bins), reliability diagram;
  - accuracy stratified by expert confidence level.
- **Baselines:**
  1. LSJ single identification (dictionary baseline);
  2. most-frequent-genus prior;
  3. LLM-judge (Option C);
  4. features-without-f1 / without-f3 ablations.
- **Calibration:** fit temperature scaling on the inner CV folds. Report pre/post calibration ECE.
- **Bootstrap** (1,000 resamples over names) for 95% CIs on all metrics.

## 6. Applying the model to all Dioscorides names

- Generate candidates for every plant cluster in pilot scope, compute features and apply the trained model.
- Clusters with fewer than two verified candidates get `P(∅)` from the learned constant and are flagged `low_candidate_coverage`.
- Store `id_posterior` with `model_version`.

## 7. Propagation downstream

- Lead score for taxon *s* and condition *d* from name *n*:
  `score_weighted(n, s, d) = P(s|n) × path_strength(s → d)`.
- Name-level aggregate (expected evidence): `Σ_s P(s|n) × path_strength(s → d)`.
- The app shows: "This lead rests 62% on *Salvia fruticosa*, 21% on *S. officinalis*, 17% unidentified."
- Sensitivity analysis: re-rank leads using the top-1 identity only, and report rank changes (Kendall τ, and the count of top-20 leads that drop out). This answers RQ4.

## 8. Explanations

For each (n, s), store the per-feature contribution wᵢ·fᵢ and the trait-level matches (e.g. "flower colour: purple ↔ purple ✓; root: fleshy ↔ woody ✗"). Show them in the app.
