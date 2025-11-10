import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import BottomNav from "@/components/BottomNav";
import { Trophy, Medal, Award } from "lucide-react";

interface LeaderboardPlayer {
  id: string;
  username: string;
  avatar_url?: string;
  points: number;
  level: number;
  missions_completed: number;
}

const Leaderboard = () => {
  const { user: authUser, profile } = useAuth();
  const [players, setPlayers] = useState<LeaderboardPlayer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/leaderboard`);
      
      if (response.ok) {
        const data = await response.json();
        setPlayers(data.leaderboard || []);
      } else {
        console.error('Failed to load leaderboard');
      }
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

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
          <h1 className="text-3xl font-bold mb-2">🏆 Leaderboard</h1>
          <p className="text-white/90">Top Climate Warriors</p>
        </div>
      </motion.div>

      <div className="max-w-2xl mx-auto p-4 space-y-4 -mt-8">
        {loading ? (
          <Card className="p-8 rounded-3xl text-center">
            <p className="text-muted-foreground">Loading leaderboard...</p>
          </Card>
        ) : players.length === 0 ? (
          <Card className="p-8 rounded-3xl text-center">
            <p className="text-muted-foreground">No players yet</p>
          </Card>
        ) : (
          players.map((player, index) => {
            const rank = index + 1;
            const isCurrentUser = player.id === authUser?.id;

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
                  {player.avatar_url ? (
                    <img 
                      src={player.avatar_url} 
                      alt={player.username}
                      className="w-14 h-14 rounded-full border-2 border-primary/30"
                    />
                  ) : (
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-heat to-primary flex items-center justify-center text-2xl">
                      {isCurrentUser ? "👤" : "🧑"}
                    </div>
                  )}

                  {/* Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-bold">
                        {player.username}
                        {isCurrentUser && (
                          <span className="ml-2 text-xs bg-primary text-white px-2 py-1 rounded-full">
                            You
                          </span>
                        )}
                      </p>
                    </div>
                    <div className="flex gap-4 text-sm text-muted-foreground mt-1">
                      <span>Level {player.level}</span>
                      <span>•</span>
                      <span>{player.missions_completed} Missions</span>
                    </div>
                  </div>

                  {/* Points */}
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary">
                      {player.points}
                    </p>
                    <p className="text-xs text-muted-foreground">pts</p>
                  </div>
                </div>
              </Card>
            </motion.div>
            );
          })
        )}
      </div>

      <BottomNav />
    </div>
  );
};

export default Leaderboard;
