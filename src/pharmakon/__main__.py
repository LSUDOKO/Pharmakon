"""Pharmakon CLI: ``python -m pharmakon <stage>``. Every stage is idempotent and cached."""

from __future__ import annotations

import json

import typer

app = typer.Typer(add_completion=False, help="Pharmakon pipeline (see spec/05_PIPELINE_SPEC.md)")


def _show(d: dict) -> None:
    typer.echo(json.dumps(d, ensure_ascii=False, indent=2, default=str))


@app.command("data")
def data(lsj: bool = typer.Option(True, help="Also stream-parse the LSJ lexicon")) -> None:
    """Phase 0: download raw sources with licences."""
    from pharmakon import sources

    _show(sources.fetch_dmm())
    _show({k: v for k, v in sources.fetch_lardos().items() if k != "files"})
    if lsj:
        _show(sources.fetch_lsj())


@app.command("verify-sources")
def verify_sources() -> None:
    """Phase 0: live checks of every API, written to docs/source_verification.md."""
    from pharmakon.verify import run

    _show(run())


@app.command("ingest-texts")
def ingest_texts() -> None:
    from pharmakon.stages_text import ingest_texts as f

    _show(f())


@app.command("ingest-galen")
def ingest_galen() -> None:
    """Galen De simpl. med. books 6–8 through Stages 1–3 (+ crosswalk and copy detection)."""
    from pharmakon.stages_text import ingest_galen as f

    _show(f())


@app.command("extract-claims")
def extract_claims(llm: bool = typer.Option(False, help="Use Claude (needs ANTHROPIC_API_KEY)")) -> None:
    from pharmakon.stages_text import extract_claims as f

    _show(f(use_llm=llm))


@app.command("map-conditions")
def map_conditions() -> None:
    from pharmakon.stages_text import map_conditions as f

    _show(f())


@app.command("gold")
def gold() -> None:
    from pharmakon.stages_text import build_gold

    _show(build_gold())


@app.command("cluster-names")
def cluster_names() -> None:
    from pharmakon.stages_text import cluster_names as f

    _show(f())


@app.command("identify")
def identify() -> None:
    from pharmakon.identify.run import run

    _show(run())


@app.command("link-chemistry")
def link_chemistry() -> None:
    from pharmakon.link.run import run_chemistry

    _show(run_chemistry())


@app.command("persistence")
def persistence() -> None:
    from pharmakon.persist.run import run

    _show(run())


@app.command("evidence-labels")
def evidence_labels() -> None:
    from pharmakon.evidence.pubmed import run

    _show(run())


@app.command("forecast")
def forecast() -> None:
    from pharmakon.forecast.run import run

    _show(run())


@app.command("leads")
def leads() -> None:
    from pharmakon.leads.rank import run

    _show(run())


@app.command("build-kg")
def build_kg() -> None:
    from pharmakon.kg.build import run

    _show(run())


@app.command("report")
def report() -> None:
    """Regenerate eval markdown reports from stage JSON."""
    from pharmakon.reporting import write_all

    _show(write_all())


if __name__ == "__main__":
    app()
