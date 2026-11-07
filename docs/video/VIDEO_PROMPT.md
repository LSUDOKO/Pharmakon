# Pharmakon — pitch film brief and production prompt

# ROLE
You are a world-class team in one person: award-winning motion designer, film editor, sound designer,
science communicator, product marketer and product manager. You have shipped launch films at the level of
Apple, Google, Anthropic, Linear, Stripe and Vercel, and explainer films for research institutes. You think
in story first, then pacing, then frames. Every second must earn its place. This film is judged by
pharmacognosists, a historian of Byzantine pharmacology and data scientists: scientific honesty is part of
the craft, not a constraint on it.

# PROJECT INPUTS (filled in)
- **Product name:** Pharmakon
- **One-line pitch:** Pharmakon reads Dioscorides' 1st-century Greek *De materia medica*, works out which
  modern plant each ancient name means (with honest probabilities), traces every remedy through 2,000 years,
  tests whether history predicts later science, and ranks untested plant–disease leads for the lab.
- **Event:** EthnoHack 2026 — Data Hackathon on Ethnopharmacology & Health, **Track 1: Traditional knowledge**.
  Judging criteria: Scientific Relevance · Innovation · Technical Implementation · Data Science Quality ·
  Feasibility · Impact · Presentation. Also eligible for: Best Scientific Rigor, Best AI Solution.
- **Required video content (hackathon rules, max 10:00):** the problem · motivation · approach · technology ·
  data · results · a demonstration · potential impact · future development. Assumptions, limitations and
  uncertainty must be stated. Unvalidated findings must never be presented as medical fact.
- **Core technology to showcase deeply (the "engine"):** a verify-first evidence chain —
  1. verbatim-span extraction from Greek (rule lexicon + LLM, every quote re-checked against the source),
  2. a probabilistic identification model P(species | ancient name) with an explicit "unidentified" option and
     a plant-description (morphology) feature,
  3. a knowledge graph linking passage → ancient name → species → compound → human target → disease
     (2,585 nodes, 9,146 edges),
  4. a frozen, leakage-free "time machine" backtest,
  5. delivery as a website, a JSON API and an MCP server any AI assistant can query.
- **Why that tech matters:** ancient names are ambiguous, so every downstream lead is only as good as the
  identification underneath it. Pharmakon carries that uncertainty all the way into the lead ranking
  (it changes 5 of the top 20), and every claim can be traced back to the exact Greek words that state it.
- **Target user:** pharmacognosy and natural-product researchers deciding what to screen next; historians of
  medicine; ethnobotanists; conservation scientists.
- **Protagonist (fictional composite — say so in small type on first appearance):** **Eleni**, a pharmacognosy
  PhD student in Athens. Her lab can afford to screen ten plant extracts this year. Her supervisor hands her
  Dioscorides: "Somewhere in here is a lead." She has 600 plant names, translations that disagree about which
  plant each one is, no way to know which remedies survived or were already studied, and a real risk of
  picking a toxic plant.
- **Key features to show (priority order):**
  1. Ancient name explorer: Greek passage with highlighted evidence spans → P(species) bars with 90% intervals →
     plant-description match chips (✓/✗) → four-era survival table → Galen passage → modern Greek village uses.
  2. Leads for the lab: certainty slider, condition filter, hide-toxic toggle, toxicity badges, evidence-path
     dialog (compound → target → disease) with the exact PubMed query, CSV export.
  3. Results: identification vs experts and dictionary; "Through time" alluvial + permutation null;
     the time machine with cutoff toggles and confidence intervals.
  4. Use it: the Pharmakon MCP connector inside **Claude on the web** (real chat, real tool calls), the same server
     in Claude Code, the JSON API (`curl`), the one-command reproduction (`make test`), the GitHub README.
- **All pages to show (live site, in story order):** Hero (torn-paper) → "One word, three plants" →
  How it works → Explorer → Through time → Results → Leads → Use it → Data & limits → footer.
  Plus: **claude.ai in Chrome with the Pharmakon connector**, a Claude Code terminal with the same MCP server,
  a `curl` to `/api`, the GitHub repo/README, a terminal running `make test`.
- **Live URLs:** site https://pharmakon.adoranto737.workers.dev · MCP https://pharmakon.adoranto737.workers.dev/mcp ·
  API https://pharmakon.adoranto737.workers.dev/api · repo https://github.com/LSUDOKO/Pharmakon
- **Local run:** `cd web && npm install && npm run dev` (site) · `make app` (Streamlit dashboard) · `make test`.
- **Test account / seed data:** none needed — the site is public and read-only. The "seed data" is the real
  pipeline output in `web/public/data/` (653 names, 1,781 leads). Never fabricate records.
- **Team names:** [TEAM MEMBER NAMES + ROLES — required by the hackathon; add before render]
- **Target length:** **8:00–9:00** (hard maximum 10:00 by the rules). Take the time to cover every required item.
- **Voice-over:** English, calm-confident founder-scientist, warm, unhurried. One narrator.
  Generated with **Sarvam AI TTS** (`bulbul:v3`), key already in `.env` as `sarvam_api_key` — never print it.
- **MCP in a real AI product:** the Pharmakon MCP server is already added as a custom connector in
  **Claude on the web (claude.ai)**, used through the user's own logged-in Chrome. The film shows it working
  there for real, plus Claude Code in a terminal.

# BRAND THEME (use exactly — no tool defaults anywhere)
| token | hex | use |
|---|---|---|
| Ink (background) | `#000000` | every frame's base; true black, not #111 |
| Card | `#0B120E` | panels, callouts, lower thirds |
| Rule | `#1F2C25` | hairlines, grid, dividers |
| Hatch | `#1E1E1E` | the hatched band behind the wordmark (135° lines, 1 px every 7 px) |
| **Verdigris (primary)** | `#17744F` | torn sheets, fills, structure, the "solution" colour |
| **Verdigris-hi (accent)** | `#3DBB82` | answers, the active word, cursor ripple, probability bars — use sparingly |
| Lichen (secondary) | `#B8E6CC` | soft labels, graph edges, secondary text on dark |
| Paper (text / torn fibre edge) | `#ECEEE7` | headlines, torn-paper fringe |
| Paper-dim (muted) | `#A9B0AB` | captions, sources, small print |
| Warn (toxicity ONLY) | `#FF5A5F` | toxicity badges and "history hurts" — never decorative |

- **Chrome wordmark gradient:** `linear-gradient(180deg, #FFFFFF 0%, #DFE3E0 45%, #8B938F 62%, #F3F5F4 100%)`.
- **Fonts:** **Outfit** (headlines 500–600, tight tracking −0.02 to −0.045em; body 300–400) ·
  **GFS Didot** (all ancient Greek, never substitute) · **JetBrains Mono** (numbers, data, code, CTS URNs,
  dimension labels). All from Google Fonts; embed in renders.
- **Logo files:** `web/public/media/mark.svg` (chrome arrows mark), `docs/media/logo-dark.png`,
  `docs/media/logo-light.png`, `web/public/favicon.svg`.
- **Corner radius:** 22–26 px on cards, 999 px on pills, 14 px on code blocks — match the site.
- **Liquid-glass buttons:** reuse the site's `.glass` style (translucent, inner highlight, soft verdigris glow)
  for any on-screen button or chip.
- **Texture & depth:** fine paper grain (feTurbulence noise, 4–6% opacity), soft verdigris radial glow in one
  corner, light vignette. No stock footage, no clip art, no lens flares.

# SIGNATURE MOTION: THE TORN-PAPER LANGUAGE (from the landing hero)
The site's hero is the film's visual identity. Rebuild it exactly, then reuse it as the film's transition system.
- **Assets (use the real files):** `web/public/media/tear-a.svg`, `tear-b.svg` (sheet masks),
  `fringe-a.svg`, `fringe-b.svg` (torn fibre edges, feTurbulence + feDisplacementMap), the Vienna Dioscorides
  folios `folio-apsinthion.webp`, `folio-iris.webp`, `folio-glukurizon.webp`, `folio-adianton.webp`,
  `folio-drakontaia.webp` (verdigris-printed, public domain), `hero-loop.mp4` / `hero-poster.jpg`.
  Read `web/src/style.css` (`.sheet`, `.fringe`, `.paper`, `.band`, `.dim`) and `web/src/main.js` (hero intro and
  scroll-linked tearing) and match their geometry, timing and easing.
- **Composition:** two diagonal torn sheets — top-right and bottom-left — printed with verdigris folios, each
  with an off-white fibrous edge (`#ECEEE7`, drop shadow 0 18px 30px rgba(0,0,0,.7)). Between them, a
  black **hatched band** with dashed construction lines running edge to edge, the chrome **pharmakon**
  wordmark with the mark, and engineering **dimension lines** in JetBrains Mono: "1,500 passages read"
  (horizontal) and "61 expert names" (vertical).
- **Title reveal:** sheets start closed (paper covers the frame), a tear rips along the diagonal with a dry
  paper-tear SFX, sheets slide apart with slight rotation and parallax (sheet A up-right, sheet B down-left,
  expo-out 900 ms), the band draws in, dimension lines extend, the wordmark resolves from blur with a chrome
  shimmer sweep, bass hit on the resolve.
- **Transitions:** section changes are torn-paper wipes — a verdigris sheet with a fibrous edge tears across the
  frame and pulls away to reveal the next scene. Vary direction and angle; never the same twice in a row.
  Use match cuts too: a folio's plant drawing becomes the explorer's candidate photo; a probability bar
  becomes a graph edge; a torn edge becomes the chart axis.
- **Continuous life:** sheets drift 1–2 px/s with parallax; folio images breathe (scale 1.00 → 1.02 over 8 s).

# THE GOAL
An 8–9 minute cinematic film that feels like a story, not a screen recording, and ticks every hackathon
requirement. A judge should finish it thinking: "This is a real problem in my field, the method is rigorous,
it works, and they were honest about what didn't work."
NOT acceptable: scrolling recordings, a few fades, voice-over on top, then an end card.

# STORY STRUCTURE (≈ 8:30)
Follow Eleni through the whole film. Each section continues her story and covers a required item.

| # | Section | Time | Hackathon item | Purpose | Visual treatment |
|---|---|---|---|---|---|
| 1 | Cold open | 0:00–0:20 | motivation | Real fact hook: in 2015 a Nobel Prize recognised artemisinin, found by reading a 4th-century Chinese medical handbook. Europe has its own handbook. | Kinetic type on black; real Vienna Dioscorides folio pushes in; first paper tear |
| 2 | Title reveal | 0:20–0:35 | — | Pharmakon + tagline "2,000 years of Greek plant medicine, measured." | Full hero torn-paper rebuild (see above), bass hit |
| 3 | Eleni's problem | 0:35–1:45 | problem | Ten extracts, 600 names. Make the three blockers felt with REAL images (see "Real proof"). | Folio fragments, real competing identifications, a translation that disagrees, a clock; muted palette, tension |
| 4 | Why it matters | 1:45–2:10 | motivation | Drugs from plants; the Greek tradition is one of the best-documented in the world, yet almost untested; respect for the communities who kept it alive. | Real plant photos, modern Greek village record cards, map of Greece |
| 5 | The turn | 2:10–2:30 | approach | One sentence: what Pharmakon does. | Fragments snap into the explorer layout; palette shifts muted → verdigris; music lifts |
| 6 | The data | 2:30–3:10 | data | One text chain + eight open databases, all licensed and verified. | Animated timeline (1st c. → 2nd c. → 13th c. → today) with real counts; database tiles fly in with licences |
| 7 | How it works | 3:10–4:20 | approach + technology | Read → verify → identify → trace → test → rank. | Pipeline as torn-paper strips; a real Greek clause with the span highlight; the identification model's features as layers; leakage controls as a lock |
| 8 | The walkthrough | 4:20–6:25 | demonstration | Eleni uses the real product to solve her real problem, end to end (longest section). | REAL screen recording with cinematic cursor, zooms, callouts (spec below) |
| 9 | Under the hood | 6:25–6:55 | technology | Make the evidence chain and the knowledge graph visible. | Recording dissolves into graph nodes; a traversal travels Greek span → name → species → compound → target → disease |
| 10 | Results | 6:55–7:45 | results | Identification, survival, the honest null, leads. | Animated charts in brand style built from `reports/stages/*.json` |
| 11 | Impact, limits, future | 7:45–8:15 | impact + future | Before/after for Eleni; who else benefits; what we don't claim; next steps. | Before/after split, benefit cards, limitation cards (calm, not apologetic) |
| 12 | Outro | 8:15–8:35 | — | Return to Eleni; tagline; team; links; disclaimer. | Torn paper closes over the frame into the end card |

Keep the walkthrough the longest section. Total runtime 8:00–9:00, never above 10:00.

# REAL PROOF — every image and every number is real
## Real images for the problem (show, don't tell)
- **Vienna Dioscorides** (Codex Vindobonensis med. gr. 1, c. AD 512) folio scans from Wikimedia Commons
  (public domain) — full-page shots before they become the verdigris folios. Credit on screen.
- **Competing identifications for one name:** take a real gold name from `reports/identification_cards.md`
  where the LSJ dictionary, the expert gold (Lardos et al. 2024) and Pharmakon disagree; show the LSJ binomial,
  the expert's choice and Pharmakon's probability bars side by side.
- **Real plant photographs** of the competing candidates from Wikimedia Commons (licence + author credit per
  file; the URLs are in `web/public/data/names/*.json` → `candidates[].image`).
- **A real PubMed search** for a lead's exact query (from `leads.json → query`) showing it has no matching
  paper — record it live on pubmed.ncbi.nlm.nih.gov.
- **Real Greek text** from `web/public/data/names/dmm-3-23.json` (ἀψίνθιον, wormwood) rendered in GFS Didot.
- Never show photos of real people (no licence); show the Nobel fact as typography with the source.

## Numbers you may use (all real; read them at build time, never retype)
From `reports/stages/*.json` and `web/public/data/` (current values in brackets — re-read before rendering):
- Texts: Dioscorides [1,500 passages, 835 chapters]; Galen [476 drug entries]; expert gold [61 names];
  modern Greek records [1,226].
- Extraction: LLM claims [5,075], spans verified [100%], rule uses recovered by the LLM [94.9%], usable claims
  [2,561 → 3,550], verified MeSH conditions [90].
- Identification (61 names, leave-one-name-out): top-1 agreement [62%] vs LSJ dictionary [31%];
  Brier [0.50] vs [1.34]; calibration error [0.21 → 0.14 with the description match; target ≤ 0.10, not met];
  LLM judge [59%, comparison only].
- Survival: [48.6%] of uses recur in modern Greece vs [40.8%] by chance (p = [0.001], 1,000 shuffles);
  Galen re-attests [37%], John the Physician [34%].
- Time machine (all body systems): [1,332–1,404] untested pairs per cutoff; popularity predicts best;
  adding history never helps and at [2005] it hurts (ΔAUPRC CI [−0.14 … −0.02]). Say "honest null".
- Chemistry: [10,252] compounds, [455] human targets, [4,880] closed compound → target → disease paths.
- Leads: [1,781] untested pairs; [16/20] top leads with a closed evidence path; [5/20] change if uncertainty
  is ignored; [2/20] carry a toxicity flag.
- Knowledge graph: [2,585] nodes, [9,146] edges.
- External facts (verify against the source before use, cite on screen in small type):
  Nobel Prize in Physiology or Medicine 2015 (Tu Youyou, artemisinin) — nobelprize.org;
  Dioscorides, *De materia medica*, 1st century AD; Vienna Dioscorides c. AD 512 — Austrian National Library.
- **Never invent a statistic.** If a number is not in the files above or a verified source, cut the line.

# THE REAL-LIFE STORY
- Eleni appears in the cold open (desk, a printed Dioscorides page, ten empty sample vials drawn as clean line
  icons), in the problem, in the walkthrough (her cursor, her searches) and in the outro (the same desk, now a
  short ranked list with toxicity flags and evidence paths, and a PubMed query she can run).
- Her walkthrough solves exactly her problem with the real data: search **ἀψίνθιον**, see the candidates with
  probabilities, check the description match, see which uses survived to modern Greek villages, then open
  **Leads**, set certainty ≥ 0.5, hide toxic plants, filter a condition, open a lead's evidence path.
- **The "aha" moment:** a lead with **no PubMed paper yet** (show the live 0-result search) but a closed
  **compound → human target → disease** path, from a plant Dioscorides named 2,000 years ago, and Pharmakon
  shows exactly how sure we are it is that plant. Choose the lead at record time from `leads.json`: non-toxic,
  `has_paths: true`, P ≥ 0.6, best rank.
- Second aha (AI): Eleni opens **Claude on the web** where the Pharmakon connector is already enabled and asks:
  "Which plants did Dioscorides use for eye diseases that nobody has tested yet? How sure are we of each
  identification? Flag toxicity." Show the real tool-call cards Claude produces (`list_conditions`,
  `list_leads`, `get_lead`, `get_ancient_name`), expand one to reveal the JSON coming back from
  `pharmakon.adoranto737.workers.dev/mcp` (with the disclaimer field), and the final answer quoting P(species),
  toxicity flags and the PubMed query. Then a follow-up: "Show me the Greek words Dioscorides used for it" →
  `get_ancient_name` returns the passage and CTS URN. This proves the data is usable by any AI assistant, not
  just our website.
- End: she exports the CSV. Ten vials fill with labels. Small type: "Research hypotheses — not medical advice."

# VISUAL IDENTITY
- Everything (motion graphics, end cards, captions, callouts, cursor, highlight boxes) uses the brand tokens.
- Black base; verdigris for structure; verdigris-hi only for answers/actions; warn red only for toxicity.
- Typography: headlines 72–160 px at 1080p, max 6 words on screen; Greek always in GFS Didot; numbers in
  JetBrains Mono. Never paragraphs.
- Safe margins ≥ 96 px; one 12-column grid; radii as on the site.
- Disclaimer "Research hypotheses only — not medical advice" appears in sections 2, 8 (leads), 10 and 12.

# MOTION DESIGN LANGUAGE
- Easing: never linear. Entrances `cubic-bezier(0.16, 1, 0.3, 1)` 300–500 ms (paper tears 700–900 ms);
  exits quick ease-in 200–300 ms; holds ≈ 0.3 s per word + 0.5 s.
- Text: word-by-word mask reveals, 20–40 px Y offset, blur-to-sharp; key words in verdigris-hi.
- Greek text: letters "ink in" left to right like a pen stroke; the evidence span highlight sweeps in
  verdigris (as on the site's `<mark>`).
- Numbers: count up in JetBrains Mono with a soft tick; intervals draw as whiskers after the point lands.
- Charts: rebuild in code from the JSON (no screenshots of charts): probability bars, the identification dot plot
  with CIs, the alluvial flow, the permutation null, the ΔAUPRC interval plot.
- Transitions: torn-paper wipes and match cuts only; no cross-dissolve spam, spins or star wipes.
- Camera: slow drift/parallax on every static scene; 2.5D layers (folio → sheet → band → type).
- Rhythm: fast cuts in the problem, spacious in the data/method, steady drive in the walkthrough, wonder under
  the hood, measured and honest in results, resolved in the outro.

# PRODUCT RECORDING SPEC (section 8)
## Capture
- Drive the real live site with Playwright (headed Chrome, kiosk window, no extensions or bookmarks bar), and
  capture with OBS at 2560×1440 60 fps (or Playwright CDP screencast at deviceScaleFactor 2), system cursor
  hidden. Log every action with timestamp and on-screen coordinates to `docs/video/actions.json`.
- Story-order shot list on the site:
  1. Hero: let the torn sheets settle, scroll so they tear apart (scroll-linked), pause on the wordmark.
  2. "One word, three plants": the real ambiguity example.
  3. How it works: the pipeline line drawing across.
  4. Explorer: type `apsinthion` with natural keystroke timing → open ἀψίνθιον → read the highlighted Greek →
     probability bars + whiskers → candidate cards with photos and description-match chips → "Two thousand
     years of this plant's uses" table → Galen passage → modern Greek village uses.
  5. Through time: filter chips (All uses → Skin & wounds), the alluvial animating, the permutation card.
  6. Results: identification chart; time machine — click 2000 → 2005 → 2010 → 2015 and let the verdict text change.
  7. Leads: certainty slider to 0.50, "Hide plants with known toxicity" on, pick a condition, open the aha lead's
     evidence-path dialog, click "Run this query on PubMed" (record the real result page), back, Download CSV.
  8. Use it: copy the MCP command.
  9. **Claude on the web (real connector):** in the user's own logged-in Chrome (do not automate login; record the
     window with OBS, or drive it with Claude in Chrome / Playwright attached to that profile):
     a. Settings → Connectors: show "Pharmakon" connected with its URL `https://pharmakon.adoranto737.workers.dev/mcp`
        and its 6 tools (search_ancient_names, get_ancient_name, list_leads, get_lead, list_conditions, get_results).
     b. New chat with the connector enabled → ask the eye-diseases question → let Claude call the tools live →
        expand one tool call to show the JSON → read the answer (P(species), toxicity, PubMed query, disclaimer).
     c. Follow-up question about the Greek words → `get_ancient_name` → passage + CTS URN.
     d. Ask "How well does Pharmakon identify plants compared with experts?" → `get_results` → real numbers.
     Privacy: fresh chat, collapse the sidebar (no chat history on screen), crop or blur the account name/email
     and avatar, no other connectors' data visible.
  10. **Claude Code terminal (same server):** `claude mcp add --transport http pharmakon https://pharmakon.adoranto737.workers.dev/mcp`,
     `claude mcp list` showing "✔ Connected", one question with visible tool calls.
     Then `curl "https://pharmakon.adoranto737.workers.dev/api/leads?condition=eye&hide_toxic=true&limit=3"`.
  11. GitHub: README top (logo, banner, status table), scroll to results tables; terminal `make test` → 27 passed.
- Remove dead time (speed-ramp loading), never fake a result. Blur nothing — there is no private data — but do not
  show API keys (the Groq key must never appear).

## Cinematic cursor & camera
- Custom cursor drawn in post: Paper `#ECEEE7` arrow with a 1 px verdigris outline; bezier paths with overshoot
  and settle; press-scale 0.85× for 120 ms with a verdigris-hi ripple ring and a soft paper-click SFX.
- Typing: realistic timing; a small keystroke chip for shortcuts.
- Auto-zoom 1.4–2.2× toward the action (Screen Studio style), eased follow, zoom back out between steps.
- Spotlight: dim everything except the element being explained (black at 60%).
- Callouts (2–5 words, Outfit 500, glass pill): "exact Greek words", "90% interval", "doubt kept, not hidden",
  "survived 2,000 years", "no paper yet", "compound → target → disease", "toxicity flagged", "frozen, no AI",
  "live MCP tool call", "same data, any AI".
- Frame the recording in a minimal dark browser mockup on a black-and-verdigris background with soft shadow;
  enter/exit the recording through a torn-paper tear or a 3D tilt.

# UNDER THE HOOD (section 9) — make the engine visible
- From the recording, the items Eleni just used (the Greek clause, ἀψίνθιον, *Artemisia absinthium*, a compound,
  a target, a disease) dissolve into **nodes**; relationships draw in as edges with travelling verdigris light pulses.
  Use the real edge types from `reports/stages/build-kg.json`: MENTIONS, CLAIMS_USE_FOR, IDENTIFIED_AS, CONTAINS,
  ACTS_ON, ASSOCIATED_WITH, ATTESTED_IN, MAPS_TO.
- Show a real query in JetBrains Mono — the actual MCP call that Claude on the web sent to the Pharmakon server
  (Streamable HTTP, JSON-RPC 2.0, stateless Cloudflare Worker reading the pipeline's own JSON), e.g.
  `{"method":"tools/call","params":{"name":"get_lead","arguments":{"rank":N}}}` — and visualise the hop-by-hop
  traversal until the disease node lights up, then cut back to the same answer in the UI.
- Then the verification layer: a Greek quote snaps onto its source passage with a ✓ (substring check), the
  identification node shows its probability and interval, and a padlock closes over the time-machine branch:
  "No AI output enters the backtest."
- One on-screen line naming the technical win: **"Every lead traces back to the exact Greek words."**
  Add the real counts (2,585 nodes · 9,146 edges · 100% spans verified). Never invent a latency number.

# RESULTS (section 10) — honest and specific
1. "Which plant is it?" — dot plot: Pharmakon 62% vs LSJ 31%, with intervals; calibration 0.21 → 0.14
   (still above the 0.10 target — say so); LLM judge 59% (comparison only, may have memorised).
2. "Did the uses survive?" — 48.6% observed vs 40.8% shuffled, p = 0.001.
3. "Did history predict science?" — the ΔAUPRC interval plot: never helps, hurts at 2005. Narrate it as a finding:
   "We report it the same way we'd report a success."
4. Leads — 1,781 untested; 16/20 with a full evidence path; uncertainty changes 5/20; 2/20 toxic, shown not hidden.

# IMPACT, LIMITS, FUTURE (section 11)
- Before/after for Eleni: "600 names, no ranking" → "a ranked shortlist with certainty, evidence paths, toxicity
  flags and the exact PubMed query". (No invented time-saved numbers.)
- Who benefits: pharmacognosy labs (what to screen), historians (Dioscorides read with evidence),
  conservation (IUCN status per species), AI assistants via MCP.
- What we don't claim (calm cards): expert gold is judgement, not ground truth; PubMed co-mention is a proxy;
  human audits pending; calibration above target; research hypotheses only.
- Responsible research: no dosing; toxicity flags with PubChem citations; Nagoya Protocol benefit-sharing.
- Next: expert audits, richer floras, Paul of Aegina and Oribasius, Arabic and Latin transmission, a screening
  partnership, a Zenodo DOI.

# VOICE-OVER (Sarvam AI — real, natural voice)
- English, calm-confident, warm. Speak like a scientist-founder telling a story. ~150 wpm →
  **1,150–1,300 words** for 8:00–8:40. Short sentences. 0.4–0.8 s pauses at section turns; silence under the
  title reveal and the aha moment.
- Deliver the script line by line with timestamps and the visual under each line.
- No buzzwords ("revolutionary", "seamless", "leverage", "unlock"). Concrete verbs, concrete numbers.
- **Engine: Sarvam AI Text-to-Speech** — `POST https://api.sarvam.ai/text-to-speech`, header
  `api-subscription-key: <value of sarvam_api_key from .env>` (read it in code; never echo it, never commit it,
  never show it on screen), JSON body `{"text", "target_language_code": "en-IN", "model": "bulbul:v3",
  "speaker": "<chosen>"}`; the response carries base64 audio in `audios[]`. Check docs.sarvam.ai for the
  current per-request text limit, `pace`, sample-rate and output-format options and use the highest quality.
- **Voice casting:** generate the same 2–3 sentence test line (with "Pharmakon", "Dioscorides", "ἀψίνθιον" and
  "Artemisia absinthium" respelled phonetically) with 4–6 `bulbul:v3` speakers and pick the most natural,
  least robotic one for a calm documentary read. Available v3 speakers include: aditya, ritu, ashutosh, priya,
  neha, rahul, pooja, rohan, simran, kavya, amit, dev, ishita, shreya, ratan, varun, manan, sumit, roopa, kabir,
  aayan, shubh, advait, anand, tanya, tarun, sunny, mani, gokul, vijay, shruti, suhani, mohit, kavitha, rehan,
  soham, rupali (fallback `bulbul:v2`: anushka, abhilash, manisha, vidya, arya, karun, hitesh).
  Present the shortlist to the user and let them choose.
- **Generation:** one request per script line or short paragraph (stay under the API's text limit), save each as
  `docs/video/vo/NN_section.wav` with its script line in `docs/video/vo/manifest.json`, so picture can be locked
  line by line and any line re-generated alone. Cache by text hash; do not re-bill unchanged lines.
- **Pronunciation:** feed the TTS phonetic respellings, keep the correct spelling in captions:
  Pharmakon → "FAR-ma-kon" · Dioscorides → "dye-oss-KOR-ih-deez" · Galen → "GAY-len" ·
  De materia medica → "day ma-TEER-ee-ah MED-ih-kah" · ἀψίνθιον → "ap-SIN-thee-on" ·
  Artemisia absinthium → "ar-teh-MEE-zee-ah ab-SIN-thee-um" · Byzantine → "BIZ-an-teen" ·
  ChEMBL → "KEM-bul" · MeSH → "mesh" · Lardos → "LAR-doss" · MCP → "M C P" ·
  AUPRC → say "precision score" instead. Listen to every line; re-generate any mispronunciation.
- **Post:** trim silences to natural breaths, light de-essing, gentle EQ (high-pass 80 Hz, slight presence lift),
  compression 2–3:1, normalise; keep the same processing chain on every line so the voice never changes colour.
- Fallback only if Sarvam fails: Chatterbox (installed at `~/.local/share/chatterbox/.venv`).

# MUSIC & SOUND DESIGN
- One CC0 / royalty-free track (or a stitched edit) with the arc: hush (cold open) → tension (problem) →
  lift (the turn) → steady drive (walkthrough) → wonder (under the hood) → measured resolve (results/outro).
  Prefer CC0 sources (e.g. freepd.com); record the licence in `docs/video/CREDITS.md`.
- Sound design: dry paper tears on every torn-paper transition, paper rustle under the sheets, soft UI clicks,
  subtle risers before reveals, a low bass hit on the title and on the aha. No cheesy whooshes.
- Auto-duck music under VO (−12 to −18 dB). Final mix −14 LUFS integrated, true peak ≤ −1 dBTP.

# CAPTIONS
- Word-timed captions from the final VO with faster-whisper (`whisper-ctranslate2`), proofread (Greek and Latin
  names!), export `.srt`.
- Burned-in version: Outfit 500, max 2 lines, bottom-centre on a subtle black gradient, active word in `#3DBB82`;
  Greek words in GFS Didot.

# TECHNICAL SPECS
- 1920×1080 (3840×2160 if feasible), 60 fps for recording sections (30 fps acceptable elsewhere, conform to 60),
  H.264 High, 12–20 Mbps (1080p), AAC 320 kbps 48 kHz, Rec.709, no crushed blacks, matched gamma between motion
  graphics and the recording.
- Devpost takes a video link: upload to YouTube (public or unlisted) and check it plays logged out.
  Keep under 10:00.

# TOOLCHAIN (local; install anything missing)
- Load the `video-stack` skill first (routes to Remotion / HyperFrames). Composition in **Remotion** (React) or
  **HyperFrames** — code-driven, every shot re-renderable.
- Recording: Playwright (scripted, action/coordinate log) + OBS or CDP screencast; FFmpeg for conforming.
- Cursor/zoom layer built in the composition from `actions.json`.
- Charts and the knowledge graph generated in code from `reports/stages/*.json`, `web/public/data/*.json` and
  `data/processed/kg/`.
- TTS: Sarvam AI `bulbul:v3` (key `sarvam_api_key` in `.env`); fallback Chatterbox. Captions: faster-whisper.
  Audio: FFmpeg `loudnorm`, sidechain ducking.
- Real AI demo: claude.ai in the user's Chrome with the Pharmakon connector (OBS capture or Claude in Chrome),
  and Claude Code in a terminal.
- Brand assets: `web/public/media/*`, `docs/media/*`, `web/src/style.css` tokens.

# WORKFLOW (stop for approval where marked)
1. Creative brief: logline, Eleni's arc, emotional arc, 3 key messages. (**Stop for approval.**)
2. Script: full VO with timestamps (~1,200 words) paired with visuals for every line; list every number with its
   source file.
3. Storyboard / shot list: every shot with timing, motion, transition, SFX, on-screen text; render one style frame
   per section in the brand (including the torn-paper title). (**Stop for approval.**)
4. Record the product per the recording spec.
5. Generate VO, lock picture to VO.
6. Build motion sections, torn-paper transitions, cursor/zoom layer, under-the-hood graph, results charts.
7. Music, sound design, mix.
8. Captions.
9. Render, run the quality checklist, fix every failure, re-render.

# DELIVERABLES
- `docs/video/pharmakon_film.mp4` (1080p; + 4K if feasible), `pharmakon_film.srt`, burned-caption version.
- `docs/video/SCRIPT.md` (VO + shot list + number sources), `docs/video/CREDITS.md` (music, images, fonts, licences).
- Thumbnail 1280×720 in the torn-paper brand style.
- 60-second cut-down for social (hook → turn → aha → results → link).
- Project source so any shot can be edited and re-rendered.

# QUALITY CHECKLIST (must all pass)
- [ ] Hook lands in 3 s; a stranger understands Eleni's problem by 1:00.
- [ ] Every hackathon video item is covered: problem, motivation, approach, technology, data, results, demo,
      impact, future — and limitations/uncertainty are stated.
- [ ] One protagonist, one story thread, first frame to last; she is labelled a fictional composite.
- [ ] The torn-paper title and transitions match the live site's hero (same masks, folios, colours, fonts).
- [ ] Every page in the shot list is shown with purpose; no dead time; no faked UI or results.
- [ ] The aha lead is real: live PubMed shows no matching paper, the evidence path exists in `leads.json`.
- [ ] The evidence chain, knowledge graph and frozen backtest are shown as essential, not decorative.
- [ ] Every number is read from the pipeline files or a cited source; none invented; the null result is stated
      plainly; calibration is shown as not yet meeting its target.
- [ ] "Research hypotheses only — not medical advice" appears; toxicity is shown in warn red; no dosing anywhere.
- [ ] Brand colours and fonts everywhere; Greek always in GFS Didot and correct.
- [ ] No headline holds fewer than its reading time; max 6 words per headline.
- [ ] Cursor never moves in straight robotic lines; every click has feedback.
- [ ] VO natural; names pronounced per the guide; synced to picture.
- [ ] Audio at −14 LUFS, voice always clear over music.
- [ ] Runtime 8:00–9:00 (never above 10:00); YouTube link plays logged out.
- [ ] Watched once with sound off (captions carry it) and once eyes-closed (VO carries it).
- [ ] The MCP demo is real: claude.ai shows the Pharmakon connector and live tool calls returning data from
      `pharmakon.adoranto737.workers.dev/mcp`; no personal chat history, email or other connectors on screen.
- [ ] VO generated with Sarvam `bulbul:v3`; the chosen voice was approved by the user; no key in any file,
      log or frame.
- [ ] Team names on the end card; no API keys anywhere on screen.
