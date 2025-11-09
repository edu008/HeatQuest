"""
STAC Service: Suche nach passenden Landsat-Szenen basierend auf GPS-Koordinaten.
Berechnet WRS-2 Path/Row mit offiziellen USGS Shapefiles und listet verfügbare Szenen direkt aus S3.
"""

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import math
import os
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class STACService:
    """
    Service für die Suche nach Landsat-Szenen.
    Nutzt offizielle USGS WRS-2 Shapefiles für präzise Path/Row Bestimmung.
    """
    
    # URLs zum offiziellen WRS-2 Shapefile (mit Fallbacks)
    WRS2_SHAPEFILE_URLS = [
        "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip",
        "https://prd-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip",
    ]
    
    def __init__(self):
        # S3-Client für direkten Zugriff auf Landsat-Bucket
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
        else:
            self.s3_client = boto3.client(
                's3',
                region_name=settings.aws_region,
                config=Config(signature_version=UNSIGNED)
            )
        self.bucket = settings.landsat_bucket
        
        # WRS-2 Shapefile Cache
        self.wrs2_gdf = None
        self.cache_dir = Path(__file__).parent.parent.parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.wrs2_shapefile_path = self.cache_dir / "WRS2_descending.shp"
    
    def _download_wrs2_shapefile(self):
        """
        Lädt das WRS-2 Shapefile von USGS herunter und entpackt es.
        Versucht mehrere URLs als Fallback.
        """
        import requests
        import zipfile
        from io import BytesIO
        
        logger.info("📥 Versuche WRS-2 Shapefile herunterzuladen...")
        
        # Versuche alle URLs
        for i, url in enumerate(self.WRS2_SHAPEFILE_URLS):
            try:
                logger.info(f"Versuche URL {i+1}/{len(self.WRS2_SHAPEFILE_URLS)}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Entpacke ZIP
                with zipfile.ZipFile(BytesIO(response.content)) as zf:
                    zf.extractall(self.cache_dir)
                
                logger.info(f"✅ WRS-2 Shapefile gespeichert in: {self.cache_dir}")
                return True
            
            except Exception as e:
                logger.warning(f"URL {i+1} fehlgeschlagen: {e}")
                continue
        
        logger.error(f"❌ Alle {len(self.WRS2_SHAPEFILE_URLS)} Download-URLs fehlgeschlagen")
        return False
    
    def _load_wrs2_shapefile(self):
        """
        Lädt das WRS-2 Shapefile mit geopandas.
        Umgeht fiona.path Probleme durch direktes Laden.
        """
        try:
            import geopandas as gpd
            import warnings
            
            # Prüfe ob Shapefile existiert
            if not self.wrs2_shapefile_path.exists():
                logger.info("WRS-2 Shapefile nicht gefunden, lade herunter...")
                if not self._download_wrs2_shapefile():
                    return False
            
            # Lade Shapefile (unterdrücke fiona Warnings)
            logger.info("📂 Lade WRS-2 Shapefile...")
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Versuche mit engine='pyogrio' (schneller und moderner)
                try:
                    self.wrs2_gdf = gpd.read_file(self.wrs2_shapefile_path, engine='pyogrio')
                    logger.info(f"✅ WRS-2 Shapefile geladen mit pyogrio ({len(self.wrs2_gdf)} Kacheln)")
                except:
                    # Fallback zu fiona ohne engine
                    import os
                    os.environ['GDAL_PAM_ENABLED'] = 'NO'
                    self.wrs2_gdf = gpd.read_file(str(self.wrs2_shapefile_path))
                    logger.info(f"✅ WRS-2 Shapefile geladen mit fiona ({len(self.wrs2_gdf)} Kacheln)")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden des WRS-2 Shapefiles: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def latlon_to_wrs2(self, lat: float, lon: float) -> Tuple[int, int]:
        """
        Konvertiert GPS-Koordinaten zu WRS-2 Path/Row.
        Nutzt offizielle USGS WRS-2 Shapefiles mit geopandas für maximale Genauigkeit.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
        
        Returns:
            Tuple (path, row)
        """
        
        # Versuche mit geopandas + WRS-2 Shapefile
        try:
            import geopandas as gpd
            from shapely.geometry import Point
            
            # Lade Shapefile falls noch nicht geladen
            if self.wrs2_gdf is None:
                if not self._load_wrs2_shapefile():
                    raise Exception("WRS-2 Shapefile konnte nicht geladen werden")
            
            # Erstelle Point-Geometrie (lon, lat!)
            point = Point(lon, lat)
            
            # Suche Kachel die den Punkt enthält
            matches = self.wrs2_gdf[self.wrs2_gdf.contains(point)]
            
            if len(matches) > 0:
                # Nimm die erste Kachel
                tile = matches.iloc[0]
                path = int(tile['PATH'])
                row = int(tile['ROW'])
                logger.info(f"📍 WRS-2 (USGS Shapefile): ({lat:.4f}, {lon:.4f}) → Path {path:03d}, Row {row:03d}")
                return (path, row)
            else:
                logger.warning(f"⚠️ Keine WRS-2 Kachel für Punkt gefunden, nutze Fallback-Formel")
        
        except Exception as e:
            logger.warning(f"⚠️ WRS-2 Shapefile-Suche fehlgeschlagen ({e}), nutze Fallback-Formel")
        
        # Fallback: Manuelle Suche in erweiterten Bereich
        # Da die Formel ungenau ist, geben wir einen guten "Startpunkt" zurück
        # und verlassen uns auf die Nachbarsuche in find_best_scene
        
        # Grobe Näherung für Path (basiert auf Längengrad)
        # Path 1 ist bei ~-64.6°, jedes Path ~1.5° breit
        lon_normalized = (lon + 180) % 360 - 180  # -180 bis +180
        path = int((lon_normalized + 64.6) / 1.5) + 1
        path = max(1, min(233, path))
        
        # Grobe Näherung für Row (basiert auf Breitengrad)  
        # Äquator ist ca. Row 60, nördlich nimmt Row ab
        row = int(60 - (lat / 1.45))
        row = max(1, min(248, row))
        
        logger.info(f"📍 WRS-2 (Fallback): ({lat:.4f}, {lon:.4f}) → Path {path:03d}, Row {row:03d} (Näherung)")
        logger.info(f"💡 Hinweis: Fallback-Formel ist ungenau, Nachbarsuche wird automatisch erweitert")
        
        return (path, row)
    
    def find_best_scene(
        self, 
        lat: float, 
        lon: float,
        max_cloud_cover: float = 30.0,
        days_back: int = 730  # 2 Jahre
    ) -> Optional[str]:
        """
        Findet die beste Landsat-Szene für gegebene Koordinaten.
        Berechnet WRS-2 Path/Row und sucht gezielt die passende Szene.
        Erweiterte Suche mit ±5 Path/Row für bessere Trefferquote.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
            max_cloud_cover: Maximale Wolkenbedeckung (aktuell nicht verwendet)
            days_back: Wie viele Tage zurück suchen (Standard: 730 = 2 Jahre)
        
        Returns:
            Szenen-ID (z.B. "LC08_L2SP_201024_20230715_02_T1") oder None
        """
        
        logger.info(f"🔍 Suche Landsat-Szene für ({lat}, {lon})")
        
        # Berechne WRS-2 Path/Row 
        path, row = self.latlon_to_wrs2(lat, lon)
        
        # Kandidaten: Haupttreffer + Nachbarn
        # Bei Shapefile: kleine Suche (±1), bei Fallback: erweiterte Suche (±10)
        candidates = [(path, row)]  # Hauptkandidat zuerst
        
        # Prüfe ob Shapefile geladen wurde (genau) oder Fallback (ungenau)
        search_range = 1 if self.wrs2_gdf is not None else 10
        
        # Füge Nachbarn hinzu
        for p_offset in range(-search_range, search_range + 1):
            if p_offset == 0:
                continue
            p = path + p_offset
            if p < 1:
                p = p + 233
            elif p > 233:
                p = p - 233
            if (p, row) not in candidates:
                candidates.append((p, row))
        
        for r_offset in range(-search_range, search_range + 1):
            if r_offset == 0:
                continue
            r = row + r_offset
            if 1 <= r <= 248 and (path, r) not in candidates:
                candidates.append((path, r))
        
        logger.info(f"🎯 Prüfe {len(candidates)} Kandidaten (Suchradius: ±{search_range})")
        
        # Suche gezielt in S3
        for i, (p, r) in enumerate(candidates):
            # Zeige nur die ersten 3 Versuche im Detail-Log
            if i < 3:
                logger.info(f"🔎 Versuche {i+1}/{len(candidates)}: Path {p:03d}, Row {r:03d}")
            elif i == 3 and len(candidates) > 5:
                logger.info(f"🔎 Suche weiter in {len(candidates)-3} weiteren Kandidaten...")
            
            scene_id = self._find_scene_in_s3(p, r, days_back)
            
            if scene_id:
                if i >= 3:
                    logger.info(f"✅ Szene gefunden nach {i+1} Versuchen: Path {p:03d}, Row {r:03d}")
                else:
                    logger.info(f"✅ Szene gefunden: {scene_id}")
                return scene_id
        
        logger.warning(f"❌ Keine Szene gefunden für ({lat}, {lon}) in {len(candidates)} Kandidaten")
        return None
    
    def _find_scene_in_s3(self, path: int, row: int, days_back: int) -> Optional[str]:
        """
        Sucht nach verfügbaren Szenen im S3-Bucket für gegebenen Path/Row.
        
        Args:
            path: WRS-2 Path
            row: WRS-2 Row
            days_back: Wie viele Tage zurück
        
        Returns:
            Szenen-ID oder None
        """
        
        # Suche in den letzten Jahren
        current_year = datetime.now().year
        years_to_search = [current_year, current_year - 1, current_year - 2]
        
        path_str = str(path).zfill(3)
        row_str = str(row).zfill(3)
        
        all_scenes = []
        
        for year in years_to_search:
            try:
                # Pfad im Bucket
                prefix = f"collection02/level-2/standard/oli-tirs/{year}/{path_str}/{row_str}/"
                
                # Liste Szenen im S3 (ohne extra Log - nur bei Erfolg)
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket,
                    Prefix=prefix,
                    Delimiter='/',
                    RequestPayer='requester'
                )
                
                # Extrahiere Szenen-Namen aus CommonPrefixes
                if 'CommonPrefixes' in response:
                    for prefix_obj in response['CommonPrefixes']:
                        scene_path = prefix_obj['Prefix']
                        scene_id = scene_path.rstrip('/').split('/')[-1]
                        
                        # Nur Landsat 8/9 Level-2 Szenen (LC08 oder LC09)
                        if (scene_id.startswith('LC08') or scene_id.startswith('LC09')) and '_L2SP_' in scene_id:
                            all_scenes.append(scene_id)
            
            except Exception as e:
                logger.debug(f"Jahr {year}: Keine Daten ({e})")
                continue
        
        if not all_scenes:
            return None
        
        # Sortiere nach Datum (neuste zuerst) - Datum ist im Scene-ID enthalten
        all_scenes.sort(reverse=True)
        
        # Nimm die neueste Szene
        best_scene = all_scenes[0]
        logger.info(f"   📅 {len(all_scenes)} Szenen verfügbar, neueste: {best_scene}")
        
        return best_scene
    

# Singleton-Instanz
stac_service = STACService()

