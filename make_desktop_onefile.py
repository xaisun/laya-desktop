# -*- coding: utf-8 -*-
"""把 laya 桌面版打包成 onefile 单 exe（原生 pywebview 窗口 + 内置服务）。

与 onedir 版的区别
- 入口换成 app_native.py：用 pywebview 开原生无边框窗口，不再弹浏览器
- --onefile：产物是单个 laya-desktop.exe（启动时会把 ~600MB 运行时解压到
  %TEMP%\\_MEIPASS，所以冷启比 onedir 慢，老板已接受）
- --windowed：无控制台黑窗，只有原生窗口
- 模型(models/, 约 1.5GB) 不进包，运行时从 exe 同级 models/ 读取（见 server._resolve_models_dir），
  所以分发时 exe 与 models 文件夹放一起即可
- pywebview 在 Windows 走 WinForms + pythonnet/clr 后端，需要把 webview/lib 里的
  WebView2 .NET 程序集一并收进包（--collect-all webview 会带上 lib/ 与 runtimes/）
"""
import os
import sys

import PyInstaller.__main__

HERE = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    os.path.join(HERE, "app_native.py"),
    "--name", "laya-desktop",
    "--onefile",
    "--windowed",           # 无控制台，只有原生窗口
    "--noconfirm",
    "--paths", HERE,
    # 前端页面随包（绝对路径，避免按 specpath 解析找不到）
    "--add-data", "%s%sweb" % (os.path.join(HERE, "web"), os.pathsep),
    # ---- 原推理依赖 ----
    "--hidden-import", "torch",
    "--hidden-import", "torch.nn",
    "--hidden-import", "transformers",
    "--hidden-import", "laya",
    "--hidden-import", "huggingface_hub",
    "--hidden-import", "safetensors",
    "--hidden-import", "numpy",
    "--hidden-import", "tokenizers",
    "--collect-all", "transformers",
    "--collect-all", "laya",
    "--collect-all", "huggingface_hub",
    # ---- pywebview / WebView2 后端依赖 ----
    "--hidden-import", "webview",
    "--hidden-import", "pythonnet",
    "--hidden-import", "clr",
    "--hidden-import", "clr_loader",
    "--hidden-import", "proxy_tools",
    "--hidden-import", "bottle",
    "--collect-all", "webview",
    "--collect-all", "pythonnet",
    # tkinter 用不到，剔除瘦身（注意：unittest 绝不能 exclude，torch 运行时要）
    "--exclude-module", "tkinter",
    "--distpath", os.path.join(HERE, "build_onefile", "dist"),
    "--workpath", os.path.join(HERE, "build_onefile", "build"),
    "--specpath", os.path.join(HERE, "build_onefile"),
])

print("BUILD DONE ->", os.path.join(HERE, "build_onefile", "dist", "laya-desktop.exe"))
