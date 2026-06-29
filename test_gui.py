"""
Quick test to verify GUI dependencies are working
"""

import sys

def test_imports():
    print("Testing GUI dependencies...")

    print("  Importing customtkinter...", end=" ")
    try:
        import customtkinter as ctk
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")
        return False

    print("  Importing tkinter...", end=" ")
    try:
        import tkinter
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")
        return False

    print("  Importing CM modules...", end=" ")
    try:
        from cm_connection import CMConnection
        from cm_search import CMSearch
        from cm_download import CMDownload
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")
        return False

    print("\nAll dependencies OK!")
    print("\nTo run the GUI, use:")
    print("  venv32\\Scripts\\python.exe gui_app.py")

    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
