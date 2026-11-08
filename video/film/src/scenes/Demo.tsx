// Scene "demo" — Eleni's walkthrough of the real, live product (s08_a–l).
// Real screen recordings (video/rec/record.cjs -> public/rec/*.mp4 + actions.json) in a browser mockup, with a
// cinematic cursor and Screen-Studio-style zoom driven from the recording's own action log, glass callouts on the
// VO, the claude.ai MCP captures (public/claude/), and a terminal replaying real captured output.
import React from "react";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame } from "remotion";
import { Audio, Video } from "@remotion/media";
import { C, MONO, Stage, ease } from "../brand";
import { BOX_W, Browser, Callout, ClaudeShots, CursorArrow, Spotlight, Terminal, Viewport, WIN_X, CONTENT_Y, clampCam, toScreen } from "./demo/parts";
import { camAt, clipFile, cursorAt, pressAt, segAt, srcTime } from "./demo/rec";
import { EDIT } from "./demo/edit";
import term from "../../public/rec/term.json";

const Recording: React.FC = () => {
  const frame = useCurrentFrame();
  const seg = segAt(EDIT.segs, frame);
  if (!seg) return null;
  const t = srcTime(seg, frame);
  const cam = clampCam(camAt(EDIT.cams[seg.clip] ?? [], t));
  const spot = (EDIT.spots[seg.clip] ?? []).map((s) => ({ rect: s.rect, a: Math.min(ease(t, s.from, s.from + 0.35, 0, 1) as number, ease(t, s.to - 0.3, s.to, 1, 0) as number) })).find((s) => s.a > 0);
  const cur = cursorAt(seg.clip, t);
  const pr = pressAt(seg.clip, t);
  const sc = toScreen(cam, cur.x, cur.y);
  return (
    <>
      <Viewport cam={cam}>
        {EDIT.segs.map((s, i) => (
          <Sequence key={i} from={s.f0} durationInFrames={s.f1 - s.f0} premountFor={40} name={`${s.clip} ${s.s0.toFixed(1)}–${s.s1.toFixed(1)}s`}>
            <Video src={staticFile(clipFile(s.clip))} muted trimBefore={Math.round(s.s0 * 30)} playbackRate={((s.s1 - s.s0) * 30) / (s.f1 - s.f0)} style={{ width: 1920, height: 1080 }} />
          </Sequence>
        ))}
        {spot && <Spotlight rect={spot.rect} amount={spot.a} />}
      </Viewport>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <CursorArrow x={sc.x - WIN_X} y={sc.y - CONTENT_Y} press={pr.press} ripples={pr.ripples} scale={1.15 + 0.12 * cam.z} />
      </AbsoluteFill>
    </>
  );
};

export const Demo: React.FC = () => {
  const frame = useCurrentFrame();
  const seg = segAt(EDIT.segs, frame);
  const inClaude = frame >= EDIT.claude.from && frame < EDIT.claude.to;
  const url = inClaude ? "claude.ai" : seg?.url ?? EDIT.segs[0].url;
  return (
    <Stage glow="bl">
      <AbsoluteFill>
        <Browser url={url} enter={0} live={!inClaude && /workers\.dev/.test(url)}>
          {inClaude ? <ClaudeShots cues={EDIT.claude.cues} /> : <Recording />}
        </Browser>
        <Sequence from={EDIT.term.from} layout="none">
          <TermWindow />
        </Sequence>
        {EDIT.callouts.map((c, i) => <Callout key={i} {...c} />)}
        {EDIT.sounds.clicks.map((f, i) => (
          <Sequence key={`c${i}`} from={Math.max(0, f - 1)} durationInFrames={12} layout="none" name="sfx click">
            <Audio src={staticFile("sfx/click-soft.mp3")} volume={0.45} />
          </Sequence>
        ))}
        {EDIT.sounds.keys.map((f, i) => (
          <Sequence key={`k${i}`} from={f} durationInFrames={8} layout="none" name="sfx key">
            <Audio src={staticFile("sfx/key-press.mp3")} volume={0.18} />
          </Sequence>
        ))}
        {EDIT.notes.map((n, i) => (
          <div key={i} style={{ position: "absolute", left: WIN_X + 8, top: 14, fontFamily: MONO, fontSize: 18, color: C.dim, opacity: ease(frame, n.from, n.from + 12, 0, 0.9) * ease(frame, n.to, n.to + 10, 1, 0) }}>{n.text}</div>
        ))}
      </AbsoluteFill>
    </Stage>
  );
};

const TermWindow: React.FC = () => {
  const frame = useCurrentFrame();
  const k = ease(frame, 0, 22, 0, 1);
  const b = EDIT.term.blocks;
  return (
    <Terminal
      title="zsh — Pharmakon"
      blocks={[
        { cmd: term.curl.cmd, out: term.curl.out, at: b[0], cps: 3.2 },
        { cmd: term.pytest.cmd, out: term.pytest.out, at: b[1], cps: 2.4 },
      ]}
      style={{ left: WIN_X + BOX_W - 980 + (1 - k) * 120, top: 268, width: 1020, height: 580, opacity: k, transform: `rotateY(${(1 - k) * -8}deg)` }}
      fontSize={17}
    />
  );
};
