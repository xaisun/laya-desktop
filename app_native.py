# -*- coding: utf-8 -*-
"""laya 桌面版 · 原生无边框窗口入口（替代浏览器操作台）。

- 复用 server.py 的 HTTP 服务（本地 API + 模型加载），不重复造轮子
- 用 pywebview 开一个原生窗口直接渲染 127.0.0.1:8811，没有浏览器地址栏/边框
- 关窗（或点页面上的『停止服务』）即 os._exit(0)，干净退出
- --no-window：不建窗口，仅起 API 服务（供 CI / 无头验证用）
"""
import os
import sys
import threading
import time

import server

NO_WINDOW = "--no-window" in sys.argv


def main():
    print("=== laya 决策引擎 · 原生窗口版 ===", flush=True)

    httpd = server.start_server()
    # 模型在后台线程加载，页面自身会轮询 /api/status 显示进度
    threading.Thread(target=server.load_models, daemon=True).start()

    if httpd is None:
        # 端口被占用：多半是另一个实例在跑，直接把窗口指过去即可
        print("（端口已被占用，直接打开已有服务）", flush=True)

    if NO_WINDOW:
        print("（--no-window）不创建窗口，仅运行 API 服务。", flush=True)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
        os._exit(0)

    import webview

    webview.create_window(
        "laya 决策引擎",
        server.URL,
        width=1120,
        height=780,
        min_size=(900, 600),
        background_color="#0f1115",
    )
    # webview.start() 阻塞，直到所有窗口关闭 → 随后整进程退出
    webview.start()
    os._exit(0)


if __name__ == "__main__":
    main()
