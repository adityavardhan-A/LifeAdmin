import os
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest

os.environ["LIFEADMIN_DB"] = str(Path(tempfile.mkdtemp()) / "test.db")

from lifeadmin import database as db  # noqa: E402
from lifeadmin.classifier import classify  # noqa: E402
from lifeadmin.export import to_csv, to_ics  # noqa: E402
from lifeadmin.extractor import extract_text, validate_file  # noqa: E402
from lifeadmin.health import health_bar, health_score  # noqa: E402
from lifeadmin.models import Document  # noqa: E402
from lifeadmin.parser import find_dates, find_vehicle_no, parse_date, parse_document  # noqa: E402
from lifeadmin.pipeline import analyse_text  # noqa: E402
from lifeadmin.reminders import evaluate, summarize  # noqa: E402

TODAY = date(2026, 10, 8)


# ---- parser
@pytest.mark.parametrize("raw,expected", [
    ("12/04/2026", date(2026, 4, 12)),
    ("12-04-2026", date(2026, 4, 12)),
    ("2026-04-12", date(2026, 4, 12)),
    ("12 April 2026", date(2026, 4, 12)),
    ("12th Apr, 2026", date(2026, 4, 12)),
    ("April 12, 2026", date(2026, 4, 12)),
])
def test_parse_date_formats(raw, expected):
    assert parse_date(raw) == expected


def test_parse_date_invalid():
    assert parse_date("31/02/2026") is None
    assert parse_date("hello") is None


def test_policy_period():
    d = find_dates("Period of Insurance: 12/04/2026 to 11/04/2027")
    assert d["start_date"] == date(2026, 4, 12) and d["expiry_date"] == date(2027, 4, 11)


def test_labelled_expiry():
    assert find_dates("Valid Until: 05/11/2026")["expiry_date"] == date(2026, 11, 5)
    assert find_dates("Due Date - 17 Oct 2026")["expiry_date"] == date(2026, 10, 17)


def test_vehicle_number():
    assert find_vehicle_no("Reg No TN63AB1234 issued") == "TN 63 AB 1234"


def test_full_insurance_parse():
    text = ("Sundaram General Insurance Company Limited\nPolicy No: INS784521\n"
            "Insured Name: Arun Kumar\nVehicle Registration No: TN 63 AB 1234\n"
            "Period of Insurance: 12/04/2026 to 11/04/2027\nTotal Premium: Rs. 14,250.00")
    f = parse_document(text)
    assert f["doc_number"] == "INS784521"
    assert f["holder_name"] == "Arun Kumar"
    assert f["amount"] == "₹14,250.00"
    assert f["expiry_date"] == date(2027, 4, 11)
    doc, _ = analyse_text(text, "Car Insurance.pdf")
    assert doc.doc_type == "Insurance"


# ---- classifier
def test_classifier_other():
    assert classify("lorem ipsum")[0] == "Other"


def test_classifier_filename_hint():
    assert classify("", "laptop_warranty.pdf")[0] == "Warranty"


# ---- reminders
def test_status_thresholds():
    def lvl(n):
        return evaluate(TODAY + timedelta(days=n), TODAY).level
    assert lvl(31) == "active"
    assert lvl(30) == "warning"
    assert lvl(8) == "warning"
    assert lvl(7) == "critical"
    assert lvl(0) == "critical"
    assert lvl(-1) == "expired"
    assert evaluate(None, TODAY).level == "none"


def test_status_message_singular():
    assert evaluate(TODAY + timedelta(days=1), TODAY).message == "Expires in 1 day."


def test_summarize():
    docs = [Document("a", expiry_date=TODAY + timedelta(days=100)),
            Document("b", expiry_date=TODAY + timedelta(days=5)),
            Document("c", expiry_date=TODAY - timedelta(days=5)),
            Document("d")]
    c = summarize(docs, TODAY)
    assert (c["total"], c["active"], c["expiring_soon"], c["expired"], c["no_expiry"]) == (4, 1, 1, 1, 1)


# ---- health
def test_health():
    full = Document("x", "Insurance", "A", "N1", "Org", expiry_date=TODAY)
    assert health_score(full) == 100
    assert health_score(Document("y")) == 0
    assert health_bar(50) == "█" * 10 + "░" * 10


# ---- extractor
def test_validate_file():
    validate_file("a.pdf", 100)
    with pytest.raises(ValueError):
        validate_file("a.exe", 100)
    with pytest.raises(ValueError):
        validate_file("a.pdf", 0)
    with pytest.raises(ValueError):
        validate_file("a.pdf", 50 * 1024 * 1024)


def test_extract_txt(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello world")
    assert extract_text(p) == "hello world"


# ---- database
def test_database_crud(tmp_path):
    db.init_db()
    doc = Document("car.pdf", "Insurance", "Arun", "P1", "Org", expiry_date=TODAY)
    doc.id = db.add_document(doc)
    got = db.get_document(doc.id)
    assert got.expiry_date == TODAY and got.doc_type == "Insurance"
    got.organization = "New Org"
    db.update_document(got)
    assert db.get_document(doc.id).organization == "New Org"
    db.dismiss_reminder(doc.id)
    assert doc.id in db.dismissed_ids()
    db.restore_reminder(doc.id)
    assert doc.id not in db.dismissed_ids()
    assert len(db.list_logs()) >= 3
    db.delete_document(doc.id)
    assert db.get_document(doc.id) is None


def test_exports():
    docs = [Document("a.pdf", "Bill", expiry_date=TODAY, id=1), Document("b.pdf", id=2)]
    assert "a.pdf" in to_csv(docs, TODAY)
    ics = to_ics(docs)
    assert ics.count("BEGIN:VEVENT") == 1 and "DTSTART;VALUE=DATE:20261008" in ics


# ---- word / excel extraction
def test_extract_docx(tmp_path):
    docx = pytest.importorskip("docx")
    d = docx.Document()
    for line in ["LIC Life Insurance Policy", "Policy No: LIC4455667", "Expiry Date: 01/11/2026"]:
        d.add_paragraph(line)
    p = tmp_path / "policy.docx"
    d.save(p)
    text = extract_text(p)
    assert "LIC4455667" in text
    assert find_dates(text)["expiry_date"] == date(2026, 11, 1)


def test_extract_xlsx(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Next Billing Date", date(2026, 10, 15)])
    ws.append(["Amount", "Rs. 649"])
    p = tmp_path / "sub.xlsx"
    wb.save(p)
    text = extract_text(p)
    assert "Next Billing Date: 15/10/2026" in text
    assert parse_document(text)["amount"] == "₹649"


def test_validate_office_types():
    validate_file("a.docx", 10)
    validate_file("a.xlsx", 10)


# ---- dashboard buckets & reminder lists
def test_dashboard_counts_and_lists():
    from lifeadmin.reminders import dashboard_counts, overdue, upcoming
    docs = [Document("a", expiry_date=TODAY + timedelta(days=100)),
            Document("b", expiry_date=TODAY + timedelta(days=20)),
            Document("c", expiry_date=TODAY + timedelta(days=3)),
            Document("d", expiry_date=TODAY - timedelta(days=5)),
            Document("e")]
    c = dashboard_counts(docs, TODAY)
    assert c == {"total": 5, "active": 2, "expiring": 1, "critical": 2}
    assert [d.filename for d in upcoming(docs, TODAY)] == ["c", "b", "a"]
    assert [d.filename for d in overdue(docs, TODAY)] == ["d"]


def test_collection_health():
    from lifeadmin.health import collection_score, timeliness_score
    fresh = Document("x", "Insurance", "A", "N1", "Org", expiry_date=TODAY + timedelta(days=90))
    stale = Document("y", "Insurance", "A", "N1", "Org", expiry_date=TODAY - timedelta(days=1))
    assert timeliness_score(fresh, TODAY) == 100 and timeliness_score(stale, TODAY) == 0
    assert collection_score([fresh, stale], TODAY) == 75
    assert collection_score([], TODAY) == 100


# ---- display helpers
def test_preview_helpers():
    from lifeadmin.preview import friendly_title, human_size, mask_number
    assert mask_number("1234 5678 9012") == "XXXX-XXXX-9012"
    assert mask_number("INS784521") == "INS784521"
    assert friendly_title("old_puc.pdf") == "Old PUC"
    assert friendly_title("1791451049_car_insurance.pdf") == "Car Insurance"
    assert human_size(2048) == "2 KB" and human_size(None) == ""


def test_user_name():
    db.init_db()
    db.set_user_name("Asha Rao")
    assert db.get_user_name() == "Asha Rao"
    with pytest.raises(ValueError):
        db.set_user_name("  ")
