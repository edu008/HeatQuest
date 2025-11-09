"""
Landsat-Service: Kernlogik für Temperaturberechnung aus Landsat-Daten.
Lädt thermische Bänder von AWS S3 und berechnet Statistiken.
"""

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import rasterio
from rasterio.mask import mask
from rasterio.io import MemoryFile
import numpy as np
from typing import Dict, Tuple, Optional
import logging

from app.core.config import settings
from app.core.geo import create_buffer_around_point
from app.services.stac_service import stac_service

logger = logging.getLogger(__name__)


class LandsatService:
    """
    Service für Zugriff auf Landsat-Daten und Temperaturberechnung.
    """
    
    def __init__(self):
        """
        Initialisiert den S3-Client mit AWS-Credentials.
        """
        # S3-Client mit Credentials
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
    
    def get_temperature(
        self, 
        lat: float, 
        lon: float, 
        radius: float = 200,
        scene_id: Optional[str] = None
    ) -> Dict:
        """
        Berechnet Temperaturstatistiken für einen Punkt und Radius.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
            radius: Radius in Metern (Standard: 200m)
            scene_id: Landsat-Szenen-ID (optional, automatische Suche)
        
        Returns:
            Dictionary mit mean_temp, min_temp, max_temp, pixel_count
        
        Raises:
            Exception: Bei Problemen mit Datendownload oder -verarbeitung
        """
        
        logger.info(f"Berechne Temperatur für ({lat}, {lon}) mit Radius {radius}m")
        
        # 1. Wenn keine scene_id angegeben, suche automatisch
        if not scene_id:
            logger.info("Keine Szenen-ID angegeben - suche automatisch passende Szene...")
            scene_id = stac_service.find_best_scene(lat, lon)
            
            if not scene_id:
                # Gib hilfreiche Fehlermeldung mit Beispielen
                example_scenes = {
                    "London": "LC09_L2SP_201024_20230721_20230802_02_T1",
                    "New York": "LC09_L2SP_014032_20230715_20230717_02_T1",
                    "Berlin": "LC09_L2SP_193025_20230721_20230802_02_T1",
                    "Tokyo": "LC09_L2SP_107035_20230715_20230717_02_T1"
                }
                examples_str = "\n".join([f"  - {city}: {sid}" for city, sid in example_scenes.items()])
                
                raise Exception(
                    f"Keine passende Landsat-Szene für Koordinaten ({lat}, {lon}) gefunden.\n\n"
                    f"Die automatische Szenensuche funktioniert derzeit nur eingeschränkt.\n"
                    f"Bitte gib eine spezifische scene_id als Parameter an.\n\n"
                    f"Beispiele für bekannte Orte:\n{examples_str}\n\n"
                    f"Nutze: http://localhost:8000/api/v1/heatmap?lat={lat}&lon={lon}&scene_id=SCENE_ID"
                )
        
        logger.info(f"Verwende Szene: {scene_id}")
        
        # 2. Erstelle Buffer um Punkt
        point, buffer_geom = create_buffer_around_point(lat, lon, radius)
        
        # 3. Lade thermisches Band von S3
        thermal_data, transform_obj, crs = self._load_thermal_band(scene_id)
        
        # 4. Validiere, dass Punkt im Raster liegt
        if not self._point_in_raster(lat, lon, transform_obj, thermal_data.shape, crs):
            raise Exception(
                f"Punkt ({lat}, {lon}) liegt nicht in der Szene {scene_id}."
            )
        
        # 5. Schneide Raster auf Buffer zu
        masked_data = self._mask_raster_with_buffer(
            thermal_data, 
            transform_obj, 
            buffer_geom,
            crs
        )
        
        # 6. Berechne Temperaturstatistiken
        stats = self._calculate_temperature_stats(masked_data)
        stats["scene_id"] = scene_id
        
        logger.info(f"Temperaturberechnung abgeschlossen: {stats}")
        return stats
    
    def _point_in_raster(self, lat: float, lon: float, transform: any, shape: tuple, crs: any) -> bool:
        """Prüft ob GPS-Punkt im Raster liegt."""
        try:
            from pyproj import CRS, Transformer
            
            transformer = Transformer.from_crs(
                CRS.from_epsg(4326),
                CRS.from_string(crs.to_string()),
                always_xy=True
            )
            
            x, y = transformer.transform(lon, lat)
            inv_transform = ~transform
            col, row = inv_transform * (x, y)
            
            height, width = shape
            in_bounds = 0 <= col < width and 0 <= row < height
            
            logger.info(f"Punkt-Validierung: ({lat}, {lon}) -> Pixel ({col:.1f}, {row:.1f}), In Bounds: {in_bounds}")
            return in_bounds
        except Exception as e:
            logger.warning(f"Fehler bei Punkt-Validierung: {e}")
            return False
    
    def _load_thermal_band(self, scene_id: str) -> Tuple[np.ndarray, any, any]:
        """
        Lädt das thermische Band (ST_B10) von S3.
        
        Args:
            scene_id: Landsat-Szenen-ID (z.B. LC08_L2SP_193024_20230801_02_T1)
        
        Returns:
            Tuple: (Raster-Array, Transform-Objekt, CRS)
        """
        
        # Konstruiere S3-Pfad zum thermischen Band
        # Format: collection02/level-2/standard/oli-tirs/YYYY/PATH/ROW/SCENE_ID/SCENE_ID_ST_B10.TIF
        
        # Parse Szenen-ID: LC08_L2SP_PPPRRR_YYYYMMDD_YYYYMMDD_CC_TX
        parts = scene_id.split('_')
        path_row = parts[2]  # z.B. "193024"
        path = path_row[:3]   # "193"
        row = path_row[3:]    # "024"
        date_str = parts[3]   # "20230801"
        year = date_str[:4]   # "2023"
        
        # Sensor bestimmen (LC08 = Landsat 8)
        sensor = "oli-tirs" if parts[0] in ["LC08", "LC09"] else "tm"
        
        s3_key = (
            f"collection02/level-2/standard/{sensor}/"
            f"{year}/{path}/{row}/{scene_id}/{scene_id}_ST_B10.TIF"
        )
        
        logger.info(f"Lade Datei von S3: s3://{self.bucket}/{s3_key}")
        
        try:
            # Lade Datei von S3 in Memory (mit RequestPayer)
            response = self.s3_client.get_object(
                Bucket=self.bucket, 
                Key=s3_key,
                RequestPayer='requester'
            )
            tif_bytes = response['Body'].read()
            
            # Öffne mit rasterio aus Memory
            with MemoryFile(tif_bytes) as memfile:
                with memfile.open() as dataset:
                    # Lese Band 1 (thermisches Band)
                    thermal_array = dataset.read(1)
                    transform = dataset.transform
                    crs = dataset.crs
                    
                    logger.info(f"Raster geladen: Shape={thermal_array.shape}, CRS={crs}")
                    
                    return thermal_array, transform, crs
        
        except Exception as e:
            logger.error(f"Fehler beim Laden der Landsat-Daten: {e}")
            raise Exception(f"Konnte Landsat-Daten nicht laden: {e}")
    
    def _mask_raster_with_buffer(
        self, 
        raster_array: np.ndarray, 
        transform: any, 
        buffer_geom: any,
        crs: any
    ) -> np.ndarray:
        """
        Schneidet das Raster auf die Buffer-Geometrie zu.
        
        Args:
            raster_array: Raster-Array
            transform: Affine-Transform des Rasters
            buffer_geom: Buffer-Geometrie (Shapely in WGS84)
            crs: CRS des Rasters
        
        Returns:
            Maskiertes Array (nur Werte innerhalb des Buffers)
        """
        
        # Transformiere Buffer von WGS84 ins Raster-CRS
        from pyproj import CRS, Transformer
        from shapely.ops import transform as shapely_transform
        from rasterio.crs import CRS as RioCRS
        from rasterio.transform import Affine
        
        transformer = Transformer.from_crs(
            CRS.from_epsg(4326),  # WGS84 (Buffer ist in diesem CRS)
            CRS.from_string(crs.to_string()),  # Raster CRS (z.B. UTM)
            always_xy=True
        )
        
        # Transformiere Buffer-Geometrie
        buffer_raster_crs = shapely_transform(transformer.transform, buffer_geom)
        
        with MemoryFile() as memfile:
            with memfile.open(
                driver='GTiff',
                height=raster_array.shape[0],
                width=raster_array.shape[1],
                count=1,
                dtype=raster_array.dtype,
                crs=crs,
                transform=transform
            ) as dataset:
                dataset.write(raster_array, 1)
                
                # Maske anwenden mit transformiertem Buffer
                out_image, out_transform = mask(
                    dataset, 
                    [buffer_raster_crs],  # Nutze transformierten Buffer
                    crop=True,
                    nodata=0
                )
                
                return out_image[0]
    
    def _calculate_temperature_stats(self, masked_array: np.ndarray) -> Dict:
        """
        Berechnet Temperaturstatistiken aus maskiertem Array.
        Konvertiert von Kelvin (Landsat ST Product) nach Celsius.
        
        Args:
            masked_array: Maskiertes Raster-Array
        
        Returns:
            Dict mit mean_temp, min_temp, max_temp, pixel_count
        """
        
        # Entferne NoData-Werte (0 oder NaN)
        valid_pixels = masked_array[(masked_array != 0) & (~np.isnan(masked_array))]
        
        if len(valid_pixels) == 0:
            raise Exception("Keine gültigen Pixel im Buffer gefunden")
        
        # Landsat Collection 2 Level-2 Surface Temperature (ST_B10)
        # Scale Factor: 0.00341802, Offset: 149.0
        # Formel: Temperature (K) = (DN * 0.00341802) + 149.0
        # Dann: Celsius = Kelvin - 273.15
        
        # Anwendung der offiziellen USGS Skalierung
        temps_kelvin = (valid_pixels * 0.00341802) + 149.0
        
        # Konvertiere zu Celsius
        temps_celsius = temps_kelvin - 273.15
        
        # Berechne Statistiken
        mean_temp = float(np.mean(temps_celsius))
        min_temp = float(np.min(temps_celsius))
        max_temp = float(np.max(temps_celsius))
        pixel_count = len(valid_pixels)
        
        return {
            "mean_temp": round(mean_temp, 2),
            "min_temp": round(min_temp, 2),
            "max_temp": round(max_temp, 2),
            "pixel_count": pixel_count
        }
    
    def load_temperature_raster_for_bbox(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        scene_id: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Lädt Temperatur-Raster für eine Bounding Box und speichert es temporär.
        
        **BATCH-OPTIMIERUNG:** Lädt Raster nur EINMAL für alle Grid-Zellen!
        
        Args:
            lat_min: Minimaler Breitengrad
            lat_max: Maximaler Breitengrad
            lon_min: Minimaler Längengrad
            lon_max: Maximaler Längengrad
            scene_id: Landsat-Szenen-ID (optional)
        
        Returns:
            Tuple: (temp_raster_path, scene_id)
        """
        import tempfile
        import os
        
        logger.info(f"🔥 Lade Temperatur-Raster für Bounding Box: ({lat_min},{lon_min}) bis ({lat_max},{lon_max})")
        
        # 1. Wenn keine scene_id angegeben, suche automatisch
        if not scene_id:
            # Verwende Zentrum der Bounding Box
            center_lat = (lat_min + lat_max) / 2
            center_lon = (lon_min + lon_max) / 2
            
            logger.info(f"🔍 Suche automatisch nach Landsat-Szene für ({center_lat:.4f}, {center_lon:.4f})...")
            scene_id = stac_service.find_best_scene(center_lat, center_lon)
            
            if not scene_id:
                # Fallback: Nutze bekannte Szenen für bekannte Regionen
                logger.warning("⚠️ Automatische Suche fehlgeschlagen, nutze Fallback-Szenen...")
                scene_id = self._get_fallback_scene(center_lat, center_lon)
                
                if not scene_id:
                    raise Exception(
                        f"Keine passende Landsat-Szene für Koordinaten ({center_lat:.4f}, {center_lon:.4f}) gefunden.\n"
                        f"Bitte gib eine scene_id als Parameter an oder nutze bekannte Regionen (London, Berlin, etc.)."
                    )
        
        logger.info(f"✅ Verwende Szene: {scene_id}")
        
        # 2. Lade komplettes Raster von S3
        thermal_data, transform_obj, crs = self._load_thermal_band(scene_id)
        
        # 3. Speichere als temporäre GeoTIFF-Datei
        temp_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_raster_path = os.path.join(temp_dir, f'temp_landsat_{scene_id}.tif')
        
        # Schreibe Raster in Datei
        with rasterio.open(
            temp_raster_path,
            'w',
            driver='GTiff',
            height=thermal_data.shape[0],
            width=thermal_data.shape[1],
            count=1,
            dtype=thermal_data.dtype,
            crs=crs,
            transform=transform_obj
        ) as dst:
            dst.write(thermal_data, 1)
        
        logger.info(f"✅ Temperatur-Raster gespeichert: {temp_raster_path}")
        logger.info(f"   Shape: {thermal_data.shape}, CRS: {crs}")
        
        return temp_raster_path, scene_id
    
    def _get_fallback_scene(self, lat: float, lon: float) -> Optional[str]:
        """
        Gibt bekannte Landsat-Szenen für populäre Regionen zurück.
        Fallback wenn die automatische STAC-Suche fehlschlägt.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
        
        Returns:
            scene_id oder None
        """
        # Bekannte Szenen für verschiedene Regionen
        known_scenes = {
            # London (51.5°N, 0.1°W)
            "london": {
                "bounds": (51.0, 52.0, -1.0, 1.0),
                "scene_id": "LC09_L2SP_201024_20230721_20230802_02_T1"
            },
            # Berlin (52.5°N, 13.4°E)
            "berlin": {
                "bounds": (52.0, 53.0, 13.0, 14.0),
                "scene_id": "LC09_L2SP_193025_20230721_20230802_02_T1"
            },
            # Paris (48.9°N, 2.4°E)
            "paris": {
                "bounds": (48.5, 49.5, 2.0, 3.0),
                "scene_id": "LC09_L2SP_200026_20230721_20230802_02_T1"
            },
            # New York (40.7°N, 74.0°W)
            "new_york": {
                "bounds": (40.0, 41.0, -75.0, -73.0),
                "scene_id": "LC09_L2SP_014032_20230715_20230717_02_T1"
            },
        }
        
        # Prüfe welche Region passt
        for region, data in known_scenes.items():
            lat_min, lat_max, lon_min, lon_max = data["bounds"]
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                logger.info(f"✅ Gefunden: {region.title()} Region → {data['scene_id']}")
                return data["scene_id"]
        
        logger.warning(f"❌ Keine Fallback-Szene für ({lat:.4f}, {lon:.4f}) verfügbar")
        return None


# Singleton-Instanz
landsat_service = LandsatService()

