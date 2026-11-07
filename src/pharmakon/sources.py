"""Phase 0 — raw-data acquisition with licence capture (``python -m pharmakon data``)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
from lxml import etree

from pharmakon import http
from pharmakon.common import INTERIM, RAW, get_logger, load_yaml, now_iso
from pharmakon.names.normalize import strip_accents

log = get_logger("data")

LSJ_BASE = "https://raw.githubusercontent.com/PerseusDL/lexica/master/CTS_XML_TEI/perseus/pdllex/grc/lsj"
LSJ_FILES = [f"grc.lsj.perseus-eng{i}.xml" for i in range(1, 28)]


def _write_meta(dest: Path, meta: dict) -> None:
    (dest / "SOURCE.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_dmm() -> dict:
    cfg = load_yaml("sources.yaml")["dmm_wellmann"]
    dest = RAW / "dmm_wellmann"
    dest.mkdir(parents=True, exist_ok=True)
    f = dest / "tlg0656.tlg001.1st1K-grc1.xml"
    if not f.exists():
        http.download(cfg["url"], str(f))
    commits = http.get_json(cfg["commits_api"]) or []
    sha = commits[0]["sha"] if commits else None
    lic = re.search(r'<licence target="([^"]+)">([^<]+)', f.read_text(encoding="utf-8"))
    meta = {
        "source_id": "dmm_wellmann",
        "url": cfg["url"],
        "last_commit_touching_file": sha,
        "licence_url": lic.group(1) if lic else None,
        "licence_text": " ".join(lic.group(2).split()) if lic else None,
        "retrieved_at": now_iso(),
        "bytes": f.stat().st_size,
    }
    (dest / "LICENSE.txt").write_text(f"{meta['licence_text']}\n{meta['licence_url']}\n", encoding="utf-8")
    _write_meta(dest, meta)
    return meta


def fetch_lardos() -> dict:
    cfg = load_yaml("sources.yaml")["jc_lardos"]
    dest = RAW / "jc_lardos"
    dest.mkdir(parents=True, exist_ok=True)
    rec = http.get_json(cfg["figshare_api"])
    files = []
    for fobj in rec["files"]:
        out = dest / fobj["name"]
        if not out.exists() or out.stat().st_size != fobj["size"]:
            http.download(fobj["download_url"], str(out))
        files.append({"name": fobj["name"], "size": fobj["size"], "md5": fobj.get("computed_md5")})
    lic = rec.get("license", {})
    (dest / "LICENSE.txt").write_text(f"{lic.get('name')}\n{lic.get('url')}\nDOI: {rec.get('doi')}\n", encoding="utf-8")
    meta = {"source_id": "jc_lardos", "doi": rec.get("doi"), "title": rec.get("title"), "licence": lic, "files": files, "retrieved_at": now_iso()}
    _write_meta(dest, meta)
    return meta


# ---- LSJ ------------------------------------------------------------------------------------

_BETA = {
    "a": "α", "b": "β", "g": "γ", "d": "δ", "e": "ε", "z": "ζ", "h": "η", "q": "θ", "i": "ι",
    "k": "κ", "l": "λ", "m": "μ", "n": "ν", "c": "ξ", "o": "ο", "p": "π", "r": "ρ", "s": "σ",
    "t": "τ", "u": "υ", "f": "φ", "x": "χ", "y": "ψ", "w": "ω", "v": "ϝ",
}


def beta_to_key(beta: str) -> str:
    """Beta Code → accent-free lowercase Greek (enough for matching)."""
    b = re.sub(r"\d+$", "", beta.lower())
    out = "".join(_BETA.get(ch, "" if ch in "/\\=()|+*'^_-" else ch) for ch in b)
    return re.sub(r"σ$", "σ", out)


# LSJ often capitalises epithets ("Artemisia Absinthium"); abbreviations end with "." and are skipped.
BINOMIAL = re.compile(r"\b([A-Z][a-z]{2,})\s+([A-Za-z][a-z]{2,}(?:-[A-Za-z][a-z]+)?)\b(?!\.)")
HEDGE = re.compile(r"(prob\.|perh\.|perhaps|probably|\?|cf\.|dub\.|acc\. to some|or )", re.I)
NOT_EPITHET = {"and", "the", "with", "from", "used", "which", "also", "etc", "for", "that", "this", "but", "not"}


def parse_lsj_file(path: Path) -> list[dict]:
    rows = []
    for _, el in etree.iterparse(str(path), tag="entryFree", recover=True, huge_tree=True):
        key = el.get("key") or ""
        text = " ".join(" ".join(el.itertext()).split())
        hits = []
        for m in BINOMIAL.finditer(text):
            genus, ep = m.group(1), m.group(2).lower()
            if ep in NOT_EPITHET:
                continue
            before = text[max(0, m.start() - 30): m.start()]
            hits.append({"binomial": f"{genus} {ep}", "hedged": bool(HEDGE.search(before)), "context": text[max(0, m.start() - 60): m.end() + 30]})
        if hits:
            rows.append({
                "lsj_id": el.get("id"),
                "lsj_key_beta": key,
                "lemma_key": strip_accents(beta_to_key(key)),
                "gloss_head": text[:240],
                "binomials": [h["binomial"] for h in hits],
                "hedged": [h["hedged"] for h in hits],
                "contexts": [h["context"] for h in hits],
            })
        el.clear()
    return rows


def fetch_lsj(keep_xml: bool = False) -> dict:
    """Stream each LSJ file, keep only entries that mention a Latin binomial, then delete the XML."""
    dest = RAW / "lsj"
    dest.mkdir(parents=True, exist_ok=True)
    out_path = INTERIM / "lsj_plants.parquet"
    if out_path.exists():
        return {"source_id": "lsj", "cached": True, "rows": len(pd.read_parquet(out_path))}
    rows: list[dict] = []
    for name in LSJ_FILES:
        f = dest / name
        if not f.exists():
            http.download(f"{LSJ_BASE}/{name}", str(f))
        part = parse_lsj_file(f)
        log.info(json.dumps({"file": name, "entries_with_binomials": len(part)}))
        rows.extend(part)
        if not keep_xml:
            f.unlink()  # disk budget: only the extracted table is kept
    df = pd.DataFrame(rows)
    df["source_id"] = "lsj"
    df["retrieved_at"] = now_iso()
    df["method"] = "lsj_binomial_regex_v1"
    INTERIM.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    (dest / "LICENSE.txt").write_text(
        "Liddell-Scott-Jones Greek-English Lexicon, Perseus Digital Library (PerseusDL/lexica).\n"
        "CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/ — credit Perseus Digital Library, "
        "http://www.perseus.tufts.edu/ ; source https://github.com/PerseusDL/lexica\n",
        encoding="utf-8",
    )
    meta = {"source_id": "lsj", "files": len(LSJ_FILES), "rows": len(df), "retrieved_at": now_iso()}
    _write_meta(dest, meta)
    return meta
