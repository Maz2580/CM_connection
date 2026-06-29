"""
Content Manager Download Module
Handles downloading documents from Content Manager
"""

import os
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime


@dataclass
class DownloadResult:
    """Data class to hold download result information"""
    record_number: str
    title: str
    success: bool
    file_path: str = ""
    error_message: str = ""
    file_size: int = 0


class CMDownload:
    """Handles downloading documents from Content Manager"""

    def __init__(self, connection):
        """
        Initialize downloader with a connection

        Args:
            connection: CMConnection instance
        """
        self.conn = connection
        self.db = connection.db

    def download_record(self, record_number: str, download_dir: str,
                        custom_filename: str = None) -> DownloadResult:
        """
        Download a single record's document

        Args:
            record_number: The record number to download
            download_dir: Directory to save the file
            custom_filename: Optional custom filename (without extension)

        Returns:
            DownloadResult object
        """
        result = DownloadResult(
            record_number=record_number,
            title="",
            success=False
        )

        try:
            # Get the record
            rec = self.db.GetRecord(record_number)
            result.title = rec.Title

            # Check if record has a document
            try:
                is_electronic = rec.IsElectronic
            except:
                is_electronic = False

            if not is_electronic:
                result.error_message = "Record has no electronic document"
                return result

            # Create download directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)

            # Get the file extension from the record
            try:
                extension = rec.Extension
                if not extension.startswith('.'):
                    extension = '.' + extension
            except:
                extension = '.dat'

            # Determine filename
            if custom_filename:
                filename = custom_filename + extension
            else:
                # Use record number as filename, replacing / with _
                safe_number = record_number.replace('/', '_').replace('\\', '_')
                filename = f"{safe_number}{extension}"

            # Full path
            file_path = os.path.join(download_dir, filename)

            # Handle filename conflicts
            file_path = self._get_unique_filepath(file_path)

            # Download the document
            rec.GetDocument(file_path, False, "", "")

            # Verify download
            if os.path.exists(file_path):
                result.success = True
                result.file_path = file_path
                result.file_size = os.path.getsize(file_path)
            else:
                result.error_message = "Download completed but file not found"

        except Exception as e:
            result.error_message = str(e)

        return result

    def download_multiple(self, record_numbers: List[str], download_dir: str,
                          progress_callback=None) -> List[DownloadResult]:
        """
        Download multiple records

        Args:
            record_numbers: List of record numbers to download
            download_dir: Directory to save files
            progress_callback: Optional callback function(current, total, record_number)

        Returns:
            List of DownloadResult objects
        """
        results = []
        total = len(record_numbers)

        for i, record_number in enumerate(record_numbers):
            if progress_callback:
                progress_callback(i + 1, total, record_number)

            result = self.download_record(record_number, download_dir)
            results.append(result)

        return results

    def _get_unique_filepath(self, file_path: str) -> str:
        """
        Get a unique filepath by appending number if file exists

        Args:
            file_path: Original file path

        Returns:
            Unique file path
        """
        if not os.path.exists(file_path):
            return file_path

        base, ext = os.path.splitext(file_path)
        counter = 1

        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def get_download_summary(self, results: List[DownloadResult]) -> dict:
        """
        Get summary of download results

        Args:
            results: List of DownloadResult objects

        Returns:
            Dictionary with summary statistics
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        total_size = sum(r.file_size for r in successful)

        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "failed_records": [(r.record_number, r.error_message) for r in failed]
        }


if __name__ == "__main__":
    # Test download functionality
    from cm_connection import CMConnection
    from cm_search import CMSearch

    print("Testing Content Manager Download...")

    conn = CMConnection()
    try:
        conn.connect("SH")
        search = CMSearch(conn)
        downloader = CMDownload(conn)

        # Get a test record
        print("\nGetting record E24/3074...")
        record = search.get_record("E24/3074")

        if record:
            print(f"  Title: {record.title}")
            print(f"  Has Document: {record.has_document}")

            if record.is_container:
                print("\nThis is a container. Getting first item with document...")
                contents = search.get_container_contents(record.number)
                for item in contents:
                    if item.has_document:
                        print(f"  Found: {item.number} - {item.title}")
                        break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()
