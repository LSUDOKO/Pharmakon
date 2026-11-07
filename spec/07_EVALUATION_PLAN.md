# 07 — Evaluation Plan ("data proofs")

Each claim the project makes must be backed by one of the evaluations below. Every number in the pitch must trace to a file in `reports/`.

## 1. Evaluation map

| Claim | Evaluation | Output file |
|---|---|---|
| Text ingestion is faithful | 20-passage manual comparison with the Perseids reader; residual-apparatus rate | `reports/eval_ingest.md` |
| Extraction is reliable | Span-verification rate; 50-claim field-level precision audit; recall on 10 fully annotated passages | `reports/eval_extraction.md` |
| Condition mapping is sensible | 50-item MeSH/ICPC audit; % mapped | `reports/eval_conditions.md` |
| Identification agrees with experts and is calibrated | LONO CV vs Lardos gold: top-1/top-3, MRR, Brier, ECE, reliability diagram; baselines; bootstrap CIs | `reports/eval_identification.md` |
| Persistence patterns are real | Counts per pattern; comparison with published qualitative findings (Mir 2026; Smaili 2026; Leonti 2015); permutation null | `reports/eval_persistence.md` |
| Forecasting value | Temporal backtest (Section 4) | `reports/eval_forecast.md` |
| Uncertainty matters | Rank sensitivity: weighted vs top-1 identification | `reports/eval_uncertainty.md` |
| Evidence labels are trustworthy | 100 positive + 50 negative PubMed label audit | `reports/eval_labels.md` |

## 2. Human audits (small, but essential)

- **Who:** a team member with pharmacy/botany background; ideally a reader of ancient Greek for the extraction audit.
- **Tooling:** the pipeline writes CSV audit sheets to `data/gold/audits/` with a `label` column. A Streamlit audit page is optional.
- **Blinding:** for label audits, the auditor does not see model scores.
- **Reporting:** precision with Wilson 95% CIs.

## 3. Identification evaluation (summary; full protocol in `06_IDENTIFICATION_MODEL.md` §5)

- **Primary metric:** top-1 agreement with the expert identification.
- **Secondary:** Brier score and ECE. Calibration is the core claim.
- **Success criterion:**
  - beats the LSJ baseline on top-1 *and* on Brier;
  - ECE ≤ 0.10 after calibration;
  - otherwise report honestly and diagnose by feature ablation.

## 4. Temporal backtest (the "time machine")

### 4.1 Units
Each row is a candidate pair (taxon *s*, MeSH disease *d*) arising from a historical claim. *s* comes from the identification posterior: use pairs with P(s|n) ≥ 0.2, and carry the probability as a feature.

### 4.2 Cutoffs and labels
- Cutoffs *T* ∈ {2000, 2005, 2010, 2015}; end year *T_end* = last complete year of PubMed indexing (e.g. 2025).
- **Eligible rows at *T*:** pairs with **no** support up to *T* (first_support_year > *T* or none).
- **Label:** 1 if first_support_year ∈ (*T*, *T_end*], else 0.
- Also report a stricter label: ≥2 papers, or ≥1 in vivo/clinical.

### 4.3 Features (strictly ≤ *T*)
- **Historical:**
  - persistence_score, pattern;
  - number of texts attesting;
  - plant part; route; ICPC chapter;
  - P(s|n);
  - attested in modern Greek studies — **only if the study was published ≤ *T***; otherwise exclude the feature for that cutoff.
- **Chemistry:**
  - number of compounds for *s* with LOTUS reference year ≤ *T*;
  - number of those with ChEMBL activities (doc year ≤ *T*) on targets associated with *d* (Open Targets score ≥0.2).
  
  Note: Open Targets associations are current, not historical. Run a sensitivity analysis without this feature and state the limitation.
- **Popularity (confounder):**
  - PubMed papers mentioning *s* (any topic) ≤ *T*;
  - papers on *d* ≤ *T*.
- **Taxonomy:** genus-level prior use rate (modern studies ≤ *T*); family one-hot (top families).

### 4.4 Models
- Logistic regression (L2) — interpretable main model.
- Gradient boosting (LightGBM) — capacity check.
- Train on rows from cutoff *T−5* with labels in (*T−5*, *T*]; test on rows at *T*. This is a rolling-origin evaluation and is the strictest version.

### 4.5 Baselines
1. **Random.**
2. **Popularity:** papers on *s* before *T*. This is the key baseline, the "rich get richer" effect.
3. **Chemistry-only.**
4. **History-only** (persistence + attestation).
5. **History + popularity** vs **popularity alone**: does history add signal? (likelihood-ratio test; ΔAUPRC with bootstrap CI)

### 4.6 Metrics and statistics
- AUROC, AUPRC (primary, because positives are rare), precision@k (k = 20, 50, 100), and lift over the base rate.
- 1,000-sample bootstrap CIs, resampling ancient names (clusters) to respect dependence.
- DeLong test for AUROC differences (or a bootstrap difference test).
- Report all cutoffs. Do not cherry-pick.

### 4.7 Leakage controls (must be documented)
- No LLM-derived plausibility features.
- Identification features exclude pharmacology (f5 excluded).
- Modern-study features gated by publication year.
- LOTUS/ChEMBL filtered by reference/document year.
- Run a "shuffled-history" control: permute persistence scores across rows. Performance should fall to the baseline.

### 4.8 Interpreting results
- If history adds signal: "Persistence over 2,000 years carries information about future pharmacological support beyond research popularity."
- If not: "In this pilot, persistence did not predict future support once popularity was controlled." Discuss label noise, sample size and domain.
- Both outcomes are publishable and are framed as scientific findings in the pitch.

## 5. Figures to produce (for slides and README)

1. Pipeline diagram.
2. Identification reliability diagram: model vs LSJ vs LLM-judge.
3. Example "identification card" for one name with feature contributions.
4. Persistence alluvial or Sankey: DMM → Galen → Paul → JC → modern, by ICPC chapter.
5. Backtest: AUPRC by cutoff, with CIs, history+pop vs pop.
6. Precision@k curve.
7. Lead table: top 15 with P(species), evidence tier and conservation flag.
8. Rank-sensitivity plot: weighted vs top-1 identity.

## 6. Reproducibility package
- `make reproduce` runs from cached raw data to every figure and table.
- Pin versions (`uv.lock`) and record the dates/versions of all data sources in `reports/data_versions.md`.
- Archive processed outputs with a Zenodo DOI after the hackathon (optional).
