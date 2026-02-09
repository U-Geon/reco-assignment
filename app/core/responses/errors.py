from enum import Enum
from starlette.status import (
    HTTP_400_BAD_REQUEST, 
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED, 
    HTTP_422_UNPROCESSABLE_ENTITY, 
    HTTP_500_INTERNAL_SERVER_ERROR
)

class ErrorStatus(Enum):
    """
    에러 상태를 정의하는 Enum Class
    """
    
    # 공통 에러 정의
    INTERNAL_SERVER_ERROR = (HTTP_500_INTERNAL_SERVER_ERROR, "ERR_500", "서버 내부 오류가 발생했습니다.")
    INVALID_REQUEST = (HTTP_400_BAD_REQUEST, "ERR_400", "잘못된 요청입니다.")
    NOT_FOUND = (HTTP_404_NOT_FOUND, "ERR_404", "리소스를 찾을 수 없습니다.")
    METHOD_NOT_ALLOWED = (HTTP_405_METHOD_NOT_ALLOWED, "ERR_405", "허용되지 않는 HTTP 메서드입니다.")
    VALIDATION_ERROR = (HTTP_422_UNPROCESSABLE_ENTITY, "ERR_422", "유효성 검사에 실패했습니다.")
    
    # 비즈니스 로직 에러 정의
    INVALID_FILE_EXTENSION = (HTTP_400_BAD_REQUEST, "FILE_001", "지원하지 않는 파일 형식입니다. (.json 파일만 가능)")
    INVALID_JSON_FORMAT = (HTTP_400_BAD_REQUEST, "FILE_002", "유효하지 않은 JSON 형식입니다.")
    OCR_DATA_EMPTY = (HTTP_400_BAD_REQUEST, "OCR_001", "OCR 데이터 내에서 유효한 텍스트를 찾을 수 없습니다.")
    
    def __init__(self, http_status: int, code: str, message: str):
        self.http_status = http_status
        self.code = code
        self.message = message


class CustomException(Exception):
    """
    비즈니스 로직에서 사용할 커스텀 예외 클래스
    """
    def __init__(self, error_status: ErrorStatus, message: str = None, data: dict = None):
        self.error_status = error_status
        self.message = message if message else error_status.message
        self.data = data
        super().__init__(self.message)