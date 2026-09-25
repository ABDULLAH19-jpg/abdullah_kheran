"""
Command-Line Interface (CLI) for Android PC Converter & Launcher.
"""

import argparse
import sys
import json
from android_pc.core.config import LauncherConfig, get_default_config_path
from android_pc.core.converter import PCAndroidConverter
from android_pc.core.launcher import AndroidLauncherEngine


def main():
    parser = argparse.ArgumentParser(
        prog="android_pc",
        description="Android PC Suite: Convert your PC files/folders into Android-style apps and run launcher UI."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a directory and convert contents into Android apps and folder.")
    scan_parser.add_argument("path", help="Directory path to scan")
    scan_parser.add_argument("--save", action="store_true", help="Save converted structure directly to configuration file")
    scan_parser.add_argument("--config", default=get_default_config_path(), help="Path to config file")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert a single file or script into an Android app shortcut.")
    convert_parser.add_argument("file", help="File path to convert")
    convert_parser.add_argument("--name", help="Custom app name")
    convert_parser.add_argument("--save", action="store_true", help="Save to config")
    convert_parser.add_argument("--config", default=get_default_config_path(), help="Path to config file")

    # Launch command
    launch_parser = subparsers.add_parser("launch", help="Start the Android-style GUI launcher.")
    launch_parser.add_argument("--config", default=get_default_config_path(), help="Path to config file")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export an app as an Android Manifest / Package Specification.")
    export_parser.add_argument("app_id", help="App ID to export spec for")
    export_parser.add_argument("--config", default=get_default_config_path(), help="Path to config file")

    args = parser.parse_args()

    if not args.command or args.command == "launch":
        # Launch GUI
        try:
            from android_pc.gui.app import run_launcher_gui
            run_launcher_gui(args.config if hasattr(args, 'config') else get_default_config_path())
        except ImportError as e:
            print(f"Failed to launch GUI: {e}")
            sys.exit(1)
        return

    config_path = args.config
    config = LauncherConfig.load_from_file(config_path)
    converter = PCAndroidConverter(config)
    engine = AndroidLauncherEngine(config)

    if args.command == "scan":
        try:
            folder, apps = converter.scan_and_convert_directory(args.path)
            print(f"Successfully converted directory '{args.path}':")
            print(f" - Created Android Folder: '{folder.title}' (ID: {folder.id})")
            print(f" - Converted {len(apps)} Apps:")
            for app in apps:
                print(f"   * [{app.icon_symbol}] {app.name} ({app.package_name}) -> {app.exec_path}")
                engine.register_app(app)

            if args.save:
                engine.config.folders.append(folder)
                engine.config.save_to_file(config_path)
                print(f"Saved conversion layout to '{config_path}'")
        except Exception as e:
            print(f"Error scanning directory: {e}")
            sys.exit(1)

    elif args.command == "convert":
        try:
            app = converter.convert_file_to_app(args.file, custom_name=args.name)
            print(f"Converted file '{args.file}' to Android App:")
            print(f" - Name: {app.name}")
            print(f" - Package: {app.package_name}")
            print(f" - Exec Path: {app.exec_path}")
            print(f" - Category: {app.category}")

            if args.save:
                engine.register_app(app)
                engine.config.save_to_file(config_path)
                print(f"Saved app shortcut to '{config_path}'")
        except Exception as e:
            print(f"Error converting file: {e}")
            sys.exit(1)

    elif args.command == "export":
        app = next((a for a in config.apps if a.id == args.app_id or a.name.lower() == args.app_id.lower()), None)
        if not app:
            print(f"App '{args.app_id}' not found in configuration.")
            sys.exit(1)

        spec = converter.generate_android_manifest_spec(app)
        print(json.dumps(spec, indent=2))


if __name__ == "__main__":
    main()
