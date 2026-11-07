import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ui import gold_table, highlight, page, perseids_url, table

from pharmakon.names.normalize import match_key, transliterate

page("Ancient Name Explorer")
st.title("Ancient Name Explorer")
clusters, post, passages, claims = table("name_clusters"), table("id_posterior"), table("passages"), table("claims_dmm")
expl, pers, modern = table("id_explanations"), table("persistence"), table("modern_studies")

post_cl = post[post["unit_kind"] == "cluster"]
names = clusters[["cluster_id", "chapter_id", "lemma"]].copy()
names["translit"] = names["lemma"].map(transliterate)
species = post_cl.dropna(subset=["accepted_name"]).groupby("unit_id")["accepted_name"].apply(lambda s: " | ".join(s))
names["species"] = names["cluster_id"].map(species).fillna("")

q = st.text_input("Search by Greek (accent-insensitive), transliteration or modern species", "ἀψίνθιον")
k = match_key(q)
mask = (names["lemma"].map(match_key).str.contains(k, regex=False) | names["translit"].str.contains(q.lower(), regex=False)
        | names["species"].str.lower().str.contains(q.lower(), regex=False)) if q else names["cluster_id"].notna()
hits = names[mask]
if hits.empty:
    st.info("No matching name.")
    st.stop()
label = {r.cluster_id: f"{r.lemma} — {r.chapter_id} ({r.translit})" for r in hits.itertuples()}
cid = st.selectbox("Name", list(label), format_func=label.get)
row = clusters.set_index("cluster_id").loc[cid]

left, right = st.columns([1.15, 1])
with left:
    st.markdown(f"### {row['lemma']}  <span class='small'>{row['chapter_id']}</span>", unsafe_allow_html=True)
    syn = [v["variant"] for v in row["variants"] if v["variant_source"] == "synonym_list"]
    if syn:
        st.caption("Synonym list (later addition to the text, Popa 2010): " + ", ".join(syn[:15]))
    if len(row["jc_crosswalk"]):
        st.caption("John the Physician (13th c.) names linked by Lardos et al.: " + ", ".join(sorted({x["jc_name_grc"] for x in row["jc_crosswalk"]})))
    st.markdown("**Dioscorides, *De materia medica* (1st c. CE)** — evidence spans highlighted")
    cc = claims[claims["chapter_id"] == row["chapter_id"]]
    for p in passages[passages["chapter_id"] == row["chapter_id"]].itertuples():
        spans = cc.loc[cc["passage_id"] == p.passage_id, "evidence_span_grc"].tolist()
        st.markdown(f"<div class='grc'>{highlight(p.text_grc, spans)}</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='small'>`{p.cts_urn}` · [Perseids reader]({perseids_url(p.passage_id)}) · "
                    f"MT: {'(machine translation)' if isinstance(p.text_en_mt, str) else 'not generated (no LLM key configured)'}</span>",
                    unsafe_allow_html=True)
    if len(cc):
        st.markdown("**Extracted claims**")
        st.dataframe(cc[["condition_text_grc", "condition_en", "plant_part", "route", "use_group", "status"]], hide_index=True, use_container_width=True)

with right:
    st.markdown("### Identification card")
    pc = post_cl[post_cl["unit_id"] == cid].sort_values("p", ascending=False)
    pc = pc.assign(name=pc["accepted_name"].fillna("unidentified (∅)"))
    fig = go.Figure(go.Bar(x=pc["p"], y=pc["name"], orientation="h",
                           error_x=dict(type="data", symmetric=False, array=pc["p_hi"] - pc["p"], arrayminus=pc["p"] - pc["p_lo"]),
                           text=[f"{v:.2f}" for v in pc["p"]], textposition="outside"))
    fig.update_layout(height=80 + 32 * len(pc), margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(range=[0, 1], title="P(species | name), 90% bootstrap interval"),
                      yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
    top = pc.iloc[0]
    if top["taxon_key"] != "__unidentified__":
        st.markdown(f"This name rests **{top['p']:.0%}** on *{top['accepted_name']}*; "
                    + ", ".join(f"{r.p:.0%} {r.name}" for r in pc.iloc[1:4].itertuples()))
    st.caption(f"Model: {pc['method'].iloc[0]}" + (" · fewer than two verified candidates" if pc["low_candidate_coverage"].iloc[0] else ""))
    ex = expl[expl["unit_id"] == cid]
    if len(ex):
        st.markdown("**Feature contributions** (wᵢ·zᵢ; positive pushes towards the candidate)")
        wcols = [c for c in ex.columns if c.startswith("w_")]
        tab = ex.set_index(ex["taxon_key"].map(dict(zip(pc["taxon_key"], pc["name"], strict=False))))[wcols]
        tab.columns = [c[2:] for c in wcols]
        st.dataframe(tab.round(3), use_container_width=True)
        st.markdown("**Candidate sources**")
        st.dataframe(ex.assign(name=ex["taxon_key"].map(dict(zip(pc["taxon_key"], pc["name"], strict=False))))[["name", "candidate_sources", "input_names", "lit_ref_years"]],
                     hide_index=True, use_container_width=True)
    st.info("Trait-match table (f1 morphology): not computed — the Greek trait extractor needs an LLM key. "
            "Expert-coded traits (Lardos et al.) are used only as a labelled oracle ablation.", icon="ℹ️")

st.markdown("### Persistence timeline")
pr = pers[pers["cluster_id"] == cid]
if pr.empty:
    st.caption("No persistence rows (no verified candidate taxon).")
else:
    def dot(v): return "●" if v is True or (isinstance(v, float) and v >= 0.5) else ("○" if v is False or isinstance(v, float) else "–")
    ug = gold_table("lardos_uses")
    show = pd.DataFrame({"use group": pr["use_group"], "Dioscorides (1st c.)": pr["present_dmm"].map(dot),
                         "John the Physician (13th c.)": pr["present_jc"].map(lambda v: dot(v) if v is not None and not pd.isna(v) else "– (not linked)"),
                         "Modern Greek (E[attested])": pr["expected_modern"].map(lambda v: f"{dot(v)} {v:.2f}"), "pattern": pr["pattern"]})
    st.dataframe(show, hide_index=True, use_container_width=True)
    st.caption("● attested · ○ not attested · – no data. Modern = Σ P(s|n)·1[s or its genus attested with that use group].")
    tk = set(pc["taxon_key"])
    mm = modern[modern["taxon_key"].isin(tk)]
    if len(mm):
        st.markdown("**Modern field-study records for the candidates** (published tables)")
        st.dataframe(mm[["study", "accepted_name", "local_name", "plant_part", "ailment_text"]], hide_index=True, use_container_width=True)
