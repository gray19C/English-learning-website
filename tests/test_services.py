from datetime import datetime, date

from app.models import AnswerLog, UserWordState
from app.services.checkin import checkin_if_done, new_words_done, reviews_done
from app.services.queue import alloc_new_words, build_today_tasks, review_session_queue
from app.services.scheduler import next_review_date, schedule_new_word

from .conftest import seed_book, seed_user


def test_today_tasks_new_words_selected(db):
    seed_book(db)
    user = seed_user(db, daily=10)
    tasks = build_today_tasks(db, user)
    assert tasks["new_total"] == 10
    assert tasks["due_today"] == 0
    assert tasks["main_button"] == "new"
    assert tasks["review_cap"] == 30


def test_learn_moves_position(db):
    seed_book(db)
    user = seed_user(db, daily=10)
    first = alloc_new_words(db, user)
    assert first[0][0] == 1  # book_id
    assert first[0][1] == 1  # word 1 first（position=1）

    for book_id, wid in first:
        level = schedule_new_word("known")
        db.add(UserWordState(user_id=user.id, book_id=book_id, word_id=wid,
                             level=level, next_review_date=next_review_date(level, date.today()),
                             first_learned_at=datetime.now()))
        db.add(AnswerLog(user_id=user.id, book_id=book_id, word_id=wid, kind="new_self",
                         result="known", level_before=0, level_after=level))
    db.commit()

    tasks = build_today_tasks(db, user)
    second = alloc_new_words(db, user)
    assert second[0][1] == 11  # 下一批从第 11 词开始


def test_review_session_queue_batches_backlog(db):
    seed_book(db)
    user = seed_user(db, daily=10)  # cap = 30
    today = date.today()
    for i in range(1, 41):
        db.add(UserWordState(user_id=user.id, book_id=1, word_id=i, level=1,
                             next_review_date=today))
    db.commit()
    batch, deferred, cap = review_session_queue(db, user, today)
    assert cap == 30
    assert len(batch) == 30
    assert deferred == 10


def test_checkin_requires_all_new_words(db):
    seed_book(db)
    user = seed_user(db, daily=10)
    done, rated = new_words_done(db, user, date.today())
    assert done is False
    assert reviews_done(db, user, date.today())[0] is True  # 无复习视为完成
    assert checkin_if_done(db, user) is False  # 未学新词不打卡


def test_checkin_after_learning_all_new(db):
    seed_book(db)
    user = seed_user(db, daily=10)
    for i in range(1, 11):
        level = schedule_new_word("known")
        db.add(UserWordState(user_id=user.id, book_id=1, word_id=i, level=level,
                             next_review_date=next_review_date(level, date.today()),
                             first_learned_at=datetime.now()))
        db.add(AnswerLog(user_id=user.id, book_id=1, word_id=i, kind="new_self", result="known",
                         level_before=0, level_after=level))
    db.commit()
    assert checkin_if_done(db, user) is True
    assert checkin_if_done(db, user) is False  # 重复不重复加