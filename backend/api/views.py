"""
API views for DigiLocker mock integration.

This module contains all the REST API views for handling DigiLocker
authentication, profile management, and document operations.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from digilocker.client_db import DigiLockerClient
from digilocker.exceptions import (
    DigiLockerError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    SessionExpiredError
)
from .serializers import (
    AuthenticateRequestSerializer,
    AuthenticateResponseSerializer,
    VerifyOTPRequestSerializer,
    VerifyOTPResponseSerializer,
    UserProfileSerializer,
    DocumentSerializer,
    DocumentDownloadSerializer,
    SessionInfoSerializer,
    LogoutResponseSerializer,
    ErrorResponseSerializer
)

# Configure logging
logger = logging.getLogger(__name__)

# Global DigiLocker client instance
digilocker_client = DigiLockerClient()


class BaseAPIView(APIView):
    """Base API view with common error handling."""
    
    permission_classes = [AllowAny]  # For demo purposes
    
    def handle_exception(self, exc):
        """Handle DigiLocker-specific exceptions."""
        if isinstance(exc, AuthenticationError):
            return Response(
                {'error': 'Authentication Failed', 'message': str(exc)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif isinstance(exc, SessionExpiredError):
            return Response(
                {'error': 'Session Expired', 'message': str(exc)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        elif isinstance(exc, NotFoundError):
            return Response(
                {'error': 'Not Found', 'message': str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, ValidationError):
            return Response(
                {'error': 'Validation Error', 'message': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, DigiLockerError):
            return Response(
                {'error': 'DigiLocker Error', 'message': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return super().handle_exception(exc)
    
    def get_session_token(self, request):
        """Extract session token from request headers."""
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            return token[7:]  # Remove 'Bearer ' prefix
        return request.headers.get('X-Session-Token')


class AuthenticateView(BaseAPIView):
    """Handle user authentication via phone number and OTP."""
    
    @extend_schema(
        operation_id="authenticate_user_phone",
        request=AuthenticateRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=AuthenticateResponseSerializer,
                description="OTP sent successfully"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid phone number format"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="User not found"
            )
        },
        summary="Initiate user authentication",
        description="Send OTP to user's phone number for authentication"
    )
    def post(self, request):
        """Initiate authentication by sending OTP."""
        serializer = AuthenticateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        
        try:
            result = digilocker_client.authenticate_user(phone_number)
            logger.info(f"Authentication initiated for {phone_number}")
            return Response(result, status=status.HTTP_200_OK)
        except (ValidationError, NotFoundError) as e:
            logger.warning(f"Authentication failed for {phone_number}: {str(e)}")
            raise


class VerifyOTPView(BaseAPIView):
    """Handle OTP verification and session creation."""
    
    @extend_schema(
        operation_id="verify_otp_create_session",
        request=VerifyOTPRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=VerifyOTPResponseSerializer,
                description="OTP verified successfully"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid OTP format"
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="OTP verification failed"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid request ID"
            )
        },
        summary="Verify OTP and create session",
        description="Verify the OTP code and create an authenticated session"
    )
    def post(self, request):
        """Verify OTP and create authenticated session."""
        serializer = VerifyOTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request_id = serializer.validated_data['request_id']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            result = digilocker_client.verify_otp(request_id, otp_code)
            logger.info(f"OTP verified successfully for request {request_id}")
            return Response(result, status=status.HTTP_200_OK)
        except (AuthenticationError, NotFoundError) as e:
            logger.warning(f"OTP verification failed for request {request_id}: {str(e)}")
            raise


class UserProfileView(BaseAPIView):
    """Handle user profile retrieval."""
    
    @extend_schema(
        operation_id="get_user_profile",
        responses={
            200: OpenApiResponse(
                response=UserProfileSerializer,
                description="User profile retrieved successfully"
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid or expired session"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="User profile not found"
            )
        },
        summary="Get user profile",
        description="Retrieve authenticated user's profile information"
    )
    def get(self, request):
        """Get user profile information."""
        session_token = self.get_session_token(request)
        if not session_token:
            return Response(
                {'error': 'Authentication Required', 'message': 'Session token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            profile = digilocker_client.get_user_profile(session_token)
            logger.info(f"Profile retrieved for session {session_token[:8]}...")
            return Response(profile, status=status.HTTP_200_OK)
        except (SessionExpiredError, NotFoundError) as e:
            logger.warning(f"Profile retrieval failed for session {session_token[:8]}...: {str(e)}")
            raise


class DocumentListView(BaseAPIView):
    """Handle document list retrieval."""
    
    @extend_schema(
        operation_id="list_user_documents",  # Add unique operation ID
        responses={
            200: OpenApiResponse(
                response=DocumentSerializer(many=True),
                description="Documents retrieved successfully"
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid or expired session"
            )
        },
        summary="List user documents",
        description="Retrieve list of user's documents from DigiLocker"
    )
    def get(self, request):
        """Get list of user's documents."""
        session_token = self.get_session_token(request)
        if not session_token:
            return Response(
                {'error': 'Authentication Required', 'message': 'Session token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            documents = digilocker_client.get_documents(session_token)
            logger.info(f"Documents retrieved for session {session_token[:8]}...")
            return Response(documents, status=status.HTTP_200_OK)
        except SessionExpiredError as e:
            logger.warning(f"Document retrieval failed for session {session_token[:8]}...: {str(e)}")
            raise


class DocumentDownloadView(BaseAPIView):
    """Handle document download."""
    
    @extend_schema(
        operation_id="download_document_by_id",  # Add unique operation ID
        responses={
            200: OpenApiResponse(
                response=DocumentDownloadSerializer,
                description="Document downloaded successfully"
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid or expired session"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Document not found"
            )
        },
        summary="Download document",
        description="Download a specific document by ID"
    )
    def get(self, request, doc_id):
        """Download a specific document."""
        session_token = self.get_session_token(request)
        if not session_token:
            return Response(
                {'error': 'Authentication Required', 'message': 'Session token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            document_data = digilocker_client.download_document(session_token, doc_id)
            logger.info(f"Document {doc_id} downloaded for session {session_token[:8]}...")
            return Response(document_data, status=status.HTTP_200_OK)
        except (SessionExpiredError, NotFoundError) as e:
            logger.warning(f"Document download failed for {doc_id}: {str(e)}")
            raise


class SessionInfoView(BaseAPIView):
    """Handle session information retrieval."""
    
    @extend_schema(
        operation_id="get_session_info",
        responses={
            200: OpenApiResponse(
                response=SessionInfoSerializer,
                description="Session information retrieved successfully"
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid or expired session"
            )
        },
        summary="Get session information",
        description="Retrieve information about the current session"
    )
    def get(self, request):
        """Get current session information."""
        session_token = self.get_session_token(request)
        if not session_token:
            return Response(
                {'error': 'Authentication Required', 'message': 'Session token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            session_info = digilocker_client.get_session_info(session_token)
            logger.info(f"Session info retrieved for {session_token[:8]}...")
            return Response(session_info, status=status.HTTP_200_OK)
        except SessionExpiredError as e:
            logger.warning(f"Session info retrieval failed: {str(e)}")
            raise


class LogoutView(BaseAPIView):
    """Handle user logout."""
    
    serializer_class = LogoutResponseSerializer  # Add explicit serializer class
    
    @extend_schema(
        operation_id="logout_user_session",
        request=None,  # No request body needed
        responses={
            200: OpenApiResponse(
                response=LogoutResponseSerializer,
                description="Logged out successfully"
            )
        },
        summary="Logout user",
        description="Logout user and invalidate session"
    )
    def post(self, request):
        """Logout user and invalidate session."""
        session_token = self.get_session_token(request)
        if session_token:
            result = digilocker_client.logout(session_token)
            logger.info(f"User logged out for session {session_token[:8]}...")
            return Response(result, status=status.HTTP_200_OK)
        
        return Response(
            {'status': 'success', 'message': 'Already logged out'},
            status=status.HTTP_200_OK
        )


class HealthCheckView(BaseAPIView):
    """Health check endpoint."""
    
    @extend_schema(
        operation_id="health_check",
        responses={
            200: OpenApiResponse(
                description="Service is healthy"
            )
        },
        summary="Health check",
        description="Check if the API service is running"
    )
    def get(self, request):
        """Simple health check endpoint."""
        return Response({
            'status': 'healthy',
            'service': 'DigiLocker Mock API',
            'version': '1.0.0',
            'timestamp': '2025-09-10T12:00:00Z'
        }, status=status.HTTP_200_OK)
