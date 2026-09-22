"""初始化数据库表（幂等，表已存在则跳过）。"""
from app.database import Base, engine
import app.models  # noqa: F401  确保所有表注册到 Base.metadata


def init() -> None:
    Base.metadata.create_all(bind=engine)
    print("数据库表初始化完成。")


if __name__ == "__main__":
    init()