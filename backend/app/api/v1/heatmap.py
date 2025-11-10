"""
Heatmap-API-Endpunkte mit Smart-Cache.
Moderne REST-API für Temperatur-Heatmaps basierend auf GPS-Koordinaten.
Nutzt Landsat-Temperaturdaten und Sentinel-2 NDVI mit optimiertem Batch-Processing.
Integriert Parent/Child-Grid-System für Community-Cache.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional, Dict, Any
import logging
import math
import os
import random

from app.models.heatmap import GridHeatScoreResponse, GridCellResponse
from app.services.grid_service import grid_service
from app.services.visualization_service import visualization_service
from app.services.parent_cell_service import parent_cell_service
from app.services.location_description_service import location_description_service
from app.services.mission_generation_service import mission_generation_service
from app.services.hotspot_detector import hotspot_detector
from app.core.supabase_client import supabase_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["heatmap"])

# Konstante für konsistente max_cells Werte
MAX_CELLS_ANALYSIS = 2  # Max. 2 Zellen pro Durchlauf


async def analyze_hotspot_cells_with_ai(
    saved_cells: list,
    parent_cell_id: str,
    user_lat: float,
    user_lon: float,
    user_id: Optional[str] = None,
    heat_score_threshold: Optional[float] = None,
    detection_method: Optional[str] = "adaptive",
    detection_params: Optional[Dict[str, Any]] = None,
    max_cells: int = MAX_CELLS_ANALYSIS  # Konsistente Verwendung der Konstante
):
    """
    Analysiert dynamisch erkannte Hotspot-Zellen mit KI.

    Args:
        saved_cells: Child-Cells aus der Datenbank
        parent_cell_id: Zugehörige Parent-Cell ID
        user_lat: User Latitude
        user_lon: User Longitude
        user_id: Optionaler User für Missionserstellung
        heat_score_threshold: Optional fixer Threshold (Fallback)
        detection_method: "percentile" | "stddev" | "color" | "adaptive"
        detection_params: Zusätzliche Parameter für die Methode
        max_cells: Max. Anzahl zufällig ausgewählter Zellen pro Durchlauf
    """
    try:
        # Validierung von max_cells
        if max_cells <= 0:
            logger.warning(f"⚠️ Invalid max_cells={max_cells}, using default {MAX_CELLS_ANALYSIS}")
            max_cells = MAX_CELLS_ANALYSIS
        
        if max_cells > 10:  # Reasonable limit
            logger.warning(f"⚠️ max_cells={max_cells} too high, capping at 10")
            max_cells = 10

        logger.info("=" * 70)
        if detection_method:
            logger.info("🤖 AI ANALYSIS: Dynamic Hotspot Detection")
            logger.info(f"   Method: {detection_method}")
        else:
            logger.info("🤖 AI ANALYSIS: Processing pre-flagged hotspot cells")
        logger.info(
            "   Static Threshold: %s",
            f"{heat_score_threshold:.2f}" if heat_score_threshold is not None else "disabled",
        )
        logger.info(f"   Max Cells: {max_cells}")

        if not saved_cells:
            logger.info("ℹ️  No cells available for analysis")
            logger.info("=" * 70)
            return

        logger.info(f"📦 Total cells received: {len(saved_cells)}")

        detection_params = detection_params or {}

        if heat_score_threshold is not None:
            logger.info("📏 Static threshold aktiv – klassische Filterung")
            hotspot_cells = [
                cell
                for cell in saved_cells
                if cell.get("heat_score") is not None and cell["heat_score"] >= heat_score_threshold
            ]
            threshold_info: Any = heat_score_threshold
        elif detection_method:
            try:
                hotspot_cells, threshold_info = hotspot_detector.detect_auto(
                    saved_cells,
                    method=detection_method,
                    **detection_params,
                )
            except ValueError as detection_error:
                logger.warning(
                    "⚠️  Unbekannte Detection-Methode '%s' (%s) – Fallback auf Percentile.",
                    detection_method,
                    detection_error,
                )
                hotspot_cells, threshold_info = hotspot_detector.detect_by_percentile(
                    saved_cells,
                    top_percentile=detection_params.get("top_percentile", 0.15),
                )
        else:
            hotspot_cells = [
                cell for cell in saved_cells if cell.get("analyzed") is True
            ]
            threshold_info = "pre-flagged analyzed=True"
            logger.info(f"📊 {len(hotspot_cells)} hotspot cells (pre-flagged)")

        if not hotspot_cells:
            logger.info("ℹ️  No hotspot cells detected")
            logger.info("=" * 70)
            return

        logger.info(f"📊 {len(hotspot_cells)} hotspot cells detected")
        if isinstance(threshold_info, (int, float)):
            logger.info(f"   Threshold info: {threshold_info:.2f}")
        else:
            logger.info(f"   Threshold info: {threshold_info}")

        child_cell_ids = [c["id"] for c in hotspot_cells if c.get("id")]

        if not child_cell_ids:
            logger.warning("⚠️ WARNING: Hotspot cells have no IDs! Cannot check for existing analyses.")
            logger.warning("   This should not happen. Skipping AI analysis to prevent duplicates.")
            logger.info("=" * 70)
            return

        logger.info(f"🔑 {len(child_cell_ids)} cells with valid IDs")

        cells_need_analysis = [c for c in hotspot_cells if c.get("analyzed") is True]
        cells_already_done = [c for c in hotspot_cells if c.get("analyzed") is False]

        if cells_already_done:
            logger.info(f"✅ {len(cells_already_done)} cells already completed (analyzed=False)")

        if not cells_need_analysis:
            logger.info("✅ All hotspot cells already analyzed (no cells with analyzed=True)")
            logger.info("=" * 70)
            return

        logger.info(f"🆕 {len(cells_need_analysis)} cells need analysis (analyzed=True)")

        hotspot_cells = cells_need_analysis
        child_cell_ids = [c["id"] for c in hotspot_cells if c.get("id")]

        logger.info("🔍 Backup-Check: Prüfe cell_analyses Tabelle...")
        existing_analyses_response = supabase_service.client.table("cell_analyses").select(
            "child_cell_id"
        ).in_("child_cell_id", child_cell_ids).execute()

        existing_child_cell_ids = set()
        if existing_analyses_response.data:
            existing_child_cell_ids = {a["child_cell_id"] for a in existing_analyses_response.data}
            logger.info(f"⚠️  Backup-Check fand {len(existing_child_cell_ids)} Zellen mit Analysen (sollte 0 sein!)")
            if len(existing_child_cell_ids) > 0:
                logger.warning("   Dies deutet auf ein Sync-Problem mit analyzed-Flag hin!")
        else:
            logger.info("✅ Backup-Check: Keine Duplikate gefunden (gut!)")

        hotspot_cells = [
            cell for cell in hotspot_cells if cell.get("id") not in existing_child_cell_ids
        ]

        filtered_count = len(cells_need_analysis) - len(hotspot_cells)
        if filtered_count > 0:
            logger.warning(f"⚠️  {filtered_count} cells durch Backup-Check gefiltert (Flag-Inkonsistenz!)")
        else:
            logger.info(f"✅ Alle {len(hotspot_cells)} Zellen bereit für KI-Analyse")

        if not hotspot_cells:
            logger.info("✅ All hotspot cells already have analyses - no AI analysis needed!")
            logger.info("=" * 70)
            return

        logger.info(f"🆕 {len(hotspot_cells)} new hotspot cells need AI analysis")

        for cell in hotspot_cells:
            lat1, lon1 = user_lat, user_lon
            lat2, lon2 = cell["center_lat"], cell["center_lon"]

            R = 6371000  # Earth radius in meters
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)

            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c

            cell["distance_to_user"] = distance

        if len(hotspot_cells) > max_cells:
            cells_to_analyze = random.sample(hotspot_cells, max_cells)
            logger.info(f"🎲 Random selection: {max_cells} out of {len(hotspot_cells)} hotspot cells")
        else:
            cells_to_analyze = hotspot_cells
            logger.info(f"🎲 Analyzing all {len(hotspot_cells)} available hotspot cells")

        cells_to_analyze_sorted = sorted(cells_to_analyze, key=lambda c: c["distance_to_user"])

        logger.info(f"🎯 Starting AI analysis for {len(cells_to_analyze)} RANDOM cells (max: {max_cells}):")
        for i, cell in enumerate(cells_to_analyze_sorted):
            logger.info(
                f"   {i+1}. {cell['cell_id']}: Heat Score={cell['heat_score']:.1f}, "
                f"Distance={cell['distance_to_user']:.0f}m"
            )
        if len(hotspot_cells) > max_cells:
            logger.info(f"   ℹ️  {len(hotspot_cells) - max_cells} weitere Zellen warten auf zukünftige Random-Auswahl")
        logger.info("=" * 70)
        
        # 8. JETZT ERST: Analyze each cell with AI (nur wenn noch keine Analyse existiert)
        analyzed_count = 0
        for idx, cell in enumerate(cells_to_analyze):
            image_path = None  # Initialize for finally block
            
            try:
                logger.info(f"\n--- Analyzing cell {idx+1}/{len(cells_to_analyze)}: {cell['cell_id']} ---")
                
                # Call location_description_service (startet KI)
                location_result = location_description_service.describe_location(
                    lat=cell['center_lat'],
                    lon=cell['center_lon'],
                    zoom=18,  # High resolution for details
                    width=640,
                    height=640
                )
                
                description = location_result['description']
                main_cause = location_result['main_cause']
                suggested_actions = location_result['suggested_actions']
                image_path = location_result['image_path']
                ai_provider = location_result['ai_provider']
                
                logger.info(f"✅ AI Description ({len(description)} chars): {description[:80]}...")
                logger.info(f"✅ Main Cause: {main_cause}")
                logger.info(f"✅ Actions: {len(suggested_actions)} suggested")
                
                # 9. Save to cell_analyses table
                # Convert confidence to Float (high=0.9, medium=0.7, low=0.5)
                confidence_str = location_result.get('confidence', 'high')
                confidence_value = 0.9 if confidence_str == 'high' else (0.7 if confidence_str == 'medium' else 0.5)
                
                analysis_data = {
                    'child_cell_id': cell['id'],
                    'parent_cell_id': parent_cell_id,
                    'latitude': cell['center_lat'],
                    'longitude': cell['center_lon'],
                    'temperature': cell.get('temperature'),
                    'ndvi': cell.get('ndvi'),
                    'heat_score': cell['heat_score'],
                    'ai_summary': description,
                    'main_cause': main_cause,
                    'suggested_actions': suggested_actions,
                    'confidence': confidence_value,  # Float instead of String!
                    'image_url': None,  # Image not stored permanently
                    'gemini_model': ai_provider,
                    'mission_generated': False  # ✅ Initial: Noch keine Mission generiert
                }
                
                response = supabase_service.client.table('cell_analyses').insert(analysis_data).execute()
                
                if response.data and len(response.data) > 0:
                    analysis_id = response.data[0]['id']
                    
                    # 10. Update Child-Cell: analyzed = False (bedeutet "fertig analysiert")
                    # WICHTIG: analyzed = False → Analyse abgeschlossen
                    #          analyzed = True → Wartet noch auf Analyse
                    child_cell_uuid = cell['id']
                    logger.info(f"   🔄 Setze analyzed=False für child_cell UUID: {child_cell_uuid}")
                    
                    # Update mit der richtigen UUID
                    update_response = supabase_service.client.table('child_cells').update({
                        'analyzed': False,
                        'ai_analysis_id': analysis_id
                    }).eq('id', child_cell_uuid).execute()
                    
                    # 10a. Verify: Lade die Zelle nochmal und prüfe ob analyzed=False
                    verify_response = supabase_service.client.table('child_cells').select('id, cell_id, analyzed').eq('id', child_cell_uuid).execute()
                    
                    if verify_response.data and len(verify_response.data) > 0:
                        verified_cell = verify_response.data[0]
                        if verified_cell.get('analyzed') == False:
                            logger.info(f"   ✅ VERIFIED: analyzed=False korrekt gesetzt für UUID {child_cell_uuid}!")
                        else:
                            logger.error(f"   ❌ FEHLER: analyzed={verified_cell.get('analyzed')} - sollte False sein!")
                    else:
                        logger.warning(f"   ⚠️ Konnte Zelle nicht verifizieren: {child_cell_uuid}")
                    
                    analyzed_count += 1
                    logger.info(f"✅ Cell {cell['cell_id']} successfully analyzed and saved! (analyzed=False)")
                else:
                    logger.error(f"❌ cell_analyses insert fehlgeschlagen - keine data in response")
                
            except Exception as e:
                logger.error(f"❌ Error analyzing cell {cell['cell_id']}: {e}")
                # WICHTIG: Setze analyzed=False auch bei Fehler, um Endlosschleife zu vermeiden
                try:
                    child_cell_uuid = cell.get('id')
                    if child_cell_uuid:
                        logger.warning(f"   🔄 Setze analyzed=False trotz Fehler für UUID: {child_cell_uuid}")
                        supabase_service.client.table('child_cells').update({
                            'analyzed': False
                        }).eq('id', child_cell_uuid).execute()
                        
                        # Verify
                        verify_error = supabase_service.client.table('child_cells').select('analyzed').eq('id', child_cell_uuid).execute()
                        if verify_error.data and len(verify_error.data) > 0:
                            logger.info(f"   ✅ analyzed=False gesetzt (trotz Analysefehler), verified: {verify_error.data[0].get('analyzed')}")
                    else:
                        logger.error(f"   ❌ Keine UUID gefunden für Zelle {cell.get('cell_id')}")
                except Exception as update_error:
                    logger.error(f"   ❌ Konnte analyzed Flag nicht setzen: {update_error}")
                
            finally:
                # 11. Delete satellite image ALWAYS after use (whether successful or error)
                if image_path:
                    try:
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            logger.info(f"🗑️  Satellite image deleted: {os.path.basename(image_path)}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not delete image: {e}")
        
        logger.info("=" * 70)
        logger.info(f"🎉 AI ANALYSIS COMPLETED: {analyzed_count}/{len(cells_to_analyze)} cells successfully analyzed")
        logger.info("=" * 70)
        
        # 12. Automatic Mission Generation (if user_id provided)
        # This runs ALWAYS when user_id is present, not only after new analyses
        # The service checks internally which analyses don't have missions yet
        if user_id:
            logger.info("\n" + "=" * 70)
            logger.info("🎯 Checking for missions to generate...")
            logger.info(f"   (Checking all analyses in parent_cell for missing missions)")
            try:
                missions = await mission_generation_service.generate_missions_from_analyses(
                    parent_cell_id=parent_cell_id,
                    user_id=user_id,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    max_missions=10  # Generate up to 10 missions
                )
                if len(missions) > 0:
                    logger.info(f"✅ {len(missions)} new missions automatically generated!")
                else:
                    logger.info(f"ℹ️  No new missions generated (all analyses already have missions)")
            except Exception as e:
                logger.error(f"⚠️ Error during mission generation: {e}")
            logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error in automatic hotspot analysis: {e}", exc_info=True)


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
    use_cache: Optional[bool] = Query(
        True,
        description="🚀 Smart-Cache nutzen (lädt aus DB wenn verfügbar)",
        example=True
    ),
    format: Optional[str] = Query(
        "json",
        description="Ausgabeformat: 'json' oder 'geojson'",
        example="json"
    ),
    user_id: Optional[str] = Query(
        None,
        description="User ID for automatic mission generation (optional)"
    )
):
    """
    🎯 **SMART HEATMAP mit Community-Cache!**
    
    Lädt Heatmap-Daten intelligent:
    - ✅ **Nutzt existierende Scans** wenn verfügbar (⚡ 0.5s statt 30s!)
    - ✅ **Scannt neu** wenn Bereich noch nicht erfasst
    - ✅ **Community-Feature:** User profitieren voneinander
    
    **Beispiel-URL:**
    ```
    /api/v1/grid-heat-score-radius?lat=51.5323&lon=-0.0531&radius_m=500&cell_size_m=30
    ```
    
    **Wie es funktioniert:**
    
    1. **User A (09:00)** scannt Bahnhofplatz → Neuer Scan, speichert Parent-Cell + Child-Cells
    2. **User B (10:00)** scannt gleichen Bereich → Parent-Cell gefunden! Lädt aus DB (⚡ instant!)
    3. **User C (11:00)** scannt 500m weiter → Neue Parent-Cell, neuer Scan
    
    **Response enthält:**
    - `grid_cells`: Heat Score Daten
    - `from_cache`: TRUE wenn aus DB geladen
    - `parent_cell_info`: Info über Parent-Cell (wer hat schon gescannt, etc.)
    - `total_scans`: Wie oft wurde dieser Bereich schon gescannt
    
    **Parameter:**
    - **lat, lon**: Koordinaten (z.B. London: 51.5323, -0.0531)
    - **radius_m**: Radius in Metern (500m = 1km Durchmesser)
    - **cell_size_m**: Zellengröße (30m = maximale Auflösung)
    - **use_cache**: TRUE = Smart-Cache nutzen (empfohlen!), FALSE = immer neu scannen
    - **scene_id**: Optional - wird automatisch gefunden
    """
    
    try:
        logger.info("=" * 70)
        logger.info(f"🎯 SMART HEATMAP REQUEST")
        logger.info(f"   Position: ({lat}, {lon})")
        logger.info(f"   Radius: {radius_m}m, Cell Size: {cell_size_m}m")
        logger.info(f"   Use Cache: {use_cache}")
        logger.info("=" * 70)
        
        # Berechne Bounding Box aus Radius
        lat_offset = radius_m / 111000
        lon_offset = radius_m / (111000 * math.cos(math.radians(lat)))
        
        lat_min = lat - lat_offset
        lat_max = lat + lat_offset
        lon_min = lon - lon_offset
        lon_max = lon + lon_offset
        
        # Variablen initialisieren
        from_cache = False
        parent_cell = None
        cell_results = []
        landsat_scene_id = None
        ndvi_source = None
        
        # ========================================
        # SMART CACHE LOGIC
        # ========================================
        if use_cache:
            # Schritt 1: Suche existierende Parent-Cell
            parent_cell = await parent_cell_service.find_existing_parent_cell(lat, lon)
            
            if parent_cell:
                # ✅ Parent-Cell gefunden! Lade aus DB
                logger.info("🎉 Parent-Cell gefunden! Lade Child-Cells aus Cache...")
                from_cache = True
                
                # Erhöhe Scan-Counter
                await parent_cell_service.increment_scan_count(parent_cell['id'])
                
                # Lade Child-Cells (FRISCH aus DB mit aktuellem analyzed Status!)
                child_cells_data = await parent_cell_service.load_child_cells(parent_cell['id'])
                
                # Debug: Zeige analyzed Status DIREKT nach dem Laden
                if child_cells_data:
                    analyzed_true_count = sum(1 for c in child_cells_data if c.get('analyzed') == True)
                    analyzed_false_count = sum(1 for c in child_cells_data if c.get('analyzed') == False)
                    logger.info(f"   📊 Nach DB-Load: {analyzed_true_count} cells mit analyzed=True, {analyzed_false_count} mit analyzed=False")
                
                # Konvertiere zu GridCellResponse
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
                
                logger.info(f"✅ {len(cell_results)} Child-Cells loaded from cache!")
                logger.info(f"⚡ This area has been scanned {parent_cell['total_scans']}x times")
                
                # Check if cells have descriptions and analyze missing ones
                await analyze_hotspot_cells_with_ai(
                    saved_cells=child_cells_data,  # Original data from DB with IDs and analyzed status
                    parent_cell_id=parent_cell['id'],
                    user_lat=lat,
                    user_lon=lon,
                    user_id=user_id,  # For automatic mission generation
                    detection_method=None,  # ✅ Korrigiert: Komma hinzugefügt
                    max_cells=MAX_CELLS_ANALYSIS  # ✅ Konsistenter Wert
                )
        
        # ========================================
        # FALLBACK: Neuer Scan
        # ========================================
        if not cell_results:
            logger.info("🔍 Kein Cache verfügbar → Starte neuen Scan...")
            
            # Generiere Grid
            grid_cells = grid_service.generate_grid(
                lat_min=lat_min,
                lat_max=lat_max,
                lon_min=lon_min,
                lon_max=lon_max,
                cell_size_m=cell_size_m
            )
            
            logger.info(f"   Grid: {len(grid_cells)} Zellen ({cell_size_m}m × {cell_size_m}m)")
            
            # Berechne Heat Scores
            if use_batch:
                cell_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores_batch(
                    grid_cells=grid_cells,
                    scene_id=scene_id,
                    max_cells=10000
                )
            else:
                cell_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores(
                    grid_cells=grid_cells,
                    scene_id=scene_id,
                    max_cells=100
                )
            
            # Speichere in DB (nur wenn Cache aktiviert)
            if use_cache:
                logger.info("💾 Speichere Scan für zukünftige User...")
                
                # Erstelle Parent-Cell
                parent_cell = await parent_cell_service.create_parent_cell(
                    lat=lat,
                    lon=lon,
                    landsat_scene_id=landsat_scene_id,
                    ndvi_source=ndvi_source
                )
                
                # Speichere Child-Cells
                saved_cells = await parent_cell_service.save_child_cells(
                    parent_cell_id=parent_cell['id'],
                    grid_cells=cell_results
                )
                
                logger.info("✅ Scan saved! Next user can load from cache.")
                
                # Automatic AI analysis for hotspot cells (Heat Score >= 11)
                await analyze_hotspot_cells_with_ai(
                    saved_cells=saved_cells,
                    parent_cell_id=parent_cell['id'],
                    user_lat=lat,
                    user_lon=lon,
                    user_id=user_id,  # For automatic mission generation
                    max_cells=MAX_CELLS_ANALYSIS  # ✅ Konsistenter Wert
                )
        
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
        
        # Erweitere Response mit Cache-Info
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
        logger.info(f"✅ Response bereit:")
        logger.info(f"   From Cache: {from_cache}")
        logger.info(f"   Total Cells: {len(cell_results)}")
        if parent_cell:
            logger.info(f"   Total Scans (dieser Bereich): {parent_cell['total_scans']}")
        logger.info("=" * 70)
        
        # Format-Ausgabe
        if format.lower() == "geojson":
            geojson = grid_service.export_to_geojson(cell_results, bounds)
            return JSONResponse(content=geojson)
        else:
            return JSONResponse(content=response_dict)
    
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
    ),
    use_cache: Optional[bool] = Query(
        True,
        description="🚀 Smart-Cache nutzen (lädt aus DB wenn verfügbar)",
        example=True
    ),
    user_id: Optional[str] = Query(
        None,
        description="User ID for automatic mission generation (optional)"
    )
):
    """
    🗺️ **INTERAKTIVE HEATMAP-VISUALISIERUNG mit Smart-Cache!**
    
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
    - ⚡ **Smart-Cache:** Lädt sofort wenn Bereich schon gescannt wurde!
    
    **Workflow:**
    1. Prüft ob Parent-Cell existiert → Lädt aus Cache (⚡ schnell!)
    2. Falls neu: Berechnet Heat Scores mit Batch-Processing
    3. Visualisiert als farbige Polygone auf Karte
    4. Gibt HTML zurück → Öffne direkt im Browser!
    
    **Parameter:**
    - **lat, lon**: Koordinaten (z.B. London: 51.5323, -0.0531)
    - **radius_m**: Radius in Metern (500m = 1km Durchmesser)
    - **cell_size_m**: Zellengröße (30m = maximale Auflösung, Landsat-Pixel-Größe)
    - **use_cache**: TRUE = Smart-Cache nutzen (empfohlen!)
    - **scene_id**: Optional - wird automatisch gefunden
    
    **Öffne die URL direkt im Browser für die interaktive Karte!** 🌍
    """
    
    try:
        logger.info("=" * 70)
        logger.info(f"🗺️  VISUALISIERUNG REQUEST")
        logger.info(f"   Position: ({lat}, {lon})")
        logger.info(f"   Radius: {radius_m}m, Cell Size: {cell_size_m}m")
        logger.info(f"   Use Cache: {use_cache}")
        logger.info("=" * 70)
        
        # Berechne Bounding Box aus Mittelpunkt + Radius
        lat_offset = radius_m / 111000
        lon_offset = radius_m / (111000 * math.cos(math.radians(lat)))
        
        lat_min = lat - lat_offset
        lat_max = lat + lat_offset
        lon_min = lon - lon_offset
        lon_max = lon + lon_offset
        
        # Variablen initialisieren
        from_cache = False
        parent_cell = None
        cell_results = []
        landsat_scene_id = None
        ndvi_source = None
        
        # ========================================
        # SMART CACHE LOGIC (wie beim JSON-Endpoint)
        # ========================================
        if use_cache:
            # Schritt 1: Suche existierende Parent-Cell
            parent_cell = await parent_cell_service.find_existing_parent_cell(lat, lon)
            
            if parent_cell:
                # ✅ Parent-Cell gefunden! Lade aus DB
                logger.info("🎉 Parent-Cell gefunden! Lade Child-Cells aus Cache...")
                from_cache = True
                
                # Erhöhe Scan-Counter
                await parent_cell_service.increment_scan_count(parent_cell['id'])
                
                # Lade Child-Cells (FRISCH aus DB mit aktuellem analyzed Status!)
                child_cells_data = await parent_cell_service.load_child_cells(parent_cell['id'])
                
                # Debug: Zeige analyzed Status DIREKT nach dem Laden
                if child_cells_data:
                    analyzed_true_count = sum(1 for c in child_cells_data if c.get('analyzed') == True)
                    analyzed_false_count = sum(1 for c in child_cells_data if c.get('analyzed') == False)
                    logger.info(f"   📊 Nach DB-Load: {analyzed_true_count} cells mit analyzed=True, {analyzed_false_count} mit analyzed=False")
                
                # Konvertiere zu GridCellResponse
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
                
                logger.info(f"✅ {len(cell_results)} Child-Cells loaded from cache!")
                logger.info(f"⚡ This area has been scanned {parent_cell['total_scans']}x times")
                
                # Check if cells have descriptions and analyze missing ones
                await analyze_hotspot_cells_with_ai(
                    saved_cells=child_cells_data,  # Original data from DB with IDs and analyzed status
                    parent_cell_id=parent_cell['id'],
                    user_lat=lat,
                    user_lon=lon,
                    user_id=user_id,  # For automatic mission generation
                    max_cells=MAX_CELLS_ANALYSIS  # ✅ Konsistenter Wert
                )
        
        # ========================================
        # FALLBACK: Neuer Scan
        # ========================================
        if not cell_results:
            logger.info("🔍 Kein Cache verfügbar → Starte neuen Scan...")
            
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
                    max_cells=10000
                )
            else:
                cell_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores(
                    grid_cells=grid_cells,
                    scene_id=scene_id,
                    max_cells=100
                )
            
            # Speichere in DB (nur wenn Cache aktiviert)
            if use_cache:
                logger.info("💾 Speichere Scan für zukünftige User...")
                
                # Erstelle Parent-Cell
                parent_cell = await parent_cell_service.create_parent_cell(
                    lat=lat,
                    lon=lon,
                    landsat_scene_id=landsat_scene_id,
                    ndvi_source=ndvi_source
                )
                
                # Speichere Child-Cells
                saved_cells = await parent_cell_service.save_child_cells(
                    parent_cell_id=parent_cell['id'],
                    grid_cells=cell_results
                )
                
                logger.info("✅ Scan saved! Next user can load from cache.")
                
                # KI-Analyse erfolgt NUR beim Login über /scan-on-login
        
        # ========================================
        # VISUALISIERUNG
        # ========================================
        bounds = {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max
        }
        
        logger.info("Erstelle Heatmap-Visualisierung...")
        html_map = visualization_service.create_heatmap(cell_results, bounds)
        
        logger.info("=" * 70)
        logger.info(f"✅ Visualisierung bereit:")
        logger.info(f"   From Cache: {from_cache}")
        logger.info(f"   Total Cells: {len(cell_results)}")
        if parent_cell:
            logger.info(f"   Total Scans (dieser Bereich): {parent_cell['total_scans']}")
        logger.info("=" * 70)
        
        return HTMLResponse(content=html_map)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Fehler bei Radius-Heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der Verarbeitung: {str(e)}"
        )

@router.post("/scan-on-login")
async def scan_on_login(
    user_id: str = Query(..., description="User ID"),
    latitude: float = Query(..., description="User Latitude", ge=-90, le=90),
    longitude: float = Query(..., description="User Longitude", ge=-180, le=180),
    radius_m: int = Query(500, description="Scan Radius", ge=100, le=2000)
):
    """
    🚀 SCAN ON LOGIN - MIT ANTI-ENDLESS-LOOP PROTECTION
    """
    try:
        logger.info("=" * 70)
        logger.info("🚀 SCAN ON LOGIN (MIT LOOP-PROTECTION)")
        logger.info(f"   User: {user_id}")
        logger.info("=" * 70)
        
        # 0. ANTI-ENDLESS-LOOP: Prüfe TODAY'S ANALYSES zuerst!
        from datetime import datetime
        today = datetime.now().date()
        
        today_analyses_response = supabase_service.client.table("cell_analyses").select(
            "id, created_at"
        ).eq("user_id", user_id).gte("created_at", f"{today}T00:00:00").execute()
        
        today_analyses_count = len(today_analyses_response.data) if today_analyses_response.data else 0
        logger.info(f"📊 {today_analyses_count} KI-Analysen von User {user_id} HEUTE")
        
        # ANTI-ENDLESS-LOOP: MAX 2 Analysen pro Tag!
        if today_analyses_count >= 2:
            logger.info("✅ MAXIMUM ERREICHT: User hat bereits 2 Analysen heute - überspringe KI-Analyse")
            return JSONResponse(content={
                "success": True,
                "message": "Tageslimit erreicht - bereits 2 Analysen heute",
                "ai_analysis_performed": False
            })
        
        # 1. Restlicher Code bleibt gleich...
        parent_cell = await parent_cell_service.find_existing_parent_cell(latitude, longitude)
        child_cells = []
        
        if parent_cell:
            logger.info(f"✅ Parent Cell bereits vorhanden: {parent_cell['id']}")
            child_cells = await parent_cell_service.load_child_cells(parent_cell['id'])
            logger.info(f"📊 {len(child_cells)} existierende Child Cells geladen")
            
            if len(child_cells) == 0:
                parent_cell = None
        
        # Neuer Scan wenn nötig...
        if not parent_cell or len(child_cells) == 0:
            logger.info("🔄 Keine Parent-Cell im Cache → starte neuen Login-Scan...")
            
            lat_offset = radius_m / 111000
            lon_offset = radius_m / (111000 * math.cos(math.radians(latitude)))
            
            lat_min = latitude - lat_offset
            lat_max = latitude + lat_offset
            lon_min = longitude - lon_offset
            lon_max = longitude + lon_offset
            
            grid_cells = grid_service.generate_grid(
                lat_min=lat_min,
                lat_max=lat_max,
                lon_min=lon_min,
                lon_max=lon_max,
                cell_size_m=30
            )
            
            logger.info(f"   Grid erstellt: {len(grid_cells)} Zellen (30m × 30m)")
            
            grid_results, landsat_scene_id, ndvi_source = grid_service.calculate_grid_heat_scores_batch(
                grid_cells=grid_cells,
                scene_id=None,
                max_cells=10000
            )
            
            parent_cell = await parent_cell_service.create_parent_cell(
                lat=latitude,
                lon=longitude,
                landsat_scene_id=landsat_scene_id,
                ndvi_source=ndvi_source
            )
            
            saved_cells = await parent_cell_service.save_child_cells(
                parent_cell_id=parent_cell['id'],
                grid_cells=grid_results
            )
            
            child_cells = saved_cells
        
        # 2. STRENGE ANTI-ENDLESS-LOOP: MAXIMAL 2 Analysen pro Tag!
        remaining_daily_analyses = 2 - today_analyses_count
        max_cells_to_analyze = min(MAX_CELLS_ANALYSIS, remaining_daily_analyses)
        
        if max_cells_to_analyze <= 0:
            logger.info("✅ TAGESLIMIT: Bereits 2 Analysen heute - überspringe KI-Analyse")
            missions_count = 0
            missions_generated = 0
        else:
            logger.info(f"🤖 Starte KI-Analyse: {max_cells_to_analyze} Zellen")
            
            await analyze_hotspot_cells_with_ai(
                saved_cells=child_cells,
                parent_cell_id=parent_cell['id'],
                user_lat=latitude,
                user_lon=longitude,
                user_id=user_id,  # WICHTIG: User-ID mitgeben!
                detection_method=None,
                max_cells=max_cells_to_analyze
            )
            missions_generated = max_cells_to_analyze
            
            if missions_generated > 0:
                missions = await mission_generation_service.generate_missions_from_analyses(
                    parent_cell_id=parent_cell['id'],
                    user_id=user_id,
                    user_lat=latitude,
                    user_lon=longitude,
                    max_missions=5
                )
                missions_count = len(missions)
            else:
                missions_count = 0
        
        return JSONResponse(content={
            "success": True,
            "today_analyses_count": today_analyses_count,
            "max_daily_analyses": 2,
            "new_missions_generated": missions_count,
            "ai_analysis_performed": missions_generated > 0
        })
        
    except Exception as e:
        logger.error(f"❌ scan-on-login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

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