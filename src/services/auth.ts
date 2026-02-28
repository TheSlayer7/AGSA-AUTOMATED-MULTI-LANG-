/**
 * Authentication Service
 * 
 * Handles user authentication via phone number and OTP
 */

import { apiClient, API_CONFIG } from './api';

export interface AuthRequest {
  phone_number: string;
}

export interface AuthResponse {
  request_id: string;
  message: string;
}

export interface VerifyOTPRequest {
  request_id: string;
  otp_code: string;
}

export interface VerifyOTPResponse {
  success: boolean;
  session_token: string;
  user_id: string;
  message: string;
}

export interface SignUpRequest {
  phone_number: string;
  name: string;
  email?: string;
  date_of_birth: string;
  gender: 'M' | 'F' | 'O';
  address: string;
}

export interface SignUpResponse {
  request_id: string;
  message: string;
  user_id: string;
}

export interface VerifySignUpOTPRequest {
  request_id: string;
  otp_code: string;
}

export interface VerifySignUpOTPResponse {
  success: boolean;
  session_token: string;
  user_id: string;
  message: string;
}

export interface UserProfile {
  user_id: string;
  name: string;
  dob: string;
  gender: 'M' | 'F' | 'O';
  address: string;
  phone_number: string;
  email?: string;
  aadhaar_number?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SessionInfo {
  session_id: string;
  user_profile: UserProfile;
  created_at: string;
  last_activity: string;
  expires_at: string;
  is_valid: boolean;
}

class AuthService {
  /**
   * Request OTP for phone number authentication
   */
  async requestOTP(phoneNumber: string): Promise<AuthResponse> {
    // Validate phone number format
    const cleanedPhone = this.validateAndFormatPhoneNumber(phoneNumber);
    
    const response = await apiClient.post<AuthResponse>(
      API_CONFIG.ENDPOINTS.AUTH,
      { phone_number: cleanedPhone }
    );
    
    return response;
  }

  /**
   * Verify OTP and get session token
   */
  async verifyOTP(requestId: string, otp: string): Promise<VerifyOTPResponse> {
    const response = await apiClient.post<VerifyOTPResponse>(
      API_CONFIG.ENDPOINTS.VERIFY_OTP,
      { request_id: requestId, otp_code: otp }
    );

    if (response.success && response.session_token) {
      // Store session token
      apiClient.setToken(response.session_token);
      
      // Store user session info
      this.storeUserSession({
        sessionToken: response.session_token,
        userId: response.user_id,
        isAuthenticated: true,
      });
    }

    return response;
  }

  /**
   * Sign up new user with KYC data
   */
  async signUp(signUpData: SignUpRequest): Promise<SignUpResponse> {
    // Validate phone number format
    const cleanedPhone = this.validateAndFormatPhoneNumber(signUpData.phone_number);
    
    const requestData = {
      ...signUpData,
      phone_number: cleanedPhone
    };
    
    const response = await apiClient.post<SignUpResponse>(
      API_CONFIG.ENDPOINTS.SIGNUP,
      requestData
    );
    
    return response;
  }

  /**
   * Verify sign-up OTP and complete registration
   */
  async verifySignUpOTP(requestId: string, otp: string): Promise<VerifySignUpOTPResponse> {
    const response = await apiClient.post<VerifySignUpOTPResponse>(
      API_CONFIG.ENDPOINTS.VERIFY_SIGNUP_OTP,
      { request_id: requestId, otp_code: otp }
    );

    if (response.success && response.session_token) {
      // Store session token
      apiClient.setToken(response.session_token);
      
      // Store user session info
      this.storeUserSession({
        sessionToken: response.session_token,
        userId: response.user_id,
        isAuthenticated: true,
      });
    }

    return response;
  }

  /**
   * Get current user profile
   */
  async getUserProfile(): Promise<UserProfile> {
    if (!apiClient.getToken()) {
      throw new Error('No authentication token found');
    }

    const profile = await apiClient.get<UserProfile>(API_CONFIG.ENDPOINTS.PROFILE);
    
    // Update stored user info
    const sessionInfo = this.getStoredSessionInfo();
    if (sessionInfo) {
      this.storeUserSession({
        ...sessionInfo,
        userProfile: profile,
      });
    }

    return profile;
  }

  /**
   * Logout user and clear session
   */
  logout(): void {
    apiClient.setToken(null);
    this.clearUserSession();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = apiClient.getToken();
    const sessionInfo = this.getStoredSessionInfo();
    return !!(token && sessionInfo?.isAuthenticated);
  }

  /**
   * Get stored session information
   */
  getStoredSessionInfo(): UserSessionInfo | null {
    try {
      const sessionData = localStorage.getItem('agsa_user_session');
      return sessionData ? JSON.parse(sessionData) : null;
    } catch {
      return null;
    }
  }

  /**
   * Store user session information
   */
  private storeUserSession(sessionInfo: UserSessionInfo): void {
    try {
      localStorage.setItem('agsa_user_session', JSON.stringify(sessionInfo));
    } catch (error) {
      console.error('Failed to store user session:', error);
    }
  }

  /**
   * Clear user session information
   */
  private clearUserSession(): void {
    try {
      localStorage.removeItem('agsa_user_session');
    } catch (error) {
      console.error('Failed to clear user session:', error);
    }
  }

  /**
   * Validate and format phone number
   */
  private validateAndFormatPhoneNumber(phoneNumber: string): string {
    // Remove all non-numeric characters
    const cleaned = phoneNumber.replace(/\D/g, '');
    
    // Handle different input formats
    let formatted: string;
    
    if (cleaned.startsWith('91') && cleaned.length === 12) {
      // Already has country code (91xxxxxxxxxx)
      formatted = `+${cleaned}`;
    } else if (cleaned.length === 10) {
      // Indian mobile number without country code
      formatted = `+91${cleaned}`;
    } else if (phoneNumber.startsWith('+91') && cleaned.length === 12) {
      // Already properly formatted
      formatted = phoneNumber;
    } else {
      throw new Error('Invalid phone number format. Please enter a valid Indian mobile number.');
    }

    // Validate Indian mobile number pattern
    const indianMobileRegex = /^\+91[6-9]\d{9}$/;
    if (!indianMobileRegex.test(formatted)) {
      throw new Error('Please enter a valid Indian mobile number starting with 6, 7, 8, or 9.');
    }

    return formatted;
  }

  /**
   * Get formatted phone number for display
   */
  formatPhoneForDisplay(phoneNumber: string): string {
    const cleaned = phoneNumber.replace(/\D/g, '');
    if (cleaned.startsWith('91') && cleaned.length === 12) {
      const number = cleaned.substring(2);
      return `+91 ${number.substring(0, 5)} ${number.substring(5)}`;
    }
    return phoneNumber;
  }
}

export interface UserSessionInfo {
  sessionToken: string;
  userId: string;
  isAuthenticated: boolean;
  userProfile?: UserProfile;
}

export const authService = new AuthService();
