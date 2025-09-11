# AGSA Government Agent AI - API Documentation

## Overview
The AGSA Government Agent AI backend provides a comprehensive REST API for authentication, user profile management, and document operations using a mock DigiLocker integration.

## Base URL
- **Development:** `http://127.0.0.1:8000/api/`
- **Production:** TBD

## Authentication
The API uses session-based authentication with phone number and OTP verification.

### Authentication Flow
1. Request OTP using phone number
2. Verify OTP to receive session token
3. Include session token in subsequent requests
4. Session expires after inactivity

## API Endpoints

### Authentication Endpoints

#### 1. Request OTP
**POST** `/api/auth/request-otp/`

Send OTP to the provided phone number for authentication.

**Request Body:**
```json
{
  "phone_number": "+919876543210"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "request_id": "uuid-string",
    "message": "OTP sent successfully"
  },
  "message": "OTP sent successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Validation Error",
  "message": "Invalid phone number format"
}
```

#### 2. Verify OTP
**POST** `/api/auth/verify-otp/`

Verify the OTP and establish a user session.

**Request Body:**
```json
{
  "request_id": "uuid-string",
  "otp_code": "123456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_token": "session-token-string",
    "user_id": "uuid-string",
    "message": "Authentication successful"
  },
  "message": "Authentication successful"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Authentication Failed",
  "message": "Invalid OTP or expired request"
}
```

#### 3. Get User Profile
**GET** `/api/auth/profile/`

Retrieve the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <session_token>
# OR
X-Session-Token: <session_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-string",
    "name": "John Doe",
    "dob": "1990-01-01",
    "gender": "M",
    "address": "123 Main St, City, State 12345",
    "phone_number": "+919876543210",
    "email": "john.doe@email.com",
    "aadhaar_number": "1234-5678-9012",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  "message": "Profile retrieved successfully"
}
```

#### 4. Get Session Info
**GET** `/api/auth/session/`

Get current session information and validity.

**Headers:**
```
Authorization: Bearer <session_token>
# OR
X-Session-Token: <session_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_id": "session-id-string",
    "user_profile": { /* UserProfile object */ },
    "created_at": "2025-01-01T00:00:00Z",
    "last_activity": "2025-01-01T12:00:00Z",
    "expires_at": "2025-01-02T00:00:00Z",
    "is_valid": true
  },
  "message": "Session info retrieved"
}
```

#### 5. Logout
**POST** `/api/auth/logout/`

Invalidate the current session.

**Headers:**
```
Authorization: Bearer <session_token>
# OR
X-Session-Token: <session_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {},
  "message": "Logged out successfully"
}
```

### Document Management Endpoints

#### 1. List User Documents
**GET** `/api/documents/`

Retrieve all documents for the authenticated user.

**Headers:**
```
Authorization: Bearer <session_token>
# OR
X-Session-Token: <session_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "doc_id": "uuid-string",
      "name": "Aadhaar Card",
      "doc_number": "1234-5678-9012",
      "issue_date": "2020-01-01",
      "expiry_date": null,
      "is_verified": true
    }
  ],
  "message": "Documents retrieved successfully"
}
```

#### 2. Get Document Types
**GET** `/api/documents/types/`

Get available document types for upload.

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Aadhaar Card",
      "issued_by": "UIDAI",
      "category": "identity",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "message": "Document types retrieved"
}
```

#### 3. Upload Document
**POST** `/api/documents/upload/`

Upload a new document for the authenticated user.

**Headers:**
```
Authorization: Bearer <session_token>
# OR
X-Session-Token: <session_token>
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```
doc_type: "1"
doc_number: "1234-5678-9012"
issue_date: "2020-01-01"
expiry_date: "2030-01-01" (optional)
file: <file_object>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "doc_id": "uuid-string",
    "user_profile": "uuid-string",
    "document_type": { /* DocumentType object */ },
    "doc_number": "1234-5678-9012",
    "issue_date": "2020-01-01",
    "expiry_date": "2030-01-01",
    "is_verified": false,
    "metadata": {},
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  "message": "Document uploaded successfully"
}
```

#### 4. Download Document
**GET** `/api/documents/{doc_id}/`

Download a specific document.

**Headers:**
```
Authorization: Bearer <session_token>
# OR
X-Session-Token: <session_token>
```

**Response (200 OK):**
```json
{
  "doc_id": "uuid-string",
  "name": "Aadhaar Card",
  "content": "base64-encoded-content",
  "mime_type": "application/pdf",
  "size": 12345,
  "filename": "aadhaar_card.pdf"
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

### Common HTTP Status Codes
- **200 OK:** Request successful
- **400 Bad Request:** Invalid request data
- **401 Unauthorized:** Authentication required or invalid
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

### Error Types
- **Validation Error:** Invalid input data
- **Authentication Failed:** Invalid credentials
- **Session Expired:** Session token expired
- **Not Found:** Requested resource not found
- **DigiLocker Error:** Mock DigiLocker service error

## Security Features

### Session Management
- Sessions expire after 24 hours of inactivity
- Session tokens are securely generated and stored
- Logout invalidates session immediately

### OTP Security
- OTPs expire after 10 minutes
- Maximum 3 OTP requests per phone number per hour
- Test OTP (123456) available for development

### Data Validation
- Phone number format validation
- File size limits (10MB max)
- Supported file types: PDF, JPG, PNG, GIF, TXT

### Rate Limiting
- Authentication endpoints are rate-limited
- Document upload limits per user

## Development Features

### Test OTP
For development and testing purposes, the OTP **123456** is always accepted for any phone number.

### Admin Interface
Access the Django admin interface at:
```
http://127.0.0.1:8000/admin/
```

Default admin credentials:
- Username: admin
- Password: admin

### Sample Data
Use the following script to populate sample data:
```bash
cd backend
uv run tests/populate_sample_data.py
```

## Frontend Integration

### Service Layer
The frontend uses a service layer for API integration:
- `src/services/api.ts` - Base API client
- `src/services/auth.ts` - Authentication service
- `src/services/documents.ts` - Document management service

### Authentication Context
React Context (`src/contexts/AuthContext.tsx`) manages authentication state across the application.

### Example Frontend Usage

#### Login Flow
```typescript
import { useAuth } from '@/contexts/AuthContext';

const { login, verifyOTP } = useAuth();

// Request OTP
const response = await login('+919876543210');
const requestId = response.request_id;

// Verify OTP
await verifyOTP(requestId, '123456');
```

#### Document Operations
```typescript
import { documentService } from '@/services/documents';

// List documents
const documents = await documentService.getUserDocuments();

// Upload document
const uploadRequest = {
  document_type_id: 1,
  doc_number: '1234-5678-9012',
  issue_date: '2020-01-01',
  file: fileObject
};
await documentService.uploadDocument(uploadRequest);

// Download document
const document = await documentService.downloadDocument(docId);
```

## Testing

### Integration Tests
Run comprehensive API tests:
```bash
cd backend
uv run tests/test_complete_flow.py
```

### Frontend Tests
Test TypeScript compilation and build:
```bash
cd frontend
npx tsc --noEmit
npm run build
```

## Deployment Considerations

### Environment Variables
Set the following in production:
- `DEBUG=False`
- `SECRET_KEY=your-secret-key`
- `ALLOWED_HOSTS=your-domain.com`
- `DATABASE_URL=your-database-url`

### Security
- Use HTTPS in production
- Implement proper CORS settings
- Set up rate limiting
- Use environment-specific session secrets
- Implement proper logging and monitoring

### Performance
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up database connection pooling
- Implement caching for frequently accessed data
- Optimize static file serving

---

**Last Updated:** September 11, 2025  
**API Version:** 1.0  
**Backend Framework:** Django 5.2.6 + Django REST Framework  
**Frontend Framework:** React + TypeScript + Vite
