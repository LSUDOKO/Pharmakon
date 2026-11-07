# Decision log

| date | decision | reason | consequence for claims |
|---|---|---|---|
| 2026-11-07 | Rule-based extraction (`rule_extract_v1`) instead of LLM | No `ANTHROPIC_API_KEY` in the build environment; the LLM path is implemented (`--llm`) | 100% exact spans; recall limited to the lexicon; reported as such |
| 2026-11-07 | No CLTK / OdyCy | Model downloads exceed the 2 GB disk budget; `unicodedata` normalisation + stem rules suffice for headword matching | Lemmatisation is approximate |
| 2026-11-07 | LOTUS (Wikidata) instead of the COCONUT dump; ChEMBL/OT via REST | Disk budget; LOTUS carries reference years needed for the backtest | Compound coverage limited to Wikidata-curated pairs |
| 2026-11-07 | LOTUS reference dates fetched from `query-scholarly.wikidata.org` | Wikidata graph split moved scholarly articles off the main endpoint | Without this, only 0.6% of pairs had a date |
| 2026-11-07 | Galen *De simpl. med.* found in First1KGreek (`tlg0057.tlg075`, books 1–11) | The spec's [VERIFY] resolved positively; books 6–8 ingested | Galen is a real node; copy detection by 4-gram containment |
| 2026-11-07 | Paul of Aegina dropped (fallback R2) | `tlg0715` absent from First1KGreek | JC (via Lardos) is the Byzantine node |
| 2026-11-07 | Transfer identification model for non-gold names | Lardos literature counts exist only for gold names | Cluster posteriors use 6 features; evaluated separately |
| 2026-11-07 | Drop GBIF HIGHERRANK matches (R7) | Spec requires EXACT or FUZZY ≥ 90 at species/genus rank | 146 names dropped: 144 LSJ regex hits, 2 Lardos names (logged in `data/interim/gbif_verification.parquet`) |
| 2026-11-07 | Persistence on Lardos use groups, not raw ICPC-2 | JC and modern records are coded in Lardos' 21 groups | ICPC-2 → use-group crosswalk in `config/use_groups.yaml` |
| 2026-11-07 | Expert trait congruence used only as an ORACLE ablation | The gold verdict is derived from it (circularity) | f1 absent from headline model |
| 2026-11-07 | PubMed pairs capped at 400 (skin pilot) | Rate limit without an NCBI API key (≤ 3 req/s) | Fewer positives per cutoff; wide CIs |
