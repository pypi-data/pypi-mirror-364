from ._abstract import AbstractFolderPicker


class GtkFolderPicker(AbstractFolderPicker):
    def pick_folder(
        self, title="Select a folder", icon: str | None = None
    ) -> str | None:
        try:
            import gi  # type:ignore noqa: F401

            gi.require_version("Gtk", "4.0")
            from gi.repository import Gtk  # type:ignore noqa: F401
        except (ImportError, ValueError):
            raise ImportError(
                "GTK 4 is required for GtkFolderPicker.\n"
                "Install GTK 4 and PyGObject:\n"
                "  Linux: sudo apt install libgtk-4-dev gir1.2-gtk-4.0\n"
                "  pip install PyGObject\n"
                "  Windows: use MSYS2 and install gtk4, pygobject"
            )

        # Optional Libadwaita support on Linux
        use_adw = False
        try:
            gi.require_version("Adw", "1")
            from gi.repository import Adw  # type:ignore noqa: F401

            use_adw = True
        except (ImportError, ValueError):
            pass  # Libadwaita not available — use plain GTK

        folder_path = ""

        def choose_folder():
            chooser = Gtk.FileChooserNative.new(
                title,
                None,
                Gtk.FileChooserAction.SELECT_FOLDER,
                "_Open",
                "_Cancel",
            )

            if icon:
                try:
                    chooser.set_icon_name(icon)
                except Exception:
                    pass  # Ignore icon issues

            response = chooser.run()
            if response == Gtk.ResponseType.ACCEPT:
                file = chooser.get_file()
                return file.get_path() if file else ""
            return ""

        if use_adw:

            class App(Adw.Application):
                def __init__(self):
                    super().__init__(application_id="com.example.folderpicker")
                    self.result = ""

                def do_activate(self):
                    Adw.ApplicationWindow(application=self)
                    self.result = choose_folder()
                    self.quit()

            app = App()
            app.run([])
            folder_path = app.result

        else:

            class App(Gtk.Application):
                def __init__(self):
                    super().__init__(application_id="com.example.folderpicker")
                    self.result = ""

                def do_activate(self):
                    self.result = choose_folder()
                    self.quit()

            app = App()
            app.run([])
            folder_path = app.result

        return folder_path
