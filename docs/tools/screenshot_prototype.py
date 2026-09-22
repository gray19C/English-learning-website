# -*- coding: utf-8 -*-
"""用无头 Edge/Chrome 将低保真原型页面截为 PNG，供 PRD 嵌入（tools/images/prototype/）。

用法：python screenshot_prototype.py [--all]
默认仅截取 PRD §4.1-4.6 主流程嵌图页 6 张；--all 截取全部 16 页。
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys
from urllib.parse import quote

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_DIR = os.path.join(BASE, "Prototype", "html")
OUT_DIR = os.path.join(BASE, "tools", "images", "prototype")

EMBED_PAGES = [
    "02_guest_trial.html", "06_today.html", "07_new_word.html",
    "08_review.html", "10_backlog.html", "13_books.html",
]

EDGE_CANDIDATES = [
    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
]

WIDTH, HEIGHT = 1440, 1200


def find_browser():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("未找到 Edge/Chrome: " + ", ".join(EDGE_CANDIDATES))


def file_uri(path):
    return "file:///" + quote(os.path.abspath(path).replace("\\", "/"))


def is_png(p):
    if not os.path.exists(p) or os.path.getsize(p) < 5000:
        return False
    with open(p, "rb") as f:
        return f.read(8) == b"\x89PNG\r\n\x1a\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="截取全部 16 页")
    args = ap.parse_args()

    browser = find_browser()
    os.makedirs(OUT_DIR, exist_ok=True)

    targets = sorted(p for p in os.listdir(HTML_DIR) if p.endswith(".html"))
    if not args.all:
        targets = [p for p in targets if p in EMBED_PAGES]

    user_data = os.path.join(os.environ.get("TEMP", "."), "opencode", "edge_headless_profile")
    os.makedirs(user_data, exist_ok=True)

    fails = []
    for page in targets:
        out = os.path.join(OUT_DIR, page.replace(".html", ".png"))
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--disable-extensions", f"--window-size={WIDTH},{HEIGHT}",
               f"--user-data-dir={user_data}",
               f"--virtual-time-budget=2500",
               f"--screenshot={out}", file_uri(os.path.join(HTML_DIR, page))]
        subprocess.run(cmd, check=False, capture_output=True)
        if is_png(out):
            print(f"[OK] {page} -> {os.path.relpath(out, BASE)} ({os.path.getsize(out)} B)")
        else:
            fails.append(page)
            print(f"[FAIL] {page} 截图生成失败")

    print()
    if fails:
        print("[FAIL] 失败页面:", fails)
        sys.exit(1)
    print(f"[PASS] 共截取 {len(targets)} 张线框图")


if __name__ == "__main__":
    main()