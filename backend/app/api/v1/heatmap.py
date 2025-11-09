"""
Heatmap API Endpoints with Smart Cache.
Modern REST API for temperature heatmaps based on GPS coordinates.
Uses Landsat temperature data and Sentinel-2 NDVI with optimized batch processing.
Integrates parent/child grid system for community cache.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import logging
import math

from app.models.heatmap import GridHeatScoreResponse, GridCellResponse
from app.services.grid_service import grid_service
from app.services.visualization_service import visualization_service
from app.services.parent_cell_service import parent_cell_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["heatmap"])


@router.get(
    "/grid-heat-score-radius",
    response_model=GridHeatScoreResponse,
    summary="Heat Score Data around a center point (JSON)",
    description="Calculates heat scores with a point as center and radius - returns JSON"
)
async def get_grid_heat_score_radius(
    lat: float = Query(
        ...,
        description="Latitude (center point)",
        ge=-90,
        le=90,
        example=51.5323
    ),
    lon: float = Query(
        ...,
        description="Longitude (center point)",
        ge=-180,
        le=180,
        example=-0.0531
    ),
    radius_m: Optional[float] = Query(
        500,
        description="Radius in meters (default: 500m)",
        gt=0,
        le=2500,
        example=500
    ),
    cell_size_m: Optional[float] = Query(
        30,
        description="Cell size in meters (default: 30m)",
        gt=0,
        le=200,
        example=30
    ),
    scene_id: Optional[str] = Query(
        None,
        description="Landsat scene ID (OPTIONAL - automatically detected!)",
        example="LC09_L2SP_201024_20230721_20230802_02_T1"
    ),
    use_batch: Optional[bool] = Query(
        True,
        description="Use batch processing",
        example=True
    ),
    use_cache: Optional[bool] = Query(
        True,
        description="🚀 Use Smart Cache (loads from DB when available)",
        example=True
    ),
    format: Optional[str] = Query(
        "json",
        description="Output format: 'json' or 'geojson'",
        example="json"
    )
):
    """
    🎯 **SMART HEATMAP with Community Cache!**
    
    Loads heatmap data intelligently:
    - ✅ **Uses existing scans** when available (⚡ 0.5s instead of 30s!)
    - ✅ **Performs new scan** when area not yet covered
    - ✅ **Community feature:** Users benefit from each other
    
    **Example URL:**
    ```
    /api/v1/grid-heat-score-radius?lat=51.5323&lon=-0.0531&radius_m=500&cell_size_m=30
    ```
    
    **How it works:**
    
    1. **User A (09:00)** scans Station Square → New scan, saves Parent + Child Cells  
    2. **User B (10:00)** scans same area → Parent Cell found! Loads from DB (⚡ instant!)  
    3. **User C (11:00)** scans 500m away → New Parent Cell, new scan  
    
    **Response includes:**
    - `grid_cells`: Heat score data  
    - `from_cache`: TRUE if loaded from DB  
    - `parent_cell_info`: Info about Parent Cell (who scanned before, etc.)  
    - `total_scans`: How many times this area was scanned  
    
    **Parameters:**
    - **lat, lon**: Coordinates (e.g., London: 51.5323, -0.0531)
    - **radius_m**: Radius in meters (500m = 1km diameter)
    - **cell_size_m**: Cell size (30m = maximum resolution)
    - **use_cache**: TRUE = Use Smart Cache (recommended!), FALSE = always rescan
    - **scene_id**: Optional - automatically found
    """
    
    try:
        logger.info("=" * 70)
        logger.info(f"🎯 SMART HEATMAP REQUEST")
        logger.info(f"   Position: ({lat}, {lon})")
        logger.info(f"   Radius: {radius_m}m, Cell Size: {cell_size_m}m")
        logger.info(f"   Use Cache: {use_cache}")
        logger.info("=" * 70)
        
        # Calculate bounding box from radius
        lat_offset = radius_m / 111000
        lon_offset = radius_m / (111000 * math.cos(math.radians(lat)))
        
        lat_min = lat - lat_offset
        lat_max = lat + lat_offset
        lon_min = lon - lon_offset
        lon_max = lon + lon_offset
        
        # Initialize variables
        from_cache = False
        parent_cell = None
        cell_results = []
        landsat_scene_id = None
        ndvi_source = None
        
        # ========================================
        # SMART CACHE LOGIC
        # ========================================
        if use_cache:
            # Step 1: Search existing Parent Cell
            parent_cell = await parent_cell_service.find_existing_parent_cell(lat, lon)
            
            if parent_cell:
                # ✅ Parent Cell found! Load from cache
                logger.info("🎉 Parent Cell found! Loading Child Cells from cache...")
                from_cache = True
                
                # Increase scan counter
                await parent_cell_service.increment_scan_count(parent_cell['id'])
                
                # Load Child Cells
                child_cells_data = await parent_cell_service.load_child_cells(parent_cell['id'])
                
                # Convert to GridCellResponse
                cell_results = [
                    GridCellResponse(
                        cell_id=cell['cell_id'],
                        lat_min=cell['lat_min'],
                        lat_max=cell['lat_max'],
                        lon_min=cell['lon_min'],
                        lon_max=cell['lon_max'],
                        temp=cell['temperature'],
                        ndvi=cell['ndvi'],
                        heat_score=cell['heat_score'],
                        pixel_count=cell.get('pixel_count')
                    )
                    for cell in child_cells_data
                ]
                
                landsat_scene_id = parent_cell.get('landsat_scene_id')
                ndvi_source = parent_cell.get('ndvi_source')
                
                logger.info(f"✅ {len(cell_results)} Child Cells loaded from cache!")
                logger.info(f"⚡ This area has already been scanned {parent_cell['total_scans']} times")
        
        # ========================================
        # FALLBACK: New Scan
        # ========================================
        if not cell_results:
            logger.info("🔍 No cache available → Starting new scan...")
            
            # Generate Grid
            grid_cells = grid_service.generate_grid(
                lat_min=lat_min,
                lat_max=lat_max,
                lon_min=lon_min,
                lon_max=lon_max,
                cell_size_m=cell_size_m
            )
            
            logger.info(f"   Grid: {len(grid_cells)} cells ({cell_size_m}m × {cell_size_m}m)")
            
            # Calculate Heat Scores
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
            
            # Save in DB (only if cache is enabled)
            if use_cache:
                logger.info("💾 Saving scan for future users...")
                
                # Create Parent Cell
                parent_cell = await parent_cell_service.create_parent_cell(
                    lat=lat,
                    lon=lon,
                    landsat_scene_id=landsat_scene_id,
                    ndvi_source=ndvi_source
                )
                
                # Save Child Cells
                await parent_cell_service.save_child_cells(
                    parent_cell_id=parent_cell['id'],
                    grid_cells=cell_results
                )
                
                logger.info("✅ Scan saved! Next user can load from cache.")
        
        # ========================================
        # RESPONSE
        # ========================================
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
        
        # Add cache info to response
        response_dict = response.dict()
        response_dict['from_cache'] = from_cache
        response_dict['parent_cell_info'] = {
            'id': parent_cell['id'],
            'cell_key': parent_cell['cell_key'],
            'total_scans': parent_cell['total_scans'],
            'last_scanned_at': parent_cell['last_scanned_at'],
            'child_cells_count': parent_cell['child_cells_count']
        } if parent_cell else None
        
        logger.info("=" * 70)
        logger.info(f"✅ Response ready:")
        logger.info(f"   From Cache: {from_cache}")
        logger.info(f"   Total Cells: {len(cell_results)}")
        if parent_cell:
            logger.info(f"   Total Scans (this area): {parent_cell['total_scans']}")
        logger.info("=" * 70)
        
        # Output format
        if format.lower() == "geojson":
            geojson = grid_service.export_to_geojson(cell_results, bounds)
            return JSONResponse(content=geojson)
        else:
            return JSONResponse(content=response_dict)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error during JSON Heat Score: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during processing: {str(e)}"
        )


@router.get(
    "/grid-heat-score-map-radius",
    response_class=HTMLResponse,
    summary="Heatmap around a center point (Visualization)",
    description="Creates an interactive heatmap with Folium - shows colored grid cells on Mapbox map"
)
async def get_grid_heat_score_map_radius(
    lat: float = Query(
        ...,
        description="Latitude (center point)",
        ge=-90,
        le=90,
        example=51.5323
    ),
    lon: float = Query(
        ...,
        description="Longitude (center point)",
        ge=-180,
        le=180,
        example=-0.0531
    ),
    radius_m: Optional[float] = Query(
        500,
        description="Radius in meters (default: 500m)",
        gt=0,
        le=2500,
        example=500
    ),
    cell_size_m: Optional[float] = Query(
        30,
        description="Cell size in meters (default: 30m for maximum resolution)",
        gt=0,
        le=200,
        example=30
    ),
    scene_id: Optional[str] = Query(
        None,
        description="Landsat scene ID (OPTIONAL - automatically detected!)",
        example="LC09_L2SP_201024_20230721_20230802_02_T1"
    ),
    use_batch: Optional[bool] = Query(
        True,
        description="Use batch processing",
        example=True
    )
):
    """
    🗺️ **INTERACTIVE HEATMAP VISUALIZATION!**
    
    Creates a beautiful interactive map with Folium (uses your Mapbox token).
    
    **Example URL:**
    ```
    /api/v1/grid-heat-score-map-radius?lat=51.5323&lon=-0.0531&radius_m=500&cell_size_m=30
    ```
    
    **Features:**
    - 🎨 Color scale: Yellow (cool) → Orange → Red (hot)
    - 🔍 Hover tooltips with details (Temp, NDVI, Heat Score)
    - 📱 Fullscreen mode
    - 🗺️ Mapbox basemap (uses .env MAP token)
    
    **Workflow:**
    1. Creates grid around your center point
    2. Calculates heat scores with batch processing (10–15× faster!)
    3. Visualizes as colored polygons on the map
    4. Returns HTML → Open directly in browser!
    
    **Parameters:**
    - **lat, lon**: Coordinates (e.g., London: 51.5323, -0.0531)
    - **radius_m**: Radius in meters (500m = 1km diameter)
    - **cell_size_m**: Cell size (30m = maximum resolution, Landsat pixel size)
    - **scene_id**: Optional - automatically found for London, Berlin, Paris, New York
    
    **Open the URL directly in your browser for the interactive map!** 🌍
    """
    
    try:
        logger.info(f"🗺️  Radius Heatmap: Center=({lat},{lon}), Radius={radius_m}m, Cells={cell_size_m}m")
        
        # Calculate bounding box from center + radius
        lat_offset = radius_m / 111000
        lon_offset = radius_m / (111000 * math.cos(math.radians(lat)))
        
        lat_min = lat - lat_offset
        lat_max = lat + lat_offset
        lon_min = lon - lon_offset
        lon_max = lon + lon_offset
        
        logger.info(f"   Calculated Bounding Box: ({lat_min:.6f},{lon_min:.6f}) to ({lat_max:.6f},{lon_max:.6f})")
        logger.info(f"   Area size: ~{radius_m*2}m × ~{radius_m*2}m")
        
        # Generate grid
        grid_cells = grid_service.generate_grid(
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            cell_size_m=cell_size_m
        )
        
        logger.info(f"   Grid created: {len(grid_cells)} cells ({cell_size_m}m × {cell_size_m}m)")
        
        # Estimate processing time
        estimated_time = len(grid_cells) * 0.015  # ~15ms per cell with batch
        logger.info(f"   ⏱️  Estimated time: ~{estimated_time:.1f}s")
        
        # Calculate heat scores with batch processing
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
        
        # Create heatmap visualization
        bounds = {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max
        }
        
        logger.info("Creating heatmap visualization...")
        html_map = visualization_service.create_heatmap(cell_results, bounds)
        
        logger.info("✅ Heatmap visualization complete!")
        
        return HTMLResponse(content=html_map)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error during Radius Heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during processing: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Checks if the API is available"
)
async def health_check():
    """
    Simple health check endpoint.
    
    Returns:
        Status information about the API
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
