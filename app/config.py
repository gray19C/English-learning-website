from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "英语学习网站 MVP"
    database_url: str = (
        "mysql+pymysql://english_app:english_app_pw@localhost:3306/english_mvp?charset=utf8mb4"
    )
    secret_key: str = "dev-secret-change-me-in-prod"
    jwt_expire_days: int = 30
    auth_cookie: str = "english_mvp_token"
    daily_new_words_default: int = 20
    review_cap_multiplier: int = 3
    guest_trial_words: int = 5
    timezone_offset_hours: int = 8

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()