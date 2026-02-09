import pytest
from app.services.ocr.ocr_service import OCRParserService
from app.models.ocr.models import OCRInput

@pytest.fixture
def parser_service():
    return OCRParserService()

def test_parse_full_ticket_perfect(parser_service):
    """
    [정상 케이스] 모든 필드가 명확하게 존재하는 경우
    """
    text = """
    ** 계 량 확 인 서 **
    상호 : (주) 테스트컴퍼니
    차량번호 : 12가 3456
    계량일자 : 2024-03-15
    총중량 : 25,000 kg
    공차중량 : 10,000 kg
    실중량 : 15,000 kg
    입고 : 09:00:00
    출고 : 09:30:00
    품명 : 고철
    """
    ocr_input = OCRInput(text=text)
    result = parser_service.parse(ocr_input)

    assert result.company_name == "(주) 테스트컴퍼니"
    assert result.vehicle_number == "3456" # 4자리 우선 추출 전략
    assert result.date == "2024-03-15"
    assert result.total_weight == 25000
    assert result.empty_weight == 10000
    assert result.net_weight == 15000
    assert result.in_time == "09:00:00"
    assert result.out_time == "09:30:00"
    assert result.product_name == "고철"

def test_parse_interleaved_noise(parser_service):
    """
    [노이즈 케이스] 라벨과 값 사이에 시간 정보 등이 끼어있는 경우 (Interleaving)
    """
    text = """
    총중량 : 11시 30분 14,080 kg
    공차중량 : 11시 40분 13,950 kg
    실중량 : 130 kg
    """
    ocr_input = OCRInput(text=text)
    result = parser_service.parse(ocr_input)

    assert result.total_weight == 14080
    assert result.empty_weight == 13950
    assert result.net_weight == 130

def test_parse_ocr_typos(parser_service):
    """
    [오타 교정] 숫자 오인식 문자(O, I, S, B) 교정 테스트
    """
    text = """
    총중량 : I4,O8O kg
    공차중량 : I3,9S0 kg
    차량번호 : 54OS
    """
    ocr_input = OCRInput(text=text)
    result = parser_service.parse(ocr_input)

    assert result.total_weight == 14080
    assert result.empty_weight == 13950

def test_time_heuristic_logic(parser_service):
    """
    [시간 추론] 여러 시간이 있을 때 입/출고 시간 자동 할당
    """
    text = """
    계량일자 : 2024-03-15
    11:00:00  <-- 입고 예상
    중간에 11:15:00 찍힘
    11:30:00  <-- 출고 예상
    """
    ocr_input = OCRInput(text=text)
    result = parser_service.parse(ocr_input)

    assert result.in_time == "11:00:00"
    assert result.out_time == "11:30:00"

def test_weight_correction_logic(parser_service):
    """
    [중량 보정] 총중량 - 공차중량 != 실중량 일 때, 계산값 우선
    """
    # 총(200) - 공차(100) = 100이어야 하는데, 실중량이 40으로 잘못 인식된 경우 (오차 60)
    text = """
    총중량 : 200 kg
    공차중량 : 100 kg
    실중량 : 40 kg
    """
    ocr_input = OCRInput(text=text)
    result = parser_service.parse(ocr_input)

    # 계산값(100)을 우선해야 함
    assert result.net_weight == 100

def test_fill_missing_weight(parser_service):
    """
    [누락 채우기] 중량 데이터 중 하나가 없을 때 역산하여 채우기
    """
    # 실중량 누락
    text1 = "총중량: 300kg, 공차중량: 100kg"
    res1 = parser_service.parse(OCRInput(text=text1))
    assert res1.net_weight == 200

    # 공차중량 누락
    text2 = "총중량: 300kg, 실중량: 200kg"
    res2 = parser_service.parse(OCRInput(text=text2))
    assert res2.empty_weight == 100

    # 총중량 누락
    text3 = "공차중량: 100kg, 실중량: 200kg"
    res3 = parser_service.parse(OCRInput(text=text3))
    assert res3.total_weight == 300

def test_vehicle_number_patterns(parser_service):
    """
    [차량번호] 4자리 숫자 우선 vs 전체 번호 패턴
    """
    # Case 1: 키워드 뒤 4자리
    text1 = "차량번호 : 1234"
    res1 = parser_service.parse(OCRInput(text=text1))
    assert res1.vehicle_number == "1234"

    # Case 2: 전체 번호 패턴 (키워드 없음)
    text2 = "어딘가에 12가 3456 적혀있음"
    res2 = parser_service.parse(OCRInput(text=text2))
    assert res2.vehicle_number == "12가3456"

def test_company_name_extraction(parser_service):
    """
    [업체명] Regex vs NER
    """
    # Case 1: 라벨(상호) 존재
    text1 = "상호 : (주) 명확한회사"
    res1 = parser_service.parse(OCRInput(text=text1))
    assert res1.company_name == "(주) 명확한회사"

    # Case 2: (주) 패턴 존재 (공백 없음)
    text2 = "어딘가에 숨어있는 (주)패턴회사"
    res2 = parser_service.parse(OCRInput(text=text2))
    assert res2.company_name == "(주) 패턴회사"

    # Case 3: (주) 패턴 존재 (공백 있음)
    text3 = "어딘가에 숨어있는 (주) 패턴회사"
    res3 = parser_service.parse(OCRInput(text=text3))
    assert res3.company_name == "(주) 패턴회사"

    # Case 4: NER 의존 (라벨X, 패턴X)
    if parser_service.nlp:
        text4 = "삼성전자에서 발행함"
        res4 = parser_service.parse(OCRInput(text=text4))
        if res4.company_name:
            assert "삼성전자" in res4.company_name
