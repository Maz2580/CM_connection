# ============================================================
# FME PythonCaller #3 - Organize Excel files into title folders
# ------------------------------------------------------------
# Place AFTER PythonCaller #2 (match). For each record that has an EXCEL
# document, create a folder named after the record TITLE and copy the Excel
# into it. Non-excel / unmatched records pass through with has_excel=0.
# Pure Python - runs in FME's own interpreter (no 32-bit needed).
#
# Adds attributes: has_excel, title_folder, excel_path
# Expose these in "Attributes to Expose".
# ============================================================
import fmeobjects
import os
import re
import shutil

# Where the title folders are created
EXCEL_DIR = r"E:\Administration\FME Jobs\Tests\FME flow\creating live query system\Camms projects\test\excels"
EXCEL_EXTS = (".xlsx", ".xls", ".xlsm", ".xlsb")


def _safe_folder(name):
    name = re.sub(r'[<>:"/\\|?*\r\n\t]', " ", str(name)).strip().strip(".")
    name = re.sub(r"\s+", " ", name)
    return name[:120] or "untitled"


class FeatureProcessor(object):
    def input(self, feature):
        fp = feature.getAttribute("filepath") or ""
        title = feature.getAttribute("title") or ""
        rec = feature.getAttribute("record_number") or ""
        is_excel = bool(fp) and fp.lower().endswith(EXCEL_EXTS) and os.path.isfile(fp)
        if not is_excel:
            feature.setAttribute("has_excel", 0)
            feature.setAttribute("title_folder", "")
            feature.setAttribute("excel_path", "")
            self.pyoutput(feature)
            return
        folder_name = _safe_folder(title) if title else _safe_folder(rec)
        dest_dir = os.path.join(EXCEL_DIR, folder_name)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, os.path.basename(fp))
        shutil.copy2(fp, dest)
        feature.setAttribute("has_excel", 1)
        feature.setAttribute("title_folder", dest_dir)
        feature.setAttribute("excel_path", dest)
        self.pyoutput(feature)

    def close(self):
        pass
