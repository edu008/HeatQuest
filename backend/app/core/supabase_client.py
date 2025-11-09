"""
Supabase Client Configuration
Handles authentication and database operations for HeatQuest
"""
from supabase import create_client, Client
from app.core.config import settings
from typing import Optional, Dict, List, Any


class SupabaseService:
    """Supabase service for database operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        if not settings.SUPABASE_URL:
            raise ValueError("SUPABASE_URL must be set")
        
        # Verwende SERVICE_ROLE_KEY falls vorhanden (bypassed RLS), sonst ANON KEY
        supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
        
        if not supabase_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY oder SUPABASE_KEY must be set")
        
        # Logge welcher Key-Typ verwendet wird
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            import logging
            logger = logging.getLogger(__name__)
            logger.info("🔑 Supabase: Verwende SERVICE_ROLE_KEY (bypassed RLS)")
        
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            supabase_key
        )
    
    # ============ User Profile Operations ============
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).single().execute()
            return response.data
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None
    
    async def create_profile(self, user_id: str, username: str) -> Optional[Dict[str, Any]]:
        """Create a new user profile"""
        try:
            profile_data = {
                'id': user_id,
                'username': username,
                'points': 0,
                'level': 1,
                'missions_completed': 0
            }
            response = self.client.table('profiles').insert(profile_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating profile: {e}")
            return None
    
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile"""
        try:
            response = self.client.table('profiles').update(updates).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating profile: {e}")
            return None
    
    async def add_points(self, user_id: str, points: int) -> Optional[Dict[str, Any]]:
        """Add points to user profile and update level"""
        profile = await self.get_profile(user_id)
        if not profile:
            return None
        
        new_points = profile['points'] + points
        new_level = (new_points // 500) + 1
        
        return await self.update_profile(user_id, {
            'points': new_points,
            'level': new_level
        })
    
    # ============ Discovery Operations ============
    
    async def create_discovery(
        self, 
        user_id: str,
        location_name: str,
        latitude: float,
        longitude: float,
        heat_score: float,
        temperature: float,
        ndvi: float,
        ai_description: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Save a new heat island discovery"""
        try:
            discovery_data = {
                'user_id': user_id,
                'location_name': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'heat_score': heat_score,
                'temperature': temperature,
                'ndvi': ndvi,
                'ai_description': ai_description,
                'image_url': image_url
            }
            response = self.client.table('discoveries').insert(discovery_data).execute()
            
            # Award points for discovery
            await self.add_points(user_id, 50)
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating discovery: {e}")
            return None
    
    async def get_user_discoveries(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all discoveries by a user"""
        try:
            response = self.client.table('discoveries').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching discoveries: {e}")
            return []
    
    async def get_top_discoveries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top heat island discoveries"""
        try:
            response = self.client.table('discoveries').select('*, profiles(username)').order('heat_score', desc=True).limit(limit).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching top discoveries: {e}")
            return []
    
    # ============ Mission Operations ============
    
    async def create_mission(
        self, 
        user_id: str,
        mission_type: str
    ) -> Optional[Dict[str, Any]]:
        """Create a new mission for user"""
        try:
            mission_data = {
                'user_id': user_id,
                'mission_type': mission_type,
                'status': 'pending',
                'points_earned': 0
            }
            response = self.client.table('missions').insert(mission_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating mission: {e}")
            return None
    
    async def complete_mission(
        self, 
        mission_id: str,
        points_earned: int
    ) -> Optional[Dict[str, Any]]:
        """Mark mission as completed"""
        try:
            # Update mission status
            response = self.client.table('missions').update({
                'status': 'completed',
                'points_earned': points_earned,
                'completed_at': 'now()'
            }).eq('id', mission_id).execute()
            
            if not response.data:
                return None
            
            mission = response.data[0]
            
            # Update user profile
            profile = await self.get_profile(mission['user_id'])
            if profile:
                await self.update_profile(mission['user_id'], {
                    'missions_completed': profile['missions_completed'] + 1
                })
                await self.add_points(mission['user_id'], points_earned)
            
            return mission
        except Exception as e:
            print(f"Error completing mission: {e}")
            return None
    
    async def get_user_missions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all missions for a user"""
        try:
            response = self.client.table('missions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching missions: {e}")
            return []
    
    # ============ Leaderboard Operations ============
    
    async def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get global leaderboard"""
        try:
            response = self.client.table('profiles').select('*').order('points', desc=True).limit(limit).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return []


# Global instance
supabase_service = SupabaseService()

