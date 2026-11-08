// The walkthrough edit: which recording plays when (time map), where the camera looks, what is spotlit, and the
// callouts — all keyed to the VO (scene("demo") line starts + whisper word times noted inline as @frame).
// The recordings were captured on a schedule matched to these words (video/rec/record.cjs), so most pieces play 1:1.
import { scene } from "../../timing";
import { type CamKey, type Piece, act, clipUrl, frameRect, fx, mk, segments, soundCues } from "./rec";
import type { Cam, ShotCue } from "./parts";
import manifest from "../../../public/claude/manifest.json";

const SITE = "pharmakon.adoranto737.workers.dev";
const D = scene("demo");
const L = (id: string) => D.lines.find((l) => l.id === `s08_${id}`)!.from;

type R = { x: number; y: number; w: number; h: number };
/** frame a rect with its top `top` px (viewport) below the top of the view */
const topCam = (r: R, z: number, top = 60, dx = 0): Cam => ({ z, x: r.x + r.w / 2 + dx, y: r.y - top / z + 540 / z });
const k = (t: number, c: Cam, d = 0.9): CamKey => ({ t, d, c });
const WIDE: Cam = { z: 1, x: 960, y: 540 };

// ---------------------------------------------------------------- time map (scene frame -> clip seconds)
const leadsBack = mk("leads", "back");
const T_CLAUDE = [L("i") + 66, L("l") - 101] as const; // 2602 .. 3360
const PIECES: Piece[] = [
  { clip: "explorer", url: SITE, anchors: [[0, 0], [1212, 40.4]] },
  { clip: "time", url: `${SITE}/#time`, anchors: [[1212, 0], [L("f"), (L("f") - 1212) / 30]] },
  {
    clip: "leads", url: `${SITE}/#leads`,
    // 1:1 except: the toxic-tag beat held in slow motion (it was only on screen 0.4 s), and the static hold before
    // "She opens one" (@2181) tightened
    anchors: [[L("f"), 0], [1610, mk("leads", "toxtag")], [1640, 4.5], [1668, 4.95], [1723, act("leads", "click", 1).t], [1950, act("leads", "click", 1).t + 227 / 30], [2160, 22.4],
      [2160 + Math.round((mk("leads", "pubmed_click") + 0.3 - 22.4) * 30), mk("leads", "pubmed_click") + 0.3]],
  },
  { clip: "pubmed", url: clipUrl("pubmed").replace(/^https:\/\//, ""), anchors: [[2320, 0.05], [2368, 1.65]] },
  { clip: "leads", url: `${SITE}/#leads`, anchors: [[2368, leadsBack], [T_CLAUDE[0], leadsBack + (T_CLAUDE[0] - 2368) / 30]] },
  { clip: "use", url: `${SITE}/#use`, anchors: [[T_CLAUDE[1], 0], [3445, (3445 - T_CLAUDE[1]) / 30]] },
  { clip: "github", url: "github.com/LSUDOKO/Pharmakon", anchors: [[3445, 0], [D.duration, (D.duration - 3445) / 30]] },
];

// ---------------------------------------------------------------- cameras (clip seconds)
const explorerCam = (): CamKey[] => {
  const search = act("explorer", "click", 0);
  const pass = fx("explorer", "passage"), probs = fx("explorer", "probabilities"), cand = fx("explorer", "candidate");
  const morph = fx("explorer", "description match"), eras = fx("explorer", "eras-table"), galen = fx("explorer", "galen"), vill = fx("explorer", "villages");
  return [
    k(0, WIDE),
    k(4.3, { z: 1.55, x: search.x! + 360, y: search.y! + 170 }, 1.1),
    k(8.5, { z: 1.3, x: 900, y: 560 }, 1.0),
    k(9.9, topCam(pass, 1.75, 40, 60), 1.0),
    k(17.0, frameRect(probs, 2.05, -120), 1.0),
    k(26.3, { z: 1.2, x: 1100, y: 560 }, 0.6),
    k(27.6, topCam(cand, 1.95, 60, -40), 0.9),
    k(33.7, frameRect(morph, 2.2, -60), 0.8),
    k(35.0, topCam(eras, 1.45, 70), 0.9),
    k(36.9, topCam(galen, 1.45, 60), 0.8),
    k(38.6, frameRect(vill, 1.7, 60), 0.8),
  ];
};
const timeCam = (): CamKey[] => {
  const al = fx("time", "alluvial"), nul = fx("time", "permutation");
  const cols = (act("time", "info", 0) as unknown as { columns: Record<string, { x: number; y: number; width: number } | null> }).columns;
  const cx = (c: string, d: number) => (cols[c] ? cols[c]!.x + cols[c]!.width / 2 : d);
  const cy = al.y + al.h * 0.55;
  return [
    k(0, { z: 1.25, x: al.x + al.w * 0.6, y: cy }),
    k(1.0, { z: 1.7, x: cx("dio", 700), y: cy }, 0.8),
    k(1.9, { z: 1.7, x: cx("gal", 860), y: cy }, 0.8),
    k(2.7, { z: 1.7, x: cx("john", 1000), y: cy }, 0.8),
    k(4.0, { z: 1.7, x: cx("mod", 1150), y: cy }, 0.8),
    k(5.1, { z: 1.25, x: al.x + al.w * 0.6, y: cy }, 0.7),
    k(6.4, frameRect(nul, 1.85, -40), 0.9),
  ];
};
const leadsCam = (): CamKey[] => {
  let tox: R | null = null;
  try { tox = fx("leads", "tox tag"); } catch { tox = null; }
  const tools = fx("leads", "tools"), card = fx("leads", "card"), meters = fx("leads", "meters"), tag = fx("leads", "path tag");
  const dlg = fx("leads", "dialog"), nop = fx("leads", "no paper"), q = fx("leads", "query"), path = fx("leads", "path"), csv = fx("leads", "csv");
  const b = leadsBack;
  return [
    k(0, WIDE),
    k(1.2, { z: 1.7, x: tools.x + tools.w * 0.55, y: tools.y + 170 }, 1.0),
    ...(tox ? [k(mk("leads", "toxtag"), frameRect(tox, 2.0, 60), 0.5)] : []),
    k(mk("leads", "hide") - 0.5, { z: 1.7, x: tools.x + tools.w * 0.55, y: tools.y + 170 }, 0.5),
    k(5.5, { z: 1.7, x: tools.x + tools.w * 0.3, y: tools.y + 170 }, 0.8),
    k(7.4, topCam(card, 1.25, 30, 380), 1.1),
    k(10.9, frameRect(meters, 2.1, -40), 0.9),
    k(13.4, frameRect(tag, 2.3, -40), 0.8),
    k(18.5, topCam(card, 1.45, 60, 180), 1.2),
    k(23.4, frameRect(dlg, 1.3, -40), 0.8),
    k(24.0, frameRect(nop, 1.8, -30), 0.8),
    k(25.7, frameRect(q, 1.75, -40), 0.7),
    k(b, frameRect(path, 1.8, -60), 0.01),
    k(b + 3.3, { z: 1.15, x: 960, y: 560 }, 0.7),
    k(b + 4.7, frameRect(csv, 1.7, -60), 0.9),
  ];
};
const pubmedCam = (): CamKey[] => {
  let r: R | null = null;
  try { r = fx("pubmed", "no results"); } catch { r = null; }
  return r ? [k(0, { z: 1.15, x: r.x + r.w / 2, y: r.y + 140 }), k(0.25, frameRect(r, 1.75, -40), 0.9)] : [k(0, WIDE)];
};
const useCam = (): CamKey[] => {
  const m = fx("use", "mcp command");
  return [k(0, { z: 1.2, x: m.x + m.w / 2 + 200, y: m.y + 60 }), k(0.4, frameRect(m, 1.9, -40), 1.0)];
};
const githubCam = (): CamKey[] => [k(0, { z: 1.12, x: 960, y: 500 }), k(2.3, { z: 1.0, x: 960, y: 540 }, 1.2), k(6.4, { z: 1.25, x: 960, y: 520 }, 1.4)];

// ---------------------------------------------------------------- claude.ai (s08_j @2690, s08_k @3144)
// 01-04 are 1568x722, 05-09 950x879 (public/claude/manifest.json). focus = fraction of the image.
const CUE: [string, number, number, [number, number], number][] = [
  ["01.jpg", T_CLAUDE[0], 2700, [0.5, 0.47], 1.9], //   connector added
  ["02.jpg", 2700, 2830, [0.47, 0.4], 1.6], //            six tools ("MCP server" @2791)
  ["03.jpg", 2830, 3030, [0.5, 0.47], 2.1], //            the question ("she simply asks" @2850)
  ["04.jpg", 3030, 3146, [0.55, 0.3], 2.0], //            first tool call running
  ["05.jpg", 3146, 3200, [0.27, 0.62], 1.55], //          tool-call rows ("calls Pharmakon's tools" @3150)
  ["06.jpg", 3200, 3266, [0.42, 0.76], 1.85], //          the JSON, disclaimer first
  ["08.jpg", 3266, 3312, [0.42, 0.42], 1.45], //          P(species) + 90% intervals, toxicity
  ["09.jpg", 3312, T_CLAUDE[1], [0.45, 0.55], 1.35], //   shortlist + PubChem sources ("straight from our data")
];
const SIZE = (f: string) => (Number(f.slice(0, 2)) <= 4 ? { w: 1568, h: 722 } : { w: 950, h: 879 });
const CUES: ShotCue[] = CUE.map(([file, from, to, focus, zoom]) => ({ file, ...SIZE(file), from, to, focus, zoom }));
const CAPTIONS = CUES.map((c) => ({ text: `claude.ai · ${(manifest as { file: string; caption: string }[]).find((m) => m.file === c.file)?.caption ?? ""}`, from: c.from, to: c.to - 6 }));

// ---------------------------------------------------------------- spotlights (clip seconds, viewport rects)
type Spot = { from: number; to: number; rect: R };
const spot = (from: number, to: number, rect: R): Spot => ({ from, to, rect });

// ---------------------------------------------------------------- callouts (scene frames, output px)
export type CalloutSpec = { text: string; from: number; to: number; x: number; y: number; align?: "left" | "center" | "right"; warn?: boolean };

export const EDIT = (() => {
  const segs = segments(PIECES);
  const b = leadsBack;
  return {
    segs,
    sounds: soundCues(segs),
    end: D.duration,
    claude: { from: T_CLAUDE[0], to: T_CLAUDE[1], cues: CUES },
    cams: { explorer: explorerCam(), time: timeCam(), leads: leadsCam(), pubmed: pubmedCam(), use: useCam(), github: githubCam() } as Record<string, CamKey[]>,
    spots: {
      explorer: [spot(10.3, 16.9, fx("explorer", "passage")), spot(17.4, 26.2, fx("explorer", "probabilities")), spot(34.0, 35.0, fx("explorer", "description match")), spot(35.6, 36.9, fx("explorer", "skin row"))],
      time: [spot(6.9, 9.3, fx("time", "observed"))],
      leads: [...(() => { try { return [spot(mk("leads", "toxtag") + 0.4, mk("leads", "hide") - 0.45, fx("leads", "tox tag"))]; } catch { return []; } })(), spot(mk("leads", "hide"), mk("leads", "cond"), fx("leads", "toxicity toggle")), spot(13.8, 18.3, fx("leads", "path tag")), spot(24.1, 25.7, fx("leads", "no paper")), spot(26.0, 27.6, fx("leads", "query")), spot(b + 0.15, b + 3.2, fx("leads", "path"))],
      pubmed: (() => { try { return [spot(0.3, 1.7, fx("pubmed", "no results"))]; } catch { return []; } })(),
    } as Record<string, Spot[]>,
    callouts: [
      { text: "exact Greek words", from: 335, to: 445, x: 1180, y: 430 },
      { text: "90% interval", from: 650, to: 712, x: 1210, y: 250 },
      { text: "doubt kept, not hidden", from: 716, to: 800, x: 1150, y: 250 },
      { text: "survived 2,000 years", from: 1412, to: 1476, x: 1150, y: 220 },
      { text: "toxicity flagged", from: 1598, to: 1672, x: 1130, y: 470, warn: true },
      { text: "compound → target → disease", from: 1912, to: 2060, x: 960, y: 230, align: "center" },
      { text: "no paper yet", from: 2216, to: 2300, x: 1180, y: 230 },
      { text: "live MCP tool call", from: 3204, to: 3264, x: 1700, y: 170, align: "right" },
      { text: "same data, any AI", from: 3300, to: 3438, x: 1700, y: 760, align: "right" },
    ] as CalloutSpec[],
    notes: [
      { text: "live site · recorded 8 Nov 2026 · real data", from: 20, to: 1180 },
      { text: "research hypotheses only — not medical advice", from: L("f"), to: T_CLAUDE[0] - 10 },
      ...CAPTIONS,
    ],
    term: { from: L("l") + 30, blocks: [8, 112] as [number, number] },
  };
})();
