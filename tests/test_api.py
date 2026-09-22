from datetime import date, datetime

from app.models import UserWordState
from app.services.scheduler import next_review_date

from .conftest import seed_book, seed_user


def _signup_onboard(client, email="u@test.com", book_id=1, daily=10):
    r = client.post("/api/signup", json={"email": email, "password": "abc123"})
    assert r.json()["ok"]
    r = client.post("/api/onboarding", json={"daily_new_words": daily, "book_id": book_id, "guest_progress": []})
    assert r.json()["ok"]


def test_full_onboarding_then_learn_and_checkin(client, db):
    seed_book(db)
    _signup_onboard(client)

    q = client.get("/api/learn/queue").json()
    assert q["ok"] and q["total"] == 10

    for it in q["items"]:
        r = client.post("/api/learn/answer", json={"book_id": it["book_id"], "word_id": it["word_id"], "rating": "known"}).json()
        assert r["ok"] and r["level"] == 2

    rv = client.get("/api/review/queue").json()
    assert rv["ok"] and rv["questions"] == []  # 新词 3 天后才复习

    done = client.post("/api/learn/complete").json()
    assert done["checkin"] is True

    html = client.get("/today").text
    assert "今日任务" in html
    assert "连续" in html


def test_review_answer_correct_and_wrong(client, db):
    seed_book(db)
    _signup_onboard(client)

    # 造 2 个到期复习词
    from app.models import AnswerLog

    for wid in (1, 2):
        db.add(UserWordState(user_id=1, book_id=1, word_id=wid, level=2,
                             next_review_date=date.today(), first_learned_at=datetime.now()))
    db.add(AnswerLog(user_id=1, book_id=1, word_id=1, kind="new_self", result="known",
                     level_before=0, level_after=2))
    db.add(AnswerLog(user_id=1, book_id=1, word_id=2, kind="new_self", result="known",
                     level_before=0, level_after=2))
    db.commit()

    q = client.get("/api/review/queue").json()
    assert q["ok"] and len(q["questions"]) == 2
    q1, q2 = q["questions"]
    for question in (q1, q2):
        assert len(question["options"]) == 4           # 四选一
        assert len({o["text"] for o in question["options"]}) == 4  # 互不雷同

    # 答对 → 等级 +1
    r = client.post("/api/review/answer", json={
        "book_id": q1["book_id"], "word_id": q1["word_id"],
        "choice_word_id": q1["word_id"],
    }).json()
    assert r["correct"] is True and r["level_after"] == 3

    # 答错 → 回落 L1（词 2 完好的仍到期）
    wrong_choice = next(o["word_id"] for o in q2["options"] if o["word_id"] != q2["word_id"])
    r = client.post("/api/review/answer", json={
        "book_id": q2["book_id"], "word_id": q2["word_id"],
        "choice_word_id": wrong_choice,
    }).json()
    assert r["correct"] is False and r["level_after"] == 1


def test_guest_trial_returns_five_words(client, db):
    seed_book(db)
    q = client.get("/api/guest/queue").json()
    assert q["ok"] and len(q["items"]) == 5
    assert all("word" in i or "text" in i for i in q["items"])


def test_feedback_submission(client, db):
    seed_book(db)
    r = client.post("/api/feedback", json={"book_id": 1, "word_id": 1, "mode": "learn", "note": "释义有误"})
    assert r.status_code == 201
    assert r.json()["ok"]


def test_require_login(client, db):
    assert client.get("/today").status_code == 401
    assert client.get("/api/learn/queue").json()["ok"] is False