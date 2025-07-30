from ._abstract import AbstractFolderPicker


class QtFolderPicker(AbstractFolderPicker):
    def pick_folder(self, title="Select a folder", icon: str | None = None) -> str:
        try:
            from PySide6.QtWidgets import QApplication, QFileDialog  # type:ignore noqa: F401
            from PySide6.QtGui import QIcon  # type:ignore noqa: F401
            import sys
        except ImportError:
            raise ImportError(
                "PySide6 is required for the QtFolderPicker. "
                "Install with `pip install cross-platform-folder-picker[qt]`."
            )

        app = QApplication.instance()
        app_created = False
        if app is None:
            app = QApplication(sys.argv)
            app_created = True

        dialog = QFileDialog()
        dialog.setWindowTitle(title)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOptions(QFileDialog.Option.ShowDirsOnly)

        if icon:
            dialog.setWindowIcon(QIcon(icon))

        folder_path = ""
        if dialog.exec():
            folder_path = dialog.selectedFiles()[0]

        if app_created:
            app.quit()

        return folder_path
