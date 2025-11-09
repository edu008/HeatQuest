"""
Konfigurationsmodul für das HeatQuest Backend.
Verwaltet AWS-Credentials und Landsat-Bucket-Einstellungen.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Zentrale Konfiguration für die Anwendung.
    Lädt Werte aus Environment-Variablen oder .env-Datei.
    """
    
    # AWS-Konfiguration
    # Hinweis: Für öffentliche Landsat-Daten sind keine Credentials erforderlich
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-west-2"
    
    # Landsat-Bucket
    landsat_bucket: str = "usgs-landsat"
    
    # Mapbox API Token für Visualisierung
    map: Optional[str] = None
    
    # API-Einstellungen
    api_title: str = "HeatQuest API"
    api_version: str = "1.0.0"
    api_description: str = "Backend für Oberflächentemperatur-Analyse aus Landsat-Daten"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton-Instanz
settings = Settings()
