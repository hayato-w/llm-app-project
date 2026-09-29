from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorHandler(Exception):
    def __init__(self, status_code: int, title: str, detail: str):
        self.status_code = status_code
        self.title = title
        self.detail = detail


async def error_handler(request: Request, exc: ErrorHandler) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"title": exc.title, "detail": exc.detail},
    )
