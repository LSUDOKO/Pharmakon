// Pharmakon Worker: static site (assets) + read-only JSON API (/api/*) + MCP server (/mcp).
// The MCP endpoint speaks the Streamable HTTP transport statelessly: every POST carries one
// JSON-RPC message and gets one JSON response. Data are the same static files the site uses.

const DISCLAIMER =
  "Research hypotheses only, not medical advice. Nothing here recommends using any plant or shows safety or efficacy.";
const PROTOCOLS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"];
const SITE = "https://pharmakon.adoranto737.workers.dev";

const cache = new Map();
async function data(env, path) {
  if (!cache.has(path)) {
    const r = await env.ASSETS.fetch(new Request(`${SITE}/data/${path}`));
    if (!r.ok) throw new Error(`no data file ${path}`);
    cache.set(path, await r.json());
  }
  return cache.get(path);
}

const strip = (s) =>
  (s || "").normalize("NFD").replace(/[̀-ͯ̓̔͂ͅ]/g, "").toLowerCase().replace(/ς/g, "σ");
const clamp = (v, lo, hi, d) => Math.max(lo, Math.min(hi, Number.isFinite(+v) ? +v : d));

// ---------- tool implementations (shared by REST and MCP) ----------

async function searchNames(env, { query = "", filter = "all", limit = 15 } = {}) {
  const names = (await data(env, "names.json")).filter((n) => !n.chapter.endsWith(".preface"));
  const q = String(query).trim();
  const g = strip(q), t = q.toLowerCase();
  const hits = names.filter((n) => {
    if (filter === "identified" && !n.top) return false;
    if (filter === "gold" && !n.gold) return false;
    if (filter === "claims" && !n.claims) return false;
    if (!q) return true;
    return strip(n.lemma).includes(g) || n.translit.includes(t) || (n.species || []).join(" ").toLowerCase().includes(t);
  });
  return {
    total: hits.length,
    results: hits.slice(0, clamp(limit, 1, 50, 15)).map((n) => ({
      id: n.id, lemma: n.lemma, translit: n.translit, chapter: n.chapter,
      top_species: n.top, p_top: n.top ? n.p : null, expert_gold: n.gold, n_claims: n.claims,
    })),
  };
}

async function getName(env, { id } = {}) {
  if (!/^[a-z0-9-]+$/.test(id || "")) throw new Error("id must look like dmm-3-23 (from search_ancient_names)");
  const d = await data(env, `names/${id}.json`);
  return {
    id: d.id, lemma: d.lemma, translit: d.translit, chapter: d.chapter, model: d.model,
    later_names: { john_the_physician: d.jc, synonym_lists: d.synonyms },
    passages: d.passages.map((p) => ({ cts_urn: p.cts, greek: p.text, evidence_spans: [...new Set(p.spans)] })),
    uses: d.claims.filter((c) => c.status === "ok").map((c) => ({
      greek: c.condition_text_grc, gloss: c.condition_en, use_group: c.use_group, plant_part: c.plant_part, route: c.route,
      found_by: c.llm ? "llm (span verified)" : "rule lexicon",
    })),
    identification: d.candidates.map((c) => ({
      species: c.taxon === "__unidentified__" ? "(unidentified)" : c.name, taxon: c.taxon, family: c.family || null,
      p: c.p, ci90: [c.lo, c.hi], iucn: c.iucn || null, photo: c.image?.page || null,
      description_match: c.morph || [],
    })),
    through_time: d.persistence.map((r) => ({
      use_group: r.use_group, dioscorides: r.present_dmm, galen: r.present_galen, john_the_physician: r.present_jc,
      modern_greece_expected: r.expected_modern, pattern: r.pattern,
    })),
    galen: d.galen.slice(0, 1).map((g) => ({ cts_urn: g.cts, heading: g.heading, word_overlap_with_dioscorides: g.copy })),
    modern_greek_uses: d.modern.slice(0, 8),
    reader: `${SITE}/#name=${d.id}`,
  };
}

async function listLeads(env, { condition, species, min_p = 0, hide_toxic = false, limit = 10, offset = 0 } = {}) {
  const leads = await data(env, "leads.json");
  const c = (condition || "").toLowerCase(), s = (species || "").toLowerCase();
  const hits = leads.filter((l) =>
    l.p >= clamp(min_p, 0, 1, 0) && (!c || l.condition.toLowerCase().includes(c)) &&
    (!s || l.species.toLowerCase().includes(s)) && (!hide_toxic || !l.toxic));
  const o = clamp(offset, 0, 1e6, 0);
  return {
    total: hits.length,
    leads: hits.slice(o, o + clamp(limit, 1, 20, 10)).map(leadView),
  };
}

const leadView = (l) => ({
  rank: l.rank, rank_if_top1_identity_only: l.rank_top1, species: l.species, family: l.family, condition: l.condition,
  p_species: l.p, lead_score: l.score, known_toxicity: !!l.toxic, toxicity_source: l.tox_url || null,
  iucn: l.iucn || null, byzantine_use: !!l.jc, modern_greek_use: !!l.modern, has_evidence_path: !!l.has_paths,
  ancient_names: l.names, pubmed_query: l.query,
});

async function getLead(env, { rank } = {}) {
  const leads = await data(env, "leads.json");
  const l = leads.find((x) => x.rank === Number(rank));
  if (!l) throw new Error(`no lead with rank ${rank}; ranks run 1–${leads.length}`);
  const paths = (await data(env, "paths.json")).filter((p) => p.taxon_key === l.taxon && p.mesh_id === l.mesh);
  return {
    ...leadView(l),
    hypothesis: `May be worth testing for ${l.condition.toLowerCase()}; PubMed has no matching pharmacology paper yet.`,
    evidence_paths: paths.slice(0, 15).map((p) => ({
      compound_inchikey: p.inchikey, compound_chembl: p.molecule_chembl_id, target_chembl: p.target_chembl_id,
      disease: p.disease_name, pchembl: p.pchembl, open_targets_score: p.ot_score, path_strength: p.path_strength,
    })),
    pubmed_url: `https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(l.query)}`,
  };
}

async function listConditions(env) {
  const counts = {};
  for (const l of await data(env, "leads.json")) counts[l.condition] = (counts[l.condition] || 0) + 1;
  return { conditions: Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([condition, leads]) => ({ condition, leads })) };
}

const SECTIONS = {
  identification: "identify", persistence: "persistence", forecast: "forecast", leads: "leads",
  labels: "evidence-labels", extraction: "extract-claims", texts: "ingest-texts", chemistry: "link-chemistry",
  galen: "ingest-galen", graph: "build-kg",
};
async function getResults(env, { section = "overview" } = {}) {
  const R = await data(env, "results.json");
  if (section === "overview") {
    const id = R.identify.results;
    return {
      identification_top1_vs_experts: id.model_calibrated.top1, identification_brier: id.model_calibrated.brier,
      identification_ece: id.model_calibrated.ece, lsj_dictionary_baseline_top1: id.baseline_lsj.top1, transfer_model_top1: id.transfer_model_calibrated.top1,
      persistence_vs_null: R.persistence.permutation_test, galen_agreement_rate: R.persistence.galen_agreement_rate, jc_agreement_rate: R.persistence.jc_agreement_rate,
      leads: R.leads, extraction: { claims: R["extract-claims"].claims_total, span_verified_rate: R["extract-claims"].exact_span_verified_rate_kept },
      sections: Object.keys(SECTIONS),
    };
  }
  const key = SECTIONS[section];
  if (!key) throw new Error(`section must be overview or one of ${Object.keys(SECTIONS).join(", ")}`);
  return R[key];
}

const str = { type: "string" }, num = { type: "number" }, bool = { type: "boolean" };
const TOOLS = [
  {
    name: "search_ancient_names", fn: searchNames,
    description: "Search the ~650 plant and drug names in Dioscorides' De materia medica (1st c.) by Greek (accents optional), transliteration, or modern Latin species. Returns ids for get_ancient_name.",
    inputSchema: { type: "object", properties: {
      query: { ...str, description: "e.g. ἀψίνθιον, apsinthion, Artemisia" },
      filter: { type: "string", enum: ["all", "identified", "gold", "claims"], description: "identified = has a likely species; gold = expert-identified by Lardos et al. 2024; claims = has extracted uses" },
      limit: { ...num, description: "1–50, default 15" } } },
  },
  {
    name: "get_ancient_name", fn: getName,
    description: "Full record for one ancient name: Greek passages with CTS URNs and verbatim evidence spans, extracted uses, P(species | name) with 90% intervals, the use's survival through Galen, John the Physician (13th c.) and modern Greece, and modern Greek folk uses.",
    inputSchema: { type: "object", required: ["id"], properties: { id: { ...str, description: "e.g. dmm-3-23" } } },
  },
  {
    name: "list_leads", fn: listLeads,
    description: "Ranked research leads: plant–condition pairs used historically, with no matching PubMed pharmacology paper yet, weighted by identification certainty. Always check known_toxicity.",
    inputSchema: { type: "object", properties: {
      condition: { ...str, description: "substring of a MeSH condition, e.g. 'ulcer', 'burn'" },
      species: { ...str, description: "substring of a Latin name" },
      min_p: { ...num, description: "minimum P(species), 0–1" },
      hide_toxic: bool, limit: { ...num, description: "1–20, default 10" }, offset: num } },
  },
  {
    name: "get_lead", fn: getLead,
    description: "One lead by rank with its compound → human target → disease evidence paths (LOTUS, ChEMBL, Open Targets) and the exact PubMed query behind its 'unstudied' label.",
    inputSchema: { type: "object", required: ["rank"], properties: { rank: num } },
  },
  {
    name: "list_conditions", fn: listConditions,
    description: "Conditions that have leads, with counts. Use the names as list_leads condition filters.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "get_results", fn: getResults,
    description: "Evaluation results with confidence intervals: overview, identification (vs expert gold), persistence (vs permutation null), forecast (rolling-origin backtest), leads, labels, extraction, texts, chemistry, galen, graph.",
    inputSchema: { type: "object", properties: { section: { type: "string", enum: ["overview", ...Object.keys(SECTIONS)] } } },
  },
];

// ---------- MCP (JSON-RPC 2.0 over Streamable HTTP, stateless) ----------

async function rpc(env, msg) {
  const { id, method, params = {} } = msg;
  const ok = (result) => ({ jsonrpc: "2.0", id, result });
  const err = (code, message) => ({ jsonrpc: "2.0", id: id ?? null, error: { code, message } });
  switch (method) {
    case "initialize":
      return ok({
        protocolVersion: PROTOCOLS.includes(params.protocolVersion) ? params.protocolVersion : PROTOCOLS[0],
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "pharmakon", title: "Pharmakon", version: "1.0.0", websiteUrl: SITE },
        instructions: `Pharmakon maps Dioscorides' 1st-century Greek materia medica to modern species, traces each use for 2,000 years, and ranks untested research leads. ${DISCLAIMER} Mention toxicity flags whenever you present a lead.`,
      });
    case "ping":
      return ok({});
    case "tools/list":
      return ok({ tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema, annotations: { readOnlyHint: true, openWorldHint: false } })) });
    case "tools/call": {
      const tool = TOOLS.find((t) => t.name === params.name);
      if (!tool) return err(-32602, `unknown tool ${params.name}`);
      try {
        const out = { disclaimer: DISCLAIMER, ...(await tool.fn(env, params.arguments || {})) };
        return ok({ content: [{ type: "text", text: JSON.stringify(out, null, 1) }], structuredContent: out, isError: false });
      } catch (e) {
        return ok({ content: [{ type: "text", text: String(e.message || e) }], isError: true });
      }
    }
    default:
      return err(-32601, `method not found: ${method}`);
  }
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Accept, Mcp-Session-Id, Mcp-Protocol-Version, Authorization",
  "Access-Control-Expose-Headers": "Mcp-Session-Id",
};
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json; charset=utf-8", ...CORS } });

async function mcp(request, env) {
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
  if (request.method !== "POST")
    return json({ jsonrpc: "2.0", id: null, error: { code: -32000, message: "POST JSON-RPC messages to this endpoint" } }, 405);
  let body;
  try { body = await request.json(); } catch { return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "parse error" } }, 400); }
  const msgs = Array.isArray(body) ? body : [body];
  const replies = [];
  for (const m of msgs) if (m && m.method && m.id !== undefined) replies.push(await rpc(env, m));
  if (!replies.length) return new Response(null, { status: 202, headers: CORS }); // notifications only
  return json(Array.isArray(body) ? replies : replies[0]);
}

// ---------- REST ----------

async function api(url, env) {
  const p = Object.fromEntries(url.searchParams);
  const route = url.pathname.replace(/^\/api\/?/, "").replace(/\/$/, "");
  const fn = {
    names: () => searchNames(env, { query: p.q, filter: p.filter, limit: p.limit }),
    leads: () => listLeads(env, { condition: p.condition, species: p.species, min_p: p.min_p, hide_toxic: p.hide_toxic === "true", limit: p.limit, offset: p.offset }),
    conditions: () => listConditions(env),
    results: () => getResults(env, { section: p.section }),
  }[route.split("/")[0]];
  const [head, arg] = route.split("/");
  try {
    if (head === "names" && arg) return json({ disclaimer: DISCLAIMER, ...(await getName(env, { id: arg })) });
    if (head === "leads" && arg) return json({ disclaimer: DISCLAIMER, ...(await getLead(env, { rank: arg })) });
    if (fn) return json({ disclaimer: DISCLAIMER, ...(await fn()) });
    if (!route) return json({ disclaimer: DISCLAIMER, endpoints: ["/api/names?q=", "/api/names/{id}", "/api/leads?condition=&species=&min_p=&hide_toxic=&limit=&offset=", "/api/leads/{rank}", "/api/conditions", "/api/results?section=", "/mcp (MCP, POST JSON-RPC)"] });
    return json({ error: `unknown endpoint /api/${route}` }, 404);
  } catch (e) {
    return json({ error: String(e.message || e) }, 400);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/mcp" || url.pathname === "/mcp/") return mcp(request, env);
    if (url.pathname === "/api" || url.pathname.startsWith("/api/")) {
      if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
      return api(url, env);
    }
    return env.ASSETS.fetch(request);
  },
};
