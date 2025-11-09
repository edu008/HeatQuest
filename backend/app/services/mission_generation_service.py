"""
Mission Generation Service.
Erstellt automatisch Missionen basierend auf cell_analyses.
"""

import logging
import math
from typing import List, Dict, Optional
from datetime import datetime

from app.core.supabase_client import supabase_service

logger = logging.getLogger(__name__)


class MissionGenerationService:
    """Service für automatische Mission-Generierung."""
    
    def __init__(self):
        self.min_heat_score_for_mission = 11.0  # Nur Hotspots
        self.max_missions_per_generation = 10
    
    async def generate_missions_from_analyses(
        self,
        parent_cell_id: str,
        user_id: str,
        user_lat: float,
        user_lon: float,
        max_missions: int = 5
    ) -> List[Dict]:
        """
        Generiert Missionen basierend auf cell_analyses.
        
        Args:
            parent_cell_id: Parent Cell ID
            user_id: User ID
            user_lat: User Latitude
            user_lon: User Longitude
            max_missions: Max. Anzahl zu generierender Missionen
        
        Returns:
            Liste von erstellten Missionen
        """
        try:
            logger.info("=" * 70)
            logger.info(f"🎯 MISSION GENERATION")
            logger.info(f"   Parent Cell: {parent_cell_id}")
            logger.info(f"   User: {user_id}")
            logger.info(f"   Max Missions: {max_missions}")
            logger.info("=" * 70)
            
            # 1. Load all analyses for this Parent Cell
            response = supabase_service.client.table('cell_analyses').select(
                '*'
            ).eq('parent_cell_id', parent_cell_id).execute()
            
            if not response.data or len(response.data) == 0:
                logger.info("ℹ️  No cell analyses found for mission generation")
                return []
            
            analyses = response.data
            logger.info(f"📊 {len(analyses)} cell analyses found")
            
            # 2. Filter: Only analyses with Heat Score >= Threshold
            hotspot_analyses = [
                a for a in analyses
                if a.get('heat_score') and a['heat_score'] >= self.min_heat_score_for_mission
            ]
            
            if not hotspot_analyses:
                logger.info(f"ℹ️  No hotspots (>= {self.min_heat_score_for_mission}) found")
                return []
            
            logger.info(f"🔥 {len(hotspot_analyses)} hotspot analyses found")
            
            # 2a. ERSTE PRÜFUNG: Welche haben bereits mission_generated = True?
            # Dies ist die primäre Prüfung (ähnlich wie analyzed Flag bei child_cells)
            already_generated = [a for a in hotspot_analyses if a.get('mission_generated') == True]
            not_generated = [a for a in hotspot_analyses if a.get('mission_generated') != True]
            
            if already_generated:
                logger.info(f"✅ {len(already_generated)} analyses already have mission_generated=True")
            
            if not not_generated:
                logger.info("✅ All analyses already have missions generated (mission_generated=True)")
                return []
            
            logger.info(f"🆕 {len(not_generated)} analyses without mission_generated flag")
            
            # Verwende nur die Analysen ohne Flag
            hotspot_analyses = not_generated
            
            # 3. ZWEITE PRÜFUNG (Backup, user-spezifisch): Check existing missions for THIS user
            # Die mission_generated Flag (Prüfung oben) ist global
            # Diese Prüfung ist user-spezifisch als zusätzliche Sicherheit
            analysis_ids = [a['id'] for a in hotspot_analyses]
            
            logger.info(f"🔍 Backup-Check: Existing missions for user {user_id}...")
            existing_missions_response = supabase_service.client.table('missions').select(
                'cell_analysis_id'
            ).in_('cell_analysis_id', analysis_ids).eq('user_id', user_id).execute()
            
            existing_analysis_ids = set()
            if existing_missions_response.data:
                existing_analysis_ids = {m['cell_analysis_id'] for m in existing_missions_response.data}
                logger.info(f"   ✅ {len(existing_analysis_ids)} analyses already have missions for this user")
            else:
                logger.info(f"   ℹ️  No existing missions found for this user")
            
            # Filter analyses that don't have missions yet
            new_analyses = [
                a for a in hotspot_analyses
                if a['id'] not in existing_analysis_ids
            ]
            
            if not new_analyses:
                logger.info("✅ All hotspots already have missions for this user - no new missions needed")
                return []
            
            logger.info(f"🆕 {len(new_analyses)} new hotspots without mission for this user")
            
            # 4. Calculate distances to user
            for analysis in new_analyses:
                distance = self._calculate_distance(
                    user_lat, user_lon,
                    analysis['latitude'], analysis['longitude']
                )
                analysis['distance_to_user'] = distance
            
            # 5. Sort by distance (closest first)
            new_analyses.sort(key=lambda a: a['distance_to_user'])
            
            # 6. Limit to max_missions
            analyses_to_create = new_analyses[:max_missions]
            
            logger.info(f"🎯 Creating {len(analyses_to_create)} new missions:")
            for i, analysis in enumerate(analyses_to_create):
                logger.info(f"   {i+1}. Heat Score={analysis['heat_score']:.1f}, Distance={analysis['distance_to_user']:.0f}m")
            
            # 7. Create missions
            created_missions = []
            for analysis in analyses_to_create:
                try:
                    mission = await self._create_mission_from_analysis(
                        analysis=analysis,
                        user_id=user_id
                    )
                    if mission:
                        created_missions.append(mission)
                        logger.info(f"✅ Mission created: {mission['title']}")
                        
                        # 7a. Setze mission_generated = True in cell_analyses
                        # WICHTIG: Dies markiert die Analyse als "Mission wurde generiert"
                        try:
                            supabase_service.client.table('cell_analyses').update({
                                'mission_generated': True
                            }).eq('id', analysis['id']).execute()
                            logger.info(f"   ✓ cell_analysis {analysis['id']} marked as mission_generated=True")
                        except Exception as update_error:
                            logger.warning(f"⚠️ Could not update mission_generated flag: {update_error}")
                            
                except Exception as e:
                    logger.error(f"❌ Error creating mission: {e}")
                    continue
            
            logger.info("=" * 70)
            logger.info(f"🎉 MISSIONS CREATED: {len(created_missions)}/{len(analyses_to_create)}")
            logger.info("=" * 70)
            
            return created_missions
        
        except Exception as e:
            logger.error(f"❌ Error in mission generation: {e}", exc_info=True)
            return []
    
    async def _create_mission_from_analysis(
        self,
        analysis: Dict,
        user_id: str
    ) -> Optional[Dict]:
        """
        Creates a mission from a cell analysis.
        
        Args:
            analysis: Cell analysis data
            user_id: User ID
        
        Returns:
            Created mission or None
        """
        try:
            # Generate mission title (mit mehr Kontext)
            title = self._generate_mission_title_advanced(analysis)
            
            # Generate description (kombiniere AI Summary und Details)
            description = self._generate_mission_description(analysis)
            
            # Extract reasons (Main Cause + zusätzliche Infos)
            reasons = self._generate_mission_reasons(analysis)
            
            # Extract actions from suggested_actions
            suggested_actions = analysis.get('suggested_actions', [])
            actions_text = []
            if isinstance(suggested_actions, list):
                for action in suggested_actions:
                    if isinstance(action, dict):
                        action_text = action.get('action', '')
                        if action_text:
                            actions_text.append(action_text)
            
            # Fallback if no actions (sollte nicht mehr passieren)
            if not actions_text:
                actions_text = [
                    "🌳 Pflanze Bäume für natürlichen Schatten",
                    "🏢 Installiere helle Oberflächen (z.B. weiße Dächer)",
                    "💧 Füge Wasserspiele oder Brunnen hinzu"
                ]
            
            # Create mission data
            mission_data = {
                'user_id': user_id,
                'parent_cell_id': analysis.get('parent_cell_id'),
                'child_cell_id': analysis.get('child_cell_id'),
                'cell_analysis_id': analysis['id'],
                'latitude': analysis['latitude'],
                'longitude': analysis['longitude'],
                'title': title,
                'description': description,
                'mission_type': 'analyze_hotspot',
                'heat_risk_score': float(analysis.get('heat_score', 0)),
                'required_actions': suggested_actions,  # As JSONB
                'status': 'pending',
                'points_earned': 0,
                'created_by_system': True,
                'distance_to_user': analysis.get('distance_to_user')
            }
            
            # Save to DB
            response = supabase_service.client.table('missions').insert(mission_data).execute()
            
            if response.data and len(response.data) > 0:
                mission = response.data[0]
                
                # Add frontend-compatible fields
                mission['heatRisk'] = mission.get('heat_risk_score', 0)
                mission['lat'] = mission['latitude']
                mission['lng'] = mission['longitude']
                mission['reasons'] = reasons
                mission['actions'] = actions_text
                mission['completed'] = mission['status'] == 'completed'
                
                return mission
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Error creating mission: {e}")
            return None
    
    def _generate_mission_title(self, analysis: Dict) -> str:
        """Generates mission title based on analysis (Legacy)."""
        heat_score = analysis.get('heat_score', 0)
        lat = analysis.get('latitude', 0)
        lon = analysis.get('longitude', 0)
        
        # Determine category based on Heat Score
        if heat_score > 30:
            prefix = "Critical Hotspot"
        elif heat_score > 20:
            prefix = "High Heat Area"
        else:
            prefix = "Heat Spot"
        
        # Format: "Critical Hotspot @ 46.95°N, 7.49°E"
        return f"{prefix} @ {lat:.2f}°N, {lon:.2f}°E"
    
    def _generate_mission_title_advanced(self, analysis: Dict) -> str:
        """Generiert verbesserten Mission-Titel mit mehr Kontext."""
        heat_score = analysis.get('heat_score', 0)
        ai_summary = analysis.get('ai_summary', '')
        
        # Versuche Location-Type aus AI-Summary zu extrahieren
        location_type = "Area"  # Default
        if ai_summary:
            summary_lower = ai_summary.lower()
            if 'residential' in summary_lower or 'houses' in summary_lower or 'apartments' in summary_lower:
                location_type = "Residential Zone"
            elif 'school' in summary_lower or 'playground' in summary_lower:
                location_type = "School Area"
            elif 'parking' in summary_lower or 'asphalt' in summary_lower:
                location_type = "Parking Zone"
            elif 'industrial' in summary_lower or 'warehouse' in summary_lower:
                location_type = "Industrial Area"
            elif 'park' in summary_lower or 'green space' in summary_lower:
                location_type = "Park Zone"
            elif 'commercial' in summary_lower or 'shopping' in summary_lower:
                location_type = "Commercial District"
        
        # Emojis basierend auf Heat Score
        if heat_score > 30:
            emoji = "🔥"
            prefix = "Critical"
        elif heat_score > 20:
            emoji = "☀️"
            prefix = "High Heat"
        elif heat_score > 15:
            emoji = "🌡️"
            prefix = "Moderate Heat"
        else:
            emoji = "🔍"
            prefix = "Investigate"
        
        # Format: "🔥 Critical: Residential Zone"
        return f"{emoji} {prefix}: {location_type}"
    
    def _generate_mission_description(self, analysis: Dict) -> str:
        """Generiert detaillierte Mission-Beschreibung."""
        ai_summary = analysis.get('ai_summary', '')
        heat_score = analysis.get('heat_score', 0)
        temperature = analysis.get('temperature')
        
        # Basis-Beschreibung
        description_parts = []
        
        if ai_summary:
            description_parts.append(ai_summary)
        
        # Füge Heat Score Details hinzu
        if heat_score > 30:
            description_parts.append(f"⚠️ Kritischer Heat Score von {heat_score:.1f} - sofortiges Handeln erforderlich!")
        elif heat_score > 20:
            description_parts.append(f"⚠️ Hoher Heat Score von {heat_score:.1f} - Maßnahmen dringend empfohlen.")
        else:
            description_parts.append(f"Heat Score: {heat_score:.1f}")
        
        # Füge Temperatur hinzu wenn vorhanden
        if temperature:
            description_parts.append(f"🌡️ Oberflächentemperatur: {temperature:.1f}°C")
        
        return " ".join(description_parts)
    
    def _generate_mission_reasons(self, analysis: Dict) -> List[str]:
        """Generiert Liste von Gründen für die Hitze."""
        reasons = []
        
        # Main Cause
        main_cause = analysis.get('main_cause')
        if main_cause:
            reasons.append(f"🔍 Hauptursache: {main_cause}")
        
        # AI Summary als zusätzlicher Kontext
        ai_summary = analysis.get('ai_summary', '')
        if ai_summary and len(reasons) == 0:
            # Falls kein main_cause, verwende ai_summary
            reasons.append(ai_summary[:200])  # Erste 200 Zeichen
        
        # Füge weitere Details hinzu wenn vorhanden
        temperature = analysis.get('temperature')
        if temperature and temperature > 35:
            reasons.append(f"🌡️ Sehr hohe Oberflächentemperatur ({temperature:.1f}°C)")
        
        ndvi = analysis.get('ndvi')
        if ndvi is not None and ndvi < 0.2:
            reasons.append(f"🌳 Wenig Vegetation (NDVI: {ndvi:.2f})")
        
        # Fallback
        if not reasons:
            reasons.append("Erhöhte Hitzebelastung in diesem Bereich festgestellt")
        
        return reasons
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculates distance between two GPS points (Haversine).
        
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance


# Singleton
mission_generation_service = MissionGenerationService()

