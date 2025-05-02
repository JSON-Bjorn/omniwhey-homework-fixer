import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '@/lib/api';
import type { User, AuthResponse } from '@/lib/types';
import { useToast } from '@/components/ui/use-toast';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();
    const { toast } = useToast();

    // Check if user is already logged in on mount
    useEffect(() => {
        const checkAuthStatus = async () => {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                setIsLoading(false);
                return;
            }

            try {
                const response = await authAPI.getCurrentUser();
                setUser(response.data);
            } catch (error) {
                localStorage.removeItem('auth_token');
            } finally {
                setIsLoading(false);
            }
        };

        checkAuthStatus();
    }, []);

    const login = async (email: string, password: string): Promise<boolean> => {
        try {
            console.log('Login attempt with email:', email);
            console.log('Making API request to authAPI.login');

            const response = await authAPI.login(email, password);
            console.log('Login response:', response.data);

            const data = response.data as AuthResponse;
            console.log('Parsed auth response:', data);

            localStorage.setItem('auth_token', data.access_token);
            console.log('Stored auth token in localStorage');

            // Get user data with the new token
            console.log('Fetching user data with token');
            const userResponse = await authAPI.getCurrentUser();
            console.log('User data response:', userResponse.data);

            setUser(userResponse.data);

            toast({
                title: 'Login successful',
                description: 'Welcome back!',
            });

            return true;
        } catch (error: any) {
            console.error('Login error:', error);
            console.error('Error response:', error.response?.data);
            const message = error.response?.data?.detail || 'Login failed';
            toast({
                title: 'Login failed',
                description: message,
                variant: 'destructive',
            });
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem('auth_token');
        setUser(null);
        navigate('/login');
        toast({
            title: 'Logged out',
            description: 'You have been logged out successfully',
        });
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated: !!user,
                isLoading,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 