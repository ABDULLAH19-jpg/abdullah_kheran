# 🤖 Android PC Suite & Launcher

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-clean-green.svg)]()

> **Transform your Linux / Desktop PC into a modern, sleek Android-style experience.**
> Convert PC directories, scripts, and desktop applications into Android-like apps and expandable folder widgets.

---

## 🌟 Key Features

- 📱 **Android Material Launcher UI**: Modern Android-style home screen with rounded app cards, status bar (live clock, WiFi, battery), top search widget, and bottom dock.
- 📁 **Folder Conversion Engine**: Turn any directory or folder hierarchy on your PC into an Android-style app group modal with a single click or CLI command.
- ⚙️ **Automatic App Packaging**: Parses Linux `.desktop` files, binary scripts (`.sh`, `.py`), and executables into Android package specifications (`com.pc.android.<app>`).
- 🔍 **Instant Search & Drawer**: Search through all installed applications by name, description, or category.
- 💾 **Persistent Workspace Layout**: Customizes and saves your desktop configuration, dark/light themes, icon layouts, and dock items in `~/.android_pc/config.json`.
- 🛠️ **Full CLI & Python API**: Perform automated folder scans, single-file conversions, and package manifest exports right from the command line.

---

## 🖥️ Graphical User Interface Preview

```
+-------------------------------------------------------------------------------+
|  🤖 Android PC                       📶 🔋 100%                   10:45 AM    |
+-------------------------------------------------------------------------------+
|  [ 🔍 Search apps or type command... ]  [+ Folder]  [📂 Scan PC Folder]       |
+-------------------------------------------------------------------------------+
|                                                                               |
|   +-----------+     +-----------+     +-----------+     +-----------+         |
|   |    📁     |     |    🌐     |     |    💻     |     |    📝     |         |
|   |  System   |     |  Chrome   |     | Terminal  |     |   Notes   |         |
|   +-----------+     +-----------+     +-----------+     +-----------+         |
|                                                                               |
|   +-----------+     +-----------+                                             |
|   |    🎨     |     |    🔢     |                                             |
|   |  Gallery  |     |  Calc     |                                             |
|   +-----------+     +-----------+                                             |
|                                                                               |
+-------------------------------------------------------------------------------+
|               ( 🌐 Browser )  ( 📁 Files )  ( 📝 Notes )                      |
+-------------------------------------------------------------------------------+
```

---

## 📐 Architecture Overview

```
android_pc/
├── core/
│   ├── config.py       # Dataclass models (AppShortcut, AndroidFolder, LauncherConfig)
│   ├── converter.py    # Desktop file parser, directory converter & Android manifest spec
│   └── launcher.py     # Grid layout manager, app launcher engine & search filter
├── gui/
│   └── app.py          # CustomTkinter Material Design Launcher GUI
├── cli/
│   └── main.py         # Command-line interface parser and runner
└── __main__.py         # Package entry point
```

---

## 🚀 Quick Start & Installation

### Prerequisites

- Python 3.8 or higher
- `customtkinter` and `Pillow`

### Installation

Clone the repository and install requirements:

```bash
git clone https://github.com/your-username/android-pc-launcher.git
cd android-pc-launcher
pip install -r requirements.txt
```

*Optionally create `requirements.txt`:*
```bash
pip install customtkinter pillow pytest
```

---

## 💻 CLI Usage Guide

### 1. Launch GUI Interface
```bash
python3 -m android_pc launch
```

### 2. Scan & Convert a PC Directory into an Android Folder
Converts all files/executables in `/path/to/folder` into an Android folder with app shortcuts:
```bash
python3 -m android_pc scan /path/to/folder --save
```

### 3. Convert a Single Executable / Script
Convert a local script or executable into an Android-style app shortcut:
```bash
python3 -m android_pc convert /usr/bin/python3 --name "Python Runtime" --save
```

### 4. Export App Android Package Spec
Export JSON Android Manifest metadata for any registered app:
```bash
python3 -m android_pc export "Python Runtime"
```

Output:
```json
{
  "manifest": {
    "package": "com.pc.android.pythonruntime",
    "versionCode": 1,
    "versionName": "1.0.0",
    "application": {
      "label": "Python Runtime",
      "icon": "📱",
      "category": "System",
      "executable": "/usr/bin/python3"
    }
  }
}
```

---

## 🧪 Running Unit Tests

Run the full automated test suite using `pytest`:

```bash
PYTHONPATH=. pytest -v
```

All core functionality (config serialization, folder scanning, launcher grid calculations, search filtering, and CLI commands) is covered by comprehensive unit tests.

---

## 🤝 Contributing

Contributions are very welcome! Please feel free to open issues, submit Pull Requests, or suggest new features.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
