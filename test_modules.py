"""
Test script to verify all modules work correctly
"""

import sys

def flush_print(msg):
    print(msg)
    sys.stdout.flush()

def main():
    flush_print("=" * 60)
    flush_print("Testing Content Manager Custom Search Modules")
    flush_print("=" * 60)

    # Test 1: Connection
    flush_print("\n[1] Testing Connection...")
    from cm_connection import CMConnection

    conn = CMConnection()
    try:
        conn.connect("SH")
        info = conn.get_connection_info()
        flush_print(f"    Connected: {info['connected']}")
        flush_print(f"    Database: {info['database_name']}")
        flush_print(f"    User: {info['current_user']}")
        flush_print("    PASSED")
    except Exception as e:
        flush_print(f"    FAILED: {e}")
        return

    # Test 2: Search
    flush_print("\n[2] Testing Search...")
    from cm_search import CMSearch

    search = CMSearch(conn)

    # Test get_record
    flush_print("    Getting record E24/3074...")
    record = search.get_record("E24/3074")
    if record:
        flush_print(f"    Found: {record.number} - {record.title}")
        flush_print(f"    Is Container: {record.is_container}")
        flush_print("    PASSED")
    else:
        flush_print("    FAILED: Record not found")

    # Test get_container_contents
    if record and record.is_container:
        flush_print("\n    Getting container contents...")
        contents = search.get_container_contents(record.number)
        flush_print(f"    Found {len(contents)} items")
        if contents:
            flush_print(f"    First item: {contents[0].number} - {contents[0].title}")
            flush_print("    PASSED")
        else:
            flush_print("    WARNING: No contents found")

    # Test 3: Download module import
    flush_print("\n[3] Testing Download Module...")
    from cm_download import CMDownload

    downloader = CMDownload(conn)
    flush_print("    Download module initialized")
    flush_print("    PASSED")

    # Test 4: UI Helpers
    flush_print("\n[4] Testing UI Helpers...")
    from ui_helpers import parse_selection

    test_cases = [
        ("1", 10, {1}),
        ("1,3,5", 10, {1, 3, 5}),
        ("1-5", 10, {1, 2, 3, 4, 5}),
        ("all", 5, {1, 2, 3, 4, 5}),
    ]

    all_passed = True
    for input_str, max_val, expected in test_cases:
        result = parse_selection(input_str, max_val)
        if result == expected:
            flush_print(f"    '{input_str}' -> {sorted(result)} OK")
        else:
            flush_print(f"    '{input_str}' -> {sorted(result)} FAILED (expected {sorted(expected)})")
            all_passed = False

    if all_passed:
        flush_print("    PASSED")
    else:
        flush_print("    SOME TESTS FAILED")

    # Cleanup
    conn.disconnect()

    flush_print("\n" + "=" * 60)
    flush_print("All module tests completed!")
    flush_print("=" * 60)


if __name__ == "__main__":
    main()
