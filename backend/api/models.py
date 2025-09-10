"""
Django models for DigiLocker mock data management.

These models provide a database-backed storage for user profiles and documents,
replacing the hardcoded mock data with dynamic, manageable content.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid
from datetime import datetime, timedelta


class UserRegistration(models.Model):
    """Model to track user registration process and OTP verification."""
    
    phone_validator = RegexValidator(
        regex=r'^\+91\d{10}$',
        message="Phone number must be in format +91xxxxxxxxxx"
    )
    phone_number = models.CharField(max_length=13, validators=[phone_validator], unique=True)
    request_id = models.CharField(max_length=100, blank=True, null=True)  # For tracking OTP requests
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # KYC Information
    name = models.CharField(max_length=200, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    aadhaar_number = models.CharField(max_length=20, blank=True, help_text="Masked Aadhaar number")
    
    kyc_completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "User Registration"
        verbose_name_plural = "User Registrations"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone_number} - {'Verified' if self.is_verified else 'Pending'}"
    
    def is_otp_valid(self):
        """Check if OTP is still valid (within 10 minutes)."""
        return (timezone.now() - self.otp_created_at).total_seconds() < 600
    
    def can_resend_otp(self):
        """Check if OTP can be resent (after 1 minute)."""
        return (datetime.now() - self.otp_created_at.replace(tzinfo=None)).total_seconds() > 60


class UserProfile(models.Model):
    """User profile model for DigiLocker mock users."""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    phone_validator = RegexValidator(
        regex=r'^\+91\d{10}$',
        message="Phone number must be in format +91xxxxxxxxxx"
    )
    phone_number = models.CharField(max_length=13, validators=[phone_validator], unique=True)
    email = models.EmailField(blank=True, null=True)
    aadhaar_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Masked Aadhaar number (e.g., ****-****-1234)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class DocumentType(models.Model):
    """Document type configuration."""
    
    name = models.CharField(max_length=100, unique=True)
    issued_by = models.CharField(max_length=200)
    category = models.CharField(max_length=50, default="identity")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """Document model for storing user documents."""
    
    doc_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    doc_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    
    # File upload
    document_file = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        help_text="Upload document file (PDF, JPG, PNG)"
    )
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-created_at']
        unique_together = ['user_profile', 'document_type']
    
    def __str__(self):
        return f"{self.document_type.name} - {self.user_profile.name}"
    
    @property
    def file_size(self):
        """Get file size in bytes."""
        if self.document_file:
            try:
                return self.document_file.size
            except (FileNotFoundError, OSError):
                # File doesn't exist on disk, return 0
                return 0
        return 0
    
    @property
    def mime_type(self):
        """Get MIME type of the file."""
        if self.document_file:
            name = self.document_file.name.lower()
            if name.endswith('.pdf'):
                return 'application/pdf'
            elif name.endswith(('.jpg', '.jpeg')):
                return 'image/jpeg'
            elif name.endswith('.png'):
                return 'image/png'
        return 'application/octet-stream'


class Session(models.Model):
    """Session model for tracking user sessions."""
    
    session_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_authenticated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id[:8]}... - {self.user_profile.name}"
    
    @property
    def is_valid(self):
        """Check if session is still valid."""
        from django.utils import timezone
        return self.is_authenticated and timezone.now() < self.expires_at


class OTPRequest(models.Model):
    """OTP request model for tracking authentication attempts."""
    
    request_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    phone_number = models.CharField(max_length=13)
    otp_code = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = "OTP Request"
        verbose_name_plural = "OTP Requests"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP {self.request_id[:8]}... - {self.phone_number}"
    
    @property
    def is_valid(self):
        """Check if OTP request is still valid."""
        from django.utils import timezone
        return (
            not self.is_verified and 
            self.attempts < self.max_attempts and 
            timezone.now() < self.expires_at
        )
