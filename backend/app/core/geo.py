"""
Geometric operations for spatial calculations.
Creates buffers around GPS coordinates and manages projection transformations.
"""

from shapely.geometry import Point
from shapely.ops import transform
from pyproj import CRS, Transformer
from typing import Tuple


def create_buffer_around_point(lat: float, lon: float, radius_meters: float = 200) -> Tuple[Point, any]:
    """
    Creates a buffer (circle) around a GPS point.
    
    Args:
        lat: Latitude (WGS84)
        lon: Longitude (WGS84)
        radius_meters: Radius in meters (default: 200m)
    
    Returns:
        Tuple of (center point, buffer geometry in WGS84)
    """
    
    # Create point in WGS84 (EPSG:4326)
    point_wgs84 = Point(lon, lat)
    
    # Transform to metric coordinate system (Web Mercator EPSG:3857)
    # for accurate distance calculations
    transformer_to_metric = Transformer.from_crs(
        CRS.from_epsg(4326),  # WGS84 (lat/lon)
        CRS.from_epsg(3857),  # Web Mercator (metric)
        always_xy=True
    )
    
    point_metric = transform(transformer_to_metric.transform, point_wgs84)
    
    # Create buffer in meters
    buffer_metric = point_metric.buffer(radius_meters)
    
    # Transform buffer back to WGS84
    transformer_to_wgs84 = Transformer.from_crs(
        CRS.from_epsg(3857),  # Web Mercator
        CRS.from_epsg(4326),  # WGS84
        always_xy=True
    )
    
    buffer_wgs84 = transform(transformer_to_wgs84.transform, buffer_metric)
    
    return point_wgs84, buffer_wgs84


def get_buffer_bounds(buffer_geom) -> Tuple[float, float, float, float]:
    """
    Determines the bounding box (min_lon, min_lat, max_lon, max_lat) of a buffer.
    
    Args:
        buffer_geom: Shapely geometry (Polygon)
    
    Returns:
        Tuple: (min_lon, min_lat, max_lon, max_lat)
    """
    bounds = buffer_geom.bounds  # (minx, miny, maxx, maxy)
    return bounds
