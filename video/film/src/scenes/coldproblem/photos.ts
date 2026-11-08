// Real plant photographs (Wikimedia Commons), URLs copied from the pipeline's own data:
// asphodel candidates from public/data/dmm-2-169.json, the rest from web/public/data/leads.json (lead species; toxicity flags as of the 2026-11-08 re-run).
// width= changed 640 -> 800. Author + licence fetched from the Commons API (imageinfo extmetadata), 2026-11-08.
export type PlantPhoto = { species: string; url: string; author: string; licence: string };

const fp = (file: string) => `https://commons.wikimedia.org/wiki/Special:FilePath/${file}?width=800`;

export const ASPHODEL = {
  ramosus: { species: "Asphodelus ramosus", url: fp("Asphodelus%20ramosus%E2%80%93IMG%206020.jpg"), author: "Kızıl", licence: "CC BY-SA 4.0" },
  aestivus: { species: "Asphodelus aestivus", url: fp("Asphodelus%20aestivus%205.jpg"), author: "Zeynel Cebeci", licence: "CC BY-SA 4.0" },
  fistulosus: { species: "Asphodelus fistulosus", url: fp("Asphodelus%20fistulosus%20-%20Onionweed%2002.jpg"), author: "Zeynel Cebeci", licence: "CC BY-SA 4.0" },
} satisfies Record<string, PlantPhoto>;

export const MOSAIC: PlantPhoto[] = [
  { species: "Artemisia absinthium", url: fp("Artemisia%20absinthium%20P1210748.jpg"), author: "David Monniaux", licence: "CC BY-SA 3.0" },
  { species: "Punica granatum", url: fp("Punica%20granatum%20004.JPG"), author: "H. Zell", licence: "CC BY-SA 3.0" },
  { species: "Pistacia terebinthus", url: fp("20090729%20parnonas10.jpg"), author: "Jean Housen", licence: "CC BY-SA 3.0" },
  { species: "Vitex agnus-castus", url: fp("Vitex%20agnus-castus%20%2815390963576%29.jpg"), author: "peganum from Henfield, England", licence: "CC BY-SA 2.0" },
  { species: "Centaurium erythraea", url: fp("Centaurium%20erythraea%20%28flowers%29.jpg"), author: "Hans Hillewaert", licence: "CC BY-SA 3.0" },
  { species: "Quercus coccifera", url: fp("Quercus%20coccifera%20Bellotas%202010-10-03%20DehesaBoyaldePuertollano.jpg"), author: "Javier martin", licence: "Public domain" },
  { species: "Achillea millefolium", url: fp("Achillea%20millefolium%20vallee-de-grace-amiens%2080%2022062007%201.jpg"), author: "O. Pichard", licence: "CC BY-SA 3.0" },
  { species: "Iris pseudacorus", url: fp("Iris%20pseudacorus%20001.jpg"), author: "Jean-Jacques MILAN", licence: "CC BY-SA 3.0" },
];
