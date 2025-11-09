"""
Quick Database Connection Test
Überprüft ob Supabase-Verbindung funktioniert und welche Tabellen existieren
"""
import sys
import os

# Füge parent directory zum path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import supabase_service


def test_connection():
    """Test Supabase Verbindung"""
    print("=" * 70)
    print("🧪 TESTE SUPABASE-VERBINDUNG")
    print("=" * 70)
    print()
    
    # Test 1: Client initialisiert?
    print("1️⃣ Client-Initialisierung...")
    try:
        if supabase_service.client:
            print("   ✅ Supabase Client erfolgreich initialisiert")
        else:
            print("   ❌ Client ist None")
            return
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        return
    
    print()
    
    # Test 2: Profiles Tabelle
    print("2️⃣ Teste 'profiles' Tabelle...")
    try:
        response = supabase_service.client.table('profiles').select('id').limit(1).execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ profiles-Tabelle existiert ({count} Einträge)")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    print()
    
    # Test 3: Parent Cells Tabelle
    print("3️⃣ Teste 'parent_cells' Tabelle...")
    try:
        response = supabase_service.client.table('parent_cells').select('id, cell_key, total_scans, child_cells_count').execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ parent_cells-Tabelle existiert ({count} Einträge)")
        
        if count > 0:
            print("\n   📊 Vorhandene Parent-Cells:")
            for cell in response.data[:5]:  # Zeige max 5
                print(f"      - {cell['cell_key']}: {cell['total_scans']} Scans, {cell['child_cells_count']} Children")
    except Exception as e:
        print(f"   ⚠️ Tabelle existiert noch nicht oder Fehler: {e}")
        print(f"   💡 Lösung: Führe database/QUICK_TEST_SCHEMA.sql in Supabase aus!")
    
    print()
    
    # Test 4: Child Cells Tabelle
    print("4️⃣ Teste 'child_cells' Tabelle...")
    try:
        response = supabase_service.client.table('child_cells').select('id').limit(1).execute()
        
        # Zähle alle
        count_response = supabase_service.client.table('child_cells').select('id', count='exact').execute()
        count = count_response.count if hasattr(count_response, 'count') else 0
        
        print(f"   ✅ child_cells-Tabelle existiert ({count} Einträge)")
    except Exception as e:
        print(f"   ⚠️ Tabelle existiert noch nicht oder Fehler: {e}")
        print(f"   💡 Lösung: Führe database/QUICK_TEST_SCHEMA.sql in Supabase aus!")
    
    print()
    
    # Test 5: Discoveries Tabelle
    print("5️⃣ Teste 'discoveries' Tabelle...")
    try:
        response = supabase_service.client.table('discoveries').select('id').limit(1).execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ discoveries-Tabelle existiert ({count} Einträge)")
    except Exception as e:
        print(f"   ⚠️ Tabelle existiert noch nicht: {e}")
    
    print()
    
    # Test 6: Missions Tabelle
    print("6️⃣ Teste 'missions' Tabelle...")
    try:
        response = supabase_service.client.table('missions').select('id').limit(1).execute()
        count = len(response.data) if response.data else 0
        print(f"   ✅ missions-Tabelle existiert ({count} Einträge)")
    except Exception as e:
        print(f"   ⚠️ Tabelle existiert noch nicht: {e}")
    
    print()
    print("=" * 70)
    print("✅ TEST ABGESCHLOSSEN")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_connection()
    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        print("\n💡 Prüfe:")
        print("   1. Ist backend/.env vorhanden?")
        print("   2. Sind SUPABASE_URL und SUPABASE_KEY gesetzt?")
        print("   3. Sind die Keys korrekt?")
        import traceback
        print("\nTraceback:")
        print(traceback.format_exc())

