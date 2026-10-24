"""Document Intelligence Score - how complete is the extracted information?"""
from __future__ import annotations

from typing import List, Tuple

from .models import Document

BAR_WIDTH = 20


def checks(doc: Document) -> List[Tuple[str, bool]]:
    return [
        ("Document type", doc.doc_type not in ("", "Other")),
        ("Organization", bool(doc.organization.strip())),
        ("Holder name", bool(doc.holder_name.strip())),
        ("Document number", bool(doc.doc_number.strip())),
        ("Expiry date", doc.expiry_date is not None),
    ]


def health_score(doc: Document) -> int:
    results = checks(doc)
    return round(100 * sum(ok for _, ok in results) / len(results))


def health_bar(score: int) -> str:
    filled = round(BAR_WIDTH * score / 100)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def verdict(score: int) -> str:
    if score == 100:
        return "Your document is complete and valid for tracking."
    if score >= 60:
        return "Mostly complete - review the missing fields so reminders stay reliable."
    return "Too little information was found - please fill in the missing fields."


# ---------------------------------------------------------------- timeliness
# Completeness (above) says whether the details were captured; timeliness says
# whether the document is still valid. Together they make the Health Score.
TIMELINESS = {"active": 100, "none": 100, "warning": 60, "critical": 25, "expired": 0}


def timeliness_score(doc: Document, today=None) -> int:
    from .reminders import status_of
    return TIMELINESS[status_of(doc, today).level]


def overall_score(doc: Document, today=None) -> int:
    """Average of completeness and timeliness for one document (0-100)."""
    return round((health_score(doc) + timeliness_score(doc, today)) / 2)


def collection_score(docs, today=None) -> int:
    """Health of the whole vault: mean overall score (100 when empty)."""
    docs = list(docs)
    if not docs:
        return 100
    return round(sum(overall_score(d, today) for d in docs) / len(docs))
