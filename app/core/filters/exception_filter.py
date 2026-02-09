from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger

# 패키지 레벨 Import 사용 (app.core.responses.__init__.py를 경유)
from app.core.responses import ApiResponse, ErrorStatus, CustomException

async def custom_exception_filter(request: Request, exc: CustomException):
    """
    [Core] CustomException 처리 핸들러
    """
    logger.warning(f"CustomException: {exc.error_status.code} - {exc.message} (Path: {request.url.path})")
    return JSONResponse(
        status_code=exc.error_status.http_status,
        content=ApiResponse.error_response(
            code=exc.error_status.code,
            message=exc.message,
            data=exc.data
        ).model_dump()
    )

async def global_exception_filter(request: Request, exc: Exception):
    """
    [Core] 모든 예외를 처리하는 글로벌 핸들러
    """
    
    # 1. FastAPI 기본 HTTPException 처리
    if isinstance(exc, HTTPException):
        logger.warning(f"HTTPException: {exc.detail} (Path: {request.url.path})")
        
        if exc.status_code == 404:
            return await custom_exception_filter(request, CustomException(ErrorStatus.NOT_FOUND))
        if exc.status_code == 405:
            return await custom_exception_filter(request, CustomException(ErrorStatus.METHOD_NOT_ALLOWED))

        code = f"HTTP_{exc.status_code}"
        message = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse.error_response(code=code, message=message).model_dump()
        )

    # 2. Pydantic 유효성 검사 실패 처리
    if isinstance(exc, RequestValidationError):
        error_details = exc.errors()
        logger.warning(f"Validation Error: {error_details} (Path: {request.url.path})")
        
        msg = f"{error_details[0]['loc'][-1]}: {error_details[0]['msg']}" if error_details else "Validation error"
        
        return await custom_exception_filter(
            request, 
            CustomException(ErrorStatus.VALIDATION_ERROR, message=msg, data={"details": error_details})
        )

    # 3. 예측하지 못한 서버 에러 (500)
    logger.error(f"Unhandled Exception: {str(exc)} (Path: {request.url.path})")
    logger.exception(exc)

    return await custom_exception_filter(
        request, 
        CustomException(ErrorStatus.INTERNAL_SERVER_ERROR)
    )
