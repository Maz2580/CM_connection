# ============================================================
# FME PythonCaller #1 - Extract CM record numbers
# ------------------------------------------------------------
# Place a PythonCaller AFTER your CSV/CAMMS reader.
# Mode: outputs MANY features per input feature (one per record number).
# Pure Python - runs in FME's own Python, no 32-bit needed.
# Paste this whole file into the PythonCaller "Class or function" body.
# ============================================================
import fmeobjects
import sys

# Folder containing record_extractor.py
TOOL_DIR = r"C:\Users\maz.ghasemi\Downloads\Maz - 2 July 2025\python\connection\content_manager\custom_search"
if TOOL_DIR not in sys.path:
    sys.path.insert(0, TOOL_DIR)

from record_extractor import extract_from_row


class RecordNumberExtractor(object):
    def input(self, feature):
        # Build a dict of all attributes on the feature
        row = {name: feature.getAttribute(name) for name in feature.getAllAttributeNames()}
        candidates = extract_from_row(row)        # scans all fields, filters fiscal years
        source_id = row.get("id") or row.get("projectId") or ""
        if not candidates:
            feature.setAttribute("record_number", "")
            feature.setAttribute("match_status", "no_candidates")
            self.pyoutput(feature)
            return
        for num in candidates:
            f = feature.clone()
            f.setAttribute("record_number", num)
            f.setAttribute("source_id", str(source_id))
            self.pyoutput(f)

    def close(self):
        pass
