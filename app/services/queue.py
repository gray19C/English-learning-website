from datetime import date, datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Book, BookWord, User, UserBook, UserWordState
from .backlog import batch_plan, review_cap


def today_date() -> date:
    return date.today() + timedelta(hours=settings.timezone_offset_hours)


def now_local() -> datetime:
    return datetime.now() + timedelta(hours=settings.timezone_offset_hours)


def active_books(db: Session, user_id: int) -> list[UserBook]:
    return list(
        db.scalars(
            select(UserBook).where(UserBook.user_id == user_id).order_by(UserBook.book_id)
        )
    )


def alloc_new_words(db: Session, user: User) -> list[tuple[int, int]]:
    """全局每日新词分配：按词书顺序填满 daily_new_words，返回 [(book_id, word_id)]。"""
    remaining = user.daily_new_words
    result: list[tuple[int, int]] = []
    for ub in active_books(db, user.id):
        if remaining <= 0:
            break
        word_ids = pick_new_words(db, user.id, ub.book_id, remaining)
        result.extend((ub.book_id, wid) for wid in word_ids)
        remaining -= len(word_ids)
    return result


def new_word_position(db: Session, user_id: int, book_id: int) -> int:
    """该词书下一个待学新词的 book_words.position（已学最大 position + 1）。"""
    max_pos = db.scalar(
        select(func.max(BookWord.position))
        .select_from(BookWord)
        .where(
            BookWord.book_id == book_id,
            BookWord.word_id.in_(
                select(UserWordState.word_id).where(
                    UserWordState.user_id == user_id,
                    UserWordState.book_id == book_id,
                )
            ),
        )
    )
    return (max_pos or 0) + 1


def pick_new_words(db: Session, user_id: int, book_id: int, count: int) -> list[int]:
    start = new_word_position(db, user_id, book_id)
    rows = db.execute(
        select(BookWord.word_id)
        .where(BookWord.book_id == book_id, BookWord.position >= start)
        .order_by(BookWord.position)
        .limit(count)
    ).all()
    return [r[0] for r in rows]


def due_reviews(db: Session, user_id: int, book_id: int, today) -> list[int]:
    rows = db.execute(
        select(UserWordState.word_id)
        .where(
            UserWordState.user_id == user_id,
            UserWordState.book_id == book_id,
            UserWordState.level >= 1,
            UserWordState.next_review_date <= today,
        )
        .order_by(UserWordState.next_review_date, UserWordState.word_id)
    ).all()
    return [r[0] for r in rows]


def review_session_queue(db: Session, user: User, today=None) -> tuple[list[tuple[int, int]], int, int]:
    """今日复习会话：跨词书合并到期词，按上限分批。

    返回 (today_batch 的 [(book_id, word_id)], 顺延数, 上限值)。
    """
    today = today or today_date()
    all_due: list[tuple[int, int]] = []
    for ub in active_books(db, user.id):
        all_due.extend((ub.book_id, wid) for wid in due_reviews(db, user.id, ub.book_id, today))

    cap = review_cap(user.daily_new_words, settings.review_cap_multiplier)
    today_batch, deferred = batch_plan(len(all_due), cap)
    return all_due[:today_batch], deferred, cap


def build_today_tasks(db: Session, user: User, today=None) -> dict:
    """今日首页任务面板（FR-03）。"""
    today = today or today_date()
    new_items = alloc_new_words(db, user)
    due_items, deferred, cap = review_session_queue(db, user, today)

    new_by_book: dict[int, int] = {}
    for book_id, _ in new_items:
        new_by_book[book_id] = new_by_book.get(book_id, 0) + 1
    due_by_book: dict[int, int] = {}
    for book_id, _ in due_items:
        due_by_book[book_id] = due_by_book.get(book_id, 0) + 1

    return {
        "today": today,
        "due_total": len(due_items) + deferred,
        "due_today": len(due_items),
        "due_deferred": deferred,
        "new_total": len(new_items),
        "review_cap": cap,
        "book_data": [
            {
                "book_id": ub.book_id,
                "due": due_by_book.get(ub.book_id, 0),
                "new": new_by_book.get(ub.book_id, 0),
            }
            for ub in active_books(db, user.id)
        ],
        "has_review": len(due_items) > 0,
        "main_button": "review" if due_items else "new",
    }


def book_progress(db: Session, user_id: int, book_id: int, small_goal: int | None) -> tuple[int, int]:
    learned = db.scalar(
        select(func.count())
        .select_from(UserWordState)
        .where(
            UserWordState.user_id == user_id,
            UserWordState.book_id == book_id,
            UserWordState.level >= 1,
        )
    ) or 0
    total = small_goal or (db.get(Book, book_id).word_count if db.get(Book, book_id) else 0)
    return learned, total