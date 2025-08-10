import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"- Client: {request.client.host if request.client else 'UNKNOWN'}"
        )
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            f"Response: {response.status_code} "
            f"- Processed in {process_time:.4f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        
        return response