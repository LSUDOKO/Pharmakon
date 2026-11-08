// Scene "data" — s06_a: one chain of texts (4 eras, real counts). s06_b: eight open databases, each verified live, licence recorded.
import React from "react";
import { useCurrentFrame } from "remotion";
import { C, CountUp, EASE_IN, MONO, OUTFIT, SAFE, Stage, Words, ease } from "../brand";
import { line } from "../timing";
import { Chip, CornerSheet, Kicker, Tick, at } from "./datamethod/ui";
import texts from "../../public/data/ingest-texts.json";
import galen from "../../public/data/ingest-galen.json";
import gold from "../../public/data/gold.json";
import persistence from "../../public/data/persistence.json";
import chem from "../../public/data/link-chemistry.json";
import mesh from "../../public/data/map-conditions.json";
import labels from "../../public/data/evidence-labels.json";
import leads from "../../public/data/leads.json";

const A = line("data", "s06_a").from;
const B = line("data", "s06_b").from;

// word-landed beats (whisper word timestamps on the VO)
const ERAS = [
  { era: "1st c. AD", who: "Dioscorides", n: texts.passages, unit: "passages", name: at(A, 3.1), num: at(A, 5.1) },
  { era: "2nd c.", who: "Galen", n: galen.drug_entries, unit: "drug entries", name: at(A, 6.9), num: at(A, 8.2) },
  { era: "13th c.", who: "John the Physician", n: gold.gold_names, unit: "expert-identified names", name: at(A, 10.7), num: at(A, 13.5) },
  { era: "today", who: "Greek villages", n: persistence.modern_records, unit: "village records", name: at(A, 15.4), num: at(A, 15.8) },
];
const COLX = [330, 750, 1170, 1590];

// licences verbatim from docs/licences.md; numbers from public/data
const DBS: { name: string; role: string; n?: number; lic: string; on: number }[] = [
  { name: "GBIF", role: "where each plant grows", lic: "CC BY 4.0", on: at(B, 2.4) },
  { name: "Wikidata · LOTUS", role: "plant compounds", n: chem.distinct_compounds, lic: "CC0", on: at(B, 3.1) },
  { name: "ChEMBL", role: "human protein targets", n: chem.human_targets, lic: "CC BY-SA 3.0", on: at(B, 5.3) },
  { name: "Open Targets", role: "target–disease links", n: chem.target_disease_rows, lic: "CC0", on: at(B, 6.4) },
  { name: "NLM MeSH", role: "verified conditions", n: mesh.distinct_mesh_ids, lic: "public domain", on: at(B, 6.6) },
  { name: "PubMed", role: "plant–disease pairs searched", n: labels.pairs, lic: "NLM terms", on: at(B, 7.4) },
  { name: "PubChem", role: "toxic genera verified", n: leads.toxic_genera_verified_in_pubchem, lic: "public domain", on: at(B, 8.4) },
  { name: "LSJ · Perseus", role: "Greek dictionary baseline", lic: "CC BY-SA 4.0", on: at(B, 8.9) },
];
const CHECKED = at(B, 9.3);
const LICENSED = at(B, 10.6);

const Timeline: React.FC = () => {
  const f = useCurrentFrame();
  // compress to the top when the databases arrive
  const k = ease(f, B - 10, B + 22, 0, 1) as number;
  const scale = 1 - 0.4 * k;
  const y = 360 - 266 * k;
  return (
    <div style={{ position: "absolute", left: 0, top: y, width: 1920, height: 440, scale: `${scale}`, transformOrigin: "960px 0px" }}>
      {/* rail */}
      <svg width={1920} height={440} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
        <line x1={COLX[0]} y1={150} x2={COLX[3]} y2={150} stroke={C.rule} strokeWidth={2} strokeDasharray="4 8" />
        {ERAS.slice(1).map((e, i) => {
          const p = ease(f, e.name - 14, e.name + 10, 0, 1) as number;
          return <line key={i} x1={COLX[i]} y1={150} x2={COLX[i] + (COLX[i + 1] - COLX[i]) * p} y2={150} stroke={C.verdigris} strokeWidth={3} />;
        })}
        {ERAS.map((e, i) => {
          const lit = ease(f, e.name, e.name + 10, 0, 1) as number;
          const ring = (f - e.name) / 30;
          return (
            <g key={i}>
              {ring > 0 && ring < 1 && <circle cx={COLX[i]} cy={150} r={14 + ring * 46} fill="none" stroke={C.hi} strokeOpacity={1 - ring} strokeWidth={2} />}
              <circle cx={COLX[i]} cy={150} r={13} fill={lit > 0.5 ? C.hi : C.ink} stroke={lit > 0 ? C.hi : C.rule} strokeWidth={3} />
            </g>
          );
        })}
      </svg>
      {ERAS.map((e, i) => {
        const o = ease(f, e.name, e.name + 14, 0, 1) as number;
        return (
          <div key={i} style={{ position: "absolute", left: COLX[i] - 200, width: 400, top: 0, textAlign: "center", opacity: 0.25 + 0.75 * o }}>
            <div style={{ fontFamily: MONO, fontSize: 24, color: o > 0.5 ? C.lichen : C.dim, letterSpacing: "0.08em", height: 110, paddingTop: 70 }}>{e.era}</div>
            <div style={{ height: 80 }} />
            <div style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 40, letterSpacing: "-0.02em", color: C.paper, translate: `0px ${(1 - o) * 20}px` }}>{e.who}</div>
            <div style={{ height: 104, marginTop: 6 }}>{f >= e.num && <CountUp to={e.n} at={e.num} dur={26} size={92} />}</div>
            <div style={{ fontFamily: OUTFIT, fontSize: 27, color: C.dim, marginTop: 8, opacity: ease(f, e.num + 8, e.num + 20, 0, 1) as number }}>{e.unit}</div>
          </div>
        );
      })}
    </div>
  );
};

const Tile: React.FC<{ d: (typeof DBS)[number]; i: number }> = ({ d, i }) => {
  const f = useCurrentFrame();
  const enter = B + 26 + i * 4;
  const o = ease(f, enter, enter + 16, 0, 1) as number;
  const lit = ease(f, d.on, d.on + 12, 0, 1) as number;
  const tick = ease(f, CHECKED + i * 3, CHECKED + i * 3 + 10, 0, 1) as number;
  const lic = ease(f, LICENSED + i * 3, LICENSED + i * 3 + 10, 0, 1) as number;
  const col = i % 4;
  const row = Math.floor(i / 4);
  return (
    <div
      style={{
        position: "absolute", left: SAFE + col * 426, top: 404 + row * 226, width: 402, height: 208, boxSizing: "border-box",
        background: C.card, borderRadius: 24, padding: "24px 26px",
        border: `1px solid ${lit > 0.5 ? "rgba(61,187,130,.55)" : C.rule}`,
        boxShadow: `0 0 ${40 * lit}px rgba(23,116,79,${0.28 * lit})`,
        opacity: o, translate: `0px ${(1 - o) * 60}px`, rotate: `${(1 - o) * (col - 1.5) * 1.2}deg`,
        display: "flex", flexDirection: "column", justifyContent: "space-between",
      }}
    >
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 32, letterSpacing: "-0.02em", color: C.paper }}>{d.name}</div>
          <div style={{ opacity: tick, scale: `${0.6 + 0.4 * tick}` }}><Tick size={30} draw={tick} /></div>
        </div>
        <div style={{ fontFamily: OUTFIT, fontSize: 23, color: lit > 0.5 ? C.lichen : C.dim, marginTop: 4 }}>{d.role}</div>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
        <div style={{ height: 52 }}>{d.n !== undefined && f >= d.on && <CountUp to={d.n} at={d.on} dur={22} size={46} color={C.hi} />}</div>
        <Chip color={lic > 0.5 ? C.lichen : C.dim} style={{ borderColor: lic > 0.5 ? C.verdigris : C.rule, background: lic > 0.5 ? "rgba(23,116,79,.18)" : "transparent" }}>{d.lic}</Chip>
      </div>
    </div>
  );
};

export const Data: React.FC = () => {
  const f = useCurrentFrame();
  const tilesOut = 1102; // scene end; Film.tsx wipes out
  return (
    <Stage glow="tr">
      <CornerSheet img="media/folio-glukurizon.webp" dx={420} dy={-260} />
      <div style={{ position: "absolute", left: SAFE, top: 92 }}>
        <Kicker>The data</Kicker>
      </div>
      <div style={{ position: "absolute", left: SAFE, top: 146, width: 1300 }}>
        <Words text="One unbroken chain of texts." at={A + 14} size={76} accent={["unbroken"]} out={B - 18} />
      </div>
      <Timeline />
      {f >= B && (
        <>
          <div style={{ position: "absolute", left: SAFE, top: 334, opacity: (ease(f, B + 20, B + 34, 0, 1) as number) * (ease(f, tilesOut - 6, tilesOut, 1, 0, EASE_IN) as number), display: "flex", alignItems: "baseline", gap: 18 }}>
            <span style={{ fontFamily: OUTFIT, fontWeight: 600, fontSize: 44, letterSpacing: "-0.025em" }}>Eight open databases.</span>
            <span style={{ fontFamily: OUTFIT, fontWeight: 400, fontSize: 30, color: f >= CHECKED ? C.lichen : C.dim }}>
              {f >= LICENSED ? "Checked live. Licence recorded." : f >= CHECKED ? "Checked live." : ""}
            </span>
          </div>
          {DBS.map((d, i) => <Tile key={d.name} d={d} i={i} />)}
        </>
      )}
    </Stage>
  );
};
