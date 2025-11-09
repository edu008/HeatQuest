"""
Sentinel-2 Service: Lädt und verarbeitet Sentinel-2 Daten für NDVI-Berechnung.
Basiert auf der Notebook-Implementierung mit B04 (Red) und B08 (NIR).
"""

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import rasterio
from rasterio.io import MemoryFile
from rasterio.mask import mask
import numpy as np
from typing import Dict, Tuple, Optional
import logging
from pyproj import CRS, Transformer
from shapely.ops import transform as shapely_transform
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class SentinelService:
    """
    Service für Sentinel-2 Daten und NDVI-Berechnung.
    Nutzt AWS Open Data Registry: s3://sentinel-s2-l2a
    
    NDVI Formel (aus deinem Notebook):
    NDVI = (NIR - Red) / (NIR + Red)
    """
    
    # Sentinel-2 L2A auf AWS (Requester Pays)
    SENTINEL_BUCKET = "sentinel-s2-l2a"
    SENTINEL_REGION = "eu-central-1"
    
    def __init__(self):
        # S3-Client für Sentinel-2 (Requester Pays aktiviert)
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=self.SENTINEL_REGION
            )
        else:
            # Ohne Credentials - nur für Public Access (wird bei Requester Pays fehlschlagen)
            self.s3_client = boto3.client(
                's3',
                region_name=self.SENTINEL_REGION,
                config=Config(signature_version=UNSIGNED)
            )
    
    def calculate_ndvi(
        self,
        lat: float,
        lon: float,
        radius: float = 200,
        mgrs_tile: Optional[str] = None
    ) -> Dict:
        """
        Berechnet NDVI für einen Punkt aus Sentinel-2 Daten.
        
        Formel aus deinem Notebook:
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            lat: Breitengrad
            lon: Längengrad
            radius: Radius in Metern
            mgrs_tile: MGRS Tile (optional, wird sonst berechnet)
        
        Returns:
            Dictionary mit mean_ndvi, min_ndvi, max_ndvi, pixel_count, source
        """
        
        logger.info(f"🌿 Berechne NDVI für ({lat}, {lon}) mit Radius {radius}m")
        
        try:
            # 1. Bestimme MGRS Tile
            if mgrs_tile is None:
                mgrs_tile = self._get_mgrs_tile(lat, lon)
            
            # 2. Finde Sentinel-2 Szene
            scene_path = self._find_sentinel_scene(mgrs_tile)
            
            if scene_path is None:
                logger.warning("⚠️ Keine Sentinel-2 Szene gefunden, nutze Schätzung")
                return self._estimate_ndvi()
            
            # 3. Lade B04 (Red) und B08 (NIR)
            logger.info("Lade Sentinel-2 Bands (B04 Red + B08 NIR)...")
            red_array, red_transform, red_crs = self._load_sentinel_band(scene_path, "B04")
            nir_array, nir_transform, nir_crs = self._load_sentinel_band(scene_path, "B08")
            
            # 4. Berechne NDVI
            logger.info("Berechne NDVI: (NIR - Red) / (NIR + Red)")
            ndvi_array = self._calculate_ndvi_from_bands(red_array, nir_array)
            
            # 5. Maskiere auf Buffer
            from app.core.geo import create_buffer_around_point
            from pyproj import CRS, Transformer
            from shapely.ops import transform as shapely_transform
            from rasterio.io import MemoryFile
            from rasterio.mask import mask
            
            # Erstelle Buffer um Punkt
            _, buffer_geom = create_buffer_around_point(lat, lon, radius)
            
            # Transformiere Buffer von WGS84 zu Raster-CRS
            transformer = Transformer.from_crs(
                CRS.from_epsg(4326),
                CRS.from_string(red_crs.to_string()),
                always_xy=True
            )
            buffer_raster_crs = shapely_transform(transformer.transform, buffer_geom)
            
            # Maskiere NDVI auf Buffer
            with MemoryFile() as memfile:
                with memfile.open(
                    driver='GTiff',
                    height=ndvi_array.shape[0],
                    width=ndvi_array.shape[1],
                    count=1,
                    dtype=ndvi_array.dtype,
                    crs=red_crs,
                    transform=red_transform
                ) as dataset:
                    dataset.write(ndvi_array, 1)
                    
                    out_image, out_transform = mask(
                        dataset,
                        [buffer_raster_crs],
                        crop=True,
                        nodata=-9999
                    )
                    
                    masked_ndvi = out_image[0]
            
            # 6. Berechne Statistiken
            valid_pixels = masked_ndvi[(masked_ndvi != -9999) & (~np.isnan(masked_ndvi))]
            
            if len(valid_pixels) == 0:
                logger.warning("Keine gültigen NDVI-Pixel gefunden, nutze Schätzung")
                return self._estimate_ndvi()
            
            mean_ndvi = float(np.mean(valid_pixels))
            min_ndvi = float(np.min(valid_pixels))
            max_ndvi = float(np.max(valid_pixels))
            pixel_count = len(valid_pixels)
            
            logger.info(f"✅ NDVI berechnet: mean={mean_ndvi:.3f}, pixels={pixel_count}")
            
            return {
                "mean_ndvi": round(mean_ndvi, 3),
                "min_ndvi": round(min_ndvi, 3),
                "max_ndvi": round(max_ndvi, 3),
                "pixel_count": pixel_count,
                "source": "sentinel-2"
            }
        
        except Exception as e:
            logger.error(f"❌ Fehler bei NDVI-Berechnung: {e}", exc_info=True)
            logger.warning("Nutze NDVI-Schätzung als Fallback")
            return self._estimate_ndvi()
    
    def _estimate_ndvi(self) -> Dict:
        """
        Schätzt NDVI für urbane Gebiete (Fallback).
        
        Returns:
            Dictionary mit geschätzten NDVI-Werten
        """
        # Intelligente Schätzung basierend auf typischen Werten:
        # Urbane Gebiete (London, Berlin): 0.2-0.35
        # Parks/Grünflächen: 0.35-0.6
        # Dichte Vegetation: 0.6-0.9
        # Wasser/Beton: -0.1 bis 0.1
        
        mean_ndvi = 0.3
        
        return {
            "mean_ndvi": round(mean_ndvi, 3),
            "min_ndvi": round(mean_ndvi - 0.1, 3),
            "max_ndvi": round(mean_ndvi + 0.1, 3),
            "pixel_count": 1,
            "source": "estimated_urban"
        }
    
    def _get_mgrs_tile(self, lat: float, lon: float) -> str:
        """
        Konvertiert GPS-Koordinaten zu MGRS Tile.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
        
        Returns:
            MGRS Tile ID (z.B. "30UXC" für London)
        """
        try:
            import mgrs
            
            m = mgrs.MGRS()
            # Konvertiere zu MGRS (Precision 0 = nur Tile, kein Grid Square Detail)
            mgrs_code = m.toMGRS(lat, lon, MGRSPrecision=0)
            
            # MGRS Format: "30UXC" (Zone + Band + 100km Grid)
            # Wir brauchen nur die ersten 5 Zeichen
            tile = mgrs_code[:5]
            
            logger.info(f"MGRS Tile für ({lat}, {lon}): {tile}")
            return tile
            
        except Exception as e:
            logger.error(f"Fehler bei MGRS-Konvertierung: {e}")
            raise
    
    def _find_sentinel_scene(
        self,
        mgrs_tile: str,
        max_cloud_cover: float = 30.0
    ) -> Optional[str]:
        """
        Findet die neueste Sentinel-2 Szene für ein MGRS Tile.
        
        Sentinel-2 Struktur:
        tiles/{UTM_ZONE}/{LAT_BAND}/{GRID_SQ}/{YEAR}/{MONTH}/{DAY}/{SEQ}/
        z.B. tiles/30/U/YC/2023/10/15/0/
        
        Args:
            mgrs_tile: MGRS Tile (z.B. "30UYC")
            max_cloud_cover: Maximale Wolkenbedeckung
        
        Returns:
            Kompletter Scene path oder None
        """
        try:
            from datetime import datetime, timedelta
            
            utm_zone = mgrs_tile[:2]  # "30"
            lat_band = mgrs_tile[2]   # "U"
            grid_sq = mgrs_tile[3:5]  # "YC"
            
            base_prefix = f"tiles/{utm_zone}/{lat_band}/{grid_sq}/"
            
            logger.info(f"Suche Sentinel-2 Szenen in: s3://{self.SENTINEL_BUCKET}/{base_prefix}")
            
            # Durchsuche die letzten 3 Monate rückwärts
            current_date = datetime.now()
            
            for days_back in range(0, 90):
                check_date = current_date - timedelta(days=days_back)
                year = check_date.year
                month = check_date.month
                day = check_date.day
                
                # Baue Präfix für diesen Tag
                day_prefix = f"{base_prefix}{year}/{month}/{day}/"
                
                try:
                    # Prüfe ob Daten für diesen Tag existieren
                    response = self.s3_client.list_objects_v2(
                        Bucket=self.SENTINEL_BUCKET,
                        Prefix=day_prefix,
                        Delimiter='/',
                        MaxKeys=10,
                        RequestPayer='requester'
                    )
                    
                    if 'CommonPrefixes' in response and len(response['CommonPrefixes']) > 0:
                        # Finde die erste Sequenz (meist "0")
                        sequences = sorted([p['Prefix'] for p in response['CommonPrefixes']])
                        scene_path = sequences[0]  # Nehme erste Sequenz
                        
                        logger.info(f"✅ Sentinel-2 Szene gefunden: {scene_path}")
                        return scene_path
                        
                except Exception as e:
                    # Dieser Tag hat keine Daten, weiter zum nächsten
                    continue
            
            logger.warning(f"❌ Keine Sentinel-2 Szene für MGRS Tile {mgrs_tile} in den letzten 90 Tagen gefunden")
            return None
                
        except Exception as e:
            logger.error(f"Fehler bei Sentinel-2 Szenensuche: {e}")
            return None
    
    def _load_sentinel_band(
        self,
        scene_path: str,
        band: str
    ) -> Tuple[np.ndarray, any, any]:
        """
        Lädt ein Sentinel-2 Band von AWS S3.
        
        Versucht verschiedene Pfad-Varianten:
        1. R10m/{band}_10m.jp2 (Standard L2A Format)
        2. {band}.jp2 (alternatives Format)
        3. {band}_10m.jp2 (direktes Format)
        
        Args:
            scene_path: Pfad zur Szene (z.B. "tiles/30/U/YC/2025/11/5/0/")
            band: Band-Name ("B04" für Red, "B08" für NIR)
        
        Returns:
            Tuple: (Raster-Array, Transform-Objekt, CRS)
        """
        
        # Verschiedene Pfad-Varianten zum Ausprobieren
        # Basierend auf AWS Exploration: tiles/30/U/YC/2025/11/8/0/R10m/B04.jp2
        possible_keys = [
            f"{scene_path.rstrip('/')}/R10m/{band}.jp2",      # ✅ Korrekt (verifiziert)
            f"{scene_path.rstrip('/')}/R10m/{band}_10m.jp2",  # Alternative 1
            f"{scene_path.rstrip('/')}/{band}.jp2",            # Alternative 2
        ]
        
        last_error = None
        
        for i, s3_key in enumerate(possible_keys):
            try:
                if i == 0:
                    logger.info(f"Versuche Band zu laden: {band}")
                
                logger.debug(f"  Versuch {i+1}: s3://{self.SENTINEL_BUCKET}/{s3_key}")
                
                # Lade von S3
                response = self.s3_client.get_object(
                    Bucket=self.SENTINEL_BUCKET,
                    Key=s3_key,
                    RequestPayer='requester'
                )
                
                band_bytes = response['Body'].read()
                
                # Öffne mit rasterio
                with MemoryFile(band_bytes) as memfile:
                    with memfile.open() as dataset:
                        band_array = dataset.read(1)
                        transform = dataset.transform
                        crs = dataset.crs
                        
                        logger.info(f"✅ Band {band} geladen: {s3_key.split('/')[-1]}, Shape={band_array.shape}, CRS={crs}")
                        
                        return band_array, transform, crs
                        
            except Exception as e:
                last_error = e
                logger.debug(f"  ❌ Versuch {i+1} fehlgeschlagen: {e}")
                continue
        
        # Wenn alle Versuche fehlgeschlagen sind
        logger.error(f"❌ Band {band} konnte nicht geladen werden nach {len(possible_keys)} Versuchen")
        logger.error(f"   Letzter Fehler: {last_error}")
        raise last_error
    
    def _calculate_ndvi_from_bands(
        self,
        red: np.ndarray,
        nir: np.ndarray
    ) -> np.ndarray:
        """
        Berechnet NDVI aus Red und NIR Bändern.
        
        Formel aus deinem Notebook:
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            red: Red Band (B04) Array
            nir: NIR Band (B08) Array
        
        Returns:
            NDVI Array
        """
        # Verhindere Division durch 0
        np.seterr(divide='ignore', invalid='ignore')
        
        denominator = nir + red
        ndvi = np.where(denominator == 0, 0, (nir - red) / denominator)
        
        # NDVI ist zwischen -1 und +1
        # Setze ungültige Werte auf 0
        ndvi = np.nan_to_num(ndvi, nan=0.0)
        
        return ndvi
    
    def load_ndvi_raster_for_bbox(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        mgrs_tile: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Lädt NDVI-Raster für eine Bounding Box und speichert es temporär.
        
        **BATCH-OPTIMIERUNG:** Lädt Raster nur EINMAL für alle Grid-Zellen!
        
        Workflow (wie im Notebook):
        1. Lade Red (B04) und NIR (B08) Bänder
        2. Berechne NDVI: (NIR - Red) / (NIR + Red)
        3. Speichere als GeoTIFF
        
        Args:
            lat_min: Minimaler Breitengrad
            lat_max: Maximaler Breitengrad
            lon_min: Minimaler Längengrad
            lon_max: Maximaler Längengrad
            mgrs_tile: MGRS Tile (optional)
        
        Returns:
            Tuple: (ndvi_raster_path, source)
        """
        import os
        
        logger.info(f"🌿 Lade NDVI-Raster für Bounding Box: ({lat_min},{lon_min}) bis ({lat_max},{lon_max})")
        
        try:
            # 1. Bestimme MGRS Tile (verwende Zentrum der Bounding Box)
            if mgrs_tile is None:
                center_lat = (lat_min + lat_max) / 2
                center_lon = (lon_min + lon_max) / 2
                mgrs_tile = self._get_mgrs_tile(center_lat, center_lon)
            
            # 2. Finde Sentinel-2 Szene
            scene_path = self._find_sentinel_scene(mgrs_tile)
            
            if scene_path is None:
                logger.warning("⚠️ Keine Sentinel-2 Szene gefunden, erstelle NDVI-Schätzung")
                return self._create_estimated_ndvi_raster(lat_min, lat_max, lon_min, lon_max)
            
            # 3. Lade B04 (Red) und B08 (NIR)
            logger.info("Lade Sentinel-2 Bands (B04 Red + B08 NIR)...")
            red_array, red_transform, red_crs = self._load_sentinel_band(scene_path, "B04")
            nir_array, nir_transform, nir_crs = self._load_sentinel_band(scene_path, "B08")
            
            # 4. Berechne NDVI (wie im Notebook)
            logger.info("Berechne NDVI: (NIR - Red) / (NIR + Red)")
            ndvi_array = self._calculate_ndvi_from_bands(red_array, nir_array)
            
            # 5. Speichere als temporäre GeoTIFF-Datei
            temp_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Eindeutiger Dateiname basierend auf MGRS Tile
            ndvi_raster_path = os.path.join(temp_dir, f'temp_ndvi_{mgrs_tile}.tif')
            
            # Schreibe NDVI-Raster in Datei
            with rasterio.open(
                ndvi_raster_path,
                'w',
                driver='GTiff',
                height=ndvi_array.shape[0],
                width=ndvi_array.shape[1],
                count=1,
                dtype='float32',
                crs=red_crs,
                transform=red_transform
            ) as dst:
                dst.write(ndvi_array.astype('float32'), 1)
            
            logger.info(f"✅ NDVI-Raster gespeichert: {ndvi_raster_path}")
            logger.info(f"   Shape: {ndvi_array.shape}, CRS: {red_crs}")
            
            return ndvi_raster_path, "sentinel-2"
        
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden von NDVI-Raster: {e}", exc_info=True)
            logger.warning("Erstelle NDVI-Schätzung als Fallback")
            return self._create_estimated_ndvi_raster(lat_min, lat_max, lon_min, lon_max)
    
    def _create_estimated_ndvi_raster(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float
    ) -> Tuple[str, str]:
        """
        Erstellt ein geschätztes NDVI-Raster für urbane Gebiete (Fallback).
        
        Args:
            lat_min, lat_max, lon_min, lon_max: Bounding Box
        
        Returns:
            Tuple: (ndvi_raster_path, source)
        """
        import os
        from rasterio.transform import from_bounds
        
        logger.info("Erstelle geschätztes NDVI-Raster für urbanes Gebiet...")
        
        # Erstelle ein kleines Raster mit geschätzten NDVI-Werten
        # Für urbane Gebiete: ~0.3
        width = 100
        height = 100
        ndvi_array = np.full((height, width), 0.3, dtype='float32')
        
        # Berechne Transform für Bounding Box
        transform = from_bounds(lon_min, lat_min, lon_max, lat_max, width, height)
        
        # Speichere als temporäre Datei
        temp_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
        os.makedirs(temp_dir, exist_ok=True)
        
        ndvi_raster_path = os.path.join(temp_dir, 'temp_ndvi_estimated.tif')
        
        with rasterio.open(
            ndvi_raster_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype='float32',
            crs='EPSG:4326',
            transform=transform
        ) as dst:
            dst.write(ndvi_array, 1)
        
        logger.info(f"✅ Geschätztes NDVI-Raster erstellt: {ndvi_raster_path}")
        
        return ndvi_raster_path, "estimated_urban"


# Singleton-Instanz
sentinel_service = SentinelService()

