from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Book, Checkin, UserBook, UserWordState
from .queue import active_books, new_word_position
from .streak import streak_days
from ..models import Word


def user_stats(db: Session, user_id: int, today) -> dict:
    mastered = db.scalar(
        select(func.count())
        .select_from(UserWordState)
        .where(UserWordState.user_id == user_id, UserWordState.level >= 3)
    ) or 0

    learning = db.scalar(
        select(func.count())
        .select_from(UserWordState)
        .where(
            UserWordState.user_id == user_id,
            UserWordState.level >= 1,
            UserWordState.level < 3,
        )
    ) or 0

    checkin_days = set(db.scalars(select(Checkin.day).where(Checkin.user_id == user_id)))
    streak = streak_days(checkin_days, today)

    book_rows = []
    for ub in active_books(db, user_id):
        book = db.get(Book, ub.book_id)
        learned = db.scalar(
            select(func.count())
            .select_from(UserWordState)
            .where(
                UserWordState.user_id == user_id,
                UserWordState.book_id == ub.book_id,
                UserWordState.level >= 1,
            )
        ) or 0
        total = ub.small_goal or book.word_count
        next_pos = new_word_position(db, user_id, ub.book_id)
        book_rows.append(
            {
                "book": book,
                "learned": learned,
                "total": total,
                "percent": round(learned / total * 100) if total else 0,
                "next_pos": next_pos,
            }
        )

    return {
        "mastered": mastered,
        "learning": learning,
        "streak": streak,
        "books": book_rows,
        "today": today,
    }


def heatmap_last7(db: Session, user_id: int, today) -> list[dict]:
    from datetime import timedelta

    checkin_days = set(db.scalars(select(Checkin.day).where(Checkin.user_id == user_id)))
    days = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        days.append({"day": day, "checked": day in checkin_days})
    return days