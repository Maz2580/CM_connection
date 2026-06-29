"""
Content Manager Record Number Extractor

Scans free-text data (e.g. a CAMMS project export) and pulls out candidate
Content Manager record numbers, filtering out look-alikes such as fiscal years.

Two ways to use it:

1. Standalone / CLI (scan a CSV):
       venv32\\Scripts\\python.exe record_extractor.py info.csv candidates.csv

2. From FME (PythonCaller) - import and call extract_record_numbers(text)
   for each feature, or extract_from_row(dict) for a whole feature.

Record number examples that ARE matched:
    M24/93415, M20/14939, E24/4343, ICO23/918, 2024/35124, 03/652/02140
Look-alikes that are EXCLUDED (fiscal years / ranges):
    2026/27, 2025/2026, 23/24, 24/25, FY26/27, 2026/67
"""

import csv
import re
import sys
import json

# A CM record number is: optional alpha prefix, 2-4 digit segment, then a slash,
# then a 3-6 digit segment, optionally a third slash + segment (e.g. 03/652/02140).
RECORD_RE = re.compile(
    r"\b([A-Za-z]{1,4})?(\d{2,4})/(\d{2,6})(?:/(\d{2,6}))?\b"
)

# Tokens that should never be treated as record numbers.
_FY_PREFIX_RE = re.compile(r"FY\s*\d", re.IGNORECASE)


def _is_fiscal_year(prefix, p1, p2, p3):
    """True if the token looks like a fiscal/financial year, not a CM number."""
    if p3:  # three-part numbers are real record numbers, never fiscal years
        return False
    n1, n2 = int(p1), int(p2)
    # Pure 2-digit/2-digit range, e.g. 23/24, 24/25, 26/27
    if len(p1) == 2 and len(p2) == 2:
        return True
    # 4-digit/2-digit consecutive year, e.g. 2026/27, 2024/25
    if len(p1) == 4 and len(p2) == 2 and (n2 == (n1 + 1) % 100):
        return True
    # 4-digit/4-digit consecutive year, e.g. 2025/2026, 2010/2011
    if len(p1) == 4 and len(p2) == 4 and n2 == n1 + 1:
        return True
    return False


def extract_record_numbers(text, require_prefix=False):
    """
    Return a de-duplicated, order-preserving list of candidate record numbers
    found in `text`. Fiscal years and obvious look-alikes are filtered out.

    If require_prefix is True, only tokens with an alpha prefix (M, E, ICO...)
    are returned (stricter, fewer false positives).
    """
    if not text:
        return []
    text = str(text)
    found = []
    seen = set()
    for m in RECORD_RE.finditer(text):
        prefix, p1, p2, p3 = m.group(1), m.group(2), m.group(3), m.group(4)
        # Skip "FY26/27" style
        start = m.start()
        if start >= 2 and _FY_PREFIX_RE.search(text[max(0, start - 3):m.end()]):
            continue
        if _is_fiscal_year(prefix, p1, p2, p3):
            continue
        if require_prefix and not prefix:
            continue
        token = m.group(0).upper()
        if token not in seen:
            seen.add(token)
            found.append(token)
    return found


def extract_from_row(row, fields=None):
    """
    Scan a dict (one CSV row / FME feature) and return list of unique candidates.
    If fields is None, scan all values.
    """
    values = row.values() if fields is None else (row.get(f, "") for f in fields)
    found, seen = [], set()
    for v in values:
        for token in extract_record_numbers(v):
            if token not in seen:
                seen.add(token)
                found.append(token)
    return found


def scan_csv(in_path, out_path=None):
    """Scan a CSV, return rows of (source_id, record_number, source_field)."""
    results = []
    with open(in_path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row_id = row.get("id") or row.get("projectId") or ""
            for field, value in row.items():
                if not value:
                    continue
                for token in extract_record_numbers(value):
                    results.append((row_id, token, field))
    if out_path:
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["source_id", "record_number", "source_field"])
            w.writerows(results)
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: record_extractor.py <input.csv> [output.csv]")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    rows = scan_csv(src, dst)
    uniq = sorted({r[1] for r in rows})
    print(f"Scanned: {src}")
    print(f"Total candidates: {len(rows)}  Unique: {len(uniq)}")
    print(json.dumps(uniq, indent=2))
