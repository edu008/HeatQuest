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

      {/* Temporary Map Placeholder - Proof of Concept */}
      <div className="flex-1 bg-muted p-4 overflow-y-auto">
        <div className="max-w-2xl mx-auto space-y-4">
          <div className="text-center py-8">
            <MapPin className="w-16 h-16 mx-auto mb-4 text-primary" />
            <h2 className="text-xl font-bold mb-2">Deine Missionen</h2>
            <p className="text-sm text-muted-foreground">
              Proof of Concept - Kartenansicht kommt später
            </p>
          </div>

          <div className="grid gap-4">
            {missions.map((mission) => (
              <Card
                key={mission.id}
                className="p-4 rounded-3xl cursor-pointer hover:shadow-lg transition-all"
                onClick={() => handleMissionClick(mission)}
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-heat to-heat-intense flex items-center justify-center text-2xl flex-shrink-0">
                    {mission.completed ? "✅" : "🚩"}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-lg mb-1">{mission.title}</h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      {mission.description}
                    </p>
                    <div className="flex items-center gap-2 mb-2">
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
                    <Button
                      size="sm"
                      disabled={mission.completed}
                      className="rounded-xl"
                    >
                      {mission.completed ? "Abgeschlossen" : "Mission starten"}
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default MapView;
