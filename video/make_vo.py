"""Generate every VO line with Sarvam (cached by text+voice hash) and write vo/manifest.json with durations."""
import hashlib, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from tts import tts

D = Path(__file__).parent
S = json.loads((D / "script.json").read_text())
v = S["voice"]
out, total = [], 0.0
for ln in S["lines"]:
    text = ln.get("tts", ln["text"])
    h = hashlib.sha1(f"{v['speaker']}|{v['model']}|{v['pace']}|{text}".encode()).hexdigest()[:10]
    f = D / "vo" / "lines" / f"{ln['id']}_{h}.wav"
    if not f.exists():
        tts(text, f, v["speaker"], v["model"], v["pace"])
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).decode())
    out.append({"id": ln["id"], "section": ln["section"], "text": ln["text"], "file": str(f.relative_to(D)), "duration": round(dur, 3)})
    total += dur
    print(ln["id"], round(dur, 2))
(D / "vo" / "manifest.json").write_text(json.dumps({"voice": v, "lines": out, "total_s": round(total, 2)}, indent=1))
print("total", round(total, 1), "s", len(out), "lines", sum(len(l["text"].split()) for l in S["lines"]), "words")
