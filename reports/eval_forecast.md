# Temporal backtest

Rolling origin: train on pairs unsupported at T−5 (labels in (T−5, T]); test on pairs unsupported at T (labels in (T, T_end]).
All features dated ≤ the row's cutoff. Label = PubMed co-mention proxy (precision pending audit).

| T | n test | positives | random | popularity | history | chemistry | history+pop | full | full (GBM) | shuffled hist+pop | ΔAUPRC(hist+pop − pop) 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2000 | 1404 | 122 | 0.0829 | 0.3812 | 0.1258 | 0.221 | 0.3603 | 0.348 | 0.3334 | 0.2936 | [-0.0783, 0.0301] |
| 2005 | 1384 | 102 | 0.0767 | 0.3407 | 0.0792 | 0.1838 | 0.2699 | 0.2184 | 0.1884 | 0.2887 | [-0.1362, -0.0169] |
| 2010 | 1361 | 79 | 0.0612 | 0.3085 | 0.0659 | 0.2373 | 0.2932 | 0.3013 | 0.3144 | 0.2667 | [-0.0762, 0.0555] |
| 2015 | 1332 | 50 | 0.0376 | 0.2746 | 0.0598 | 0.1717 | 0.2814 | 0.2763 | 0.2035 | 0.258 | [-0.0548, 0.0601] |

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
  "h_p_species": 0.3222,
  "h_n_dmm_claims": -0.0935,
  "h_present_jc": -0.2166,
  "h_modern_attested": -0.393,
  "h_topical_share": 0.0628,
  "h_n_texts": -0.3724,
  "c_n_compounds": 0.552,
  "c_n_compounds_active_on_assoc_targets": 0.1505,
  "pop_species": 0.2667,
  "pop_disease": 1.2847
 },
 "2005": {
  "h_p_species": 0.0756,
  "h_n_dmm_claims": 0.0042,
  "h_present_jc": 0.1091,
  "h_modern_attested": 0.2375,
  "h_topical_share": 0.1999,
  "h_n_texts": 0.2134,
  "c_n_compounds": 0.0911,
  "c_n_compounds_active_on_assoc_targets": -0.2539,
  "pop_species": 0.9629,
  "pop_disease": 0.9166
 },
 "2010": {
  "h_p_species": 0.3579,
  "h_n_dmm_claims": -0.3146,
  "h_present_jc": -0.2917,
  "h_modern_attested": 0.2673,
  "h_topical_share": 0.1478,
  "h_n_texts": 0.0227,
  "c_n_compounds": 1.4893,
  "c_n_compounds_active_on_assoc_targets": 0.1302,
  "pop_species": 0.6444,
  "pop_disease": 0.9743
 },
 "2015": {
  "h_p_species": 0.1944,
  "h_n_dmm_claims": -0.0154,
  "h_present_jc": 0.139,
  "h_modern_attested": -0.0703,
  "h_topical_share": -0.1245,
  "h_n_texts": 0.0274,
  "c_n_compounds": 0.5918,
  "c_n_compounds_active_on_assoc_targets": 0.1689,
  "pop_species": 0.6504,
  "pop_disease": 1.1372
 }
}
```
