# Cross-Platform-Folder-Picker

> A (near zero dependency by default) cross platform folder picker

[![Downloads](https://static.pepy.tech/badge/cross-platform-folder-picker)](https://pepy.tech/project/cross-platform-folder-picker) [![Pypi Badge](https://img.shields.io/pypi/v/cross-platform-folder-picker.svg)](https://pypi.org/project/cross-platform-folder-picker/)

![Example GIF](https://raw.githubusercontent.com/baseplate-admin/Cross-Platform-Folder-Picker/refs/heads/master/assets/example.gif)

# Features

-   Opens a folder dialog using:
    -   Default:
        -   `tkinter` for windows (falls back to `ctypes`)
        -   `zenity`/`kdialog` for linux
        -   `osascript` for macOS
    -   Optionally:
        -   `qt`
        -   `gtk`
-   Customize the title and icon of the dialog

# Installation

```shell
pip install cross-platform-folder-picker
```

# Usage

```python
from cross_platform_folder_picker import open_folder_picker

res = open_folder_picker()
```

# Roadmap

-   Investigate a better way to handle folder open dialog
-   Reduce dependency on tkinter on windows
