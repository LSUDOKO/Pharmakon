# DH2027 submission: what to enter in ConfTool

**Portal:** https://www.conftool.pro/dh2027/
**Deadline:** 21 November 2026, 11:59 GMT (5:29 PM IST), as shown in ConfTool. Submit by 18 November.

**Submit the long paper:** `Pharmakon_DH2027_long_paper.pdf`
- 11 pages, A4, LaTeX.
- 2,702 words counted, inside the 2,500–3,000 limit. The count covers the abstract, body, headings and captions; it excludes tables, references, the AI disclosure and the appendix.
- 6 figures and 4 tables.
- 23 references. Every DOI was checked against Crossref or DataCite.

The short paper (`Pharmakon_DH2027_short_paper.pdf`, 1,098 words) is a fallback only. Submit one format, not both.

## Before you submit: read it and check it yourself

The paper was drafted with AI assistance, as its disclosure says. You are the author. Read every sentence and make sure you can explain and defend it, because the review is open and you will present it. To change anything, edit `long/main.tex` and rebuild:

```bash
.venv/bin/python docs/dh2027/long/figures.py   # from the repo root; only if figure data or style changes
cd docs/dh2027/long
python3 wordcount.py                         # keep 2,500–3,000
~/.local/bin/tectonic -X compile main.tex    # → main.pdf
cp main.pdf ../Pharmakon_DH2027_long_paper.pdf
```

## Account (ConfTool → Register)

| Field | Enter |
|---|---|
| Name | your full legal name, as it should appear in the programme |
| Organization | National Institute of Technology Hamirpur |
| Department | Department of Computer Science and Engineering |
| Country | India |
| ORCID | create one free at https://orcid.org if you do not have one |
| Code of Conduct / open peer review | tick both (required) |
| ADHO association | "I do not belong to an ADHO association" |

## Submission form (Submit Contribution → Long Paper)

| Field | Enter |
|---|---|
| Contribution type | **Long Paper** (2,500–3,000 words) |
| Special track | **none**. Do not tick Technical Track or Digital Art(s) Track. |
| Title | Keeping Uncertainty Visible: A Verified, Probabilistic Reading of Dioscorides’ De materia medica, from Greek Plant Names to Testable Hypotheses |
| Authors | Arpit, National Institute of Technology Hamirpur, India (presenting author) |
| Language | English |
| Keywords | Dioscorides; Byzantine medicine; ancient Greek; uncertainty; plant identification; ethnopharmacology; reproducibility; knowledge graphs; negative results |
| Topics | Pick the closest options from ConfTool’s list. Good matches if offered: *text mining / analysis*; *history of science / medicine*; *classical studies*; *data modeling*; *linked open data / knowledge graphs*; *open science / reproducibility*; *artificial intelligence and machine learning* |
| Conference theme area | 2. Creative methods and interpretation (secondary: 3. Creative engagements with cultural heritage) |
| Presentation preference | In person or online, as you prefer. DH2027 is partly hybrid, and online presenters can also apply for bursaries. |
| Generative AI disclosure | paste the text below |
| File | upload `Pharmakon_DH2027_long_paper.pdf` |

### Abstract text (if the form asks for a plain-text abstract)

```
Dioscorides' De materia medica (first century CE) is among the most copied pharmacological texts of the Greek tradition, but three uncertainties stand between it and testable science: which plants its names denote, which of its uses survived, and whether historical use anticipates later pharmacological research. We present Pharmakon, an open pipeline that models these uncertainties instead of resolving them by fiat. It segments Wellmann's edition and Galen's De simplicium medicamentorum into CTS-addressed passages, extracts medical-use claims that must quote their Greek verbatim, assigns each ancient name a probability distribution over verified species with an explicit "unidentified" option, traces each use through Galen, John the Physician and modern ethnobotanical records, and tests predictive value in a leakage-controlled backtest. On 61 expert judgements the model's first choice agrees 62% of the time (95% CI 51-75%), against 39% for a uniform guess and 31% for the standard lexicon, but its probabilities are not yet calibrated. Uses recur in the modern record more often than chance (48.6% vs. 40.8%, p = 0.001). Historical features, however, never reliably improve on research popularity in predicting later research, and at one cutoff make the ranking worse: we report this null as a central result. We argue that displaying contested names, untranslatable conditions and negative findings is a creative methodological choice for computational reading.
```

### Generative AI disclosure (paste into the form; also in the PDF)

```
Research: Two language models, Claude (Anthropic) and gpt-oss-120b (via Groq), were used to propose additional medical-use claims and condition-lexicon stems, to extract plant-description traits, and as a comparison baseline ("LLM judge"). Every proposed claim and trait had to quote its source verbatim and was kept only if the quotation was found by exact string match; all language-model outputs are excluded from the backtest. Claude Code was used extensively to write the software, documentation and website. Submission: This paper was drafted with the assistance of Claude and was reviewed, edited and approved by the author, who takes full responsibility for its content.
```

## After submitting

1. Check for the ConfTool confirmation email. No email means it did not go through.
2. **February 2027:** decision.
3. **If accepted:**
   - long papers are published in the *Anthology of Computers and the Humanities*;
   - send the final version in March 2027 and register;
   - apply for an **ADHO bursary**: the call opens after acceptance and is open to students, including online presenters.
4. Add the accepted paper to the README, `CITATION.cff` and your CV.
