/**
 * Document Management Service
 * 
 * Handles document operations including listing, downloading, and management
 */

import { apiClient, API_CONFIG } from './api';

export interface DocumentType {
  id: number;
  name: string;
  issued_by: string;
  category: string;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  doc_id: string;
  user_profile: string;
  document_type: DocumentType;
  doc_number: string;
  issue_date: string;
  expiry_date?: string;
  is_verified: boolean;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  file_size?: number;
  mime_type?: string;
}

export interface DocumentListItem {
  doc_id: string;
  name: string;
  doc_number: string;
  issue_date: string;
  expiry_date?: string;
  is_verified: boolean;
}

export interface DocumentDownload {
  doc_id: string;
  name: string;
  content: string; // Base64 encoded or text content
  mime_type: string;
  size: number;
  filename: string;
}

export interface DocumentUploadRequest {
  document_type_id: number;
  doc_number: string;
  issue_date: string;
  expiry_date?: string;
  file: File;
  metadata?: Record<string, any>;
}

class DocumentService {
  /**
   * Get list of user's documents
   */
  async getUserDocuments(): Promise<{success: boolean; data: DocumentListItem[]; message: string}> {
    if (!apiClient.getToken()) {
      throw new Error('No authentication token found');
    }

    const response = await apiClient.get<{success: boolean; data: DocumentListItem[]; message: string}>(
      API_CONFIG.ENDPOINTS.DOCUMENTS
    );

    return response;
  }

  /**
   * Get list of user's documents (legacy method)
   */
  async getDocuments(): Promise<DocumentListItem[]> {
    const response = await this.getUserDocuments();
    return response.data;
  }

  /**
   * Download a specific document
   */
  async downloadDocument(docId: string): Promise<DocumentDownload> {
    if (!apiClient.getToken()) {
      throw new Error('No authentication token found');
    }

    const document = await apiClient.get<DocumentDownload>(
      API_CONFIG.ENDPOINTS.DOCUMENT_DOWNLOAD(docId)
    );

    return document;
  }

  /**
   * Get document types available for upload
   */
  async getDocumentTypes(): Promise<{success: boolean; data: DocumentType[]; message: string}> {
    try {
      const response = await apiClient.get<{success: boolean; data: DocumentType[]; message: string}>(
        API_CONFIG.ENDPOINTS.DOCUMENT_TYPES
      );
      return response;
    } catch (error) {
      // Return default document types if endpoint doesn't exist
      return {
        success: true,
        data: [
          {
            id: 1,
            name: 'Aadhaar Card',
            issued_by: 'UIDAI',
            category: 'identity',
            is_active: true,
            created_at: new Date().toISOString(),
          },
          {
            id: 2,
            name: 'PAN Card',
            issued_by: 'Income Tax Department',
            category: 'identity',
            is_active: true,
            created_at: new Date().toISOString(),
          },
          {
            id: 3,
            name: 'Driving License',
            issued_by: 'Transport Department',
            category: 'license',
            is_active: true,
            created_at: new Date().toISOString(),
          },
        ],
        message: 'Default document types loaded'
      };
    }
  }

  /**
   * Upload a new document
   */
  async uploadDocument(request: DocumentUploadRequest): Promise<Document> {
    if (!apiClient.getToken()) {
      throw new Error('No authentication token found');
    }

    // Create FormData for file upload
    const formData = new FormData();
    formData.append('doc_type', request.document_type_id.toString());
    formData.append('doc_number', request.doc_number);
    formData.append('issue_date', request.issue_date);
    
    if (request.expiry_date) {
      formData.append('expiry_date', request.expiry_date);
    }
    
    formData.append('file', request.file);

    // Make request with FormData (no JSON content type)
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.DOCUMENT_UPLOAD}`, {
      method: 'POST',
      headers: {
        'X-Session-Token': apiClient.getToken() || '',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || errorData.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Update document metadata
   */
  async updateDocument(docId: string, updates: Partial<Document>): Promise<Document> {
    if (!apiClient.getToken()) {
      throw new Error('No authentication token found');
    }

    const document = await apiClient.put<Document>(
      API_CONFIG.ENDPOINTS.DOCUMENT_DOWNLOAD(docId),
      updates
    );

    return document;
  }

  /**
   * Delete a document
   */
  async deleteDocument(docId: string): Promise<void> {
    if (!apiClient.getToken()) {
      throw new Error('No authentication token found');
    }

    await apiClient.delete(API_CONFIG.ENDPOINTS.DOCUMENT_DOWNLOAD(docId));
  }

  /**
   * Get document preview/thumbnail
   */
  async getDocumentPreview(docId: string): Promise<string> {
    const document = await this.downloadDocument(docId);
    
    // For images, return the content directly
    if (document.mime_type.startsWith('image/')) {
      return `data:${document.mime_type};base64,${document.content}`;
    }
    
    // For other types, you might want to generate thumbnails
    // This is a placeholder - implement based on your needs
    return '';
  }

  /**
   * Check document verification status
   */
  async verifyDocument(docId: string): Promise<{ is_verified: boolean; verification_details?: any }> {
    if (!apiClient.getToken()) {
      throw new Error('No authentication token found');
    }

    // This would be a separate endpoint for document verification
    try {
      const result = await apiClient.post<{ is_verified: boolean; verification_details?: any }>(`/api/documents/${docId}/verify/`, {});
      return result;
    } catch (error) {
      // Fallback if verification endpoint doesn't exist
      return { is_verified: false };
    }
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Get file extension from MIME type
   */
  getFileExtension(mimeType: string): string {
    const mimeToExt: Record<string, string> = {
      'application/pdf': 'pdf',
      'image/jpeg': 'jpg',
      'image/png': 'png',
      'image/gif': 'gif',
      'text/plain': 'txt',
      'application/msword': 'doc',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    };

    return mimeToExt[mimeType] || 'file';
  }

  /**
   * Validate file for upload
   */
  validateFile(file: File): { isValid: boolean; error?: string } {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = [
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/gif',
      'text/plain',
    ];

    if (file.size > maxSize) {
      return {
        isValid: false,
        error: `File size must be less than ${this.formatFileSize(maxSize)}`,
      };
    }

    if (!allowedTypes.includes(file.type)) {
      return {
        isValid: false,
        error: 'File type not supported. Please upload PDF, JPG, PNG, GIF, or TXT files.',
      };
    }

    return { isValid: true };
  }
}

export const documentService = new DocumentService();
