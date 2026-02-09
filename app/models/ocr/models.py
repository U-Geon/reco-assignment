from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class OCRWord(BaseModel):
    text: str
    boundingBox: Optional[Dict[str, Any]] = Field(default=None)
    confidence: float = 0.0

class OCRPage(BaseModel):
    text: str
    words: List[OCRWord] = Field(default_factory=list)
    confidence: float = 0.0
    width: Optional[int] = None
    height: Optional[int] = None

class OCRInput(BaseModel):
    """
    [Domain Model] OCR 엔진으로부터 전달받은 원본 데이터
    """
    text: str
    pages: List[OCRPage] = Field(default_factory=list)
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = Field(default=None)

class WeighbridgeTicket(BaseModel):
    """
    [Domain Model] 파싱된 계근지 데이터
    """
    company_name: Optional[str] = Field(None, description="회사명")
    product_name: Optional[str] = Field(None, description="제품명")
    vehicle_number: Optional[str] = Field(None, description="차량번호")
    
    date: Optional[str] = Field(None, description="계량일자 (YYYY-MM-DD)")
    
    in_time: Optional[str] = Field(None, description="입고시간 (HH:MM:SS)")
    out_time: Optional[str] = Field(None, description="출고시간 (HH:MM:SS)")
    
    total_weight: Optional[int] = Field(None, description="총중량 (kg)")
    empty_weight: Optional[int] = Field(None, description="공차중량 (kg)")
    net_weight: Optional[int] = Field(None, description="실중량 (kg)")
    
    confidence_score: float = Field(0.0, description="파싱 신뢰도")
    uncertain: bool = Field(False, description="검토 필요 여부")
    
    original_text: Optional[str] = Field(None, description="원본 텍스트 (디버깅용)")
