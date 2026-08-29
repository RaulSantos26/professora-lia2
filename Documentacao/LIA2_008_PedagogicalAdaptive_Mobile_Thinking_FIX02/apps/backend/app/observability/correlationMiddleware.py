from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, callNext):
        correlationId = request.headers.get("X-Correlation-Id") or str(uuid4())
        request.state.correlationId = correlationId

        response = await callNext(request)
        response.headers["X-Correlation-Id"] = correlationId
        return response
