import { useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useGame } from "@/contexts/GameContext";
import { useNavigate } from "react-router-dom";
import BottomNav from "@/components/BottomNav";
import { Camera, MapPin } from "lucide-react";

const MapView = () => {
  const { missions, setActiveMission, user } = useGame();
  const navigate = useNavigate();

  const openMissions = missions.filter((m) => !m.completed);

  const handleMissionClick = (mission: any) => {
    setActiveMission(mission);
    navigate(`/mission/${mission.id}`);
  };

  return (
    <div className="relative min-h-screen bg-background pb-20">
      {/* Header */}
      <motion.div
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="bg-gradient-to-b from-card/95 to-transparent backdrop-blur-sm p-4"
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

      {/* Map Area Placeholder */}
      <div className="relative h-[50vh] bg-gradient-to-br from-muted via-background to-muted/50 flex items-center justify-center">
        <div className="text-center space-y-4 p-8">
          <MapPin className="w-16 h-16 mx-auto text-primary animate-bounce" />
          <h2 className="text-2xl font-bold">Karte wird geladen...</h2>
          <p className="text-muted-foreground">Deine Missionen werden hier angezeigt</p>
        </div>
      </div>

      {/* Missions List */}
      <div className="max-w-2xl mx-auto p-4 space-y-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          🎯 Offene Missionen ({openMissions.length})
        </h2>

        {openMissions.length === 0 ? (
          <Card className="p-6 text-center">
            <p className="text-muted-foreground">
              Keine Missionen verfügbar. Erstelle eine neue durch Analyse!
            </p>
          </Card>
        ) : (
          openMissions.map((mission, i) => (
            <motion.div
              key={mission.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card
                onClick={() => handleMissionClick(mission)}
                className="p-4 cursor-pointer hover:shadow-lg transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-heat to-primary flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">🔥</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold">{mission.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {mission.description}
                    </p>
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex-1 bg-muted rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-heat to-heat-intense h-full rounded-full"
                          style={{ width: `${mission.heatRisk}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold text-heat">
                        {mission.heatRisk}%
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))
        )}
      </div>

      <BottomNav />
    </div>
  );
};

export default MapView;
