"""
Content Manager Multi-Record Matcher

Given a list of candidate record numbers (from record_extractor.py), this
verifies which ones actually exist in Content Manager and downloads the ones
that do. Designed to be called from FME (32-bit venv) via subprocess.

CLI:
    venv32\\Scripts\\python.exe cm_match.py <candidates.csv> <output_dir>
    venv32\\Scripts\\python.exe cm_match.py "M24/93415,2024/35124" <output_dir>

Input candidates.csv: must have a 'record_number' column (record_extractor.py
output). Other columns (source_id) are carried through to the manifest.

Output: manifest.json in <output_dir> listing matched + downloaded + missing.
Exit codes: 0 all matched & downloaded, 1 partial, 2 fatal error.
"""

import csv
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cm_connection import CMConnection
from cm_search import CMSearch
from cm_download import CMDownload


def log(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}")
    sys.stdout.flush()


def load_candidates(arg):
    """Accept a CSV path or comma-separated list. Return list of (record, source_id)."""
    if os.path.isfile(arg):
        out = []
        with open(arg, encoding="utf-8-sig", newline="") as fh:
            r = csv.DictReader(fh)
            for row in r:
                num = (row.get("record_number") or "").strip()
                if num:
                    out.append((num, row.get("source_id", "")))
        return out
    return [(n.strip(), "") for n in arg.split(",") if n.strip()]


def run(candidates_arg, output_dir, database_id="SH"):
    candidates = load_candidates(candidates_arg)
    # de-dup while keeping first source_id
    seen, ordered = set(), []
    for num, src in candidates:
        if num not in seen:
            seen.add(num)
            ordered.append((num, src))

    results = {"timestamp": datetime.now().isoformat(), "output_directory": output_dir,
               "total_candidates": len(ordered), "matched": 0, "missing": 0,
               "downloaded": 0, "failed": 0, "files": []}

    conn = CMConnection()
    conn.connect(database_id)
    log(f"Connected to {conn.database_name} as {conn.current_user}")
    search, downloader = CMSearch(conn), CMDownload(conn)
    os.makedirs(output_dir, exist_ok=True)

    for i, (num, src) in enumerate(ordered, 1):
        rec = search.get_record(num)
        entry = {"record_number": num, "source_id": src, "matched": bool(rec),
                 "has_document": False, "success": False, "filepath": None,
                 "title": None, "error": None}
        if not rec:
            results["missing"] += 1
            log(f"[{i}/{len(ordered)}] {num}: NOT FOUND")
        else:
            results["matched"] += 1
            entry["title"] = rec.title
            entry["has_document"] = rec.has_document
            if rec.has_document:
                dl = downloader.download_record(num, output_dir)
                entry["success"] = dl.success
                entry["filepath"] = dl.file_path if dl.success else None
                entry["error"] = None if dl.success else dl.error_message
                results["downloaded" if dl.success else "failed"] += 1
                log(f"[{i}/{len(ordered)}] {num}: {'OK ' + os.path.basename(dl.file_path) if dl.success else 'FAIL'}")
            else:
                log(f"[{i}/{len(ordered)}] {num}: matched, no document")
        results["files"].append(entry)

    try:
        conn.disconnect()
    except Exception:
        pass

    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: cm_match.py <candidates.csv|nums,csv> <output_dir>")
        return 2
    r = run(sys.argv[1], sys.argv[2])
    log(f"matched={r['matched']} missing={r['missing']} downloaded={r['downloaded']} failed={r['failed']}")
    return 0 if r["failed"] == 0 and r["missing"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
