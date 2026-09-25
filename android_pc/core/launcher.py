"""
Android Launcher Engine managing grid layouts, folder popups,
app search, dock items, and application execution.
"""

import subprocess
import shlex
import os
from typing import List, Dict, Optional, Tuple, Any
from android_pc.core.config import LauncherConfig, AppShortcut, AndroidFolder


class AndroidLauncherEngine:
    """Core launcher manager that coordinates apps, folders, and layout logic."""

    def __init__(self, config: Optional[LauncherConfig] = None):
        self.config = config or LauncherConfig()

    def register_app(self, app: AppShortcut, add_to_dock: bool = False) -> None:
        """Registers a new application shortcut into launcher."""
        existing_index = next((i for i, a in enumerate(self.config.apps) if a.id == app.id), None)
        if existing_index is not None:
            self.config.apps[existing_index] = app
        else:
            self.config.apps.append(app)

        if add_to_dock and app.id not in self.config.dock_app_ids:
            self.config.dock_app_ids.append(app.id)

    def unregister_app(self, app_id: str) -> None:
        """Removes an application shortcut from launcher, dock, and folders."""
        self.config.apps = [a for a in self.config.apps if a.id != app_id]
        if app_id in self.config.dock_app_ids:
            self.config.dock_app_ids.remove(app_id)
        for folder in self.config.folders:
            if app_id in folder.app_ids:
                folder.app_ids.remove(app_id)

    def create_folder(self, title: str, app_ids: List[str]) -> AndroidFolder:
        """Creates an Android-style folder combining multiple apps."""
        import uuid
        folder = AndroidFolder(
            id=str(uuid.uuid4())[:8],
            title=title,
            app_ids=list(app_ids)
        )
        self.config.folders.append(folder)
        return folder

    def remove_folder(self, folder_id: str) -> None:
        """Deletes an Android folder without deleting the underlying apps."""
        self.config.folders = [f for f in self.config.folders if f.id != folder_id]

    def add_app_to_folder(self, folder_id: str, app_id: str) -> bool:
        """Adds an app to an existing folder."""
        for folder in self.config.folders:
            if folder.id == folder_id:
                if app_id not in folder.app_ids:
                    folder.app_ids.append(app_id)
                return True
        return False

    def remove_app_from_folder(self, folder_id: str, app_id: str) -> bool:
        """Removes an app from a folder."""
        for folder in self.config.folders:
            if folder.id == folder_id:
                if app_id in folder.app_ids:
                    folder.app_ids.remove(app_id)
                    return True
        return False

    def search_apps(self, query: str) -> List[AppShortcut]:
        """Filters registered applications by name or category matching the search query."""
        if not query.strip():
            return self.config.apps
        q = query.lower().strip()
        return [
            app for app in self.config.apps
            if q in app.name.lower() or q in app.category.lower() or q in app.description.lower()
        ]

    def get_grid_items(self) -> List[Dict[str, Any]]:
        """
        Returns grid items (standalone apps and folders) for display on the home screen.
        Apps inside folders are excluded from top-level home screen grid.
        """
        apps_in_folders = set()
        for folder in self.config.folders:
            apps_in_folders.update(folder.app_ids)

        items = []
        # Add standalone folders
        for folder in self.config.folders:
            items.append({
                "type": "folder",
                "data": folder,
                "id": folder.id,
                "name": folder.title,
                "icon": folder.icon_symbol,
            })

        # Add standalone apps
        for app in self.config.apps:
            if app.id not in apps_in_folders:
                items.append({
                    "type": "app",
                    "data": app,
                    "id": app.id,
                    "name": app.name,
                    "icon": app.icon_symbol,
                })

        return items

    def get_dock_apps(self) -> List[AppShortcut]:
        """Returns the list of AppShortcut objects currently placed in the dock."""
        dock_dict = {app.id: app for app in self.config.apps}
        return [dock_dict[app_id] for app_id in self.config.dock_app_ids if app_id in dock_dict]

    def launch_app(self, app_id: str) -> Tuple[bool, str]:
        """
        Executes the PC application corresponding to the given app_id.
        Returns a tuple of (success_boolean, message_string).
        """
        app = next((a for a in self.config.apps if a.id == app_id), None)
        if not app:
            return False, f"App with ID '{app_id}' not found."

        try:
            exec_cmd = app.exec_path
            if not exec_cmd:
                return False, "No executable path configured for this app."

            if os.path.exists(exec_cmd) and not os.access(exec_cmd, os.X_OK):
                subprocess.Popen(["xdg-open", exec_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                args = shlex.split(exec_cmd)
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            return True, f"Launched {app.name} successfully."
        except Exception as e:
            return False, f"Failed to launch {app.name}: {str(e)}"
