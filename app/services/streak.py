"""打卡与连续天数（FR-08）：以自然日计，用户所在时区（MVP 用服务器时区）。

streak 计算规则：
- 若今日已打卡，从今日往回数连续天数；
- 若今日未打卡，则从昨日往回数（今日尚未结束，次数仍有效）。
"""

from datetime import date, timedelta


def _consecutive(days: set[date], start: date) -> int:
    count = 0
    cur = start
    while cur in days:
        count += 1
        cur = cur - timedelta(days=1)
    return count


def streak_days(checkin_days: set[date], today: date | None = None) -> int:
    today = today or date.today()
    if today in checkin_days:
        return _consecutive(checkin_days, today)
    return _consecutive(checkin_days, today - timedelta(days=1))


def is_streak_alive(checkin_days: set[date], today: date | None = None) -> bool:
    today = today or date.today()
    return today in checkin_days or (today - timedelta(days=1)) in checkin_days