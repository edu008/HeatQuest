import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useGame } from "@/contexts/GameContext";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import BottomNav from "@/components/BottomNav";
import { Camera, Loader2 } from "lucide-react";
import MapboxMap from "@/components/MapboxMap";
import { useHeatmap } from "@/hooks/useHeatmap";
import { useI18n } from "@/contexts/I18nContext";

const MapView = () => {
  const { missions, setActiveMission, user } = useGame();
  const { user: authUser, loading } = useAuth();
  const navigate = useNavigate();
  const { scanCurrentLocation, loading: scanLoading, data: heatmapData } = useHeatmap();
  const { t } = useI18n();
  
  // Mapbox Token aus Environment Variable oder localStorage (Fallback)
  const envToken = import.meta.env.VITE_MAPBOX_TOKEN;
  const [mapboxToken, setMapboxToken] = useState<string>(() => {
    return envToken || localStorage.getItem("mapbox_public_token") || "";
  });
  
  const handleSaveToken = () => {
    localStorage.setItem("mapbox_public_token", mapboxToken);
    window.location.reload(); // Reload um Token zu aktivieren
  };

  // Automatischer Scan beim Laden der Map
  useEffect(() => {
    console.log('🗺️ MapView - Auth status:', { loading, hasUser: !!authUser, email: authUser?.email })
    
    if (!loading && !authUser) {
      console.log('❌ No user found, redirecting to login...')
      navigate("/");
      return;
    }
    
    if (!loading && authUser && !heatmapData && !scanLoading) {
      console.log('✅ User authenticated, auto-scanning current location...')
      // Auto-scan nach kurzer Verzögerung
      const timer = setTimeout(async () => {
        try {
          await scanCurrentLocation(500); // 500m radius
        } catch (error) {
          console.error('Auto-scan failed:', error);
        }
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [authUser, loading, navigate, heatmapData, scanLoading, scanCurrentLocation]);

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
        className="sticky top-0 z-[1000] w-full bg-card/95 backdrop-blur-sm p-4 shadow-sm"
      >
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-heat via-primary to-cool-intense bg-clip-text text-transparent">
              HeatQuest
            </h1>
            <p className="text-sm text-muted-foreground">
              {loading
                ? t("loading")
                : t("hello_user", { name: authUser?.user_metadata?.user_name || authUser?.email?.split("@")[0] || user?.username || "" })}
            </p>
          </div>
          <Button
            onClick={() => navigate("/analyze")}
            disabled={scanLoading}
            className="rounded-2xl bg-gradient-to-r from-heat to-primary hover:from-heat-intense hover:to-heat shadow-lg"
          >
            <Camera className="w-5 h-5 mr-2" />
            {t("analyze")}
          </Button>
        </div>
      </motion.div>

      {/* Loading Indicator */}
      {scanLoading && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-24 left-4 right-4 z-[999] max-w-md"
        >
          <Card className="p-4 bg-card/95 backdrop-blur-sm">
            <div className="flex items-center space-x-3">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
              <div>
                <h3 className="font-bold">{t("analyzing_area")}</h3>
                <p className="text-sm text-muted-foreground">
                  {t("checking_area_cached")}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Heatmap Data Display */}
      {!scanLoading && heatmapData && (() => {
        // Berechne Statistiken aus Grid Cells
        const hotspots = heatmapData.grid_cells.filter(c => c.is_hotspot);
        const avgTemp = heatmapData.grid_cells.reduce((sum, c) => sum + c.temp, 0) / heatmapData.grid_cells.length;
        const avgNdvi = heatmapData.grid_cells.reduce((sum, c) => sum + c.ndvi, 0) / heatmapData.grid_cells.length;
        
        return (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-24 left-4 right-4 z-[999] max-w-md"
          >
            <Card className="p-4 bg-card/95 backdrop-blur-sm">
              <h3 className="font-bold mb-2">{t("area_analysis")}</h3>
              <div className="text-sm space-y-1">
                <p>📊 {t("total_cells")}: {heatmapData.total_cells}</p>
                <p>🔥 {t("hotspots")}: {hotspots.length}</p>
                <p>🌡️ {t("avg_temp")}: {avgTemp.toFixed(1)}°C</p>
                <p>🌿 {t("avg_ndvi")}: {avgNdvi.toFixed(2)}</p>
                <p>
                  {heatmapData.from_cache ? (
                    <span className="text-green-500">⚡ {t("previously_scanned")}</span>
                  ) : (
                    <span className="text-blue-500">🆕 {t("newly_scanned")}</span>
                  )}
                </p>
                {heatmapData.parent_cell_info && (
                  <p className="text-xs text-muted-foreground">
                    📍 {t("scanned_times", { count: heatmapData.parent_cell_info.total_scans })}
                  </p>
                )}
              </div>
            </Card>
          </motion.div>
        );
      })()}

      {/* Map Area (push below header height ~6rem) */}
      {mapboxToken ? (
        <div className="h-[calc(100dvh-5rem)] w-full">
          <MapboxMap token={mapboxToken} missions={missions} onMissionClick={handleMissionClick} />
        </div>
      ) : (
        <div className="h-[calc(100dvh-5rem)] w-full flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 rounded-3xl space-y-4">
            <h2 className="text-xl font-bold">{t("mapbox_token_title")}</h2>
            <p className="text-sm text-muted-foreground">{t("mapbox_token_desc")}</p>
            <Input
              placeholder={t("token_placeholder")}
              value={mapboxToken}
              onChange={(e) => setMapboxToken(e.target.value)}
              className="rounded-xl"
            />
            <Button onClick={handleSaveToken} disabled={!mapboxToken.trim()} className="w-full rounded-xl">
              {t("show_map")}
            </Button>
            <p className="text-xs text-muted-foreground">
              {t("token_help")}
            </p>
          </Card>
        </div>
      )}

      <BottomNav />
    </div>
  );
};

export default MapView;
