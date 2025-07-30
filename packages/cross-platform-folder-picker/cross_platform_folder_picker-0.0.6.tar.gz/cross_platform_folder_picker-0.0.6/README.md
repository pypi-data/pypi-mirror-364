# Cross-Platform-Folder-Picker

> A (near zero dependency by default) cross platform folder picker

[![Downloads](https://static.pepy.tech/badge/cross-platform-folder-picker)](https://pepy.tech/project/cross-platform-folder-picker) [![Pypi Badge](https://img.shields.io/pypi/v/cross-platform-folder-picker.svg)](https://pypi.org/project/cross-platform-folder-picker/)

![Example GIF](https://raw.githubusercontent.com/baseplate-admin/Cross-Platform-Folder-Picker/refs/heads/master/assets/example.gif)

# Features

- Opens a folder dialog using:
  - Default:
    - `tkinter` for Windows (falls back to `ctypes`)
    - `zenity` / `kdialog` for Linux
    - `osascript` for macOS
  - Optionally:
    - `qt`
    - `gtk`
- Customize the dialog’s title and icon easily  
- Uses native dialogs where possible for a familiar look & feel  
- Falls back gracefully if native options aren’t available  
- Super simple to use in scripts, CLI tools, or GUI apps

# Installation

```shell
pip install cross-platform-folder-picker
```

# Usage

```python
from cross_platform_folder_picker import open_folder_picker

folder = open_folder_picker()
print(folder)  # Prints the selected folder path, or None if you cancel
```

# Roadmap

- Let me know what features or improvements you'd like to see next!
