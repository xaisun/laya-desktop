# -*- coding: utf-8 -*-
"""在桌面创建 laya 实测结果页面的快捷方式。

用 .url (InternetShortcut) 纯文本格式，因为本机 COM 被安全策略拦截，
无法用 WScript.Shell 创建 .lnk。

关键坑：Windows 按系统 codepage(GBK) 读取 .url 文件，
必须用 gbk 编码写入，否则中文与图标会变空白。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DESKTOP = r"C:\Users\sunxi\Desktop"
TARGET = r"C:\Users\sunxi\WorkBuddy\2026-09-22-04-34-48\laya-demo\实测结果.html"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
LNK_NAME = "laya 实测结果.url"

print("目标文件存在:", os.path.isfile(TARGET))
print("桌面存在    :", os.path.isdir(DESKTOP))
if not os.path.isfile(TARGET):
    raise SystemExit("目标 HTML 不存在，终止")

url = "file:///" + TARGET.replace("\\", "/")
lines = [
    "[InternetShortcut]",
    "URL=" + url,
    "IconFile=" + EDGE,
    "IconIndex=0",
    "",
]
data = "\r\n".join(lines)

dst = os.path.join(DESKTOP, LNK_NAME)
with open(dst, "wb") as f:
    f.write(data.encode("gbk", errors="replace"))

print("已写入      :", dst)
print("文件大小    :", os.path.getsize(dst), "字节")
print("--- 回读校验 (gbk 解码) ---")
with open(dst, "rb") as f:
    raw = f.read()
print(raw.decode("gbk", errors="replace"))
print("--- 结构校验 ---")
ok = raw.startswith(b"[InternetShortcut]") and b"URL=file:///" in raw
print("结构正确    :", ok)
