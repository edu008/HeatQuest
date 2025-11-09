import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { useGame } from "@/contexts/GameContext";
import BottomNav from "@/components/BottomNav";
import { Trophy, Medal, Award } from "lucide-react";
import { useI18n } from "@/contexts/I18nContext";

// Mock leaderboard data
const mockPlayers = [
  { username: "EcoWarrior", xp: 2500, level: 6, missions: 25 },
  { username: "GreenHero", xp: 2100, level: 5, missions: 21 },
  { username: "ClimateChamp", xp: 1800, level: 4, missions: 18 },
  { username: "CoolCrusader", xp: 1500, level: 4, missions: 15 },
  { username: "HeatHunter", xp: 1200, level: 3, missions: 12 },
];

const Leaderboard = () => {
  const { user } = useGame();
  const { t } = useI18n();

  const allPlayers = user
    ? [
        ...mockPlayers,
        {
          username: user.username,
          xp: user.xp,
          level: user.level,
          missions: user.completedMissions,
        },
      ].sort((a, b) => b.xp - a.xp)
    : mockPlayers;

  const getIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-6 h-6 text-yellow-500" />;
      case 2:
        return <Medal className="w-6 h-6 text-gray-400" />;
      case 3:
        return <Award className="w-6 h-6 text-amber-600" />;
      default:
        return <span className="w-6 text-center font-bold text-muted-foreground">#{rank}</span>;
    }
  };

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header */}
      <motion.div
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="bg-gradient-to-r from-heat via-primary to-cool-intense p-6"
      >
        <div className="max-w-2xl mx-auto text-white">
          <h1 className="text-3xl font-bold mb-2">🏆 {t("leaderboard_title")}</h1>
          <p className="text-white/90">{t("leaderboard_subtitle")}</p>
        </div>
      </motion.div>

      <div className="max-w-2xl mx-auto p-4 space-y-4 -mt-8">
        {allPlayers.map((player, index) => {
          const rank = index + 1;
          const isCurrentUser = player.username === user?.username;

          return (
            <motion.div
              key={player.username}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card
                className={`p-4 rounded-3xl ${
                  isCurrentUser
                    ? "bg-gradient-to-r from-primary/10 to-secondary/10 border-2 border-primary"
                    : "bg-card"
                }`}
              >
                <div className="flex items-center gap-4">
                  {/* Rank */}
                  <div className="flex items-center justify-center w-12">
                    {getIcon(rank)}
                  </div>

                  {/* Avatar */}
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-heat to-primary flex items-center justify-center text-2xl">
                    {isCurrentUser ? "👤" : "🧑"}
                  </div>

                  {/* Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-bold">
                        {player.username}
                        {isCurrentUser && (
                          <span className="ml-2 text-xs bg-primary text-white px-2 py-1 rounded-full">
                            {t("you")}
                          </span>
                        )}
                      </p>
                    </div>
                    <div className="flex gap-4 text-sm text-muted-foreground mt-1">
                      <span>{t("level_label")} {player.level}</span>
                      <span>•</span>
                      <span>{player.missions} {t("missions_label")}</span>
                    </div>
                  </div>

                  {/* XP */}
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary">
                      {player.xp}
                    </p>
                    <p className="text-xs text-muted-foreground">{t("xp_label")}</p>
                  </div>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <BottomNav />
    </div>
  );
};

export default Leaderboard;
