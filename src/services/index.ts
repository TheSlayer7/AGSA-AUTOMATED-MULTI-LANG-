/**
 * Service Layer Index
 * 
 * Centralized exports for all API services
 */

export * from './api';
export * from './auth';
export * from './documents';

// Re-export commonly used services
export { authService } from './auth';
export { documentService } from './documents';
export { apiClient } from './api';
