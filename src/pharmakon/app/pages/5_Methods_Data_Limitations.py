import streamlit as st
from ui import ROOT, page

page("Methods, Data & Limitations")
st.title("Methods, data & limitations")
for f, title in [("docs/limitations.md", "Limitations"), ("docs/licences.md", "Licences"), ("docs/source_verification.md", "Source verification"),
                 ("docs/decisions.md", "Decision log")]:
    p = ROOT / f
    with st.expander(title, expanded=title == "Limitations"):
        st.markdown(p.read_text(encoding="utf-8") if p.exists() else f"`{f}` not found.")
st.markdown("#### How to cite")
st.code("Pharmakon (2026). An uncertainty-aware map of Greek and Byzantine pharmacology. https://github.com/LSUDOKO/Pharmakon", language="text")
