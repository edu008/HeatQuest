import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useGame } from "@/contexts/GameContext";
import { useNavigate } from "react-router-dom";
import BottomNav from "@/components/BottomNav";
import { Flag, Camera } from "lucide-react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Custom mission marker
const missionIcon = L.divIcon({
  className: "custom-mission-marker",
  html: `
    <div class="relative">
      <div class="absolute inset-0 bg-heat rounded-full blur-md opacity-50 animate-pulse"></div>
      <div class="relative bg-gradient-to-br from-heat to-heat-intense rounded-full p-2 shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path>
          <line x1="4" y1="22" x2="4" y2="15"></line>
        </svg>
      </div>
    </div>
  `,
  iconSize: [40, 40],
  iconAnchor: [20, 40],
});

// User location marker
const userIcon = L.divIcon({
  className: "custom-user-marker",
  html: `
    <div class="relative">
      <div class="absolute inset-0 bg-secondary rounded-full blur-md opacity-50 animate-pulse"></div>
      <div class="relative bg-gradient-to-br from-secondary to-cool-intense rounded-full p-2 shadow-lg border-2 border-white">
        <div class="w-4 h-4 bg-white rounded-full"></div>
      </div>
    </div>
  `,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});

function LocationMarker() {
  const [position, setPosition] = useState<[number, number] | null>(null);
  const map = useMap();

  useEffect(() => {
    map.locate({ setView: true, maxZoom: 13 });

    map.on("locationfound", (e) => {
      setPosition([e.latlng.lat, e.latlng.lng]);
    });
  }, [map]);

  return position === null ? null : (
    <Marker position={position} icon={userIcon}>
      <Popup>Du bist hier 📍</Popup>
    </Marker>
  );
}

const MapView = () => {
  const { missions, setActiveMission, user } = useGame();
  const navigate = useNavigate();
  const [isMapReady, setIsMapReady] = useState(false);

  // Fix for default markers in react-leaflet
  useEffect(() => {
    try {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
        iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
      });
      setIsMapReady(true);
    } catch (error) {
      console.error("Error setting up Leaflet icons:", error);
      setIsMapReady(true);
    }
  }, []);

  useEffect(() => {
    if (!user) {
      navigate("/");
    }
  }, [user, navigate]);

  if (!isMapReady) {
    return <div className="h-screen w-full flex items-center justify-center">Loading map...</div>;
  }

  const handleMissionClick = (mission: any) => {
    setActiveMission(mission);
    navigate(`/mission/${mission.id}`);
  };

  return (
    <div className="relative h-screen w-full">
      {/* Header */}
      <motion.div
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="absolute top-0 left-0 right-0 z-[1000] bg-gradient-to-b from-card/95 to-transparent backdrop-blur-sm p-4"
      >
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-heat via-primary to-cool-intense bg-clip-text text-transparent">
              HeatQuest
            </h1>
            <p className="text-sm text-muted-foreground">
              Hallo, {user?.username}! 👋
            </p>
          </div>
          <Button
            onClick={() => navigate("/analyze")}
            className="rounded-2xl bg-gradient-to-r from-heat to-primary hover:from-heat-intense hover:to-heat shadow-lg"
          >
            <Camera className="w-5 h-5 mr-2" />
            Analysieren
          </Button>
        </div>
      </motion.div>

      {/* Map */}
      <MapContainer
        center={[46.9479, 7.4474]}
        zoom={13}
        className="h-full w-full"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker />
        {missions.map((mission) => (
          <Marker
            key={mission.id}
            position={[mission.lat, mission.lng]}
            icon={missionIcon}
          >
            <Popup>
              <div className="space-y-2 p-2">
                <h3 className="font-bold text-lg">{mission.title}</h3>
                <p className="text-sm text-muted-foreground">
                  {mission.description}
                </p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-muted rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-heat to-heat-intense h-full rounded-full"
                      style={{ width: `${mission.heatRisk}%` }}
                    />
                  </div>
                  <span className="text-sm font-bold text-heat">
                    {mission.heatRisk}%
                  </span>
                </div>
                <Button
                  onClick={() => handleMissionClick(mission)}
                  disabled={mission.completed}
                  className="w-full rounded-xl"
                >
                  {mission.completed ? "✅ Abgeschlossen" : "🚀 Mission starten"}
                </Button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      <BottomNav />
    </div>
  );
};

export default MapView;
