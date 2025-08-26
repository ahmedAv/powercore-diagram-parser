from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import image_processing
from app.core.logging_config import setup_logging
import logging

# Setup logging
# setup_logging()
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="API for PDF processing and equipment dimension extraction using LangGraph",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(
        image_processing.router,
        prefix=f"{settings.API_V1_STR}/image",
        tags=["pdf-processing"]
    )

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"API v1 available at {settings.API_V1_STR}")
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown
    """
    logger.info("Application shutdown initiated")


@app.get("/")
async def root():
    """
    Root endpoint - Health check and API information
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "api_version": "v1",
        "docs": "/docs",
        "endpoints": {
            "image_processing": f"{settings.API_V1_STR}/image/process-image/"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get("/info")
async def api_info():
    """
    API information endpoint
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "API for image analysis",
        "openapi_url": f"{settings.API_V1_STR}/openapi.json",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )