"""Headless check that every Streamlit page renders without errors."""
import os, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["LIFEADMIN_DB"] = str(Path(tempfile.mkdtemp()) / "smoke.db")

from streamlit.testing.v1 import AppTest

from lifeadmin import database as db
from lifeadmin.pipeline import analyse_file

root = Path(__file__).resolve().parent.parent
db.init_db()
for p in sorted((root / "sample_docs").glob("*.pdf")):
    doc, _, _ = analyse_file(p)
    db.add_document(doc)

for page in ["Dashboard", "Upload", "Documents", "Reminders"]:
    at = AppTest.from_file(str(root / "app.py"), default_timeout=30)
    at.session_state["nav"] = page
    at.run()
    assert not at.exception, (page, at.exception)
    print("OK:", page)
