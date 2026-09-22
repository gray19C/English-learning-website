from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import current_user
from ..database import get_db
from ..models import AnswerLog, Event, User, UserWordState, Word
from ..services.checkin import checkin_if_done
from ..services.queue import alloc_new_words, today_date
from ..services.scheduler import next_review_date, schedule_new_word
from ..services.words import card_dict

router = APIRouter(prefix="/api/learn", tags=["learn"])


class AnswerIn(BaseModel):
    book_id: int
    word_id: int
    rating: str  # known / fuzzy / unknown


@router.get("/queue")
def learn_queue(db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    items = []
    for book_id, word_id in alloc_new_words(db, user):
        card = card_dict(db.get(Word, word_id))
        items.append({"book_id": book_id, "word_id": word_id, "card": card})
    return {"ok": True, "items": items, "total": len(items)}


@router.post("/answer")
def learn_answer(data: AnswerIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    st = db.query(UserWordState).filter_by(
        user_id=user.id, book_id=data.book_id, word_id=data.word_id
    ).first()

    level_after = 0
    if data.rating in ("known", "fuzzy"):
        level = schedule_new_word(data.rating)
        if not st:
            st = UserWordState(
                user_id=user.id, book_id=data.book_id, word_id=data.word_id,
                first_learned_at=datetime.now(),
            )
            db.add(st)
        old_level = st.level or 0
        st.level = max(old_level, level)
        st.next_review_date = next_review_date(st.level, today_date())
        st.last_review_at = datetime.now()
        level_after = st.level

    db.add(AnswerLog(
        user_id=user.id, book_id=data.book_id, word_id=data.word_id,
        kind="new_self", result=data.rating,
        level_before=st.level if st else 0, level_after=level_after,
    ))
    db.add(Event(user_id=user.id, name="new_word_self", props={"book_id": data.book_id, "word_id": data.word_id, "rating": data.rating}))
    db.commit()
    return {"ok": True, "level": level_after}


@router.post("/complete")
def learn_complete(db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    checkin = checkin_if_done(db, user)
    db.add(Event(user_id=user.id, name="learn_session_complete"))
    db.commit()
    return {"ok": True, "checkin": checkin}