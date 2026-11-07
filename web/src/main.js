import { animate, scroll, inView, stagger } from "motion";
import { initExplorer, openName } from "./explorer.js";
import { wordProbs, alluvial, nullBars, idChart, forecastChart } from "./charts.js";
import { initLeads } from "./leads.js";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
document.documentElement.classList.add("js");
const EASE = [0.22, 1, 0.36, 1];
const fmt = (n) => Number(n).toLocaleString("en-GB");

async function getJSON(p) {
  const r = await fetch(p);
  if (!r.ok) throw new Error(`${p}: ${r.status}`);
  return r.json();
}

/* ---------------------------------------------------------------- hero choreography */
function heroIntro() {
  const a = document.querySelector(".sheet-a");
  const b = document.querySelector(".sheet-b");
  const band = document.querySelector(".band");
  const mark = document.querySelector(".wordmark .chrome");
  if (reduce) return;
  animate(a, { x: ["18%", "0%"], y: ["-18%", "0%"], opacity: [0, 1] }, { duration: 1.4, ease: EASE });
  animate(b, { x: ["-18%", "0%"], y: ["18%", "0%"], opacity: [0, 1] }, { duration: 1.4, ease: EASE, delay: 0.08 });
  animate(band, { clipPath: ["inset(0 50% 0 50%)", "inset(-200px -200vw -200px -200vw)"] }, { duration: 1.1, ease: EASE, delay: 0.45 });
  animate(".wm-mark", { rotate: [-90, 0], scale: [0.4, 1], opacity: [0, 1] }, { type: "spring", stiffness: 120, damping: 14, delay: 0.9 });
  mark.style.backgroundSize = "100% 260%";
  animate(mark, { backgroundPositionY: ["100%", "0%"], opacity: [0, 1] }, { duration: 1.6, ease: EASE, delay: 0.8 });
  animate(".dim", { opacity: [0, 1] }, { duration: 0.8, delay: stagger(0.15, { startDelay: 1.3 }) });
  animate(".hero-copy > *", { opacity: [0, 1], y: [18, 0] }, { duration: 0.9, ease: EASE, delay: stagger(0.12, { startDelay: 1.2 }) });

  // Scroll-linked: the sheets tear apart and the band sinks as you leave the hero.
  const hero = document.querySelector(".hero");
  const opts = { target: hero, offset: ["start start", "end start"] };
  scroll(animate(a, { x: ["0%", "22%"], y: ["0%", "-20%"], rotate: [0, 4] }, { ease: "linear" }), opts);
  scroll(animate(b, { x: ["0%", "-22%"], y: ["0%", "20%"], rotate: [0, -4] }, { ease: "linear" }), opts);
  scroll(animate(band, { scale: [1, 0.9], opacity: [1, 0.2] }, { ease: "linear" }), opts);
  scroll(animate(".hero-copy", { y: [0, 80], opacity: [1, 0] }, { ease: "linear" }), opts);
}

/* ---------------------------------------------------------------- reveals + counters */
function reveals() {
  if (reduce) return;
  inView(".reveal", (el) => {
    animate(el, { opacity: [0, 1], y: [28, 0], filter: ["blur(6px)", "blur(0px)"] }, { duration: 0.9, ease: EASE });
  }, { amount: 0.25 });
  // folio parallax inside the sticky column
  const folio = document.querySelector(".word-folio img");
  scroll(animate(folio, { y: [40, -40], scale: [1.04, 1] }, { ease: "linear" }), { target: document.querySelector(".word"), offset: ["start end", "end start"] });
}

function countUp(el, to, decimals = 0) {
  if (reduce) { el.textContent = decimals ? to.toFixed(decimals) : fmt(to); return; }
  animate(0, to, { duration: 1.6, ease: EASE, onUpdate: (v) => { el.textContent = decimals ? v.toFixed(decimals) : fmt(Math.round(v)); } });
}

/* ---------------------------------------------------------------- liquid glass physics */
function glassButtons() {
  document.querySelectorAll(".btn.glass").forEach((btn) => {
    btn.addEventListener("pointermove", (e) => {
      const r = btn.getBoundingClientRect();
      btn.style.setProperty("--gx", `${((e.clientX - r.left) / r.width) * 100}%`);
      btn.style.setProperty("--gy", `${((e.clientY - r.top) / r.height) * 100}%`);
      if (!reduce && btn.hasAttribute("data-magnetic")) {
        animate(btn, { x: (e.clientX - r.left - r.width / 2) * 0.18, y: (e.clientY - r.top - r.height / 2) * 0.3 }, { type: "spring", stiffness: 300, damping: 18 });
      }
    });
    btn.addEventListener("pointerleave", () => {
      btn.style.setProperty("--gx", "50%");
      btn.style.setProperty("--gy", "0%");
      if (!reduce) animate(btn, { x: 0, y: 0 }, { type: "spring", stiffness: 260, damping: 15 });
    });
  });
}

/* ---------------------------------------------------------------- pipeline steps */
function steps(res) {
  const s = (k) => res[k] || {};
  const idn = s("identify");
  const items = [
    ["Read the Greek", s("ingest-texts").passages + s("ingest-galen").galen_passages_books_6_8, "passages, Dioscorides + Galen"],
    ["Extract uses", s("extract-claims").claims_kept, "claims, each with its exact Greek words"],
    ["Name the plants", idn.clusters_top1_is_taxon, `names with a likely species (of ${fmt(idn.clusters_scored)})`],
    ["Link the chemistry", s("link-chemistry").taxon_compound_pairs, "plant–compound pairs, dated"],
    ["Follow through time", s("persistence").rows, "uses traced across four eras"],
    ["Test against the future", s("evidence-labels").pairs, "plant–condition pairs backtested"],
    ["Rank the leads", s("leads").unsupported_today, "untested hypotheses, uncertainty-weighted"],
  ];
  const ol = document.getElementById("steps");
  items.forEach(([title, n, label]) => {
    const li = document.createElement("li");
    li.className = "step";
    li.innerHTML = `<strong data-count="${n}">0</strong><h3>${title}</h3><span>${label}</span>`;
    ol.appendChild(li);
  });
  const line = ol.querySelector(".steps-line");
  if (!reduce) {
    line.style.transformOrigin = "0 50%";
    scroll(animate(line, { scaleX: [0, 1] }, { ease: "linear" }), { target: ol, offset: ["start 85%", "end 55%"] });
    animate(".step", { opacity: 0 }, { duration: 0 });
    inView(ol, () => {
      animate(".step", { opacity: [0, 1], y: [24, 0] }, { duration: 0.7, ease: EASE, delay: stagger(0.09) });
      ol.querySelectorAll("[data-count]").forEach((el) => countUp(el, Number(el.dataset.count)));
    }, { amount: 0.3 });
  } else {
    ol.querySelectorAll("[data-count]").forEach((el) => countUp(el, Number(el.dataset.count)));
  }
}

function sources() {
  const list = [
    ["Dioscorides, De materia medica", "Wellmann ed., First1KGreek TEI · CC BY-SA 4.0"],
    ["Galen, De simpl. med. 6–8", "Kühn ed., First1KGreek TEI · CC BY-SA 4.0"],
    ["Lardos et al. 2024 expert data", "figshare 10.17637/rh.23736189 · CC BY 4.0"],
    ["Liddell–Scott–Jones lexicon", "Perseus Digital Library · CC BY-SA 4.0"],
    ["Modern Greek field studies", "Mount Pelion 2023, North Aegean 2018 · CC BY"],
    ["GBIF backbone + occurrences", "species verification, counts only"],
    ["Wikidata / LOTUS", "compounds with dated references · CC0"],
    ["ChEMBL 37", "bioactivities with document years · CC BY-SA 3.0"],
    ["Open Targets", "target–disease associations · CC0"],
    ["NLM MeSH + PubMed", "disease vocabulary, per-year evidence counts"],
    ["PubChem", "GHS hazard citations for toxicity flags"],
  ];
  document.getElementById("sources").innerHTML = list.map(([b, s]) => `<li><b>${b}</b><span>${s}</span></li>`).join("");
}

function tour() {
  const v = document.getElementById("tour");
  const b = document.getElementById("tour-play");
  let userPaused = false;
  const label = () => { b.textContent = v.paused ? "Play tour" : "Pause tour"; };
  b.addEventListener("click", () => { if (v.paused) { userPaused = false; v.play(); } else { userPaused = true; v.pause(); } label(); });
  v.addEventListener("play", label); v.addEventListener("pause", label);
  inView(v, () => { if (!userPaused && !reduce) v.play().catch(() => {}); return () => v.pause(); }, { amount: 0.5 });
  if (reduce) b.textContent = "Play tour";
  if (!reduce) scroll(animate(".tour-frame", { rotateX: [12, 0], scale: [0.92, 1] }, { ease: "linear" }), { target: document.querySelector(".tour"), offset: ["start end", "center center"] });
}

function navSpy() {
  const links = [...document.querySelectorAll(".nav nav a")];
  links.forEach((a) => {
    const sec = document.querySelector(a.getAttribute("href"));
    if (sec) inView(sec, () => { links.forEach((l) => l.classList.toggle("active", l === a)); }, { amount: 0.3 });
  });
}

async function main() {
  heroIntro();
  glassButtons();
  sources();
  tour();
  const [res, names, leads] = await Promise.all([getJSON("/data/results.json"), getJSON("/data/names.json"), getJSON("/data/leads.json")]);
  document.querySelector('[data-stat="passages"]').textContent = fmt(res["ingest-texts"].passages);
  document.querySelector('[data-stat="gold"]').textContent = fmt(res.gold_counts.names);
  steps(res);
  wordProbs(document.getElementById("word-probs"), await getJSON("/data/names/dmm-3-23.json"));
  initExplorer(names);
  alluvial(document.getElementById("alluvial"), res.flows);
  nullBars(document.getElementById("nullbars"), res.persistence.permutation_test, document.getElementById("null-note"));
  idChart(document.getElementById("idchart"), res.identify, document.getElementById("id-note"));
  forecastChart(res.forecast, res.forecast_hits);
  initLeads(leads, await getJSON("/data/paths.json"));
  reveals();
  navSpy();
  document.querySelectorAll("[data-open]").forEach((a) => a.addEventListener("click", () => openName(a.dataset.open)));
}

main().catch((e) => {
  console.error(e);
  const d = document.getElementById("detail");
  if (d) d.innerHTML = `<p class="empty">The data files did not load (${e.message}). Reload the page; if it persists, the deployment is missing <code>/data</code>.</p>`;
});
