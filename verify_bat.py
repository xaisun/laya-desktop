# -*- coding: utf-8 -*-
"""验证桌面「启动 laya.bat」能否真正拉起服务。

用 --no-browser 避免验证时反复弹浏览器窗口（bat 里 %* 会把参数透传给 server.py）。
stdin 接 DEVNULL：这样服务结束后 bat 里的 pause 读到 EOF 会立即返回，整条链路能干净收尾。
"""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

p = subprocess.Popen(
    ["cmd", "/c", "启动 laya.bat", "--no-browser"],
    cwd=r"C:\Users\sunxi\Desktop",
    stdin=subprocess.DEVNULL,
)
print("bat 已启动，pid=%d" % p.pid, flush=True)
rc = p.wait()
print("bat 退出，返回码=%d" % rc, flush=True)
