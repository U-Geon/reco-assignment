import pytest
from pydantic import ValidationError
from app.api.v1.ocr.dtos import OCRRequest, OCRPageDto, OCRWordDto

def test_ocr_request_valid():
    """정상적인 OCRRequest 생성 테스트"""
    data = {
        "text": "테스트 텍스트",
        "confidence": 0.95,
        "pages": [
            {
                "text": "페이지 텍스트",
                "words": [{"text": "단어", "confidence": 0.99}],
                "confidence": 0.95,
                "width": 1000,
                "height": 2000
            }
        ]
    }
    request = OCRRequest(**data)
    assert request.text == "테스트 텍스트"
    assert len(request.pages) == 1
    assert request.pages[0].words[0].text == "단어"

def test_ocr_request_missing_text():
    """필수 필드(text) 누락 시 ValidationError 발생 테스트"""
    data = {
        "confidence": 0.95
    }
    with pytest.raises(ValidationError):
        OCRRequest(**data)

def test_ocr_page_dto_defaults():
    """OCRPageDto 기본값 테스트"""
    data = {"text": "페이지 텍스트"}
    page = OCRPageDto(**data)
    assert page.words == []
    assert page.confidence == 0.0
    assert page.width is None

def test_ocr_word_dto_valid():
    """OCRWordDto 생성 테스트"""
    data = {
        "text": "단어",
        "boundingBox": {"vertices": [{"x": 1, "y": 1}]},
        "confidence": 0.9
    }
    word = OCRWordDto(**data)
    assert word.text == "단어"
    assert word.boundingBox["vertices"][0]["x"] == 1
