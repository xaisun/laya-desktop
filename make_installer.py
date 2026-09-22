# -*- coding: utf-8 -*-
"""把 onefile exe + models + 启动器 拼成 7z 自解压安装包 laya-desktop-setup.exe。

流程
1. 把 build_onefile/dist/laya-desktop.exe + models/ + installer/*.bat 放进 stage/
2. 7z 压成 stage.7z（LZMA，-mx=7）
3. copy /b 7z.sfx + sfx_config.txt + stage.7z -> laya-desktop-setup.exe
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ONEFILE_EXE = os.path.join(HERE, "build_onefile", "dist", "laya-desktop.exe")
MODELS_SRC = os.path.join(HERE, "models")
INSTALLER_DIR = os.path.join(HERE, "installer")
STAGE = os.path.join(HERE, "build_onefile", "stage")
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"
SEVEN_SFX = r"C:\Program Files\7-Zip\7z.sfx"
OUT_SETUP = os.path.join(HERE, "build_onefile", "laya-desktop-setup.exe")


def check():
    miss = [p for p in (ONEFILE_EXE, MODELS_SRC, SEVEN_ZIP, SEVEN_SFX) if not os.path.exists(p)]
    if miss:
        print("缺少必要文件，先完成 onefile 构建并确认 7z：")
        for m in miss:
            print("  -", m)
        sys.exit(1)


def stage():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)
    # exe
    shutil.copy2(ONEFILE_EXE, os.path.join(STAGE, "laya-desktop.exe"))
    # 启动器 + 安装助手
    for n in ("laya-launch.bat", "install_helper.bat"):
        shutil.copy2(os.path.join(INSTALLER_DIR, n), os.path.join(STAGE, n))
    # 模型（大，直接拷）
    dst_models = os.path.join(STAGE, "models")
    print("拷贝模型 %s -> %s ..." % (MODELS_SRC, dst_models), flush=True)
    shutil.copytree(MODELS_SRC, dst_models)
    print("stage 就绪:", STAGE, flush=True)


def build():
    archive = os.path.join(HERE, "build_onefile", "stage.7z")
    cfg = os.path.join(INSTALLER_DIR, "sfx_config.txt")
    # 7z a -t7z archive -r stage\*
    subprocess.run(
        [SEVEN_ZIP, "a", "-t7z", "-mx=7", "-r", archive, os.path.join(STAGE, "*")],
        check=True,
    )
    # copy /b 7z.sfx + cfg + archive -> setup.exe
    with open(OUT_SETUP, "wb") as out:
        for part in (SEVEN_SFX, cfg, archive):
            with open(part, "rb") as f:
                out.write(f.read())
    print("安装包生成:", OUT_SETUP, flush=True)
    print("体积:", round(os.path.getsize(OUT_SETUP) / 1e9, 2), "GB", flush=True)


if __name__ == "__main__":
    check()
    stage()
    build()
