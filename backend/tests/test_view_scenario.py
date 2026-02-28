import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

from chat.ai_service import gemini_service

# Test exactly what the Django view does
try:
    print("Testing Django view scenario...")
    
    message_content = "Hello, I need help with government services"
    
    # Build user context exactly like in the view
    user_context = {
        'name': 'User',  # This is what happens when hasattr check fails
        'phone': '+919999999999',
        'documents': []  # Add actual documents from user profile if available
    }
    
    print(f"Message content: {message_content}")
    print(f"User context: {user_context}")
    
    # Generate AI response using analyze_user_message - exactly like the view
    ai_response = gemini_service.analyze_user_message(
        message=message_content,
        user_context=user_context
    )
    
    print(f"AI Response: {ai_response}")
    
    # Process response exactly like the view
    ai_response_content = ai_response.get('response', 'I apologize, but I am having trouble processing your request right now.')
    intent_category = ai_response.get('category', 'ASK')
    confidence_score = ai_response.get('confidence', 0.7)
    action_required = len(ai_response.get('action_plan', [])) > 0
    
    print(f"Final content: {ai_response_content}")
    print(f"Intent: {intent_category}")
    print(f"Confidence: {confidence_score}")
    print(f"Action required: {action_required}")
    
except Exception as e:
    print(f"Exception occurred: {e}")
    import traceback
    traceback.print_exc()
