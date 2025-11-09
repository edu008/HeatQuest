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

  // Lade Profil aus Datenbank
  const loadProfile = async (userId: string) => {
    try {
      console.log('📥 Loading profile for:', userId)
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) {
        console.error('❌ Profile load error:', error)
        console.error('Error details:', {
          code: error.code,
          message: error.message,
          details: error.details
        })
        
        // Wenn Profil nicht existiert (PGRST116), versuche es zu erstellen
        if (error.code === 'PGRST116') {
          console.log('⚠️ Profile not found, will try to create...')
          // Hole User Info von Auth
          const { data: { user } } = await supabase.auth.getUser()
          if (user) {
            await ensureProfile(user.id, user.user_metadata)
          }
          return
        }
        
        throw error
      }
      
      console.log('✅ Profile loaded:', data)
      setProfile(data)
    } catch (error) {
      console.error('❌ Error loading profile:', error)
      toast.error('Failed to load profile. Please refresh the page.')
    }
  }

  // Erstelle Profil falls noch nicht vorhanden (für OAuth-Logins)
  const ensureProfile = async (userId: string, metadata?: any) => {
    try {
      console.log('🔍 Checking if profile exists for:', userId)
      console.log('📋 Metadata:', metadata)
      
      // Prüfe ob Profil existiert
      const { data: existingProfile, error: fetchError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (existingProfile) {
        console.log('✅ Profile exists:', existingProfile)
        setProfile(existingProfile)
        return
      }

      console.log('⚠️ Profile does not exist, creating...')
      console.log('Fetch error (expected if not exists):', fetchError)

      // Erstelle neues Profil
      const username = 
        metadata?.user_name || 
        metadata?.full_name || 
        metadata?.name ||
        metadata?.email?.split('@')[0] || 
        `user_${userId.slice(0, 8)}`

      console.log('📝 Creating profile with username:', username)

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

      if (error) {
        console.error('❌ Error creating profile:', error)
        throw error
      }
      
      console.log('✅ Profile created:', newProfile)
      setProfile(newProfile)
      toast.success(`Welcome, ${username}! 🎉`)
    } catch (error) {
      console.error('❌ Error ensuring profile:', error)
      toast.error('Failed to create profile. Please try again.')
    }
  }

  // Initialisiere Auth State
  useEffect(() => {
    console.log('🔄 AuthContext: Initializing...')
    console.log('🔗 Current URL:', window.location.href)
    
    const initAuth = async () => {
      try {
        // Prüfe ob OAuth Redirect (URL enthält #access_token oder ?code=)
        const isOAuthRedirect = window.location.hash.includes('access_token') || window.location.search.includes('code=')
        
        if (isOAuthRedirect) {
          console.log('🔐 OAuth redirect detected! Processing...')
        }
        
        // Hole aktuelle Session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
          console.error('❌ Session error:', sessionError)
          setInitError(sessionError.message)
        }
        
        console.log('📦 Initial session:', session ? 'Found' : 'None')
        
        if (session) {
          console.log('📝 Session details:', {
            user: session.user.email,
            provider: session.user.app_metadata.provider,
            expires: new Date(session.expires_at! * 1000).toLocaleString()
          })
        }
        
        setSession(session)
        setUser(session?.user ?? null)
        
        if (session?.user) {
          console.log('👤 User found:', session.user.email)
          console.log('🔑 Provider:', session.user.app_metadata.provider)
          
          // Bei OAuth: Erstelle/Lade Profil
          if (session.user.app_metadata.provider !== 'email') {
            console.log('🔐 OAuth user detected, ensuring profile...')
            await ensureProfile(session.user.id, session.user.user_metadata)
          } else {
            await loadProfile(session.user.id)
          }
        }
      } catch (err) {
        console.error('❌ Auth init error:', err)
        setInitError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
        console.log('✅ AuthContext: Ready!')
      }
    }
    
    initAuth()

    // Höre auf Auth Changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔔 Auth event:', event, session ? 'Session exists' : 'No session')
      
      setSession(session)
      setUser(session?.user ?? null)
      
      if (session?.user) {
        console.log('👤 User in event:', session.user.email)
        console.log('🔑 Provider:', session.user.app_metadata.provider)
        
        // Bei OAuth-Login (SIGNED_IN) stelle sicher, dass Profil existiert
        if (event === 'SIGNED_IN' && session.user.app_metadata.provider !== 'email') {
          console.log('🔐 OAuth SIGNED_IN, ensuring profile...')
          await ensureProfile(session.user.id, session.user.user_metadata)
        } else {
          await loadProfile(session.user.id)
        }
      } else {
        console.log('❌ No user, clearing profile')
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
      console.log(`🔐 Starting OAuth with ${provider}...`)
      console.log('Origin:', window.location.origin)
      
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      })

      if (error) {
        console.error('❌ OAuth Error:', error)
        toast.error(`OAuth Error: ${error.message}`)
        throw error
      }
      
      console.log('✅ OAuth Response:', data)
      console.log('🔗 Will redirect to:', data.url)
      // Note: User wird automatisch weitergeleitet, daher kein toast hier
    } catch (error) {
      const authError = error as AuthError
      console.error('❌ Caught Error:', authError)
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

