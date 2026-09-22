from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    daily_new_words: Mapped[int] = mapped_column(Integer, default=20)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(16), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    phonetic: Mapped[str | None] = mapped_column(String(128), nullable=True)
    pos: Mapped[str | None] = mapped_column(String(32), nullable=True)
    definition: Mapped[str | None] = mapped_column(String(512), nullable=True)
    example: Mapped[str | None] = mapped_column(String(512), nullable=True)
    frequency_rank: Mapped[int] = mapped_column(Integer, default=0)


class BookWord(Base):
    __tablename__ = "book_words"
    __table_args__ = (UniqueConstraint("book_id", "word_id", name="uq_book_word"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), index=True)
    position: Mapped[int] = mapped_column(Integer, index=True)


class UserBook(Base):
    __tablename__ = "user_books"
    __table_args__ = (UniqueConstraint("user_id", "book_id", name="uq_user_book"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    small_goal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class UserWordState(Base):
    __tablename__ = "user_word_state"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", "word_id", name="uq_user_word_state"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), index=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_review_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    first_learned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AnswerLog(Base):
    __tablename__ = "answer_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))  # new_self / review_mcq / guest
    result: Mapped[str] = mapped_column(String(16))  # known / fuzzy / unknown / correct / wrong
    level_before: Mapped[int] = mapped_column(Integer, default=0)
    level_after: Mapped[int] = mapped_column(Integer, default=0)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)


class Checkin(Base):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_user_checkin"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    day: Mapped[date] = mapped_column(Date, index=True)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    mode: Mapped[str] = mapped_column(String(16))  # learn / review
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="open")  # open / fixed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    props: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)