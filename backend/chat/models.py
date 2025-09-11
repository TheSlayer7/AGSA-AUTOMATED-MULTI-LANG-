"""
Chat models for storing conversation history and managing AI interactions.
"""

from django.db import models
from django.utils import timezone
from api.models import UserProfile


class ChatSession(models.Model):
    """Model to track chat sessions for users."""
    
    SESSION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, default="New Conversation")
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
    
    def __str__(self):
        return f"{self.user_profile.name} - {self.title}"


class ChatMessage(models.Model):
    """Model to store individual messages in a chat session."""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('status', 'Status'),
        ('summary', 'Summary'),
        ('system', 'System'),
    ]
    
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_id = models.CharField(max_length=100)
    content = models.TextField()
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # AI-specific fields
    intent_category = models.CharField(max_length=100, blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    extracted_entities = models.JSONField(blank=True, null=True)
    action_required = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
    
    def __str__(self):
        return f"{self.session.title} - {self.sender}: {self.content[:50]}..."


class ConversationContext(models.Model):
    """Model to store conversation context and state."""
    
    FLOW_STATES = [
        ('idle', 'Idle'),
        ('eligibility_check', 'Eligibility Check'),
        ('document_verification', 'Document Verification'),
        ('form_filling', 'Form Filling'),
        ('application_submission', 'Application Submission'),
        ('status_inquiry', 'Status Inquiry'),
    ]
    
    session = models.OneToOneField(ChatSession, on_delete=models.CASCADE, related_name='context')
    current_flow = models.CharField(max_length=50, choices=FLOW_STATES, default='idle')
    user_intent = models.CharField(max_length=100, blank=True)
    extracted_data = models.JSONField(default=dict)
    pending_actions = models.JSONField(default=list)
    conversation_summary = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Conversation Context"
        verbose_name_plural = "Conversation Contexts"
    
    def __str__(self):
        return f"{self.session.title} - {self.current_flow}"
