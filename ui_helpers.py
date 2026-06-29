"""
UI Helper Functions
Display formatting and user input handling for the CLI interface
"""

import os
import sys
from typing import List, Set, Optional


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header"""
    width = 70
    print("=" * width)
    print(f" {title}".center(width))
    print("=" * width)


def print_subheader(title: str):
    """Print a formatted subheader"""
    print(f"\n{title}")
    print("-" * 60)


def print_record_info(record, show_index: int = None):
    """
    Print formatted record information

    Args:
        record: RecordInfo object
        show_index: Optional index number to display
    """
    prefix = f"{show_index:4}. " if show_index is not None else "  "

    print(f"{prefix}{record.number}")
    print(f"      Title: {record.title}")

    if record.record_type:
        print(f"      Type: {record.record_type}")

    if record.is_container:
        print(f"      [FOLDER]")
    elif record.has_document:
        print(f"      [HAS DOCUMENT]")


def print_record_table(records: list, start_index: int = 1):
    """
    Print records in a table format

    Args:
        records: List of RecordInfo objects
        start_index: Starting index number
    """
    if not records:
        print("  No records found.")
        return

    # Print header
    print(f"\n{'#':>4}  {'Record Number':<15} {'Title':<45} {'Type':<10}")
    print("-" * 80)

    for i, rec in enumerate(records, start=start_index):
        # Truncate title if too long
        title = rec.title[:42] + "..." if len(rec.title) > 45 else rec.title

        # Determine type indicator
        if rec.is_container:
            type_str = "[FOLDER]"
        elif rec.has_document:
            type_str = "[DOC]"
        else:
            type_str = ""

        print(f"{i:>4}  {rec.number:<15} {title:<45} {type_str:<10}")


def print_download_progress(current: int, total: int, record_number: str):
    """Print download progress"""
    percentage = (current / total) * 100
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)

    print(f"\r  [{bar}] {current}/{total} ({percentage:.0f}%) - {record_number}", end="")
    sys.stdout.flush()

    if current == total:
        print()  # New line at the end


def print_download_summary(summary: dict):
    """Print download summary"""
    print_subheader("Download Summary")
    print(f"  Total files: {summary['total']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Total size: {summary['total_size_mb']} MB")

    if summary['failed_records']:
        print("\n  Failed downloads:")
        for record_num, error in summary['failed_records']:
            print(f"    - {record_num}: {error}")


def get_user_input(prompt: str, default: str = None) -> str:
    """
    Get input from user with optional default value

    Args:
        prompt: Prompt to display
        default: Default value if user presses Enter

    Returns:
        User input string
    """
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    user_input = input(prompt).strip()
    return user_input if user_input else (default or "")


def get_directory_input(prompt: str = "Enter download directory") -> str:
    """
    Get and validate a directory path from user

    Args:
        prompt: Prompt to display

    Returns:
        Valid directory path
    """
    while True:
        path = get_user_input(prompt)

        if not path:
            print("  Please enter a directory path.")
            continue

        # Expand user path (e.g., ~)
        path = os.path.expanduser(path)

        # Convert to absolute path
        path = os.path.abspath(path)

        # Check if parent directory exists or can be created
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            print(f"  Parent directory does not exist: {parent}")
            create = get_user_input("  Create it? (y/n)", "y")
            if create.lower() != 'y':
                continue

        return path


def parse_selection(selection: str, max_value: int) -> Set[int]:
    """
    Parse user selection string into set of indices

    Supports:
    - Single numbers: "1"
    - Comma-separated: "1,3,5"
    - Ranges: "1-5"
    - Mixed: "1,3-5,8"
    - All: "a" or "all"

    Args:
        selection: User input string
        max_value: Maximum valid value

    Returns:
        Set of selected indices (1-based)
    """
    selection = selection.strip().lower()

    # Handle "all" selection
    if selection in ('a', 'all'):
        return set(range(1, max_value + 1))

    selected = set()

    # Split by comma
    parts = selection.split(',')

    for part in parts:
        part = part.strip()

        if '-' in part:
            # Range
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())

                for i in range(start, end + 1):
                    if 1 <= i <= max_value:
                        selected.add(i)
            except ValueError:
                continue
        else:
            # Single number
            try:
                num = int(part)
                if 1 <= num <= max_value:
                    selected.add(num)
            except ValueError:
                continue

    return selected


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation

    Args:
        prompt: Question to ask
        default: Default value if user presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    response = get_user_input(f"{prompt} ({default_str})")

    if not response:
        return default

    return response.lower() in ('y', 'yes')


def print_menu(options: List[str], title: str = "Options"):
    """
    Print a menu of options

    Args:
        options: List of option strings
        title: Menu title
    """
    print(f"\n{title}:")
    for i, option in enumerate(options, 1):
        print(f"  [{i}] {option}")


def wait_for_enter(message: str = "Press Enter to continue..."):
    """Wait for user to press Enter"""
    input(f"\n{message}")


if __name__ == "__main__":
    # Test UI helpers
    print_header("UI Helpers Test")

    # Test selection parsing
    print("\nTesting selection parser:")
    test_cases = ["1", "1,3,5", "1-5", "1,3-5,8", "all", "a"]
    for test in test_cases:
        result = parse_selection(test, 10)
        print(f"  '{test}' -> {sorted(result)}")

    # Test confirmation
    print("\nTesting confirmation:")
    result = confirm_action("Do you want to continue?", default=True)
    print(f"  Result: {result}")
