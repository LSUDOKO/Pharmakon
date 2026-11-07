PY ?= .venv/bin/python
PK = $(PY) -m pharmakon

.PHONY: setup data verify pilot forecast leads app test lint report readme reproduce

setup:            ## create the venv and install (uv, fallback pip)
	uv venv --python 3.12 .venv || python3 -m venv .venv
	uv pip install --python .venv -e ".[dev,llm]" || .venv/bin/pip install -e ".[dev,llm]"

data:             ## Phase 0: raw sources with licences (DMM TEI, Lardos figshare, LSJ)
	$(PK) data

verify:           ## live checks of every API → docs/source_verification.md
	$(PK) verify-sources

pilot:            ## stages 1–9 on the pilot scope
	$(PK) ingest-texts
	$(PK) gold
	$(PK) extract-claims
	$(PK) map-conditions
	$(PK) cluster-names
	$(PK) identify
	$(PK) ingest-galen
	$(PK) link-chemistry
	$(PK) persistence
	$(PK) evidence-labels

forecast:         ## stage 10
	$(PK) forecast

leads:            ## stage 11 + knowledge graph
	$(PK) leads
	$(PK) build-kg

app:              ## stage 12: explorer (reads committed data/processed, no pipeline needed)
	$(PY) -m streamlit run src/pharmakon/app/Home.py

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check src tests

report:           ## regenerate reports/*.md, figures, docs/data_dictionary.md
	$(PK) report

readme:           ## regenerate README.md charts and tables from reports/stages + web/public/data
	$(PK) readme

reproduce: data pilot forecast leads report   ## everything from cached raw data (HTTP cache in data/cache)
