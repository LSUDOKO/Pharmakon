// Pharmakon brand system for the film — mirrors web/src/style.css. Every scene imports from here.
import React from "react";
import { loadFont as loadOutfit } from "@remotion/google-fonts/Outfit";
import { loadFont as loadDidot } from "@remotion/google-fonts/GFSDidot";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const OUTFIT = loadOutfit("normal", { weights: ["300", "400", "500", "600", "700"], subsets: ["latin"] }).fontFamily;
export const DIDOT = loadDidot("normal", { weights: ["400"], subsets: ["greek", "greek-ext", "latin"] }).fontFamily;
export const MONO = loadMono("normal", { weights: ["400", "600"], subsets: ["latin"] }).fontFamily;

export const C = {
  ink: "#000000",
  card: "#0B120E",
  rule: "#1F2C25",
  hatch: "#1E1E1E",
  verdigris: "#17744F",
  hi: "#3DBB82",
  lichen: "#B8E6CC",
  paper: "#ECEEE7",
  dim: "#A9B0AB",
  warn: "#FF5A5F",
} as const;

export const CHROME = "linear-gradient(180deg, #FFFFFF 0%, #DFE3E0 45%, #8B938F 62%, #F3F5F4 100%)";
export const EXPO = Easing.bezier(0.16, 1, 0.3, 1);
export const EASE_IN = Easing.bezier(0.55, 0, 1, 0.45);
export const SAFE = 120; // px side margin at 1080p

/** clamp-interpolate helper with the brand ease */
export const ease = (frame: number, a: number, b: number, from: number | string, to: number | string, easing = EXPO) =>
  interpolate(frame, [a, b], [from as number, to as number], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing });

/** Base frame: true black, faint verdigris glow in a corner, paper grain, vignette. Wrap every scene in it. */
export const Stage: React.FC<{ children: React.ReactNode; glow?: "tr" | "bl" | "none" }> = ({ children, glow = "tr" }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.ink, fontFamily: OUTFIT, color: C.paper, overflow: "hidden" }}>
      {glow !== "none" && (
        <AbsoluteFill
          style={{
            background: `radial-gradient(circle at ${glow === "tr" ? "92% 6%" : "8% 94%"}, rgba(23,116,79,.30), transparent 42%)`,
            opacity: 0.85 + 0.15 * Math.sin(frame / 45),
          }}
        />
      )}
      {children}
      <Grain />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,.55) 100%)", pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};

/** Animated paper grain (seeded by frame, deterministic). */
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.05 }) => {
  const frame = useCurrentFrame();
  const seed = frame % 8;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, mixBlendMode: "screen" }}>
      <svg width="100%" height="100%">
        <filter id={`grain${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={3} seed={seed} />
          <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.1 -0.2" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#grain${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

/** Word-by-word headline reveal: mask wipe up + blur-to-sharp. `accent` words render in verdigris-hi. */
export const Words: React.FC<{
  text: string;
  at?: number; // start frame (local)
  stagger?: number; // frames between words
  size?: number;
  weight?: number;
  color?: string;
  accent?: string[];
  font?: string;
  style?: React.CSSProperties;
  out?: number; // frame to start exit (optional)
}> = ({ text, at = 0, stagger = 3, size = 96, weight = 600, color = C.paper, accent = [], font = OUTFIT, style, out }) => {
  const frame = useCurrentFrame();
  const words = text.split(" ");
  const exit = out === undefined ? 1 : ease(frame, out, out + 8, 1, 0, EASE_IN);
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: `0 ${size * 0.26}px`, fontFamily: font, fontSize: size, fontWeight: weight, lineHeight: 1.08, letterSpacing: font === OUTFIT ? "-0.025em" : 0, color, opacity: exit, ...style }}>
      {words.map((w, i) => {
        const s = at + i * stagger;
        const isAccent = accent.some((a) => w.toLowerCase().replace(/[^\p{L}\d%.,]/gu, "").startsWith(a.toLowerCase()));
        return (
          <span key={i} style={{ display: "inline-block", overflow: "hidden", paddingBottom: size * 0.12, marginBottom: -size * 0.12 }}>
            <span
              style={{
                display: "inline-block",
                color: isAccent ? C.hi : undefined,
                translate: `0px ${ease(frame, s, s + 14, size * 0.45, 0)}px`,
                opacity: ease(frame, s, s + 10, 0, 1),
                filter: `blur(${ease(frame, s, s + 12, 10, 0)}px)`,
              }}
            >
              {w}
            </span>
          </span>
        );
      })}
    </div>
  );
};

/** Number counting up in JetBrains Mono. */
export const CountUp: React.FC<{ to: number; at?: number; dur?: number; decimals?: number; suffix?: string; prefix?: string; size?: number; color?: string; style?: React.CSSProperties }> = ({
  to, at = 0, dur = 30, decimals = 0, suffix = "", prefix = "", size = 120, color = C.hi, style,
}) => {
  const frame = useCurrentFrame();
  const v = ease(frame, at, at + dur, 0, to) as number;
  const txt = v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  return (
    <span style={{ fontFamily: MONO, fontWeight: 600, fontSize: size, color, letterSpacing: "-0.03em", opacity: ease(frame, at, at + 6, 0, 1), ...style }}>
      {prefix}
      {txt}
      {suffix}
    </span>
  );
};

/** Small source line, bottom-left, paper-dim mono. */
export const Source: React.FC<{ text: string; at?: number }> = ({ text, at = 0 }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: SAFE, bottom: 64, fontFamily: MONO, fontSize: 20, color: C.dim, opacity: ease(frame, at, at + 12, 0, 0.9) }}>
      {text}
    </div>
  );
};

/** Liquid-glass pill (as the site's .glass buttons). */
export const Glass: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      display: "inline-flex", alignItems: "center", gap: 12, padding: "14px 26px", borderRadius: 999,
      background: "linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.03))",
      border: "1px solid rgba(184,230,204,.28)", boxShadow: "inset 0 1px 0 rgba(255,255,255,.22), 0 10px 40px rgba(23,116,79,.25)",
      backdropFilter: "blur(14px)", color: C.paper, fontFamily: OUTFIT, fontWeight: 500, fontSize: 30, ...style,
    }}
  >
    {children}
  </div>
);

/** Card surface. */
export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.card, border: `1px solid ${C.rule}`, borderRadius: 26, padding: "36px 40px", ...style }}>{children}</div>
);

/** A torn paper sheet using the site's masks (a = top-right, b = bottom-left). */
export const TornSheet: React.FC<{ which: "a" | "b"; img?: string; style?: React.CSSProperties }> = ({ which, img, style }) => {
  const mask = (f: string): React.CSSProperties => ({
    maskImage: `url(${staticFile(`media/${f}-${which}.svg`)})`, WebkitMaskImage: `url(${staticFile(`media/${f}-${which}.svg`)})`,
    maskSize: "100% 100%", WebkitMaskSize: "100% 100%", maskRepeat: "no-repeat", WebkitMaskRepeat: "no-repeat",
  });
  return (
    <AbsoluteFill style={style}>
      <AbsoluteFill style={{ ...mask("fringe"), background: C.paper, filter: "drop-shadow(0 18px 30px rgba(0,0,0,.7))" }} />
      <AbsoluteFill style={{ ...mask("tear"), background: C.verdigris }}>
        {img && <Img src={staticFile(img)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** The chrome wordmark with the mark. */
export const Wordmark: React.FC<{ size?: number; style?: React.CSSProperties }> = ({ size = 168, style }) => (
  <div style={{ display: "flex", alignItems: "center", gap: size * 0.18, ...style }}>
    <Img src={staticFile("media/mark.svg")} style={{ width: size * 0.78, height: size * 0.78 }} />
    <span style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: size, letterSpacing: "-0.045em", lineHeight: 1, backgroundImage: CHROME, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", paddingBottom: size * 0.08 }}>
      pharmakon
    </span>
  </div>
);

/** Greek text in GFS Didot. */
export const Greek: React.FC<{ children: React.ReactNode; size?: number; style?: React.CSSProperties }> = ({ children, size = 64, style }) => (
  <span lang="grc" style={{ fontFamily: DIDOT, fontSize: size, lineHeight: 1.35, color: C.paper, ...style }}>{children}</span>
);

/** Fictional-composite label for Eleni. */
export const fictional = "Eleni is a fictional composite";

/** fps helper for scenes */
export const useSec = () => {
  const { fps } = useVideoConfig();
  return (s: number) => Math.round(s * fps);
};
