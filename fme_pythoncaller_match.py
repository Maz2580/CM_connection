# ============================================================
# FME PythonCaller #2 - Verify + download from Content Manager
# ------------------------------------------------------------
# Place a PythonCaller AFTER the extractor + a Sampler/Deduplicator on
# record_number (so each number is queried once). This collects all incoming
# record numbers, shells out ONCE to the 32-bit venv (cm_match.py), reads the
# manifest, and adds filepath/match info back onto features.
#
# Why subprocess: the CM COM SDK is 32-bit only; FME's Python is 64-bit.
# ============================================================
import fmeobjects
import os
import sys
import csv
import json
import tempfile
import subprocess

TOOL_DIR = r"C:\Users\maz.ghasemi\Downloads\Maz - 2 July 2025\python\connection\content_manager\custom_search"
PY32 = os.path.join(TOOL_DIR, "venv32", "Scripts", "python.exe")
MATCH = os.path.join(TOOL_DIR, "cm_match.py")
OUTPUT_DIR = r"C:\GIS\Data\CM_Downloads"   # <-- set your download folder


class FeatureProcessor(object):
    def __init__(self):
        self.features = []
        self.logger = fmeobjects.FMELogFile()

    def input(self, feature):
        self.features.append(feature)

    def close(self):
        nums = [f.getAttribute("record_number") for f in self.features
                if f.getAttribute("record_number")]
        if not nums:
            for f in self.features:
                self.pyoutput(f)
            return
        # Write candidates.csv for cm_match.py
        cand = os.path.join(tempfile.gettempdir(), "fme_candidates.csv")
        with open(cand, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["record_number", "source_id"])
            for n in sorted(set(nums)):
                w.writerow([n, ""])
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        subprocess.run([PY32, MATCH, cand, OUTPUT_DIR], cwd=TOOL_DIR, timeout=1800)
        # Read manifest -> map record_number to result
        manifest = json.load(open(os.path.join(OUTPUT_DIR, "manifest.json")))
        info = {e["record_number"]: e for e in manifest["files"]}
        for f in self.features:
            e = info.get(f.getAttribute("record_number"), {})
            f.setAttribute("matched", 1 if e.get("matched") else 0)
            f.setAttribute("filepath", e.get("filepath") or "")
            f.setAttribute("title", e.get("title") or "")
            f.setAttribute("download_ok", 1 if e.get("success") else 0)
            self.pyoutput(f)
