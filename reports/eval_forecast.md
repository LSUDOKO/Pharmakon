# Temporal backtest

Rolling origin: train on pairs unsupported at T−5 (labels in (T−5, T]); test on pairs unsupported at T (labels in (T, T_end]).
All features dated ≤ the row's cutoff. Label = PubMed co-mention proxy (precision pending audit).

| T | n test | positives | random | popularity | history | chemistry | history+pop | full | full (GBM) | shuffled hist+pop | ΔAUPRC(hist+pop − pop) 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2000 | 392 | 46 | 0.1069 | 0.1662 | 0.1451 | 0.142 | 0.1581 | 0.1614 | 0.1623 | 0.1207 | [-0.0713, 0.0445] |
| 2005 | 385 | 39 | 0.1148 | 0.3796 | 0.1242 | 0.1008 | 0.3384 | 0.3642 | 0.1901 | 0.2663 | [-0.1422, 0.0733] |
| 2010 | 373 | 27 | 0.1318 | 0.5577 | 0.0855 | 0.0732 | 0.5516 | 0.3091 | 0.3578 | 0.4417 | [-0.0626, 0.0582] |
| 2015 | 366 | 20 | 0.1092 | 0.5005 | 0.0619 | 0.0503 | 0.4617 | 0.4018 | 0.4791 | 0.3786 | [-0.1261, 0.0488] |

Precision@k and AUROC per model: `reports/stages/forecast.json`.

## Leakage controls

* no LLM features
* identification uses no pharmacology
* modern studies gated by publication year ≤ T
* LOTUS reference year and ChEMBL document year ≤ T
* shuffled-history control reported
* Open Targets associations are current (not historical): see full_without_OT_dependent

## Interpretation

Read the ΔAUPRC column: if its 95% CI excludes 0, persistence/history adds information beyond research popularity at that cutoff; otherwise the pilot finds no added signal at that cutoff. All cutoffs are reported; none were selected after the fact.

**Result: null.** At every cutoff the ΔAUPRC CI includes 0; popularity (papers on the species before T) dominates.

**Diagnosis.** History-only AUPRC falls to or below the base rate at 2010/2015, and the history coefficients are mostly negative (more Dioscorides claims, JC or modern attestation → lower score). The likely mechanism is *selection*: eligibility is "no PubMed support up to T", so the best-attested traditional remedies were studied early and leave the eligible pool; what remains at later cutoffs is enriched for well-attested-but-unstudied pairs that stay unstudied. Small positive counts (20–46) and the unaudited co-mention label add noise. A survival model over all years (R9) is the natural next step.

Full-model logistic coefficients per cutoff:

```json
{
 "2000": {
  "h_p_species": 0.3544,
  "h_n_dmm_claims": -0.2751,
  "h_present_jc": -0.0796,
  "h_modern_attested": -0.1764,
  "h_topical_share": 0.4864,
  "h_n_texts": -0.1522,
  "c_n_compounds": 0.6966,
  "c_n_compounds_active_on_assoc_targets": 0.0,
  "pop_species": -0.4772,
  "pop_disease": 0.495
 },
 "2005": {
  "h_p_species": 0.1978,
  "h_n_dmm_claims": -0.5998,
  "h_present_jc": -0.1934,
  "h_modern_attested": -0.2643,
  "h_topical_share": 0.3005,
  "h_n_texts": -0.2634,
  "c_n_compounds": -0.4838,
  "c_n_compounds_active_on_assoc_targets": -0.0839,
  "pop_species": 1.0155,
  "pop_disease": 0.305
 },
 "2010": {
  "h_p_species": -0.1489,
  "h_n_dmm_claims": -0.2938,
  "h_present_jc": -0.3344,
  "h_modern_attested": 0.1051,
  "h_topical_share": 0.102,
  "h_n_texts": -0.0865,
  "c_n_compounds": 0.3066,
  "c_n_compounds_active_on_assoc_targets": 0.2044,
  "pop_species": 1.0095,
  "pop_disease": 1.1155
 },
 "2015": {
  "h_p_species": -0.1271,
  "h_n_dmm_claims": -0.2196,
  "h_present_jc": -0.228,
  "h_modern_attested": -0.3447,
  "h_topical_share": 0.0376,
  "h_n_texts": -0.3378,
  "c_n_compounds": 0.3546,
  "c_n_compounds_active_on_assoc_targets": -0.4626,
  "pop_species": 1.1293,
  "pop_disease": 1.5757
 }
}
```
