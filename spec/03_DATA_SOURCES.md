# 03 — Data Sources

Each source has a `source_id` used in provenance columns.
- **[verified]**: checked on 7 Nov 2026.
- **[VERIFY]**: must be confirmed by the agent before use (record results in `docs/source_verification.md`).

Licences can change. Re-check at download time and store a copy of the licence text in `data/raw/<source_id>/LICENSE.txt`.

---

## 1. Historical Greek texts

### `dmm_wellmann` — Dioscorides, *De materia medica* [verified]
- **Edition:** Max Wellmann, *Pedanii Dioscuridis Anazarbei De materia medica libri quinque*, 3 vols, Berlin: Weidmann 1906–1914. Public domain.
- **Digital text:** First Thousand Years of Greek (Open Greek and Latin), TEI XML.
  - CTS URN: `urn:cts:greekLit:tlg0656.tlg001.1st1K-grc1`.
  - Readable online, e.g. `https://cts.perseids.org/read/greekLit/tlg0656/tlg001/1st1K-grc1/3.2.3-3.4.1`.
- **Repository:** `https://github.com/OpenGreekAndLatin/First1KGreek` (path `data/tlg0656/tlg001/`).
  - Clone with `git clone --depth 1 --filter=blob:none --sparse` then `git sparse-checkout set data/tlg0656 data/tlg0057 data/tlg0715`.
- **Licence:** First1KGreek XML is distributed under CC BY-SA 4.0 **[VERIFY exact licence in repo]**.
- **Notes:**
  - Passages include critical apparatus text in places (sigla such as `R`, `E`, `Di`). The loader must strip `<note>`/apparatus elements and keep the main text.
  - Verify by sampling 20 passages against the Perseids reader.
  - Related: `tlg0656.tlg002` (*Euporista / De simplicibus*, Wellmann vol. 3) also exists in First1KGreek [verified]. Optional.

### `galen_simpl` — Galen, *De simplicium medicamentorum temperamentis ac facultatibus*
- **Edition:** C. G. Kühn, *Claudii Galeni Opera omnia*, vols 11–12, Leipzig 1826 [verified bibliographic details].
  - Books 1–5 (theory): vol. 11, pp. 379–788.
  - Books 6–11 (individual simples: plants, then minerals, animals): continue into vol. 12.
- **Digital text:** look for Galen (`tlg0057`) in First1KGreek **[VERIFY which work number corresponds to De simpl. med. and whether books 6–8 are present]**.
- **Fallbacks:** Kühn scans (Internet Archive; BIU Santé Medica) with Greek OCR. Medimanus/Pharmantica (Harvard CHS) lists the work's structure and Kühn pagination [verified]: `https://medimanus.chs.harvard.edu/app/pharmantica/de_simplicibus_header`.
- **Pilot use:** books 6–8 (plants).

### `paul_aegina` — Paul of Aegina, *Epitome medicae libri septem*, book 7
- **Edition:** J. L. Heiberg, *Corpus Medicorum Graecorum* IX 1–2, Leipzig/Berlin: Teubner 1921–1924 [verified bibliographic details].
- **Digital text:** CMG digital facsimiles are offered by the Berlin-Brandenburg Academy (CMG online) **[VERIFY URL and terms]**. Also check First1KGreek for `tlg0715` **[VERIFY]**.
- **Fallback:** OCR of CMG PDF with manual spot-checks; or skip Paul and use Lardos John-the-Physician data as the Byzantine node.

### `jc_lardos` — John the Physician's *Therapeutics* (via Lardos et al.) [verified]
- **Data:** Royal Holloway figshare, `https://doi.org/10.17637/rh.23736189.v1`. The data directory lists 11 data files:
  1. JC lemma and word tags
  2. Plant names JC–DMM
  3. DMM plant descriptions
  4. JC plant uses
  5. Candidate plants and MPNS validation
  6. Modern plant descriptions
  7. PubMed / clinical-trial data
  8. Modern medicinal uses
  9. Botanical comparative analysis
  10. Medicinal comparative analysis
  11. Statistical evaluation
- **Paper:** Lardos et al. 2024, *J Ethnopharmacol* 322:117622, doi:10.1016/j.jep.2023.117622 (CC BY 4.0).
- **Licence of data files:** **[VERIFY on figshare record]** (likely CC BY 4.0).
- **Use:**
  - **gold standard** for identification (files 2, 5, 9, 11);
  - Byzantine node for persistence (file 4);
  - feature template (files 3, 6).

### `iatrosophia_cy` — Cypriot iatrosophia (optional)
- Lardos, Prieto-Garcia & Heinrich 2011, *Front. Pharmacol.* (open access). Tables of plant uses. Use only the published tables.

### `dmm_staub` — Staub, Casu & Leonti 2016 DMM database (optional comparison set)
- 5,314 uses / 536 taxa / 924 herbal drugs from the Matthioli 1568 version [verified counts].
- **[VERIFY]** whether supplementary data are downloadable. If not, email the corresponding author (Leonti, University of Cagliari) and describe the non-commercial research use. Do not scrape the paywalled PDF.

### Copyrighted translations — do NOT ingest
- Beck (2005; 3rd ed. 2017, Olms), Osbaldeston & Wood (2000, Ibidis). These may be consulted by humans for checking but must not be copied into the repo.
- Goodyer/Gunther (1655 translation; first printed 1933–34): **[VERIFY copyright status in your jurisdiction]**. Treat as do-not-ingest unless confirmed public domain.

---

## 2. Lexical resources for ancient Greek

| source_id | Resource | Use | Access / licence |
|---|---|---|---|
| `lsj` | Liddell–Scott–Jones Greek–English Lexicon (Perseus digital) | Glosses; often gives Linnaean binomials for plant names → candidate species | Perseus XML on GitHub (PerseusDL/lexica) **[VERIFY licence, expected CC BY-SA]** |
| `cltk` | Classical Language Toolkit | Lemmatisation, normalisation of Greek | `pip install cltk`, MIT |
| `odycy` | OdyCy (spaCy pipelines for ancient Greek) | Lemmatisation/POS as alternative | **[VERIFY package name and licence]** |
| `glossga` | GlossGA (BBAW, Greek–Arabic glossary) | Source metadata for Dioscorides/Galen editions and Arabic transmission | `https://glossga.bbaw.de` [verified pages exist] — reference only |

---

## 3. Botanical taxonomy and distribution

| source_id | Resource | Use | Access / licence |
|---|---|---|---|
| `gbif_backbone` | GBIF Backbone Taxonomy + species match API | Canonical names, synonyms, keys | `https://api.gbif.org/v1/species/match?name=...`; backbone is CC BY 4.0 **[VERIFY]** |
| `gbif_occ` | GBIF occurrences | Presence in East Mediterranean (geographic plausibility feature) | `https://api.gbif.org/v1/occurrence/search` with `country=GR,CY,TR` or a WKT polygon; per-record licences (CC0 / CC BY / CC BY-NC) — keep only aggregated counts |
| `wfo` | World Flora Online Plant List | Accepted names/synonymy cross-check | `https://www.worldfloraonline.org/` **[VERIFY licence]** |
| `flora_greece` | Flora of Greece Web (Dimopoulos et al. checklist, EDIT platform) | Authoritative presence in Greece, floristic regions, endemism, Greek common names | `https://portal.cybertaxonomy.org/flora-greece/` [verified]. Version V (Nov 2023): 5,959 species, 7,972 records. **[VERIFY bulk-export option and terms]** — otherwise query per taxon politely |
| `powo` | Plants of the World Online (Kew) | Native range, descriptions for morphology features | `https://powo.science.kew.org`, Python `pykew` **[VERIFY terms for descriptions]** |
| `mpns` | Kew Medicinal Plant Names Services | Maps pharmaceutical/common names to scientific names (used by Lardos et al.) | `https://mpns.science.kew.org` **[VERIFY access/terms]** |
| `wikidata_taxa` | Wikidata | Vernacular names (P1843) in Greek (`el`), IUCN status (P141), external IDs | SPARQL `https://query.wikidata.org/sparql`, CC0 |

---

## 4. Chemistry, targets, diseases

| source_id | Resource | Use | Access / licence |
|---|---|---|---|
| `coconut` | COCONUT 2.0 | Species → natural-product structures (InChIKey/SMILES), organism parts | `https://coconut.naturalproducts.net`; bulk SDF/CSV/dump; curated dataset **CC0** [verified]. Paper: NAR 2025, doi:10.1093/nar/gkae1063 |
| `lotus` | LOTUS (on Wikidata) | Referenced structure–organism pairs **with literature references (dates)** — essential for pre-cutoff chemistry features | Wikidata SPARQL (P703 "found in taxon" with references) and mirror `https://lotus.naturalproducts.net`; **CC0** [verified]. Paper: eLife 2022, doi:10.7554/eLife.70780 |
| `pubchem` | PubChem PUG-REST | Name → CID → InChIKey resolution | `https://pubchem.ncbi.nlm.nih.gov/rest/pug/`, public domain |
| `chembl` | ChEMBL (latest release) | Compound → target bioactivities with **document year** (for temporal filtering) | REST `https://www.ebi.ac.uk/chembl/api/data/` or SQLite dump from EBI FTP; CC BY-SA 3.0 **[VERIFY current release licence]** |
| `opentargets` | Open Targets Platform | Target → disease association scores | GraphQL `https://api.platform.opentargets.org/api/v4/graphql`; data downloads; CC0 **[VERIFY]** |
| `mesh` | NLM MeSH | Disease vocabulary for mapping ancient conditions | `https://id.nlm.nih.gov/mesh/` (RDF/SPARQL, lookup API); public domain |
| `mondo` | MONDO via EBI OLS4 | Cross-ontology disease IDs | `https://www.ebi.ac.uk/ols4/api`, CC BY 4.0 |
| `icpc2` | ICPC-2 chapters | Coarse condition categories for historical claims (Staub et al. 2015 discuss disease classification for ethnopharmacology; **[VERIFY]** that they recommend ICPC-2 before citing it that way) | WHO-FIC / WONCA **[VERIFY licence; may require using chapter labels only]** |

---

## 5. Evidence and time stamps (for the backtest)

| source_id | Resource | Use | Access |
|---|---|---|---|
| `pubmed` | NCBI E-utilities (ESearch/ESummary/EFetch) | First year a species–condition pair appears in pharmacological literature; research-effort counts before cutoff | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`; requires `email`; API key raises limit to 10 req/s |
| `europepmc` | Europe PMC REST | Cross-check counts; full-text mention search | `https://www.ebi.ac.uk/europepmc/webservices/rest/` |
| `ctgov` | ClinicalTrials.gov API v2 | Optional "clinical" tier of evidence | `https://clinicaltrials.gov/api/v2/` |

---

## 6. Modern Greek ethnobotany (endpoint)

| source_id | Study | Access |
|---|---|---|
| `eth_naegean` | Axiotis, Halabalaki & Skaltsounis 2018, *Front. Pharmacol.* 9:409, doi:10.3389/fphar.2018.00409 — 109 species, 52 families | Open access; Supplementary Table 1 [verified article] |
| `eth_pelion` | Tsioutsiou, Cheilari & Aligiannis 2023, *Front. Pharmacol.* 14:1225580, doi:10.3389/fphar.2023.1225580 — skin ailments, Mount Pelion | Open access [verified article] |
| `eth_milos` | Perouli & Bareka 2022, *Mediterranean Botany* 43:e75357 — Milos, 16th–21st c. | Open access [verified article] |
| `eth_crete` | Skoula et al. 2009/2010 (Crete) | **[VERIFY availability]** |
| `eth_epirus` | Vokou et al. 1993 (Zagori); Malamas & Marselos 1992 | **[VERIFY availability]** |

Extract tables manually or with a table parser, then have a human check a 10% sample. Record species, part, preparation, use and informant counts.

---

## 7. Conservation

| source_id | Resource | Use | Access |
|---|---|---|---|
| `iucn` | IUCN Red List API v4 | Global/European status | Token required; non-commercial terms **[VERIFY]** |
| `wikidata_iucn` | Wikidata P141 | Lightweight fallback | CC0 |
| `flora_greece_endemic` | Flora of Greece web endemism flags | Greek endemics | as above |

---

## 8. LLM

| source_id | Use | Notes |
|---|---|---|
| `llm_claude` | Extraction, normalisation, candidate proposal, machine translation of Greek passages | Anthropic API; temperature 0; JSON schema; cached; model ID logged. Never used as a plausibility oracle in the backtest. |

---

## Download / access checklist (Phase 0)

- [ ] First1KGreek sparse clone; confirm `tlg0656.tlg001` exists; note commit hash.
- [ ] Confirm Galen and Paul availability (or choose fallbacks).
- [ ] Download Lardos figshare files; record licence.
- [ ] COCONUT CSV dump; record version/date.
- [ ] LOTUS SPARQL test query returns pairs with reference DOIs.
- [ ] ChEMBL SQLite (or REST) works; record release number.
- [ ] Open Targets GraphQL test query.
- [ ] NCBI API key works (10 req/s).
- [ ] Flora of Greece access mode confirmed.
- [ ] Modern Greek study supplementary tables downloaded.
