from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings

from .database import init_db

from .routes import router


BASE_DIR = Path(
    __file__
).resolve().parent.parent


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()

    yield


app = FastAPI(
    title=settings.app_name,

    description=(
        "AI-powered 7-day fitness plan "
        "generator using Gemini and SQLite."
    ),

    version="1.0.0",

    lifespan=lifespan,
)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    https_only=False,
    same_site="lax"
)


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static"
)


app.include_router(router)


@app.get("/health", tags=["system"])
def health():

    return {
        "status": "ok",
        "service": "fitbuddy"
    }