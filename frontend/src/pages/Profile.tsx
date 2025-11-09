import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useGame } from "@/contexts/GameContext";
import { useNavigate } from "react-router-dom";
import BottomNav from "@/components/BottomNav";
import { Trophy, Target, Flame, LogOut } from "lucide-react";
import { useI18n } from "@/contexts/I18nContext";

const Profile = () => {
  const { user, missions, logout } = useGame();
  const navigate = useNavigate();
  const { t } = useI18n();

  const completedMissions = missions.filter((m) => m.completed);
  const activeMissions = missions.filter((m) => !m.completed);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const xpToNextLevel = user ? (user.level + 1) * 500 - user.xp : 0;
  const xpProgress = user ? (user.xp % 500) / 500 : 0;

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <motion.div
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="bg-gradient-to-r from-heat via-primary to-cool-intense p-6"
      >
        <div className="max-w-2xl mx-auto text-white">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold">{t("profile")}</h1>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="rounded-full text-white hover:bg-white/20"
            >
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-4xl">
              👤
            </div>
            <div>
              <p className="text-2xl font-bold">{user?.username}</p>
              <p className="text-white/90">{t("level_label")} {user?.level}</p>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="max-w-2xl mx-auto p-4 space-y-6 -mt-8">
        {/* XP Progress */}
        <Card className="p-6 rounded-3xl bg-card/95 backdrop-blur-sm shadow-xl">
          <div className="flex items-center gap-3 mb-3">
            <Flame className="w-6 h-6 text-primary" />
            <div className="flex-1">
              <p className="text-sm text-muted-foreground">{t("experience_points")}</p>
              <p className="text-2xl font-bold">{user?.xp} {t("xp_label")}</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">{t("until_level", { next: (user?.level || 0) + 1 })}</span>
              <span className="font-semibold">{xpToNextLevel} XP</span>
            </div>
            <div className="h-3 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-heat to-primary transition-all duration-500"
                style={{ width: `${xpProgress * 100}%` }}
              />
            </div>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <Card className="p-6 rounded-3xl text-center">
            <Trophy className="w-8 h-8 mx-auto mb-2 text-primary" />
            <p className="text-3xl font-bold">{completedMissions.length}</p>
            <p className="text-sm text-muted-foreground">{t("completed_label")}</p>
          </Card>
          <Card className="p-6 rounded-3xl text-center">
            <Target className="w-8 h-8 mx-auto mb-2 text-secondary" />
            <p className="text-3xl font-bold">{activeMissions.length}</p>
            <p className="text-sm text-muted-foreground">{t("active_missions_label")}</p>
          </Card>
        </div>

        {/* Missions Lists */}
        {completedMissions.length > 0 && (
          <Card className="p-6 rounded-3xl">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-primary" />
              {t("completed_missions_label")}
            </h2>
            <div className="space-y-3">
              {completedMissions.map((mission, i) => (
                <motion.div
                  key={mission.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center gap-3 p-3 bg-muted/50 rounded-xl"
                >
                  <span className="text-2xl">✅</span>
                  <div className="flex-1">
                    <p className="font-medium">{mission.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {mission.heatRisk}% {t("heat_risk")}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
        )}

        {activeMissions.length > 0 && (
          <Card className="p-6 rounded-3xl">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-secondary" />
              {t("active_missions_label")}
            </h2>
            <div className="space-y-3">
              {activeMissions.map((mission, i) => (
                <motion.div
                  key={mission.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  onClick={() => navigate(`/mission/${mission.id}`)}
                  className="flex items-center gap-3 p-3 bg-muted/50 rounded-xl cursor-pointer hover:bg-muted transition-colors"
                >
                  <span className="text-2xl">🚩</span>
                  <div className="flex-1">
                    <p className="font-medium">{mission.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {mission.heatRisk}% {t("heat_risk")}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>
        )}
      </div>

      <BottomNav />
    </div>
  );
};

export default Profile;
