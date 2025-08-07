from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response
from typing import Callable
import time
import logging
from utils.api_security import RateLimiter

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, calls_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiters = {}
        self.calls_per_minute = calls_per_minute

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Create or get rate limiter for this IP
        if client_ip not in self.rate_limiters:
            self.rate_limiters[client_ip] = RateLimiter(
                max_calls=self.calls_per_minute,
                time_window=60
            )
        
        # Check rate limit
        if not self.rate_limiters[client_ip].can_make_request():
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content="Rate limit exceeded",
                status_code=429
            )
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Track timing
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - Processed in {process_time:.2f} seconds"
        )
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application"""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
