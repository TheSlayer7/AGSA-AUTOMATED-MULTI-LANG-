"""
URL configuration for chat app.
"""

from django.urls import path
from .views import ChatSessionView, SendMessageView, EligibilityCheckView, FormAssistanceView

urlpatterns = [
    path('sessions/', ChatSessionView.as_view(), name='chat_sessions'),
    path('send/', SendMessageView.as_view(), name='send_message'),
    path('eligibility/', EligibilityCheckView.as_view(), name='eligibility_check'),
    path('form-assistance/', FormAssistanceView.as_view(), name='form_assistance'),
]
