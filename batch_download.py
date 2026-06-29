"""
Content Manager Batch Download Tool
For automated/silent downloads - designed for FME integration

How to use:
    1. Edit download_config.json with your record number and output directory
    2. Run this script (or call from FME)

The script reads settings from download_config.json in the same folder.
"""

import json
import os
import sys
from datetime import datetime

# Add current directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cm_connection import CMConnection
from cm_search import CMSearch
from cm_download import CMDownload


# Config file path (same folder as this script)
CONFIG_FILE = os.path.join(SCRIPT_DIR, "download_config.json")


def log(message):
    """Print message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()


def load_config():
    """Load configuration from JSON file"""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    # Validate required fields
    if not config.get("record_number"):
        raise ValueError("Config missing 'record_number'")
    if not config.get("output_directory"):
        raise ValueError("Config missing 'output_directory'")

    return config


def write_manifest(results, output_path):
    """Write download manifest to JSON file"""
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "record_number": results["record"],
        "output_directory": results["output_dir"],
        "total_files": results["total"],
        "downloaded": results["downloaded"],
        "failed": results["failed"],
        "files": results["files"]
    }

    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return manifest


def download_all(config):
    """
    Download all contents of the configured record
    Returns: dict with results
    """
    record_number = config["record_number"]
    output_dir = config["output_directory"]
    database_id = config.get("options", {}).get("database_id", "SH")

    results = {
        "record": record_number,
        "output_dir": output_dir,
        "success": False,
        "total": 0,
        "downloaded": 0,
        "failed": 0,
        "files": []
    }

    # Connect to Content Manager
    log("Connecting to Content Manager...")

    try:
        connection = CMConnection()
        connection.connect(database_id)

        info = connection.get_connection_info()
        log(f"Connected to: {info['database_name']} as {info['current_user']}")

        search = CMSearch(connection)
        downloader = CMDownload(connection)

    except Exception as e:
        log(f"ERROR: Connection failed: {e}")
        return results

    # Get the record
    log(f"Searching for record: {record_number}")
    record = search.get_record(record_number)

    if not record:
        log(f"ERROR: Record '{record_number}' not found")
        connection.disconnect()
        return results

    log(f"Found: {record.title}")

    # Determine what to download
    if record.is_container:
        log(f"Record is a container (folder)")
        contents = search.get_container_contents(record_number)
        records_to_download = [r for r in contents if r.has_document]
        log(f"Found {len(contents)} items, {len(records_to_download)} have documents")
    else:
        if record.has_document:
            records_to_download = [record]
            log(f"Single record with document")
        else:
            log(f"Record has no document attached")
            records_to_download = []

    results["total"] = len(records_to_download)

    if not records_to_download:
        log("No documents to download")
        results["success"] = True
        connection.disconnect()
        return results

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    log(f"Output directory: {output_dir}")

    # Download each record
    log(f"\nDownloading {len(records_to_download)} files...")
    log("-" * 60)

    for i, rec in enumerate(records_to_download, 1):
        log(f"[{i}/{len(records_to_download)}] {rec.number} - {rec.title[:40]}...")

        download_result = downloader.download_record(rec.number, output_dir)

        # Extract filename from file_path
        if download_result.success and download_result.file_path:
            filename = os.path.basename(download_result.file_path)
        else:
            filename = None

        file_info = {
            "record_number": rec.number,
            "title": rec.title,
            "success": download_result.success,
            "filename": filename,
            "filepath": download_result.file_path if download_result.success else None,
            "error": download_result.error_message if not download_result.success else None
        }

        results["files"].append(file_info)

        if download_result.success:
            results["downloaded"] += 1
            log(f"    OK: {filename}")
        else:
            results["failed"] += 1
            log(f"    FAILED: {download_result.error_message}")

    # Disconnect
    try:
        connection.disconnect()
    except:
        pass

    results["success"] = results["failed"] == 0
    return results


def main():
    """Main entry point"""
    log("=" * 60)
    log("Content Manager Batch Download")
    log("=" * 60)

    # Load config
    try:
        log(f"Loading config from: {CONFIG_FILE}")
        config = load_config()
        log(f"Record: {config['record_number']}")
        log(f"Output: {config['output_directory']}")
    except Exception as e:
        log(f"ERROR: {e}")
        return 2

    # Run download
    results = download_all(config)

    # Write manifest if configured
    if config.get("options", {}).get("create_manifest", True):
        manifest_path = os.path.join(config["output_directory"], "manifest.json")
        write_manifest(results, manifest_path)
        log(f"\nManifest written to: {manifest_path}")

    # Summary
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    log(f"Files downloaded: {results['downloaded']}")
    log(f"Files failed: {results['failed']}")

    if results["success"]:
        log("Status: SUCCESS")
        return 0
    elif results["downloaded"] > 0:
        log("Status: PARTIAL SUCCESS")
        return 1
    else:
        log("Status: FAILED")
        return 2


if __name__ == "__main__":
    sys.exit(main())
