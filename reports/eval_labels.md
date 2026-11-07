# Evidence labels (PubMed co-mention proxy)

* Pairs: 400 (172 species × 23 MeSH terms; skin pilot 397).
* With ≥1 record to 2025: 54 (0.135).
* First-support-year quantiles: {'0.1': 1984.0, '0.5': 2010.0, '0.9': 2023.0}
* Eligible / positive per cutoff: {'2000': {'eligible': 392, 'positive': 46}, '2005': {'eligible': 385, 'positive': 39}, '2010': {'eligible': 373, 'positive': 27}, '2015': {'eligible': 366, 'positive': 20}}

The exact query string is stored with each row of `data/processed/evidence_labels.parquet`.

**Human audit: pending.** The blinded audit sheet is in `data/gold/audits/`. No precision figure is claimed until a person fills it in; numbers below are automatic checks only.
