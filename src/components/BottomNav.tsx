import { Link, useLocation } from 'react-router-dom';
import { MapIcon, Trophy, User, Target } from 'lucide-react';

const BottomNav = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/map', icon: MapIcon, label: 'Map' },
    { path: '/leaderboard', icon: Trophy, label: 'Rangliste' },
    { path: '/missions', icon: Target, label: 'Missionen' },
    { path: '/profile', icon: User, label: 'Profil' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-background border-t border-border z-50">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                isActive
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="w-6 h-6" />
              <span className="text-xs mt-1">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNav;
