"""
Pydantic models for the Heatmap API.
Defines request and response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class HeatmapRequest(BaseModel):
    """
    Request schema for heatmap queries.
    """
    lat: float = Field(..., description="Latitude (WGS84)", ge=-90, le=90)
    lon: float = Field(..., description="Longitude (WGS84)", ge=-180, le=180)
    radius: Optional[float] = Field(200, description="Radius in meters", gt=0)
    
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
    Response schema with calculated temperature values.
    """
    mean_temp: float = Field(..., description="Average temperature in °C")
    min_temp: float = Field(..., description="Minimum temperature in °C")
    max_temp: float = Field(..., description="Maximum temperature in °C")
    unit: str = Field(default="°C", description="Temperature unit")
    scene_id: str = Field(..., description="ID of the used Landsat scene")
    pixel_count: int = Field(..., description="Number of evaluated pixels")
    
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
    Response schema with Heat Score (Temperature + NDVI).
    """
    temp: float = Field(..., description="Average temperature in °C")
    ndvi: float = Field(..., description="NDVI value (Normalized Difference Vegetation Index)")
    heat_score: float = Field(..., description="Heat Score = temp - (0.3 * ndvi)")
    unit: str = Field(default="°C", description="Temperature unit")
    scene_id: str = Field(..., description="ID of the used Landsat scene")
    pixel_count: int = Field(..., description="Number of evaluated pixels")
    ndvi_source: Optional[str] = Field(None, description="Source of NDVI data")
    
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
    Error response schema.
    """
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")


class GridCellResponse(BaseModel):
    """
    Response schema for a single grid cell.
    """
    cell_id: str = Field(..., description="Cell ID (e.g. 'cell_0_0')")
    lat_min: float = Field(..., description="Minimum latitude")
    lat_max: float = Field(..., description="Maximum latitude")
    lon_min: float = Field(..., description="Minimum longitude")
    lon_max: float = Field(..., description="Maximum longitude")
    temp: Optional[float] = Field(None, description="Average temperature in °C")
    ndvi: Optional[float] = Field(None, description="Average NDVI")
    heat_score: Optional[float] = Field(None, description="Heat Score = temp - (0.3 * ndvi)")
    pixel_count: Optional[int] = Field(None, description="Number of valid pixels")


class GridHeatScoreResponse(BaseModel):
    """
    Response schema for grid-based heat score calculation.
    """
    grid_cells: list[GridCellResponse] = Field(..., description="List of all grid cells with heat scores")
    total_cells: int = Field(..., description="Number of grid cells")
    cell_size_m: float = Field(200, description="Cell size in meters")
    bounds: dict = Field(..., description="Bounding box (lat_min, lat_max, lon_min, lon_max)")
    scene_id: str = Field(..., description="ID of the used Landsat scene")
    ndvi_source: str = Field(..., description="Source of NDVI data")
    
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
        