import ctypes
from ctypes import wintypes

class SHFILEOPSTRUCTW(ctypes.Structure):
    # 注意：绝不能设 _pack_=1，必须 C 自然对齐，否则 x64 下字段错位
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("wFunc", wintypes.UINT),
        ("pFrom", wintypes.LPCWSTR),
        ("pTo", wintypes.LPCWSTR),
        ("fFlags", wintypes.UINT),
        ("fAnyOperationsAborted", wintypes.BOOL),
        ("hNameMappings", wintypes.LPVOID),
        ("lpszProgressTitle", wintypes.LPCWSTR),
    ]

FO_DELETE = 0x0003
FOF_ALLOWUNDO = 0x0040       # 送回收站（可恢复）
FOF_NOCONFIRMATION = 0x0010  # 无头环境跳过确认框
FOF_SILENT = 0x0004          # 不弹进度

targets = [
    r"C:\Users\sunxi\Desktop\laya-desktop",
    r"C:\Users\sunxi\Desktop\启动 laya 桌面版.bat",
]
# pFrom 必须是双 null 结尾的多串（各路径用 \0 分隔再补一个 \0）
pFrom = "\0".join(targets) + "\0\0"

struc = SHFILEOPSTRUCTW(
    0, FO_DELETE, pFrom, None,
    FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT,
    0, 0, None,
)

shell32 = ctypes.windll.shell32
ret = shell32.SHFileOperationW(ctypes.byref(struc))
if ret == 0 and not struc.fAnyOperationsAborted:
    print("RECYCLE OK -> targets moved to Recycle Bin")
else:
    print("RECYCLE FAILED ret=%s aborted=%s" % (ret, struc.fAnyOperationsAborted))
