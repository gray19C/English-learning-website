# -*- coding: utf-8 -*-
"""验证低保真原型：页面齐全 / 页面间链接无死链 / 每页含断点标注、主区、页脚 /
每页含标准 PRD 对照标注条（PRD_prototype_mapping.md）且内容一致 /
核心流程页关键词覆盖 / Figma 规格文档存在。"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE, "Prototype", "html")
MAPPING = os.path.join(BASE, "Prototype", "PRD_prototype_mapping.md")
FIGMA = os.path.join(BASE, "Prototype", "figma", "figma_spec.md")
INDEX = os.path.join(HTML, "index.html")

# 每页标准标注条必须命中的 FR 与里程碑（与 PRD_prototype_mapping.md 第一节一致）
PAGE_REFS = {
    "00_landing.html": (["FR-10"], ["M2"]),
    "01_book_detail.html": (["FR-10"], ["M2"]),
    "02_guest_trial.html": (["FR-01"], ["M2"]),
    "03_signup.html": (["FR-01"], ["M2"]),
    "04_login.html": (["FR-01"], ["M2"]),
    "05_onboarding.html": (["FR-02"], ["M2"]),
    "06_today.html": (["FR-03", "FR-08"], ["M2", "M3"]),
    "07_new_word.html": (["FR-04"], ["M2"]),
    "08_review.html": (["FR-05", "FR-06"], ["M3"]),
    "09_done.html": (["FR-08"], ["M3"]),
    "10_backlog.html": (["FR-07"], ["M3"]),
    "11_stats.html": (["FR-09"], ["M3"]),
    "12_settings.html": (["FR-02", "FR-06"], ["M3"]),
    "13_books.html": (["FR-11", "FR-10"], ["M3"]),
    "14_feedback.html": (["FR-10"], ["M4"]),
}

# 主流程嵌图页（PRD §4.1-4.6 各嵌 1 张线框图）
EMBED_PAGES = ["02_guest_trial.html", "06_today.html", "07_new_word.html",
               "08_review.html", "10_backlog.html", "13_books.html"]

fails = []

pages = [p for p in sorted(os.listdir(HTML)) if p.endswith(".html")]
if len(pages) < 16:
    fails.append(f"页面数量不足，期望>=16（含 index），实际={len(pages)}")
print(f"[OK] 页面文件共 {len(pages)} 个")

if not os.path.exists(INDEX):
    fails.append("缺少 index.html 流程总览")
else:
    print("[OK] index.html 存在（流程总览）")

if not os.path.exists(MAPPING):
    fails.append("缺少 PRD_prototype_mapping.md 对照映射表")
else:
    with open(MAPPING, encoding="utf-8") as f:
        mapping = f.read()
    unmapped = [p for p in pages if p != "index.html" and p not in mapping]
    if unmapped:
        fails.append(f"映射表未覆盖页面: {sorted(unmapped)}")
    else:
        print("[OK] 映射表覆盖全部页面")

if not os.path.exists(FIGMA):
    fails.append("缺少 figma_spec.md")
else:
    print("[OK] figma_spec.md 存在")

# 1) 链接完整性
all_pages = set(pages)
href_map = {}
for p in pages:
    with open(os.path.join(HTML, p), encoding="utf-8") as f:
        text = f.read()
    refs = set(re.findall(r'href="([^"#]+\.html)"', text))
    href_map[p] = refs - all_pages

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

# 2) 每页结构 + 标准标注条（.prd-ref）与映射一致
for p in pages:
    with open(os.path.join(HTML, p), encoding="utf-8") as f:
        text = f.read()
    if '<div class="breakpoints">' not in text:
        fails.append(f"{p} 缺少断点标注 `.breakpoints`")
    if "<main" not in text:
        fails.append(f"{p} 缺少 `<main>` 主区")
    if 'class="footer"' not in text:
        fails.append(f"{p} 缺少页脚")
    if '<div class="prd-ref">' not in text:
        fails.append(f"{p} 缺少标准 PRD 对照标注条 `.prd-ref`")
        continue
    ref = text.split('<div class="prd-ref">', 1)[1].split("</div>", 1)[0]
    frs, ms = PAGE_REFS.get(p, ([], []))
    miss = []
    for fr in frs:
        if fr not in ref:
            miss.append(f"缺 {fr}")
    for m in ms:
        if f"里程碑" not in ref or m not in ref:
            miss.append(f"缺里程碑 {m}")
    if "<b>FR：</b>" not in ref or "<b>里程碑：</b>" not in ref:
        miss.append("标注条字段不完整（需 FR / 里程碑）")
    if miss and p not in ("index.html",):
        fails.append(f"{p} 标注条: {', '.join(miss)}")

# 3) 核心流程页关键词（防止空页）
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
for p in pages:
    if p in PAGE_KEYWORDS:
        with open(os.path.join(HTML, p), encoding="utf-8") as f:
            text = f.read()
        missing = [k for k in PAGE_KEYWORDS[p] if k not in text]
        if missing:
            fails.append(f"{p} 缺少关键内容: {missing}")

# 4) 主流程嵌图页标注应声明「主嵌图页」
for p in EMBED_PAGES:
    with open(os.path.join(HTML, p), encoding="utf-8") as f:
        text = f.read()
    if "主嵌图页" not in text.split('<div class="prd-ref">', 1)[1]:
        fails.append(f"{p} 为 PRD §4.x 主嵌图页，标注条应声明「主嵌图页」")

print("[OK] 页面结构、标注条与映射一致性校验完成")

print()
if fails:
    for f in fails:
        print("[FAIL]", f)
    raise SystemExit(1)
print("[PASS] 全部原型校验通过")