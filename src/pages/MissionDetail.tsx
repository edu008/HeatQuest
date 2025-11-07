import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useGame } from "@/contexts/GameContext";
import { ArrowLeft, MapPin } from "lucide-react";
import { toast } from "sonner";

const MissionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { missions, completeMission } = useGame();
  const [checkedActions, setCheckedActions] = useState<Set<number>>(new Set());

  const mission = missions.find((m) => m.id === id);

  useEffect(() => {
    if (!mission) {
      navigate("/map");
    }
  }, [mission, navigate]);

  if (!mission) return null;

  const toggleAction = (index: number) => {
    const newChecked = new Set(checkedActions);
    if (newChecked.has(index)) {
      newChecked.delete(index);
    } else {
      newChecked.add(index);
    }
    setCheckedActions(newChecked);
  };

  const handleComplete = () => {
    if (checkedActions.size === 0) {
      toast.error("Bitte wähle mindestens eine Aktion aus!");
      return;
    }

    completeMission(mission.id);
    toast.success("Mission abgeschlossen! 🎉 +100 XP");
    navigate("/profile");
  };

  const allActionsChecked = checkedActions.size === mission.actions.length;

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <motion.div
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="sticky top-0 z-10 bg-gradient-to-r from-heat via-primary to-cool-intense p-4"
      >
        <div className="max-w-2xl mx-auto">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
            className="rounded-full text-white hover:bg-white/20 mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="text-white">
            <h1 className="text-2xl font-bold">{mission.title}</h1>
            <p className="text-white/90 flex items-center gap-2 mt-1">
              <MapPin className="w-4 h-4" />
              {mission.description}
            </p>
          </div>
        </div>
      </motion.div>

      <div className="max-w-2xl mx-auto p-4 space-y-6 -mt-8">
        {/* Heat Risk Card */}
        <Card className="p-6 rounded-3xl bg-card/95 backdrop-blur-sm shadow-xl">
          <h2 className="font-semibold mb-3">Heat Risk Level</h2>
          <div className="flex items-center gap-3">
            <div className="flex-1 bg-muted rounded-full h-4">
              <div
                className="bg-gradient-to-r from-heat to-heat-intense h-full rounded-full transition-all animate-pulse-glow"
                style={{ width: `${mission.heatRisk}%` }}
              />
            </div>
            <span className="text-3xl font-bold text-heat">
              {mission.heatRisk}%
            </span>
          </div>
        </Card>

        {/* Reasons */}
        <Card className="p-6 rounded-3xl">
          <h2 className="font-semibold mb-3">Warum ist es hier heiß? 🔥</h2>
          <ul className="space-y-3">
            {mission.reasons.map((reason, i) => (
              <motion.li
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start gap-3 p-3 bg-muted/50 rounded-xl"
              >
                <span className="text-heat text-xl">🔥</span>
                <span className="flex-1 text-sm">{reason}</span>
              </motion.li>
            ))}
          </ul>
        </Card>

        {/* Actions Checklist */}
        <Card className="p-6 rounded-3xl">
          <h2 className="font-semibold mb-3">Deine Aktionen ✅</h2>
          <div className="space-y-3">
            {mission.actions.map((action, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-start gap-3 p-3 bg-muted/50 rounded-xl hover:bg-muted transition-colors cursor-pointer"
                onClick={() => toggleAction(i)}
              >
                <Checkbox
                  checked={checkedActions.has(i)}
                  onCheckedChange={() => toggleAction(i)}
                  className="mt-1"
                />
                <span className="flex-1 text-sm">{action}</span>
              </motion.div>
            ))}
          </div>
        </Card>

        {/* Complete Button */}
        <Button
          onClick={handleComplete}
          disabled={mission.completed || checkedActions.size === 0}
          className="w-full h-14 text-lg rounded-2xl bg-gradient-to-r from-heat via-primary to-cool-intense hover:shadow-xl transition-all"
        >
          {mission.completed ? (
            "✅ Mission abgeschlossen"
          ) : allActionsChecked ? (
            "🎉 Mission abschließen (+100 XP)"
          ) : (
            `Mission abschließen (${checkedActions.size}/${mission.actions.length})`
          )}
        </Button>
      </div>
    </div>
  );
};

export default MissionDetail;
