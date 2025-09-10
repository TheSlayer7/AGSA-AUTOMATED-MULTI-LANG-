"""
Serializers for API app.

Defines DRF serializers for request/response data validation and transformation.
"""

from rest_framework import serializers
from .models import UserRegistration


class AuthenticateRequestSerializer(serializers.Serializer):
    """Serializer for authentication request."""
    phone_number = serializers.CharField(
        max_length=13, 
        min_length=13,
        help_text="Phone number in format +91xxxxxxxxxx"
    )
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if not value.startswith('+91'):
            raise serializers.ValidationError("Phone number must start with +91")
        if not value[3:].isdigit():
            raise serializers.ValidationError("Phone number must contain only digits after +91")
        return value


class AuthenticateResponseSerializer(serializers.Serializer):
    """Serializer for authentication response."""
    request_id = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    expires_in = serializers.IntegerField()
    mock_otp = serializers.CharField(required=False)


class VerifyOTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP verification request."""
    request_id = serializers.CharField(help_text="Request ID from authentication response")
    otp_code = serializers.CharField(
        max_length=6, 
        min_length=6,
        help_text="6-digit OTP code"
    )
    
    def validate_otp_code(self, value):
        """Validate OTP code format."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class VerifyOTPResponseSerializer(serializers.Serializer):
    """Serializer for OTP verification response."""
    session_token = serializers.CharField()
    user_id = serializers.CharField()
    expires_at = serializers.DateTimeField()
    status = serializers.CharField()
    message = serializers.CharField()


class UserProfileSerializer(serializers.Serializer):
    """Serializer for user profile data."""
    user_id = serializers.CharField()
    name = serializers.CharField()
    dob = serializers.DateField()
    gender = serializers.CharField()
    address = serializers.CharField()
    phone_number = serializers.CharField()
    email = serializers.EmailField(allow_null=True, required=False)
    aadhaar_number = serializers.CharField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)


class DocumentSerializer(serializers.Serializer):
    """Serializer for document metadata."""
    id = serializers.CharField()
    type = serializers.CharField()
    issued_by = serializers.CharField()
    issue_date = serializers.DateField()
    doc_number = serializers.CharField()
    file_size = serializers.IntegerField()
    mime_type = serializers.CharField()
    is_verified = serializers.BooleanField()
    metadata = serializers.DictField(required=False)
    created_at = serializers.DateTimeField(required=False)


class DocumentDownloadSerializer(serializers.Serializer):
    """Serializer for document download response."""
    document = DocumentSerializer()
    content = serializers.CharField(help_text="Base64 encoded document content")
    content_type = serializers.CharField()
    encoding = serializers.CharField()


class SessionInfoSerializer(serializers.Serializer):
    """Serializer for session information."""
    session_id = serializers.CharField()
    user_id = serializers.CharField()
    phone_number = serializers.CharField()
    is_authenticated = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    last_activity = serializers.DateTimeField()
    is_valid = serializers.BooleanField()


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer for logout response."""
    status = serializers.CharField()
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    error = serializers.CharField()
    message = serializers.CharField()
    error_code = serializers.CharField(required=False)
    details = serializers.DictField(required=False)


# Sign-up flow serializers
class SignUpRequestSerializer(serializers.Serializer):
    """Serializer for user sign-up request with KYC data."""
    phone_number = serializers.CharField(
        max_length=13, 
        min_length=13,
        help_text="Phone number in format +91xxxxxxxxxx"
    )
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    address = serializers.CharField()
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if not value.startswith('+91'):
            raise serializers.ValidationError("Phone number must start with +91")
        if not value[3:].isdigit():
            raise serializers.ValidationError("Phone number must contain only digits after +91")
        return value


class SignUpResponseSerializer(serializers.Serializer):
    """Serializer for sign-up response."""
    request_id = serializers.CharField()
    message = serializers.CharField()
    user_id = serializers.CharField()


class VerifySignUpOTPRequestSerializer(serializers.Serializer):
    """Serializer for sign-up OTP verification request."""
    request_id = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)


class VerifySignUpOTPResponseSerializer(serializers.Serializer):
    """Serializer for sign-up OTP verification response."""
    success = serializers.BooleanField()
    message = serializers.CharField()
    session_token = serializers.CharField()
    user_id = serializers.CharField()


class CompleteKYCRequestSerializer(serializers.Serializer):
    """Serializer for KYC completion request."""
    name = serializers.CharField(max_length=200)
    dob = serializers.DateField()
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    address = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    aadhaar_number = serializers.CharField(max_length=20, required=False, allow_blank=True)


class CompleteKYCResponseSerializer(serializers.Serializer):
    """Serializer for KYC completion response."""
    status = serializers.CharField()
    message = serializers.CharField()
    user_profile = UserProfileSerializer()
