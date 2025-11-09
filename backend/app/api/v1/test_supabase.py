"""
Test endpoint for Supabase connection
"""
from fastapi import APIRouter, HTTPException
import logging

from app.core.supabase_client import supabase_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["test"])


@router.get(
    "/test-supabase",
    summary="🧪 Test Supabase Connection",
    description="Checks whether the Supabase connection is working"
)
async def test_supabase_connection():
    """
    Tests the connection to Supabase.
    
    **Checks:**
    1. Is the Supabase client initialized?
    2. Can it access the profiles table?
    3. Can it access the parent_cells table?
    
    Returns:
        Status information about the Supabase connection
    """
    try:
        logger.info("🧪 Testing Supabase connection...")
        
        results = {
            "status": "testing",
            "tests": {}
        }
        
        # Test 1: Is client initialized?
        try:
            if supabase_service.client:
                results["tests"]["client_initialized"] = {
                    "status": "✅ OK",
                    "message": "Supabase client successfully initialized"
                }
                logger.info("✅ Test 1: Client OK")
            else:
                results["tests"]["client_initialized"] = {
                    "status": "❌ ERROR",
                    "message": "Supabase client is None"
                }
                logger.error("❌ Test 1: Client is None")
        except Exception as e:
            results["tests"]["client_initialized"] = {
                "status": "❌ ERROR",
                "message": f"Client error: {str(e)}"
            }
            logger.error(f"❌ Test 1 error: {e}")
        
        # Test 2: Can access profiles table?
        try:
            response = supabase_service.client.table('profiles').select('id').limit(1).execute()
            results["tests"]["profiles_table"] = {
                "status": "✅ OK",
                "message": f"profiles table accessible",
                "data_count": len(response.data) if response.data else 0
            }
            logger.info(f"✅ Test 2: profiles table OK ({len(response.data) if response.data else 0} entries)")
        except Exception as e:
            results["tests"]["profiles_table"] = {
                "status": "❌ ERROR",
                "message": f"Error accessing table: {str(e)}"
            }
            logger.error(f"❌ Test 2 error: {e}")
        
        # Test 3: Can access parent_cells table?
        try:
            response = supabase_service.client.table('parent_cells').select('id').limit(1).execute()
            results["tests"]["parent_cells_table"] = {
                "status": "✅ OK",
                "message": f"parent_cells table accessible",
                "data_count": len(response.data) if response.data else 0
            }
            logger.info(f"✅ Test 3: parent_cells table OK ({len(response.data) if response.data else 0} entries)")
        except Exception as e:
            results["tests"]["parent_cells_table"] = {
                "status": "⚠️ WARNING",
                "message": f"Table does not exist yet or error: {str(e)}",
                "hint": "Run database/QUICK_TEST_SCHEMA.sql in Supabase!"
            }
            logger.warning(f"⚠️ Test 3: parent_cells error: {e}")
        
        # Test 4: Can access child_cells table?
        try:
            response = supabase_service.client.table('child_cells').select('id').limit(1).execute()
            results["tests"]["child_cells_table"] = {
                "status": "✅ OK",
                "message": f"child_cells table accessible",
                "data_count": len(response.data) if response.data else 0
            }
            logger.info(f"✅ Test 4: child_cells table OK ({len(response.data) if response.data else 0} entries)")
        except Exception as e:
            results["tests"]["child_cells_table"] = {
                "status": "⚠️ WARNING",
                "message": f"Table does not exist yet or error: {str(e)}",
                "hint": "Run database/QUICK_TEST_SCHEMA.sql in Supabase!"
            }
            logger.warning(f"⚠️ Test 4: child_cells error: {e}")
        
        # Overall status
        all_ok = all(
            test.get("status", "").startswith("✅") 
            for test in results["tests"].values()
            if test.get("status", "").startswith("✅") or test.get("status", "").startswith("⚠️")
        )
        
        if all_ok:
            results["status"] = "✅ ALL OK"
            results["message"] = "Supabase connection works!"
        else:
            critical_errors = [
                name for name, test in results["tests"].items()
                if test.get("status", "").startswith("❌")
            ]
            if critical_errors:
                results["status"] = "❌ ERROR"
                results["message"] = f"Critical errors in: {', '.join(critical_errors)}"
            else:
                results["status"] = "⚠️ WARNING"
                results["message"] = "Connection OK, but some tables are missing"
        
        logger.info("=" * 70)
        logger.info(f"🧪 Test completed: {results['status']}")
        logger.info("=" * 70)
        
        return results
    
    except Exception as e:
        logger.error(f"❌ Unexpected error during Supabase test: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error testing connection: {str(e)}"
        )


@router.get(
    "/test-supabase-write",
    summary="🧪 Test Supabase Write Access",
    description="Creates a test parent cell to verify write access"
)
async def test_supabase_write():
    """
    Tests whether we can write to Supabase.
    Creates a test parent cell and then deletes it.
    """
    try:
        logger.info("🧪 Testing Supabase write access...")
        
        # Test data
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
        
        # Try creating
        logger.info("   Creating test parent cell...")
        response = supabase_service.client.table('parent_cells').insert(test_data).execute()
        
        if not response.data or len(response.data) == 0:
            return {
                "status": "❌ ERROR",
                "message": "Could not create test data",
                "error": "No data in response"
            }
        
        created_id = response.data[0]['id']
        logger.info(f"   ✅ Test parent cell created: {created_id}")
        
        # Delete again
        logger.info("   Deleting test parent cell...")
        delete_response = supabase_service.client.table('parent_cells').delete().eq('id', created_id).execute()
        logger.info("   ✅ Test parent cell deleted")
        
        return {
            "status": "✅ OK",
            "message": "Write access works!",
            "details": {
                "created_id": created_id,
                "cell_key": test_data['cell_key']
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Error during write test: {e}", exc_info=True)
        return {
            "status": "❌ ERROR",
            "message": f"Write access failed: {str(e)}",
            "hint": "Check: 1) SQL schema executed? 2) RLS policies correct? 3) .env configuration correct?"
        }
    