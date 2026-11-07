"""Smoke-test every explorer page with Streamlit's AppTest against the committed processed data."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "src" / "pharmakon" / "app"
PAGES = [APP / "Home.py", *sorted((APP / "pages").glob("*.py"))]


@pytest.mark.skipif(not (APP.parents[2] / "data" / "processed" / "passages.parquet").exists(), reason="processed data not present")
@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.stem)
def test_page_renders_without_exception(page):
    at = AppTest.from_file(str(page), default_timeout=60)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert any("not medical advice" in w.value for w in at.warning)
