# DH2027 submission: what to enter in ConfTool

**Portal:** https://www.conftool.pro/dh2027/ · **Deadline:** 20 November 2026, 11:59 PM AoE (submit by 18 November)
**File to upload:** `Pharmakon_DH2027_short_paper.pdf` (A4, 5 pages; body 1,088 words, inside the 1,000–1,250 limit for short papers)

## Before you submit: read it and check it yourself

The paper was drafted with AI assistance, as its disclosure says. You are the author: read every sentence and make sure you can explain and defend it. Change anything that is not how you would put it, then re-render the PDF:

```bash
cd docs/dh2027
python3 wordcount.py                      # keep 1,000–1,250
/opt/google/chrome/chrome --headless --no-pdf-header-footer \
  --print-to-pdf=Pharmakon_DH2027_short_paper.pdf "file://$PWD/paper.html"
```

## Account (ConfTool → Register)

| Field | Enter |
|---|---|
| Name | Arpit (use your full legal name as it should appear in the programme) |
| Organisation | National Institute of Technology Hamirpur |
| Country | India |
| Email | your email |
| ORCID | create one free at https://orcid.org if you do not have one |
| Status | Student (this matters later for ADHO bursaries) |

## Submission form (Your Area → Submit a Contribution)

| Field | Enter |
|---|---|
| Contribution type | **Short Paper** |
| Special track | **none**. Do not tick Technical Track or Digital Art(s) Track. |
| Title | Keeping Uncertainty Visible: A Verified, Probabilistic Reading of Dioscorides’ De materia medica, from Greek Plant Names to Testable Hypotheses |
| Authors | Arpit, National Institute of Technology Hamirpur, India (presenting author) |
| Language | English |
| Keywords | Dioscorides; Byzantine medicine; ancient Greek; uncertainty; plant identification; ethnopharmacology; reproducibility; knowledge graphs |
| Topics | Pick the closest options from ConfTool’s list. Good matches if offered: *text mining / analysis*; *history of science / medicine*; *classical studies*; *data modeling*; *linked open data / knowledge graphs*; *open science / reproducibility*; *artificial intelligence and machine learning* |
| Conference theme area | 2. Creative methods and interpretation (secondary: 3. Creative engagements with cultural heritage) |
| Presentation preference | In person or online, as you prefer. DH2027 is partly hybrid, and online presenters can also apply for bursaries. |
| Generative AI disclosure | paste the text below |
| File | upload the PDF |

### Abstract text (if the form asks for a plain-text abstract)

```
Dioscorides' De materia medica (first century CE), copied for some fifteen centuries, is a rich but fragile source for the history of pharmacology: its plant names are uncertain, the survival of its uses has rarely been measured, and claims that historical use anticipates modern activity are seldom tested without hindsight. Pharmakon is an open pipeline that keeps these uncertainties visible. It segments Wellmann's edition and Galen's De simplicium medicamentorum (First1KGreek TEI, CTS URNs) into passages, extracts medical-use claims that must quote their Greek verbatim (3,696 claims, no mismatches), and assigns each ancient name a probability distribution over GBIF-verified species with an explicit "unidentified" option. On 61 expert identifications its first choice agrees 62% of the time (95% CI 51–75%; uniform guess 39%, LSJ lexicon 31%), although calibration misses its target. 48.6% of uses recur in modern Greek ethnobotanical records against 40.8% by chance (p = 0.001). A leakage-free backtest finds that historical features do not improve on research popularity in predicting later research, a null we report as a central result. The outputs (1,781 research hypotheses, a knowledge graph, a website, an API and an MCP server) are open and citable (doi:10.5281/zenodo.24106413). We argue that displaying contested names, untranslatable conditions and negative results is a creative methodological choice for computational reading.
```

### Generative AI disclosure (paste into the form; also in the PDF)

```
Research: Two language models, Claude (Anthropic) and gpt-oss-120b (via Groq), were used to propose additional medical-use claims and condition-lexicon stems, to extract plant-description traits, and as a comparison baseline ("LLM judge"). Every proposed claim and trait had to quote its source verbatim and was kept only if the quotation was found by exact string match; all language-model outputs are excluded from the backtest. Claude Code was used extensively to write the software, documentation and website. Submission: This abstract was drafted with the assistance of Claude and was reviewed, edited and approved by the author, who takes full responsibility for its content.
```

## After submitting

1. Check for the ConfTool confirmation email. No email means it did not go through.
2. **February 2027:** decision.
3. If accepted:
   - send the final version in March 2027 and register;
   - apply for an **ADHO bursary**: the call opens after acceptance and is open to students, including online presenters.
4. Add the accepted paper to the README and to your CV.
