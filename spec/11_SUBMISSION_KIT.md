# 11 — Submission Kit (Devpost, slides, video, README)

EthnoHack requires four things:
1. a Devpost project page;
2. a public GitHub repository;
3. a pitch video of at most 10 minutes;
4. a slide deck of at most 10 slides.

The organisers recommend the structure **Problem → Data → Method → Prototype → Results → Impact**, with assumptions, limitations, uncertainty and data-quality issues clearly identified.

## 1. Devpost page — field-by-field template

- **Project title:** Pharmakon — 2,000 years of Greek medicine, tested against the future
- **Challenge track:** Track 1 — Traditional knowledge
- **Short description (≤200 chars):** AI that reads Dioscorides and Byzantine texts, identifies their plants with calibrated probabilities, traces remedies to modern Greek folk medicine, and backtests them against later science.
- **Problem statement:**
  - Historical identifications are uncertain;
  - diachronic analyses are manual;
  - herb–disease models are rarely tested with time splits.
- **Solution / approach:**
  - pipeline stages;
  - the identification model;
  - the persistence analysis;
  - the temporal backtest;
  - uncertainty-weighted leads.
- **Technologies:**
  - Python, Anthropic Claude (extraction/normalisation);
  - CLTK, RDKit, scikit-learn/statsmodels, DuckDB, NetworkX;
  - Streamlit.
- **Data sources:** list with licences (copy from `docs/licences.md`).
- **Results:** 3–5 headline numbers with CIs (identification, backtest, uncertainty effect) and a screenshot of the explorer.
- **Team members:** names, disciplines, roles.
- **Impact and future development:**
  - extend to Arabic/Latin transmission and Ayurvedic corpora;
  - partner with pharmacognosy labs for screening of top leads;
  - Zenodo dataset release.
- **Limitations** (explicit paragraph): gold is expert judgement; PubMed proxy labels; pilot domain only; Open Targets associations are current, not historical.

## 2. Slide deck (max 10 slides)

1. **Title + hook.** "Dioscorides wrote about 600 plants. Which ones are they really, and was he right?" Team and track.
2. **Problem.**
   - Three blockers: identification uncertainty, no diachronic analysis at scale, no honest test.
   - One example name with three competing identities.
3. **Data.**
   - The text chain timeline (1st → 2nd → 7th → 13th c. → modern Greek studies).
   - Open databases (COCONUT, LOTUS, ChEMBL, Open Targets, GBIF, Flora of Greece).
   - Licences.
4. **Method I — Extraction & identification.**
   - Span-verified claims; evidence streams; calibrated posterior.
   - Figure: an identification card.
5. **Method II — Persistence & time machine.**
   - Alignment across texts; strict temporal split; popularity baseline; leakage controls.
6. **Prototype (demo screenshot).** The Ancient Name Explorer.
7. **Results I — Identification.** Reliability diagram plus metrics vs LSJ and LLM-judge baselines.
8. **Results II — Persistence + backtest.** Sankey plus AUPRC-by-cutoff chart with CIs; one "hit" example.
9. **Impact & leads.**
   - Top leads with P(species), toxicity and conservation flags.
   - How uncertainty changed the ranking.
10. **Limitations, ethics, next steps.** Disclaimer; label audit; expert gold caveat; roadmap; thanks and links.

## 3. Pitch video script (target 8–9 minutes; hard max 10)

| Time | Segment | Content |
|---|---|---|
| 0:00–0:40 | Hook | Show a Greek passage from Dioscorides, then the question: "Which plant is this, and was the remedy right?" |
| 0:40–1:40 | Problem & motivation | The three blockers; why the Greek tradition; why uncertainty matters (one misidentification breaks a whole lead) |
| 1:40–2:40 | Data | The text chain and databases; open licences; public-domain Greek editions |
| 2:40–4:00 | Method | Extraction with verbatim spans; probabilistic identification; persistence; temporal backtest with leakage controls |
| 4:00–6:00 | Live demo | Explorer: search a name → identification card → passages across centuries → evidence paths → Time Machine page → Leads |
| 6:00–7:30 | Results | Identification metrics; persistence findings; backtest vs popularity; uncertainty effect |
| 7:30–8:30 | Impact & future | Screening priorities; traditional-use dossiers; extension to other corpora; conservation |
| 8:30–9:00 | Limitations & close | Disclaimer; honest caveats; team; repo link |

**Recording tips:**
- Record the demo separately at 1080p.
- Keep captions on.
- Show numbers with CIs exactly as in `reports/`.

## 4. GitHub README skeleton

```
# Pharmakon
> Research hypotheses only — not medical advice.

## What it does
## Why it matters (problem)
## Data (with licences)  → docs/licences.md
## Method (pipeline diagram)
## Results (with CIs; links to reports/)
## Demo (link + screenshots)
## Reproduce
   uv sync && make data && make reproduce
## Limitations  → docs/limitations.md
## Responsible research
## Team
## How to cite / acknowledgements
```

## 5. Final submission checklist
- [ ] Devpost page: every required field filled; track selected.
- [ ] Public GitHub repo: source code, data-processing scripts, notebooks, installation instructions, README, dataset references and licences, reproduction instructions.
- [ ] Video ≤ 10:00, uploaded, link works when logged out.
- [ ] Slides ≤ 10, PDF uploaded.
- [ ] App URL works when logged out.
- [ ] Integrity checklist in `10_RESPONSIBLE_RESEARCH.md` §7 complete.
- [ ] All team members listed on Devpost.
