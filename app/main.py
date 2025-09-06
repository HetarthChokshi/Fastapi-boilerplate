import logging
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logger import logger
from app.api import auth, users
from app.utils.response import error_response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        client_ip = request.client.host
        method = request.method
        url = str(request.url)
        
        logger.info(f"Request: {method} {url} from {client_ip}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            status_code = response.status_code
            
            logger.info(
                f"Response: {method} {url} - {status_code} - {process_time:.3f}s"
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Error: {method} {url} - {str(e)} - {process_time:.3f}s"
            )
            raise


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs" if settings.ENV == "development" else None,
        redoc_url="/redoc" if settings.ENV == "development" else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,  
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.VERSION,
            "environment": settings.ENV,
            "docs_url": "/docs" if settings.ENV == "development" else "Disabled in production"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.VERSION
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return error_response(
            status_code=500,
            message="Internal server error"
        )
    
    # HTTP exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP exception handler"""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
        return error_response(
            status_code=exc.status_code,
            message=exc.detail
        )
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup event"""
        logger.info(f"{settings.APP_NAME} v{settings.VERSION} starting up...")
        logger.info(f"Environment: {settings.ENV}")
        logger.info(f"Log level: {settings.LOG_LEVEL}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event"""
        logger.info(f"{settings.APP_NAME} shutting down...")
    
    return app


# Create the FastAPI app instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
