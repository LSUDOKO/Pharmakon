import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ui import page, stage, table

page("Time Machine")
st.title("Time Machine — temporal backtest")
fc = stage("forecast")
if not fc.get("results"):
    st.info("Backtest has not been run in this data version.")
    st.stop()
cut = st.sidebar.selectbox("Cutoff year T", sorted(fc["results"], key=int), index=len(fc["results"]) - 1)
res = fc["results"][cut]
st.markdown(f"Train on pairs unsupported at **{int(cut) - 5}** (labels in ({int(cut) - 5}, {cut}]); test on pairs unsupported at **{cut}** "
            f"(label: first PubMed support in ({cut}, {fc['t_end']}]). Train rows {res['train_rows']} ({res['train_positives']} positive).")
t = pd.DataFrame(res["test"]).T
ci = res.get("bootstrap_ci", {})
fig = go.Figure()
for m in ["random", "popularity_raw", "popularity", "chemistry", "history", "history+popularity", "full", "full_gbm", "shuffled_history+popularity"]:
    if m in t.index and pd.notna(t.loc[m].get("auprc")):
        lo, hi = ci.get(m, [None, None])
        fig.add_bar(x=[m], y=[t.loc[m, "auprc"]], error_y=dict(type="data", symmetric=False, array=[hi - t.loc[m, "auprc"]] if hi else [0],
                    arrayminus=[t.loc[m, "auprc"] - lo] if lo else [0]), name=m)
fig.add_hline(y=t.loc["random", "base_rate"], line_dash="dot", annotation_text="base rate")
fig.update_layout(showlegend=False, yaxis_title="AUPRC (95% cluster-bootstrap CI)", height=420)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(t[[c for c in ["n", "positives", "base_rate", "auroc", "auprc", "auprc_lift", "p_at_20", "p_at_50", "p_at_100"] if c in t.columns]], use_container_width=True)
if "delta_auprc_histpop_minus_pop" in ci:
    st.markdown(f"**Does history add signal beyond popularity?** ΔAUPRC 95% CI = {ci['delta_auprc_histpop_minus_pop']} "
                f"(share of bootstrap samples with Δ ≤ 0: {ci.get('p_delta_auprc_le_0')}).")
st.markdown("**Leakage control** — shuffled history: AUPRC "
            f"{t.loc['shuffled_history+popularity'].get('auprc')} vs history+popularity {t.loc['history+popularity'].get('auprc')}.")
hits = table("forecast_hits")
h = hits[hits["cutoff"] == int(cut)]
h = h.assign(pubmed=h["query_string"].map(lambda q: "https://pubmed.ncbi.nlm.nih.gov/?term=" + __import__("urllib.parse").parse.quote(q)))
st.markdown("#### Hits (ranked highly at T, later gained support)")
st.dataframe(h[h["label"] == 1][["accepted_name", "mesh_label", "score_histpop", "first_support_year", "pubmed"]],
             column_config={"pubmed": st.column_config.LinkColumn("PubMed query")}, hide_index=True, use_container_width=True)
st.markdown("#### Misses — no support found (yet)")
st.dataframe(h[h["label"] == 0][["accepted_name", "mesh_label", "score_histpop", "pubmed"]],
             column_config={"pubmed": st.column_config.LinkColumn("PubMed query")}, hide_index=True, use_container_width=True)
st.caption(fc.get("label_note", ""))
