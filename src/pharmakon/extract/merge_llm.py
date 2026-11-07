"""Merge LLM-extracted claims (Claude session, ``data/llm/claims_session*.jsonl``) with ``rule_extract_v1``.

Policy (LLMs propose; the lexicon, MeSH and the span check verify):
- Every LLM span and condition span is re-verified against the passage; failures are archived and counted.
- The LLM's condition words are mapped through the same Greek condition lexicon as the rules, so MeSH
  codes still come only from the verified map. LLM claims with no lexicon match are kept apart
  (``interim/claims_llm_out_of_lexicon.parquet``) as candidates for extending the lexicon.
- Rule claims marked ``ambiguous`` (no therapeutic cue) that the LLM also reads as a use become ``ok``
  with ``llm_confirmed=True``; their original status stays in ``rule_status``.
- LLM claims whose lexicon condition the rules missed in that passage are added with
  ``extractor_version=llm_extract_v1:<model>``.
- The temporal backtest reads only rule claims with their ``rule_status`` (forecast.run.rule_claims).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from pharmakon.common import DATA, now_iso
from pharmakon.extract.lexicon import find_all, lexicon
from pharmakon.extract.span_verify import verify
from pharmakon.names.normalize import strip_accents
from pharmakon.schemas import ExtractedClaim


def load_session(files: list[Path] | None = None) -> tuple[dict[str, list[dict]], dict[str, str]]:
    """passage_id → raw LLM claims (last file wins per passage), passage_id → method."""
    out: dict[str, list[dict]] = {}
    method: dict[str, str] = {}
    for f in files if files is not None else sorted((DATA / "llm").glob("claims_session*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                out[d["passage_id"]] = d.get("claims", [])
                method[d["passage_id"]] = d.get("method", "llm_extract_v1:claude-session")
    return out, method


def merge(rule: pd.DataFrame, passages: pd.DataFrame, claim_id, substance_type_for) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """Return (merged claims, archived LLM span failures, out-of-lexicon LLM claims, stats)."""
    session, method = load_session()
    rule = rule.copy()
    rule["rule_status"] = rule["status"]
    rule["llm_confirmed"] = False
    if not session:
        return rule, rule.head(0), pd.DataFrame(), {"llm_session": "none"}
    lx = lexicon()
    text = passages.set_index("passage_id")["text_grc"].to_dict()
    meta = passages.set_index("passage_id")
    covered = [p for p in session if p in text]
    ts = now_iso()
    new_rows, archived, ool = [], [], []
    confirmed_idx: set = set()
    llm_hits_on_rule: set = set()
    n_llm = 0
    for pid in covered:
        rp = rule[rule["passage_id"] == pid]
        stems_rule = dict(zip(rp["condition_stem"], rp.index, strict=False))
        for raw in session[pid]:
            n_llm += 1
            c = ExtractedClaim.model_validate(raw)
            ok_span = verify(c.evidence_span_grc, text[pid])[0]
            ok_cond = verify(c.condition_text_grc, text[pid])[0]
            if not (ok_span and ok_cond):
                archived.append({"passage_id": pid, **c.model_dump(), "status": "span_mismatch", "method": method[pid]})
                continue
            hits = find_all(c.condition_text_grc, lx.conditions)
            if not hits:
                ool.append({"passage_id": pid, **c.model_dump(), "method": method[pid]})
                continue
            for surface, e in {e.stem: (s, e) for s, e in hits}.values():
                if e.stem in stems_rule:
                    idx = stems_rule[e.stem]
                    llm_hits_on_rule.add(idx)
                    if rule.at[idx, "status"] == "ambiguous":
                        confirmed_idx.add(idx)
                    continue
                m = meta.loc[pid]
                new_rows.append({
                    "claim_id": claim_id(pid, e.value, c.plant_part or "", c.evidence_span_grc, "llm"),
                    "passage_id": pid, "chapter_id": m["chapter_id"], "work": m["work"], "century_ce": int(m["century_ce"]),
                    "substance_name_grc": c.substance_name_grc, "substance_lemma": strip_accents(c.substance_name_grc),
                    "substance_type": substance_type_for(m["work"], int(m["book"]), str(m["chapter"])),
                    "plant_part": c.plant_part, "preparation": c.preparation, "route": c.route,
                    "condition_text_grc": surface, "condition_en": e.value, "condition_stem": e.stem, "icpc2_chapter": e.get("icpc2"),
                    "evidence_span_grc": c.evidence_span_grc, "span_verified": True, "span_verified_loose": False, "status": "ok",
                    "uncertain_fields": list(c.uncertain_fields), "therapeutic_cue": True, "extractor_version": f"llm_extract_v1:{method[pid].split(':', 1)[-1]}",
                    "source_id": "dmm_wellmann", "retrieved_at": ts, "method": method[pid], "rule_status": None, "llm_confirmed": True,
                })
                stems_rule[e.stem] = -1  # one LLM claim per (passage, condition)
    for idx in confirmed_idx:
        rule.at[idx, "status"] = "ok"
        rule.at[idx, "llm_confirmed"] = True
    for idx in llm_hits_on_rule:
        rule.at[idx, "llm_confirmed"] = True
    merged = pd.concat([rule, pd.DataFrame(new_rows)], ignore_index=True) if new_rows else rule
    rc = rule[rule["passage_id"].isin(covered)]
    ool_df = pd.DataFrame(ool)
    stats = {
        "llm_session_passages": len(covered),
        "llm_claims": n_llm,
        "llm_span_verified_rate": round(1 - len(archived) / n_llm, 4) if n_llm else None,
        "llm_claims_archived_span_mismatch": len(archived),
        "rule_claims_in_covered_passages": int(len(rc)),
        "rule_ok_recovered_by_llm": round(float(rc.loc[rc["rule_status"] == "ok"].index.isin(list(llm_hits_on_rule)).mean()), 4) if len(rc) else None,
        "rule_ambiguous_confirmed_by_llm": len(confirmed_idx),
        "rule_ambiguous_in_covered": int((rc["rule_status"] == "ambiguous").sum()),
        "llm_new_claims_in_lexicon": len(new_rows),
        "llm_claims_out_of_lexicon": len(ool),
        "top_out_of_lexicon_conditions": Counter(strip_accents(x["condition_text_grc"]).lower() for x in ool).most_common(25),
    }
    return merged, pd.DataFrame(archived), ool_df, stats
