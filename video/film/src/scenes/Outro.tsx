// Scene "outro" (s12_a–b): back at Eleni's desk — ten vials now labelled — then torn paper closes into the end card.
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, DIDOT, EASE_IN, MONO, OUTFIT, SAFE, Stage, TornSheet, Wordmark, Words, ease, fictional } from "../brand";
import { scene } from "../timing";
import { VIALS, at } from "./results/data";
import { DISCLAIMER, Grid } from "./results/kit";

const S = "outro";
const L = (id: string, phrase = "") => at(S, id, phrase);

const Vial: React.FC<{ x: number; fill: number; label: number }> = ({ x, fill, label }) => {
  const w = 64, h = 210, top = 400, r = w / 2;
  const body = `M${x - r} ${top + 30} V${top + h - r} A${r} ${r} 0 0 0 ${x + r} ${top + h - r} V${top + 30}`;
  const level = top + h - (h - 70) * fill;
  return (
    <g>
      <clipPath id={`vial${label}`}>
        <path d={`${body} Z`} />
      </clipPath>
      <rect x={x - r} y={level} width={w} height={top + h - level} fill={C.verdigris} clipPath={`url(#vial${label})`} />
      <line x1={x - r + 4} x2={x + r - 4} y1={level} y2={level} stroke={C.hi} strokeWidth={3} opacity={fill > 0.02 ? 1 : 0} />
      <path d={body} fill="none" stroke={C.dim} strokeWidth={2.5} />
      <rect x={x - r - 6} y={top} width={w + 12} height={30} rx={6} fill={C.card} stroke={C.dim} strokeWidth={2.5} />
    </g>
  );
};

const Desk: React.FC = () => {
  const f = useCurrentFrame();
  const tNames = L("s12_a", "six hundred");
  const tEnds = L("s12_a", "She ends");
  const pitch = (1920 - 2 * SAFE) / VIALS.length;
  const xs = VIALS.map((_, i) => SAFE + pitch * (i + 0.5));
  return (
    <>
      <div style={{ position: "absolute", left: SAFE, top: 130, display: "flex", alignItems: "center", gap: 40 }}>
        <div style={{ fontFamily: MONO, fontWeight: 600, fontSize: 84, color: C.dim, letterSpacing: "-0.03em", opacity: ease(f, tNames, tNames + 12, 0, 1), translate: `0px ${ease(f, tNames, tNames + 16, 20, 0)}px` }}>
          600 names
        </div>
        <svg width={110} height={40} style={{ opacity: ease(f, tEnds - 6, tEnds + 4, 0, 1) }}>
          <line x1={0} x2={ease(f, tEnds - 6, tEnds + 10, 0, 96)} y1={20} y2={20} stroke={C.lichen} strokeWidth={4} />
          <path d="M88 8 L108 20 L88 32" fill="none" stroke={C.lichen} strokeWidth={4} opacity={ease(f, tEnds + 6, tEnds + 12, 0, 1)} />
        </svg>
        <Words text="a shortlist she can defend" at={tEnds + 4} size={84} accent={["defend"]} />
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
        <line x1={SAFE - 20} x2={1920 - SAFE + 20} y1={618} y2={618} stroke={C.rule} strokeWidth={2} />
        {xs.map((x, i) => (
          <Vial key={i} x={x} label={i} fill={ease(f, tEnds + 6 + i * 7, tEnds + 40 + i * 7, 0, VIALS[i].p) as number} />
        ))}
      </svg>
      {xs.map((x, i) => {
        const v = VIALS[i];
        const [genus, ...rest] = v.species.split(" ");
        const t = tEnds + 20 + i * 7;
        return (
          <div key={i} style={{ position: "absolute", left: x - pitch / 2, width: pitch, top: 640, textAlign: "center", opacity: ease(f, t, t + 14, 0, 1), translate: `0px ${ease(f, t, t + 18, 14, 0)}px` }}>
            <div style={{ fontFamily: MONO, fontSize: 17, color: C.dim }}>#{v.rank}</div>
            <div style={{ fontFamily: DIDOT, fontStyle: "italic", fontSize: 27, lineHeight: 1.12, color: C.paper, marginTop: 4 }}>
              {genus}
              <br />
              {rest.join(" ")}
            </div>
            <div style={{ fontFamily: MONO, fontSize: 18, color: C.lichen, marginTop: 6 }}>P {v.p.toFixed(2)}</div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: SAFE, right: SAFE, top: 812, display: "flex", justifyContent: "space-between", fontFamily: MONO, fontSize: 19, color: C.dim, opacity: ease(f, tEnds + 60, tEnds + 80, 0, 0.9) }}>
        <span>{fictional} · fill = P(species) ≥ 0.5 · no toxicity flag</span>
        <span>{DISCLAIMER}</span>
      </div>
    </>
  );
};

const EndCard: React.FC<{ t: number }> = ({ t }) => {
  const f = useCurrentFrame();
  const tWord = L("s12_b");
  const band = ease(f, t + 8, t + 30, 0, 1) as number;
  const word = ease(f, tWord - 6, tWord + 20, 0, 1) as number;
  const line = (k: number) => ({ opacity: ease(f, tWord + 18 + k * 6, tWord + 32 + k * 6, 0, 1), translate: `0px ${ease(f, tWord + 18 + k * 6, tWord + 36 + k * 6, 14, 0)}px` });
  return (
    <>
      {/* hatched band with dashed construction lines, as on the site */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 270, height: 250, background: `repeating-linear-gradient(135deg, rgba(255,255,255,.05) 0 1px, transparent 1px 7px), ${C.ink}`, borderTop: "1px dashed rgba(236,238,231,.2)", borderBottom: "1px dashed rgba(236,238,231,.2)", clipPath: `inset(0 ${(1 - band) * 50}% 0 ${(1 - band) * 50}%)` }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 270, height: 250, display: "flex", alignItems: "center", justifyContent: "center", opacity: word, filter: `blur(${(1 - word) * 16}px)`, scale: `${0.96 + 0.04 * word}` }}>
        <Wordmark size={156} />
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 560, display: "flex", flexDirection: "column", alignItems: "center", gap: 20, textAlign: "center" }}>
        <div style={{ fontFamily: MONO, fontSize: 30, color: C.paper, ...line(0) }}>
          pharmakon.adoranto737.workers.dev <span style={{ color: C.dim }}>·</span> github.com/LSUDOKO/Pharmakon <span style={{ color: C.dim }}>·</span> <span style={{ color: C.hi }}>/mcp</span>
        </div>
        <div style={{ fontSize: 34, fontWeight: 500, color: C.lichen, ...line(1) }}>EthnoHack 2026 · Track 1 — Traditional knowledge</div>
        <div style={{ fontSize: 30, color: C.dim, ...line(2) }}>Built by Arpit · B.Tech Computer Science, NIT Hamirpur</div>
        <div style={{ fontFamily: MONO, fontSize: 21, color: C.dim, marginTop: 14, ...line(3) }}>{DISCLAIMER}</div>
      </div>
    </>
  );
};

export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const t = scene(S);
  const tClose = L("s12_b") - 44; // torn paper closes in just before "Pharmakon."
  const deskOut = ease(f, tClose - 4, tClose + 12, 0, 1, EASE_IN) as number;
  const close = ease(f, tClose, tClose + 27, 0, 1) as number; // 900 ms expo, as the hero
  const drift = f * 0.03;
  return (
    <Stage glow="tr">
      <Grid />
      {deskOut < 1 && (
        <AbsoluteFill style={{ opacity: 1 - deskOut, scale: `${1 + (f / t.duration) * 0.02 - deskOut * 0.03}`, fontFamily: OUTFIT, color: C.paper }}>
          <Desk />
        </AbsoluteFill>
      )}
      {close > 0 && (
        <>
          <TornSheet which="a" img="media/folio-apsinthion.webp" style={{ translate: `${(1 - close) * 900 + 140 + drift}px ${-(1 - close) * 600 - 150 - drift * 0.5}px`, rotate: `${(1 - close) * 6}deg` }} />
          <TornSheet which="b" img="media/folio-iris.webp" style={{ translate: `${-(1 - close) * 900 - 180 - drift}px ${(1 - close) * 600 + 170 + drift * 0.5}px`, rotate: `${-(1 - close) * 6}deg` }} />
          <AbsoluteFill style={{ fontFamily: OUTFIT, color: C.paper, scale: `${1 + Math.max(0, f - tClose) / 6000}` }}>
            <EndCard t={tClose} />
          </AbsoluteFill>
        </>
      )}
    </Stage>
  );
};
