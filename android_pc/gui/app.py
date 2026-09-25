"""
Android-Style Desktop GUI Launcher Application.
Uses CustomTkinter / Tkinter to render Material Design dark/light UI,
Android top status bar, search widget, desktop grid, app drawer, and folder popups.
"""

import sys
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from android_pc.core.config import LauncherConfig, AppShortcut, AndroidFolder, get_default_config_path
from android_pc.core.converter import PCAndroidConverter
from android_pc.core.launcher import AndroidLauncherEngine


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AndroidPCLauncherGUI(ctk.CTk):
    """Main application window for Android PC Launcher."""

    def __init__(self, config_path: str = None):
        super().__init__()

        self.config_path = config_path or get_default_config_path()
        self.config = LauncherConfig.load_from_file(self.config_path)

        # Populate default apps if empty
        if not self.config.apps:
            self._add_default_sample_apps()

        self.engine = AndroidLauncherEngine(self.config)
        self.converter = PCAndroidConverter(self.config)

        self.title("Android PC Launcher")
        self.geometry("1024x720")
        self.minsize(800, 600)

        self.configure(fg_color="#121212" if self.config.theme_mode == "dark" else "#F5F5F5")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_status_bar()
        self._build_top_bar()
        self._build_main_grid()
        self._build_dock()

        self._start_clock_timer()

    def _add_default_sample_apps(self):
        """Creates sample Android-style desktop apps for demonstration."""
        sample_apps = [
            AppShortcut("app_terminal", "Terminal", "com.pc.android.terminal", "x-terminal-emulator", "💻", category="System"),
            AppShortcut("app_browser", "Chrome Web", "com.pc.android.browser", "x-www-browser", "🌐", category="Internet"),
            AppShortcut("app_files", "Files", "com.pc.android.files", "xdg-open .", "📁", category="Utilities"),
            AppShortcut("app_calc", "Calculator", "com.pc.android.calc", "bc", "🔢", category="Utilities"),
            AppShortcut("app_notes", "Notes", "com.pc.android.notes", "gedit", "📝", category="Office"),
            AppShortcut("app_media", "Gallery", "com.pc.android.gallery", "eog", "🎨", category="Graphics"),
        ]
        self.config.apps.extend(sample_apps)

        # Create default folder
        system_folder = AndroidFolder(
            id="folder_sys",
            title="System Tools",
            app_ids=["app_terminal", "app_calc"],
            icon_symbol="📁"
        )
        self.config.folders.append(system_folder)
        self.config.dock_app_ids = ["app_browser", "app_files", "app_notes"]
        self.config.save_to_file(self.config_path)

    def _build_status_bar(self):
        """Android top status bar showing time, battery, wifi, and status icons."""
        self.status_bar = ctk.CTkFrame(self, height=30, fg_color="#1E1E1E", corner_radius=0)
        self.status_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # Left side: Android system label
        self.status_left = ctk.CTkLabel(self.status_bar, text=" Android PC", font=("Roboto", 12, "bold"), text_color="#3D5AFE")
        self.status_left.pack(side="left", padx=15)

        # Right side: System stats & clock
        self.clock_label = ctk.CTkLabel(self.status_bar, text="00:00 AM", font=("Roboto", 12, "bold"), text_color="#FFFFFF")
        self.clock_label.pack(side="right", padx=15)

        self.sys_icons = ctk.CTkLabel(self.status_bar, text="📶 🔋 100% ", font=("Roboto", 12), text_color="#AAAAAA")
        self.sys_icons.pack(side="right", padx=5)

    def _build_top_bar(self):
        """Android search widget and top options."""
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(15, 10))

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            self.top_frame,
            placeholder_text="🔍 Search apps or type command...",
            font=("Roboto", 14),
            height=40,
            corner_radius=20,
            fg_color="#2A2A2A",
            border_width=0
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_query_change)

        # Add Folder Button
        self.btn_add_folder = ctk.CTkButton(
            self.top_frame,
            text="+ Folder",
            width=90,
            height=40,
            corner_radius=20,
            fg_color="#3D5AFE",
            hover_color="#304FFE",
            command=self._on_add_folder_click
        )
        self.btn_add_folder.pack(side="right", padx=5)

        # Scan Folder Button
        self.btn_scan = ctk.CTkButton(
            self.top_frame,
            text="📂 Scan PC Folder",
            width=130,
            height=40,
            corner_radius=20,
            fg_color="#00C853",
            hover_color="#00E676",
            command=self._on_scan_folder_click
        )
        self.btn_scan.pack(side="right", padx=5)

    def _build_main_grid(self):
        """Scrollable grid displaying home screen apps and folders."""
        self.grid_scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.grid_scrollable.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.refresh_grid()

    def refresh_grid(self, search_query: str = ""):
        """Clears and re-renders desktop grid items."""
        for widget in self.grid_scrollable.winfo_children():
            widget.destroy()

        if search_query.strip():
            matched_apps = self.engine.search_apps(search_query)
            items = [{"type": "app", "data": app, "id": app.id, "name": app.name, "icon": app.icon_symbol} for app in matched_apps]
        else:
            items = self.engine.get_grid_items()

        cols = self.config.grid_columns
        for index, item in enumerate(items):
            row = index // cols
            col = index % cols

            card = ctk.CTkFrame(
                self.grid_scrollable,
                width=110,
                height=110,
                corner_radius=18,
                fg_color="#1E1E1E",
                border_width=1,
                border_color="#333333"
            )
            card.grid(row=row, column=col, padx=12, pady=12)
            card.grid_propagate(False)

            icon_lbl = ctk.CTkLabel(card, text=item["icon"], font=("Segoe UI Emoji", 36))
            icon_lbl.pack(pady=(12, 2))

            name_lbl = ctk.CTkLabel(card, text=item["name"], font=("Roboto", 11, "bold"), text_color="#EEEEEE")
            name_lbl.pack(pady=(0, 5))

            if item["type"] == "app":
                app_obj = item["data"]
                card.bind("<Button-1>", lambda e, a_id=app_obj.id: self._on_launch_app(a_id))
                icon_lbl.bind("<Button-1>", lambda e, a_id=app_obj.id: self._on_launch_app(a_id))
                name_lbl.bind("<Button-1>", lambda e, a_id=app_obj.id: self._on_launch_app(a_id))
            elif item["type"] == "folder":
                folder_obj = item["data"]
                card.bind("<Button-1>", lambda e, f_obj=folder_obj: self._open_folder_modal(f_obj))
                icon_lbl.bind("<Button-1>", lambda e, f_obj=folder_obj: self._open_folder_modal(f_obj))
                name_lbl.bind("<Button-1>", lambda e, f_obj=folder_obj: self._open_folder_modal(f_obj))

    def _build_dock(self):
        """Android desktop bottom dock panel."""
        self.dock_frame = ctk.CTkFrame(self, height=85, fg_color="#1A1A1A", corner_radius=25, border_width=1, border_color="#333333")
        self.dock_frame.grid(row=3, column=0, sticky="ew", padx=80, pady=(5, 15))

        self.refresh_dock()

    def refresh_dock(self):
        """Refreshes the pinned dock icons."""
        for widget in self.dock_frame.winfo_children():
            widget.destroy()

        dock_apps = self.engine.get_dock_apps()
        container = ctk.CTkFrame(self.dock_frame, fg_color="transparent")
        container.pack(expand=True)

        for app in dock_apps:
            btn = ctk.CTkButton(
                container,
                text=app.icon_symbol,
                font=("Segoe UI Emoji", 28),
                width=60,
                height=60,
                corner_radius=18,
                fg_color="#2A2A2A",
                hover_color="#3D5AFE",
                command=lambda a_id=app.id: self._on_launch_app(a_id)
            )
            btn.pack(side="left", padx=12, pady=10)

    def _start_clock_timer(self):
        """Updates status bar clock every second."""
        now = datetime.datetime.now().strftime("%I:%M %p")
        self.clock_label.configure(text=now)
        self.after(1000, self._start_clock_timer)

    def _on_search_query_change(self, event=None):
        query = self.search_entry.get()
        self.refresh_grid(search_query=query)

    def _on_launch_app(self, app_id: str):
        success, message = self.engine.launch_app(app_id)
        if not success:
            messagebox.showinfo("Android Launcher", message)

    def _open_folder_modal(self, folder: AndroidFolder):
        """Displays an Android modal dialog showing apps inside the folder."""
        popup = ctk.CTkToplevel(self)
        popup.title(folder.title)
        popup.geometry("400x350")
        popup.transient(self)
        popup.grab_set()

        title_lbl = ctk.CTkLabel(popup, text=f"📁 {folder.title}", font=("Roboto", 18, "bold"), text_color="#3D5AFE")
        title_lbl.pack(pady=15)

        folder_scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        folder_scroll.pack(fill="both", expand=True, padx=15, pady=10)

        folder_apps = [a for a in self.config.apps if a.id in folder.app_ids]
        if not folder_apps:
            empty_lbl = ctk.CTkLabel(folder_scroll, text="No apps in folder.", font=("Roboto", 12))
            empty_lbl.pack(pady=20)

        for app in folder_apps:
            item_frame = ctk.CTkFrame(folder_scroll, fg_color="#252525", corner_radius=10)
            item_frame.pack(fill="x", pady=5)

            btn = ctk.CTkButton(
                item_frame,
                text=f"{app.icon_symbol}  {app.name}",
                font=("Roboto", 14),
                anchor="w",
                fg_color="transparent",
                hover_color="#304FFE",
                command=lambda a_id=app.id: [popup.destroy(), self._on_launch_app(a_id)]
            )
            btn.pack(side="left", fill="x", expand=True, padx=10, pady=5)

    def _on_add_folder_click(self):
        """Dialog to create a new desktop folder."""
        dialog = ctk.CTkInputDialog(text="Enter folder name:", title="Create Android Folder")
        folder_name = dialog.get_input()
        if folder_name and folder_name.strip():
            self.engine.create_folder(folder_name.strip(), [])
            self.config.save_to_file(self.config_path)
            self.refresh_grid()

    def _on_scan_folder_click(self):
        """Converts a local folder into an Android Folder."""
        from tkinter import filedialog
        dir_path = filedialog.askdirectory(title="Select PC Folder to Convert to Android Folder")
        if dir_path:
            try:
                folder, apps = self.converter.scan_and_convert_directory(dir_path)
                for app in apps:
                    self.engine.register_app(app)
                self.config.folders.append(folder)
                self.config.save_to_file(self.config_path)
                self.refresh_grid()
                messagebox.showinfo("Success", f"Converted folder '{folder.title}' with {len(apps)} apps!")
            except Exception as e:
                messagebox.showerror("Error", str(e))


def run_launcher_gui(config_path: str = None):
    """Main launcher entrypoint."""
    app = AndroidPCLauncherGUI(config_path=config_path)
    app.mainloop()


if __name__ == "__main__":
    run_launcher_gui()
