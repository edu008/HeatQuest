import { createContext, useContext, useState, ReactNode } from 'react'
import { User, Session } from '@supabase/supabase-js'

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
  const [user] = useState<User | null>(null)
  const [profile] = useState<Profile | null>(null)
  const [session] = useState<Session | null>(null)
  const [loading] = useState(false)

  const signUp = async () => {
    console.log('Mock signUp called')
  }

  const signIn = async () => {
    console.log('Mock signIn called')
  }

  const signInWithOAuth = async () => {
    console.log('Mock signInWithOAuth called')
  }

  const signOut = async () => {
    console.log('Mock signOut called')
  }

  const updateProfile = async () => {
    console.log('Mock updateProfile called')
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
