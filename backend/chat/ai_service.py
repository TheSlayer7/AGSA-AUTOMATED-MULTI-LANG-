"""
AI service for chat functionality using Google Gemini AI.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiChatService:
    """Service for handling AI chat interactions with Gemini."""
    
    def __init__(self):
        self.model = None
        self._initialized = False
        
        # System prompt for AGSA assistant (simplified for faster responses)
        self.system_prompt = """You are AGSA, an AI assistant for Indian government services. Be concise and helpful.

Response Format - Always return JSON:
{
    "category": "ASK",
    "intent": "brief intent description",
    "confidence": 0.8,
    "response": "your concise response",
    "action_plan": [],
    "required_documents": [],
    "eligible_schemes": [],
    "next_steps": "next action"
}

Keep responses short and practical. Focus on the user's immediate need."""
        
    def _ensure_initialized(self):
        """Ensure the service is initialized before use."""
        if self._initialized:
            return
            
        try:
            # Import Django settings here to avoid import-time issues
            from django.conf import settings
            
            # Configure Gemini AI
            api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
            if not api_key:
                logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")
                self.model = None
                self._initialized = True
                return
            
            genai.configure(api_key=api_key)
            
            # Configure for faster responses
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=512,  # Limit tokens for faster response
                candidate_count=1,
            )
            
            self.model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config=generation_config,
                system_instruction=self.system_prompt
            )
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
            
        self._initialized = True

    def analyze_user_message(self, message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user message and generate appropriate response.
        
        Args:
            message: User's message
            user_context: Additional context about the user
            
        Returns:
            Dict containing analysis and response
        """
        # Ensure the service is initialized
        self._ensure_initialized()
        
        if not self.model:
            logger.warning("Gemini model not available, using fallback")
            return self._fallback_response(message)
        
        try:
            # Create simplified prompt for faster response
            prompt = f"""User: "{message}"

Respond with JSON for this government services query. Be brief and helpful."""

            # Log the attempt for debugging
            logger.info(f"Attempting Gemini API call for message: {message[:50]}...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Log successful response
            logger.info("Gemini API call successful")
            
            # Try to parse JSON response
            try:
                response_text = response.text.strip()
                
                # Handle JSON wrapped in markdown code blocks
                if response_text.startswith('```json') and response_text.endswith('```'):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith('```') and response_text.endswith('```'):
                    response_text = response_text[3:-3].strip()
                
                result = json.loads(response_text)
                return result
            except json.JSONDecodeError:
                logger.warning("Gemini response was not JSON, wrapping in basic structure")
                # If not JSON, wrap in basic structure
                return {
                    "category": "ASK",
                    "intent": "general_inquiry",
                    "confidence": 0.7,
                    "response": response.text.strip(),
                    "action_plan": [],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "Please provide more specific information about your requirements."
                }
                
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {e}")
            return self._fallback_response(message)

    def generate_form_assistance(self, scheme_name: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate form filling assistance for a specific scheme.
        
        Args:
            scheme_name: Name of the government scheme
            user_data: User's personal information
            
        Returns:
            Dict containing form assistance
        """
        if not self.model:
            return self._fallback_form_assistance(scheme_name)
        
        try:
            prompt = f"""As AGSA, help the user fill out the application form for "{scheme_name}".

User Data Available:
{json.dumps(user_data, indent=2)}

Please provide:
1. Pre-filled form fields based on available data
2. Missing information that needs to be collected
3. Step-by-step guidance for form completion
4. Common mistakes to avoid
5. Required supporting documents

Respond in JSON format with fields: pre_filled_data, missing_fields, completion_steps, warnings, documents_required."""

            response = self.model.generate_content(prompt)
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return self._fallback_form_assistance(scheme_name)
                
        except Exception as e:
            logger.error(f"Error in form assistance generation: {e}")
            return self._fallback_form_assistance(scheme_name)

    def check_scheme_eligibility(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check eligibility for various government schemes.
        
        Args:
            user_profile: User's profile information
            
        Returns:
            List of eligible schemes with details
        """
        if not self.model:
            return self._fallback_eligibility()
        
        try:
            prompt = f"""As AGSA, analyze the user profile and determine eligibility for Indian government schemes.

User Profile:
{json.dumps(user_profile, indent=2)}

Please check eligibility for major schemes like:
- Pradhan Mantri Awas Yojana
- PM-KISAN
- Ayushman Bharat
- Mudra Loan Scheme
- NREGA
- Sukanya Samriddhi Yojana
- Atal Pension Yojana

Respond with JSON array containing:
- scheme_name: Name of the scheme
- eligible: true/false
- eligibility_score: 0.0-1.0
- reason: Why eligible/not eligible
- benefits: Expected benefits
- next_steps: How to apply
- required_documents: Documents needed"""

            response = self.model.generate_content(prompt)
            
            try:
                result = json.loads(response.text)
                return result if isinstance(result, list) else []
            except json.JSONDecodeError:
                return self._fallback_eligibility()
                
        except Exception as e:
            logger.error(f"Error in eligibility check: {e}")
            return self._fallback_eligibility()

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Simple fallback response when AI is not available - shows LLM unavailability."""
        return {
            "category": "ASK",
            "intent": "llm_unavailable",
            "confidence": 0.3,
            "response": "I'm currently unable to connect to the AI service. Please check your internet connection or try again later. For immediate assistance, please contact support.",
            "action_plan": [],
            "required_documents": [],
            "eligible_schemes": [],
            "next_steps": "Please try again later when the AI service is available."
        }

        # COMMENTED OUT: Enhanced fallback responses - will be used once LLM integration is fixed
        """
        message_lower = message.lower()
        
        # Housing/Awas related queries
        if any(keyword in message_lower for keyword in ['housing', 'home', 'awas', 'house']):
            return {
                "category": "AGENTIC_WORK",
                "intent": "housing_scheme_inquiry",
                "confidence": 0.8,
                "response": '''PRADHAN MANTRI AWAS YOJANA (PMAY)

Key Benefits:
- Subsidy up to Rs 2.67 lakhs on home loans
- Interest rate subsidy for 20 years
- For families with annual income up to Rs 18 lakhs

Eligibility Criteria:
- First-time home buyer
- Family income within prescribed limits
- No pucca house in family name

Next Steps:
1. Check detailed eligibility criteria
2. Gather required documents
3. Apply through PMAY portal

Would you like me to help verify your eligibility and gather the required documents?''',
                "action_plan": [
                    "Verify family income eligibility",
                    "Check if family owns any pucca house",
                    "Gather required documents (Income certificate, Aadhaar, PAN, Bank details)",
                    "Apply through official PMAY portal"
                ],
                "required_documents": ["Income Certificate", "Aadhaar Card", "PAN Card", "Bank Account Details", "Property Documents"],
                "eligible_schemes": ["Pradhan Mantri Awas Yojana"],
                "next_steps": "Let me help you check your exact eligibility and document requirements."
            }
        
        # Farmer/Agriculture related queries
        elif any(keyword in message_lower for keyword in ['farmer', 'agriculture', 'kisan', 'crop', 'farming']):
            return {
                "category": "AGENTIC_WORK", 
                "intent": "farmer_scheme_inquiry",
                "confidence": 0.8,
                "response": '''GOVERNMENT SCHEMES FOR FARMERS

PM-KISAN (Pradhan Mantri Kisan Samman Nidhi):
- Rs 6,000 annually in 3 installments
- Direct benefit transfer to bank account
- For small and marginal farmers

Kisan Credit Card (KCC):
- Easy access to credit for farming needs
- Low interest rates
- Flexible repayment terms

Crop Insurance Schemes:
- Protection against natural calamities
- Premium subsidy from government

Next Steps:
1. Verify land ownership documents
2. Check bank account linking with Aadhaar
3. Apply through respective portals

Which scheme would you like to know more about?''',
                "action_plan": [
                    "Verify land ownership documents",
                    "Check Aadhaar-bank account linking", 
                    "Choose appropriate scheme based on needs",
                    "Apply through official portals"
                ],
                "required_documents": ["Land Records", "Aadhaar Card", "Bank Account Details", "Passport Size Photos"],
                "eligible_schemes": ["PM-KISAN", "Kisan Credit Card", "Crop Insurance"],
                "next_steps": "Tell me about your land size and farming type to suggest the best schemes."
            }
        
        # Healthcare related queries
        elif any(keyword in message_lower for keyword in ['health', 'medical', 'hospital', 'treatment', 'ayushman']):
            return {
                "category": "AGENTIC_WORK",
                "intent": "healthcare_scheme_inquiry", 
                "confidence": 0.8,
                "response": '''AYUSHMAN BHARAT - PRADHAN MANTRI JAN AROGYA YOJANA

Coverage:
- Free treatment up to Rs 5 lakhs per family per year
- 1,393+ medical packages covered
- Cashless treatment at empaneled hospitals

Eligibility:
- Based on SECC 2011 database
- Automatic eligibility for rural families
- Specific occupation categories in urban areas

Benefits:
- No premium payment required
- Pre and post-hospitalization coverage
- Coverage across India

Next Steps:
1. Check if your family is in SECC database
2. Generate/download Ayushman card
3. Find nearby empaneled hospitals

Would you like me to help you check your eligibility?''',
                "action_plan": [
                    "Check family eligibility in SECC database",
                    "Generate Ayushman Bharat card if eligible", 
                    "Find nearby empaneled hospitals",
                    "Understand claim process"
                ],
                "required_documents": ["Aadhaar Card", "Ration Card", "Mobile Number"],
                "eligible_schemes": ["Ayushman Bharat PMJAY"],
                "next_steps": "Let me help you verify your family's eligibility status."
            }
        
        # Business/MSME related queries
        elif any(keyword in message_lower for keyword in ['business', 'loan', 'mudra', 'startup', 'msme']):
            return {
                "category": "AGENTIC_WORK",
                "intent": "business_scheme_inquiry",
                "confidence": 0.8,
                "response": '''PRADHAN MANTRI MUDRA YOJANA

Loan Categories:
- SHISHU: Up to Rs 50,000 for starting business
- KISHORE: Rs 50,001 to Rs 5 lakhs for growth
- TARUN: Rs 5,00,001 to Rs 10 lakhs for expansion

Key Features:
- No collateral required
- Competitive interest rates
- Easy application process

Eligible Activities:
- Trading, manufacturing, service sector
- Small transport vehicles
- Food service units
- Textile production

Next Steps:
1. Prepare business plan
2. Gather required documents
3. Approach nearest bank/NBFC

What type of business are you planning to start?''',
                "action_plan": [
                    "Prepare detailed business plan",
                    "Calculate loan amount needed",
                    "Gather required documents",
                    "Apply at nearest bank or NBFC"
                ],
                "required_documents": ["Aadhaar Card", "PAN Card", "Business Plan", "Bank Statements", "Address Proof"],
                "eligible_schemes": ["Pradhan Mantri Mudra Yojana", "Stand-up India", "MSME Loans"],
                "next_steps": "Tell me about your business idea to suggest the right loan category and amount."
            }
        
        # General inquiry
        else:
            return {
                "category": "ASK",
                "intent": "general_inquiry", 
                "confidence": 0.7,
                "response": '''WELCOME TO AGSA - GOVERNMENT SERVICES ASSISTANT

I can help you with various government schemes and services:

Popular Categories:
- HOUSING: Pradhan Mantri Awas Yojana
- AGRICULTURE: PM-KISAN, Crop Insurance
- HEALTHCARE: Ayushman Bharat PMJAY
- BUSINESS: Mudra Loans, Startup India
- SOCIAL SECURITY: Pension schemes, Child welfare

What I can do:
- Check your eligibility for schemes
- Help gather required documents
- Assist with application forms
- Track application status

To get started, tell me:
- What type of assistance do you need?
- Which government service interests you?
- Any specific scheme you've heard about?

How can I help you today?''',
                "action_plan": [],
                "required_documents": [],
                "eligible_schemes": ["PM Awas Yojana", "PM-KISAN", "Ayushman Bharat", "Mudra Loans"],
                "next_steps": "Please tell me which government service or scheme you're interested in."
            }
        """

    def _fallback_form_assistance(self, scheme_name: str) -> Dict[str, Any]:
        """Simple fallback when AI is not available for form assistance."""
        return {
            "error": "AI service unavailable",
            "message": f"Form assistance for {scheme_name} is currently unavailable. Please try again later when the AI service is restored.",
            "pre_filled_data": {},
            "missing_fields": [],
            "completion_steps": [],
            "warnings": [],
            "documents_required": []
        }

        # COMMENTED OUT: Enhanced form assistance - will be used once LLM integration is fixed
        """
        return {
            "pre_filled_data": {},
            "missing_fields": ["name", "address", "phone_number", "aadhaar_number"],
            "completion_steps": [
                f"Gather all required documents for {scheme_name}",
                "Fill in personal information carefully",
                "Review all details before submission",
                "Submit the application online or at nearest center"
            ],
            "warnings": ["Ensure all information is accurate", "Keep copies of all documents"],
            "documents_required": ["Aadhaar Card", "PAN Card", "Bank Account Details", "Income Certificate"]
        }
        """

    def _fallback_eligibility(self) -> List[Dict[str, Any]]:
        """Simple fallback when AI is not available for eligibility check.""" 
        return [{
            "scheme_name": "AI Service Unavailable",
            "eligible": False,
            "eligibility_score": 0.0,
            "reason": "Cannot check eligibility - AI service is currently unavailable. Please try again later.",
            "benefits": "",
            "next_steps": "Try again when AI service is restored",
            "required_documents": []
        }]

        # COMMENTED OUT: Enhanced eligibility check - will be used once LLM integration is fixed
        """
        return [
            {
                "scheme_name": "Pradhan Mantri Awas Yojana",
                "eligible": True,
                "eligibility_score": 0.8,
                "reason": "Based on basic criteria, you may be eligible",
                "benefits": "Housing subsidy up to ₹2.5 lakhs",
                "next_steps": "Complete detailed eligibility verification",
                "required_documents": ["Income Certificate", "Aadhaar", "Bank Details"]
            }
        ]
        """


# Global instance
gemini_service = GeminiChatService()
