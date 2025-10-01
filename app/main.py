import uvicorn
from fastapi import FastAPI
from app.api.routers.v1 import ocr_chunking

from app.config.settings import settings

app = FastAPI(title="OCR Chunking Microservice")

app.include_router(
    ocr_chunking.router,
    prefix="/api/v1",
    tags=["OCR Chunking"]
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
