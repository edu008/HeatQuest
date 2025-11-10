import React, { useEffect, useRef, useState } from "react";
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
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [mapReady, setMapReady] = useState(false);

  // Hole User Position beim ersten Laden
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation([position.coords.longitude, position.coords.latitude]);
        },
        (error) => {
          console.error("Error getting user location:", error);
          // Fallback zu Bern, falls Geolocation fehlschlägt
          setUserLocation([7.4474, 46.9479]);
        }
      );
    } else {
      // Fallback zu Bern, falls Geolocation nicht unterstützt wird
      setUserLocation([7.4474, 46.9479]);
    }
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current || !userLocation) return;

    mapboxgl.accessToken = token;

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: userLocation,
      zoom: 15,
      pitch: 0,
      attributionControl: true,
      // Deaktiviere manuelle Interaktionen
      dragPan: false,
      scrollZoom: false,
      boxZoom: false,
      dragRotate: false,
      keyboard: false,
      doubleClickZoom: false,
      touchZoomRotate: false,
    });

    // Geolocate Control mit automatischem Tracking
    const geolocate = new mapboxgl.GeolocateControl({
      positionOptions: { 
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 6000
      },
      trackUserLocation: true,
      showUserHeading: true,
      showUserLocation: true,
      showAccuracyCircle: false,
      fitBoundsOptions: {
        maxZoom: 15
      }
    });
    mapRef.current.addControl(geolocate, "top-right");

    // Automatisch die Karte mit GPS-Position synchronisieren
    mapRef.current.once("load", () => {
      geolocate.trigger();
      setMapReady(true);
    });

    // Event Listener für GPS-Updates
    geolocate.on('geolocate', (e) => {
      const { longitude, latitude } = e.coords;
      console.log('📍 GPS Update:', latitude, longitude);
      
      // Zentriere Karte auf neue Position
      mapRef.current?.flyTo({
        center: [longitude, latitude],
        zoom: 15,
        speed: 0.8,
        curve: 1,
        essential: true
      });
    });

    return () => {
      // Cleanup markers
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      // Cleanup map
      mapRef.current?.remove();
      mapRef.current = null;
      setMapReady(false);
    };
  }, [token, userLocation]);

  useEffect(() => {
    if (!mapRef.current || !mapReady) return;

    // Clear previous markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // Add mission markers
    missions.forEach((mission) => {
      const el = document.createElement("div");
      el.className = "mapbox-mission-marker";
      el.innerHTML = `
        <div class="relative animate-pulse">
          <div class="absolute inset-0 rounded-full blur-lg opacity-60" style="background: radial-gradient(circle, hsla(var(--heat)/.8) 0%, transparent 70%);"></div>
          <div class="relative rounded-full p-2 shadow-xl" style="background: linear-gradient(135deg, hsl(var(--heat)) 0%, hsl(var(--heat-intense)) 100%);">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white" stroke="none">
              <path d="M8.5 14.5c.5-1 1.5-2 2.5-3 1 .5 2 1 3 2-1 1.5-2 2.5-3 3-.5-1-1-1.5-1.5-2zm4.5-9.5c-1 2-2.5 3.5-3.5 5 0 0-1.5 1.5-2 3.5-.5 2 .5 4 2.5 4.5s4-1 4.5-3c.5-2-.5-3.5-1-4.5 0 0 1-2 1.5-3.5.5-1.5.5-3-.5-4-.5-.5-1-.5-1.5 0z"/>
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
  }, [missions, onMissionClick, mapReady]);

  return <div ref={mapContainerRef} className="h-full w-full" />;
};

export default MapboxMap;
