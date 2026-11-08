// Presenter takes (video/make_presenter.py): Arpit on camera, inside the brand.
// Phone footage (854×480, bright room) is shown in a graded card, never full frame: cropped to the face, pulled
// toward black and verdigris, grained, with a verdigris rule drawing in. Two uses:
//   • PresenterScene — the "intro" and "handoff" sections, card right + kinetic type left;
//   • SplitFrame — inside a narrated scene, while his line plays the scene shrinks to a screen on the left
//     and his card stands on the right; the scene's own animation keeps running on his real word timing.
import React from "react";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Video } from "@remotion/media";
import { C, EXPO, Grain, MONO, OUTFIT, SAFE, Stage, Words, ease } from "./brand";
import { Line, scene } from "./timing";

const SRC_W = 1708; // upscaled source (2× the 854×480 phone file)
const SRC_H = 960;
const NAME = "Arpit";

/** Word start (scene-local frame) of the first word containing `phrase`. */
const wordAt = (l: Line, phrase: string) => {
  const w = l.words!.find((x) => x.w.toLowerCase().includes(phrase.toLowerCase()))!;
  return l.from + Math.round(w.s * 30);
};

/** The graded, cropped video card. `at` = card entrance frame; video plays from `videoAt` (local). */
export const PresenterCard: React.FC<{
  line: Line; videoAt: number; durationInFrames: number; at: number; w: number; h: number; tag?: boolean; style?: React.CSSProperties;
}> = ({ line, videoAt, durationInFrames, at, w, h, tag = true, style }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const v = line.video!;
  const k = h / SRC_H;
  const vw = SRC_W * k;
  const left = Math.min(0, Math.max(w - vw, w / 2 - v.cx * 2 * k));
  const inn = spring({ frame: f - at, fps, config: { stiffness: 140, damping: 18 } });
  const reveal = ease(f, at, at + 22, 100, 0) as number; // clip opens upward, like the site's band
  const rule = ease(f, at + 8, at + 34, 0, 1) as number;
  return (
    <div style={{ position: "absolute", width: w, height: h + (tag ? 70 : 0), ...style }}>
      <div
        style={{
          position: "absolute", left: 0, top: 0, width: w, height: h, borderRadius: 26, overflow: "hidden", background: C.card,
          boxShadow: "0 0 0 1px rgba(255,255,255,.07), 0 40px 120px rgba(0,0,0,.75)",
          clipPath: `inset(${reveal}% 0 0 0 round 26px)`, translate: `0px ${(1 - inn) * 40}px`, scale: `${0.97 + 0.03 * inn}`,
        }}
      >
        <Sequence from={videoAt} durationInFrames={durationInFrames} layout="none">
          <Video
            src={staticFile(v.src)}
            muted
            trimBefore={Math.round(v.from_s * 30)}
            style={{ position: "absolute", left, top: 0, width: vw, height: h, maxWidth: "none", filter: "saturate(.68) contrast(1.12) brightness(.82)" }}
          />
        </Sequence>
        {/* grade: wall pulled toward verdigris-grey, edges to black, a little paper grain */}
        <AbsoluteFill style={{ background: "#7FA693", mixBlendMode: "multiply", opacity: 0.55 }} />
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.30) 0%, transparent 30%, transparent 62%, rgba(0,0,0,.72) 100%)" }} />
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 38%, transparent 48%, rgba(0,0,0,.6) 100%)" }} />
        <Grain opacity={0.09} />
        {/* verdigris rule drawing across the top edge */}
        <div style={{ position: "absolute", left: 0, top: 0, height: 3, width: `${rule * 100}%`, background: C.hi }} />
        {/* live dot */}
        <div style={{ position: "absolute", left: 22, top: 22, display: "flex", alignItems: "center", gap: 10, opacity: rule }}>
          <div style={{ width: 10, height: 10, borderRadius: 5, background: C.hi, boxShadow: `0 0 12px ${C.hi}`, opacity: 0.6 + 0.4 * Math.sin(f / 6) }} />
          <span style={{ fontFamily: MONO, fontSize: 16, color: C.lichen, letterSpacing: "0.12em" }}>ON CAMERA</span>
        </div>
      </div>
      {tag && (
        <div style={{ position: "absolute", left: 4, top: h + 18, opacity: ease(f, at + 14, at + 30, 0, 1) as number, translate: `0px ${ease(f, at + 14, at + 30, 10, 0)}px` }}>
          <span style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 26, color: C.paper }}>{NAME}</span>
          <span style={{ fontFamily: MONO, fontSize: 16, color: C.dim, marginLeft: 14 }}>built Pharmakon</span>
        </div>
      )}
    </div>
  );
};

/** Full sections "intro" and "handoff". */
export const PresenterScene: React.FC<{ id: "intro" | "handoff" }> = ({ id }) => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const l = scene(id).lines[0];
  const W = 600;
  const H = 780;
  return (
    <Stage glow="tr">
      {/* faint folio behind the type, like the site hero */}
      <AbsoluteFill style={{ background: `repeating-linear-gradient(135deg, rgba(255,255,255,.035) 0 1px, transparent 1px 7px)`, opacity: 0.7 }} />
      <PresenterCard line={l} videoAt={0} durationInFrames={durationInFrames} at={0} w={W} h={H} tag={false} style={{ left: 1920 - SAFE - W, top: 92 }} />
      <div style={{ position: "absolute", left: SAFE, top: id === "intro" ? 250 : 360, width: 1920 - 2 * SAFE - W - 80 }}>
        {id === "intro" ? (
          <>
            <Words text={`Hi, I'm ${NAME}.`} at={l.from - 2} size={124} stagger={5} accent={[NAME]} />
            <div style={{ marginTop: 44, display: "flex", alignItems: "center", gap: 18, opacity: ease(f, wordAt(l, "B.Tech") - 6, wordAt(l, "B.Tech") + 10, 0, 1) as number }}>
              <div style={{ width: ease(f, wordAt(l, "B.Tech") - 6, wordAt(l, "B.Tech") + 16, 0, 40), height: 2, background: C.hi }} />
              <span style={{ fontFamily: MONO, fontSize: 30, color: C.lichen }}>B.Tech · Computer Science</span>
            </div>
            <div style={{ marginTop: 18, marginLeft: 58, fontFamily: OUTFIT, fontSize: 44, fontWeight: 500, color: C.paper, opacity: ease(f, wordAt(l, "National") - 4, wordAt(l, "National") + 12, 0, 1) as number }}>
              National Institute of Technology
            </div>
            <div style={{ marginTop: 6, marginLeft: 58, fontFamily: OUTFIT, fontSize: 44, fontWeight: 300, color: C.dim, opacity: ease(f, wordAt(l, "Hamirpur") - 4, wordAt(l, "Hamirpur") + 12, 0, 1) as number }}>
              Hamirpur, India
            </div>
            <div style={{ marginTop: 70, opacity: ease(f, wordAt(l, "Before") - 4, wordAt(l, "Before") + 12, 0, 1) as number }}>
              <Words text="Before the build — who it's for." at={wordAt(l, "Before") - 2} size={46} weight={400} color={C.dim} stagger={3} />
            </div>
          </>
        ) : (
          <Words text="Let me show you." at={l.from - 2} size={124} stagger={6} accent={["show"]} />
        )}
      </div>
    </Stage>
  );
};

/** Wrap a narrated scene: while one of its presenter lines plays, the scene becomes a screen on the left. */
export const SplitFrame: React.FC<{ sceneId: string; children: React.ReactNode }> = ({ sceneId, children }) => {
  const f = useCurrentFrame();
  const sc = scene(sceneId);
  // merge adjacent lines from the same take into one window
  const wins: { a: number; b: number; first: Line }[] = [];
  for (const l of sc.lines.filter((x) => x.video)) {
    const last = wins[wins.length - 1];
    if (last && last.first.video!.clip === l.video!.clip && l.from - last.b <= 2) last.b = l.from + l.dur;
    else wins.push({ a: l.from, b: l.from + l.dur, first: l });
  }
  if (!wins.length || sceneId === "intro" || sceneId === "handoff") return <>{children}</>;
  const p = Math.max(0, ...wins.map((w) => Math.min(ease(f, w.a - 14, w.a + 10, 0, 1) as number, 1 - (ease(f, w.b, w.b + 22, 0, 1) as number))));
  const S = 0.655;
  const s = 1 - (1 - S) * p;
  const x = 72 * p;
  const y = (1080 * (1 - S)) / 2 - 58;
  const CW = 470;
  const CH = 620;
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      {p > 0 && (
        <Stage glow="tr">
          <AbsoluteFill style={{ background: `repeating-linear-gradient(135deg, rgba(255,255,255,.03) 0 1px, transparent 1px 7px)` }} />
        </Stage>
      )}
      <AbsoluteFill
        style={{
          transformOrigin: "0 0", translate: `${x}px ${y * p}px`, scale: `${s}`, borderRadius: 30 * p, overflow: "hidden",
          boxShadow: p > 0 ? `0 0 0 ${2 * p}px rgba(255,255,255,.08), 0 50px 140px rgba(0,0,0,${0.8 * p})` : undefined,
        }}
      >
        {children}
      </AbsoluteFill>
      {wins.map((w, i) =>
        f >= w.a - 70 && f < w.b + 24 ? (
          <div key={i} style={{ opacity: 1 - (ease(f, w.b, w.b + 18, 0, 1) as number) }}>
            <PresenterCard line={w.first} videoAt={w.a} durationInFrames={w.b - w.a + 24} at={w.a - 8} w={CW} h={CH}
              style={{ left: 1920 - 72 - CW, top: y + 6, translate: `${(1 - p) * 80}px 0px` }} />
          </div>
        ) : null,
      )}
    </AbsoluteFill>
  );
};

void EXPO;
