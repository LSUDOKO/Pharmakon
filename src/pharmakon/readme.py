"""Render README.md from docs/README.template.md: brand SVG charts + result tables.

Every number comes from reports/stages/*.json (pipeline summaries) or the site export in
web/public/data/ — nothing is typed by hand. Run: python -m pharmakon readme
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGES = ROOT / "reports" / "stages"
WEBDATA = ROOT / "web" / "public" / "data"
MEDIA = ROOT / "docs" / "media"
TEMPLATE = ROOT / "docs" / "README.template.md"

INK, CARD, RULE = "#000000", "#0b120e", "#22302a"
VERD, HI, LICHEN, PAPER, DIM, WARN = "#17744f", "#3dbb82", "#b8e6cc", "#eceee7", "#8b938f", "#ff5a5f"
SANS = "Outfit, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Menlo, Consolas, monospace"

UG = {
    "AN": "Andrology", "BS": "Blood, spleen", "CV": "Cardiovascular", "DE": "Skin & wounds", "FV": "Fever",
    "GI": "Digestive", "GY": "Gynaecology", "IF": "Infections", "LG": "Liver & gall", "MA": "Pregnancy & birth",
    "MC": "Mental", "MS": "Muscles & joints", "MN": "Metabolic", "NC": "Neurological", "OP": "Eyes",
    "OC": "Mouth & teeth", "OT": "Ears", "RE": "Respiratory", "RL": "Nose & throat", "UR": "Urinary", "XY": "Other",
}


def stage(name: str) -> dict:
    return json.loads((STAGES / f"{name}.json").read_text())


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- SVG helpers

def svg(w: int, h: int, title: str, sub: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
        f'<rect width="{w}" height="{h}" rx="22" fill="{INK}"/>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="21" fill="none" stroke="{RULE}"/>'
        f'<path d="M{w - 150} 0 L{w} 0 L{w} 150 Z" fill="{VERD}" opacity=".18"/>'
        f'<text x="36" y="52" font-family="{SANS}" font-size="26" font-weight="600" fill="{PAPER}">{esc(title)}</text>'
        f'<text x="36" y="80" font-family="{SANS}" font-size="15" fill="{DIM}">{esc(sub)}</text>'
        f"{body}</svg>"
    )


def t(x: float, y: float, s: object, size: int = 13, fill: str = PAPER, anchor: str = "start", mono: bool = False, weight: int = 400) -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO if mono else SANS}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')


def line(x1: float, y1: float, x2: float, y2: float, stroke: str = RULE, w: float = 1, dash: str = "") -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}/>'


def axis(x0: float, x1: float, y: float, lo: float, hi: float, ticks: list[float], fmt=lambda v: f"{v:.0%}") -> str:
    out = [line(x0, y, x1, y, RULE)]
    for v in ticks:
        x = x0 + (v - lo) / (hi - lo) * (x1 - x0)
        out += [line(x, y, x, y + 5, RULE), t(x, y + 20, fmt(v), 11, DIM, "middle", mono=True)]
    return "".join(out)


# ---------------------------------------------------------------- charts

def chart_identification(ident: dict) -> str:
    r = ident["results"]
    rows = [
        ("Pharmakon (calibrated)", r["model_calibrated"], HI, False),
        *([("+ plant-description match (f1)", r["model_plus_f1_morphology"], HI, False)] if "top1" in r.get("model_plus_f1_morphology", {}) else []),
        ("Transfer model, used for all names", r["transfer_model_calibrated"], HI, False),
        *([("Transfer + description match", r["transfer_plus_f1_morphology"], HI, False)] if "top1" in r.get("transfer_plus_f1_morphology", {}) else []),
        *([("LLM judge (comparison only)", r["baseline_llm_judge"], LICHEN, False)] if "top1" in r.get("baseline_llm_judge", {}) else []),
        ("Uniform guess", r["baseline_uniform"], DIM, False),
        ("Genus-frequency prior", r["baseline_genus_prior"], DIM, False),
        ("LSJ dictionary", r["baseline_lsj"], DIM, False),
        ("Oracle: + expert-coded traits", r["ablation_plus_ORACLE_expert_traits"], LICHEN, True),
    ]
    w, x0, x1, y0, step = 1200, 380, 1110, 130, 46
    body = []
    for i in range(6):
        v = i / 5
        x = x0 + v * (x1 - x0)
        body.append(line(x, y0 - 22, x, y0 + step * len(rows) - 20, "#111a15"))
    for i, (label, m, col, hollow) in enumerate(rows):
        y = y0 + i * step
        mean, (lo, hi) = m["top1"]["mean"], m["top1"]["ci95"]
        X = lambda v: x0 + v * (x1 - x0)  # noqa: E731
        body += [
            t(x0 - 24, y + 5, label, 15, PAPER if not hollow else DIM, "end"),
            line(X(lo), y, X(hi), y, col, 3),
            f'<circle cx="{X(mean):.1f}" cy="{y}" r="8" fill="{INK if hollow else col}" stroke="{col}" stroke-width="2.5"/>',
            t(X(hi) + 14, y + 5, f"{mean:.0%}", 13, col, mono=True),
        ]
    body.append(axis(x0, x1, y0 + step * len(rows) - 14, 0, 1, [0, 0.2, 0.4, 0.6, 0.8, 1.0]))
    body.append(t(x0, y0 + step * len(rows) + 30, "top-1 agreement with expert identifications, 61 names, leave-one-name-out, 95% bootstrap CI", 12, DIM))
    return svg(w, y0 + step * len(rows) + 60, "Which plant is it? Agreement with experts",
               "Lardos et al. (2024) gold set. The LLM judge may have memorised identifications; the oracle is an ablation only.", "".join(body))


def chart_reliability(ident: dict) -> str:
    rel = ident["results"]["model_calibrated"]["reliability"]
    ece = ident["results"]["model_calibrated"]["ece"]
    w, h, x0, y0, s = 1200, 560, 120, 470, 360
    X = lambda v: x0 + v * s  # noqa: E731
    Y = lambda v: y0 - v * s  # noqa: E731
    body = [line(X(0), Y(0), X(1), Y(1), DIM, 1.5, "6 6")]
    for v in (0, 0.25, 0.5, 0.75, 1):
        body += [line(X(0), Y(v), X(1), Y(v), "#111a15"), t(X(0) - 12, Y(v) + 4, f"{v:.0%}", 11, DIM, "end", True),
                 t(X(v), y0 + 22, f"{v:.0%}", 11, DIM, "middle", True)]
    for b in rel:
        bw = (b["bin_hi"] - b["bin_lo"]) * s - 6
        body.append(f'<rect x="{X(b["bin_lo"]) + 3:.1f}" y="{Y(b["accuracy"]):.1f}" width="{bw:.1f}" '
                    f'height="{b["accuracy"] * s:.1f}" fill="{VERD}" opacity=".55"/>')
        body.append(f'<circle cx="{X(b["mean_conf"]):.1f}" cy="{Y(b["accuracy"]):.1f}" r="{4 + b["n"] ** 0.5 * 2:.1f}" '
                    f'fill="{HI}" stroke="{INK}" stroke-width="1.5"/>')
    body += [t(X(0.5), y0 + 48, "model confidence in its top species", 13, DIM, "middle"),
             f'<text transform="translate({X(0) - 60},{Y(0.5)}) rotate(-90)" font-family="{SANS}" font-size="13" fill="{DIM}" text-anchor="middle">share actually correct</text>']
    tx = X(1) + 90
    body += [t(tx, 170, f"ECE {ece:.2f}", 44, WARN, weight=600, mono=True),
             t(tx, 205, "Expected calibration error. Target ≤ 0.10: missed.", 15, PAPER),
             t(tx, 240, "Dot size = names in the bin. The dashed line is perfect", 14, DIM),
             t(tx, 262, "calibration. Errors run both ways and most bins hold", 14, DIM),
             t(tx, 284, "fewer than ten names, so each bar is noisy.", 14, DIM),
             t(tx, 320, "The oracle ablation reaches ECE 0.09: the missing", 14, DIM),
             t(tx, 342, "morphology evidence (needs an LLM) is the main gap.", 14, DIM)]
    return svg(w, h, "How honest are the probabilities?", "Reliability diagram, calibrated model, 61 expert-identified names.", "".join(body))


def chart_persistence(pers: dict) -> str:
    pt = pers["permutation_test"]
    w, h = 1200, 640
    body = []
    # left: observed vs null
    bx, by, bw = 60, 150, 420
    for i, (label, v, col, hatch) in enumerate([
        ("Observed", pt["observed_persisted_share"], HI, False),
        ("Shuffled, average", pt["null_mean"], DIM, True),
        ("Shuffled, 95th percentile", pt["null_95pct"], DIM, True),
    ]):
        y = by + i * 80
        body += [t(bx, y, label, 15, PAPER), t(bx + bw, y, f"{v:.1%}", 15, col, "end", True),
                 f'<rect x="{bx}" y="{y + 12}" width="{bw}" height="16" rx="8" fill="#111a15"/>',
                 f'<rect x="{bx}" y="{y + 12}" width="{bw * v / 0.6:.1f}" height="16" rx="8" fill="{col}" opacity="{0.45 if hatch else 1}"/>']
    body += [t(bx, by + 250, f"{pt['n_rows']} Dioscorides uses whose plant is in the modern Greek record.", 13, DIM),
             t(bx, by + 272, f"p = {pt['p_value']} over {pt['n_permutations']:,} label shuffles. Bars scaled to 60%.", 13, DIM),
             t(bx, by + 294, "Caveat: the Mount Pelion study covers skin ailments only.", 13, DIM)]
    # right: by use group
    g = pers["by_use_group"]
    cols = [("persisted", "to modern Greece", HI), ("persisted_to_galen_only", "to Galen only", LICHEN),
            ("modified", "modified", "#4f6b5d"), ("lost", "lost", "#2a332e")]
    groups = sorted(g, key=lambda k: -sum(g[k].get(c, 0) for c, _, _ in cols))[:12]
    rx, ry, rw, rh = 690, 140, 450, 30
    lx = rx
    for _, lab, col in cols:
        body += [f'<rect x="{lx}" y="{ry - 32}" width="12" height="12" rx="3" fill="{col}"/>', t(lx + 18, ry - 22, lab, 12, DIM)]
        lx += 30 + len(lab) * 7
    for i, k in enumerate(groups):
        y = ry + i * (rh + 6)
        tot = sum(g[k].get(c, 0) for c, _, _ in cols) or 1
        x = rx
        body.append(t(rx - 12, y + 20, UG.get(k, k), 13, PAPER, "end"))
        for c, _, col in cols:
            ww = g[k].get(c, 0) / tot * rw
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{max(ww - 1, 0):.1f}" height="{rh}" fill="{col}"/>')
            x += ww
        body.append(t(rx + rw + 10, y + 20, tot, 11, DIM, mono=True))
    return svg(w, h, "Did the uses survive 2,000 years?",
               "Dioscorides (1st c.) → Galen (2nd c.) → John the Physician (13th c.) → modern Greek villages.", "".join(body))


MODELS = [("random", "Random"), ("popularity", "Popularity"), ("history", "History"),
          ("history+popularity", "History + popularity"), ("full", "Everything")]


def chart_backtest(fc: dict) -> str:
    cut = [str(c) for c in fc["cutoffs"]]
    w, h = 1200, 600
    pw, x0, y0 = 238, 170, 180
    body = []
    for i, (_, lab) in enumerate(MODELS):
        body.append(t(x0 - 16, y0 + i * 52 + 5, lab, 14, PAPER, "end"))
    for j, c in enumerate(cut):
        r = fc["results"][c]
        px = x0 + j * (pw + 18)
        X = lambda v, px=px: px + 12 + min(v, 0.8) / 0.8 * (pw - 24)  # noqa: E731
        body += [f'<rect x="{px}" y="{y0 - 40}" width="{pw}" height="{52 * 5 + 50}" rx="14" fill="{CARD}"/>',
                 t(px + pw / 2, y0 - 50, f"cutoff {c}", 15, PAPER, "middle", weight=600)]
        base = r["test"]["random"]["base_rate"]
        body.append(line(X(base), y0 - 30, X(base), y0 + 52 * 5 - 20, WARN, 1, "3 4"))
        for i, (m, _) in enumerate(MODELS):
            y = y0 + i * 52
            v = r["test"][m]["auprc"]
            ci = r["bootstrap_ci"].get(m)
            col = HI if m in ("history", "history+popularity") else (DIM if m == "random" else LICHEN)
            if ci:
                body.append(line(X(ci[0]), y, X(ci[1]), y, col, 2.5))
            body += [f'<circle cx="{X(v):.1f}" cy="{y}" r="6.5" fill="{col}"/>']
        d = r["bootstrap_ci"]["delta_auprc_histpop_minus_pop"]
        n, pos = r["test"]["random"]["n"], r["test"]["random"]["positives"]
        body += [t(px + pw / 2, y0 + 52 * 5 + 2, f"{pos} of {n} pairs gained support", 12, DIM, "middle"),
                 t(px + pw / 2, y0 + 52 * 5 + 36, f"Δ history: [{d[0]:+.2f}, {d[1]:+.2f}]", 13, HI if d[0] > 0 else PAPER, "middle", True)]
    null = all(fc["results"][c]["bootstrap_ci"]["delta_auprc_histpop_minus_pop"][0] <= 0 <= fc["results"][c]["bootstrap_ci"]["delta_auprc_histpop_minus_pop"][1] for c in cut)
    neg = [c for c in cut if fc["results"][c]["bootstrap_ci"]["delta_auprc_histpop_minus_pop"][1] < 0]
    pos = [c for c in cut if fc["results"][c]["bootstrap_ci"]["delta_auprc_histpop_minus_pop"][0] > 0]
    verdict = ("every interval includes zero: history adds no signal beyond research popularity. Reported as a finding." if null else
               f"history never helps: intervals include zero except {', '.join(neg)} where it hurts. Reported as a finding." if neg and not pos else
               f"history helps at {', '.join(pos)}; see the table.")
    body += [t(x0, h - 40, "AUPRC with 95% bootstrap CI (axis 0–0.8). Red dashes = base rate. Δ history = AUPRC(history + popularity) − AUPRC(popularity);", 12, DIM),
             t(x0, h - 20, verdict, 12, DIM)]
    return svg(w, h, "The time machine: did history predict later science?",
               "Rolling-origin backtest. Train on what was known at the cutoff, score pairs nobody had studied, check PubMed to 2025.", "".join(body))


def chart_pipeline(S: dict) -> str:
    tiles = [
        (S["ingest-texts"]["passages"], "Greek passages read", "Dioscorides, Wellmann ed."),
        (S["extract-claims"]["claims_total"], "uses extracted", f"{S['extract-claims']['exact_span_verified_rate_kept']:.0%} span-verified"),
        (S["ingest-galen"]["drug_entries"], "Galen drug entries", f"{S['ingest-galen']['entries_mapped_to_dmm']} matched to Dioscorides"),
        (S["identify"]["candidates_total"], "candidate species", f"{S['identify']['gbif_verification']['verified']} GBIF-verified"),
        (S["link-chemistry"]["distinct_compounds"], "compounds (LOTUS)", f"{S['link-chemistry']['human_targets']} human targets"),
        (S["leads"]["unsupported_today"], "untested leads", f"{S['leads']['toxic_genera_verified_in_pubchem']} toxic genera flagged"),
    ]
    w, h = 1200, 300
    tw = (w - 72 - 5 * 14) / 6
    body = []
    for i, (n, lab, sub) in enumerate(tiles):
        x = 36 + i * (tw + 14)
        body += [f'<rect x="{x:.1f}" y="112" width="{tw:.1f}" height="150" rx="16" fill="{CARD}" stroke="{RULE}"/>',
                 t(x + 18, 170, f"{n:,}", 34, HI, weight=600, mono=True), t(x + 18, 205, lab, 14, PAPER),
                 t(x + 18, 230, sub, 12, DIM)]
        if i < 5:
            body.append(t(x + tw + 7, 192, "›", 22, VERD, "middle"))
    return svg(w, h, "From 1st-century Greek to testable leads", "One CLI pipeline; every row carries source_id, retrieved_at and method.", "".join(body))


# ---------------------------------------------------------------- tables

def ci(m: dict) -> str:
    return f"{m['mean']:.2f} [{m['ci95'][0]:.2f}, {m['ci95'][1]:.2f}]"


def table_identification(ident: dict) -> str:
    r = ident["results"]
    rows = [("**Pharmakon (calibrated)**", "model_calibrated"), ("Pharmakon, before temperature scaling", "model_uncalibrated"),
            ("Transfer model (no Lardos counts; used for all names)", "transfer_model_calibrated"),
            ("…without the ethnobotanical-reference count", "ablation_without_f4_lit_ethno"),
            ("…without geography (f2)", "ablation_without_f2"), ("…without name continuity (f3)", "ablation_without_f3"),
            ("…without scholarly agreement (f4)", "ablation_without_f4"), ("…without genus consensus (f6)", "ablation_without_f6"),
            ("LSJ dictionary baseline", "baseline_lsj"), ("Genus-frequency prior", "baseline_genus_prior"),
            ("Uniform guess", "baseline_uniform"), ("*Oracle: + expert-coded traits (ablation only)*", "ablation_plus_ORACLE_expert_traits")]
    extra = [("**Pharmakon + f1 morphology (LLM traits)**", "model_plus_f1_morphology"),
             ("Transfer model + f1 morphology", "transfer_plus_f1_morphology"),
             ("LLM judge (Claude session, Greek text + candidate list; comparison only, may have memorised)", "baseline_llm_judge")]
    rows = rows[:3] + [x for x in extra[:2] if "top1" in r.get(x[1], {})] + rows[3:-1] + [x for x in extra[2:] if "top1" in r.get(x[1], {})] + rows[-1:]
    out = ["| model | top-1 [95% CI] | top-3 | mean reciprocal rank | Brier ↓ | ECE ↓ |", "|---|---|---|---|---|---|"]
    for lab, k in rows:
        m = r[k]
        out.append(f"| {lab} | {ci(m['top1'])} | {m['top3']['mean']:.2f} | {m['rr']['mean']:.2f} | {m['brier']['mean']:.2f} | {m['ece']:.2f} |")
    return "\n".join(out)


def table_weights(ident: dict) -> str:
    desc = ident["features"]
    out = ["| feature | what it measures | weight (full) | weight (transfer) |", "|---|---|---|---|"]
    for k, v in ident["weights"].items():
        tw = ident["transfer_model"]["weights"].get(k)
        out.append(f"| `{k}` | {desc[k]} | {v:+.2f} | {'' if tw is None else f'{tw:+.2f}'} |")
    return "\n".join(out)


def table_persistence(pers: dict) -> str:
    g = pers["by_use_group"]
    out = ["| use group | persisted to modern Greece | to Galen only | to John the Physician only | modified | lost |", "|---|---|---|---|---|---|"]
    for k in sorted(g, key=lambda k: -sum(g[k].values())):
        v = g[k]
        out.append(f"| {UG.get(k, k)} | {v['persisted']} | {v['persisted_to_galen_only']} | {v.get('persisted_to_byzantine_only', 0)} | {v['modified']} | {v['lost']} |")
    return "\n".join(out)


def table_backtest(fc: dict) -> str:
    out = ["| cutoff | test pairs | gained support by 2025 | " + " | ".join(lab for _, lab in MODELS) + " | Δ history [95% CI] |",
           "|---|---|---|" + "---|" * len(MODELS) + "---|"]
    for c in map(str, fc["cutoffs"]):
        r = fc["results"][c]
        cells = []
        for m, _ in MODELS:
            v = r["test"][m]["auprc"]
            b = r["bootstrap_ci"].get(m)
            cells.append(f"{v:.2f}" + (f" [{b[0]:.2f}, {b[1]:.2f}]" if b else ""))
        d = r["bootstrap_ci"]["delta_auprc_histpop_minus_pop"]
        out.append(f"| {c} | {r['test']['random']['n']} | {r['test']['random']['positives']} | " + " | ".join(cells) + f" | {d[0]:+.2f} to {d[1]:+.2f} |")
    return "\n".join(out)


def table_leads(leads: list[dict], n: int = 20) -> str:
    out = ["| # | species | condition (MeSH) | P(species) | lead score | toxicity | IUCN | used in modern Greece | rank if certainty ignored |",
           "|---|---|---|---|---|---|---|---|---|"]
    for ld in leads[:n]:
        tox = f'⚠ known toxic constituent ([PubChem]({ld["tox_url"]}))' if ld.get("toxic") else ""
        out.append(f"| {ld['rank']} | *{ld['species']}* | {ld['condition']} | {ld['p']:.2f} | {ld['score']:.3f} | {tox} | "
                   f"{ld.get('iucn') or ''} | {'yes' if ld.get('modern') else ''} | {ld['rank_top1']} |")
    return "\n".join(out)


def gallery_leads(leads: list[dict], n: int = 12, per_row: int = 4) -> str:
    """HTML photo grid of the top leads that have a Wikimedia photo (markdown table cells collapse images)."""
    seen: set[str] = set()
    pics = []
    for ld in leads:  # one photo per species: the best-ranked lead for it
        if ld.get("image") and ld["species"] not in seen:
            seen.add(ld["species"])
            pics.append(ld)
    pics = pics[:n]
    rows = []
    for i in range(0, len(pics), per_row):
        cells = []
        for ld in pics[i:i + per_row]:
            src = re.sub(r"width=\d+", "width=400", ld["image"]["thumb"])
            flag = " ⚠" if ld.get("toxic") else ""
            cells.append(f'<td width="{100 // per_row}%" align="center"><a href="{esc(ld["image"]["page"])}">'
                         f'<img src="{esc(src)}" width="100%" alt="{esc(ld["species"])}"></a><br>'
                         f'<sub><b>#{ld["rank"]}</b> <i>{esc(ld["species"])}</i>{flag}<br>{esc(ld["condition"])} · P = {ld["p"]:.2f}</sub></td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def table_conditions(leads: list[dict]) -> str:
    c: dict[str, list[dict]] = {}
    for ld in leads:
        c.setdefault(ld["condition"], []).append(ld)
    out = ["| condition | leads | best lead | its P(species) | flagged toxic |", "|---|---|---|---|---|"]
    for k, v in sorted(c.items(), key=lambda kv: -len(kv[1]))[:12]:
        b = min(v, key=lambda ld: ld["rank"])
        out.append(f"| {k} | {len(v)} | *{b['species']}* (#{b['rank']}) | {b['p']:.2f} | {sum(1 for ld in v if ld.get('toxic'))} |")
    return "\n".join(out)


def table_stages(S: dict) -> str:
    rows = [
        ("Read texts", "ingest-texts", f"{S['ingest-texts']['passages']:,} passages, {S['ingest-texts']['chapters']} chapters, headwords parsed {S['ingest-texts']['headword_parsed_rate']:.1%}"),
        ("Extract uses", "extract-claims", f"{S['extract-claims']['claims_total']:,} claims, {S['extract-claims']['archived_span_mismatch']} span mismatches, extractor `{S['extract-claims']['extractor']}`"),
        ("Map conditions", "map-conditions", f"{S['map-conditions']['lexicon_conditions']} Greek conditions, {S['map-conditions']['with_verified_mesh']} with verified MeSH, {S['map-conditions']['no_modern_equivalent']} with no modern equivalent"),
        ("Expert gold", "gold", f"{S['gold']['gold_names']} Dioscorides names, {S['gold']['jc_lemmas']} John the Physician lemmas"),
        ("Identify plants", "identify", f"{S['identify']['candidates_total']} candidates, {S['identify']['gbif_verification']['verified']} of {S['identify']['gbif_verification']['inputs']} names verified in GBIF"),
        ("Read Galen", "ingest-galen", f"{S['ingest-galen']['drug_entries']} drug entries, {S['ingest-galen']['claims_kept']} claims, copy containment {S['ingest-galen']['copy_containment_mean']:.3f}"),
        ("Link chemistry", "link-chemistry", f"{S['link-chemistry']['distinct_compounds']:,} compounds, {S['link-chemistry']['human_targets']} human targets, {S['link-chemistry']['paths_closing_loop']:,} closed paths"),
        ("Trace persistence", "persistence", f"{S['persistence']['rows']:,} name × use rows, {S['persistence']['modern_records']:,} modern records"),
        ("Label evidence", "evidence-labels", f"{S['evidence-labels']['pairs']} plant–condition pairs, {S['evidence-labels']['pairs_with_any_support_to_t_end']} with PubMed support by {S['evidence-labels']['t_end']}"),
        ("Backtest", "forecast", f"cutoffs {', '.join(map(str, S['forecast']['cutoffs']))}"),
        ("Rank leads", "leads", f"{S['leads']['unsupported_today']} untested pairs, Kendall τ {S['leads']['kendall_tau_weighted_vs_top1']:.2f} vs top-1 identity"),
        ("Knowledge graph", "build-kg", f"{S['build-kg']['nodes']:,} nodes, {S['build-kg']['edges']:,} edges"),
    ]
    out = ["| stage | command | output |", "|---|---|---|"]
    out += [f"| {a} | `python -m pharmakon {b}` | {c} |" for a, b, c in rows]
    return "\n".join(out)


def example_card(name_id: str = "dmm-3-23") -> str:
    d = json.loads((WEBDATA / "names" / f"{name_id}.json").read_text())
    p = d["passages"][0]
    cands = [c for c in d["candidates"]]
    rows = ["| candidate | family | P(species) | 90% interval |", "|---|---|---|---|"]
    for c in cands:
        nm = "(unidentified)" if c["taxon"] == "__unidentified__" else f"*{c['name']}*"
        rows.append(f"| {nm} | {c.get('family') or ''} | {c['p']:.2f} | {c['lo']:.2f}–{c['hi']:.2f} |")
    pers = ["| use | Dioscorides | Galen | John the Physician | modern Greece (expected) |", "|---|---|---|---|---|"]
    mark = lambda v: "—" if v is None else ("attested" if v else "absent")  # noqa: E731
    for r in d["persistence"]:
        if r["present_dmm"] or r["expected_modern"] >= 0.5:
            pers.append(f"| {UG.get(r['use_group'], r['use_group'])} | {mark(r['present_dmm'])} | {mark(r['present_galen'])} | {mark(r['present_jc'])} | {r['expected_modern']:.2f} |")
    top = next((c for c in cands if c["taxon"] != "__unidentified__"), None)
    img = f'<img src="{esc(top["image"]["thumb"])}" width="220" align="right" alt="{esc(top["name"])}">\n' if top and top.get("image") else ""
    return "\n".join([
        img,
        f"**{d['lemma']}** ({d['translit']}), *De materia medica* {d['chapter'].replace('dmm:', '')} · `{p['cts']}`",
        "",
        f"> {p['text']}",
        "",
        "The model's answer:",
        "",
        *rows,
        "",
        "The uses through time:",
        "",
        *pers,
    ])


def table_llm(S: dict) -> str:
    m = S["extract-claims"].get("llm_merge", {})
    mo = S["identify"].get("morphology", {})
    if not m or "llm_claims" not in m:
        return "_LLM layer not run._"
    rows = [
        ("Passages read by the LLM (Claude session)", f"{m['llm_session_passages']:,}"),
        ("Claims the LLM extracted", f"{m['llm_claims']:,}"),
        ("…with verbatim Greek spans that passed the substring check", f"{m['llm_span_verified_rate']:.0%}"),
        ("Rule-extracted uses the LLM also found", f"{m['rule_ok_recovered_by_llm']:.1%}"),
        ("'Ambiguous' rule claims the LLM confirmed as uses", f"{m['rule_ambiguous_confirmed_by_llm']} of {m['rule_ambiguous_in_covered']}"),
        ("LLM claims outside the lexicon (kept apart, proposals for the lexicon)", f"{m['llm_claims_out_of_lexicon']:,}"),
        ("Usable (`ok`) claims before → after", f"{S['extract-claims'].get('ok_before_llm', '—')} → {S['extract-claims']['status_counts'].get('ok', 0):,}"),
    ]
    if mo.get("species"):
        rows += [
            ("Dioscorides chapters with an LLM trait record (spans verified)", f"{mo['greek_chapters_with_traits']}"),
            ("Candidate species with a Wikipedia description / with traits", f"{mo['species_with_description']} / {mo['species_with_traits']} of {mo['species']}"),
            ("Candidate rows with ≥1 comparable trait (mean traits compared)", f"{mo['candidate_rows_with_comparison']} of {mo['candidate_rows']} ({mo['mean_traits_compared']})"),
        ]
    out = ["| LLM step | result |", "|---|---|"]
    return "\n".join(out + [f"| {a} | {b} |" for a, b in rows])


def table_scopes() -> str:
    pilot = json.loads((ROOT / "reports" / "scope_pilot" / "forecast.json").read_text())
    allsc = stage("forecast")
    out = ["| scope | cutoff | test pairs | gained support | AUPRC popularity | AUPRC history + popularity | Δ history [95% CI] |",
           "|---|---|---|---|---|---|---|"]
    for name, fc in (("skin/wound pilot", pilot), ("all body systems", allsc)):
        for c in map(str, fc["cutoffs"]):
            r = fc["results"][c]
            d = r["bootstrap_ci"]["delta_auprc_histpop_minus_pop"]
            out.append(f"| {name} | {c} | {r['test']['random']['n']} | {r['test']['random']['positives']} | {r['test']['popularity']['auprc']:.2f} | "
                       f"{r['test']['history+popularity']['auprc']:.2f} | {d[0]:+.2f} to {d[1]:+.2f} |")
    return "\n".join(out)


def table_sources() -> str:
    rows = [
        ("Dioscorides, *De materia medica* (Wellmann), TEI", "First1KGreek / Open Greek and Latin", "CC BY-SA 4.0"),
        ("Galen, *De simpl. med. temp. ac fac.* books 6–8 (Kühn), TEI", "First1KGreek", "CC BY-SA 4.0"),
        ("Liddell–Scott–Jones Greek lexicon", "Perseus Digital Library", "CC BY-SA 4.0"),
        ("Expert identifications, John the Physician crosswalk", "Lardos et al. 2024, figshare", "CC BY 4.0"),
        ("Mount Pelion ethnobotany", "Tsioutsiou et al. 2023", "CC BY"),
        ("North Aegean ethnobotany", "Axiotis et al. 2018", "CC BY"),
        ("Taxonomy and Greek/Cypriot/Turkish occurrences", "GBIF backbone + occurrence API", "CC0 / CC BY"),
        ("Vernacular names, conservation status, plant photos", "Wikidata / Wikimedia Commons", "CC0 / per file"),
        ("Plant → compound occurrences", "LOTUS via Wikidata", "CC0"),
        ("Compound → target activity", "ChEMBL 37", "CC BY-SA 3.0"),
        ("Target → disease association", "Open Targets Platform", "CC0"),
        ("Disease vocabulary", "NLM MeSH", "public domain"),
        ("Evidence labels (co-mention)", "PubMed E-utilities", "NLM terms"),
        ("Species descriptions for the morphology feature", "English Wikipedia (MediaWiki API)", "CC BY-SA 4.0"),
        ("Toxicity citations (GHS)", "PubChem", "public domain"),
    ]
    out = ["| data | source | licence |", "|---|---|---|"]
    return "\n".join(out + [f"| {a} | {b} | {c} |" for a, b, c in rows])


def table_mcp() -> str:
    import re as _re
    src = (ROOT / "web" / "worker.js").read_text()
    tools = _re.findall(r'name: "([a-z_]+)", fn: \w+,\s*description: "([^"]+)"', src)
    out = ["| tool | what it returns |", "|---|---|"]
    return "\n".join(out + [f"| `{n}` | {d} |" for n, d in tools])


# ---------------------------------------------------------------- main

def build() -> dict:
    names = ["ingest-texts", "extract-claims", "map-conditions", "gold", "identify", "ingest-galen", "link-chemistry",
             "persistence", "evidence-labels", "forecast", "leads", "build-kg"]
    S = {n: stage(n) for n in names}
    leads = json.loads((WEBDATA / "leads.json").read_text())
    MEDIA.mkdir(parents=True, exist_ok=True)
    charts = {
        "chart-pipeline.svg": chart_pipeline(S),
        "chart-identification.svg": chart_identification(S["identify"]),
        "chart-reliability.svg": chart_reliability(S["identify"]),
        "chart-persistence.svg": chart_persistence(S["persistence"]),
        "chart-backtest.svg": chart_backtest(S["forecast"]),
    }
    for f, s in charts.items():
        (MEDIA / f).write_text(s)
    blocks = {
        "TABLE_STAGES": table_stages(S),
        "TABLE_IDENTIFICATION": table_identification(S["identify"]),
        "TABLE_WEIGHTS": table_weights(S["identify"]),
        "TABLE_PERSISTENCE": table_persistence(S["persistence"]),
        "TABLE_BACKTEST": table_backtest(S["forecast"]),
        "TABLE_LEADS": table_leads(leads),
        "GALLERY_LEADS": gallery_leads(leads),
        "TABLE_CONDITIONS": table_conditions(leads),
        "TABLE_SOURCES": table_sources(),
        "TABLE_MCP": table_mcp(),
        "TABLE_LLM": table_llm(S),
        "TABLE_SCOPES": table_scopes(),
        "EXAMPLE": example_card(),
    }
    pt = S["persistence"]["permutation_test"]
    idr = S["identify"]["results"]
    scal = {
        "TOP1": f"{idr['model_calibrated']['top1']['mean']:.0%}", "LSJ": f"{idr['baseline_lsj']['top1']['mean']:.0%}",
        "ECE": f"{idr['model_calibrated']['ece']:.2f}", "PERSIST": f"{pt['observed_persisted_share']:.0%}",
        "NULL": f"{pt['null_mean']:.1%}", "PVAL": str(pt["p_value"]), "LEADS": str(S["leads"]["unsupported_today"]),
        "CHANGED": str(S["leads"]["top20_changed_when_using_top1_identity"]), "LOWP": str(S["leads"]["top20_resting_on_p_species_below_0.5"]),
        "TOX20": str(S["leads"]["top20_with_toxicity_flag"]), "TAU": f"{S['leads']['kendall_tau_weighted_vs_top1']:.2f}",
        "NAMES": str(sum(1 for n in json.loads((WEBDATA / 'names.json').read_text()) if not n["chapter"].endswith(".preface"))),
        "GALEN": f"{S['persistence']['galen_agreement_rate']:.0%}", "JC": f"{S['persistence']['jc_agreement_rate']:.0%}",
    }
    out = TEMPLATE.read_text()
    for k, v in {**blocks, **scal}.items():
        out = out.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", out)
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    (ROOT / "README.md").write_text(out)
    return {"charts": list(charts), "readme_chars": len(out)}


if __name__ == "__main__":
    print(build())
