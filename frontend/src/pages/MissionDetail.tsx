import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useGame } from "@/contexts/GameContext";
import {
  ArrowLeft,
  MapPin,
  CheckCircle2,
  Flame,
  Sparkles,
  Target,
  Clock,
  FileText,
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

export default function MissionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { missions, completeMission } = useGame();

  const mission = useMemo(() => missions.find((m) => m.id === id), [missions, id]);

  useEffect(() => {
    if (!mission) navigate("/map");
  }, [mission, navigate]);

  const [checkedActions, setCheckedActions] = useState<Set<number>>(new Set());

  if (!mission) return null;

  const toggleAction = (index: number) => {
    setCheckedActions((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const completionPercentage = (checkedActions.size / mission.actions.length) * 100;
  const estMinutes = mission.timeMinutes || 15;

  const handleComplete = () => {
    if (checkedActions.size === 0) {
      toast({ title: "Select at least one action", description: "Pick actions you completed." });
      return;
    }
    completeMission(mission.id);
    toast({ title: "Mission completed!", description: "Great job reducing heat here." });
    navigate("/map");
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <Button variant="ghost" onClick={() => navigate(-1)} className="gap-2">
          <ArrowLeft className="h-4 w-4" /> Back
        </Button>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MapPin className="h-4 w-4" /> Unknown location
        </div>
      </div>

      {/* Title and heat badge */}
      <Card className="p-6 rounded-3xl mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">{mission.title}</h1>
            <p className="text-sm text-muted-foreground">{mission.description}</p>
          </div>
          <div className="flex items-center gap-2 text-heat">
            <Flame className="h-5 w-5" />
            <span className="text-sm">{mission.riskLevel || 78}%</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
            <span>Completion</span>
            <span>{Math.min(100, Math.round(completionPercentage))}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-gradient-to-r from-primary via-heat to-cool-intense"
              style={{ width: `${Math.min(100, Math.round(completionPercentage))}%` }}
            />
          </div>
        </div>
      </Card>

      {/* Compact stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Card className="p-3 rounded-2xl text-center">
          <div className="flex items-center justify-center gap-1 text-sm">
            <Sparkles className="h-4 w-4" />
            <span>+{mission.rewardXp || 100} XP</span>
          </div>
        </Card>
        <Card className="p-3 rounded-2xl text-center">
          <div className="flex items-center justify-center gap-1 text-sm">
            <Target className="h-4 w-4" />
            <span>{mission.actions.length} steps</span>
          </div>
        </Card>
        <Card className="p-3 rounded-2xl text-center">
          <div className="flex items-center justify-center gap-1 text-sm">
            <Clock className="h-4 w-4" />
            <span>{estMinutes} min</span>
          </div>
        </Card>
      </div>

      {/* Main content */}
      <div className="grid gap-4">
        <Card className="p-6 rounded-3xl">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-4 w-4" />
            <h2 className="font-semibold">Context</h2>
          </div>
          <p className="text-sm text-muted-foreground">{mission.context}</p>
        </Card>

        <Card className="p-6 rounded-3xl">
          <h2 className="font-semibold mb-3">Actions</h2>
          <div className="space-y-3">
            {mission.actions.map((action, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
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
      </div>

      {/* Footer action */}
      <div className="mt-6">
        <Button
          className="w-full rounded-2xl h-12 text-base gap-2"
          onClick={handleComplete}
          disabled={checkedActions.size === 0}
        >
          <CheckCircle2 className="h-5 w-5" /> Complete Mission
        </Button>
      </div>
    </div>
  );
}