from ._abstract import AbstractFolderPicker

import ctypes
from ctypes import wintypes, POINTER, byref, cast, c_void_p, c_wchar_p

# Load the required Windows DLLs for COM and Shell functions
ole32 = ctypes.OleDLL("ole32")  # For COM initialization and memory management
shell32 = ctypes.WinDLL("shell32")  # Shell API (loaded here but not used directly)


class GUID(ctypes.Structure):
    """
    Represents a Windows GUID (Globally Unique Identifier) structure.
    Used to identify COM classes and interfaces.

    The constructor accepts a GUID string (e.g. "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}")
    and initializes the structure accordingly.
    """

    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, guid_str):
        # Convert the string form of a GUID into its binary representation
        super().__init__()
        ole32.CLSIDFromString(ctypes.c_wchar_p(guid_str), byref(self))


def check_hresult(hr):
    """
    Simple helper that raises a Windows error if the HRESULT indicates failure.
    """
    if hr != 0:
        # Pass plain int to WinError to satisfy type checker
        raise ctypes.WinError(int(hr))


class IUnknown(ctypes.Structure):
    """
    Base COM interface from which other COM interfaces inherit.
    Contains three fundamental methods: QueryInterface, AddRef, and Release.
    """

    pass


LPUNKNOWN = POINTER(IUnknown)

IUnknown._fields_ = [("lpVtbl", POINTER(ctypes.c_void_p))]


class IUnknownVTable(ctypes.Structure):
    """
    Defines the vtable (virtual method table) layout for the IUnknown interface.
    """

    _fields_ = [
        (
            "QueryInterface",
            ctypes.WINFUNCTYPE(
                ctypes.HRESULT, POINTER(IUnknown), POINTER(GUID), POINTER(c_void_p)
            ),
        ),
        ("AddRef", ctypes.WINFUNCTYPE(ctypes.c_ulong, POINTER(IUnknown))),
        ("Release", ctypes.WINFUNCTYPE(ctypes.c_ulong, POINTER(IUnknown))),
    ]


# Note: Removed invalid assignment to IUnknown.lpVtbl


# CLSID and IID for the File Open Dialog COM object/interface
CLSID_FileOpenDialog = GUID("{DC1C5A9C-E88A-4DDE-A5A1-60F82A20AEF7}")
IID_IFileOpenDialog = GUID("{D57C7288-D4AD-4768-BE02-9D969532D960}")

# Constants for dialog options
SIGDN_FILESYSPATH = (
    0x80058000  # Use to get the full file system path from an IShellItem
)
FOS_PICKFOLDERS = 0x00000020  # Flag to indicate folder selection dialog

# HRESULT code when user cancels the dialog
ERROR_CANCELLED = -2147023673


class IFileOpenDialog(ctypes.Structure):
    """
    COM interface for the File Open Dialog.
    Extends IUnknown with methods to configure and show the dialog, then get the user's selection.
    """

    pass


LPFILEOPENDIALOG = POINTER(IFileOpenDialog)


# Function prototypes for important IFileOpenDialog methods
ShowFunc = ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, wintypes.HWND)
SetOptionsFunc = ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, ctypes.c_ulong)
GetOptionsFunc = ctypes.WINFUNCTYPE(
    ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(ctypes.c_ulong)
)
GetResultFunc = ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(c_void_p))


# IShellItem interface and related constants
IID_IShellItem = GUID("{43826D1E-E718-42EE-BC55-A1E261C37BFE}")


class IShellItem(ctypes.Structure):
    """
    Represents a Shell item, such as a file or folder, returned from the dialog.
    Used here mainly to retrieve the selected folder's path.
    """

    pass


LPSHELLITEM = POINTER(IShellItem)

GetDisplayNameFunc = ctypes.WINFUNCTYPE(
    ctypes.HRESULT, LPSHELLITEM, ctypes.c_ulong, POINTER(c_wchar_p)
)


class IFileOpenDialogVtbl(ctypes.Structure):
    """
    Virtual method table for the IFileOpenDialog interface.
    Contains all the COM methods accessible on the dialog object.
    """

    _fields_ = [
        # IUnknown methods
        (
            "QueryInterface",
            ctypes.WINFUNCTYPE(
                ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(GUID), POINTER(c_void_p)
            ),
        ),
        ("AddRef", ctypes.WINFUNCTYPE(ctypes.c_ulong, LPFILEOPENDIALOG)),
        ("Release", ctypes.WINFUNCTYPE(ctypes.c_ulong, LPFILEOPENDIALOG)),
        # IModalWindow
        ("Show", ShowFunc),
        # IFileDialog methods
        (
            "SetFileTypes",
            ctypes.WINFUNCTYPE(
                ctypes.HRESULT, LPFILEOPENDIALOG, ctypes.c_uint, POINTER(c_void_p)
            ),
        ),
        (
            "SetFileTypeIndex",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, ctypes.c_uint),
        ),
        (
            "GetFileTypeIndex",
            ctypes.WINFUNCTYPE(
                ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(ctypes.c_uint)
            ),
        ),
        (
            "Advise",
            ctypes.WINFUNCTYPE(
                ctypes.HRESULT, LPFILEOPENDIALOG, c_void_p, POINTER(ctypes.c_ulong)
            ),
        ),
        (
            "Unadvise",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, ctypes.c_ulong),
        ),
        ("SetOptions", SetOptionsFunc),
        ("GetOptions", GetOptionsFunc),
        (
            "SetDefaultFolder",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, LPSHELLITEM),
        ),
        (
            "SetFolder",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, LPSHELLITEM),
        ),
        (
            "GetFolder",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(LPSHELLITEM)),
        ),
        (
            "GetCurrentSelection",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(LPSHELLITEM)),
        ),
        (
            "SetFileName",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, c_wchar_p),
        ),
        (
            "GetFileName",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(c_wchar_p)),
        ),
        ("SetTitle", ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, c_wchar_p)),
        (
            "SetOkButtonLabel",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, c_wchar_p),
        ),
        (
            "SetFileNameLabel",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, c_wchar_p),
        ),
        ("GetResult", GetResultFunc),
    ]


IFileOpenDialog._fields_ = [("lpVtbl", POINTER(IFileOpenDialogVtbl))]


class IShellItemVtbl(ctypes.Structure):
    """
    Virtual method table for the IShellItem interface.
    Allows querying information about the selected item.
    """

    _fields_ = [
        # IUnknown methods
        (
            "QueryInterface",
            ctypes.WINFUNCTYPE(
                ctypes.HRESULT, LPSHELLITEM, POINTER(GUID), POINTER(c_void_p)
            ),
        ),
        ("AddRef", ctypes.WINFUNCTYPE(ctypes.c_ulong, LPSHELLITEM)),
        ("Release", ctypes.WINFUNCTYPE(ctypes.c_ulong, LPSHELLITEM)),
        # IShellItem-specific methods
        (
            "BindToHandler",
            ctypes.WINFUNCTYPE(
                ctypes.HRESULT, LPSHELLITEM, c_void_p, POINTER(GUID), POINTER(c_void_p)
            ),
        ),
        (
            "GetParent",
            ctypes.WINFUNCTYPE(ctypes.HRESULT, LPSHELLITEM, POINTER(LPSHELLITEM)),
        ),
        ("GetDisplayName", GetDisplayNameFunc),
    ]


IShellItem._fields_ = [("lpVtbl", POINTER(IShellItemVtbl))]


class WindowsFolderPicker(AbstractFolderPicker):
    """
    Windows implementation of a folder picker dialog using COM's IFileOpenDialog.

    Opens the standard Windows folder selection dialog and returns
    the path of the folder selected by the user, or None if cancelled.

    Parameters:
        title (str): Dialog window title (default: "Select a folder")
        icon (str|None): Unused here, but could be used to specify a custom icon

    Returns:
        str or None: The full path to the selected folder, or None if the user cancels.
    """

    def pick_folder(
        self, title="Select a folder", icon: str | None = None
    ) -> str | None:
        # Initialize COM library on this thread
        ole32.CoInitialize(None)

        pDialog = c_void_p()

        # Create an instance of the FileOpenDialog COM object
        hr = ole32.CoCreateInstance(
            byref(CLSID_FileOpenDialog),
            None,
            1,  # CLSCTX_INPROC_SERVER
            byref(IID_IFileOpenDialog),
            byref(pDialog),
        )
        check_hresult(hr)

        # Cast the pointer to the IFileOpenDialog interface
        dialog = cast(pDialog, LPFILEOPENDIALOG)

        # Get current dialog options
        options = ctypes.c_ulong()
        hr = dialog.contents.lpVtbl.contents.GetOptions(dialog, byref(options))
        check_hresult(hr)

        # Add the folder picking option flag
        new_options = options.value | FOS_PICKFOLDERS
        hr = dialog.contents.lpVtbl.contents.SetOptions(dialog, new_options)
        check_hresult(hr)

        try:
            # Show the dialog (no parent window)
            hr = dialog.contents.lpVtbl.contents.Show(dialog, None)
        except WindowsError as e:
            # Handle the case where user cancels the dialog (HRESULT 0x800704C7)
            if e.winerror == ERROR_CANCELLED:
                return None
            else:
                raise

        # If dialog returned cancelled HRESULT, return None
        if hr == ERROR_CANCELLED:
            return None
        check_hresult(hr)

        # Get the selected item (should be a folder)
        pItem = c_void_p()
        hr = dialog.contents.lpVtbl.contents.GetResult(dialog, byref(pItem))
        check_hresult(hr)

        shell_item = cast(pItem, LPSHELLITEM)

        # Retrieve the full file system path from the shell item
        pszName = c_wchar_p()
        hr = shell_item.contents.lpVtbl.contents.GetDisplayName(
            shell_item, SIGDN_FILESYSPATH, byref(pszName)
        )
        check_hresult(hr)

        folder_path = pszName.value

        # Free memory allocated by Windows for the path string
        ole32.CoTaskMemFree(pszName)

        # Release COM interfaces
        shell_item.contents.lpVtbl.contents.Release(shell_item)
        dialog.contents.lpVtbl.contents.Release(dialog)

        # Uninitialize COM library for this thread
        ole32.CoUninitialize()

        if not folder_path:
            raise RuntimeError("Failed to retrieve folder path.")

        return folder_path
