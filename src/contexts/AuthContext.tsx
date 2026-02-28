/**
 * Authentication Context
 * 
 * Provides authentication state management across the application
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authService, UserProfile, UserSessionInfo, SignUpRequest } from '@/services/auth';

interface AuthContextType {
  // Authentication state
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  sessionInfo: UserSessionInfo | null;

  // Authentication actions
  login: (phoneNumber: string) => Promise<{ request_id: string; message: string }>;
  verifyOTP: (requestId: string, otp: string) => Promise<void>;
  signUp: (signUpData: SignUpRequest) => Promise<{ request_id: string; message: string; user_id: string }>;
  verifySignUpOTP: (requestId: string, otp: string) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;

  // Utility functions
  formatPhoneNumber: (phone: string) => string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [sessionInfo, setSessionInfo] = useState<UserSessionInfo | null>(null);

  // Initialize authentication state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setIsLoading(true);
      
      // Check if user is authenticated
      const authenticated = authService.isAuthenticated();
      const storedSessionInfo = authService.getStoredSessionInfo();
      
      setIsAuthenticated(authenticated);
      setSessionInfo(storedSessionInfo);

      if (authenticated && storedSessionInfo) {
        // Try to fetch fresh user profile
        try {
          const profile = await authService.getUserProfile();
          setUser(profile);
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          // If profile fetch fails, user might need to re-authenticate
          if (error instanceof Error && error.message.includes('token')) {
            logout();
          } else {
            // Use stored profile if available
            setUser(storedSessionInfo.userProfile || null);
          }
        }
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (phoneNumber: string) => {
    try {
      setIsLoading(true);
      const response = await authService.requestOTP(phoneNumber);
      return response;
    } catch (error: any) {
      // Check if user needs to sign up
      if (error.status === 404 && error.data?.action === 'signup_required') {
        throw new Error('SIGNUP_REQUIRED');
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOTP = async (requestId: string, otp: string) => {
    try {
      setIsLoading(true);
      const response = await authService.verifyOTP(requestId, otp);
      
      if (response.success) {
        // Update authentication state
        setIsAuthenticated(true);
        const sessionInfo = authService.getStoredSessionInfo();
        setSessionInfo(sessionInfo);

        // Fetch user profile
        const profile = await authService.getUserProfile();
        setUser(profile);
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setUser(null);
    setSessionInfo(null);
  };

  const refreshProfile = async () => {
    try {
      if (!isAuthenticated) {
        throw new Error('User not authenticated');
      }

      const profile = await authService.getUserProfile();
      setUser(profile);
    } catch (error) {
      console.error('Failed to refresh profile:', error);
      throw error;
    }
  };

  const signUp = async (signUpData: SignUpRequest) => {
    try {
      setIsLoading(true);
      const response = await authService.signUp(signUpData);
      return response;
    } catch (error) {
      console.error('Sign up failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const verifySignUpOTP = async (requestId: string, otp: string) => {
    try {
      setIsLoading(true);
      const response = await authService.verifySignUpOTP(requestId, otp);
      
      // Update authentication state
      setIsAuthenticated(true);
      setSessionInfo({
        sessionToken: response.session_token,
        userId: response.user_id,
        isAuthenticated: true,
      });

      // Fetch user profile
      await refreshProfile();
    } catch (error) {
      console.error('Sign up OTP verification failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const formatPhoneNumber = (phone: string) => {
    return authService.formatPhoneForDisplay(phone);
  };

  const value: AuthContextType = {
    isAuthenticated,
    isLoading,
    user,
    sessionInfo,
    login,
    verifyOTP,
    signUp,
    verifySignUpOTP,
    logout,
    refreshProfile,
    formatPhoneNumber,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Protected Route Component
interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return fallback || <div>Please log in to access this page.</div>;
  }

  return <>{children}</>;
}
