from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAIError

from app.core.config import get_settings
from app.routers import chat, health, items

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(health.router)
app.include_router(items.router)
app.include_router(chat.router)


@app.exception_handler(OpenAIError)
def openai_error_handler(request: Request, exc: OpenAIError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/")
def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.app_name}"}
