# CAMMS → Content Manager → SDE — FME Workflow Guide

This is the full pipeline, built entirely in FME. It reads the CAMMS export,
extracts Content Manager record numbers, verifies + downloads them, then joins
the Excel data to SDE GIS features by asset ID.

## Pipeline

```
CSV/CAMMS Reader
   │
   ▼
PythonCaller #1  (fme_pythoncaller_extract.py)   ← pure Python, FME's interpreter
   │   one feature per record_number (fiscal years removed)
   ▼
Deduplicator (key: record_number)
   │
   ▼
PythonCaller #2  (fme_pythoncaller_match.py)     ← shells out to 32-bit venv32
   │   adds: matched, filepath, title, download_ok
   ▼
Tester  matched = 1 AND filepath != ''
   │
   ▼
FeatureReader (XLSX)  dataset = @Value(filepath)  → reads each downloaded Excel
   │   exposes asset id column
   ▼
FeatureMerger / FeatureJoiner ── SDE Reader (GIS layers)
   │   join on asset id
   ▼
FeatureWriter (SDE / GIS layer)
```

## Why two PythonCallers
- **Extract** is pure Python → runs in FME's 64-bit interpreter.
- **Match/download** needs the Content Manager COM SDK, which is **32-bit only**,
  so it shells out to `venv32\Scripts\python.exe cm_match.py`.

## Step-by-step
1. **Reader**: read `info.csv` (or keep CAMMS cache). All columns become attributes.
2. **PythonCaller #1**: paste `fme_pythoncaller_extract.py`. Class: `RecordNumberExtractor`.
   Output attrs: `record_number`, `source_id`, `match_status`.
3. **Deduplicator**: group by `record_number` (query each number once).
4. **PythonCaller #2**: paste `fme_pythoncaller_match.py`. Class: `CMMatcher`.
   Set `OUTPUT_DIR` to your download folder. New attrs: `matched`, `filepath`,
   `title`, `download_ok`.
5. **Tester**: keep `matched=1` and `filepath` not empty.
6. **FeatureReader (XLSX)**: Source Dataset = `@Value(filepath)`. Reads each Excel.
7. **SDE Reader**: add your GIS layers.
8. **FeatureMerger**: Requestor = SDE, Supplier = Excel; join key = asset id.
9. **Writer**: update SDE/GIS layer.

## Test the scripts outside FME first
```cmd
cd "...\custom_search"
venv32\Scripts\python.exe record_extractor.py "<path>\info.csv" candidates.csv
venv32\Scripts\python.exe cm_match.py candidates.csv "C:\GIS\Data\CM_Downloads"
```
manifest.json shows matched / missing / downloaded.

## Files
| File | Role |
|------|------|
| record_extractor.py | Extract record numbers (pure Python, FME-safe) |
| cm_match.py | Verify + download list of numbers (32-bit venv) |
| fme_pythoncaller_extract.py | PythonCaller #1 body |
| fme_pythoncaller_match.py | PythonCaller #2 body |
