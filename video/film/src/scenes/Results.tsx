// Scene "results" (s10_a–f): does it work? Identification, calibration, survival, the honest null, the leads.
// Every number comes from ./results/data.ts (public/data/*.json). Sub-beats land on the VO via at(scene, line, phrase).
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, CountUp, MONO, OUTFIT, SAFE, Stage, Words, ease } from "../brand";
import { scene } from "../timing";
import { BACKTEST, ECE, BRIER, ID_ROWS, LEADS, MODERN_RECORDS, N_NAMES, PERM, at, fmt, pct, signed } from "./results/data";
import { Beat, DISCLAIMER, Grid, HatchDef, Kicker, Note } from "./results/kit";

const S = "results";
const L = (id: string, phrase = "") => at(S, id, phrase);

// ---------- s10_a ----------
const Opening: React.FC = () => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 40, paddingBottom: 80 }}>
    <Words text="Does it work?" at={0} size={160} stagger={4} accent={["work"]} />
    <Note at={L("s10_a") + 26} style={{ fontSize: 26, letterSpacing: "0.08em" }}>
      {N_NAMES} names · {fmt(PERM.n_rows)} uses · {BACKTEST.length} cutoffs · {fmt(LEADS.unsupported_today)} leads
    </Note>
  </AbsoluteFill>
);

// ---------- s10_b: identification dot plot ----------
const IdPlot: React.FC = () => {
  const f = useCurrentFrame();
  const x0 = 640, x1 = 1240, y0 = 372, pitch = 104;
  const X = (v: number) => x0 + v * (x1 - x0);
  const tPh = L("s10_b", "Pharmakon agrees");
  const tLsj = L("s10_b", "The standard dictionary");
  const times = [tPh, tPh + 10, tLsj + 26, tLsj];
  const col = { hi: C.hi, ghost: C.lichen, dim: C.dim } as const;
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 140 }}>
        <Words text="Which plant is it?" at={L("s10_b") - 8} size={84} />
        <Note at={L("s10_b") + 10} style={{ marginTop: 14 }}>
          top-1 agreement with expert identifications · {N_NAMES} names · leave-one-name-out · 95% CI
        </Note>
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        {[0, 0.25, 0.5, 0.75, 1].map((v) => (
          <g key={v} opacity={ease(f, L("s10_b"), L("s10_b") + 20, 0, 1)}>
            <line x1={X(v)} x2={X(v)} y1={330} y2={y0 + pitch * 3 + 40} stroke={C.rule} strokeWidth={1.5} />
            <text x={X(v)} y={y0 + pitch * 3 + 78} fill={C.dim} fontFamily={MONO} fontSize={20} textAnchor="middle">{pct(v)}</text>
          </g>
        ))}
        {ID_ROWS.map((r, i) => {
          const t = times[i];
          const y = y0 + i * pitch;
          const c = col[r.tone];
          const dot = ease(f, t, t + 12, 0, 1) as number;
          const w = ease(f, t + 8, t + 26, 0, 1) as number;
          const m = X(r.top1.mean);
          return (
            <g key={r.label} opacity={ease(f, t - 4, t + 6, 0, 1)}>
              <line x1={m - (m - X(r.top1.ci95[0])) * w} x2={m + (X(r.top1.ci95[1]) - m) * w} y1={y} y2={y} stroke={c} strokeWidth={4} strokeLinecap="round" opacity={0.75} />
              {[0, 1].map((k) => (
                <line key={k} x1={X(r.top1.ci95[k])} x2={X(r.top1.ci95[k])} y1={y - 12} y2={y + 12} stroke={c} strokeWidth={3} opacity={ease(f, t + 22, t + 28, 0, 0.75)} />
              ))}
              <circle cx={m} cy={y} r={14 * dot} fill={r.tone === "ghost" ? C.ink : c} stroke={c} strokeWidth={r.tone === "ghost" ? 4 : 0} />
              <text x={X(r.top1.ci95[1]) + 22} y={y + 9} fill={c} fontFamily={MONO} fontSize={26} opacity={w}>{pct(r.top1.mean)}</text>
            </g>
          );
        })}
      </svg>
      {ID_ROWS.map((r, i) => (
        <div key={r.label} style={{ position: "absolute", left: SAFE, top: y0 + i * pitch - 30, width: 480, opacity: ease(f, times[i] - 4, times[i] + 8, 0, 1) }}>
          <div style={{ fontSize: 34, fontWeight: 500, color: r.tone === "hi" ? C.paper : C.dim, lineHeight: 1.1 }}>{r.label}</div>
          <div style={{ fontFamily: MONO, fontSize: 19, color: C.dim, marginTop: 4 }}>{r.sub}</div>
        </div>
      ))}
      <div style={{ position: "absolute", left: 1390, top: 330, width: 420 }}>
        <CountUp to={ID_ROWS[0].top1.mean * 100} at={L("s10_b", "sixty two")} dur={24} suffix="%" size={190} />
        <div style={{ fontSize: 34, color: C.paper, marginTop: -6, opacity: ease(f, L("s10_b", "sixty two") + 6, L("s10_b", "sixty two") + 20, 0, 1) }}>agree with experts</div>
        <div style={{ marginTop: 48, display: "flex", alignItems: "baseline", gap: 18 }}>
          <CountUp to={ID_ROWS[3].top1.mean * 100} at={L("s10_b", "thirty one")} dur={20} suffix="%" size={88} color={C.dim} />
          <span style={{ fontSize: 30, color: C.dim, opacity: ease(f, L("s10_b", "thirty one"), L("s10_b", "thirty one") + 14, 0, 1) }}>dictionary</span>
        </div>
        <Note at={L("s10_b", "thirty one") + 34} style={{ marginTop: 40, fontSize: 24, lineHeight: 1.5 }}>
          Brier {BRIER.model.toFixed(2)} vs {BRIER.lsj.toFixed(2)}
          <br />
          lower is better
        </Note>
      </div>
    </>
  );
};

// ---------- s10_c: calibration gauge ----------
const Calibration: React.FC = () => {
  const f = useCurrentFrame();
  const x0 = SAFE, x1 = 1920 - SAFE, max = 0.3, y = 650;
  const X = (v: number) => x0 + (v / max) * (x1 - x0);
  const tStart = L("s10_c", "calibration error");
  const tMove = L("s10_c", "to point one four");
  const tTarget = L("s10_c", "Our target");
  const tNot = L("s10_c", "We are not");
  const v = ease(f, tMove - 6, tMove + 26, ECE.before, ECE.after) as number;
  const show = ease(f, tStart, tStart + 12, 0, 1) as number;
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 140 }}>
        <Words text="Getting more honest" at={L("s10_c") - 8} size={84} accent={["honest"]} />
        <Note at={L("s10_c") + 10} style={{ marginTop: 14 }}>
          calibration error (ECE) of P(species) · {N_NAMES} names · plant-description match added
        </Note>
      </div>
      <div style={{ position: "absolute", left: SAFE, top: 330, display: "flex", alignItems: "center", gap: 44, fontFamily: MONO, fontWeight: 600, fontSize: 132, letterSpacing: "-0.03em" }}>
        <span style={{ color: C.dim, opacity: show }}>{ECE.before.toFixed(2)}</span>
        <svg width={120} height={40} style={{ opacity: ease(f, tMove - 8, tMove + 4, 0, 1) }}>
          <line x1={0} x2={ease(f, tMove - 8, tMove + 10, 0, 104)} y1={20} y2={20} stroke={C.lichen} strokeWidth={4} />
          <path d="M96 8 L116 20 L96 32" fill="none" stroke={C.lichen} strokeWidth={4} opacity={ease(f, tMove + 6, tMove + 12, 0, 1)} />
        </svg>
        <span style={{ color: C.hi, opacity: ease(f, tMove, tMove + 12, 0, 1) }}>{ECE.after.toFixed(2)}</span>
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <HatchDef id="gap" color={C.dim} />
        <g opacity={ease(f, L("s10_c"), L("s10_c") + 20, 0, 1)}>
          <line x1={x0} x2={x1} y1={y} y2={y} stroke={C.rule} strokeWidth={3} />
          {[0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3].map((t) => (
            <g key={t}>
              <line x1={X(t)} x2={X(t)} y1={y - 10} y2={y + 10} stroke={C.rule} strokeWidth={2} />
              <text x={X(t)} y={y + 48} fill={C.dim} fontFamily={MONO} fontSize={22} textAnchor="middle">{t.toFixed(2)}</text>
            </g>
          ))}
          <text x={x0} y={y - 46} fill={C.dim} fontFamily={MONO} fontSize={22}>← lower is better</text>
        </g>
        {/* not-there-yet gap: target → current */}
        <rect x={X(ECE.target)} y={y - 14} width={(X(ECE.after) - X(ECE.target)) * (ease(f, tNot - 4, tNot + 16, 0, 1) as number)} height={28} fill="url(#gap)" opacity={0.9} />
        {/* trail from 0.21 to the marker */}
        <line x1={X(ECE.before)} x2={X(v)} y1={y} y2={y} stroke={C.hi} strokeWidth={6} opacity={show} />
        <line x1={X(ECE.before)} x2={X(ECE.before)} y1={y - 22} y2={y + 22} stroke={C.dim} strokeWidth={3} opacity={show} />
        <circle cx={X(v)} cy={y} r={18 * show} fill={C.hi} />
        <circle cx={X(v)} cy={y} r={18 + 16 * (ease(f, tMove + 20, tMove + 44, 0, 1) as number)} fill="none" stroke={C.hi} strokeWidth={2} opacity={f < tMove + 20 ? 0 : (ease(f, tMove + 20, tMove + 44, 0.8, 0) as number)} />
        {/* target */}
        <g opacity={ease(f, tTarget, tTarget + 12, 0, 1)}>
          <line x1={X(ECE.target)} x2={X(ECE.target)} y1={y - 90} y2={y + 22} stroke={C.paper} strokeWidth={2} strokeDasharray="8 8" />
          <text x={X(ECE.target)} y={y - 104} fill={C.paper} fontFamily={MONO} fontSize={26} textAnchor="middle">target {ECE.target.toFixed(2)}</text>
        </g>
      </svg>
      <div style={{ position: "absolute", left: (X(ECE.target) + X(ECE.after)) / 2 - 200, width: 400, top: y + 92, textAlign: "center" }}>
        <Words text="not there yet" at={tNot} size={48} weight={500} style={{ justifyContent: "center" }} />
      </div>
    </>
  );
};

// ---------- s10_d: survival vs shuffled ----------
const Survival: React.FC = () => {
  const f = useCurrentFrame();
  const x0 = 560, w = 1000, max = 0.6;
  const X = (v: number) => x0 + (v / max) * w;
  const tObs = L("s10_d", "Forty nine");
  const tNull = L("s10_d", "against");
  const rows = [
    { label: "Observed", sub: "uses that recur today", v: PERM.observed_persisted_share, t: tObs, y: 400 },
    { label: "By chance", sub: `mean of ${fmt(PERM.n_permutations)} shuffles`, v: PERM.null_mean, t: tNull, y: 540 },
  ];
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 140 }}>
        <Words text="The uses survived" at={L("s10_d") - 8} size={84} accent={["survived"]} />
        <Note at={L("s10_d") + 10} style={{ marginTop: 14 }}>
          of {fmt(PERM.n_rows)} Dioscorides uses whose plant is in the modern Greek record ({fmt(MODERN_RECORDS)} village records)
        </Note>
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <HatchDef id="null" color={C.lichen} />
        <defs>
          <linearGradient id="obs" x1="0" x2="1">
            <stop offset="0" stopColor={C.verdigris} />
            <stop offset="1" stopColor={C.hi} />
          </linearGradient>
        </defs>
        {[0, 0.2, 0.4, 0.6].map((t) => (
          <g key={t} opacity={ease(f, L("s10_d"), L("s10_d") + 20, 0, 1)}>
            <line x1={X(t)} x2={X(t)} y1={350} y2={630} stroke={C.rule} strokeWidth={1.5} />
            <text x={X(t)} y={668} fill={C.dim} fontFamily={MONO} fontSize={20} textAnchor="middle">{pct(t)}</text>
          </g>
        ))}
        {rows.map((r, i) => {
          const g = ease(f, r.t, r.t + 26, 0, 1) as number;
          return (
            <g key={r.label}>
              <rect x={x0} y={r.y - 32} width={(X(r.v) - x0) * g} height={64} rx={10} fill={i === 0 ? "url(#obs)" : "url(#null)"} opacity={i === 0 ? 1 : 0.55} />
              <text x={X(max) + 60} y={r.y + 20} fill={i === 0 ? C.hi : C.lichen} fontFamily={MONO} fontWeight={600} fontSize={56} opacity={ease(f, r.t + 16, r.t + 28, 0, 1)}>
                {pct(r.v, 1)}
              </text>
            </g>
          );
        })}
        <g opacity={ease(f, tNull + 30, tNull + 44, 0, 1)}>
          <line x1={X(PERM.null_95pct)} x2={X(PERM.null_95pct)} y1={350} y2={610} stroke={C.paper} strokeWidth={2} strokeDasharray="6 8" />
          <text x={X(PERM.null_95pct)} y={712} fill={C.paper} fontFamily={MONO} fontSize={22} textAnchor="middle">95% of shuffles ≤ {pct(PERM.null_95pct, 1)}</text>
        </g>
      </svg>
      {rows.map((r) => (
        <div key={r.label} style={{ position: "absolute", left: SAFE, top: r.y - 34, opacity: ease(f, r.t - 4, r.t + 8, 0, 1) }}>
          <div style={{ fontSize: 38, fontWeight: 500 }}>{r.label}</div>
          <div style={{ fontFamily: MONO, fontSize: 19, color: C.dim, marginTop: 2 }}>{r.sub}</div>
        </div>
      ))}
      <div style={{ position: "absolute", left: SAFE, top: 750, display: "flex", alignItems: "baseline", gap: 24, opacity: ease(f, L("s10_d", "by chance"), L("s10_d", "by chance") + 14, 0, 1) }}>
        <span style={{ fontFamily: MONO, fontWeight: 600, fontSize: 64, color: C.hi }}>p = {PERM.p_value.toFixed(3)}</span>
        <span style={{ fontSize: 28, color: C.dim }}>{fmt(PERM.n_permutations)} label shuffles</span>
      </div>
      <Note at={L("s10_d", "by chance") + 20} style={{ position: "absolute", left: 860, top: 792, fontSize: 18 }}>
        caveat: the Mount Pelion study covers skin ailments only, which favours skin uses
      </Note>
    </>
  );
};

// ---------- s10_e: the honest null (ΔAUPRC per cutoff) ----------
const Backtest: React.FC = () => {
  const f = useCurrentFrame();
  const lo = -0.2, hi = 0.1, x0 = 560, x1 = 1440, y0 = 420, pitch = 92;
  const X = (v: number) => x0 + ((v - lo) / (hi - lo)) * (x1 - x0);
  const tPop = L("s10_e", "Research popularity");
  const tRows = L("s10_e", "adding history");
  const t2005 = L("s10_e", "in 2005");
  const tNull = L("s10_e", "We report");
  const popAuprc = BACKTEST.map((b) => b.pop);
  const swap = ease(f, tNull - 4, tNull + 6, 0, 1) as number;
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 140, width: 1100, height: 120 }}>
        <div style={{ position: "absolute", opacity: 1 - swap }}>
          <Words text="Did history predict science?" at={L("s10_e") - 8} size={84} />
        </div>
        <div style={{ position: "absolute", opacity: swap }}>
          <Words text="An honest null." at={tNull} size={84} accent={["null."]} />
        </div>
      </div>
      <Note at={L("s10_e") + 10} style={{ position: "absolute", left: SAFE, top: 256 }}>
        Δ precision score (AUPRC) = history + popularity − popularity alone · 95% bootstrap CI
      </Note>
      <Note at={tRows + 30} style={{ position: "absolute", left: SAFE, top: 790 }}>
        frozen backtest · no LLM features · modern studies gated by publication year
      </Note>
      <div style={{ position: "absolute", right: SAFE, top: 160, opacity: ease(f, tPop, tPop + 14, 0, 1), translate: `0px ${ease(f, tPop, tPop + 18, 12, 0)}px`, textAlign: "right" }}>
        <div style={{ fontFamily: MONO, fontSize: 20, color: C.dim, letterSpacing: "0.08em" }}>POPULARITY ALONE · AUPRC</div>
        <div style={{ fontFamily: MONO, fontWeight: 600, fontSize: 44, color: C.lichen }}>
          {Math.min(...popAuprc).toFixed(2)}–{Math.max(...popAuprc).toFixed(2)}
        </div>
        <div style={{ fontFamily: MONO, fontSize: 19, color: C.dim, marginTop: 2 }}>
          chance ≈ base rate {Math.min(...BACKTEST.map((b) => b.base)).toFixed(2)}–{Math.max(...BACKTEST.map((b) => b.base)).toFixed(2)}
        </div>
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <g opacity={ease(f, L("s10_e"), L("s10_e") + 20, 0, 1)}>
          {[-0.2, -0.1, 0, 0.1].map((t) => (
            <g key={t}>
              <line x1={X(t)} x2={X(t)} y1={y0 - 50} y2={y0 + pitch * 3 + 40} stroke={t === 0 ? C.paper : C.rule} strokeWidth={t === 0 ? 2 : 1.5} strokeDasharray={t === 0 ? "6 8" : undefined} opacity={t === 0 ? 0.6 : 1} />
              <text x={X(t)} y={y0 + pitch * 3 + 76} fill={C.dim} fontFamily={MONO} fontSize={20} textAnchor="middle">{t === 0 ? "0" : signed(t, 2)}</text>
            </g>
          ))}
          <text x={X(0) - 18} y={y0 - 66} fill={C.dim} fontFamily={MONO} fontSize={20} textAnchor="end">← history hurts</text>
          <text x={X(0) + 18} y={y0 - 66} fill={C.dim} fontFamily={MONO} fontSize={20}>helps →</text>
        </g>
        {BACKTEST.map((b, i) => {
          const t = tRows + i * 9;
          const y = y0 + i * pitch;
          const isBad = b.year === "2005";
          const red = isBad ? (ease(f, t2005, t2005 + 14, 0, 1) as number) : 0;
          const c = red > 0.5 ? C.warn : C.lichen;
          const w = ease(f, t + 8, t + 28, 0, 1) as number;
          const m = X(b.delta);
          return (
            <g key={b.year} opacity={ease(f, t - 2, t + 8, 0, 1)}>
              <line x1={m - (m - X(b.ci[0])) * w} x2={m + (X(b.ci[1]) - m) * w} y1={y} y2={y} stroke={c} strokeWidth={isBad ? 5 + red * 2 : 5} strokeLinecap="round" />
              <circle cx={m} cy={y} r={13 * (ease(f, t, t + 12, 0, 1) as number)} fill={red > 0.5 ? C.warn : C.hi} />
              {isBad && (
                <text x={X(b.ci[0])} y={y - 26} fill={C.warn} fontFamily={MONO} fontWeight={600} fontSize={26} opacity={red}>history hurts</text>
              )}
            </g>
          );
        })}
      </svg>
      {BACKTEST.map((b, i) => {
        const t = tRows + i * 9;
        const isBad = b.year === "2005";
        const red = isBad ? (ease(f, t2005, t2005 + 14, 0, 1) as number) : 0;
        return (
          <React.Fragment key={b.year}>
            <div style={{ position: "absolute", left: SAFE, top: y0 + i * pitch - 30, opacity: ease(f, t - 2, t + 8, 0, 1) }}>
              <div style={{ fontFamily: MONO, fontSize: 40, fontWeight: 600, color: red > 0.5 ? C.warn : C.paper, lineHeight: 1 }}>{b.year}</div>
              <div style={{ fontFamily: MONO, fontSize: 18, color: C.dim, marginTop: 6 }}>{fmt(b.n)} pairs · {b.positives} later studied</div>
            </div>
            <div style={{ position: "absolute", left: 1500, top: y0 + i * pitch - 18, fontFamily: MONO, fontSize: 28, color: red > 0.5 ? C.warn : C.dim, opacity: ease(f, t + 20, t + 32, 0, 1) }}>
              {signed(b.ci[0])} … {signed(b.ci[1])}
            </div>
          </React.Fragment>
        );
      })}
    </>
  );
};

// ---------- s10_f: the leads ----------
const Leads: React.FC = () => {
  const f = useCurrentFrame();
  const tN = L("s10_f", "one thousand");
  const t16 = L("s10_f", "Sixteen");
  const t2 = L("s10_f", "Seven carry");
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 200 }}>
        <CountUp to={LEADS.unsupported_today} at={tN} dur={40} size={250} />
        <div style={{ fontSize: 52, fontWeight: 500, marginTop: -4, opacity: ease(f, tN + 10, tN + 24, 0, 1) }}>untested plant–disease leads</div>
        <Note at={tN + 24} style={{ marginTop: 14 }}>
          no matching PubMed paper yet (co-mention search) · of {fmt(LEADS.candidate_pairs_scored)} pairs scored
        </Note>
      </div>
      {[
        { n: LEADS.top20_with_closed_evidence_path, c: C.hi, t: t16, head: "top leads with a full chemical path", sub: "compound → human target → disease" },
        { n: LEADS.top20_with_toxicity_flag, c: C.warn, t: t2, head: "carry a toxicity flag", sub: "shown, never hidden · PubChem-cited" },
      ].map((s, i) => (
        <div key={i} style={{ position: "absolute", left: 1180, top: 210 + i * 250, borderLeft: `3px solid ${s.c}`, paddingLeft: 32, opacity: ease(f, s.t, s.t + 12, 0, 1), translate: `${ease(f, s.t, s.t + 18, 30, 0)}px 0px` }}>
          <div style={{ fontFamily: MONO, fontWeight: 600, fontSize: 120, color: s.c, lineHeight: 1, letterSpacing: "-0.03em" }}>
            {s.n}
            <span style={{ fontSize: 64, color: C.dim }}>/20</span>
          </div>
          <div style={{ fontSize: 34, marginTop: 12 }}>{s.head}</div>
          <div style={{ fontFamily: MONO, fontSize: 21, color: C.dim, marginTop: 6 }}>{s.sub}</div>
        </div>
      ))}
      <div style={{ position: "absolute", left: SAFE, top: 740, display: "inline-flex", alignItems: "center", gap: 16, padding: "14px 28px", borderRadius: 999, border: `1px solid ${C.rule}`, background: C.card, opacity: ease(f, t2 + 40, t2 + 56, 0, 1) }}>
        <div style={{ width: 10, height: 10, borderRadius: 99, background: C.hi }} />
        <span style={{ fontSize: 30, color: C.paper }}>{DISCLAIMER}</span>
      </div>
    </>
  );
};

export const Results: React.FC = () => {
  const f = useCurrentFrame();
  const t = scene(S);
  const start = (id: string) => L(id) - 14;
  const stop = (id: string) => L(id) - 24; // exit just before the next line
  return (
    <Stage glow="tr">
      <Grid />
      <AbsoluteFill style={{ scale: `${1 + (f / t.duration) * 0.02}`, fontFamily: OUTFIT, color: C.paper }}>
        <Beat from={-18} to={stop("s10_b")}>
          <Opening />
        </Beat>
        <Beat from={start("s10_b")} to={stop("s10_c")}>
          <Kicker text="01 · identification" at={start("s10_b")} />
          <IdPlot />
        </Beat>
        <Beat from={start("s10_c")} to={stop("s10_d")}>
          <Kicker text="01 · calibration" at={start("s10_c")} />
          <Calibration />
        </Beat>
        <Beat from={start("s10_d")} to={stop("s10_e")}>
          <Kicker text="02 · did the uses survive?" at={start("s10_d")} />
          <Survival />
        </Beat>
        <Beat from={start("s10_e")} to={stop("s10_f")}>
          <Kicker text="03 · the time machine" at={start("s10_e")} />
          <Backtest />
        </Beat>
        <Beat from={start("s10_f")} to={t.duration + 20}>
          <Kicker text="04 · leads for Eleni" at={start("s10_f")} />
          <Leads />
        </Beat>
      </AbsoluteFill>
      <div style={{ position: "absolute", right: SAFE, top: 94, fontFamily: MONO, fontSize: 20, color: C.dim, opacity: ease(f, 10, 30, 0, 0.9) }}>{DISCLAIMER}</div>
    </Stage>
  );
};
