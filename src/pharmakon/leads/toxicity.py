"""Toxicity flags with live PubChem citations (CID + GHS hazard statements)."""

from __future__ import annotations

import re

import pandas as pd

from pharmakon import http
from pharmakon.common import load_yaml, now_iso

PUG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
VIEW = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound"


def ghs(cid: int) -> list[str]:
    js = http.get_json(f"{VIEW}/{cid}/JSON", params={"heading": "GHS Classification"})
    text = str(js or "")
    return sorted(set(re.findall(r"(H\d{3})(?: \([\d.]+%\))?: ([A-Z][^\"\[\]']{3,60})", text)))


SEVERE = {"H300", "H301", "H310", "H311", "H330", "H331", "H340", "H341", "H350", "H351", "H360", "H361", "H370", "H372"}


def build() -> pd.DataFrame:
    rows = []
    for genus, names in load_yaml("toxic_taxa.yaml")["genera"].items():
        names = names if isinstance(names, list) else [names]
        cids: list[tuple[str, int]] = []
        for nm in names:
            js = http.get_json(f"{PUG}/compound/name/{nm}/cids/JSON") or {}
            cids += [(nm, int(c)) for c in ((js.get("IdentifierList") or {}).get("CID") or [])[:3]]
        compound = names[0]
        cid, hz, severe = (cids[0][1] if cids else None), [], []
        for nm, c in cids:  # take the first name form / record with severe GHS data
            h = ghs(int(c))
            sv = [f"{a}: {t.strip()}" for a, t in h if a in SEVERE]
            if sv:
                compound, cid, hz, severe = nm, int(c), h, sv
                break
            if not hz:
                hz = h
        rows.append({"genus": genus, "marker_compound": compound, "pubchem_cid": cid,
                     "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}" if cid else None,
                     "ghs_severe_hazards": severe, "ghs_all": [f"{h}: {t.strip()}" for h, t in hz],
                     "verified": bool(cid and severe),
                     "citation_status": "pubchem_ghs_severe" if severe else "listed_in_spec; no severe GHS statement found in PubChem for marker"})
    df = pd.DataFrame(rows)
    df["source_id"], df["retrieved_at"], df["method"] = "pubchem", now_iso(), "pug_rest_name_to_cid+pug_view_ghs"
    return df
