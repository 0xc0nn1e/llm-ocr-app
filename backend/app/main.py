from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.errors import AppError
from app.routers import upload

app = FastAPI(title="画像OCR・説明文生成API")

app.include_router(upload.router)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert any AppError into a consistent structured JSON response.

    Response shape:
        {"error": {"code": "<ERROR_CODE>", "message": "<JAPANESE_ERROR_MESSAGE>"}}

    This gives the frontend a stable `code` to branch on while `message`
    stays human-readable and translatable.
    """
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": {"code": exc.code.value, "message": exc.message}},
    )

@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}