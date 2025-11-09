"""
Test-Endpoint für Supabase-Verbindung
"""
from fastapi import APIRouter, HTTPException
import logging

from app.core.supabase_client import supabase_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["test"])


@router.get(
    "/test-supabase",
    summary="🧪 Test Supabase Verbindung",
    description="Prüft ob Supabase-Verbindung funktioniert"
)
async def test_supabase_connection():
    """
    Testet die Verbindung zu Supabase.
    
    **Prüft:**
    1. Supabase Client initialisiert?
    2. Kann auf profiles-Tabelle zugreifen?
    3. Kann auf parent_cells-Tabelle zugreifen?
    
    Returns:
        Status-Information über Supabase-Verbindung
    """
    try:
        logger.info("🧪 Teste Supabase-Verbindung...")
        
        results = {
            "status": "testing",
            "tests": {}
        }
        
        # Test 1: Client vorhanden?
        try:
            if supabase_service.client:
                results["tests"]["client_initialized"] = {
                    "status": "✅ OK",
                    "message": "Supabase Client erfolgreich initialisiert"
                }
                logger.info("✅ Test 1: Client OK")
            else:
                results["tests"]["client_initialized"] = {
                    "status": "❌ FEHLER",
                    "message": "Supabase Client ist None"
                }
                logger.error("❌ Test 1: Client ist None")
        except Exception as e:
            results["tests"]["client_initialized"] = {
                "status": "❌ FEHLER",
                "message": f"Client-Fehler: {str(e)}"
            }
            logger.error(f"❌ Test 1 Fehler: {e}")
        
        # Test 2: Kann auf profiles-Tabelle zugreifen?
        try:
            response = supabase_service.client.table('profiles').select('id').limit(1).execute()
            results["tests"]["profiles_table"] = {
                "status": "✅ OK",
                "message": f"profiles-Tabelle erreichbar",
                "data_count": len(response.data) if response.data else 0
            }
            logger.info(f"✅ Test 2: profiles-Tabelle OK ({len(response.data) if response.data else 0} Einträge)")
        except Exception as e:
            results["tests"]["profiles_table"] = {
                "status": "❌ FEHLER",
                "message": f"Fehler beim Zugriff: {str(e)}"
            }
            logger.error(f"❌ Test 2 Fehler: {e}")
        
        # Test 3: Kann auf parent_cells-Tabelle zugreifen?
        try:
            response = supabase_service.client.table('parent_cells').select('id').limit(1).execute()
            results["tests"]["parent_cells_table"] = {
                "status": "✅ OK",
                "message": f"parent_cells-Tabelle erreichbar",
                "data_count": len(response.data) if response.data else 0
            }
            logger.info(f"✅ Test 3: parent_cells-Tabelle OK ({len(response.data) if response.data else 0} Einträge)")
        except Exception as e:
            results["tests"]["parent_cells_table"] = {
                "status": "⚠️ WARNUNG",
                "message": f"Tabelle existiert noch nicht oder Fehler: {str(e)}",
                "hint": "Führe database/QUICK_TEST_SCHEMA.sql in Supabase aus!"
            }
            logger.warning(f"⚠️ Test 3: parent_cells Fehler: {e}")
        
        # Test 4: Kann auf child_cells-Tabelle zugreifen?
        try:
            response = supabase_service.client.table('child_cells').select('id').limit(1).execute()
            results["tests"]["child_cells_table"] = {
                "status": "✅ OK",
                "message": f"child_cells-Tabelle erreichbar",
                "data_count": len(response.data) if response.data else 0
            }
            logger.info(f"✅ Test 4: child_cells-Tabelle OK ({len(response.data) if response.data else 0} Einträge)")
        except Exception as e:
            results["tests"]["child_cells_table"] = {
                "status": "⚠️ WARNUNG",
                "message": f"Tabelle existiert noch nicht oder Fehler: {str(e)}",
                "hint": "Führe database/QUICK_TEST_SCHEMA.sql in Supabase aus!"
            }
            logger.warning(f"⚠️ Test 4: child_cells Fehler: {e}")
        
        # Gesamtstatus
        all_ok = all(
            test.get("status", "").startswith("✅") 
            for test in results["tests"].values()
            if test.get("status", "").startswith("✅") or test.get("status", "").startswith("⚠️")
        )
        
        if all_ok:
            results["status"] = "✅ ALLES OK"
            results["message"] = "Supabase-Verbindung funktioniert!"
        else:
            critical_errors = [
                name for name, test in results["tests"].items()
                if test.get("status", "").startswith("❌")
            ]
            if critical_errors:
                results["status"] = "❌ FEHLER"
                results["message"] = f"Kritische Fehler bei: {', '.join(critical_errors)}"
            else:
                results["status"] = "⚠️ WARNUNG"
                results["message"] = "Verbindung OK, aber einige Tabellen fehlen noch"
        
        logger.info("=" * 70)
        logger.info(f"🧪 Test abgeschlossen: {results['status']}")
        logger.info("=" * 70)
        
        return results
    
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler beim Supabase-Test: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Testen der Verbindung: {str(e)}"
        )


@router.get(
    "/test-supabase-write",
    summary="🧪 Test Supabase Schreibzugriff",
    description="Erstellt Test-Parent-Cell um Schreibzugriff zu prüfen"
)
async def test_supabase_write():
    """
    Testet ob wir in Supabase schreiben können.
    Erstellt eine Test-Parent-Cell und löscht sie wieder.
    """
    try:
        logger.info("🧪 Teste Supabase Schreibzugriff...")
        
        # Test-Daten
        test_data = {
            'cell_key': 'test_00.00_00.00',
            'center_lat': 0.0,
            'center_lon': 0.0,
            'bbox_min_lat': -0.01,
            'bbox_min_lon': -0.01,
            'bbox_max_lat': 0.01,
            'bbox_max_lon': 0.01,
            'total_scans': 1,
            'last_scanned_at': 'now()'
        }
        
        # Versuche zu erstellen
        logger.info("   Erstelle Test-Parent-Cell...")
        response = supabase_service.client.table('parent_cells').insert(test_data).execute()
        
        if not response.data or len(response.data) == 0:
            return {
                "status": "❌ FEHLER",
                "message": "Konnte Test-Daten nicht erstellen",
                "error": "Keine Daten in Response"
            }
        
        created_id = response.data[0]['id']
        logger.info(f"   ✅ Test-Parent-Cell erstellt: {created_id}")
        
        # Lösche wieder
        logger.info("   Lösche Test-Parent-Cell...")
        delete_response = supabase_service.client.table('parent_cells').delete().eq('id', created_id).execute()
        logger.info("   ✅ Test-Parent-Cell gelöscht")
        
        return {
            "status": "✅ OK",
            "message": "Schreibzugriff funktioniert!",
            "details": {
                "created_id": created_id,
                "cell_key": test_data['cell_key']
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Schreibtest: {e}", exc_info=True)
        return {
            "status": "❌ FEHLER",
            "message": f"Schreibzugriff fehlgeschlagen: {str(e)}",
            "hint": "Prüfe: 1) SQL-Schema ausgeführt? 2) RLS-Policies korrekt? 3) .env korrekt?"
        }

