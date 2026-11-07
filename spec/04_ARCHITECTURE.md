# 04 — Architecture

## 1. High-level flow

```mermaid
flowchart LR
  subgraph Texts
    A1[Dioscorides TEI] --> C[Corpus loader]
    A2[Galen TEI/OCR] --> C
    A3[Paul of Aegina] --> C
    A4[Lardos JC data] --> X
    A5[Modern Greek studies] --> X
  end
  C --> S[Segmenter: chapter/passage + CTS URN]
  S --> E[LLM claim extraction + span verification]
  E --> X[Claims table]
  X --> N[Name resolution: lemma clusters]
  N --> ID[Probabilistic identification]
  ID --> T[Taxon distribution per name]
  T --> CH[Compounds: COCONUT/LOTUS]
  CH --> TG[Targets: ChEMBL]
  TG --> DS[Diseases: Open Targets/MeSH]
  X --> CM[Condition mapping: ICPC-2 + MeSH]
  CM --> P[Persistence alignment across texts]
  T --> P
  P --> F[Backtest features ≤ cutoff]
  DS --> F
  PM[PubMed first-evidence years] --> F
  F --> M[Forecast models + baselines]
  M --> L[Leads, weighted by P(species)]
  L --> APP[Explorer app]
  P --> APP
  ID --> APP
```

## 2. Repository layout

```
pharmakon/
├── CLAUDE.md
├── spec/                      # this pack
├── config/
│   ├── sources.yaml           # URLs, versions, cutoffs
│   ├── pilot.yaml             # pilot domain (skin/wounds), texts in scope
│   └── prompts/               # versioned prompt templates (*.md)
├── data/
│   ├── raw/<source_id>/       # untouched downloads + LICENSE.txt (gitignored if large)
│   ├── interim/               # parsed, not yet linked
│   ├── processed/             # final parquet tables
│   ├── gold/                  # gold sets (Lardos-derived, audits)
│   ├── cache/                 # http + llm caches
│   └── pharmakon.duckdb
├── src/pharmakon/
│   ├── __main__.py            # CLI (typer)
│   ├── schemas.py             # Pydantic models for all tables
│   ├── http.py                # cached, rate-limited client
│   ├── llm.py                 # Anthropic client wrapper, caching, schema validation
│   ├── corpus/
│   │   ├── first1k.py         # TEI → passages (strip apparatus)
│   │   ├── ocr_loader.py      # fallback for OCR texts
│   │   └── segment.py
│   ├── extract/
│   │   ├── claims.py          # LLM extraction
│   │   └── span_verify.py
│   ├── names/
│   │   ├── normalize.py       # Greek normalisation, lemma clustering
│   │   └── crosswalk.py       # same plant across texts
│   ├── identify/
│   │   ├── candidates.py      # LSJ, Lardos, Staub, LLM proposals → verified taxa
│   │   ├── features.py        # morphology, geography, name continuity, agreement
│   │   ├── model.py           # conditional logit / Bayesian combination
│   │   └── calibrate.py
│   ├── link/
│   │   ├── taxonomy.py        # GBIF/WFO/Flora of Greece
│   │   ├── chemistry.py       # COCONUT/LOTUS, InChIKey identity
│   │   ├── targets.py         # ChEMBL with document years
│   │   └── disease.py         # MeSH/MONDO/Open Targets, ICPC-2
│   ├── persist/
│   │   ├── align.py
│   │   └── score.py
│   ├── evidence/
│   │   ├── pubmed.py          # query builder, first-year labels
│   │   └── audit.py           # label audit sampling
│   ├── forecast/
│   │   ├── features.py        # strictly ≤ cutoff
│   │   ├── models.py          # logistic, gradient boosting
│   │   ├── baselines.py
│   │   └── evaluate.py        # AUROC/AUPRC/P@k + bootstrap
│   ├── leads/rank.py
│   ├── kg/build.py            # NetworkX graph + optional Neo4j export
│   └── app/                   # Streamlit explorer
├── tests/
├── notebooks/
├── reports/                   # phase reports, figures
├── docs/                      # data_dictionary, limitations, source_verification
├── Makefile
└── pyproject.toml
```

## 3. Core tables (Parquet; schemas in `schemas.py`)

### `passages`
| column | type | notes |
|---|---|---|
| passage_id | str | `{work}:{book}.{chapter}.{section}` |
| cts_urn | str | full CTS URN |
| work | enum | `dmm`, `galen_simpl`, `paul7`, ... |
| century_ce | int | 1, 2, 7, 13 ... |
| text_grc | str | NFC-normalised Greek, apparatus stripped |
| text_en_mt | str? | machine translation, labelled |
| source_id, retrieved_at, method | | provenance |

### `claims`
| column | type | notes |
|---|---|---|
| claim_id | str | hash |
| passage_id | str | FK |
| substance_name_grc | str | as written |
| substance_lemma | str | normalised |
| substance_type | enum | plant, mineral, animal, compound_preparation, unknown |
| plant_part | enum | root, leaf, seed, fruit, flower, bark, juice/sap, resin/gum, whole, oil, other |
| preparation | str | e.g. decoction, plaster, with wine |
| route | enum | topical, oral, inhaled, rectal/vaginal, other |
| condition_text_grc | str | verbatim |
| condition_en | str | normalised English description |
| icpc2_chapter | str | e.g. `S` (skin) |
| mesh_ids | list[str] | verified only |
| evidence_span_grc | str | verbatim substring of passage |
| span_verified | bool | |
| status | enum | ok, span_mismatch, ambiguous, archived |
| extractor_version | str | prompt + model |

### `name_clusters`
Groups spellings/lemmas across texts that refer to the same ancient drug name (e.g. ἀψίνθιον variants). Columns: `cluster_id, lemma, variants[], works[], crosswalk_method, confidence`.

### `id_candidates`
`cluster_id, taxon_key (GBIF), accepted_name, family, candidate_sources[], features{...}`

### `id_posterior`
`cluster_id, taxon_key, p, p_lo, p_hi, model_version, calibrated(bool)`. The probabilities for each cluster sum to 1 and include an explicit `__unidentified__` bucket.

### `taxon_compounds`
`taxon_key, inchikey, source (coconut|lotus), reference_doi, reference_year, organism_part`

### `compound_targets`
`inchikey, chembl_target_id, pchembl, assay_type, doc_year, tier`

### `target_disease`
`chembl_target_id|ensembl_id, disease_id (MONDO/EFO/MeSH), ot_score, tier`

### `persistence`
`cluster_id, icpc2_chapter, plant_part, present_in{dmm,galen,paul,jc,modern}, first_attested_century, persistence_score, pattern (persisted|modified|lost|novel)`

### `evidence_labels`
`taxon_key, mesh_id, first_support_year, n_papers_by_year{...}, query_string, audited(bool), audit_label`

### `forecast_dataset`
One row per (cluster, taxon, condition) pair at a given cutoff *T*: features ≤ *T* and label (support appears in (*T*, *T_end*]).

### `leads`
`cluster_id, taxon_key, mesh_id, lead_score, p_species, score_weighted, path_ids[], conservation_status, toxicity_flag`

## 4. Knowledge-graph view

Nodes:
- `Passage`
- `AncientName`
- `Taxon`
- `Compound` (InChIKey)
- `Target` (ChEMBL ID)
- `Disease` (MONDO/MeSH)
- `ConditionCategory` (ICPC-2)
- `Text`/`Period`

Edges (all with provenance, tier and confidence):
- `MENTIONS` (Passage→AncientName)
- `CLAIMS_USE_FOR` (AncientName→ConditionCategory; with part, route and span)
- `IDENTIFIED_AS` (AncientName→Taxon; **p**)
- `CONTAINS` (Taxon→Compound; reference year)
- `ACTS_ON` (Compound→Target; pChEMBL, doc year)
- `ASSOCIATED_WITH` (Target→Disease; OT score)
- `MAPS_TO` (ConditionCategory/condition→Disease)
- `ATTESTED_IN` (claim→Text)

**Path scoring:**
- weakest-link tier (as in DeepRoot) multiplied by `P(IDENTIFIED_AS)`;
- the explorer shows both the unweighted path and the weighted path.

## 5. Technology choices

- `typer` CLI, `pydantic` v2, `polars` or `pandas`, `duckdb`, `pyarrow`, `networkx`.
- `lxml` for TEI; `cltk` (or OdyCy) for Greek lemmatisation; `rapidfuzz` for string similarity; `unidecode` plus a custom Greek → Latin transliteration for name-continuity features.
- `rdkit` for InChIKey and canonicalisation.
- `chembl_webresource_client` or a local ChEMBL SQLite.
- `scikit-learn`, `statsmodels` (conditional logit), optionally `pymc` for a Bayesian identification model.
- `streamlit` + `plotly`/`altair` + `pyvis` for the app.
- `anthropic` SDK for LLM calls.
