// Shared pieces for the results / impact / outro scenes.
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, EASE_IN, MONO, SAFE, ease } from "../../brand";

export const DISCLAIMER = "Research hypotheses only — not medical advice";

/** A full-frame beat: rises in on `from`, sinks out quickly at `to`. Not rendered outside its window. */
export const Beat: React.FC<{ from: number; to: number; children: React.ReactNode }> = ({ from, to, children }) => {
  const f = useCurrentFrame();
  if (f < from - 1 || f > to + 12) return null;
  const inn = ease(f, from, from + 18, 0, 1) as number;
  const out = ease(f, to, to + 10, 0, 1, EASE_IN) as number;
  return (
    <AbsoluteFill style={{ opacity: inn * (1 - out), translate: `0px ${(1 - inn) * 24 - out * 16}px` }}>{children}</AbsoluteFill>
  );
};

/** Section kicker top-left: verdigris tick + mono label. */
export const Kicker: React.FC<{ text: string; at: number }> = ({ text, at }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: SAFE, top: 92, display: "flex", alignItems: "center", gap: 16, opacity: ease(f, at, at + 12, 0, 1) }}>
      <div style={{ width: ease(f, at, at + 20, 0, 36), height: 2, background: C.hi }} />
      <span style={{ fontFamily: MONO, fontSize: 22, letterSpacing: "0.14em", color: C.lichen, textTransform: "uppercase" }}>{text}</span>
    </div>
  );
};

/** Small mono line (sources, axis notes). Kept above the caption band. */
export const Note: React.FC<{ children: React.ReactNode; at: number; style?: React.CSSProperties }> = ({ children, at, style }) => {
  const f = useCurrentFrame();
  return <div style={{ fontFamily: MONO, fontSize: 22, color: C.dim, opacity: ease(f, at, at + 14, 0, 0.95), ...style }}>{children}</div>;
};

/** Faint 12-column rule grid — the composed background every frame starts on. */
export const Grid: React.FC<{ opacity?: number }> = ({ opacity = 0.35 }) => {
  const f = useCurrentFrame();
  const cols = Array.from({ length: 13 }, (_, i) => SAFE + (i * (1920 - 2 * SAFE)) / 12);
  return (
    <AbsoluteFill style={{ opacity, translate: `${-f * 0.04}px 0px` }}>
      <svg width={1920} height={1080}>
        {cols.map((x, i) => (
          <line key={i} x1={x} x2={x} y1={0} y2={1080} stroke={C.rule} strokeWidth={1} strokeDasharray="2 10" />
        ))}
      </svg>
    </AbsoluteFill>
  );
};

/** SVG hatch pattern (135°, 1 px every 7 px) for "chance" / "not yet" fills. */
export const HatchDef: React.FC<{ id: string; color: string }> = ({ id, color }) => (
  <defs>
    <pattern id={id} width={7} height={7} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1={0} y1={0} x2={0} y2={7} stroke={color} strokeWidth={2} />
    </pattern>
  </defs>
);
