# -*- coding: utf-8 -*-
"""验证低保真原型：页面齐全 / 页面间链接无死链 / 每页含断点标注与主区 /
Figma 规格文档存在 / 关键流程页面关键词覆盖。"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE, "Prototype", "html")
FIGMA = os.path.join(BASE, "Prototype", "figma", "figma_spec.md")
INDEX = os.path.join(HTML, "index.html")

# PRD 流程页关键词：每个核心流程页必须命中其对应 FR 关键词，防止空页
PAGE_KEYWORDS = {
    "00_landing.html": ["免", "词书", "学 5 个词"],
    "01_book_detail.html": ["四级核心", "词频", "数据来源", "纠错"],
    "02_guest_trial.html": ["游客", "5", "不认识"],
    "03_signup.html": ["注册", "密码", "合并"],
    "04_login.html": ["登录", "密码"],
    "05_onboarding.html": ["每日新词数", "词书", "小目标"],
    "06_today.html": ["今日任务", "复习", "新词", "连续天数"],
    "07_new_word.html": ["不认识", "待巩固", "音标"],
    "08_review.html": ["四选一", "防偷看", "等级"],
    "09_done.html": ["连续", "完成", "打卡"],
    "10_backlog.html": ["积压", "批", "无惩罚"],
    "11_stats.html": ["已掌握", "热力图", "间隔"],
    "12_settings.html": ["每日新词数", "间隔规则", "至少保留一本"],
    "13_books.html": ["切换", "独立", "考研高频"],
    "14_feedback.html": ["位置快照", "提交", "审核"],
}

fails = []

pages = [p for p in sorted(os.listdir(HTML)) if p.endswith(".html")]
if len(pages) < 16:
    fails.append(f"页面数量不足，期望>=16（含 index），实际={len(pages)}")
print(f"[OK] 页面文件共 {len(pages)} 个")

if not os.path.exists(INDEX):
    fails.append("缺少 index.html 流程总览")
else:
    print("[OK] index.html 存在（流程总览）")

if not os.path.exists(FIGMA):
    fails.append("缺少 figma_spec.md")
else:
    print("[OK] figma_spec.md 存在")

# 1) index.html 应引用全部 15 个页面  2) 所有 .html 互相引用均需可解析
all_pages = set(pages)
href_map = {}
for p in pages:
    with open(os.path.join(HTML, p), encoding="utf-8") as f:
        text = f.read()
    refs = set(re.findall(r'href="([^"#]+\.html)"', text))
    href_map[p] = refs - all_pages  # 只保留指向不存在页面的引用

broken = {p: sorted(refs) for p, refs in href_map.items() if refs}
if broken:
    fails.append(f"死链: {broken}")
else:
    print("[OK] 全部页面间链接可解析（无死链）")

with open(INDEX, encoding="utf-8") as f:
    idx = f.read()
table_pages = re.findall(r'<td>(0?\d+)</td><td><a href="([0-9a-z_]+\.html)"', idx)
linked = {name for _, name in table_pages}
uncovered = all_pages - {"index.html"} - linked
if uncovered:
    fails.append(f"index 未覆盖页面: {sorted(uncovered)}")
else:
    print(f"[OK] index 索引覆盖 {len(linked)} 个页面")

# 3) 每页结构与关键词校验
for p in pages:
    with open(os.path.join(HTML, p), encoding="utf-8") as f:
        text = f.read()
    if '<div class="breakpoints">' not in text:
        fails.append(f"{p} 缺少断点标注 `.breakpoints`")
    if "<main" not in text:
        fails.append(f"{p} 缺少 `<main>` 主区")
    if 'class="footer"' not in text and "copyright" not in text.lower():
        fails.append(f"{p} 缺少页脚")
    if p in PAGE_KEYWORDS:
        missing = [k for k in PAGE_KEYWORDS[p] if k not in text]
        if missing:
            fails.append(f"{p} 缺少关键词: {missing}")

print("[OK] 页面结构与关键词校验完成")

print()
if fails:
    for f in fails:
        print("[FAIL]", f)
    raise SystemExit(1)
print("[PASS] 全部原型校验通过")