import { Link } from 'react-router-dom';
import { Home, MapPin, CheckCircle, Clock } from 'lucide-react';

const mockMissions = [
  {
    id: 1,
    title: 'Hotspot Scanner',
    description: 'Scanne 3 Hitzeinsel-Hotspots in deiner Nähe',
    points: 150,
    status: 'active',
    progress: 2,
    total: 3,
    location: 'Wien Innere Stadt',
  },
  {
    id: 2,
    title: 'Temperatur-Tracker',
    description: 'Erfasse Temperaturdaten an 5 verschiedenen Orten',
    points: 200,
    status: 'active',
    progress: 1,
    total: 5,
    location: 'Wien',
  },
  {
    id: 3,
    title: 'Grünoasen-Finder',
    description: 'Finde 2 kühlende Grünflächen',
    points: 100,
    status: 'completed',
    progress: 2,
    total: 2,
    location: 'Prater',
  },
];

const Missions = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <Link
            to="/"
            className="bg-white rounded-lg p-3 shadow-lg hover:bg-gray-100 transition-colors"
          >
            <Home className="w-6 h-6" />
          </Link>
          <h1 className="text-3xl font-bold text-white">🎯 Missionen</h1>
          <div className="w-12"></div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 text-center border border-white/20">
            <div className="text-3xl font-bold text-white">5</div>
            <div className="text-sm text-white/80">Aktiv</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 text-center border border-white/20">
            <div className="text-3xl font-bold text-white">12</div>
            <div className="text-sm text-white/80">Abgeschlossen</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 text-center border border-white/20">
            <div className="text-3xl font-bold text-white">1850</div>
            <div className="text-sm text-white/80">Punkte</div>
          </div>
        </div>

        {/* Missions List */}
        <div className="space-y-4">
          {mockMissions.map((mission) => (
            <div
              key={mission.id}
              className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-bold text-white">
                      {mission.title}
                    </h3>
                    {mission.status === 'completed' ? (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : (
                      <Clock className="w-5 h-5 text-yellow-400" />
                    )}
                  </div>
                  <p className="text-white/80 mb-3">{mission.description}</p>
                  <div className="flex items-center gap-2 text-sm text-white/70">
                    <MapPin className="w-4 h-4" />
                    <span>{mission.location}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full font-bold text-sm">
                    +{mission.points} XP
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mt-4">
                <div className="flex justify-between text-sm text-white/80 mb-2">
                  <span>Fortschritt</span>
                  <span>
                    {mission.progress}/{mission.total}
                  </span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-green-400 to-blue-500 h-full transition-all"
                    style={{
                      width: `${(mission.progress / mission.total) * 100}%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Missions;
