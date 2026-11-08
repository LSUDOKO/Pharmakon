// The recording log (public/rec/actions.json, written by video/rec/record.cjs) and the maths that turns it into
// an edit: one piecewise-linear time map (scene frame -> clip seconds) drives the video, the camera and the cursor.
import data from "../../../public/rec/actions.json";
import type { Cam } from "./parts";

export type Act = {
  t: number; type: string; x?: number; y?: number; w?: number; h?: number; dur?: number;
  name?: string; label?: string; from?: number; to?: number; text?: string;
};
type ClipData = { file: string; duration: number; actions: Act[]; url: string };
const CLIPS = (data as unknown as { clips: Record<string, ClipData> }).clips;

export const hasClip = (c: string) => Boolean(CLIPS[c]);
export const clipFile = (c: string) => CLIPS[c].file;
export const clipDur = (c: string) => CLIPS[c].duration;
export const clipUrl = (c: string) => decodeURIComponent(CLIPS[c].url);

/** time (s) of a logged mark */
export const mk = (c: string, name: string): number => {
  const a = CLIPS[c]?.actions.find((x) => x.type === "mark" && x.name === name);
  if (!a) throw new Error(`no mark ${c}:${name}`);
  return a.t;
};
/** logged focus rect (viewport px) */
export const fx = (c: string, label: string, nth = 0): { x: number; y: number; w: number; h: number; t: number } => {
  const a = CLIPS[c]?.actions.filter((x) => x.type === "focus" && x.label === label)[nth];
  if (!a) throw new Error(`no focus ${c}:${label}#${nth}`);
  return { x: a.x!, y: a.y!, w: a.w!, h: a.h!, t: a.t };
};
/** n-th logged action of a type (e.g. the 3rd click) */
export const act = (c: string, type: string, nth = 0): Act => CLIPS[c].actions.filter((x) => x.type === type)[nth];

// ---------------------------------------------------------------- time map
/** A run of one clip: anchors are [sceneFrame, clipSeconds]; consecutive anchors play linearly. */
export type Piece = { clip: string; url: string; anchors: [number, number][] };
export type Seg = { clip: string; url: string; f0: number; f1: number; s0: number; s1: number };

export const segments = (pieces: Piece[]): Seg[] =>
  pieces.flatMap((p) => p.anchors.slice(1).map((a, i) => ({ clip: p.clip, url: p.url, f0: p.anchors[i][0], f1: a[0], s0: Math.round(p.anchors[i][1] * 30) / 30, s1: a[1] })));

export const segAt = (segs: Seg[], frame: number): Seg | null => segs.find((s) => frame >= s.f0 && frame < s.f1) ?? null;
export const srcTime = (s: Seg, frame: number) => s.s0 + ((frame - s.f0) / (s.f1 - s.f0)) * (s.s1 - s.s0);

// ---------------------------------------------------------------- camera
/** At clip time t, ease over d seconds to camera c. */
export type CamKey = { t: number; d: number; c: Cam };
const smooth = (p: number) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
export const camAt = (keys: CamKey[], t: number): Cam => {
  let cur: Cam = keys.length ? { ...keys[0].c } : { z: 1, x: 960, y: 540 };
  for (const k of keys) {
    if (t <= k.t) break;
    const e = smooth(Math.min(1, (t - k.t) / k.d));
    cur = { z: cur.z + (k.c.z - cur.z) * e, x: cur.x + (k.c.x - cur.x) * e, y: cur.y + (k.c.y - cur.y) * e };
  }
  return cur;
};
/** camera that frames a rect at zoom z, with the rect centre placed `lift` px (viewport) above the view centre */
export const frameRect = (r: { x: number; y: number; w: number; h: number }, z: number, lift = 0): Cam => ({ z, x: r.x + r.w / 2, y: r.y + r.h / 2 + lift / z });

// ---------------------------------------------------------------- cursor
const back = (k: number) => { const c1 = 1.25, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };

/** Cursor position at clip time t: curved (quadratic bezier) paths with a small overshoot and settle. */
export const cursorAt = (c: string, t: number) => {
  const acts = CLIPS[c].actions;
  let p = { x: 960, y: 600 };
  let n = 0;
  for (const a of acts) {
    if (a.type === "cursor") { p = { x: a.x!, y: a.y! }; continue; }
    if (a.type !== "move") continue;
    if (t < a.t) break;
    const dur = Math.max(0.05, a.dur ?? 0.5);
    const k = Math.min(1, (t - a.t) / dur);
    const q = { x: a.x!, y: a.y! };
    if (k < 1) {
      const dx = q.x - p.x, dy = q.y - p.y, len = Math.hypot(dx, dy) || 1;
      const bend = Math.min(70, len * 0.16) * (n % 2 ? 1 : -1);
      const m = { x: (p.x + q.x) / 2 - (dy / len) * bend, y: (p.y + q.y) / 2 + (dx / len) * bend };
      const e = back(k);
      const u = 1 - e;
      return { x: u * u * p.x + 2 * u * e * m.x + e * e * q.x, y: u * u * p.y + 2 * u * e * m.y + e * e * q.y };
    }
    p = q;
    n++;
  }
  // idle: a breath of drift so the cursor never looks frozen
  return { x: p.x + Math.sin(t * 1.3) * 1.2, y: p.y + Math.cos(t * 1.1) * 1.0 };
};

/** 0..1 press amount and click ripple ages (s) at clip time t */
export const pressAt = (c: string, t: number) => {
  const acts = CLIPS[c].actions;
  let press = 0;
  const ripples: number[] = [];
  let down: number | null = null;
  for (const a of acts) {
    if (a.t > t + 0.2) break;
    if (a.type === "click") {
      const d = t - a.t;
      if (d > -0.06 && d < 0.18) press = Math.max(press, d < 0 ? (d + 0.06) / 0.06 : d < 0.1 ? 1 : 1 - (d - 0.1) / 0.08);
      if (d >= 0 && d < 0.6) ripples.push(d);
    }
    if (a.type === "press" && a.t <= t) down = a.t;
    if (a.type === "release" && a.t <= t) { down = null; if (t - a.t < 0.6) ripples.push(t - a.t); }
  }
  if (down !== null) press = Math.min(1, (t - down) / 0.06);
  return { press, ripples };
};

/** scene frames of every click (and every 3rd typed key) that falls inside the edit */
export const soundCues = (segs: Seg[]) => {
  const clicks: number[] = [], keys: number[] = [];
  for (const s of segs) {
    const toF = (t: number) => Math.round(s.f0 + ((t - s.s0) / (s.s1 - s.s0)) * (s.f1 - s.f0));
    const inside = (t: number) => t >= s.s0 && t < s.s1;
    for (const a of CLIPS[s.clip].actions) {
      if ((a.type === "click" || a.type === "press") && inside(a.t)) clicks.push(toF(a.t));
      if (a.type === "type" && a.text) for (let i = 0; i < a.text.length; i += 3) { const t = a.t + (a.dur ?? 1) * (i / a.text.length); if (inside(t)) keys.push(toF(t)); }
    }
  }
  return { clicks, keys };
};
