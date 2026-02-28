"""
DigiLocker Mock Client - Database-driven version

This module provides a mock implementation of DigiLocker API client
that works with Django models for dynamic document management.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .exceptions import DigiLockerError, AuthenticationError, DocumentNotFoundError, NotFoundError, ValidationError


# Response models for API compatibility
class AuthResponse:
    def __init__(self, success: bool, session_token: str, expires_at: str, user_id: str):
        self.success = success
        self.session_token = session_token
        self.expires_at = expires_at
        self.user_id = user_id
    
    def to_dict(self):
        return {
            'success': self.success,
            'session_token': self.session_token,
            'expires_at': self.expires_at,
            'user_id': self.user_id
        }


class KYCInfo:
    def __init__(self, user_id: str, name: str, dob: str, gender: str, address: str, 
                 phone_number: str, email: str, aadhaar_number: str):
        self.user_id = user_id
        self.name = name
        self.dob = dob
        self.gender = gender
        self.address = address
        self.phone_number = phone_number
        self.email = email
        self.aadhaar_number = aadhaar_number
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'dob': self.dob,
            'gender': self.gender,
            'address': self.address,
            'phone_number': self.phone_number,
            'email': self.email,
            'aadhaar_number': self.aadhaar_number
        }


class DocumentInfo:
    def __init__(self, doc_id: str, name: str, type: str, issued_by: str, 
                 issue_date: str, expiry_date: Optional[str], size: int, 
                 mime_type: str, is_verified: bool):
        self.doc_id = doc_id
        self.name = name
        self.type = type
        self.issued_by = issued_by
        self.issue_date = issue_date
        self.expiry_date = expiry_date
        self.size = size
        self.mime_type = mime_type
        self.is_verified = is_verified
    
    def to_dict(self):
        return {
            'doc_id': self.doc_id,
            'name': self.name,
            'type': self.type,
            'issued_by': self.issued_by,
            'issue_date': self.issue_date,
            'expiry_date': self.expiry_date,
            'size': self.size,
            'mime_type': self.mime_type,
            'is_verified': self.is_verified
        }


class DigiLockerClient:
    """Mock DigiLocker client with database-backed document management."""
    
    def __init__(self, base_url: str = "https://api.digilocker.gov.in"):
        """Initialize the DigiLocker client."""
        self.base_url = base_url
        self.session_token = None
        self.authenticated_user = None
    
    def _get_django_models(self):
        """Import Django models (lazy import to avoid circular dependencies)."""
        from api.models import UserProfile, Document, Session, OTPRequest
        return UserProfile, Document, Session, OTPRequest
    
    def _generate_otp(self) -> str:
        """Generate a random 6-digit OTP."""
        return ''.join(random.choices(string.digits, k=6))
    
    def _generate_session_token(self) -> str:
        """Generate a random session token."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def request_otp(self, phone_number: str) -> Dict[str, Any]:
        """
        Request OTP for authentication.
        
        Args:
            phone_number: Mobile number in format +91xxxxxxxxxx
            
        Returns:
            Dictionary containing request ID and status
            
        Raises:
            DigiLockerError: If phone number format is invalid
        """
        # Validate phone number format
        if not phone_number.startswith('+91') or len(phone_number) != 13:
            raise DigiLockerError("Invalid phone number format. Use +91xxxxxxxxxx")
        
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        # Check if user exists
        try:
            user_profile = UserProfile.objects.get(phone_number=phone_number, is_active=True)
        except ObjectDoesNotExist:
            raise DigiLockerError("User not found or inactive")
        
        # Generate OTP
        otp_code = self._generate_otp()
        
        # Create OTP request
        otp_request = OTPRequest.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # In a real implementation, you would send SMS here
        print(f"📱 Mock SMS: Your OTP is {otp_code}")
        
        return {
            "request_id": str(otp_request.request_id),
            "message": "OTP sent successfully",
            "expires_in": 600  # 10 minutes
        }
    
    def verify_otp(self, request_id: str, otp: str) -> AuthResponse:
        """
        Verify OTP and authenticate user.
        
        Args:
            request_id: OTP request ID
            otp: OTP code
            
        Returns:
            AuthResponse object
            
        Raises:
            AuthenticationError: If OTP is invalid or expired
        """
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        try:
            otp_request = OTPRequest.objects.get(request_id=request_id)
        except ObjectDoesNotExist:
            raise AuthenticationError("Invalid request ID")
        
        # Check if OTP request is valid
        if not otp_request.is_valid:
            if otp_request.is_verified:
                raise AuthenticationError("OTP already used")
            elif otp_request.attempts >= otp_request.max_attempts:
                raise AuthenticationError("Maximum OTP attempts exceeded")
            else:
                raise AuthenticationError("OTP expired")
        
        # Increment attempts
        otp_request.attempts += 1
        otp_request.save()
        
        # Verify OTP (support test OTP for development)
        if otp == "123456" or otp_request.otp_code == otp:
            # Valid OTP
            pass
        else:
            if otp_request.attempts >= otp_request.max_attempts:
                raise AuthenticationError("Maximum OTP attempts exceeded")
            raise AuthenticationError("Invalid OTP")
        
        # Mark OTP as verified
        otp_request.is_verified = True
        otp_request.save()
        
        # Get user profile
        try:
            user_profile = UserProfile.objects.get(phone_number=otp_request.phone_number)
        except ObjectDoesNotExist:
            raise AuthenticationError("User not found")
        
        # Create session
        session_token = self._generate_session_token()
        session = Session.objects.create(
            user_profile=user_profile,
            session_id=session_token,
            is_authenticated=True,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Store session info
        self.session_token = session_token
        self.authenticated_user = user_profile
        
        return AuthResponse(
            success=True,
            session_token=session_token,
            expires_at=session.expires_at.isoformat(),
            user_id=str(user_profile.user_id)
        )
    
    def get_user_info(self, session_token: str) -> KYCInfo:
        """
        Get user KYC information.
        
        Args:
            session_token: Session token from authentication
            
        Returns:
            KYCInfo object
            
        Raises:
            AuthenticationError: If session is invalid
        """
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        try:
            session = Session.objects.get(session_id=session_token)
        except ObjectDoesNotExist:
            raise AuthenticationError("Invalid session token")
        
        if not session.is_valid:
            raise AuthenticationError("Session expired or invalid")
        
        # Update last activity
        session.last_activity = timezone.now()
        session.save()
        
        user_profile = session.user_profile
        
        return KYCInfo(
            user_id=str(user_profile.user_id),
            name=user_profile.name,
            dob=user_profile.dob.isoformat(),
            gender=user_profile.gender,
            address=user_profile.address,
            phone_number=user_profile.phone_number,
            email=user_profile.email or "",
            aadhaar_number=user_profile.aadhaar_number or ""
        )
    
    def list_documents(self, session_token: str) -> List[DocumentInfo]:
        """
        List all documents for authenticated user.
        
        Args:
            session_token: Session token from authentication
            
        Returns:
            List of DocumentInfo objects
            
        Raises:
            AuthenticationError: If session is invalid
        """
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        try:
            session = Session.objects.get(session_id=session_token)
        except ObjectDoesNotExist:
            raise AuthenticationError("Invalid session token")
        
        if not session.is_valid:
            raise AuthenticationError("Session expired or invalid")
        
        # Update last activity
        session.last_activity = timezone.now()
        session.save()
        
        # Get user documents
        documents = Document.objects.filter(
            user_profile=session.user_profile
        ).select_related('document_type')
        
        document_list = []
        for doc in documents:
            document_list.append(DocumentInfo(
                doc_id=str(doc.doc_id),
                name=doc.document_type.name,
                type=doc.document_type.category,
                issued_by=doc.document_type.issued_by,
                issue_date=doc.issue_date.isoformat(),
                expiry_date=doc.expiry_date.isoformat() if doc.expiry_date else None,
                size=doc.file_size,
                mime_type=doc.mime_type,
                is_verified=doc.is_verified
            ))
        
        return document_list
    
    def download_document(self, session_token: str, doc_id: str) -> Dict[str, Any]:
        """
        Download a document by ID.
        
        Args:
            session_token: Session token from authentication
            doc_id: Document ID
            
        Returns:
            Dictionary containing document data and metadata
            
        Raises:
            AuthenticationError: If session is invalid
            DocumentNotFoundError: If document not found
        """
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        try:
            session = Session.objects.get(session_id=session_token)
        except ObjectDoesNotExist:
            raise AuthenticationError("Invalid session token")
        
        if not session.is_valid:
            raise AuthenticationError("Session expired or invalid")
        
        # Update last activity
        session.last_activity = timezone.now()
        session.save()
        
        # Get document
        try:
            document = Document.objects.get(
                doc_id=doc_id,
                user_profile=session.user_profile
            )
        except ObjectDoesNotExist:
            raise DocumentNotFoundError(f"Document {doc_id} not found")
        
        # Read file content
        if document.document_file:
            try:
                with document.document_file.open('rb') as f:
                    file_content = f.read()
                # Encode to base64 for frontend consumption
                import base64
                encoded_content = base64.b64encode(file_content).decode('utf-8')
            except Exception as e:
                raise DigiLockerError(f"Error reading document file: {str(e)}")
        else:
            raise DocumentNotFoundError("Document file not available")

        return {
            "doc_id": str(document.doc_id),
            "name": document.document_type.name,
            "content": encoded_content,  # Base64 encoded content
            "mime_type": document.mime_type,
            "size": document.file_size,
            "filename": document.document_file.name.split('/')[-1]
        }
    
    def get_session_info(self, session_token: str) -> Dict[str, Any]:
        """
        Get session information.
        
        Args:
            session_token: Session token from authentication
            
        Returns:
            Dictionary containing session information
            
        Raises:
            AuthenticationError: If session is invalid
        """
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        try:
            session = Session.objects.get(session_id=session_token)
        except ObjectDoesNotExist:
            raise AuthenticationError("Invalid session token")
        
        if not session.is_valid:
            raise AuthenticationError("Session expired or invalid")
        
        # Update last activity
        session.last_activity = timezone.now()
        session.save()
        
        return {
            "session_id": str(session.session_id),
            "user_id": str(session.user_profile.user_id),
            "is_authenticated": session.is_authenticated,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "last_activity": session.last_activity.isoformat()
        }
    
    def logout(self, session_token: str) -> Dict[str, Any]:
        """
        Logout user and invalidate session.
        
        Args:
            session_token: Session token from authentication
            
        Returns:
            Dictionary containing logout status
            
        Raises:
            AuthenticationError: If session is invalid
        """
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        try:
            session = Session.objects.get(session_id=session_token)
        except ObjectDoesNotExist:
            raise AuthenticationError("Invalid session token")
        
        # Mark session as not authenticated
        session.is_authenticated = False
        session.save()
        
        # Clear client session info
        self.session_token = None
        self.authenticated_user = None
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    
    def get_document_types(self) -> List[Dict[str, Any]]:
        """
        Get list of available document types.
        
        Returns:
            List of available document types with metadata
        """
        # Return predefined document types that match our models
        document_types = [
            {
                "id": 1,
                "name": "Aadhaar Card",
                "description": "Unique Identification Document",
                "required_fields": ["doc_number", "issue_date"],
                "issuer": "UIDAI"
            },
            {
                "id": 2,
                "name": "PAN Card",
                "description": "Permanent Account Number",
                "required_fields": ["doc_number", "issue_date"],
                "issuer": "Income Tax Department"
            },
            {
                "id": 3,
                "name": "Passport",
                "description": "Indian Passport",
                "required_fields": ["doc_number", "issue_date", "expiry_date"],
                "issuer": "Ministry of External Affairs"
            },
            {
                "id": 4,
                "name": "Driving License",
                "description": "Driving License",
                "required_fields": ["doc_number", "issue_date", "expiry_date"],
                "issuer": "State Transport Department"
            },
            {
                "id": 5,
                "name": "Voter ID",
                "description": "Voter Identity Card",
                "required_fields": ["doc_number", "issue_date"],
                "issuer": "Election Commission of India"
            },
            {
                "id": 6,
                "name": "Ration Card",
                "description": "Ration Card",
                "required_fields": ["doc_number", "issue_date"],
                "issuer": "State Government"
            },
            {
                "id": 7,
                "name": "Birth Certificate",
                "description": "Birth Certificate",
                "required_fields": ["doc_number", "issue_date"],
                "issuer": "Municipal Corporation"
            },
            {
                "id": 8,
                "name": "Marriage Certificate",
                "description": "Marriage Certificate", 
                "required_fields": ["doc_number", "issue_date"],
                "issuer": "Municipal Corporation"
            }
        ]
        
        return document_types
    
    def upload_document(self, phone_number: str, file, doc_type: int, 
                       doc_number: str, issue_date: str, expiry_date: str = None) -> Dict[str, Any]:
        """
        Upload a new document for the user.
        
        Args:
            phone_number: User's phone number
            file: Uploaded file object
            doc_type: Document type ID
            doc_number: Document number
            issue_date: Issue date (YYYY-MM-DD format)
            expiry_date: Expiry date (YYYY-MM-DD format, optional)
            
        Returns:
            Dictionary containing upload result
            
        Raises:
            ValidationError: If input validation fails
            NotFoundError: If user or document type not found
        """
        import os
        import uuid
        from datetime import datetime
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        UserProfile, Document, Session, OTPRequest = self._get_django_models()
        
        # Get user by phone number
        try:
            user = UserProfile.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            raise NotFoundError(f"User with phone number {phone_number} not found")
        
        # Validate document type
        document_types = self.get_document_types()
        doc_type_info = next((dt for dt in document_types if dt['id'] == doc_type), None)
        if not doc_type_info:
            raise ValidationError(f"Invalid document type: {doc_type}")
        
        # Validate file
        if not file:
            raise ValidationError("File is required")
        
        # Check file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            raise ValidationError("File size must be less than 10MB")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt']
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise ValidationError(f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        # Validate dates
        try:
            issue_date_obj = datetime.strptime(issue_date, '%Y-%m-%d').date()
            expiry_date_obj = None
            if expiry_date:
                expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                if expiry_date_obj <= issue_date_obj:
                    raise ValidationError("Expiry date must be after issue date")
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Save file
        file_path = f"documents/{user.user_id}/{doc_id}{file_extension}"
        file_name = default_storage.save(file_path, ContentFile(file.read()))
        
        # Create document record
        document = Document.objects.create(
            doc_id=doc_id,
            doc_type=doc_type,
            name=doc_type_info['name'],
            doc_number=doc_number,
            issue_date=issue_date_obj,
            expiry_date=expiry_date_obj,
            is_verified=True,  # Auto-verify for demo
            file_path=file_name,
            file_size=file.size,
            file_type=file.content_type or 'application/octet-stream',
            user=user
        )
        
        return {
            "doc_id": doc_id,
            "name": doc_type_info['name'],
            "doc_type": doc_type,
            "doc_number": doc_number,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "is_verified": True,
            "file_size": file.size,
            "uploaded_at": datetime.now().isoformat()
        }
