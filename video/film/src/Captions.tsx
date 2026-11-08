// Burned-in captions: Outfit 500, max 2 lines, bottom-centre on a soft black gradient, active word in verdigris-hi.
// Word timing is proportional to characters inside each VO line (text = the exact script, so spelling is right).
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, DIDOT, OUTFIT } from "./brand";
import { SCENES } from "./timing";

type Word = { w: string; s: number; e: number };
type Group = { s: number; e: number; words: Word[] };

const GREEK = /[Ͱ-Ͽἀ-῿]/;

const build = (): Group[] => {
  const groups: Group[] = [];
  for (const sc of SCENES) {
    for (const l of sc.lines) {
      if (l.id === "s02_a") continue; // the title tagline is already on screen as type
      const start = sc.start + l.from + 4; // a few frames of breath before the first word
      const speak = Math.max(10, l.dur - 10);
      const words = l.text.split(" ");
      const weights = words.map((w) => w.length + 2);
      const total = weights.reduce((a, b) => a + b, 0);
      let acc = 0;
      const timed: Word[] = l.words
        ? l.words.map((w) => ({ w: w.w, s: sc.start + l.from + w.s * 30, e: sc.start + l.from + w.e * 30 })) // presenter: real word timing
        : words.map((w, i) => {
            const s = start + (acc / total) * speak;
            acc += weights[i];
            return { w, s, e: start + (acc / total) * speak };
          });
      // chunk into caption groups: ≤ 9 words or ≤ 56 chars, prefer breaking after punctuation
      let cur: Word[] = [];
      const flush = () => {
        if (cur.length) groups.push({ s: cur[0].s, e: cur[cur.length - 1].e, words: cur });
        cur = [];
      };
      timed.forEach((tw) => {
        cur.push(tw);
        const chars = cur.map((x) => x.w).join(" ").length;
        if (cur.length >= 9 || chars >= 56 || (/[.?!:]$/.test(tw.w) && cur.length >= 3) || (/[,;]$/.test(tw.w) && chars >= 30)) flush();
      });
      flush();
    }
  }
  // hold each group until the next starts (max 0.6 s) so captions don't flicker
  groups.forEach((g, i) => {
    const next = groups[i + 1];
    g.e = Math.min(next ? next.s : g.e + 18, g.e + 18);
  });
  return groups;
};

const GROUPS = build();

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const g = GROUPS.find((x) => frame >= x.s && frame < x.e);
  if (!g) return null;
  const fadeIn = Math.min(1, (frame - g.s) / 4);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 230, background: "linear-gradient(180deg, transparent, rgba(0,0,0,.72) 55%, rgba(0,0,0,.85))" }} />
      <div
        style={{
          position: "relative", marginBottom: 74, maxWidth: 1380, textAlign: "center", fontFamily: OUTFIT, fontWeight: 500, fontSize: 42,
          lineHeight: 1.28, letterSpacing: "-0.01em", color: C.paper, opacity: fadeIn, textShadow: "0 2px 14px rgba(0,0,0,.85)",
        }}
      >
        {g.words.map((w, i) => {
          const active = frame >= w.s && frame < w.e;
          const said = frame >= w.e;
          return (
            <span key={i} style={{ fontFamily: GREEK.test(w.w) ? DIDOT : OUTFIT, color: active ? C.hi : said ? C.paper : "rgba(236,238,231,.62)" }}>
              {w.w}
              {i < g.words.length - 1 ? " " : ""}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** SRT for the delivery (same groups as burned in). */
export const toSrt = (fps: number): string => {
  const ts = (f: number) => {
    const ms = Math.round((f / fps) * 1000);
    const h = Math.floor(ms / 3600000), m = Math.floor((ms % 3600000) / 60000), s = Math.floor((ms % 60000) / 1000), r = ms % 1000;
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(r).padStart(3, "0")}`;
  };
  return GROUPS.map((g, i) => `${i + 1}\n${ts(g.s)} --> ${ts(g.e)}\n${g.words.map((w) => w.w).join(" ")}\n`).join("\n");
};
