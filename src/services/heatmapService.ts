// Heatmap Service - Backend API Integration

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface HeatmapRequest {
  latitude: number;
  longitude: number;
  radius_m?: number;
  cell_size_m?: number;
  use_cache?: boolean;
  user_id?: string; // For automatic mission generation
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
    console.log('🌡️ Mock heatmap for:', request);

    const lat = request.latitude;
    const lon = request.longitude;
    const radius = request.radius_m ?? 500;
    const cellSize = request.cell_size_m ?? 30;

    const metersToDegLat = (m: number) => m / 111_320;
    const metersToDegLon = (m: number, latitude: number) => m / (111_320 * Math.cos((latitude * Math.PI) / 180) + 1e-6);

    const latDelta = metersToDegLat(radius);
    const lonDelta = metersToDegLon(radius, lat);

    // Grid size roughly proportional to radius/cellSize
    const cellsPerAxis = Math.max(6, Math.min(20, Math.round((radius / cellSize))));
    const stepLat = (latDelta * 2) / cellsPerAxis;
    const stepLon = (lonDelta * 2) / cellsPerAxis;

    const grid: GridCell[] = [];

    for (let i = 0; i < cellsPerAxis; i++) {
      for (let j = 0; j < cellsPerAxis; j++) {
        const center_lat = (lat - latDelta) + stepLat * (i + 0.5);
        const center_lon = (lon - lonDelta) + stepLon * (j + 0.5);

        const lat_min = center_lat - stepLat / 2;
        const lat_max = center_lat + stepLat / 2;
        const lon_min = center_lon - stepLon / 2;
        const lon_max = center_lon + stepLon / 2;

        // Simple synthetic metrics
        const dx = (i - cellsPerAxis / 2) / (cellsPerAxis / 2);
        const dy = (j - cellsPerAxis / 2) / (cellsPerAxis / 2);
        const dist = Math.sqrt(dx * dx + dy * dy);

        const baseTemp = 26 + 6 * Math.max(0, 1 - dist) + (Math.sin(i * 0.7) + Math.cos(j * 0.5)) * 0.8;
        const ndvi = Math.max(0, Math.min(1, 0.6 - 0.4 * Math.max(0, 1 - dist) + (Math.sin((i + j) * 0.3) * 0.1)));
        const heat_score = Math.max(0, Math.min(1, (baseTemp - 24) / 10 * (1 - ndvi * 0.7)));
        const is_hotspot = heat_score > 0.7;

        grid.push({
          cell_id: `cell_${i}_${j}`,
          lat_min,
          lat_max,
          lon_min,
          lon_max,
          center_lat,
          center_lon,
          temperature: Number(baseTemp.toFixed(1)),
          temp: Number(baseTemp.toFixed(1)),
          ndvi: Number(ndvi.toFixed(2)),
          heat_score: Number(heat_score.toFixed(2)),
          is_hotspot,
        });
      }
    }

    const response: HeatmapResponse = {
      grid_cells: grid,
      total_cells: grid.length,
      cell_size_m: cellSize,
      bounds: {
        lat_min: lat - latDelta,
        lat_max: lat + latDelta,
        lon_min: lon - lonDelta,
        lon_max: lon + lonDelta,
      },
      scene_id: 'mock_scene',
      ndvi_source: 'mock',
      from_cache: true,
      parent_cell_info: {
        id: 'mock-parent',
        cell_key: `${lat.toFixed(2)}_${lon.toFixed(2)}`,
        total_scans: 3,
        last_scanned_at: new Date().toISOString(),
        child_cells_count: grid.length,
      },
    };

    console.log('✅ Mock heatmap generated:', { cells: response.total_cells });
    return Promise.resolve(response);
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

