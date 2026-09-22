# -*- coding: utf-8 -*-
"""验证冻结后的 laya-desktop.exe：等 ready → 预测 → 关闭。
关键：本机 Bash 会注入 http_proxy，挡住 127.0.0.1 回环，所以用 ProxyHandler({}) 禁代理。
"""
import json
import sys
import time
import urllib.request

URL = "http://127.0.0.1:8811"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def get(path):
    return json.loads(opener.open(URL + path, timeout=10).read().decode("utf-8"))


def post(path, data):
    req = urllib.request.Request(
        URL + path,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(opener.open(req, timeout=180).read().decode("utf-8"))


def main():
    t0 = time.time()
    ready = False
    while time.time() - t0 < 200:
        try:
            st = get("/api/status")
        except Exception as e:
            time.sleep(2)
            continue
        phase = st.get("phase")
        print("[status] phase=%s msg=%s models_ok=%s load=%ss"
              % (phase, st.get("message"), st.get("models_ok"), st.get("load_seconds")),
              flush=True)
        if phase == "ready":
            ready = True
            break
        if phase == "error":
            print("[FAIL] load error:", st.get("error"), flush=True)
            sys.exit(1)
        time.sleep(3)

    if not ready:
        print("[FAIL] 200s 内未就绪", flush=True)
        sys.exit(1)

    sample = {
        "from": "zhang@example.cn",
        "subject": "生产环境完全无法登录",
        "body": "我们生产环境从今天早上九点开始就登不进去了，所有员工都受影响，"
                "定单积压了几百单。今天之内必须解决，不然我们就换供应商了。",
    }
    r = post("/api/predict", {"scenario": "support", "state": sample})
    print("[predict] ok=%s elapsed_ms=%s" % (r.get("ok"), r.get("elapsed_ms")), flush=True)
    print("[predict] answers=%s" % json.dumps(r.get("answers"), ensure_ascii=False)[:1000], flush=True)
    print("[predict] routing=%s" % json.dumps(r.get("routing"), ensure_ascii=False)[:400], flush=True)

    post("/api/shutdown", {})
    print("[shutdown] 已发送，exe 应在 1s 内退出", flush=True)


if __name__ == "__main__":
    main()
