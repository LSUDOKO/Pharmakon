"""Stage 1–2 tests on a fixture cut from the real First1KGreek TEI (DMM I.3, III.22, III.23)."""

from pathlib import Path

from lxml import etree

from pharmakon.corpus.first1k import chapters_to_frames, clean_element, parse_synonyms, parse_tei
from pharmakon.extract.claims import extract, rule_extract, substance_type_for
from pharmakon.extract.span_verify import verify
from pharmakon.names.normalize import strip_accents, transliterate

FIX = Path(__file__).parent / "fixtures" / "dmm_fixture.xml"


def _frames():
    return chapters_to_frames(parse_tei(FIX), "urn:cts:greekLit:tlg0656.tlg001.1st1K-grc1")


def test_parse_structure_and_headwords():
    passages, chapters = _frames()
    assert set(chapters["chapter_id"]) == {"dmm:1.3", "dmm:3.22", "dmm:3.23"}
    heads = dict(zip(chapters["chapter_id"], chapters["headword_grc"], strict=True))
    assert heads["dmm:3.22"] == "ἀλόη"
    assert heads["dmm:3.23"] == "ἀψίνθιον"
    assert heads["dmm:1.3"] == "μῆον"  # no raised dot: first-token fallback
    assert passages["cts_urn"].str.startswith("urn:cts:greekLit:tlg0656.tlg001.1st1K-grc1:").all()
    assert passages["passage_id"].is_unique


def test_apparatus_is_stripped():
    passages, _ = _frames()
    text = " ".join(passages["text_grc"])
    # Footnote apparatus (e.g. "SIM.", "EXC.", "RV:") must not leak into the main text.
    for marker in ("SIM.", "EXC.", "RV:", "Orib", "Pl. XXVII"):
        assert marker not in text
    assert not any(ch.isdigit() for ch in text)


def test_synonym_list_parsed_and_flagged():
    _, chapters = _frames()
    syn = chapters.set_index("chapter_id").loc["dmm:3.22", "synonyms"]
    assert "ἀμφίβιον" in syn  # from "22 RV: ἀλόη· οἱ δὲ ἀμφίβιον, ..."
    parsed = parse_synonyms("23 RV: ἀψίνθιον βαθύπικρον· Αἰγύπτιοι σομί, Ῥωμαῖοι ἀψίνθιουμ ῥούστικουμ.")
    assert {"name": "σομί", "attributed_to": "Αἰγύπτιοι"} in parsed


def test_nested_chapter_text_not_duplicated():
    xml = (
        '<div xmlns="http://www.tei-c.org/ns/1.0" type="textpart" subtype="chapter" n="1"><p>ἄκορον πρὸς ἕλκη.</p>'
        '<div type="textpart" subtype="chapter" n="2"><p>μῆον πρὸς βῆχα.</p></div></div>'
    )
    assert "μῆον" not in clean_element(etree.fromstring(xml))


def test_rule_extraction_spans_verify_exactly():
    passages, _ = _frames()
    claims, stats = extract(passages)
    assert len(claims) > 10
    assert claims["span_verified"].all()
    p = passages.set_index("passage_id")["text_grc"]
    for r in claims.itertuples():
        assert r.evidence_span_grc in p[r.passage_id]
        assert r.condition_text_grc in r.evidence_span_grc
    aloe = claims[claims.chapter_id == "dmm:3.22"]
    assert "wounds" in set(aloe["condition_en"])  # πρὸς δὲ κόλλησιν τραυμάτων


def test_side_effect_clause_is_ambiguous_not_ok():
    row = {"text_grc": "ἔστι δὲ καὶ κεφαλαλγὲς πλεῖον ἢ δεῖ πινόμενον.", "headword_grc": "ἀψίνθιον"}
    out = rule_extract(row)
    assert out and not out[0]["therapeutic_cue"]


def test_span_verify_modes():
    assert verify("πρὸς  ἕλκη", "καὶ πρὸς ἕλκη ποιεῖ") == (True, True)
    assert verify("προς ελκη", "καὶ πρὸς ἕλκη ποιεῖ") == (False, True)
    assert verify("πρὸς βῆχα", "καὶ πρὸς ἕλκη ποιεῖ") == (False, False)


def test_greek_normalisation():
    assert strip_accents("Ἀψίνθιον") == "αψινθιον"
    assert transliterate("ἀψίνθιον", latinise=True) == "apsinthium"
    assert transliterate("ὑοσκύαμος") == "hyoskyamos"


def test_substance_type_layout():
    assert substance_type_for("dmm", 2, "10") == "animal"
    assert substance_type_for("dmm", 2, "120") == "plant"
    assert substance_type_for("dmm", 1, "40") == "compound_preparation"
