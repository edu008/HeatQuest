import { Link } from 'react-router-dom';
import { Home, Trophy, Medal, Award } from 'lucide-react';

const mockLeaderboard = [
  { rank: 1, username: 'HeatHunter', points: 5280, level: 12, missions: 45 },
  { rank: 2, username: 'CoolExplorer', points: 4850, level: 11, missions: 42 },
  { rank: 3, username: 'TempTracker', points: 4320, level: 10, missions: 38 },
  { rank: 4, username: 'UrbanScout', points: 3890, level: 9, missions: 35 },
  { rank: 5, username: 'HeatSeeker', points: 3560, level: 9, missions: 32 },
  { rank: 6, username: 'ClimateHero', points: 3240, level: 8, missions: 29 },
  { rank: 7, username: 'ThermalFinder', points: 2980, level: 8, missions: 27 },
  { rank: 8, username: 'HotspotPro', points: 2750, level: 7, missions: 25 },
];

const getRankIcon = (rank: number) => {
  switch (rank) {
    case 1:
      return <Trophy className="w-6 h-6 text-yellow-400" />;
    case 2:
      return <Medal className="w-6 h-6 text-gray-400" />;
    case 3:
      return <Award className="w-6 h-6 text-amber-700" />;
    default:
      return <span className="text-white font-bold">#{rank}</span>;
  }
};

const Leaderboard = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <Link
            to="/"
            className="bg-white rounded-lg p-3 shadow-lg hover:bg-gray-100 transition-colors"
          >
            <Home className="w-6 h-6" />
          </Link>
          <h1 className="text-3xl font-bold text-white">🏆 Rangliste</h1>
          <div className="w-12"></div>
        </div>

        {/* Top 3 Podium */}
        <div className="grid grid-cols-3 gap-4 mb-8 max-w-2xl mx-auto">
          {/* 2nd Place */}
          <div className="mt-8">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center">
              <Medal className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <div className="text-white font-bold text-lg mb-1">
                {mockLeaderboard[1].username}
              </div>
              <div className="text-white/80 text-sm">
                {mockLeaderboard[1].points} XP
              </div>
            </div>
          </div>

          {/* 1st Place */}
          <div className="transform scale-110">
            <div className="bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl p-4 border-2 border-yellow-300 text-center shadow-2xl">
              <Trophy className="w-16 h-16 text-white mx-auto mb-2" />
              <div className="text-white font-bold text-xl mb-1">
                {mockLeaderboard[0].username}
              </div>
              <div className="text-white/90 text-sm">
                {mockLeaderboard[0].points} XP
              </div>
            </div>
          </div>

          {/* 3rd Place */}
          <div className="mt-8">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center">
              <Award className="w-12 h-12 text-amber-700 mx-auto mb-2" />
              <div className="text-white font-bold text-lg mb-1">
                {mockLeaderboard[2].username}
              </div>
              <div className="text-white/80 text-sm">
                {mockLeaderboard[2].points} XP
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard List */}
        <div className="space-y-3 max-w-2xl mx-auto">
          {mockLeaderboard.map((player) => (
            <div
              key={player.rank}
              className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 hover:bg-white/20 transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                    {getRankIcon(player.rank)}
                  </div>
                  <div className="flex-1">
                    <div className="text-white font-bold text-lg">
                      {player.username}
                    </div>
                    <div className="text-white/70 text-sm">
                      Level {player.level} • {player.missions} Missionen
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">
                    {player.points}
                  </div>
                  <div className="text-white/70 text-sm">XP</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
