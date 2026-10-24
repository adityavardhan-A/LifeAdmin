"""LifeAdmin look & feel: theme CSS, inline SVG icons and small HTML components.

Everything visual lives here so app.py can stay about behaviour. The layout
follows the screen designs in the project document (Figures 2-4): dark navy
canvas, left navigation, rounded cards, coloured status pills.
"""
from __future__ import annotations

import base64
import calendar
import html as _html
from datetime import date
from typing import Dict, Iterable, List, Optional, Tuple

import streamlit as st

# ---------------------------------------------------------------- palette
C = {
    "bg": "#070B1F",
    "panel": "#0D1330",
    "panel2": "#111838",
    "line": "rgba(110, 125, 220, 0.16)",
    "text": "#E8ECFF",
    "muted": "#8B93B8",
    "indigo": "#5B5EF4",
    "indigo2": "#7C7FFA",
    "green": "#22C55E",
    "amber": "#F5A524",
    "red": "#EF4444",
    "blue": "#3B82F6",
    "slate": "#64748B",
}

# status level -> (pill label, text colour, background)
PILL = {
    "active": ("Active", "#4ADE80", "rgba(34,197,94,0.14)"),
    "warning": ("Expiring Soon", "#FBBF24", "rgba(245,165,36,0.14)"),
    "critical": ("Critical", "#F87171", "rgba(239,68,68,0.16)"),
    "expired": ("Overdue", "#F87171", "rgba(239,68,68,0.16)"),
    "none": ("No Expiry", "#A5B4FC", "rgba(99,102,241,0.14)"),
    "processed": ("Processed", "#4ADE80", "rgba(34,197,94,0.14)"),
    "pending": ("Pending", "#93C5FD", "rgba(59,130,246,0.16)"),
    "completed": ("Completed", "#A5B4FC", "rgba(99,102,241,0.16)"),
    "upcoming": ("Upcoming", "#4ADE80", "rgba(34,197,94,0.14)"),
}

# ---------------------------------------------------------------- icons
# Stroke icons on a 24x24 grid.
_ICON_PATHS: Dict[str, str] = {
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5"/>',
    "upload": '<path d="M4 14.9A7 7 0 1 1 15.7 8h1.8a4.5 4.5 0 0 1 2.5 8.2"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    "files": '<path d="M15 2H8a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z"/><path d="M15 2v5h5"/><path d="M4 7v13a2 2 0 0 0 2 2h10"/>',
    "check": '<circle cx="12" cy="12" r="10"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "alert": '<circle cx="12" cy="12" r="10"/><path d="M12 7.5v5"/><path d="M12 16.5h.01"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "car": '<path d="M5 17H3v-5l2-5h14l2 5v5h-2"/><path d="M3 12h18"/><circle cx="7.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/><path d="M9.5 17h5"/>',
    "id": '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="11" r="2"/><path d="M14 10h4"/><path d="M14 14h4"/><path d="M5 16c.6-1.2 1.7-1.8 3-1.8s2.4.6 3 1.8"/>',
    "cap": '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 2 9 2 12 0v-5"/><path d="M22 10v6"/>',
    "receipt": '<path d="M5 2h14v20l-2.3-1.5L14.3 22 12 20.5 9.7 22l-2.4-1.5L5 22z"/><path d="M9 7h6"/><path d="M9 11h6"/><path d="M9 15h4"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"/>',
    "repeat": '<path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M3 21v-5h5"/>',
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/>',
    "sparkle": '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3z"/>',
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
    "list": '<path d="M9 6h12"/><path d="M9 12h12"/><path d="M9 18h12"/><path d="M4 6h.01"/><path d="M4 12h.01"/><path d="M4 18h.01"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M8 17V11"/><path d="M13 17V7"/><path d="M18 17v-4"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "history": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
}

TYPE_STYLE: Dict[str, Tuple[str, str]] = {   # doc type -> (icon, colour)
    "ID": ("id", "#6366F1"),
    "Insurance": ("shield", "#14B8A6"),
    "Vehicle": ("car", "#8B5CF6"),
    "Certificate": ("cap", "#6366F1"),
    "Bill": ("receipt", "#F97316"),
    "Warranty": ("wrench", "#06B6D4"),
    "Subscription": ("repeat", "#EC4899"),
    "Other": ("file", "#64748B"),
}


def esc(s: object) -> str:
    return _html.escape(str(s if s is not None else ""))


def icon(name: str, size: int = 18, color: str = "currentColor", stroke: float = 1.8) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'style="flex-shrink:0">{_ICON_PATHS[name]}</svg>')


def icon_tile(name: str, color: str, size: int = 40, radius: int = 11, icon_size: int = 20,
              solid: bool = False) -> str:
    bg = color if solid else _alpha(color, 0.16)
    fg = "#fff" if solid else color
    return (f'<div class="la-tile" style="width:{size}px;height:{size}px;border-radius:{radius}px;'
            f'background:{bg};color:{fg}">{icon(name, icon_size, fg)}</div>')


def type_tile(doc_type: str, size: int = 40) -> str:
    name, color = TYPE_STYLE.get(doc_type, TYPE_STYLE["Other"])
    return icon_tile(name, color, size)


def file_badge(filename: str, size: int = 30) -> str:
    """Small coloured file glyph: red PDF, blue image, Word, Excel, text."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    color, label = {
        "pdf": ("#EF4444", "PDF"), "png": ("#3B82F6", ""), "jpg": ("#3B82F6", ""),
        "jpeg": ("#3B82F6", ""), "docx": ("#2563EB", "W"), "xlsx": ("#16A34A", "X"),
        "txt": ("#64748B", "TXT"),
    }.get(ext, ("#64748B", ""))
    h = size
    w = round(size * 0.8)
    inner = (f'<text x="12" y="17.2" text-anchor="middle" font-size="{6 if len(label) > 1 else 8}" '
             f'font-weight="800" fill="#fff" font-family="Inter,Arial">{label}</text>' if label else
             '<circle cx="9.5" cy="11" r="1.6" fill="#fff"/><path d="M5.5 19l4.5-4.5 2.5 2.5 2.5-3 3.5 5z" fill="#fff"/>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 24 28" style="flex-shrink:0">'
            f'<path d="M3 2.5A2.5 2.5 0 0 1 5.5 0H15l6 6v19.5a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 25.5z" fill="{color}"/>'
            f'<path d="M15 0v4.5A1.5 1.5 0 0 0 16.5 6H21z" fill="#fff" fill-opacity=".45"/>{inner}</svg>')


def _alpha(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


def pill(kind: str, label: Optional[str] = None) -> str:
    text, fg, bg = PILL.get(kind, PILL["none"])
    return f'<span class="la-pill" style="color:{fg};background:{bg}">{esc(label or text)}</span>'


# ---------------------------------------------------------------- brand art
LOGO_SVG = (
    '<svg width="34" height="34" viewBox="0 0 48 48" aria-hidden="true">'
    '<defs><linearGradient id="lg-oct" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#FF7A5C"/><stop offset="1" stop-color="#E5483A"/></linearGradient></defs>'
    '<path fill="url(#lg-oct)" d="M24 3C15.7 3 10 9 10 16.5c0 4.4 1.9 7.6 4.6 9.6L10.2 33c-1.2 1.9-3.4 2.4-5 1.6 '
    '1 2.6 4.6 3.4 7 1.4l4.4-5.2-1.2 7.4c-.4 2-2 3.3-3.8 3.4 2.2 1.6 5.6.8 6.6-1.9L20.4 32l1.2 9.4c.2 1.4 1.1 '
    '2.6 2.4 2.6s2.2-1.2 2.4-2.6l1.2-9.4 2.2 7.8c1 2.7 4.4 3.5 6.6 1.9-1.8-.1-3.4-1.4-3.8-3.4l-1.2-7.4 4.4 5.2c2.4 '
    '2 6 1.2 7-1.4-1.6.8-3.8.3-5-1.6l-4.4-6.9c2.7-2 4.6-5.2 4.6-9.6C38 9 32.3 3 24 3z"/>'
    '<ellipse cx="19" cy="16" rx="3.2" ry="3.6" fill="#fff"/><ellipse cx="29" cy="16" rx="3.2" ry="3.6" fill="#fff"/>'
    '<circle cx="19.6" cy="16.8" r="1.6" fill="#1B1F3B"/><circle cx="29.6" cy="16.8" r="1.6" fill="#1B1F3B"/>'
    '<path d="M21 22.5c1.8 1.3 4.2 1.3 6 0" stroke="#7A1E16" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
    '</svg>'
)

MOUNTAIN_SVG = (
    '<svg class="la-mtn" viewBox="0 0 360 120" preserveAspectRatio="xMaxYMax slice" aria-hidden="true">'
    '<defs><linearGradient id="m1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3F9E"/>'
    '<stop offset="1" stop-color="#1A1E5A"/></linearGradient>'
    '<linearGradient id="m2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4C52C9"/>'
    '<stop offset="1" stop-color="#232877"/></linearGradient></defs>'
    '<path d="M0 120 L70 62 L120 92 L190 40 L250 85 L300 55 L360 90 L360 120Z" fill="url(#m1)" opacity=".75"/>'
    '<path d="M120 120 L215 52 L262 86 L300 66 L360 104 L360 120Z" fill="url(#m2)"/>'
    '<path d="M300 66 L300 34" stroke="#C7CAFF" stroke-width="2"/><path d="M300 34 L318 40 L300 46Z" fill="#7C7FFA"/>'
    '<circle cx="246" cy="22" r="1.2" fill="#C7CAFF"/><circle cx="272" cy="10" r="1" fill="#C7CAFF"/>'
    '<circle cx="318" cy="26" r="1.3" fill="#C7CAFF"/><circle cx="344" cy="12" r="1" fill="#C7CAFF"/></svg>'
)

# ---------------------------------------------------------------- CSS
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root { --la-bg:#070B1F; --la-panel:#0D1330; --la-panel2:#111838; --la-line:rgba(110,125,220,.16);
        --la-text:#E8ECFF; --la-muted:#8B93B8; --la-indigo:#5B5EF4; }

html, body, .stApp, [class*="css"], button, input, textarea, select { font-family:'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif !important; }
/* keep Streamlit's icon font for :material/ icons */
[data-testid="stIconMaterial"], span[role="img"][translate="no"] { font-family:'Material Symbols Rounded' !important; }

.stApp { background: radial-gradient(1200px 600px at 70% -10%, rgba(76,82,201,.14), transparent 60%), var(--la-bg) !important; color:var(--la-text); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display:none !important; }
header[data-testid="stHeader"] { background:transparent !important; height:0 !important; }
.block-container, [data-testid="stMainBlockContainer"] { padding:1.1rem 2rem 2.5rem 2rem !important; max-width:1480px; }
h1, h2, h3, h4 { color:var(--la-text) !important; letter-spacing:-.01em; }
p, li, label, span { color:inherit; }
a { color:#A5B4FC; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background:#080C22 !important; border-right:1px solid rgba(110,125,220,.12) !important; min-width:244px !important; max-width:244px !important; }
[data-testid="stSidebarHeader"] { height:.6rem !important; min-height:.6rem !important; padding:0 !important; }
[data-testid="stSidebarUserContent"] { padding:0 .9rem 1.2rem .9rem !important; min-height:calc(100vh - 1.2rem); display:flex; flex-direction:column; }
[data-testid="stSidebarUserContent"] > div:first-child { flex:1; display:flex; flex-direction:column; }
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] { flex:1; }
.st-key-sidebar_footer, [data-testid="stSidebar"] [data-testid="stLayoutWrapper"]:has(> .st-key-sidebar_footer),
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has(> div > .st-key-sidebar_footer) { margin-top:auto !important; }
.la-brand { display:flex; align-items:center; gap:.6rem; padding:.55rem .35rem 1.3rem .35rem; }
.la-brand span { font-weight:800; font-size:1.28rem; color:#fff; letter-spacing:-.02em; }
.la-motto { color:#8B93B8; font-size:.78rem; line-height:1.35; padding:0 .4rem; }
.la-motto i { display:block; width:34px; height:2px; border-radius:2px; background:#5B5EF4; margin-top:.55rem; }

[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stRadio"]),
[data-testid="stSidebar"] [data-testid="stRadio"], [data-testid="stSidebar"] [data-testid="stRadio"] > div { width:100% !important; max-width:100% !important; }
[data-testid="stSidebar"] [role="radiogroup"] { gap:.3rem !important; width:100%; }
[data-testid="stSidebar"] [role="radiogroup"] > div { width:100%; }
[data-testid="stSidebar"] [role="radiogroup"] label { width:100%; margin:0 !important; padding:.62rem .8rem !important; border-radius:10px;
    color:#AEB5D6 !important; font-weight:500; transition:background .15s ease, color .15s ease; cursor:pointer; }
[data-testid="stSidebar"] [role="radiogroup"] label p { font-size:.92rem !important; display:flex; align-items:center; gap:.65rem; }
[data-testid="stSidebar"] [role="radiogroup"] label span[role="img"] { font-size:1.2rem !important; }
/* hide the radio circles */
[data-testid="stSidebar"] [role="radiogroup"] label div:has(+ [data-testid="stMarkdownContainer"]),
[data-testid="stSidebar"] [role="radiogroup"] label[data-baseweb="radio"] > div:first-child { display:none !important; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(91,94,244,.12); color:#fff !important; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background:linear-gradient(90deg,#3E41C9,#4B4FE0); color:#fff !important;
    box-shadow:0 6px 18px rgba(75,79,224,.35); }

/* ---------- top bar ---------- */
.st-key-topbar { margin-bottom:.4rem; }
.st-key-topsearch input { background:#0F1535 url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238B93B8' stroke-width='2' stroke-linecap='round'><circle cx='11' cy='11' r='7'/><path d='m21 21-4.3-4.3'/></svg>") no-repeat 12px center !important;
    padding-left:36px !important; border-radius:10px !important; color:var(--la-text) !important; height:38px; }
.st-key-topsearch [data-baseweb="input"], .st-key-topsearch [data-baseweb="base-input"] { background:transparent !important; border:1px solid var(--la-line) !important; border-radius:10px !important; }
[class*="st-key-bell"] button { background:transparent !important; border:none !important; box-shadow:none !important; padding:.3rem .5rem !important; min-height:38px; position:relative; }
[class*="st-key-bell"] button div[aria-hidden="true"], [class*="st-key-bell"] button > div:has(> svg) { display:none !important; }
[class*="st-key-bell"] button span[role="img"] { font-size:1.35rem !important; color:#C9CEEA; }
.st-key-bell_on button::after { content:""; position:absolute; top:7px; right:9px; width:8px; height:8px; border-radius:50%; background:#EF4444; box-shadow:0 0 0 2px var(--la-bg); }
.st-key-avatar button { background:transparent !important; border:none !important; box-shadow:none !important; min-height:38px; gap:.2rem; }
.st-key-avatar button p { white-space:nowrap; font-weight:600 !important; font-size:.9rem !important; color:#E8ECFF; }
.st-key-avatar button::before { width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#6D6FF7,#4338CA);
    color:#fff; font-weight:700; font-size:.78rem; display:inline-flex; align-items:center; justify-content:center; margin-right:.5rem; }

/* ---------- cards ---------- */
div[class*="st-key-card"] { background:linear-gradient(180deg, rgba(17,24,56,.92), rgba(13,19,48,.92)) !important;
    border:1px solid var(--la-line) !important; border-radius:16px !important; padding:1.05rem 1.15rem !important; }
div[class*="st-key-card"] [data-testid="stVerticalBlockBorderWrapper"] { border:none !important; }
.la-card-title { display:flex; align-items:center; gap:.55rem; font-weight:700; font-size:.98rem; color:#fff; min-height:32px; }
.la-card-title svg { color:#8F94FF; }
.la-sub { color:var(--la-muted); font-size:.82rem; }
button[kind="tertiary"] { color:#A5B4FC !important; font-size:.8rem !important; font-weight:600 !important; padding:.15rem 0 !important; min-height:0 !important; }
button[kind="tertiary"]:hover { color:#fff !important; }
div[class*="st-key-viewall"] { display:flex; justify-content:flex-end; }
div[class*="st-key-viewall"] [data-testid="stButton"] { margin-left:auto; }

/* page header */
.la-head { display:flex; align-items:center; gap:.9rem; margin:.25rem 0 1.1rem 0; }
.la-head h1 { font-size:1.55rem !important; font-weight:700 !important; margin:0 !important; padding:0 !important; line-height:1.2; }
.la-head p { margin:.15rem 0 0 0; color:var(--la-muted); font-size:.9rem; }
.la-greet h1 { font-size:1.6rem !important; font-weight:700 !important; margin:0 !important; padding:.2rem 0 0 0 !important; }
.la-greet p { margin:.2rem 0 1.1rem 0; color:var(--la-muted); font-size:.92rem; }

.la-tile { display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.la-pill { display:inline-block; padding:.22rem .62rem; border-radius:999px; font-size:.72rem; font-weight:600; white-space:nowrap; }

/* KPI cards */
.la-kpi { border-radius:16px; padding:1rem 1.1rem; display:flex; gap:.9rem; align-items:flex-start; border:1px solid; min-height:112px; }
.la-kpi .lbl { font-size:.82rem; color:#C9CEEA; font-weight:500; }
.la-kpi .val { font-size:1.75rem; font-weight:800; color:#fff; line-height:1.15; margin-top:.2rem; }
.la-kpi .cap { font-size:.76rem; color:var(--la-muted); margin-top:.15rem; }

/* list rows */
.la-row { display:flex; align-items:center; gap:.8rem; padding:.62rem 0; border-bottom:1px solid rgba(110,125,220,.09); }
.la-row:last-child { border-bottom:none; }
.la-row .main { flex:1; min-width:0; }
.la-row .t { color:#EEF0FF; font-weight:600; font-size:.88rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.la-row .s { color:var(--la-muted); font-size:.76rem; margin-top:.1rem; display:flex; align-items:center; gap:.3rem; }
.la-empty { color:var(--la-muted); font-size:.85rem; padding:1rem 0; text-align:center; }

/* donut legend */
.la-legend { display:flex; flex-direction:column; gap:1rem; justify-content:center; height:100%; padding-top:2.2rem; }
.la-legend div { display:flex; align-items:center; gap:.6rem; font-size:.88rem; color:#D7DBF5; }
.la-legend b { margin-left:auto; color:#fff; font-weight:700; }
.la-legend em { color:var(--la-muted); font-style:normal; width:3.4rem; text-align:right; font-size:.8rem; }
.la-dot { width:10px; height:10px; border-radius:50%; display:inline-block; flex-shrink:0; }

/* promo */
.la-promo { position:relative; overflow:hidden; border-radius:16px; min-height:150px; padding:1.2rem 1.3rem;
    background:linear-gradient(135deg,#1B1F5E 0%,#14184A 55%,#0E1238 100%); border:1px solid rgba(124,127,250,.25); }
.la-promo .q { position:relative; z-index:1; font-size:1.12rem; font-weight:700; color:#fff; line-height:1.45; max-width:62%; }
.la-promo .q span { color:#8F94FF; }
.la-promo .by { position:relative; z-index:1; font-size:.78rem; color:#A5B4FC; margin-top:.6rem; }
.la-mtn { position:absolute; right:0; bottom:0; width:100%; height:100%; }

/* ---------- upload ---------- */
.st-key-card_drop [data-testid="stFileUploader"] > label { display:none; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"], .st-key-card_drop section[data-testid="stFileUploadDropzone"] {
    min-height:300px; display:flex !important; flex-direction:column; align-items:center; justify-content:center; gap:.4rem;
    background:rgba(10,15,40,.55) !important; border:1.6px dashed rgba(124,127,250,.5) !important; border-radius:14px !important; padding:1.6rem !important; text-align:center; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"]:hover { border-color:#8F94FF !important; background:rgba(40,44,120,.18) !important; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"]::before {
    content:"Drag & drop your files here"; display:block; order:0; color:#fff; font-weight:700; font-size:1.08rem; padding-top:64px;
    background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 24 24' fill='none' stroke='%238F94FF' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'><path d='M4 14.9A7 7 0 1 1 15.7 8h1.8a4.5 4.5 0 0 1 2.5 8.2'/><path d='M12 12v9'/><path d='m16 16-4-4-4 4'/></svg>") no-repeat top center; }
.st-key-card_drop [data-testid="stFileUploaderDropzoneInstructions"] { order:1; display:flex !important; flex-direction:column; align-items:center; margin:0 !important; }
.st-key-card_drop [data-testid="stFileUploaderDropzoneInstructions"] > div,
.st-key-card_drop [data-testid="stFileUploaderDropzoneInstructions"] > span { display:none !important; }
.st-key-card_drop [data-testid="stFileUploaderDropzoneInstructions"]::before { content:"or click to browse"; color:#AEB5D6; font-size:.86rem; }
.st-key-card_drop [data-testid="stFileUploaderDropzoneInstructions"]::after { content:var(--la-supports, "Supports PDF, JPG, PNG, DOCX, XLSX, TXT (Max 10MB)"); color:#8B93B8; font-size:.78rem; margin-top:.75rem; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"] > span, .st-key-card_drop section[data-testid="stFileUploaderDropzone"] > button { order:2; margin-top:.7rem; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"] button { background:linear-gradient(135deg,#5B5EF4,#4B4FE0) !important; border:none !important;
    color:#fff !important; border-radius:10px !important; padding:.5rem 1.5rem !important; box-shadow:0 6px 18px rgba(75,79,224,.4); }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"] button p { font-size:0 !important; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"] button p::after,
.st-key-card_drop section[data-testid="stFileUploaderDropzone"] button:not(:has(p)):not(:has(svg))::after { content:"Choose Files"; font-size:.88rem; font-weight:600; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"] button:not(:has(p)):not(:has(svg)) { font-size:0 !important; }
.st-key-card_drop section[data-testid="stFileUploaderDropzone"] button [data-testid="stIconMaterial"] { font-size:1.05rem; }
.st-key-card_drop [data-testid="stFileUploaderFile"] { background:rgba(17,24,56,.8); border-radius:10px; padding:.35rem .6rem; }

div[class*="st-key-qt"] { background:rgba(10,15,40,.55); border:1px solid var(--la-line); border-radius:12px; padding:.9rem .4rem .4rem .4rem !important; text-align:center; }
div[class*="st-key-qt"] .la-qt { display:flex; justify-content:center; padding-bottom:.15rem; }
div[class*="st-key-qt"] [data-testid="stElementContainer"], div[class*="st-key-qt"] [data-testid="stButton"] { width:100% !important; display:flex; justify-content:center; }
div[class*="st-key-qt"] button { justify-content:center; color:#D7DBF5 !important; font-size:.8rem !important; }
div[class*="st-key-qt"]:hover { border-color:rgba(124,127,250,.55); }
div[class*="st-key-qtsel_"] { border-color:#7C7FFA !important; background:rgba(91,94,244,.14) !important; }

.la-extract { display:flex; gap:.9rem; align-items:flex-start; padding:.75rem; border-radius:12px; background:rgba(10,15,40,.55); border:1px solid var(--la-line); }
.la-thumb { width:82px; height:104px; border-radius:8px; object-fit:cover; object-position:top; background:#fff; flex-shrink:0; border:1px solid rgba(255,255,255,.1); }
.la-thumb-ph { width:82px; height:104px; border-radius:8px; background:rgba(91,94,244,.12); display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.la-fields { width:100%; margin-top:.75rem; border-radius:12px; background:rgba(10,15,40,.55); border:1px solid var(--la-line); padding:.55rem .85rem; }
.la-fields div { display:flex; font-size:.82rem; padding:.32rem 0; }
.la-fields span { color:var(--la-muted); width:42%; flex-shrink:0; }
.la-fields b { color:#EEF0FF; font-weight:500; word-break:break-word; }

.st-key-viewdetails [data-testid="stLayoutWrapper"], .st-key-viewdetails [data-testid="stPopover"],
.st-key-viewdetails [data-testid="stPopover"] > div, .st-key-viewdetails [data-testid="stPopoverButton"] { width:100% !important; }
.st-key-viewdetails [data-testid="stPopoverButton"] { background:rgba(91,94,244,.10) !important; border:1px solid rgba(124,127,250,.4) !important; color:#C7CAFF !important; justify-content:center; }

/* ---------- reminders ---------- */
div[class*="st-key-rem_"] { background:linear-gradient(180deg, rgba(17,24,56,.92), rgba(13,19,48,.92)); border:1px solid var(--la-line);
    border-radius:14px; padding:.8rem 1rem !important; }
div[class*="st-key-rem_"]:hover { border-color:rgba(124,127,250,.45); }
.la-rem { display:flex; align-items:center; gap:.95rem; }
.la-rem .t { color:#fff; font-weight:700; font-size:.94rem; }
.la-rem .d { color:var(--la-muted); font-size:.8rem; margin-top:.12rem; }
.la-rem .w { color:#AEB5D6; font-size:.78rem; margin-top:.4rem; display:flex; align-items:center; gap:.35rem; }
.la-rem .w b { font-weight:500; }
div[class*="st-key-rem_"] [data-testid="stPopoverButton"] { background:transparent !important; border:none !important; box-shadow:none !important; color:#8B93B8 !important; }
div[class*="st-key-rem_"] [data-testid="stPopoverButton"] div[aria-hidden="true"] { display:none !important; }

.st-key-remtabs [data-testid="stButtonGroup"] button, .st-key-doctabs [data-testid="stButtonGroup"] button { background:#0F1535 !important; border:1px solid var(--la-line) !important; color:#AEB5D6 !important;
    border-radius:10px !important; padding:.35rem 1.1rem !important; margin-right:.45rem; }
.st-key-remtabs [data-testid="stButtonGroup"] button[aria-checked="true"], .st-key-doctabs [data-testid="stButtonGroup"] button[aria-checked="true"] { background:linear-gradient(135deg,#5B5EF4,#4B4FE0) !important; color:#fff !important; border-color:transparent !important; }

.la-cal { width:100%; border-collapse:separate; border-spacing:0 .25rem; text-align:center; border:none !important; margin:0 !important; display:table !important; }
.la-cal tr, .la-cal th, .la-cal td { border:none !important; background:transparent !important; }
.la-cal th { color:var(--la-muted); font-weight:500; font-size:.74rem; padding:.35rem 0; }
.la-cal td { font-size:.82rem; color:#D7DBF5; height:40px; vertical-align:top; padding-top:.3rem; position:relative; }
.la-cal td.o { color:#3F4670; }
.la-cal td .n { display:inline-flex; width:28px; height:28px; align-items:center; justify-content:center; border-radius:50%; }
.la-cal td.today .n { background:linear-gradient(135deg,#6D6FF7,#4B4FE0); color:#fff; font-weight:700; box-shadow:0 4px 14px rgba(91,94,244,.5); }
.la-cal td .dots { display:flex; gap:3px; justify-content:center; margin-top:1px; }
.la-cal td .dots i { width:5px; height:5px; border-radius:50%; display:block; }
.la-cal-head { text-align:center; font-weight:700; color:#fff; font-size:1rem; padding-top:.35rem; }
div[class*="st-key-calnav"] .stButton > button[kind="secondary"] { background:transparent !important; border:none !important; box-shadow:none !important; color:#C9CEEA !important; }
div[class*="st-key-calnav"] .stButton > button[kind="secondary"]:hover { color:#fff !important; background:rgba(91,94,244,.15) !important; }
div[class*="st-key-calnav_next"] [data-testid="stButton"] { display:flex; justify-content:flex-end; }

.la-sum { display:grid; grid-template-columns:1fr 1fr; gap:.6rem; }
.la-sum > div { display:flex; gap:.7rem; align-items:center; padding:.75rem; border-radius:12px; background:rgba(10,15,40,.55); border:1px solid var(--la-line); }
.la-sum b { display:block; color:#fff; font-size:1.2rem; font-weight:800; line-height:1.1; }
.la-sum span { color:var(--la-muted); font-size:.76rem; }

/* ---------- native widgets ---------- */
[data-testid="stForm"] { border:1px solid var(--la-line) !important; border-radius:14px !important; background:rgba(10,15,40,.45); }
div[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="base-input"] { background-color:#0F1535 !important; border-color:var(--la-line) !important; border-radius:10px !important; }
.stButton > button, .stDownloadButton > button, [data-testid="stPopoverButton"] { border-radius:10px !important; font-weight:600 !important; }
.stButton > button[kind="secondary"], .stDownloadButton > button { background:#141B42 !important; border:1px solid var(--la-line) !important; color:#E8ECFF !important; }
.stButton > button[kind="secondary"]:hover, .stDownloadButton > button:hover { border-color:#7C7FFA !important; color:#fff !important; }
button[kind="primary"], button[kind="primaryFormSubmit"] { background:linear-gradient(135deg,#5B5EF4,#4B4FE0) !important; border:none !important; color:#fff !important;
    box-shadow:0 6px 18px rgba(75,79,224,.35) !important; }
[data-testid="stDataFrame"] { border:1px solid var(--la-line); border-radius:12px; overflow:hidden; }
[data-testid="stExpander"] details { border:1px solid var(--la-line) !important; border-radius:12px !important; background:rgba(10,15,40,.45); }
[data-testid="stAlert"] { border-radius:12px !important; }
pre, code { font-family:'JetBrains Mono', ui-monospace, Consolas, monospace !important; }
.la-health { font-size:.84rem; }
.la-health .bar { height:8px; border-radius:6px; background:rgba(255,255,255,.08); overflow:hidden; margin:.45rem 0 .7rem 0; }
.la-health .bar i { display:block; height:100%; border-radius:6px; }
.la-health div.ck { display:flex; justify-content:space-between; padding:.2rem 0; color:#C9CEEA; }
</style>
"""


def inject_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def html(markup: str) -> None:
    """Render HTML. Lines are joined so Markdown never treats them as code."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


# ---------------------------------------------------------------- components
def brand() -> str:
    return f'<div class="la-brand">{LOGO_SVG}<span>LifeAdmin</span></div>'


def motto() -> str:
    return '<div class="la-motto">Less chaos.<br/>More life.<i></i></div>'


def page_header(title: str, subtitle: str, icon_name: str) -> str:
    return (f'<div class="la-head">{icon_tile(icon_name, "#7C7FFA", 48, 13, 24)}'
            f'<div><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div></div>')


def card_title(title: str, icon_name: str) -> str:
    return f'<div class="la-card-title">{icon(icon_name, 18)}<span>{esc(title)}</span></div>'


KPI_STYLE = {
    "total": ("files", "#6366F1", "linear-gradient(135deg, rgba(79,70,229,.30), rgba(24,30,80,.55))", "rgba(99,102,241,.35)"),
    "active": ("check", "#22C55E", "linear-gradient(135deg, rgba(22,101,52,.40), rgba(14,32,40,.55))", "rgba(34,197,94,.30)"),
    "expiring": ("clock", "#F5A524", "linear-gradient(135deg, rgba(146,94,10,.40), rgba(36,30,26,.55))", "rgba(245,165,36,.30)"),
    "critical": ("alert", "#EF4444", "linear-gradient(135deg, rgba(153,27,27,.42), rgba(40,20,34,.55))", "rgba(239,68,68,.32)"),
}


def kpi(kind: str, label: str, value: object, caption: str) -> str:
    ic, col, bg, border = KPI_STYLE[kind]
    return (f'<div class="la-kpi" style="background:{bg};border-color:{border}">'
            f'{icon_tile(ic, col, 44, 12, 22, solid=kind != "total")}'
            f'<div><div class="lbl">{esc(label)}</div><div class="val">{esc(value)}</div>'
            f'<div class="cap">{esc(caption)}</div></div></div>')


def row(leading: str, title: str, sub: str, trailing: str = "", sub_icon: str = "") -> str:
    si = icon(sub_icon, 12) if sub_icon else ""
    return (f'<div class="la-row">{leading}<div class="main"><div class="t" title="{esc(title)}">{esc(title)}</div>'
            f'<div class="s">{si}{sub}</div></div>{trailing}</div>')


def rows(items: List[str], empty: str) -> str:
    return "".join(items) if items else f'<div class="la-empty">{esc(empty)}</div>'


def legend(entries: Iterable[Tuple[str, str, int, int]]) -> str:
    out = []
    for label, color, count, pct in entries:
        out.append(f'<div><span class="la-dot" style="background:{color}"></span>{esc(label)}'
                   f'<b>{count}</b><em>({pct}%)</em></div>')
    return f'<div class="la-legend">{"".join(out)}</div>'


def promo(line1: str, line2: str, highlight: str = "", byline: str = "") -> str:
    hl = f"<br/><span>{esc(highlight)}</span>" if highlight else ""
    by = f'<div class="by">— {esc(byline)}</div>' if byline else ""
    return (f'<div class="la-promo">{MOUNTAIN_SVG}<div class="q">{esc(line1)}<br/>{esc(line2)}{hl}</div>{by}</div>')


def thumb_img(png: Optional[bytes]) -> str:
    if not png:
        return f'<div class="la-thumb-ph">{icon("file", 30, "#8F94FF")}</div>'
    return f'<img class="la-thumb" src="data:image/png;base64,{base64.b64encode(png).decode()}"/>'


def fields_table(pairs: List[Tuple[str, str]]) -> str:
    body = "".join(f'<div><span>{esc(k)}</span><b>: {esc(v)}</b></div>' for k, v in pairs)
    return f'<div class="la-fields">{body}</div>'


def health_meter(score: int, checks: List[Tuple[str, bool]], verdict: str) -> str:
    color = "#22C55E" if score >= 80 else "#F5A524" if score >= 50 else "#EF4444"
    ck = "".join(f'<div class="ck"><span>{esc(lbl)}</span><span style="color:{"#4ADE80" if ok else "#F87171"}">'
                 f'{"✓" if ok else "✗"}</span></div>' for lbl, ok in checks)
    return (f'<div class="la-health"><div style="display:flex;justify-content:space-between"><span class="la-sub">Completeness</span>'
            f'<b style="color:{color}">{score}%</b></div><div class="bar"><i style="width:{score}%;background:{color}"></i></div>'
            f'{ck}<div class="la-sub" style="margin-top:.5rem">{esc(verdict)}</div></div>')


def month_calendar(year: int, month: int, marks: Dict[date, List[Tuple[str, str]]],
                   today: date) -> str:
    """HTML month grid. marks: day -> [(colour, tooltip), ...]."""
    cal = calendar.Calendar(firstweekday=6)  # Sunday first, like the design
    head = "".join(f"<th>{d}</th>" for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    body = []
    for week in cal.monthdatescalendar(year, month):
        cells = []
        for d in week:
            cls = []
            if d.month != month:
                cls.append("o")
            if d == today:
                cls.append("today")
            dots = marks.get(d, []) if d.month == month else []
            tip = esc("; ".join(t for _, t in dots))
            dot_html = "".join(f'<i style="background:{c}"></i>' for c, _ in dots[:3])
            cells.append(f'<td class="{" ".join(cls)}" title="{tip}"><span class="n">{d.day}</span>'
                         f'<div class="dots">{dot_html}</div></td>')
        body.append(f"<tr>{''.join(cells)}</tr>")
    return f'<table class="la-cal"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def summary_grid(items: List[Tuple[str, str, object, str]]) -> str:
    out = "".join(f'<div>{icon_tile(ic, col, 36, 10, 18, solid=True)}<div><b>{esc(v)}</b><span>{esc(lbl)}</span></div></div>'
                  for ic, col, v, lbl in items)
    return f'<div class="la-sum">{out}</div>'


def avatar_css(initials: str) -> None:
    st.markdown(f'<style>.st-key-avatar button::before {{ content:"{esc(initials)}"; }}</style>',
                unsafe_allow_html=True)
