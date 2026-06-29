# Content Manager Custom Search Tool

A tool for searching and downloading records from Micro Focus Content Manager.

**Three interfaces available:**
- **GUI Version** (Recommended) - Modern graphical interface with checkboxes
- **CLI Version** - Command-line interface
- **Batch Mode** - Silent/automated downloads for FME integration

## Features

- Search records by record number (e.g., `E24/3074`)
- Search records by title keyword
- View contents of container records (folders)
- Download single or multiple documents
- Checkbox selection (GUI) or text selection (CLI)
- Configurable download directory
- Progress tracking for downloads

---

## Quick Start

### Step 1: Open Command Prompt

Navigate to this folder:

```cmd
cd "C:\Users\maz.ghasemi\Downloads\Maz - 2 July 2025\python\connection\content_manager\custom_search"
```

### Step 2: Choose Your Interface

#### Option A: GUI Version (Recommended)

```cmd
venv32\Scripts\python.exe gui_app.py
```

This opens a modern graphical window with:
- Search box for record numbers
- Browse button for download directory
- Checkbox list for selecting items
- Progress bar for downloads

#### Option B: CLI Version

```cmd
venv32\Scripts\python.exe main.py
```

This runs in the command prompt with text-based menus.

---

## GUI Interface

The graphical interface provides:

```
┌─────────────────────────────────────────────────────────────┐
│  Content Manager Search Tool                                │
│  ✓ Connected: CONTEXT | User: Maz Ghasemi                   │
├─────────────────────────────────────────────────────────────┤
│  Record Number: [____________] [🔍 Search]                  │
│  Download to: [______________________] [Browse]             │
├─────────────────────────────────────────────────────────────┤
│  📁 Asset Renewal Programs (39 items)                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ☐ │ 1  │ M25/133489  │ 2026-27 Footpath Renewal...    │ │
│  │ ☑ │ 2  │ M25/131298  │ 2026-27 Guard Railing...       │ │
│  │ ☑ │ 3  │ M25/129489  │ 2026-27 Guard Railing...       │ │
│  └────────────────────────────────────────────────────────┘ │
│  [Select All] [Deselect All]       [⬇ Download Selected]   │
├─────────────────────────────────────────────────────────────┤
│  Ready                              [████████░░░░] 50%      │
└─────────────────────────────────────────────────────────────┘
```

### GUI Usage:
1. Enter a record number and click **Search**
2. Check the boxes next to items you want to download
3. Set the download directory using **Browse**
4. Click **Download Selected**
5. Files are saved to your chosen directory

---

## CLI Interface (Alternative)

### Main Menu

When you start the CLI tool (`main.py`), you'll see:

```
============================================================
                Content Manager Search Tool
============================================================

MAIN MENU
============================================================

  [1] Search by Record Number
  [2] Search by Title Keyword
  [3] Change Download Directory
  [Q] Quit
```

### Searching by Record Number

1. Select option `1`
2. Enter the record number (e.g., `E24/3074`)
3. The tool will show:
   - **If it's a single record**: Display details and option to download
   - **If it's a container (folder)**: Display all contents with selection options

### Selecting Items for Download

When viewing container contents, you can select items using:

| Input | Description |
|-------|-------------|
| `A` or `all` | Download all items |
| `1` | Download item #1 |
| `1,3,5` | Download items 1, 3, and 5 |
| `1-5` | Download items 1 through 5 |
| `1,3-5,8` | Download items 1, 3, 4, 5, and 8 |
| `V` | View details of a specific item |
| `B` | Go back to main menu |

### Setting Download Directory

- Default directory: `~/Downloads/ContentManager`
- Change it from the main menu (option 3)
- Or enter a custom path when prompted during download

## File Structure

```
custom_search/
├── gui_app.py           # GUI version (recommended)
├── main.py              # CLI version (alternative)
├── batch_download.py    # Batch mode for FME integration
├── download_config.json # Configuration for batch downloads
├── cm_connection.py     # Connection handler
├── cm_search.py         # Search functionality
├── cm_download.py       # Download functionality
├── ui_helpers.py        # CLI display helpers
├── venv32/              # 32-bit Python environment
├── README.md            # This file
├── FME_INTEGRATION.md   # FME PythonCreator setup guide
├── PROJECT_OVERVIEW.md  # Stakeholder documentation
└── ROADMAP.md           # Development roadmap
```

---

## FME Integration (Batch Mode)

For automated downloads in FME workflows, use the **PythonCreator** transformer.

### Quick Start

1. Edit `download_config.json` with your record number and output directory
2. Add a PythonCreator to your FME workflow (see `FME_INTEGRATION.md` for full code)
3. The PythonCreator outputs one feature per downloaded file with `filepath` attribute
4. Use FeatureReader to read the Excel files

### Batch Download (Manual Test)

```cmd
venv32\Scripts\python.exe batch_download.py
```

This reads settings from `download_config.json` and creates `manifest.json` in the output directory.

See `FME_INTEGRATION.md` for complete documentation.

## Example Session

```
============================================================
                Content Manager Search Tool
============================================================

Connecting to Content Manager...
  Connected to: CONTEXT
  User: Maz Ghasemi

MAIN MENU
============================================================
  [1] Search by Record Number

Enter choice: 1

Search by Record Number
------------------------------------------------------------
Enter record number: E24/3074

Searching for: E24/3074...

Record Found: E24/3074
------------------------------------------------------------
  Title: Asset Renewal Programs
  Is Container: True

Contents of: E24/3074
------------------------------------------------------------
Loading contents...

   #  Record Number    Title                                          Type
--------------------------------------------------------------------------------
   1  M25/133489       2026-27 Footpath Renewal Program...            [DOC]
   2  M25/131298       2026-27 Guard Railing on Road Bridges...       [DOC]
   3  M25/129489       2026-27 Guard Railing on Road Bridges...       [DOC]
   ...

OPTIONS:
  [A]     - Download ALL items
  [1,2,5] - Download specific items (comma-separated)
  [1-5]   - Download range of items
  [V]     - View an item's details
  [B]     - Go back to main menu

Enter selection: 1-3
```

## Troubleshooting

### "Class not registered" error
Make sure you're using the 32-bit Python from `venv32`:
```cmd
venv32\Scripts\python.exe main.py
```

### Connection errors
- Ensure Content Manager client is installed
- Verify you have access to the database
- Check network connectivity

### Download fails
- Verify you have write permissions to the download directory
- Check if the record has an attached document (shown as `[DOC]`)

## Technical Notes

- Uses `Trimsdk.Database` COM object
- Requires 32-bit Python (COM SDK limitation)
- Windows authentication is used automatically
- Database ID: `SH` (CONTEXT)
