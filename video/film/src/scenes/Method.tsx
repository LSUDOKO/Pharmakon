// Scene "method" — four beats on one rail: READ (verbatim span check) · IDENTIFY (asphodel, 4 evidence layers → P with 90% whiskers)
// · TRACE (four eras vs a shuffled null) · TEST (time machine, frozen, no AI). All numbers from public/data.
import React from "react";
import { random, useCurrentFrame } from "remotion";
import { C, CountUp, DIDOT, EASE_IN, MONO, OUTFIT, SAFE, Stage, Words, ease } from "../brand";
import { line } from "../timing";
import { Arrow, Chip, Cross, InkGreek, Kicker, Padlock, Reveal, Tick, at } from "./datamethod/ui";
import wormwood from "../../public/data/dmm-3-23.json";
import asph from "../../public/data/dmm-2-169.json";
import claims from "../../public/data/extract-claims.json";
import persistence from "../../public/data/persistence.json";
import forecast from "../../public/data/forecast.json";

const L1 = line("method", "s07_a").from;
const L2 = line("method", "s07_b").from;
const L3 = line("method", "s07_c").from;
const L4 = line("method", "s07_d").from;
const END = 2167;

/** Mount a chapter between a and b with a rise-in and a quick ease-in exit. */
const Chap: React.FC<{ a: number; b: number; children: React.ReactNode }> = ({ a, b, children }) => {
  const f = useCurrentFrame();
  if (f < a - 2 || f > b + 10) return null;
  const x = ease(f, b, b + 9, 1, 0, EASE_IN) as number;
  const i = a <= 0 ? 1 : (ease(f, a, a + 12, 0, 1) as number);
  return <div style={{ position: "absolute", inset: 0, opacity: x * i, translate: `0px ${(1 - x) * -18 + (1 - i) * 18}px` }}>{children}</div>;
};

const STEPS = ["Read", "Identify", "Trace", "Test"];
const STARTS = [L1 - 30, L2 - 10, L3 - 10, L4 - 10];
const Rail: React.FC = () => {
  const f = useCurrentFrame();
  const idx = STARTS.filter((s) => f >= s).length - 1;
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 84 }}>
        <Kicker>{`0${idx + 1} · ${STEPS[idx]}`}</Kicker>
      </div>
      <div style={{ position: "absolute", right: SAFE, top: 76, display: "flex", gap: 14 }}>
        {STEPS.map((s, i) => {
          const on = ease(f, STARTS[i], STARTS[i] + 14, 0, 1) as number;
          const active = i === idx;
          return (
            <div key={s} style={{ width: 150 }}>
              <div style={{ fontFamily: MONO, fontSize: 18, letterSpacing: "0.1em", textTransform: "uppercase", color: active ? C.hi : on > 0.5 ? C.lichen : C.dim, opacity: active ? 1 : 0.7 }}>{s}</div>
              <div style={{ height: 3, marginTop: 8, background: C.rule, borderRadius: 2, overflow: "hidden" }}>
                <div style={{ height: 3, width: `${on * 100}%`, background: active ? C.hi : C.verdigris }} />
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
};

// ---------------- 01 READ ----------------
const P0 = wormwood.passages[0];
const SPAN = P0.spans[0];
const CLAIM = wormwood.claims[0]; // στομάχῳ → stomach complaints
const Read: React.FC = () => {
  const f = useCurrentFrame();
  const lex = at(L1, 1.9);
  const llm = at(L1, 3.0);
  const mark = at(L1, 3.9);
  const quote = at(L1, 5.7);
  const notIn = at(L1, 9.3);
  const exact = at(L1, 11.4);
  const out = at(L1, 12.9);
  const count = at(L1, 13.7);
  const passed = at(L1, 15.8);
  const tickOk = ease(f, exact, exact + 12, 0, 1) as number;
  const struck = ease(f, out, out + 10, 0, 1) as number;
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 168, width: 1560 }}>
        <InkGreek text={SPAN} a={L1 + 26} dur={70} size={54} mark={CLAIM.condition_text_grc} markAt={mark} />
        <Reveal a={L1 + 60}><div style={{ fontFamily: MONO, fontSize: 20, color: C.dim, marginTop: 10 }}>Dioscorides 3.23 · {P0.cts}</div></Reveal>
      </div>
      <div style={{ position: "absolute", left: SAFE, top: 412, display: "flex", alignItems: "center", gap: 18 }}>
        {[["rule lexicon", lex], ["language model", llm]].map(([t, a]) => (
          <Reveal key={t as string} a={a as number} dy={14}>
            <Chip color={C.paper} style={{ fontSize: 22, padding: "8px 18px", borderColor: f >= mark ? C.verdigris : C.rule }}>
              {f >= mark && <Tick size={20} draw={ease(f, mark, mark + 10, 0, 1) as number} />}
              {t as string}
            </Chip>
          </Reveal>
        ))}
        <Reveal a={mark + 6} dy={0} style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <Arrow w={60} draw={ease(f, mark + 6, mark + 16, 0, 1) as number} />
          <span style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 40, color: C.hi, letterSpacing: "-0.02em" }}>{CLAIM.condition_en}</span>
          <span style={{ fontFamily: MONO, fontSize: 18, color: C.dim }}>use group {CLAIM.use_group}</span>
        </Reveal>
      </div>

      {/* the check */}
      <Reveal a={quote} style={{ position: "absolute", left: SAFE, top: 524, width: 1000 }}>
        <div style={{ background: C.card, border: `1px solid ${C.rule}`, borderRadius: 24, padding: "28px 34px" }}>
          <div style={{ fontFamily: OUTFIT, fontSize: 26, color: C.dim, marginBottom: 14 }}>Every claim must quote its Greek words.</div>
          <div style={{ display: "flex", alignItems: "center", gap: 16, fontFamily: MONO, fontSize: 26, color: C.lichen }}>
            <span style={{ opacity: ease(f, notIn - 10, notIn, 0.4, 1) as number }}>passage.includes(claim.quote)</span>
            <span style={{ color: tickOk > 0.5 ? C.hi : C.dim, display: "flex", alignItems: "center", gap: 8, opacity: tickOk }}>
              <Tick size={30} draw={tickOk} /> true
            </span>
          </div>
          <div style={{ fontFamily: MONO, fontSize: 18, color: C.dim, marginTop: 8, opacity: ease(f, exact, exact + 12, 0, 1) as number }}>Unicode NFC · whitespace-normalised · character for character</div>
          <div style={{ height: 1, background: C.rule, margin: "20px 0" }} />
          <div style={{ display: "flex", alignItems: "center", gap: 14, opacity: (ease(f, notIn, notIn + 12, 0, 1) as number) * (1 - 0.55 * struck) }}>
            <Cross size={26} />
            <span style={{ fontFamily: OUTFIT, fontSize: 26, color: C.dim, position: "relative" }}>
              quote not in source
              <span style={{ position: "absolute", left: 0, top: "52%", height: 2, width: `${struck * 100}%`, background: C.dim }} />
            </span>
            <Arrow w={44} color={C.dim} />
            <span style={{ fontFamily: MONO, fontSize: 20, color: C.dim }}>archived · span_mismatch</span>
          </div>
        </div>
      </Reveal>

      <div style={{ position: "absolute", left: 1210, top: 530, width: 600 }}>
        <Reveal a={count}>
          <CountUp to={claims.llm_merge.llm_claims} at={count} dur={26} size={124} />
          <div style={{ fontFamily: OUTFIT, fontSize: 28, color: C.paper, marginTop: -6 }}>claims from the language model</div>
        </Reveal>
        <Reveal a={passed} style={{ marginTop: 26, display: "flex", alignItems: "center", gap: 16 }}>
          <Tick size={44} draw={ease(f, passed, passed + 12, 0, 1) as number} />
          <span style={{ fontFamily: MONO, fontWeight: 600, fontSize: 54, color: C.hi }}>{Math.round(claims.llm_merge.llm_span_verified_rate * 100)}%</span>
          <span style={{ fontFamily: OUTFIT, fontSize: 28, color: C.paper }}>exact quotes</span>
        </Reveal>
        <Reveal a={passed + 10}><div style={{ fontFamily: MONO, fontSize: 18, color: C.dim, marginTop: 10 }}>{claims.llm_merge.llm_claims_archived_span_mismatch} archived as span_mismatch</div></Reveal>
      </div>
    </>
  );
};

// ---------------- 02 IDENTIFY ----------------
const LAYERS = [
  { q: "Grows in Greece?", tag: "f2 · GBIF records", t: at(L2, 5.2) },
  { q: "Modern name echoes it?", tag: "f3 · Greek & Latin names", t: at(L2, 6.8) },
  { q: "Scholars agree?", tag: "f4 · LSJ + literature", t: at(L2, 9.7) },
  { q: "Description matches?", tag: "f1 · leaves, flowers, roots", t: at(L2, 11.2) },
];
const MORPH_T = [at(L2, 13.6), at(L2, 14.5), at(L2, 15.4)];
const BARS = at(L2, 17.2);
const UNID = at(L2, 19.1);
const PMAX = 0.6;
const BAR_W = 700;
type Morph = { trait: string; a: string; b: string; ok: boolean };
const parseMorph = (s: string): Morph => {
  const [trait, rest] = s.split(": ");
  const [a, b] = rest.split(" ↔ ");
  return { trait: trait.replace(/_/g, " "), a: a.replace(/_/g, " "), b: b.replace(/ [✓✗]$/u, "").replace(/_/g, " ").replace(/\//g, " / "), ok: s.trim().endsWith("✓") };
};

const Identify: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 150 }}>
        <Reveal a={at(L2, 2.1)}>
          <div lang="grc" style={{ fontFamily: DIDOT, fontSize: 104, lineHeight: 1.1, color: C.paper }}>{asph.lemma}</div>
          <div style={{ fontFamily: MONO, fontSize: 20, color: C.dim, marginTop: 4 }}>asphodel · Dioscorides {asph.chapter.replace("dmm:", "")}</div>
        </Reveal>
      </div>
      {LAYERS.map((l, i) => {
        const o = ease(f, l.t, l.t + 16, 0, 1) as number;
        const hot = ease(f, l.t, l.t + 6, 0, 1) as number * (ease(f, l.t + 30, l.t + 50, 1, 0) as number);
        return (
          <div key={i} style={{
            position: "absolute", left: SAFE + i * 10, top: 372 + i * 106, width: 640, height: 92, boxSizing: "border-box",
            background: C.card, borderRadius: 22, border: `1px solid ${hot > 0.3 ? C.hi : C.rule}`,
            boxShadow: `0 16px 40px rgba(0,0,0,.6), 0 0 ${30 * hot}px rgba(61,187,130,.35)`,
            padding: "0 28px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 4,
            opacity: o, translate: `${(1 - o) * -80}px ${(1 - o) * 20}px`, scale: `${0.94 + 0.06 * o}`,
          }}>
            <span style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: 32, color: C.paper, letterSpacing: "-0.015em" }}>{l.q}</span>
            <span style={{ fontFamily: MONO, fontSize: 16, color: C.lichen }}>{l.tag}</span>
          </div>
        );
      })}

      {/* P(species | name) */}
      <div style={{ position: "absolute", left: 880, top: 170, width: 920 }}>
        <Reveal a={at(L2, 3.8)}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <span style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 34 }}>P(species |</span>
            <span lang="grc" style={{ fontFamily: DIDOT, fontSize: 38 }}>{asph.lemma}</span>
            <span style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 34, marginLeft: -6 }}>)</span>
          </div>
          <div style={{ fontFamily: MONO, fontSize: 17, color: C.dim, marginTop: 4, opacity: ease(f, BARS + 30, BARS + 44, 0, 1) as number }}>whiskers: 90% bootstrap interval</div>
        </Reveal>
        {asph.candidates.map((c, i) => {
          const y = 96 + i * 142;
          const rowIn = ease(f, at(L2, 3.8) + 6 + i * 4, at(L2, 3.8) + 20 + i * 4, 0, 1) as number;
          const s = BARS + i * 6;
          const grow = ease(f, s, s + 20, 0, 1) as number;
          const wh = ease(f, s + 18, s + 30, 0, 1) as number;
          const unid = c.name === null;
          const focus = unid ? (ease(f, UNID, UNID + 12, 0, 1) as number) : 0;
          const px = (v: number) => (v / PMAX) * BAR_W;
          const morph = (c.morph as string[]).map(parseMorph);
          return (
            <div key={i} style={{ position: "absolute", left: 0, top: y, width: 920, opacity: rowIn }}>
              <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", width: BAR_W + 180 }}>
                <span style={{ fontFamily: OUTFIT, fontSize: 34, fontStyle: unid ? "normal" : "italic", color: unid ? (focus > 0.5 ? C.hi : C.lichen) : C.paper }}>
                  {unid ? "unidentified" : c.name}
                </span>
                <span style={{ fontFamily: MONO, fontWeight: 600, fontSize: 32, color: unid ? C.lichen : C.hi, opacity: grow }}>{Math.round(c.p * 100 * grow)}%</span>
              </div>
              <svg width={BAR_W + 10} height={30} style={{ display: "block", marginTop: 8, overflow: "visible" }}>
                <rect x={0} y={9} width={BAR_W} height={12} rx={6} fill={C.rule} opacity={0.6} />
                <rect x={0} y={9} width={px(c.p) * grow} height={12} rx={6} fill={unid ? "none" : C.hi} stroke={unid ? C.lichen : "none"} strokeDasharray={unid ? "5 4" : undefined} strokeWidth={1.5}
                  style={{ filter: unid ? undefined : "drop-shadow(0 0 8px rgba(61,187,130,.45))" }} />
                {wh > 0 && (
                  <g stroke={C.paper} strokeWidth={2} opacity={wh}>
                    <line x1={px(c.lo)} y1={15} x2={px(c.lo) + (px(c.hi) - px(c.lo)) * wh} y2={15} />
                    <line x1={px(c.lo)} y1={5} x2={px(c.lo)} y2={25} />
                    {wh > 0.95 && <line x1={px(c.hi)} y1={5} x2={px(c.hi)} y2={25} />}
                  </g>
                )}
              </svg>
              <div style={{ display: "flex", gap: 8, marginTop: 10, height: 30 }}>
                {morph.map((m, j) => {
                  const t = MORPH_T[Math.min(j, 2)] + i * 3;
                  const o = ease(f, t, t + 10, 0, 1) as number;
                  return (
                    <Chip key={j} color={m.ok ? C.lichen : C.dim} style={{ fontSize: 14, padding: "4px 9px", gap: 5, whiteSpace: "nowrap", opacity: o, scale: `${0.9 + 0.1 * o}`, borderColor: m.ok ? C.verdigris : C.rule }}>
                      {m.trait}: {m.a} <Arrow w={22} both color={C.dim} /> {m.b} {m.ok ? <Tick size={16} /> : <Cross size={14} />}
                    </Chip>
                  );
                })}
              </div>
            </div>
          );
        })}
        <svg width={BAR_W + 40} height={40} style={{ position: "absolute", left: 0, top: 96 + 3 * 142 + 92, overflow: "visible", opacity: ease(f, BARS, BARS + 16, 0, 1) as number }}>
          {[0, 0.2, 0.4, 0.6].map((v) => (
            <g key={v}>
              <line x1={(v / PMAX) * BAR_W} y1={0} x2={(v / PMAX) * BAR_W} y2={8} stroke={C.dim} strokeWidth={1.5} />
              <text x={(v / PMAX) * BAR_W} y={28} fill={C.dim} fontFamily={MONO} fontSize={16} textAnchor="middle">{`${v * 100}%`}</text>
            </g>
          ))}
        </svg>
      </div>
    </>
  );
};

// ---------------- 03 TRACE ----------------
const ERAS = [
  { who: "Dioscorides", era: "1st c. AD", t: L3 + 4, note: "" },
  { who: "Galen", era: "2nd c.", t: at(L3, 1.9), note: `${Math.round(persistence.galen_agreement_rate * 100)}% re-attested` },
  { who: "John the Physician", era: "13th c.", t: at(L3, 2.8), note: `${Math.round(persistence.jc_agreement_rate * 100)}% re-attested` },
  { who: "Greek villages", era: "today", t: at(L3, 3.7), note: `${persistence.modern_records.toLocaleString("en-US")} records` },
];
const EX = [330, 750, 1170, 1590];
// 16 illustrative strands whose dots/endpoints are derived from the rates printed on screen
const PT = persistence.permutation_test;
const N = 16;
const nG = Math.round(N * persistence.galen_agreement_rate); // dots at Galen
const nJ = Math.round(N * persistence.jc_agreement_rate); // dots at John
const nT = Math.round(N * PT.observed_persisted_share); // strands reaching today
const nGhost = Math.round(N * PT.null_mean); // shuffled strands reaching today
const G_ORDER = [0, 2, 4, 6, nT, nT + 1, 1, 3, 5, 7];
const J_ORDER = [1, 3, 5, 7, 0, 2, 4, 6];
const GSET = G_ORDER.slice(0, nG);
const JSET = J_ORDER.slice(0, nJ);
const STRANDS = Array.from({ length: N }, (_, i) => ({
  reach: i < nT ? 3 : GSET.includes(i) ? 1 : 0,
  dots: [GSET.includes(i), JSET.includes(i), i < nT],
}));
// seeded row permutation so the ghost does not line up with the real strands
const GHOST = Array.from({ length: N }, (_, i) => (i < nGhost ? 3 : i < nGhost + 2 ? 1 : 0))
  .map((r, i) => ({ r, key: random(`g${i}`) })).sort((a, b) => a.key - b.key).map((g) => g.r);
const SHUF = at(L3, 5.0);
const SHUF2 = at(L3, 6.3);
const TRAD = at(L3, 7.4);

const Trace: React.FC = () => {
  const f = useCurrentFrame();
  const ghost = ease(f, SHUF, SHUF + 20, 0, 1) as number;
  const real = ease(f, TRAD, TRAD + 14, 0, 1) as number;
  const endX = (reach: number) => (reach === 0 ? EX[0] + 150 : EX[reach]);
  const strandPath = (y: number, x2: number) => `M${EX[0]} 330 C ${EX[0] + 90} 330 ${EX[0] + 60} ${y} ${EX[0] + 150} ${y} L ${x2} ${y}`;
  return (
    <>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={EX[0]} y1={330} x2={EX[3]} y2={330} stroke={C.rule} strokeWidth={2} strokeDasharray="4 8" />
        {/* shuffled ghost */}
        {GHOST.map((r, i) => {
          const y = 420 + i * 19 + 7;
          return <path key={`g${i}`} d={strandPath(y, endX(r))} fill="none" stroke={C.dim} strokeWidth={1.5} strokeDasharray="4 6" opacity={0.6 * ghost * (1 - 0.45 * real)} />;
        })}
        {/* real strands */}
        {STRANDS.map((s, i) => {
          const y = 420 + i * 19;
          const x2 = endX(s.reach);
          const lastT = ERAS[Math.max(1, s.reach)].t;
          const p = ease(f, L3 + 10 + i * 2, lastT + 12, 0, 1) as number;
          const col = s.reach === 3 ? C.hi : s.reach === 0 ? C.rule : C.lichen;
          return (
            <g key={i}>
              <path d={strandPath(y, x2)} fill="none" stroke={col} strokeWidth={s.reach === 0 ? 1.5 : 2.5} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p}
                opacity={s.reach === 0 ? 0.7 : 0.75 + 0.25 * real} style={{ filter: real > 0 && s.reach === 3 ? `drop-shadow(0 0 ${6 * real}px rgba(61,187,130,.7))` : undefined }} />
              {[1, 2, 3].filter((k) => s.dots[k - 1] && f >= ERAS[k].t).map((k) => <circle key={k} cx={EX[k]} cy={y} r={4} fill={col} />)}
            </g>
          );
        })}
        {ERAS.map((e, i) => {
          const lit = ease(f, e.t, e.t + 10, 0, 1) as number;
          return <circle key={i} cx={EX[i]} cy={330} r={12} fill={lit > 0.5 ? C.hi : C.ink} stroke={lit > 0 ? C.hi : C.rule} strokeWidth={3} />;
        })}
      </svg>
      {ERAS.map((e, i) => {
        const o = ease(f, e.t, e.t + 14, 0, 1) as number;
        return (
          <div key={i} style={{ position: "absolute", left: EX[i] - 200, width: 400, top: 170, textAlign: "center", opacity: o, translate: `0px ${(1 - o) * 16}px` }}>
            <div style={{ fontFamily: MONO, fontSize: 20, color: C.lichen }}>{e.era}</div>
            <div style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 36, letterSpacing: "-0.02em", marginTop: 4 }}>{e.who}</div>
            <div style={{ fontFamily: MONO, fontSize: 18, color: C.dim, marginTop: 4, height: 24 }}>{e.note}</div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 1640, top: 430, display: "flex", flexDirection: "column", gap: 12 }}>
        <Reveal a={L3 + 40}><Chip color={C.hi} style={{ borderColor: C.verdigris }}>real order</Chip></Reveal>
        <Reveal a={SHUF2}><Chip color={C.dim} style={{ borderStyle: "dashed" }}>shuffled × {persistence.permutation_test.n_permutations.toLocaleString("en-US")}</Chip></Reveal>
      </div>
      <div style={{ position: "absolute", left: SAFE, top: 760 }}>
        <Words text="Coincidence can't pass for tradition." at={TRAD} size={64} accent={["tradition"]} />
      </div>
    </>
  );
};

// ---------------- 04 TEST (time machine) ----------------
const CUTS = forecast.cutoffs;
const YEAR_T = [at(L4, 2.4), at(L4, 3.5), at(L4, 4.2), at(L4, 5.0)];
const KNOWN = at(L4, 5.8);
const RANK = at(L4, 7.5);
const CHECK = at(L4, 10.1);
const NOAI = at(L4, 12.0);
const Y0 = 1990;
const Y1 = forecast.t_end;
const AX0 = SAFE;
const AX1 = 1800;
const yx = (y: number) => AX0 + ((y - Y0) / (Y1 - Y0)) * (AX1 - AX0);
const res = (c: number) => forecast.results[String(c) as keyof typeof forecast.results].test.random;

const Test: React.FC = () => {
  const f = useCurrentFrame();
  const k = Math.max(0, YEAR_T.filter((t) => f >= t).length - 1);
  // eased cutoff position between steps
  let cx = yx(CUTS[0]);
  YEAR_T.forEach((t, i) => { if (i > 0) cx += (ease(f, t, t + 12, 0, 1) as number) * (yx(CUTS[i]) - yx(CUTS[i - 1])); });
  const roll = ease(f, YEAR_T[k], YEAR_T[k] + 10, 1, 0) as number;
  const axisIn = ease(f, YEAR_T[0] - 20, YEAR_T[0], 0, 1) as number;
  const known = ease(f, KNOWN, KNOWN + 14, 0, 1) as number;
  return (
    <>
      <Reveal a={at(L4, 0.7)} style={{ position: "absolute", left: SAFE, top: 150 }}>
        <div style={{ fontFamily: MONO, fontSize: 20, color: C.dim }}>stand in the year</div>
        <div style={{ height: 176, overflow: "hidden" }}>
          <div style={{ fontFamily: MONO, fontWeight: 600, fontSize: 172, color: C.hi, letterSpacing: "-0.04em", lineHeight: 1, translate: `0px ${roll * 60}px`, opacity: 1 - roll * 0.8, filter: `blur(${roll * 6}px)` }}>
            {f >= YEAR_T[0] ? CUTS[k] : "····"}
          </div>
        </div>
      </Reveal>

      {/* per-cutoff table: untested pairs ranked, studied by t_end */}
      <div style={{ position: "absolute", left: 820, top: 160, width: 980, fontFamily: MONO }}>
        <Reveal a={RANK - 8}>
          <div style={{ display: "grid", gridTemplateColumns: "180px 1fr 1fr", fontSize: 18, color: C.dim, paddingBottom: 10, borderBottom: `1px solid ${C.rule}` }}>
            <span>cutoff</span><span>untested pairs ranked</span><span style={{ opacity: ease(f, CHECK, CHECK + 10, 0, 1) as number }}>studied by {Y1}</span>
          </div>
        </Reveal>
        {CUTS.map((c, i) => {
          const r = res(c);
          const o = ease(f, RANK + i * 5, RANK + i * 5 + 12, 0, 1) as number;
          const o2 = ease(f, CHECK + i * 5, CHECK + i * 5 + 12, 0, 1) as number;
          const act = i === k && f >= YEAR_T[0];
          return (
            <div key={c} style={{ display: "grid", gridTemplateColumns: "180px 1fr 1fr", fontSize: 34, padding: "9px 0", borderBottom: `1px solid ${C.rule}`, opacity: o, color: act ? C.paper : C.dim }}>
              <span style={{ color: act ? C.hi : C.dim }}>{c}</span>
              <span>{r.n.toLocaleString("en-US")}</span>
              <span style={{ opacity: o2, color: C.lichen }}>{r.positives}</span>
            </div>
          );
        })}
      </div>

      {/* time axis: known (left of cutoff) vs hidden future (hatched) */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: axisIn }}>
        <defs>
          <pattern id="hatch" width={7} height={7} patternUnits="userSpaceOnUse" patternTransform="rotate(135)">
            <line x1={0} y1={0} x2={0} y2={7} stroke={C.hatch} strokeWidth={2} />
          </pattern>
        </defs>
        <rect x={AX0} y={500} width={cx - AX0} height={84} fill="rgba(23,116,79,.20)" />
        <rect x={cx} y={500} width={AX1 - cx} height={84} fill="url(#hatch)" />
        <rect x={cx} y={500} width={AX1 - cx} height={84} fill="rgba(0,0,0,.35)" />
        <line x1={AX0} y1={584} x2={AX1} y2={584} stroke={C.rule} strokeWidth={2} />
        {Array.from({ length: (Y1 - Y0) / 5 + 1 }, (_, i) => Y0 + i * 5).map((y) => (
          <g key={y}>
            <line x1={yx(y)} y1={584} x2={yx(y)} y2={594} stroke={C.dim} strokeWidth={1.5} />
            <text x={yx(y)} y={618} fill={C.dim} fontFamily={MONO} fontSize={17} textAnchor="middle">{y}</text>
          </g>
        ))}
        <line x1={cx} y1={480} x2={cx} y2={596} stroke={C.hi} strokeWidth={3} style={{ filter: "drop-shadow(0 0 8px rgba(61,187,130,.8))" }} />
      </svg>
      <div style={{ position: "absolute", left: cx - 330, width: 310, top: 520, textAlign: "right", fontFamily: OUTFIT, fontSize: 24, color: C.lichen, opacity: known }}>only what was known then</div>
      <div style={{ position: "absolute", left: cx + 22, top: 520, fontFamily: OUTFIT, fontSize: 24, color: C.dim, opacity: known }}>hidden: what science did next</div>

      {/* the lock */}
      <div style={{ position: "absolute", left: SAFE, top: 662, display: "flex", alignItems: "center", gap: 36 }}>
        <div style={{ opacity: ease(f, NOAI - 6, NOAI + 4, 0, 1) as number }}><Padlock a={NOAI + 4} size={92} /></div>
        <div>
          <Words text="No AI output in this test." at={NOAI} size={62} accent={["no", "ai"]} />
          <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
            {[0, 1, 4].map((j) => forecast.leakage_controls[j]).map((c, i) => (
              <Reveal key={c} a={NOAI + 18 + i * 5} dy={10}><Chip color={C.lichen}>{c}</Chip></Reveal>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export const Method: React.FC = () => (
  <Stage glow="tr">
    <Rail />
    <Chap a={0} b={L2 - 20}><Read /></Chap>
    <Chap a={L2 - 6} b={L3 - 20}><Identify /></Chap>
    <Chap a={L3 - 10} b={L4 - 20}><Trace /></Chap>
    <Chap a={L4 - 10} b={END + 20}><Test /></Chap>
  </Stage>
);
