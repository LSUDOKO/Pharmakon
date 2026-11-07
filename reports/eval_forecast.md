# Temporal backtest

Rolling origin: train on pairs unsupported at T−5 (labels in (T−5, T]); test on pairs unsupported at T (labels in (T, T_end]).
All features dated ≤ the row's cutoff. Label = PubMed co-mention proxy (precision pending audit).

| T | n test | positives | random | popularity | history | chemistry | history+pop | full | full (GBM) | shuffled hist+pop | ΔAUPRC(hist+pop − pop) 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|

Precision@k and AUROC per model: `reports/stages/forecast.json`.

## Leakage controls


## Interpretation

Read the ΔAUPRC column: if its 95% CI excludes 0, persistence/history adds information beyond research popularity at that cutoff; otherwise the pilot finds no added signal at that cutoff. All cutoffs are reported; none were selected after the fact.
