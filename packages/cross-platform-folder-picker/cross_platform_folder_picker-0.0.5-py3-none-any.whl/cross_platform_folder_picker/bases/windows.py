from ._abstract import AbstractFolderPicker

import ctypes
from ctypes import wintypes, POINTER, byref, cast, c_void_p, c_wchar_p

ole32 = ctypes.OleDLL("ole32")
shell32 = ctypes.WinDLL("shell32")


# GUID struct
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, guid_str):
        super().__init__()
        ole32.CLSIDFromString(ctypes.c_wchar_p(guid_str), byref(self))


# HRESULT check helper
def check_hresult(hr):
    if hr != 0:
        raise ctypes.WinError(ctypes.HRESULT(hr))


# IUnknown interface
class IUnknown(ctypes.Structure):
    pass


LPUNKNOWN = POINTER(IUnknown)

IUnknown._fields_ = [("lpVtbl", POINTER(ctypes.c_void_p))]


# Define vtable for IUnknown (3 methods)
class IUnknownVTable(ctypes.Structure):
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


# Set vtable type to IUnknown
IUnknown.lpVtbl = POINTER(IUnknownVTable)

# IFileOpenDialog interface ID and CLSID
CLSID_FileOpenDialog = GUID("{DC1C5A9C-E88A-4DDE-A5A1-60F82A20AEF7}")
IID_IFileOpenDialog = GUID("{D57C7288-D4AD-4768-BE02-9D969532D960}")

SIGDN_FILESYSPATH = 0x80058000
FOS_PICKFOLDERS = 0x00000020

# HRESULT for cancel operation
ERROR_CANCELLED = -2147023673


# IFileOpenDialog interface extends IUnknown with vtable methods
class IFileOpenDialog(ctypes.Structure):
    pass


LPFILEOPENDIALOG = POINTER(IFileOpenDialog)

# VTable function prototypes
# HRESULT Show(HWND hwndParent);
ShowFunc = ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, wintypes.HWND)
# HRESULT SetOptions(FILEOPENDIALOGOPTIONS fos);
SetOptionsFunc = ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, ctypes.c_ulong)
# HRESULT GetOptions(FILEOPENDIALOGOPTIONS *pfos);
GetOptionsFunc = ctypes.WINFUNCTYPE(
    ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(ctypes.c_ulong)
)
# HRESULT GetResult(IShellItem **ppsi);
GetResultFunc = ctypes.WINFUNCTYPE(ctypes.HRESULT, LPFILEOPENDIALOG, POINTER(c_void_p))

# IShellItem interface ID
IID_IShellItem = GUID("{43826D1E-E718-42EE-BC55-A1E261C37BFE}")


# IShellItem interface (only GetDisplayName needed)
class IShellItem(ctypes.Structure):
    pass


LPSHELLITEM = POINTER(IShellItem)

GetDisplayNameFunc = ctypes.WINFUNCTYPE(
    ctypes.HRESULT, LPSHELLITEM, ctypes.c_ulong, POINTER(c_wchar_p)
)


class IFileOpenDialogVtbl(ctypes.Structure):
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
        # IFileDialog
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
        # IShellItem methods
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
    def pick_folder(
        self, title="Select a folder", icon: str | None = None
    ) -> str | None:
        ole32.CoInitialize(None)

        pDialog = c_void_p()

        hr = ole32.CoCreateInstance(
            byref(CLSID_FileOpenDialog),
            None,
            1,
            byref(IID_IFileOpenDialog),
            byref(pDialog),
        )
        check_hresult(hr)

        dialog = cast(pDialog, LPFILEOPENDIALOG)

        options = ctypes.c_ulong()
        hr = dialog.contents.lpVtbl.contents.GetOptions(dialog, byref(options))
        check_hresult(hr)

        new_options = options.value | FOS_PICKFOLDERS
        hr = dialog.contents.lpVtbl.contents.SetOptions(dialog, new_options)
        check_hresult(hr)

        try:
            hr = dialog.contents.lpVtbl.contents.Show(dialog, None)
        except WindowsError as e:
            # Handle cancel HRESULT: 0x800704C7
            if e.winerror == ERROR_CANCELLED:
                return None
            else:
                raise

        if hr == ERROR_CANCELLED:
            return None
        check_hresult(hr)

        pItem = c_void_p()
        hr = dialog.contents.lpVtbl.contents.GetResult(dialog, byref(pItem))
        check_hresult(hr)

        shell_item = cast(pItem, LPSHELLITEM)

        pszName = c_wchar_p()
        hr = shell_item.contents.lpVtbl.contents.GetDisplayName(
            shell_item, SIGDN_FILESYSPATH, byref(pszName)
        )
        check_hresult(hr)

        folder_path = pszName.value

        # Free the memory allocated for pszName by Windows
        ole32.CoTaskMemFree(pszName)

        # Release interfaces
        shell_item.contents.lpVtbl.contents.Release(shell_item)
        dialog.contents.lpVtbl.contents.Release(dialog)

        ole32.CoUninitialize()
        if not folder_path:
            raise RuntimeError("Failed to retrieve folder path.")

        return folder_path
