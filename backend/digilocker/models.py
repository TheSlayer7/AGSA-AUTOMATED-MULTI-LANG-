"""
Data models for DigiLocker mock package.

This module contains dataclasses representing the core entities
used in DigiLocker operations like user profiles, documents, and sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class UserProfile:
    """Represents a user's profile information from DigiLocker."""
    
    user_id: str
    name: str
    dob: str  # Format: YYYY-MM-DD
    gender: str  # M/F/O
    address: str
    phone_number: str
    email: Optional[str] = None
    aadhaar_number: Optional[str] = None  # Masked for privacy
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the profile to a dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "dob": self.dob,
            "gender": self.gender,
            "address": self.address,
            "phone_number": self.phone_number,
            "email": self.email,
            "aadhaar_number": self.aadhaar_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class Document:
    """Represents a document stored in DigiLocker."""
    
    doc_id: str
    doc_type: str  # e.g., "Aadhaar", "PAN", "Driver's License"
    issued_by: str  # Issuing authority
    issue_date: str  # Format: YYYY-MM-DD
    doc_number: str  # Document number (masked for privacy)
    file_size: int  # Size in bytes
    mime_type: str  # e.g., "application/pdf"
    is_verified: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary for JSON serialization."""
        return {
            "id": self.doc_id,
            "type": self.doc_type,
            "issued_by": self.issued_by,
            "issue_date": self.issue_date,
            "doc_number": self.doc_number,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "is_verified": self.is_verified,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class Session:
    """Represents an authenticated session for a user."""
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    phone_number: str = ""
    is_authenticated: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now())
    last_activity: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Check if the session is still valid (not expired)."""
        return self.is_authenticated and datetime.now() < self.expires_at
    
    def refresh(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the session to a dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "is_authenticated": self.is_authenticated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_valid": self.is_valid(),
        }


@dataclass
class OTPRequest:
    """Represents an OTP verification request."""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phone_number: str = ""
    otp_code: str = ""
    attempts: int = 0
    max_attempts: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now())
    is_verified: bool = False
    
    def is_valid(self) -> bool:
        """Check if the OTP request is still valid."""
        return (
            not self.is_verified and 
            self.attempts < self.max_attempts and 
            datetime.now() < self.expires_at
        )
    
    def increment_attempts(self) -> None:
        """Increment the number of verification attempts."""
        self.attempts += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the OTP request to a dictionary."""
        return {
            "request_id": self.request_id,
            "phone_number": self.phone_number,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_verified": self.is_verified,
            "is_valid": self.is_valid(),
        }
