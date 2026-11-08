// Scene "hood" — s09_a: the knowledge graph (real counts). s09_b: one real lead path (get_lead rank 1) lights hop by hop,
// Greek words → κύαμος → Vicia faba → naringenin → CA4 → retinitis pigmentosa, each hop with its edge kind and source.
import React from "react";
import { random, useCurrentFrame } from "remotion";
import { C, CountUp, DIDOT, EASE_IN, MONO, OUTFIT, SAFE, Stage, Words, ease } from "../brand";
import { line } from "../timing";
import { Chip, Code, Kicker, Tick, at } from "./datamethod/ui";
import kg from "../../public/data/build-kg.json";
import claims from "../../public/data/extract-claims.json";
import hp from "../../public/data/hood-path.json";

const A = line("hood", "s09_a").from;
const B = line("hood", "s09_b").from;

// ---- background graph: seeded jittered grid, node kinds in the real proportions of build-kg.json ----
const KINDS = Object.keys(kg.node_kinds) as (keyof typeof kg.node_kinds)[];
const TOTAL_NODES = KINDS.reduce((s, k) => s + kg.node_kinds[k], 0);
const STYLE: Record<string, { r: number; fill: string; ring?: boolean }> = {
  Passage: { r: 3, fill: C.dim },
  AncientName: { r: 4.5, fill: C.paper },
  Taxon: { r: 5.5, fill: C.hi },
  Disease: { r: 5, fill: C.lichen, ring: true },
  Target: { r: 5, fill: C.verdigris },
  Compound: { r: 4, fill: C.lichen },
  ConditionCategory: { r: 8, fill: C.hi, ring: true },
  Text: { r: 9, fill: C.paper, ring: true },
};
type GNode = { x: number; y: number; kind: string; ph: number; d: number };
const COLS = 17;
const ROWS = 9;
const NODES: GNode[] = [];
for (let r = 0; r < ROWS; r++) {
  for (let c = 0; c < COLS; c++) {
    const i = r * COLS + c;
    const x = 90 + (c + 0.5 + (random(`x${i}`) - 0.5) * 0.8) * (1740 / COLS);
    const y = 70 + (r + 0.5 + (random(`y${i}`) - 0.5) * 0.8) * (780 / ROWS);
    let u = random(`k${i}`) * TOTAL_NODES;
    let kind: string = KINDS[0];
    for (const k of KINDS) {
      u -= kg.node_kinds[k];
      if (u <= 0) { kind = k; break; }
    }
    NODES.push({ x, y, kind, ph: random(`p${i}`) * 6.28, d: Math.hypot(x - 960, y - 450) });
  }
}
// ponytail: O(n²) nearest-neighbour edges over ~150 nodes, computed once at module load
const EDGES: [number, number][] = [];
NODES.forEach((n, i) => {
  NODES.map((m, j) => ({ j, d: Math.hypot(n.x - m.x, n.y - m.y) }))
    .filter((o) => o.j !== i)
    .sort((a, b) => a.d - b.d)
    .slice(0, 2)
    .forEach((o) => { if (!EDGES.some(([a, b]) => (a === o.j && b === i))) EDGES.push([i, o.j]); });
});
const pos = (n: GNode, f: number) => ({ x: n.x + Math.sin(f / 80 + n.ph) * 5, y: n.y + Math.cos(f / 95 + n.ph) * 4 });

const Graph: React.FC = () => {
  const f = useCurrentFrame();
  const dim = ease(f, B - 6, B + 20, 1, 0.2) as number;
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: dim, filter: `blur(${(1 - dim) * 1.5}px)` }}>
      {EDGES.map(([a, b], k) => {
        const s = -60 + (NODES[a].d / 1000) * 120 + 10;
        const p = ease(f, s, s + 22, 0, 1) as number;
        if (p <= 0) return null;
        const P = pos(NODES[a], f);
        const Q = pos(NODES[b], f);
        // occasional travelling light pulse along an edge
        const cyc = (f + k * 37) % 150;
        const pulse = k % 5 === 0 && f > A + 60 && cyc < 40 ? cyc / 40 : -1;
        return (
          <g key={k}>
            <line x1={P.x} y1={P.y} x2={P.x + (Q.x - P.x) * p} y2={P.y + (Q.y - P.y) * p} stroke={C.lichen} strokeOpacity={0.22} strokeWidth={1.2} />
            {pulse >= 0 && <circle cx={P.x + (Q.x - P.x) * pulse} cy={P.y + (Q.y - P.y) * pulse} r={2.6} fill={C.hi} opacity={Math.sin(pulse * Math.PI)} />}
          </g>
        );
      })}
      {NODES.map((n, i) => {
        const s = -60 + (n.d / 1000) * 120;
        const o = ease(f, s, s + 14, 0, 1) as number;
        const st = STYLE[n.kind];
        const P = pos(n, f);
        return st.ring ? (
          <circle key={i} cx={P.x} cy={P.y} r={st.r * o} fill={C.ink} stroke={st.fill} strokeWidth={2} opacity={o} />
        ) : (
          <circle key={i} cx={P.x} cy={P.y} r={st.r * o} fill={st.fill} opacity={0.9 * o} />
        );
      })}
    </svg>
  );
};

// ---- the real path ----
const XS = [270, 556, 842, 1128, 1414, 1680];
const YS = [500, 470, 500, 470, 500, 470];
const HOP = [at(B, 1.7), at(B, 2.8), at(B, 4.2), at(B, 5.3), at(B, 6.6), at(B, 7.8)]; // "Greek words … disease"
const SRC = at(B, 8.5); // "every step carries its source"
const BACK = at(B, 10.4); // "so every lead traces back"
const EXACT = at(B, 12.0); // "the exact words"

const [g0, n1, n2, n3, n4, n5] = hp.hops;
const EDGE_LABELS = [
  { kind: n1.edge_in, val: "", src: "TEI · First1KGreek" },
  { kind: n2.edge_in, val: `p ${n2.p!.toFixed(2)} [${n2.lo!.toFixed(2)}–${n2.hi!.toFixed(2)}]`, src: "GBIF · model" },
  { kind: n3.edge_in, val: `ref. ${n3.reference_year}`, src: "LOTUS · Wikidata" },
  { kind: n4.edge_in, val: `pChEMBL ${n4.pchembl}`, src: "ChEMBL" },
  { kind: n5.edge_in, val: `OT ${n5.ot_score!.toFixed(2)}`, src: "Open Targets" },
];

const PathNode: React.FC<{ i: number; children: React.ReactNode }> = ({ i, children }) => {
  const f = useCurrentFrame();
  const lit = ease(f, HOP[i], HOP[i] + 10, 0, 1) as number;
  const ring = (f - HOP[i]) / 24;
  const back = BACK + (5 - i) * 7; // reverse pulse arrival
  const flash = f >= back && f < back + 14 ? 1 - (f - back) / 14 : 0;
  const greek = i === 0 ? (ease(f, EXACT, EXACT + 14, 0, 1) as number) : 0;
  return (
    <>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
        {ring > 0 && ring < 1 && <circle cx={XS[i]} cy={YS[i]} r={16 + ring * 40} fill="none" stroke={C.hi} strokeOpacity={1 - ring} strokeWidth={2} />}
        <circle cx={XS[i]} cy={YS[i]} r={15 + 6 * flash + 4 * greek} fill={lit > 0.5 ? C.verdigris : C.ink} stroke={C.hi} strokeWidth={3} opacity={0.3 + 0.7 * lit}
          style={{ filter: `drop-shadow(0 0 ${12 * lit + 18 * flash + 22 * greek}px rgba(61,187,130,.8))` }} />
      </svg>
      <div style={{ position: "absolute", left: XS[i] - 145, width: 290, top: YS[i] + 34, textAlign: "center", opacity: lit, translate: `0px ${(1 - lit) * 16}px` }}>{children}</div>
    </>
  );
};

const PathEdges: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {XS.slice(0, 5).map((x, i) => {
          const p = ease(f, HOP[i + 1] - 16, HOP[i + 1], 0, 1) as number;
          const x2 = XS[i + 1];
          const y1 = YS[i];
          const y2 = YS[i + 1];
          const pf = (f - (HOP[i + 1] - 16)) / 16; // forward pulse
          const bf = (f - (BACK + (4 - i) * 7)) / 7; // backward pulse, disease → Greek
          const dot = (t: number) => <circle cx={x + (x2 - x) * t} cy={y1 + (y2 - y1) * t} r={6} fill={C.hi} style={{ filter: "drop-shadow(0 0 10px rgba(61,187,130,.9))" }} />;
          return (
            <g key={i}>
              <line x1={x} y1={y1} x2={x2} y2={y2} stroke={C.rule} strokeWidth={2} strokeDasharray="3 7" opacity={ease(f, B, B + 16, 0, 1) as number} />
              <line x1={x} y1={y1} x2={x + (x2 - x) * p} y2={y1 + (y2 - y1) * p} stroke={C.hi} strokeWidth={3} />
              {pf > 0 && pf < 1 && dot(pf)}
              {bf > 0 && bf < 1 && dot(1 - bf)}
            </g>
          );
        })}
      </svg>
      {EDGE_LABELS.map((e, i) => {
        const o = ease(f, HOP[i + 1] - 6, HOP[i + 1] + 8, 0, 1) as number;
        const s = ease(f, SRC + i * 5, SRC + i * 5 + 10, 0, 1) as number;
        const mx = (XS[i] + XS[i + 1]) / 2;
        const my = (YS[i] + YS[i + 1]) / 2;
        return (
          <div key={i} style={{ position: "absolute", left: mx - 140, width: 280, top: my - 118, textAlign: "center", opacity: o, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
            <div style={{ opacity: s, scale: `${0.8 + 0.2 * s}`, height: 34 }}><Chip color={C.lichen} style={{ fontSize: 16, borderColor: C.verdigris, background: "rgba(23,116,79,.16)" }}>{e.src}</Chip></div>
            <div style={{ fontFamily: MONO, fontSize: 17, color: C.lichen, letterSpacing: "0.04em" }}>{e.kind}</div>
            <div style={{ fontFamily: MONO, fontSize: 16, color: C.dim, height: 20 }}>{e.val}</div>
          </div>
        );
      })}
    </>
  );
};

const sub: React.CSSProperties = { fontFamily: MONO, fontSize: 16, color: C.dim, marginTop: 6 };
const title: React.CSSProperties = { fontFamily: OUTFIT, fontWeight: 600, fontSize: 32, letterSpacing: "-0.02em", color: C.paper, lineHeight: 1.1 };

export const Hood: React.FC = () => {
  const f = useCurrentFrame();
  const statsOut = ease(f, B - 22, B - 8, 1, 0, EASE_IN) as number;
  const reqDim = ease(f, HOP[0] - 6, HOP[0] + 14, 1, 0.55) as number;
  const verified = ease(f, EXACT, EXACT + 12, 0, 1) as number;
  const REQ = A + 118;
  const RES = REQ + 52;
  return (
    <Stage glow="bl">
      <Graph />
      <div style={{ position: "absolute", left: SAFE, top: 52 }}>
        <Kicker>Under the hood</Kicker>
      </div>

      {/* s09_a: real counts */}
      <div style={{ position: "absolute", left: SAFE - 160, top: 190, padding: "110px 160px 120px", background: "radial-gradient(closest-side, rgba(0,0,0,.92) 45%, rgba(0,0,0,0) 100%)", opacity: statsOut }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 20 }}>
          <CountUp to={kg.nodes} at={at(A, 1.5)} dur={28} size={120} />
          <span style={{ fontFamily: OUTFIT, fontSize: 40, color: C.paper, opacity: ease(f, at(A, 1.9), at(A, 2.3), 0, 1) as number }}>nodes</span>
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 20 }}>
          <CountUp to={kg.edges} at={at(A, 3.6)} dur={28} size={120} />
          <span style={{ fontFamily: OUTFIT, fontSize: 40, color: C.paper, opacity: ease(f, at(A, 4.0), at(A, 4.4), 0, 1) as number }}>links</span>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, width: 760, marginTop: 22 }}>
          {Object.keys(kg.edge_kinds).map((k, i) => {
            const o = ease(f, at(A, 4.2) + i * 3, at(A, 4.2) + i * 3 + 10, 0, 1) as number;
            return (
              <Chip key={k} color={C.lichen} style={{ fontSize: 16, opacity: o, background: "rgba(0,0,0,.6)" }}>
                {k} <span style={{ color: C.dim }}>{kg.edge_kinds[k as keyof typeof kg.edge_kinds].toLocaleString("en-US")}</span>
              </Chip>
            );
          })}
        </div>
      </div>

      {/* the real MCP call Claude sends, and an excerpt of the live response */}
      {f >= REQ - 10 && (
        <div style={{ position: "absolute", left: SAFE, top: 96, width: 1680, display: "flex", gap: 24, alignItems: "flex-start", opacity: ease(f, REQ - 10, REQ, 0, 1) as number }}>
          <Code text={hp.mcp_request} a={REQ} cps={1.9} size={21} label="POST /mcp · JSON-RPC 2.0 · tools/call" style={{ opacity: reqDim, width: 1000, boxSizing: "border-box", minHeight: 186 }} />
          <div style={{ flex: 1, background: C.card, border: `1px solid ${C.rule}`, borderRadius: 14, padding: "16px 22px", fontFamily: MONO, fontSize: 16, lineHeight: 1.55, color: C.paper, minHeight: 186, boxSizing: "border-box" }}>
            <div style={{ fontSize: 15, color: C.dim, marginBottom: 4 }}>response · pharmakon.adoranto737.workers.dev</div>
            {hp.mcp_response_excerpt.slice(0, 5).map((l, i) => (
              <div key={i} style={{ opacity: ease(f, RES + i * 5, RES + i * 5 + 8, 0, 1) as number, color: i === 0 ? C.dim : C.lichen, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{l}</div>
            ))}
          </div>
        </div>
      )}

      {/* s09_b: the path */}
      <PathEdges />
      <PathNode i={0}>
        <div lang="grc" style={{ fontFamily: DIDOT, fontSize: 31, lineHeight: 1.25, color: C.paper }}>{g0.span_grc}</div>
        <div style={sub}>CTS {g0.id} · {g0.condition_en}</div>
        <div style={{ height: 34, marginTop: 8, display: "flex", justifyContent: "center", opacity: verified, scale: `${0.85 + 0.15 * verified}` }}>
          <Chip color={C.hi} style={{ fontSize: 16, borderColor: C.hi, background: "rgba(23,116,79,.25)" }}><Tick size={18} draw={verified} /> exact quote in source</Chip>
        </div>
      </PathNode>
      <PathNode i={1}>
        <div lang="grc" style={{ fontFamily: DIDOT, fontSize: 46, lineHeight: 1.1, color: C.paper }}>{n1.label}</div>
        <div style={sub}>ancient name · {n1.id.replace("cl:", "")}</div>
      </PathNode>
      <PathNode i={2}>
        <div style={{ ...title, fontStyle: "italic", fontWeight: 500 }}>{n2.label}</div>
        <div style={sub}>species · GBIF {n2.id.replace("gbif:", "")}</div>
      </PathNode>
      <PathNode i={3}>
        <div style={title}>{n3.label}</div>
        <div style={sub}>compound · {n3.chembl}</div>
      </PathNode>
      <PathNode i={4}>
        <div style={title}>{n4.label}</div>
        <div style={{ ...sub, fontFamily: OUTFIT, fontSize: 19 }}>{n4.pref_name}</div>
        <div style={sub}>human target · {n4.id}</div>
      </PathNode>
      <PathNode i={5}>
        <div style={title}>{n5.label}</div>
        <div style={sub}>disease · MeSH {n5.id.replace("mesh:", "")}</div>
        <div style={sub}>lead: {hp.lead.condition}</div>
      </PathNode>

      {/* the technical win */}
      <div style={{ position: "absolute", left: SAFE, right: SAFE, top: 736, display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
        <Words text="Every lead traces back to the exact Greek words." at={BACK + 6} stagger={3} size={52} accent={["exact", "greek"]} style={{ justifyContent: "center" }} />
        <div style={{ fontFamily: MONO, fontSize: 22, color: C.dim, opacity: ease(f, EXACT + 10, EXACT + 24, 0, 1) as number }}>
          {kg.nodes.toLocaleString("en-US")} nodes · {kg.edges.toLocaleString("en-US")} edges · {Math.round(claims.exact_span_verified_rate_kept * 100)}% spans verified
        </div>
      </div>
    </Stage>
  );
};
