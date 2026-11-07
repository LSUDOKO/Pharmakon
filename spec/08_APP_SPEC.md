# 08 — Explorer App Specification

**Framework:** Streamlit (multipage). **Data:** reads Parquet/DuckDB from `data/processed/` (read-only). **Deploy:** Streamlit Community Cloud or Hugging Face Spaces. Include a small sample dataset so the demo runs without the full pipeline.

**Global UI elements:**
- A banner on every page: "Research hypotheses only — not medical advice. Identifications are probabilistic."
- A sidebar with pilot domain, cutoff selector (for backtest pages) and data version.

## Page 1 — Home
- One-paragraph explanation of the project.
- Four headline numbers. Each one comes from `reports/*.json`, never hard-coded:
  - passages processed;
  - claims extracted;
  - names identified (with mean top-1 probability);
  - backtest AUPRC vs popularity baseline.
- Pipeline diagram.

## Page 2 — Ancient Name Explorer (hero screen)
- **Search:** by Greek (accent-insensitive), transliteration, or modern species.
- **Left column:** passages across centuries. One card per work:
  - Greek text, with the evidence span highlighted;
  - machine translation, labelled "MT";
  - CTS URN link to Perseids.
- **Right column:** identification card.
  - Bar chart of P(s|n) with credible intervals, including "unidentified".
  - Per-candidate feature contributions (morphology, geography, name continuity, scholarly agreement).
  - Trait-match table (Dioscorides trait ↔ modern trait, ✓/✗/?).
  - Candidate sources (LSJ, Lardos, Staub, LLM-proposed and verified).
- **Bottom:** persistence timeline. Columns per text; rows per condition category; filled/empty dots.

## Page 3 — Evidence Paths
- Pick a name or taxon and a condition. The page shows the paths Taxon → Compound → Target → Disease as an interactive graph (pyvis) and a table.
- Columns: tier per edge, pChEMBL, OT score, reference years, and path strength × P(species).
- A toggle switches between "weighted by identification probability" and "top-1 identity only".

## Page 4 — Time Machine (backtest)
- Cutoff selector *T*. Charts:
  - AUPRC/AUROC by model vs baselines, with CIs;
  - precision@k.
- "Hits table": pairs the model ranked highly at *T* that later gained support, with the first supporting PMID and year (a link to PubMed).
- "Misses table": highly ranked pairs that did not gain support, labelled "no support found (yet)".
- Leakage-control results (shuffled-history control).

## Page 5 — Leads
- Ranked unsupported pairs today.
- Filters: condition, plant part, P(species) ≥ x, conservation status, toxicity flag.
- Each row expands to its evidence paths and identification card.
- Export to CSV.

## Page 6 — Methods, Data & Limitations
- Renders `docs/limitations.md`, the source licences table, verification status and how to cite.

## Non-functional requirements
- Loads in under 5 s on the sample dataset.
- Usable on a phone screen (Streamlit default layout; avoid wide tables without scroll).
- Greek fonts render correctly. Test with Noto Serif or GFS Didot via CSS.
- Accessibility: never rely on colour alone. Use ✓/✗ symbols and text labels.
