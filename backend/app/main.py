from fastapi import FastAPI

from app.config import settings

app = FastAPI(title="画像OCR・説明文生成API")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}