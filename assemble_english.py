# -*- coding: utf-8 -*-
"""从 HF 缓存里那些完整的 blob 拼出一个可用的本地模型目录。

背景：这台机器上 huggingface_hub 1.x 的快照落盘环节会产出 0 字节文件
（blobs 里的数据是完整的，snapshot 目录下全是空文件）。所以直接按 blob 拼。

blob 不按哈希硬编码，改按**字节数**匹配 —— 五个文件大小互不相同，不会有歧义。
"""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BLOBS = os.path.expanduser(
    r"~\.cache\huggingface\hub\models--convaiinnovations--laya\blobs"
)
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "english")

# 期望的字节数来自 HF API 的仓库清单（convaiinnovations/laya @ 1c5edc1）
EXPECT = [
    ("model.safetensors", 842609210),
    ("rl_agent_config.json", 745),
    ("encoder/config.json", 2083),
    ("tokenizer/tokenizer.json", 3583228),
    ("tokenizer/tokenizer_config.json", 308),
]

# --- 建立 大小 -> blob 路径 索引 -------------------------------------------
size_map = {}
for root, _dirs, files in os.walk(BLOBS):
    for name in files:
        if name.endswith(".refs"):
            continue
        p = os.path.join(root, name)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            size_map.setdefault(os.path.getsize(p), []).append(p)

print(f"blob 索引: {len(size_map)} 种大小 -> {sum(len(v) for v in size_map.values())} 个文件")
for s in sorted(size_map, reverse=True):
    print(f"   {s:>12} bytes : {[os.path.basename(x) for x in size_map[s]]}")

os.makedirs(DEST, exist_ok=True)
ok = True

print("\n--- 拷贝 ---")
for rel, expect_size in EXPECT:
    cands = size_map.get(expect_size)
    if not cands:
        print(f"[缺失] {rel}: 缓存里没有 {expect_size} 字节的 blob")
        ok = False
        continue
    src = cands[0]
    dst = os.path.join(DEST, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    got = os.path.getsize(dst)
    flag = "OK " if got == expect_size else "BAD"
    if got != expect_size:
        ok = False
    print(f"[{flag}] {rel:<34} {got:>12} bytes")

print("\n--- JSON 校验 ---")
for rel in ("rl_agent_config.json", "encoder/config.json", "tokenizer/tokenizer_config.json"):
    p = os.path.join(DEST, rel.replace("/", os.sep))
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        print(f"[OK ] {rel:<34} keys={list(d)[:5]}")
    except Exception as e:
        ok = False
        print(f"[BAD] {rel:<34} {type(e).__name__}: {e}")

print("\n--- model.safetensors 结构校验 ---")
p = os.path.join(DEST, "model.safetensors")
try:
    with open(p, "rb") as f:
        first8 = int.from_bytes(f.read(8), "little")
        meta = json.loads(f.read(first8).decode("utf-8"))
    n = len(meta) - (1 if "__metadata__" in meta else 0)
    print(f"header 长度 = {first8} bytes")
    print(f"张量数量   = {n}")
    print(f"文件总大小 = {os.path.getsize(p)} bytes （header 8+{first8} + 权重）")
    if first8 <= 0 or first8 > 50_000_000 or n == 0:
        ok = False
        print("[BAD] header 看起来不像 safetensors")
except Exception as e:
    ok = False
    print(f"[BAD] {type(e).__name__}: {e}")

print("\n结果:", "全部通过" if ok else "有失败项")
sys.exit(0 if ok else 1)
