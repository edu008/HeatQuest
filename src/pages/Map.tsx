import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Camera, Loader2 } from 'lucide-react';
import BottomNav from '../components/BottomNav';

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
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [userName] = useState('edu008');

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

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 3000);
  };

  return (
    <div className="relative w-full h-screen pb-16">
      <div ref={mapContainer} className="absolute inset-0" />
      
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-white to-transparent p-4 z-10">
        <div className="flex justify-between items-center max-w-lg mx-auto">
          <div>
            <h1 className="text-2xl font-bold">
              <span className="text-primary">Heat</span>
              <span className="text-muted-foreground">Quest</span>
            </h1>
            <p className="text-sm text-muted-foreground">Hello, {userName}! 👋</p>
          </div>
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-full font-medium shadow-lg transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            <Camera className="w-5 h-5" />
            Analyze
          </button>
        </div>
      </div>

      {/* Analysis Modal */}
      {isAnalyzing && (
        <div className="absolute top-20 left-4 right-4 max-w-lg mx-auto z-20">
          <div className="bg-white rounded-2xl shadow-2xl p-6">
            <div className="flex items-start gap-4">
              <Loader2 className="w-8 h-8 text-primary animate-spin flex-shrink-0 mt-1" />
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-2">Analyzing Area...</h3>
                <p className="text-muted-foreground text-sm">
                  Checking if this area was already scanned
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <BottomNav />
    </div>
  );
};

export default Map;
