import { apiClient } from './api';

// Types for schemes
export interface Scheme {
  scheme_id: string;
  scheme_name: string;
  slug: string;
  level: 'central' | 'state' | 'district' | 'block' | 'panchayat';
  level_display: string;
  scheme_category: string;
  category_display: string;
  state?: string;
  is_active: boolean;
  created_at: string;
  document_count: number;
}

export interface SchemeDetail extends Scheme {
  details?: string;
  benefits?: string;
  eligibility?: string;
  application?: string;
  documents?: string;
  ministry_department?: string;
  launch_date?: string;
  website_url?: string;
  updated_at: string;
  required_documents_list: string[];
  document_objects: SchemeDocument[];
}

export interface SchemeDocument {
  document_name: string;
  document_type: string;
  is_mandatory: boolean;
  description?: string;
}

export interface EligibilityCheck {
  age?: number;
  gender?: 'male' | 'female' | 'other';
  income?: number;
  state?: string;
  category?: 'general' | 'obc' | 'sc' | 'st' | 'ews';
  occupation?: string;
  education?: string;
  is_rural?: boolean;
}

export interface EligibilityResult {
  scheme: Scheme;
  eligible: boolean;
  confidence: number;
  matches: string[];
  eligibility_text: string;
}

export interface SchemeFilters {
  search?: string;
  level?: string;
  category?: string;
  state?: string;
  is_active?: boolean;
  has_documents?: boolean;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface SchemeStats {
  total_schemes: number;
  active_schemes: number;
  central_schemes: number;
  state_schemes: number;
  categories: Array<{
    category: string;
    category_display: string;
    count: number;
  }>;
}

export interface FilterOptions {
  categories: Array<{ value: string; label: string }>;
  levels: Array<{ value: string; label: string }>;
  states: Array<{ value: string; label: string }>;
}

// API responses
export interface SchemesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Scheme[];
}

export interface EligibilityResponse {
  eligible_schemes: EligibilityResult[];
  total_found: number;
  user_criteria: EligibilityCheck;
  summary?: string;
}

// Schemes API service
export const schemesService = {
  // Get list of schemes with filters
  getSchemes: async (filters: SchemeFilters = {}): Promise<SchemesResponse> => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    
    return await apiClient.get<SchemesResponse>(`/api/schemes/?${params.toString()}`);
  },

  // Get scheme details by slug
  getSchemeDetail: async (slug: string): Promise<SchemeDetail> => {
    return await apiClient.get<SchemeDetail>(`/api/schemes/${slug}/`);
  },

  // Check eligibility for schemes
  checkEligibility: async (criteria: EligibilityCheck): Promise<EligibilityResponse> => {
    return await apiClient.post<EligibilityResponse>('/api/schemes/eligibility-check/', criteria);
  },

  // Get scheme documents
  getSchemeDocuments: async (slug: string) => {
    return await apiClient.get(`/api/schemes/${slug}/documents/`);
  },

  // Get schemes by category
  getSchemesByCategory: async (category: string, page = 1): Promise<SchemesResponse> => {
    return await apiClient.get<SchemesResponse>(`/api/schemes/categories/${category}/?page=${page}`);
  },

  // Get scheme statistics
  getSchemeStats: async (): Promise<SchemeStats> => {
    return await apiClient.get<SchemeStats>('/api/schemes/stats/');
  },

  // Get filter options
  getFilterOptions: async (): Promise<FilterOptions> => {
    return await apiClient.get<FilterOptions>('/api/schemes/filters/');
  },

  // Search schemes
  searchSchemes: async (query: string, filters: Partial<SchemeFilters> = {}): Promise<SchemesResponse> => {
    return schemesService.getSchemes({
      search: query,
      ...filters
    });
  }
};
