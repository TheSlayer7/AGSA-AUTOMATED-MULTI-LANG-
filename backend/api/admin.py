"""
Django admin configuration for DigiLocker mock data management.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, DocumentType, Document, Session, OTPRequest


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    
    list_display = ('name', 'phone_number', 'email', 'gender', 'is_active', 'created_at')
    list_filter = ('gender', 'is_active', 'created_at')
    search_fields = ('name', 'phone_number', 'email', 'aadhaar_number')
    readonly_fields = ('user_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'name', 'dob', 'gender')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Identity', {
            'fields': ('aadhaar_number',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    """Admin interface for DocumentType model."""
    
    list_display = ('name', 'issued_by', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'issued_by')
    readonly_fields = ('created_at',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model."""
    
    list_display = ('document_type', 'user_profile', 'doc_number', 'is_verified', 'file_info', 'created_at')
    list_filter = ('document_type', 'is_verified', 'created_at', 'issue_date')
    search_fields = ('doc_number', 'user_profile__name', 'user_profile__phone_number')
    readonly_fields = ('doc_id', 'file_size', 'mime_type', 'created_at', 'updated_at')
    
    def file_info(self, obj):
        """Display file information."""
        if obj.document_file:
            return format_html(
                '<a href="{}" target="_blank">{}</a><br><small>{} bytes</small>',
                obj.document_file.url,
                obj.document_file.name.split('/')[-1],
                obj.file_size
            )
        return "No file"
    file_info.short_description = "File"
    
    fieldsets = (
        ('Document Information', {
            'fields': ('doc_id', 'document_type', 'user_profile', 'doc_number')
        }),
        ('Validity', {
            'fields': ('issue_date', 'expiry_date', 'is_verified')
        }),
        ('File Upload', {
            'fields': ('document_file', 'file_size', 'mime_type')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin interface for Session model."""
    
    list_display = ('session_short_id', 'user_profile', 'is_authenticated', 'is_valid_status', 'created_at', 'expires_at')
    list_filter = ('is_authenticated', 'created_at', 'expires_at')
    search_fields = ('session_id', 'user_profile__name', 'user_profile__phone_number')
    readonly_fields = ('session_id', 'is_valid', 'created_at', 'last_activity')
    
    def session_short_id(self, obj):
        """Display short session ID."""
        return f"{obj.session_id[:8]}..."
    session_short_id.short_description = "Session ID"
    
    def is_valid_status(self, obj):
        """Display session validity status."""
        return "✓ Valid" if obj.is_valid else "✗ Invalid"
    is_valid_status.short_description = "Status"


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    """Admin interface for OTPRequest model."""
    
    list_display = ('request_short_id', 'phone_number', 'otp_code', 'attempts', 'is_verified', 'is_valid_status', 'created_at')
    list_filter = ('is_verified', 'created_at', 'expires_at')
    search_fields = ('request_id', 'phone_number')
    readonly_fields = ('request_id', 'is_valid', 'created_at')
    
    def request_short_id(self, obj):
        """Display short request ID."""
        return f"{obj.request_id[:8]}..."
    request_short_id.short_description = "Request ID"
    
    def is_valid_status(self, obj):
        """Display OTP validity status."""
        return "✓ Valid" if obj.is_valid else "✗ Invalid"
    is_valid_status.short_description = "Status"
