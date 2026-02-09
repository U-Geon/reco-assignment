from fastapi import APIRouter
from app.api.v1.ocr import router as ocr_router

router = APIRouter()
router.include_router(ocr_router, prefix="/ocr", tags=["OCR"])