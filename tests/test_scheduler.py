from datetime import date

from app.services.scheduler import (
    next_review_date,
    schedule_new_word,
    schedule_review,
)


def test_schedule_new_word_known_is_level2():
    assert schedule_new_word("known") == 2


def test_schedule_new_word_fuzzy_is_level1():
    assert schedule_new_word("fuzzy") == 1


def test_schedule_new_word_unknown_returns_none():
    assert schedule_new_word("unknown") is None


def test_schedule_review_correct_upgrades_capped_at5():
    assert schedule_review(1, True) == 2
    assert schedule_review(3, True) == 4
    assert schedule_review(5, True) == 5


def test_schedule_review_wrong_falls_to_level1():
    assert schedule_review(4, False) == 1


def test_interval_table():
    assert next_review_date(1, date(2026, 9, 22)) == date(2026, 9, 23)
    assert next_review_date(2, date(2026, 9, 22)) == date(2026, 9, 25)
    assert next_review_date(3, date(2026, 9, 22)) == date(2026, 9, 29)
    assert next_review_date(4, date(2026, 9, 22)) == date(2026, 10, 6)
    assert next_review_date(5, date(2026, 9, 22)) == date(2026, 10, 22)


def test_deterministic_sequence():
    """FR-06 验收：给定初始状态与作答序列，间隔序列可复现。

    间隔从本次复习日起算（FR-06）：L1 首学(09-22) → 答对 L2 (09-25)
    → 答对 L3 (10-02) → 答对 L4 (10-16) → 答对 L5 (11-15) → 保持 L5(12-15)。
    """
    today = date(2026, 9, 22)
    level = schedule_new_word("fuzzy")  # L1
    assert level == 1
    first = True
    days = []
    for correct in (True, True, True, True, True):
        level = schedule_review(level, correct)
        next_day = next_review_date(level, today)
        days.append((level, next_day))
        today = next_day
        if first:
            first = False
    assert [d[0] for d in days] == [2, 3, 4, 5, 5]
    assert days[0][1] == date(2026, 9, 25)
    assert days[1][1] == date(2026, 10, 2)
    assert days[2][1] == date(2026, 10, 16)
    assert days[3][1] == date(2026, 11, 15)
    assert days[4][1] == date(2026, 12, 15)