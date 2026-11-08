// Scene "cold" — the hook. 2015 Nobel (artemisinin) -> an ancient Chinese handbook -> Europe has one too (Vienna Dioscorides).
// Sync: word offsets inside each VO line come from a whisper word-timestamp pass over public/vo/s01_*.wav.
// Ends on folio-adianton filling the frame (unrotated, scale >= 1.08 cover) for the Title tear.
import React from "react";
import { AbsoluteFill, Img, interpolate, interpolateColors, staticFile, useCurrentFrame } from "remotion";
import { C, EASE_IN, MONO, OUTFIT, SAFE, Stage, Words, ease } from "../brand";
import { scene } from "../timing";
import { Book, Cite, cue } from "./coldproblem/kit";

const ID = "cold";

// Folio box sized to cover 1920x1080 with 8% overscan (adianton is 1400x1278).
const FW = 1920 * 1.08;
const FH = (FW * 1278) / 1400;

export const Cold: React.FC = () => {
  const f = useCurrentFrame();
  const D = scene(ID).duration;
  const A = cue(ID, 0); // "In 2015, a Nobel Prize recognised ... artemisinin"
  const B = cue(ID, 1); // "Its discoverer found the clue in a Chinese medical handbook ..."
  const K = cue(ID, 2); // "Europe has a handbook like that too. And it is even older."

  // ---------- beat 1: 2015 / Nobel Prize / artemisinin ----------
  const t2015 = A + 2;
  const tNobel = A + 39;
  const tArt = A + 94;
  const tMal = A + 136;
  const out1 = B - 18;
  const g1 = ease(f, out1, out1 + 14, 1, 0, EASE_IN) as number;
  const g1y = ease(f, out1, out1 + 14, 0, -40, EASE_IN) as number;
  const shrink = ease(f, tNobel - 8, tNobel + 16, 0, 1) as number;
  const yrY = interpolate(shrink, [0, 1], [540, 300]);
  const yrScale = interpolate(shrink, [0, 1], [1, 0.34]) * (1 + 0.04 * (ease(f, t2015, tNobel, 0, 1) as number));
  const art = "artemisinin";

  // ---------- beat 2: the handbook ----------
  const in2 = B - 6;
  const out2 = K - 26;
  const g2 = Math.min(ease(f, in2, in2 + 10, 0, 1) as number, ease(f, out2, out2 + 14, 1, 0, EASE_IN) as number);
  const tDim = B + 98; // "1600"
  const dimW = ease(f, tDim - 6, tDim + 18, 0, 400) as number;

  // ---------- beat 3: the folio ----------
  const tIn = K - 8;
  const push = ease(f, D - 46, D - 4, 0, 1) as number;
  const pageScale = 640 / FH;
  const enter = ease(f, tIn, tIn + 26, 0, 1) as number;
  const scale = interpolate(push, [0, 1], [pageScale * (0.9 + 0.1 * enter) * (1 + 0.0006 * Math.max(0, f - tIn)), 1]) * (1 + 0.0009 * Math.max(0, f - (D - 8)));
  const cx = interpolate(push, [0, 1], [1290, 960]);
  const cy = interpolate(push, [0, 1], [470, 540]) - (push < 1 ? 0.05 * Math.max(0, f - tIn) : 0);
  const rot = interpolate(push, [0, 1], [-7 + 4 * enter - 0.01 * Math.max(0, f - tIn), 0]);
  const txt3 = Math.min(ease(f, K, K + 10, 0, 1) as number, ease(f, D - 50, D - 38, 1, 0, EASE_IN) as number);

  return (
    <Stage glow="none">
      {/* beat 1 */}
      {f < out1 + 16 && (
        <AbsoluteFill style={{ opacity: g1, translate: `0px ${g1y}px`, scale: `${1 + f * 0.00015}` }}>
          <div
            style={{
              position: "absolute", left: 0, right: 0, top: yrY - 150, textAlign: "center", fontFamily: MONO, fontWeight: 600, fontSize: 260,
              letterSpacing: "-0.04em", color: interpolateColors(shrink, [0, 1], [C.paper, C.dim]), scale: `${yrScale}`,
              opacity: ease(f, t2015, t2015 + 10, 0, 1), filter: `blur(${ease(f, t2015, t2015 + 14, 14, 0)}px)`,
            }}
          >
            2015
          </div>
          <div style={{ position: "absolute", top: 368, left: 960 - (ease(f, tNobel, tNobel + 26, 0, 380) as number), width: (ease(f, tNobel, tNobel + 26, 0, 760) as number), height: 1, background: C.dim, opacity: 0.45 }} />
          <Words text="Nobel Prize" at={tNobel - 2} size={150} weight={600} style={{ position: "absolute", top: 392, left: 0, right: 0, justifyContent: "center" }} />
          <div style={{ position: "absolute", top: 590, left: 0, right: 0, textAlign: "center", fontFamily: MONO, fontSize: 92, letterSpacing: "-0.02em" }}>
            {art.split("").map((ch, i) => {
              const s = tArt - 4 + i * 2;
              return (
                <span key={i} style={{ opacity: ease(f, s, s + 6, 0, 1), filter: `blur(${ease(f, s, s + 8, 6, 0)}px)`, display: "inline-block", translate: `0px ${ease(f, s, s + 10, 16, 0)}px` }}>
                  {ch}
                </span>
              );
            })}
          </div>
          <Words text="a drug against malaria" at={tMal - 4} size={42} weight={300} color={C.dim} stagger={2} style={{ position: "absolute", top: 718, left: 0, right: 0, justifyContent: "center" }} />
          <Cite style={{ position: "absolute", top: 806, left: 0, right: 0, textAlign: "center" }} opacity={ease(f, tNobel + 30, tNobel + 44, 0, 1) as number}>
            nobelprize.org · The Nobel Prize in Physiology or Medicine 2015 · Tu Youyou (shared)
          </Cite>
        </AbsoluteFill>
      )}

      {/* beat 2 */}
      {f >= in2 && f < out2 + 16 && (
        <AbsoluteFill style={{ opacity: g2, scale: `${1 + (f - in2) * 0.00018}` }}>
          <div style={{ position: "absolute", top: 150, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
            <Book draw={ease(f, B + 2, B + 74, 0, 1) as number} color={C.paper} size={290} />
          </div>
          <Words text="A Handbook of Prescriptions for Emergencies" at={B + 62} size={62} weight={500} stagger={2} style={{ position: "absolute", top: 380, left: 0, right: 0, justifyContent: "center" }} />
          <Words text="Ge Hong · East Jin dynasty" at={B + 76} size={34} weight={300} color={C.dim} stagger={2} style={{ position: "absolute", top: 468, left: 0, right: 0, justifyContent: "center" }} />
          {/* engineering dimension line, as on the site's hero */}
          <div style={{ position: "absolute", top: 610, left: 960 - dimW, width: dimW * 2, height: 1, background: C.dim, opacity: 0.7 }} />
          {[-1, 1].map((s) => (
            <div key={s} style={{ position: "absolute", top: 596, left: 960 + s * dimW - 0.5, width: 1, height: 28, background: C.dim, opacity: dimW > 395 ? 0.8 : 0 }} />
          ))}
          <div style={{ position: "absolute", top: 560, left: 560 - 200, width: 400, textAlign: "center", fontFamily: MONO, fontSize: 24, color: C.dim, opacity: ease(f, tDim + 14, tDim + 24, 0, 1) }}>AD 317–420</div>
          <div style={{ position: "absolute", top: 560, left: 1360 - 200, width: 400, textAlign: "center", fontFamily: MONO, fontSize: 24, color: C.dim, opacity: ease(f, tDim + 16, tDim + 26, 0, 1) }}>2015</div>
          <div style={{ position: "absolute", top: 588, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
            <span style={{ background: C.ink, padding: "0 22px", fontFamily: MONO, fontSize: 36, color: C.paper, opacity: ease(f, tDim, tDim + 10, 0, 1), filter: `blur(${ease(f, tDim, tDim + 12, 8, 0)}px)` }}>
              ≈ 1,600 years
            </span>
          </div>
          <Cite style={{ position: "absolute", top: 720, left: 0, right: 0, textAlign: "center" }} opacity={ease(f, B + 90, B + 104, 0, 1) as number}>
            nobelprize.org · Tu Youyou, Nobel Lecture 2015 · handbook dated East Jin dynasty, c. AD 317–420
          </Cite>
        </AbsoluteFill>
      )}

      {/* beat 3: Europe has one too — the Vienna Dioscorides */}
      {f >= tIn && (
        <>
          <div
            style={{
              position: "absolute", width: FW, height: FH, left: cx - FW / 2, top: cy - FH / 2,
              transform: `rotate(${rot}deg) scale(${scale})`, opacity: enter, filter: `blur(${(1 - enter) * 10}px)`,
              boxShadow: `0 ${60 * (1 - push)}px ${120 * (1 - push)}px rgba(0,0,0,${0.85 * (1 - push)})`, background: C.verdigris,
            }}
          >
            <Img src={staticFile("media/folio-adianton.webp")} style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }} />
          </div>
          <div style={{ position: "absolute", left: SAFE, top: 280, width: 680, opacity: txt3 }}>
            <Words text="Europe has one too." at={K + 2} size={112} weight={600} stagger={4} />
            <div style={{ marginTop: 44, fontFamily: OUTFIT, fontWeight: 400, fontSize: 36, color: C.dim, opacity: ease(f, K + 66, K + 78, 0, 1) }}>Dioscorides, De materia medica</div>
            <div style={{ marginTop: 6, fontFamily: MONO, fontSize: 60, color: C.paper, letterSpacing: "-0.02em", opacity: ease(f, K + 70, K + 80, 0, 1), filter: `blur(${ease(f, K + 70, K + 82, 8, 0)}px)` }}>
              1st century AD
            </div>
          </div>
          <Cite style={{ position: "absolute", top: 822, left: 1290 - 500, width: 1000, textAlign: "center", fontSize: 17 }} opacity={Math.min(ease(f, K + 24, K + 38, 0, 1) as number, txt3)}>
            Vienna Dioscorides, c. AD 512 · Austrian National Library · public domain
          </Cite>
        </>
      )}
    </Stage>
  );
};
