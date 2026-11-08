// Scene "turn" — the chaos of the problem snaps into a clean five-step strip, one step per verb the VO names:
// Read · Identify · Trace · Test · Rank. Palette shifts from muted paper-dim to verdigris as the steps light.
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, DIDOT, EXPO, Glass, MONO, OUTFIT, Stage, Wordmark, ease } from "../brand";
import { Photo, Vial, cue, rnd } from "./coldproblem/kit";
import { ASPHODEL } from "./coldproblem/photos";

const ID = "turn";
const CW = 300; // card width
const CH = 372;
const TOP = 318;
const left = (i: number) => 150 + i * 330;
const TW = 260; // token box
const TH = 196;

const Token: React.FC<{ i: number }> = ({ i }) => {
  const box: React.CSSProperties = { width: TW, height: TH, borderRadius: 18, overflow: "hidden", position: "relative", background: C.card, border: `1px solid ${C.rule}` };
  if (i === 0)
    return (
      <div style={box}>
        <Img src={staticFile("media/folio-apsinthion.webp")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 20%" }} />
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "26px 14px 8px", background: "linear-gradient(180deg, transparent, rgba(0,0,0,.85))" }}>
          <span lang="grc" style={{ fontFamily: DIDOT, fontSize: 36, color: C.paper }}>ἀψίνθιον</span>
        </div>
      </div>
    );
  if (i === 1)
    return (
      <div style={box}>
        <Photo src={ASPHODEL.aestivus.url} style={{ objectPosition: "50% 30%" }} />
      </div>
    );
  if (i === 2) {
    const xs = [30, 96, 162, 228];
    return (
      <div style={box}>
        <svg width={TW} height={TH}>
          <line x1={30} y1={92} x2={228} y2={92} stroke={C.lichen} strokeWidth={2} strokeDasharray="5 5" opacity={0.7} />
          {xs.map((x, k) => (
            <g key={k}>
              <circle cx={x} cy={92} r={11} fill={C.ink} stroke={C.hi} strokeWidth={2.5} />
              <text x={x} y={136} textAnchor="middle" fontFamily={MONO} fontSize={15} fill={C.dim}>{["1st", "2nd", "13th", "today"][k]}</text>
            </g>
          ))}
        </svg>
      </div>
    );
  }
  if (i === 3)
    return (
      <div style={{ ...box, display: "flex", alignItems: "center", justifyContent: "center", gap: 18 }}>
        {[2000, 2005, 2010, 2015].map((y, k) => (
          <div key={y} style={{ fontFamily: MONO, fontSize: 22, color: k === 0 ? C.paper : C.dim, writingMode: "vertical-rl", rotate: "180deg", borderLeft: k === 0 ? `2px solid ${C.hi}` : "none", paddingLeft: 6 }}>{y}</div>
        ))}
      </div>
    );
  return (
    <div style={{ ...box, display: "flex", alignItems: "flex-end", justifyContent: "center", gap: 14, paddingBottom: 22 }}>
      {[0, 1, 2, 3, 4].map((k) => (
        <div key={k} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
          <span style={{ fontFamily: MONO, fontSize: 15, color: k < 3 ? C.lichen : C.dim }}>{k + 1}</span>
          <Vial w={32} h={118} color={k < 3 ? C.lichen : C.dim} />
        </div>
      ))}
    </div>
  );
};

// where each token floats in the chaos (centre x, centre y, rotation, scale)
const CHAOS = [
  { x: 330, y: 200, r: -14, s: 1.35 },
  { x: 1580, y: 190, r: 11, s: 1.4 },
  { x: 1690, y: 780, r: -8, s: 1.2 },
  { x: 270, y: 790, r: 9, s: 1.25 },
  { x: 1010, y: 830, r: -5, s: 1.3 },
];
const DEBRIS = [
  { img: "folio-iris", x: 720, y: 210, r: 8, w: 170 },
  { img: "folio-glukurizon", x: 1260, y: 520, r: -11, w: 190 },
  { img: "folio-drakontaia", x: 560, y: 560, r: 13, w: 160 },
  { img: "folio-adianton", x: 1380, y: 840, r: 6, w: 150 },
  { q: true, x: 900, y: 440, r: -6, w: 120 },
  { q: true, x: 1720, y: 470, r: 12, w: 90 },
  { q: true, x: 140, y: 500, r: 4, w: 100 },
];

const STEPS = [
  { verb: "Read", note: "exact Greek, quoted", off: 44 },
  { verb: "Identify", note: "P(species), honestly", off: 71 },
  { verb: "Trace", note: "four eras", off: 179 },
  { verb: "Test", note: "the time machine", off: 255 },
  { verb: "Rank", note: "a shortlist", off: 357 },
];

export const Turn: React.FC = () => {
  const f = useCurrentFrame();
  const A = cue(ID, 0);
  const snap = A + 12; // "So we built Pharmakon"
  const times = STEPS.map((s) => A + s.off);
  const litCount = times.reduce((n, t) => n + (ease(f, t - 2, t + 12, 0, 1) as number), 0);

  return (
    <Stage glow="none">
      {/* verdigris arrives with each lit step */}
      <AbsoluteFill style={{ background: "radial-gradient(circle at 90% 4%, rgba(23,116,79,.38), transparent 45%), radial-gradient(circle at 6% 98%, rgba(23,116,79,.30), transparent 42%)", opacity: litCount / 5 }} />

      {/* debris of the problem, cleared by the snap */}
      {DEBRIS.map((d, k) => {
        const out = ease(f, snap + k * 2, snap + 22 + k * 2, 0, 1) as number;
        const dx = (d.x - 960) * 0.5 * out;
        const dy = (d.y - 540) * 0.5 * out;
        const fl = Math.sin((f + k * 30) / 40) * 6;
        return (
          <div key={k} style={{ position: "absolute", left: d.x - d.w / 2, top: d.y - d.w * 0.7 + fl, width: d.w, translate: `${dx}px ${dy}px`, rotate: `${d.r + out * 20 * (rnd(k) - 0.5)}deg`, opacity: 0.5 * (1 - out), filter: `blur(${out * 12}px)` }}>
            {"img" in d && d.img ? (
              <Img src={staticFile(`media/${d.img}.webp`)} style={{ width: "100%", filter: "saturate(.1) brightness(.7)", boxShadow: "0 20px 40px rgba(0,0,0,.8)" }} />
            ) : (
              <div style={{ fontFamily: OUTFIT, fontWeight: 300, fontSize: d.w, color: C.dim, lineHeight: 1 }}>?</div>
            )}
          </div>
        );
      })}

      <div style={{ position: "absolute", left: 0, right: 0, top: 128, display: "flex", justifyContent: "center", opacity: ease(f, snap, snap + 18, 0, 1), filter: `blur(${ease(f, snap, snap + 20, 10, 0)}px)` }}>
        <Wordmark size={76} />
      </div>

      {/* rail under the strip */}
      <div style={{ position: "absolute", left: left(0) + CW / 2, top: TOP + CH + 52, width: 4 * 330, height: 2, background: C.rule, opacity: ease(f, snap + 10, snap + 30, 0, 1) }} />
      <div style={{ position: "absolute", left: left(0) + CW / 2, top: TOP + CH + 52, height: 2, width: interpolate(litCount, [1, 5], [0, 4 * 330], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), background: C.hi, boxShadow: `0 0 12px ${C.hi}` }} />

      <AbsoluteFill style={{ scale: `${1 + Math.max(0, f - snap) * 0.00008}` }}>
        {STEPS.map((s, i) => {
          const t = times[i];
          const slot = ease(f, snap + 8 + i * 4, snap + 26 + i * 4, 0, 1) as number;
          const lit = ease(f, t - 2, t + 12, 0, 1) as number;
          return (
            <div key={s.verb} style={{ position: "absolute", left: left(i), top: TOP, width: CW, height: CH, opacity: slot, translate: `0px ${(1 - slot) * 30}px` }}>
              <div style={{ position: "absolute", inset: 0, borderRadius: 24, border: `1.5px dashed ${C.rule}`, opacity: 1 - lit }} />
              <div style={{ position: "absolute", inset: 0, borderRadius: 24, background: C.card, border: `1px solid ${C.verdigris}`, boxShadow: "0 24px 60px rgba(23,116,79,.22)", opacity: lit }} />
              <div style={{ position: "absolute", left: 0, right: 0, top: 238, display: "flex", justifyContent: "center" }}>
                <div style={{ position: "absolute", fontFamily: OUTFIT, fontWeight: 500, fontSize: 30, color: C.dim, padding: "14px 26px", opacity: 1 - lit }}>{s.verb}</div>
                <Glass style={{ opacity: lit, scale: `${0.9 + 0.1 * lit}`, fontWeight: 600 }}>
                  <span style={{ width: 9, height: 9, borderRadius: 9, background: C.hi, boxShadow: `0 0 10px ${C.hi}` }} />
                  {s.verb}
                </Glass>
              </div>
              <div style={{ position: "absolute", left: 0, right: 0, top: 318, textAlign: "center", fontFamily: MONO, fontSize: 19, color: C.lichen, opacity: lit * 0.9 }}>{s.note}</div>
              {/* rail dot */}
              <div style={{ position: "absolute", left: CW / 2 - 7, top: CH + 46, width: 14, height: 14, borderRadius: 14, background: lit > 0.5 ? C.hi : C.ink, border: `2px solid ${lit > 0.5 ? C.hi : C.rule}`, boxShadow: lit > 0.5 ? `0 0 14px ${C.hi}` : "none" }} />
            </div>
          );
        })}

        {/* tokens: float in the chaos, fly into their slot on their verb */}
        {STEPS.map((s, i) => {
          const t = times[i];
          const p = ease(f, t - 10, t + 12, 0, 1, EXPO) as number;
          const c = CHAOS[i];
          const fx = Math.sin((f + i * 50) / 38) * 8 * (1 - p);
          const fy = Math.cos((f + i * 70) / 44) * 7 * (1 - p);
          const tx = left(i) + 20 + TW / 2;
          const ty = TOP + 22 + TH / 2;
          // after the snap, waiting tokens line up faintly beneath their own slot, then rise into it on their verb
          const park = ease(f, snap + i * 3, snap + 24 + i * 3, 0, 1) as number;
          const px = interpolate(park, [0, 1], [c.x, tx]);
          const py = interpolate(park, [0, 1], [c.y, 905]);
          const x = interpolate(p, [0, 1], [px, tx]) + fx;
          const y = interpolate(p, [0, 1], [py, ty]) + fy;
          const restS = interpolate(park, [0, 1], [c.s, 0.5]);
          const restR = interpolate(park, [0, 1], [c.r + Math.sin(f / 60 + i) * 1.5, 0]);
          const restO = interpolate(park, [0, 1], [0.55, 0.3]);
          return (
            <div
              key={s.verb}
              style={{
                position: "absolute", left: x - TW / 2, top: y - TH / 2, width: TW, height: TH,
                rotate: `${interpolate(p, [0, 1], [restR, 0])}deg`, scale: `${interpolate(p, [0, 1], [restS, 1])}`,
                opacity: interpolate(p, [0, 1], [restO, 1]), filter: `saturate(${interpolate(p, [0, 1], [0.08, 1])}) brightness(${interpolate(p, [0, 1], [0.7, 1])})`,
                boxShadow: `0 ${30 * (1 - p) + 6}px ${60 * (1 - p) + 20}px rgba(0,0,0,.7)`, borderRadius: 18,
              }}
            >
              <Token i={i} />
            </div>
          );
        })}
      </AbsoluteFill>
    </Stage>
  );
};
