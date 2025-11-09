"""
Location Description Service.
Ruft Satellitenbilder ab und analysiert sie mit Vision-KI.
Modular aufgebaut für einfachen Austausch von Anbietern.
"""

import os
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple
import base64
from datetime import datetime
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class LocationDescriptionService:
    """
    Service für Satellitenbild-Abruf und KI-basierte Standortbeschreibung.
    """
    
    def __init__(self):
        """
        Initialisiert den Service und erstellt notwendige Verzeichnisse.
        """
        logger.info("=" * 70)
        logger.info("🚀 Location Description Service wird initialisiert...")
        logger.info("=" * 70)
        
        # Cache-Verzeichnis für Satellitenbilder
        self.cache_dir = Path(__file__).parent.parent.parent / "cache" / "satellite_images"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Cache-Verzeichnis: {self.cache_dir}")
        
        # Vertex AI Service Account laden
        self.vertex_credentials = None
        self.vertex_project_id = None
        self.best_vertex_model = None  # Cache für bestes Modell
        logger.info("🔐 Lade Vertex AI Credentials...")
        self._load_vertex_credentials()
        
        # Prüfe verfügbare Anbieter
        self._check_available_providers()
        
        logger.info("=" * 70)
        logger.info("✅ Location Description Service erfolgreich initialisiert!")
        logger.info("=" * 70)
    
    def _load_vertex_credentials(self):
        """
        Lädt Vertex AI Service Account Credentials aus JSON-Datei.
        """
        try:
            # Pfad zur Service Account JSON
            base_path = Path(__file__).parent.parent.parent
            service_account_path = base_path / settings.vertex_service_account_path
            
            logger.info(f"   Suche Service Account: {settings.vertex_service_account_path}")
            logger.info(f"   Vollständiger Pfad: {service_account_path}")
            logger.info(f"   Datei existiert: {service_account_path.exists()}")
            
            if not service_account_path.exists():
                logger.warning(f"⚠️ Vertex AI Service Account nicht gefunden!")
                logger.warning(f"   Erwarteter Pfad: {service_account_path}")
                logger.warning(f"   Bitte stelle sicher, dass die Datei existiert.")
                return
            
            # Lade JSON
            logger.info(f"   Lade JSON-Datei...")
            with open(service_account_path, 'r') as f:
                self.vertex_credentials = json.load(f)
            
            self.vertex_project_id = self.vertex_credentials.get('project_id')
            client_email = self.vertex_credentials.get('client_email', 'unbekannt')
            
            logger.info(f"   ✅ Credentials erfolgreich geladen!")
            logger.info(f"   📋 Projekt-ID: {self.vertex_project_id}")
            logger.info(f"   📧 Service Account: {client_email}")
            logger.info(f"   🌍 Region: {settings.vertex_location}")
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ungültige JSON-Datei: {e}")
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Vertex AI Credentials: {e}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
    
    def _find_best_vertex_model(self) -> Optional[str]:
        """
        Findet automatisch das beste verfügbare Gemini-Modell in Vertex AI.
        Nutzt Google's offizielle stabile Aliasse (immer neueste Version).
        Cached das Ergebnis für zukünftige Anfragen.
        
        Returns:
            Modell-Name oder None
        """
        if self.best_vertex_model:
            # Bereits gecached
            return self.best_vertex_model
        
        if not self.vertex_credentials or not self.vertex_project_id:
            return None
        
        logger.info("🔍 Suche bestes verfügbares Gemini-Modell (mit stabilen Aliassen)...")
        
        # Google's stabile Aliasse - verweisen immer auf neueste stabile Version!
        # Quelle: https://firebase.google.com/docs/vertex-ai/gemini-models
        models_to_try = [
            "gemini-2.0-flash",      # Neueste Generation (falls verfügbar)
            "gemini-1.5-flash",      # Stabil, schnell (empfohlen)
            "gemini-1.5-pro",        # Stabil, leistungsstark
            "gemini-pro-vision",     # Legacy (immer verfügbar)
        ]
        
        # Generiere Access Token
        access_token = self._get_vertex_access_token()
        if not access_token:
            return None
        
        project_id = self.vertex_project_id
        location = settings.vertex_location
        
        # Teste jedes Modell mit einem minimalen Request
        for model_name in models_to_try:
            try:
                logger.info(f"   🔎 Teste Modell: {model_name}")
                
                endpoint = (
                    f"https://{location}-aiplatform.googleapis.com/v1/"
                    f"projects/{project_id}/locations/{location}/"
                    f"publishers/google/models/{model_name}:generateContent"
                )
                
                # Minimaler Test-Request (Gemini-kompatibles Format)
                test_payload = {
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": "test"}]
                    }],
                    "generationConfig": {"maxOutputTokens": 1}
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                
                response = requests.post(endpoint, headers=headers, json=test_payload, timeout=10)
                
                if response.status_code == 200:
                    # Modell gefunden und funktioniert!
                    self.best_vertex_model = model_name
                    logger.info(f"   ✅ Bestes Modell gefunden: {model_name}")
                    logger.info(f"      (Stabil-Alias → immer neueste Version)")
                    return model_name
                
                elif response.status_code == 404:
                    logger.info(f"   ⏭️  {model_name}: Nicht verfügbar (404)")
                    continue
                
                elif response.status_code == 403:
                    logger.warning(f"   ⚠️  {model_name}: Keine Berechtigung (403)")
                    error_info = response.json() if response.text else {}
                    if 'error' in error_info and 'message' in error_info['error']:
                        logger.warning(f"      Grund: {error_info['error']['message'][:150]}")
                    continue
                    
                else:
                    logger.warning(f"   ⚠️  {model_name}: Fehler {response.status_code}")
                    logger.warning(f"      Response: {response.text[:200]}")
                    continue
            
            except Exception as e:
                logger.warning(f"   ⚠️  {model_name}: Exception - {str(e)[:100]}")
                continue
        
        logger.warning("⚠️ Kein funktionierendes Gemini-Modell gefunden")
        logger.warning("💡 Tipp: Prüfe ob 'Vertex AI API' aktiviert ist und Service Account Berechtigung hat")
        return None
    
    def _check_available_providers(self):
        """
        Prüft welche Anbieter verfügbar sind und loggt die Informationen.
        """
        logger.info("🔍 Prüfe verfügbare Anbieter...")
        
        # Satellitenbild-Anbieter
        logger.info("📡 Satellitenbild-Anbieter:")
        if settings.map:
            logger.info(f"   ✅ Mapbox (MAP): Verfügbar")
        else:
            logger.warning(f"   ⚠️ Mapbox (MAP): Nicht konfiguriert")
        
        if settings.google_maps_api_key:
            logger.info(f"   ✅ Google Maps: Verfügbar")
        else:
            logger.info(f"   ℹ️ Google Maps: Nicht konfiguriert")
        
        # Vision-KI-Anbieter
        logger.info("🤖 Vision-KI-Anbieter:")
        if self.vertex_credentials and self.vertex_project_id:
            logger.info(f"   ✅ Vertex AI (Service Account): Verfügbar")
            logger.info(f"      Projekt: {self.vertex_project_id}")
            
            # Finde bestes Modell
            best_model = self._find_best_vertex_model()
            if best_model:
                logger.info(f"      Bestes Modell: {best_model}")
            else:
                logger.warning(f"      ⚠️ Kein funktionierendes Modell gefunden")
        else:
            logger.warning(f"   ⚠️ Vertex AI: Nicht verfügbar (Credentials fehlen)")
        
        if settings.google_gemini_api_key:
            logger.info(f"   ✅ Google Gemini API (direkt): Verfügbar")
        else:
            logger.info(f"   ℹ️ Google Gemini API: Nicht konfiguriert")
        
        if settings.openai_api_key:
            logger.info(f"   ✅ OpenAI GPT-4 Vision: Verfügbar")
        else:
            logger.info(f"   ℹ️ OpenAI: Nicht konfiguriert")
        
        # Zusammenfassung
        satellite_providers = sum([
            bool(settings.map),
            bool(settings.google_maps_api_key)
        ])
        ai_providers = sum([
            bool(self.vertex_credentials and self.vertex_project_id),
            bool(settings.google_gemini_api_key),
            bool(settings.openai_api_key)
        ])
        
        logger.info(f"📊 Zusammenfassung: {satellite_providers} Satellitenbild-Anbieter, {ai_providers} Vision-KI-Anbieter verfügbar")
        
        if satellite_providers == 0:
            logger.error(f"❌ WARNUNG: Kein Satellitenbild-Anbieter konfiguriert!")
        if ai_providers == 0:
            logger.error(f"❌ WARNUNG: Kein Vision-KI-Anbieter konfiguriert!")
    
    def _get_vertex_access_token(self) -> Optional[str]:
        """
        Generiert ein Access Token für Vertex AI mittels Service Account.
        
        Returns:
            Access Token oder None
        """
        if not self.vertex_credentials:
            logger.debug("Keine Vertex Credentials vorhanden")
            return None
        
        try:
            logger.debug("Importiere google-auth...")
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            logger.debug("Erstelle Credentials aus Service Account...")
            # Erstelle Credentials aus Service Account
            credentials = service_account.Credentials.from_service_account_info(
                self.vertex_credentials,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            logger.debug("Erneuere Access Token...")
            # Token erneuern
            credentials.refresh(Request())
            
            token_preview = credentials.token[:20] + "..." if credentials.token else "None"
            logger.debug(f"Access Token generiert: {token_preview}")
            
            return credentials.token
        
        except ImportError as e:
            logger.error(f"❌ google-auth nicht installiert: {e}")
            logger.error("   Installiere mit: pip install google-auth")
            return None
        
        except Exception as e:
            logger.error(f"❌ Fehler beim Generieren des Vertex AI Access Tokens: {e}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
    
    def describe_location(
        self, 
        lat: float, 
        lon: float,
        zoom: int = 17,
        width: int = 640,
        height: int = 640
    ) -> Dict:
        """
        Hauptfunktion: Ruft Satellitenbild ab und analysiert es mit KI.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
            zoom: Zoom-Level (1-20)
            width: Bildbreite in Pixeln
            height: Bildhöhe in Pixeln
        
        Returns:
            Dictionary mit Beschreibung und Metadaten
        """
        logger.info("=" * 70)
        logger.info(f"🌍 Starte Location Description für ({lat}, {lon})")
        logger.info(f"   Zoom: {zoom}, Größe: {width}x{height}px")
        logger.info("=" * 70)
        
        # 1. Satellitenbild abrufen
        logger.info("📥 Schritt 1/2: Satellitenbild abrufen...")
        image_path, provider = self._fetch_satellite_image(lat, lon, zoom, width, height)
        logger.info(f"✅ Satellitenbild gespeichert: {image_path}")
        logger.info(f"   Anbieter: {provider}")
        
        # 2. KI-Analyse durchführen
        logger.info("🤖 Schritt 2/2: KI-Analyse durchführen...")
        analysis_dict, ai_provider = self._analyze_image_with_ai(image_path)
        logger.info(f"✅ KI-Analyse abgeschlossen!")
        logger.info(f"   Anbieter: {ai_provider}")
        logger.info(f"   Beschreibung ({len(analysis_dict['description'])} Zeichen): {analysis_dict['description'][:100]}...")
        
        result = {
            "description": analysis_dict["description"],
            "main_cause": analysis_dict["main_cause"],
            "suggested_actions": analysis_dict["suggested_actions"],
            "lat": lat,
            "lon": lon,
            "image_path": str(image_path),
            "image_provider": provider,
            "ai_provider": ai_provider,
            "confidence": "high" if analysis_dict["description"] else "low"
        }
        
        logger.info("=" * 70)
        logger.info("✅ Location Description erfolgreich abgeschlossen!")
        logger.info("=" * 70)
        
        return result
    
    def _fetch_satellite_image(
        self,
        lat: float,
        lon: float,
        zoom: int,
        width: int,
        height: int
    ) -> Tuple[Path, str]:
        """
        Ruft Satellitenbild über API ab und speichert es lokal.
        Unterstützt mehrere Anbieter mit automatischem Fallback.
        
        Args:
            lat: Breitengrad
            lon: Längengrad
            zoom: Zoom-Level
            width: Bildbreite
            height: Bildhöhe
        
        Returns:
            Tuple (Dateipfad, Anbieter-Name)
        """
        # Dateiname generieren
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"satellite_{lat}_{lon}_{timestamp}.png"
        image_path = self.cache_dir / filename
        
        # Versuche verschiedene Anbieter (Mapbox zuerst)
        providers = [
            self._fetch_from_mapbox,
            self._fetch_from_google_maps
        ]
        
        for provider_func in providers:
            try:
                success, provider_name = provider_func(lat, lon, zoom, width, height, image_path)
                if success:
                    return image_path, provider_name
            except Exception as e:
                logger.warning(f"⚠️ {provider_func.__name__} fehlgeschlagen: {e}")
                continue
        
        raise Exception("Alle Satellitenbild-Anbieter fehlgeschlagen")
    
    def _fetch_from_mapbox(
        self,
        lat: float,
        lon: float,
        zoom: int,
        width: int,
        height: int,
        output_path: Path
    ) -> Tuple[bool, str]:
        """
        Ruft Satellitenbild über Mapbox Static Images API ab.
        Verwendet MAP Umgebungsvariable.
        
        Returns:
            Tuple (Erfolg, Anbieter-Name)
        """
        if not settings.map:
            logger.debug("MAP (Mapbox Token) nicht konfiguriert")
            return False, "Mapbox"
        
        logger.info("📡 Versuche Mapbox Static Images API...")
        
        # Mapbox Static Images API: Satellite-v9 Style
        url = (
            f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
            f"{lon},{lat},{zoom}/{width}x{height}@2x"
            f"?access_token={settings.map}"
        )
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Speichere Bild
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✅ Mapbox: Bild abgerufen ({len(response.content)} bytes)")
        return True, "Mapbox Satellite"
    
    def _fetch_from_google_maps(
        self,
        lat: float,
        lon: float,
        zoom: int,
        width: int,
        height: int,
        output_path: Path
    ) -> Tuple[bool, str]:
        """
        Ruft Satellitenbild über Google Maps Static API ab.
        
        Returns:
            Tuple (Erfolg, Anbieter-Name)
        """
        if not settings.google_maps_api_key:
            logger.debug("Google Maps API Key nicht konfiguriert")
            return False, "Google Maps"
        
        logger.info("📡 Versuche Google Maps Static API...")
        
        # Google Maps Static API: Satellite
        url = (
            f"https://maps.googleapis.com/maps/api/staticmap"
            f"?center={lat},{lon}"
            f"&zoom={zoom}"
            f"&size={width}x{height}"
            f"&maptype=satellite"
            f"&scale=2"
            f"&key={settings.google_maps_api_key}"
        )
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Speichere Bild
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✅ Google Maps: Bild abgerufen ({len(response.content)} bytes)")
        return True, "Google Maps Satellite"
    
    def _parse_json_response(self, text: str) -> Dict:
        """
        Extrahiert und parsed JSON aus KI-Response (robust gegen Markdown-Blöcke).
        
        Returns:
            Dictionary mit description, main_cause, suggested_actions
        """
        try:
            # Entferne Markdown-Code-Blöcke (```json ... ```)
            if "```" in text:
                parts = text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{") and part.endswith("}"):
                        text = part
                        break
            
            # Parse JSON
            data = json.loads(text)
            
            # Validiere erforderliche Felder
            return {
                "description": data.get("description", "No description available"),
                "main_cause": data.get("main_cause", "Unknown cause"),
                "suggested_actions": data.get("suggested_actions", [])
            }
        
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON-Parsing fehlgeschlagen: {e}")
            # Fallback: Nutze Text als Beschreibung
            return {
                "description": text.strip(),
                "main_cause": "Analysis incomplete",
                "suggested_actions": []
            }
    
    def _analyze_image_with_ai(self, image_path: Path) -> Tuple[Dict, str]:
        """
        Analysiert Satellitenbild mit Vision-KI.
        Unterstützt mehrere KI-Anbieter mit automatischem Fallback.
        
        Args:
            image_path: Pfad zum Satellitenbild
        
        Returns:
            Tuple (Analysis-Dict, KI-Anbieter-Name)
        """
        # Versuche verschiedene KI-Anbieter (Vertex AI zuerst, dann Gemini direkt, dann OpenAI)
        analyzers = [
            self._analyze_with_vertex_ai,
            self._analyze_with_gemini_direct,
            self._analyze_with_openai
        ]
        
        for analyzer_func in analyzers:
            try:
                analysis_dict, provider_name = analyzer_func(image_path)
                if analysis_dict and analysis_dict.get("description"):
                    return analysis_dict, provider_name
            except Exception as e:
                logger.warning(f"⚠️ {analyzer_func.__name__} fehlgeschlagen: {e}")
                continue
        
        raise Exception("Alle Vision-KI-Anbieter fehlgeschlagen")
    
    def _analyze_with_vertex_ai(self, image_path: Path) -> Tuple[Dict, str]:
        """
        Analysiert Bild mit Google Vertex AI Vision.
        Verwendet Service Account JSON für Authentifizierung.
        
        Returns:
            Tuple (Analysis-Dict, Anbieter-Name)
        """
        if not self.vertex_credentials or not self.vertex_project_id:
            logger.debug("Vertex AI Credentials nicht geladen")
            return {}, "Google Vertex AI"
        
        logger.info("🤖 Versuche Google Vertex AI Vision...")
        
        # Generiere Access Token
        access_token = self._get_vertex_access_token()
        if not access_token:
            logger.error("❌ Konnte kein Vertex AI Access Token generieren")
            return {}, "Google Vertex AI"
        
        # Bild als Base64 kodieren
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Vertex AI API Request (über REST API)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        # Prompt für Satellitenbild-Analyse (auf Englisch) - mit strukturierter Ausgabe
        prompt = (
            "Analyze this satellite image for heat stress factors. Respond ONLY with valid JSON in this exact format:\n\n"
            "{\n"
            '  "description": "Brief 2-3 sentence description of what is visible (buildings, streets, green spaces, etc.)",\n'
            '  "main_cause": "Primary cause of heat stress in this area",\n'
            '  "suggested_actions": [\n'
            '    {"priority": "high/medium/low", "action": "Action name", "description": "Brief explanation"}\n'
            "  ]\n"
            "}\n\n"
            "Focus on urban heat factors: asphalt, building density, lack of vegetation, sealed surfaces. "
            "Suggest 2-4 concrete cooling measures. Keep all text concise and in English."
        )
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": image_data
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 800,
                "temperature": 0.4
            }
        }
        
        # Verwende Gemini Vision über Vertex AI
        project_id = self.vertex_project_id
        location = settings.vertex_location
        
        # Hole bestes Modell (cached wenn bereits ermittelt)
        model_name = self.best_vertex_model or self._find_best_vertex_model()
        
        if not model_name:
            logger.error("❌ Kein verfügbares Gemini-Modell gefunden")
            return {}, "Google Vertex AI"
        
        logger.info(f"   Verwende Modell: {model_name}")
        
        # Vertex AI Endpoint
        endpoint = (
            f"https://{location}-aiplatform.googleapis.com/v1/"
            f"projects/{project_id}/locations/{location}/"
            f"publishers/google/models/{model_name}:generateContent"
        )
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Prüfe ob Antwort vorhanden
                if 'candidates' not in result or len(result['candidates']) == 0:
                    logger.error(f"❌ Keine Antwort von Vertex AI: {result}")
                    return {}, "Google Vertex AI"
                
                raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                analysis_dict = self._parse_json_response(raw_text)
                
                logger.info(f"✅ Vertex AI: Analyse abgeschlossen mit {model_name}")
                return analysis_dict, f"Google Vertex AI ({model_name})"
            
            else:
                # Fehler
                error_detail = response.text
                logger.error(f"❌ Vertex AI API Fehler ({response.status_code}): {error_detail}")
                
                if response.status_code == 403:
                    logger.error("💡 Mögliche Lösungen:")
                    logger.error("   1. Aktiviere Vertex AI API: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com")
                    logger.error("   2. Füge dem Service Account die Rolle 'Vertex AI User' hinzu")
                    logger.error("   3. Warte einige Minuten nach Aktivierung der API")
                
                elif response.status_code == 404:
                    logger.error(f"❌ Modell {model_name} plötzlich nicht mehr verfügbar")
                    # Cache löschen für nächsten Versuch
                    self.best_vertex_model = None
                
                response.raise_for_status()
        
        except Exception as e:
            logger.error(f"❌ Fehler bei Vertex AI Request: {e}")
            raise
        
        return {}, "Google Vertex AI"
    
    def _analyze_with_gemini_direct(self, image_path: Path) -> Tuple[Dict, str]:
        """
        Analysiert Bild mit Google Gemini API (direkt, ohne Vertex AI).
        Einfachere Alternative wenn Vertex AI nicht verfügbar ist.
        
        Returns:
            Tuple (Analysis-Dict, Anbieter-Name)
        """
        if not settings.google_gemini_api_key:
            logger.debug("Google Gemini API Key nicht konfiguriert")
            return {}, "Google Gemini"
        
        logger.info("🤖 Versuche Google Gemini API (direkt)...")
        
        # Bild als Base64 kodieren
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Prompt für Satellitenbild-Analyse (auf Englisch) - mit strukturierter Ausgabe
        prompt = (
            "Analyze this satellite image for heat stress factors. Respond ONLY with valid JSON in this exact format:\n\n"
            "{\n"
            '  "description": "Brief 2-3 sentence description of what is visible (buildings, streets, green spaces, etc.)",\n'
            '  "main_cause": "Primary cause of heat stress in this area",\n'
            '  "suggested_actions": [\n'
            '    {"priority": "high/medium/low", "action": "Action name", "description": "Brief explanation"}\n'
            "  ]\n"
            "}\n\n"
            "Focus on urban heat factors: asphalt, building density, lack of vegetation, sealed surfaces. "
            "Suggest 2-4 concrete cooling measures. Keep all text concise and in English."
        )
        
        # Gemini API Request (vereinfachter Zugang)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.google_gemini_api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_data
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 800,
                "temperature": 0.4
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Prüfe ob Antwort vorhanden
        if 'candidates' not in result or len(result['candidates']) == 0:
            logger.error(f"❌ Keine Antwort von Gemini API: {result}")
            return {}, "Google Gemini"
        
        raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
        analysis_dict = self._parse_json_response(raw_text)
        
        logger.info(f"✅ Gemini API: Analyse abgeschlossen")
        return analysis_dict, "Google Gemini API (direkt)"
    
    def _analyze_with_openai(self, image_path: Path) -> Tuple[Dict, str]:
        """
        Analysiert Bild mit OpenAI GPT-4 Vision.
        
        Returns:
            Tuple (Analysis-Dict, Anbieter-Name)
        """
        if not settings.openai_api_key:
            logger.debug("OpenAI API Key nicht konfiguriert")
            return {}, "OpenAI GPT-4 Vision"
        
        logger.info("🤖 Versuche OpenAI GPT-4 Vision...")
        
        # Bild als Base64 kodieren
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # OpenAI API Request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.openai_api_key}"
        }
        
        payload = {
            "model": "gpt-4o",  # GPT-4 Vision
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyze this satellite image for heat stress factors. Respond ONLY with valid JSON in this exact format:\n\n"
                                "{\n"
                                '  "description": "Brief 2-3 sentence description of what is visible (buildings, streets, green spaces, etc.)",\n'
                                '  "main_cause": "Primary cause of heat stress in this area",\n'
                                '  "suggested_actions": [\n'
                                '    {"priority": "high/medium/low", "action": "Action name", "description": "Brief explanation"}\n'
                                "  ]\n"
                                "}\n\n"
                                "Focus on urban heat factors: asphalt, building density, lack of vegetation, sealed surfaces. "
                                "Suggest 2-4 concrete cooling measures. Keep all text concise and in English."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 800
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        raw_text = result['choices'][0]['message']['content'].strip()
        analysis_dict = self._parse_json_response(raw_text)
        
        logger.info(f"✅ OpenAI: Analyse abgeschlossen")
        return analysis_dict, "OpenAI GPT-4 Vision"


# Singleton-Instanz
location_description_service = LocationDescriptionService()

