"""
Pydantic models for the Location Description API.
Defines request and response schemas for satellite image analysis.
"""

from pydantic import BaseModel, Field
from typing import Optional


class LocationDescriptionRequest(BaseModel):
    """
    Request schema for Location Description queries.
    """
    lat: float = Field(..., description="Latitude (WGS84)", ge=-90, le=90)
    lon: float = Field(..., description="Longitude (WGS84)", ge=-180, le=180)
    zoom: Optional[int] = Field(17, description="Zoom level for satellite image (1-20)", ge=1, le=20)
    width: Optional[int] = Field(640, description="Image width in pixels", ge=100, le=1280)
    height: Optional[int] = Field(640, description="Image height in pixels", ge=100, le=1280)
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 51.5074,
                "lon": -0.1278,
                "zoom": 17,
                "width": 640,
                "height": 640
            }
        }


class LocationDescriptionResponse(BaseModel):
    """
    Response schema with AI-generated description of the satellite image.
    """
    description: str = Field(..., description="AI-generated description of the location")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    image_path: str = Field(..., description="Path to the stored satellite image")
    image_provider: str = Field(..., description="Provider of the satellite image")
    ai_provider: str = Field(..., description="AI provider for image analysis")
    confidence: Optional[str] = Field(None, description="Confidence of AI analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "A densely built city district with large buildings, paved streets, and few green spaces. In the center, there is a historical building with characteristic architecture.",
                "lat": 51.5074,
                "lon": -0.1278,
                "image_path": "cache/satellite_images/satellite_51.5074_-0.1278.png",
                "image_provider": "Mapbox",
                "ai_provider": "OpenAI GPT-4 Vision",
                "confidence": "high"
            }
        }

