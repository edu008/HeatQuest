/**
 * Hook für Mission-Management
 * Lädt Missionen vom Backend basierend auf User-Position
 */

import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

export interface MissionAction {
  action: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Mission {
  id: string;
  title: string;
  description: string;
  lat: number;
  lng: number;
  heatRisk: number;
  reasons: string[];
  actions: (string | MissionAction)[]; // Support both old string format and new object format
  completed: boolean;
  imageUrl?: string;
  distance_to_user?: number;
  cell_analysis_id?: string;
  status?: string;
}

export const useMissions = () => {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  /**
   * Lädt Missionen für den aktuellen User
   */
  const loadMissions = useCallback(async () => {
    if (!user?.id) {
      console.log('❌ No user ID available for loading missions');
      return [];
    }

    try {
      setLoading(true);
      setError(null);

      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const url = `${apiUrl}/api/v1/missions?user_id=${user.id}&include_completed=true`;
      
      console.log('🔍 Loading missions from:', url);
      console.log('📝 User ID:', user.id);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', response.headers.get('content-type'));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Response error:', errorText);
        throw new Error(`Failed to load missions: ${response.status} - ${errorText.substring(0, 100)}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('❌ Non-JSON response:', text.substring(0, 200));
        throw new Error('API returned non-JSON response. Is the backend running?');
      }

      const data = await response.json();
      console.log('✅ Missionen geladen:', data);

      // Extrahiere Missionen aus Response
      const loadedMissions: Mission[] = data.missions || [];
      
      // Sortiere nach Entfernung (nächste zuerst)
      loadedMissions.sort((a, b) => {
        const distA = a.distance_to_user || Infinity;
        const distB = b.distance_to_user || Infinity;
        return distA - distB;
      });

      setMissions(loadedMissions);
      return loadedMissions;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('❌ Fehler beim Laden der Missionen:', errorMessage);
      setError(errorMessage);
      return [];
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  /**
   * Markiert eine Mission als abgeschlossen
   */
  const completeMission = useCallback(async (missionId: string) => {
    if (!user?.id) {
      console.log('❌ No user ID available for completing mission');
      return false;
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/missions/${missionId}/complete`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user.id,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to complete mission: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Mission abgeschlossen:', data);

      // Update local state
      setMissions((prev) =>
        prev.map((m) =>
          m.id === missionId ? { ...m, completed: true, status: 'completed' } : m
        )
      );

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('❌ Fehler beim Abschließen der Mission:', errorMessage);
      return false;
    }
  }, [user?.id]);

  /**
   * Fügt eine neue Mission hinzu (lokal)
   */
  const addMission = useCallback((mission: Mission) => {
    setMissions((prev) => {
      // Prüfe ob Mission bereits existiert
      if (prev.some((m) => m.id === mission.id)) {
        return prev;
      }
      return [...prev, mission];
    });
  }, []);

  /**
   * Entfernt alle abgeschlossenen Missionen aus der Liste
   */
  const removeCompletedMissions = useCallback(() => {
    setMissions((prev) => prev.filter((m) => !m.completed));
  }, []);

  /**
   * Gibt nur offene Missionen zurück
   */
  const getOpenMissions = useCallback(() => {
    return missions.filter((m) => !m.completed && m.status !== 'completed');
  }, [missions]);

  /**
   * Gibt nur abgeschlossene Missionen zurück
   */
  const getCompletedMissions = useCallback(() => {
    return missions.filter((m) => m.completed || m.status === 'completed');
  }, [missions]);

  return {
    missions,
    loading,
    error,
    loadMissions,
    completeMission,
    addMission,
    removeCompletedMissions,
    getOpenMissions,
    getCompletedMissions,
  };
};

