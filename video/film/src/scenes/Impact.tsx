// Scene "impact" (s11_a–c): who it helps, what we don't claim, what comes next.
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, DIDOT, MONO, OUTFIT, SAFE, Stage, Words, ease } from "../brand";
import { scene } from "../timing";
import { IUCN_ROWS, IUCN_SPECIES, N_NAMES, SPECIES_TOTAL, TOP_LEAD, WORMWOOD, at, fmt } from "./results/data";
import { Beat, Grid, Kicker } from "./results/kit";

const S = "impact";
const L = (id: string, phrase = "") => at(S, id, phrase);

/** Line icon drawn like a pen stroke (100×100 viewBox). */
const Icon: React.FC<{ d: string; t: number }> = ({ d, t }) => {
  const f = useCurrentFrame();
  return (
    <svg width={84} height={84} viewBox="0 0 100 100">
      <path d={d} fill="none" stroke={C.hi} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={ease(f, t, t + 30, 1, 0)} />
    </svg>
  );
};

const ICONS = {
  flask: "M38 10 H62 M44 10 V38 L18 80 Q14 88 24 88 H76 Q86 88 82 80 L56 38 V10 M30 66 H70",
  book: "M50 24 C38 15 22 15 10 19 V83 C22 79 38 79 50 87 C62 79 78 79 90 83 V19 C78 15 62 15 50 24 Z M50 24 V87",
  leaf: "M18 84 C18 44 46 16 86 14 C86 54 60 84 18 84 Z M18 84 L62 40",
};

const BenefitCard: React.FC<{ x: number; t: number; icon: string; title: string; line: string; children: React.ReactNode }> = ({ x, t, icon, title, line, children }) => {
  const f = useCurrentFrame();
  const p = ease(f, t, t + 20, 0, 1) as number;
  return (
    <div style={{ position: "absolute", left: x, top: 290, width: 533, height: 530, boxSizing: "border-box", background: C.card, border: `1px solid ${p > 0.5 ? C.rule : "rgba(31,44,37,.6)"}`, borderRadius: 26, padding: "40px 40px", opacity: 0.45 + 0.55 * p }}>
      <div style={{ opacity: p, translate: `0px ${(1 - p) * 30}px` }}>
        <Icon d={icon} t={t + 4} />
        <div style={{ fontSize: 52, fontWeight: 600, letterSpacing: "-0.03em", marginTop: 18 }}>{title}</div>
        <div style={{ fontSize: 30, color: C.dim, marginTop: 6, lineHeight: 1.25 }}>{line}</div>
      </div>
      <div style={{ position: "absolute", left: 40, right: 40, bottom: 36, borderTop: `1px solid ${C.rule}`, paddingTop: 22, opacity: ease(f, t + 18, t + 34, 0, 1) }}>{children}</div>
    </div>
  );
};

const statusShort = (s: string) => s.toLowerCase();

const Benefits: React.FC = () => (
  <>
    <div style={{ position: "absolute", left: SAFE, top: 140 }}>
      <Words text="Who it helps" at={0} size={84} accent={["helps"]} />
    </div>
    <BenefitCard x={SAFE} t={L("s11_a")} icon={ICONS.flask} title="Labs" line="a shortlist with reasons">
      <div style={{ fontFamily: MONO, fontSize: 19, color: C.dim }}>LEAD #{TOP_LEAD.rank}</div>
      <div style={{ fontSize: 36, fontStyle: "italic", marginTop: 4 }}>{TOP_LEAD.species}</div>
      <div style={{ fontFamily: MONO, fontSize: 21, color: C.lichen, marginTop: 6 }}>
        {TOP_LEAD.condition} · P {TOP_LEAD.p.toFixed(2)} · path {TOP_LEAD.has_paths ? "✓" : "—"}
      </div>
    </BenefitCard>
    <BenefitCard x={SAFE + 573} t={L("s11_a", "For historians")} icon={ICONS.book} title="Historians" line="Dioscorides, read with evidence">
      <div style={{ fontFamily: DIDOT, fontSize: 60, lineHeight: 1.1 }} lang="grc">{WORMWOOD.lemma}</div>
      <div style={{ fontFamily: MONO, fontSize: 19, color: C.lichen, marginTop: 8 }}>{WORMWOOD.chapter} · every quote checked</div>
    </BenefitCard>
    <BenefitCard x={SAFE + 1146} t={L("s11_a", "For conservation")} icon={ICONS.leaf} title="Conservation" line="IUCN status per species, where assessed">
      {IUCN_ROWS.map((r) => (
        <div key={r.species} style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12, marginBottom: 6 }}>
          <span style={{ fontSize: 25, fontStyle: "italic", whiteSpace: "nowrap" }}>{r.species}</span>
          <span style={{ fontFamily: MONO, fontSize: 17, color: C.lichen, whiteSpace: "nowrap" }}>{statusShort(r.iucn as string)}</span>
        </div>
      ))}
      <div style={{ fontFamily: MONO, fontSize: 17, color: C.dim, marginTop: 6 }}>
        {fmt(IUCN_SPECIES)} of {fmt(SPECIES_TOTAL)} lead species assessed
      </div>
    </BenefitCard>
  </>
);

const LIMITS = [
  { phrase: "Expert judgement", title: "Expert judgement ≠ ground truth", sub: `${N_NAMES} gold names · wide intervals` },
  { phrase: "A search hit", title: "A search hit is only a proxy", sub: "PubMed co-mention, not evidence of effect" },
  { phrase: "our audits", title: "Audits still need human experts", sub: "quotes verified word for word, not yet expert-reviewed" },
  { phrase: "Everything here", title: "Hypotheses, never medical advice", sub: "no dosing · toxicity flagged, never hidden" },
];

const Limits: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 140 }}>
        <Words text="What we don't claim" at={L("s11_b") - 10} size={84} color={C.paper} />
      </div>
      {LIMITS.map((c, i) => {
        const t = L("s11_b", c.phrase) - 4;
        const p = ease(f, t, t + 18, 0, 1) as number;
        return (
          <div key={i} style={{ position: "absolute", left: SAFE + (i % 2) * 860, top: 300 + Math.floor(i / 2) * 260, width: 820, height: 220, boxSizing: "border-box", background: C.card, border: `1px solid ${C.rule}`, borderRadius: 24, padding: "34px 40px", opacity: p, translate: `0px ${(1 - p) * 26}px` }}>
            <div style={{ fontFamily: MONO, fontSize: 20, color: C.lichen, letterSpacing: "0.12em" }}>0{i + 1}</div>
            <div style={{ fontSize: 44, fontWeight: 500, color: C.paper, marginTop: 14, letterSpacing: "-0.02em" }}>{c.title}</div>
            <div style={{ fontFamily: MONO, fontSize: 21, color: C.dim, marginTop: 12 }}>{c.sub}</div>
          </div>
        );
      })}
    </>
  );
};

const STEPS = [
  { phrase: "expert audits", title: "Expert audits", sub: "claims · conditions · labels" },
  { phrase: "richer", title: "Richer plant descriptions", sub: "Flora of Greece · POWO" },
  { phrase: "more Byzantine", title: "More Byzantine authors", sub: "Paul of Aegina · Oribasius" },
  { phrase: "a lab partner", title: "A lab partner", sub: "to test the top leads" },
];

const Roadmap: React.FC = () => {
  const f = useCurrentFrame();
  const x0 = 260, x1 = 1660, y = 500;
  const xs = STEPS.map((_, i) => x0 + (i * (x1 - x0)) / (STEPS.length - 1));
  const ts = STEPS.map((s) => L("s11_c", s.phrase) - 4);
  // lit length: grows to each node as it is named
  let lit = x0;
  ts.forEach((t, i) => {
    if (i > 0) lit = Math.max(lit, ease(f, t - 10, t + 6, xs[i - 1], xs[i]) as number);
  });
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 140 }}>
        <Words text="What comes next" at={L("s11_c") - 10} size={84} accent={["next"]} />
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={x0} x2={ease(f, L("s11_c") - 10, L("s11_c") + 20, x0, x1)} y1={y} y2={y} stroke={C.rule} strokeWidth={3} />
        <line x1={x0} x2={lit} y1={y} y2={y} stroke={C.hi} strokeWidth={4} />
        {xs.map((x, i) => {
          const on = ease(f, ts[i], ts[i] + 10, 0, 1) as number;
          return (
            <g key={i}>
              <circle cx={x} cy={y} r={34 * on} fill="none" stroke={C.hi} strokeWidth={1.5} opacity={on * 0.5} />
              <circle cx={x} cy={y} r={20} fill={on > 0.5 ? C.hi : C.ink} stroke={on > 0.5 ? C.hi : C.rule} strokeWidth={3} opacity={ease(f, L("s11_c") - 10, L("s11_c") + 10, 0, 1)} />
            </g>
          );
        })}
      </svg>
      {STEPS.map((s, i) => {
        const p = ease(f, ts[i], ts[i] + 16, 0, 1) as number;
        return (
          <div key={i} style={{ position: "absolute", left: xs[i] - 200, top: y + 64, width: 400, textAlign: "center", opacity: 0.25 + 0.75 * p, translate: `0px ${(1 - p) * 16}px` }}>
            <div style={{ fontFamily: MONO, fontSize: 20, color: p > 0.5 ? C.hi : C.dim, letterSpacing: "0.12em" }}>0{i + 1}</div>
            <div style={{ fontSize: 38, fontWeight: 500, marginTop: 8, lineHeight: 1.15, color: p > 0.5 ? C.paper : C.dim }}>{s.title}</div>
            <div style={{ fontFamily: MONO, fontSize: 20, color: C.dim, marginTop: 10, opacity: p }}>{s.sub}</div>
          </div>
        );
      })}
    </>
  );
};

export const Impact: React.FC = () => {
  const f = useCurrentFrame();
  const t = scene(S);
  return (
    <Stage glow="bl">
      <Grid />
      <AbsoluteFill style={{ scale: `${1 + (f / t.duration) * 0.02}`, fontFamily: OUTFIT, color: C.paper }}>
        <Beat from={-18} to={L("s11_b") - 24}>
          <Kicker text="impact · who benefits" at={0} />
          <Benefits />
        </Beat>
        <Beat from={L("s11_b") - 14} to={L("s11_c") - 24}>
          <Kicker text="limits · stated plainly" at={L("s11_b") - 14} />
          <Limits />
        </Beat>
        <Beat from={L("s11_c") - 14} to={t.duration + 20}>
          <Kicker text="future development" at={L("s11_c") - 14} />
          <Roadmap />
        </Beat>
      </AbsoluteFill>
    </Stage>
  );
};
