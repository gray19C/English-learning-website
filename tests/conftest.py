import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./data_test.db")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app

# 确保所有模型已注册
from app import models  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def _prepare_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(_prepare_db):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    with TestClient(app) as c:
        yield c


def seed_book(db, book_id=1, slug="cet4", count=50):
    """插入一本基础词书（word_id 从 1..count，position=id）。"""
    from app.models import Book, BookWord, Word

    db.add(Book(id=book_id, slug=slug, name="四级核心", description="测试词书", difficulty="CET-4", word_count=count))
    for i in range(1, count + 1):
        db.add(Word(id=i, text=f"word{i}", phonetic=f"/w{i}/", pos="n.",
                    definition=f"释义{i}", frequency_rank=10000 - i))
        db.add(BookWord(book_id=book_id, word_id=i, position=i))
    db.commit()


def seed_user(db, email="a@b.com", daily=10, book_id=1):
    from app.auth import hash_password
    from app.models import User, UserBook

    user = User(id=1, email=email, password_hash=hash_password("abc123"), nickname="t", daily_new_words=daily)
    db.add(user)
    db.flush()
    db.add(UserBook(user_id=user.id, book_id=book_id))
    db.commit()
    return user