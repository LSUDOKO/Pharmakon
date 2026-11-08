// YouTube thumbnail (render as a still, 1920×1080 → 1280×720): the presenter's face, the hero's torn folio,
// one big real number. Same tokens, fonts and grade as the film.
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, DIDOT, MONO, OUTFIT, TornSheet, Wordmark } from "./brand";

export const Thumbnail: React.FC = () => (
  <AbsoluteFill style={{ background: C.ink, fontFamily: OUTFIT, color: C.paper, overflow: "hidden" }}>
    {/* verdigris glow behind the face */}
    <AbsoluteFill style={{ background: "radial-gradient(circle at 78% 40%, rgba(23,116,79,.55), transparent 48%)" }} />

    {/* the face, graded like the film's presenter card */}
    <div style={{ position: "absolute", right: -40, top: 0, width: 1000, height: 1080, overflow: "hidden" }}>
      <Img src={staticFile("presenter/thumb_face.png")} style={{ position: "absolute", height: 1040, left: -300, top: 40, filter: "saturate(.8) contrast(1.18) brightness(.97)" }} />
      <AbsoluteFill style={{ background: "#86AE9A", mixBlendMode: "multiply", opacity: 0.5 }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 46% 58% at 56% 46%, transparent 55%, rgba(0,0,0,.82) 100%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(90deg, #000 0%, rgba(0,0,0,.85) 14%, rgba(0,0,0,0) 46%)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.45) 0%, transparent 22%, transparent 70%, rgba(0,0,0,.9) 100%)" }} />
    </div>

    {/* torn folio, bottom-left, as in the site hero */}
    <TornSheet which="b" img="media/folio-apsinthion.webp" style={{ translate: "-10% 25%", rotate: "-3deg" }} />

    {/* type */}
    <div style={{ position: "absolute", left: 96, top: 84 }}>
      <Wordmark size={76} />
    </div>
    <div style={{ position: "absolute", left: 96, top: 230, width: 1060 }}>
      <div style={{ fontWeight: 700, fontSize: 290, lineHeight: 0.9, letterSpacing: "-0.05em", color: C.hi, textShadow: "0 8px 40px rgba(0,0,0,.6)" }}>1,781</div>
      <div style={{ fontWeight: 650, fontSize: 118, lineHeight: 1, letterSpacing: "-0.035em", marginTop: 18, textShadow: "0 6px 30px rgba(0,0,0,.8)" }}>untested leads</div>
      <div style={{ fontWeight: 400, fontSize: 60, lineHeight: 1.15, letterSpacing: "-0.02em", marginTop: 26, color: C.lichen, textShadow: "0 4px 24px rgba(0,0,0,.9)" }}>
        from a 2,000-year-old
        <br />
        Greek drug book
      </div>
    </div>
    <div style={{ position: "absolute", left: 1180, bottom: 74, display: "flex", alignItems: "baseline", gap: 18 }}>
      <span lang="grc" style={{ fontFamily: DIDOT, fontSize: 64, color: C.paper }}>ἀψίνθιον</span>
      <span style={{ fontFamily: MONO, fontSize: 26, color: C.dim }}>Dioscorides 3.23</span>
    </div>
    <div style={{ position: "absolute", inset: 0, boxShadow: `inset 0 0 0 10px ${C.verdigris}` }} />
  </AbsoluteFill>
);
