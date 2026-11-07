# Frontend plan — pharmakon.pages.dev

## Concept
**Verdigris herbarium × torn paper.** The reference brand (black field, torn paper sheets, hatched band, chrome
wordmark, construction lines with dimension callouts) is translated to the subject:
- the torn sheets are **verdigris green** paper — ἰὸς ξυστός, the copper-green pigment Dioscorides describes in book V;
- printed on them, as a cyanotype-style "verdigris print", are folios of the **Vienna Dioscorides** (6th c., public domain);
- the dimension callouts carry the real pipeline numbers (1,500 passages, 61 expert names, …).

## Tokens
| name | hex | role |
|---|---|---|
| ink | #000000 | page field |
| verdigris | #17744F | paper, primary accent |
| verdigris-hi | #3DBB82 | data highlight, focus |
| lichen | #B8E6CC | light text on green, probability bars |
| paper | #ECEEE7 | torn fringe, body text on black |
| hatch | #1E1E1E | hatched band, rules |
| warning | #FF5A5F | known-toxicity badge only |

Type: **Outfit** (wordmark, UI, body), **GFS Didot** (all Greek text, historical voice), **JetBrains Mono**
(dimension callouts only — the construction-line motif from the brand reference).

## Layout
```
[hero: black field · torn green sheets (live folio video inside) · hatched band · chrome wordmark + dimensions · glass CTAs]
[one word, three plants: folio | live probability bars for ἀψίνθιον]
[pipeline: 7 steps as a measured timeline with real counts]
[explorer: search ▸ list | passage (Didot, highlighted spans) · candidates with Commons photos · era strip]
[two thousand years: alluvial DMM → Galen → JC → modern + permutation null]
[identification: model vs baselines with CIs · reliability]
[time machine: AUPRC by cutoff with CIs · honest null · hits]
[leads: filterable table, photos, toxicity badges, CSV, evidence paths]
[data & integrity: sources, licences, limitations, credits]
```
Left-aligned text; the hero is the only centred composition.

## Principles
- One orchestrated motion moment (hero tear-in + chrome sweep). Everything else moves only in response to the user.
- Liquid-glass controls (blurred, specular, refractive edge) are the only glossy material; all data surfaces stay flat.
- Every number on the page is loaded from `data/results.json`, exported by the pipeline — none typed into HTML.
- Research-only disclaimer is permanent; toxicity is never colour-only (badge + text).
- Responsive to 360 px, keyboard focus visible, `prefers-reduced-motion` respected.

## Build / deploy
Vite static build (`web/`), D3 for charts, data from `python -m pharmakon.web_export`. Deployed with
`wrangler pages deploy web/dist --project-name pharmakon`.
