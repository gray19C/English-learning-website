from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import current_user
from ..config import settings
from ..database import get_db
from ..models import Book, Event, Feedback, User, UserBook, Word
from ..services.queue import active_books
from ..services.words import card_dict

router = APIRouter(prefix="/api", tags=["misc"])


class FeedbackIn(BaseModel):
    book_id: int
    word_id: int
    mode: str = "learn"
    note: str | None = None


class EventIn(BaseModel):
    name: str
    props: dict | None = None


class SettingsIn(BaseModel):
    daily_new_words: int


class BookActivateIn(BaseModel):
    book_id: int
    small_goal: int | None = None


@router.get("/guest/queue")
def guest_queue(db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.slug == "cet4").first()
    if not book:
        return {"ok": False, "error": "词书未就绪"}
    from ..models import BookWord
    rows = (
        db.query(BookWord.word_id)
        .filter(BookWord.book_id == book.id)
        .order_by(BookWord.position)
        .limit(settings.guest_trial_words)
        .all()
    )
    items = [card_dict(db.get(Word, r[0])) for r in rows]
    return {"ok": True, "book_id": book.id, "items": items}


@router.post("/guest/answer")
def guest_answer(data: EventIn):
    return {"ok": True}


@router.post("/feedback", status_code=201)
def submit_feedback(
    data: FeedbackIn,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user),
):
    fb = Feedback(
        user_id=user.id if user else None,
        book_id=data.book_id,
        word_id=data.word_id,
        mode=data.mode,
        note=data.note,
    )
    db.add(fb)
    db.commit()
    return {"ok": True, "id": fb.id}


@router.post("/events")
def track_event(data: EventIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    db.add(Event(user_id=user.id if user else None, name=data.name, props=data.props))
    db.commit()
    return {"ok": True}


@router.post("/settings")
def update_settings(data: SettingsIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    user.daily_new_words = data.daily_new_words
    db.commit()
    return {"ok": True}


@router.post("/books/activate")
def activate_book(data: BookActivateIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    book = db.get(Book, data.book_id)
    if not book:
        return {"ok": False, "error": "词书不存在"}
    if not db.query(UserBook).filter_by(user_id=user.id, book_id=data.book_id).first():
        db.add(UserBook(user_id=user.id, book_id=data.book_id, small_goal=data.small_goal))
        db.commit()
    return {"ok": True}


@router.post("/books/deactivate")
def deactivate_book(data: BookActivateIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    if len(active_books(db, user.id)) <= 1:
        return {"ok": False, "error": "至少保留一本词书"}
    db.query(UserBook).filter_by(user_id=user.id, book_id=data.book_id).delete()
    db.commit()
    return {"ok": True}