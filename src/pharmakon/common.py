"""Shared paths, provenance helpers, table IO and stage reporting."""

from __future__ import annotations

import datetime as dt
import json
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(os.environ.get("PHARMAKON_ROOT", Path(__file__).resolve().parents[2]))
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
GOLD = DATA / "gold"
CACHE = DATA / "cache"
SAMPLE = DATA / "sample"
REPORTS = ROOT / "reports"
CONFIG = ROOT / "config"
LOGS = ROOT / "logs"
DUCKDB_PATH = DATA / "pharmakon.duckdb"

PROVENANCE_COLS = ("source_id", "retrieved_at", "method")


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def load_yaml(name: str) -> dict[str, Any]:
    with open(CONFIG / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def frozen_posterior() -> Path:
    """Non-LLM identification posterior: the backtest's inputs may not depend on LLM output (CLAUDE.md rule 6)."""
    p = PROCESSED / "id_posterior_nollm.parquet"
    return p if p.exists() else PROCESSED / "id_posterior.parquet"


def pilot() -> dict[str, Any]:
    """Pilot config, optionally overridden by config/scope_<PHARMAKON_SCOPE>.yaml (e.g. PHARMAKON_SCOPE=all)."""
    cfg = load_yaml("pilot.yaml")
    scope = env("PHARMAKON_SCOPE")
    if scope:
        cfg = {**cfg, **load_yaml(f"scope_{scope}.yaml"), "scope": scope}
    return cfg


def env(name: str, default: str | None = None) -> str | None:
    """Read a variable from the environment, falling back to a local .env file."""
    if os.environ.get(name):
        return os.environ[name]
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip().startswith(f"{name}="):
                val = line.split("=", 1)[1].strip()
                if val:
                    return val
    return default


def get_logger(stage: str) -> logging.Logger:
    LOGS.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger(f"pharmakon.{stage}")
    if not log.handlers:
        log.setLevel(logging.INFO)
        fh = logging.FileHandler(LOGS / f"{stage}.jsonl", encoding="utf-8")
        fh.setFormatter(logging.Formatter('{"t":"%(asctime)s","lvl":"%(levelname)s","msg":%(message)s}'))
        log.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(f"[{stage}] %(message)s"))
        log.addHandler(sh)
    return log


def add_provenance(df: pd.DataFrame, source_id: str, method: str, retrieved_at: str | None = None) -> pd.DataFrame:
    df = df.copy()
    if "source_id" not in df.columns:
        df["source_id"] = source_id
    if "retrieved_at" not in df.columns:
        df["retrieved_at"] = retrieved_at or now_iso()
    if "method" not in df.columns:
        df["method"] = method
    return df


def write_table(df: pd.DataFrame, path: Path, require_provenance: bool = True) -> Path:
    """Write a parquet table; refuse rows without provenance (CLAUDE.md rule 4)."""
    if require_provenance:
        missing = [c for c in PROVENANCE_COLS if c not in df.columns]
        if missing:
            raise ValueError(f"{path.name}: missing provenance columns {missing}")
        if len(df) and df[list(PROVENANCE_COLS)].isna().any().any():
            raise ValueError(f"{path.name}: null provenance values")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def write_stage_report(stage: str, summary: dict[str, Any]) -> Path:
    out = REPORTS / "stages" / f"{stage}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"stage": stage, "generated_at": now_iso(), **summary}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return out


def read_stage_report(stage: str) -> dict[str, Any]:
    p = REPORTS / "stages" / f"{stage}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))
