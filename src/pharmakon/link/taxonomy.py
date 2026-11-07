"""GBIF backbone verification, occurrence counts and Wikidata vernacular names / IUCN status."""

from __future__ import annotations

import re
from functools import lru_cache

import pandas as pd

from pharmakon import http
from pharmakon.common import now_iso

GBIF = "https://api.gbif.org/v1"
EAST_MED = ("GR", "CY", "TR")
_AUTHOR = re.compile(r"\s+(\(?[A-Z][\w.\-'&\s,()]*)$")


def clean_name(name: str) -> str:
    """Strip authorities / annotations: 'Asphodelus aestivus Brot.' → 'Asphodelus aestivus'."""
    name = re.sub(r"\(.*?\)", " ", str(name))
    name = re.sub(r"\b(subsp|ssp|var|f)\.?\s+[a-z-]+", " ", name)
    toks = name.replace("×", " ").split()
    keep = []
    for t in toks:
        if not keep:
            if t[:1].isupper() and t.isalpha():
                keep.append(t)
            continue
        if re.fullmatch(r"[a-z][a-z-]+", t) and len(keep) < 2:
            keep.append(t)
        else:
            break
    return " ".join(keep)


@lru_cache(maxsize=None)
def gbif_match(name: str) -> dict:
    js = http.get_json(f"{GBIF}/species/match", params={"name": name, "kingdom": "Plantae", "verbose": "false"}) or {}
    return js


def verify_taxon(name: str) -> dict:
    """Generate-then-verify rule (spec/05 Stage 5 + R7): Plantae, EXACT or FUZZY≥90, species/genus."""
    raw = clean_name(name)
    res = {"input_name": name, "clean_name": raw, "verified": False, "reason": None}
    if not raw:
        res["reason"] = "unparseable"
        return res
    m = gbif_match(raw)
    mt, conf, rank, kingdom = m.get("matchType"), m.get("confidence", 0), m.get("rank"), m.get("kingdom")
    res.update({
        "match_type": mt, "confidence": conf, "rank": rank, "kingdom": kingdom,
        "usage_key": m.get("usageKey"), "species_key": m.get("speciesKey"), "genus_key": m.get("genusKey"),
        "accepted_name": m.get("species") if rank in {"SPECIES", "SUBSPECIES", "VARIETY", "FORM"} else m.get("canonicalName"),
        "family": m.get("family"), "genus": m.get("genus"), "status": m.get("status"),
    })
    if kingdom != "Plantae":
        res["reason"] = f"kingdom={kingdom}"
    elif mt not in {"EXACT", "FUZZY"} or (mt == "FUZZY" and conf < 90):
        res["reason"] = f"match={mt}:{conf}"
    elif rank not in {"SPECIES", "SUBSPECIES", "VARIETY", "FORM", "GENUS"}:
        res["reason"] = f"rank={rank}"
    else:
        res["verified"] = True
        res["taxon_rank"] = "GENUS" if rank == "GENUS" else "SPECIES"
        key = m.get("speciesKey") if res["taxon_rank"] == "SPECIES" else m.get("genusKey") or m.get("usageKey")
        res["taxon_key"] = f"gbif:{key}"
    return res


def verify_many(names: list[str]) -> pd.DataFrame:
    rows = [verify_taxon(n) for n in dict.fromkeys(n for n in names if isinstance(n, str) and n.strip())]
    df = pd.DataFrame(rows)
    df["source_id"] = "gbif_backbone"
    df["retrieved_at"] = now_iso()
    df["method"] = "gbif_match"
    return df


@lru_cache(maxsize=None)
def occurrence_counts(taxon_key: int) -> dict[str, int]:
    """Occurrence counts per East-Mediterranean country (aggregated counts only; see licences)."""
    js = http.get_json(
        f"{GBIF}/occurrence/search",
        params=[("taxonKey", taxon_key), ("limit", 0), ("facet", "country"), *[("country", c) for c in EAST_MED]],
    ) or {}
    counts = {c: 0 for c in EAST_MED}
    for facet in js.get("facets", []):
        for c in facet.get("counts", []):
            if c["name"] in counts:
                counts[c["name"]] = int(c["count"])
    return counts


def wikidata_by_gbif(gbif_keys: list[int]) -> pd.DataFrame:
    """Greek vernacular names (P1843@el), IUCN status (P141) and taxon name for GBIF keys (P846)."""
    rows = []
    keys = [str(k) for k in dict.fromkeys(gbif_keys) if k]
    for i in range(0, len(keys), 80):
        chunk = " ".join(f'"{k}"' for k in keys[i : i + 80])
        q = f"""
        SELECT ?gbif ?item ?taxonName ?vern ?iucnLabel WHERE {{
          VALUES ?gbif {{ {chunk} }}
          ?item wdt:P846 ?gbif .
          OPTIONAL {{ ?item wdt:P225 ?taxonName . }}
          OPTIONAL {{ ?item wdt:P1843 ?vern . FILTER(LANG(?vern) = "el") }}
          OPTIONAL {{ ?item wdt:P141 ?iucn . ?iucn rdfs:label ?iucnLabel . FILTER(LANG(?iucnLabel) = "en") }}
        }}"""
        for b in http.sparql(q):
            rows.append(b)
    df = pd.DataFrame(rows, columns=["gbif", "item", "taxonName", "vern", "iucnLabel"])
    if df.empty:
        return pd.DataFrame(columns=["gbif_key", "wikidata", "taxon_name", "vernacular_el", "iucn_status"])
    agg = df.groupby("gbif").agg(
        wikidata=("item", "first"),
        taxon_name=("taxonName", "first"),
        vernacular_el=("vern", lambda s: sorted({x for x in s if isinstance(x, str)})),
        iucn_status=("iucnLabel", "first"),
    ).reset_index().rename(columns={"gbif": "gbif_key"})
    agg["wikidata"] = agg["wikidata"].str.rsplit("/", n=1).str[-1]
    agg["source_id"] = "wikidata_taxa"
    agg["retrieved_at"] = now_iso()
    agg["method"] = "wikidata_sparql_P846"
    return agg
