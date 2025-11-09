import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useGame } from "@/contexts/GameContext";
import { ArrowLeft, MapPin, Flame } from "lucide-react";

const MissionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { missions, completeMission } = useGame();
  const [checkedActions, setCheckedActions] = useState<Set<number>>(new Set());

  const mission = missions.find((m) => m.id === id);

  if (!mission) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Mission nicht gefunden</p>
      </div>
    );
  }

  const handleActionToggle = (index: number) => {
    const newChecked = new Set(checkedActions);
    if (newChecked.has(index)) {
      newChecked.delete(index);
    } else {
      newChecked.add(index);
    }
    setCheckedActions(newChecked);
  };

  const handleComplete = () => {
    completeMission(mission.id);
    navigate("/map");
  };

  const allActionsChecked =
    checkedActions.size === mission.actions.length && mission.actions.length > 0;

  return (
    <div className="min-h-screen bg-background pb-20">
      <motion.div
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="sticky top-0 z-10 bg-card/95 backdrop-blur-sm border-b border-border p-4"
      >
        <div className="flex items-center gap-4 max-w-2xl mx-auto">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="rounded-full"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-xl font-bold">{mission.title}</h1>
            <p className="text-sm text-muted-foreground">{mission.description}</p>
          </div>
        </div>
      </motion.div>

      <div className="max-w-2xl mx-auto p-4 space-y-6">
        <Card className="p-6 rounded-3xl">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <MapPin className="w-6 h-6 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Standort</p>
                <p className="font-semibold">
                  {mission.lat.toFixed(4)}, {mission.lng.toFixed(4)}
                </p>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Flame className="w-5 h-5 text-heat" />
                  <span className="font-semibold">Heat Risk Score</span>
                </div>
                <span className="text-2xl font-bold text-heat">
                  {mission.heatRisk}%
                </span>
              </div>
              <div className="h-3 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-heat to-heat-intense transition-all"
                  style={{ width: `${mission.heatRisk}%` }}
                />
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6 rounded-3xl">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            🔥 Gründe für die Hitzebelastung
          </h3>
          <ul className="space-y-2">
            {mission.reasons.map((reason, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-muted-foreground"
              >
                <span className="text-heat mt-0.5">•</span>
                {reason}
              </li>
            ))}
          </ul>
        </Card>

        <Card className="p-6 rounded-3xl">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            ✅ Vorgeschlagene Aktionen
          </h3>
          <div className="space-y-3">
            {mission.actions.map((action, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-3 bg-muted/50 rounded-xl cursor-pointer hover:bg-muted transition-colors"
                onClick={() => handleActionToggle(i)}
              >
                <Checkbox
                  checked={checkedActions.has(i)}
                  onCheckedChange={() => handleActionToggle(i)}
                  className="mt-0.5"
                />
                <span className="flex-1 text-sm">{action}</span>
              </div>
            ))}
          </div>
        </Card>

        {!mission.completed && (
          <Button
            onClick={handleComplete}
            disabled={!allActionsChecked}
            className="w-full h-12 rounded-2xl bg-gradient-to-r from-heat via-primary to-cool-intense hover:shadow-lg disabled:opacity-50"
          >
            {allActionsChecked
              ? "🎉 Mission abschließen (+100 XP)"
              : "Alle Aktionen abhaken zum Abschließen"}
          </Button>
        )}

        {mission.completed && (
          <Card className="p-6 rounded-3xl bg-gradient-to-r from-primary/10 to-secondary/10 border-2 border-primary">
            <div className="text-center">
              <span className="text-4xl mb-2 block">✅</span>
              <p className="font-bold text-primary">Mission abgeschlossen!</p>
              <p className="text-sm text-muted-foreground mt-1">
                Gut gemacht! Du hast 100 XP verdient.
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default MissionDetail;
