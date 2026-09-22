from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routers import auth, learn, misc, pages, review

app = FastAPI(title="英语学习网站 MVP")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(learn.router)
app.include_router(review.router)
app.include_router(misc.router)