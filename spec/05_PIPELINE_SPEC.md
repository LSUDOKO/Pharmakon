# 05 — Pipeline Specification

Every stage is a CLI command: `python -m pharmakon <stage> [--config config/pilot.yaml]`. Stages are idempotent, cached and resumable. Each prints a count summary and writes a small report to `reports/stages/<stage>.json`.

---

## Stage 1 — `ingest-texts`

**Input:** First1KGreek TEI for `tlg0656.tlg001` (plus Galen/Paul when available).

**Steps:**
1. Parse TEI with `lxml`. Walk `div[@type='textpart']` to get book / chapter / section numbers. Build the CTS URN per section.
2. Remove the critical apparatus and editorial notes: `<note>`, `<app>`, `<rdg>`, line-number `<lb/>` artefacts and siglum strings. Keep `<lem>` readings.
   - The Perseids rendering shows apparatus fragments mixed into text, so check for residual sigla. Use a regex for sequences like ` R `, ` E `, `Di`, `om.`, `libri`, `cf.`, `mavult`. Flag passages with residue rather than deleting text blindly.
3. Normalise Unicode to NFC. Normalise whitespace. Keep original accents. Store a separate accent-stripped lowercase form for matching.
4. Write `data/interim/passages.parquet`.

**Acceptance:**
- every book (1–5) present; chapter counts logged and compared against the TEI structure;
- a 20-passage manual comparison with the Perseids reader matches;
- residual-apparatus flag rate reported.

---

## Stage 2 — `extract-claims`

**Input:** passages in pilot scope.
- Pilot: chapters whose text mentions skin/wound vocabulary. Prefilter with a Greek keyword list (e.g. ἕλκ- ulcer, τραῦμα wound, λειχήν, λέπρα, ψώρα, ἐρυσίπελας, φλεγμονή, ἐπινυκτίς, ἄκροχορδών, κηλίς, ἀλφός, πυρίκαυστα burns, χοιράδες, φύματα).
- Also take all chapters of books 1–4 (plants). Record the prefilter recall on a 50-chapter manual sample.

**LLM task:** one call per passage. JSON schema = Pydantic `ClaimList`.

**Prompt template** (`config/prompts/extract_v1.md`), essentials:
```
You are annotating a passage of Dioscorides' De materia medica (Greek, Wellmann edition).
Return ONLY JSON matching the schema.
For each therapeutic statement, output:
- substance_name_grc: the headword or substance as written in the passage
- substance_type: plant | mineral | animal | compound_preparation | unknown
- plant_part, preparation (Greek words quoted + short English gloss), route
- condition_text_grc: the exact Greek words naming the condition
- condition_en: a cautious English rendering (do not modernise beyond the text)
- evidence_span_grc: an EXACT contiguous substring of the passage that states this use
Rules:
- Never invent text. If unsure, set field to null and add to "uncertain_fields".
- Do not identify the plant botanically. Do not use modern disease names unless the Greek clearly denotes them.
- One claim per (substance, part, condition) combination.
```

**Post-processing:**
- `span_verify`: NFC-normalise, collapse whitespace, then exact substring check; if that fails, try an accent-insensitive check and flag `span_verified_loose`. Archive failures.
- Deduplicate within passage.

**Acceptance:**
- ≥98% of kept claims are exactly span-verified;
- human audit of 50 random claims records precision (field-level), with target precision ≥0.85 for substance, part and condition;
- recall estimated on 10 passages fully annotated by a human.

---

## Stage 3 — `map-conditions`

**Goal:** map `condition_text_grc` / `condition_en` to:
1. an **ICPC-2 chapter** (coarse; robust for historical text), and
2. zero or more **MeSH descriptors** (fine; only when defensible).

**Method (generate-then-verify, as in DeepRoot):**
- The LLM proposes up to three English canonical names plus an ICPC-2 chapter letter, with rationale. It never outputs codes.
- Verify names against MeSH by exact or synonym match (MeSH lookup API). Unverified names are kept as text with `mesh_ids=[]`.
- Keep an explicit `no_modern_equivalent` class (e.g. humoral concepts).

**Acceptance:**
- a 50-item human audit of MeSH mappings;
- the share of claims with ≥1 verified MeSH ID is reported.

---

## Stage 4 — `cluster-names`

Group substance names into `name_clusters` within and across texts.
- Lemmatise with CLTK/OdyCy, then apply a rapidfuzz similarity on the accent-stripped form.
- Use explicit crosswalks where available: Lardos data file 2 (JC↔DMM plant names) and Dioscorides chapter headwords.
- Dioscorides chapters often list synonyms (οἱ δὲ … καλοῦσι, "some call it…"). Parse these synonym lists as variants **flagged as such**. The synonym lists are later additions (Popa 2010), so mark `variant_source="synonym_list"`.

**Acceptance:** precision of 100 sampled merges ≥0.9 (human check).

---

## Stage 5 — `identify` (details in `06_IDENTIFICATION_MODEL.md`)

1. **Candidate generation** (union, then verification):
   - Lardos candidates (file 5);
   - LSJ binomials parsed from entries;
   - Staub 2016 putative identities (if available);
   - LLM proposals (max 5, constrained to "taxa plausibly present in the Eastern Mediterranean").
   
   **Every candidate must resolve via GBIF species match** (`matchType` EXACT or FUZZY with confidence ≥90, and `rank` species or genus). Drop unresolvable candidates and log them.
2. **Feature computation** per (cluster, candidate).
3. **Model scoring → posterior** with an `__unidentified__` bucket.
4. **Calibration** (temperature or isotonic) fitted on the gold set with cross-validation.

---

## Stage 6 — `link-chemistry`, `link-targets`, `link-diseases`

- **Taxon → compounds:**
  - **COCONUT:** exact species-name match on the organism field, then genus fallback flagged `tier=genus`.
  - **LOTUS via Wikidata SPARQL:** P703 "found in taxon" on compound items, with the reference (P248 "stated in" → publication date P577) to get **reference_year**.
  - Identity is the InChIKey; collapse stereo variants on the first 14 characters for "same scaffold".
- **Compound → targets:**
  - ChEMBL by InChIKey (fallback: canonical SMILES).
  - Keep activities with `pchembl_value ≥ 5`, assay type B/F, `data_validity_comment IS NULL`.
  - Keep the **document year** (`docs.year`).
  - Tiers: mechanism (T1), pChEMBL≥7 (T2), ≥6 (T3), ≥5 or phenotypic (T4).
- **Target → disease:** Open Targets association score.
  - Tiers: ≥0.7 T1, ≥0.4 T2, ≥0.2 T3.
  - For antimicrobial targets (organism-type targets), map pathogen → infection disease via MeSH.
- Close the loop: a lead path exists when Taxon→Compound→Target→Disease and Disease ∈ mapped MeSH set of the claim (or its MeSH tree descendants).

---

## Stage 7 — `ingest-modern`, `ingest-jc`

- Parse supplementary tables of modern Greek studies into the `claims` schema with `work="modern_<site>"` and `century_ce=20/21`. Species are already binomials: resolve via GBIF directly (`p=1.0` identity, with `id_source="field_voucher"` where vouchers are reported).
- Parse Lardos file 4 (JC plant uses) into claims with `work="jc"`, `century_ce=13`.

---

## Stage 8 — `persistence`

For each (`cluster_id` or `taxon_key`, ICPC-2 chapter, optionally plant part):
- `present_in` flags per work;
- `pattern`:
  - **persisted**: in DMM and modern;
  - **modified**: same plant, different condition chapter;
  - **lost**: in DMM, absent from all later texts;
  - **novel**: modern only.
- `persistence_score` = weighted fraction of later texts attesting the claim. Weights favour independence from the immediately preceding text: Galen copies Dioscorides heavily, so down-weight near-verbatim copies detected by Greek n-gram overlap > threshold.

**Matching at species level** uses the identification posterior. The expected persistence is
E[persist] = Σ_s P(s | ancient name) · 1[s or its genus attested later for the same chapter].

---

## Stage 9 — `evidence-labels`

For each (taxon, MeSH disease) pair arising from claims:
- **PubMed query template** (store the exact string with each row):
  ```
  ("<Genus species>"[tiab] OR "<accepted synonyms>"[tiab])
  AND ("<MeSH term>"[MeSH Terms] OR "<entry terms>"[tiab])
  AND ("Plant Extracts"[MeSH] OR "Phytochemicals"[MeSH] OR pharmacology[sh] OR "drug effects"[sh])
  ```
- Use ESearch with `datetype=pdat`, `mindate`/`maxdate` by year, to get per-year counts (or retrieve PMIDs with years via ESummary).
- `first_support_year` = first year with ≥1 matching record (variants: ≥2 records; or ≥1 in vivo/clinical by publication type).
- **Audit:** a human checks 100 random positive labels (does the paper actually test the plant for that condition?) and 50 negatives. Report label precision and use it in the discussion.

---

## Stage 10 — `forecast` (details in `07_EVALUATION_PLAN.md`)

Build the `forecast_dataset` per cutoff *T* ∈ {2000, 2005, 2010, 2015}, train models, compare to baselines and write metrics plus figures.

---

## Stage 11 — `leads`

- Score current (no-cutoff) pairs that are **unsupported today**. Rank by model score × `P(species)`.
- Attach:
  - conservation status (IUCN/Wikidata, Flora of Greece endemism);
  - toxicity flag;
  - best evidence paths.
- Output `leads.parquet` and `reports/leads_top50.md` with uncertainty bars.

---

## Stage 12 — `build-kg`, `app`

- Assemble the NetworkX graph (and optional Neo4j CSV export).
- Run `streamlit run src/pharmakon/app/Home.py`.

---

## Makefile targets

```
make setup        # uv sync, pre-commit
make data         # download/clone all raw sources (Phase 0 checklist)
make pilot        # stages 1–9 on pilot scope
make forecast     # stage 10
make leads        # stage 11
make app          # stage 12
make test         # pytest
make report       # regenerate figures/tables for slides
```
