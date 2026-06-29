# ============================================================
# FME PythonCaller #4 - Match record TITLE to an SDE Capital Works layer
# ------------------------------------------------------------
# Place AFTER PythonCaller #3 (organize). Collects titles, shells out ONCE to a
# Python that has pyodbc (FME's own Python does NOT), which reads the Capital
# Works layer list from SDE (read-only) and fuzzy-matches each title.
#
# Adds attributes: sde_layer, match_score
# Expose these in "Attributes to Expose".
# ============================================================
import fmeobjects
import os
import csv
import json
import tempfile
import subprocess

TOOL_DIR = r"C:\Users\maz.ghasemi\Downloads\Maz - 2 July 2025\python\connection\content_manager\custom_search"
# Python that HAS pyodbc (64-bit). FME's bundled Python does not.
PY_SDE = r"C:\Users\maz.ghasemi\AppData\Local\Programs\Python\Python313\python.exe"
MATCH = os.path.join(TOOL_DIR, "sde_layer_match.py")


class FeatureProcessor(object):
    def __init__(self):
        self.features = []

    def input(self, feature):
        self.features.append(feature)

    def close(self):
        titles = [f.getAttribute("title") for f in self.features
                  if f.getAttribute("title")]
        if not titles:
            for f in self.features:
                self.pyoutput(f)
            return
        tmp = tempfile.gettempdir()
        tin = os.path.join(tmp, "fme_titles.csv")
        tout = os.path.join(tmp, "fme_title_matches.csv")
        with open(tin, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["title"])
            for t in sorted(set(titles)):
                w.writerow([t])
        subprocess.run([PY_SDE, MATCH, tin, tout], cwd=TOOL_DIR, timeout=600)
        # Read mapping title -> (layer, score)
        mapping = {}
        with open(tout, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                mapping[row["title"]] = (row.get("sde_layer", ""), row.get("match_score", ""))
        for f in self.features:
            layer, score = mapping.get(f.getAttribute("title") or "", ("", ""))
            f.setAttribute("sde_layer", layer)
            f.setAttribute("match_score", score)
            self.pyoutput(f)
