"""Figures for the DH2027 long paper. Every value is read from the pipeline's outputs
(reports/stages/*.json, web/public/data/names/*.json); nothing is typed by hand.
Run from the repo root:  .venv/bin/python docs/dh2027/long/figures.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)
STAGES = ROOT / "reports" / "stages"
J = lambda n: json.loads((STAGES / f"{n}.json").read_text())  # noqa: E731

ACCENT, ACCENT2, GREY, LIGHT, WARN, INK = "#17744f", "#3dbb82", "#8a8f8c", "#d9dedb", "#c0392b", "#1a1a1a"
plt.rcParams.update({
    "font.family": "Noto Sans", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.2, "axes.edgecolor": "#444",
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})
UG = {"AN": "Andrology", "BS": "Blood, spleen", "CV": "Cardiovascular", "DE": "Skin & wounds", "FV": "Fever",
      "GI": "Digestive", "GY": "Gynaecology", "IF": "Infections", "LG": "Liver & gall", "MA": "Pregnancy & birth",
      "MC": "Mental", "MS": "Muscles & joints", "MN": "Metabolic", "NC": "Neurological", "OP": "Eyes",
      "OC": "Mouth & teeth", "OT": "Ears", "RE": "Respiratory", "RL": "Nose & throat", "UR": "Urinary", "XY": "Other"}


def fig_identification():
    R = J("identify")["results"]
    rows = [("Pharmakon (calibrated)", "model_calibrated", ACCENT, "o"),
            ("+ description match", "model_plus_f1_morphology", ACCENT, "o"),
            ("Transfer model (no expert-derived counts)", "transfer_model_calibrated", ACCENT2, "o"),
            ("LLM judge (comparison only)", "baseline_llm_judge", GREY, "D"),
            ("Uniform guess", "baseline_uniform", INK, "o"),
            ("Genus-frequency prior", "baseline_genus_prior", INK, "o"),
            ("LSJ lexicon", "baseline_lsj", INK, "o")]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 2.55), gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.42})
    for i, (lab, k, col, mk) in enumerate(rows):
        t = R[k]["top1"]; lo, hi = t["ci95"]; y = len(rows) - 1 - i
        a.plot([lo, hi], [y, y], color=col, lw=1.4, solid_capstyle="butt")
        a.plot(t["mean"], y, mk, color=col, ms=5.2, mfc="white" if mk == "D" else col, mew=1.2)
        a.text(hi + 0.02, y, f"{t['mean']:.2f}", va="center", fontsize=7, color="#333")
    a.set_yticks(range(len(rows))); a.set_yticklabels([r[0] for r in rows][::-1])
    a.set_xlim(0, 1); a.set_xlabel("top-1 agreement with experts (n = 61)")
    a.axvline(R["baseline_uniform"]["top1"]["mean"], color=LIGHT, lw=0.8, ls="--", zorder=0)
    a.set_title("(a) Which plant is it?", loc="left")
    for lab, k, col, mk in [("calibrated", "model_calibrated", ACCENT, "o"), ("before scaling", "model_uncalibrated", GREY, "s"),
                            ("+ description", "model_plus_f1_morphology", ACCENT2, "^")]:
        rel = R[k]["reliability"]
        b.plot([r["mean_conf"] for r in rel], [r["accuracy"] for r in rel], "-", color=col, lw=0.8, alpha=0.6)
        b.scatter([r["mean_conf"] for r in rel], [r["accuracy"] for r in rel], s=[8 + 4 * r["n"] for r in rel],
                  color=col, marker=mk, label=f"{lab} (ECE {R[k]['ece']:.2f})", zorder=3, edgecolors="white", linewidths=0.4)
    b.plot([0, 1], [0, 1], color="#999", lw=0.7, ls="--"); b.set_xlim(0, 1); b.set_ylim(0, 1.05)
    b.set_xlabel("predicted probability of top choice"); b.set_ylabel("observed accuracy")
    b.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.24), ncol=1, handletextpad=0.3, fontsize=6.8)
    b.set_title("(b) Are the probabilities honest?", loc="left")
    fig.savefig(OUT / "fig_identification.pdf")


def fig_survival():
    P = J("persistence")
    groups = sorted(P["by_use_group"].items(), key=lambda kv: -sum(kv[1].values()))[:12][::-1]
    cats = [("persisted", "survives to today", ACCENT), ("persisted_to_galen_only", "only as far as Galen", ACCENT2),
            ("persisted_to_byzantine_only", "only as far as Byzantium", "#9ccfb5"),
            ("modified", "modified", "#c9b37e"), ("lost", "lost", LIGHT)]
    fig, ax = plt.subplots(figsize=(6.6, 2.7))
    left = [0] * len(groups)
    for key, lab, col in cats:
        vals = [g[1].get(key, 0) for g in groups]
        ax.barh(range(len(groups)), vals, left=left, color=col, label=lab, height=0.72, edgecolor="white", linewidth=0.4)
        left = [l + v for l, v in zip(left, vals)]
    ax.set_yticks(range(len(groups))); ax.set_yticklabels([UG.get(g[0], g[0]) for g in groups])
    ax.set_xlabel("Dioscorides name–use rows")
    pt = P["permutation_test"]
    ax.legend(frameon=False, ncol=5, loc="lower center", bbox_to_anchor=(0.45, 1.0), handlelength=1.1, columnspacing=1.0)
    ax.text(0.98, 0.06, f"overall: {pt['observed_persisted_share']:.1%} recur vs {pt['null_mean']:.1%} by chance\n"
            f"(null 95th pct. {pt['null_95pct']:.1%}; p = {pt['p_value']}; n = {pt['n_rows']})",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.2, color="#333")
    fig.savefig(OUT / "fig_survival.pdf")


def fig_backtest():
    F = J("forecast")
    cuts = ["2000", "2005", "2010", "2015"]; x = [int(c) for c in cuts]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 2.45), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.35})
    for k, lab, col, ls, mk in [("popularity", "popularity", INK, "-", "o"), ("history+popularity", "history + popularity", ACCENT, "-", "o"),
                                ("full", "everything (+ chemistry)", ACCENT2, "--", "s"), ("shuffled_history+popularity", "shuffled history + popularity", GREY, ":", "^"),
                                ("chemistry", "chemistry", "#c9b37e", "-", "v"), ("history", "history alone", WARN, "-", "D"), ("random", "random", "#bbb", "-", "")]:
        a.plot(x, [F["results"][c]["test"][k]["auprc"] for c in cuts], ls=ls, marker=mk, color=col, lw=1.1, ms=3.5, label=lab)
    a.set_xticks(x); a.set_ylabel("AUPRC"); a.set_xlabel("cutoff year"); a.set_ylim(0, 0.45)
    a.legend(frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, handlelength=1.8, columnspacing=0.9)
    a.set_title("(a) Predicting what science studied next", loc="left")
    for i, c in enumerate(cuts):
        t = F["results"][c]["test"]; lo, hi = F["results"][c]["bootstrap_ci"]["delta_auprc_histpop_minus_pop"]
        d = t["history+popularity"]["auprc"] - t["popularity"]["auprc"]; col = WARN if hi < 0 else INK
        b.plot([lo, hi], [i, i], color=col, lw=1.4); b.plot(d, i, "o", color=col, ms=4.5)
    b.axvline(0, color="#999", lw=0.7, ls="--"); b.set_yticks(range(4)); b.set_yticklabels(cuts); b.invert_yaxis()
    b.set_xlabel("Δ AUPRC, adding history (95% CI)"); b.set_title("(b) Does history help?", loc="left")
    fig.savefig(OUT / "fig_backtest.pdf")


def fig_example():
    d = json.loads((ROOT / "web/public/data/names/dmm-3-23.json").read_text())
    cands = sorted(d["candidates"], key=lambda c: -c["p"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 2.2), gridspec_kw={"width_ratios": [1, 1.25], "wspace": 0.55})
    for i, c in enumerate(cands):
        lab = "unidentified" if c["taxon"] == "__unidentified__" else c["name"]
        col = GREY if c["taxon"] == "__unidentified__" else ACCENT
        a.barh(i, c["p"], color=col, height=0.55); a.plot([c["lo"], c["hi"]], [i, i], color=INK, lw=1)
        a.text(c["hi"] + 0.02, i, f"{c['p']:.2f}", va="center", fontsize=7)
    a.set_yticks(range(len(cands))); a.set_yticklabels(["unidentified" if c["taxon"] == "__unidentified__" else c["name"] for c in cands],
                                                       fontstyle="italic"); a.invert_yaxis()
    a.set_xlim(0, 1); a.set_xlabel("P(species | ἀψίνθιον), 90% interval"); a.set_title("(a) Which plant?", loc="left")
    rows = [r for r in d["persistence"] if r["present_dmm"]]
    eras = ["Dioscorides\n1st c.", "Galen\n2nd c.", "John the\nPhysician", "modern\n(expected)"]
    for i, r in enumerate(rows):
        vals = [1.0 if r["present_dmm"] else 0.0, None if r["present_galen"] is None else float(r["present_galen"]),
                None if r["present_jc"] is None else float(r["present_jc"]), r["expected_modern"]]
        for j, v in enumerate(vals):
            if v is None:
                b.add_patch(plt.Rectangle((j, i), 0.92, 0.85, fc="white", ec=LIGHT, lw=0.6, hatch="////"))
            else:
                b.add_patch(plt.Rectangle((j, i), 0.92, 0.85, fc=ACCENT if v >= 0.5 else (LIGHT if v == 0 else ACCENT2), ec="white"))
    b.set_xlim(0, 4); b.set_ylim(len(rows), 0); b.set_xticks([j + 0.46 for j in range(4)]); b.set_xticklabels(eras, fontsize=6.8)
    b.set_yticks([i + 0.42 for i in range(len(rows))]); b.set_yticklabels([UG.get(r["use_group"], r["use_group"]) for r in rows], fontsize=6.8)
    b.tick_params(length=0); [s.set_visible(False) for s in b.spines.values()]
    b.set_title("(b) Its uses through time (hatched = no linked text)", loc="left")
    fig.savefig(OUT / "fig_example.pdf")


if __name__ == "__main__":
    fig_identification(); fig_survival(); fig_backtest(); fig_example()
    print(sorted(p.name for p in OUT.glob("*.pdf")))
