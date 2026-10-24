"""Module 6 - smart reminder logic.

    > 30 days  -> Active
    <= 30 days -> Warning  (Expiring soon)
    <= 7 days  -> Critical
    < 0 days   -> Expired
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Iterable, List, Optional

from .models import Document

WARNING_DAYS = 30
CRITICAL_DAYS = 7


@dataclass(frozen=True)
class Status:
    level: str          # active | warning | critical | expired | none
    label: str
    icon: str
    days: Optional[int]
    message: str
    action: str


def _plural(n: int) -> str:
    return f"{n} day" if abs(n) == 1 else f"{n} days"


def evaluate(expiry: Optional[date], today: Optional[date] = None) -> Status:
    today = today or date.today()
    if expiry is None:
        return Status("none", "NO EXPIRY", "⚪", None,
                      "No expiry date recorded.", "Add an expiry date if this document has one.")
    days = (expiry - today).days
    renew_by = max(today, expiry - timedelta(days=3))
    renew_text = f"Renew before {renew_by.day} {renew_by.strftime('%B %Y')}."
    if days < 0:
        return Status("expired", "EXPIRED", "🔴", days,
                      f"Expired {_plural(-days)} ago.", "Renew immediately.")
    if days == 0:
        return Status("critical", "CRITICAL", "🔴", 0, "Expires today.", "Renew today.")
    if days <= CRITICAL_DAYS:
        return Status("critical", "CRITICAL", "🔴", days, f"Expires in {_plural(days)}.", renew_text)
    if days <= WARNING_DAYS:
        return Status("warning", "EXPIRING SOON", "🟠", days, f"Expires in {_plural(days)}.", renew_text)
    return Status("active", "ACTIVE", "🟢", days, f"{_plural(days)} remaining.", "No action needed.")


def status_of(doc: Document, today: Optional[date] = None) -> Status:
    return evaluate(doc.expiry_date, today)


def summarize(docs: Iterable[Document], today: Optional[date] = None) -> Dict[str, int]:
    counts = {"total": 0, "active": 0, "expiring_soon": 0, "critical": 0, "expired": 0, "no_expiry": 0}
    for d in docs:
        counts["total"] += 1
        level = status_of(d, today).level
        if level == "active":
            counts["active"] += 1
        elif level == "warning":
            counts["expiring_soon"] += 1
        elif level == "critical":
            counts["expiring_soon"] += 1
            counts["critical"] += 1
        elif level == "expired":
            counts["expired"] += 1
        else:
            counts["no_expiry"] += 1
    return counts


def needing_attention(docs: Iterable[Document], today: Optional[date] = None) -> List[Document]:
    """Documents that are expired/critical/warning, most urgent first."""
    urgent = [d for d in docs if status_of(d, today).level in {"expired", "critical", "warning"}]
    return sorted(urgent, key=lambda d: d.expiry_date)


# ---------------------------------------------------------------- dashboard view
# The dashboard (Figure 2) groups everything into three buckets:
#   active    -> > 30 days left, or no expiry date at all ("Up to date")
#   expiring  -> 8-30 days left                           ("Within 30 days")
#   critical  -> <= 7 days left or already expired        ("Overdue / Needs attention")
def bucket(doc: Document, today: Optional[date] = None) -> str:
    level = status_of(doc, today).level
    if level in {"critical", "expired"}:
        return "critical"
    if level == "warning":
        return "expiring"
    return "active"


def dashboard_counts(docs: Iterable[Document], today: Optional[date] = None) -> Dict[str, int]:
    counts = {"total": 0, "active": 0, "expiring": 0, "critical": 0}
    for d in docs:
        counts["total"] += 1
        counts[bucket(d, today)] += 1
    return counts


def upcoming(docs: Iterable[Document], today: Optional[date] = None) -> List[Document]:
    """Documents whose expiry is today or later, soonest first."""
    today = today or date.today()
    return sorted((d for d in docs if d.expiry_date and d.expiry_date >= today),
                  key=lambda d: d.expiry_date)


def overdue(docs: Iterable[Document], today: Optional[date] = None) -> List[Document]:
    """Documents already past their expiry, most overdue first."""
    today = today or date.today()
    return sorted((d for d in docs if d.expiry_date and d.expiry_date < today),
                  key=lambda d: d.expiry_date)
