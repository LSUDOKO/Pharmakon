// Scene "motivation" — real plant photographs (Wikimedia Commons, URLs from Pharmakon's own leads data) in a slow
// parallax mosaic; "Documented for 2,000 years. Rarely tested." Still restrained colour: verdigris arrives in the Turn.
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, MONO, OUTFIT, SAFE, Stage, Words, ease } from "../brand";
import { Cite, Photo, cue } from "./coldproblem/kit";
import { ASPHODEL, MOSAIC, PlantPhoto } from "./coldproblem/photos";
import { at } from "./results/data";

const ID = "motivation";
const COLS: { x: number; y0: number; dir: number; tiles: { ph: PlantPhoto; h: number }[] }[] = [
  { x: 860, y0: -60, dir: -1, tiles: [{ ph: MOSAIC[0], h: 440 }, { ph: MOSAIC[4], h: 360 }, { ph: MOSAIC[5], h: 400 }] },
  { x: 1210, y0: -120, dir: 1, tiles: [{ ph: MOSAIC[1], h: 360 }, { ph: MOSAIC[2], h: 460 }, { ph: MOSAIC[6], h: 380 }] },
  { x: 1560, y0: -40, dir: -1, tiles: [{ ph: MOSAIC[3], h: 420 }, { ph: ASPHODEL.aestivus, h: 380 }, { ph: MOSAIC[7], h: 400 }] },
];

export const Motivation: React.FC = () => {
  const f = useCurrentFrame();
  const A = cue(ID, 0);
  const tDoc = at(ID, "s04_a", "documented");
  const tNever = at(ID, "s04_a", "none of it");
  const dimFirst = ease(f, tNever, tNever + 16, 1, 0.45) as number;

  return (
    <Stage glow="none">
      {COLS.map((col, ci) => {
        let y = col.y0 + col.dir * f * 0.14;
        return col.tiles.map((t, ti) => {
          const top = y;
          y += t.h + 20;
          const s = ci * 4 + ti * 6 - 16;
          const enter = ease(f, s, s + 26, 0, 1) as number;
          return (
            <div
              key={`${ci}-${ti}`}
              style={{
                position: "absolute", left: col.x, top, width: 330, height: t.h, borderRadius: 22, overflow: "hidden", background: C.card,
                opacity: enter, scale: `${1.06 - 0.06 * enter}`, filter: `blur(${(1 - enter) * 10}px)`,
              }}
            >
              <Photo src={t.ph.url} style={{ filter: "saturate(.55) brightness(.82)", scale: `${1.02 + 0.03 * (f / 496)}` }} />
              <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "40px 18px 14px", background: "linear-gradient(180deg, transparent, rgba(0,0,0,.78))" }}>
                <div style={{ fontFamily: OUTFIT, fontStyle: "italic", fontSize: 22, color: C.paper }}>{t.ph.species}</div>
                <div style={{ fontFamily: MONO, fontSize: 15, color: C.dim, marginTop: 3, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  © {t.ph.author} · {t.ph.licence}
                </div>
              </div>
            </div>
          );
        });
      })}
      {/* fade the mosaic's left edge into the black text column */}
      <AbsoluteFill style={{ background: "linear-gradient(90deg, #000 0%, #000 42%, rgba(0,0,0,0) 50%)" }} />
      <div style={{ position: "absolute", left: SAFE, top: 236, width: 640 }}>
        <div style={{ fontFamily: MONO, fontSize: 22, color: C.dim, letterSpacing: "0.12em", textTransform: "uppercase", opacity: ease(f, A + 4, A + 16, 0, 1) }}>why it matters</div>
        <div style={{ marginTop: 34, opacity: dimFirst }}>
          <Words text="Documented for 2,000 years." at={tDoc - 4} size={88} stagger={4} />
        </div>
        <div style={{ marginTop: 40 }}>
          <Words text="Rarely tested." at={tNever - 4} size={88} stagger={5} />
        </div>
      </div>
      <Cite style={{ position: "absolute", left: SAFE, top: 812, fontSize: 16 }} opacity={ease(f, 40, 56, 0, 1) as number}>
        Photos: Wikimedia Commons · species from Pharmakon's leads and candidates
      </Cite>
    </Stage>
  );
};
