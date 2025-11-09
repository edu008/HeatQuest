import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface Mission {
  id: string;
  title: string;
  description: string;
  lat: number;
  lng: number;
  heatRisk: number;
  reasons: string[];
  actions: string[];
  completed: boolean;
}

interface UserProfile {
  username: string;
  xp: number;
  level: number;
  completedMissions: number;
}

interface GameContextType {
  user: UserProfile | null;
  missions: Mission[];
  activeMission: Mission | null;
  login: (username: string) => void;
  logout: () => void;
  addMission: (mission: Mission) => void;
  setActiveMission: (mission: Mission | null) => void;
  completeMission: (missionId: string) => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

const initialMissions: Mission[] = [
  {
    id: "1",
    title: "Bahnhofplatz Bern",
    description: "Große Asphaltfläche ohne Schatten",
    lat: 46.9491,
    lng: 7.4386,
    heatRisk: 85,
    reasons: ["Große Asphaltfläche", "Kein Schatten", "Hohe Sonneneinstrahlung"],
    actions: ["Bäume pflanzen", "Reflektierende Oberflächen", "Wasserflächen"],
    completed: false,
  },
  {
    id: "2",
    title: "Paradeplatz Zürich",
    description: "Zentrale Platzfläche mit hoher Hitzebelastung",
    lat: 47.3699,
    lng: 8.5396,
    heatRisk: 78,
    reasons: ["Steinflächen absorbieren Hitze", "Wenig Schatten", "Hoher Fußgängerverkehr"],
    actions: ["Schattenstrukturen", "Grüne Inseln", "Sprühnebel-Systeme"],
    completed: false,
  },
  {
    id: "3",
    title: "Place Neuve Genf",
    description: "Offener Platz mit minimaler Vegetation",
    lat: 46.2,
    lng: 6.1422,
    heatRisk: 72,
    reasons: ["Minimale Vegetation", "Dunkles Pflaster", "Wenig Kühlung"],
    actions: ["Mobile Grünwände", "Solar-Schattensegel", "Stadtbäume pflanzen"],
    completed: false,
  },
];

export const GameProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [missions, setMissions] = useState<Mission[]>(initialMissions);
  const [activeMission, setActiveMission] = useState<Mission | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("heatquest_user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
  }, []);

  useEffect(() => {
    if (user) {
      localStorage.setItem("heatquest_user", JSON.stringify(user));
    }
  }, [user]);

  const login = (username: string) => {
    setUser({ username, xp: 0, level: 1, completedMissions: 0 });
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("heatquest_user");
  };

  const addMission = (mission: Mission) => {
    setMissions((prev) => [...prev, mission]);
  };

  const completeMission = (missionId: string) => {
    setMissions((prev) =>
      prev.map((m) => (m.id === missionId ? { ...m, completed: true } : m))
    );
    
    if (user) {
      const xpGain = 100;
      const newXp = user.xp + xpGain;
      const newLevel = Math.floor(newXp / 500) + 1;
      setUser({
        ...user,
        xp: newXp,
        level: newLevel,
        completedMissions: user.completedMissions + 1,
      });
    }
  };

  return (
    <GameContext.Provider
      value={{
        user,
        missions,
        activeMission,
        login,
        logout,
        addMission,
        setActiveMission,
        completeMission,
      }}
    >
      {children}
    </GameContext.Provider>
  );
};

export const useGame = () => {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error("useGame must be used within GameProvider");
  }
  return context;
};
