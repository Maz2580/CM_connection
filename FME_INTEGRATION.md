# FME Integration Guide

This guide explains how to integrate the Content Manager download tool with FME workflows using **PythonCreator**.

---

## Overview

The integration uses a **PythonCreator** transformer that:
1. Runs `batch_download.py` to download files from Content Manager
2. Reads the resulting `manifest.json`
3. Creates one FME feature per downloaded file with metadata attributes

**Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│  1. Edit download_config.json                               │
│         ↓                                                   │
│  2. Run FME Workbench                                       │
│         ↓                                                   │
│  3. PythonCreator calls batch_download.py                   │
│         ↓                                                   │
│  4. PythonCreator reads manifest.json                       │
│         ↓                                                   │
│  5. PythonCreator outputs features (one per file)           │
│         ↓                                                   │
│  6. FeatureReader reads Excel files using filepath          │
│         ↓                                                   │
│  7. FME processes and updates GIS layer                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Configure the Download

Before running FME, edit the config file:

**File:** `download_config.json`

```json
{
    "description": "Configuration for Content Manager batch downloads",

    "record_number": "E24/3074",
    "output_directory": "C:\\GIS\\Data\\Downloads",

    "options": {
        "create_manifest": true,
        "database_id": "SH"
    }
}
```

| Setting | Description |
|---------|-------------|
| `record_number` | The Content Manager record to download (e.g., `E24/3074`) |
| `output_directory` | Where to save downloaded files |
| `create_manifest` | If true, creates `manifest.json` with download details |
| `database_id` | Content Manager database (usually `SH`) |

---

## Step 2: Add PythonCreator to FME Workflow

Add a **PythonCreator** transformer to your FME workflow with the following code:

```python
import fmeobjects
import subprocess
import os
import json


class FeatureCreator:
    """
    PythonCreator: Downloads files from Content Manager and creates
    one feature per downloaded file.
    """

    def __init__(self):
        # Paths to Content Manager download tool
        self.script_dir = r"C:\Users\maz.ghasemi\Downloads\Maz - 2 July 2025\python\connection\content_manager\custom_search"
        self.python_exe = os.path.join(self.script_dir, "venv32", "Scripts", "python.exe")
        self.batch_script = os.path.join(self.script_dir, "batch_download.py")
        self.config_file = os.path.join(self.script_dir, "download_config.json")

        # Logger
        self.logger = fmeobjects.FMELogFile()

        # Store features to output
        self.features_to_output = []

    def log(self, message, severity=fmeobjects.FME_INFORM):
        """Log message to FME"""
        self.logger.logMessageString(str(message), severity)

    def input(self, feature):
        """
        Called for each input feature.
        In PythonCreator, this is called once with a dummy feature.
        We do all our work here and store features in a list.
        """

        self.log("=" * 60)
        self.log("Starting Content Manager Download...")
        self.log("=" * 60)

        # Run the batch download script
        try:
            result = subprocess.run(
                [self.python_exe, self.batch_script],
                capture_output=True,
                text=True,
                cwd=self.script_dir,
                timeout=300
            )

            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    self.log(line)

            if result.stderr:
                self.log(f"STDERR: {result.stderr}", fmeobjects.FME_WARN)

            self.log(f"Download script exit code: {result.returncode}")

        except Exception as e:
            self.log(f"ERROR: {e}", fmeobjects.FME_ERROR)
            self.features_to_output.append(self._create_error_feature(str(e)))
            return

        # Read config
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            output_dir = config.get("output_directory", "")
        except Exception as e:
            self.log(f"Config error: {e}", fmeobjects.FME_ERROR)
            self.features_to_output.append(self._create_error_feature(f"Config error: {e}"))
            return

        # Read manifest
        manifest_path = os.path.join(output_dir, "manifest.json")

        if not os.path.exists(manifest_path):
            self.log(f"Manifest not found: {manifest_path}", fmeobjects.FME_ERROR)
            self.features_to_output.append(self._create_error_feature("Manifest not created"))
            return

        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            self.log(f"Manifest error: {e}", fmeobjects.FME_ERROR)
            self.features_to_output.append(self._create_error_feature(f"Manifest error: {e}"))
            return

        # Create features for each file
        files = manifest.get("files", [])

        if not files:
            self.log("No files in manifest", fmeobjects.FME_WARN)
            self.features_to_output.append(self._create_error_feature("No files downloaded"))
            return

        self.log(f"Creating {len(files)} features from manifest...")

        for file_info in files:
            feat = fmeobjects.FMEFeature()

            # char(200) attributes
            feat.setAttribute("record_number", str(file_info.get("record_number") or ""))
            feat.setAttribute("title", str(file_info.get("title") or ""))
            feat.setAttribute("filename", str(file_info.get("filename") or ""))
            feat.setAttribute("filepath", str(file_info.get("filepath") or ""))
            feat.setAttribute("source_record", str(manifest.get("record_number") or ""))
            feat.setAttribute("download_timestamp", str(manifest.get("timestamp") or ""))
            feat.setAttribute("error_message", str(file_info.get("error") or ""))

            # logical attribute
            feat.setAttribute("success", 1 if file_info.get("success") else 0)

            # int32 attributes
            feat.setAttribute("total_files", int(manifest.get("total_files") or 0))
            feat.setAttribute("downloaded_count", int(manifest.get("downloaded") or 0))
            feat.setAttribute("failed_count", int(manifest.get("failed") or 0))

            # Status
            feat.setAttribute("download_status", "SUCCESS" if file_info.get("success") else "FAILED")

            self.features_to_output.append(feat)

        self.log(f"Successfully created {len(files)} features")
        self.log("=" * 60)

    def close(self):
        """
        Called after input() completes.
        Output all stored features using pyoutput.
        """
        for feat in self.features_to_output:
            self.pyoutput(feat)

    def _create_error_feature(self, error_message):
        """Create an error feature"""
        feat = fmeobjects.FMEFeature()
        feat.setAttribute("record_number", "")
        feat.setAttribute("title", "")
        feat.setAttribute("filename", "")
        feat.setAttribute("filepath", "")
        feat.setAttribute("source_record", "")
        feat.setAttribute("download_timestamp", "")
        feat.setAttribute("error_message", str(error_message)[:200])
        feat.setAttribute("success", 0)
        feat.setAttribute("total_files", 0)
        feat.setAttribute("downloaded_count", 0)
        feat.setAttribute("failed_count", 0)
        feat.setAttribute("download_status", "ERROR")
        return feat
```

---

## Step 3: Configure Exposed Attributes

In the PythonCreator transformer, expose the following attributes:

| Output Attribute | Type |
|------------------|------|
| `record_number` | char(200) |
| `title` | char(200) |
| `filename` | char(200) |
| `filepath` | char(200) |
| `source_record` | char(200) |
| `download_timestamp` | char(200) |
| `success` | logical |
| `total_files` | int32 |
| `downloaded_count` | int32 |
| `failed_count` | int32 |
| `error_message` | char(200) |
| `download_status` | char(200) |

---

## Step 4: Use Downloaded Files

After the PythonCreator, each feature contains:
- `filepath` - Full path to the downloaded file
- `record_number` - Content Manager record number
- `success` - Whether download succeeded

Use a **FeatureReader** to read the Excel files using the `filepath` attribute.

---

## Manifest File

The `batch_download.py` script creates a `manifest.json` file with download details:

```json
{
    "timestamp": "2026-01-16T14:30:00",
    "record_number": "E24/3074",
    "output_directory": "C:\\GIS\\Data\\Downloads",
    "total_files": 39,
    "downloaded": 39,
    "failed": 0,
    "files": [
        {
            "record_number": "M25/133489",
            "title": "2026-27 Footpath Renewal Program",
            "success": true,
            "filename": "2026-27 Footpath Renewal Program.xlsx",
            "filepath": "C:\\GIS\\Data\\Downloads\\2026-27 Footpath Renewal Program.xlsx"
        },
        ...
    ]
}
```

---

## Exit Codes

The batch download script returns exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success - all files downloaded |
| 1 | Partial success - some files failed |
| 2 | Error - connection failed or config error |

---

## Example FME Workflow

```
┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
│  PythonCreator   │───→│FeatureReader │───→│FeatureMerger │
│  (download +     │    │(Excel files  │    │(join on ID)  │
│   create features)│    │ via filepath)│    │              │
└──────────────────┘    └──────────────┘    └──────────────┘
                                                   │
                                                   ↓
                                            ┌──────────────┐
                                            │FeatureWriter │
                                            │ (GIS layer)  │
                                            └──────────────┘
```

1. **PythonCreator** - Downloads files and creates features with metadata
2. **FeatureReader** - Reads Excel files using the `filepath` attribute
3. **FeatureMerger** - Joins Excel data to GIS features using UniqueID
4. **FeatureWriter** - Updates the GIS layer

---

## Changing Projects

To use this for a different project:

1. Edit `download_config.json`
2. Change `record_number` to the new Content Manager record
3. Change `output_directory` if needed
4. Run FME

No code changes required!

---

## Troubleshooting

### "Class not registered" error
The PythonCreator uses the 32-bit Python from `venv32`. Ensure the path in the script is correct:
```
venv32\Scripts\python.exe batch_download.py
```

### Download fails
- Check Content Manager is accessible
- Verify you have permissions to the record
- Check the output directory is writable

### No features output
- Check FME log for error messages
- Verify `manifest.json` was created in the output directory
- Ensure `create_manifest` is set to `true` in config

---

## Files

| File | Purpose |
|------|---------|
| `download_config.json` | Configuration - edit this before running |
| `batch_download.py` | The script called by PythonCreator |
| `manifest.json` | Created in output directory with download results |
