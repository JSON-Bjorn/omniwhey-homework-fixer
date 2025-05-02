import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/lib/types'
import { authAPI } from '@/lib/api'

interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    isLoading: boolean

    // Actions
    setUser: (user: User | null) => void
    setToken: (token: string | null) => void
    setIsLoading: (isLoading: boolean) => void

    // Async actions
    login: (email: string, password: string) => Promise<boolean>
    logout: () => void
    checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: true,

            setUser: (user) => set({
                user,
                isAuthenticated: !!user
            }),

            setToken: (token) => {
                set({ token })

                // Update localStorage for backward compatibility with Context API
                if (token) {
                    localStorage.setItem('auth_token', token)
                } else {
                    localStorage.removeItem('auth_token')
                }
            },

            setIsLoading: (isLoading) => set({ isLoading }),

            login: async (email, password) => {
                try {
                    const response = await authAPI.login(email, password)
                    const { access_token } = response.data

                    // Store token
                    get().setToken(access_token)

                    // Fetch user data
                    await get().checkAuth()
                    return true
                } catch (error) {
                    console.error('Login error:', error)
                    return false
                }
            },

            logout: () => {
                // Clear auth data
                get().setToken(null)
                get().setUser(null)
            },

            checkAuth: async () => {
                const { token } = get()

                if (!token) {
                    // Try to get token from localStorage (for compatibility with context API)
                    const localToken = localStorage.getItem('auth_token')
                    if (localToken) {
                        get().setToken(localToken)
                    } else {
                        get().setIsLoading(false)
                        return
                    }
                }

                try {
                    get().setIsLoading(true)
                    const response = await authAPI.getCurrentUser()
                    get().setUser(response.data)
                } catch (error) {
                    // Clear invalid token
                    get().setToken(null)
                    get().setUser(null)
                } finally {
                    get().setIsLoading(false)
                }
            }
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ token: state.token }), // Only persist the token
        }
    )
) 