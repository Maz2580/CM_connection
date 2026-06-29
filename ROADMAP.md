# Content Manager Custom Search Tool - Implementation Roadmap

## Project Overview

A search and download tool for Micro Focus Content Manager with two interfaces:
- **GUI Version** - Modern graphical interface with checkboxes (CustomTkinter)
- **CLI Version** - Command-line interface with text menus

**Capabilities:**
- Search for records by record number
- View contents of container records (folders)
- Select single or multiple records for download
- Download documents to a user-specified directory
- Progress tracking for downloads

---

## Implementation Phases

### Phase 1: Foundation ✅ COMPLETED
**Status:** Done

| Task | Status |
|------|--------|
| Set up project folder structure | ✅ |
| Create 32-bit Python virtual environment | ✅ |
| Install required packages (pywin32) | ✅ |
| Establish Content Manager COM connection | ✅ |
| Test basic record retrieval | ✅ |

---

### Phase 2: Core Search Module ✅ COMPLETED
**Status:** Done

| Task | Status |
|------|--------|
| Create `cm_connection.py` - Connection handler class | ✅ |
| Create `cm_search.py` - Search functionality class | ✅ |
| Create `cm_download.py` - Download functionality class | ✅ |
| Implement record type detection (folder vs single record) | ✅ |
| Implement container contents listing | ✅ |

**Files created:**
- `cm_connection.py` - CMConnection class with connect/disconnect
- `cm_search.py` - CMSearch class with get_record() and get_container_contents()
- `cm_download.py` - CMDownload class with download_record() and download_multiple()

---

### Phase 3: Interactive CLI Interface ✅ COMPLETED
**Status:** Done

| Task | Status |
|------|--------|
| Create main menu interface | ✅ |
| Implement record number input prompt | ✅ |
| Display search results in formatted table | ✅ |
| Implement selection system (single/multiple) | ✅ |
| Add download directory configuration | ✅ |
| Add progress indicators for downloads | ✅ |

**Files created:**
- `main.py` - Interactive CLI with menus
- `ui_helpers.py` - Display formatting and selection parsing

---

### Phase 4: Download Functionality ✅ COMPLETED
**Status:** Done

| Task | Status |
|------|--------|
| Implement single file download | ✅ |
| Implement batch download (multiple files) | ✅ |
| Add download progress tracking | ✅ |
| Handle filename conflicts | ✅ |
| Create download summary report | ✅ |
| Preserve original filenames | ✅ |

---

### Phase 5: GUI Interface ✅ COMPLETED
**Status:** Done

| Task | Status |
|------|--------|
| Install CustomTkinter library | ✅ |
| Create modern graphical window | ✅ |
| Implement checkbox selection for records | ✅ |
| Add browse button for directory selection | ✅ |
| Add progress bar for downloads | ✅ |
| Implement threaded downloads (non-blocking UI) | ✅ |
| Add Select All / Deselect All buttons | ✅ |

**Files created:**
- `gui_app.py` - Full GUI application with CustomTkinter

---

### Phase 6: Documentation ✅ COMPLETED
**Status:** Done

| Task | Status |
|------|--------|
| Create README.md with usage instructions | ✅ |
| Create PROJECT_OVERVIEW.md for stakeholders | ✅ |
| Update ROADMAP.md with progress | ✅ |

---

### Phase 7: FME Integration ✅ COMPLETED
**Status:** Done

| Task | Status |
|------|--------|
| Create config file for easy project switching | ✅ |
| Create batch download script (no user interaction) | ✅ |
| Output download results in manifest.json | ✅ |
| Document FME integration steps | ✅ |
| Test integration with FME workflow | ⏳ Ready for testing |

**Files created:**
- `download_config.json` - Configuration file (edit before running)
- `batch_download.py` - Silent batch download script for FME
- `FME_INTEGRATION.md` - Step-by-step FME integration guide

**How it works:**
1. Edit `download_config.json` with record number and output directory
2. FME calls `batch_download.py` via SystemCaller or PythonCaller
3. Files are downloaded to the specified directory
4. `manifest.json` is created with download results
5. FME continues to read the downloaded files and update GIS layer

---

### Phase 8: Future Enhancements ⏳ OPTIONAL
**Status:** Not Started

| Task | Status |
|------|--------|
| Add search by title keyword | ⏳ Optional |
| Add search history | ⏳ Optional |
| Add favorites/bookmarks | ⏳ Optional |
| Export results to CSV/Excel | ⏳ Optional |
| Add configuration file for defaults | ⏳ Optional |
| Add logging for troubleshooting | ⏳ Optional |
| Skip already downloaded files option | ⏳ Optional |

---

## Current File Structure

```
custom_search/
├── gui_app.py           # GUI version (recommended)
├── main.py              # CLI version (alternative)
├── batch_download.py    # FME batch download script
├── download_config.json # Config file for batch downloads
├── cm_connection.py     # Connection handler
├── cm_search.py         # Search functionality
├── cm_download.py       # Download functionality
├── ui_helpers.py        # CLI display helpers
├── test_modules.py      # Module tests
├── test_gui.py          # GUI dependency test
├── venv32/              # 32-bit Python environment
├── README.md            # User documentation
├── PROJECT_OVERVIEW.md  # Stakeholder documentation
├── FME_INTEGRATION.md   # FME integration guide
└── ROADMAP.md           # This file
```

---

## Completed Features Summary

| Feature | CLI | GUI | Batch (FME) |
|---------|-----|-----|-------------|
| Search by record number | ✅ | ✅ | ✅ |
| View container contents | ✅ | ✅ | ✅ |
| Single item download | ✅ | ✅ | ✅ |
| Multiple item download | ✅ | ✅ | ✅ |
| Custom download directory | ✅ | ✅ | ✅ |
| Progress indication | ✅ | ✅ | ✅ |
| Select all / Deselect all | ✅ | ✅ | - |
| Checkbox selection | - | ✅ | - |
| Browse for directory | - | ✅ | - |
| Threaded downloads | - | ✅ | - |
| Config file support | - | - | ✅ |
| Manifest output (JSON) | - | - | ✅ |
| Silent/automated mode | - | - | ✅ |

---

## Commands Reference

**Run GUI version (recommended):**
```cmd
cd "C:\Users\maz.ghasemi\Downloads\Maz - 2 July 2025\python\connection\content_manager\custom_search"
venv32\Scripts\python.exe gui_app.py
```

**Run CLI version:**
```cmd
cd "C:\Users\maz.ghasemi\Downloads\Maz - 2 July 2025\python\connection\content_manager\custom_search"
venv32\Scripts\python.exe main.py
```

**Run tests:**
```cmd
venv32\Scripts\python.exe test_modules.py
venv32\Scripts\python.exe test_gui.py
```

**Run batch download (for FME):**
```cmd
venv32\Scripts\python.exe batch_download.py
```
(Reads settings from `download_config.json`)

---

## Technical Notes

- Uses `Trimsdk.Database` COM object (official Micro Focus SDK)
- Requires 32-bit Python (COM SDK limitation)
- Windows authentication is used automatically
- Database ID: `SH` (CONTEXT)
- Read-only operations only (search and download)
- COM SDK has occasional segfaults at cleanup (doesn't affect functionality)

---

## What's Next?

All core functionality is complete! The tool is ready for:

1. **Testing with FME** - Try the batch download in your FME workflow
2. **Optional Enhancements** - Phase 8 features if needed

**To test FME integration:**
1. Edit `download_config.json` with your record and output path
2. Run `batch_download.py` manually to verify it works
3. Add to your FME workflow using SystemCaller or PythonCaller
4. See `FME_INTEGRATION.md` for detailed instructions

---

*Last updated: January 2026*
