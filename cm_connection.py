"""
Content Manager Connection Handler
Manages connection to Micro Focus Content Manager via COM SDK
"""

import win32com.client
import pythoncom
import sys


class CMConnection:
    """Handles connection to Content Manager database"""

    def __init__(self):
        self.db = None
        self.is_connected = False
        self.database_name = None
        self.database_id = None
        self.current_user = None

    def connect(self, database_id="SH"):
        """
        Connect to Content Manager database

        Args:
            database_id: Database ID to connect to (default: "SH")

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Initialize COM
            pythoncom.CoInitialize()

            # Create database object
            self.db = win32com.client.Dispatch("Trimsdk.Database")

            # Connect to specified database
            self.db.Id = database_id

            # Store connection info
            self.database_id = database_id
            self.database_name = self.db.Name
            self.current_user = self.db.CurrentUser.FormattedName
            self.is_connected = True

            return True

        except Exception as e:
            self.is_connected = False
            raise ConnectionError(f"Failed to connect to Content Manager: {e}")

    def disconnect(self):
        """Disconnect from Content Manager"""
        try:
            self.db = None
            self.is_connected = False
            pythoncom.CoUninitialize()
        except:
            pass

    def get_available_databases(self):
        """
        Get list of available databases

        Returns:
            list: List of tuples (id, name) for each database
        """
        databases = []
        try:
            dbs = win32com.client.Dispatch("Trimsdk.Databases")
            for i in range(dbs.Count):
                db_item = dbs.Item(i)
                databases.append((db_item.Id, db_item.Name))
        except Exception as e:
            pass
        return databases

    def get_connection_info(self):
        """
        Get current connection information

        Returns:
            dict: Connection details
        """
        return {
            "connected": self.is_connected,
            "database_id": self.database_id,
            "database_name": self.database_name,
            "current_user": self.current_user
        }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Singleton instance for easy access
_connection = None

def get_connection():
    """Get or create the global connection instance"""
    global _connection
    if _connection is None:
        _connection = CMConnection()
    return _connection


if __name__ == "__main__":
    # Test connection
    print("Testing Content Manager Connection...")

    conn = CMConnection()
    try:
        conn.connect("SH")
        info = conn.get_connection_info()
        print(f"Connected: {info['connected']}")
        print(f"Database: {info['database_name']} ({info['database_id']})")
        print(f"User: {info['current_user']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.disconnect()
