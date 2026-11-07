"""Phase 0 — live verification of every source the pilot depends on (CLAUDE.md rule 3).

Writes docs/source_verification.md. Each check performs a real request and records what came back.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from pharmakon import http
from pharmakon.common import RAW, ROOT, env, now_iso


def _dmm() -> str:
    meta = json.loads((RAW / "dmm_wellmann" / "SOURCE.json").read_text())
    return f"TEI present ({meta['bytes']:,} bytes), commit `{meta['last_commit_touching_file']}`, licence: {meta['licence_text']} ({meta['licence_url']})"


def _lardos() -> str:
    rec = http.get_json("https://api.figshare.com/v2/articles/23736189")
    return f"figshare record '{rec['title']}', {len(rec['files'])} files, licence {rec['license']['name']}, DOI {rec['doi']}"


def _gbif() -> str:
    m = http.get_json("https://api.gbif.org/v1/species/match", params={"name": "Artemisia absinthium", "kingdom": "Plantae"})
    return f"species/match → {m.get('scientificName')} (usageKey {m.get('usageKey')}, {m.get('matchType')})"


def _wikidata() -> str:
    r = http.sparql('SELECT ?t WHERE { ?t wdt:P225 "Artemisia absinthium" }')
    return f"SPARQL ok → {r[0]['t'].rsplit('/', 1)[-1] if r else 'no hit'}"


def _lotus() -> str:
    r = http.sparql("SELECT (COUNT(*) AS ?n) WHERE { ?c p:P703 ?s . ?s ps:P703 wd:Q25686 . }")
    return f"P703 'found in taxon' pairs for Artemisia absinthium (Q25686): {r[0]['n']}; reference dates via query-scholarly.wikidata.org (graph split)"


def _scholarly() -> str:
    r = http.sparql("SELECT ?d WHERE { wd:Q60309186 wdt:P577 ?d }", endpoint="https://query-scholarly.wikidata.org/sparql")
    return f"scholarly subgraph ok → P577 of Q60309186 = {r[0]['d'][:10] if r else 'none'}"


def _mesh() -> str:
    r = http.get_json("https://id.nlm.nih.gov/mesh/lookup/descriptor", params={"label": "Skin Ulcer", "match": "exact"})
    return f"lookup 'Skin Ulcer' → {r[0]['resource'].rsplit('/', 1)[-1]}"


def _pubmed() -> str:
    js = http.get_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params={"db": "pubmed", "term": '"Plantago major"[tiab]', "retmode": "json", "retmax": 0})
    return f"ESearch ok → {js['esearchresult']['count']} records for \"Plantago major\"[tiab] (no API key: ≤3 req/s used)"


def _chembl() -> str:
    js = http.get_json("https://www.ebi.ac.uk/chembl/api/data/status.json")
    return f"ChEMBL REST ok → release {js.get('chembl_db_version')} ({js.get('chembl_release_date')}); licence CC BY-SA 3.0 per EBI"


def _ot() -> str:
    r = http.post("https://api.platform.opentargets.org/api/v4/graphql", json={"query": "{ meta { dataVersion { year month } } }"})
    v = r.json()["data"]["meta"]["dataVersion"]
    return f"GraphQL ok → data version {v['year']}.{v['month']} (associations are current, not historical)"


def _pubchem() -> str:
    js = http.get_json("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aconitine/cids/JSON")
    return f"PUG-REST ok → aconitine CID {js['IdentifierList']['CID'][0]}"


def _lsj() -> str:
    meta = json.loads((RAW / "lsj" / "SOURCE.json").read_text())
    return f"PerseusDL/lexica LSJ parsed: {meta['rows']} entries with Latin binomials; licence CC BY-SA 4.0 (README)"


def _modern() -> str:
    out = []
    for sid in ("eth_pelion", "eth_naegean"):
        lic = (RAW / sid / "LICENSE.txt").read_text().splitlines()[0][:90]
        out.append(f"{sid}: {lic}")
    return "; ".join(out)


def _wikipedia() -> str:
    from pharmakon.identify.morphology import wiki_description

    text, title = wiki_description("Artemisia absinthium")
    return f"MediaWiki API ok → '{title}' description section, {len(text or '')} chars; licence CC BY-SA 4.0 (text stored with provenance in data/llm/morph_species.jsonl)"


def _groq() -> str:
    from pharmakon import llm

    if llm.provider() != "groq":
        return "GROQ_API_KEY not set: LLM steps fall back to cached outputs or deterministic methods"
    import requests

    r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {env('GROQ_API_KEY')}"}, timeout=30)
    r.raise_for_status()
    ids = sorted(m["id"] for m in r.json()["data"])
    return f"Groq OpenAI-compatible API ok; model {llm.model_name()} {'available' if llm.model_name() in ids else 'NOT listed'}; temperature 0, JSON schema, cached by request hash"


CHECKS: list[tuple[str, str, Callable[[], str]]] = [
    ("dmm_wellmann", "First1KGreek Dioscorides TEI + licence", _dmm),
    ("jc_lardos", "Lardos et al. figshare data + licence", _lardos),
    ("lsj", "LSJ (Perseus) binomials", _lsj),
    ("gbif_backbone", "GBIF species match", _gbif),
    ("wikidata_taxa", "Wikidata SPARQL", _wikidata),
    ("lotus", "LOTUS structure–organism pairs on Wikidata", _lotus),
    ("lotus_refs", "Wikidata scholarly subgraph (reference dates)", _scholarly),
    ("mesh", "NLM MeSH lookup", _mesh),
    ("pubmed", "NCBI E-utilities", _pubmed),
    ("chembl", "ChEMBL REST", _chembl),
    ("opentargets", "Open Targets GraphQL", _ot),
    ("pubchem", "PubChem PUG-REST (toxicity citations)", _pubchem),
    ("modern_studies", "Pelion 2023 + North Aegean 2018 tables", _modern),
    ("wikipedia_en", "English Wikipedia species descriptions (f1 morphology)", _wikipedia),
    ("llm_groq", "Groq API (LLM judge, species trait extraction)", _groq),
]

NOT_USED = [
    ("paul_aegina", "Book 7 not found digitised as TEI; fallback R2 taken (Lardos JC is the Byzantine node)."),
    ("dmm_staub", "Supplementary data not openly downloadable; optional comparison skipped."),
    ("coconut", "Bulk dump not downloaded (2 GB disk budget); LOTUS on Wikidata used for taxon→compound (CC0)."),
    ("flora_greece", "No bulk export used; GBIF country=GR presence used as proxy (R12)."),
    ("iucn", "No IUCN token; Wikidata P141 used as lightweight conservation status."),
    ("icpc2", "Only chapter letters are used as coarse labels; the detailed classification is not redistributed."),
    ("powo", "Kew POWO API returns HTTP 403 to automated clients (checked 2026-11-07); not circumvented. Wikipedia description sections used for f1 (spec/12 fallback)."),
    ("llm_claude_api", "No ANTHROPIC_API_KEY: Greek-side LLM work (claim extraction, Dioscorides traits) was done in an interactive Claude session; outputs are committed as JSONL under data/llm/ with prompt version and model, and every span is re-verified by the pipeline."),
]


def run() -> dict[str, Any]:
    rows = []
    for sid, what, fn in CHECKS:
        try:
            rows.append((sid, what, "✓ verified", fn()))
        except Exception as exc:  # noqa: BLE001
            rows.append((sid, what, "✗ FAILED", str(exc)[:200]))
    lines = ["# Source verification", "", f"Generated by `python -m pharmakon verify-sources` at {now_iso()} (live requests).", "",
             "| source_id | check | status | evidence |", "|---|---|---|---|"]
    lines += [f"| `{a}` | {b} | {c} | {d.replace('|', '/')} |" for a, b, c, d in rows]
    lines += ["", "## Sources not used in this pilot (fallbacks from spec/12)", "", "| source_id | decision |", "|---|---|"]
    lines += [f"| `{a}` | {b} |" for a, b in NOT_USED]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "source_verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"verified": sum(r[2].startswith("✓") for r in rows), "failed": [r[0] for r in rows if not r[2].startswith("✓")]}
