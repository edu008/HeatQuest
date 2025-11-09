"""
Location-Description-API-Endpunkte.
REST-API für KI-basierte Standortbeschreibung aus Satellitenbildern.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import logging
from pathlib import Path

from app.models.location_description import LocationDescriptionRequest, LocationDescriptionResponse
from app.services.location_description_service import location_description_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["location-description"])


@router.get(
    "/describe-location",
    response_model=LocationDescriptionResponse,
    summary="KI-Beschreibung eines Standorts",
    description="Ruft Satellitenbild ab und analysiert es mit Vision-KI"
)
async def describe_location(
    lat: float = Query(
        ...,
        description="Breitengrad",
        ge=-90,
        le=90,
        example=51.5074
    ),
    lon: float = Query(
        ...,
        description="Längengrad",
        ge=-180,
        le=180,
        example=-0.1278
    ),
    zoom: Optional[int] = Query(
        17,
        description="Zoom-Level (1-20, Standard: 17)",
        ge=1,
        le=20,
        example=17
    ),
    width: Optional[int] = Query(
        640,
        description="Bildbreite in Pixeln (Standard: 640)",
        ge=100,
        le=1280,
        example=640
    ),
    height: Optional[int] = Query(
        640,
        description="Bildhöhe in Pixeln (Standard: 640)",
        ge=100,
        le=1280,
        example=640
    )
):
    """
    🤖 **KI-BASIERTE STANDORTBESCHREIBUNG**
    
    Automatische Analyse eines Standorts anhand von Satellitenbildern:
    1. Ruft hochauflösendes Satellitenbild für Koordinaten ab
    2. Speichert Bild lokal
    3. Analysiert Bildinhalt mit Vision-KI
    4. Gibt natürlichsprachige Beschreibung zurück
    
    **Beispiel-URL:**
    ```
    /api/v1/describe-location?lat=51.5074&lon=-0.1278&zoom=17
    ```
    
    **Response enthält:**
    - KI-generierte Beschreibung (2-3 Sätze)
    - Koordinaten
    - Pfad zum gespeicherten Bild
    - Verwendete Anbieter (Bild + KI)
    - Konfidenz der Analyse
    
    **Unterstützte Bildquellen:**
    - Mapbox Satellite (verwendet MAP env variable)
    - Google Maps Satellite (Fallback)
    
    **Unterstützte KI-Anbieter:**
    - Google Vertex AI / Gemini Vision (verwendet VERTEX env variable)
    - OpenAI GPT-4 Vision (Fallback)
    
    **Was wird erkannt:**
    - Gebäude und Bebauungsdichte
    - Straßen und Verkehrswege
    - Grünflächen und Parks
    - Gewässer (Flüsse, Seen)
    - Stadtstruktur und Landnutzung
    
    **Parameter:**
    - **lat, lon**: GPS-Koordinaten (z.B. London: 51.5074, -0.1278)
    - **zoom**: Detailgrad (17 = Straßenebene, 14 = Stadtteilebene)
    - **width, height**: Bildgröße (Standard: 640x640px)
    
    **Konfiguration:**
    - Mapbox: `MAP` in .env
    - Vertex AI: `vertex-access.json` im Backend-Root (bereits vorhanden! ✅)
    - Optional: Weitere Anbieter in .env
    """
    
    try:
        logger.info(f"🌍 Location Description Request: ({lat}, {lon}), Zoom={zoom}")
        
        # Rufe Service auf
        result = location_description_service.describe_location(
            lat=lat,
            lon=lon,
            zoom=zoom,
            width=width,
            height=height
        )
        
        # Erstelle Response
        response = LocationDescriptionResponse(**result)
        
        logger.info(f"✅ Location Description erfolgreich: {result['ai_provider']}")
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Fehler bei Location Description: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der Verarbeitung: {str(e)}"
        )


@router.post(
    "/describe-location",
    response_model=LocationDescriptionResponse,
    summary="KI-Beschreibung eines Standorts (POST)",
    description="Ruft Satellitenbild ab und analysiert es mit Vision-KI (POST-Variante)"
)
async def describe_location_post(request: LocationDescriptionRequest):
    """
    🤖 **KI-BASIERTE STANDORTBESCHREIBUNG (POST)**
    
    POST-Variante des describe-location Endpoints.
    Nimmt JSON-Body statt Query-Parameter.
    
    **Beispiel-Request:**
    ```json
    {
        "lat": 51.5074,
        "lon": -0.1278,
        "zoom": 17,
        "width": 640,
        "height": 640
    }
    ```
    
    Siehe GET-Variante für Details.
    """
    
    try:
        logger.info(f"🌍 Location Description Request (POST): ({request.lat}, {request.lon})")
        
        # Rufe Service auf
        result = location_description_service.describe_location(
            lat=request.lat,
            lon=request.lon,
            zoom=request.zoom,
            width=request.width,
            height=request.height
        )
        
        # Erstelle Response
        response = LocationDescriptionResponse(**result)
        
        logger.info(f"✅ Location Description erfolgreich: {result['ai_provider']}")
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Fehler bei Location Description: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der Verarbeitung: {str(e)}"
        )


@router.get(
    "/satellite-image/{lat}/{lon}",
    response_class=FileResponse,
    summary="Satellitenbild abrufen",
    description="Gibt das gespeicherte Satellitenbild zurück"
)
async def get_satellite_image(
    lat: float,
    lon: float
):
    """
    📷 **SATELLITENBILD ANZEIGEN**
    
    Gibt das zuletzt für diese Koordinaten abgerufene Satellitenbild zurück.
    
    **Beispiel-URL:**
    ```
    /api/v1/satellite-image/51.5074/-0.1278
    ```
    
    **Response:** PNG-Bild
    
    **Hinweis:** Bild muss vorher über `/describe-location` abgerufen worden sein.
    """
    
    try:
        # Suche nach Bild im Cache
        cache_dir = Path(__file__).parent.parent.parent.parent / "cache" / "satellite_images"
        
        # Finde neuestes Bild für diese Koordinaten
        pattern = f"satellite_{lat}_{lon}_*.png"
        matching_files = list(cache_dir.glob(pattern))
        
        if not matching_files:
            raise HTTPException(
                status_code=404,
                detail=f"Kein Satellitenbild für Koordinaten ({lat}, {lon}) gefunden. Rufe zuerst /describe-location auf."
            )
        
        # Nimm neueste Datei
        latest_image = max(matching_files, key=lambda p: p.stat().st_mtime)
        
        logger.info(f"📷 Satellitenbild zurückgegeben: {latest_image.name}")
        
        return FileResponse(
            latest_image,
            media_type="image/png",
            filename=f"satellite_{lat}_{lon}.png"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen des Satellitenbildes: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen des Bildes: {str(e)}"
        )

