"""Pharmakon explorer — Home. Run: streamlit run src/pharmakon/app/Home.py"""

import streamlit as st
from ui import page, stage

page("Home")
st.title("Pharmakon")
st.subheader("An uncertainty-aware, 2,000-year map of Greek and Byzantine pharmacology")
st.markdown(
    "Pharmakon reads Dioscorides' *De materia medica* (1st c. CE, Wellmann edition), extracts every therapeutic claim "
    "with a **verbatim, verified Greek span**, estimates which modern plant each ancient name refers to **with a calibrated "
    "probability** (evaluated against the expert gold set of Lardos et al. 2024), traces each use to John the Physician "
    "(13th c.) and modern Greek ethnobotany, and tests with a **strict time split** whether history predicts later "
    "pharmacological support. Uncertainty is carried into every lead.")

ing, ext, idn, fc = stage("ingest-texts"), stage("extract-claims"), stage("identify"), stage("forecast")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Passages processed", f"{ing.get('passages', '—'):,}" if ing else "—")
c2.metric("Claims extracted (span-verified)", f"{ext.get('claims_kept', '—'):,}" if ext else "—",
          help=f"Exact span verification rate: {ext.get('exact_span_verified_rate_kept')}")
c3.metric("Names identified (top-1 is a taxon)", idn.get("clusters_top1_is_taxon", "—"),
          help=f"Mean top-1 probability across {idn.get('clusters_scored')} names: {idn.get('mean_top1_probability_clusters')}")
auprc = "—"
if fc.get("results"):
    last = fc["results"][max(fc["results"], key=int)]["test"]
    auprc = f"{last['history+popularity'].get('auprc', float('nan')):.3f} vs {last['popularity'].get('auprc', float('nan')):.3f}"
c4.metric("Backtest AUPRC (history+pop vs pop, last cutoff)", auprc)

if idn.get("results"):
    r = idn["results"]
    st.markdown("#### Identification vs expert gold (leave-one-name-out, 61 names)")
    st.table({k: {"top-1": v["top1"]["mean"], "top-1 95% CI": str(v["top1"]["ci95"]), "Brier": v["brier"]["mean"], "ECE": v["ece"]}
              for k, v in r.items() if "top1" in v})

st.markdown("#### Pipeline")
st.graphviz_chart("""
digraph { rankdir=LR; node [shape=box, style=rounded, fontsize=10];
 TEI [label="Dioscorides TEI\\n(First1KGreek)"]; X [label="Claims +\\nverified spans"]; M [label="MeSH / ICPC-2 /\\nuse groups"];
 N [label="Name clusters\\n(+JC crosswalk)"]; I [label="P(species | name)\\nconditional logit"]; C [label="LOTUS → ChEMBL\\n→ Open Targets"];
 P [label="Persistence\\nDMM→JC→modern"]; E [label="PubMed labels\\n(per year)"]; F [label="Temporal backtest"]; L [label="Leads × P(species)"];
 TEI->X->M; X->N->I; I->C; I->P; M->P; I->E; M->E; P->F; C->F; E->F; F->L; I->L }
""")
st.caption("Every number on this page is read from reports/stages/*.json, written by the pipeline.")
