from app.services.backlog import batch_plan, review_cap


def test_batch_within_cap_all_today():
    today, deferred = batch_plan(10, 30)
    assert today == 10
    assert deferred == 0


def test_batch_over_cap_split():
    today, deferred = batch_plan(80, 60)
    assert today == 60
    assert deferred == 20


def test_batch_exact_cap():
    today, deferred = batch_plan(60, 60)
    assert today == 60
    assert deferred == 0


def test_batch_zero_due():
    assert batch_plan(0, 60) == (0, 0)


def test_review_cap_multiplier():
    assert review_cap(20, 3) == 60
    assert review_cap(5, 3) == 15
    assert review_cap(0, 3) == 1