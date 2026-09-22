# -*- coding: utf-8 -*-
"""把 laya 本地服务(server.py) 打包成独立桌面 exe。

设计要点
- 采用 onedir（单文件夹）：exe 与其依赖库放在一个文件夹里，启动时不再
  把 torch 等大库解压到 %TEMP%（onefile 每次启动都要解压 ~1GB，很慢且
  反复写临时盘）。onedir 启动只加载模型，体验最好。
- 模型(models/, 约 1.5GB) 不进包，打包后手动拷进 dist/laya-desktop/models，
  随 exe 一起分发，实现真正「独立、可移动」。
- web/index.html 用 --add-data 带进去，冻结后 BASE 指向 exe 所在目录，
  因此 web/ 与 models/ 都与 exe 同目录即可被找到。
- 冻结态下 BASE 的解析：优先用 sys._MEIPASS(onefile 用)，否则用 exe 目录。
"""
import os
import sys

import PyInstaller.__main__

HERE = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    # 入口：直接复用 server.py（它已用 __file__ 推算 BASE，onedir 下即 exe 目录）
    os.path.join(HERE, "server.py"),
    "--name", "laya-desktop",
    "--onedir",
    "--console",            # 保留控制台，方便看加载进度 / Ctrl+C 停止
    "--noconfirm",
    "--paths", HERE,
    # 前端页面随包（数据源用绝对路径，避免 PyInstaller 按 specpath 解析找不到）
    "--add-data", "%s%sweb" % (os.path.join(HERE, "web"), os.pathsep),
    # 关键依赖：torch 有官方 hook 基本够；transformers 大量动态 import，
    # 用 collect-all 兜底，确保任意子模块都被打进去
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
    # tkinter 用不到（界面是浏览器操作台），剔除瘦身；unittest 千万别 exclude，
    # torch/transformers 运行时会 import unittest，剔了会 ModuleNotFoundError
    "--exclude-module", "tkinter",
    "--distpath", os.path.join(HERE, "build_out", "dist"),
    "--workpath", os.path.join(HERE, "build_out", "build"),
    "--specpath", os.path.join(HERE, "build_out"),
])

print("BUILD DONE ->", os.path.join(HERE, "build_out", "dist", "laya-desktop", "laya-desktop.exe"))
