"""Stage 6 linkers: taxon → compounds (LOTUS on Wikidata, with reference years),
compound → targets (ChEMBL, with document years), target → disease (Open Targets, with MeSH xrefs).

Every identifier comes from an API response; nothing is typed in by hand.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from pharmakon import http
from pharmakon.common import now_iso

CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
OT = "https://api.platform.opentargets.org/api/v4/graphql"


def lotus_compounds(qids: list[str], batch: int = 8) -> pd.DataFrame:
    """Structure–organism pairs (P703 'found in taxon') with their reference and its date (P577)."""
    rows = []
    for i in range(0, len(qids), batch):
        vals = " ".join(f"wd:{q}" for q in qids[i : i + batch])
        q = f"""
        SELECT ?taxon ?cmp ?ik ?ref ?date WHERE {{
          VALUES ?taxon {{ {vals} }}
          ?cmp p:P703 ?st . ?st ps:P703 ?taxon .
          ?cmp wdt:P235 ?ik .
          OPTIONAL {{ ?st prov:wasDerivedFrom ?d . ?d pr:P248 ?ref . OPTIONAL {{ ?ref wdt:P577 ?date }} }}
        }}"""
        try:
            res = http.sparql(q)
        except Exception as exc:  # noqa: BLE001 - SPARQL timeouts are logged as a gap, not fatal (R11)
            rows.append({"taxon": None, "error": str(exc)[:200], "batch": vals})
            continue
        rows.extend(res)
    df = pd.DataFrame(rows)
    if df.empty or "cmp" not in df.columns:
        return pd.DataFrame(columns=["wikidata", "compound_qid", "inchikey", "reference_qid", "reference_year"])
    df = df.dropna(subset=["cmp"])
    df["wikidata"] = df["taxon"].str.rsplit("/", n=1).str[-1]
    df["compound_qid"] = df["cmp"].str.rsplit("/", n=1).str[-1]
    df["reference_qid"] = df.get("ref", pd.Series(dtype=str)).str.rsplit("/", n=1).str[-1]
    df["reference_year"] = pd.to_numeric(df.get("date", pd.Series(dtype=str)).str[:4], errors="coerce").astype("Int64")
    df = df.rename(columns={"ik": "inchikey"})
    out = df.groupby(["wikidata", "compound_qid", "inchikey"], as_index=False).agg(
        reference_qids=("reference_qid", lambda s: sorted({x for x in s if isinstance(x, str)})),
        reference_year=("reference_year", "min"),
    )
    # Since the 2025 WDQS graph split, scholarly-article items (the LOTUS references) live on a separate
    # endpoint, so their publication dates (P577) are fetched from query-scholarly.wikidata.org.
    refs = sorted({q for qs in out["reference_qids"] for q in qs})
    years = reference_years(refs)
    out["reference_year"] = out["reference_qids"].map(lambda qs: min((years[q] for q in qs if q in years), default=None)).astype("Int64")
    out["source_id"], out["retrieved_at"], out["method"] = "lotus", now_iso(), "wikidata_sparql_P703_P248+scholarly_P577"
    return out


def reference_years(qids: list[str], batch: int = 200) -> dict[str, int]:
    out: dict[str, int] = {}
    for i in range(0, len(qids), batch):
        vals = " ".join(f"wd:{q}" for q in qids[i : i + batch])
        try:
            res = http.sparql(f"SELECT ?r ?date WHERE {{ VALUES ?r {{ {vals} }} ?r wdt:P577 ?date }}",
                              endpoint="https://query-scholarly.wikidata.org/sparql")
        except Exception:  # noqa: BLE001
            continue
        for b in res:
            if b.get("date"):
                q = b["r"].rsplit("/", 1)[-1]
                y = int(b["date"][:4])
                out[q] = min(out.get(q, y), y)
    return out


def chembl_ids(inchikeys: list[str], batch: int = 40) -> pd.DataFrame:
    rows = []
    for i in range(0, len(inchikeys), batch):
        ks = ",".join(inchikeys[i : i + batch])
        js = http.get_json(f"{CHEMBL}/molecule.json", params={
            "molecule_structures__standard_inchi_key__in": ks, "limit": 1000,
            "only": "molecule_chembl_id,pref_name,molecule_structures"}) or {}
        for m in js.get("molecules", []):
            st = m.get("molecule_structures") or {}
            rows.append({"inchikey": st.get("standard_inchi_key"), "molecule_chembl_id": m["molecule_chembl_id"], "pref_name": m.get("pref_name")})
    return pd.DataFrame(rows, columns=["inchikey", "molecule_chembl_id", "pref_name"])


def _activities(mol: str) -> list[dict]:
    js = http.get_json(f"{CHEMBL}/activity.json", params={
        "molecule_chembl_id": mol, "pchembl_value__gte": 5, "limit": 1000,
        "only": "target_chembl_id,pchembl_value,assay_type,document_year,data_validity_comment,target_organism,standard_type,document_chembl_id"}) or {}
    out = []
    for a in js.get("activities", []):
        if a.get("data_validity_comment") is not None or a.get("assay_type") not in {"B", "F"}:
            continue
        out.append({"molecule_chembl_id": mol, **{k: a.get(k) for k in ("target_chembl_id", "pchembl_value", "assay_type", "document_year", "target_organism", "standard_type", "document_chembl_id")}})
    return out


def chembl_activities(mols: list[str], workers: int = 4) -> pd.DataFrame:
    with ThreadPoolExecutor(workers) as ex:
        rows = [r for part in ex.map(_activities, mols) for r in part]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["pchembl_value"] = pd.to_numeric(df["pchembl_value"], errors="coerce")
    df["tier"] = pd.cut(df["pchembl_value"], [0, 6, 7, 99], right=False, labels=["T4", "T3", "T2"]).astype(str)
    return df


def _mechanisms(mol: str) -> list[dict]:
    js = http.get_json(f"{CHEMBL}/mechanism.json", params={"molecule_chembl_id": mol, "only": "target_chembl_id,mechanism_of_action"}) or {}
    return [{"molecule_chembl_id": mol, **m} for m in js.get("mechanisms", []) if m.get("target_chembl_id")]


def chembl_mechanisms(mols: list[str], workers: int = 4) -> pd.DataFrame:
    with ThreadPoolExecutor(workers) as ex:
        rows = [r for part in ex.map(_mechanisms, mols) for r in part]
    return pd.DataFrame(rows, columns=["molecule_chembl_id", "target_chembl_id", "mechanism_of_action"])


def _target(tid: str) -> dict:
    js = http.get_json(f"{CHEMBL}/target/{tid}.json") or {}
    acc = [c.get("accession") for c in js.get("target_components", []) if c.get("accession")]
    return {"target_chembl_id": tid, "target_type": js.get("target_type"), "organism": js.get("organism"),
            "pref_name": js.get("pref_name"), "uniprot": acc}


def chembl_targets(tids: list[str], workers: int = 4) -> pd.DataFrame:
    with ThreadPoolExecutor(workers) as ex:
        return pd.DataFrame(list(ex.map(_target, tids)))


OT_ERRORS: list[dict] = []


def _ot_query(q: str, variables: dict) -> dict:
    """One GraphQL call; network failures are recorded as gaps (OT_ERRORS) instead of aborting."""
    try:
        r = http.post(OT, json={"query": q, "variables": variables}, timeout=120)
        r.raise_for_status()
        return r.json().get("data") or {}
    except Exception as exc:  # noqa: BLE001
        OT_ERRORS.append({"variables": variables, "error": str(exc)[:160]})
        return {}


def ot_ensembl(uniprot: str) -> str | None:
    d = _ot_query("query($q:String!){ search(queryString:$q, entityNames:[\"target\"], page:{index:0,size:1}){ hits { id } } }", {"q": uniprot})
    hits = (d.get("search") or {}).get("hits") or []
    return hits[0]["id"] if hits else None


def ot_associations(ensembl: str, min_score: float = 0.2) -> list[dict]:
    q = """query($id:String!){ target(ensemblId:$id){ id approvedSymbol
      associatedDiseases(page:{index:0,size:200}){ rows { score disease { id name dbXRefs } } } } }"""
    d = _ot_query(q, {"id": ensembl})
    t = d.get("target") or {}
    out = []
    for r in ((t.get("associatedDiseases") or {}).get("rows") or []):
        if r["score"] < min_score:
            continue
        mesh = [x.split(":", 1)[1] for x in (r["disease"].get("dbXRefs") or []) if x.upper().startswith("MESH:")]
        out.append({"ensembl_id": ensembl, "symbol": t.get("approvedSymbol"), "disease_id": r["disease"]["id"],
                    "disease_name": r["disease"]["name"], "ot_score": float(r["score"]), "mesh_xrefs": mesh})
    return out


def mesh_descendants(mesh_ids: list[str]) -> dict[str, list[str]]:
    """MeSH descriptors below each given descriptor (via the NLM MeSH SPARQL endpoint)."""
    out: dict[str, list[str]] = {}
    for mid in mesh_ids:
        q = f"""PREFIX mesh: <http://id.nlm.nih.gov/mesh/> PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        SELECT DISTINCT ?d WHERE {{ mesh:{mid} meshv:treeNumber ?tn . ?dtn meshv:parentTreeNumber+ ?tn . ?d meshv:treeNumber ?dtn . }}"""
        try:
            res = http.sparql(q, endpoint="https://id.nlm.nih.gov/mesh/sparql")
        except Exception:  # noqa: BLE001
            res = []
        out[mid] = sorted({r["d"].rsplit("/", 1)[-1] for r in res})
    return out
