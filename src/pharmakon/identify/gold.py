"""Parse the Lardos et al. 2024 research data (figshare 10.17637/rh.23736189.v1, CC BY 4.0).

Outputs (data/gold/):
* ``lardos_gold``      — expert verdict per (ancient name, candidate): botanical tier + uses score.
* ``lardos_reports``   — every published identification (reference, year, study type) per candidate.
* ``lardos_oracle``    — expert-coded trait congruence (ORACLE ablation only, never a headline feature).
* ``lardos_dmm_link``  — JC name ↔ DMM name ↔ Dioscorides chapter.
* ``lardos_uses``      — JC (13th c.) and modern use groups per plant, with reference years.
  Clinical-trial / PubMed rows of Data file 10 are outcome data and are excluded on purpose.
"""

from __future__ import annotations

import re
import warnings

import pandas as pd

from pharmakon.common import RAW, now_iso
from pharmakon.link.taxonomy import clean_name
from pharmakon.names.normalize import strip_accents

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
D = RAW / "jc_lardos"
F2 = D / "Data file 2 - Plant names JC-DMM.xlsx"
F5 = D / "Data file 5 - List of candidate plants and MPNS validation.xlsx"
F10 = D / "Data file 10 - Medicinal comparative analysis.xlsx"
F11 = D / "Data file 11 - Statistical evaluation.xlsx"
TIERS = {"STRONG": 3, "MODERATE": 2, "WEAK": 1, "NOT_FOUND": 0}
USE_GROUPS = ["AN", "BS", "CV", "DE", "FV", "GI", "GY", "ID", "LG", "MA", "MC", "MN", "MS", "NC", "OC", "OP", "OT", "RE", "RL", "UR", "XY"]
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
_CAND = re.compile(r"^(.*?)\s*\((\d)\)\s*$")


def _prov(df: pd.DataFrame, method: str) -> pd.DataFrame:
    df["source_id"] = "jc_lardos"
    df["retrieved_at"] = now_iso()
    df["method"] = method
    return df


def name_key(name: str) -> str:
    return clean_name(name).lower()


def parse_final_results() -> pd.DataFrame:
    raw = pd.read_excel(F11, "Final Results (Bot Info & Uses)", header=None)
    body = raw.iloc[2:].reset_index(drop=True)
    cols = {12: "STRONG", 13: "MODERATE", 14: "WEAK", 15: "NOT_FOUND"}
    rows = []
    for r in body.itertuples(index=False):
        if pd.isna(r[1]):
            continue
        for ci, tier in cols.items():
            cell = r[ci]
            if pd.isna(cell):
                continue
            for line in str(cell).split("\n"):
                line = line.strip()
                if not line:
                    continue
                m = _CAND.match(line)
                cname, uses = (m.group(1), int(m.group(2))) if m else (line, None)
                rows.append({
                    "jc_lemma_tag": r[0], "jc_id": r[1], "jc_name_grc": r[3], "jc_name_translit": str(r[4]).strip(),
                    "dmm_id": r[5], "dmm_name_grc": r[6], "candidate_name": cname.strip(),
                    "candidate_key": name_key(cname), "bot_tier": tier, "bot_tier_rank": TIERS[tier],
                    "uses_score": uses,
                })
    df = pd.DataFrame(rows)
    df["gold_id"] = df["dmm_id"]
    df["expert_score"] = df["bot_tier_rank"] * 10 + df["uses_score"].fillna(0)
    best = df.groupby("gold_id")["expert_score"].transform("max")
    df["is_expert_top"] = df["expert_score"].eq(best) & df["bot_tier_rank"].gt(0)
    conf = df.groupby("gold_id")["bot_tier_rank"].transform("max")
    df["expert_confidence"] = conf.map({v: k for k, v in TIERS.items()})
    # A name whose best candidate is only WEAK / not found is an expert "unidentified" case.
    df["expert_unidentified"] = conf.le(1)
    return _prov(df, "lardos_final_results_parse_v1")


def parse_candidates() -> pd.DataFrame:
    fc = pd.read_excel(F5, "Final Candidate Plants List")
    fc = fc.rename(columns={"Lemma tag": "jc_lemma_tag", "JC_ID": "jc_id", "DMM plant name": "dmm_name_grc",
                            "DMM name (Beck, 2005)": "dmm_name_beck", "CP_ID": "cp_id",
                            "Accepted_Family": "family_kew", "Accepted_Name": "accepted_name_kew"})
    fc["candidate_key"] = fc["accepted_name_kew"].map(name_key)
    keep = ["jc_lemma_tag", "jc_id", "dmm_name_grc", "dmm_name_beck", "cp_id", "family_kew", "accepted_name_kew", "candidate_key"]
    return _prov(fc[keep].copy(), "lardos_candidates_parse_v1")


def parse_reports() -> pd.DataFrame:
    rep = pd.read_excel(F5, "Reported Candidate Plants")
    val = pd.read_excel(F5, "Kew-MPNS Validation")[["RC_ID", "Accepted_Name", "CP_ID"]]
    df = rep.merge(val, on="RC_ID", how="left")
    df = df.rename(columns={"Lemma tag": "jc_lemma_tag", "JC_ID": "jc_id", "Reported name": "reported_name",
                            "Reference": "reference", "Study Type": "study_type", "Accepted_Name": "accepted_name_kew", "CP_ID": "cp_id"})
    df["ref_year"] = df["reference"].astype(str).str.extract(r"(\d{4})")[0].astype("Int64")
    df["candidate_key"] = df["accepted_name_kew"].fillna(df["reported_name"]).map(name_key)
    keep = ["jc_lemma_tag", "jc_id", "RC_ID", "reported_name", "reference", "ref_year", "study_type", "accepted_name_kew", "cp_id", "candidate_key"]
    return _prov(df[keep].copy(), "lardos_reports_parse_v1")


def parse_oracle() -> pd.DataFrame:
    ev = pd.read_excel(F11, "Bot Info Evaluation")
    df = ev.rename(columns={"DMM_ID": "dmm_id", "CP_ID": "cp_id", "Accepted_Name": "accepted_name_kew",
                            "Overall Score": "oracle_bot_score", "Feature Categories with Negative Correlation": "oracle_neg",
                            "Feature Categories with Insufficient Data": "oracle_insufficient"})
    df["candidate_key"] = df["accepted_name_kew"].map(name_key)
    df["gold_id"] = df["dmm_id"]
    keep = ["gold_id", "cp_id", "candidate_key", "oracle_bot_score", "oracle_neg", "oracle_insufficient"]
    return _prov(df[keep].copy(), "lardos_oracle_expert_traits_v1")


def parse_dmm_link() -> pd.DataFrame:
    lk = pd.read_excel(F2, "Linking JC with DMM plant names")
    lk.columns = [str(c).strip() for c in lk.columns]
    df = lk.rename(columns={"JC plant name": "jc_name_grc", "JC plant name transcribed": "jc_name_translit", "Lemma tag": "jc_lemma_tag",
                            "Connection with DMM": "connection", "DMM plant name": "dmm_name_grc", "DMM chapter": "dmm_chapter_ref",
                            "Category DMM plant name": "dmm_category"})
    def to_ch(ref: object) -> str | None:
        m = re.match(r"\s*([IVΙ]+)\s*,\s*(\d+)", str(ref).replace("Ι", "I"))
        return f"dmm:{ROMAN.get(m.group(1), 0)}.{m.group(2)}" if m else None
    df["dmm_chapter_id"] = df["dmm_chapter_ref"].map(to_ch)
    df["dmm_name_key"] = df["dmm_name_grc"].astype(str).map(lambda s: strip_accents(s).strip(" ?"))
    keep = ["jc_lemma_tag", "jc_name_grc", "jc_name_translit", "connection", "dmm_name_grc", "dmm_name_key", "dmm_chapter_ref", "dmm_chapter_id", "dmm_category"]
    return _prov(df[keep].copy(), "lardos_link_parse_v1")


def parse_uses() -> pd.DataFrame:
    h = pd.read_excel(F10, "Historical vs. Modern data")
    h.columns = [str(c).strip() for c in h.columns]
    h = h[h["Reference type"].isin(["Historical", "Herbal med", "Ethnobot", "Ethnobot CY"])].copy()
    rows = []
    for r in h.to_dict("records"):
        groups = [g for g in USE_GROUPS if g in r and isinstance(r[g], str) and r[g].strip().lower() == "x"]
        ref = str(r.get("Reference") or "")
        year = re.search(r"(\d{4})", ref)
        historical = r["Reference type"] == "Historical"
        for g in groups:
            rows.append({
                "dmm_name_beck": str(r["JC plant name"]).strip(),
                "node": "jc" if historical else "modern",
                "reference_type": r["Reference type"],
                "reference": ref,
                "ref_year": int(year.group(1)) if year else (1300 if historical else None),
                "plant_name": None if historical else r.get("Plant"),
                "candidate_key": None if historical else name_key(str(r.get("Plant"))),
                "plant_part": r.get("Plant part used"),
                "use_group": g,
            })
    return _prov(pd.DataFrame(rows), "lardos_uses_parse_v1")


def gold_chapter_map(gold_df: pd.DataFrame, link: pd.DataFrame) -> pd.DataFrame:
    """Map each gold name (often a sub-type, e.g. ``αριστολοχεία: στρογγύλη``) to its DMM chapter."""
    lk = link[link["dmm_chapter_id"].notna()].copy()
    lk["k"] = lk["dmm_name_grc"].astype(str).map(lambda s: strip_accents(s).split(" (")[0].split(",")[0].strip(" ?"))
    rows = []
    for g in gold_df.drop_duplicates("gold_id").to_dict("records"):
        full = strip_accents(g["dmm_name_grc"]).replace(":", " ").replace(",", " ")
        toks = full.split()
        base = toks[0] if toks else ""
        cand = lk[lk["jc_lemma_tag"] == g["jc_lemma_tag"]]
        hit = cand[cand["k"] == " ".join(toks)]
        if hit.empty:
            hit = cand[cand["k"].str.split().str[0] == base]
            if hit["dmm_chapter_id"].nunique() > 1 and len(toks) > 1:
                q = [t for t in toks[1:] if len(t) > 3]
                better = hit[hit["k"].map(lambda k, q=q: any(t[:4] in k for t in q))]
                hit = better if not better.empty else hit
        if hit.empty:
            hit = cand
        rows.append({
            "gold_id": g["gold_id"],
            "dmm_lemma_base": base,
            "dmm_chapter_id": hit["dmm_chapter_id"].iloc[0] if len(hit) else None,
            "chapter_link_method": "lardos_file2" if len(hit) else "unlinked",
        })
    return pd.DataFrame(rows)
