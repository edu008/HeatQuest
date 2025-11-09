import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Home, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';

// Mock heatmap data points (Temperatur-Hotspots)
const heatmapData = [
  { lat: 48.2082, lon: 16.3738, intensity: 0.9, temp: 38 }, // Wien Zentrum
  { lat: 48.2100, lon: 16.3800, intensity: 0.7, temp: 35 },
  { lat: 48.2050, lon: 16.3700, intensity: 0.8, temp: 37 },
  { lat: 48.2120, lon: 16.3750, intensity: 0.6, temp: 34 },
  { lat: 48.2090, lon: 16.3820, intensity: 0.85, temp: 36 },
];

const Map = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [showHeatmap, setShowHeatmap] = useState(true);

  useEffect(() => {
    if (!mapContainer.current) return;

    const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN;
    if (!mapboxToken) {
      console.error('Mapbox token not found');
      return;
    }

    mapboxgl.accessToken = mapboxToken;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [16.3738, 48.2082], // Wien
      zoom: 13,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // Add heatmap markers
    map.current.on('load', () => {
      heatmapData.forEach((point) => {
        const el = document.createElement('div');
        el.className = 'heatmap-marker';
        el.style.backgroundColor = `rgba(255, ${255 - point.intensity * 200}, 0, ${point.intensity})`;
        el.style.width = `${20 + point.intensity * 30}px`;
        el.style.height = `${20 + point.intensity * 30}px`;
        el.style.borderRadius = '50%';
        el.style.border = '2px solid white';
        el.style.cursor = 'pointer';
        el.style.boxShadow = '0 0 20px rgba(255, 100, 0, 0.5)';

        const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(
          `<div style="padding: 8px;">
            <h3 style="margin: 0 0 8px 0; font-weight: bold;">Hotspot</h3>
            <p style="margin: 0;">🌡️ Temperatur: ${point.temp}°C</p>
            <p style="margin: 4px 0 0 0; font-size: 0.9em; color: #666;">
              Heat Score: ${(point.intensity * 100).toFixed(0)}%
            </p>
          </div>`
        );

        new mapboxgl.Marker(el)
          .setLngLat([point.lon, point.lat])
          .setPopup(popup)
          .addTo(map.current!);
      });
    });

    return () => {
      map.current?.remove();
    };
  }, []);

  return (
    <div className="relative w-full h-screen">
      <div ref={mapContainer} className="absolute inset-0" />
      
      {/* Header */}
      <div className="absolute top-4 left-4 right-4 flex justify-between items-center">
        <Link
          to="/"
          className="bg-white rounded-lg p-3 shadow-lg hover:bg-gray-100 transition-colors"
        >
          <Home className="w-6 h-6" />
        </Link>
        
        <div className="bg-white rounded-lg px-4 py-2 shadow-lg">
          <h2 className="text-lg font-bold">🔥 HeatQuest Map</h2>
        </div>

        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          className="bg-white rounded-lg p-3 shadow-lg hover:bg-gray-100 transition-colors"
        >
          <Layers className="w-6 h-6" />
        </button>
      </div>

      {/* Info Card */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg p-4 shadow-lg max-w-sm">
        <h3 className="font-bold text-lg mb-2">Legende</h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span>Hohe Temperatur (35°C+)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-orange-500"></div>
            <span>Mittlere Temperatur (30-35°C)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span>Niedrige Temperatur (25-30°C)</span>
          </div>
        </div>
        <p className="text-xs text-gray-600 mt-3">
          Klicke auf einen Marker für Details
        </p>
      </div>
    </div>
  );
};

export default Map;
