"""Load the 24 demo documents into LifeAdmin.

    python scripts/load_demo.py            # add/refresh the demo documents
    python scripts/load_demo.py --reset    # back up the database, start empty, then load

Dates are generated relative to today, so the demo always shows overdue,
due-today, critical, expiring-soon, active and no-expiry documents.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lifeadmin.demo import load_demo, reset_database  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="back up the database and start empty first")
    args = ap.parse_args()
    if args.reset:
        backup = reset_database()
        if backup:
            print(f"Backed up the old database to {backup}")
    n = load_demo()
    print(f"Loaded {n} demo documents. Run: streamlit run app.py")
