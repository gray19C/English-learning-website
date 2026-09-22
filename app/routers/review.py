from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import current_user
from ..database import get_db
from ..models import AnswerLog, Event, User, UserWordState, Word
from ..services.checkin import checkin_if_done
from ..services.queue import review_session_queue, today_date
from ..services.scheduler import next_review_date, schedule_review
from ..services.words import card_dict, review_question

router = APIRouter(prefix="/api/review", tags=["review"])


class AnswerIn(BaseModel):
    book_id: int
    word_id: int
    choice_word_id: int


@router.get("/queue")
def review_queue(db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    due_items, deferred, cap = review_session_queue(db, user)
    questions = []
    for book_id, word_id in due_items:
        word = db.get(Word, word_id)
        q = review_question(db, word, book_id)
        q["book_id"] = book_id
        questions.append(q)
    return {"ok": True, "questions": questions, "deferred": deferred, "cap": cap}


@router.post("/answer")
def review_answer(data: AnswerIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    word = db.get(Word, data.word_id)
    st = db.query(UserWordState).filter_by(
        user_id=user.id, book_id=data.book_id, word_id=data.word_id
    ).first()
    level_before = st.level if st else 0
    correct = data.choice_word_id == data.word_id
    new_level = schedule_review(level_before, correct)

    if st is None:
        st = UserWordState(
            user_id=user.id, book_id=data.book_id, word_id=data.word_id,
            first_learned_at=datetime.now(),
        )
        db.add(st)
    if correct:
        st.level = new_level
        st.next_review_date = next_review_date(new_level, today_date())
    else:
        st.level = 1  # 答错回落 L1，回到今日队尾（客户端重排）; 答对后可升级
        st.next_review_date = today_date()
    st.last_review_at = datetime.now()

    db.add(AnswerLog(
        user_id=user.id, book_id=data.book_id, word_id=data.word_id,
        kind="review_mcq", result="correct" if correct else "wrong",
        level_before=level_before, level_after=st.level,
    ))
    db.add(Event(user_id=user.id, name="review_answer", props={"word_id": data.word_id, "correct": correct}))
    db.commit()
    return {
        "ok": True,
        "correct": correct,
        "level_after": st.level,
        "correct_definition": word.definition if word else "",
        "card": card_dict(word),
    }


@router.post("/complete")
def review_complete(db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    checkin = checkin_if_done(db, user)
    db.commit()
    return {"ok": True, "checkin": checkin}