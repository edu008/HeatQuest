// Location Service - User Position Tracking und Speicherung

export interface UserLocation {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: Date;
}

export interface SavedLocation extends UserLocation {
  id: string;
  userId: string;
  scanned: boolean;
  scanData?: any;
}

class LocationService {
  private currentLocation: UserLocation | null = null;
  private watchId: number | null = null;

  /**
   * Hole aktuelle User-Position
   */
  async getCurrentPosition(): Promise<UserLocation> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation wird nicht unterstützt'));
        return;
      }

      console.log('📍 Requesting current position...');

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location: UserLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date(),
          };

          console.log('✅ Location found:', location);
          this.currentLocation = location;
          resolve(location);
        },
        (error) => {
          console.error('❌ Location error:', error);
          reject(this.handleLocationError(error));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    });
  }

  /**
   * Starte kontinuierliches Position-Tracking
   */
  startWatching(callback: (location: UserLocation) => void): void {
    if (!navigator.geolocation) {
      console.error('Geolocation nicht verfügbar');
      return;
    }

    console.log('👀 Starting location watch...');

    this.watchId = navigator.geolocation.watchPosition(
      (position) => {
        const location: UserLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date(),
        };

        this.currentLocation = location;
        callback(location);
      },
      (error) => {
        console.error('Watch error:', error);
      },
      {
        enableHighAccuracy: true,
        maximumAge: 30000,
        timeout: 27000,
      }
    );
  }

  /**
   * Stoppe Position-Tracking
   */
  stopWatching(): void {
    if (this.watchId !== null) {
      console.log('🛑 Stopping location watch');
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
  }

  /**
   * Speichere Location in localStorage
   */
  saveLocation(location: UserLocation, userId: string): string {
    const id = `loc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const savedLocation: SavedLocation = {
      id,
      userId,
      ...location,
      scanned: false,
    };

    // Hole existierende Locations
    const locations = this.getSavedLocations(userId);
    locations.push(savedLocation);

    // Speichere (max 50 Locations)
    const limited = locations.slice(-50);
    localStorage.setItem(`user_locations_${userId}`, JSON.stringify(limited));

    console.log('💾 Location saved:', id);
    return id;
  }

  /**
   * Hole gespeicherte Locations für User
   */
  getSavedLocations(userId: string): SavedLocation[] {
    const stored = localStorage.getItem(`user_locations_${userId}`);
    if (!stored) return [];

    try {
      return JSON.parse(stored);
    } catch {
      return [];
    }
  }

  /**
   * Markiere Location als gescannt
   */
  markLocationScanned(locationId: string, userId: string, scanData: any): void {
    const locations = this.getSavedLocations(userId);
    const location = locations.find(l => l.id === locationId);
    
    if (location) {
      location.scanned = true;
      location.scanData = scanData;
      localStorage.setItem(`user_locations_${userId}`, JSON.stringify(locations));
      console.log('✅ Location marked as scanned:', locationId);
    }
  }

  /**
   * Hole letzte bekannte Position
   */
  getLastKnownLocation(): UserLocation | null {
    return this.currentLocation;
  }

  /**
   * Error Handling
   */
  private handleLocationError(error: GeolocationPositionError): Error {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        return new Error('Location permission denied. Please enable location access.');
      case error.POSITION_UNAVAILABLE:
        return new Error('Location information unavailable.');
      case error.TIMEOUT:
        return new Error('Location request timed out.');
      default:
        return new Error('Unknown location error.');
    }
  }

  /**
   * Prüfe ob Permissions vorhanden
   */
  async checkPermissions(): Promise<boolean> {
    if (!navigator.permissions) {
      return true; // Assume granted if API not available
    }

    try {
      const result = await navigator.permissions.query({ name: 'geolocation' as PermissionName });
      console.log('📍 Location permission:', result.state);
      return result.state !== 'denied';
    } catch {
      return true;
    }
  }
}

export const locationService = new LocationService();

