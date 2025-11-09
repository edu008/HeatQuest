import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database Types
export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string
          username: string
          avatar_url: string | null
          points: number
          level: number
          missions_completed: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          username: string
          avatar_url?: string | null
          points?: number
          level?: number
          missions_completed?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          username?: string
          avatar_url?: string | null
          points?: number
          level?: number
          missions_completed?: number
          updated_at?: string
        }
      }
      discoveries: {
        Row: {
          id: string
          user_id: string
          location_name: string
          latitude: number
          longitude: number
          heat_score: number
          temperature: number
          ndvi: number
          ai_description: string | null
          image_url: string | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          location_name: string
          latitude: number
          longitude: number
          heat_score: number
          temperature: number
          ndvi: number
          ai_description?: string | null
          image_url?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          location_name?: string
          latitude?: number
          longitude?: number
          heat_score?: number
          temperature?: number
          ndvi?: number
          ai_description?: string | null
          image_url?: string | null
        }
      }
      missions: {
        Row: {
          id: string
          user_id: string
          mission_type: string
          status: 'pending' | 'completed'
          points_earned: number
          completed_at: string | null
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          mission_type: string
          status?: 'pending' | 'completed'
          points_earned?: number
          completed_at?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          status?: 'pending' | 'completed'
          points_earned?: number
          completed_at?: string | null
        }
      }
    }
  }
}

