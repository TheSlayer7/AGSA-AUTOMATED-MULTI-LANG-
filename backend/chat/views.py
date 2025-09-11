"""
Chat views for handling AI-powered conversations.
"""

import uuid
import logging
import time
from datetime import datetime
from typing import Dict, Any
from django.db import models
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
        start_time = time.time()
        request_timestamp = datetime.now().isoformat()
        
        # Immediate debug output to console
        print(f"[DEBUG] Chat request received at {request_timestamp}")
        print(f"[DEBUG] Request data: {request.data}")
        
        logger.info(f"[CHAT_FLOW] ===== NEW CHAT REQUEST STARTED =====")
        logger.info(f"[CHAT_FLOW] Request received at: {request_timestamp}")
        logger.info(f"[CHAT_FLOW] Request data: {request.data}")
        
        try:
            # Step 1: Validate request data
            step_start = time.time()
            serializer = SendMessageRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 1 - Request validation: {step_duration:.2f}ms")
            
            # Get or create session
            session_id = serializer.validated_data.get('session_id')
            message_content = serializer.validated_data['message']
            message_type = serializer.validated_data['message_type']
            
            logger.info(f"[CHAT_FLOW] Session ID: {session_id}")
            logger.info(f"[CHAT_FLOW] Message content: {message_content[:100]}...")
            
            # Step 2: Get user profile (optimized with select_for_update for faster access)
            step_start = time.time()
            user_profile, created = UserProfile.objects.select_for_update().get_or_create(
                phone_number='+919999999999',
                defaults={
                    'user_id': str(uuid.uuid4()),
                    'name': 'Test User',
                    'is_active': True
                }
            )
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 2 - User profile fetch: {step_duration:.2f}ms")
            
            # Step 3: Get or create session
            step_start = time.time()
            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id, user_profile=user_profile)
                    logger.info(f"[CHAT_FLOW] Found existing session: {session_id}")
                except ChatSession.DoesNotExist:
                    session = self._create_new_session(user_profile)
                    logger.info(f"[CHAT_FLOW] Created new session (session not found): {session.session_id}")
            else:
                session = self._create_new_session(user_profile)
                logger.info(f"[CHAT_FLOW] Created new session (no session ID): {session.session_id}")
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 3 - Session management: {step_duration:.2f}ms")
            
            # Step 4: Save user message (optimized)
            step_start = time.time()
            user_message = ChatMessage(
                session=session,
                message_id=str(uuid.uuid4()),
                content=message_content,
                sender='user',
                message_type=message_type
            )
            user_message.save()
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 4 - Save user message: {step_duration:.2f}ms")
            
            # Step 5: Prepare context for AI (minimal for speed)
            step_start = time.time()
            # Skip recent messages query for maximum speed - use minimal context
            user_context = {
                'name': 'User',  # Simplified
                'phone': user_profile.phone_number,
                'documents': []  # Skip document lookup for speed
            }
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 5 - Prepare AI context: {step_duration:.2f}ms")
            
            # Step 6: Call AI service (This is likely the bottleneck)
            ai_start_time = time.time()
            logger.info(f"[CHAT_FLOW] Step 6 - CALLING GEMINI AI SERVICE...")
            logger.info(f"[CHAT_FLOW] AI call started at: {datetime.now().isoformat()}")
            
            # Debug print
            print(f"[DEBUG] About to call Gemini AI service at {datetime.now().isoformat()}")
            
            try:
                ai_response = gemini_service.analyze_user_message(
                    message=message_content,
                    user_context=user_context
                )
                
                ai_duration = (time.time() - ai_start_time) * 1000
                print(f"[DEBUG] Gemini AI response received after {ai_duration:.2f}ms")
                logger.info(f"[CHAT_FLOW] Step 6 - AI service response received: {ai_duration:.2f}ms")
                logger.info(f"[CHAT_FLOW] AI response: {ai_response}")
                
                ai_response_content = ai_response.get('response', 'I apologize, but I am having trouble processing your request right now.')
                intent_category = ai_response.get('category', 'ASK')
                confidence_score = ai_response.get('confidence', 0.7)
                action_required = len(ai_response.get('action_plan', [])) > 0
                
                # NEW: Database Integration - If AI detected scheme search intent
                if intent_category == 'SCHEME_SEARCH':
                    db_start = time.time()
                    logger.info(f"[CHAT_FLOW] Step 6.1 - SCHEME SEARCH DETECTED, querying database...")
                    
                    # Extract search parameters from AI response
                    search_params = ai_response.get('search_params', {})
                    scheme_category = search_params.get('scheme_category', '')
                    keywords = search_params.get('keywords', [])
                    limit = search_params.get('limit', 10)
                    
                    # Import here to avoid circular imports
                    from schemes.models import Scheme, SchemeCategory
                    
                    # Query database for matching schemes
                    schemes_queryset = Scheme.objects.filter(is_active=True)
                    
                    # Filter by category if specified
                    if scheme_category:
                        # Map common terms to scheme categories
                        category_mapping = {
                            'healthcare': SchemeCategory.HEALTHCARE,
                            'health': SchemeCategory.HEALTHCARE,
                            'medical': SchemeCategory.HEALTHCARE,
                            'education': SchemeCategory.EDUCATION,
                            'agriculture': SchemeCategory.AGRICULTURE,
                            'employment': SchemeCategory.EMPLOYMENT,
                            'housing': SchemeCategory.HOUSING,
                            'financial': SchemeCategory.FINANCIAL_INCLUSION,
                        }
                        
                        mapped_category = category_mapping.get(scheme_category.lower())
                        if mapped_category:
                            schemes_queryset = schemes_queryset.filter(scheme_category=mapped_category)
                        else:
                            logger.warning(f"[CHAT_FLOW] Category '{scheme_category}' not mapped to any scheme category")
                    
                    # Filter by keywords if specified
                    if keywords:
                        for keyword in keywords:
                            schemes_queryset = schemes_queryset.filter(
                                models.Q(scheme_name__icontains=keyword) |
                                models.Q(details__icontains=keyword) |
                                models.Q(eligibility__icontains=keyword)
                            )
                    
                    # Get schemes with limit
                    schemes = list(schemes_queryset[:limit])
                    
                    db_duration = (time.time() - db_start) * 1000
                    logger.info(f"[CHAT_FLOW] Step 6.1 - Database query completed: {db_duration:.2f}ms, found {len(schemes)} schemes")
                    
                    # Format schemes into response
                    if schemes:
                        scheme_list = []
                        for scheme in schemes:
                            scheme_list.append(f"• {scheme.scheme_name}")
                            if scheme.details:
                                scheme_list.append(f"  {scheme.details[:100]}...")
                            if scheme.benefits:
                                scheme_list.append(f"  Benefits: {scheme.benefits[:100]}...")
                            scheme_list.append("")  # Empty line for spacing
                        
                        ai_response_content = f"I found {len(schemes)} scheme(s) for you:\n\n" + "\n".join(scheme_list)
                        ai_response_content += f"\n\nWould you like more details about any specific scheme? I can also help you check eligibility requirements."
                    else:
                        ai_response_content = f"I searched our database but couldn't find any schemes matching '{scheme_category}'. However, I can help you explore other categories like education, agriculture, employment, or housing schemes."
                
            except Exception as e:
                ai_duration = (time.time() - ai_start_time) * 1000
                logger.error(f"[CHAT_FLOW] Step 6 - AI service ERROR after {ai_duration:.2f}ms: {e}")
                ai_response_content = "I'm currently unable to process your request due to a service interruption. Please try again in a few moments or contact support for assistance."
                intent_category = 'llm_unavailable'
                confidence_score = 0.0
                action_required = False
            
            # Step 7: Save assistant message (optimized)
            step_start = time.time()
            assistant_message = ChatMessage(
                session=session,
                message_id=str(uuid.uuid4()),
                content=ai_response_content,
                sender='assistant',
                message_type='text',
                intent_category=intent_category,
                confidence_score=confidence_score,
                action_required=action_required
            )
            assistant_message.save()
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 7 - Save assistant message: {step_duration:.2f}ms")
            
            # Step 8: Update session and context (optimized)
            step_start = time.time()
            # Bulk update session
            ChatSession.objects.filter(id=session.id).update(
                last_activity=user_message.timestamp,
                title="Government Services Chat"
            )
            
            # Use get_or_create with minimal defaults
            context, created = ConversationContext.objects.get_or_create(
                session=session,
                defaults={'current_flow': 'idle', 'user_intent': 'general_inquiry'}
            )
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 8 - Update session/context: {step_duration:.2f}ms")
            
            # Step 9: Serialize response (optimized for speed)
            step_start = time.time()
            response_data = {
                'session_id': session.session_id,
                'user_message': {
                    'message_id': user_message.message_id,
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                },
                'assistant_message': {
                    'message_id': assistant_message.message_id,
                    'content': assistant_message.content,
                    'timestamp': assistant_message.timestamp.isoformat(),
                    'confidence_score': assistant_message.confidence_score,
                    'intent_category': assistant_message.intent_category
                },
                'context': {
                    'current_flow': context.current_flow,
                    'user_intent': context.user_intent
                }
            }
            step_duration = (time.time() - step_start) * 1000
            logger.info(f"[CHAT_FLOW] Step 9 - Serialize response: {step_duration:.2f}ms")
            
            # Total timing
            total_duration = (time.time() - start_time) * 1000
            response_timestamp = datetime.now().isoformat()
            
            logger.info(f"[CHAT_FLOW] ===== CHAT REQUEST COMPLETED =====")
            logger.info(f"[CHAT_FLOW] Response sent at: {response_timestamp}")
            logger.info(f"[CHAT_FLOW] TOTAL REQUEST TIME: {total_duration:.2f}ms")
            logger.info(f"[CHAT_FLOW] =========================================")
            
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
