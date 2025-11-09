import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session, AuthError } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'
import { toast } from 'sonner'

interface Profile {
  id: string
  username: string
  avatar_url: string | null
  points: number
  level: number
  missions_completed: number
}

interface AuthContextType {
  user: User | null
  profile: Profile | null
  session: Session | null
  loading: boolean
  signUp: (email: string, password: string, username: string) => Promise<void>
  signIn: (email: string, password: string) => Promise<void>
  signInWithOAuth: (provider: 'github' | 'google') => Promise<void>
  signOut: () => Promise<void>
  updateProfile: (updates: Partial<Profile>) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  // Lade Profil aus Datenbank
  const loadProfile = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) throw error
      setProfile(data)
    } catch (error) {
      console.error('Error loading profile:', error)
    }
  }

  // Erstelle Profil falls noch nicht vorhanden (für OAuth-Logins)
  const ensureProfile = async (userId: string, metadata?: any) => {
    try {
      // Prüfe ob Profil existiert
      const { data: existingProfile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (existingProfile) {
        setProfile(existingProfile)
        return
      }

      // Erstelle neues Profil
      const username = 
        metadata?.user_name || 
        metadata?.full_name || 
        metadata?.email?.split('@')[0] || 
        `user_${userId.slice(0, 8)}`

      const { data: newProfile, error } = await supabase
        .from('profiles')
        .insert({
          id: userId,
          username,
          avatar_url: metadata?.avatar_url || metadata?.picture || null,
          points: 0,
          level: 1,
          missions_completed: 0,
        })
        .select()
        .single()

      if (error) throw error
      setProfile(newProfile)
      toast.success(`Willkommen, ${username}! 🎉`)
    } catch (error) {
      console.error('Error ensuring profile:', error)
    }
  }

  // Initialisiere Auth State
  useEffect(() => {
    // Hole aktuelle Session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      if (session?.user) {
        loadProfile(session.user.id)
      }
      setLoading(false)
    })

    // Höre auf Auth Changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      
      if (session?.user) {
        // Bei OAuth-Login (SIGNED_IN) stelle sicher, dass Profil existiert
        if (event === 'SIGNED_IN' && session.user.app_metadata.provider !== 'email') {
          await ensureProfile(session.user.id, session.user.user_metadata)
        } else {
          await loadProfile(session.user.id)
        }
      } else {
        setProfile(null)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  // Sign Up
  const signUp = async (email: string, password: string, username: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      })

      if (error) throw error

      // Erstelle Profil
      if (data.user) {
        const { error: profileError } = await supabase
          .from('profiles')
          .insert({
            id: data.user.id,
            username,
            points: 0,
            level: 1,
            missions_completed: 0,
          })

        if (profileError) throw profileError
      }

      toast.success('Account erfolgreich erstellt! 🎉')
    } catch (error) {
      const authError = error as AuthError
      toast.error(authError.message || 'Registrierung fehlgeschlagen')
      throw error
    }
  }

  // Sign In
  const signIn = async (email: string, password: string) => {
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error

      toast.success('Willkommen zurück! 🔥')
    } catch (error) {
      const authError = error as AuthError
      toast.error(authError.message || 'Login fehlgeschlagen')
      throw error
    }
  }

  // OAuth Login (GitHub, Google)
  const signInWithOAuth = async (provider: 'github' | 'google') => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/map`,
        },
      })

      if (error) throw error
      
      // Note: User wird automatisch weitergeleitet, daher kein toast hier
    } catch (error) {
      const authError = error as AuthError
      toast.error(authError.message || 'OAuth Login fehlgeschlagen')
      throw error
    }
  }

  // Sign Out
  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error

      toast.success('Erfolgreich abgemeldet')
    } catch (error) {
      const authError = error as AuthError
      toast.error(authError.message || 'Abmeldung fehlgeschlagen')
      throw error
    }
  }

  // Update Profile
  const updateProfile = async (updates: Partial<Profile>) => {
    if (!user) return

    try {
      const { error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('id', user.id)

      if (error) throw error

      // Aktualisiere lokalen State
      setProfile((prev) => (prev ? { ...prev, ...updates } : null))
      toast.success('Profil aktualisiert! ✅')
    } catch (error) {
      console.error('Error updating profile:', error)
      toast.error('Profil-Update fehlgeschlagen')
      throw error
    }
  }

  const value: AuthContextType = {
    user,
    profile,
    session,
    loading,
    signUp,
    signIn,
    signInWithOAuth,
    signOut,
    updateProfile,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

