# -*- coding: utf-8 -*-
"""生成安装包所需的纯 ASCII 辅助文件（避开 .bat 的 BOM / 中文坑）。

产物放在 laya-demo/installer/：
- 启动 laya 决策引擎.bat  : 同目录启动 onefile exe（会被拷到桌面当快捷方式）
- install_helper.bat      : SFX 解压后执行——把启动器拷到桌面并启动程序
- sfx_config.txt          : 7z 自解压配置（UTF-8 BOM）
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "installer")
os.makedirs(OUT, exist_ok=True)

# 同目录启动器（纯 ASCII，CRLF，无 BOM）
launcher = (
    "@echo off\r\n"
    'start "" "%~dp0laya-desktop.exe"\r\n'
    "exit /b 0\r\n"
)
with open(os.path.join(OUT, "laya-launch.bat"), "w", newline="", encoding="ascii") as f:
    f.write(launcher)

# 解压后助手：把启动器放到桌面，并直接启动程序（内容必须纯 ASCII）
helper = (
    "@echo off\r\n"
    "set \"EXE=%~dp0laya-desktop.exe\"\r\n"
    "set \"LNK=%USERPROFILE%\\Desktop\\laya-launch.bat\"\r\n"
    "copy /Y \"%~dp0laya-launch.bat\" \"%LNK%\" >nul 2>&1\r\n"
    "start \"\" \"%EXE%\"\r\n"
    "exit /b 0\r\n"
)
with open(os.path.join(OUT, "install_helper.bat"), "w", newline="", encoding="ascii") as f:
    f.write(helper)

# 7z SFX 配置：UTF-8 + BOM；InstallPath 用相对路径 laya-desktop（解压到安装包同级，
# 不依赖 %LOCALAPPDATA% 展开，避免 7z SFX 不展开环境变量时生成字面量文件夹）
config = (
    ";!@Install@!UTF-8!\r\n"
    'Title="laya 决策引擎 安装程序"\r\n'
    'BeginPrompt="即将安装 laya 决策引擎（约 2GB），解压到安装包同级的 laya 文件夹。继续？"\r\n'
    'InstallPath="laya"\r\n'
    'RunProgram="install_helper.bat"\r\n'
    ";!@InstallEnd@!\r\n"
)
with open(os.path.join(OUT, "sfx_config.txt"), "w", newline="", encoding="utf-8-sig") as f:
    f.write(config)

print("installer assets written to", OUT)
for n in ("laya-launch.bat", "install_helper.bat", "sfx_config.txt"):
    p = os.path.join(OUT, n)
    with open(p, "rb") as f:
        head = f.read(3)
    print(" -", n, "first3=", head)
