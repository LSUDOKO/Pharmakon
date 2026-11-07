# Identification vs expert gold (Lardos et al. 2024)

**Caveat:** the gold standard is expert judgement (botanical congruence + use congruence), not ground truth.

Leave-one-name-out over 61 gold names (grouped by the 50 JC lemmas); 95% bootstrap CIs over names (1,000).

| model | top-1 | top-1 95% CI | top-3 | MRR | log loss | Brier | ECE |
|---|---|---|---|---|---|---|---|
| model_calibrated | 0.623 | [0.5082, 0.7541] | 0.918 | 0.7784 | 0.9845 | 0.5004 | 0.2097 |
| model_uncalibrated | 0.623 | [0.5082, 0.7541] | 0.918 | 0.7784 | 0.9812 | 0.4956 | 0.1366 |
| baseline_lsj | 0.3115 | [0.1967, 0.4426] | 0.8033 | 0.5746 | 9.4441 | 1.3443 | 0.6885 |
| baseline_genus_prior | 0.377 | [0.2623, 0.5082] | 0.8689 | 0.6169 | 1.1572 | 0.5923 | 0.0935 |
| baseline_uniform | 0.3934 | [0.2787, 0.5246] | 0.8689 | 0.632 | 1.2005 | 0.632 | 0.1221 |
| baseline_llm_judge | not_run — ANTHROPIC_API_KEY not set (spec/06 Option C is comparison-only) | | | | | | |
| ablation_without_f2 | 0.6557 | [0.541, 0.7869] | 0.918 | 0.7929 | 1.0355 | 0.5388 | 0.2367 |
| ablation_without_f3 | 0.623 | [0.5082, 0.7541] | 0.918 | 0.7811 | 0.967 | 0.491 | 0.1842 |
| ablation_without_f4 | 0.541 | [0.4098, 0.6721] | 0.9016 | 0.7219 | 1.08 | 0.5536 | 0.1403 |
| ablation_without_f6 | 0.6557 | [0.541, 0.7869] | 0.918 | 0.7967 | 0.9711 | 0.4919 | 0.1979 |
| transfer_model_calibrated | 0.5574 | [0.4262, 0.6885] | 0.918 | 0.7388 | 1.067 | 0.5481 | 0.1471 |
| ablation_plus_ORACLE_expert_traits | 0.8361 | [0.7377, 0.918] | 0.9836 | 0.9112 | 0.3705 | 0.2216 | 0.093 |

## Success criterion (spec/07 §3)

* Beats the LSJ dictionary baseline on top-1 **and** Brier: **yes**.
* ECE ≤ 0.10 after calibration: **no** (calibrated 0.2097, uncalibrated 0.1366). Diagnosis: with 61 names each ECE bin holds ≈6 names, so ECE is noisy; temperature scaling (T=1.1688) is fitted by NLL on tie-aware targets, which need not minimise top-1 ECE. The expert-trait ORACLE ablation reaches ECE 0.093: the missing morphology stream (f1, needs an LLM) is the main gap.

## Weights (full model)

```json
{
 "f2_geo_log_occ": 0.2048,
 "f2_present_gr": 0.6771,
 "f3_vernacular_sim": 0.0277,
 "f3_epithet_sim": 0.0739,
 "f4_lit_dmm": 0.4715,
 "f4_lit_ethno": 0.37,
 "f4_lsj": -0.2835,
 "f6_genus_consensus": 0.1742
}
```
Unidentified-bucket utility b = -0.4116; temperature 1.1688.

The **transfer model** (no Lardos literature counts, so it can score all Dioscorides names) is the one applied to clusters:
```json
{
 "features": [
  "f2_geo_log_occ",
  "f2_present_gr",
  "f3_vernacular_sim",
  "f3_epithet_sim",
  "f4_lsj",
  "f6_genus_consensus"
 ],
 "weights": {
  "f2_geo_log_occ": 0.3742,
  "f2_present_gr": 0.6753,
  "f3_vernacular_sim": 0.0303,
  "f3_epithet_sim": 0.222,
  "f4_lsj": -0.3116,
  "f6_genus_consensus": 0.1601
 },
 "none_utility_b": -0.7453,
 "temperature": 1.1844
}
```
Accuracy by expert confidence: [{'expert_confidence': 'MODERATE', 'mean': 0.731, 'count': 26}, {'expert_confidence': 'NOT_FOUND', 'mean': 0.5, 'count': 2}, {'expert_confidence': 'STRONG', 'mean': 0.68, 'count': 25}, {'expert_confidence': 'WEAK', 'mean': 0.125, 'count': 8}]

GBIF verification of candidates: {'inputs': 683, 'verified': 537, 'fail_reasons': {'match=HIGHERRANK:99': 116, 'match=HIGHERRANK:94': 5, 'kingdom=Fungi': 5, 'kingdom=Chromista': 5, 'match=HIGHERRANK:96': 5, 'match=FUZZY:86': 3, 'match=FUZZY:89': 3, 'match=HIGHERRANK:95': 1, 'match=FUZZY:80': 1, 'match=FUZZY:87': 1}}

Applied to 653 Dioscorides names: 293 have a taxon as top-1; 516 have fewer than two verified candidates (`low_candidate_coverage`).

Reliability diagram: `figures/reliability.html`. Example identification cards: `identification_cards.md`.
