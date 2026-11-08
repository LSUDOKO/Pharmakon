// Shared helpers for the Cold / Problem / Motivation / Turn scenes.
import React, { useState } from "react";
import { Img, staticFile } from "remotion";
import { C, MONO, ease } from "../../brand";
import { scene } from "../../timing";

/** Frame (scene-relative) of a word: VO line i start + the word's offset in that line (from whisper word timings). */
export const cue = (sceneId: string, i: number, offset = 0) => scene(sceneId).lines[i].from + offset;

/** Fade-in at `a`, fade-out at `b` (both with brand easing). */
export const life = (f: number, a: number, b: number, inDur = 12, outDur = 14) =>
  Math.min(ease(f, a, a + inDur, 0, 1) as number, ease(f, b, b + outDur, 1, 0) as number);

/** Remote photo that falls back to a local folio if it fails to load. */
export const Photo: React.FC<{ src: string; fallback?: string; style?: React.CSSProperties }> = ({ src, fallback = "media/folio-iris.webp", style }) => {
  const [bad, setBad] = useState(false);
  return (
    <Img
      src={bad ? staticFile(fallback) : src}
      onError={() => setBad(true)}
      maxRetries={4}
      style={{ width: "100%", height: "100%", objectFit: "cover", display: "block", ...style }}
    />
  );
};

/** Small mono citation / credit line. */
export const Cite: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; opacity?: number }> = ({ children, style, opacity = 1 }) => (
  <div style={{ fontFamily: MONO, fontSize: 18, color: C.dim, letterSpacing: "0.01em", opacity: 0.9 * opacity, ...style }}>{children}</div>
);

/** A sample vial drawn as a clean line icon. draw: 0..1 stroke progress. */
export const Vial: React.FC<{ draw?: number; color?: string; w?: number; h?: number; style?: React.CSSProperties }> = ({
  draw = 1, color = C.dim, w = 52, h = 190, style,
}) => {
  const sw = 2.4;
  const props = { pathLength: 1, strokeDasharray: 1, strokeDashoffset: 1 - draw, fill: "none", stroke: color, strokeWidth: sw, strokeLinecap: "round" as const };
  return (
    <svg width={w} height={h} viewBox="0 0 52 190" style={{ overflow: "visible", ...style }}>
      {/* cap */}
      <path {...props} d="M8 6 H44 V30 H8 Z" />
      {/* tube with round bottom */}
      <path {...props} d="M12 30 V160 A14 14 0 0 0 40 160 V30" />
      {/* label line */}
      <path {...props} d="M17 64 H35" opacity={0.6} />
    </svg>
  );
};

/** Open book, ink-line SVG drawn progressively. */
export const Book: React.FC<{ draw: number; color?: string; size?: number }> = ({ draw, color = C.paper, size = 300 }) => {
  const seg = (i: number, n: number) => Math.max(0, Math.min(1, draw * n - i));
  const p = (d: string, i: number, n: number, op = 1) => (
    <path d={d} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - seg(i, n)} fill="none" stroke={color} strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" opacity={op} />
  );
  const n = 9;
  return (
    <svg width={size} height={size * 0.62} viewBox="0 0 300 186" style={{ overflow: "visible" }}>
      {p("M150 40 C120 22 70 18 18 26 V164 C70 156 120 160 150 178", 0, n)}
      {p("M150 40 C180 22 230 18 282 26 V164 C230 156 180 160 150 178", 1, n)}
      {p("M150 40 V178", 2, n)}
      {p("M40 52 C70 48 104 50 130 60", 3, n, 0.55)}
      {p("M40 76 C70 72 104 74 130 84", 4, n, 0.55)}
      {p("M40 100 C70 96 104 98 130 108", 5, n, 0.55)}
      {p("M170 60 C196 50 230 48 260 52", 6, n, 0.55)}
      {p("M170 84 C196 74 230 72 260 76", 7, n, 0.55)}
      {p("M170 108 C196 98 230 96 260 100", 8, n, 0.55)}
    </svg>
  );
};

/** Deterministic pseudo-random in [0,1) from an integer seed. */
export const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
