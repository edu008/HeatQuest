import { MapPin, Flame } from 'lucide-react';
import BottomNav from '../components/BottomNav';

const mockMissions = [
  {
    id: 1,
    title: 'Urban Heat Island Analysis',
    location: 'Downtown Vienna',
    heatRisk: 87,
    distance: '0.3 km',
    description: 'Analyze heat patterns in the city center',
  },
  {
    id: 2,
    title: 'Park Temperature Survey',
    location: 'Prater Park',
    heatRisk: 45,
    distance: '1.2 km',
    description: 'Compare temperatures in green spaces',
  },
  {
    id: 3,
    title: 'Asphalt Zone Check',
    location: 'Industrial District',
    heatRisk: 92,
    distance: '2.1 km',
    description: 'Measure heat in high-density areas',
  },
];

const Missions = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary via-primary/80 to-secondary pb-20">
      <div className="container mx-auto px-4 py-8 max-w-lg">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Missionen</h1>
          <p className="text-white/80">Verfügbare Climate Quests</p>
        </div>

        {/* Missions List */}
        <div className="space-y-4">
          {mockMissions.map((mission) => (
            <div
              key={mission.id}
              className="bg-white rounded-2xl p-5 shadow-lg"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="font-bold text-lg mb-1">{mission.title}</h3>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                    <MapPin className="w-4 h-4" />
                    <span>{mission.location}</span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <div className="flex items-center gap-1">
                    <Flame className="w-4 h-4 text-primary" />
                    <span className="font-bold text-primary">{mission.heatRisk}%</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{mission.distance}</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                {mission.description}
              </p>
              <button className="w-full py-3 bg-primary hover:bg-primary/90 text-white rounded-xl font-medium transition-colors">
                Start Mission
              </button>
            </div>
          ))}
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default Missions;
