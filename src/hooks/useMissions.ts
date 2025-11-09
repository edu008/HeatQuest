/**
 * Hook für Mission-Management
 * Lädt Missionen vom Backend basierend auf User-Position
 */

import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContextMock';

export interface Mission {
  id: string;
  title: string;
  description: string;
  lat: number;
  lng: number;
  heatRisk: number;
  reasons: string[];
  actions: string[];
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
    console.log('🔍 Mock: Loading missions...');
    
    // Return empty array for now (missions come from GameContext dummy data)
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    setLoading(false);
    
    return [];
  }, []);

  /**
   * Markiert eine Mission als abgeschlossen
   */
  const completeMission = useCallback(async (missionId: string) => {
    console.log('✅ Mock: Completing mission', missionId);
    
    // Update local state
    setMissions((prev) =>
      prev.map((m) =>
        m.id === missionId ? { ...m, completed: true, status: 'completed' } : m
      )
    );

    return true;
  }, []);

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

