"""
Content Manager Search Module
Handles record searching and retrieval
"""

import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RecordInfo:
    """Data class to hold record information"""
    number: str
    title: str
    uri: int
    is_container: bool
    record_type: str = ""
    date_created: str = ""
    has_document: bool = False


class CMSearch:
    """Handles searching and retrieving records from Content Manager"""

    def __init__(self, connection):
        """
        Initialize search with a connection

        Args:
            connection: CMConnection instance
        """
        self.conn = connection
        self.db = connection.db

    def get_record(self, record_number: str) -> Optional[RecordInfo]:
        """
        Get a single record by its number

        Args:
            record_number: The record number (e.g., "E24/3074")

        Returns:
            RecordInfo object or None if not found
        """
        try:
            rec = self.db.GetRecord(record_number)

            # Get basic info
            info = RecordInfo(
                number=rec.Number,
                title=rec.Title,
                uri=rec.Uri,
                is_container=rec.IsContainer
            )

            # Try to get additional info
            try:
                info.record_type = rec.RecordType.Name
            except:
                pass

            try:
                info.date_created = str(rec.DateCreated)
            except:
                pass

            try:
                # Check if record has a document attached
                info.has_document = rec.IsElectronic
            except:
                pass

            return info

        except Exception as e:
            return None

    def get_record_object(self, record_number: str):
        """
        Get the raw COM record object

        Args:
            record_number: The record number

        Returns:
            COM Record object or None
        """
        try:
            return self.db.GetRecord(record_number)
        except:
            return None

    def get_container_contents(self, record_number: str) -> List[RecordInfo]:
        """
        Get all records contained within a container

        Args:
            record_number: The container record number

        Returns:
            List of RecordInfo objects
        """
        contents = []

        try:
            # Get the container record
            container = self.db.GetRecord(record_number)

            if not container.IsContainer:
                return contents

            # Create search for contained records
            search = self.db.NewRecordSearch()
            search.AddContainedWithinClause(container)

            # Execute search
            results = search.GetRecords()
            count = results.Count

            for i in range(count):
                try:
                    rec = results.Item(i)

                    info = RecordInfo(
                        number=rec.Number,
                        title=rec.Title,
                        uri=rec.Uri,
                        is_container=rec.IsContainer
                    )

                    # Try to get additional info
                    try:
                        info.record_type = rec.RecordType.Name
                    except:
                        pass

                    try:
                        info.has_document = rec.IsElectronic
                    except:
                        pass

                    contents.append(info)

                except Exception as e:
                    continue

        except Exception as e:
            pass

        return contents

    def search_by_title(self, title_keyword: str, max_results: int = 100) -> List[RecordInfo]:
        """
        Search for records by title keyword

        Args:
            title_keyword: Keyword to search in title
            max_results: Maximum number of results to return

        Returns:
            List of RecordInfo objects
        """
        results_list = []

        try:
            search = self.db.NewRecordSearch()
            search.AddTitleWordClause(title_keyword)

            results = search.GetRecords()
            count = min(results.Count, max_results)

            for i in range(count):
                try:
                    rec = results.Item(i)

                    info = RecordInfo(
                        number=rec.Number,
                        title=rec.Title,
                        uri=rec.Uri,
                        is_container=rec.IsContainer
                    )

                    try:
                        info.record_type = rec.RecordType.Name
                    except:
                        pass

                    try:
                        info.has_document = rec.IsElectronic
                    except:
                        pass

                    results_list.append(info)

                except:
                    continue

        except Exception as e:
            pass

        return results_list


if __name__ == "__main__":
    # Test search functionality
    from cm_connection import CMConnection

    print("Testing Content Manager Search...")

    conn = CMConnection()
    try:
        conn.connect("SH")
        search = CMSearch(conn)

        # Test get_record
        print("\nGetting record E24/3074...")
        record = search.get_record("E24/3074")
        if record:
            print(f"  Number: {record.number}")
            print(f"  Title: {record.title}")
            print(f"  Is Container: {record.is_container}")

        # Test get_container_contents
        if record and record.is_container:
            print(f"\nGetting contents of {record.number}...")
            contents = search.get_container_contents(record.number)
            print(f"  Found {len(contents)} items")
            for i, item in enumerate(contents[:5]):
                print(f"  {i+1}. {item.number} - {item.title}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()
