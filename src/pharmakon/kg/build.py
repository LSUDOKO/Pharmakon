"""Stage 12a — NetworkX knowledge graph (spec/04 §4) with GraphML and Neo4j-CSV export."""

from __future__ import annotations

import json

import networkx as nx
import pandas as pd

from pharmakon.common import PROCESSED, get_logger, write_stage_report

NONE = "__unidentified__"


def build_graph() -> nx.MultiDiGraph:
    G = nx.MultiDiGraph()
    claims = pd.read_parquet(PROCESSED / "claims_dmm.parquet")
    claims = claims[claims["status"] == "ok"]
    clusters = pd.read_parquet(PROCESSED / "name_clusters.parquet")
    ch2cl = dict(zip(clusters["chapter_id"], clusters["cluster_id"], strict=True))
    for c in clusters.itertuples():
        G.add_node(c.cluster_id, kind="AncientName", label=c.lemma)
    G.add_node("text:dmm", kind="Text", label="Dioscorides, De materia medica", century=1)
    for r in claims.itertuples():
        cl = ch2cl.get(r.chapter_id)
        if cl is None:
            continue
        G.add_node(r.passage_id, kind="Passage", label=r.passage_id)
        G.add_edge(r.passage_id, cl, key="MENTIONS", kind="MENTIONS")
        G.add_edge(r.passage_id, "text:dmm", key="ATTESTED_IN", kind="ATTESTED_IN")
        cc = f"ug:{r.use_group}"
        G.add_node(cc, kind="ConditionCategory", label=r.use_group)
        G.add_edge(cl, cc, key=f"CLAIMS_USE_FOR:{r.claim_id}", kind="CLAIMS_USE_FOR", part=r.plant_part or "", route=r.route or "",
                   span=r.evidence_span_grc, claim_id=r.claim_id)
        for m in r.mesh_ids:
            G.add_node(f"mesh:{m}", kind="Disease", label=m)
            G.add_edge(cc, f"mesh:{m}", key="MAPS_TO", kind="MAPS_TO")
    post = pd.read_parquet(PROCESSED / "id_posterior.parquet")
    for r in post[(post["unit_kind"] == "cluster") & (post["taxon_key"] != NONE) & (post["p"] > 0.05)].itertuples():
        G.add_node(r.taxon_key, kind="Taxon", label=r.accepted_name)
        G.add_edge(r.unit_id, r.taxon_key, key="IDENTIFIED_AS", kind="IDENTIFIED_AS", p=float(r.p), p_lo=float(r.p_lo), p_hi=float(r.p_hi))
    tc = pd.read_parquet(PROCESSED / "taxon_compounds.parquet")
    paths = pd.read_parquet(PROCESSED / "evidence_paths.parquet")
    used = set(paths["inchikey"]) if len(paths) else set()
    for r in tc[tc["inchikey"].isin(used)].itertuples():
        G.add_node(f"ik:{r.inchikey}", kind="Compound", label=r.inchikey)
        G.add_edge(r.taxon_key, f"ik:{r.inchikey}", key="CONTAINS", kind="CONTAINS", reference_year=int(r.reference_year) if pd.notna(r.reference_year) else -1)
    for r in paths.drop_duplicates(["inchikey", "target_chembl_id", "disease_id"]).itertuples():
        G.add_node(r.target_chembl_id, kind="Target", label=r.target_chembl_id)
        G.add_node(f"mesh:{r.disease_mesh}", kind="Disease", label=r.disease_name)
        G.add_edge(f"ik:{r.inchikey}", r.target_chembl_id, key="ACTS_ON", kind="ACTS_ON", tier=r.ct_tier, pchembl=float(r.pchembl),
                   doc_year=int(r.activity_doc_year) if pd.notna(r.activity_doc_year) else -1)
        G.add_edge(r.target_chembl_id, f"mesh:{r.disease_mesh}", key="ASSOCIATED_WITH", kind="ASSOCIATED_WITH", tier=r.td_tier, ot_score=float(r.ot_score))
    return G


def run() -> dict:
    log = get_logger("build-kg")
    G = build_graph()
    out = PROCESSED / "kg"
    out.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(G, out / "pharmakon.graphml")
    pd.DataFrame([{"id": n, **d} for n, d in G.nodes(data=True)]).to_csv(out / "neo4j_nodes.csv", index=False)
    pd.DataFrame([{"source": u, "target": v, **d} for u, v, d in G.edges(data=True)]).to_csv(out / "neo4j_edges.csv", index=False)
    kinds = pd.Series([d.get("kind") for _, d in G.nodes(data=True)]).value_counts().to_dict()
    ekinds = pd.Series([d.get("kind") for _, _, d in G.edges(data=True)]).value_counts().to_dict()
    summary = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "node_kinds": kinds, "edge_kinds": ekinds}
    log.info(json.dumps(summary))
    write_stage_report("build-kg", summary)
    return summary
