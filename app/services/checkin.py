"""打卡判定（FR-08）：当日新词 + 当日复习批次全部完成才打卡。"""

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..models import AnswerLog, Checkin, User
from .queue import alloc_new_words, review_session_queue, today_date


def _distinct_result_count(db: Session, user_id: int, day, kind: str, results: tuple[str, ...]) -> int:
    return db.scalar(
        select(func.count()).select_from(
            select(AnswerLog.word_id)
            .where(
                AnswerLog.user_id == user_id,
                AnswerLog.kind == kind,
                AnswerLog.result.in_(results),
                func.date(AnswerLog.answered_at) == day,
            )
            .distinct()
            .subquery()
        )
    ) or 0


def new_words_done(db: Session, user: User, day) -> tuple[bool, int]:
    """今日需学新词是否全部进入复习序列（known/fuzzy）。"""
    available = len(alloc_new_words(db, user))
    rated = _distinct_result_count(db, user.id, day, "new_self", ("known", "fuzzy"))
    done = available > 0 and rated >= available
    return done, rated


def reviews_done(db: Session, user: User, day) -> tuple[bool, int]:
    """今日复习批次是否全部答对（答对词数 >= 今日批次）。"""
    due_today, _, _ = review_session_queue(db, user, day)
    if not due_today:
        return True, 0
    answered = _distinct_result_count(db, user.id, day, "review_mcq", ("correct",))
    return answered >= len(due_today), answered


def checkin_if_done(db: Session, user: User, day=None, force: bool = False) -> bool:
    """完成任务则打卡 +1；返回是否打卡成功。"""
    day = day or today_date()
    login_user = db.get(User, user.id) if user.id else user
    new_done, _ = new_words_done(db, login_user, day)
    review_done, _ = reviews_done(db, login_user, day)
    if force or (new_done and review_done):
        exists = db.scalar(
            select(Checkin.id).where(Checkin.user_id == user.id, Checkin.day == day)
        )
        if not exists:
            db.add(Checkin(user_id=user.id, day=day))
            db.commit()
            return True
    return False