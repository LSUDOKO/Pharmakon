// The full film: scenes back to back (from timing.ts), every VO line at its absolute frame, the score ducked
// under the voice, torn-paper wipes on cuts (with paper-tear SFX), bass hits on the title rip and the end mark,
// and burned-in captions on top.
import React from "react";
import { AbsoluteFill, Sequence, interpolate, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { SCENES, TOTAL } from "./timing";
import { Captions } from "./Captions";
import { Wipe, WIPE_FRAMES } from "./Wipe";
import { Cold } from "./scenes/Cold";
import { Title } from "./scenes/Title";
import { Problem } from "./scenes/Problem";
import { Motivation } from "./scenes/Motivation";
import { Turn } from "./scenes/Turn";
import { Data } from "./scenes/Data";
import { Method } from "./scenes/Method";
import { Demo } from "./scenes/Demo";
import { Hood } from "./scenes/Hood";
import { Results } from "./scenes/Results";
import { Impact } from "./scenes/Impact";
import { Outro } from "./scenes/Outro";
import { PresenterScene, SplitFrame } from "./Presenter";

const Intro: React.FC = () => <PresenterScene id="intro" />;
const Handoff: React.FC = () => <PresenterScene id="handoff" />;

export const SCENE_COMPONENTS: Record<string, React.FC> = {
  cold: Cold, title: Title, intro: Intro, handoff: Handoff, problem: Problem, motivation: Motivation, turn: Turn, data: Data,
  method: Method, demo: Demo, hood: Hood, results: Results, impact: Impact, outro: Outro,
};

const FOLIOS = ["media/folio-iris.webp", "media/folio-glukurizon.webp", "media/folio-adianton.webp", "media/folio-drakontaia.webp", "media/folio-apsinthion.webp"];
// cuts that get a wipe (the cold → title cut is the title's own tear)
const CUTS = SCENES.slice(1).map((s) => s.start).filter((_, i) => SCENES[i + 1].id !== "title");

// voice intervals (absolute frames) for ducking
const VO = SCENES.flatMap((s) => s.lines.map((l) => [s.start + l.from, s.start + l.from + l.dur] as const));
const BED = 0.12; // music under the voice (≈ −18 dB)
const OPEN = 0.34; // music in the gaps
const musicVolume = (f: number) => {
  let d = Infinity;
  for (const [a, b] of VO) {
    if (f >= a - 6 && f <= b + 4) { d = 0; break; }
    d = Math.min(d, Math.abs(f - (a - 6)), Math.abs(f - (b + 4)));
  }
  const v = BED + (OPEN - BED) * Math.min(1, d / 18);
  const edges = interpolate(f, [0, 20, TOTAL - 75, TOTAL - 5], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return v * edges;
};

const title = SCENES.find((s) => s.id === "title")!;
const outro = SCENES.find((s) => s.id === "outro")!;

export const Film: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    {SCENES.map((s) => {
      const Comp = SCENE_COMPONENTS[s.id];
      return (
        <Sequence key={s.id} name={`scene: ${s.id}`} from={s.start} durationInFrames={s.duration}>
          <SplitFrame sceneId={s.id}>
            <Comp />
          </SplitFrame>
        </Sequence>
      );
    })}

    {CUTS.map((c, i) => (
      <Sequence key={`wipe${c}`} name={`wipe @${c}`} from={c - WIPE_FRAMES / 2} durationInFrames={WIPE_FRAMES}>
        <Wipe seed={i * 13 + 3} folio={FOLIOS[i % FOLIOS.length]} dir={i % 2 === 0 ? 1 : -1} />
      </Sequence>
    ))}

    <Captions />

    {/* ---------- audio ---------- */}
    <Audio src={staticFile("music/score.wav")} volume={(f) => musicVolume(f)} />
    {SCENES.flatMap((s) =>
      s.lines.map((l) => (
        <Sequence key={l.id} name={`vo: ${l.id}`} from={s.start + l.from} durationInFrames={l.dur + 2} layout="none">
          <Audio src={staticFile(`vo/${l.file}`)} volume={1} />
        </Sequence>
      )),
    )}
    {CUTS.map((c, i) => (
      <Sequence key={`tear${c}`} from={c - 9} durationInFrames={60} layout="none">
        <Audio src={staticFile(`sfx/tear-${(i % 3) + 1}.wav`)} volume={0.42} />
      </Sequence>
    ))}
    <Sequence from={title.start + 13} durationInFrames={70} layout="none">
      <Audio src={staticFile("sfx/tear-2.wav")} volume={0.6} />
    </Sequence>
    <Sequence from={title.start + 14} durationInFrames={120} layout="none">
      <Audio src={staticFile("sfx/impact-bass-1.mp3")} volume={0.55} />
    </Sequence>
    <Sequence from={outro.start + outro.lines[1].from} durationInFrames={120} layout="none">
      <Audio src={staticFile("sfx/impact-bass-2.mp3")} volume={0.5} />
    </Sequence>
  </AbsoluteFill>
);

/** One scene alone with its own VO, for previewing a scene in Studio. */
export const SceneSolo: React.FC<{ id: string }> = ({ id }) => {
  const s = SCENES.find((x) => x.id === id)!;
  const Comp = SCENE_COMPONENTS[id];
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <SplitFrame sceneId={id}>
        <Comp />
      </SplitFrame>
      {s.lines.map((l) => (
        <Sequence key={l.id} from={l.from} durationInFrames={l.dur + 2} layout="none">
          <Audio src={staticFile(`vo/${l.file}`)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
