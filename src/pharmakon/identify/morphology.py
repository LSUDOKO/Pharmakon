"""f1 — morphological agreement (spec/06): Dioscorides' description vs a modern description.

Two trait records per (name, candidate):
- Greek side: extracted from the Dioscorides chapter (Claude session, ``data/llm/morph_greek.jsonl``,
  prompt ``config/prompts/morph_greek_v1.md``). The prompt never shows candidate species.
- Modern side: extracted from the species' English Wikipedia "Description" section (CC BY-SA 4.0)
  with the configured LLM provider (prompt ``morph_species_v1``). POWO was the preferred source but
  refuses automated clients (HTTP 403; docs/source_verification.md).

Every trait keeps a verbatim span; traits whose span is not a substring of their source text, or
whose values fall outside ``VOCAB``, are dropped. f1 = (matches − mismatches) / compared traits,
0 when nothing is comparable, so missing descriptions are neutral rather than penalised.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from pharmakon import http, llm
from pharmakon.common import DATA, PROCESSED, get_logger, now_iso, write_table
from pharmakon.extract.span_verify import verify
from pharmakon.schemas import MorphRecord

LLM_DIR = DATA / "llm"
GREEK_OUT = LLM_DIR / "morph_greek.jsonl"
SPECIES_OUT = LLM_DIR / "morph_species.jsonl"
WIKI = "https://en.wikipedia.org/w/api.php"

VOCAB: dict[str, list[str]] = {
    "habit": ["herb", "subshrub", "shrub", "tree", "climber", "aquatic", "grass_like", "fern", "bulbous", "succulent"],
    "life_span": ["annual", "biennial", "perennial"],
    "height": ["low", "medium", "tall"],  # <0.3 m, 0.3–1.5 m, >1.5 m (Greek: cubits/spans converted by the reader)
    "stem": ["woody", "herbaceous", "hollow", "angular", "hairy", "smooth", "branched", "unbranched", "creeping"],
    "leaf_form": ["entire", "toothed", "lobed", "finely_divided", "compound", "linear_grasslike", "needle_scale", "absent", "large", "small"],
    "leaf_surface": ["hairy", "smooth", "rough", "fleshy", "grey_silvery", "dark_green", "sticky"],
    "flower_colour": ["white", "yellow", "red_pink", "purple_blue", "green", "brown"],
    "inflorescence": ["umbel", "head_composite", "spike", "raceme_cluster", "solitary", "catkin"],
    "fruit": ["berry_fleshy", "pod_legume", "capsule", "nut_acorn", "small_seeds", "winged", "burr_prickly", "cone", "pome_drupe"],
    "root": ["bulb_tuber", "thick_fleshy", "fibrous", "woody", "long_taproot", "aromatic_root"],
    "spines": ["spiny", "unarmed"],
    "smell": ["aromatic", "foul", "pungent"],
    "taste": ["bitter", "sweet", "pungent_sharp", "astringent", "sour", "salty"],
    "habitat": ["wet_marsh", "rocky_mountain", "coastal_sandy", "cultivated_garden", "woodland_shade", "field_roadside", "walls_ruins"],
}
TRAITS = list(VOCAB)


def clean_record(raw: dict, text: str) -> tuple[dict[str, list[str]], dict[str, str], int]:
    """Keep traits with an exact span in ``text`` and in-vocabulary values. Returns (values, spans, dropped)."""
    rec = MorphRecord.model_validate(raw)
    vals, spans, dropped = {}, {}, 0
    for t in TRAITS:
        tr = getattr(rec, t)
        if tr is None or not tr.values:
            continue
        ok_vals = [v for v in tr.values if v in VOCAB[t]]
        exact, _ = verify(tr.span, text)
        if not ok_vals or not exact:
            dropped += 1
            continue
        vals[t], spans[t] = sorted(set(ok_vals)), tr.span
    return vals, spans, dropped


def agreement(a: dict[str, list[str]], b: dict[str, list[str]]) -> tuple[float, int, list[str]]:
    """(f1 score in [-1, 1], traits compared, human-readable matches)."""
    m = mm = 0
    notes = []
    for t in TRAITS:
        if t in a and t in b:
            hit = bool(set(a[t]) & set(b[t]))
            m, mm = m + hit, mm + (not hit)
            notes.append(f"{t}: {'/'.join(a[t])} ↔ {'/'.join(b[t])} {'✓' if hit else '✗'}")
    n = m + mm
    return ((m - mm) / n if n else 0.0), n, notes


# ---------------------------------------------------------------- Greek side (Claude session)

def write_greek_inputs(unit_ids: list[str] | None = None, path: Path | None = None) -> Path:
    """Chapter texts the Claude session reads. Candidate species are deliberately NOT included."""
    from pharmakon.identify.candidates import build_units

    units = build_units()
    if unit_ids is not None:
        units = units[units["unit_id"].isin(unit_ids)]
    ch = pd.read_parquet(PROCESSED / "dmm_chapters.parquet").set_index("chapter_id")
    path = path or LLM_DIR / "inputs" / "morph_greek_inputs.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    with path.open("w", encoding="utf-8") as f:
        for u in units.itertuples():
            cid = str(u.cluster_id).removeprefix("cl:")
            if cid in seen or cid not in ch.index:
                continue
            seen.add(cid)
            f.write(json.dumps({"chapter_id": cid, "headword_grc": ch.loc[cid, "headword_grc"], "text_grc": ch.loc[cid, "text_grc"]},
                               ensure_ascii=False) + "\n")
    return path


def load_greek() -> pd.DataFrame:
    """Session outputs → verified trait table, one row per chapter."""
    ch = pd.read_parquet(PROCESSED / "dmm_chapters.parquet").set_index("chapter_id")
    rows = []
    files = sorted(LLM_DIR.glob("morph_greek*.jsonl"))
    if not files:
        return pd.DataFrame(columns=["chapter_id", "traits", "spans", "dropped", "method"])
    for line in (ln for f in files for ln in f.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        d = json.loads(line)
        cid = d["chapter_id"]
        if cid not in ch.index:
            continue
        vals, spans, dropped = clean_record(d.get("traits") or {}, ch.loc[cid, "text_grc"])
        rows.append({"chapter_id": cid, "traits": json.dumps(vals, ensure_ascii=False), "spans": json.dumps(spans, ensure_ascii=False),
                     "dropped": dropped, "method": d.get("method", "morph_greek_v1:claude-session")})
    return pd.DataFrame(rows).drop_duplicates("chapter_id", keep="last")


# ---------------------------------------------------------------- modern side (Wikipedia + LLM)

def wiki_description(species: str) -> tuple[str | None, str | None]:
    """English Wikipedia plain-text 'Description' section (or the lead if none). Returns (text, page title)."""
    # Plain requests (not the shared sqlite cache): the text itself is stored in data/llm/morph_species.jsonl.
    import time

    import requests

    time.sleep(0.5)
    r = requests.get(WIKI, params={"action": "query", "prop": "extracts", "explaintext": 1, "titles": species,
                                   "format": "json", "redirects": 1}, headers={"User-Agent": http.USER_AGENT}, timeout=30)
    r.raise_for_status()
    js = r.json()
    pages = (js or {}).get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {}) if pages else {}
    text = page.get("extract") or ""
    if not text:
        return None, None
    title = page.get("title")
    # A redirect to the genus or to a different binomial is not a description of this species;
    # a redirect to a common-name article ("Caper") is.
    genus = species.split(" ")[0]
    if title and title != species and (title == genus or re.fullmatch(r"[A-Z][a-z]+ [a-z-]+", title)):
        return None, title
    m = re.search(r"\n==+ *(Description|Morphology|Characteristics)[^=]*==+\n(.*?)(?=\n== [^=]|\Z)", text, re.S)
    body = m.group(2) if m else text.split("\n==")[0]
    body = re.sub(r"\n==+[^=]+==+\n", "\n", body).strip()
    return (body[:4000] or None), title


SPECIES_SESSION = LLM_DIR / "morph_species_session.jsonl"


def species_traits(taxa: pd.DataFrame, use_llm: bool = True) -> pd.DataFrame:
    """One verified trait record per species (taxon_key, accepted_name).

    Descriptions are fetched once and stored in ``morph_species.jsonl``. Traits come from the API LLM
    (Groq) or, when its daily budget is spent, from a Claude session (``morph_species_session.jsonl``).
    """
    log = get_logger("morphology")
    rows, cache = [], {}
    if SPECIES_OUT.exists():
        for line in SPECIES_OUT.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            cache[d["accepted_name"]] = d
    for sf in sorted(LLM_DIR.glob("morph_species_session*.jsonl")):
        for line in sf.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            if d["accepted_name"] in cache and not cache[d["accepted_name"]].get("traits"):
                cache[d["accepted_name"]] |= {"traits": d["traits"], "method": d.get("method", "morph_species_v1:claude-session")}
    out = SPECIES_OUT.open("a", encoding="utf-8")
    for r in taxa.drop_duplicates("accepted_name").itertuples():
        name = r.accepted_name
        if name in cache:
            d = cache[name]
        else:
            text, title = wiki_description(name)
            d = {"accepted_name": name, "taxon_key": r.taxon_key, "wiki_title": title, "description": text, "traits": None, "method": None}
            if text and use_llm and llm.available():
                try:
                    res, meta = llm.structured("morph_species_v1", f"Species: {name}\n\nDescription:\n{text}", MorphRecord,
                                               max_tokens=2500, effort="low")
                    d["traits"], d["method"] = res.model_dump(), f"morph_species_v1:{meta['provider']}:{meta['model']}"
                except Exception as e:  # noqa: BLE001 — recorded, never silently dropped
                    d["method"] = f"error:{type(e).__name__}:{str(e)[:120]}"
                    log.warning(json.dumps({"species": name, "error": d["method"]}))
                    if "daily limit" in str(e):
                        break
            out.write(json.dumps(d, ensure_ascii=False) + "\n")
            out.flush()
        vals, spans, dropped = clean_record(d["traits"], d["description"]) if d.get("traits") and d.get("description") else ({}, {}, 0)
        rows.append({"taxon_key": r.taxon_key, "accepted_name": name, "wiki_title": d.get("wiki_title"),
                     "has_description": bool(d.get("description")), "traits": json.dumps(vals), "spans": json.dumps(spans, ensure_ascii=False),
                     "dropped": dropped, "method": d.get("method")})
    out.close()
    return pd.DataFrame(rows)


def build_f1(feats: pd.DataFrame, units: pd.DataFrame) -> tuple[pd.Series, dict]:
    """f1 for every candidate row of ``feats`` (aligned index) + coverage stats; writes morphology tables."""
    greek = load_greek().set_index("chapter_id")
    # Trait extraction is a separate, explicit step (Groq or a Claude session); here we only read stored records.
    sp = species_traits(feats[["taxon_key", "accepted_name"]], use_llm=False)
    spm = {r.accepted_name: json.loads(r.traits) for r in sp.itertuples()}
    cl = units.set_index("unit_id")["cluster_id"].to_dict()
    scores, rows = [], []
    for r in feats.itertuples():
        cid = str(cl.get(r.unit_id, "")).removeprefix("cl:")
        g = json.loads(greek.loc[cid, "traits"]) if cid in greek.index else {}
        s = spm.get(r.accepted_name, {})
        f, n, notes = agreement(g, s)
        scores.append(f)
        rows.append({"unit_id": r.unit_id, "taxon_key": r.taxon_key, "accepted_name": r.accepted_name, "chapter_id": cid,
                     "f1_morph": f, "traits_compared": n, "matches": notes})
    tab = pd.DataFrame(rows)
    ts = now_iso()
    tab["source_id"], tab["retrieved_at"], tab["method"] = "dmm_wellmann+wikipedia_en", ts, "morph_agreement_v1"
    write_table(tab, PROCESSED / "id_morphology.parquet")
    sp["source_id"], sp["retrieved_at"] = "wikipedia_en", ts
    sp["method"] = sp["method"].fillna("no_description")
    write_table(sp, PROCESSED / "species_traits.parquet")
    gt = greek.reset_index()
    gt["source_id"], gt["retrieved_at"] = "dmm_wellmann", ts
    write_table(gt, PROCESSED / "dmm_traits.parquet")
    stats = {
        "greek_chapters_with_traits": int((greek["traits"] != "{}").sum()) if len(greek) else 0,
        "greek_traits_dropped_unverified": int(greek["dropped"].sum()) if len(greek) else 0,
        "species": int(len(sp)), "species_with_description": int(sp["has_description"].sum()),
        "species_with_traits": int((sp["traits"] != "{}").sum()),
        "species_traits_dropped_unverified": int(sp["dropped"].sum()),
        "candidate_rows_with_comparison": int((tab["traits_compared"] > 0).sum()), "candidate_rows": int(len(tab)),
        "mean_traits_compared": round(float(tab.loc[tab["traits_compared"] > 0, "traits_compared"].mean()), 2) if (tab["traits_compared"] > 0).any() else 0,
    }
    return pd.Series(scores, index=feats.index), stats
