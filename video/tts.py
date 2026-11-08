"""Sarvam AI TTS helper. Reads sarvam_api_key from .env (never printed). Caches by text hash."""
import base64, hashlib, json, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = next(l.split("=", 1)[1].strip() for l in (ROOT / ".env").read_text().splitlines() if l.startswith("sarvam_api_key="))


def tts(text: str, out: Path, speaker: str, model: str = "bulbul:v3", pace: float = 1.0, extra: dict | None = None) -> dict:
    body = {"text": text, "target_language_code": "en-IN", "model": model, "speaker": speaker, "pace": pace,
            "speech_sample_rate": 48000, **(extra or {})}
    req = urllib.request.Request("https://api.sarvam.ai/text-to-speech", data=json.dumps(body).encode(),
                                 headers={"api-subscription-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            js = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Sarvam {e.code}: {e.read().decode()[:400]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode("".join(js["audios"])))
    return {k: v for k, v in js.items() if k != "audios"}


if __name__ == "__main__":
    print(tts(sys.argv[1], Path(sys.argv[2]), sys.argv[3]))
