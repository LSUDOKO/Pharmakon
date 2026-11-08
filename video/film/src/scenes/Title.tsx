// Scene "title" — the site's torn-paper hero, rebuilt frame-for-frame (web/src/main.js heroIntro + style.css .band/.dim).
// Opens on the full-frame folio Cold ends on; the page tears along the diagonal, the two sheets pull apart,
// the hatched band draws open, the mark spins in, the chrome wordmark sweeps, dimension lines and tagline land on the VO.
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, CHROME, EXPO, MONO, OUTFIT, Stage, TornSheet, Words, ease } from "../brand";
import { scene } from "../timing";

const TEAR = 14; // frame the page rips

export const Title: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = scene("title");
  const vo = t.lines[0].from;

  // full folio (continuity from Cold) until the rip
  const fullOpacity = interpolate(frame, [TEAR - 1, TEAR + 2], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const shake = frame >= TEAR && frame < TEAR + 6 ? Math.sin(frame * 2.7) * (TEAR + 6 - frame) * 1.2 : 0;

  // sheets: start overlapping (covering the frame), pull apart with expo ease, then keep a slow parallax drift
  const apart = interpolate(frame, [TEAR, TEAR + 1.4 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EXPO });
  const drift = Math.max(0, frame - TEAR) / fps;
  // final resting place leaves the centre band and tagline clear (the 16:9 frame squeezes the site's masks)
  const ax = -26 + 37 * apart + drift * 0.18;
  const ay = 24 - 37 * apart - drift * 0.14;
  const bx = 26 - 37 * apart - drift * 0.18;
  const by = -24 + 37 * apart + drift * 0.14;

  // band opens from the centre (clip-path inset), mark springs, chrome sweeps
  const bandAt = TEAR + Math.round(0.45 * fps);
  const bandOpen = interpolate(frame, [bandAt, bandAt + 1.1 * fps], [50, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EXPO });
  const markAt = TEAR + Math.round(0.9 * fps);
  const markS = spring({ frame: frame - markAt, fps, config: { stiffness: 120, damping: 14 } });
  const sweep = interpolate(frame, [TEAR + 0.8 * fps, TEAR + 2.4 * fps], [100, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EXPO });
  const wmOpacity = ease(frame, TEAR + 0.8 * fps, TEAR + 1.6 * fps, 0, 1);
  const dimA = ease(frame, TEAR + 1.3 * fps, TEAR + 2.1 * fps, 0, 1);
  const dimB = ease(frame, TEAR + 1.45 * fps, TEAR + 2.25 * fps, 0, 1);
  const breathe = 1 + 0.012 * Math.sin(frame / 40);
  const outFade = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <Stage glow="none">
      {/* the two torn sheets — Vienna Dioscorides folios printed in verdigris */}
      <TornSheet which="a" img="media/folio-apsinthion.webp" style={{ translate: `${ax + shake * 0.02}% ${ay}%`, rotate: `${apart * 0.6 + drift * 0.05}deg`, opacity: frame < TEAR ? 0 : 1 }} />
      <TornSheet which="b" img="media/folio-glukurizon.webp" style={{ translate: `${bx - shake * 0.02}% ${by}%`, rotate: `${-apart * 0.6 - drift * 0.05}deg`, opacity: frame < TEAR ? 0 : 1 }} />

      {/* full folio from the Cold scene, held until the rip */}
      <AbsoluteFill style={{ opacity: fullOpacity }}>
        <Img src={staticFile("media/folio-adianton.webp")} style={{ width: "100%", height: "100%", objectFit: "cover", scale: "1.08" }} />
      </AbsoluteFill>

      {/* hatched band with construction lines, wordmark and dimension lines */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: outFade }}>
        <div style={{ position: "relative", top: -60, scale: `${breathe}` }}>
          {/* construction lines across the frame */}
          <div style={{ position: "absolute", left: -1200, right: -1200, top: 0, borderTop: "1px dashed rgba(236,238,231,.22)", opacity: 1 - bandOpen / 50 }} />
          <div style={{ position: "absolute", left: -1200, right: -1200, bottom: 0, borderTop: "1px dashed rgba(236,238,231,.22)", opacity: 1 - bandOpen / 50 }} />
          <div
            style={{
              width: 1180,
              padding: "64px 70px",
              background: `repeating-linear-gradient(135deg, rgba(255,255,255,.055) 0 1px, transparent 1px 7px), ${C.ink}`,
              boxShadow: "0 0 0 1px rgba(255,255,255,.06), 0 0 160px 60px rgba(0,0,0,.75)",
              clipPath: `inset(0 ${bandOpen}% 0 ${bandOpen}%)`,
              display: "flex",
              justifyContent: "center",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 30 }}>
              <Img
                src={staticFile("media/mark.svg")}
                style={{ width: 132, height: 132, rotate: `${-90 + 90 * markS}deg`, scale: `${0.4 + 0.6 * markS}`, opacity: Math.min(1, markS * 1.4) }}
              />
              <span
                style={{
                  fontFamily: OUTFIT, fontWeight: 500, fontSize: 168, letterSpacing: "-0.045em", lineHeight: 1, paddingBottom: 14,
                  backgroundImage: CHROME, backgroundSize: "100% 260%", backgroundPositionY: `${sweep}%`,
                  WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", opacity: wmOpacity,
                }}
              >
                pharmakon
              </span>
            </div>
          </div>
          {/* horizontal dimension line */}
          <div style={{ position: "absolute", left: "50%", top: -40, translate: "-50% 0", display: "flex", alignItems: "center", gap: 16, opacity: dimA }}>
            <span style={{ width: 300 * dimA, borderTop: "1px solid rgba(236,238,231,.35)" }} />
            <span style={{ fontFamily: MONO, fontSize: 22, color: "rgba(236,238,231,.66)", whiteSpace: "nowrap" }}>1,500 passages read</span>
            <span style={{ width: 300 * dimA, borderTop: "1px solid rgba(236,238,231,.35)" }} />
          </div>
          {/* vertical dimension line */}
          <div style={{ position: "absolute", left: -24, top: "50%", translate: "-100% -50%", rotate: "-90deg", transformOrigin: "100% 50%", fontFamily: MONO, fontSize: 22, color: "rgba(236,238,231,.66)", whiteSpace: "nowrap", opacity: dimB }}>
            61 expert names
          </div>
        </div>
      </AbsoluteFill>

      {/* tagline on the VO */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 690 }}>
        <Words text="2,000 years of Greek plant medicine, measured." at={vo + 18} stagger={4} size={54} weight={400} accent={["measured"]} style={{ justifyContent: "center", textShadow: "0 2px 18px rgba(0,0,0,.9)" }} />
      </AbsoluteFill>
      <div style={{ position: "absolute", right: 160, bottom: 236, fontFamily: OUTFIT, fontSize: 22, color: C.dim, opacity: ease(frame, vo + 40, vo + 60, 0, 1) }}>
        Research hypotheses only — not medical advice.
      </div>
    </Stage>
  );
};

// keep Easing referenced for future eases without lint noise
void Easing;
