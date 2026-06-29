"""
Content Manager Custom Search Tool
Interactive CLI for searching and downloading records from Content Manager
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cm_connection import CMConnection
from cm_search import CMSearch, RecordInfo
from cm_download import CMDownload
from ui_helpers import (
    clear_screen, print_header, print_subheader,
    print_record_info, print_record_table,
    print_download_progress, print_download_summary,
    get_user_input, get_directory_input, parse_selection,
    confirm_action, wait_for_enter
)


class ContentManagerApp:
    """Main application class for Content Manager search tool"""

    def __init__(self):
        self.connection = None
        self.search = None
        self.downloader = None
        self.default_download_dir = os.path.expanduser("~/Downloads/ContentManager")

    def connect(self) -> bool:
        """Establish connection to Content Manager"""
        try:
            print("\nConnecting to Content Manager...")
            self.connection = CMConnection()
            self.connection.connect("SH")

            self.search = CMSearch(self.connection)
            self.downloader = CMDownload(self.connection)

            info = self.connection.get_connection_info()
            print(f"  Connected to: {info['database_name']}")
            print(f"  User: {info['current_user']}")
            return True

        except Exception as e:
            print(f"  Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from Content Manager"""
        if self.connection:
            self.connection.disconnect()

    def run(self):
        """Main application loop"""
        clear_screen()
        print_header("Content Manager Search Tool")

        # Connect to CM
        if not self.connect():
            print("\nFailed to connect. Exiting.")
            return

        try:
            while True:
                self.main_menu()

        except KeyboardInterrupt:
            print("\n\nExiting...")
        finally:
            self.disconnect()

    def main_menu(self):
        """Display main menu and handle user choice"""
        print("\n" + "=" * 60)
        print("MAIN MENU")
        print("=" * 60)
        print("\n  [1] Search by Record Number")
        print("  [2] Search by Title Keyword")
        print("  [3] Change Download Directory")
        print("  [Q] Quit")

        print(f"\n  Current download directory: {self.default_download_dir}")

        choice = get_user_input("\nEnter choice").lower()

        if choice == '1':
            self.search_by_number()
        elif choice == '2':
            self.search_by_title()
        elif choice == '3':
            self.change_download_dir()
        elif choice in ('q', 'quit', 'exit'):
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("  Invalid choice. Please try again.")

    def search_by_number(self):
        """Search for a record by its number"""
        print_subheader("Search by Record Number")

        record_number = get_user_input("Enter record number (e.g., E24/3074)")
        if not record_number:
            return

        print(f"\nSearching for: {record_number}...")

        # Get the record
        record = self.search.get_record(record_number)

        if not record:
            print(f"  Record '{record_number}' not found.")
            wait_for_enter()
            return

        # Display record info
        print_subheader(f"Record Found: {record.number}")
        print(f"  Title: {record.title}")
        print(f"  URI: {record.uri}")
        print(f"  Type: {record.record_type}")
        print(f"  Is Container: {record.is_container}")
        print(f"  Has Document: {record.has_document}")

        if record.is_container:
            # It's a folder - show contents
            self.handle_container(record)
        else:
            # It's a single record
            self.handle_single_record(record)

    def handle_container(self, container: RecordInfo):
        """Handle a container (folder) record"""
        print_subheader(f"Contents of: {container.number}")

        # Get container contents
        print("Loading contents...")
        contents = self.search.get_container_contents(container.number)

        if not contents:
            print("  No contents found in this container.")
            wait_for_enter()
            return

        # Display contents
        print_record_table(contents)

        # Selection menu
        self.container_menu(contents)

    def container_menu(self, contents: list):
        """Display menu for container contents"""
        while True:
            print("\n" + "-" * 60)
            print("OPTIONS:")
            print("  [A]     - Download ALL items")
            print("  [1,2,5] - Download specific items (comma-separated)")
            print("  [1-5]   - Download range of items")
            print("  [V]     - View an item's details")
            print("  [B]     - Go back to main menu")

            choice = get_user_input("\nEnter selection").strip()

            if not choice:
                continue

            if choice.lower() == 'b':
                return

            if choice.lower() == 'v':
                # View specific item
                item_num = get_user_input("Enter item number to view")
                try:
                    idx = int(item_num) - 1
                    if 0 <= idx < len(contents):
                        item = contents[idx]
                        self.view_record_details(item)
                    else:
                        print("  Invalid item number.")
                except ValueError:
                    print("  Please enter a valid number.")
                continue

            # Parse selection for download
            selected = parse_selection(choice, len(contents))

            if not selected:
                print("  No valid items selected.")
                continue

            # Get download directory
            print(f"\n  Selected {len(selected)} item(s) for download.")
            download_dir = get_user_input(
                "Download directory",
                self.default_download_dir
            )

            if not download_dir:
                download_dir = self.default_download_dir

            # Confirm download
            if not confirm_action(f"Download {len(selected)} item(s) to '{download_dir}'?", True):
                continue

            # Perform downloads
            self.download_selected(contents, selected, download_dir)

    def handle_single_record(self, record: RecordInfo):
        """Handle a single (non-container) record"""
        while True:
            print("\n" + "-" * 60)
            print("OPTIONS:")
            if record.has_document:
                print("  [D] - Download this document")
            print("  [B] - Go back to main menu")

            choice = get_user_input("\nEnter choice").lower()

            if choice == 'b':
                return

            if choice == 'd' and record.has_document:
                # Download the document
                download_dir = get_user_input(
                    "Download directory",
                    self.default_download_dir
                )

                if not download_dir:
                    download_dir = self.default_download_dir

                print(f"\nDownloading {record.number}...")
                result = self.downloader.download_record(record.number, download_dir)

                if result.success:
                    print(f"  SUCCESS: Saved to {result.file_path}")
                    print(f"  Size: {result.file_size:,} bytes")
                else:
                    print(f"  FAILED: {result.error_message}")

                wait_for_enter()
                return

    def view_record_details(self, record: RecordInfo):
        """View detailed information about a record"""
        print_subheader(f"Record Details: {record.number}")
        print(f"  Number: {record.number}")
        print(f"  Title: {record.title}")
        print(f"  URI: {record.uri}")
        print(f"  Type: {record.record_type}")
        print(f"  Is Container: {record.is_container}")
        print(f"  Has Document: {record.has_document}")

        wait_for_enter()

    def download_selected(self, contents: list, selected: set, download_dir: str):
        """Download selected records"""
        print_subheader("Downloading...")

        # Get record numbers to download
        records_to_download = []
        for idx in sorted(selected):
            record = contents[idx - 1]
            if record.has_document:
                records_to_download.append(record.number)
            else:
                print(f"  Skipping {record.number} - no document attached")

        if not records_to_download:
            print("  No documents to download.")
            wait_for_enter()
            return

        print(f"\n  Downloading {len(records_to_download)} document(s)...\n")

        # Download with progress
        results = self.downloader.download_multiple(
            records_to_download,
            download_dir,
            progress_callback=print_download_progress
        )

        # Show summary
        summary = self.downloader.get_download_summary(results)
        print_download_summary(summary)

        print(f"\n  Files saved to: {download_dir}")
        wait_for_enter()

    def search_by_title(self):
        """Search for records by title keyword"""
        print_subheader("Search by Title Keyword")

        keyword = get_user_input("Enter keyword to search in titles")
        if not keyword:
            return

        print(f"\nSearching for '{keyword}'...")

        results = self.search.search_by_title(keyword, max_results=50)

        if not results:
            print("  No records found matching that keyword.")
            wait_for_enter()
            return

        print_subheader(f"Search Results: {len(results)} records found")
        print_record_table(results)

        # Allow selection
        self.container_menu(results)

    def change_download_dir(self):
        """Change the default download directory"""
        print_subheader("Change Download Directory")
        print(f"  Current: {self.default_download_dir}")

        new_dir = get_directory_input("Enter new download directory")
        if new_dir:
            self.default_download_dir = new_dir
            print(f"  Download directory changed to: {new_dir}")


def main():
    """Entry point"""
    app = ContentManagerApp()
    app.run()


if __name__ == "__main__":
    main()
