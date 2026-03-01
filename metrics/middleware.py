import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from .service import track_event

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        # guardá evento técnico
        await track_event(
            type="http_request",
            endpoint=f"{request.method} {request.url.path}",
            duration_ms=duration_ms,
        )
        return response