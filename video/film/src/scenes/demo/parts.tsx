// Visual parts of the walkthrough: browser mockup, cinematic cursor, callout pill, spotlight, terminal, claude.ai shots.
import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { C, EASE_IN, EXPO, Glass, MONO, ease } from "../../brand";

// Mockup geometry (output px). Content shows the 1920x1080 page viewport scaled to BOX_W x BOX_H.
export const BOX_W = 1600;
export const BOX_H = 900;
export const BAR_H = 46;
export const WIN_X = (1920 - BOX_W) / 2;
export const WIN_Y = 52;
export const CONTENT_Y = WIN_Y + BAR_H;
export const BASE = BOX_W / 1920;

export type Cam = { z: number; x: number; y: number };

/** Clamp a camera so the visible window stays inside the 1920x1080 page viewport. */
export const clampCam = (c: Cam): Cam => {
  const hw = 960 / c.z, hh = 540 / c.z;
  return { z: c.z, x: Math.min(1920 - hw, Math.max(hw, c.x)), y: Math.min(1080 - hh, Math.max(hh, c.y)) };
};

/** viewport px -> output px, for a camera */
export const toScreen = (c: Cam, x: number, y: number) => {
  const s = BASE * c.z;
  return { x: WIN_X + (x - (c.x - 960 / c.z)) * s, y: CONTENT_Y + (y - (c.y - 540 / c.z)) * s };
};

export const Browser: React.FC<{ url: string; children: React.ReactNode; enter?: number; style?: React.CSSProperties; live?: boolean }> = ({ url, children, enter = 0, style, live }) => {
  const frame = useCurrentFrame();
  const k = ease(frame, enter, enter + 40, 0, 1);
  const drift = Math.sin(frame / 70) * 2;
  return (
    <AbsoluteFill style={{ perspective: 2200, ...style }}>
      {/* soft verdigris glow behind the window */}
      <div style={{ position: "absolute", left: WIN_X - 120, top: WIN_Y + 80, width: BOX_W + 240, height: BOX_H, borderRadius: 400, background: "radial-gradient(ellipse at center, rgba(23,116,79,.32), transparent 65%)", filter: "blur(40px)", opacity: 0.5 + 0.5 * k }} />
      <div
        style={{
          position: "absolute", left: WIN_X, top: WIN_Y, width: BOX_W, height: BOX_H + BAR_H, borderRadius: 20, overflow: "hidden",
          background: C.card, border: `1px solid ${C.rule}`,
          boxShadow: "0 50px 120px rgba(0,0,0,.85), 0 0 0 1px rgba(184,230,204,.06), 0 0 90px rgba(23,116,79,.22)",
          transform: `translateY(${(1 - k) * 40 + drift}px) rotateX(${(1 - k) * 12}deg) scale(${0.95 + 0.05 * k})`, transformOrigin: "50% 100%",
        }}
      >
        <div style={{ height: BAR_H, display: "flex", alignItems: "center", padding: "0 20px", gap: 9, borderBottom: `1px solid ${C.rule}`, background: "#050806" }}>
          {[0, 1, 2].map((i) => <span key={i} style={{ width: 12, height: 12, borderRadius: 99, background: C.rule, border: `1px solid #2a3a31` }} />)}
          <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 22px", borderRadius: 999, background: "rgba(255,255,255,.04)", border: `1px solid ${C.rule}`, fontFamily: MONO, fontSize: 17, color: C.dim, maxWidth: 1000, whiteSpace: "nowrap", overflow: "hidden" }}>
              <svg width="12" height="14" viewBox="0 0 12 14"><rect x="1" y="6" width="10" height="7" rx="2" fill={C.dim} /><path d="M3 6V4a3 3 0 0 1 6 0v2" stroke={C.dim} strokeWidth="1.6" fill="none" /></svg>
              {url}
            </div>
          </div>
          <div style={{ width: 66, display: "flex", justifyContent: "flex-end", fontFamily: MONO, fontSize: 13, color: C.hi, letterSpacing: "0.12em", opacity: live ? 0.9 : 0 }}>
            <span style={{ width: 7, height: 7, borderRadius: 9, background: C.hi, marginRight: 7, marginTop: 4, opacity: 0.6 + 0.4 * Math.sin(frame / 8) }} />LIVE
          </div>
        </div>
        <div style={{ position: "relative", width: BOX_W, height: BOX_H, overflow: "hidden", background: C.ink }}>{children}</div>
      </div>
    </AbsoluteFill>
  );
};

/** The page viewport (1920x1080 css px) under a camera, rendered inside the mockup content box. */
export const Viewport: React.FC<{ cam: Cam; children: React.ReactNode }> = ({ cam, children }) => {
  const s = BASE * cam.z;
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transformOrigin: "0 0", transform: `scale(${s}) translate(${-(cam.x - 960 / cam.z)}px, ${-(cam.y - 540 / cam.z)}px)` }}>
      {children}
    </div>
  );
};

/** Dim everything but one rect (viewport px). Lives inside <Viewport>. */
export const Spotlight: React.FC<{ rect: { x: number; y: number; w: number; h: number }; amount: number }> = ({ rect, amount }) =>
  amount <= 0.001 ? null : (
    <div style={{ position: "absolute", left: rect.x, top: rect.y, width: rect.w, height: rect.h, borderRadius: 18, boxShadow: `0 0 0 4000px rgba(0,0,0,${0.6 * amount})`, outline: `1.5px solid rgba(61,187,130,${0.55 * amount})`, outlineOffset: 2 }} />
  );

/** Cursor arrow (paper, 1px verdigris outline) + click ripple, drawn in output px. */
export const CursorArrow: React.FC<{ x: number; y: number; press: number; ripples: number[]; scale?: number; opacity?: number }> = ({ x, y, press, ripples, scale = 1.35, opacity = 1 }) => (
  <>
    {ripples.map((age, i) => {
      const k = Math.min(1, age / 0.55);
      const r = 8 + 40 * EXPO(k);
      return <div key={i} style={{ position: "absolute", left: x - r, top: y - r, width: 2 * r, height: 2 * r, borderRadius: 999, border: `2.5px solid ${C.hi}`, opacity: (1 - k) * 0.95, boxShadow: `0 0 18px rgba(61,187,130,${0.5 * (1 - k)})` }} />;
    })}
    <svg
      width={34} height={44} viewBox="-2 -2 22 28"
      style={{ position: "absolute", left: x - 2 * scale, top: y - 2 * scale, transform: `scale(${scale * (1 - 0.15 * press)})`, transformOrigin: "2px 2px", filter: "drop-shadow(0 4px 8px rgba(0,0,0,.55))", opacity }}
    >
      <path d="M0 0 L0 19.5 L5 15 L8.6 23.2 L12 21.7 L8.5 13.6 L15 13.6 Z" fill={C.paper} stroke={C.verdigris} strokeWidth={1} strokeLinejoin="round" />
    </svg>
  </>
);

/** Glass callout pill with a verdigris-hi dot; 2-5 words. */
export const Callout: React.FC<{ text: string; from: number; to: number; x: number; y: number; align?: "left" | "center" | "right"; warn?: boolean }> = ({ text, from, to, x, y, align = "left", warn }) => {
  const frame = useCurrentFrame();
  if (frame < from - 1 || frame > to + 10) return null;
  const i = ease(frame, from, from + 16, 0, 1);
  const o = frame > to ? ease(frame, to, to + 9, 1, 0, EASE_IN) : 1;
  const tx = align === "center" ? "-50%" : align === "right" ? "-100%" : "0%";
  return (
    <div style={{ position: "absolute", left: x, top: y, transform: `translate(${tx}, ${(1 - i) * 18}px) scale(${0.92 + 0.08 * i})`, opacity: i * o, filter: `blur(${(1 - i) * 8}px)`, transformOrigin: "left center" }}>
      <Glass style={{ fontSize: 32, padding: "14px 28px", background: "linear-gradient(180deg, rgba(11,18,14,.86), rgba(11,18,14,.72))", border: `1px solid ${warn ? "rgba(255,90,95,.55)" : "rgba(61,187,130,.45)"}` }}>
        <span style={{ width: 11, height: 11, borderRadius: 99, background: warn ? C.warn : C.hi, boxShadow: `0 0 14px ${warn ? C.warn : C.hi}` }} />
        <span style={{ whiteSpace: "nowrap", letterSpacing: "-0.01em" }}>{text}</span>
      </Glass>
    </div>
  );
};

// ---------------------------------------------------------------- terminal
type TermBlock = { cmd: string; out: string[]; at: number; cps?: number };

const colorJson = (l: string): React.ReactNode => {
  const m = l.match(/^(\s*)"([^"]+)":\s?(.*)$/);
  if (!m) return <span style={{ color: C.dim }}>{l}</span>;
  const v = m[3];
  const vc = /^"/.test(v) ? C.paper : /^(true|false|null)/.test(v) ? C.lichen : /^[\d.-]/.test(v) ? C.hi : C.dim;
  return (
    <>
      {m[1]}<span style={{ color: C.lichen }}>"{m[2]}"</span><span style={{ color: C.dim }}>: </span><span style={{ color: vc }}>{v}</span>
    </>
  );
};

/** Animated terminal: types each command, then prints its real captured output line by line. */
export const Terminal: React.FC<{ blocks: TermBlock[]; title: string; style?: React.CSSProperties; fontSize?: number }> = ({ blocks, title, style, fontSize = 19 }) => {
  const frame = useCurrentFrame();
  const rows: React.ReactNode[] = [];
  blocks.forEach((b, bi) => {
    if (frame < b.at) return;
    const cps = b.cps ?? 2.2; // chars per frame
    const typed = Math.min(b.cmd.length, Math.floor((frame - b.at) * cps));
    const done = typed >= b.cmd.length;
    const tDone = b.at + Math.ceil(b.cmd.length / cps) + 6;
    rows.push(
      <div key={`c${bi}`} style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
        <span style={{ color: C.hi }}>❯ </span>
        <span style={{ color: C.paper }}>{b.cmd.slice(0, typed)}</span>
        {(!done || frame < tDone) && <span style={{ display: "inline-block", width: fontSize * 0.55, height: fontSize * 1.05, background: C.hi, verticalAlign: "text-bottom", opacity: Math.floor(frame / 8) % 2 ? 0.25 : 0.9 }} />}
      </div>,
    );
    const shown = frame < tDone ? 0 : Math.min(b.out.length, Math.floor((frame - tDone) * 1.6) + 1);
    b.out.slice(0, shown).forEach((l, li) => {
      const big = /passed/.test(l);
      rows.push(
        <div key={`o${bi}-${li}`} style={{ whiteSpace: "pre", color: big ? C.hi : C.dim, fontWeight: big ? 600 : 400 }}>
          {big ? l : b.out[0] === "{" ? colorJson(l) : l}
        </div>,
      );
    });
    if (bi < blocks.length - 1 && frame >= tDone) rows.push(<div key={`s${bi}`} style={{ height: fontSize * 0.7 }} />);
  });
  return (
    <div style={{ position: "absolute", borderRadius: 16, overflow: "hidden", background: "rgba(5,8,6,.96)", border: `1px solid ${C.rule}`, boxShadow: "0 40px 100px rgba(0,0,0,.85), 0 0 70px rgba(23,116,79,.25)", ...style }}>
      <div style={{ height: 40, display: "flex", alignItems: "center", gap: 8, padding: "0 16px", borderBottom: `1px solid ${C.rule}`, fontFamily: MONO, fontSize: 14, color: C.dim }}>
        {[0, 1, 2].map((i) => <span key={i} style={{ width: 11, height: 11, borderRadius: 99, background: C.rule }} />)}
        <span style={{ marginLeft: 12 }}>{title}</span>
      </div>
      <div style={{ padding: "16px 22px", fontFamily: MONO, fontSize, lineHeight: 1.42, display: "flex", flexDirection: "column", justifyContent: "flex-end", height: "calc(100% - 40px)", overflow: "hidden" }}>{rows}</div>
    </div>
  );
};

// ---------------------------------------------------------------- claude.ai screenshots
/** One claude.ai capture on a schedule: `from`..`to` scene frames, Ken-Burns from the whole image to `focus` at `zoom`. */
export type ShotCue = { file: string; w: number; h: number; from: number; to: number; focus: [number, number]; zoom: number };

/** Real claude.ai screenshots, fitted (contain, never stretched) in the mockup, crossfading, slow push to each focus. */
export const ClaudeShots: React.FC<{ cues: ShotCue[] }> = ({ cues }) => {
  const frame = useCurrentFrame();
  const layer = (c: ShotCue, opacity: number) => {
    const fit = Math.min(BOX_W / c.w, BOX_H / c.h);
    const dw = c.w * fit, dh = c.h * fit;
    const e = EXPO(Math.max(0, Math.min(1, (frame - c.from) / Math.max(1, c.to - c.from))));
    const p = 0.35 + 0.65 * e; // already moving at the cut, settles on the focus
    const z = 1 + (c.zoom - 1) * p;
    const cx = dw / 2 + (c.focus[0] * dw - dw / 2) * p, cy = dh / 2 + (c.focus[1] * dh - dh / 2) * p;
    return (
      <div key={c.file} style={{ position: "absolute", left: 0, top: 0, width: dw, height: dh, transformOrigin: "0 0", transform: `translate(${BOX_W / 2 - cx * z}px, ${BOX_H / 2 - cy * z}px) scale(${z})`, opacity }}>
        <Img src={staticFile(`claude/${c.file}`)} style={{ width: dw, height: dh, display: "block" }} />
      </div>
    );
  };
  const i = cues.findIndex((c) => frame >= c.from && frame < c.to);
  if (i < 0) return null;
  const fade = i > 0 ? (ease(frame, cues[i].from, cues[i].from + 10, 0, 1) as number) : 1;
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      {i > 0 && fade < 1 && layer(cues[i - 1], 1)}
      {layer(cues[i], fade)}
    </AbsoluteFill>
  );
};
