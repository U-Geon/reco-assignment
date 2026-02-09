import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app import api
from app.core.responses import CustomException
from app.core.filters import custom_exception_filter, global_exception_filter
from app.core.interceptors import LoggingInterceptor

app = FastAPI(title="Weighbridge OCR Parser API", version="1.0.0")

# 1. Middleware 등록
app.add_middleware(LoggingInterceptor)
app.add_middleware(
    CORSMiddleware,
    allow_origins={"*"},
    allow_credentials=True,
    allow_methods={"OPTIONS", "GET", "POST", "DELETE", "PUT"},
    allow_headers={"*"},
)

# 2. Exception Handlers 정의
app.add_exception_handler(CustomException, custom_exception_filter)
app.add_exception_handler(HTTPException, global_exception_filter)
app.add_exception_handler(RequestValidationError, global_exception_filter)
app.add_exception_handler(Exception, global_exception_filter)

# 3. Router 등록
app.include_router(api.router, prefix="/api")

if __name__ == "__main__":
    # 실행 시 프로젝트 루트에서: python -m app.main
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
