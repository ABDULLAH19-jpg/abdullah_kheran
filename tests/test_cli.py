"""
Unit tests for android_pc.cli.main
"""

import sys
import pytest
from unittest.mock import patch
from android_pc.cli.main import main


def test_cli_scan_command(tmp_path, capsys):
    scan_dir = tmp_path / "sample_folder"
    scan_dir.mkdir()
    (scan_dir / "app1.py").write_text("print('test')")

    config_file = tmp_path / "cfg.json"

    test_args = ["android_pc", "scan", str(scan_dir), "--save", "--config", str(config_file)]
    with patch.object(sys, "argv", test_args):
        main()

    captured = capsys.readouterr()
    assert "Successfully converted directory" in captured.out
    assert "Saved conversion layout to" in captured.out


def test_cli_convert_command(tmp_path, capsys):
    sample_file = tmp_path / "run.sh"
    sample_file.write_text("#!/bin/bash")
    config_file = tmp_path / "cfg.json"

    test_args = ["android_pc", "convert", str(sample_file), "--name", "Runner", "--save", "--config", str(config_file)]
    with patch.object(sys, "argv", test_args):
        main()

    captured = capsys.readouterr()
    assert "Converted file" in captured.out
    assert "Runner" in captured.out


def test_cli_export_command(tmp_path, capsys):
    config_file = tmp_path / "cfg.json"

    # First save an app
    sample_file = tmp_path / "run.sh"
    sample_file.write_text("#!/bin/bash")
    test_args1 = ["android_pc", "convert", str(sample_file), "--name", "RunnerApp", "--save", "--config", str(config_file)]
    with patch.object(sys, "argv", test_args1):
        main()

    # Now export
    test_args2 = ["android_pc", "export", "RunnerApp", "--config", str(config_file)]
    with patch.object(sys, "argv", test_args2):
        main()

    captured = capsys.readouterr()
    assert "manifest" in captured.out
    assert "com.pc.android.runnerapp" in captured.out
