// Shared bits for the Data / Method / Hood scenes. Glyphs outside the fonts' latin subset (→ ✓ ✗ ↔) are drawn as SVG.
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, DIDOT, EASE_IN, MONO, TornSheet, ease } from "../../brand";

/** frame where word `t` seconds into a VO line lands (line.from is scene-relative) */
export const at = (lineFrom: number, t: number) => lineFrom + Math.round(t * 30);

export const Tick: React.FC<{ size?: number; color?: string; draw?: number }> = ({ size = 28, color = C.hi, draw = 1 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{ flex: "none" }}>
    <path d="M4 12.5l5 5L20 6.5" fill="none" stroke={color} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
  </svg>
);

export const Cross: React.FC<{ size?: number; color?: string }> = ({ size = 24, color = C.dim }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{ flex: "none" }}>
    <path d="M6 6l12 12M18 6L6 18" fill="none" stroke={color} strokeWidth={2.4} strokeLinecap="round" />
  </svg>
);

export const Arrow: React.FC<{ w?: number; color?: string; both?: boolean; draw?: number }> = ({ w = 40, color = C.lichen, both = false, draw = 1 }) => (
  <svg width={w} height={18} viewBox={`0 0 ${w} 18`} style={{ flex: "none", overflow: "visible" }}>
    <line x1={both ? 3 : 0} y1={9} x2={(w - 3) * draw} y2={9} stroke={color} strokeWidth={2} strokeLinecap="round" />
    {draw > 0.95 && <path d={`M${w - 9} 3l7 6-7 6`} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />}
    {both && <path d="M10 3L3 9l7 6" fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />}
  </svg>
);

/** Small mono kicker, e.g. "02 · IDENTIFY". */
export const Kicker: React.FC<{ children: React.ReactNode; color?: string; style?: React.CSSProperties }> = ({ children, color = C.hi, style }) => (
  <div style={{ fontFamily: MONO, fontSize: 22, letterSpacing: "0.22em", textTransform: "uppercase", color, ...style }}>{children}</div>
);

/** Fade + rise in at `a`, quick ease-in exit at `out`. */
export const Reveal: React.FC<{ a: number; out?: number; dy?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ a, out, dy = 24, children, style }) => {
  const f = useCurrentFrame();
  const o = ease(f, a, a + 14, 0, 1) as number;
  const x = out === undefined ? 1 : (ease(f, out, out + 8, 1, 0, EASE_IN) as number);
  return (
    <div style={{ opacity: o * x, translate: `0px ${(1 - o) * dy - (1 - x) * 12}px`, filter: `blur(${(1 - o) * 8}px)`, ...style }}>{children}</div>
  );
};

/**
 * Greek that "inks in" left to right (clip-path wipe on one run, so polytonic diacritics stay intact).
 * `mark` is highlighted with a verdigris sweep starting at `markAt`.
 */
export const InkGreek: React.FC<{ text: string; a: number; dur: number; size?: number; mark?: string; markAt?: number; style?: React.CSSProperties }> = ({
  text, a, dur, size = 48, mark, markAt = 0, style,
}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [a, a + dur], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const t = text.normalize("NFC");
  const m = mark ? mark.normalize("NFC") : "";
  const i = m ? t.indexOf(m) : -1;
  const sweep = ease(f, markAt, markAt + 16, 0, 100) as number;
  const parts = i < 0 ? [t] : [t.slice(0, i), t.slice(i, i + m.length), t.slice(i + m.length)];
  return (
    <div lang="grc" style={{ fontFamily: DIDOT, fontSize: size, lineHeight: 1.42, color: C.paper, clipPath: `inset(-10% ${100 - p}% -10% 0)`, ...style }}>
      {parts.map((s, k) =>
        k === 1 ? (
          <span key={k} style={{ position: "relative", whiteSpace: "nowrap" }}>
            <span style={{ position: "absolute", left: -6, right: -6, top: "8%", bottom: "4%", borderRadius: 8, background: "rgba(23,116,79,.55)", border: `1px solid ${C.hi}`, clipPath: `inset(0 ${100 - sweep}% 0 0)` }} />
            <span style={{ position: "relative", color: sweep > 50 ? C.lichen : C.paper }}>{s}</span>
          </span>
        ) : (
          <span key={k}>{s}</span>
        ),
      )}
    </div>
  );
};

/** Code block in JetBrains Mono, radius 14 (as on the site). Types in from `a`. */
export const Code: React.FC<{ text: string; a: number; cps?: number; size?: number; style?: React.CSSProperties; label?: string }> = ({ text, a, cps = 2.2, size = 24, style, label }) => {
  const f = useCurrentFrame();
  const n = Math.max(0, Math.floor((f - a) * cps));
  const caret = f >= a && n < text.length && Math.floor(f / 8) % 2 === 0;
  return (
    <div style={{ background: C.card, border: `1px solid ${C.rule}`, borderRadius: 14, padding: "18px 24px", fontFamily: MONO, fontSize: size, lineHeight: 1.5, color: C.lichen, ...style }}>
      {label && <div style={{ fontSize: size * 0.72, color: C.dim, marginBottom: 6 }}>{label}</div>}
      <span>{text.slice(0, n)}</span>
      {caret && <span style={{ background: C.hi, color: C.ink }}> </span>}
    </div>
  );
};

/** Licence / status chip in mono. */
export const Chip: React.FC<{ children: React.ReactNode; color?: string; style?: React.CSSProperties }> = ({ children, color = C.dim, style }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 8, fontFamily: MONO, fontSize: 18, color, border: `1px solid ${C.rule}`, borderRadius: 999, padding: "5px 12px", ...style }}>{children}</span>
);

/** Padlock that closes (shackle drops) between `a` and `a+12`. */
export const Padlock: React.FC<{ a: number; size?: number }> = ({ a, size = 120 }) => {
  const f = useCurrentFrame();
  const drop = ease(f, a, a + 12, -14, 0) as number;
  const glow = ease(f, a + 8, a + 24, 0, 1) as number;
  return (
    <svg width={size} height={size * 1.2} viewBox="0 0 100 120" style={{ overflow: "visible", filter: `drop-shadow(0 0 ${18 * glow}px rgba(61,187,130,.55))` }}>
      <path d={`M28 ${58 + drop} V38 a22 22 0 0 1 44 0 V${58 + drop}`} fill="none" stroke={C.lichen} strokeWidth={8} strokeLinecap="round" />
      <rect x={14} y={54} width={72} height={58} rx={12} fill={C.verdigris} stroke={C.hi} strokeWidth={2} />
      <circle cx={50} cy={78} r={7} fill={C.ink} />
      <rect x={47} y={80} width={6} height={16} rx={3} fill={C.ink} />
    </svg>
  );
};

/** A torn folio sheet pushed into the top-right corner as set dressing (site masks + public-domain folio). */
export const CornerSheet: React.FC<{ img: string; dx?: number; dy?: number; opacity?: number }> = ({ img, dx = 640, dy = -330, opacity = 1 }) => {
  const f = useCurrentFrame();
  return (
    <TornSheet
      which="a"
      img={img}
      style={{ translate: `${dx + f * 0.04}px ${dy - f * 0.03}px`, scale: `${1 + f * 0.00002}`, opacity }}
    />
  );
};
