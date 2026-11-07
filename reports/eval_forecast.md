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
