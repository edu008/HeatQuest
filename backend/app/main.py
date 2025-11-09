"""
HeatQuest Backend - Main Application.
FastAPI server for surface temperature analysis from Landsat data.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.v1.heatmap import router as heatmap_router
from app.api.v1.location_description import router as location_description_router
from app.api.v1.test_supabase import router as test_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(heatmap_router)
app.include_router(location_description_router)
app.include_router(test_router)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with welcome message.
    """
    return {
        "message": "Welcome to the HeatQuest API",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "services": {
            "heatmap": {
                "description": "🚀 Smart temperature analysis with community cache",
                "endpoints": [
                    "/api/v1/grid-heat-score-radius",
                    "/api/v1/grid-heat-score-map-radius"
                ]
            },
            "location_description": {
                "description": "AI-based location description from satellite imagery",
                "endpoints": [
                    "/api/v1/describe-location"
                ]
            }
        }
    }


@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts.
    """
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.api_title} v{settings.api_version} is starting...")
    logger.info(f"📍 AWS Region: {settings.aws_region}")
    logger.info(f"🛰️  Landsat Bucket: {settings.landsat_bucket}")
    logger.info(f"📚 API Documentation: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the application shuts down.
    """
    logger.info("🛑 HeatQuest API is shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    # Start server (for local development only)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    