"""
Custom exceptions for DigiLocker mock package.

This module defines all the custom exceptions that can be raised
by the DigiLocker mock client during various operations.
"""


class DigiLockerError(Exception):
    """Base exception class for all DigiLocker-related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationError(DigiLockerError):
    """Raised when authentication fails (invalid credentials, OTP verification, etc.)."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class SessionExpiredError(DigiLockerError):
    """Raised when session token has expired or is invalid."""
    
    def __init__(self, message: str = "Session has expired"):
        super().__init__(message, "SESSION_EXPIRED")


class NotFoundError(DigiLockerError):
    """Raised when requested resource (user, document) is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND")


class DocumentNotFoundError(DigiLockerError):
    """Raised when requested document is not found."""
    
    def __init__(self, message: str = "Document not found"):
        super().__init__(message, "DOCUMENT_NOT_FOUND")


class ValidationError(DigiLockerError):
    """Raised when input validation fails (invalid phone number, OTP format, etc.)."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, "VALIDATION_ERROR")


class RateLimitError(DigiLockerError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT")


class ServiceUnavailableError(DigiLockerError):
    """Raised when DigiLocker service is temporarily unavailable."""
    
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message, "SERVICE_UNAVAILABLE")
