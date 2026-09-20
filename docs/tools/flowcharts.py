# -*- coding: utf-8 -*-
"""生成 PRD 所需的 6 张流程图 PNG（matplotlib 绘制，CJK 字体自动回退）。"""
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, PathPatch, Ellipse
from matplotlib.path import Path

plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC"
]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)

BLUE = "#1f6fb2"
BLUE_L = "#eaf3fb"
GREEN = "#237a57"
GREEN_L = "#e9f5ef"
ORANGE = "#b8711a"
ORANGE_L = "#fdf3e3"
RED = "#b3352b"
RED_L = "#fdeceb"
GRAY = "#667085"
GRAY_L = "#f2f4f7"


class Chart:
    def __init__(self, ax):
        self.ax = ax
        self.nodes = {}

    def add(self, nid, x, y, w, h, text, shape="rect", fc=BLUE_L, ec=BLUE, fs=11):
        self.nodes[nid] = (x, y, w, h)
        ax = self.ax
        if shape == "diamond":
            verts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
            patch = PathPatch(Path(verts + [verts[0]]), fc=fc, ec=ec, lw=1.2)
        elif shape == "ellipse":
            patch = Ellipse((x, y), w, h, fc=fc, ec=ec, lw=1.2)
        else:
            patch = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                   boxstyle="round,pad=0.015,rounding_size=0.09",
                                   fc=fc, ec=ec, lw=1.2, zorder=2)
        ax.add_patch(patch)
        ax.text(x, y, text, ha="center", va="center", fontsize=fs, linespacing=1.35, zorder=3)

    def link(self, a, b, label=None, color="#333333", fs=9, style="-|>"):
        ax = self.ax
        (x1, y1, _, _), (x2, y2, _, _) = self.nodes[a], self.nodes[b]
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                     mutation_scale=15, lw=1.2, color=color,
                                     shrinkA=6, shrinkB=6, zorder=1))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            if y1 != y2:
                ax.text(mx, my + 0.22, label, fontsize=fs, color="#8a4b12",
                        ha="center", va="bottom", zorder=4)
            else:
                ax.text(mx, my + 0.35, label, fontsize=fs, color="#8a4b12",
                        ha="center", va="bottom", zorder=4)


def new_fig():
    fig, ax = plt.subplots(figsize=(9.6, 12.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis("off")
    c = Chart(ax)
    return fig, c


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved:", path)


def note(ax, x, y, text, color=GRAY, fs=9):
    ax.text(x, y, text, fontsize=fs, color=color, ha="center", va="center",
            style="italic")


# ---------------------------------------------------------------- F1 首次使用漏斗
def f1_funnel():
    fig, c = new_fig()
    c.add("start", 5.0, 15.1, 4.0, 1.0, "游客访问网站（搜索 / 分享链接进入）", shape="ellipse")
    c.add("land", 5.0, 12.9, 3.9, 1.05, "首页着陆（游客模式，免注册可直接体验）")
    c.add("setup", 5.0, 10.7, 3.9, 1.2, "选择目标词书 + 设置每日新词数\n（默认 20 个 / 天）")
    c.add("learn5", 5.0, 8.5, 3.9, 1.05, "立即学习 5 个词\n（第一次“记住了一个词”的正反馈）", fc=GREEN_L, ec=GREEN)
    c.add("done5", 5.0, 6.3, 3.9, 1.0, "首次成就感页（展示已记住词数）", fc=GREEN_L, ec=GREEN)
    c.add("reg?", 5.0, 4.1, 3.8, 1.3, "是否注册保存进度？", shape="diamond")
    c.add("reg", 5.0, 1.7, 3.9, 1.05, "注册 / 登录 → 进度云同步 → 今日首页", fc=BLUE_L, ec=BLUE)
    c.add("guest", 8.4, 1.7, 3.0, 1.0, "暂不注册（游客模式继续，进度存本地）", fc=GRAY_L, ec=GRAY)
    c.link("start", "land")
    c.link("land", "setup")
    c.link("setup", "learn5")
    c.link("learn5", "done5")
    c.link("done5", "reg?")
    c.link("reg?", "reg", "是")
    c.link("reg?", "guest", "否")
    note(c.ax, 8.4, 3.6, "注：老用户直接登录即可\n回到“今日首页”，跳过此漏斗")
    save(fig, "f1_funnel.png")


# ---------------------------------------------------------------- F2 每日学习总流程
def f2_daily():
    fig, c = new_fig()
    c.add("start", 5.0, 15.2, 3.8, 1.0, "进入今日首页", shape="ellipse")
    c.add("calc", 5.0, 13.4, 3.9, 1.1, "计算今日任务：到期复习词 + 新词配额")
    c.add("rev?", 5.0, 11.2, 3.7, 1.3, "有到期复习？", shape="diamond")
    c.add("review", 5.0, 8.8, 3.9, 1.15, "复习队列：四选一自测\n（逐张完成）", fc=BLUE_L, ec=BLUE)
    c.add("skip", 2.1, 8.8, 3.4, 0.95, "无到期复习\n直接跳过复习环节", fc=GRAY_L, ec=GRAY)
    c.add("new", 4.0, 6.4, 3.9, 1.05, "学习今日新词（卡片自评，N 个）", fc=GREEN_L, ec=GREEN)
    c.add("finish", 4.0, 3.9, 3.9, 1.1, "今日完成页：打卡 +1\n连续学习天数更新", fc=GREEN_L, ec=GREEN)
    c.add("end", 4.0, 1.4, 3.9, 1.0, "生成明日复习任务，结束今日", shape="ellipse")
    c.link("start", "calc")
    c.link("calc", "rev?")
    c.link("rev?", "review", "是")
    c.link("rev?", "skip", "否")
    c.link("review", "new")
    c.link("skip", "new")
    c.link("new", "finish")
    c.link("finish", "end")
    note(c.ax, 8.3, 9.0, "顺序原则：先复习\n（清积压，符合遗忘曲线）\n再学新词")
    save(fig, "f2_daily.png")


# ---------------------------------------------------------------- F3 新词学习自评
def f3_new_word():
    fig, c = new_fig()
    c.add("start", 5.0, 15.2, 3.8, 1.0, "开始一轮新词学习", shape="ellipse")
    c.add("card", 5.0, 12.8, 3.9, 1.5, "展示单词卡片\n单词 / 音标 / 词性 / 释义 / 例句")
    c.add("self?", 5.0, 10.3, 3.6, 1.5, "用户自评是否认识？", shape="diamond")
    c.add("known", 7.9, 7.9, 3.4, 1.4, "认识：进入复习序列\n间隔 1 天 → 3 天 → 7 天递增", fc=GREEN_L, ec=GREEN)
    c.add("fuzzy", 5.0, 7.9, 3.4, 1.4, "模糊：短间隔重测\n（本轮稍后重现一次）\n计入明日复习", fc=ORANGE_L, ec=ORANGE)
    c.add("unknown", 2.1, 7.9, 3.4, 1.4, "不认识：本轮末尾\n重新出现，重学一遍\n直至本轮内记忆成功", fc=RED_L, ec=RED)
    c.add("empty", 5.0, 4.0, 3.6, 1.0, "本轮新词队列清空", shape="ellipse")
    c.link("start", "card")
    c.link("card", "self?")
    c.link("self?", "known", "认识", color=GREEN)
    c.link("self?", "fuzzy", "模糊", color=ORANGE)
    c.link("self?", "unknown", "不认识", color=RED)
    c.link("known", "empty")
    c.link("fuzzy", "empty")
    c.link("unknown", "empty")
    c.link("unknown", "card", "本轮重学", color=RED, fs=8)
    note(c.ax, 8.5, 5.2, "认识与模糊的词\n进入复习队列按计划复习；\n不认识的在当轮内反复学")
    save(fig, "f3_new_word.png")


# ---------------------------------------------------------------- F4 复习四选一与间隔决策
def f4_review():
    fig, c = new_fig()
    c.add("start", 5.0, 15.2, 3.8, 1.0, "复习队列开始", shape="ellipse")
    c.add("card", 5.0, 13.2, 3.9, 1.3, "展示单词 + 音标\n（隐藏释义与例句）")
    c.add("ans?", 5.0, 10.9, 3.6, 1.5, "四选一选义作答", shape="diamond")
    c.add("correct", 7.8, 8.7, 3.5, 1.5, "回答正确：记忆等级 +1\n选择下一步间隔\n（1 / 3 / 7 / 14 / 30 天）", fc=GREEN_L, ec=GREEN)
    c.add("wrong", 2.2, 8.7, 3.5, 1.5, "回答错误：记忆等级清零\n标记为重学 → 进入本日\n待复习队尾 → 明日优先", fc=RED_L, ec=RED)
    c.add("next?", 5.0, 6.0, 3.5, 1.2, "队列还有下一张？", shape="diamond")
    c.add("done", 5.0, 2.6, 3.9, 1.2, "今日复习完成（到期清空）", fc=GREEN_L, ec=GREEN)
    c.link("start", "card")
    c.link("card", "ans?")
    c.link("ans?", "correct", "正确", color=GREEN)
    c.link("ans?", "wrong", "错误", color=RED)
    c.link("correct", "next?")
    c.link("wrong", "next?")
    c.link("next?", "done", "否")
    c.link("next?", "ans?", "是", fs=8)
    note(c.ax, 8.4, 4.3, "错误重学后当轮内\n再次出现在队尾，直到答对；\n明日复习优先排期")
    save(fig, "f4_review.png")


# ---------------------------------------------------------------- F5 缺席分批容错
def f5_backlog():
    fig, c = new_fig()
    c.add("start", 5.0, 15.2, 3.8, 1.0, "缺席几天后回来学习", shape="ellipse")
    c.add("calc", 5.0, 13.4, 4.2, 1.2, "统计到期未复习的积压量 X\n（缺席期间未到期词顺延排队）")
    c.add("cmp?", 5.0, 11.2, 4.0, 1.4, "X ≤ 每日新词上限\n（如 ≤ 20）?", shape="diamond")
    c.add("all", 2.3, 8.6, 3.5, 1.4, "是：全部并入今日任务\n一次性正常消化", fc=GREEN_L, ec=GREEN)
    c.add("batch", 7.7, 8.6, 3.7, 1.6, "否：分批摊开\n按每日上限拆成多批\n今日先消化第一批", fc=ORANGE_L, ec=ORANGE)
    c.add("new", 5.0, 5.6, 4.0, 1.1, "复习完成 → 进入今日新词学习")
    c.add("done", 5.0, 3.0, 4.0, 1.2, "恢复到正常学习节奏\n（不给缺席惩罚）", fc=GREEN_L, ec=GREEN)
    c.link("start", "calc")
    c.link("calc", "cmp?")
    c.link("cmp?", "all", "是", color=GREEN)
    c.link("cmp?", "batch", "否", color=ORANGE)
    c.link("all", "new")
    c.link("batch", "new")
    c.link("new", "done")
    note(c.ax, 8.5, 11.3, "分批规则：剩余批次\n按每日上限自动消化，\n约 D 天内追平进度")
    save(fig, "f5_backlog.png")


# ---------------------------------------------------------------- F6 词书切换
def f6_switch():
    fig, c = new_fig()
    c.add("start", 5.0, 15.2, 3.9, 1.0, "在统计 / 设置中选择新词书", shape="ellipse")
    c.add("pick", 5.0, 13.3, 4.2, 1.2, "选择目标词书 + 可选小目标\n（只背前 N 词）")
    c.add("confirm", 5.0, 11.2, 3.0, 1.0, "确认切换")
    c.add("newbook", 2.4, 8.4, 3.6, 1.5, "新词书从第 1 个词开始\n进入“新词学习”队列", fc=BLUE_L, ec=BLUE)
    c.add("oldbook", 7.6, 8.4, 3.8, 1.4, "原词书复习任务保留并行\n不受切换影响", fc=GRAY_L, ec=GRAY)
    c.add("merge", 5.0, 5.6, 4.0, 1.1, "统计合并展示：总掌握率\n+ 各词书独立进度")
    c.add("end", 5.0, 3.0, 4.0, 1.1, "可随时切回原词书\n各词书进度互不干扰", shape="ellipse")
    c.link("start", "pick")
    c.link("pick", "confirm")
    c.link("confirm", "newbook")
    c.link("confirm", "oldbook")
    c.link("newbook", "merge")
    c.link("oldbook", "merge")
    c.link("merge", "end")
    note(c.ax, 5.0, 0.9, "各词书独立队列，切换不丢失任何进度", fs=9)
    save(fig, "f6_switch.png")


if __name__ == "__main__":
    from matplotlib import font_manager

    fonts = sorted({f.name for f in font_manager.fontManager.ttflist})
    print("检测到可用 CJK 字体:", [f for f in fonts if any(
        k in f for k in ("YaHei", "SimHei", "PingFang", "Noto Sans CJK"))])
    f1_funnel()
    f2_daily()
    f3_new_word()
    f4_review()
    f5_backlog()
    f6_switch()