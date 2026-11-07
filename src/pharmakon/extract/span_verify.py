"""Verbatim evidence-span verification (CLAUDE.md rule 2)."""

from __future__ import annotations

from pharmakon.names.normalize import norm_text, strip_accents


def verify(span: str, passage: str) -> tuple[bool, bool]:
    """Return (exact, loose). Exact = NFC + whitespace-normalised substring.

    Loose = accent/case-insensitive substring; such claims are flagged ``span_verified_loose``.
    """
    if not span or not span.strip():
        return False, False
    s, p = norm_text(span), norm_text(passage)
    if s in p:
        return True, True
    return False, strip_accents(s) in strip_accents(p)
