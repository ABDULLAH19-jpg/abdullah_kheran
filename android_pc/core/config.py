"""
Core configuration models and persistent storage manager for Android PC Launcher.
"""

from dataclasses import dataclass, field, asdict
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class AppShortcut:
    """Represents an application shortcut converted into Android app style."""
    id: str
    name: str
    package_name: str
    exec_path: str
    icon_symbol: str = "📱"
    icon_path: Optional[str] = None
    category: str = "Utilities"
    description: str = ""
    is_system_app: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppShortcut":
        return cls(**data)


@dataclass
class AndroidFolder:
    """Represents an Android-style desktop folder containing apps."""
    id: str
    title: str
    app_ids: List[str] = field(default_factory=list)
    icon_symbol: str = "📁"
    color_accent: str = "#3D5AFE"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AndroidFolder":
        return cls(**data)


@dataclass
class LauncherConfig:
    """Global configuration settings for the Android PC Launcher."""
    theme_mode: str = "dark"  # dark or light
    grid_columns: int = 5
    grid_rows: int = 4
    wallpaper_color: str = "#121212"
    accent_color: str = "#6200EE"
    enable_dock: bool = True
    dock_app_ids: List[str] = field(default_factory=list)
    apps: List[AppShortcut] = field(default_factory=list)
    folders: List[AndroidFolder] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theme_mode": self.theme_mode,
            "grid_columns": self.grid_columns,
            "grid_rows": self.grid_rows,
            "wallpaper_color": self.wallpaper_color,
            "accent_color": self.accent_color,
            "enable_dock": self.enable_dock,
            "dock_app_ids": self.dock_app_ids,
            "apps": [app.to_dict() for app in self.apps],
            "folders": [folder.to_dict() for folder in self.folders],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LauncherConfig":
        data_copy = dict(data)
        apps_data = data_copy.pop("apps", [])
        folders_data = data_copy.pop("folders", [])

        apps = [AppShortcut.from_dict(app) for app in apps_data]
        folders = [AndroidFolder.from_dict(folder) for folder in folders_data]

        return cls(apps=apps, folders=folders, **data_copy)

    def save_to_file(self, path: str) -> None:
        """Saves current launcher configuration to a JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, path: str) -> "LauncherConfig":
        """Loads launcher configuration from a JSON file."""
        if not os.path.exists(path):
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


def get_default_config_path() -> str:
    """Returns the default user configuration file path."""
    home = Path.home()
    return str(home / ".android_pc" / "config.json")
