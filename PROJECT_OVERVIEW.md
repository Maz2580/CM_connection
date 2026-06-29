# Content Manager Search Tool - Project Overview

## What Is This?

This is a custom search and download tool for Micro Focus Content Manager (our records management system). It provides a user-friendly way to find records and download multiple documents at once, instead of downloading them one by one through the standard interface.

---

## Why Was This Built?

### The Problem
When working with large sets of records in Content Manager (like the Asset Renewal Programs folder with 39+ items), downloading documents individually is:
- Time-consuming
- Repetitive
- Prone to missing files
- Inefficient for regular updates

### The Solution
This tool allows you to:
- Search for a record or folder by its record number
- See all contents of a folder in one view
- Select multiple items (or all items) with checkboxes
- Download everything to a folder of your choice in one click

---

## How Does It Connect?

### Using Official Micro Focus Tools
This tool uses the **official Content Manager SDK** (Software Development Kit) provided by Micro Focus. This is the same technology that other approved applications use to connect to Content Manager.

Key points:
- **No workarounds or hacks** - We use the official COM interface (`Trimsdk.Database`)
- **Same authentication as normal login** - Uses your Windows credentials automatically
- **Read-only operations** - The tool only reads and downloads; it cannot modify, delete, or create records
- **Same permissions as your user account** - You can only access what you're already allowed to access

### Connection Details
| Setting | Value |
|---------|-------|
| Database ID | SH |
| Database Name | CONTEXT |
| Authentication | Windows (automatic) |
| Access Level | Same as your user permissions |

---

## Is This Safe?

### Security Assurances

1. **Official API**
   - Uses the Micro Focus-provided SDK, not a third-party or custom solution
   - Same interface used by other enterprise integrations

2. **No Stored Credentials**
   - Your password is never entered or saved
   - Uses Windows single sign-on (your logged-in Windows account)

3. **Read-Only Access**
   - The tool can only:
     - Search for records
     - View record information
     - Download documents
   - The tool cannot:
     - Create records
     - Modify records
     - Delete records
     - Change permissions

4. **No Network Exposure**
   - Runs locally on your computer
   - No data sent to external servers
   - Downloads go directly to your specified folder

5. **Audit Trail**
   - All access is logged in Content Manager as normal
   - Same audit trail as if you accessed records through the standard interface

---

## How to Use It

### Option 1: Graphical Interface (Recommended)

1. Open Command Prompt
2. Navigate to the tool folder
3. Run: `venv32\Scripts\python.exe gui_app.py`
4. A window opens with:
   - Search box for record numbers
   - Checkbox list for selecting items
   - Browse button for choosing download location
   - Download button with progress bar

### Option 2: Command Line Interface

1. Open Command Prompt
2. Navigate to the tool folder
3. Run: `venv32\Scripts\python.exe main.py`
4. Follow the text-based menus

---

## FME Integration (Implemented)

### Previous Manual Process
Previously, when GIS data in Content Manager was updated, the workflow was:
1. Manually open Content Manager
2. Navigate to the relevant folder
3. Download each document one by one
4. Import into GIS tools

### Current Automated Process
The tool is now integrated with FME (Feature Manipulation Engine) using a **PythonCreator** transformer:

1. **PythonCreator calls `batch_download.py`** automatically
2. **Downloads are fetched** from Content Manager without manual intervention
3. **PythonCreator outputs one feature per file** with metadata (filepath, record_number, etc.)
4. **FeatureReader uses the filepath** to read downloaded Excel files
5. **GIS data is updated** in the same workflow

### FME Workflow
```
PythonCreator → FeatureReader → FeatureMerger → FeatureWriter
(download)      (read Excel)    (join on ID)    (update GIS)
```

### Benefits Achieved
- **Time Savings** - No more manual download sessions
- **Consistency** - Same process every time, no missed files
- **Freshness** - GIS data can be updated on a schedule
- **Reduced Errors** - Automation eliminates human mistakes

See `FME_INTEGRATION.md` for full technical documentation.

---

## Technical Requirements

| Requirement | Details |
|-------------|---------|
| Operating System | Windows |
| Content Manager | Must be installed (client or full) |
| Python | 32-bit version (included in venv32 folder) |
| Network | Access to Content Manager server |
| Permissions | Standard Content Manager user access |

---

## Summary

| Aspect | Details |
|--------|---------|
| **What it does** | Searches Content Manager and downloads multiple documents at once |
| **How it connects** | Uses official Micro Focus SDK with Windows authentication |
| **Security** | Read-only access, no stored passwords, same audit trail |
| **Manual use** | Bulk downloads through GUI or command line |
| **Automated use** | FME integration via PythonCreator for GIS updates |

---

## Questions?

For technical questions about this tool, contact the GIS team.

For Content Manager access or permissions, contact your records management administrator.

---

*Document created: January 2026*
*Tool Version: 1.0*
