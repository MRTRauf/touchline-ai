from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_unavailable_data_is_explicit():
    root=Path(__file__).resolve().parents[1]
    assert not (root/'deployment/cloud_bundle').exists()
    assert not (root/'deployment/quality_flags.json').exists()
    app=AppTest.from_file(str(root/'app.py')).run(timeout=30)
    assert not app.exception
    assert any('unavailable or inconsistent' in e.value for e in app.error)
