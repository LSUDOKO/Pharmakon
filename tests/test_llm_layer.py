"""LLM layer: span verification, trait agreement, merge policy and backtest isolation."""

import pandas as pd

from pharmakon.identify.morphology import agreement, clean_record


def test_clean_record_drops_unverified_and_out_of_vocab():
    text = "a perennial herb with yellow flowers and bitter leaves"
    raw = {
        "habit": {"values": ["herb"], "span": "perennial herb"},
        "flower_colour": {"values": ["yellow"], "span": "purple flowers"},  # span not in text → dropped
        "taste": {"values": ["umami"], "span": "bitter leaves"},  # value not in vocabulary → dropped
    }
    vals, spans, dropped = clean_record(raw, text)
    assert vals == {"habit": ["herb"]} and spans["habit"] == "perennial herb" and dropped == 2


def test_agreement_is_neutral_without_overlap_and_signed_otherwise():
    assert agreement({}, {"habit": ["tree"]})[:2] == (0.0, 0)
    f, n, _ = agreement({"habit": ["herb"], "flower_colour": ["yellow"]}, {"habit": ["herb"], "flower_colour": ["white"]})
    assert n == 2 and f == 0.0
    assert agreement({"habit": ["herb"]}, {"habit": ["herb", "subshrub"]})[0] == 1.0


def test_backtest_reads_only_rule_claims(tmp_path, monkeypatch):
    from pharmakon.forecast import run as fr

    df = pd.DataFrame({
        "extractor_version": ["rule_extract_v1", "rule_extract_v1", "rule_extract_v1+lex_llm", "llm_extract_v1:x"],
        "status": ["ok", "ok", "ok", "ok"], "rule_status": ["ok", "ambiguous", "ok", None],
        "substance_type": ["plant"] * 4, "claim_id": list("abcd"),
    })
    df.to_parquet(tmp_path / "claims_dmm.parquet")
    monkeypatch.setattr(fr, "PROCESSED", tmp_path)
    out = fr.rule_claims()
    assert out["claim_id"].tolist() == ["a"]  # LLM-confirmed, LLM-lexicon and LLM claims are excluded
