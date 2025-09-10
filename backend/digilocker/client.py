"""
DigiLocker Mock Client

This module provides a mock implementation of DigiLocker API client.
It simulates all the core DigiLocker functionalities including user authentication,
KYC data retrieval, and document management without making actual API calls.
"""

import random
import time
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import uuid

from .models import UserProfile, Document, Session, OTPRequest
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    SessionExpiredError,
    RateLimitError
)


class DigiLockerClient:
    """
    Mock DigiLocker API client for development and testing.
    
    This client simulates the behavior of the actual DigiLocker service
    without making real API calls. It maintains in-memory storage for
    mock data and sessions.
    """
    
    def __init__(self):
        """Initialize the mock client with sample data."""
        self._sessions: Dict[str, Session] = {}
        self._otp_requests: Dict[str, OTPRequest] = {}
        self._users: Dict[str, UserProfile] = {}
        self._documents: Dict[str, List[Document]] = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> None:
        """Initialize mock users and their documents."""
        # Sample users
        sample_users = [
            {
                "user_id": "user_001",
                "name": "Frank Mathew Sajan",
                "dob": "2005-06-19",
                "gender": "M",
                "address": "Thodupuzha, Kerala, India - 685584",
                "phone_number": "+919876543210",
                "email": "frank@example.com",
                "aadhaar_number": "****-****-1234"
            },
            {
                "user_id": "user_002", 
                "name": "Priya Sharma",
                "dob": "1990-03-15",
                "gender": "F",
                "address": "Mumbai, Maharashtra, India - 400001",
                "phone_number": "+919876543211",
                "email": "priya@example.com",
                "aadhaar_number": "****-****-5678"
            },
            {
                "user_id": "user_003",
                "name": "Rajesh Kumar",
                "dob": "1985-12-08", 
                "gender": "M",
                "address": "Delhi, India - 110001",
                "phone_number": "+919876543212",
                "email": "rajesh@example.com",
                "aadhaar_number": "****-****-9012"
            }
        ]
        
        for user_data in sample_users:
            user = UserProfile(**user_data)
            self._users[user.phone_number] = user
            
            # Create sample documents for each user
            user_docs = [
                Document(
                    doc_id=f"doc_{user.user_id}_aadhaar",
                    doc_type="Aadhaar Card",
                    issued_by="Unique Identification Authority of India (UIDAI)",
                    issue_date="2020-01-15",
                    doc_number=user.aadhaar_number,
                    file_size=2048576,  # 2MB
                    mime_type="application/pdf",
                    metadata={"category": "identity", "validity": "lifetime"}
                ),
                Document(
                    doc_id=f"doc_{user.user_id}_pan",
                    doc_type="PAN Card", 
                    issued_by="Income Tax Department",
                    issue_date="2019-06-10",
                    doc_number="ABCDE1234F",
                    file_size=1024768,  # 1MB
                    mime_type="application/pdf",
                    metadata={"category": "identity", "validity": "lifetime"}
                ),
                Document(
                    doc_id=f"doc_{user.user_id}_license",
                    doc_type="Driving License",
                    issued_by="Regional Transport Office",
                    issue_date="2021-03-20",
                    doc_number="DL1420110012345",
                    file_size=1536000,  # 1.5MB
                    mime_type="application/pdf",
                    metadata={"category": "license", "validity": "2031-03-20"}
                )
            ]
            self._documents[user.user_id] = user_docs
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format."""
        # Simple validation for Indian phone numbers
        return (
            phone_number.startswith("+91") and 
            len(phone_number) == 13 and 
            phone_number[3:].isdigit()
        )
    
    def _generate_otp(self) -> str:
        """Generate a random 6-digit OTP."""
        return f"{random.randint(100000, 999999)}"
    
    def _simulate_network_delay(self) -> None:
        """Simulate network delay for realistic behavior."""
        time.sleep(random.uniform(0.5, 1.5))
    
    def authenticate_user(self, phone_number: str) -> Dict[str, Any]:
        """
        Initiate user authentication by sending OTP to phone number.
        
        Args:
            phone_number (str): User's phone number in format +91xxxxxxxxxx
            
        Returns:
            Dict containing request_id and status
            
        Raises:
            ValidationError: If phone number format is invalid
            RateLimitError: If too many requests from the same number
        """
        self._simulate_network_delay()
        
        if not self._validate_phone_number(phone_number):
            raise ValidationError("Invalid phone number format. Use +91xxxxxxxxxx")
        
        # Check if user exists in our mock database
        if phone_number not in self._users:
            raise NotFoundError(f"User with phone number {phone_number} not found")
        
        # Generate OTP request
        otp_code = self._generate_otp()
        otp_request = OTPRequest(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=datetime.now() + timedelta(minutes=5)
        )
        
        self._otp_requests[otp_request.request_id] = otp_request
        
        # In real implementation, OTP would be sent via SMS
        # For mock, we return the OTP in response (DON'T DO THIS IN PRODUCTION!)
        return {
            "request_id": otp_request.request_id,
            "status": "success",
            "message": "OTP sent successfully",
            "expires_in": 300,  # 5 minutes
            "mock_otp": otp_code  # Only for development/testing
        }
    
    def verify_otp(self, request_id: str, otp_code: str) -> Dict[str, Any]:
        """
        Verify OTP and create authenticated session.
        
        Args:
            request_id (str): Request ID from authenticate_user response
            otp_code (str): 6-digit OTP code
            
        Returns:
            Dict containing session token and user info
            
        Raises:
            NotFoundError: If request_id is invalid
            AuthenticationError: If OTP is incorrect or expired
        """
        self._simulate_network_delay()
        
        if request_id not in self._otp_requests:
            raise NotFoundError("Invalid request ID")
        
        otp_request = self._otp_requests[request_id]
        
        if not otp_request.is_valid():
            raise AuthenticationError("OTP has expired or maximum attempts exceeded")
        
        otp_request.increment_attempts()
        
        if otp_request.otp_code != otp_code:
            if otp_request.attempts >= otp_request.max_attempts:
                raise AuthenticationError("Maximum OTP attempts exceeded")
            raise AuthenticationError(f"Invalid OTP. {otp_request.max_attempts - otp_request.attempts} attempts remaining")
        
        # OTP verified successfully
        otp_request.is_verified = True
        user = self._users[otp_request.phone_number]
        
        # Create authenticated session
        session = Session(
            user_id=user.user_id,
            phone_number=user.phone_number,
            is_authenticated=True,
            expires_at=datetime.now() + timedelta(hours=24)  # 24-hour session
        )
        
        self._sessions[session.session_id] = session
        
        return {
            "session_token": session.session_id,
            "user_id": user.user_id,
            "expires_at": session.expires_at.isoformat(),
            "status": "success",
            "message": "Authentication successful"
        }
    
    def get_user_profile(self, session_token: str) -> Dict[str, Any]:
        """
        Retrieve user profile information.
        
        Args:
            session_token (str): Valid session token
            
        Returns:
            Dict containing user profile data
            
        Raises:
            SessionExpiredError: If session is invalid or expired
            NotFoundError: If user not found
        """
        self._simulate_network_delay()
        
        session = self._validate_session(session_token)
        user = None
        
        # Find user by user_id
        for phone, user_profile in self._users.items():
            if user_profile.user_id == session.user_id:
                user = user_profile
                break
        
        if not user:
            raise NotFoundError("User profile not found")
        
        session.refresh()
        return user.to_dict()
    
    def get_documents(self, session_token: str) -> List[Dict[str, Any]]:
        """
        Retrieve list of user's documents.
        
        Args:
            session_token (str): Valid session token
            
        Returns:
            List of document metadata
            
        Raises:
            SessionExpiredError: If session is invalid or expired
        """
        self._simulate_network_delay()
        
        session = self._validate_session(session_token)
        
        if session.user_id not in self._documents:
            return []
        
        documents = self._documents[session.user_id]
        session.refresh()
        
        return [doc.to_dict() for doc in documents]
    
    def download_document(self, session_token: str, doc_id: str) -> Dict[str, Any]:
        """
        Download a specific document.
        
        Args:
            session_token (str): Valid session token
            doc_id (str): Document ID to download
            
        Returns:
            Dict containing document data and content
            
        Raises:
            SessionExpiredError: If session is invalid or expired
            NotFoundError: If document not found
        """
        self._simulate_network_delay()
        
        session = self._validate_session(session_token)
        
        # Find document
        document = None
        if session.user_id in self._documents:
            for doc in self._documents[session.user_id]:
                if doc.doc_id == doc_id:
                    document = doc
                    break
        
        if not document:
            raise NotFoundError(f"Document with ID {doc_id} not found")
        
        # Generate mock PDF content
        mock_pdf_content = self._generate_mock_pdf_content(document)
        
        session.refresh()
        
        return {
            "document": document.to_dict(),
            "content": base64.b64encode(mock_pdf_content).decode('utf-8'),
            "content_type": document.mime_type,
            "encoding": "base64"
        }
    
    def _validate_session(self, session_token: str) -> Session:
        """
        Validate session token and return session object.
        
        Args:
            session_token (str): Session token to validate
            
        Returns:
            Session object if valid
            
        Raises:
            SessionExpiredError: If session is invalid or expired
        """
        if session_token not in self._sessions:
            raise SessionExpiredError("Invalid session token")
        
        session = self._sessions[session_token]
        
        if not session.is_valid():
            # Clean up expired session
            del self._sessions[session_token]
            raise SessionExpiredError("Session has expired")
        
        return session
    
    def _generate_mock_pdf_content(self, document: Document) -> bytes:
        """
        Generate mock PDF content for a document.
        
        Args:
            document (Document): Document to generate content for
            
        Returns:
            bytes: Mock PDF content
        """
        # Simple mock PDF content
        pdf_header = b"%PDF-1.4\n"
        mock_content = f"""
Mock {document.doc_type}
Document ID: {document.doc_id}
Document Number: {document.doc_number}
Issued by: {document.issued_by}
Issue Date: {document.issue_date}

This is a mock document generated for development purposes.
Do not use for official purposes.
        """.encode('utf-8')
        
        # Very basic PDF structure (not a real PDF, just mock content)
        pdf_content = pdf_header + mock_content
        return pdf_content
    
    def logout(self, session_token: str) -> Dict[str, Any]:
        """
        Logout user and invalidate session.
        
        Args:
            session_token (str): Session token to invalidate
            
        Returns:
            Dict containing logout status
        """
        if session_token in self._sessions:
            del self._sessions[session_token]
        
        return {
            "status": "success",
            "message": "Logged out successfully"
        }
    
    def get_session_info(self, session_token: str) -> Dict[str, Any]:
        """
        Get information about current session.
        
        Args:
            session_token (str): Session token
            
        Returns:
            Dict containing session information
            
        Raises:
            SessionExpiredError: If session is invalid or expired
        """
        session = self._validate_session(session_token)
        return session.to_dict()
