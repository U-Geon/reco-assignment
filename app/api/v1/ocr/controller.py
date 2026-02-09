from fastapi import APIRouter, UploadFile, File, Response
from fastapi.responses import StreamingResponse
import json
import io

from app.models import OCRInput
from app.services import OCRParserService
from app.core.responses import ApiResponse, CustomException, ErrorStatus
from app.core.utils import dict_to_csv
from .dtos import OCRRequest, WeighbridgeResponse

router = APIRouter()
parser_service = OCRParserService()

@router.post(
    "/upload-ocr",
    response_model=ApiResponse[WeighbridgeResponse],
    summary="OCR 결과 파일 업로드 파싱",
    description="OCR 결과가 담긴 `.json` 파일을 업로드하여 계근지 정보를 파싱합니다.",
    response_description="파싱된 계근지 데이터"
)
async def upload_ocr_file(file: UploadFile = File(..., description="OCR 결과 JSON 파일")):
    """
    OCR 결과 JSON 파일을 업로드합니다.
    """
    if not file.filename.endswith('.json'):
        raise CustomException(ErrorStatus.INVALID_FILE_EXTENSION)

    try:
        content = await file.read()
        json_data = json.loads(content)
        
        ocr_request = OCRRequest(**json_data)
        ocr_input = OCRInput(**ocr_request.model_dump())
        ticket = parser_service.parse(ocr_input)
        response = WeighbridgeResponse(**ticket.model_dump())
        
        return ApiResponse.success_response(data=response)
        
    except json.JSONDecodeError:
        raise CustomException(ErrorStatus.INVALID_JSON_FORMAT)

@router.post(
    "/export/csv",
    summary="파싱 결과 CSV 다운로드",
    description="OCR 결과 JSON 파일을 업로드하여 파싱 후 CSV 파일로 다운로드합니다.",
    response_class=StreamingResponse
)
async def export_ocr_to_csv(file: UploadFile = File(..., description="OCR 결과 JSON 파일")):
    """
    OCR 결과 JSON 파일을 받아 파싱된 데이터를 CSV 파일로 반환합니다.
    """
    if not file.filename.endswith('.json'):
        raise CustomException(ErrorStatus.INVALID_FILE_EXTENSION)

    try:
        content = await file.read()
        json_data = json.loads(content)
        
        # Validation & Parsing
        ocr_request = OCRRequest(**json_data)
        ocr_input = OCRInput(**ocr_request.model_dump())
        ticket = parser_service.parse(ocr_input)
        response_dto = WeighbridgeResponse(**ticket.model_dump())
        
        # DTO를 dict로 변환 후 CSV 문자열 생성
        csv_content = dict_to_csv(response_dto.model_dump())
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=weighbridge_ticket.csv"}
        )
    except json.JSONDecodeError:
        raise CustomException(ErrorStatus.INVALID_JSON_FORMAT)

@router.post(
    "/export/json",
    summary="파싱 결과 JSON 파일 다운로드",
    description="OCR 결과 JSON 파일을 업로드하여 파싱 후 JSON 파일로 다운로드합니다.",
    response_class=Response
)
async def export_ocr_to_json(file: UploadFile = File(..., description="OCR 결과 JSON 파일")):
    """
    OCR 결과 JSON 파일을 받아 파싱된 데이터를 JSON 파일로 반환합니다.
    """
    if not file.filename.endswith('.json'):
        raise CustomException(ErrorStatus.INVALID_FILE_EXTENSION)

    try:
        content = await file.read()
        json_data = json.loads(content)
        
        # Validation & Parsing
        ocr_request = OCRRequest(**json_data)
        ocr_input = OCRInput(**ocr_request.model_dump())
        ticket = parser_service.parse(ocr_input)
        response_dto = WeighbridgeResponse(**ticket.model_dump())
        
        json_content = response_dto.model_dump_json(indent=2, exclude_none=True)
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=weighbridge_ticket.json"}
        )
    except json.JSONDecodeError:
        raise CustomException(ErrorStatus.INVALID_JSON_FORMAT)
