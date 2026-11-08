// Every number the results / impact / outro scenes put on screen. Read from public/data at build time — never retyped.
import identify from "../../../public/data/identify.json";
import persistence from "../../../public/data/persistence.json";
import forecast from "../../../public/data/forecast.json";
import leadsStage from "../../../public/data/leads.json"; // reports/stages/leads.json (stage summary)
import leadsWeb from "../../../public/data/leads_web.json"; // web/public/data/leads.json (the 1,781 leads)
import wormwood from "../../../public/data/dmm-3-23.json";
import { Line, scene } from "../../timing";

const R = identify.results;

// identify.json → results.*.top1 {mean, ci95}, brier.mean, ece
export const ID_ROWS = [
  { label: "Pharmakon", sub: "calibrated model", top1: R.model_calibrated.top1, tone: "hi" as const },
  { label: "+ description match", sub: "plant-description feature", top1: R.model_plus_f1_morphology.top1, tone: "hi" as const },
  { label: "LLM judge", sub: "comparison only — may have memorised", top1: R.baseline_llm_judge.top1, tone: "ghost" as const },
  { label: "LSJ dictionary", sub: "the standard reference", top1: R.baseline_lsj.top1, tone: "dim" as const },
];
export const N_NAMES = R.model_calibrated.n_names; // identify.json → results.model_calibrated.n_names (61)
export const BRIER = { model: R.model_calibrated.brier.mean, lsj: R.baseline_lsj.brier.mean }; // 0.50 vs 1.34
export const ECE = { before: R.model_calibrated.ece, after: R.model_plus_f1_morphology.ece, target: 0.1 }; // 0.21 → 0.14; target from the brief

// persistence.json → permutation_test
export const PERM = persistence.permutation_test;
export const MODERN_RECORDS = persistence.modern_records; // persistence.json → modern_records (1,226) // observed 0.4862, null_mean 0.4078, null_95pct 0.4331, p 0.001, n_permutations 1000, n_rows 508

// forecast.json → results[cutoff]; delta point = test["history+popularity"].auprc − test.popularity.auprc (derived)
type Cut = keyof typeof forecast.results;
export const BACKTEST = (forecast.cutoffs.map(String) as Cut[]).map((c) => {
  const r = forecast.results[c];
  return {
    year: c,
    ci: r.bootstrap_ci.delta_auprc_histpop_minus_pop as number[],
    delta: r.test["history+popularity"].auprc - r.test.popularity.auprc,
    pop: r.test.popularity.auprc,
    base: r.test.popularity.base_rate,
    n: r.test.popularity.n,
    positives: r.test.popularity.positives,
  };
});

// leads.json (stage) → unsupported_today, top20_*
export const LEADS = leadsStage;

// leads_web.json → top distinct species that are not toxic-flagged and have P(species) ≥ 0.5 (the demo's certainty filter)
type Lead = (typeof leadsWeb)[number];
const distinct = (pred: (l: Lead) => boolean, n: number) => {
  const out: Lead[] = [];
  for (const l of leadsWeb as Lead[]) {
    if (out.length >= n) break;
    if (pred(l) && !out.some((o) => o.species === l.species)) out.push(l);
  }
  return out;
};
export const VIALS = distinct((l) => !l.toxic && l.p >= 0.5, 10);
export const TOP_LEAD = (leadsWeb as Lead[])[0]; // rank 1
export const IUCN_ROWS = (() => {
  const out: Lead[] = [];
  for (const status of ["near threatened", "Data Deficient", "least concern"]) out.push(...distinct((l) => l.iucn === status, 1));
  return out;
})();
// distinct species with a non-null IUCN status / distinct species in the leads
export const IUCN_SPECIES = new Set((leadsWeb as Lead[]).filter((l) => !!l.iucn).map((l) => l.species)).size;
export const SPECIES_TOTAL = new Set((leadsWeb as Lead[]).map((l) => l.species)).size;

// dmm-3-23.json → lemma (ἀψίνθιον), chapter
export const WORMWOOD = { lemma: wormwood.lemma, chapter: wormwood.chapter };

// ---------- formatting ----------
export const pct = (x: number, d = 0) => `${(x * 100).toFixed(d)}%`;
export const signed = (x: number, d = 2) => `${x < 0 ? "−" : "+"}${Math.abs(x).toFixed(d)}`;
export const fmt = (x: number) => x.toLocaleString("en-US");

/** Frame (scene-local) where `phrase` is spoken inside VO line `id`, estimated by its character position. */
export const at = (sceneId: string, id: string, phrase = "") => {
  const l = scene(sceneId).lines.find((x: Line) => x.id === id)!;
  const i = phrase ? l.text.indexOf(phrase) : 0;
  if (i < 0) throw new Error(`phrase "${phrase}" not in ${id}`);
  if (l.words) {
    // presenter takes: real word timing (text is the words joined by single spaces)
    let p = 0;
    for (const w of l.words) {
      if (p + w.w.length > i) return l.from + Math.round(w.s * 30);
      p += w.w.length + 1;
    }
  }
  return Math.round(l.from + (l.dur * i) / l.text.length);
};
export const end = (sceneId: string, id: string) => {
  const l = scene(sceneId).lines.find((x: Line) => x.id === id)!;
  return l.from + l.dur;
};
