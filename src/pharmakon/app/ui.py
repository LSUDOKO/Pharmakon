"""Shared Streamlit helpers: data loading (read-only), banner, sidebar, Greek typography."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

PROCESSED = ROOT / "data" / "processed"
SAMPLE = ROOT / "data" / "sample"
STAGES = ROOT / "reports" / "stages"
DISCLAIMER = ("**Research hypotheses only — not medical advice.** Identifications are probabilistic. "
              "Nothing here is a recommendation to use any plant, or evidence of safety or efficacy.")
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;1,400&display=swap');
.grc { font-family: 'Noto Serif', 'GFS Didot', serif; font-size: 1.05rem; line-height: 1.6; }
.grc mark { background: #ffe9a8; color: inherit; padding: 0 2px; border-radius: 3px; }
.badge-tox { background:#b00020; color:white; padding:1px 6px; border-radius:4px; font-size:0.8rem; }
.small { font-size: 0.85rem; opacity: 0.85; }
</style>
"""


def data_dir() -> Path:
    return PROCESSED if (PROCESSED / "passages.parquet").exists() else SAMPLE


@st.cache_data(show_spinner=False)
def table(name: str) -> pd.DataFrame:
    p = data_dir() / f"{name}.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


@st.cache_data(show_spinner=False)
def gold_table(name: str) -> pd.DataFrame:
    for base in (ROOT / "data" / "gold", SAMPLE / "gold"):
        p = base / f"{name}.parquet"
        if p.exists():
            return pd.read_parquet(p)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def stage(name: str) -> dict:
    for base in (STAGES, SAMPLE / "stages"):
        p = base / f"{name}.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


def page(title: str) -> None:
    st.set_page_config(page_title=f"Pharmakon — {title}", page_icon="🌿", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.warning(DISCLAIMER)
    with st.sidebar:
        st.markdown("### Pharmakon")
        st.caption("Pilot domain: skin conditions & wounds (ICPC-2 S / Lardos use group DE)")
        ing = stage("ingest-texts")
        st.caption(f"Data version: First1KGreek commit `{str(ing.get('source_commit', '?'))[:10]}` · generated {ing.get('generated_at', '?')[:10]}")
        st.caption("Data directory: " + data_dir().name)


def perseids_url(passage_id: str) -> str:
    ref = passage_id.split(":", 1)[1].replace("dup1", "").replace("dup2", "")
    return f"https://cts.perseids.org/read/greekLit/tlg0656/tlg001/1st1K-grc1/{ref}"


def highlight(text: str, spans: list[str]) -> str:
    import html

    out = html.escape(text)
    for s in sorted(set(spans), key=len, reverse=True):
        es = html.escape(s)
        if es and es in out:
            out = out.replace(es, f"<mark>{es}</mark>", 1)
    return out
