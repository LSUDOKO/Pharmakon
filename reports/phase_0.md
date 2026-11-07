# Phase 0 — Setup and source verification

- Repo, `pyproject.toml`, Makefile, config, cached HTTP client (`http.py`), optional LLM wrapper (`llm.py`).
- Live checks of 13 sources pass: see `docs/source_verification.md`.
- Dioscorides TEI commit `da4b902db4989d63d45c87730911a91abb9ea19f`; Lardos figshare CC BY 4.0; Galen found in First1KGreek (tlg0057.tlg075); Paul → fallback R2.
- Open: no ANTHROPIC/NCBI/IUCN keys in the build environment (documented fallbacks).
