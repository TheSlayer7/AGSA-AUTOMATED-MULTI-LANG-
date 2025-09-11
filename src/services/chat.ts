/**
 * Chat service for API communication
 */

import { apiClient, API_CONFIG } from './index';

export interface ChatMessage {
  message_id: string;
  content: string;
  sender: 'user' | 'assistant' | 'system';
  message_type: 'text' | 'status' | 'summary' | 'system';
  timestamp: string;
  intent_category?: string;
  confidence_score?: number;
  extracted_entities?: Record<string, any>;
  action_required?: boolean;
}

export interface ChatSession {
  session_id: string;
  title: string;
  status: 'active' | 'archived' | 'deleted';
  created_at: string;
  updated_at: string;
  last_activity: string;
  messages: ChatMessage[];
  message_count: number;
}

export interface ConversationContext {
  current_flow: string;
  user_intent: string;
  extracted_data: Record<string, any>;
  pending_actions: string[];
  conversation_summary: string;
  last_updated: string;
}

export interface SendMessageRequest {
  session_id?: string;
  message: string;
  message_type?: 'text' | 'status' | 'summary';
}

export interface SendMessageResponse {
  session_id: string;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  context: ConversationContext;
}

export interface EligibilityScheme {
  scheme_name: string;
  eligible: boolean;
  eligibility_score: number;
  reason: string;
  benefits: string;
  next_steps: string;
  required_documents: string[];
}

export interface EligibilityResponse {
  user_profile: Record<string, any>;
  eligible_schemes: EligibilityScheme[];
  total_schemes_checked: number;
  eligible_count: number;
}

export interface FormAssistanceResponse {
  pre_filled_data: Record<string, any>;
  missing_fields: string[];
  completion_steps: string[];
  warnings: string[];
  documents_required: string[];
}

class ChatService {
  /**
   * Get user's chat sessions
   */
  async getSessions(): Promise<ChatSession[]> {
    const response = await apiClient.get<ChatSession[]>(
      API_CONFIG.ENDPOINTS.CHAT.SESSIONS
    );
    return response;
  }

  /**
   * Create a new chat session
   */
  async createSession(): Promise<ChatSession> {
    const response = await apiClient.post<ChatSession>(
      API_CONFIG.ENDPOINTS.CHAT.SESSIONS
    );
    return response;
  }

  /**
   * Send a message and get AI response
   */
  async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await apiClient.post<SendMessageResponse>(
      API_CONFIG.ENDPOINTS.CHAT.SEND,
      request
    );
    return response;
  }

  /**
   * Check eligibility for government schemes
   */
  async checkEligibility(): Promise<EligibilityResponse> {
    const response = await apiClient.post<EligibilityResponse>(
      API_CONFIG.ENDPOINTS.CHAT.ELIGIBILITY
    );
    return response;
  }

  /**
   * Get form filling assistance
   */
  async getFormAssistance(schemeName: string): Promise<FormAssistanceResponse> {
    const response = await apiClient.post<FormAssistanceResponse>(
      API_CONFIG.ENDPOINTS.CHAT.FORM_ASSISTANCE,
      { scheme_name: schemeName }
    );
    return response;
  }
}

export const chatService = new ChatService();
