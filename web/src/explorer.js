import { animate, stagger } from "motion";
import { probBars, esc } from "./charts.js";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const EASE = [0.22, 1, 0.36, 1];
const UG = {
  AN: "Andrology", BS: "Blood, spleen", CV: "Cardiovascular", DE: "Skin & wounds", FV: "Fever", GI: "Digestive", GY: "Gynaecology",
  IF: "Infections", LG: "Liver & gall", MA: "Pregnancy & birth", MC: "Mental", MS: "Muscles & joints", MN: "Metabolic", NC: "Neurological",
  OP: "Eyes", OC: "Mouth & teeth", OT: "Ears", RE: "Respiratory", RL: "Nose & throat", UR: "Urinary", XY: "Other",
};
const FEAT = {
  f2_geo_log_occ: "grows in Greece/Cyprus/Turkey", f2_present_gr: "recorded in Greece", f3_vernacular_sim: "modern Greek name echoes it",
  f3_epithet_sim: "Latin name echoes the Greek", f4_lit_dmm: "botanical historians propose it", f4_lit_ethno: "ethnobotanists propose it",
  f4_lsj: "LSJ dictionary gives it", f6_genus_consensus: "sources agree on the genus",
};

let NAMES = [];
let filter = "all";
let current = null;
const cache = new Map();

const strip = (s) => (s || "").normalize("NFD").replace(/[̀-ͯ̓̔͂ͅ]/g, "").toLowerCase().replace(/ς/g, "σ");

export function initExplorer(names) {
  NAMES = names.filter((n) => !n.chapter.endsWith(".preface")).map((n) => ({ ...n, _k: strip(n.lemma), _s: (n.species || []).join(" ").toLowerCase() }));
  const q = document.getElementById("q");
  q.addEventListener("input", render);
  document.querySelectorAll(".ex-side .chip").forEach((c) => c.addEventListener("click", () => {
    filter = c.dataset.filter;
    document.querySelectorAll(".ex-side .chip").forEach((x) => x.classList.toggle("on", x === c));
    render();
  }));
  q.value = "";
  render();
  const fromHash = location.hash.startsWith("#name=") ? location.hash.slice(6) : null;
  openName(fromHash || "dmm-3-23", false);
}

function matches(n, term) {
  if (filter === "identified" && !n.top) return false;
  if (filter === "gold" && !n.gold) return false;
  if (filter === "claims" && !n.claims) return false;
  if (!term) return true;
  const t = term.toLowerCase();
  return n._k.includes(strip(term)) || n.translit.includes(t) || n._s.includes(t);
}

function render() {
  const term = document.getElementById("q").value.trim();
  const list = NAMES.filter((n) => matches(n, term));
  const ul = document.getElementById("name-list");
  ul.innerHTML = list.slice(0, 250).map((n) => `
    <li><button role="option" data-id="${n.id}" aria-selected="${n.id === current}">
      <span class="g" lang="grc">${esc(n.lemma)}</span>
      <span class="t">${n.top ? esc(n.top) : `${esc(n.translit)} · not identified`}</span>
      <span class="p">${n.top ? Math.round(n.p * 100) + "%" : "∅"}</span>
    </button></li>`).join("");
  document.getElementById("list-count").textContent = list.length > 250 ? `Showing 250 of ${list.length} names. Refine the search to see more.` : `${list.length} names`;
  ul.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => openName(b.dataset.id)));
}

async function load(id) {
  if (!cache.has(id)) {
    const r = await fetch(`/data/names/${id}.json`);
    if (!r.ok) throw new Error(`No record for ${id}`);
    cache.set(id, await r.json());
  }
  return cache.get(id);
}

function highlight(text, spans) {
  let out = esc(text);
  [...new Set(spans)].sort((a, b) => b.length - a.length).forEach((s) => {
    const e = esc(s);
    if (e && out.includes(e)) out = out.replace(e, `<mark>${e}</mark>`);
  });
  return out;
}

const perseids = (id) => `https://cts.perseids.org/read/greekLit/tlg0656/tlg001/1st1K-grc1/${id.split(":")[1].replace(/dup\d+/g, "")}`;

function dot(v, linked = true) {
  if (!linked || v === null || v === undefined) return `<span class="dot na">no record</span>`;
  return v ? `<span class="dot yes"><i></i>attested</span>` : `<span class="dot no"><i></i>absent</span>`;
}

export async function openName(id, scroll = true) {
  current = id;
  document.querySelectorAll("#name-list button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.id === id)));
  const el = document.getElementById("detail");
  let d;
  try { d = await load(id); } catch (e) { el.innerHTML = `<p class="empty">${esc(e.message)}. Pick another name from the list.</p>`; return; }
  history.replaceState(null, "", `#name=${id}`);
  const top = d.candidates[0];
  const cands = d.candidates.filter((c) => c.taxon !== "__unidentified__");
  const claimsOk = d.claims.filter((c) => c.status === "ok");
  const groups = [...new Set(claimsOk.map((c) => c.use_group))];
  el.innerHTML = `
    <div class="dh"><h3 lang="grc">${esc(d.lemma)}</h3><span class="meta">${esc(d.translit)} · De materia medica ${esc(d.chapter.replace("dmm:", ""))}</span></div>
    <p class="dsub">${d.jc.length ? `John the Physician (13th c.) calls it <span class="greek" lang="grc">${d.jc.map(esc).join(", ")}</span>. ` : ""}${d.synonyms.length ? `Later synonym lists add <span class="greek" lang="grc">${d.synonyms.slice(0, 6).map(esc).join(", ")}</span>.` : ""}</p>
    <div class="dgrid">
      <div>
        <p class="dlabel">What Dioscorides wrote${claimsOk.length ? ` — ${claimsOk.length} uses highlighted` : ""}</p>
        <div class="passages">${d.passages.map((p) => `<p class="passage" lang="grc">${highlight(p.text, p.spans)}</p>
          <a class="cite" href="${perseids(p.id)}" target="_blank" rel="noopener">${esc(p.cts)} — open in the Perseids reader</a>`).join("")}</div>
        ${groups.length ? `<p class="dlabel">Uses by body system</p><div class="tags">${groups.map((g) => `<span class="tag">${UG[g] || g}</span>`).join("")}</div>` : ""}
      </div>
      <div>
        <p class="dlabel">Which plant is it?</p>
        <div class="probs"></div>
        <p class="fine">${top && top.taxon !== "__unidentified__" ? `This name rests ${Math.round(top.p * 100)}% on <i>${esc(top.name)}</i>. ` : "No candidate is likely enough; most weight sits on “unidentified”. "}Whiskers show the 90% bootstrap interval.</p>
        <div class="cands">${cands.map((c) => `
          <div class="cand">
            ${c.image ? `<a href="${c.image.page}" target="_blank" rel="noopener" aria-label="Photo of ${esc(c.name)} on Wikimedia Commons"><img class="ph" src="${c.image.thumb}" alt="${esc(c.name)}" loading="lazy" referrerpolicy="no-referrer"/></a>` : `<div class="ph blank" data-folio="${c.name.length % 3}" aria-hidden="true"></div>`}
            <div>
              <div class="nm">${esc(c.name)}</div>
              <div class="fam">${esc(c.family || "")} · P = ${c.p.toFixed(2)}${c.iucn ? ` · IUCN: ${esc(c.iucn)}` : ""}</div>
              <div class="contrib">${Object.entries(c.contrib).filter(([, v]) => Math.abs(v) > 0.05).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])).slice(0, 3)
                .map(([k, v]) => `<span class="${v > 0 ? "pos" : "neg"}">${v > 0 ? "+" : "−"} ${FEAT[k] || k}</span>`).join("")}</div>
              ${c.image ? `<div class="credit">Photo: Wikimedia Commons</div>` : ""}
            </div>
          </div>`).join("")}</div>
      </div>
    </div>
    ${d.persistence.length ? `<div class="eras"><p class="dlabel">Two thousand years of this plant's uses</p>
      <table><thead><tr><th>Use</th><th>Dioscorides, 1st c.</th><th>Galen, 2nd c.</th><th>John the Physician, 13th c.</th><th>Modern Greece</th></tr></thead><tbody>
      ${d.persistence.filter((r) => r.present_dmm || r.expected_modern >= 0.5).map((r) => `<tr><td>${UG[r.use_group] || r.use_group}</td><td>${dot(r.present_dmm)}</td><td>${dot(r.present_galen, r.present_galen !== null)}</td><td>${dot(r.present_jc, r.present_jc !== null)}</td>
        <td>${dot(r.expected_modern >= 0.5)} <span class="fine">${r.expected_modern.toFixed(2)}</span></td></tr>`).join("")}
      </tbody></table><p class="fine">Modern column: probability-weighted chance that the identified plant (or its genus) is used for this today.</p></div>` : ""}
    ${d.galen.length ? `<div class="galen"><p class="dlabel">Galen on the same drug</p><p class="passage" lang="grc">${highlight(d.galen[0].text, d.galen[0].spans)}${d.galen[0].text.length >= 900 ? "…" : ""}</p>
      <span class="fine">${esc(d.galen[0].cts)} · ${Math.round(d.galen[0].copy * 100)}% word overlap with Dioscorides</span></div>` : ""}
    ${d.modern.length ? `<p class="dlabel" style="margin-top:24px">In modern Greek villages</p><ul class="modern-list">${d.modern.slice(0, 5).map((m) =>
      `<li><b><i>${esc(m.accepted_name || "")}</i></b> (${esc(m.local_name || "")}) — ${esc(m.ailment_text).slice(0, 160)} <span class="fine">[${m.study === "eth_pelion" ? "Mount Pelion 2023" : "North Aegean 2018"}]</span></li>`).join("")}</ul>` : ""}
  `;
  probBars(el.querySelector(".probs"), d.candidates);
  if (!reduce) animate(el.children, { opacity: [0, 1], y: [14, 0] }, { duration: 0.5, ease: EASE, delay: stagger(0.05) });
  if (scroll) document.getElementById("explorer").scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
}
