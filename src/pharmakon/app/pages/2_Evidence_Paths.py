import plotly.graph_objects as go
import streamlit as st
from ui import page, table

page("Evidence Paths")
st.title("Evidence paths: Taxon → Compound → Target → Disease")
paths, post, leads = table("evidence_paths"), table("id_posterior"), table("leads")
if paths.empty:
    st.info("No evidence paths in this data version.")
    st.stop()
taxa = post.dropna(subset=["accepted_name"]).drop_duplicates("taxon_key").set_index("taxon_key")["accepted_name"]
paths = paths.assign(species=paths["taxon_key"].map(taxa))
sp = st.selectbox("Species", sorted(paths["species"].dropna().unique()))
sub = paths[paths["species"] == sp]
dis = st.selectbox("Claimed condition (MeSH)", sorted(sub["mesh_id"].unique()))
sub = sub[sub["mesh_id"] == dis]
mode = st.radio("Path strength", ["weighted by identification probability", "top-1 identity only"], horizontal=True)
pc = post[(post["taxon_key"] == sub["taxon_key"].iloc[0]) & (post["unit_kind"] == "cluster")]
p_species = float(pc["p"].max()) if len(pc) else 0.0
is_top1 = bool(len(pc)) and any(post[post["unit_id"] == u].sort_values("p").iloc[-1]["taxon_key"] == sub["taxon_key"].iloc[0] for u in pc["unit_id"])
w = p_species if mode.startswith("weighted") else float(is_top1)
st.markdown(f"P(*{sp}* | ancient name) = **{p_species:.2f}** · top-1 identity: **{'yes' if is_top1 else 'no'}** · multiplier used: **{w:.2f}**")
sub = sub.assign(weighted_strength=sub["path_strength"] * w).sort_values("weighted_strength", ascending=False)
labels, idx = [], {}
def node(x):
    if x not in idx:
        idx[x] = len(labels)
        labels.append(x)
    return idx[x]
src, dst, val = [], [], []
top = sub.head(40)
for r in top.itertuples():
    a, b, c, d = node(sp), node(r.inchikey[:14]), node(r.target_chembl_id), node(r.disease_name)
    for s, t in ((a, b), (b, c), (c, d)):
        src.append(s); dst.append(t); val.append(max(r.weighted_strength, 0.01))
fig = go.Figure(go.Sankey(node=dict(label=labels, pad=12), link=dict(source=src, target=dst, value=val)))
fig.update_layout(height=520, margin=dict(l=5, r=5, t=5, b=5))
st.plotly_chart(fig, use_container_width=True)
st.dataframe(sub[["inchikey", "molecule_chembl_id", "target_chembl_id", "disease_name", "ct_tier", "pchembl", "td_tier", "ot_score",
                  "compound_ref_year", "activity_doc_year", "path_strength", "weighted_strength"]], hide_index=True, use_container_width=True)
st.caption("Tiers: ChEMBL mechanism T1, pChEMBL≥7 T2, ≥6 T3, ≥5 T4; Open Targets ≥0.7 T1, ≥0.4 T2, ≥0.2 T3. "
           "Path strength = weakest link. Compounds via LOTUS (Wikidata P703) with reference year.")
