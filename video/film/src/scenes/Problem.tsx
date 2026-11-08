// Scene "problem" — Eleni's three blockers. Muted palette throughout (paper-dim, desaturated images); warn red only for the
// single "wasted year" strike the SPEC asks for. Sync: word offsets from a whisper pass over public/vo/s03_*.wav.
import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { C, CountUp, DIDOT, EASE_IN, MONO, OUTFIT, SAFE, Stage, Words, ease, fictional } from "../brand";
import { Cite, Photo, Vial, cue, life } from "./coldproblem/kit";
import { ASPHODEL } from "./coldproblem/photos";

const ID = "problem";
const MUTE = "saturate(.12) brightness(.78) contrast(1.05)";
const abs = (s: React.CSSProperties): React.CSSProperties => ({ position: "absolute", ...s });

const Label: React.FC<{ n: string; text: string; at: number }> = ({ n, text, at }) => {
  const f = useCurrentFrame();
  return (
    <div style={abs({ left: SAFE, top: 112, fontFamily: MONO, fontSize: 22, color: C.dim, letterSpacing: "0.12em", textTransform: "uppercase", opacity: ease(f, at, at + 12, 0, 1), translate: `${ease(f, at, at + 16, -16, 0)}px 0px` })}>
      <span style={{ color: C.paper }}>{n}</span>&nbsp;&nbsp;{text}
    </div>
  );
};

export const Problem: React.FC = () => {
  const f = useCurrentFrame();
  const A = cue(ID, 0); // Meet Eleni ... ten plant extracts this year
  const B = cue(ID, 1); // supervisor hands her Dioscorides ... six hundred plants ... a lead
  const N = cue(ID, 2); // the names: asphodel
  const W = cue(ID, 3); // wrong plant = wasted
  const E = cue(ID, 4); // which remedies survived
  const P = cue(ID, 5); // does history predict science

  // ---------------- beat 1: Eleni + ten empty vials ----------------
  const out1 = B - 2;
  const b1 = ease(f, out1, out1 + 14, 1, 0, EASE_IN) as number;

  // ---------------- beat 2: the book, fanned ----------------
  const in2 = B + 6;
  const out2 = N - 30;
  const fan = ease(f, B + 34, B + 70, 0, 1) as number;
  const b2 = life(f, in2, out2);
  const lead = ease(f, B + 352, B + 372, 0, 1) as number;
  const folios = ["folio-apsinthion", "folio-iris", "folio-glukurizon", "folio-drakontaia"];

  // ---------------- beat 3: one name, three plants ----------------
  const cards = [
    { ph: ASPHODEL.ramosus, src: "LSJ dictionary", cue: N + 110 },
    { ph: ASPHODEL.aestivus, src: "Experts · Lardos 2024", cue: N + 176 },
    { ph: ASPHODEL.fistulosus, src: "also plausible", cue: N + 250 },
  ];
  const allLit = N + 300;
  const fall = ease(f, W - 4, W + 16, 0, 1, EASE_IN) as number;
  const greek = "ἀσφόδελος";

  // ---------------- beat 4: wrong plant = wasted year ----------------
  const out4 = E - 26;
  const strike = ease(f, W + 82, W + 92, 0, 1) as number;

  // ---------------- beat 5: survival across eras ----------------
  const out5 = P - 24;
  const eras = [
    { x: 300, who: "Dioscorides", when: "1st c.", t: E + 50 },
    { x: 740, who: "Galen", when: "2nd c.", t: E + 84 },
    { x: 1180, who: "John the Physician", when: "13th c.", t: E + 114 },
    { x: 1620, who: "Greek villages", when: "today", t: E + 162 },
  ];

  // ---------------- beat 6: does history predict science ----------------
  const qPulse = 0.62 + 0.3 * Math.sin((f - P) / 9);

  return (
    <Stage glow="none">
      {/* ===== beat 1 ===== */}
      {f < out1 + 16 && (
        <AbsoluteFill style={{ opacity: b1, scale: `${1 + f * 0.00012}` }}>
          <div style={abs({ top: 770, left: SAFE, width: 1920 - 2 * SAFE, height: 1, background: C.dim, opacity: 0.35 })} />
          {/* the printed Dioscorides page on her desk */}
          <div style={abs({ left: 170, top: 770 - 250, width: 171, height: 250, rotate: "-4deg", transformOrigin: "bottom left", boxShadow: "0 20px 40px rgba(0,0,0,.8)", translate: `0px ${-f * 0.03}px` })}>
            <Img src={staticFile("media/folio-apsinthion.webp")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: MUTE }} />
          </div>
          <Words text="Eleni" at={A + 4} size={160} style={abs({ left: SAFE, top: 160 })} />
          <div style={abs({ left: SAFE + 6, top: 362, fontFamily: MONO, fontSize: 30, color: C.dim })}>
            <span style={{ opacity: ease(f, A + 32, A + 44, 0, 1) }}>pharmacognosy PhD</span>
            <span style={{ opacity: ease(f, A + 92, A + 104, 0, 1) }}> · Athens</span>
          </div>
          <Cite style={abs({ left: SAFE + 6, top: 414 })} opacity={ease(f, A + 14, A + 28, 0, 1) as number}>
            {fictional}
          </Cite>
          <div style={abs({ left: 862, top: 392, display: "flex", alignItems: "baseline", gap: 22, opacity: ease(f, A + 150, A + 160, 0, 1) })}>
            <CountUp to={10} at={A + 150} dur={18} size={128} color={C.paper} />
            <span style={{ fontFamily: MONO, fontSize: 32, color: C.dim }}>extracts / year</span>
          </div>
          {Array.from({ length: 10 }).map((_, i) => (
            <Vial key={i} draw={ease(f, A + 150 + i * 3, A + 172 + i * 3, 0, 1) as number} color={C.paper} style={abs({ left: 868 + i * 92, top: 770 - 192 })} />
          ))}
        </AbsoluteFill>
      )}

      {/* ===== beat 2 ===== */}
      {f >= in2 && f < out2 + 16 && (
        <AbsoluteFill style={{ opacity: b2, scale: `${1 + (f - in2) * 0.0001}` }}>
          {folios.map((fo, i) => {
            const k = i - 1.5;
            const enter = ease(f, in2 + i * 4, in2 + 22 + i * 4, 0, 1) as number;
            const isLead = i === 2;
            return (
              <div
                key={fo}
                style={abs({
                  left: 1340 - 180, top: 830 - 540, width: 360, height: 540, transformOrigin: "50% 100%",
                  rotate: `${k * 15 * fan + Math.sin((f + i * 40) / 70) * 0.6}deg`,
                  translate: `${k * 60 * fan}px ${(1 - enter) * 120 - (isLead ? lead * 40 : 0)}px`,
                  opacity: enter, boxShadow: "0 30px 60px rgba(0,0,0,.85)", zIndex: isLead ? 2 : 1,
                })}
              >
                <Img src={staticFile(`media/${fo}.webp`)} style={{ width: "100%", height: "100%", objectFit: "cover", display: "block", filter: isLead ? `saturate(.12) brightness(${0.78 + 0.2 * lead})` : MUTE }} />
              </div>
            );
          })}
          <Words text="De materia medica" at={B + 84} size={100} style={abs({ left: SAFE, top: 196, width: 760 })} />
          <div style={abs({ left: SAFE + 4, top: 432, fontFamily: MONO, fontSize: 28, color: C.dim, opacity: ease(f, B + 148, B + 160, 0, 1) })}>Dioscorides · 1st century AD</div>
          <Words text="copied by hand for 1,500 years" at={B + 184} size={46} weight={400} color={C.dim} stagger={3} style={abs({ left: SAFE, top: 494, width: 760 })} />
          <div style={abs({ left: SAFE, top: 590, display: "flex", alignItems: "baseline", gap: 20 })}>
            <CountUp to={600} prefix="≈" at={B + 288} dur={26} size={130} color={C.paper} />
            <span style={{ fontFamily: OUTFIT, fontSize: 46, color: C.dim, opacity: ease(f, B + 296, B + 308, 0, 1) }}>plants</span>
          </div>
          <Cite style={abs({ left: SAFE + 4, top: 790, fontSize: 16 })} opacity={ease(f, in2 + 30, in2 + 44, 0, 1) as number}>
            Vienna Dioscorides, c. AD 512 · public domain
          </Cite>
        </AbsoluteFill>
      )}

      {/* ===== beat 3: one name, three plants ===== */}
      {f >= N - 6 && f < W + 34 && (
        <AbsoluteFill style={{ scale: `${1 + (f - N) * 0.0001}` }}>
          <div style={{ opacity: ease(f, W - 6, W + 8, 1, 0, EASE_IN) }}>
            <Label n="01" text="the names" at={N} />
            <div style={abs({ left: 0, right: 0, top: 96, textAlign: "center" })}>
              <span lang="grc" style={{ fontFamily: DIDOT, fontSize: 150, color: C.paper, lineHeight: 1.2 }}>
                {greek.split("").map((ch, i) => {
                  const s = N + 22 + i * 3;
                  return (
                    <span key={i} style={{ opacity: ease(f, s, s + 8, 0, 1), filter: `blur(${ease(f, s, s + 10, 8, 0)}px)` }}>
                      {ch}
                    </span>
                  );
                })}
              </span>
            </div>
            <div style={abs({ left: 0, right: 0, top: 300, textAlign: "center", fontFamily: MONO, fontSize: 24, color: C.dim, opacity: ease(f, N + 44, N + 56, 0, 1) })}>
              asphodelos · De materia medica 2.169
            </div>
          </div>
          <Cite style={abs({ left: 0, right: 0, top: 834, textAlign: "center", fontSize: 16 })} opacity={life(f, N + 90, W - 8)}>
            Photos: Wikimedia Commons · names per LSJ and Lardos et al. 2024 (as recorded in Pharmakon's data)
          </Cite>
          {cards.map((c, i) => {
            const enter = ease(f, N + 46 + i * 6, N + 68 + i * 6, 0, 1) as number;
            const lit = f >= c.cue;
            const next = i < 2 ? cards[i + 1].cue : allLit;
            const focus = f >= c.cue && f < next ? 1 : f >= allLit ? 1 : f < cards[0].cue ? 1 : 0.42;
            const op = ease(f, c.cue - 4, c.cue + 8, 0, 1) as number;
            return (
              <div
                key={c.ph.species}
                style={abs({
                  left: 240 + i * 500, top: 388, width: 440, height: 430, borderRadius: 24, overflow: "hidden",
                  background: C.card, border: `1px solid ${lit && focus === 1 && f < allLit ? C.dim : C.rule}`,
                  opacity: enter * (0.35 + 0.65 * focus) * (1 - fall), filter: `blur(${(1 - enter) * 8}px)`,
                  translate: `${(i - 1) * 40 * fall}px ${(1 - enter) * 70 + fall * 280}px`, rotate: `${(i - 1) * 9 * fall + (i - 1) * 0.4}deg`,
                })}
              >
                <div style={{ height: 290, overflow: "hidden" }}>
                  <Photo src={c.ph.url} style={{ filter: lit ? "saturate(.4) brightness(.9)" : MUTE, scale: `${1.04 + (f - N) * 0.00012}` }} />
                </div>
                <div style={{ padding: "16px 22px" }}>
                  <div style={{ fontFamily: MONO, fontSize: 19, color: C.dim, opacity: op }}>{c.src} →</div>
                  <div style={{ fontFamily: OUTFIT, fontStyle: "italic", fontSize: 34, color: C.paper, marginTop: 4, height: 44 }}>
                    {lit ? (
                      <span style={{ opacity: op, filter: `blur(${ease(f, c.cue - 4, c.cue + 8, 6, 0)}px)`, display: "inline-block" }}>{c.ph.species}</span>
                    ) : (
                      <span style={{ fontStyle: "normal", color: C.dim, fontWeight: 300 }}>?</span>
                    )}
                  </div>
                  <div style={{ fontFamily: MONO, fontSize: 15, color: C.dim, opacity: 0.7, marginTop: 14 }}>
                    © {c.ph.author} · {c.ph.licence}
                  </div>
                </div>
              </div>
            );
          })}
        </AbsoluteFill>
      )}

      {/* ===== beat 4: wrong plant = wasted year ===== */}
      {f >= W + 4 && f < out4 + 16 && (
        <AbsoluteFill style={{ opacity: life(f, W + 4, out4), scale: `${1 + (f - W) * 0.00015}` }}>
          {Array.from({ length: 10 }).map((_, i) => (
            <Vial key={i} w={60} h={220} draw={ease(f, W + 10 + i * 2, W + 30 + i * 2, 0, 1) as number} color={C.paper}
              style={abs({ left: 462 + i * 104, top: 270, opacity: 1 - 0.55 * strike })} />
          ))}
          <svg width={1920} height={1080} style={abs({ left: 0, top: 0 })}>
            <line x1={410} y1={470} x2={1510} y2={300} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - strike} stroke={C.warn} strokeWidth={7} strokeLinecap="round" />
          </svg>
          <div style={abs({ left: 0, right: 0, top: 600, display: "flex", justifyContent: "center", gap: 26 })}>
            <Words text="Wrong plant" at={W + 16} size={96} />
            <Words text="= a wasted year" at={W + 80} size={96} color={C.dim} />
          </div>
        </AbsoluteFill>
      )}

      {/* ===== beat 5: did the remedies survive? ===== */}
      {f >= E - 4 && f < out5 + 16 && (
        <AbsoluteFill style={{ opacity: life(f, E - 4, out5), scale: `${1 + (f - E) * 0.0001}` }}>
          <Label n="02" text="survival" at={E} />
          <Words text="Which remedies survived?" at={E + 26} size={92} style={abs({ left: SAFE, top: 168 })} />
          {eras.slice(0, 3).map((e, i) => {
            const nx = eras[i + 1];
            const len = (ease(f, nx.t - 16, nx.t + 2, 0, 1) as number) * (nx.x - e.x - 64);
            return (
              <div key={i} style={abs({ left: e.x + 32, top: 541, width: len, height: 0, borderTop: `2px dashed ${C.dim}`, opacity: 0.6 })} />
            );
          })}
          {eras.map((e) => {
            const on = ease(f, e.t - 4, e.t + 8, 0, 1) as number;
            const pop = 1 + 0.18 * Math.sin(Math.PI * (ease(f, e.t - 4, e.t + 10, 0, 1, (x) => x) as number));
            return (
              <React.Fragment key={e.who}>
                <div style={abs({ left: e.x - 260, width: 520, top: 430, textAlign: "center", fontFamily: OUTFIT, fontWeight: 500, fontSize: 36, color: C.paper, opacity: on, translate: `0px ${(1 - on) * 14}px` })}>{e.who}</div>
                <div
                  style={abs({
                    left: e.x - 32, top: 510, width: 64, height: 64, borderRadius: 999, border: `2px solid ${on > 0.5 ? C.paper : C.rule}`,
                    display: "flex", alignItems: "center", justifyContent: "center", fontFamily: OUTFIT, fontWeight: 300, fontSize: 36,
                    color: on > 0.5 ? C.paper : C.dim, scale: `${pop}`, opacity: 0.4 + 0.6 * on, background: C.ink,
                  })}
                >
                  ?
                </div>
                <div style={abs({ left: e.x - 200, width: 400, top: 590, textAlign: "center", fontFamily: MONO, fontSize: 22, color: C.dim, opacity: on })}>{e.when}</div>
              </React.Fragment>
            );
          })}
          <Words text="Traced by hand." at={E + 230} size={64} style={abs({ left: 0, right: 0, top: 676, justifyContent: "center" })} />
          <svg width={540} height={30} viewBox="0 0 540 30" style={abs({ left: 960 - 270, top: 760 })}>
            <path d="M6 18 C80 8 150 24 230 14 S380 6 440 17 S510 20 534 12" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - (ease(f, E + 240, E + 262, 0, 1) as number)} fill="none" stroke={C.dim} strokeWidth={3} strokeLinecap="round" />
          </svg>
          <div style={abs({ left: 0, right: 0, top: 800, textAlign: "center", fontFamily: MONO, fontSize: 24, color: C.dim, opacity: ease(f, E + 268, E + 280, 0, 1) })}>one plant at a time</div>
        </AbsoluteFill>
      )}

      {/* ===== beat 6: does history predict science? ===== */}
      {f >= P - 4 && (
        <AbsoluteFill style={{ opacity: ease(f, P - 4, P + 8, 0, 1), scale: `${1 + (f - P) * 0.00012}` }}>
          <Label n="03" text="prediction" at={P} />
          <Words text="Does history predict science?" at={P + 10} size={96} style={abs({ left: 0, right: 0, top: 220, justifyContent: "center" })} />
          {[
            { x: 420, t: "ancient use", s: "Dioscorides", at: P + 60 },
            { x: 1500, t: "later science", s: "what got studied", at: P + 86 },
          ].map((n) => (
            <div key={n.t} style={abs({ left: n.x - 220, width: 440, top: 500, textAlign: "center", opacity: ease(f, n.at, n.at + 12, 0, 1), translate: `0px ${ease(f, n.at, n.at + 16, 18, 0)}px` })}>
              <div style={{ fontFamily: OUTFIT, fontWeight: 500, fontSize: 44, color: C.paper }}>{n.t}</div>
              <div style={{ fontFamily: MONO, fontSize: 22, color: C.dim, marginTop: 6 }}>{n.s}</div>
            </div>
          ))}
          {/* a bridge that never closes */}
          <div style={abs({ left: 640, top: 530, width: ease(f, P + 66, P + 96, 0, 230), borderTop: `2px dashed ${C.dim}`, opacity: 0.8 })} />
          <div style={abs({ left: 1050, top: 530, width: 230, borderTop: `2px dashed ${C.rule}`, opacity: ease(f, P + 90, P + 110, 0, 1) })} />
          <div
            style={abs({
              left: 960 - 80, width: 160, top: 440, textAlign: "center", fontFamily: OUTFIT, fontWeight: 300, fontSize: 150, lineHeight: 1, color: C.dim,
              opacity: (ease(f, P + 94, P + 108, 0, 1) as number) * qPulse, filter: `blur(${1.6 - 1.6 * qPulse}px)`, rotate: `${Math.sin((f - P) / 23) * 4}deg`,
            })}
          >
            ?
          </div>
          <div style={abs({ left: 0, right: 0, top: 720, textAlign: "center", fontFamily: MONO, fontSize: 26, color: C.dim, letterSpacing: "0.04em", opacity: ease(f, P + 182, P + 196, 0, 1) })}>
            rarely tested honestly
          </div>
        </AbsoluteFill>
      )}
    </Stage>
  );
};
