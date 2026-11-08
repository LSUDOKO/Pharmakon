// Devpost project thumbnail, 3:2 (1500×1000): the site hero's torn folios, the hatched band and the logo.
import React from "react";
import { AbsoluteFill } from "remotion";
import { C, MONO, OUTFIT, TornSheet, Wordmark } from "./brand";

export const DevpostCard: React.FC = () => (
  <AbsoluteFill style={{ background: C.ink, fontFamily: OUTFIT, color: C.paper, overflow: "hidden" }}>
    <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 46%, rgba(23,116,79,.35), transparent 55%)" }} />
    <TornSheet which="a" img="media/folio-apsinthion.webp" style={{ translate: "14% -20%", rotate: "0.6deg" }} />
    <TornSheet which="b" img="media/folio-glukurizon.webp" style={{ translate: "-14% 20%", rotate: "-0.6deg" }} />
    {/* hatched band with construction lines, as on the site hero */}
    <div style={{ position: "absolute", left: 0, right: 0, top: 330, height: 300, background: `repeating-linear-gradient(135deg, rgba(255,255,255,.055) 0 1px, transparent 1px 7px), ${C.ink}`, borderTop: "1px dashed rgba(236,238,231,.25)", borderBottom: "1px dashed rgba(236,238,231,.25)", boxShadow: "0 0 120px 40px rgba(0,0,0,.8)" }} />
    <div style={{ position: "absolute", left: 0, right: 0, top: 330, height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Wordmark size={176} />
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 660, textAlign: "center", fontSize: 50, fontWeight: 400, letterSpacing: "-0.02em", textShadow: "0 4px 24px rgba(0,0,0,.95)" }}>
      2,000 years of Greek plant medicine, <span style={{ color: C.hi }}>measured.</span>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 286, textAlign: "center", fontFamily: MONO, fontSize: 24, color: "rgba(236,238,231,.7)" }}>
      Dioscorides → species → compound → target → disease
    </div>
  </AbsoluteFill>
);
