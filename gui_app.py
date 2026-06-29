"""
Content Manager Search Tool - GUI Version
Modern graphical interface using CustomTkinter
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cm_connection import CMConnection
from cm_search import CMSearch, RecordInfo
from cm_download import CMDownload


# Set appearance
ctk.set_appearance_mode("System")  # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")


class ScrollableCheckboxFrame(ctk.CTkScrollableFrame):
    """Scrollable frame with checkboxes for record selection"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.checkbox_list = []
        self.record_list = []

    def clear(self):
        """Clear all checkboxes"""
        for widget in self.winfo_children():
            widget.destroy()
        self.checkbox_list = []
        self.record_list = []

    def add_header(self):
        """Add header row"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(5, 10))

        # Header labels
        ctk.CTkLabel(header_frame, text="", width=40).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="#", width=40, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Record Number", width=120, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Title", width=400, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Type", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

    def add_record(self, index: int, record: RecordInfo):
        """Add a record row with checkbox"""
        self.record_list.append(record)

        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(fill="x", padx=5, pady=2)

        # Checkbox
        var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(row_frame, text="", variable=var, width=40)
        checkbox.pack(side="left", padx=2)
        self.checkbox_list.append(var)

        # Index
        ctk.CTkLabel(row_frame, text=str(index), width=40).pack(side="left", padx=2)

        # Record number
        ctk.CTkLabel(row_frame, text=record.number, width=120, anchor="w").pack(side="left", padx=5)

        # Title (truncated)
        title = record.title[:55] + "..." if len(record.title) > 58 else record.title
        ctk.CTkLabel(row_frame, text=title, width=400, anchor="w").pack(side="left", padx=5)

        # Type indicator
        if record.is_container:
            type_text = "📁 Folder"
        elif record.has_document:
            type_text = "📄 Doc"
        else:
            type_text = "—"
        ctk.CTkLabel(row_frame, text=type_text, width=80).pack(side="left", padx=5)

    def get_selected_records(self):
        """Get list of selected records"""
        selected = []
        for i, var in enumerate(self.checkbox_list):
            if var.get():
                selected.append(self.record_list[i])
        return selected

    def select_all(self):
        """Select all checkboxes"""
        for var in self.checkbox_list:
            var.set(True)

    def deselect_all(self):
        """Deselect all checkboxes"""
        for var in self.checkbox_list:
            var.set(False)

    def get_selected_count(self):
        """Get count of selected items"""
        return sum(1 for var in self.checkbox_list if var.get())


class ContentManagerGUI(ctk.CTk):
    """Main GUI Application"""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Content Manager Search Tool")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Connection objects
        self.connection = None
        self.search = None
        self.downloader = None
        self.current_records = []

        # Default download directory
        self.download_dir = os.path.expanduser("~/Downloads/ContentManager")

        # Build UI
        self.create_widgets()

        # Connect to Content Manager
        self.after(100, self.connect_to_cm)

    def create_widgets(self):
        """Create all UI widgets"""

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === Header Frame ===
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Content Manager Search Tool",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=15, pady=10)

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="Connecting...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right", padx=15, pady=10)

        # === Search Frame ===
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Record number search
        ctk.CTkLabel(self.search_frame, text="Record Number:").pack(side="left", padx=(15, 5), pady=10)

        self.search_entry = ctk.CTkEntry(self.search_frame, width=200, placeholder_text="e.g., E24/3074")
        self.search_entry.pack(side="left", padx=5, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.search_record())

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="🔍 Search",
            width=100,
            command=self.search_record
        )
        self.search_button.pack(side="left", padx=5, pady=10)

        # Separator
        ctk.CTkLabel(self.search_frame, text="|").pack(side="left", padx=10)

        # Download directory
        ctk.CTkLabel(self.search_frame, text="Download to:").pack(side="left", padx=5, pady=10)

        self.dir_entry = ctk.CTkEntry(self.search_frame, width=250)
        self.dir_entry.pack(side="left", padx=5, pady=10)
        self.dir_entry.insert(0, self.download_dir)

        self.browse_button = ctk.CTkButton(
            self.search_frame,
            text="Browse",
            width=80,
            command=self.browse_directory
        )
        self.browse_button.pack(side="left", padx=5, pady=10)

        # === Results Frame ===
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)

        # Results header
        self.results_header = ctk.CTkLabel(
            self.results_frame,
            text="Enter a record number and click Search",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.results_header.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # Scrollable checkbox frame for results
        self.results_list = ScrollableCheckboxFrame(
            self.results_frame,
            width=850,
            height=350
        )
        self.results_list.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # === Action Frame ===
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Selection buttons
        self.select_all_btn = ctk.CTkButton(
            self.action_frame,
            text="Select All",
            width=100,
            command=self.select_all
        )
        self.select_all_btn.pack(side="left", padx=(15, 5), pady=10)

        self.deselect_all_btn = ctk.CTkButton(
            self.action_frame,
            text="Deselect All",
            width=100,
            command=self.deselect_all
        )
        self.deselect_all_btn.pack(side="left", padx=5, pady=10)

        # Selection count label
        self.selection_label = ctk.CTkLabel(
            self.action_frame,
            text="0 items selected"
        )
        self.selection_label.pack(side="left", padx=20, pady=10)

        # Download button
        self.download_button = ctk.CTkButton(
            self.action_frame,
            text="⬇ Download Selected",
            width=150,
            fg_color="green",
            hover_color="darkgreen",
            command=self.download_selected
        )
        self.download_button.pack(side="right", padx=15, pady=10)

        # === Progress Frame ===
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready",
            anchor="w"
        )
        self.progress_label.pack(side="left", padx=15, pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(side="right", padx=15, pady=10)
        self.progress_bar.set(0)

    def connect_to_cm(self):
        """Connect to Content Manager"""
        try:
            self.connection = CMConnection()
            self.connection.connect("SH")
            self.search = CMSearch(self.connection)
            self.downloader = CMDownload(self.connection)

            info = self.connection.get_connection_info()
            self.status_label.configure(
                text=f"✓ Connected: {info['database_name']} | User: {info['current_user']}",
                text_color="green"
            )
            self.progress_label.configure(text="Ready - Enter a record number to search")

        except Exception as e:
            self.status_label.configure(
                text=f"✗ Connection failed: {str(e)[:50]}",
                text_color="red"
            )
            messagebox.showerror("Connection Error", f"Failed to connect to Content Manager:\n{e}")

    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(
            initialdir=self.dir_entry.get(),
            title="Select Download Directory"
        )
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.download_dir = directory

    def search_record(self):
        """Search for a record"""
        record_number = self.search_entry.get().strip()

        if not record_number:
            messagebox.showwarning("Input Required", "Please enter a record number.")
            return

        if not self.search:
            messagebox.showerror("Not Connected", "Not connected to Content Manager.")
            return

        # Clear previous results
        self.results_list.clear()
        self.progress_label.configure(text=f"Searching for {record_number}...")
        self.progress_bar.set(0.2)
        self.update()

        # Get the record
        record = self.search.get_record(record_number)

        if not record:
            self.results_header.configure(text=f"Record '{record_number}' not found")
            self.progress_label.configure(text="Record not found")
            self.progress_bar.set(0)
            messagebox.showinfo("Not Found", f"Record '{record_number}' was not found.")
            return

        self.progress_bar.set(0.5)
        self.update()

        if record.is_container:
            # Get container contents
            self.progress_label.configure(text=f"Loading contents of {record_number}...")
            self.update()

            contents = self.search.get_container_contents(record_number)

            if contents:
                self.results_header.configure(
                    text=f"📁 {record.title} ({len(contents)} items)"
                )

                # Add header and records
                self.results_list.add_header()
                for i, rec in enumerate(contents, 1):
                    self.results_list.add_record(i, rec)

                self.current_records = contents
                self.progress_label.configure(text=f"Found {len(contents)} items")
            else:
                self.results_header.configure(text=f"📁 {record.title} (empty)")
                self.progress_label.configure(text="Container is empty")

        else:
            # Single record
            self.results_header.configure(text=f"📄 {record.title}")
            self.results_list.add_header()
            self.results_list.add_record(1, record)
            self.current_records = [record]
            self.progress_label.configure(text="Found 1 record")

        self.progress_bar.set(1.0)
        self.after(1000, lambda: self.progress_bar.set(0))
        self.update_selection_count()

    def select_all(self):
        """Select all items"""
        self.results_list.select_all()
        self.update_selection_count()

    def deselect_all(self):
        """Deselect all items"""
        self.results_list.deselect_all()
        self.update_selection_count()

    def update_selection_count(self):
        """Update the selection count label"""
        count = self.results_list.get_selected_count()
        self.selection_label.configure(text=f"{count} item(s) selected")

    def download_selected(self):
        """Download selected records"""
        selected = self.results_list.get_selected_records()

        if not selected:
            messagebox.showwarning("No Selection", "Please select items to download.")
            return

        # Filter to only records with documents
        downloadable = [r for r in selected if r.has_document]

        if not downloadable:
            messagebox.showwarning(
                "No Documents",
                "None of the selected items have downloadable documents."
            )
            return

        # Get download directory
        download_dir = self.dir_entry.get().strip()
        if not download_dir:
            messagebox.showwarning("Directory Required", "Please specify a download directory.")
            return

        # Confirm download
        if not messagebox.askyesno(
            "Confirm Download",
            f"Download {len(downloadable)} document(s) to:\n{download_dir}?"
        ):
            return

        # Create directory if needed
        os.makedirs(download_dir, exist_ok=True)

        # Start download in background thread
        self.download_button.configure(state="disabled", text="Downloading...")
        thread = threading.Thread(
            target=self.perform_download,
            args=(downloadable, download_dir)
        )
        thread.start()

    def perform_download(self, records, download_dir):
        """Perform download in background thread"""
        total = len(records)
        successful = 0
        failed = 0

        for i, record in enumerate(records):
            # Update progress
            progress = (i + 1) / total
            self.after(0, lambda p=progress, r=record.number: self.update_download_progress(p, r, i+1, total))

            # Download
            result = self.downloader.download_record(record.number, download_dir)

            if result.success:
                successful += 1
            else:
                failed += 1

        # Complete
        self.after(0, lambda: self.download_complete(successful, failed, download_dir))

    def update_download_progress(self, progress, record_number, current, total):
        """Update download progress (called from main thread)"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"Downloading {current}/{total}: {record_number}")

    def download_complete(self, successful, failed, download_dir):
        """Handle download completion"""
        self.progress_bar.set(0)
        self.download_button.configure(state="normal", text="⬇ Download Selected")
        self.progress_label.configure(text=f"Complete: {successful} downloaded, {failed} failed")

        # Show summary
        message = f"Download Complete!\n\n"
        message += f"Successful: {successful}\n"
        message += f"Failed: {failed}\n\n"
        message += f"Files saved to:\n{download_dir}"

        messagebox.showinfo("Download Complete", message)

        # Open folder option
        if messagebox.askyesno("Open Folder", "Open download folder?"):
            os.startfile(download_dir)

    def on_closing(self):
        """Handle window close"""
        if self.connection:
            try:
                self.connection.disconnect()
            except:
                pass
        self.destroy()


def main():
    """Entry point"""
    app = ContentManagerGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
