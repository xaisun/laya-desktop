# -*- coding: utf-8 -*-
"""验证客户端：绕开工具注入的 http_proxy，直连本机 8811。

Bash 工具环境里带着 http_proxy=http://127.0.0.1:11347，
urllib 默认会走它，对 127.0.0.1 的请求会拿到 502 Bad Gateway
（表现为「明明服务在监听却连不上」），所以必须显式禁用代理。
"""
import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:8811"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def get(path, timeout=6):
    with OPENER.open(BASE + path, timeout=timeout) as r:
        return json.load(r)


def post(path, obj, timeout=180):
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"})
    with OPENER.open(req, timeout=timeout) as r:
        return json.load(r)


def wait_ready(limit=170):
    st = {}
    deadline = time.time() + limit
    while time.time() < deadline:
        try:
            st = get("/api/status")
        except Exception as e:
            print("  [等待中] %s" % type(e).__name__, flush=True)
            time.sleep(3)
            continue
        print("  phase=%-8s | %s" % (st.get("phase"), st.get("message")), flush=True)
        if st.get("phase") in ("ready", "error"):
            return st
        time.sleep(4)
    return st


if __name__ == "__main__":
    print("=== 等 bat 拉起的服务就绪 ===")
    st = wait_ready()
    if st.get("phase") != "ready":
        print("!! 未就绪，最后状态:", st)
        raise SystemExit(1)
    print("  就绪 | 加载 %ss | laya %s | 已加载 %s"
          % (st.get("load_seconds"), st.get("laya_version"), st.get("loaded")))

    print("\n=== 跑一次判断（中文工单）===")
    t = time.perf_counter()
    res = post("/api/predict", {"scenario": "support", "state": {
        "from": "wang@example.cn", "subject": "付款一直失败",
        "body": "我们的对公转账连续三次失败，客服电话打不通，今天下午三点前必须付出去，"
                "否则合同违约。再这样我们要考虑换一家了。"}})
    print("  往返 %.0f ms | 推理 %.1f ms" % ((time.perf_counter() - t) * 1000, res["elapsed_ms"]))
    print("  路由:", res["routing"].get("model"), "|", res["routing"].get("reason"))
    for k, a in res["answers"].items():
        v = a.get("choice", a.get("score", a.get("noul")))
        print("   - %-18s %s" % (k, v))

    print("\n=== 停止服务（重点验证进程能真正退出）===")
    print(" ", post("/api/shutdown", {}, timeout=15))
    time.sleep(2)
    for i in range(10):
        time.sleep(1)
        try:
            get("/api/status", timeout=2)
            print("  仍在监听… %ds" % (i + 1))
        except Exception as e:
            print("  已停止（%d 秒后探测失败: %s）" % (i + 1, type(e).__name__))
            break
