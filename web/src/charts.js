import * as d3 from "d3";
import { sankey, sankeyLinkHorizontal } from "d3-sankey";
import { animate, inView, stagger } from "motion";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const EASE = [0.22, 1, 0.36, 1];
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function grow(container, sel = ".fill") {
  const els = container.querySelectorAll(sel);
  if (reduce) return;
  els.forEach((e) => (e.style.transform = "scaleX(0)"));
  inView(container, () => { animate(els, { scaleX: [0, 1] }, { duration: 1.1, ease: EASE, delay: stagger(0.08) }); }, { amount: 0.4 });
}

/* probability bars with interval whiskers ------------------------------------------------- */
export function probBars(el, cands) {
  el.innerHTML = cands.map((c) => {
    const none = c.taxon === "__unidentified__";
    return `<div class="pbar"><span class="name ${none ? "none" : ""}">${none ? "unidentified (∅)" : esc(c.name)}</span>
      <span class="track"><span class="fill ${none ? "none" : ""}" style="width:${(c.p * 100).toFixed(1)}%"></span>
      <span class="ci" style="left:${(c.lo * 100).toFixed(1)}%;width:${Math.max(0.4, (c.hi - c.lo) * 100).toFixed(1)}%"></span></span>
      <span class="val">${c.p.toFixed(2)}</span></div>`;
  }).join("");
  grow(el);
}

export function wordProbs(el, d) {
  el.innerHTML = `<p class="dlabel">P(plant | ἀψίνθιον) from the model</p><div></div>`;
  probBars(el.lastElementChild, d.candidates);
}

/* alluvial: Dioscorides → Galen → John the Physician → modern ------------------------------ */
export function alluvial(svg, flows) {
  const COLS = [["dmm", "Dioscorides"], ["galen", "Galen"], ["jc", "John the Physician"], ["modern", "Modern Greece"]];
  const color = { attested: "#3dbb82", absent: "#4a514d", "no record": "#232725", all: "#17744f" };
  const draw = (ug) => {
    const rows = flows.filter((f) => ug === "ALL" || f.use_group === ug);
    const nodes = new Map();
    const node = (col, state) => { const k = `${col}:${state}`; if (!nodes.has(k)) nodes.set(k, { id: k, col, state }); return k; };
    const links = new Map();
    const add = (a, b, n) => { const k = `${a}|${b}`; links.set(k, (links.get(k) || 0) + n); };
    rows.forEach((r) => {
      const s0 = node("dmm", "all"), s1 = node("galen", r.galen), s2 = node("jc", r.jc), s3 = node("modern", r.modern);
      add(s0, s1, r.n); add(s1, s2, r.n); add(s2, s3, r.n);
    });
    const W = 760, H = 440;
    const order = { attested: 0, absent: 1, "no record": 2, all: 0 };
    const graph = sankey().nodeId((d) => d.id).nodeWidth(14).nodePadding(16).nodeSort((a, b) => order[a.state] - order[b.state]).extent([[96, 34], [W - 120, H - 6]])({
      nodes: [...nodes.values()].map((d) => ({ ...d })),
      links: [...links].map(([k, v]) => ({ source: k.split("|")[0], target: k.split("|")[1], value: v })),
    });
    const s = d3.select(svg).attr("viewBox", `0 0 ${W} ${H}`);
    s.selectAll("*").remove();
    s.append("g").selectAll("text").data(COLS).join("text").attr("class", "col")
      .attr("x", (d, i) => 96 + i * ((W - 216 - 14) / 3) + 7).attr("y", 16).attr("text-anchor", "middle").text((d) => d[1]);
    const lk = s.append("g").attr("fill", "none").selectAll("path").data(graph.links).join("path")
      .attr("d", sankeyLinkHorizontal()).attr("stroke", (d) => color[d.target.state]).attr("stroke-opacity", 0.38)
      .attr("stroke-width", (d) => Math.max(1, d.width));
    lk.append("title").text((d) => `${d.value} uses: ${d.source.state === "all" ? "Dioscorides" : d.source.state} → ${d.target.state}`);
    s.append("g").selectAll("rect").data(graph.nodes).join("rect")
      .attr("x", (d) => d.x0).attr("y", (d) => d.y0).attr("width", (d) => d.x1 - d.x0).attr("height", (d) => Math.max(1, d.y1 - d.y0))
      .attr("rx", 3).attr("fill", (d) => color[d.state]);
    s.append("g").selectAll("text.n").data(graph.nodes.filter((d) => d.y1 - d.y0 > 10)).join("text")
      .attr("x", (d) => (d.col === "dmm" ? d.x0 - 8 : d.col === "modern" ? d.x1 + 8 : d.x1 + 6))
      .attr("y", (d) => (d.y0 + d.y1) / 2).attr("dy", "0.35em")
      .attr("text-anchor", (d) => (d.col === "dmm" ? "end" : "start"))
      .text((d) => `${d.state === "all" ? "all uses" : d.state} ${d.value}`);
    if (!reduce) {
      lk.attr("pathLength", 1).style("stroke-dasharray", "1 1").style("stroke-dashoffset", 1)
        .style("transition", (d, i) => `stroke-dashoffset 1.4s cubic-bezier(.22,1,.36,1) ${i * 0.02}s`);
      requestAnimationFrame(() => requestAnimationFrame(() => lk.style("stroke-dashoffset", 0)));
    }
  };
  let started = false;
  const start = () => { if (!started) { started = true; draw("ALL"); } };
  if (reduce) start(); else inView(svg, start, { amount: 0.2 });
  document.querySelectorAll("[data-ug]").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll("[data-ug]").forEach((x) => x.classList.toggle("on", x === b));
    started = true;
    draw(b.dataset.ug);
  }));
}

/* observed vs shuffled ------------------------------------------------------------------- */
export function nullBars(el, t, note) {
  const rows = [["Observed", t.observed_persisted_share, ""], ["Shuffled, average", t.null_mean, "null"], ["Shuffled, 95th percentile", t.null_95pct, "null"]];
  el.innerHTML = rows.map(([l, v, c]) => `<div class="nb ${c}"><div class="lbl"><span>${l}</span><b>${(v * 100).toFixed(1)}%</b></div><div class="tr"><div class="fl" style="width:${v * 100}%"></div></div></div>`).join("");
  note.textContent = `${t.n_rows} uses; p = ${t.p_value} over ${t.n_permutations.toLocaleString("en-GB")} shuffles. Caveat: the Mount Pelion study only covers skin ailments, which favours skin uses.`;
  grow(el, ".fl");
}

/* identification: model vs baselines ------------------------------------------------------ */
export function idChart(el, idn, note) {
  const r = idn.results;
  const rows = [
    ["Pharmakon", "model_calibrated", "main"],
    ["…without ethnobotanical counts", "ablation_without_f4_lit_ethno", "main"],
    ["+ plant-description match (LLM traits)", "model_plus_f1_morphology", "main"],
    ["Transfer model (all names)", "transfer_model_calibrated", "main"],
    ["Transfer + description match", "transfer_plus_f1_morphology", "main"],
    ["LLM judge (comparison only)", "baseline_llm_judge", "base"],
    ["Genus frequency", "baseline_genus_prior", "base"],
    ["Uniform guess", "baseline_uniform", "base"],
    ["LSJ dictionary", "baseline_lsj", "base"],
    ["Oracle: expert-coded traits", "ablation_plus_ORACLE_expert_traits", "oracle"],
  ].filter(([, k]) => r[k] && r[k].top1);
  const W = 560, rowH = 36, L = 250, H = rows.length * rowH + 40;
  const x = d3.scaleLinear([0, 1], [L, W - 20]);
  const s = d3.select(el).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  s.append("g").attr("class", "axis").attr("transform", `translate(0,${H - 24})`).call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(".0%")).tickSizeOuter(0));
  const g = s.append("g").selectAll("g").data(rows).join("g").attr("transform", (d, i) => `translate(0,${i * rowH + 14})`);
  g.append("text").attr("class", "lab").attr("x", L - 14).attr("y", 5).attr("text-anchor", "end").text((d) => d[0]);
  g.append("line").attr("x1", (d) => x(r[d[1]].top1.ci95[0])).attr("x2", (d) => x(r[d[1]].top1.ci95[1]))
    .attr("stroke", (d) => (d[2] === "main" ? "#b8e6cc" : "#6b736f")).attr("stroke-width", 2).attr("stroke-dasharray", (d) => (d[2] === "oracle" ? "4 3" : null));
  const dots = g.append("circle").attr("cx", (d) => x(r[d[1]].top1.mean)).attr("r", 7)
    .attr("fill", (d) => (d[2] === "main" ? "#3dbb82" : d[2] === "oracle" ? "#000" : "#8a938e")).attr("stroke", (d) => (d[2] === "oracle" ? "#b8e6cc" : "none")).attr("stroke-width", 2);
  g.append("text").attr("x", (d) => x(r[d[1]].top1.ci95[1]) + 8).attr("y", 5).text((d) => `${Math.round(r[d[1]].top1.mean * 100)}%`);
  if (!reduce) { dots.attr("r", 0); inView(el, () => { animate(dots.nodes(), { r: [0, 7] }, { type: "spring", stiffness: 220, damping: 12, delay: stagger(0.09) }); }, { amount: 0.4 }); }
  const m = r.model_calibrated, l = r.baseline_lsj;
  const f = r.model_plus_f1_morphology;
  note.textContent = `Brier score ${m.brier.mean.toFixed(2)} vs ${l.brier.mean.toFixed(2)} for the dictionary (lower is better). Calibration error ${m.ece.toFixed(2)}` +
    (f ? `, ${f.ece.toFixed(2)} once Dioscorides' plant descriptions are compared with modern ones — still above our ≤ 0.10 target.` : ` misses our ≤ 0.10 target.`) +
    ` The LLM judge may have memorised published identifications. Expert judgement is not ground truth.`;
}

/* backtest ------------------------------------------------------------------------------- */
export function forecastChart(fc, hits) {
  const cuts = Object.keys(fc.results).sort();
  const box = document.getElementById("cutoffs");
  box.innerHTML = cuts.map((c, i) => `<button class="chip ${i === cuts.length - 1 ? "on" : ""}" data-cut="${c}">${c}</button>`).join("");
  const el = document.getElementById("fcchart");
  const verdict = document.getElementById("fc-verdict");
  const models = [["Random", "random"], ["Popularity only", "popularity"], ["History only", "history"], ["History + popularity", "history+popularity"], ["Everything", "full"]];
  const draw = (cut) => {
    const res = fc.results[cut];
    const W = 560, rowH = 40, L = 190, H = models.length * rowH + 44;
    const x = d3.scaleLinear([0, Math.max(0.7, ...models.map(([, k]) => (res.bootstrap_ci[k] || [0, 0])[1]))], [L, W - 30]);
    el.innerHTML = "";
    const s = d3.select(el).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
    s.append("g").attr("class", "axis").attr("transform", `translate(0,${H - 24})`).call(d3.axisBottom(x).ticks(5).tickSizeOuter(0));
    const base = res.test.random.base_rate;
    s.append("line").attr("x1", x(base)).attr("x2", x(base)).attr("y1", 4).attr("y2", H - 24).attr("stroke", "#ff5a5f").attr("stroke-dasharray", "3 4");
    s.append("text").attr("x", x(base) + 6).attr("y", H - 30).text(`base rate ${(base * 100).toFixed(1)}%`);
    const g = s.append("g").selectAll("g").data(models).join("g").attr("transform", (d, i) => `translate(0,${i * rowH + 14})`);
    g.append("text").attr("class", "lab").attr("x", L - 14).attr("y", 5).attr("text-anchor", "end").text((d) => d[0]);
    g.filter((d) => res.bootstrap_ci[d[1]]).append("line").attr("x1", (d) => x(res.bootstrap_ci[d[1]][0])).attr("x2", (d) => x(res.bootstrap_ci[d[1]][1])).attr("stroke", "#b8e6cc").attr("stroke-width", 2);
    const c = g.append("circle").attr("cx", (d) => x(res.test[d[1]].auprc || 0)).attr("r", 7).attr("fill", (d) => (d[1].includes("history") ? "#3dbb82" : "#8a938e"));
    if (!reduce) c.each(function (d) { animate(this, { cx: [x(0), x(res.test[d[1]].auprc || 0)] }, { duration: 0.8, ease: EASE }); });
    g.append("text").attr("x", W - 4).attr("y", 5).attr("text-anchor", "end").text((d) => (res.test[d[1]].auprc ?? 0).toFixed(2));
    const dci = res.bootstrap_ci.delta_auprc_histpop_minus_pop || [];
    const pos = res.test.full.positives, n = res.test.full.n;
    verdict.innerHTML = `<b>${cut}:</b> of ${n} untested pairs, ${pos} gained support by ${fc.t_end}. Adding 2,000 years of history to research popularity changed the score (AUPRC) by between ${dci[0]?.toFixed(2)} and ${dci[1]?.toFixed(2)} (95% interval). ${dci[1] < 0 ? "That interval is below zero: here <b>history made the ranking worse than popularity alone</b>." : dci[0] > 0 ? "That interval is above zero: here <b>history added signal beyond popularity</b>." : "That interval includes zero: <b>history did not predict future studies beyond popularity</b>."} We report it as a finding, not a failure.`;
    const h = hits.filter((x) => String(x.cutoff) === cut && x.label === 1).slice(0, 3);
    if (h.length) verdict.innerHTML += `<br/><span class="fine">Ranked high at ${cut} and later studied: ${h.map((x) => `<i>${esc(x.accepted_name)}</i> for ${esc(x.mesh_label.toLowerCase())} (${x.first_support_year})`).join("; ")}.</span>`;
  };
  box.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
    box.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
    draw(b.dataset.cut);
  }));
  draw(cuts[cuts.length - 1]);
}
