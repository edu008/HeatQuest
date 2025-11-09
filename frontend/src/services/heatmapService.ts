// Heatmap Service - Backend API Integration

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface HeatmapRequest {
  latitude: number;
  longitude: number;
  radius_m?: number;
  cell_size_m?: number;
  use_cache?: boolean;
}

export interface GridCell {
  cell_id: string;
  lat_min: number;
  lat_max: number;
  lon_min: number;
  lon_max: number;
  center_lat: number;
  center_lon: number;
  temperature: number;
  temp: number; // Alias für temperature
  ndvi: number;
  heat_score: number;
  is_hotspot: boolean;
}

export interface HeatmapResponse {
  grid_cells: GridCell[];
  total_cells: number;
  cell_size_m: number;
  bounds: {
    lat_min: number;
    lat_max: number;
    lon_min: number;
    lon_max: number;
  };
  scene_id?: string;
  ndvi_source?: string;
  from_cache: boolean;
  parent_cell_info?: {
    id: string;
    cell_key: string;
    total_scans: number;
    last_scanned_at: string;
    child_cells_count: number;
  };
}

class HeatmapService {
  /**
   * Hole Heatmap-Daten für Position
   */
  async getHeatmapForLocation(request: HeatmapRequest): Promise<HeatmapResponse> {
    console.log('🌡️ Requesting heatmap for:', request);

    const params = new URLSearchParams({
      lat: request.latitude.toString(),
      lon: request.longitude.toString(),
      radius_m: (request.radius_m || 500).toString(),
      cell_size_m: (request.cell_size_m || 30).toString(),
      use_cache: (request.use_cache !== false).toString(),
      use_batch: 'true',
      format: 'json',
    });

    try {
      const response = await fetch(
        `${BACKEND_URL}/api/v1/grid-heat-score-radius?${params}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const error = await response.json();
        console.error('❌ Backend error:', error);
        throw new Error(error.detail || 'Failed to fetch heatmap');
      }

      const data: HeatmapResponse = await response.json();
      
      // Map temperature to temp for compatibility
      if (data.grid_cells) {
        data.grid_cells = data.grid_cells.map(cell => ({
          ...cell,
          temp: cell.temperature,
        }));
      }
      
      console.log('✅ Heatmap received:', {
        cells: data.grid_cells?.length,
        cached: data.from_cache,
        parent_cell: data.parent_cell_info?.cell_key,
      });

      return data;
    } catch (error) {
      console.error('❌ Heatmap request failed:', error);
      throw error;
    }
  }

  /**
   * Prüfe ob Parent Cell für Location existiert
   */
  async checkParentCell(latitude: number, longitude: number): Promise<{
    exists: boolean;
    parentCellId?: string;
    lastScanned?: string;
  }> {
    // Diese Info kommt aus der Heatmap Response
    // Wenn use_cache=true und cached=true, existiert Parent Cell
    try {
      const result = await this.getHeatmapForLocation({
        latitude,
        longitude,
        radius_m: 100, // Kleiner Radius für schnellen Check
        use_cache: true,
      });

      return {
        exists: result.from_cache === true,
        parentCellId: result.parent_cell_info?.id,
      };
    } catch (error) {
      console.error('Check parent cell failed:', error);
      return { exists: false };
    }
  }

  /**
   * Trigger neuen Heatmap-Scan (force, kein Cache)
   */
  async scanNewLocation(
    latitude: number,
    longitude: number,
    radius_m: number = 500
  ): Promise<HeatmapResponse> {
    console.log('🚀 Starting new heatmap scan...');

    return this.getHeatmapForLocation({
      latitude,
      longitude,
      radius_m,
      cell_size_m: 30,
      use_cache: false, // Force neuer Scan
    });
  }

  /**
   * Hole gecachte Heatmap (schnell)
   */
  async getCachedHeatmap(
    latitude: number,
    longitude: number,
    radius_m: number = 500
  ): Promise<HeatmapResponse | null> {
    try {
      const result = await this.getHeatmapForLocation({
        latitude,
        longitude,
        radius_m,
        use_cache: true,
      });

      // Wenn nicht aus Cache, return null
      if (!result.from_cache) {
        return null;
      }

      return result;
    } catch {
      return null;
    }
  }
}

export const heatmapService = new HeatmapService();

