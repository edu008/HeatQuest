import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useGame } from "@/contexts/GameContext";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import BottomNav from "@/components/BottomNav";
import MapboxMap from "@/components/MapboxMap";

const MapView = () => {
  const { missions, setActiveMission, user, loadMissions, missionsLoading } = useGame();
  const { user: authUser, loading } = useAuth();
  const navigate = useNavigate();
  
  // Track ob Missionen bereits beim normalen Seitenwechsel geladen wurden
  const normalLoadDone = useRef(false);
  const loginScanStarted = useRef(false);
  
  // Mapbox Token aus Environment Variable oder localStorage (Fallback)
  const envToken = import.meta.env.VITE_MAPBOX_TOKEN;
  const [mapboxToken, setMapboxToken] = useState<string>(() => {
    return envToken || localStorage.getItem("mapbox_public_token") || "";
  });
  
  const handleSaveToken = () => {
    localStorage.setItem("mapbox_public_token", mapboxToken);
    window.location.reload(); // Reload um Token zu aktivieren
  };

  // Login-Scan nur beim Login, nicht bei Seitenwechsel
  useEffect(() => {
    console.log('🗺️ MapView - Auth status:', { loading, hasUser: !!authUser, email: authUser?.email })
    
    if (!loading && !authUser) {
      console.log('❌ No user found, redirecting to login...')
      navigate("/");
      return;
    }
    
    if (!loading && authUser) {
      const needsLoginScan = sessionStorage.getItem('needsLoginScan');
      
      if (needsLoginScan === 'true' && !loginScanStarted.current) {
        console.log('🚀 Login-Scan startet...')
        loginScanStarted.current = true;
        normalLoadDone.current = true; // Missions werden unten manuell geladen
        // Lade vorhandene Missionen sofort, bevor der Backend-Scan fertig ist
        loadMissions();
        
        // GPS-Position holen
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            async (position) => {
              try {
                const { latitude, longitude } = position.coords;
                console.log(`📍 GPS: ${latitude}, ${longitude}`);
                
                // Backend Login-Scan aufrufen
                const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await fetch(
                  `${apiUrl}/api/v1/scan-on-login?user_id=${authUser.id}&latitude=${latitude}&longitude=${longitude}&radius_m=500`,
                  { method: 'POST' }
                );
                
                if (response.ok) {
                  const result = await response.json();
                  console.log('✅ Login-Scan completed:', result);
                } else {
                  console.error('❌ Login-Scan failed:', response.status);
                }
                
                // Flag entfernen
                sessionStorage.removeItem('needsLoginScan');
                loginScanStarted.current = false;
                
                // Missionen laden
                const missionsAfterScan = await loadMissions();
                console.log(`✅ ${missionsAfterScan.length} missions loaded after login scan!`);
                
              } catch (error) {
                console.error('❌ Login-Scan error:', error);
                sessionStorage.removeItem('needsLoginScan');
                loginScanStarted.current = false;
                loadMissions(); // Versuche dennoch Missionen zu laden
              }
            },
            (error) => {
              console.error('❌ GPS error:', error);
              sessionStorage.removeItem('needsLoginScan');
              loginScanStarted.current = false;
              loadMissions(); // Lade Missionen trotzdem
            }
          );
        } else {
          console.error('❌ Geolocation not supported');
          sessionStorage.removeItem('needsLoginScan');
          loginScanStarted.current = false;
          loadMissions();
        }
      } else {
        // Kein Login-Scan, lade Missionen nur einmal beim normalen Seitenwechsel
        if (!normalLoadDone.current && !missionsLoading) {
          console.log('📋 Loading missions (no login-scan)...')
          normalLoadDone.current = true;
          loadMissions();
        }
      }
    }
  }, [authUser, loading, navigate, loadMissions]);

  const handleMissionClick = (mission: any) => {
    setActiveMission(mission);
    navigate(`/mission/${mission.id}`);
  };

  return (
    <div className="relative h-screen w-full">
      {/* Header */}
      <motion.div
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="absolute top-0 left-0 right-0 z-[1000] bg-gradient-to-b from-card/95 to-transparent backdrop-blur-sm p-4"
      >
        <div className="flex items-center justify-center max-w-2xl mx-auto">
          <div className="text-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-heat via-primary to-cool-intense bg-clip-text text-transparent">
              HeatQuest
            </h1>
            <p className="text-sm text-muted-foreground">
              {loading ? "Loading..." : `Hello, ${authUser?.user_metadata?.user_name || authUser?.email?.split('@')[0] || user?.username}! 👋`}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Map Area */}
      {mapboxToken ? (
        <div className="h-full w-full">
          <MapboxMap token={mapboxToken} missions={missions} onMissionClick={handleMissionClick} />
        </div>
      ) : (
        <div className="flex-1 h-full w-full flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 rounded-3xl space-y-4">
            <h2 className="text-xl font-bold">Mapbox Token</h2>
            <p className="text-sm text-muted-foreground">
              Füge deinen Mapbox Public Token ein, um die Karte zu laden.
            </p>
            <Input
              placeholder="pk.eyJ1Ijo..."
              value={mapboxToken}
              onChange={(e) => setMapboxToken(e.target.value)}
              className="rounded-xl"
            />
            <Button onClick={handleSaveToken} disabled={!mapboxToken.trim()} className="w-full rounded-xl">
              Karte anzeigen
            </Button>
            <p className="text-xs text-muted-foreground">
              Du findest den Token unter mapbox.com → Tokens.
            </p>
          </Card>
        </div>
      )}

      <BottomNav />
    </div>
  );
};

export default MapView;
