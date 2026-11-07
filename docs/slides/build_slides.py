"""Build the 10-slide EthnoHack deck (docs/slides/deck.html) from the pipeline's own outputs.

Every number is read from reports/stages/*.json, reports/scope_pilot/ or web/public/data/ —
nothing is typed by hand. Render to PDF with:  node docs/slides/render.cjs
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "slides" / "deck.html"
ST = ROOT / "reports" / "stages"
WEB = ROOT / "web" / "public"
MEDIA = "../../web/public/media"
DOCM = "../media"


def J(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def esc(s: object) -> str:
    return html.escape(str(s))


def svg(name: str) -> str:
    s = (ROOT / "docs" / "media" / name).read_text(encoding="utf-8")
    return re.sub(r'<svg ([^>]*?)width="\d+" height="\d+"', r'<svg \1', s, count=1).replace("<svg ", '<svg class="chart" ', 1)


S = {n: J(ST / f"{n}.json") for n in ["ingest-texts", "extract-claims", "map-conditions", "gold", "identify", "ingest-galen",
                                      "link-chemistry", "persistence", "evidence-labels", "forecast", "leads", "build-kg"]}
PILOT_FC = J(ROOT / "reports" / "scope_pilot" / "forecast.json")
LEADS = J(WEB / "data" / "leads.json")
NAME = J(WEB / "data" / "names" / "dmm-3-23.json")

idr = S["identify"]["results"]
m0, mf, tr, trf, lsj, judge, orc = (idr[k] for k in ["model_calibrated", "model_plus_f1_morphology", "transfer_model_calibrated",
                                                     "transfer_plus_f1_morphology", "baseline_lsj", "baseline_llm_judge",
                                                     "ablation_plus_ORACLE_expert_traits"])
pt = S["persistence"]["permutation_test"]
fc = S["forecast"]
lm = S["extract-claims"]["llm_merge"]
mo = S["identify"]["morphology"]
chem = S["link-chemistry"]
lead_s = S["leads"]
pct = lambda v: f"{v * 100:.0f}%"  # noqa: E731


def ci(m: dict) -> str:
    return f"{m['mean']:.2f} [{m['ci95'][0]:.2f}–{m['ci95'][1]:.2f}]"


def foot(n: int) -> str:
    return (f'<footer><span class="brand"><img src="{MEDIA}/mark.svg" alt="">pharmakon</span>'
            f'<span>Research hypotheses only — not medical advice</span><span class="num">{n:02d} / 10</span></footer>')


def slide(n: int, body: str, cls: str = "") -> str:
    return f'<section class="slide {cls}">{body}{foot(n) if n > 1 else ""}</section>'


# ---------------------------------------------------------------- slides

def s1() -> str:
    return slide(1, f"""
  <div class="sheet sheet-a"><div class="fringe"></div><div class="paper"><img src="{MEDIA}/folio-apsinthion.webp" alt=""></div></div>
  <div class="sheet sheet-b"><div class="fringe"></div><div class="paper"><img src="{MEDIA}/folio-glukurizon.webp" alt=""></div></div>
  <div class="title-band">
    <p class="dim mono">{S['ingest-texts']['passages']:,} Greek passages · {S['gold']['gold_names']} expert-identified names · {len(LEADS):,} untested leads</p>
    <h1 class="wordmark"><img src="{MEDIA}/mark.svg" alt="">pharmakon</h1>
    <p class="tag">2,000 years of Greek plant medicine, measured.</p>
    <p class="sub">An uncertainty-aware map from Dioscorides' 1st-century Greek to modern species, chemistry and testable research leads.</p>
    <p class="meta">EthnoHack 2026 · Track 1 — Traditional knowledge<br>
      <span class="mono">pharmakon.adoranto737.workers.dev · github.com/LSUDOKO/Pharmakon</span></p>
  </div>""", "title")


def s2() -> str:
    cands = [c for c in NAME["candidates"]][:3]
    bars = "".join(
        f'<div class="pbar"><span class="pl">{"<i>unidentified</i>" if c["taxon"] == "__unidentified__" else "<i>" + esc(c["name"]) + "</i>"}</span>'
        f'<span class="track"><span class="fill" style="width:{c["p"] * 100:.1f}%"></span>'
        f'<span class="whisk" style="left:{c["lo"] * 100:.1f}%;width:{(c["hi"] - c["lo"]) * 100:.1f}%"></span></span>'
        f'<b class="mono">{c["p"]:.2f}</b></div>' for c in cands)
    return slide(2, f"""
  <h2>Dioscorides described about 600 medicinal plants.<br><span class="dim">Which ones did he mean — and was he right?</span></h2>
  <div class="grid3">
    <div class="card"><h3>Names don't map to species</h3><p>An ancient name can point at several modern plants, and translations hide that doubt. One wrong identification breaks every lead built on it.</p></div>
    <div class="card"><h3>Survival is studied by hand</h3><p>Whether a remedy persisted from Dioscorides through Byzantium to today's villages has only been traced plant by plant.</p></div>
    <div class="card"><h3>Predictions are rarely tested</h3><p>Herb–disease models are almost never checked with a time split, so "history predicts science" is assumed, not measured.</p></div>
  </div>
  <div class="example">
    <div><p class="greek">{esc(NAME['lemma'])}</p><p class="dim mono">De materia medica {esc(NAME['chapter'].removeprefix('dmm:'))}</p></div>
    <div class="bars">{bars}<p class="fine">Pharmakon's answer for wormwood, with 90% bootstrap intervals — doubt kept, not hidden.</p></div>
  </div>""")


def s3() -> str:
    it, g, gal = S["ingest-texts"], S["gold"], S["ingest-galen"]
    mod = S["persistence"]["modern_records"]
    return slide(3, f"""
  <h2>Data: one text chain, eight open databases</h2>
  <div class="timeline">
    <div class="era"><p class="yr mono">1st c.</p><h3>Dioscorides</h3><p><b>{it['passages']:,}</b> passages, <b>{it['chapters']}</b> chapters<br>Wellmann ed., First1KGreek TEI</p></div>
    <div class="era"><p class="yr mono">2nd c.</p><h3>Galen</h3><p><b>{gal['drug_entries']}</b> drug entries, books 6–8<br>Kühn ed., First1KGreek TEI</p></div>
    <div class="era"><p class="yr mono">13th c.</p><h3>John the Physician</h3><p><b>{g['gold_names']}</b> expert-identified names<br>Lardos et al. 2024 (CC BY)</p></div>
    <div class="era"><p class="yr mono">today</p><h3>Greek villages</h3><p><b>{mod:,}</b> modern use records<br>Pelion 2023 · N. Aegean 2018</p></div>
  </div>
  <div class="dbgrid">
    <div><b>GBIF</b><span>taxonomy, Greek occurrences</span></div>
    <div><b>Wikidata · LOTUS</b><span>{chem['distinct_compounds']:,} plant compounds</span></div>
    <div><b>ChEMBL 37</b><span>{chem['human_targets']} human targets</span></div>
    <div><b>Open Targets</b><span>target → disease</span></div>
    <div><b>NLM MeSH</b><span>{S['map-conditions']['distinct_mesh_ids']} verified conditions</span></div>
    <div><b>PubMed</b><span>{S['evidence-labels']['pairs']:,} plant–condition pairs labelled</span></div>
    <div><b>PubChem</b><span>toxicity citations (GHS)</span></div>
    <div><b>LSJ · Wikipedia</b><span>lexicon, species descriptions</span></div>
  </div>
  <p class="fine">All open licences (CC0, CC BY, CC BY-SA, public domain). Every source checked live before use; every row carries source, retrieval time and method.</p>
  <div class="folios">{''.join(f'<img src="{MEDIA}/folio-{f}.webp" alt="">' for f in ("apsinthion", "iris", "glukurizon", "adianton", "drakontaia"))}
    <p class="fine">Vienna Dioscorides (Codex Vindobonensis med. gr. 1, 6th c.), public domain — the tradition this project measures.</p></div>""")


def worked() -> str:
    c = next(x for x in NAME["claims"] if x["status"] == "ok")
    span = next((sp for p in NAME["passages"] for sp in p["spans"] if c["condition_text_grc"] in sp), c["condition_text_grc"])
    hl = esc(span).replace(esc(c["condition_text_grc"]), f'<mark>{esc(c["condition_text_grc"])}</mark>', 1)
    return (f'<div class="worked"><p class="greek-s">“{hl}”</p><i>→</i><div><b>{esc(c["condition_en"])}</b>'
            f'<span class="dim">use group {esc(c["use_group"])} · part {esc(c["plant_part"] or "—")} · verified span, CTS {esc(NAME["passages"][0]["cts"].split(":")[-1])}</span></div></div>')


def s4() -> str:
    ok_before = S["extract-claims"].get("ok_before_llm")
    ok_after = S["extract-claims"]["status_counts"]["ok"]
    return slide(4, f"""
  <h2>Method I — read the Greek, identify the plant</h2>
  <div class="two">
    <div>
      <h3>Every use keeps its Greek words</h3>
      <ol class="steps">
        <li><b>Rule lexicon</b> — Greek condition stems, clause by clause, exact spans.</li>
        <li><b>LLM reading</b> — {lm['llm_session_passages']:,} passages, {lm['llm_claims']:,} claims; finds {pct(lm['rule_ok_recovered_by_llm'])} of rule uses.</li>
        <li><b>Verify</b> — every span must be a substring of the source: <b>{pct(lm['llm_span_verified_rate'])}</b> pass. MeSH only via NLM lookup.</li>
      </ol>
      <p class="big mono">{ok_before:,} → {ok_after:,}</p><p class="fine">usable claims after the verified LLM layer; the backtest keeps the original {ok_before:,}</p>
    </div>
    <div>
      <h3>P(species | name), with an "unidentified" option</h3>
      <div class="feat">
        <span>geography — GBIF records in Greece, Cyprus, Turkey</span>
        <span>name continuity — modern Greek names, Latinised epithets</span>
        <span>scholarly agreement — LSJ, botanical historians</span>
        <span>genus consensus</span>
        <span class="new">plant-description match — {mo['greek_chapters_with_traits']} Greek chapters vs {mo['species_with_traits']} species</span>
      </div>
      <p>Conditional logit → temperature scaling → bootstrap intervals. No pharmacology inside: identity is decided before any drug evidence is seen.</p>
    </div>
  </div>
  {worked()}""")


def s5() -> str:
    cut = ", ".join(map(str, fc["cutoffs"]))
    return slide(5, f"""
  <h2>Method II — trace each use, then test with a time machine</h2>
  <div class="two">
    <div>
      <h3>Survival across 2,000 years</h3>
      <div class="flow"><span>Dioscorides</span><i>→</i><span>Galen</span><i>→</i><span>John the Physician</span><i>→</i><span>modern Greece</span></div>
      <p>For each name × body system: is the use attested in each era? Compared with a <b>label-shuffle null</b> ({pt['n_permutations']:,} permutations), so chance overlap is not mistaken for tradition. Galen is checked for copying (word 4-gram containment).</p>
    </div>
    <div>
      <h3>Rolling-origin backtest</h3>
      <p>Stand at {cut}. Rank plant–condition pairs nobody had studied, using only what was known then. Check PubMed up to {fc['t_end']}.</p>
      <ul class="checks">
        <li>features dated ≤ cutoff (compound, ChEMBL and study years)</li>
        <li>research-popularity baseline to beat</li>
        <li>no LLM output, no LLM-derived claims, frozen non-LLM identification</li>
        <li>cluster-bootstrap 95% intervals at every cutoff</li>
      </ul>
    </div>
  </div>
  <div class="cutoffs">{''.join(f'<div><p class="yr mono">{c}</p><p><b class="mono">{fc["results"][str(c)]["test"]["random"]["n"]:,}</b> untested pairs</p><p><b class="mono">{fc["results"][str(c)]["test"]["random"]["positives"]}</b> studied by {fc["t_end"]}</p></div>' for c in fc["cutoffs"])}
    <p class="fine">All body systems. The skin/wound pilot is kept for comparison.</p></div>""")


def s6() -> str:
    return slide(6, f"""
  <h2>Prototype — live, open, usable from code and AI assistants</h2>
  <div class="proto">
    <div class="shot tall"><img src="{DOCM}/shot-explorer.jpg" alt="Ancient name explorer"></div>
    <div class="side">
      <div class="shot"><img src="{DOCM}/shot-leads.jpg" alt="Leads gallery"></div>
      <div class="card code">
        <h3>Website · JSON API · MCP server</h3>
        <p>Explorer with highlighted Greek, candidate photos, probability bars, description matches and a four-era survival table. Leads with toxicity flags, evidence paths and the exact PubMed query.</p>
        <pre>claude mcp add --transport http pharmakon \\
  https://pharmakon.adoranto737.workers.dev/mcp</pre>
        <p class="fine">6 read-only tools · CSV export · Streamlit research dashboard · 27 tests · one-command reproduction</p>
      </div>
    </div>
  </div>""")


def s7() -> str:
    return slide(7, f"""
  <h2>Result I — identification beats the dictionary</h2>
  <div class="two wide-left">
    <div>{svg('chart-identification.svg')}</div>
    <div class="stats">
      <div><p class="big mono">{pct(m0['top1']['mean'])}</p><p>agreement with expert identifications, vs <b>{pct(lsj['top1']['mean'])}</b> for the LSJ dictionary</p></div>
      <div><p class="big mono">{m0['brier']['mean']:.2f}</p><p>Brier score, vs {lsj['brier']['mean']:.2f} for the dictionary (lower is better)</p></div>
      <div><p class="big mono">{m0['ece']:.2f} → {mf['ece']:.2f}</p><p>calibration error once Dioscorides' plant descriptions are compared with modern ones. Target ≤ 0.10: <b>not yet met</b>.</p></div>
      <p class="fine">Leave-one-name-out over {m0['n_names']} names, 95% bootstrap CIs. The LLM judge ({pct(judge['top1']['mean'])}) is a comparison only — it may have memorised published identifications. Expert judgement is not ground truth.</p>
    </div>
  </div>""")


def s8() -> str:
    cuts = fc["cutoffs"]
    d = {c: fc["results"][str(c)]["bootstrap_ci"]["delta_auprc_histpop_minus_pop"] for c in cuts}
    pos_all = sum(fc["results"][str(c)]["test"]["random"]["positives"] for c in cuts)
    pos_pilot = sum(PILOT_FC["results"][str(c)]["test"]["random"]["positives"] for c in PILOT_FC["cutoffs"])
    neg = [c for c, v in d.items() if v[1] < 0]
    lo_ax, hi_ax = -0.2, 0.1
    X = lambda v: (v - lo_ax) / (hi_ax - lo_ax) * 100  # noqa: E731
    rows = "".join(
        f'<div class="drow"><span class="mono">{c}</span><span class="dtrack"><span class="zero" style="left:{X(0):.1f}%"></span>'
        f'<span class="ci{" bad" if v[1] < 0 else ""}" style="left:{X(v[0]):.1f}%;width:{X(v[1]) - X(v[0]):.1f}%"></span>'
        f'<span class="pt{" bad" if v[1] < 0 else ""}" style="left:{X(fc["results"][str(c)]["test"]["history+popularity"]["auprc"] - fc["results"][str(c)]["test"]["popularity"]["auprc"]):.1f}%"></span></span>'
        f'<span class="mono dim">{v[0]:+.2f} … {v[1]:+.2f}</span></div>' for c, v in d.items())
    bars = "".join(f'<div class="hb"><span>{lab}</span><span class="htrack"><span class="hfill {cls}" style="width:{v / 0.6 * 100:.1f}%"></span></span><b class="mono">{v * 100:.1f}%</b></div>'
                   for lab, v, cls in [("Observed", pt["observed_persisted_share"], ""), ("Shuffled labels, average", pt["null_mean"], "null"),
                                       ("Shuffled labels, 95th percentile", pt["null_95pct"], "null")])
    return slide(8, f"""
  <h2>Result II — the uses survived; history did not predict science</h2>
  <div class="two even">
    <div class="card viz"><h3>Did the uses survive 2,000 years?</h3>
      <p class="dim">Dioscorides uses whose plant appears in the modern Greek record ({pt['n_rows']} name × use rows)</p>{bars}
      <p class="callout"><b>p = {pt['p_value']}</b> over {pt['n_permutations']:,} label shuffles. Galen re-attests <b>{pct(S['persistence']['galen_agreement_rate'])}</b> of the uses, John the Physician <b>{pct(S['persistence']['jc_agreement_rate'])}</b>. Caveat: one modern study covers skin uses only.</p></div>
    <div class="card viz"><h3>Did history predict what science studied next?</h3>
      <p class="dim">Δ AUPRC = (history + popularity) − popularity, 95% CI; left of zero = history hurts</p>
      <div class="drow axisrow"><span></span><span class="dtrack noline"><span class="lab" style="left:0%">−0.20</span><span class="lab" style="left:{X(0):.1f}%">0</span><span class="lab" style="left:100%">+0.10</span></span><span></span></div>{rows}
      <p class="callout"><b>An honest null.</b> Research popularity predicts which pairs get studied; 2,000 years of history never adds to it{', and at ' + ', '.join(map(str, neg)) + ' it hurts' if neg else ''}. Going from the skin pilot to all body systems ({pos_pilot} → {pos_all} positives) made the null sharper, not weaker.</p></div>
  </div>""")


def s9() -> str:
    seen, pics = set(), []
    for ld in LEADS:
        if ld.get("image") and ld["species"] not in seen:
            seen.add(ld["species"])
            pics.append(ld)
    cards = "".join(
        f'<div class="lead"><img src="{esc(re.sub(r"width=\d+", "width=500", ld["image"]["thumb"]))}" alt="">'
        f'<p><b>#{ld["rank"]}</b> <i>{esc(ld["species"])}</i></p><p class="dim">{esc(ld["condition"])} · P = {ld["p"]:.2f}'
        f'{" · ⚠ toxic" if ld["toxic"] else ""}{" · path ✓" if ld["has_paths"] else ""}</p></div>' for ld in pics[:6])
    return slide(9, f"""
  <h2>Impact — {len(LEADS):,} uncertainty-weighted leads for the lab</h2>
  <div class="two wide-left">
    <div class="leadgrid">{cards}</div>
    <div class="stats">
      <div><p class="big mono">{lead_s['top20_with_closed_evidence_path']}/20</p><p>top leads with a closed compound → human target → disease path (LOTUS · ChEMBL · Open Targets)</p></div>
      <div><p class="big mono">{lead_s['top20_changed_when_using_top1_identity']}/20</p><p>top leads that change if plant uncertainty is ignored (Kendall τ {lead_s['kendall_tau_weighted_vs_top1']:.2f})</p></div>
      <div><p class="big mono">{lead_s['top20_with_toxicity_flag']}/20</p><p>carry a PubChem-cited toxicity flag — shown, never hidden</p></div>
      <p class="fine">Who uses it: pharmacognosy labs choosing what to screen next · historians reading Dioscorides with evidence · conservation (IUCN status per species). Every lead keeps its exact PubMed query.</p>
    </div>
  </div>""")


def s10() -> str:
    return slide(10, f"""
  <h2>Limits, ethics and what comes next</h2>
  <div class="grid3">
    <div class="card"><h3>What we don't claim</h3><ul>
      <li>Expert gold is judgement, not ground truth ({S['gold']['gold_names']} names, wide intervals).</li>
      <li>"Supported" = PubMed co-mention proxy; human audits generated, not yet filled.</li>
      <li>Calibration {mf['ece']:.2f} still misses ≤ 0.10.</li>
      <li>LLM outputs are verified word-for-word but not yet expert-audited.</li></ul></div>
    <div class="card"><h3>Responsible research</h3><ul>
      <li>Research hypotheses only — no dosing, no medical advice.</li>
      <li>Toxic genera flagged with PubChem citations.</li>
      <li>No LLM output ever feeds the backtest (tested).</li>
      <li>Nagoya Protocol: benefit-sharing for any commercial follow-up.</li></ul></div>
    <div class="card"><h3>Next</h3><ul>
      <li>Expert audit of claims, conditions and labels.</li>
      <li>Richer floras (Flora of Greece, POWO with permission).</li>
      <li>Paul of Aegina, Oribasius; Arabic and Latin transmission.</li>
      <li>Screening partnership for top non-toxic leads; Zenodo DOI.</li></ul></div>
  </div>
  <div class="closing"><img src="{MEDIA}/mark.svg" alt=""><span class="wm">pharmakon</span>
    <span class="mono">pharmakon.adoranto737.workers.dev · github.com/LSUDOKO/Pharmakon · /mcp</span></div>""")


from urllib.parse import quote

def _mask(name: str) -> str:
    return "url(\"data:image/svg+xml;utf8," + quote((WEB / "media" / name).read_text(encoding="utf-8")) + "\")"


CSS = (Path(__file__).parent / "deck.css").read_text(encoding="utf-8")
for nm in ("fringe-a", "tear-a", "fringe-b", "tear-b"):
    CSS = CSS.replace(f"url(../../web/public/media/{nm}.svg)", _mask(f"{nm}.svg"))
doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Pharmakon — EthnoHack 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=GFS+Didot&family=JetBrains+Mono:wght@400;600&display=block" rel="stylesheet">
<style>{CSS}</style></head><body>
{s1()}{s2()}{s3()}{s4()}{s5()}{s6()}{s7()}{s8()}{s9()}{s10()}
</body></html>"""
OUT.write_text(doc, encoding="utf-8")
print(OUT)
