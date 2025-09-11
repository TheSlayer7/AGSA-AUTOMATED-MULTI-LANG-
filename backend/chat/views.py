"""
Chat views for handling AI-powered conversations.
"""

import uuid
import logging
from typing import Dict, Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from api.models import UserProfile
from .models import ChatSession, ChatMessage, ConversationContext
from .serializers import (
    ChatSessionSerializer, ChatMessageSerializer, ConversationContextSerializer,
    SendMessageRequestSerializer, SendMessageResponseSerializer, ChatAnalysisSerializer
)
from .ai_service import gemini_service

logger = logging.getLogger(__name__)


class ChatSessionView(APIView):
    """Handle chat session management."""
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id="get_chat_sessions",
        responses={
            200: OpenApiResponse(
                response=ChatSessionSerializer(many=True),
                description="User's chat sessions"
            )
        },
        summary="Get user's chat sessions",
        description="Retrieve all chat sessions for the authenticated user"
    )
    def get(self, request):
        """Get user's chat sessions."""
        try:
            # For demo purposes, we'll use a test user profile
            # Authentication is optional for now
            user_profile, created = UserProfile.objects.get_or_create(
                phone_number='+919999999999',
                defaults={
                    'user_id': str(uuid.uuid4()),
                    'name': 'Test User',
                    'is_active': True
                }
            )
            
            sessions = ChatSession.objects.filter(user_profile=user_profile, status='active')
            serializer = ChatSessionSerializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting chat sessions: {e}")
            return Response(
                {'error': 'Failed to retrieve chat sessions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        operation_id="create_chat_session",
        responses={
            201: OpenApiResponse(
                response=ChatSessionSerializer,
                description="New chat session created"
            )
        },
        summary="Create new chat session",
        description="Create a new chat session for the user"
    )
    def post(self, request):
        """Create a new chat session."""
        try:
            # For demo purposes, use test user profile
            user_profile, created = UserProfile.objects.get_or_create(
                phone_number='+919999999999',
                defaults={
                    'user_id': str(uuid.uuid4()),
                    'name': 'Test User',
                    'is_active': True
                }
            )
            
            # Create new session
            session = ChatSession.objects.create(
                user_profile=user_profile,
                session_id=str(uuid.uuid4()),
                title="New Conversation"
            )
            
            # Create conversation context
            ConversationContext.objects.create(session=session)
            
            # Add welcome message
            welcome_msg = ChatMessage.objects.create(
                session=session,
                message_id=str(uuid.uuid4()),
                content="Hello! I'm your AGSA assistant. I'm here to help you navigate government services and find schemes you're eligible for. What would you like assistance with today?",
                sender='assistant',
                message_type='text'
            )
            
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return Response(
                {'error': 'Failed to create chat session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendMessageView(APIView):
    """Handle sending messages in chat."""
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id="send_chat_message",
        request=SendMessageRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=SendMessageResponseSerializer,
                description="Message sent and AI response generated"
            )
        },
        summary="Send chat message",
        description="Send a message and get AI assistant response"
    )
    def post(self, request):
        """Send a message and get AI response."""
        try:
            serializer = SendMessageRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get or create session
            session_id = serializer.validated_data.get('session_id')
            message_content = serializer.validated_data['message']
            message_type = serializer.validated_data['message_type']
            
            # Get user profile
            user_profile, created = UserProfile.objects.get_or_create(
                phone_number='+919999999999',
                defaults={
                    'user_id': str(uuid.uuid4()),
                    'name': 'Test User',
                    'is_active': True
                }
            )
            
            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id, user_profile=user_profile)
                except ChatSession.DoesNotExist:
                    session = self._create_new_session(user_profile)
            else:
                session = self._create_new_session(user_profile)
            
            # Save user message
            user_message = ChatMessage.objects.create(
                session=session,
                message_id=str(uuid.uuid4()),
                content=message_content,
                sender='user',
                message_type=message_type
            )
            
            # Get AI response from Gemini
            try:
                # Get conversation history for context
                recent_messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:5]
                
                # Build user context (you can expand this with actual user profile data)
                user_context = {
                    'name': user_profile.name if hasattr(user_profile, 'name') else 'User',
                    'phone': user_profile.phone_number,
                    'documents': []  # Add actual documents from user profile if available
                }
                
                # Log before calling AI service
                logger.info(f"Calling Gemini service for message: {message_content[:50]}...")
                
                # Generate AI response using analyze_user_message
                ai_response = gemini_service.analyze_user_message(
                    message=message_content,
                    user_context=user_context
                )
                
                # Log the response
                logger.info(f"Gemini service returned: {ai_response}")
                
                ai_response_content = ai_response.get('response', 'I apologize, but I am having trouble processing your request right now.')
                intent_category = ai_response.get('category', 'ASK')
                confidence_score = ai_response.get('confidence', 0.7)
                action_required = len(ai_response.get('action_plan', [])) > 0
                
            except Exception as e:
                print(f"DEBUG: Exception in Gemini call: {e}")
                logger.error(f"Gemini AI error: {e}")
                # Show service unavailable message instead of dummy responses
                ai_response_content = "I'm currently unable to process your request due to a service interruption. Please try again in a few moments or contact support for assistance."
                intent_category = 'llm_unavailable'
                confidence_score = 0.0
                action_required = False
            
            # Create assistant message
            assistant_message = ChatMessage.objects.create(
                session=session,
                message_id=str(uuid.uuid4()),
                content=ai_response_content,
                sender='assistant',
                message_type='text',
                intent_category=intent_category,
                confidence_score=confidence_score,
                action_required=action_required
            )
            
            # Update session
            session.last_activity = user_message.timestamp
            session.title = "Government Services Chat"
            session.save()
            
            # Get or create conversation context
            context, created = ConversationContext.objects.get_or_create(
                session=session,
                defaults={
                    'current_flow': 'idle',
                    'user_intent': 'general_inquiry',
                    'extracted_data': {},
                    'pending_actions': []
                }
            )
            
            # Serialize response
            response_data = {
                'session_id': session.session_id,
                'user_message': ChatMessageSerializer(user_message).data,
                'assistant_message': ChatMessageSerializer(assistant_message).data,
                'context': ConversationContextSerializer(context).data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _create_new_session(self, user_profile):
        """Create a new chat session."""
        session = ChatSession.objects.create(
            user_profile=user_profile,
            session_id=str(uuid.uuid4()),
            title="New Conversation"
        )
        return session

class EligibilityCheckView(APIView):
    """Handle scheme eligibility checks."""
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id="check_scheme_eligibility",
        responses={
            200: OpenApiResponse(
                response=ChatAnalysisSerializer,
                description="Eligibility analysis results"
            )
        },
        summary="Check scheme eligibility",
        description="Check user's eligibility for various government schemes"
    )
    def post(self, request):
        """Check eligibility for government schemes."""
        try:
            # Get user profile
            user_profile, created = UserProfile.objects.get_or_create(
                phone_number='+919999999999',
                defaults={
                    'user_id': str(uuid.uuid4()),
                    'name': 'Test User',
                    'is_active': True
                }
            )
            
            # Prepare user data for eligibility check
            user_data = {
                'name': user_profile.name,
                'phone': user_profile.phone_number,
                'email': user_profile.email,
                'address': user_profile.address,
                'age': self._calculate_age(user_profile.dob) if user_profile.dob else None,
                'gender': user_profile.gender,
                'documents': self._get_user_documents(user_profile)
            }
            
            # Get AI eligibility analysis
            eligible_schemes = gemini_service.check_scheme_eligibility(user_data)
            
            return Response({
                'user_profile': user_data,
                'eligible_schemes': eligible_schemes,
                'total_schemes_checked': len(eligible_schemes),
                'eligible_count': len([s for s in eligible_schemes if s.get('eligible', False)])
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking eligibility: {e}")
            return Response(
                {'error': 'Failed to check eligibility'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_age(self, dob):
        """Calculate age from date of birth."""
        try:
            from datetime import date
            today = date.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            return None
    
    def _get_user_documents(self, user_profile):
        """Get list of user's documents."""
        return ['Aadhaar Card', 'PAN Card', 'Income Certificate']


class FormAssistanceView(APIView):
    """Handle form filling assistance."""
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id="get_form_assistance",
        responses={
            200: OpenApiResponse(
                description="Form filling assistance"
            )
        },
        summary="Get form assistance",
        description="Get AI assistance for filling government forms"
    )
    def post(self, request):
        """Get form filling assistance."""
        try:
            scheme_name = request.data.get('scheme_name', 'General Application')
            
            # Get user profile
            user_profile, created = UserProfile.objects.get_or_create(
                phone_number='+919999999999',
                defaults={
                    'user_id': str(uuid.uuid4()),
                    'name': 'Test User',
                    'is_active': True
                }
            )
            
            # Prepare user data
            user_data = {
                'name': user_profile.name,
                'phone': user_profile.phone_number,
                'email': user_profile.email,
                'address': user_profile.address,
                'dob': user_profile.dob.isoformat() if user_profile.dob else None,
                'gender': user_profile.gender,
            }
            
            # Get AI form assistance
            form_assistance = gemini_service.generate_form_assistance(scheme_name, user_data)
            
            return Response(form_assistance, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting form assistance: {e}")
            return Response(
                {'error': 'Failed to get form assistance'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
