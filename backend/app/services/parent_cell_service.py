"""
Parent Cell Service
Verwaltet große Rasterzellen (~1km) um zu prüfen, ob ein Bereich bereits gescannt wurde.
"""
import math
import logging
from typing import Optional, Dict, List, Tuple
from app.core.supabase_client import supabase_service
from app.services.hotspot_detector import hotspot_detector

logger = logging.getLogger(__name__)


class ParentCellService:
    """
    Service für Parent-Cell-Verwaltung.
    Parent-Cells sind große Bereiche (~1km), um Duplikate zu vermeiden.
    """
    
    def __init__(self):
        self.grid_size_degrees = 0.01  # ~1km bei mittleren Breitengraden
    
    def create_parent_cell_key(
        self, 
        lat: float, 
        lon: float,
        precision: int = 2
    ) -> str:
        """
        Erstellt einen eindeutigen Key für eine Parent-Cell.
        
        Beispiel:
        - Position: (51.5323, -0.0531)
        - Key: "parent_51.53_-0.05"
        
        Args:
            lat: Breitengrad
            lon: Längengrad
            precision: Anzahl Dezimalstellen (2 = ~1km)
        
        Returns:
            Parent-Cell-Key
        """
        lat_rounded = round(lat, precision)
        lon_rounded = round(lon, precision)
        return f"parent_{lat_rounded}_{lon_rounded}"
    
    def calculate_parent_bbox(
        self, 
        lat: float, 
        lon: float
    ) -> Dict[str, float]:
        """
        Berechnet Bounding Box für Parent-Cell um eine Position.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
        
        Returns:
            Dict mit bbox_min_lat, bbox_max_lat, bbox_min_lon, bbox_max_lon
        """
        # Runde auf Grid (0.01° = ~1km)
        lat_grid = math.floor(lat / self.grid_size_degrees) * self.grid_size_degrees
        lon_grid = math.floor(lon / self.grid_size_degrees) * self.grid_size_degrees
        
        return {
            "bbox_min_lat": lat_grid,
            "bbox_max_lat": lat_grid + self.grid_size_degrees,
            "bbox_min_lon": lon_grid,
            "bbox_max_lon": lon_grid + self.grid_size_degrees,
            "center_lat": lat_grid + (self.grid_size_degrees / 2),
            "center_lon": lon_grid + (self.grid_size_degrees / 2)
        }
    
    async def find_existing_parent_cell(
        self, 
        lat: float, 
        lon: float
    ) -> Optional[Dict]:
        """
        Sucht nach existierender Parent-Cell für eine Position.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
        
        Returns:
            Parent-Cell-Daten oder None
        """
        try:
            # Erstelle Key für diese Position
            cell_key = self.create_parent_cell_key(lat, lon)
            
            logger.debug(f"🔍 Suche Parent-Cell: {cell_key}")
            
            # Suche in DB
            response = supabase_service.client.table('parent_cells').select('*').eq('cell_key', cell_key).execute()
            
            if response.data and len(response.data) > 0:
                parent_cell = response.data[0]
                logger.debug(f"✅ Parent-Cell gefunden! ID: {parent_cell['id']}")
                logger.debug(f"   Gescannt: {parent_cell['total_scans']}x")
                logger.debug(f"   Child-Cells: {parent_cell['child_cells_count']}")
                logger.debug(f"   Letzter Scan: {parent_cell['last_scanned_at']}")
                return parent_cell
            else:
                logger.debug(f"❌ Keine Parent-Cell gefunden für {cell_key}")
                return None
        
        except Exception as e:
            logger.error(f"Fehler bei Parent-Cell-Suche: {e}")
            return None
    
    async def create_parent_cell(
        self,
        lat: float,
        lon: float,
        landsat_scene_id: Optional[str] = None,
        sentinel_scene_id: Optional[str] = None,
        ndvi_source: Optional[str] = None
    ) -> Dict:
        """
        Erstellt eine neue Parent-Cell.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
            landsat_scene_id: Landsat-Szenen-ID
            sentinel_scene_id: Sentinel-2-Szenen-ID
            ndvi_source: NDVI-Quelle
        
        Returns:
            Erstellte Parent-Cell
        """
        try:
            # Erstelle Key und BBox
            cell_key = self.create_parent_cell_key(lat, lon)
            bbox = self.calculate_parent_bbox(lat, lon)
            
            logger.info(f"📦 Erstelle neue Parent-Cell: {cell_key}")
            logger.info(f"   BBox: ({bbox['bbox_min_lat']:.4f}, {bbox['bbox_min_lon']:.4f}) "
                       f"bis ({bbox['bbox_max_lat']:.4f}, {bbox['bbox_max_lon']:.4f})")
            
            # Erstelle in DB
            parent_data = {
                'cell_key': cell_key,
                'center_lat': bbox['center_lat'],
                'center_lon': bbox['center_lon'],
                'bbox_min_lat': bbox['bbox_min_lat'],
                'bbox_min_lon': bbox['bbox_min_lon'],
                'bbox_max_lat': bbox['bbox_max_lat'],
                'bbox_max_lon': bbox['bbox_max_lon'],
                'total_scans': 1,
                'last_scanned_at': 'now()',
                'landsat_scene_id': landsat_scene_id,
                'sentinel_scene_id': sentinel_scene_id,
                'ndvi_source': ndvi_source
            }
            
            response = supabase_service.client.table('parent_cells').insert(parent_data).execute()
            
            parent_cell = response.data[0]
            logger.info(f"✅ Parent-Cell erstellt! ID: {parent_cell['id']}")
            
            return parent_cell
        
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Parent-Cell: {e}")
            raise
    
    async def increment_scan_count(self, parent_cell_id: str) -> None:
        """
        Erhöht den Scan-Counter einer Parent-Cell.
        
        Args:
            parent_cell_id: Parent-Cell-ID
        """
        try:
            response = supabase_service.client.table('parent_cells').update({
                'total_scans': supabase_service.client.table('parent_cells').select('total_scans').eq('id', parent_cell_id).execute().data[0]['total_scans'] + 1,
                'last_scanned_at': 'now()'
            }).eq('id', parent_cell_id).execute()
            
            logger.info(f"📊 Scan-Counter erhöht für Parent-Cell {parent_cell_id}")
        
        except Exception as e:
            logger.error(f"Fehler beim Erhöhen des Scan-Counters: {e}")
    
    async def load_child_cells(
        self, 
        parent_cell_id: str,
        only_hotspots: bool = False
    ) -> List[Dict]:
        """
        Lädt Child-Cells einer Parent-Cell aus der DB.
        
        Args:
            parent_cell_id: Parent-Cell-ID
            only_hotspots: Wenn True, lade nur Zellen mit analyzed=True (Performance-Optimierung)
        
        Returns:
            Liste von Child-Cells
        """
        try:
            if only_hotspots:
                logger.debug(f"📥 Lade Hotspot-Cells (analyzed=True) für Parent {parent_cell_id}...")
                # ✅ BUG FIX #9: Lade nur Hotspots, verhindert Supabase 1000-Zeilen-Limit
                response = supabase_service.client.table('child_cells')\
                    .select('*')\
                    .eq('parent_cell_id', parent_cell_id)\
                    .eq('analyzed', True)\
                    .execute()
            else:
                logger.debug(f"📥 Lade alle Child-Cells für Parent {parent_cell_id}...")
                # WARNUNG: Supabase gibt standardmäßig nur 1000 Zeilen zurück!
                # Für große Parent-Cells (>1000 Zellen) könnte Pagination nötig sein
                response = supabase_service.client.table('child_cells')\
                    .select('*')\
                    .eq('parent_cell_id', parent_cell_id)\
                    .limit(2000)\
                    .execute()
            
            child_cells = response.data or []
            logger.debug(f"✅ {len(child_cells)} Child-Cells geladen")
            
            # Debug: Prüfe ob 'analyzed' Feld vorhanden ist
            if child_cells:
                needs_analysis_count = sum(1 for c in child_cells if c.get('analyzed') == True)
                already_done_count = sum(1 for c in child_cells if c.get('analyzed') == False)
                
                if needs_analysis_count > 0:
                    logger.debug(f"   🔄 {needs_analysis_count} cells warten auf KI-Analyse (analyzed=True)")
                if already_done_count > 0:
                    logger.debug(f"   ✅ {already_done_count} cells bereits analysiert (analyzed=False)")
            
            return child_cells
        
        except Exception as e:
            logger.error(f"Fehler beim Laden der Child-Cells: {e}")
            return []
    
    async def save_child_cells(
        self,
        parent_cell_id: str,
        grid_cells: List[Dict]
    ) -> List[Dict]:
        """
        Speichert Child-Cells in der Datenbank.
        
        Args:
            parent_cell_id: Parent-Cell-ID
            grid_cells: Liste von GridCellResponse-Objekten
        
        Returns:
            Gespeicherte Child-Cells
        """
        try:
            logger.info(f"💾 Speichere {len(grid_cells)} Child-Cells...")
            
            # Dynamische Hotspot-Erkennung für neue Child-Cells
            detection_input = [
                {'cell_id': cell.cell_id, 'heat_score': cell.heat_score}
                for cell in grid_cells
            ]

            hotspot_cells, threshold_info = hotspot_detector.detect_auto(
                detection_input,
                method="adaptive"
            )
            hotspot_ids = {c['cell_id'] for c in hotspot_cells}

            logger.info(
                "🔥 Dynamic hotspot marking: %d/%d Zellen benötigen Analyse",
                len(hotspot_ids),
                len(grid_cells)
            )
            if isinstance(threshold_info, (int, float)):
                logger.info("   Threshold: %.2f", threshold_info)
            else:
                logger.info("   Threshold info: %s", threshold_info)

            # Konvertiere zu DB-Format
            child_cells_data = []
            for cell in grid_cells:
                needs_analysis = cell.cell_id in hotspot_ids

                child_data = {
                    'parent_cell_id': parent_cell_id,
                    'cell_id': cell.cell_id,
                    'center_lat': (cell.lat_min + cell.lat_max) / 2,
                    'center_lon': (cell.lon_min + cell.lon_max) / 2,
                    'lat_min': cell.lat_min,
                    'lat_max': cell.lat_max,
                    'lon_min': cell.lon_min,
                    'lon_max': cell.lon_max,
                    'temperature': cell.temp,
                    'ndvi': cell.ndvi,
                    'heat_score': cell.heat_score,
                    'cell_size_m': 30,  # TODO: Dynamisch
                    'pixel_count': cell.pixel_count,
                    'is_hotspot': needs_analysis,
                    'analyzed': needs_analysis  # ✅ True → wartet auf Analyse
                }
                child_cells_data.append(child_data)
            
            # Batch-Insert
            response = supabase_service.client.table('child_cells').insert(child_cells_data).execute()
            
            saved_cells = response.data or []
            
            # Debug: Zeige wie viele Zellen auf Analyse warten
            cells_to_analyze = sum(1 for c in child_cells_data if c.get('analyzed') == True)
            logger.info(f"✅ {len(saved_cells)} Child-Cells gespeichert!")
            if cells_to_analyze > 0:
                logger.info(f"   🔄 {cells_to_analyze} Zellen warten auf KI-Analyse (dynamischer Threshold)")
            
            # Trigger updatet automatisch Parent-Cell-Stats
            
            return saved_cells
        
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Child-Cells: {e}")
            raise


# Singleton-Instanz
parent_cell_service = ParentCellService()

