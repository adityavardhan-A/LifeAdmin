"""Exports: CSV (Pandas) and ICS calendar file with expiry reminders."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Iterable, List, Optional

import pandas as pd

from .models import Document
from .reminders import status_of


def documents_dataframe(docs: Iterable[Document], today: Optional[date] = None) -> pd.DataFrame:
    rows = []
    for d in docs:
        s = status_of(d, today)
        rows.append({
            "ID": d.id, "Type": d.doc_type, "File": d.filename, "Holder": d.holder_name,
            "Number": d.doc_number, "Organization": d.organization, "Vehicle": d.vehicle_no,
            "Amount": d.amount, "Start": d.start_date, "Expiry": d.expiry_date,
            "Days left": s.days, "Status": f"{s.icon} {s.label}",
        })
    cols = ["ID", "Type", "File", "Holder", "Number", "Organization", "Vehicle",
            "Amount", "Start", "Expiry", "Days left", "Status"]
    return pd.DataFrame(rows, columns=cols)


def to_csv(docs: Iterable[Document], today: Optional[date] = None) -> str:
    return documents_dataframe(docs, today).to_csv(index=False)


def to_ics(docs: Iterable[Document]) -> str:
    """One all-day event per expiry date, with a 7-day and 30-day alarm."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines: List[str] = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//LifeAdmin//EN", "CALSCALE:GREGORIAN"]
    for d in docs:
        if not d.expiry_date:
            continue
        end = d.expiry_date + timedelta(days=1)
        title = f"{d.doc_type} expires: {d.filename}".replace(",", " ")
        lines += [
            "BEGIN:VEVENT",
            f"UID:lifeadmin-{d.id}-{d.expiry_date:%Y%m%d}@lifeadmin.local",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{d.expiry_date:%Y%m%d}",
            f"DTEND;VALUE=DATE:{end:%Y%m%d}",
            f"SUMMARY:{title}",
            f"DESCRIPTION:{(d.organization or '')} {(d.doc_number or '')}".strip(),
        ]
        for days in (30, 7):
            lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{title}",
                      f"TRIGGER:-P{days}D", "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
