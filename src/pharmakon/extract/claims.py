"""Stage 2 — claim extraction with verbatim, verified evidence spans.

Two extractors share one output schema:
* ``rule_extract_v1`` (default, deterministic): clause-level matching of the Greek condition
  lexicon; the evidence span is the clause itself, cut from the stored passage text.
* ``llm_extract_v1`` (when ANTHROPIC_API_KEY is set and ``--llm`` is passed): Claude with the
  ``extract_v1`` prompt, temperature 0, schema-validated; every span is then verified.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

import pandas as pd

from pharmakon import llm
from pharmakon.common import now_iso
from pharmakon.extract.lexicon import find_all, lexicon, tokens
from pharmakon.extract.span_verify import verify
from pharmakon.names.normalize import strip_accents
from pharmakon.schemas import ClaimList

RULE_VERSION = "rule_extract_v1"
CLAUSE = re.compile(r"[^·.;]+[·.;]?")
# Therapeutic cues (accent-stripped stems). A clause naming a condition without any cue is
# kept as ``status="ambiguous"`` (it may describe a side effect, e.g. κεφαλαλγὲς ὄν).
CUES = (
    "προς", "αρμοζ", "αρμοδ", "ποιει", "ποιουσ", "βοηθ", "ιαται", "ιασθ", "ιωμεν", "θεραπευ",
    "αγαθ", "ωφελ", "παυ", "καθαιρ", "αγει", "αγουσ", "κινει", "ιστησ", "ιστασ", "στελλ",
    "επουλ", "κολλ", "λυει", "διαφορ", "αποκαθ", "θρυπτ", "σμηχ", "πραυν", "εκκαθ", "τηκ",
    "ξηραιν", "χρησιμ", "ποτιζ", "αφιστ", "αποτρεπ", "κατασταλ", "αναστελλ", "επιτηδει",
    "αρμοττ", "δυναται", "κωλυ", "εκβαλλ", "εκβαλ", "ανακαθαιρ", "ρυπτ", "κατασπ",
    "ιων", "ιατ", "εξαιρ", "φθειρ", "αφαιρ", "εξαγ", "μαλασσ", "λεαιν", "αποσμηχ", "επι",
)
AGENT = re.compile(r"(τικ|ωτικ)")


def substance_type_for(work: str, book: int, chapter: str) -> str:
    """Dioscorides book layout: II.1–84 animals/animal products, I.30–63 prepared oils, V wines/minerals."""
    if work != "dmm":
        return "plant"
    try:
        n = int(re.match(r"\d+", chapter).group(0))  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        return "unknown"
    if book == 2 and n < 85:
        return "animal"
    if book == 1 and 30 <= n <= 63:
        return "compound_preparation"
    if book == 5:
        if n <= 3:
            return "plant"  # V.1–3: vine, wild vine
        return "mineral" if n >= 84 else "compound_preparation"
    return "plant"


def clauses(text: str) -> list[str]:
    return [c.strip() for c in CLAUSE.findall(text) if c.strip()]


def _claim_id(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]


def rule_extract(passage: dict) -> list[dict]:
    lx = lexicon()
    text = passage["text_grc"]
    head = passage.get("headword_grc")
    head = head if isinstance(head, str) and head else "?"
    out: list[dict] = []
    current_part: str | None = None
    for cl in clauses(text):
        parts = find_all(cl, lx.parts)
        inherited = False
        if parts:
            current_part = parts[0][1].value
        else:
            inherited = current_part is not None
        conds = find_all(cl, lx.conditions)
        if not conds:
            continue
        keys = [k for _, k in tokens(cl)]
        cue = any(k.startswith(CUES) for k in keys)
        routes = find_all(cl, lx.routes)
        preps = find_all(cl, lx.preparations)
        seen: set[str] = set()
        for surface, e in conds:
            if e.value in seen:
                continue
            seen.add(e.value)
            uncertain = []
            if inherited:
                uncertain.append("plant_part")
            if current_part is None:
                uncertain.append("plant_part")
            out.append({
                "substance_name_grc": head,
                "plant_part": current_part,
                "preparation": "; ".join(dict.fromkeys(f"{s} ({p.value})" for s, p in preps)) or None,
                "route": routes[0][1].value if routes else None,
                "condition_text_grc": surface,
                "condition_en": e.value,
                "icpc2_chapter": e.get("icpc2"),
                "condition_stem": e.stem,
                "evidence_span_grc": cl,
                "uncertain_fields": sorted(set(uncertain)),
                "therapeutic_cue": cue or bool(AGENT.search(e.stem)),
            })
    return out


def llm_extract(passage: dict) -> tuple[list[dict], dict]:
    user = f"Passage {passage['cts_urn']} (headword: {passage.get('headword_grc')}):\n\n{passage['text_grc']}"
    res, meta = llm.structured("extract_v1", user, ClaimList)
    rows = []
    for c in res.claims:
        d = c.model_dump()
        d["icpc2_chapter"] = None
        d["condition_stem"] = None
        rows.append(d)
    return rows, meta


def extract(passages: pd.DataFrame, use_llm: bool = False) -> tuple[pd.DataFrame, dict]:
    rows: list[dict] = []
    stats = {"passages": int(len(passages)), "llm_calls": 0, "extractor": RULE_VERSION}
    ts = now_iso()
    for p in passages.to_dict("records"):
        if use_llm:
            raw, meta = llm_extract(p)
            version = f"llm_extract_v1:{meta['model']}"
            stats["llm_calls"] += 1
            stats["extractor"] = version
        else:
            raw, version = rule_extract(p), RULE_VERSION
        stype = substance_type_for(p["work"], int(p["book"]), str(p["chapter"]))
        for c in raw:
            exact, loose = verify(c["evidence_span_grc"], p["text_grc"])
            cue = c.get("therapeutic_cue", True)
            status = ("ok" if cue else "ambiguous") if exact else "span_mismatch"
            rows.append({
                "claim_id": _claim_id(p["passage_id"], c["condition_en"] or "", c.get("plant_part") or "", c["evidence_span_grc"]),
                "passage_id": p["passage_id"],
                "chapter_id": p["chapter_id"],
                "work": p["work"],
                "century_ce": int(p["century_ce"]),
                "substance_name_grc": c["substance_name_grc"],
                "substance_lemma": strip_accents(c["substance_name_grc"]),
                "substance_type": c.get("substance_type") if use_llm and c.get("substance_type") else stype,
                "plant_part": c.get("plant_part"),
                "preparation": c.get("preparation"),
                "route": c.get("route"),
                "condition_text_grc": c["condition_text_grc"],
                "condition_en": c.get("condition_en"),
                "condition_stem": c.get("condition_stem"),
                "icpc2_chapter": c.get("icpc2_chapter"),
                "evidence_span_grc": c["evidence_span_grc"],
                "span_verified": exact,
                "span_verified_loose": (not exact) and loose,
                "status": status,
                "uncertain_fields": c.get("uncertain_fields", []),
                "therapeutic_cue": bool(cue),
                "extractor_version": version,
                "source_id": {"dmm": "dmm_wellmann", "galen": "galen_simpl"}.get(p["work"], p["work"]),
                "retrieved_at": ts,
                "method": version,
            })
    df = pd.DataFrame(rows)
    if len(df):
        df = df.drop_duplicates(subset=["passage_id", "condition_en", "plant_part", "substance_name_grc"])
    return df, stats


def prefilter_pilot(passages: pd.DataFrame, books: Iterable[int], extra_chapters: Iterable[str] = ()) -> pd.DataFrame:
    """Pilot scope: plant books (1–4), all chapters (spec/05 Stage 2), plus gold-linked chapters."""
    extra = set(extra_chapters)
    return passages[passages["book"].isin(list(books)) | passages["chapter_id"].isin(extra)].copy()
