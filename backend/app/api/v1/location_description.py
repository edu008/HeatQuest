"""
Location Description API Endpoints.
REST API for AI-based location description from satellite imagery.
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
    summary="AI description of a location",
    description="Fetches a satellite image and analyzes it with Vision AI"
)
async def describe_location(
    lat: float = Query(
        ...,
        description="Latitude",
        ge=-90,
        le=90,
        example=51.5074
    ),
    lon: float = Query(
        ...,
        description="Longitude",
        ge=-180,
        le=180,
        example=-0.1278
    ),
    zoom: Optional[int] = Query(
        17,
        description="Zoom level (1–20, default: 17)",
        ge=1,
        le=20,
        example=17
    ),
    width: Optional[int] = Query(
        640,
        description="Image width in pixels (default: 640)",
        ge=100,
        le=1280,
        example=640
    ),
    height: Optional[int] = Query(
        640,
        description="Image height in pixels (default: 640)",
        ge=100,
        le=1280,
        example=640
    )
):
    """
    🤖 **AI-BASED LOCATION DESCRIPTION**
    
    Automatically analyzes a location using satellite imagery:
    1. Fetches a high-resolution satellite image for given coordinates
    2. Saves the image locally
    3. Analyzes the image using Vision AI
    4. Returns a natural language description
    
    **Example URL:**
    ```
    /api/v1/describe-location?lat=51.5074&lon=-0.1278&zoom=17
    ```
    
    **Response includes:**
    - AI-generated description (2–3 sentences)
    - Coordinates
    - Path to saved image
    - Providers used (image + AI)
    - Confidence score of the analysis
    
    **Supported image sources:**
    - Mapbox Satellite (uses MAP env variable)
    - Google Maps Satellite (fallback)
    
    **Supported AI providers:**
    - Google Vertex AI / Gemini Vision (uses VERTEX env variable)
    - OpenAI GPT-4 Vision (fallback)
    
    **Detectable features:**
    - Buildings and density
    - Roads and traffic networks
    - Green spaces and parks
    - Water bodies (rivers, lakes)
    - Urban structure and land use
    
    **Parameters:**
    - **lat, lon**: GPS coordinates (e.g., London: 51.5074, -0.1278)
    - **zoom**: Level of detail (17 = street level, 14 = neighborhood)
    - **width, height**: Image size (default: 640x640px)
    
    **Configuration:**
    - Mapbox: `MAP` in .env
    - Vertex AI: `vertex-access.json` in backend root (already provided ✅)
    - Optional: Other providers can be added via .env
    """
    
    try:
        logger.info(f"🌍 Location Description Request: ({lat}, {lon}), Zoom={zoom}")
        
        # Call the service
        result = location_description_service.describe_location(
            lat=lat,
            lon=lon,
            zoom=zoom,
            width=width,
            height=height
        )
        
        # Create response
        response = LocationDescriptionResponse(**result)
        
        logger.info(f"✅ Location description successful: {result['ai_provider']}")
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error in Location Description: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during processing: {str(e)}"
        )


@router.post(
    "/describe-location",
    response_model=LocationDescriptionResponse,
    summary="AI description of a location (POST)",
    description="Fetches a satellite image and analyzes it with Vision AI (POST version)"
)
async def describe_location_post(request: LocationDescriptionRequest):
    """
    🤖 **AI-BASED LOCATION DESCRIPTION (POST)**
    
    POST version of the describe-location endpoint.
    Accepts a JSON body instead of query parameters.
    
    **Example Request:**
    ```json
    {
        "lat": 51.5074,
        "lon": -0.1278,
        "zoom": 17,
        "width": 640,
        "height": 640
    }
    ```
    
    See the GET version for details.
    """
    
    try:
        logger.info(f"🌍 Location Description Request (POST): ({request.lat}, {request.lon})")
        
        # Call the service
        result = location_description_service.describe_location(
            lat=request.lat,
            lon=request.lon,
            zoom=request.zoom,
            width=request.width,
            height=request.height
        )
        
        # Create response
        response = LocationDescriptionResponse(**result)
        
        logger.info(f"✅ Location description successful: {result['ai_provider']}")
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error in Location Description: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during processing: {str(e)}"
        )


@router.get(
    "/satellite-image/{lat}/{lon}",
    response_class=FileResponse,
    summary="Retrieve satellite image",
    description="Returns the saved satellite image"
)
async def get_satellite_image(
    lat: float,
    lon: float
):
    """
    📷 **SHOW SATELLITE IMAGE**
    
    Returns the most recently fetched satellite image for given coordinates.
    
    **Example URL:**
    ```
    /api/v1/satellite-image/51.5074/-0.1278
    ```
    
    **Response:** PNG image
    
    **Note:** The image must first be retrieved via `/describe-location`.
    """
    
    try:
        # Look for image in cache
        cache_dir = Path(__file__).parent.parent.parent.parent / "cache" / "satellite_images"
        
        # Find latest image for these coordinates
        pattern = f"satellite_{lat}_{lon}_*.png"
        matching_files = list(cache_dir.glob(pattern))
        
        if not matching_files:
            raise HTTPException(
                status_code=404,
                detail=f"No satellite image found for coordinates ({lat}, {lon}). Please call /describe-location first."
            )
        
        # Take the most recent file
        latest_image = max(matching_files, key=lambda p: p.stat().st_mtime)
        
        logger.info(f"📷 Returned satellite image: {latest_image.name}")
        
        return FileResponse(
            latest_image,
            media_type="image/png",
            filename=f"satellite_{lat}_{lon}.png"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error retrieving satellite image: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving image: {str(e)}"
        )
    