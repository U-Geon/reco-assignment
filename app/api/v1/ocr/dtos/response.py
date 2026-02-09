from pydantic import BaseModel, Field
from typing import Optional

class WeighbridgeResponse(BaseModel):
    """
    계근지 파싱 결과 응답 DTO
    """
    company_name: Optional[str] = Field(None, description="추출된 회사명", json_schema_extra={"example": "정우리사이클링 (주)"})
    product_name: Optional[str] = Field(None, description="추출된 제품명", json_schema_extra={"example": "고철"})
    vehicle_number: Optional[str] = Field(None, description="차량번호 (숫자 4자리 또는 전체 번호)", json_schema_extra={"example": "5405"})
    
    date: Optional[str] = Field(None, description="계량일자 (YYYY-MM-DD)", json_schema_extra={"example": "2026-02-01"})
    in_time: Optional[str] = Field(None, description="입고시간 (HH:MM:SS)", json_schema_extra={"example": "11:33:00"})
    out_time: Optional[str] = Field(None, description="출고시간 (HH:MM:SS)", json_schema_extra={"example": "11:55:35"})
    
    total_weight: Optional[int] = Field(None, description="총중량 (kg)", json_schema_extra={"example": 14080})
    empty_weight: Optional[int] = Field(None, description="공차중량 (kg)", json_schema_extra={"example": 13950})
    net_weight: Optional[int] = Field(None, description="실중량 (kg)", json_schema_extra={"example": 130})
    
    confidence_score: float = Field(0.0, description="OCR 엔진 신뢰도 점수", json_schema_extra={"example": 0.9108})
    uncertain: bool = Field(False, description="데이터 불확실성 여부 (검토 필요 시 True)", json_schema_extra={"example": False})

    model_config = {
        "json_schema_extra": {
            "example": {
                "company_name": "정우리사이클링 (주)",
                "vehicle_number": "5405",
                "date": "2026-02-01",
                "in_time": "11:33:00",
                "out_time": "11:55:35",
                "total_weight": 14080,
                "empty_weight": 13950,
                "net_weight": 130,
                "confidence_score": 0.9108,
                "uncertain": False
            }
        }
    }
