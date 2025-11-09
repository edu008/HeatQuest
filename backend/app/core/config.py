"""
Configuration module for the HeatQuest Backend.
Manages AWS credentials and Landsat bucket settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Central configuration for the application.
    Loads values from environment variables or the .env file.
    """
    
    # AWS Configuration
    # Note: For public Landsat data, no credentials are required
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-west-2"
    
    # Landsat Bucket
    landsat_bucket: str = "usgs-landsat"
    
    # Mapbox API Token for visualization and satellite imagery
    map: Optional[str] = None
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Vertex AI Configuration
    vertex_service_account_path: str = "vertex-access.json"
    vertex_location: str = "us-east4"  # Gemini models available (previously: us-central1)
    vertex_project_id: Optional[str] = None  # Vertex AI Project ID
    google_application_credentials: Optional[str] = None  # Path to service account JSON
    vertex: Optional[str] = None  # Vertex AI API Key (if used)
    
    # Optional: Other providers
    google_maps_api_key: Optional[str] = None
    google_gemini_api_key: Optional[str] = None  # Direct Gemini API access (alternative to Vertex)
    openai_api_key: Optional[str] = None
    
    # API Settings
    api_title: str = "HeatQuest API"
    api_version: str = "1.0.0"
    api_description: str = "Backend for surface temperature analysis from Landsat data"
    
    # Pydantic v2 Config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore unknown fields from .env
    )


# Singleton instance
settings = Settings()
