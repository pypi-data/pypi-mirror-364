"""
Directory selection UI for polygon measurement tool.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Tuple


class DirectorySelector:
    """Simple directory selection dialog with enhanced UI."""

    def __init__(self):
        self.root = None
        self.images_dir = None
        self.labels_dir = None
        self.output_dir = None
        self.dir_labels = {}
        self.status_label = None

    def select_directory(self, title: str = "Select Directory") -> Optional[str]:
        """Show directory selection dialog."""
        try:
            if self.root is None:
                self.root = tk.Tk()
                self.root.withdraw()  # Hide the main window

            directory = filedialog.askdirectory(title=title)
            return directory if directory else None
        except Exception as e:
            print(f"Error opening directory dialog: {e}")
            return None

    def show_setup_dialog(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Show setup dialog for selecting directories."""
        try:
            if self.root is None:
                self.root = tk.Tk()

            self.root.title("Polygon Measurement Tool - Setup")
            self.root.geometry("600x400")

            # Configure root window
            self.root.configure(bg="#f0f0f0")

            # Initialize directory display labels dictionary
            self.dir_labels = {}

            # Create main frame
            main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Create UI elements
            self._create_title_section(main_frame)
            self._create_directory_selectors(main_frame)
            self._create_buttons(main_frame)
            self._create_status_label(main_frame)

            # Center the window
            self._center_window()

            # Run the dialog
            self.root.mainloop()

            return self.images_dir, self.labels_dir, self.output_dir

        except Exception as e:
            print(f"Error creating setup dialog: {e}")
            return None, None, None

    def _create_title_section(self, parent):
        """Create the title section of the dialog."""
        title_label = tk.Label(
            parent,
            text="Polygon Measurement Tool",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#1a1a1a",
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            parent,
            text="Please select your working directories:",
            font=("Arial", 11),
            bg="#f0f0f0",
            fg="#333333",
        )
        subtitle_label.pack(pady=(0, 20))

    def _create_directory_selectors(self, parent):
        """Create directory selection widgets."""
        self._create_directory_selector(parent, "Images Directory:", "images")
        self._create_directory_selector(parent, "Labels Directory:", "labels")
        self._create_directory_selector(parent, "Output Directory:", "output")

    def _create_directory_selector(self, parent, label_text: str, dir_type: str):
        """Create a directory selector widget."""
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(fill=tk.X, pady=5)

        # Label
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#1a1a1a",
            width=15,
            anchor="w",
        )
        label.pack(side=tk.LEFT)

        # Directory display label
        dir_label = tk.Label(
            frame,
            text="(Not selected)",
            font=("Arial", 10),
            bg="#ffffff",
            fg="#333333",
            anchor="w",
            relief="sunken",
            borderwidth=1,
        )
        dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        self.dir_labels[dir_type] = dir_label

        # Browse button
        browse_btn = tk.Button(
            frame,
            text="Browse...",
            command=lambda: self._browse_directory(dir_type),
            bg="#1565c0",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            relief="raised",
            borderwidth=2,
            activebackground="#1976d2",
            activeforeground="white",
        )
        browse_btn.pack(side=tk.RIGHT)

    def _create_buttons(self, parent):
        """Create the action buttons."""
        button_frame = tk.Frame(parent, bg="#f0f0f0")
        button_frame.pack(pady=20)

        # Start button
        start_btn = tk.Button(
            button_frame,
            text="Start Processing",
            command=self._on_start,
            bg="#2e7d32",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            relief="raised",
            borderwidth=2,
            activebackground="#388e3c",
            activeforeground="white",
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            bg="#c62828",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=10,
            relief="raised",
            borderwidth=2,
            activebackground="#d32f2f",
            activeforeground="white",
        )
        cancel_btn.pack(side=tk.LEFT)

    def _create_status_label(self, parent):
        """Create the status label."""
        self.status_label = tk.Label(
            parent,
            text="",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="#b71c1c",
        )
        self.status_label.pack(pady=(10, 0))

    def _center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"600x400+{x}+{y}")

    def _browse_directory(self, dir_type: str):
        """Handle directory browsing."""
        title_map = {
            "images": "Select Images Directory",
            "labels": "Select Labels Directory",
            "output": "Select Output Directory",
        }

        directory = self.select_directory(title_map.get(dir_type, "Select Directory"))

        if directory:
            setattr(self, f"{dir_type}_dir", directory)

            # Update display
            short_path = directory if len(directory) <= 50 else "..." + directory[-47:]
            self.dir_labels[dir_type].config(
                text=short_path,
                fg="#000000",
                bg="#e8f5e8",
            )
            self.status_label.config(
                text="",
                fg="#b71c1c",
                bg="#f0f0f0",
            )

    def _on_start(self):
        """Handle start button click."""
        if not self.images_dir:
            self._show_error("Please select an images directory")
            return
        if not self.labels_dir:
            self._show_error("Please select a labels directory")
            return
        if not self.output_dir:
            # Use default output directory
            import os

            self.output_dir = os.path.join(os.getcwd(), "polygon_measurements")

        self.root.quit()
        self.root.destroy()

    def _on_cancel(self):
        """Handle cancel button click."""
        self.images_dir = None
        self.labels_dir = None
        self.output_dir = None
        self.root.quit()
        self.root.destroy()

    def _show_error(self, message: str):
        """Show error message in status label."""
        self.status_label.config(
            text=message,
            fg="#ffffff",
            bg="#d32f2f",
        )
