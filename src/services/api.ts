/**
 * API Configuration and Base Client
 * 
 * Provides centralized configuration for API calls to Django backend
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  ENDPOINTS: {
    AUTH: '/api/auth/request-otp/',
    VERIFY_OTP: '/api/auth/verify-otp/',
    SIGNUP: '/api/auth/signup/',
    VERIFY_SIGNUP_OTP: '/api/auth/verify-signup-otp/',
    PROFILE: '/api/auth/profile/',
    DOCUMENTS: '/api/documents/',
    DOCUMENT_TYPES: '/api/documents/types/',
    DOCUMENT_UPLOAD: '/api/documents/upload/',
    DOCUMENT_DOWNLOAD: (docId: string) => `/api/documents/${docId}/`,
    CHAT: {
      SESSIONS: '/api/chat/sessions/',
      SEND: '/api/chat/send/',
      ELIGIBILITY: '/api/chat/eligibility/',
      FORM_ASSISTANCE: '/api/chat/form-assistance/',
    },
  },
} as const;

export interface ApiResponse<T = any> {
  success?: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  error: string;
  message: string;
  status?: number;
}

/**
 * Base API client with error handling and authentication
 */
class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = API_CONFIG.BASE_URL) {
    this.baseURL = baseURL;
    this.token = this.getStoredToken();
  }

  private getStoredToken(): string | null {
    try {
      return localStorage.getItem('agsa_session_token');
    } catch {
      return null;
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('agsa_session_token', token);
    } else {
      localStorage.removeItem('agsa_session_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const startTime = performance.now();
    const timestamp = new Date().toISOString();
    
    console.log(`[API_CLIENT] ${options.method || 'GET'} ${endpoint} - Started at: ${timestamp}`);
    
    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      defaultHeaders['X-Session-Token'] = this.token;
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
        'Connection': 'keep-alive',  // Reuse connections for speed
        'Keep-Alive': 'timeout=5, max=100',
      },
      // Enable HTTP/2 and connection reuse
      keepalive: true,
    };

    try {
      const response = await fetch(url, config);
      const networkDuration = performance.now() - startTime;
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const totalDuration = performance.now() - startTime;
        
        console.error(`[API_CLIENT] ${options.method || 'GET'} ${endpoint} - ERROR after ${totalDuration.toFixed(2)}ms`);
        console.error('[API_CLIENT] Network time:', `${networkDuration.toFixed(2)}ms`);
        console.error('[API_CLIENT] Error data:', errorData);
        throw new Error(errorData.message || errorData.error || `HTTP ${response.status}`);
      }

      const parseStartTime = performance.now();
      const data = await response.json();
      const parseDuration = performance.now() - parseStartTime;
      const totalDuration = performance.now() - startTime;
      
      console.log(`[API_CLIENT] ${options.method || 'GET'} ${endpoint} - SUCCESS after ${totalDuration.toFixed(2)}ms`);
      console.log('[API_CLIENT] Network time:', `${networkDuration.toFixed(2)}ms`);
      console.log('[API_CLIENT] Parse time:', `${parseDuration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      const totalDuration = performance.now() - startTime;
      console.error(`[API_CLIENT] ${options.method || 'GET'} ${endpoint} - EXCEPTION after ${totalDuration.toFixed(2)}ms`);
      console.error('[API_CLIENT] Exception:', error);
      
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.makeRequest<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.makeRequest<T>(endpoint, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient();
