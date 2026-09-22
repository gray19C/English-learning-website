"""缺席分批容错（FR-07）：纯函数，可单测。

每日复习上限 = 每日新词数 × 每日复习倍数（默认 ×3，待运营验证）。
积压 ≤ 上限 → 全部并入今日；积压 > 上限 → 今日消化第一批，其余顺延。
顺延的实现方式：不修改任何等级/日期，次日同一批仍处于"到期"状态，
再按同上限消化一批，自然做到「每日自动消化一批直至追平」。
"""


def batch_plan(due_count: int, cap: int) -> tuple[int, int]:
    """返回 (今日可消化数, 顺延数)。

    今日可消化数 = min(due_count, cap)，顺延数 = due_count - 今日可消化数。
    """
    today_batch = min(due_count, cap)
    return today_batch, max(0, due_count - today_batch)


def review_cap(daily_new_words: int, multiplier: int) -> int:
    return max(1, daily_new_words * multiplier)