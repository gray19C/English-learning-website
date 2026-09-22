"""间隔调度引擎（确定性纯函数，可复现，FR-06）。

记忆等级 L1-L5，间隔 1 / 3 / 7 / 14 / 30 天。
- 新词自评：认识 → L2（3 天）；模糊 → L1（1 天）。
- 复习四选一：答对 → 等级 +1（封顶 L5，之后按 30 天循环）；答错 → 回落 L1 并回到今日队尾。
"""

from datetime import date, timedelta

KIND_NEW = "new_self"
KIND_REVIEW = "review_mcq"

RESULT_KNOWN = "known"
RESULT_FUZZY = "fuzzy"
RESULT_UNKNOWN = "unknown"
RESULT_CORRECT = "correct"
RESULT_WRONG = "wrong"

INTERVALS: dict[int, int] = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
MAX_LEVEL = 5


def interval_days(level: int) -> int:
    """按记忆等级返回间隔天数。"""
    return INTERVALS.get(level, 30)


def next_review_date(level: int, today: date) -> date:
    """间隔从本次复习日起算，非固定日期（FR-06）。"""
    return today + timedelta(days=interval_days(level))


def schedule_new_word(rating: str) -> int | None:
    """新词三态自评 -> 初始记忆等级。

    unknown（不认识）本轮回末重现，不产生调度结果，返回 None。
    """
    if rating == RESULT_KNOWN:
        return 2
    if rating == RESULT_FUZZY:
        return 1
    if rating == RESULT_UNKNOWN:
        return None
    raise ValueError(f"未知的自评结果: {rating}")


def schedule_review(level: int, correct: bool) -> int:
    """复习作答 -> 新记忆等级。

    答对：等级 +1（封顶 5）；答错：回落 L1。
    """
    if correct:
        return min((level or 0) + 1, MAX_LEVEL)
    return 1


def review_due_at(level: int, today: date) -> date:
    """给定当前等级与作答结果后的下一次复习时间。"""
    return next_review_date(level, today)