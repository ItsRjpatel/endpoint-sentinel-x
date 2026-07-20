from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import SentinelException
from app.core.logging import setup_logging

# Initialize logging configuration
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles FastAPI backend startup and shutdown lifecycles."""
    logger.info("Initializing Endpoint Sentinel X Core Services...")
    yield
    logger.info("Shutting down Endpoint Sentinel X Core Services...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware Configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API endpoints
app.include_router(api_router)


# Global Custom Exception Handlers
@app.exception_handler(SentinelException)
async def sentinel_exception_handler(request: Request, exc: SentinelException):
    """Maps custom domain exceptions into client-friendly JSON error responses."""
    logger.warn(
        "Application domain exception intercepted",
        path=request.url.path,
        error_code=exc.code,
        message=exc.message,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.message,
            "code": exc.code,
            "details": exc.details,
        },
    )


@app.get("/")
async def root():
    """Service landing redirection mapping."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
