"""
API views for DigiLocker mock integration.

This module contains all the REST API views for handling DigiLocker
authentication, profile management, and document operations.
"""

import logging
import random
import string
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
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
from .models import UserRegistration, UserProfile
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
    ErrorResponseSerializer,
    SignUpRequestSerializer,
    SignUpResponseSerializer,
    VerifySignUpOTPRequestSerializer,
    VerifySignUpOTPResponseSerializer,
    CompleteKYCRequestSerializer,
    CompleteKYCResponseSerializer
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


def generate_otp():
    """Generate a random 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))


class SignUpView(BaseAPIView):
    """Handle user sign-up with phone number."""
    
    @extend_schema(
        operation_id="user_signup",
        request=SignUpRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=SignUpResponseSerializer,
                description="Sign-up OTP sent successfully"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid phone number or user already exists"
            )
        },
        summary="User sign-up",
        description="Start the sign-up process by sending OTP to phone number"
    )
    def post(self, request):
        """Start user sign-up process with KYC data."""
        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        name = serializer.validated_data['name']
        email = serializer.validated_data.get('email', '')
        date_of_birth = serializer.validated_data['date_of_birth']
        gender = serializer.validated_data['gender']
        address = serializer.validated_data['address']
        
        # Check if user already exists in UserProfile
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            return Response(
                {'error': 'User already exists', 'message': 'Phone number is already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate OTP
        otp = generate_otp()
        
        # Create or update registration record with KYC data
        registration, created = UserRegistration.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'otp': otp, 
                'attempts': 0, 
                'is_verified': False,
                'name': name,
                'email': email,
                'dob': date_of_birth,
                'gender': gender,
                'address': address,
                'kyc_completed': True  # Since we're collecting KYC data upfront
            }
        )
        
        if not created:
            # Update existing registration with new KYC data
            registration.otp = otp
            registration.otp_created_at = timezone.now()
            registration.attempts = 0
            registration.is_verified = False
            registration.name = name
            registration.email = email
            registration.dob = date_of_birth
            registration.gender = gender
            registration.address = address
            registration.kyc_completed = True
            registration.save()
        
        # Generate a temporary request ID for this registration
        request_id = str(uuid.uuid4())
        
        # Store request_id in session or cache for verification
        # For simplicity, we'll use the registration ID as request_id
        registration.request_id = request_id
        registration.save()
        
        logger.info(f"Sign-up OTP generated for {phone_number}")
        
        # Mock SMS sending
        print(f"📱 Mock SMS: Your AGSA registration OTP is {otp}")
        
        return Response({
            'request_id': request_id,
            'message': 'OTP sent to your phone number for registration',
            'user_id': str(registration.id)
        }, status=status.HTTP_200_OK)


class VerifySignUpOTPView(BaseAPIView):
    """Handle sign-up OTP verification."""
    
    @extend_schema(
        operation_id="verify_signup_otp",
        request=VerifySignUpOTPRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=VerifySignUpOTPResponseSerializer,
                description="OTP verified successfully"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid OTP or expired"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Registration not found"
            )
        },
        summary="Verify sign-up OTP",
        description="Verify the sign-up OTP and create a temporary session for KYC"
    )
    def post(self, request):
        """Verify sign-up OTP and create user profile."""
        serializer = VerifySignUpOTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        request_id = serializer.validated_data['request_id']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            registration = UserRegistration.objects.get(request_id=request_id)
        except UserRegistration.DoesNotExist:
            return Response(
                {'error': 'Registration not found', 'message': 'Please start sign-up process again'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if OTP is valid
        if not registration.is_otp_valid():
            return Response(
                {'error': 'OTP expired', 'message': 'Please request a new OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check attempts
        if registration.attempts >= 3:
            return Response(
                {'error': 'Too many attempts', 'message': 'Please request a new OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify OTP
        if registration.otp != otp_code:
            registration.attempts += 1
            registration.save()
            return Response(
                {'error': 'Invalid OTP', 'message': 'Please enter the correct OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # OTP verified successfully, create user profile
        registration.is_verified = True
        registration.save()
        
        # Create UserProfile from registration data
        user_profile = UserProfile.objects.create(
            user_id=str(uuid.uuid4()),
            name=registration.name,
            dob=registration.dob,
            gender=registration.gender,
            address=registration.address,
            phone_number=registration.phone_number,
            email=registration.email,
            is_active=True
        )
        
        # Create a new OTP request for session creation
        from api.models import OTPRequest
        session_otp_request = OTPRequest.objects.create(
            phone_number=user_profile.phone_number,
            otp_code="123456",  # Auto-verified for registration
            is_verified=True,
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Use verify_otp to create session
        try:
            auth_response = digilocker_client.verify_otp(
                str(session_otp_request.request_id),
                "123456"
            )
            session_token = auth_response.session_token
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            session_token = "temp_session_" + str(uuid.uuid4())[:8]
        
        logger.info(f"User registration completed for {registration.phone_number}")
        
        return Response({
            'success': True,
            'message': 'Registration completed successfully',
            'session_token': session_token,
            'user_id': user_profile.user_id
        }, status=status.HTTP_200_OK)


class CompleteKYCView(BaseAPIView):
    """Handle KYC completion for new users."""
    
    @extend_schema(
        operation_id="complete_kyc",
        request=CompleteKYCRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=CompleteKYCResponseSerializer,
                description="KYC completed and user profile created"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Invalid KYC data or session"
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Registration not found"
            )
        },
        summary="Complete KYC information",
        description="Complete the KYC process and create user profile"
    )
    def post(self, request):
        """Complete KYC and create user profile."""
        # Get session token from header
        session_token = self.get_session_token(request)
        if not session_token:
            return Response(
                {'error': 'Session required', 'message': 'Please provide session token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CompleteKYCRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # For demo purposes, we'll use phone number from request data
        # In a real app, you'd get it from the session token
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response(
                {'error': 'Phone number required', 'message': 'Please provide phone number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            registration = UserRegistration.objects.get(
                phone_number=phone_number,
                is_verified=True
            )
        except UserRegistration.DoesNotExist:
            return Response(
                {'error': 'Invalid session', 'message': 'Please verify your phone number first'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update registration with KYC data
        registration.name = serializer.validated_data['name']
        registration.dob = serializer.validated_data['dob']
        registration.gender = serializer.validated_data['gender']
        registration.address = serializer.validated_data['address']
        registration.email = serializer.validated_data.get('email', '')
        registration.aadhaar_number = serializer.validated_data.get('aadhaar_number', '')
        registration.kyc_completed = True
        registration.save()
        
        # Create UserProfile
        user_profile = UserProfile.objects.create(
            user_id=str(uuid.uuid4()),
            name=registration.name,
            dob=registration.dob,
            gender=registration.gender,
            address=registration.address,
            phone_number=registration.phone_number,
            email=registration.email,
            aadhaar_number=registration.aadhaar_number
        )
        
        logger.info(f"KYC completed for {phone_number}")
        
        profile_serializer = UserProfileSerializer(user_profile)
        
        return Response({
            'status': 'success',
            'message': 'KYC completed successfully. You can now log in.',
            'user_profile': profile_serializer.data
        }, status=status.HTTP_201_CREATED)


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
            result = digilocker_client.request_otp(phone_number)
            logger.info("Authentication initiated for a user phone number")
            return Response(result, status=status.HTTP_200_OK)
        except DigiLockerError as e:
            error_message = str(e)
            if "User not found or inactive" in error_message:
                logger.warning("Authentication failed: User not registered for submitted phone number")
                return Response(
                    {
                        'error': 'User not found', 
                        'message': 'Phone number not registered. Please sign up first.',
                        'action': 'signup_required'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                logger.warning(f"Authentication failed: {error_message}")
                return Response(
                    {'error': 'Authentication failed', 'message': error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValidationError, NotFoundError) as e:
            logger.warning(f"Authentication failed: {str(e)}")
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
            # Convert AuthResponse object to dictionary for JSON serialization
            if hasattr(result, 'to_dict'):
                return Response(result.to_dict(), status=status.HTTP_200_OK)
            else:
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
            profile = digilocker_client.get_user_info(session_token)
            logger.info(f"Profile retrieved for session {session_token[:8]}...")
            # Convert KYCInfo object to dictionary for JSON serialization
            if hasattr(profile, 'to_dict'):
                return Response(profile.to_dict(), status=status.HTTP_200_OK)
            else:
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
            documents = digilocker_client.list_documents(session_token)
            logger.info(f"Documents retrieved for session {session_token[:8]}...")
            # Convert DocumentInfo objects to dictionaries for JSON serialization
            if documents and hasattr(documents[0], 'to_dict'):
                documents_dict = [doc.to_dict() for doc in documents]
            else:
                documents_dict = documents if documents else []
            
            return Response({
                'success': True,
                'data': documents_dict,
                'message': f'Retrieved {len(documents_dict)} documents'
            }, status=status.HTTP_200_OK)
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


class DocumentTypesView(BaseAPIView):
    """Get available document types."""
    
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Document types retrieved successfully"
            ),
            500: ErrorResponseSerializer
        },
        summary="Get document types",
        description="Retrieve list of available document types for upload"
    )
    def get(self, request):
        """Get all available document types."""
        try:
            document_types = digilocker_client.get_document_types()
            return Response({
                'success': True,
                'data': document_types,
                'message': 'Document types retrieved successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting document types: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve document types',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentUploadView(BaseAPIView):
    """Upload a new document."""
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary', 'description': 'Document file to upload'},
                    'doc_type': {'type': 'integer', 'description': 'Document type ID'},
                    'doc_number': {'type': 'string', 'description': 'Document number'},
                    'issue_date': {'type': 'string', 'format': 'date', 'description': 'Issue date (YYYY-MM-DD)'},
                    'expiry_date': {'type': 'string', 'format': 'date', 'description': 'Expiry date (YYYY-MM-DD, optional)'},
                },
                'required': ['file', 'doc_type', 'doc_number', 'issue_date']
            }
        },
        responses={
            201: OpenApiResponse(
                description="Document uploaded successfully"
            ),
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer
        },
        summary="Upload document",
        description="Upload a new document to the user's profile"
    )
    def post(self, request):
        """Upload a new document."""
        session_token = self.get_session_token(request)
        if not session_token:
            return Response(
                {'error': 'Authentication Required', 'message': 'Session token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            # Get form data
            uploaded_file = request.FILES.get('file')
            doc_type = request.data.get('doc_type')
            doc_number = request.data.get('doc_number')
            issue_date = request.data.get('issue_date')
            expiry_date = request.data.get('expiry_date')
            
            # Validate required fields
            if not all([uploaded_file, doc_type, doc_number, issue_date]):
                return Response({
                    'success': False,
                    'error': 'Missing required fields',
                    'message': 'file, doc_type, doc_number, and issue_date are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user profile from session token
            try:
                user_profile = digilocker_client.get_user_info(session_token)
                phone_number = user_profile.phone_number if hasattr(user_profile, 'phone_number') else '+919876543210'
            except Exception:
                phone_number = '+919876543210'  # Fallback for demo
            
            # Upload document
            result = digilocker_client.upload_document(
                phone_number=phone_number,
                file=uploaded_file,
                doc_type=int(doc_type),
                doc_number=doc_number,
                issue_date=issue_date,
                expiry_date=expiry_date
            )
            
            return Response({
                'success': True,
                'data': result,
                'message': 'Document uploaded successfully'
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'success': False,
                'error': 'Validation error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return Response({
                'success': False,
                'error': 'Upload failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
