"""First1KGreek TEI → passages. Strips the critical apparatus, keeps the main text.

Stage 1 (``ingest-texts``) of spec/05_PIPELINE_SPEC.md.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from lxml import etree

from pharmakon.names.normalize import is_greek, norm_text, strip_accents

TEI = "{http://www.tei-c.org/ns/1.0}"
NS = {"t": "http://www.tei-c.org/ns/1.0"}
DROP_TAGS = {f"{TEI}note", f"{TEI}del", f"{TEI}head", f"{TEI}gap"}
HEAD_SEP = re.compile(r"[··;:]")
DIGITS = re.compile(r"(?<!\w)\d+(?!\w)")
# Residual apparatus: Latin sigla/abbreviations or runs of Latin-script words inside Greek text.
SIGLA = re.compile(r"\b(om|libri|cf|mavult|correxi|add|transpos|codd|ras|al|RV|Dl|Di|Da)\b\.?")
LATIN_RUN = re.compile(r"(?:\b[A-Za-z]{2,}\b[\s,.;]*){2,}")


@dataclass
class Chapter:
    book: int
    chapter: str
    sections: list[tuple[str, str]] = field(default_factory=list)  # (section n, cleaned text)
    synonyms_raw: list[str] = field(default_factory=list)
    headword: str | None = None


def _remove_keep_tail(el: etree._Element) -> None:
    parent = el.getparent()
    if parent is None:
        return
    tail = el.tail or ""
    prev = el.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or "") + " " + tail
    else:
        parent.text = (parent.text or "") + " " + tail
    parent.remove(el)


def _is_nested_chapter(e: etree._Element, root: etree._Element) -> bool:
    return e is not root and e.tag == f"{TEI}div" and e.get("subtype") == "chapter"


def clean_element(el: etree._Element) -> str:
    """Return the main text of ``el`` with apparatus elements removed (works on a copy).

    Some First1KGreek chapters are (wrongly) nested inside the previous chapter; nested
    chapter divs are excluded here and parsed on their own.
    """
    el = copy.deepcopy(el)
    for nested in [e for e in el.iter() if _is_nested_chapter(e, el)]:
        nested.getparent().remove(nested)
    for bad in [e for e in el.iter() if e.tag in DROP_TAGS]:
        _remove_keep_tail(bad)
    paras = el.findall(f".//{TEI}p") or [el]
    text = " ".join(" ".join(p.itertext()) for p in paras)
    text = text.replace("|", " ")
    text = DIGITS.sub(" ", text)  # printed line/section numbers carried into the TEI
    text = re.sub(r"\s+([,.·;])", r"\1", norm_text(text))
    return norm_text(text)


def residue_flags(text: str) -> list[str]:
    flags = []
    if SIGLA.search(text):
        flags.append("sigla")
    if LATIN_RUN.search(text):
        flags.append("latin_run")
    if any(ch in text for ch in "⟨⟩[]†"):
        flags.append("editorial_brackets")
    return flags


def parse_headword(first_section: str) -> str | None:
    """Dioscorides chapters open with the drug name followed by a raised dot: ``ἀψίνθιον· ...``."""
    m = HEAD_SEP.search(first_section[:120])
    head = first_section[: m.start()].strip(" ,.") if m else ""
    if not head or len(head.split()) > 5:
        # No raised dot: the chapter opens directly with the drug name (``ἄκορον τὰ μὲν φύλλα``).
        toks = [t for t in first_section.split()[:3] if strip_accents(t) not in ARTICLES] or first_section.split()
        head = toks[0].strip(" ,.·") if toks else ""
    head = re.split(r",|\bοἱ δ", head)[0].strip(" ,.")
    toks = [t for t in head.split() if strip_accents(t) not in ARTICLES]
    if len(toks) > 1:
        second = toks[1]
        keep = second[:1].isupper() or strip_accents(second).startswith(QUALIFIERS)
        toks = toks[:2] if keep else toks[:1]
    head = " ".join(toks)
    if not head or not is_greek(head) or len(head.split()) > 5:
        return None
    return head


ARTICLES = {"ο", "η", "το", "οι", "αι", "τα", "περι", "δε", "δ", "και", "τε", "γαρ", "μεν", "ουν", "εστι", "εστιν", "του", "της", "των", "τω", "τη", "τον", "την", "εν", "ως"}
# Qualifiers that belong to a drug name (ἄμπελος ἀγρία, χελιδόνιον μέγα, ...).
QUALIFIERS = ("αγρι", "ημερ", "μεγ", "μικρ", "λευκ", "μελαν", "θαλασσ", "ορειν", "εδωδιμ", "κηπαι", "ετερ", "αρρεν", "θηλ")
_RV = re.compile(r"^\s*\d*\s*RV\s*:\s*(.*)$", re.S)


def parse_synonyms(rv_note: str) -> list[dict[str, str]]:
    """Parse an ``RV:`` synonym note: ``ἀλόη· οἱ δὲ ἀμφίβιον, ... Ῥωμαῖοι ἀλόαμ``.

    These lists are later additions to the text (Popa 2010) and are flagged ``synonym_list``.
    """
    m = _RV.match(norm_text(rv_note))
    if not m:
        return []
    body = re.sub(r"\[[^\]]*\]", " ", m.group(1))  # editor-bracketed material
    body = DIGITS.sub(" ", body)
    parts = HEAD_SEP.split(body, maxsplit=1)
    rest = parts[1] if len(parts) > 1 else parts[0]
    out = []
    for chunk in re.split(r",", rest):
        chunk = norm_text(chunk).strip(" .;")
        if not chunk:
            continue
        who = "anonymous"
        mm = re.match(r"^(οἱ δὲ|οἱ δ᾿|οἱ δ’)\s+(.*)$", chunk)
        if mm:
            name = mm.group(2)
        else:
            mm = re.match(r"^(\S+?(?:οι|ες|ται))\s+(.*)$", chunk)  # e.g. Ῥωμαῖοι, Αἰγύπτιοι, Δάκοι
            if mm and len(mm.group(2).split()) <= 4:
                who, name = mm.group(1), mm.group(2)
            else:
                name = chunk
        name = name.strip(" .;·")
        if name and is_greek(name) and len(name.split()) <= 4:
            out.append({"name": name, "attributed_to": who})
    return out


def parse_tei(path: Path) -> list[Chapter]:
    tree = etree.parse(str(path))
    chapters: list[Chapter] = []
    for book in tree.xpath('//t:div[@subtype="book"]', namespaces=NS):
        bn = int(book.get("n"))
        seen: dict[str, int] = {}
        for ch in book.xpath('.//t:div[@subtype="chapter"]', namespaces=NS):
            n = ch.get("n")
            seen[n] = seen.get(n, 0) + 1
            # A few chapter divs reuse an earlier @n (TEI encoding errors): keep them, disambiguated.
            cid = n if seen[n] == 1 else f"{n}dup{seen[n] - 1}"
            c = Chapter(book=bn, chapter=cid)
            secs = ch.xpath('t:div[@subtype="section"]', namespaces=NS)
            if secs:
                for s in secs:
                    c.sections.append((s.get("n"), clean_element(s)))
            else:
                c.sections.append(("1", clean_element(ch)))
            own = [n for n in ch.iter(f"{TEI}note") if n.xpath('ancestor::t:div[@subtype="chapter"][1]', namespaces=NS)[0] is ch]
            for note in own:
                txt = " ".join(note.itertext())
                if _RV.match(norm_text(txt)):
                    c.synonyms_raw.append(norm_text(txt))
            if c.sections:
                c.headword = parse_headword(c.sections[0][1])
            chapters.append(c)
    return chapters


def chapters_to_frames(chapters: list[Chapter], cts_base: str, work: str = "dmm", century: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, chrows = [], []
    for c in chapters:
        syns = [s for raw in c.synonyms_raw for s in parse_synonyms(raw)]
        chrows.append({
            "work": work,
            "book": c.book,
            "chapter": c.chapter,
            "chapter_id": f"{work}:{c.book}.{c.chapter}",
            "headword_grc": c.headword,
            "headword_key": strip_accents(c.headword) if c.headword else None,
            "synonyms": [s["name"] for s in syns],
            "synonym_attribution": [s["attributed_to"] for s in syns],
            "n_sections": len(c.sections),
            "text_grc": " ".join(t for _, t in c.sections),
        })
        seen: dict[str, int] = {}
        for sn, text in c.sections:
            if not text:
                continue
            seen[sn] = seen.get(sn, 0) + 1
            if seen[sn] > 1:
                sn = f"{sn}dup{seen[sn] - 1}"
            rows.append({
                "passage_id": f"{work}:{c.book}.{c.chapter}.{sn}",
                "cts_urn": f"{cts_base}:{c.book}.{c.chapter}.{sn}",
                "work": work,
                "book": c.book,
                "chapter": c.chapter,
                "section": sn,
                "chapter_id": f"{work}:{c.book}.{c.chapter}",
                "century_ce": century,
                "headword_grc": c.headword,
                "text_grc": text,
                "text_key": strip_accents(text),
                "text_en_mt": None,
                "residue_flags": residue_flags(text),
            })
    return pd.DataFrame(rows), pd.DataFrame(chrows)
