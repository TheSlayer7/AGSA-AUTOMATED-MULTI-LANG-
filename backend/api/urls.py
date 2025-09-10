"""
URL configuration for API app.

Defines URL patterns for DigiLocker mock API endpoints.
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # DigiLocker Authentication endpoints
    path('digilocker/authenticate/', views.AuthenticateView.as_view(), name='digilocker_authenticate'),
    path('digilocker/verify-otp/', views.VerifyOTPView.as_view(), name='digilocker_verify_otp'),
    path('digilocker/logout/', views.LogoutView.as_view(), name='digilocker_logout'),
    
    # DigiLocker Profile endpoints
    path('digilocker/profile/', views.UserProfileView.as_view(), name='digilocker_profile'),
    path('digilocker/session/', views.SessionInfoView.as_view(), name='digilocker_session'),
    
    # DigiLocker Documents endpoints
    path('digilocker/documents/', views.DocumentListView.as_view(), name='digilocker_documents'),
    path('digilocker/documents/<str:doc_id>/', views.DocumentDownloadView.as_view(), name='digilocker_document_download'),
    
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
]
