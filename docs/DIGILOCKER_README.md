# DigiLocker Mock API

A comprehensive mock implementation of the DigiLocker API for development and testing purposes. This package provides a complete simulation of DigiLocker's authentication, profile management, and document operations without requiring actual DigiLocker integration.

## 🚀 Features

- **User Authentication**: Phone-based OTP authentication flow
- **Profile Management**: Retrieve user KYC data (name, DOB, gender, address)
- **Document Management**: List and download mock documents (Aadhaar, PAN, Driving License)
- **Session Management**: Secure session handling with token-based authentication
- **RESTful API**: Clean REST endpoints with comprehensive documentation
- **Error Handling**: Proper HTTP status codes and error responses
- **Mock Data**: Pre-populated with realistic sample data for testing

## 📁 Project Structure

```
agsa-gov-agent-ai/
├── backend/                    # Django backend with Python files
│   ├── digilocker/            # Mock DigiLocker Python package
│   │   ├── __init__.py
│   │   ├── client.py          # Main client with mock API operations
│   │   ├── models.py          # Data models (UserProfile, Document, Session)
│   │   └── exceptions.py      # Custom exceptions
│   ├── agsa/
│   │   ├── settings.py        # Django settings with CORS & DRF
│   │   └── urls.py            # Main URL configuration
│   ├── api/
│   │   ├── views.py           # DRF API views
│   │   ├── serializers.py     # Request/response serializers
│   │   ├── urls.py            # API URL patterns
│   │   └── requirements.txt   # Python dependencies
│   ├── setup.py               # Package setup for digilocker
│   ├── test_api.py            # API testing script
│   ├── pyproject.toml         # UV project configuration
│   ├── uv.lock                # UV lock file
│   └── manage.py              # Django management script
├── src/                       # React frontend
├── public/                    # Static assets
└── README.md                  # Main project documentation
```

## 🛠 Installation & Setup

### 1. Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### 2. Environment Setup

```bash
# Navigate to the project root
cd agsa-gov-agent-ai

# Create and activate virtual environment (if not already done)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Install the digilocker package in development mode
pip install -e .
```

### 3. Django Setup

```bash
# From the backend directory
cd backend  # if not already there

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔗 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/digilocker/authenticate/` | Send OTP to phone number |
| POST | `/api/digilocker/verify-otp/` | Verify OTP and get session token |
| POST | `/api/digilocker/logout/` | Logout and invalidate session |

### Profile & Session

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/digilocker/profile/` | Get user profile information |
| GET | `/api/digilocker/session/` | Get current session info |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/digilocker/documents/` | List user's documents |
| GET | `/api/digilocker/documents/{doc_id}/` | Download specific document |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/` | Health check |

## 📋 Example API Usage

### 1. Authentication Flow

```bash
# Step 1: Request OTP
curl -X POST http://localhost:8000/api/digilocker/authenticate/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'

# Response:
# {
#   "request_id": "abc-123-def",
#   "status": "success", 
#   "message": "OTP sent successfully",
#   "expires_in": 300,
#   "mock_otp": "123456"
# }

# Step 2: Verify OTP
curl -X POST http://localhost:8000/api/digilocker/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "abc-123-def",
    "otp_code": "123456"
  }'

# Response:
# {
#   "session_token": "xyz-789-session",
#   "user_id": "user_001",
#   "expires_at": "2025-09-11T12:00:00Z",
#   "status": "success",
#   "message": "Authentication successful"
# }
```

### 2. Profile Retrieval

```bash
curl -X GET http://localhost:8000/api/digilocker/profile/ \
  -H "Authorization: Bearer xyz-789-session"

# Response:
# {
#   "user_id": "user_001",
#   "name": "Frank Mathew Sajan",
#   "dob": "2005-06-19",
#   "gender": "M",
#   "address": "Thodupuzha, Kerala, India - 685584",
#   "phone_number": "+919876543210",
#   "email": "frank@example.com",
#   "aadhaar_number": "****-****-1234"
# }
```

### 3. Document Operations

```bash
# List documents
curl -X GET http://localhost:8000/api/digilocker/documents/ \
  -H "Authorization: Bearer xyz-789-session"

# Response:
# [
#   {
#     "id": "doc_user_001_aadhaar",
#     "type": "Aadhaar Card",
#     "issued_by": "Unique Identification Authority of India (UIDAI)",
#     "issue_date": "2020-01-15",
#     "doc_number": "****-****-1234",
#     "file_size": 2048576,
#     "mime_type": "application/pdf",
#     "is_verified": true
#   },
#   {
#     "id": "doc_user_001_pan", 
#     "type": "PAN Card",
#     "issued_by": "Income Tax Department",
#     "issue_date": "2019-06-10",
#     "doc_number": "ABCDE1234F",
#     "file_size": 1024768,
#     "mime_type": "application/pdf",
#     "is_verified": true
#   }
# ]

# Download specific document
curl -X GET http://localhost:8000/api/digilocker/documents/doc_user_001_aadhaar/ \
  -H "Authorization: Bearer xyz-789-session"

# Response:
# {
#   "document": { /* document metadata */ },
#   "content": "JVBERi0xLjQ...", // base64 encoded content
#   "content_type": "application/pdf",
#   "encoding": "base64"
# }
```

## 🧪 Sample Test Users

The mock API comes with pre-populated test users:

| Phone Number | Name | User ID | Available Documents |
|-------------|------|---------|-------------------|
| +919876543210 | Frank Mathew Sajan | user_001 | Aadhaar, PAN, Driving License |
| +919876543211 | Priya Sharma | user_002 | Aadhaar, PAN, Driving License |
| +919876543212 | Rajesh Kumar | user_003 | Aadhaar, PAN, Driving License |

For any of these users, you can use any 6-digit OTP (the mock returns the OTP in the authentication response).

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOW_ALL_ORIGINS=True
```

### Django Settings

Key settings in `backend/agsa/settings.py`:

```python
# Enable CORS for frontend integration
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'AGSA DigiLocker Mock API',
    'DESCRIPTION': 'Mock implementation of DigiLocker API',
    'VERSION': '1.0.0',
}
```

## 🚨 Error Handling

The API returns appropriate HTTP status codes:

| Status Code | Description |
|------------|-------------|
| 200 | Success |
| 400 | Bad Request (validation errors) |
| 401 | Unauthorized (invalid/expired session) |
| 404 | Not Found (user/document not found) |
| 500 | Internal Server Error |

Error response format:
```json
{
  "error": "Authentication Failed",
  "message": "Invalid OTP. 2 attempts remaining",
  "error_code": "AUTH_ERROR"
}
```

## 🔐 Security Considerations

This is a **MOCK IMPLEMENTATION** for development only:

- ⚠️ **DO NOT use in production**
- ⚠️ **OTP codes are returned in API responses** (for testing convenience)
- ⚠️ **No real authentication or encryption**
- ⚠️ **All data is stored in memory** (lost on restart)

For production:
- Implement proper OTP delivery (SMS gateway)
- Use secure session storage (Redis/database)
- Add proper authentication middleware
- Enable HTTPS and proper CORS configuration
- Implement rate limiting and request validation

## 🧰 Development Tools

### Running Tests

```bash
# Run Django tests
python manage.py test

# Test specific app
python manage.py test api
```

### Code Quality

```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black .

# Check linting
flake8 .

# Sort imports
isort .
```

## 🔄 Integration with Frontend

To integrate with your React frontend:

1. **Update API Base URL**: Set `VITE_API_BASE_URL=http://localhost:8000` in your frontend `.env`

2. **Authentication Flow**:
   ```javascript
   // Replace mock authentication in src/pages/Auth.tsx
   const response = await fetch('/api/digilocker/authenticate/', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ phone_number: '+919876543210' })
   });
   ```

3. **Session Management**:
   ```javascript
   // Store session token and use in subsequent requests
   localStorage.setItem('sessionToken', response.session_token);
   
   // Add to request headers
   headers: {
     'Authorization': `Bearer ${sessionToken}`
   }
   ```

## 📊 Monitoring & Logging

The API includes comprehensive logging:

```python
# View logs in development
tail -f logs/django.log

# Key log events:
# - Authentication attempts
# - Session creation/validation
# - Document access
# - Error conditions
```

## 🚀 Deployment

### Development
```bash
python manage.py runserver 0.0.0.0:8000
```

### Production (Docker)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "agsa.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 📞 Support

For questions or issues:

1. Check the API documentation at `/api/docs/`
2. Review the error response messages
3. Ensure proper session token usage
4. Verify request payload format

## 📄 License

This project is for development and testing purposes only. Not licensed for production use.

---

**Note**: This is a mock implementation designed for development. Replace with actual DigiLocker integration for production deployment.
