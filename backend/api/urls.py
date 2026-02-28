"""
URL configuration for API app.

Defines URL patterns for DigiLocker mock API endpoints.
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Sign-up endpoints
    path('auth/signup/', views.SignUpView.as_view(), name='auth_signup'),
    path('auth/verify-signup-otp/', views.VerifySignUpOTPView.as_view(), name='auth_verify_signup_otp'),
    path('auth/signup/complete-kyc/', views.CompleteKYCView.as_view(), name='auth_signup_complete_kyc'),
    
    # Authentication endpoints
    path('auth/request-otp/', views.AuthenticateView.as_view(), name='auth_request_otp'),
    path('auth/verify-otp/', views.VerifyOTPView.as_view(), name='auth_verify_otp'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
    path('auth/profile/', views.UserProfileView.as_view(), name='auth_profile'),
    path('auth/session/', views.SessionInfoView.as_view(), name='auth_session'),
    
    # Documents endpoints
    path('documents/', views.DocumentListView.as_view(), name='documents_list'),
    path('documents/types/', views.DocumentTypesView.as_view(), name='documents_types'),
    path('documents/upload/', views.DocumentUploadView.as_view(), name='documents_upload'),
    path('documents/<str:doc_id>/', views.DocumentDownloadView.as_view(), name='documents_download'),
    
    # Legacy DigiLocker endpoints (for backward compatibility)
    path('digilocker/authenticate/', views.AuthenticateView.as_view(), name='digilocker_authenticate'),
    path('digilocker/verify-otp/', views.VerifyOTPView.as_view(), name='digilocker_verify_otp'),
    path('digilocker/logout/', views.LogoutView.as_view(), name='digilocker_logout'),
    path('digilocker/profile/', views.UserProfileView.as_view(), name='digilocker_profile'),
    path('digilocker/session/', views.SessionInfoView.as_view(), name='digilocker_session'),
    path('digilocker/documents/', views.DocumentListView.as_view(), name='digilocker_documents'),
    path('digilocker/documents/<str:doc_id>/', views.DocumentDownloadView.as_view(), name='digilocker_document_download'),
    
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
]
