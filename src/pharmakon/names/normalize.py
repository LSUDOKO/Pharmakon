"""Greek normalisation, accent stripping and Greek → Latin transliteration.

Pure ``unicodedata``; no external NLP models (CLTK is too heavy for this pilot, see docs/decisions.md).
"""

from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_ROUGH = "̔"  # combining reversed comma above (dasia / rough breathing)
_FINAL_SIGMA = "ς"

_LETTERS = {
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "e", "θ": "th",
    "ι": "i", "κ": "k", "λ": "l", "μ": "m", "ν": "n", "ξ": "x", "ο": "o", "π": "p",
    "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "y", "φ": "ph", "χ": "ch", "ψ": "ps",
    "ω": "o", "ϝ": "w",
}
_DIGRAPHS = [("γγ", "ng"), ("γκ", "nk"), ("γξ", "nx"), ("γχ", "nch"), ("ου", "ou"), ("αυ", "au"), ("ευ", "eu"), ("ηυ", "eu")]
# Latinised spelling, as used in Linnaean epithets (κ→c, αι→ae, οι→oe, ει→i, ου→u, -ον→-um).
_LATIN_DIGRAPHS = [("αι", "ae"), ("οι", "oe"), ("ει", "i"), ("ου", "u"), ("γγ", "ng"), ("γκ", "nc"), ("αυ", "au"), ("ευ", "eu")]


def nfc(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize("NFC", s)


def collapse_ws(s: str) -> str:
    return _WS.sub(" ", s).strip()


def norm_text(s: str) -> str:
    """NFC + whitespace collapse. This is the canonical stored form of Greek text."""
    return collapse_ws(nfc(s))


def strip_accents(s: str) -> str:
    """Accent/breathing-insensitive lowercase form used for matching."""
    if not isinstance(s, str):
        return ""
    d = unicodedata.normalize("NFD", s)
    d = "".join(ch for ch in d if unicodedata.category(ch) != "Mn")
    d = d.replace("ϲ", "σ").lower().replace(_FINAL_SIGMA, "σ")
    return collapse_ws(unicodedata.normalize("NFC", d))


def match_key(s: str) -> str:
    """Accent-stripped, punctuation-free key for fuzzy lemma matching."""
    s = strip_accents(s)
    s = re.sub(r"[^\w\s]", " ", s)
    return collapse_ws(re.sub(r"\d", " ", s))


def _has_rough(word: str) -> bool:
    d = unicodedata.normalize("NFD", word)
    head = d[:4]
    return _ROUGH in head


def transliterate(s: str, latinise: bool = False) -> str:
    """Greek → Latin letters. ``latinise`` follows Linnaean conventions (κ→c, -ον→-um)."""
    out_words = []
    for word in nfc(s).split():
        rough = _has_rough(word)
        w = strip_accents(word)
        w = re.sub(r"[^\w]", "", w)
        if not w:
            continue
        if latinise:
            w = re.sub(r"ον$", "um", w)
            w = re.sub(r"ος$", "us", w)
        pairs = _LATIN_DIGRAPHS if latinise else _DIGRAPHS
        for g, lat in pairs:
            w = w.replace(g, lat)
        w = w.replace("ρρ", "rrh").replace("ῥ", "rh")
        res = []
        for i, ch in enumerate(w):
            lat = _LETTERS.get(ch, ch)
            if latinise and ch == "κ":
                lat = "c"
            if latinise and ch == "υ":
                lat = "y"
            if ch == "ρ" and i == 0:
                lat = "rh"
            res.append(lat)
        t = "".join(res)
        if rough and t and t[0] in "aeiouy":
            t = "h" + t
        out_words.append(t)
    return " ".join(out_words)


def is_greek(s: str) -> bool:
    return any("Ͱ" <= ch <= "Ͽ" or "ἀ" <= ch <= "῿" for ch in s)
