"""
Pydantic-Modelle für die Location-Description-API.
Definiert Request- und Response-Schemas für Satellitenbildanalyse.
"""

from pydantic import BaseModel, Field
from typing import Optional


class LocationDescriptionRequest(BaseModel):
    """
    Request-Schema für Location-Description-Abfragen.
    """
    lat: float = Field(..., description="Breitengrad (WGS84)", ge=-90, le=90)
    lon: float = Field(..., description="Längengrad (WGS84)", ge=-180, le=180)
    zoom: Optional[int] = Field(17, description="Zoom-Level für Satellitenbild (1-20)", ge=1, le=20)
    width: Optional[int] = Field(640, description="Bildbreite in Pixeln", ge=100, le=1280)
    height: Optional[int] = Field(640, description="Bildhöhe in Pixeln", ge=100, le=1280)
    
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
    Response-Schema mit KI-generierter Beschreibung des Satellitenbildes.
    """
    description: str = Field(..., description="KI-generierte Beschreibung des Standorts")
    lat: float = Field(..., description="Breitengrad")
    lon: float = Field(..., description="Längengrad")
    image_path: str = Field(..., description="Pfad zum gespeicherten Satellitenbild")
    image_provider: str = Field(..., description="Anbieter des Satellitenbildes")
    ai_provider: str = Field(..., description="KI-Anbieter für die Bildanalyse")
    confidence: Optional[str] = Field(None, description="Konfidenz der KI-Analyse")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Ein dicht bebautes Stadtviertel mit großen Gebäuden, asphaltierten Straßen und wenigen Grünflächen. Im Zentrum ist ein historisches Gebäude mit charakteristischer Architektur zu sehen.",
                "lat": 51.5074,
                "lon": -0.1278,
                "image_path": "cache/satellite_images/satellite_51.5074_-0.1278.png",
                "image_provider": "Mapbox",
                "ai_provider": "OpenAI GPT-4 Vision",
                "confidence": "high"
            }
        }

