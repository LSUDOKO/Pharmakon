"""Greek vocabulary matcher built from config/conditions_lexicon.yaml."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from pharmakon.common import load_yaml
from pharmakon.names.normalize import match_key

TOKEN = re.compile(r"[\wͰ-Ͽἀ-῿᾽᾿’ʼ᾽]+")


@dataclass(frozen=True)
class Entry:
    stem: str
    value: str
    extra: tuple[tuple[str, Any], ...] = ()
    exact: frozenset[str] = frozenset()
    exclude: tuple[str, ...] = ()

    def matches(self, key: str) -> bool:
        if self.exact:
            return key in self.exact
        return key.startswith(self.stem) and not key.startswith(self.exclude)

    def get(self, name: str, default: Any = None) -> Any:
        return dict(self.extra).get(name, default)


@dataclass
class Lexicon:
    conditions: list[Entry] = field(default_factory=list)
    parts: list[Entry] = field(default_factory=list)
    preparations: list[Entry] = field(default_factory=list)
    routes: list[Entry] = field(default_factory=list)


def _entries(rows: list[dict[str, Any]], value_key: str) -> list[Entry]:
    out = []
    for r in rows:
        extra = tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in r.items() if k not in {"stem", value_key, "exact", "exclude"})
        out.append(Entry(
            stem=match_key(r["stem"]),
            value=r[value_key],
            extra=extra,
            exact=frozenset(match_key(x) for x in r.get("exact", []) or []),
            exclude=tuple(match_key(x) for x in r.get("exclude", []) or []),
        ))
    # Longest stem first so the most specific entry wins.
    return sorted(out, key=lambda e: -len(e.stem))


@lru_cache(maxsize=1)
def lexicon() -> Lexicon:
    y = load_yaml("conditions_lexicon.yaml")
    extra: list[dict[str, Any]] = []
    try:  # LLM-proposed extension (from out-of-lexicon LLM claims); MeSH still verified by lookup.
        extra = [{**r, "llm_proposed": True} for r in load_yaml("conditions_lexicon_llm.yaml").get("conditions", [])]
    except FileNotFoundError:
        pass
    return Lexicon(
        conditions=_entries(y["conditions"] + extra, "en"),
        parts=_entries(y["plant_parts"], "part"),
        preparations=_entries(y["preparations"], "en"),
        routes=_entries(y["routes"], "route"),
    )


def tokens(text: str) -> list[tuple[str, str]]:
    """Return (surface form, match key) pairs."""
    return [(m.group(0), match_key(m.group(0))) for m in TOKEN.finditer(text)]


def first_match(key: str, entries: list[Entry]) -> Entry | None:
    for e in entries:
        if e.matches(key):
            return e
    return None


def find_all(text: str, entries: list[Entry]) -> list[tuple[str, Entry]]:
    hits = []
    for surface, key in tokens(text):
        e = first_match(key, entries)
        if e is not None:
            hits.append((surface, e))
    return hits


def pilot_stems() -> list[str]:
    return [e.stem for e in lexicon().conditions if e.get("pilot")]
