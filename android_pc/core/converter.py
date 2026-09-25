"""
PC Desktop and Directory Converter module.
Converts local PC applications, .desktop shortcuts, executable files,
and folder hierarchies into Android-style apps and folders.
"""

import os
import re
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from android_pc.core.config import AppShortcut, AndroidFolder, LauncherConfig


CATEGORY_ICONS = {
    "Development": "💻",
    "Games": "🎮",
    "Graphics": "🎨",
    "Internet": "🌐",
    "Media": "🎬",
    "Office": "📄",
    "System": "⚙️",
    "Utilities": "🛠️",
    "Folder": "📁",
    "Default": "📱",
}


class PCAndroidConverter:
    """Converts local file paths, directories, and desktop entry files into Android launcher artifacts."""

    def __init__(self, config: Optional[LauncherConfig] = None):
        self.config = config or LauncherConfig()

    @staticmethod
    def sanitize_package_name(name: str) -> str:
        """Generates a valid Android package name format (com.pc.appname)."""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        if not clean_name:
            clean_name = "app" + str(uuid.uuid4())[:8]
        return f"com.pc.android.{clean_name}"

    def parse_desktop_file(self, filepath: str) -> Optional[AppShortcut]:
        """Parses a Linux .desktop shortcut file into an AppShortcut."""
        if not os.path.exists(filepath):
            return None

        name = None
        exec_cmd = None
        icon = None
        category = "Utilities"
        comment = ""

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                in_desktop_entry = False
                for line in f:
                    line = line.strip()
                    if line == "[Desktop Entry]":
                        in_desktop_entry = True
                        continue
                    elif line.startswith("[") and line != "[Desktop Entry]":
                        in_desktop_entry = False

                    if in_desktop_entry and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key == "Name" and not name:
                            name = value
                        elif key == "Exec" and not exec_cmd:
                            # Remove desktop spec field codes like %f, %u
                            exec_cmd = re.sub(r'%[a-zA-Z]', '', value).strip()
                        elif key == "Icon" and not icon:
                            icon = value
                        elif key == "Categories":
                            cats = value.split(";")
                            if cats and cats[0]:
                                category = cats[0]
                        elif key == "Comment" and not comment:
                            comment = value

            if not name or not exec_cmd:
                return None

            app_id = str(uuid.uuid4())[:8]
            pkg_name = self.sanitize_package_name(name)
            icon_symbol = CATEGORY_ICONS.get(category, CATEGORY_ICONS["Default"])

            return AppShortcut(
                id=app_id,
                name=name,
                package_name=pkg_name,
                exec_path=exec_cmd,
                icon_symbol=icon_symbol,
                icon_path=icon,
                category=category,
                description=comment,
                is_system_app=False,
            )
        except Exception:
            return None

    def convert_file_to_app(self, filepath: str, custom_name: Optional[str] = None) -> AppShortcut:
        """Converts an executable or arbitrary file into an Android App Shortcut."""
        path_obj = Path(filepath)
        app_name = custom_name or path_obj.stem.capitalize()
        app_id = str(uuid.uuid4())[:8]
        pkg_name = self.sanitize_package_name(app_name)

        ext = path_obj.suffix.lower()
        icon_symbol = CATEGORY_ICONS["Default"]
        category = "Utilities"

        if ext in [".py", ".sh", ".bash", ".exe", ".bin"]:
            category = "System"
            icon_symbol = CATEGORY_ICONS["System"]
        elif ext in [".png", ".jpg", ".jpeg", ".svg"]:
            category = "Graphics"
            icon_symbol = CATEGORY_ICONS["Graphics"]
        elif ext in [".mp4", ".mkv", ".mp3", ".wav"]:
            category = "Media"
            icon_symbol = CATEGORY_ICONS["Media"]

        return AppShortcut(
            id=app_id,
            name=app_name,
            package_name=pkg_name,
            exec_path=str(path_obj.resolve()),
            icon_symbol=icon_symbol,
            category=category,
            description=f"Converted file: {path_obj.name}",
        )

    def scan_and_convert_directory(self, dir_path: str) -> Tuple[AndroidFolder, List[AppShortcut]]:
        """
        Scans a directory on the PC and converts all contained files/executables
        into Android App Shortcuts grouped into a single AndroidFolder.
        """
        dir_obj = Path(dir_path)
        if not dir_obj.exists() or not dir_obj.is_dir():
            raise ValueError(f"Directory '{dir_path}' does not exist or is not a valid directory.")

        folder_id = str(uuid.uuid4())[:8]
        folder_title = dir_obj.name.capitalize()
        converted_apps: List[AppShortcut] = []

        for entry in os.listdir(dir_path):
            full_path = dir_obj / entry
            if full_path.is_file() and not entry.startswith("."):
                if entry.endswith(".desktop"):
                    app = self.parse_desktop_file(str(full_path))
                    if app:
                        converted_apps.append(app)
                else:
                    app = self.convert_file_to_app(str(full_path))
                    converted_apps.append(app)

        app_ids = [app.id for app in converted_apps]
        android_folder = AndroidFolder(
            id=folder_id,
            title=folder_title,
            app_ids=app_ids,
            icon_symbol=CATEGORY_ICONS["Folder"],
        )

        return android_folder, converted_apps

    def generate_android_manifest_spec(self, app: AppShortcut) -> Dict[str, Any]:
        """Generates an Android Manifest / Package Spec representation for export."""
        return {
            "manifest": {
                "package": app.package_name,
                "versionCode": 1,
                "versionName": "1.0.0",
                "application": {
                    "label": app.name,
                    "icon": app.icon_symbol,
                    "category": app.category,
                    "executable": app.exec_path,
                },
            }
        }
