import sys

try:
    import PySide6  # type: ignore  # noqa: F401

    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
try:
    import gi  # type: ignore  # noqa: F401

    HAS_GI = True
except ImportError:
    gi = None
    HAS_GI = False


def open_folder_picker():
    """
    Opens a folder picker dialog and returns the selected folder path.

    Returns:
        str: The path of the selected folder.
    """

    if HAS_PYSIDE6:
        from .bases import QtFolderPicker

        picker = QtFolderPicker()
    elif HAS_GI:
        from .bases import GtkFolderPicker

        picker = GtkFolderPicker()
    else:
        match sys.platform:
            case "win32":
                try:
                    import tkinter  # type: ignore  # noqa: F401
                    from .bases import TkinterFolderPicker

                    picker = TkinterFolderPicker()
                except ImportError:
                    from .bases import WindowsFolderPicker

                    picker = WindowsFolderPicker()
            case "darwin":
                from .bases import MacOSFolderPicker

                picker = MacOSFolderPicker()
            case "linux":
                from .bases import LinuxFolderPicker

                picker = LinuxFolderPicker()
            case _:
                raise NotImplementedError(f"Unsupported platform: {sys.platform}")

    return picker.pick_folder()
