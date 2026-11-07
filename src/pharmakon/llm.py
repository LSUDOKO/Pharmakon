"""LLM client wrapper: temperature 0, JSON-schema output, hash-keyed disk cache.

Providers: Groq (OpenAI-compatible, ``GROQ_API_KEY``; default ``openai/gpt-oss-120b``) or
Anthropic (``ANTHROPIC_API_KEY``). ``PHARMAKON_LLM_PROVIDER`` forces one. The LLM path is
OPTIONAL: without a key every stage falls back to its deterministic method and says so in
its provenance column. The API key is never written to the cache.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from pharmakon.common import CACHE, CONFIG, env

T = TypeVar("T", bound=BaseModel)
LLM_CACHE = CACHE / "llm"
DEFAULT_MODEL = {"anthropic": "claude-sonnet-5-5", "groq": "openai/gpt-oss-120b"}
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def provider() -> str | None:
    forced = env("PHARMAKON_LLM_PROVIDER")
    if forced:
        return forced
    if env("GROQ_API_KEY"):
        return "groq"
    if env("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None


def available() -> bool:
    return provider() is not None


def model_name() -> str:
    prov = provider() or "anthropic"
    return env("PHARMAKON_LLM_MODEL") or DEFAULT_MODEL[prov]


def load_prompt(name: str) -> tuple[str, str]:
    """Return (prompt text, prompt version) from config/prompts/<name>.md."""
    path = CONFIG / "prompts" / f"{name}.md"
    return path.read_text(encoding="utf-8"), name


def _key(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _groq(model: str, system: str, user: str, schema: dict, max_tokens: int, effort: str) -> tuple[dict, str]:
    """One Groq chat completion with JSON-schema output; waits on 429 using retry-after."""
    import requests

    body = {
        "model": model, "temperature": 0, "seed": 13, "max_completion_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_schema", "json_schema": {"name": "emit", "strict": False, "schema": schema}},
    }
    if model.startswith("openai/gpt-oss"):
        body["reasoning_effort"] = effort
    headers = {"Authorization": f"Bearer {env('GROQ_API_KEY')}", "Content-Type": "application/json"}
    for attempt in range(8):
        r = requests.post(GROQ_URL, json=body, headers=headers, timeout=120)
        if r.status_code == 413 or "request too large" in r.text.lower():
            raise RuntimeError("Groq: request larger than the per-minute token limit; shorten the input or max_tokens")
        if r.status_code == 429 or r.status_code >= 500:
            wait = float(r.headers.get("retry-after") or 0) or min(60.0, 4.0 * 2**attempt)
            low = r.text.lower()
            if "per day" in low or "(rpd)" in low or "(tpd)" in low:
                raise RuntimeError("Groq daily limit reached (requests or tokens per day); rerun later — results so far are cached")
            time.sleep(wait + 0.5)
            continue
        if r.status_code == 400 and "json_validate_failed" in r.text and attempt < 2:
            body["max_completion_tokens"] = int(body["max_completion_tokens"] * 1.5)
            continue
        r.raise_for_status()
        js = r.json()
        content = js["choices"][0]["message"]["content"]
        rem = r.headers.get("x-ratelimit-remaining-tokens")
        if rem is not None and int(float(rem)) < 1500:  # stay under the per-minute token budget
            time.sleep(float(str(r.headers.get("x-ratelimit-reset-tokens", "5s")).rstrip("s").split("m")[-1] or 5) + 0.5)
        return json.loads(content), js.get("model", model)
    raise RuntimeError("Groq: retries exhausted")


def structured(prompt_name: str, user_content: str, schema: type[T], max_tokens: int = 4096,
               effort: str = "medium") -> tuple[T, dict]:
    """Call the model and validate the reply against ``schema``. Cached by request hash."""
    system, version = load_prompt(prompt_name)
    prov = provider() or "anthropic"
    model = model_name()
    payload = {
        "provider": prov,
        "reasoning_effort": effort if prov == "groq" else None,
        "model": model,
        "prompt_version": version,
        "system": system,
        "user": user_content,
        "schema": schema.model_json_schema(),
        "temperature": 0,
    }
    key = _key(payload)
    cache_file: Path = LLM_CACHE / f"{key}.json"
    meta = {"provider": prov, "model": model, "prompt_version": version, "temperature": 0, "cache_key": key}
    if cache_file.exists():
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        return schema.model_validate(data["response"]), meta | {"cached": True}
    if not available():
        raise RuntimeError("no LLM key (GROQ_API_KEY / ANTHROPIC_API_KEY); use the deterministic method instead")
    if prov == "groq":
        raw, served = _groq(model, system + "\n\nReturn ONLY a JSON object matching this JSON schema:\n"
                            + json.dumps(schema.model_json_schema(), ensure_ascii=False), user_content,
                            schema.model_json_schema(), max_tokens, effort)
        result = schema.model_validate(raw)
        LLM_CACHE.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({"request": payload, "response": result.model_dump(), "model": served},
                                         ensure_ascii=False), encoding="utf-8")
        return result, meta | {"cached": False, "model": served}
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
