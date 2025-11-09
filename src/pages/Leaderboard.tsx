import { Trophy } from 'lucide-react';
import BottomNav from '../components/BottomNav';

const mockLeaderboard = [
  { rank: 1, username: 'EcoWarrior', avatar: '👨', points: 2500, level: 6, missions: 25 },
  { rank: 2, username: 'GreenHero', avatar: '👨', points: 2100, level: 5, missions: 21 },
  { rank: 3, username: 'ClimateChamp', avatar: '👨', points: 1800, level: 4, missions: 18 },
  { rank: 4, username: 'CoolCrusader', avatar: '👨', points: 1500, level: 4, missions: 15 },
];

const Leaderboard = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary via-primary/80 to-secondary pb-20">
      <div className="container mx-auto px-4 py-8 max-w-lg">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Trophy className="w-8 h-8 text-white" />
            <h1 className="text-3xl font-bold text-white">Rangliste</h1>
          </div>
          <p className="text-white/80">Die Top Climate Warriors</p>
        </div>

        {/* Leaderboard List */}
        <div className="space-y-3">
          {mockLeaderboard.map((player) => (
            <div
              key={player.rank}
              className="bg-white rounded-2xl p-4 shadow-lg"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  <div className="relative">
                    {player.rank <= 3 && (
                      <div className="absolute -top-2 -left-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center text-white text-xs font-bold">
                        {player.rank === 1 ? '🏆' : player.rank === 2 ? '🥈' : '🥉'}
                      </div>
                    )}
                    <div className="w-14 h-14 bg-primary rounded-full flex items-center justify-center text-2xl">
                      {player.avatar}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-lg">
                      {player.username}
                    </div>
                    <div className="text-muted-foreground text-sm">
                      Level {player.level} • {player.missions} Missionen
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary">
                    {player.points}
                  </div>
                  <div className="text-muted-foreground text-sm">XP</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default Leaderboard;
