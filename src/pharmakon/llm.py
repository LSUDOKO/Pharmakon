"""Anthropic client wrapper: temperature 0, JSON-schema output, hash-keyed disk cache.

The LLM path is OPTIONAL. Without ``ANTHROPIC_API_KEY`` every stage falls back to its
deterministic method (e.g. ``rule_extract_v1``) and says so in its provenance column.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from pharmakon.common import CACHE, CONFIG, env

T = TypeVar("T", bound=BaseModel)
LLM_CACHE = CACHE / "llm"
DEFAULT_MODEL = "claude-sonnet-5-5"


def available() -> bool:
    return bool(env("ANTHROPIC_API_KEY"))


def model_name() -> str:
    return env("PHARMAKON_LLM_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL


def load_prompt(name: str) -> tuple[str, str]:
    """Return (prompt text, prompt version) from config/prompts/<name>.md."""
    path = CONFIG / "prompts" / f"{name}.md"
    return path.read_text(encoding="utf-8"), name


def _key(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def structured(prompt_name: str, user_content: str, schema: type[T], max_tokens: int = 4096) -> tuple[T, dict]:
    """Call the model and validate the reply against ``schema``. Cached by request hash."""
    system, version = load_prompt(prompt_name)
    model = model_name()
    payload = {
        "model": model,
        "prompt_version": version,
        "system": system,
        "user": user_content,
        "schema": schema.model_json_schema(),
        "temperature": 0,
    }
    key = _key(payload)
    cache_file: Path = LLM_CACHE / f"{key}.json"
    meta = {"model": model, "prompt_version": version, "temperature": 0, "cache_key": key}
    if cache_file.exists():
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        return schema.model_validate(data["response"]), meta | {"cached": True}
    if not available():
        raise RuntimeError("ANTHROPIC_API_KEY not set; use the deterministic method instead")
    import anthropic  # optional dependency: pip install pharmakon[llm]

    client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY"))
    tool = {
        "name": "emit",
        "description": "Return the structured result.",
        "input_schema": schema.model_json_schema(),
    }
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": "emit"},
        messages=[{"role": "user", "content": user_content}],
    )
    block = next(b for b in msg.content if getattr(b, "type", "") == "tool_use")
    result = schema.model_validate(block.input)
    LLM_CACHE.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps({"request": payload, "response": result.model_dump(), "model": msg.model}, ensure_ascii=False),
        encoding="utf-8",
    )
    return result, meta | {"cached": False, "model": msg.model}
