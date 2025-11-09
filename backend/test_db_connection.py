"""
Quick Database Connection Test
Checks if Supabase connection works and which tables exist
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import supabase_service


def test_connection():
    """Test Supabase Connection"""
    print("=" * 70)
    print("🧪 TESTING SUPABASE CONNECTION")
    print("=" * 70)
    print()
    
    # Test 1: Client initialized?
    print("1️⃣ Client Initialization...")
    try:
        if supabase_service.client:
            print("   ✅ Supabase Client successfully initialized")
        else:
            print("   ❌ Client is None")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print()
    
    # Test 2: Profiles Table
    print("2️⃣ Testing 'profiles' table...")
    try:
        response = supabase_service.client.table('profiles').select('id').limit(1).execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ profiles table exists ({count} entries)")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    print()
    
    # Test 3: Parent Cells Table
    print("3️⃣ Testing 'parent_cells' table...")
    try:
        response = supabase_service.client.table('parent_cells').select('id, cell_key, total_scans, child_cells_count').execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ parent_cells table exists ({count} entries)")
        
        if count > 0:
            print("\n   📊 Available Parent-Cells:")
            for cell in response.data[:5]:  # Show max 5
                print(f"      - {cell['cell_key']}: {cell['total_scans']} Scans, {cell['child_cells_count']} Children")
    except Exception as e:
        print(f"   ⚠️ Table does not exist yet or error: {e}")
        print(f"   💡 Solution: Run database/QUICK_TEST_SCHEMA.sql in Supabase!")
    
    print()
    
    # Test 4: Child Cells Table
    print("4️⃣ Testing 'child_cells' table...")
    try:
        response = supabase_service.client.table('child_cells').select('id').limit(1).execute()
        
        # Count all
        count_response = supabase_service.client.table('child_cells').select('id', count='exact').execute()
        count = count_response.count if hasattr(count_response, 'count') else 0
        
        print(f"   ✅ child_cells table exists ({count} entries)")
    except Exception as e:
        print(f"   ⚠️ Table does not exist yet or error: {e}")
        print(f"   💡 Solution: Run database/QUICK_TEST_SCHEMA.sql in Supabase!")
    
    print()
    
    # Test 5: Discoveries Table
    print("5️⃣ Testing 'discoveries' table...")
    try:
        response = supabase_service.client.table('discoveries').select('id').limit(1).execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ discoveries table exists ({count} entries)")
    except Exception as e:
        print(f"   ⚠️ Table does not exist yet: {e}")
    
    print()
    
    # Test 6: Missions Table
    print("6️⃣ Testing 'missions' table...")
    try:
        response = supabase_service.client.table('missions').select('id').limit(1).execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ missions table exists ({count} entries)")
    except Exception as e:
        print(f"   ⚠️ Table does not exist yet: {e}")
    
    print()
    print("=" * 70)
    print("✅ TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_connection()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("\n💡 Check:")
        print("   1. Is backend/.env present?")
        print("   2. Are SUPABASE_URL and SUPABASE_KEY set?")
        print("   3. Are the keys correct?")
        import traceback
        print("\nTraceback:")
        print(traceback.format_exc())

