from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.handler import ErrorHandler, error_handler
from app.routers import chat, items, products

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.add_exception_handler(ErrorHandler, error_handler)

app.include_router(items.router)
app.include_router(products.router)
app.include_router(chat.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.app_name}"}
