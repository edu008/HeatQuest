import { Link } from 'react-router-dom';
import { MapPin, Target, Trophy, User } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-500 via-red-500 to-pink-500">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-lg">
            🔥 HeatQuest
          </h1>
          <p className="text-xl text-white/90 max-w-2xl mx-auto">
            Entdecke urbane Hitzeinseln und hilf mit, deine Stadt kühler zu machen!
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <Link
            to="/map"
            className="bg-white/10 backdrop-blur-md hover:bg-white/20 rounded-2xl p-8 transition-all hover:scale-105 border border-white/20"
          >
            <MapPin className="w-12 h-12 text-white mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Karte</h2>
            <p className="text-white/80">
              Erkunde Hitzeinsel-Hotspots in deiner Umgebung
            </p>
          </Link>

          <Link
            to="/missions"
            className="bg-white/10 backdrop-blur-md hover:bg-white/20 rounded-2xl p-8 transition-all hover:scale-105 border border-white/20"
          >
            <Target className="w-12 h-12 text-white mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Missionen</h2>
            <p className="text-white/80">
              Erfülle Aufgaben und sammle Punkte
            </p>
          </Link>

          <Link
            to="/leaderboard"
            className="bg-white/10 backdrop-blur-md hover:bg-white/20 rounded-2xl p-8 transition-all hover:scale-105 border border-white/20"
          >
            <Trophy className="w-12 h-12 text-white mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Rangliste</h2>
            <p className="text-white/80">
              Vergleiche dich mit anderen Explorern
            </p>
          </Link>

          <Link
            to="/profile"
            className="bg-white/10 backdrop-blur-md hover:bg-white/20 rounded-2xl p-8 transition-all hover:scale-105 border border-white/20"
          >
            <User className="w-12 h-12 text-white mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Profil</h2>
            <p className="text-white/80">
              Verwalte dein Konto und deine Erfolge
            </p>
          </Link>
        </div>

        <div className="mt-16 text-center">
          <div className="inline-flex gap-8 text-white/80 text-sm">
            <div>
              <div className="text-3xl font-bold text-white">1.2K+</div>
              <div>Entdeckungen</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">500+</div>
              <div>Explorer</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">85</div>
              <div>Hotspots</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
