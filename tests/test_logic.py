"""Logic tests: identification model, metrics, Galen helpers, provenance guard, modern use groups."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pharmakon.common import wilson_ci, write_table
from pharmakon.corpus.galen import containment, heading_names, stem
from pharmakon.forecast.run import metrics, precision_at
from pharmakon.identify.model import CLogit, Unit, ece, unit_metrics
from pharmakon.link.taxonomy import clean_name
from pharmakon.persist.modern import _use_groups


def _synthetic(n_units=80, seed=0):
    """Candidate 0 carries a strong positive feature; ∅ is right when no candidate has it."""
    rng = np.random.default_rng(seed)
    units = []
    for i in range(n_units):
        k = int(rng.integers(2, 5))
        X = rng.normal(size=(k, 2))
        y = np.zeros(k + 1)
        if i % 5 == 0:
            y[-1] = 1.0
            X[:, 0] -= 2.0
        else:
            X[0, 0] += 3.0
            y[0] = 1.0
        units.append(Unit(str(i), X, y))
    return units


def test_clogit_learns_signal_and_none_bucket():
    units = _synthetic()
    m = CLogit(l2=0.1).fit(units)
    assert m.w[0] > 1.0  # the informative feature gets a large positive weight
    acc = np.mean([np.argmax(m.predict(u.X)) == np.argmax(u.y) for u in units])
    assert acc > 0.85
    p = m.predict(units[1].X)
    assert abs(p.sum() - 1) < 1e-9 and len(p) == len(units[1].X) + 1


def test_temperature_scaling_bounds():
    units = _synthetic()
    m = CLogit().fit(units)
    T = m.fit_temperature(units, [m.utilities(u.X) for u in units])
    assert 0.25 <= T <= 8.0


def test_unit_metrics_and_ece():
    p = np.array([0.7, 0.2, 0.1])
    y = np.array([1.0, 0.0, 0.0])
    m = unit_metrics(p, y)
    assert m["top1"] == 1.0 and m["rr"] == 1.0 and abs(m["logloss"] + np.log(0.7)) < 1e-9
    e, rows = ece(np.array([0.9, 0.9, 0.2]), np.array([1.0, 0.0, 0.0]))
    assert 0 <= e <= 1 and sum(r["n"] for r in rows) == 3


def test_precision_at_k_and_metrics():
    y = np.array([1, 0, 1, 0, 0])
    s = np.array([0.9, 0.8, 0.7, 0.1, 0.0])
    assert precision_at(y, s, 2) == 0.5
    m = metrics(y, s)
    assert m["positives"] == 2 and 0 < m["auprc"] <= 1


def test_wilson_ci():
    lo, hi = wilson_ci(8, 10)
    assert 0.4 < lo < 0.8 < hi <= 1.0


def test_write_table_refuses_missing_provenance(tmp_path: Path):
    with pytest.raises(ValueError):
        write_table(pd.DataFrame({"a": [1]}), tmp_path / "x.parquet")
    df = pd.DataFrame({"a": [1], "source_id": ["s"], "retrieved_at": ["t"], "method": ["m"]})
    assert write_table(df, tmp_path / "ok.parquet").exists()


def test_galen_heading_and_stem():
    assert heading_names("α΄. Περὶ ἀβροτόνου τε καὶ ἀψινθίου καὶ τῶν ἑκατέρου εἰδῶν.") == ["αβροτονου", "αψινθιου"]
    assert stem("αβροτονου") == stem("αβροτονον")
    assert containment("ἡ δὲ ῥίζα πρὸς ἕλκη ἁρμόζει", "ἡ δὲ ῥίζα πρὸς ἕλκη ἁρμόζει καλῶς") == 1.0
    assert containment("ἄλλο τι λέγει ὁ Γαληνός", "ἡ δὲ ῥίζα πρὸς ἕλκη") == 0.0


def test_clean_name_strips_authors():
    assert clean_name("Asphodelus aestivus Brot.") == "Asphodelus aestivus"
    assert clean_name("Cirsium ferox (L.) DC.") == "Cirsium ferox"
    assert clean_name("Anthemis rosea Sm subsp. rosea") == "Anthemis rosea"


def test_modern_use_groups():
    assert "DE" in _use_groups("Cuts/wounds/burns (4)")
    assert set(_use_groups("Decoction of leaves as diuretic and against dysentery")) >= {"UR", "GI"}
