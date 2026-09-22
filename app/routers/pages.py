from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..auth import current_user, require_user
from ..database import get_db
from ..models import Book, BookWord, User, Word
from ..services.checkin import new_words_done, reviews_done
from ..services.queue import active_books, build_today_tasks
from ..services.stats import heatmap_last7, user_stats

router = APIRouter(tags=["pages"])


def ctx(user: User | None) -> dict:
    return {"user": user, "books_all": Book}


@router.get("/")
def landing(request: Request, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    if user and active_books(db, user.id):
        return RedirectResponse("/today", status_code=302)
    books = db.query(Book).order_by(Book.id).all()
    return templates_render(request, "landing.html", {"books": books, "user": user})


@router.get("/books")
def books_app(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    from ..services.queue import book_progress
    stats = user_stats(db, user.id, None)
    all_books = db.query(Book).order_by(Book.id).all()
    return templates_render(request, "books.html", {"stats": stats, "books_all": all_books, "user": user})


@router.get("/books/{slug}")
def book_detail(request: Request, slug: str, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    book = db.query(Book).filter(Book.slug == slug).first()
    if not book:
        raise HTTPException(status_code=404, detail="词书不存在")
    rows = (
        db.query(BookWord, Word)
        .join(Word, BookWord.word_id == Word.id)
        .filter(BookWord.book_id == book.id)
        .order_by(BookWord.position)
        .limit(50)
        .all()
    )
    preview = [{"word": w.text, "phonetic": w.phonetic, "pos": w.pos, "definition": w.definition} for _, w in rows]
    return templates_render(request, "book_detail.html", {"book": book, "preview": preview, "user": user})


@router.get("/trial")
def trial(request: Request, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    return templates_render(request, "trial.html", {"user": user})


@router.get("/signup")
def signup_page(request: Request, user: User | None = Depends(current_user)):
    if user:
        return RedirectResponse("/onboarding", status_code=302)
    return templates_render(request, "signup.html", {"user": user})


@router.get("/login")
def login_page(request: Request, user: User | None = Depends(current_user)):
    if user:
        return RedirectResponse("/today", status_code=302)
    return templates_render(request, "login.html", {"user": user})


@router.get("/onboarding")
def onboarding_page(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if active_books(db, user.id):
        return RedirectResponse("/today", status_code=302)
    books = db.query(Book).order_by(Book.id).all()
    return templates_render(request, "onboarding.html", {"books": books, "user": user})


@router.get("/today")
def today(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    from sqlalchemy import select

    from ..models import Checkin
    from ..services.streak import streak_days

    tasks = build_today_tasks(db, user)
    heatmap = heatmap_last7(db, user.id, tasks["today"])
    checkin_days = set(db.scalars(select(Checkin.day).where(Checkin.user_id == user.id)))
    streak = streak_days(checkin_days, tasks["today"])
    context = {**tasks, "heatmap": heatmap, "streak": streak, "user": user}
    return templates_render(request, "today.html", context)


@router.get("/learn")
def learn(request: Request, user: User = Depends(require_user)):
    return templates_render(request, "learn.html", {"user": user})


@router.get("/review")
def review(request: Request, user: User = Depends(require_user)):
    return templates_render(request, "review.html", {"user": user})


@router.get("/done")
def done(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    from sqlalchemy import select

    from ..models import Checkin
    from ..services.streak import streak_days

    tasks = build_today_tasks(db, user)
    checkin_days = set(db.scalars(select(Checkin.day).where(Checkin.user_id == user.id)))
    streak = streak_days(checkin_days, tasks["today"])
    return templates_render(request, "done.html", {**tasks, "streak": streak, "user": user})


@router.get("/backlog")
def backlog(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    tasks = build_today_tasks(db, user)
    return templates_render(request, "backlog.html", {**tasks, "user": user})


@router.get("/stats")
def stats(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    tasks = build_today_tasks(db, user)
    data = user_stats(db, user.id, tasks["today"])
    heatmap = heatmap_last7(db, user.id, tasks["today"])
    return templates_render(request, "stats.html", {**data, "heatmap": heatmap, "user": user})


@router.get("/settings")
def settings(request: Request, user: User = Depends(require_user)):
    return templates_render(request, "settings.html", {"user": user})


def templates_render(request: Request, name: str, context: dict):
    from ..templates import templates
    return templates.TemplateResponse(request, name, context)