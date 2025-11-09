import React, { createContext, useContext, useState, useEffect } from "react";

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

export interface UserProfile {
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
  completeMission: (missionId: string) => Promise<boolean>;
  updateMissionActions: (missionId: string, actions: string[]) => void;
  loadMissions: () => Promise<Mission[]>;  // Neu
  missionsLoading: boolean;  // Neu
}

const GameContext = createContext<GameContextType | undefined>(undefined);

// Dummy missions für Demo
const dummyMissions: Mission[] = [
  {
    id: "1",
    title: "Bahnhofplatz Bern",
    description: "Große Asphaltfläche ohne Schatten",
    lat: 46.9491,
    lng: 7.4386,
    heatRisk: 85,
    reasons: [
      "Large asphalt area without shade",
      "No visible vegetation",
      "High sun exposure",
    ],
    actions: [
      "Plant trees along the street",
      "Install cool reflective surfaces",
      "Add water features for cooling",
    ],
    completed: false,
  },
  {
    id: "2",
    title: "Paradeplatz Zürich",
    description: "Zentrale Platzfläche mit hoher Hitzebelastung",
    lat: 47.3699,
    lng: 8.5396,
    heatRisk: 78,
    reasons: [
      "Stone surface absorbs heat",
      "Limited shade areas",
      "High pedestrian traffic",
    ],
    actions: [
      "Install temporary shade structures",
      "Create green islands",
      "Add misting systems",
    ],
    completed: false,
  },
  {
    id: "3",
    title: "Place Neuve Genf",
    description: "Offener Platz mit minimaler Vegetation",
    lat: 46.2,
    lng: 6.1422,
    heatRisk: 72,
    reasons: [
      "Open square with minimal vegetation",
      "Dark pavement",
      "Limited cooling features",
    ],
    actions: [
      "Add portable green walls",
      "Install solar shade sails",
      "Plant urban trees",
    ],
    completed: false,
  },
];

export const GameProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [activeMission, setActiveMission] = useState<Mission | null>(null);
  const [missions, setMissions] = useState<Mission[]>(dummyMissions);
  const [missionsLoading, setMissionsLoading] = useState(false);

  // Load from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("heatquest_user");

    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Save to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem("heatquest_user", JSON.stringify(user));
    }
  }, [user]);

  const login = (username: string) => {
    const newUser: UserProfile = {
      username,
      xp: 0,
      level: 1,
      completedMissions: 0,
    };
    setUser(newUser);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("heatquest_user");
  };

  const addMission = (mission: Mission) => {
    setMissions((prev) => [...prev, mission]);
  };

  const loadMissions = async () => {
    return missions;
  };

  const completeMission = async (missionId: string) => {
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
    
    return true;
  };

  const updateMissionActions = (missionId: string, actions: string[]) => {
    // Wird aktuell nicht vom Backend unterstützt, nur lokal
    console.log('updateMissionActions:', missionId, actions);
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
        updateMissionActions,
        loadMissions,  // Neu: Funktion zum Laden der Missionen
        missionsLoading,  // Neu: Loading-Status
      }}
    >
      {children}
    </GameContext.Provider>
  );
};

export const useGame = () => {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error("useGame must be used within GameProvider");
  }
  return context;
};
