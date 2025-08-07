from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class WaterMonitoringException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def error_handler(request: Request, exc: WaterMonitoringException) -> JSONResponse:
    """Global error handler for the application"""
    error_response = {
        "error": True,
        "message": str(exc),
        "path": request.url.path,
        "status_code": exc.status_code
    }
    
    # Log the error
    logger.error(f"Error handling request: {error_response}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )

def setup_exception_handlers(app: Any) -> None:
    """Configure exception handlers for the application"""
    
    @app.exception_handler(WaterMonitoringException)
    async def handle_water_monitoring_exception(request: Request, exc: WaterMonitoringException):
        return await error_handler(request, exc)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        return await error_handler(
            request,
            WaterMonitoringException(str(exc.detail), exc.status_code)
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(request: Request, exc: Exception):
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        
        return await error_handler(
            request,
            WaterMonitoringException(
                "An unexpected error occurred",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        )
