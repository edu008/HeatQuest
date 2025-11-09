import React, { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { Mission } from "@/contexts/GameContext";

interface MapboxMapProps {
  token: string;
  missions: Mission[];
  onMissionClick: (mission: Mission) => void;
}

const MapboxMap: React.FC<MapboxMapProps> = ({ token, missions, onMissionClick }) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    mapboxgl.accessToken = token;

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: [7.4474, 46.9479],
      zoom: 13,
      pitch: 0,
      attributionControl: true,
    });

    // Place controls away from the header
    mapRef.current.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), "bottom-right");

    const geolocate = new mapboxgl.GeolocateControl({
      positionOptions: { enableHighAccuracy: true },
      trackUserLocation: true,
      showUserHeading: true,
    });
    mapRef.current.addControl(geolocate, "bottom-right");

    // Attempt to center on user once available
    mapRef.current.once("load", () => {
      geolocate.trigger();
    });

    return () => {
      // Cleanup markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      // Cleanup map
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [token]);

  useEffect(() => {
    if (!mapRef.current) return;

    // Clear previous markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // Add mission markers
    missions.forEach((mission) => {
      const el = document.createElement("div");
      el.className = "mapbox-mission-marker";
      el.innerHTML = `
        <div class="relative">
          <div class="absolute inset-0 rounded-full blur-md opacity-50" style="background: radial-gradient(circle, hsla(var(--heat)/.6) 0%, transparent 70%);"></div>
          <div class="relative rounded-full p-2 shadow-lg" style="background: linear-gradient(135deg, hsl(var(--heat)) 0%, hsl(var(--heat-intense)) 100%);">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path>
              <line x1="4" y1="22" x2="4" y2="15"></line>
            </svg>
          </div>
        </div>`;

      el.style.cursor = "pointer";
      el.addEventListener("click", () => onMissionClick(mission));

      const marker = new mapboxgl.Marker({ element: el, anchor: "bottom" })
        .setLngLat([mission.lng, mission.lat])
        .addTo(mapRef.current!);

      markersRef.current.push(marker);
    });
  }, [missions, onMissionClick]);

  return <div ref={mapContainerRef} className="h-full w-full" />;
};

export default MapboxMap;
