import { useState, useCallback } from 'react';
import { locationService, UserLocation } from '@/services/locationService';
import { heatmapService, HeatmapResponse } from '@/services/heatmapService';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';

export interface HeatmapState {
  loading: boolean;
  data: HeatmapResponse | null;
  error: string | null;
  userLocation: UserLocation | null;
}

export const useHeatmap = () => {
  const { user } = useAuth();
  const [state, setState] = useState<HeatmapState>({
    loading: false,
    data: null,
    error: null,
    userLocation: null,
  });

  /**
   * Hole User Location und prüfe Parent Cell
   */
  const scanCurrentLocation = useCallback(async (radius_m: number = 500) => {
    if (!user) {
      toast.error('Please login first');
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // 1. Hole User Position
      console.log('📍 Getting user location...');
      const location = await locationService.getCurrentPosition();
      
      setState(prev => ({ ...prev, userLocation: location }));
      toast.success(`Location found: ${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`);

      // 2. Speichere Location
      const locationId = locationService.saveLocation(location, user.id);
      console.log('💾 Location saved:', locationId);

      // 3. Prüfe Parent Cell & Scanne (Backend macht beides automatisch!)
      console.log('🔍 Requesting heatmap (auto checks cache)...');
      toast.loading('Analyzing area...', {
        duration: 30000,
      });

      const heatmapData = await heatmapService.getHeatmapForLocation({
        latitude: location.latitude,
        longitude: location.longitude,
        radius_m,
        use_cache: true, // Backend checkt automatisch Cache
        user_id: user.id, // For automatic mission generation
      });

      setState(prev => ({ 
        ...prev, 
        loading: false, 
        data: heatmapData,
        error: null 
      }));

      // Markiere als gescannt
      locationService.markLocationScanned(locationId, user.id, heatmapData);

      // Berechne Hotspots aus Grid Cells
      const hotspotCount = heatmapData.grid_cells.filter(cell => cell.is_hotspot).length;
      
      // Unterschiedliche Messages je nach Cache
      if (heatmapData.from_cache) {
        toast.success(
          `Found ${hotspotCount} hotspots! ⚡ (loaded from cache)`,
          { duration: 3000 }
        );
      } else {
        toast.success(
          `Area scanned! Found ${hotspotCount} hotspots in ${heatmapData.total_cells} cells 🔥`,
          { duration: 5000 }
        );
      }

      return heatmapData;

    } catch (error: any) {
      console.error('❌ Scan failed:', error);
      const errorMessage = error.message || 'Failed to scan location';
      
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: errorMessage 
      }));

      toast.error(errorMessage);
      throw error;
    }
  }, [user]);

  /**
   * Lade spezifische Koordinaten
   */
  const scanCoordinates = useCallback(async (
    latitude: number,
    longitude: number,
    radius_m: number = 500
  ) => {
    if (!user) {
      toast.error('Please login first');
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      console.log(`🌡️ Scanning coordinates: ${latitude}, ${longitude}`);

      // Request heatmap with user_id for mission generation
      toast.loading('Scanning...', { duration: 30000 });
      const heatmapData = await heatmapService.getHeatmapForLocation({
        latitude,
        longitude,
        radius_m,
        use_cache: true,
        user_id: user.id, // For automatic mission generation
      });

      setState(prev => ({ 
        ...prev, 
        loading: false, 
        data: heatmapData 
      }));

      toast.success('Scan complete! 🔥');
      return heatmapData;

    } catch (error: any) {
      console.error('❌ Scan failed:', error);
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error.message 
      }));
      toast.error(error.message);
      throw error;
    }
  }, [user]);

  /**
   * Reset State
   */
  const reset = useCallback(() => {
    setState({
      loading: false,
      data: null,
      error: null,
      userLocation: null,
    });
  }, []);

  return {
    ...state,
    scanCurrentLocation,
    scanCoordinates,
    reset,
  };
};

