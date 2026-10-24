"""Small helpers for the Upload screen: thumbnails, file sizes, masking."""
from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Optional

from .extractor import IMAGE_EXTENSIONS


def thumbnail(data: bytes, filename: str, width: int = 220) -> Optional[bytes]:
    """PNG preview of the first page/image, or None if it can't be rendered."""
    ext = Path(filename).suffix.lower()
    try:
        from PIL import Image

        if ext in IMAGE_EXTENSIONS:
            img = Image.open(io.BytesIO(data))
        elif ext == ".pdf":
            import pypdfium2 as pdfium  # optional, renders PDF pages

            pdf = pdfium.PdfDocument(data)
            page = pdf[0]
            img = page.render(scale=width / page.get_width()).to_pil()
            pdf.close()
        else:
            return None
        img = img.convert("RGB")
        img.thumbnail((width, width * 2))
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except Exception:
        return None


def human_size(n: Optional[int]) -> str:
    if n is None:
        return ""
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / 1024 / 1024:.1f} MB"


def file_size(path: str) -> Optional[int]:
    try:
        return Path(path).stat().st_size if path else None
    except OSError:
        return None


_AADHAAR = re.compile(r"^\d{4}[\s\-]?\d{4}[\s\-]?(\d{4})$")


def mask_number(number: str) -> str:
    """Hide all but the last 4 digits of an Aadhaar number for display."""
    m = _AADHAAR.match((number or "").strip())
    return f"XXXX-XXXX-{m.group(1)}" if m else number


_ACRONYMS = {"puc", "rc", "pan", "gst", "id", "lic", "emi", "kyc", "itr", "tv", "ac"}


def friendly_title(filename: str) -> str:
    """'old_puc.pdf' -> 'Old PUC'."""
    stem = re.sub(r"^\d{9,}_", "", Path(filename).stem)  # drop upload timestamp prefix
    words = re.split(r"[\s_\-]+", stem)
    return " ".join(w.upper() if w.lower() in _ACRONYMS else w.capitalize() for w in words if w) or filename
