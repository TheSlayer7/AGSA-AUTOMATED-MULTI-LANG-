"""
DigiLocker Mock Package

A mock implementation of DigiLocker API for development and testing purposes.
This package simulates the behavior of the actual DigiLocker service without
making real API calls.

Author: AGSA Development Team
Version: 1.0.0
"""

from .client import DigiLockerClient
from .models import UserProfile, Document, Session
from .exceptions import (
    DigiLockerError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    SessionExpiredError
)

__version__ = "1.0.0"
__author__ = "AGSA Development Team"

__all__ = [
    "DigiLockerClient",
    "UserProfile", 
    "Document",
    "Session",
    "DigiLockerError",
    "AuthenticationError",
    "NotFoundError", 
    "ValidationError",
    "SessionExpiredError"
]
