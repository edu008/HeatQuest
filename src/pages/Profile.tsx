import { Link } from 'react-router-dom';
import { Home, MapPin, Target, Trophy, TrendingUp } from 'lucide-react';

const Profile = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-500 via-teal-500 to-blue-500">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <Link
            to="/"
            className="bg-white rounded-lg p-3 shadow-lg hover:bg-gray-100 transition-colors"
          >
            <Home className="w-6 h-6" />
          </Link>
          <h1 className="text-3xl font-bold text-white">👤 Profil</h1>
          <div className="w-12"></div>
        </div>

        {/* Profile Card */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 mb-8">
          <div className="flex flex-col items-center text-center mb-6">
            <div className="w-24 h-24 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-4xl mb-4 shadow-lg">
              🔥
            </div>
            <h2 className="text-3xl font-bold text-white mb-2">HeatExplorer</h2>
            <p className="text-white/80 mb-4">Level 8 • Explorer</p>
            <div className="flex gap-4 text-sm">
              <span className="bg-white/20 px-4 py-2 rounded-full text-white">
                Rang #15
              </span>
              <span className="bg-white/20 px-4 py-2 rounded-full text-white">
                2.850 XP
              </span>
            </div>
          </div>

          {/* Level Progress */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-white/80 mb-2">
              <span>Fortschritt Level 9</span>
              <span>2.850 / 3.200 XP</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-green-400 to-blue-500 h-full transition-all"
                style={{ width: '89%' }}
              ></div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 rounded-xl p-4 text-center border border-white/20">
              <MapPin className="w-8 h-8 text-white mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">28</div>
              <div className="text-sm text-white/80">Entdeckungen</div>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center border border-white/20">
              <Target className="w-8 h-8 text-white mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">23</div>
              <div className="text-sm text-white/80">Missionen</div>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center border border-white/20">
              <Trophy className="w-8 h-8 text-white mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">12</div>
              <div className="text-sm text-white/80">Erfolge</div>
            </div>
            <div className="bg-white/10 rounded-xl p-4 text-center border border-white/20">
              <TrendingUp className="w-8 h-8 text-white mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">85%</div>
              <div className="text-sm text-white/80">Genauigkeit</div>
            </div>
          </div>
        </div>

        {/* Recent Achievements */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">🏅 Erfolge</h3>
          <div className="space-y-3">
            <div className="bg-white/10 rounded-lg p-4 flex items-center gap-4">
              <div className="text-3xl">🔥</div>
              <div className="flex-1">
                <div className="font-bold text-white">Hitzejäger</div>
                <div className="text-sm text-white/70">
                  Entdecke 25 Hotspots
                </div>
              </div>
              <div className="text-yellow-400 font-bold">+200 XP</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4 flex items-center gap-4">
              <div className="text-3xl">🌡️</div>
              <div className="flex-1">
                <div className="font-bold text-white">Temperatur-Tracker</div>
                <div className="text-sm text-white/70">
                  Erfasse 50 Temperaturen
                </div>
              </div>
              <div className="text-yellow-400 font-bold">+150 XP</div>
            </div>
            <div className="bg-white/10 rounded-lg p-4 flex items-center gap-4 opacity-50">
              <div className="text-3xl">🎯</div>
              <div className="flex-1">
                <div className="font-bold text-white">Mission Master</div>
                <div className="text-sm text-white/70">
                  Schließe 50 Missionen ab
                </div>
              </div>
              <div className="text-white/50">23/50</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
