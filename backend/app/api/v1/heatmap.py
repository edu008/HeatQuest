"""
Heatmap-API-Endpunkte.
Moderne REST-API für Temperatur-Heatmaps basierend auf GPS-Koordinaten.
Nutzt Landsat-Temperaturdaten und Sentinel-2 NDVI mit optimiertem Batch-Processing.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import logging
import math

from app.models.heatmap import GridHeatScoreResponse
from app.services.grid_service import grid_service
from app.services.visualization_service import visualization_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["heatmap"])


@router.get(
    "/grid-heat-score-radius",
    response_model=GridHeatScoreResponse,
    summary="Heat Score Daten um einen Mittelpunkt (JSON)",
    description="Berechnet Heat Scores mit einem Punkt als Zentrum und Radius - gibt JSON zurück"
)
async def get_grid_heat_score_radius(
    lat: float = Query(
        ...,
        description="Breitengrad (Mittelpunkt)",
        ge=-90,
        le=90,
        example=51.5323
    ),
    lon: float = Query(
        ...,
        description="Längengrad (Mittelpunkt)",
        ge=-180,
        le=180,
        example=-0.0531
    ),
    radius_m: Optional[float] = Query(
        500,
        description="Radius in Metern (Standard: 500m)",
        gt=0,
        le=2500,
        example=500
    ),
    cell_size_m: Optional[float] = Query(
        30,
        description="Zellengröße in Metern (Standard: 30m)",
        gt=0,
        le=200,
        example=30
    ),
    scene_id: Optional[str] = Query(
        None,
        description="Landsat-Szenen-ID (OPTIONAL - wird automatisch gesucht!)",
        example="LC09_L2SP_201024_20230721_20230802_02_T1"
    ),
    use_batch: Optional[bool] = Query(
        True,
        description="Batch-Processing nutzen",
        example=True
    ),
    format: Optional[str] = Query(
        "json",
        description="Ausgabeformat: 'json' oder 'geojson'",
        example="json"
    )
):
    """
    🎯 **EINFACHSTER ENDPOINT FÜR JSON-DATEN!**
    
    Gib nur Mittelpunkt + Radius an, bekomme JSON mit allen Heat Scores zurück!
    
    **Beispiel-URL:**
    ```
    /api/v1/grid-heat-score-radius?lat=51.5323&lon=-0.0531&radius_m=500&cell_size_m=30
    ```
    
    **Das wars!** Keine scene_id, keine Bounding Box - nur Koordinaten! 🚀
    
    **Response enthält:**
    - Liste aller Grid-Zellen mit temp, ndvi, heat_score
    - Total cells
    - Bounds
    - Scene ID (automatisch gefunden für London, Berlin, Paris, New York)
    - NDVI source
    
    **Format-Optionen:**
    - `json` (Standard): Strukturierte JSON-Response
    - `geojson`: GeoJSON für GIS-Tools (QGIS, Leaflet, etc.)
    
    **Parameter:**
    - **lat, lon**: Koordinaten (z.B. London: 51.5323, -0.0531)
    - **radius_m**: Radius in Metern (500m = 1km Durchmesser)
    - **cell_size_m**: Zellengröße (30m = maximale Auflösung)
    - **scene_id**: Optional - wird automatisch gefunden
    """
    
    try:
        logger.info(f"🎯 JSON Heat Score: Zentrum=({lat},{lon}), Radius={radius_m}m")
        
        # Berechne Bounding Box aus Radius
        lat_offset = radius_m / 111000
        lon_offset = radius_m / (111000 * math.cos(math.radians(lat)))
        
        lat_min = lat - lat_offset
        lat_max = lat + lat_offset
        lon_min = lon - lon_offset
        lon_max = lon + lon_offset
        
        # Generiere Grid
        grid_cells = grid_service.generate_grid(
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            cell_size_m=cell_size_m
        )
        
        logger.info(f"   Grid: {len(grid_cells)} Zellen ({cell_size_m}m × {cell_size_m}m)")
        
        # Berechne Heat Scores mit Batch-Processing
        if use_batch:
            cell_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores_batch(
                grid_cells=grid_cells,
                scene_id=scene_id,
                max_cells=5000
            )
        else:
            cell_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores(
                grid_cells=grid_cells,
                scene_id=scene_id,
                max_cells=100
            )
        
        # Erstelle Response
        bounds = {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max
        }
        
        response = GridHeatScoreResponse(
            grid_cells=cell_results,
            total_cells=len(cell_results),
            cell_size_m=cell_size_m,
            bounds=bounds,
            scene_id=landsat_scene_id,
            ndvi_source=ndvi_source
        )
        
        # Format-Ausgabe
        if format.lower() == "geojson":
            geojson = grid_service.export_to_geojson(cell_results, bounds)
            return JSONResponse(content=geojson)
        else:
            return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Fehler bei JSON Heat Score: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der Verarbeitung: {str(e)}"
        )


@router.get(
    "/grid-heat-score-map-radius",
    response_class=HTMLResponse,
    summary="Heatmap um einen Mittelpunkt (Visualisierung)",
    description="Erstellt eine interaktive Heatmap mit Folium - zeigt farbige Grid-Zellen auf Mapbox-Karte"
)
async def get_grid_heat_score_map_radius(
    lat: float = Query(
        ...,
        description="Breitengrad (Mittelpunkt)",
        ge=-90,
        le=90,
        example=51.5323
    ),
    lon: float = Query(
        ...,
        description="Längengrad (Mittelpunkt)",
        ge=-180,
        le=180,
        example=-0.0531
    ),
    radius_m: Optional[float] = Query(
        500,
        description="Radius in Metern (Standard: 500m)",
        gt=0,
        le=2500,
        example=500
    ),
    cell_size_m: Optional[float] = Query(
        30,
        description="Zellengröße in Metern (Standard: 30m für maximale Auflösung)",
        gt=0,
        le=200,
        example=30
    ),
    scene_id: Optional[str] = Query(
        None,
        description="Landsat-Szenen-ID (OPTIONAL - wird automatisch gesucht!)",
        example="LC09_L2SP_201024_20230721_20230802_02_T1"
    ),
    use_batch: Optional[bool] = Query(
        True,
        description="Batch-Processing nutzen",
        example=True
    )
):
    """
    🗺️ **INTERAKTIVE HEATMAP-VISUALISIERUNG!**
    
    Erstellt eine schöne interaktive Karte mit Folium (nutzt deinen Mapbox-Token).
    
    **Beispiel-URL:**
    ```
    /api/v1/grid-heat-score-map-radius?lat=51.5323&lon=-0.0531&radius_m=500&cell_size_m=30
    ```
    
    **Features:**
    - 🎨 Farbskala: Gelb (kühl) → Orange → Rot (heiß)
    - 🔍 Hover-Tooltips mit Details (Temp, NDVI, Heat Score)
    - 📱 Fullscreen-Modus
    - 🗺️ Mapbox-Basemap (nutzt .env MAP Token)
    
    **Workflow:**
    1. Erstellt Grid um deinen Mittelpunkt
    2. Berechnet Heat Scores mit Batch-Processing (10-15x schneller!)
    3. Visualisiert als farbige Polygone auf Karte
    4. Gibt HTML zurück → Öffne direkt im Browser!
    
    **Parameter:**
    - **lat, lon**: Koordinaten (z.B. London: 51.5323, -0.0531)
    - **radius_m**: Radius in Metern (500m = 1km Durchmesser)
    - **cell_size_m**: Zellengröße (30m = maximale Auflösung, Landsat-Pixel-Größe)
    - **scene_id**: Optional - wird automatisch gefunden für London, Berlin, Paris, New York
    
    **Öffne die URL direkt im Browser für die interaktive Karte!** 🌍
    """
    
    try:
        logger.info(f"🗺️  Radius-Heatmap: Zentrum=({lat},{lon}), Radius={radius_m}m, Zellen={cell_size_m}m")
        
        # Berechne Bounding Box aus Mittelpunkt + Radius
        lat_offset = radius_m / 111000
        lon_offset = radius_m / (111000 * math.cos(math.radians(lat)))
        
        lat_min = lat - lat_offset
        lat_max = lat + lat_offset
        lon_min = lon - lon_offset
        lon_max = lon + lon_offset
        
        logger.info(f"   Berechnete Bounding Box: ({lat_min:.6f},{lon_min:.6f}) bis ({lat_max:.6f},{lon_max:.6f})")
        logger.info(f"   Gebietsgröße: ~{radius_m*2}m × ~{radius_m*2}m")
        
        # Generiere Grid
        grid_cells = grid_service.generate_grid(
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            cell_size_m=cell_size_m
        )
        
        logger.info(f"   Grid erstellt: {len(grid_cells)} Zellen ({cell_size_m}m × {cell_size_m}m)")
        
        # Schätze Verarbeitungszeit
        estimated_time = len(grid_cells) * 0.015  # ~15ms pro Zelle mit Batch
        logger.info(f"   ⏱️  Geschätzte Zeit: ~{estimated_time:.1f}s")
        
        # Berechne Heat Scores mit Batch-Processing
        if use_batch:
            cell_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores_batch(
                grid_cells=grid_cells,
                scene_id=scene_id,
                max_cells=5000
            )
        else:
            cell_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores(
                grid_cells=grid_cells,
                scene_id=scene_id,
                max_cells=100
            )
        
        # Erstelle Heatmap-Visualisierung
        bounds = {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max
        }
        
        logger.info("Erstelle Heatmap-Visualisierung...")
        html_map = visualization_service.create_heatmap(cell_results, bounds)
        
        logger.info("✅ Heatmap-Visualisierung abgeschlossen!")
        
        return HTMLResponse(content=html_map)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Fehler bei Radius-Heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der Verarbeitung: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Prüft, ob die API verfügbar ist"
)
async def health_check():
    """
    Einfacher Health-Check-Endpoint.
    
    Returns:
        Status-Information über die API
    """
    return {
        "status": "healthy",
        "service": "HeatQuest API",
        "version": "2.0.0",
        "endpoints": {
            "json": "/api/v1/grid-heat-score-radius",
            "map": "/api/v1/grid-heat-score-map-radius"
        }
    }
