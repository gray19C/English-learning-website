"""词卡序列化与四选一干扰项生成（FR-05：干扰项随机取同词书其他词条释义）。"""

import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import BookWord, Word


def card_dict(word: Word | None) -> dict | None:
    if word is None:
        return None
    return {
        "id": word.id,
        "text": word.text,
        "phonetic": word.phonetic or "",
        "pos": word.pos or "",
        "definition": word.definition or "",
        "example": word.example or "",
    }


def review_question(db: Session, word: Word, book_id: int, distractors: int = 3) -> dict:
    """构造四选一题目：正确释义 + 同词书随机干扰项，返回脱敏后的题目数据。

    返回 {word_id, text, phonetic, options: [{text, word_id}], correct_word_id}。
    """
    options = [{"text": word.definition or "", "word_id": word.id}]

    same_book = db.execute(
        select(BookWord.word_id)
        .where(BookWord.book_id == book_id, BookWord.word_id != word.id)
        .limit(500)
    ).all()
    pool_ids = [r[0] for r in same_book]

    if len(pool_ids) < distractors:
        fallback = db.execute(select(Word.id).where(Word.id != word.id).limit(500)).all()
        pool_ids = [r[0] for r in fallback]

    chosen = set()
    for wid in random.sample(pool_ids, min(distractors, len(pool_ids))):
        if wid in chosen or wid == word.id:
            continue
        chosen.add(wid)
        w = db.get(Word, wid)
        if w and w.definition:
            options.append({"text": w.definition, "word_id": wid})
        if len(options) >= distractors + 1:
            break

    options_set = {o["text"] for o in options}
    if len(options_set) < 2:
        options = options[:1]
        options.append({"text": "——", "word_id": None})

    random.shuffle(options)
    return {
        "word_id": word.id,
        "text": word.text,
        "phonetic": word.phonetic or "",
        "options": options,
        "correct_word_id": word.id,
    }