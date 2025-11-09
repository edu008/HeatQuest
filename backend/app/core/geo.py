"""
Geometrische Operationen für räumliche Berechnungen.
Erstellt Buffer um GPS-Koordinaten und verwaltet Projektionsumwandlungen.
"""

from shapely.geometry import Point
from shapely.ops import transform
from pyproj import CRS, Transformer
from typing import Tuple


def create_buffer_around_point(lat: float, lon: float, radius_meters: float = 200) -> Tuple[Point, any]:
    """
    Erstellt einen Buffer (Kreis) um einen GPS-Punkt.
    
    Args:
        lat: Breitengrad (WGS84)
        lon: Längengrad (WGS84)
        radius_meters: Radius in Metern (Standard: 200m)
    
    Returns:
        Tuple aus (Mittelpunkt, Buffer-Geometrie in WGS84)
    """
    
    # Erstelle Punkt in WGS84 (EPSG:4326)
    point_wgs84 = Point(lon, lat)
    
    # Transformiere in metrisches Koordinatensystem (Web Mercator EPSG:3857)
    # für genaue Distanzberechnung
    transformer_to_metric = Transformer.from_crs(
        CRS.from_epsg(4326),  # WGS84 (lat/lon)
        CRS.from_epsg(3857),  # Web Mercator (metrisch)
        always_xy=True
    )
    
    point_metric = transform(transformer_to_metric.transform, point_wgs84)
    
    # Erstelle Buffer in Metern
    buffer_metric = point_metric.buffer(radius_meters)
    
    # Transformiere Buffer zurück nach WGS84
    transformer_to_wgs84 = Transformer.from_crs(
        CRS.from_epsg(3857),  # Web Mercator
        CRS.from_epsg(4326),  # WGS84
        always_xy=True
    )
    
    buffer_wgs84 = transform(transformer_to_wgs84.transform, buffer_metric)
    
    return point_wgs84, buffer_wgs84


def get_buffer_bounds(buffer_geom) -> Tuple[float, float, float, float]:
    """
    Ermittelt die Bounding Box (min_lon, min_lat, max_lon, max_lat) eines Buffers.
    
    Args:
        buffer_geom: Shapely-Geometrie (Polygon)
    
    Returns:
        Tuple: (min_lon, min_lat, max_lon, max_lat)
    """
    bounds = buffer_geom.bounds  # (minx, miny, maxx, maxy)
    return bounds
