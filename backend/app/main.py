"""
HeatQuest Backend - Hauptanwendung.
FastAPI-Server für Oberflächentemperatur-Analyse aus Landsat-Daten.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.v1.heatmap import router as heatmap_router
from app.api.v1.location_description import router as location_description_router
from app.api.v1.missions import router as missions_router
from app.api.v1.test_supabase import router as test_router

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPI-App initialisieren
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS-Middleware hinzufügen (für Frontend-Integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion auf spezifische Origins beschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(heatmap_router)
app.include_router(location_description_router)
app.include_router(missions_router)
app.include_router(test_router)


@app.get("/", tags=["root"])
async def root():
    """
    Root-Endpoint mit Willkommensnachricht.
    """
    return {
        "message": "Willkommen bei der HeatQuest API",
        "version": settings.api_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "services": {
            "heatmap": {
                "description": "🚀 Smart Temperatur-Analyse mit Community-Cache",
                "endpoints": [
                    "/api/v1/grid-heat-score-radius",
                    "/api/v1/grid-heat-score-map-radius"
                ]
            },
            "location_description": {
                "description": "🤖 KI-basierte Standortbeschreibung aus Satellitenbildern",
                "endpoints": [
                    "/api/v1/describe-location"
                ]
            },
            "missions": {
                "description": "🎯 Mission-Management und Auto-Generierung",
                "endpoints": [
                    "/api/v1/missions",
                    "/api/v1/missions/generate"
                ]
            }
        }
    }


@app.on_event("startup")
async def startup_event():
    """
    Wird beim Start der Anwendung ausgeführt.
    """
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.api_title} v{settings.api_version} wird gestartet...")
    logger.info(f"📍 AWS Region: {settings.aws_region}")
    logger.info(f"🛰️  Landsat Bucket: {settings.landsat_bucket}")
    logger.info(f"📚 API-Dokumentation: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Wird beim Herunterfahren der Anwendung ausgeführt.
    """
    logger.info("🛑 HeatQuest API wird heruntergefahren...")


if __name__ == "__main__":
    import uvicorn
    
    # Server starten (nur für lokale Entwicklung)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
