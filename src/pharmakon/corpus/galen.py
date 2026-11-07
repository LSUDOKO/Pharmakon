"""Galen, De simplicium medicamentorum temperamentis ac facultatibus (Kühn XI–XII), books 6–8 (plants).

First1KGreek ``tlg0057.tlg075.1st1K-grc1`` (CC BY-SA 4.0). In books 6–8 each drug entry opens with an
editorial heading ``[α΄. Περὶ ἀβροτόνου ...]`` (genitive). Entries are mapped to Dioscorides headwords
by accent-stripped stem matching; textual dependence on Dioscorides is measured by word 4-gram
containment (spec/05 Stage 8 copy detection).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

from pharmakon.common import RAW
from pharmakon.corpus.first1k import chapters_to_frames, parse_tei
from pharmakon.names.normalize import match_key

CTS = "urn:cts:greekLit:tlg0057.tlg075.1st1K-grc1"
URL = "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0057/tlg075/tlg0057.tlg075.1st1K-grc1.xml"
PLANT_BOOKS = (6, 7, 8)
HEAD = re.compile(r"^\[([^\]]*)\]")
GENERIC = {"ριζησ", "ριζων", "καρπου", "χυλου", "φυλλων", "σπερματοσ", "οπου", "δακρυου", "των", "του", "τησ", "ειδων", "ετερου",
           "εκατερου", "αγριασ", "αγριου", "ημερου", "και", "τε", "η", "περι"}
ENDINGS = sorted(["ου", "ησ", "ασ", "εωσ", "οσ", "ον", "η", "α", "ων", "ιδοσ", "ιου", "ιον", "ιοσ", "εοσ", "ουσ", "ιδοσ", "ακοσ", "ατοσ", "ι"], key=len, reverse=True)


def stem(w: str) -> str:
    for e in ENDINGS:
        if w.endswith(e) and len(w) - len(e) >= 3:
            return w[: -len(e)]
    return w


def heading_names(head: str) -> list[str]:
    """``α΄. Περὶ ἀβροτόνου τε καὶ ἀψινθίου`` → ['αβροτονου', 'αψινθιου'] (accent-stripped)."""
    h = match_key(head)
    h = re.sub(r"^\S{1,3}\s+", "", h)  # numeral
    h = h.split("περι", 1)[1] if "περι" in h else h
    out = []
    for part in re.split(r"\b(?:τε και|και|η)\b", h):
        toks = [t for t in part.split() if t not in GENERIC and len(t) > 2]
        if toks:
            out.append(toks[0])
    return out


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    f = RAW / "galen_simpl" / "tlg0057.tlg075.1st1K-grc1.xml"
    if not f.exists():
        from pharmakon import http

        f.parent.mkdir(parents=True, exist_ok=True)
        http.download(URL, str(f))
        (f.parent / "LICENSE.txt").write_text("CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/ — First1KGreek (OGL)\n", encoding="utf-8")
    passages, _ = chapters_to_frames(parse_tei(Path(f)), CTS, work="galen", century=2)
    passages = passages[passages["book"].isin(PLANT_BOOKS)].reset_index(drop=True)
    # Group sections into drug entries: a new entry starts at each bracketed heading.
    entry, heads, cur, cur_head = [], [], None, None
    for r in passages.itertuples():
        m = HEAD.match(r.text_grc)
        if m:
            cur, cur_head = r.passage_id, m.group(1)
        entry.append(cur or r.passage_id)
        heads.append(cur_head)
    passages["entry_id"] = entry
    passages["entry_heading"] = heads
    passages["chapter_id"] = passages["entry_id"]  # one drug entry = one "chapter" unit downstream
    passages["headword_grc"] = passages["entry_heading"].map(lambda h: " ".join(heading_names(h)[:1]) if isinstance(h, str) else None)
    entries = passages.groupby("entry_id").agg(heading=("entry_heading", "first"), text=("text_grc", " ".join), book=("book", "first")).reset_index()
    entries["names_key"] = entries["heading"].map(lambda h: heading_names(h) if isinstance(h, str) else [])
    return passages, entries


def crosswalk(entries: pd.DataFrame, dmm_chapters: pd.DataFrame) -> pd.DataFrame:
    """Map each Galen entry to Dioscorides chapters (books 1–5) by headword stem; ≥ 88 fuzzy ratio."""
    d = dmm_chapters.dropna(subset=["headword_key"]).copy()
    d["k1"] = d["headword_key"].map(lambda k: match_key(k).split()[0] if match_key(k) else "")
    d["st"] = d["k1"].map(stem)
    rows = []
    for e in entries.itertuples():
        for nm in e.names_key:
            s = stem(nm)
            exact = d[d["st"] == s]
            if len(exact):
                hit, score = exact, 100.0
            else:
                sc = d["st"].map(lambda x, s=s: fuzz.ratio(x, s))
                hit = d[sc >= 88]
                score = float(sc.max()) if len(sc) else 0.0
            for h in hit.itertuples():
                rows.append({"entry_id": e.entry_id, "galen_name_key": nm, "dmm_chapter_id": h.chapter_id, "dmm_headword": h.headword_grc,
                             "match_score": score, "copy_containment": containment(e.text, h.text_grc)})
    return pd.DataFrame(rows)


def _grams(text: str, n: int = 4) -> set[tuple[str, ...]]:
    t = match_key(text).split()
    return {tuple(t[i : i + n]) for i in range(len(t) - n + 1)}


def containment(galen_text: str, dmm_text: str) -> float:
    """Share of Galen word 4-grams that also occur in the Dioscorides chapter (0 = independent)."""
    g = _grams(galen_text)
    return round(len(g & _grams(dmm_text)) / len(g), 4) if g else 0.0
