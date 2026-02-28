"""
Chat serializers for API endpoints.
"""

from rest_framework import serializers
from .models import ChatSession, ChatMessage, ConversationContext


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    class Meta:
        model = ChatMessage
        fields = [
            'message_id', 'content', 'sender', 'message_type', 
            'timestamp', 'intent_category', 'confidence_score', 
            'extracted_entities', 'action_required'
        ]
        read_only_fields = ['timestamp', 'intent_category', 'confidence_score', 'extracted_entities']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'session_id', 'title', 'status', 'created_at', 
            'updated_at', 'last_activity', 'messages', 'message_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_activity']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationContextSerializer(serializers.ModelSerializer):
    """Serializer for conversation context."""
    
    class Meta:
        model = ConversationContext
        fields = [
            'current_flow', 'user_intent', 'extracted_data', 
            'pending_actions', 'conversation_summary', 'last_updated'
        ]
        read_only_fields = ['last_updated']


class SendMessageRequestSerializer(serializers.Serializer):
    """Serializer for sending a message request."""
    
    session_id = serializers.CharField(max_length=100, required=False)
    message = serializers.CharField()
    message_type = serializers.ChoiceField(
        choices=ChatMessage.MESSAGE_TYPE_CHOICES,
        default='text'
    )


class SendMessageResponseSerializer(serializers.Serializer):
    """Serializer for send message response."""
    
    session_id = serializers.CharField()
    user_message = ChatMessageSerializer()
    assistant_message = ChatMessageSerializer()
    context = ConversationContextSerializer()


class ChatAnalysisSerializer(serializers.Serializer):
    """Serializer for AI chat analysis response."""
    
    intent_category = serializers.CharField()
    confidence_score = serializers.FloatField()
    extracted_entities = serializers.JSONField()
    suggested_action = serializers.CharField()
    requires_documents = serializers.BooleanField()
    eligible_schemes = serializers.ListField(child=serializers.CharField(), required=False)
