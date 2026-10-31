from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

SCRIPT = """
from pathlib import Path
from matcher import extract_pdf
from pipeline import run_analysis
from ui import render_results
S = Path('sample_data')
t, p = extract_pdf(S / 'sample_resume.pdf')
render_results(run_analysis(t, (S / 'sample_jd.txt').read_text(), 'combined', p))
"""


def test_results_render_without_error():
    at = AppTest.from_string(SCRIPT, default_timeout=60).run()
    assert not at.exception, at.exception
    assert len(at.tabs) == 5


def test_app_loads():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception, at.exception
    assert any("Analyze" in b.label for b in at.button)


def test_sample_button_flow():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    at.checkbox[0].check()
    next(b for b in at.button if "Analyze" in b.label).click()
    at.run()
    assert not at.exception, at.exception
    assert len(at.tabs) == 5
