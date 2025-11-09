"""
Konfigurationsmodul für das HeatQuest Backend.
Verwaltet AWS-Credentials und Landsat-Bucket-Einstellungen.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
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
    
    # Mapbox API Token für Visualisierung und Satellitenbilder
    map: Optional[str] = None
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None  # ANON Key für Client-Side
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None  # SERVICE_ROLE Key für Backend (bypassed RLS)
    
    # Vertex AI Configuration
    vertex_service_account_path: str = "vertex-access.json"
    vertex_location: str = "us-east4"  # Gemini-Modelle verfügbar (früher: us-central1)
    vertex_project_id: Optional[str] = None  # Vertex AI Project ID
    google_application_credentials: Optional[str] = None  # Path to service account JSON
    vertex: Optional[str] = None  # Vertex AI API Key (falls verwendet)
    
    # Optional: Weitere Anbieter
    google_maps_api_key: Optional[str] = None
    google_gemini_api_key: Optional[str] = None  # Direkter Gemini API Zugriff (Alternative zu Vertex)
    openai_api_key: Optional[str] = None
    
    # API-Einstellungen
    api_title: str = "HeatQuest API"
    api_version: str = "1.0.0"
    api_description: str = "Backend für Oberflächentemperatur-Analyse aus Landsat-Daten"
    
    # Pydantic v2 Config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignoriere unbekannte Felder aus .env
    )


# Singleton-Instanz
settings = Settings()
