"""ECDICT 词表导入（M1）：从 ecdict.csv 派生三本词书并按词频排序。

用法：先 init_db 建表，再运行 python -m app.seed.import_ecdict
幂等：内容表（books/words/book_words）先清空再全量重建。
"""

import csv
from pathlib import Path

from sqlalchemy import text

from ..database import SessionLocal
from ..models import Book, BookWord, Word

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "ecdict.csv"

BOOK_DEFS = {
    "cet4": {"name": "四级核心", "difficulty": "CET-4", "desc": "四六级考试四级核心词汇，按词频降序。"},
    "cet6": {"name": "六级（含四级）", "difficulty": "CET-6", "desc": "六级备考词表（含四级词汇），按词频降序。"},
    "ky": {"name": "考研高频", "difficulty": "考研", "desc": "全国硕士研究生考试高频词汇，按词频降序。"},
}

ALLOWED = ("cet4", "cet6", "ky")


def clean_definition(raw: str) -> str:
    if not raw:
        return ""
    text = raw.replace("\\n", "； ").replace("\n", "； ")
    parts = [p.strip(" ;；") for p in text.split("；") if p.strip(" ;；")]
    return "；".join(parts)[:512]


def scan() -> dict:
    """返回 word -> info，覆盖三本词书词条合集。"""
    union: dict[str, dict] = {}
    book_words: dict[str, set[str]] = {k: set() for k in ALLOWED}
    with open(DATA_FILE, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if len(row) < 13:
                continue
            word = row[0].strip()
            if not word:
                continue
            tag = row[7] or ""
            flags = [k for k in ALLOWED if k in tag]
            if not flags:
                continue
            for k in flags:
                book_words[k].add(word)
            if word in union:
                continue
            frq = row[9].strip()
            bnc = row[8].strip()
            rank = 0
            for v in (frq, bnc):
                if v.isdigit() and int(v) > 0:
                    rank = int(v)
                    break
            union[word] = {
                "phonetic": row[1].strip(),
                "pos": row[4].strip(),
                "definition": clean_definition(row[3]) or row[2].strip()[:512],
                "rank": rank,
            }
    # 六级（含四级）：cet6 并入 cet4 词集
    book_words["cet6"] |= book_words["cet4"]
    return union, book_words


def main() -> None:
    if not DATA_FILE.exists():
        raise SystemExit(f"缺少词表文件：{DATA_FILE}。请先下载 ECDICT csv 放到 data/ 目录。")

    union, book_words = scan()

    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM book_words"))
        db.execute(text("DELETE FROM feedback"))
        db.execute(text("DELETE FROM answer_log"))
        db.execute(text("DELETE FROM user_word_state"))
        db.execute(text("DELETE FROM user_books"))
        db.execute(text("DELETE FROM checkins"))
        db.execute(text("DELETE FROM events"))
        db.execute(text("DELETE FROM words"))
        db.execute(text("DELETE FROM books"))
        db.commit()

        # words
        word_ids: dict[str, int] = {}
        for i, (w, info) in enumerate(union.items(), start=1):
            obj = Word(
                text=w,
                phonetic=info["phonetic"],
                pos=info["pos"],
                definition=info["definition"],
                example=None,
                frequency_rank=info["rank"],
            )
            db.add(obj)
            if i % 5000 == 0:
                db.flush()
        db.flush()

        for obj in db.query(Word).all():
            word_ids[obj.text] = obj.id
        db.commit()

        # books
        books = {}
        for slug, meta in BOOK_DEFS.items():
            b = Book(slug=slug, name=meta["name"], difficulty=meta["difficulty"], description=meta["desc"])
            db.add(b)
            books[slug] = b
        db.flush()

        # book_words by frequency rank
        for slug, words_set in book_words.items():
            items = [(word_ids[w], union[w]["rank"], w) for w in words_set if w in word_ids]
            items.sort(key=lambda x: (x[1] or 10 ** 9, x[2]))
            for pos, (wid, _rank, _w) in enumerate(items, start=1):
                db.add(BookWord(book_id=books[slug].id, word_id=wid, position=pos))
            books[slug].word_count = len(items)

        db.commit()

        for slug in ALLOWED:
            b = db.query(Book).filter(Book.slug == slug).first()
            print(f"{b.name}: {b.word_count} 词")
    finally:
        db.close()


if __name__ == "__main__":
    main()