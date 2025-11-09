import { Link, useLocation } from "react-router-dom";
import { Map, Trophy, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/contexts/I18nContext";

const BottomNav = () => {
  const location = useLocation();
  const { t } = useI18n();

  const navItems = [
    { icon: Map, label: t("map"), path: "/map" },
    { icon: Trophy, label: t("leaderboard"), path: "/leaderboard" },
    { icon: User, label: t("profile"), path: "/profile" },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-card border-t border-border z-50">
      <div className="flex justify-around items-center h-16 max-w-2xl mx-auto">
        {navItems.map(({ icon: Icon, label, path }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={cn(
                "flex flex-col items-center justify-center flex-1 h-full transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Icon className={cn("w-6 h-6 mb-1", isActive && "animate-pulse-glow")} />
              <span className="text-xs font-medium">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNav;
