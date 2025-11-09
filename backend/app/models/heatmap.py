"""
Pydantic-Modelle für die Heatmap-API.
Definiert Request- und Response-Schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class HeatmapRequest(BaseModel):
    """
    Request-Schema für Heatmap-Abfragen.
    """
    lat: float = Field(..., description="Breitengrad (WGS84)", ge=-90, le=90)
    lon: float = Field(..., description="Längengrad (WGS84)", ge=-180, le=180)
    radius: Optional[float] = Field(200, description="Radius in Metern", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 51.5395,
                "lon": -0.055,
                "radius": 200
            }
        }


class HeatmapResponse(BaseModel):
    """
    Response-Schema mit berechneten Temperaturwerten.
    """
    mean_temp: float = Field(..., description="Durchschnittstemperatur in °C")
    min_temp: float = Field(..., description="Minimale Temperatur in °C")
    max_temp: float = Field(..., description="Maximale Temperatur in °C")
    unit: str = Field(default="°C", description="Temperatureinheit")
    scene_id: str = Field(..., description="ID der verwendeten Landsat-Szene")
    pixel_count: int = Field(..., description="Anzahl der ausgewerteten Pixel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mean_temp": 28.6,
                "min_temp": 26.9,
                "max_temp": 30.2,
                "unit": "°C",
                "scene_id": "LC08_L2SP_193024_20230801_02_T1",
                "pixel_count": 156
            }
        }


class HeatScoreResponse(BaseModel):
    """
    Response-Schema mit Heat Score (Temperatur + NDVI).
    """
    temp: float = Field(..., description="Durchschnittstemperatur in °C")
    ndvi: float = Field(..., description="NDVI-Wert (Normalized Difference Vegetation Index)")
    heat_score: float = Field(..., description="Heat Score = temp - (0.3 * ndvi)")
    unit: str = Field(default="°C", description="Temperatureinheit")
    scene_id: str = Field(..., description="ID der verwendeten Landsat-Szene")
    pixel_count: int = Field(..., description="Anzahl der ausgewerteten Pixel")
    ndvi_source: Optional[str] = Field(None, description="Quelle der NDVI-Daten")
    
    class Config:
        json_schema_extra = {
            "example": {
                "temp": 12.5,
                "ndvi": 0.35,
                "heat_score": 12.39,
                "unit": "°C",
                "scene_id": "LC09_L2SP_201024_20251030_20251104_02_T1",
                "pixel_count": 54,
                "ndvi_source": "estimated"
            }
        }


class ErrorResponse(BaseModel):
    """
    Fehler-Response-Schema.
    """
    error: str = Field(..., description="Fehlermeldung")
    details: Optional[str] = Field(None, description="Detaillierte Fehlerinformationen")


class GridCellResponse(BaseModel):
    """
    Response-Schema für eine einzelne Grid-Zelle.
    """
    cell_id: str = Field(..., description="Zellen-ID (z.B. 'cell_0_0')")
    lat_min: float = Field(..., description="Minimaler Breitengrad")
    lat_max: float = Field(..., description="Maximaler Breitengrad")
    lon_min: float = Field(..., description="Minimaler Längengrad")
    lon_max: float = Field(..., description="Maximaler Längengrad")
    temp: Optional[float] = Field(None, description="Durchschnittstemperatur in °C")
    ndvi: Optional[float] = Field(None, description="Durchschnittlicher NDVI")
    heat_score: Optional[float] = Field(None, description="Heat Score = temp - (0.3 * ndvi)")
    pixel_count: Optional[int] = Field(None, description="Anzahl gültiger Pixel")


class GridHeatScoreResponse(BaseModel):
    """
    Response-Schema für Grid-basierte Heat Score Berechnung.
    """
    grid_cells: list[GridCellResponse] = Field(..., description="Liste aller Grid-Zellen mit Heat Scores")
    total_cells: int = Field(..., description="Anzahl der Grid-Zellen")
    cell_size_m: float = Field(200, description="Zellengröße in Metern")
    bounds: dict = Field(..., description="Bounding Box (lat_min, lat_max, lon_min, lon_max)")
    scene_id: str = Field(..., description="ID der verwendeten Landsat-Szene")
    ndvi_source: str = Field(..., description="Quelle der NDVI-Daten")
    
    class Config:
        json_schema_extra = {
            "example": {
                "grid_cells": [
                    {
                        "cell_id": "cell_0_0",
                        "lat_min": 51.524,
                        "lat_max": 51.5258,
                        "lon_min": -0.0745,
                        "lon_max": -0.0727,
                        "temp": 12.5,
                        "ndvi": 0.35,
                        "heat_score": 12.39,
                        "pixel_count": 45
                    }
                ],
                "total_cells": 240,
                "cell_size_m": 200,
                "bounds": {
                    "lat_min": 51.524,
                    "lat_max": 51.5405,
                    "lon_min": -0.0745,
                    "lon_max": -0.0317
                },
                "scene_id": "LC09_L2SP_201024_20251030_20251104_02_T1",
                "ndvi_source": "sentinel-2"
            }
        }

