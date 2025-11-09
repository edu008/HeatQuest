import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useGame } from "@/contexts/GameContext";
import { useNavigate } from "react-router-dom";
import BottomNav from "@/components/BottomNav";
import { Camera } from "lucide-react";
import MapboxMap from "@/components/MapboxMap";

const MapView = () => {
  const { missions, setActiveMission, user } = useGame();
  const navigate = useNavigate();
  const [mapboxToken, setMapboxToken] = useState<string>(() => localStorage.getItem("mapbox_public_token") || "");
  const handleSaveToken = () => {
    localStorage.setItem("mapbox_public_token", mapboxToken);
  };

  useEffect(() => {
    if (!user) {
      navigate("/");
    }
  }, [user, navigate]);

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
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-heat via-primary to-cool-intense bg-clip-text text-transparent">
              HeatQuest
            </h1>
            <p className="text-sm text-muted-foreground">
              Hallo, {user?.username}! 👋
            </p>
          </div>
          <Button
            onClick={() => navigate("/analyze")}
            className="rounded-2xl bg-gradient-to-r from-heat to-primary hover:from-heat-intense hover:to-heat shadow-lg"
          >
            <Camera className="w-5 h-5 mr-2" />
            Analysieren
          </Button>
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
