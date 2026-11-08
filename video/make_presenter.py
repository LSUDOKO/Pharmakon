"""Cut the presenter takes (public/presenter/p*.mp4) into film lines.

For each piece: one accurate cut for video and audio, speech cleaned (high-pass, FFT denoise tuned to the
room's noise floor, gentle compression, de-ess) and levelled to the narrator (-18 LUFS, two-pass), a 2x lanczos
upscale for the video, and word timings from whisper (corrected for mis-hearings) so captions and scene cues follow
the real speech. Writes vo/presenter.json, which make_timing.py merges over the narrator manifest.

Needs the whisper JSONs: whisper-ctranslate2 <clip>.wav --model small.en --word_timestamps True --output_format json
"""
import json, subprocess, sys
from pathlib import Path

D = Path(__file__).parent
PUB = D / "film" / "public"
SRC = PUB / "presenter"
OUT_V = SRC / "cut"
OUT_A = PUB / "vo"
WHISPER = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC / "whisper"

# word index -> corrected text; "" merges the word into the previous one (keeps its timing)
FIX = {
    "p1": {2: "Arpit.", 3: "Currently", 6: "B.Tech", 7: "", 15: "Technology,", 16: "Hamirpur,", 30: "it's", 31: "for."},
    "p2": {0: "Why", 4: "Plants", 5: "", 14: "drugs,", 18: "tradition", 32: "became", 33: "a hypothesis", 37: "test."},
    "p3": {2: "show you."},
    "p4": {9: "2,000", 10: "years", 11: "", 14: "predict", 15: "what", 17: "studies", 21: "Research", 22: "",
           31: "", 42: "would", 44: "a success."},
    "p5": {6: "Expert", 7: "judgement", 17: "a proxy", 19: "evidence,", 25: "", 33: "hypothesis,", 34: "never", 35: "",
           38: "Next:", 40: "audits,", 41: "", 44: "descriptions,", 45: "more", 47: "authors,"},
}
# pieces: (id, clip, cut_from, cut_to, section, replaces|None); s11_b/s11_c share one continuous take
PIECES = [
    ("p1", "p1", 1.65, 16.10, "intro", None),
    ("p2", "p2", 0.70, 16.80, "motivation", "s04_a"),  # ends before "so we built Pharmakon" (the narrator says it)
    ("p3", "p3", 1.25, 3.05, "handoff", None),        # "Let me show you." then the narrator's "Here is Eleni using it."
    ("p4", "p4", 1.85, 25.35, "results", "s10_e"),
    ("p5b", "p5", 1.05, 19.62, "impact", "s11_b"),
    ("p5c", "p5", 19.62, 33.75, "impact", "s11_c"),
]
VIDEO = {"p1": (1.65, 16.10), "p2": (0.70, 16.80), "p3": (1.25, 3.05), "p4": (1.85, 25.35), "p5": (1.05, 33.75)}
CX = {"p1": 409, "p2": 453, "p3": 400, "p4": 462, "p5": 453}  # face centre x in the 854-px source, for the card crop

AF = "highpass=f=90,lowpass=f=12500,afftdn=nf=-50:nr=24:tn=1,agate=threshold=0.012:ratio=2.5:range=0.12:attack=4:release=180:knee=3,acompressor=threshold=-24dB:ratio=2:attack=12:release=160,deesser=i=0.3,alimiter=limit=0.55:attack=3:release=50:level=disabled"


def run(*a):
    return subprocess.run(a, check=True, capture_output=True, text=True)


def words(clip):
    d = json.loads((WHISPER / f"{clip}.json").read_text())
    ws = [dict(w=w["word"].strip(), s=w["start"], e=w["end"]) for s in d["segments"] for w in s["words"]]
    out = []
    for i, w in enumerate(ws):
        t = FIX.get(clip, {}).get(i, w["w"])
        if t == "":
            out[-1]["e"] = w["e"]
        else:
            out.append(dict(w=t, s=w["s"], e=w["e"]))
    return out


def clean_audio(src, a, b, dst):
    base = ["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-to", f"{b}", "-i", str(src), "-vn", "-ac", "1", "-ar", "48000"]
    m = subprocess.run([x if x != "error" else "info" for x in base] + ["-af", AF + ",loudnorm=I=-18:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-18:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    fade = f"afade=t=in:d=0.04,afade=t=out:st={b - a - 0.06:.3f}:d=0.06"
    run(*base, "-af", f"{AF},{ln},volume=2.5dB,alimiter=limit=0.84:attack=2:release=40:level=disabled,{fade}", "-c:a", "pcm_s16le", str(dst))


def main():
    OUT_V.mkdir(parents=True, exist_ok=True)
    for clip, (a, b) in VIDEO.items():
        dst = OUT_V / f"{clip}.mp4"
        if not dst.exists():
            run("ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-to", f"{b}", "-i", str(SRC / f"{clip}.mp4"), "-an",
                "-vf", "scale=1708:960:flags=lanczos,unsharp=5:5:0.5", "-c:v", "libx264", "-crf", "15", "-g", "15",
                "-pix_fmt", "yuv420p", str(dst))
    pieces = []
    for pid, clip, a, b, section, replaces in PIECES:
        wav = OUT_A / f"presenter_{pid}.wav"
        clean_audio(SRC / f"{clip}.mp4", a, b, wav)
        ws = [dict(w=w["w"], s=round(max(0, w["s"] - a), 3), e=round(w["e"] - a, 3))
              for w in words(clip) if w["s"] >= a - 0.05 and w["e"] <= b + 0.05]
        va, _ = VIDEO[clip]
        pieces.append(dict(id=replaces or f"{pid}", section=section, replaces=replaces, file=wav.name,
                           duration=round(b - a, 3), text=" ".join(w["w"] for w in ws), words=ws,
                           video=dict(src=f"presenter/cut/{clip}.mp4", from_s=round(a - va, 3), cx=CX[clip], clip=clip)))
        print(f"{pid:4} {section:10} {b - a:5.2f}s  {pieces[-1]['text']}")
    (D / "vo" / "presenter.json").write_text(json.dumps(pieces, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
