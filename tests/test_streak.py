from datetime import date, timedelta

from app.services.streak import is_streak_alive, streak_days


def test_streak_counts_consecutive_from_today():
    today = date(2026, 9, 22)
    days = {today - timedelta(days=i) for i in range(5)}
    assert streak_days(days, today) == 5


def test_streak_alive_without_today():
    """今日未打卡但从昨日连续，次数仍有效。"""
    today = date(2026, 9, 22)
    days = {today - timedelta(days=i) for i in range(1, 4)}
    assert streak_days(days, today) == 3
    assert is_streak_alive(days, today) is True


def test_streak_broken_if_old():
    today = date(2026, 9, 22)
    days = {today - timedelta(days=2), today - timedelta(days=3)}
    assert streak_days(days, today) == 0
    assert is_streak_alive(days, today) is False


def test_streak_empty():
    assert streak_days(set(), date(2026, 9, 22)) == 0


def test_streak_continues_after_checkin():
    today = date(2026, 9, 22)
    days = {today - timedelta(days=1), today - timedelta(days=2)}  # 昨日/前日
    assert streak_days(days, today) == 2
    assert streak_days(days | {today}, today) == 3