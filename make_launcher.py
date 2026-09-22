# -*- coding: utf-8 -*-
"""生成桌面启动器 laya 桌面版.bat（纯 ASCII + CRLF + 无 BOM）。"""
content = (
    "@echo off\r\n"
    "chcp 65001 >nul 2>&1\r\n"
    "title laya-desktop\r\n"
    'set "EXE=C:\\Users\\sunxi\\Desktop\\laya-desktop\\laya-desktop.exe"\r\n'
    'if not exist "%EXE%" goto noexe\r\n'
    'start "" "%EXE%"\r\n'
    "exit /b 0\r\n"
    ":noexe\r\n"
    "echo [ERROR] laya-desktop.exe not found:\r\n"
    "echo   %EXE%\r\n"
    "echo   Make sure the Desktop\\laya-desktop folder is present.\r\n"
    "pause\r\n"
    "exit /b 1\r\n"
)
dst = r"C:\Users\sunxi\Desktop\启动 laya 桌面版.bat"
with open(dst, "w", newline="", encoding="ascii") as f:
    f.write(content)
print("launcher written ->", dst)
