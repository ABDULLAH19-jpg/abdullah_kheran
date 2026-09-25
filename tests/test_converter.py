"""
Unit tests for android_pc.core.converter
"""

import os
import pytest
from pathlib import Path
from android_pc.core.converter import PCAndroidConverter
from android_pc.core.config import LauncherConfig


def test_sanitize_package_name():
    pkg = PCAndroidConverter.sanitize_package_name("My Custom App 123!")
    assert pkg == "com.pc.android.mycustomapp123"

    empty_pkg = PCAndroidConverter.sanitize_package_name("!@#$%^")
    assert empty_pkg.startswith("com.pc.android.app")


def test_convert_file_to_app(tmp_path):
    script_file = tmp_path / "myscript.sh"
    script_file.write_text("#!/bin/bash\necho 'hello'")

    converter = PCAndroidConverter()
    app = converter.convert_file_to_app(str(script_file), custom_name="My Shell Script")

    assert app.name == "My Shell Script"
    assert app.category == "System"
    assert app.exec_path == str(script_file.resolve())


def test_parse_desktop_file(tmp_path):
    desktop_file = tmp_path / "test_app.desktop"
    content = """[Desktop Entry]
Name=Test Browser
Exec=test-browser %u
Icon=browser-icon
Categories=Internet;WebBrowser;
Comment=Fast web browser
"""
    desktop_file.write_text(content)

    converter = PCAndroidConverter()
    app = converter.parse_desktop_file(str(desktop_file))

    assert app is not None
    assert app.name == "Test Browser"
    assert app.exec_path == "test-browser"
    assert app.category == "Internet"
    assert app.icon_symbol == "🌐"


def test_scan_and_convert_directory(tmp_path):
    dir_to_scan = tmp_path / "ProjectDir"
    dir_to_scan.mkdir()

    f1 = dir_to_scan / "main.py"
    f1.write_text("print('hello')")

    f2 = dir_to_scan / "readme.txt"
    f2.write_text("info")

    converter = PCAndroidConverter()
    folder, apps = converter.scan_and_convert_directory(str(dir_to_scan))

    assert folder.title == "Projectdir"
    assert len(apps) == 2
    assert len(folder.app_ids) == 2


def test_generate_android_manifest_spec():
    converter = PCAndroidConverter()
    app = converter.convert_file_to_app("/usr/bin/python3", custom_name="Python Executable")
    spec = converter.generate_android_manifest_spec(app)

    assert "manifest" in spec
    assert spec["manifest"]["package"] == app.package_name
    assert spec["manifest"]["application"]["label"] == "Python Executable"
