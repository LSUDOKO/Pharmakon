"""Checks for LLM outputs produced in an interactive Claude session (written as JSONL under data/llm/).

Session outputs are not temperature-0 API calls, so they are committed as files with their prompt
version and model in a ``method`` field, and every stage that reads them re-verifies each span.

    python -m pharmakon.llm_session check morph data/llm/morph_greek.jsonl
    python -m pharmakon.llm_session check claims data/llm/claims_session.jsonl data/llm/inputs/claims_inputs.jsonl
    python -m pharmakon.llm_session check species data/llm/morph_species_session_part1.jsonl data/llm/inputs/morph_species_inputs_part1.jsonl
    python -m pharmakon.llm_session check judge data/llm/judge_session.jsonl data/llm/inputs/judge_inputs.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from pharmakon.common import PROCESSED
from pharmakon.extract.span_verify import verify
from pharmakon.schemas import ExtractedClaim, MorphRecord


def _lines(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def check_morph(out: Path) -> dict:
    from pharmakon.identify.morphology import TRAITS, VOCAB

    ch = pd.read_parquet(PROCESSED / "dmm_chapters.parquet").set_index("chapter_id")
    problems, n_traits = [], 0
    for d in _lines(out):
        cid = d.get("chapter_id")
        if cid not in ch.index:
            problems.append(f"{cid}: unknown chapter_id")
            continue
        try:
            rec = MorphRecord.model_validate(d.get("traits") or {})
        except ValidationError as e:
            problems.append(f"{cid}: schema error {e.errors()[0]['msg']}")
            continue
        for t in TRAITS:
            tr = getattr(rec, t)
            if tr is None:
                continue
            n_traits += 1
            bad = [v for v in tr.values if v not in VOCAB[t]]
            if bad:
                problems.append(f"{cid}.{t}: values not in vocabulary {bad}")
            if not verify(tr.span, ch.loc[cid, "text_grc"])[0]:
                problems.append(f"{cid}.{t}: span not an exact substring: {tr.span[:60]!r}")
    return {"records": len(_lines(out)), "traits": n_traits, "problems": problems}


def check_species(out: Path, inputs: Path) -> dict:
    from pharmakon.identify.morphology import TRAITS, VOCAB

    src = {d["accepted_name"]: d["description"] for d in _lines(inputs)}
    problems, n, seen = [], 0, set()
    for d in _lines(out):
        name = d.get("accepted_name")
        seen.add(name)
        if name not in src:
            problems.append(f"{name}: not in inputs")
            continue
        try:
            rec = MorphRecord.model_validate(d.get("traits") or {})
        except ValidationError as e:
            problems.append(f"{name}: schema error {e.errors()[0]['msg']}")
            continue
        for t in TRAITS:
            tr = getattr(rec, t)
            if tr is None:
                continue
            n += 1
            bad = [v for v in tr.values if v not in VOCAB[t]]
            if bad:
                problems.append(f"{name}.{t}: values not in vocabulary {bad}")
            if not verify(tr.span, src[name])[0]:
                problems.append(f"{name}.{t}: span not an exact substring: {tr.span[:60]!r}")
    missing = sorted(set(src) - seen)
    return {"records": len(seen & set(src)), "traits": n, "n_missing": len(missing), "missing": missing[:10], "problems": problems}


def check_judge(out: Path, inputs: Path) -> dict:
    src = {d["unit_id"]: d["candidates"] for d in _lines(inputs)}
    problems, seen = [], set()
    for d in _lines(out):
        uid = d.get("unit_id")
        seen.add(uid)
        if uid not in src:
            problems.append(f"{uid}: not in inputs")
            continue
        names = [p.get("candidate") for p in d.get("probabilities", [])]
        extra = [x for x in names if x not in src[uid]]
        if extra:
            problems.append(f"{uid}: candidates not in the list {extra}")
        tot = sum(float(p.get("p", 0)) for p in d.get("probabilities", [])) + float(d.get("p_none_of_these", 0))
        if abs(tot - 1) > 0.02:
            problems.append(f"{uid}: probabilities sum to {tot:.3f}, not 1")
    missing = sorted(set(src) - seen)
    return {"records": len(seen & set(src)), "n_missing": len(missing), "missing": missing[:10], "problems": problems}


def check_claims(out: Path, inputs: Path) -> dict:
    src = {d["passage_id"]: d["text_grc"] for d in _lines(inputs)}
    problems, n = [], 0
    seen = set()
    for d in _lines(out):
        pid = d.get("passage_id")
        seen.add(pid)
        if pid not in src:
            problems.append(f"{pid}: unknown passage_id")
            continue
        for i, c in enumerate(d.get("claims", [])):
            n += 1
            try:
                cl = ExtractedClaim.model_validate(c)
            except ValidationError as e:
                problems.append(f"{pid}#{i}: schema error {e.errors()[0]['loc']} {e.errors()[0]['msg']}")
                continue
            if not verify(cl.evidence_span_grc, src[pid])[0]:
                problems.append(f"{pid}#{i}: evidence_span_grc not an exact substring: {cl.evidence_span_grc[:60]!r}")
            if not verify(cl.condition_text_grc, src[pid])[0]:
                problems.append(f"{pid}#{i}: condition_text_grc not an exact substring: {cl.condition_text_grc[:40]!r}")
    missing = sorted(set(src) - seen)
    return {"passages_in": len(src), "passages_out": len(seen & set(src)), "missing": missing[:20], "n_missing": len(missing),
            "claims": n, "problems": problems}


if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] != "check":
        raise SystemExit(__doc__)
    kind = sys.argv[2]
    if kind == "morph":
        res = check_morph(Path(sys.argv[3]))
    else:
        res = {"claims": check_claims, "species": check_species, "judge": check_judge}[kind](Path(sys.argv[3]), Path(sys.argv[4]))
    probs = res.pop("problems")
    print(json.dumps(res, ensure_ascii=False))
    print(f"{len(probs)} problems")
    for p in probs[:80]:
        print(" -", p)
