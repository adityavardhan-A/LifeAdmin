"""Every demo sample must be read, classified and given the intended status."""
import importlib.util
import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

os.environ.setdefault("LIFEADMIN_DB", str(Path(tempfile.mkdtemp()) / "test.db"))

pytest.importorskip("reportlab")
pytest.importorskip("docx")
pytest.importorskip("openpyxl")

from lifeadmin.pipeline import analyse_file  # noqa: E402
from lifeadmin.reminders import status_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TODAY = date(2026, 10, 15)


def _ms():
    spec = importlib.util.spec_from_file_location("make_samples", ROOT / "scripts" / "make_samples.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_samples_cover_every_case(tmp_path):
    ms = _ms()
    paths = ms.main(TODAY, tmp_path)
    assert len(paths) >= 20
    levels = set()
    for p in paths:
        doc, _, _ = analyse_file(p)
        expected_type, expected_level = ms.EXPECTED[p.name]
        level = status_of(doc, TODAY).level
        assert (doc.doc_type, level) == (expected_type, expected_level), p.name
        levels.add(level)
    assert levels == {"expired", "critical", "warning", "active", "none"}
    assert {p.suffix for p in paths} == {".pdf", ".docx", ".xlsx", ".txt"}
