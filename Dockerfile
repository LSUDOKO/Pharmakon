# Pharmakon: the pipeline CLI, the committed tables and the Streamlit research dashboard.
#   docker run --rm ghcr.io/lsudoko/pharmakon --help
#   docker run --rm -p 8501:8501 --entrypoint streamlit ghcr.io/lsudoko/pharmakon \
#       run src/pharmakon/app/Home.py --server.address=0.0.0.0
# Secrets (NCBI_API_KEY, GROQ_API_KEY, ...) are never baked in: pass them with --env-file at run time.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="Pharmakon" \
      org.opencontainers.image.description="Uncertainty-aware, 2,000-year map of Greek and Byzantine pharmacology: pipeline CLI, committed tables and research dashboard. Research hypotheses only, not medical advice." \
      org.opencontainers.image.source="https://github.com/LSUDOKO/Pharmakon" \
      org.opencontainers.image.url="https://pharmakon.adoranto737.workers.dev" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PHARMAKON_ROOT=/app
WORKDIR /app

COPY pyproject.toml README.md LICENSE Makefile ./
COPY src ./src
RUN pip install -e ".[llm]"

COPY config ./config
COPY data/processed ./data/processed
COPY data/gold ./data/gold
COPY data/llm ./data/llm
COPY data/external ./data/external
COPY reports ./reports
COPY web/public/data ./web/public/data
COPY docs/README.template.md ./docs/README.template.md

RUN useradd --create-home pharmakon && chown -R pharmakon /app
USER pharmakon
EXPOSE 8501
ENTRYPOINT ["pharmakon"]
CMD ["--help"]
