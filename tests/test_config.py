"""
Unit tests for android_pc.core.config
"""

import os
import json
import pytest
from android_pc.core.config import LauncherConfig, AppShortcut, AndroidFolder, get_default_config_path


def test_app_shortcut_dataclass():
    app = AppShortcut(
        id="app1",
        name="Test App",
        package_name="com.pc.test",
        exec_path="/usr/bin/testapp",
        icon_symbol="🎮",
        category="Games"
    )
    assert app.id == "app1"
    assert app.name == "Test App"
    assert app.package_name == "com.pc.test"

    app_dict = app.to_dict()
    assert app_dict["id"] == "app1"
    assert app_dict["category"] == "Games"

    reconstructed = AppShortcut.from_dict(app_dict)
    assert reconstructed.id == app.id
    assert reconstructed.name == app.name


def test_android_folder_dataclass():
    folder = AndroidFolder(
        id="fold1",
        title="Games Folder",
        app_ids=["app1", "app2"],
        icon_symbol="📁"
    )
    assert folder.id == "fold1"
    assert len(folder.app_ids) == 2

    folder_dict = folder.to_dict()
    reconstructed = AndroidFolder.from_dict(folder_dict)
    assert reconstructed.title == "Games Folder"
    assert reconstructed.app_ids == ["app1", "app2"]


def test_launcher_config_serialization(tmp_path):
    config = LauncherConfig(
        theme_mode="light",
        grid_columns=6,
        grid_rows=5,
        dock_app_ids=["app1"]
    )
    app = AppShortcut("app1", "App 1", "com.app.one", "/bin/app1")
    folder = AndroidFolder("f1", "Folder 1", ["app1"])
    config.apps.append(app)
    config.folders.append(folder)

    config_file = tmp_path / "test_config.json"
    config.save_to_file(str(config_file))

    assert os.path.exists(config_file)

    loaded_config = LauncherConfig.load_from_file(str(config_file))
    assert loaded_config.theme_mode == "light"
    assert loaded_config.grid_columns == 6
    assert len(loaded_config.apps) == 1
    assert loaded_config.apps[0].name == "App 1"
    assert len(loaded_config.folders) == 1
    assert loaded_config.folders[0].title == "Folder 1"


def test_default_config_path():
    path = get_default_config_path()
    assert ".android_pc" in path
    assert path.endswith("config.json")
