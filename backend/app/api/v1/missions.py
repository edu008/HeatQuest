"""
Missions-API-Endpunkte.
REST-API für Mission-Management und Gamification.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.models.mission import (
    MissionCreate,
    MissionResponse,
    MissionUpdate,
    MissionListResponse
)
from app.services.mission_generation_service import mission_generation_service
from app.core.supabase_client import supabase_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["missions"])


@router.post(
    "/missions/generate",
    summary="Generiere Missionen automatisch",
    description="Erstellt Missionen basierend auf cell_analyses für einen User"
)
async def generate_missions(
    user_id: str = Query(..., description="User ID"),
    parent_cell_id: str = Query(..., description="Parent Cell ID"),
    user_lat: float = Query(..., description="User Latitude", ge=-90, le=90),
    user_lon: float = Query(..., description="User Longitude", ge=-180, le=180),
    max_missions: Optional[int] = Query(5, description="Max. Anzahl Missionen", ge=1, le=10)
):
    """
    🎯 **AUTOMATISCHE MISSION-GENERIERUNG**
    
    Erstellt Missionen basierend auf vorhandenen cell_analyses:
    - Findet Hotspot-Zellen (Heat Score >= 11)
    - Prüft ob User bereits Missionen für diese Zellen hat
    - Sortiert nach Entfernung zum User
    - Erstellt neue Missionen
    
    **Workflow:**
    1. User scannt Bereich → AI-Analysen werden erstellt
    2. System ruft `/missions/generate` auf
    3. Missionen werden automatisch erstellt
    4. Frontend kann Missionen abrufen
    
    **Beispiel-URL:**
    ```
    /api/v1/missions/generate?user_id=...&parent_cell_id=...&user_lat=46.95&user_lon=7.49
    ```
    
    **Response:**
    - Liste von neu erstellten Missionen
    - Kompatibel mit Frontend Mission-Interface
    """
    
    try:
        logger.info(f"🎯 Mission Generation Request: User={user_id}, Parent={parent_cell_id}")
        
        missions = await mission_generation_service.generate_missions_from_analyses(
            parent_cell_id=parent_cell_id,
            user_id=user_id,
            user_lat=user_lat,
            user_lon=user_lon,
            max_missions=max_missions
        )
        
        logger.info(f"✅ {len(missions)} Missionen generiert")
        
        return JSONResponse(content={
            "success": True,
            "missions_created": len(missions),
            "missions": missions
        })
    
    except Exception as e:
        logger.error(f"❌ Fehler bei Mission-Generierung: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei Mission-Generierung: {str(e)}"
        )


@router.get(
    "/missions",
    summary="Liste aller Missionen eines Users",
    description="Gibt alle Missionen eines Users zurück"
)
async def get_user_missions(
    user_id: str = Query(..., description="User ID"),
    status: Optional[str] = Query(None, description="Filter nach Status (pending, active, completed)"),
    include_completed: Optional[bool] = Query(True, description="Completed Missionen inkludieren")
):
    """
    📋 **USER MISSIONEN ABRUFEN**
    
    Gibt alle Missionen eines Users zurück, kompatibel mit Frontend.
    
    **Filter-Optionen:**
    - `status`: Filter nach Status (pending, active, completed, cancelled)
    - `include_completed`: False = nur offene Missionen
    
    **Beispiel-URL:**
    ```
    /api/v1/missions?user_id=123&include_completed=false
    ```
    
    **Response Format:**
    - Kompatibel mit Frontend `Mission` Interface
    - Enthält: id, title, description, lat, lng, heatRisk, reasons, actions, completed
    """
    
    try:
        logger.info(f"📋 Get Missions: User={user_id}, Status={status}, Include Completed={include_completed}")
        
        # Query Builder
        query = supabase_service.client.table('missions').select('*').eq('user_id', user_id)
        
        # Filter nach Status
        if status:
            query = query.eq('status', status)
        elif not include_completed:
            query = query.in_('status', ['pending', 'active'])
        
        # Sortiere nach created_at DESC
        query = query.order('created_at', desc=True)
        
        response = query.execute()
        
        if not response.data:
            return JSONResponse(content={
                "missions": [],
                "total_count": 0,
                "pending_count": 0,
                "completed_count": 0,
                "user_id": user_id
            })
        
        missions_raw = response.data
        
        # Konvertiere zu Frontend-Format
        missions = []
        for mission in missions_raw:
            # Extrahiere vollständige Actions mit Details aus required_actions JSONB
            actions_detailed = []
            required_actions = mission.get('required_actions', [])
            if isinstance(required_actions, list):
                for action in required_actions:
                    if isinstance(action, dict):
                        actions_detailed.append({
                            'action': action.get('action', ''),
                            'description': action.get('description', ''),
                            'priority': action.get('priority', 'medium')
                        })
            
            # Fallback
            if not actions_detailed:
                actions_detailed = [
                    {
                        'action': 'Analyze area',
                        'description': 'Document the current heat conditions',
                        'priority': 'high'
                    }
                ]
            
            # Reasons (aus Main Cause oder Analysis)
            reasons = []
            if mission.get('description'):
                reasons.append(mission['description'])
            
            # Frontend-kompatibles Format
            mission_response = {
                "id": mission['id'],
                "user_id": mission['user_id'],
                "title": mission['title'],
                "description": mission.get('description'),
                "lat": mission['latitude'],
                "lng": mission['longitude'],
                "heatRisk": mission.get('heat_risk_score', 0),
                "reasons": reasons,
                "actions": actions_detailed,  # Vollständige Action-Objekte mit description & priority
                "completed": mission['status'] == 'completed',
                "imageUrl": None,
                # Additional fields
                "parent_cell_id": mission.get('parent_cell_id'),
                "child_cell_id": mission.get('child_cell_id'),
                "cell_analysis_id": mission.get('cell_analysis_id'),
                "mission_type": mission.get('mission_type'),
                "status": mission['status'],
                "points_earned": mission.get('points_earned', 0),
                "distance_to_user": mission.get('distance_to_user'),
                "created_at": mission['created_at'],
                "completed_at": mission.get('completed_at')
            }
            
            missions.append(mission_response)
        
        # Zähle Statistiken
        total_count = len(missions)
        pending_count = sum(1 for m in missions if m['status'] in ['pending', 'active'])
        completed_count = sum(1 for m in missions if m['status'] == 'completed')
        
        logger.info(f"✅ {total_count} Missions retrieved (Pending: {pending_count}, Completed: {completed_count})")
        
        return JSONResponse(content={
            "missions": missions,
            "total_count": total_count,
            "pending_count": pending_count,
            "completed_count": completed_count,
            "user_id": user_id
        })
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Missionen: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen der Missionen: {str(e)}"
        )


@router.get(
    "/missions/{mission_id}",
    summary="Einzelne Mission abrufen",
    description="Gibt Details einer Mission zurück"
)
async def get_mission(mission_id: str):
    """
    🎯 **EINZELNE MISSION ABRUFEN**
    
    Gibt Details einer spezifischen Mission zurück.
    
    **Beispiel-URL:**
    ```
    /api/v1/missions/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    
    try:
        logger.info(f"🎯 Get Mission: {mission_id}")
        
        response = supabase_service.client.table('missions').select('*').eq('id', mission_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Mission nicht gefunden")
        
        mission = response.data
        
        # Konvertiere zu Frontend-Format (wie oben)
        actions_detailed = []
        required_actions = mission.get('required_actions', [])
        if isinstance(required_actions, list):
            for action in required_actions:
                if isinstance(action, dict):
                    actions_detailed.append({
                        'action': action.get('action', ''),
                        'description': action.get('description', ''),
                        'priority': action.get('priority', 'medium')
                    })
        
        if not actions_detailed:
            actions_detailed = [{
                'action': 'Analyze area',
                'description': 'Document the current heat conditions',
                'priority': 'high'
            }]
        
        reasons = []
        if mission.get('description'):
            reasons.append(mission['description'])
        
        mission_response = {
            "id": mission['id'],
            "user_id": mission['user_id'],
            "title": mission['title'],
            "description": mission.get('description'),
            "lat": mission['latitude'],
            "lng": mission['longitude'],
            "heatRisk": mission.get('heat_risk_score', 0),
            "reasons": reasons,
            "actions": actions_detailed,  # Vollständige Action-Objekte
            "completed": mission['status'] == 'completed',
            "imageUrl": None,
            "parent_cell_id": mission.get('parent_cell_id'),
            "child_cell_id": mission.get('child_cell_id'),
            "cell_analysis_id": mission.get('cell_analysis_id'),
            "mission_type": mission.get('mission_type'),
            "status": mission['status'],
            "points_earned": mission.get('points_earned', 0),
            "distance_to_user": mission.get('distance_to_user'),
            "created_at": mission['created_at'],
            "completed_at": mission.get('completed_at')
        }
        
        return JSONResponse(content=mission_response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Mission: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen der Mission: {str(e)}"
        )


@router.put(
    "/missions/{mission_id}/complete",
    summary="Mission abschließen",
    description="Markiert eine Mission als abgeschlossen und vergibt Punkte"
)
async def complete_mission(
    mission_id: str,
    user_id: str = Query(..., description="User ID für Verifizierung")
):
    """
    ✅ **MISSION ABSCHLIESSEN**
    
    Markiert Mission als abgeschlossen und vergibt XP.
    
    **Workflow:**
    1. Prüft ob Mission dem User gehört
    2. Ändert Status zu 'completed'
    3. Vergibt 100 XP (oder custom Punkte)
    4. Setzt completed_at Timestamp
    
    **Beispiel-URL:**
    ```
    PUT /api/v1/missions/123/complete?user_id=456
    ```
    """
    
    try:
        logger.info(f"✅ Complete Mission: {mission_id} by User {user_id}")
        
        # Prüfe ob Mission existiert und User gehört
        response = supabase_service.client.table('missions').select('*').eq('id', mission_id).eq('user_id', user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Mission nicht gefunden oder gehört anderem User")
        
        mission = response.data
        
        if mission['status'] == 'completed':
            raise HTTPException(status_code=400, detail="Mission bereits abgeschlossen")
        
        # Update Mission
        update_data = {
            'status': 'completed',
            'completed_at': 'now()',
            'points_earned': 100,  # Standard XP
            'completed_by_user_id': user_id
        }
        
        update_response = supabase_service.client.table('missions').update(update_data).eq('id', mission_id).execute()
        
        if not update_response.data:
            raise HTTPException(status_code=500, detail="Fehler beim Update")
        
        logger.info(f"✅ Mission {mission_id} abgeschlossen! +100 XP")
        
        return JSONResponse(content={
            "success": True,
            "mission_id": mission_id,
            "status": "completed",
            "points_earned": 100,
            "message": "Mission erfolgreich abgeschlossen! +100 XP"
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Abschließen der Mission: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abschließen: {str(e)}"
        )


@router.post(
    "/missions/generate-from-existing-analyses",
    summary="Generate missions from existing analyses (DEBUG)",
    description="Generates missions for ALL existing analyses that don't have missions yet"
)
async def generate_from_existing_analyses(
    user_id: str = Query(..., description="User ID"),
    user_lat: float = Query(..., description="User Latitude (for distance calculation)", ge=-90, le=90),
    user_lon: float = Query(..., description="User Longitude (for distance calculation)", ge=-180, le=180)
):
    """
    🛠️ **DEBUG: GENERATE MISSIONS FROM EXISTING ANALYSES**
    
    This endpoint generates missions for ALL existing cell analyses that don't have missions yet.
    Useful for retroactively generating missions after data was already collected.
    
    **Example:**
    ```
    POST /api/v1/missions/generate-from-existing-analyses?user_id=USER_UUID&user_lat=46.95&user_lon=7.49
    ```
    
    **Process:**
    1. Loads ALL cell analyses from ALL parent cells
    2. Filters analyses with Heat Score >= 11
    3. Checks which don't have missions yet
    4. Generates missions for them
    """
    
    try:
        logger.info("=" * 70)
        logger.info("🛠️ DEBUG: Generate missions from ALL existing analyses")
        logger.info(f"   User: {user_id}")
        logger.info("=" * 70)
        
        # Get ALL parent cells
        parent_cells_response = supabase_service.client.table('parent_cells').select('id').execute()
        
        if not parent_cells_response.data:
            return JSONResponse(content={
                "success": False,
                "message": "No parent cells found",
                "missions_created": 0
            })
        
        parent_cell_ids = [p['id'] for p in parent_cells_response.data]
        logger.info(f"📊 Found {len(parent_cell_ids)} parent cells")
        
        total_missions = []
        
        # Generate missions for each parent cell
        for parent_id in parent_cell_ids:
            try:
                missions = await mission_generation_service.generate_missions_from_analyses(
                    parent_cell_id=parent_id,
                    user_id=user_id,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    max_missions=100  # High limit to process all
                )
                total_missions.extend(missions)
            except Exception as e:
                logger.error(f"⚠️ Error for parent {parent_id}: {e}")
                continue
        
        logger.info("=" * 70)
        logger.info(f"✅ TOTAL MISSIONS GENERATED: {len(total_missions)}")
        logger.info("=" * 70)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Successfully generated {len(total_missions)} missions",
            "missions_created": len(total_missions),
            "missions": total_missions[:10]  # Return first 10 as preview
        })
    
    except Exception as e:
        logger.error(f"❌ Error in debug mission generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.post(
    "/missions/cleanup-duplicate-analyses",
    summary="Cleanup duplicate cell analyses (DEBUG)",
    description="Removes duplicate cell_analyses entries (keeps only the newest one per child_cell_id)"
)
async def cleanup_duplicate_analyses():
    """
    🧹 **DEBUG: CLEANUP DUPLICATE ANALYSES**
    
    Removes duplicate cell_analyses entries that have the same child_cell_id.
    Keeps only the newest entry (by created_at) for each child_cell_id.
    
    **Example:**
    ```
    POST /api/v1/missions/cleanup-duplicate-analyses
    ```
    """
    
    try:
        logger.info("=" * 70)
        logger.info("🧹 Starting duplicate cleanup...")
        
        # Get all analyses ordered by created_at DESC
        response = supabase_service.client.table('cell_analyses').select(
            'id, child_cell_id, created_at'
        ).order('created_at', desc=True).execute()
        
        if not response.data:
            return JSONResponse(content={
                "success": True,
                "message": "No analyses found",
                "duplicates_removed": 0
            })
        
        analyses = response.data
        logger.info(f"📊 Found {len(analyses)} total analyses")
        
        # Track which child_cell_ids we've seen
        seen_child_cell_ids = set()
        duplicates_to_delete = []
        
        for analysis in analyses:
            child_cell_id = analysis['child_cell_id']
            
            if child_cell_id in seen_child_cell_ids:
                # This is a duplicate - mark for deletion
                duplicates_to_delete.append(analysis['id'])
                logger.info(f"   🗑️  Duplicate found for child_cell: {child_cell_id}")
            else:
                # First occurrence - keep it
                seen_child_cell_ids.add(child_cell_id)
        
        logger.info(f"🔍 Found {len(duplicates_to_delete)} duplicates to delete")
        
        # Delete duplicates
        if duplicates_to_delete:
            for analysis_id in duplicates_to_delete:
                supabase_service.client.table('cell_analyses').delete().eq('id', analysis_id).execute()
            
            logger.info(f"✅ Deleted {len(duplicates_to_delete)} duplicate analyses")
        
        logger.info("=" * 70)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Cleanup completed. Removed {len(duplicates_to_delete)} duplicates.",
            "total_analyses_checked": len(analyses),
            "duplicates_removed": len(duplicates_to_delete),
            "unique_analyses_remaining": len(seen_child_cell_ids)
        })
    
    except Exception as e:
        logger.error(f"❌ Error in cleanup: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.post(
    "/missions/{mission_id}/claim",
    summary="Mission reservieren",
    description="Reserviert eine Mission für einen User"
)
async def claim_mission(
    mission_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    🎯 **MISSION RESERVIEREN**
    
    Reserviert eine Mission für einen User:
    - Ändert Status von 'pending' zu 'active'
    - Setzt assigned_user_id
    - Andere User können diese Mission nicht mehr übernehmen
    """
    try:
        logger.info(f"🎯 Claim Mission: {mission_id} by User {user_id}")
        
        # Prüfe ob Mission existiert und verfügbar ist
        response = supabase_service.client.table('missions').select('*').eq('id', mission_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        mission = response.data[0]
        
        # Prüfe ob Mission bereits reserviert ist
        if mission.get('status') == 'active' and mission.get('assigned_user_id'):
            if mission['assigned_user_id'] != user_id:
                raise HTTPException(status_code=400, detail="Mission already claimed by another user")
            else:
                return JSONResponse(content={"success": True, "message": "Mission already claimed by you"})
        
        # Reserviere Mission
        update_response = supabase_service.client.table('missions').update({
            'status': 'active',
            'assigned_user_id': user_id,
            'updated_at': 'now()'
        }).eq('id', mission_id).execute()
        
        logger.info(f"✅ Mission {mission_id} claimed by {user_id}")
        
        return JSONResponse(content={"success": True, "mission": update_response.data[0] if update_response.data else None})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error claiming mission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/missions/{mission_id}/complete-action",
    summary="Action abschließen",
    description="Schließt eine einzelne Action ab und vergibt Punkte"
)
async def complete_action(
    mission_id: str,
    user_id: str = Query(..., description="User ID"),
    action_index: int = Query(..., description="Index der Action (0-based)")
):
    """
    ✅ **ACTION ABSCHLIESSEN**
    
    Schließt eine einzelne Action ab:
    - Markiert Action als completed
    - Vergibt Punkte basierend auf Priorität:
      - HIGH: 50 Punkte
      - MEDIUM: 30 Punkte
      - LOW: 20 Punkte
    - Aktualisiert User-Profile
    """
    try:
        logger.info(f"✅ Complete Action: Mission {mission_id}, User {user_id}, Action {action_index}")
        
        # Hole Mission
        response = supabase_service.client.table('missions').select('*').eq('id', mission_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        mission = response.data[0]
        
        # Prüfe ob User diese Mission beansprucht hat
        if mission.get('assigned_user_id') != user_id:
            raise HTTPException(status_code=403, detail="You don't own this mission")
        
        # Hole required_actions (JSONB)
        required_actions = mission.get('required_actions', [])
        
        if action_index < 0 or action_index >= len(required_actions):
            raise HTTPException(status_code=400, detail="Invalid action index")
        
        action = required_actions[action_index]
        
        # Prüfe ob bereits completed
        if action.get('completed', False):
            return JSONResponse(content={"success": True, "message": "Action already completed", "points_awarded": 0})
        
        # Markiere als completed
        action['completed'] = True
        required_actions[action_index] = action
        
        # Berechne Punkte
        priority = action.get('priority', 'medium')
        points_map = {'high': 50, 'medium': 30, 'low': 20}
        points = points_map.get(priority, 20)
        
        # Update Mission
        supabase_service.client.table('missions').update({
            'required_actions': required_actions,
            'updated_at': 'now()'
        }).eq('id', mission_id).execute()
        
        # Update User Points
        profile_response = supabase_service.client.table('profiles').select('points, level, missions_completed').eq('id', user_id).execute()
        
        if profile_response.data and len(profile_response.data) > 0:
            current_points = profile_response.data[0].get('points', 0)
            current_level = profile_response.data[0].get('level', 1)
            current_missions_completed = profile_response.data[0].get('missions_completed', 0)
            new_points = current_points + points
            
            # Level-Up Logik (500 Punkte pro Level)
            new_level = (new_points // 500) + 1
            
            supabase_service.client.table('profiles').update({
                'points': new_points,
                'level': new_level
            }).eq('id', user_id).execute()
            
            logger.info(f"✅ User {user_id}: +{points} points (Total: {new_points}, Level: {new_level})")
        
        # Prüfe ob alle Actions completed sind
        all_completed = all(a.get('completed', False) for a in required_actions)
        
        if all_completed:
            # Mission als completed markieren
            supabase_service.client.table('missions').update({
                'status': 'completed',
                'completed_at': 'now()'
            }).eq('id', mission_id).execute()
            
            # Update missions_completed counter
            if profile_response.data and len(profile_response.data) > 0:
                supabase_service.client.table('profiles').update({
                    'missions_completed': current_missions_completed + 1
                }).eq('id', user_id).execute()
            
            logger.info(f"🎉 Mission {mission_id} fully completed!")
        
        return JSONResponse(content={
            "success": True,
            "points_awarded": points,
            "action_completed": True,
            "mission_completed": all_completed
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error completing action: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/missions/{mission_id}/release",
    summary="Mission freigeben",
    description="Gibt eine Mission frei, damit andere User sie übernehmen können"
)
async def release_mission(
    mission_id: str,
    user_id: str = Query(..., description="User ID")
):
    """
    🔓 **MISSION FREIGEBEN**
    
    Gibt eine Mission frei:
    - Setzt Status zurück auf 'pending'
    - Entfernt assigned_user_id
    - Andere User können Mission übernehmen
    - Fortschritt bleibt erhalten (completed actions bleiben)
    """
    try:
        logger.info(f"🔓 Release Mission: {mission_id} by User {user_id}")
        
        # Hole Mission
        response = supabase_service.client.table('missions').select('*').eq('id', mission_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        mission = response.data[0]
        
        # Prüfe ob User diese Mission besitzt
        if mission.get('assigned_user_id') != user_id:
            raise HTTPException(status_code=403, detail="You don't own this mission")
        
        # Gebe Mission frei
        supabase_service.client.table('missions').update({
            'status': 'pending',
            'assigned_user_id': None,
            'updated_at': 'now()'
        }).eq('id', mission_id).execute()
        
        logger.info(f"✅ Mission {mission_id} released")
        
        return JSONResponse(content={"success": True, "message": "Mission released successfully"})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error releasing mission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/leaderboard",
    summary="Leaderboard abrufen",
    description="Gibt die Top 5 Spieler sortiert nach Punkten zurück"
)
async def get_leaderboard(limit: int = Query(5, description="Max. Anzahl Spieler", ge=1, le=5)):
    """
    🏆 **LEADERBOARD**
    
    Gibt die Top-Spieler sortiert nach Punkten zurück.
    """
    try:
        logger.info(f"🏆 Get Leaderboard (limit: {limit})")
        
        # Hole Top-Spieler aus profiles Tabelle
        response = supabase_service.client.table('profiles')\
            .select('id, username, avatar_url, points, level, missions_completed')\
            .order('points', desc=True)\
            .limit(limit)\
            .execute()
        
        leaderboard = response.data if response.data else []
        
        logger.info(f"✅ {len(leaderboard)} Spieler im Leaderboard")
        
        return JSONResponse(content={
            "leaderboard": leaderboard,
            "total_players": len(leaderboard)
        })
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen des Leaderboards: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen des Leaderboards: {str(e)}"
        )


@router.get(
    "/missions/health",
    summary="Health Check",
    description="Prüft ob Mission-Service verfügbar ist"
)
async def health_check():
    """Health Check für Mission-Service."""
    return {
        "status": "healthy",
        "service": "Mission Service",
        "version": "1.0.0"
    }

