"""
Secure error handling utilities for production-safe error responses.
"""
import logging
import traceback
import uuid
from typing import Dict, Any, Optional, Tuple
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


class SecureErrorHandler:
    """
    Handles errors securely by logging detailed information server-side
    while returning generic, safe error messages to clients.
    """
    
    # Generic error messages that don't expose internal details
    GENERIC_ERROR_MESSAGES = {
        'validation': 'The provided data is invalid. Please check your input and try again.',
        'authentication': 'Authentication failed. Please check your credentials.',
        'authorization': 'You do not have permission to perform this action.',
        'not_found': 'The requested resource was not found.',
        'server_error': 'An internal error occurred. Please try again later.',
        'database_error': 'A database error occurred. Please try again later.',
        'external_service': 'An external service is temporarily unavailable. Please try again later.',
        'file_upload': 'File upload failed. Please check the file and try again.',
        'rate_limit': 'Too many requests. Please wait before trying again.',
        'maintenance': 'The service is temporarily unavailable for maintenance.',
    }
    
    @classmethod
    def handle_exception(cls, exception: Exception, 
                        error_type: str = 'server_error',
                        context: Optional[Dict[str, Any]] = None,
                        logger_name: str = 'api') -> Tuple[Response, str]:
        """
        Handle an exception securely.
        
        Args:
            exception: The exception that occurred
            error_type: Type of error (key in GENERIC_ERROR_MESSAGES)
            context: Additional context for logging (sanitized)
            logger_name: Name of the logger to use
            
        Returns:
            Tuple of (Response object, error_id for tracking)
        """
        logger = logging.getLogger(logger_name)
        
        # Generate unique error ID for tracking
        error_id = str(uuid.uuid4())[:8]
        
        # Log detailed error information server-side
        cls._log_detailed_error(logger, exception, error_id, context)
        
        # Return generic error response to client
        response = cls._create_safe_response(error_type, error_id)
        
        return response, error_id
    
    @classmethod
    def _log_detailed_error(cls, logger: logging.Logger, 
                           exception: Exception, 
                           error_id: str,
                           context: Optional[Dict[str, Any]] = None):
        """
        Log detailed error information for debugging (server-side only).
        """
        # Basic error information
        error_info = {
            'error_id': error_id,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
        }
        
        # Add sanitized context if provided
        if context:
            safe_context = cls._sanitize_context(context)
            error_info.update(safe_context)
        
        # Log the error with full details
        logger.error(f"Error ID {error_id}: {error_info}")
        
        # In development, also log the traceback
        if settings.DEBUG:
            logger.error(f"Error ID {error_id} - Traceback:", exc_info=True)
        else:
            # In production, log traceback to a separate detailed log
            logger.error(f"Error ID {error_id} - Stack trace: {traceback.format_exc()}")
    
    @classmethod
    def _sanitize_context(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive information from context before logging.
        """
        sensitive_keys = {
            'password', 'token', 'secret', 'key', 'api_key',
            'aadhaar_number', 'phone_number', 'email', 'session_token'
        }
        
        safe_context = {}
        for key, value in context.items():
            if key.lower() in sensitive_keys:
                safe_context[key] = '***REDACTED***'
            elif isinstance(value, str) and len(value) > 100:
                # Truncate very long strings
                safe_context[key] = value[:97] + '...'
            else:
                safe_context[key] = value
        
        return safe_context
    
    @classmethod
    def _create_safe_response(cls, error_type: str, error_id: str) -> Response:
        """
        Create a safe error response for the client.
        """
        # Get generic message
        message = cls.GENERIC_ERROR_MESSAGES.get(error_type, cls.GENERIC_ERROR_MESSAGES['server_error'])
        
        # Determine appropriate HTTP status
        status_map = {
            'validation': status.HTTP_400_BAD_REQUEST,
            'authentication': status.HTTP_401_UNAUTHORIZED,
            'authorization': status.HTTP_403_FORBIDDEN,
            'not_found': status.HTTP_404_NOT_FOUND,
            'rate_limit': status.HTTP_429_TOO_MANY_REQUESTS,
            'server_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'database_error': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'external_service': status.HTTP_503_SERVICE_UNAVAILABLE,
            'file_upload': status.HTTP_400_BAD_REQUEST,
            'maintenance': status.HTTP_503_SERVICE_UNAVAILABLE,
        }
        
        response_status = status_map.get(error_type, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create response data
        response_data = {
            'success': False,
            'error': error_type.replace('_', ' ').title(),
            'message': message,
            'error_id': error_id  # For support/debugging purposes
        }
        
        # In development, add more details
        if settings.DEBUG:
            response_data['debug_note'] = f"Check server logs for error ID: {error_id}"
        
        return Response(response_data, status=response_status)
    
    @classmethod
    def handle_validation_error(cls, errors: Any, 
                               context: Optional[Dict[str, Any]] = None) -> Response:
        """
        Handle validation errors specifically.
        """
        logger = logging.getLogger('api.validation')
        error_id = str(uuid.uuid4())[:8]
        
        # Log validation error details
        logger.warning(f"Validation Error ID {error_id}: {errors}")
        if context:
            safe_context = cls._sanitize_context(context)
            logger.warning(f"Validation Error ID {error_id} - Context: {safe_context}")
        
        # Return generic validation error
        response_data = {
            'success': False,
            'error': 'Validation Error',
            'message': cls.GENERIC_ERROR_MESSAGES['validation'],
            'error_id': error_id
        }
        
        # In development, include field-specific errors (but sanitized)
        if settings.DEBUG and hasattr(errors, 'message_dict'):
            # Sanitize field names and messages
            safe_errors = {}
            for field, messages in errors.message_dict.items():
                if field.lower() not in {'password', 'token', 'secret', 'aadhaar_number'}:
                    safe_errors[field] = messages
            if safe_errors:
                response_data['field_errors'] = safe_errors
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def secure_api_view(error_type: str = 'server_error'):
    """
    Decorator for API views to handle exceptions securely.
    
    Usage:
        @secure_api_view('database_error')
        def my_view(request):
            # view logic
    """
    def decorator(view_func):
        def wrapper(*args, **kwargs):
            try:
                return view_func(*args, **kwargs)
            except Exception as e:
                response, error_id = SecureErrorHandler.handle_exception(
                    e, error_type, context={'view': view_func.__name__}
                )
                return response
        return wrapper
    return decorator


# Convenience functions for common error types
def handle_database_error(exception: Exception, context: Optional[Dict] = None) -> Response:
    """Handle database-related errors."""
    response, _ = SecureErrorHandler.handle_exception(exception, 'database_error', context)
    return response


def handle_external_service_error(exception: Exception, service_name: str) -> Response:
    """Handle external service errors."""
    context = {'service': service_name}
    response, _ = SecureErrorHandler.handle_exception(exception, 'external_service', context)
    return response


def handle_file_upload_error(exception: Exception, filename: Optional[str] = None) -> Response:
    """Handle file upload errors."""
    context = {'operation': 'file_upload'}
    if filename:
        context['filename'] = filename
    response, _ = SecureErrorHandler.handle_exception(exception, 'file_upload', context)
    return response