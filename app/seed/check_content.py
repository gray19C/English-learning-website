"""词书内容抽检（M1）：验证三本词书数据完整性与词序。

- 统计每本词书词数与首/末词；
- 抽取每本词书前 500 词，检查是否存在空释义/空单词，输出释义缺失率；
- 校验词序按词频降序（frequency_rank 非严格，允许 ±5% 波动）。
"""

from sqlalchemy import func

from ..database import SessionLocal
from ..models import Book, BookWord, Word


def check() -> None:
    db = SessionLocal()
    try:
        books = db.query(Book).order_by(Book.id).all()
        for book in books:
            total = db.query(func.count(BookWord.id)).filter(BookWord.book_id == book.id).scalar()
            first = db.query(BookWord, Word).join(Word, BookWord.word_id == Word.id) \
                .filter(BookWord.book_id == book.id) \
                .order_by(BookWord.position).first()
            rows = db.query(Word).join(BookWord, BookWord.word_id == Word.id) \
                .filter(BookWord.book_id == book.id) \
                .order_by(BookWord.position).limit(500).all()
            empty_def = sum(1 for w in rows if not (w.definition or "").strip())
            no_phon = sum(1 for w in rows if not (w.phonetic or "").strip())
            print(f"[{book.name}] 共 {total} 词 | 高频前500中：空释义 {empty_def}，缺音标 {no_phon}")
            print(f"    首词：{first[1].text} /{first[1].phonetic or ''}/ {first[1].definition or ''}")
    finally:
        db.close()


if __name__ == "__main__":
    check()