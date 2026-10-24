"""Data model (OOP): a Document dataclass shared by every module."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional

DOC_TYPES = [
    "ID", "Insurance", "Certificate", "Bill",
    "Warranty", "Vehicle", "Subscription", "Other",
]


def to_iso(d: Optional[date]) -> str:
    return d.isoformat() if d else ""


def from_iso(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


@dataclass
class Document:
    filename: str
    doc_type: str = "Other"
    holder_name: str = ""
    doc_number: str = ""
    organization: str = ""
    vehicle_no: str = ""
    amount: str = ""
    start_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: str = ""
    stored_path: str = ""
    uploaded_at: str = ""
    id: Optional[int] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["start_date"] = to_iso(self.start_date)
        d["expiry_date"] = to_iso(self.expiry_date)
        return d

    @classmethod
    def from_row(cls, row) -> "Document":
        r = dict(row)
        r["start_date"] = from_iso(r.get("start_date"))
        r["expiry_date"] = from_iso(r.get("expiry_date"))
        return cls(**r)
