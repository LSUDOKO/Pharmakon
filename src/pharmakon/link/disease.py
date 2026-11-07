"""MeSH verification (Stage 3) and disease look-ups. Codes always come from NLM, never from us."""

from __future__ import annotations

import pandas as pd

from pharmakon import http
from pharmakon.common import now_iso
from pharmakon.extract.lexicon import lexicon

MESH = "https://id.nlm.nih.gov/mesh"


def mesh_exact(label: str) -> dict | None:
    """Exact-label MeSH descriptor match. Returns {mesh_id, label} or None."""
    js = http.get_json(f"{MESH}/lookup/descriptor", params={"label": label, "match": "exact", "limit": 5})
    for hit in js or []:
        if hit["label"].lower() == label.lower():
            return {"mesh_id": hit["resource"].rsplit("/", 1)[-1], "mesh_label": hit["label"]}
    return None


def mesh_terms(mesh_id: str) -> list[str]:
    js = http.get_json(f"{MESH}/lookup/details", params={"descriptor": mesh_id, "includes": "terms"})
    return [t["label"] for t in (js or {}).get("terms", [])]


def mesh_tree_numbers(mesh_id: str) -> list[str]:
    js = http.get_json(f"{MESH}/{mesh_id}.json")
    if not js:
        return []
    tn = js.get("treeNumber", [])
    tn = tn if isinstance(tn, list) else [tn]
    return [t.rsplit("/", 1)[-1] for t in tn]


def build_condition_map() -> pd.DataFrame:
    """One row per lexicon condition entry with verified MeSH IDs (lexicon_map_v1)."""
    rows = []
    ts = now_iso()
    for e in lexicon().conditions:
        labels = list(e.get("mesh", ()) or ())
        verified, unverified = [], []
        for lab in labels:
            hit = mesh_exact(lab)
            (verified if hit else unverified).append(hit or lab)
        rows.append({
            "condition_stem": e.stem,
            "condition_en": e.value,
            "icpc2_chapter": e.get("icpc2"),
            "pilot": bool(e.get("pilot")),
            "mesh_ids": [v["mesh_id"] for v in verified],
            "mesh_labels": [v["mesh_label"] for v in verified],
            "mesh_unverified": unverified,
            "no_modern_equivalent": not labels,
            "source_id": "mesh",
            "retrieved_at": ts,
            "method": "lexicon_map_v1+mesh_exact",
        })
    return pd.DataFrame(rows)


def mesh_details(mesh_ids: list[str]) -> pd.DataFrame:
    rows = []
    ts = now_iso()
    for mid in sorted(set(mesh_ids)):
        terms = mesh_terms(mid)
        rows.append({
            "mesh_id": mid,
            "mesh_label": terms[0] if terms else mid,
            "entry_terms": terms,
            "tree_numbers": mesh_tree_numbers(mid),
            "source_id": "mesh",
            "retrieved_at": ts,
            "method": "mesh_lookup_details",
        })
    return pd.DataFrame(rows)
