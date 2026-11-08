// Square logo (1000×1000): the mark over the chrome wordmark on true black with a faint verdigris glow.
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, CHROME, OUTFIT } from "./brand";

export const LogoSquare: React.FC = () => (
  <AbsoluteFill style={{ background: C.ink, alignItems: "center", justifyContent: "center", fontFamily: OUTFIT }}>
    <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 40%, rgba(23,116,79,.42), transparent 52%)" }} />
    <Img src={staticFile("media/mark.svg")} style={{ width: 380, height: 380, marginTop: -60 }} />
    <span style={{ fontWeight: 500, fontSize: 150, letterSpacing: "-0.045em", lineHeight: 1, marginTop: 40, backgroundImage: CHROME, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", paddingBottom: 12 }}>
      pharmakon
    </span>
  </AbsoluteFill>
);
