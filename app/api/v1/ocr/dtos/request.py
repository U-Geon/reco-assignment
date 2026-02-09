from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class OCRWordDto(BaseModel):
    text: str = Field(..., description="인식된 단어 텍스트")
    boundingBox: Optional[Dict[str, Any]] = Field(None, description="단어의 좌표 정보 (vertices 등)")
    confidence: float = Field(0.0, description="단어 인식 신뢰도 (0.0 ~ 1.0)")

class OCRPageDto(BaseModel):
    text: str = Field(..., description="페이지 전체 텍스트")
    words: List[OCRWordDto] = Field(default_factory=list, description="페이지 내 단어 목록")
    confidence: float = Field(0.0, description="페이지 인식 신뢰도")
    width: Optional[int] = Field(None, description="이미지 너비")
    height: Optional[int] = Field(None, description="이미지 높이")

class OCRRequest(BaseModel):
    """
    OCR 엔진으로부터 전달받는 원본 데이터 요청 DTO
    """
    text: str = Field(..., description="OCR 전체 텍스트 (줄바꿈 포함)", json_schema_extra={"example": "** 계 량 확 인 서 ** \n(공급자 보관용)..."})
    pages: List[OCRPageDto] = Field(default_factory=list, description="페이지별 상세 정보")
    confidence: float = Field(0.0, description="전체 신뢰도 (0.0 ~ 1.0)", json_schema_extra={"example": 0.9108})
    metadata: Optional[Dict[str, Any]] = Field(None, description="메타데이터 (페이지 정보 등)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "** 계 량 확 인 서 ** \n(공급자 보관용) \n계량 일자: 2026-02-01 \n차량 번호: 5405 \n총 중 량 : 14,080 kg \n공차중량 : 13,950 kg \n실 중 량 : 130 kg \n정우리사이클링 (주)",
                "confidence": 0.9108,
                "metadata": {
                    "pages": [{"height": 1920, "page": 1, "width": 1440}]
                },
                "pages": []
            }
        }
    }
