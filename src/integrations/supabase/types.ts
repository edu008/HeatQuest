export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      cell_analyses: {
        Row: {
          ai_summary: string | null
          child_cell_id: string
          confidence: number | null
          created_at: string | null
          gemini_model: string | null
          heat_score: number | null
          id: string
          image_url: string | null
          latitude: number
          longitude: number
          main_cause: string | null
          mission_generated: boolean | null
          ndvi: number | null
          parent_cell_id: string
          suggested_actions: Json | null
          temperature: number | null
        }
        Insert: {
          ai_summary?: string | null
          child_cell_id: string
          confidence?: number | null
          created_at?: string | null
          gemini_model?: string | null
          heat_score?: number | null
          id?: string
          image_url?: string | null
          latitude: number
          longitude: number
          main_cause?: string | null
          mission_generated?: boolean | null
          ndvi?: number | null
          parent_cell_id: string
          suggested_actions?: Json | null
          temperature?: number | null
        }
        Update: {
          ai_summary?: string | null
          child_cell_id?: string
          confidence?: number | null
          created_at?: string | null
          gemini_model?: string | null
          heat_score?: number | null
          id?: string
          image_url?: string | null
          latitude?: number
          longitude?: number
          main_cause?: string | null
          mission_generated?: boolean | null
          ndvi?: number | null
          parent_cell_id?: string
          suggested_actions?: Json | null
          temperature?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "cell_analyses_child_cell_id_fkey"
            columns: ["child_cell_id"]
            isOneToOne: false
            referencedRelation: "child_cells"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "cell_analyses_parent_cell_id_fkey"
            columns: ["parent_cell_id"]
            isOneToOne: false
            referencedRelation: "parent_cells"
            referencedColumns: ["id"]
          },
        ]
      }
      child_cells: {
        Row: {
          ai_analysis_id: string | null
          analyzed: boolean | null
          cell_id: string
          cell_size_m: number | null
          center_lat: number
          center_lon: number
          created_at: string | null
          heat_score: number | null
          id: string
          is_hotspot: boolean | null
          lat_max: number
          lat_min: number
          lon_max: number
          lon_min: number
          ndvi: number | null
          parent_cell_id: string
          pixel_count: number | null
          temperature: number | null
          updated_at: string | null
        }
        Insert: {
          ai_analysis_id?: string | null
          analyzed?: boolean | null
          cell_id: string
          cell_size_m?: number | null
          center_lat: number
          center_lon: number
          created_at?: string | null
          heat_score?: number | null
          id?: string
          is_hotspot?: boolean | null
          lat_max: number
          lat_min: number
          lon_max: number
          lon_min: number
          ndvi?: number | null
          parent_cell_id: string
          pixel_count?: number | null
          temperature?: number | null
          updated_at?: string | null
        }
        Update: {
          ai_analysis_id?: string | null
          analyzed?: boolean | null
          cell_id?: string
          cell_size_m?: number | null
          center_lat?: number
          center_lon?: number
          created_at?: string | null
          heat_score?: number | null
          id?: string
          is_hotspot?: boolean | null
          lat_max?: number
          lat_min?: number
          lon_max?: number
          lon_min?: number
          ndvi?: number | null
          parent_cell_id?: string
          pixel_count?: number | null
          temperature?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "child_cells_parent_cell_id_fkey"
            columns: ["parent_cell_id"]
            isOneToOne: false
            referencedRelation: "parent_cells"
            referencedColumns: ["id"]
          },
        ]
      }
      discoveries: {
        Row: {
          avg_heat_score: number | null
          avg_ndvi: number | null
          avg_temperature: number | null
          cell_size_m: number
          created_at: string | null
          hotspot_cells_found: number | null
          id: string
          image_url: string | null
          latitude: number
          location_name: string
          longitude: number
          notes: string | null
          parent_cell_id: string
          radius_m: number
          total_cells_viewed: number | null
          user_id: string
        }
        Insert: {
          avg_heat_score?: number | null
          avg_ndvi?: number | null
          avg_temperature?: number | null
          cell_size_m: number
          created_at?: string | null
          hotspot_cells_found?: number | null
          id?: string
          image_url?: string | null
          latitude: number
          location_name: string
          longitude: number
          notes?: string | null
          parent_cell_id: string
          radius_m: number
          total_cells_viewed?: number | null
          user_id: string
        }
        Update: {
          avg_heat_score?: number | null
          avg_ndvi?: number | null
          avg_temperature?: number | null
          cell_size_m?: number
          created_at?: string | null
          hotspot_cells_found?: number | null
          id?: string
          image_url?: string | null
          latitude?: number
          location_name?: string
          longitude?: number
          notes?: string | null
          parent_cell_id?: string
          radius_m?: number
          total_cells_viewed?: number | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "discoveries_parent_cell_id_fkey"
            columns: ["parent_cell_id"]
            isOneToOne: false
            referencedRelation: "parent_cells"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "discoveries_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
        ]
      }
      missions: {
        Row: {
          cell_analysis_id: string | null
          child_cell_id: string | null
          completed_at: string | null
          completed_by_user_id: string | null
          created_at: string | null
          created_by_system: boolean | null
          description: string | null
          distance_to_user: number | null
          heat_risk_score: number | null
          id: string
          latitude: number
          longitude: number
          mission_type: string | null
          parent_cell_id: string | null
          points_earned: number | null
          required_actions: Json | null
          status: string | null
          title: string
          user_id: string
        }
        Insert: {
          cell_analysis_id?: string | null
          child_cell_id?: string | null
          completed_at?: string | null
          completed_by_user_id?: string | null
          created_at?: string | null
          created_by_system?: boolean | null
          description?: string | null
          distance_to_user?: number | null
          heat_risk_score?: number | null
          id?: string
          latitude: number
          longitude: number
          mission_type?: string | null
          parent_cell_id?: string | null
          points_earned?: number | null
          required_actions?: Json | null
          status?: string | null
          title: string
          user_id: string
        }
        Update: {
          cell_analysis_id?: string | null
          child_cell_id?: string | null
          completed_at?: string | null
          completed_by_user_id?: string | null
          created_at?: string | null
          created_by_system?: boolean | null
          description?: string | null
          distance_to_user?: number | null
          heat_risk_score?: number | null
          id?: string
          latitude?: number
          longitude?: number
          mission_type?: string | null
          parent_cell_id?: string | null
          points_earned?: number | null
          required_actions?: Json | null
          status?: string | null
          title?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "missions_cell_analysis_id_fkey"
            columns: ["cell_analysis_id"]
            isOneToOne: false
            referencedRelation: "cell_analyses"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "missions_child_cell_id_fkey"
            columns: ["child_cell_id"]
            isOneToOne: false
            referencedRelation: "child_cells"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "missions_completed_by_user_id_fkey"
            columns: ["completed_by_user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "missions_parent_cell_id_fkey"
            columns: ["parent_cell_id"]
            isOneToOne: false
            referencedRelation: "parent_cells"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "missions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
        ]
      }
      parent_cells: {
        Row: {
          avg_heat_score: number | null
          avg_ndvi: number | null
          avg_temperature: number | null
          bbox_max_lat: number
          bbox_max_lon: number
          bbox_min_lat: number
          bbox_min_lon: number
          cell_key: string
          center_lat: number
          center_lon: number
          child_cells_count: number | null
          created_at: string | null
          hotspot_percentage: number | null
          id: string
          landsat_scene_id: string | null
          last_scanned_at: string | null
          ndvi_source: string | null
          sentinel_scene_id: string | null
          total_scans: number | null
          updated_at: string | null
        }
        Insert: {
          avg_heat_score?: number | null
          avg_ndvi?: number | null
          avg_temperature?: number | null
          bbox_max_lat: number
          bbox_max_lon: number
          bbox_min_lat: number
          bbox_min_lon: number
          cell_key: string
          center_lat: number
          center_lon: number
          child_cells_count?: number | null
          created_at?: string | null
          hotspot_percentage?: number | null
          id?: string
          landsat_scene_id?: string | null
          last_scanned_at?: string | null
          ndvi_source?: string | null
          sentinel_scene_id?: string | null
          total_scans?: number | null
          updated_at?: string | null
        }
        Update: {
          avg_heat_score?: number | null
          avg_ndvi?: number | null
          avg_temperature?: number | null
          bbox_max_lat?: number
          bbox_max_lon?: number
          bbox_min_lat?: number
          bbox_min_lon?: number
          cell_key?: string
          center_lat?: number
          center_lon?: number
          child_cells_count?: number | null
          created_at?: string | null
          hotspot_percentage?: number | null
          id?: string
          landsat_scene_id?: string | null
          last_scanned_at?: string | null
          ndvi_source?: string | null
          sentinel_scene_id?: string | null
          total_scans?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      profiles: {
        Row: {
          avatar_url: string | null
          created_at: string | null
          id: string
          level: number | null
          missions_completed: number | null
          points: number | null
          username: string | null
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string | null
          id: string
          level?: number | null
          missions_completed?: number | null
          points?: number | null
          username?: string | null
        }
        Update: {
          avatar_url?: string | null
          created_at?: string | null
          id?: string
          level?: number | null
          missions_completed?: number | null
          points?: number | null
          username?: string | null
        }
        Relationships: []
      }
      user_locations: {
        Row: {
          accuracy: number | null
          context: string | null
          id: string
          latitude: number
          longitude: number
          mission_id: string | null
          parent_cell_id: string | null
          recorded_at: string | null
          user_id: string
        }
        Insert: {
          accuracy?: number | null
          context?: string | null
          id?: string
          latitude: number
          longitude: number
          mission_id?: string | null
          parent_cell_id?: string | null
          recorded_at?: string | null
          user_id: string
        }
        Update: {
          accuracy?: number | null
          context?: string | null
          id?: string
          latitude?: number
          longitude?: number
          mission_id?: string | null
          parent_cell_id?: string | null
          recorded_at?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_locations_mission_id_fkey"
            columns: ["mission_id"]
            isOneToOne: false
            referencedRelation: "missions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_locations_parent_cell_id_fkey"
            columns: ["parent_cell_id"]
            isOneToOne: false
            referencedRelation: "parent_cells"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_locations_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
