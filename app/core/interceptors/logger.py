import time
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingInterceptor(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Request Logging
        logger.info(f"Incoming Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Response Logging
            logger.info(f"Request Completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request Failed: {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.4f}s")
            raise e # 예외를 다시 던져서 Exception Handler가 잡도록 함
