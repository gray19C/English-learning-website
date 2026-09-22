from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from ..auth import create_token, current_user, hash_password, verify_password, settings
from ..database import get_db
from ..models import User
from ..services.queue import active_books, today_date

router = APIRouter(prefix="/api", tags=["auth"])


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nickname: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class GuestItem(BaseModel):
    word_id: int
    result: str
    book_id: int | None = None


class OnboardIn(BaseModel):
    daily_new_words: int = Field(default=20, ge=5, le=200)
    book_id: int
    small_goal: int | None = None
    guest_progress: list[GuestItem] = []


def set_auth_cookie(resp: Response, user_id: int) -> None:
    resp.set_cookie(
        settings.auth_cookie,
        create_token(user_id),
        max_age=settings.jwt_expire_days * 86400,
        httponly=True,
        samesite="lax",
    )


@router.post("/signup")
def signup(data: SignupIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        return {"ok": False, "error": "该邮箱已注册"}

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        nickname=data.nickname or data.email.split("@")[0],
        daily_new_words=settings.daily_new_words_default,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    resp = JSONResponse({"ok": True})
    set_auth_cookie(resp, user.id)
    return resp


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        return {"ok": False, "error": "邮箱或密码错误"}
    resp = JSONResponse({"ok": True})
    set_auth_cookie(resp, user.id)
    return resp


@router.post("/logout")
def logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(settings.auth_cookie)
    return resp


@router.post("/onboarding")
def onboarding(data: OnboardIn, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return {"ok": False, "error": "请先登录"}
    from ..models import BookWord, UserBook, UserWordState, AnswerLog
    from ..services.scheduler import schedule_new_word
    from ..services.words import card_dict

    ub = db.query(UserBook).filter(UserBook.user_id == user.id, UserBook.book_id == data.book_id).first()
    if not ub:
        ub = UserBook(user_id=user.id, book_id=data.book_id, small_goal=data.small_goal)
        db.add(ub)

    user.daily_new_words = data.daily_new_words
    if data.small_goal is not None:
        ub.small_goal = data.small_goal

    for item in data.guest_progress:
        if item.book_id != data.book_id:
            continue
        level = schedule_new_word(item.result)
        if level is None:
            continue
        st = db.query(UserWordState).filter_by(
            user_id=user.id, book_id=data.book_id, word_id=item.word_id
        ).first()
        if not st:
            st = UserWordState(user_id=user.id, book_id=data.book_id, word_id=item.word_id)
            db.add(st)
        st.level = max(st.level or 0, level)
        from ..services.scheduler import next_review_date
        st.next_review_date = next_review_date(st.level, today_date())
        st.first_learned_at = st.first_learned_at or __import__("datetime").datetime.now()
        db.add(AnswerLog(
            user_id=user.id, book_id=data.book_id, word_id=item.word_id,
            kind="new_self", result=item.result,
            level_before=0, level_after=st.level,
        ))

    db.commit()
    return {"ok": True}