"""Identification features f2–f4, f6 (spec/06 §2). No feature uses pharmacological evidence.

f1 (morphology) needs an LLM trait extractor for the Greek descriptions; without an API key it is
not computed. The expert-coded trait congruence of Lardos et al. is available ONLY as a labelled
``oracle_bot`` ablation, because the gold verdict was derived from it.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from rapidfuzz import fuzz

from pharmakon.link.taxonomy import occurrence_counts, wikidata_by_gbif
from pharmakon.names.normalize import match_key, strip_accents, transliterate

FEATURES = {
    "f2_geo_log_occ": "log(1 + GBIF occurrences in GR+CY+TR)",
    "f2_present_gr": "≥1 GBIF occurrence in Greece",
    "f3_vernacular_sim": "max similarity of ancient name to modern Greek vernacular names (Wikidata P1843@el)",
    "f3_epithet_sim": "max similarity of Latinised ancient name to genus / epithet",
    "f4_lit_dmm": "log(1 + # botanical-history references proposing the taxon) [Lardos file 5]",
    "f4_lit_ethno": "log(1 + # ethnobotanical references linking the name to the taxon) [Lardos file 5]",
    "f4_lsj": "LSJ gives the binomial (1 asserted, 0.5 hedged)",
    "f6_genus_consensus": "share of the unit's candidates in the same genus",
}
GROUPS = {
    "f2": ["f2_geo_log_occ", "f2_present_gr"],
    "f3": ["f3_vernacular_sim", "f3_epithet_sim"],
    "f4": ["f4_lit_dmm", "f4_lit_ethno", "f4_lsj"],
    "f6": ["f6_genus_consensus"],
}


def _greek_sim(a: str, b: str) -> float:
    ka, kb = match_key(a), match_key(b)
    if not ka or not kb:
        return 0.0
    return max(fuzz.ratio(ka, kb), 0.9 * fuzz.partial_ratio(ka, kb)) / 100.0


def _latin_sim(greek: str, genus: str | None, epithet: str | None) -> float:
    best = 0.0
    words = [w for w in strip_accents(greek).split() if len(w) > 2]
    for w in words:
        lat = transliterate(w, latinise=True)
        plain = transliterate(w)
        for target in (genus, epithet):
            if not target:
                continue
            t = target.lower()
            best = max(best, fuzz.ratio(lat, t) / 100.0, fuzz.ratio(plain, t) / 100.0)
    return best


def enrich_taxa(cand: pd.DataFrame) -> pd.DataFrame:
    """Per-taxon external facts: occurrence counts and Greek vernacular names / IUCN status."""
    keys = sorted({int(k) for k in cand["species_key"].dropna()})
    wd = wikidata_by_gbif(keys)
    wd["gbif_key"] = wd["gbif_key"].astype(int)
    rows = []
    for k in keys:
        occ = occurrence_counts(k)
        rows.append({"species_key": k, "occ_GR": occ["GR"], "occ_CY": occ["CY"], "occ_TR": occ["TR"]})
    tx = pd.DataFrame(rows).merge(wd, left_on="species_key", right_on="gbif_key", how="left")
    tx["vernacular_el"] = tx["vernacular_el"].map(lambda v: list(v) if isinstance(v, list | np.ndarray) else [])
    return tx.drop(columns=[c for c in ("gbif_key",) if c in tx.columns])


def compute(cand: pd.DataFrame, units: pd.DataFrame, taxa: pd.DataFrame) -> pd.DataFrame:
    df = cand.merge(taxa[["species_key", "occ_GR", "occ_CY", "occ_TR", "vernacular_el", "iucn_status", "wikidata"]],
                    on="species_key", how="left")
    names = units.set_index("unit_id")["names_grc"].to_dict()
    occ = df[["occ_GR", "occ_CY", "occ_TR"]].fillna(0).sum(axis=1)
    df["f2_geo_log_occ"] = np.log1p(occ)
    df["f2_present_gr"] = (df["occ_GR"].fillna(0) > 0).astype(float)
    vs, es = [], []
    for r in df.itertuples():
        anc = list(names.get(r.unit_id, []))
        vern = r.vernacular_el if isinstance(r.vernacular_el, list) else []
        vs.append(max((_greek_sim(a, v) for a in anc for v in vern), default=0.0))
        acc = (r.accepted_name or "").split()
        es.append(max((_latin_sim(a, acc[0] if acc else None, acc[1] if len(acc) > 1 else None) for a in anc), default=0.0))
    df["f3_vernacular_sim"] = vs
    df["f3_epithet_sim"] = es
    df["f4_lit_dmm"] = np.log1p(df["lit_refs_dmm_texts"].astype(float))
    df["f4_lit_ethno"] = np.log1p(df["lit_refs_ethnobot"].astype(float))
    df["f4_lsj"] = np.where(df["lsj_asserts"], 1.0, np.where(df["lsj_hedged_only"], 0.5, 0.0))
    n = df.groupby("unit_id")["taxon_key"].transform("count")
    g = df.groupby(["unit_id", "genus"])["taxon_key"].transform("count")
    df["f6_genus_consensus"] = (g / n).where(n > 1, 0.0)
    return df


def has_value(x: object) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x))
