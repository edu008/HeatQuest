import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session, AuthError } from '@supabase/supabase-js'
import { supabase } from '@/integrations/supabase/client'
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
  const [initError, setInitError] = useState<string | null>(null)

  const loadProfile = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) {
        if (error.code === 'PGRST116') {
          const { data: { user } } = await supabase.auth.getUser()
          if (user) {
            await ensureProfile(user.id, user.user_metadata)
          }
          return
        }
        throw error
      }
      
      setProfile(data)
    } catch (error) {
      toast.error('Failed to load profile')
    }
  }

  const ensureProfile = async (userId: string, metadata?: any) => {
    try {
      const { data: existingProfile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (existingProfile) {
        setProfile(existingProfile)
        return
      }

      const username = 
        metadata?.user_name || 
        metadata?.full_name || 
        metadata?.name ||
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
      toast.success(`Welcome, ${username}!`)
    } catch (error) {
      toast.error('Failed to create profile')
    }
  }

  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      setSession(session)
      setUser(session?.user ?? null)

      if (session?.user) {
        setTimeout(() => {
          if (session.user.app_metadata.provider !== 'email') {
            ensureProfile(session.user.id, session.user.user_metadata)
          } else {
            loadProfile(session.user.id)
          }
        }, 0)
      } else {
        setProfile(null)
      }
    })

    supabase.auth
      .getSession()
      .then(({ data: { session }, error: sessionError }) => {
        if (sessionError) {
          setInitError(sessionError.message)
        }

        setSession(session)
        setUser(session?.user ?? null)

        if (session?.user) {
          setTimeout(() => {
            if (session.user.app_metadata.provider !== 'email') {
              ensureProfile(session.user.id, session.user.user_metadata)
            } else {
              loadProfile(session.user.id)
            }
          }, 0)
        }
      })
      .catch((err) => {
        setInitError(err instanceof Error ? err.message : 'Unknown error')
      })
      .finally(() => {
        setLoading(false)
      })

    return () => subscription.unsubscribe()
  }, [])

  // Sign Up
  const signUp = async (email: string, password: string, username: string) => {
    try {
      const redirectUrl = `${window.location.origin}/auth/callback`
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: redirectUrl }
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

  const signInWithOAuth = async (provider: 'github' | 'google') => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      })

      if (error) {
        toast.error(`OAuth Error: ${error.message}`)
        throw error
      }
    } catch (error) {
      const authError = error as AuthError
      toast.error(authError.message || 'OAuth Login failed')
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

