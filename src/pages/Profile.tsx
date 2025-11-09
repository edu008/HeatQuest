import { Share, Flame, Trophy, Target } from 'lucide-react';
import BottomNav from '../components/BottomNav';

const Profile = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary via-primary/80 to-secondary pb-20">
      <div className="container mx-auto px-4 py-8 max-w-lg">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">Profil</h1>
          <button className="text-white p-2">
            <Share className="w-6 h-6" />
          </button>
        </div>

        {/* Profile Header */}
        <div className="bg-gradient-to-br from-primary via-primary/80 to-secondary rounded-3xl p-8 mb-6 relative overflow-hidden">
          <div className="absolute top-4 right-4 text-white">Level</div>
          <div className="flex items-center gap-4 mb-4">
            <div className="w-20 h-20 bg-secondary/30 rounded-full flex items-center justify-center">
              <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center text-white">
                👤
              </div>
            </div>
          </div>
        </div>

        {/* XP Card */}
        <div className="bg-white rounded-3xl p-6 shadow-lg mb-6">
          <div className="flex items-start gap-4 mb-4">
            <Flame className="w-8 h-8 text-primary" />
            <div className="flex-1">
              <div className="text-muted-foreground text-sm mb-1">Experience Points</div>
              <div className="text-3xl font-bold">XP</div>
              <div className="flex justify-between items-center mt-4 mb-2">
                <span className="text-muted-foreground text-sm">Bis Level 1</span>
                <span className="font-bold">0 XP</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-primary h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-3xl p-6 shadow-lg text-center">
            <Trophy className="w-12 h-12 text-primary mx-auto mb-3" />
            <div className="text-4xl font-bold mb-1">0</div>
            <div className="text-muted-foreground text-sm">Abgeschlossen</div>
          </div>
          <div className="bg-white rounded-3xl p-6 shadow-lg text-center">
            <Target className="w-12 h-12 text-secondary mx-auto mb-3" />
            <div className="text-4xl font-bold mb-1">58</div>
            <div className="text-muted-foreground text-sm">Aktive Missionen</div>
          </div>
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default Profile;
