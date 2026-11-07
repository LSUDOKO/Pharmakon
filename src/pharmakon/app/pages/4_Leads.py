import streamlit as st
from ui import page, table

page("Leads")
st.title("Leads — unsupported pairs today, weighted by P(species)")
st.caption("Hypotheses for screening prioritisation only. Never a recommendation to use any plant.")
leads = table("leads")
if leads.empty:
    st.info("No leads in this data version.")
    st.stop()
c1, c2, c3 = st.columns(3)
cond = c1.multiselect("Condition", sorted(leads["mesh_label"].unique()))
pmin = c2.slider("P(species) ≥", 0.0, 1.0, 0.2, 0.05)
hide_tox = c3.checkbox("Hide toxic taxa", value=False)
df = leads[leads["p_species"] >= pmin]
if cond:
    df = df[df["mesh_label"].isin(cond)]
if hide_tox:
    df = df[~df["toxicity_flag"]]
df = df.assign(toxicity=df["toxicity_flag"].map({True: "⚠ KNOWN TOXICITY", False: ""}), conservation=df["conservation_status"].fillna("not assessed"))
st.dataframe(df[["rank_weighted", "toxicity", "accepted_name", "mesh_label", "p_species", "score_weighted", "rank_top1_only", "path_strength",
                 "conservation", "toxicity_citation"]],
             column_config={"toxicity_citation": st.column_config.LinkColumn("PubChem hazard"), "p_species": st.column_config.ProgressColumn("P(species)", min_value=0, max_value=1)},
             hide_index=True, width="stretch")
st.download_button("Export CSV", df.drop(columns=["clusters"]).to_csv(index=False).encode(), "pharmakon_leads.csv", "text/csv")
sel = st.selectbox("Inspect a lead", df["accepted_name"] + " — " + df["mesh_label"])
if sel:
    r = df[(df["accepted_name"] + " — " + df["mesh_label"]) == sel].iloc[0]
    st.markdown(f"Ancient names: {', '.join(r['clusters'])} · JC attests use group: {bool(r['h_present_jc'])} · "
                f"modern Greek attestation: {bool(r['h_modern_attested'])} · Dioscorides claims (log1p): {r['h_n_dmm_claims']:.2f}")
    st.code(r["query_string"], language="text")
    st.caption("Open the Ancient Name Explorer and Evidence Paths pages for the identification card and the compound paths.")
