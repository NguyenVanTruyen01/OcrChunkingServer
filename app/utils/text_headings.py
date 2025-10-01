import re
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Pre-compiled heading regex patterns
# ---------------------------------------------------------------------------

# Punctuation tokens commonly found after numbers/Roman numerals.
# Treat ".-" as a single token to support legacy forms like "Điều 1.- ..."
PUNCT_ONE = r"(?:\.-|[.\-:–—)])"

HEADING_PATTERNS = [
    # ===== Top-level =====
    # Phần I / Phần 1 / PHẦN A
    re.compile(r"^\s*(Phần)\s+(?:[IVXLCDM]+|\d+|[A-Z])\.?\s*(.*)$",
               re.IGNORECASE | re.UNICODE),

    # Chương I
    re.compile(r"^\s*(Chương)\s+[IVXLCDM]+\.?\s*(.*)$",
               re.IGNORECASE | re.UNICODE),

    # Mục I / Mục 1 (allow Roman & Arabic)
    re.compile(r"^\s*(Mục)\s+(?:[IVXLCDM]+|\d+)\.?\s*(.*)$",
               re.IGNORECASE | re.UNICODE),

    # Tiểu mục 1 / Tiểu mục II
    re.compile(r"^\s*(Tiểu\s*mục)\s+(?:[IVXLCDM]+|\d+)\.?\s*(.*)$",
               re.IGNORECASE | re.UNICODE),

    # ===== Điều, Khoản, Điểm, Tiết =====
    # Điều 1. / Điều 1: / Điều 1.- / Điều 1) ...
    re.compile(r"^\s*(Điều)\s+\d+\s*(?:%s\s*)?(.*)$" % PUNCT_ONE,
               re.IGNORECASE | re.UNICODE),

    # Khoản 1. / Khoản 1)
    re.compile(r"^\s*(Khoản)\s+\d+\s*(?:%s\s*)?(.*)$" % PUNCT_ONE,
               re.IGNORECASE | re.UNICODE),

    # Điểm a) / Điểm b.
    re.compile(r"^\s*(Điểm)\s+[A-Za-z]\s*[.)]?\s*(.*)$",
               re.IGNORECASE | re.UNICODE),

    # Tiết a) / Tiết 1.
    re.compile(r"^\s*(Tiết)\s+[A-Za-z0-9]\s*[.)]?\s*(.*)$",
               re.IGNORECASE | re.UNICODE),

    # ===== Phụ lục / Mẫu / Biểu =====
    # Phụ lục I / Phụ lục số 01 / PHỤ LỤC A
    re.compile(r"^\s*(Phụ\s*lục)\s+(?:số\s*)?(?:[IVXLCDM]+|\d+|[A-Z])\.?\s*(.*)$",
               re.IGNORECASE | re.UNICODE),

    # Mẫu số 01 / Biểu số 2
    re.compile(r"^\s*(Mẫu|Biểu)\s*(?:số)?\s*\d+\s*(?:%s\s*)?(.*)$" % PUNCT_ONE,
               re.IGNORECASE | re.UNICODE),

    # ===== Roman-only (fallback) =====
    # Require EITHER: ≥2 Roman chars with no punctuation, OR punctuation present.
    # This avoids matching plain "I ..." sentences.
    re.compile(r"^\s*(?:[IVXLCDM]{2,}|[IVXLCDM]+[.)])\s+(.{3,})$",
               re.UNICODE),
]

# ----------------- Guards to avoid bullets/lists -----------------

# A) / b. ...
SKIP_BARE_ALPHA = re.compile(r"^[A-Za-z][.)]\s")
# a) / b. ... (lowercase only)
SKIP_LOWER_ALPHA = re.compile(r"^[a-z][.)]\s")
# 1) / 1. / 1-
SKIP_DANGEROUS_NUM = re.compile(r"^\d+[.)-]\s")

# Keywords for legal headings (used to exempt from some guards if needed)
KEYWORD_PREFIX = re.compile(
    r"^(Phần|Chương|Mục|Tiểu\s*mục|Điều|Khoản|Điểm|Tiết|Phụ\s*lục|Mẫu|Biểu)\b",
    re.IGNORECASE | re.UNICODE
)

def find_headings(text: str) -> List[Tuple[int, int, str]]:
    """
    Detect heading lines and keep the full heading text.

    Returns:
        List of tuples (start_index, end_index, heading_text)
    """
    results: List[Tuple[int, int, str]] = []
    pos = 0  # running absolute character offset

    for line in text.splitlines(True):  # preserve newlines to track positions
        stripped = line.strip()

        # --- Guards: skip obvious bullets/lists ---
        # Skip "a) ...", "b.", "C)" etc. (lines that start with single letter + punct)
        if SKIP_BARE_ALPHA.match(stripped) or SKIP_LOWER_ALPHA.match(stripped):
            pos += len(line)
            continue

        # Skip "1) ...", "1.", "1-" unless the line starts with legal keywords
        if SKIP_DANGEROUS_NUM.match(stripped) and not KEYWORD_PREFIX.match(stripped):
            pos += len(line)
            continue

        # --- Match headings ---
        for pat in HEADING_PATTERNS:
            if pat.match(stripped):
                # keep the full line sans leading/trailing spaces
                results.append((pos, pos + len(line), stripped))
                break

        pos += len(line)

    return results