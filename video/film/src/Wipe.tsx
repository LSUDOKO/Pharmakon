// Torn-paper wipe between scenes: a verdigris sheet with fibrous off-white edges (same feTurbulence +
// feDisplacementMap recipe as the site's tear/fringe masks) sweeps diagonally across the cut.
import React from "react";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C } from "./brand";

export const WIPE_FRAMES = 30; // whole sweep; frame is fully covered around the middle

export const Wipe: React.FC<{ seed: number; folio: string; dir?: 1 | -1 }> = ({ seed, folio, dir = 1 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, WIPE_FRAMES], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.65, 0, 0.35, 1) });
  const W = 2700;
  const H = 3600;
  const x = dir * interpolate(p, [0, 1], [-2900, 2900]);
  const angle = dir === 1 ? -22 : 22;
  const id = `w${seed}`;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 960 - W / 2, top: 540 - H / 2, width: W, height: H, translate: `${x}px 0px`, rotate: `${angle}deg` }}>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ overflow: "visible", filter: "drop-shadow(0 30px 40px rgba(0,0,0,.65))" }}>
          <defs>
            <filter id={`${id}f`} x="-10%" y="-2%" width="120%" height="104%">
              <feTurbulence type="fractalNoise" baseFrequency="0.012 0.035" numOctaves={5} seed={seed} result="n" />
              <feDisplacementMap in="SourceGraphic" in2="n" scale={70} xChannelSelector="R" yChannelSelector="G" />
            </filter>
            <filter id={`${id}p`} x="-10%" y="-2%" width="120%" height="104%">
              <feTurbulence type="fractalNoise" baseFrequency="0.016 0.04" numOctaves={5} seed={seed + 7} result="n" />
              <feDisplacementMap in="SourceGraphic" in2="n" scale={46} xChannelSelector="R" yChannelSelector="G" />
            </filter>
            <pattern id={`${id}img`} patternUnits="userSpaceOnUse" width={W} height={H}>
              <rect width={W} height={H} fill={C.verdigris} />
              <image href={staticFile(folio)} x={W * 0.12} y={H * 0.25} width={W * 0.76} height={H * 0.5} preserveAspectRatio="xMidYMid slice" opacity={0.85} />
            </pattern>
          </defs>
          {/* fibrous paper edge */}
          <rect x={W * 0.08} y={-40} width={W * 0.84} height={H + 80} fill={C.paper} filter={`url(#${id}f)`} />
          {/* printed verdigris sheet */}
          <rect x={W * 0.1} y={-40} width={W * 0.8} height={H + 80} fill={`url(#${id}img)`} filter={`url(#${id}p)`} />
        </svg>
      </div>
    </AbsoluteFill>
  );
};
