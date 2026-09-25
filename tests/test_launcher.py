"""
Unit tests for android_pc.core.launcher
"""

import pytest
from android_pc.core.config import LauncherConfig, AppShortcut, AndroidFolder
from android_pc.core.launcher import AndroidLauncherEngine


@pytest.fixture
def sample_engine():
    config = LauncherConfig()
    app1 = AppShortcut("a1", "Chrome", "com.browser", "google-chrome", "🌐", category="Internet")
    app2 = AppShortcut("a2", "Terminal", "com.terminal", "bash", "💻", category="System")
    app3 = AppShortcut("a3", "Calculator", "com.calc", "bc", "🔢", category="Utilities")

    folder1 = AndroidFolder("f1", "Tools", ["a2", "a3"])

    config.apps = [app1, app2, app3]
    config.folders = [folder1]
    config.dock_app_ids = ["a1"]

    return AndroidLauncherEngine(config)


def test_register_and_unregister_app(sample_engine):
    new_app = AppShortcut("a4", "GIMP", "com.gimp", "gimp", "🎨", category="Graphics")
    sample_engine.register_app(new_app, add_to_dock=True)

    assert len(sample_engine.config.apps) == 4
    assert "a4" in sample_engine.config.dock_app_ids

    sample_engine.unregister_app("a4")
    assert len(sample_engine.config.apps) == 3
    assert "a4" not in sample_engine.config.dock_app_ids


def test_folder_management(sample_engine):
    folder = sample_engine.create_folder("Work", ["a1"])
    assert len(sample_engine.config.folders) == 2
    assert folder.title == "Work"

    success = sample_engine.add_app_to_folder(folder.id, "a2")
    assert success is True
    assert "a2" in folder.app_ids

    remove_success = sample_engine.remove_app_from_folder(folder.id, "a1")
    assert remove_success is True
    assert "a1" not in folder.app_ids

    sample_engine.remove_folder(folder.id)
    assert len(sample_engine.config.folders) == 1


def test_search_apps(sample_engine):
    results = sample_engine.search_apps("Chrome")
    assert len(results) == 1
    assert results[0].id == "a1"

    cat_results = sample_engine.search_apps("Internet")
    assert len(cat_results) == 1

    empty_results = sample_engine.search_apps("nonexistent")
    assert len(empty_results) == 0


def test_get_grid_items(sample_engine):
    items = sample_engine.get_grid_items()
    # f1 folder contains a2 and a3, so grid items should be 1 folder (f1) and 1 standalone app (a1)
    assert len(items) == 2
    types = [item["type"] for item in items]
    assert "folder" in types
    assert "app" in types


def test_get_dock_apps(sample_engine):
    dock = sample_engine.get_dock_apps()
    assert len(dock) == 1
    assert dock[0].name == "Chrome"


def test_launch_app_not_found(sample_engine):
    success, msg = sample_engine.launch_app("nonexistent_id")
    assert success is False
    assert "not found" in msg
