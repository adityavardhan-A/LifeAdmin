"""Module 3 - information extraction with regular expressions.

Dates are read day-first (Indian convention): 12/04/2026 = 12 April 2026.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Dict, Optional, Tuple

# ---------- dates ----------
_DATE = (
    r"(?:\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4}"
    r"|\d{4}-\d{2}-\d{2}"
    r"|\d{1,2}(?:st|nd|rd|th)?[\s\-]+[A-Za-z]{3,9}\.?,?[\s\-]+\d{4}"
    r"|[A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})"
)
_FORMATS = ["%d/%m/%Y", "%Y/%m/%d", "%d %B %Y", "%d %b %Y", "%B %d %Y", "%b %d %Y"]

EXPIRY_LABELS = [
    r"expiry\s*date", r"date\s*of\s*expiry", r"expires?\s*(?:on)?", r"expiration\s*date",
    r"valid\s*(?:until|till|upto|up\s*to|through|thru)", r"valid\s*to",
    r"due\s*date", r"renewal\s*date", r"renew\s*(?:on|by|before)",
    r"warranty\s*(?:valid\s*)?(?:until|till|ends?)", r"next\s*billing\s*date",
    r"end\s*date", r"date\s*of\s*validity",
]
START_LABELS = [
    r"start\s*date", r"issue\s*date", r"date\s*of\s*issue", r"issued\s*on",
    r"valid\s*from", r"commencement\s*date", r"purchase\s*date", r"date\s*of\s*purchase",
    r"invoice\s*date", r"bill\s*date", r"effective\s*date",
]
PERIOD_LABELS = r"(?:period\s*of\s*insurance|policy\s*period|insurance\s*period|validity\s*period|period)"


def parse_date(text: str) -> Optional[date]:
    """Parse a single date string. Returns None if it cannot be understood."""
    s = re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", text.strip(), flags=re.I)
    s = s.replace(",", " ").replace(".", " ") if re.search(r"[A-Za-z]", s) else s
    s = re.sub(r"[\-.]", "/", s) if re.fullmatch(r"\d{1,4}[\-./]\d{1,2}[\-./]\d{1,4}", s) else s
    s = re.sub(r"[\s\-]+", " ", s).strip() if re.search(r"[A-Za-z]", s) else s
    for fmt in _FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _first_date_after(labels: list, text: str) -> Optional[date]:
    for label in labels:
        m = re.search(rf"(?:{label})[^\d\n]{{0,30}}?({_DATE})", text, re.I)
        if m:
            d = parse_date(m.group(1))
            if d:
                return d
    return None


def find_dates(text: str) -> Dict[str, Optional[date]]:
    """Return {'start_date': ..., 'expiry_date': ...}."""
    start = expiry = None
    # "Policy period: 12/04/2026 to 11/04/2027"
    m = re.search(
        rf"{PERIOD_LABELS}[^\d\n]{{0,30}}?({_DATE})[^\d\n]{{0,25}}?(?:to|till|until|and|-)\s*({_DATE})",
        text, re.I)
    if m:
        start, expiry = parse_date(m.group(1)), parse_date(m.group(2))
    start = start or _first_date_after(START_LABELS, text)
    expiry = expiry or _first_date_after(EXPIRY_LABELS, text)
    # "valid from X to Y"
    if not expiry:
        m = re.search(rf"from\s+({_DATE})\s+(?:to|till|until)\s+({_DATE})", text, re.I)
        if m:
            start = start or parse_date(m.group(1))
            expiry = parse_date(m.group(2))
    return {"start_date": start, "expiry_date": expiry}


# ---------- identifiers ----------
_NUMBER_PATTERNS = [
    r"(?:policy|certificate|licen[cs]e|invoice|bill|receipt|registration|document|"
    r"serial|account|consumer|customer|order|membership|roll|enrol(?:l)?ment|passport|"
    r"id|card)\s*(?:no\.?|number|num|#)\s*[:\-]?\s*([A-Z0-9][A-Z0-9/\-]{3,24})",
]
_PAN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
_AADHAAR = re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")
_PASSPORT = re.compile(r"\b[A-PR-WY][0-9]{7}\b")
VEHICLE_RE = re.compile(r"\b([A-Z]{2})[\s\-]?(\d{1,2})[\s\-]?([A-Z]{1,3})[\s\-]?(\d{4})\b")


def find_doc_number(text: str) -> str:
    for pat in _NUMBER_PATTERNS:
        m = re.search(pat, text, re.I)
        if m and re.search(r"\d", m.group(1)):
            return m.group(1).upper().rstrip("-/")
    for rx in (_PAN, _AADHAAR, _PASSPORT):
        m = rx.search(text)
        if m:
            return m.group(0)
    return ""


def find_vehicle_no(text: str) -> str:
    m = VEHICLE_RE.search(text.upper())
    if not m:
        return ""
    return " ".join(m.groups())


# ---------- amount ----------
_AMOUNT = r"(?:Rs\.?|INR|₹)\s?\.?\s?([\d,]+(?:\.\d{1,2})?)"


def find_amount(text: str) -> str:
    for label in (r"total\s*(?:amount|premium|payable)?", r"(?:net\s*)?premium", r"amount\s*(?:due|payable)?",
                  r"grand\s*total", r"price", r"fee"):
        m = re.search(rf"{label}[^\d\n₹]{{0,25}}{_AMOUNT}", text, re.I)
        if m:
            return f"₹{m.group(1)}"
    m = re.search(_AMOUNT, text, re.I)
    return f"₹{m.group(1)}" if m else ""


# ---------- names ----------
_NAME_LABELS = (
    r"(?:insured\s*name|policy\s*holder|policyholder|name\s*of\s*(?:the\s*)?(?:holder|candidate|student|owner|insured)|"
    r"holder\s*name|candidate\s*name|student\s*name|customer\s*name|registered\s*owner|owner\s*name|"
    r"card\s*holder|name)"
)


def find_holder_name(text: str) -> str:
    m = re.search(rf"{_NAME_LABELS}\s*[:\-]\s*([A-Za-z][A-Za-z .']{{2,40}})", text, re.I)
    if m:
        name = re.split(r"\s{2,}|\b(?:DOB|Date|Policy|Address|Age|Sex|Gender)\b", m.group(1))[0]
        return name.strip(" .").title()
    return ""


_ORG_HINT = re.compile(
    r"\b(insurance|assurance|bank|university|institute|college|board|corporation|"
    r"limited|ltd|pvt|private|technologies|motors|electronics|telecom|authority|"
    r"department|council|school|hospital|airlines|energy|power|broadband)\b", re.I)


def find_organization(text: str) -> str:
    m = re.search(r"(?:issued\s*by|insurer|company|issuing\s*authority|provider|seller|sold\s*by|"
                  r"organi[sz]ation|bank|university)\s*[:\-]\s*([^\n]{3,60})", text, re.I)
    if m:
        return m.group(1).strip(" .")
    for line in text.splitlines()[:25]:
        line = line.strip()
        if 3 < len(line) <= 60 and _ORG_HINT.search(line) and not re.search(r"\d{4}", line):
            return line
    return ""


def parse_document(text: str) -> Dict[str, object]:
    """Run every extractor and return a dict of fields."""
    dates = find_dates(text)
    return {
        "holder_name": find_holder_name(text),
        "doc_number": find_doc_number(text),
        "organization": find_organization(text),
        "vehicle_no": find_vehicle_no(text),
        "amount": find_amount(text),
        **dates,
    }
