import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useGame } from "@/contexts/GameContext";
import { ArrowLeft, MapPin } from "lucide-react";

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
      return;
    }

    completeMission(mission.id);
    navigate("/profile");
  };

  const allActionsChecked = checkedActions.size === mission.actions.length;

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <motion.div
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="bg-gradient-to-r from-heat via-primary to-cool-intense p-6 pb-12"
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
          </div>
        </div>
      </motion.div>

      <div className="max-w-2xl mx-auto px-4 -mt-6 space-y-4">
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
          <h2 className="font-semibold mb-3">Why is it so hot here? 🔥</h2>
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
          <h2 className="font-semibold mb-3">Your Actions ✅</h2>
          <div className="space-y-3">
            {mission.actions.map((action, i) => {
              // Handle both string and object format for backwards compatibility
              const actionText = typeof action === 'string' ? action : action.action;
              const actionDescription = typeof action === 'object' && action.description ? action.description : '';
              const actionPriority = typeof action === 'object' && action.priority ? action.priority : 'medium';
              
              // Priority badge colors
              const priorityColors = {
                high: 'bg-red-500/20 text-red-600 border-red-500/30',
                medium: 'bg-yellow-500/20 text-yellow-600 border-yellow-500/30',
                low: 'bg-blue-500/20 text-blue-600 border-blue-500/30'
              };
              
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-start gap-3 p-4 bg-muted/50 rounded-xl hover:bg-muted transition-colors cursor-pointer border border-transparent hover:border-primary/20"
                  onClick={() => toggleAction(i)}
                >
                  <Checkbox
                    checked={checkedActions.has(i)}
                    onCheckedChange={() => toggleAction(i)}
                    className="mt-1"
                  />
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{actionText}</span>
                      {typeof action === 'object' && action.priority && (
                        <span className={`text-xs px-2 py-0.5 rounded-full border ${priorityColors[actionPriority as keyof typeof priorityColors]}`}>
                          {actionPriority}
                        </span>
                      )}
                    </div>
                    {actionDescription && (
                      <p className="text-xs text-muted-foreground">{actionDescription}</p>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </Card>

        {/* Complete Button */}
        <Button
          onClick={handleComplete}
          disabled={mission.completed || checkedActions.size === 0}
          className="w-full h-14 text-lg rounded-2xl bg-gradient-to-r from-heat via-primary to-cool-intense hover:shadow-xl transition-all"
        >
          {mission.completed ? (
            "✅ Mission Completed"
          ) : allActionsChecked ? (
            "🎉 Complete Mission (+100 XP)"
          ) : (
            `Complete Mission (${checkedActions.size}/${mission.actions.length})`
          )}
        </Button>
      </div>
    </div>
  );
};

export default MissionDetail;
