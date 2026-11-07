import { animate, stagger } from "motion";
import { esc } from "./charts.js";
import { openName } from "./explorer.js";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const EASE = [0.22, 1, 0.36, 1];
let LEADS = [], PATHS = [], shown = 12;

export function initLeads(leads, paths) {
  LEADS = leads;
  PATHS = paths;
  const sel = document.getElementById("lead-cond");
  [...new Set(leads.map((l) => l.condition))].sort().forEach((c) => sel.insertAdjacentHTML("beforeend", `<option>${esc(c)}</option>`));
  const pmin = document.getElementById("pmin");
  pmin.addEventListener("input", () => { document.getElementById("pmin-out").textContent = Number(pmin.value).toFixed(2); shown = 12; render(); });
  sel.addEventListener("change", () => { shown = 12; render(); });
  document.getElementById("hide-tox").addEventListener("change", () => { shown = 12; render(); });
  document.getElementById("more").addEventListener("click", () => { shown += 12; render(true); });
  document.getElementById("csv").addEventListener("click", csv);
  render();
}

function filtered() {
  const cond = document.getElementById("lead-cond").value;
  const pmin = Number(document.getElementById("pmin").value);
  const hide = document.getElementById("hide-tox").checked;
  return LEADS.filter((l) => l.p >= pmin && (!cond || l.condition === cond) && (!hide || !l.toxic));
}

function card(l) {
  return `<button class="lead" data-rank="${l.rank}" aria-label="Lead ${l.rank}: ${esc(l.species)} for ${esc(l.condition)}">
    ${l.image ? `<img class="img" src="${l.image.thumb}" alt="" loading="lazy" referrerpolicy="no-referrer"/>` : `<div class="img blank" data-folio="${l.rank % 3}" aria-hidden="true"></div>`}
    <span class="rank glass">#${l.rank}</span>
    <div class="body">
      <span class="sp">${esc(l.species)}</span>
      <span class="cond">${esc(l.condition)} · ${esc(l.family || "")}</span>
      <div class="meters">
        <span>plant certainty</span><span class="tr"><span class="fl" style="display:block;width:${l.p * 100}%"></span></span><b>${l.p.toFixed(2)}</b>
        <span>lead score</span><span class="tr"><span class="fl" style="display:block;width:${Math.min(1, l.score / 0.4) * 100}%"></span></span><b>${l.score.toFixed(3)}</b>
      </div>
      <div class="tags">
        ${l.toxic ? `<span class="tag tox">⚠ Known toxicity</span>` : ""}
        ${l.jc ? `<span class="tag ok">Byzantine use</span>` : ""}
        ${l.modern ? `<span class="tag ok">Modern Greek use</span>` : ""}
        ${l.has_paths ? `<span class="tag ok">Compound → target path</span>` : ""}
        ${l.iucn ? `<span class="tag">IUCN: ${esc(l.iucn)}</span>` : ""}
        ${l.rank_top1 !== l.rank ? `<span class="tag">#${l.rank_top1} if certainty ignored</span>` : ""}
      </div>
    </div></button>`;
}

function render(append = false) {
  const list = filtered();
  const grid = document.getElementById("lead-grid");
  const before = append ? grid.children.length : 0;
  grid.innerHTML = list.length ? list.slice(0, shown).map(card).join("") : `<p class="empty">No leads match these filters. Lower the certainty threshold or pick another condition.</p>`;
  document.getElementById("more").hidden = shown >= list.length;
  grid.querySelectorAll(".lead").forEach((b) => b.addEventListener("click", () => detail(LEADS.find((l) => String(l.rank) === b.dataset.rank))));
  const fresh = [...grid.querySelectorAll(".lead")].slice(before);
  if (!reduce && fresh.length) animate(fresh, { opacity: [0, 1], y: [24, 0], scale: [0.97, 1] }, { duration: 0.6, ease: EASE, delay: stagger(0.04) });
}

function detail(l) {
  let dlg = document.querySelector("dialog.paths");
  if (!dlg) { dlg = document.createElement("dialog"); dlg.className = "paths"; document.body.appendChild(dlg); }
  const ps = PATHS.filter((p) => p.taxon_key === l.taxon && p.mesh_id === l.mesh).slice(0, 8);
  dlg.innerHTML = `
    <button class="btn glass small close" aria-label="Close">Close</button>
    <h3>${esc(l.species)}</h3>
    <p>Hypothesis: may be worth testing for <b>${esc(l.condition.toLowerCase())}</b>. PubMed has no matching pharmacology paper yet.${l.toxic ? ` <span class="tag tox">⚠ Known toxicity</span> <a href="${l.tox_url}" target="_blank" rel="noopener">PubChem hazard record</a>.` : ""}</p>
    <p class="dlabel">Evidence paths: compound → human target → disease</p>
    ${ps.length ? ps.map((p) => `<div class="path-row"><span title="${esc(p.inchikey)}">${esc(p.molecule_chembl_id)}</span><span>${esc(p.target_chembl_id)} (${esc(p.ct_tier)})</span><span>${esc(p.disease_name)}</span><span>strength ${Number(p.path_strength).toFixed(2)}</span></div>`).join("")
      : `<p class="fine">No closed compound → target → disease path within the pilot's linking caps.</p>`}
    <p class="dlabel" style="margin-top:18px">The PubMed query behind the label</p>
    <code>${esc(l.query)}</code>
    <p style="margin-top:16px"><a href="https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(l.query)}" target="_blank" rel="noopener">Run this query on PubMed</a></p>
    <div class="cta-row" style="justify-content:flex-start;margin-top:12px">${l.names.map((n) => `<button class="btn glass small" data-name="${n}">Open the ancient name</button>`).join("")}</div>`;
  dlg.querySelector(".close").addEventListener("click", () => dlg.close());
  dlg.querySelectorAll("[data-name]").forEach((b) => b.addEventListener("click", () => { dlg.close(); openName(b.dataset.name); }));
  dlg.showModal();
  if (!reduce) animate(dlg, { opacity: [0, 1], scale: [0.96, 1] }, { type: "spring", stiffness: 260, damping: 22 });
}

function csv() {
  const rows = filtered();
  const cols = ["rank", "species", "family", "condition", "p", "score", "toxic", "iucn", "jc", "modern", "query"];
  const out = [cols.join(","), ...rows.map((r) => cols.map((c) => `"${String(r[c] ?? "").replace(/"/g, '""')}"`).join(","))].join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([out], { type: "text/csv" }));
  a.download = "pharmakon_leads.csv";
  a.click();
}
