"""
AI service for chat functionality using Google Gemini AI with Multi-Language Support.
Supports English, Bengali/Bangla, Malayalam, Hindi, Tamil, Telugu, and more.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from django.conf import settings
import re

logger = logging.getLogger(__name__)

class MultiLangGeminiChatService:
    """Enhanced service for handling AI chat interactions with multi-language support."""
    
    def __init__(self):
        self.model = None
        self._initialized = False
        
        # Language detection patterns
        self.language_patterns = {
            'bengali': [
                'হ্যালো', 'হাই', 'কেমন আছেন', 'সহায়তা', 'স্কিম', 'যোজনা', 'সরকারি', 
                'আবাসন', 'বাড়ি', 'কৃষি', 'চাষাবাদ', 'স্বাস্থ্য', 'চিকিৎসা', 'ব্যবসা',
                'আমি', 'আপনি', 'কি', 'কীভাবে', 'কোথায়', 'কখন'
            ],
            'malayalam': [
                'ഹലോ', 'ഹായ്', 'എങ്ങനെയുണ്ട്', 'സഹായം', 'പദ്ധതി', 'സർക്കാർ',
                'വീട്', 'കൃഷി', 'ആരോഗ്യം', 'ചികിത്സ', 'ബിസിനസ്സ്', 'വ്യാപാരം',
                'ഞാൻ', 'നിങ്ങൾ', 'എന്ത്', 'എങ്ങനെ', 'എവിടെ', 'എപ്പോൾ'
            ],
            'hindi': [
                'हैलो', 'नमस्ते', 'कैसे हैं', 'सहायता', 'योजना', 'सरकारी',
                'आवास', 'घर', 'कृषि', 'खेती', 'स्वास्थ्य', 'इलाज', 'व्यापार',
                'मैं', 'आप', 'क्या', 'कैसे', 'कहाँ', 'कब'
            ],
            'tamil': [
                'வணக்கம்', 'ஹலோ', 'எப்படி இருக்கீங்க', 'உதவி', 'திட்டம்', 'அரசு',
                'வீடு', 'விவசாயம்', 'உடல்நலம்', 'சிகிச்சை', 'வணிகம்',
                'நான்', 'நீங்கள்', 'என்ன', 'எப்படி', 'எங்கே', 'எப்போது'
            ],
            'telugu': [
                'హలో', 'నమస్కారం', 'ఎలా ఉన్నారు', 'సహాయం', 'పథకం', 'ప్రభుత్వం',
                'ఇల్లు', 'వ్యవసాయం', 'ఆరోగ్యం', 'చికిత్స', 'వ్యాపారం',
                'నేను', 'మీరు', 'ఏమిటి', 'ఎలా', 'ఎక్కడ', 'ఎప్పుడు'
            ]
        }
        
        # Multi-language system prompt
        self.system_prompt = """AGSA AI: Multi-Language Government Services Assistant

Your job: Analyze user intent in any language (English, Bengali/Bangla, Malayalam, Hindi, Tamil, Telugu) and create action plans for Indian government schemes.

IMPORTANT LANGUAGE RULES:
1. Detect the user's language from their message
2. ALWAYS respond in the SAME language as the user's input
3. If user writes in Bengali, respond in Bengali
4. If user writes in Malayalam, respond in Malayalam  
5. If user writes in English, respond in English
6. If mixed languages, use the primary language detected

Categories you can search (in any language):
- "healthcare" (স্বাস্থ্য, ആരോഗ്യം, स्वास्थ्य, உடல்நலம், ఆరోగ్యం)
- "education" (শিক্ষা, വിദ്യാഭ്യാസം, शिक्षा, கல்வி, విద్య)
- "agriculture" (কৃষি, കൃഷി, कृषि, விவசாயம், వ్యవసాయం)
- "employment" (চাকরি, ജോലി, रोजगार, வேலை, ఉద్యోగం)
- "housing" (আবাসন, വീട്, आवास, வீடு, ఇల్లు)
- "financial_inclusion" (আর্থিক, സാമ്പത്തിക, वित्तीय, நிதி, ఆర్థిక)

JSON response format (keep field names in English but content in user's language):
{
    "category": "SCHEME_SEARCH|ASK|ELIGIBILITY",
    "intent": "brief description in user's language",
    "confidence": 0.9,
    "language_detected": "bengali|malayalam|hindi|tamil|telugu|english",
    "response": "Response text in user's language",
    "action_plan": ["steps in user's language"],
    "search_params": {
        "scheme_category": "healthcare",
        "keywords": ["health", "medical"],
        "limit": 10
    },
    "required_documents": ["documents in user's language"],
    "eligible_schemes": ["scheme names in user's language"],
    "next_steps": "Next steps in user's language"
}

CRITICAL: Always respond in the user's input language. Bengali users get Bengali responses, Malayalam users get Malayalam responses, etc.
"""

        # Multi-language fallback responses
        self.fallback_responses = {
            'english': {
                'greeting': {
                    "category": "ASK",
                    "intent": "greeting", 
                    "confidence": 0.9,
                    "language_detected": "english",
                    "response": """👋 Hello! Welcome to AGSA - Your Government Services Assistant!

I'm here to help you navigate government schemes and services. I can assist you in multiple languages including English, Bengali, Malayalam, Hindi, Tamil, and Telugu.

🏠 **HOUSING SCHEMES**: Pradhan Mantri Awas Yojana (PMAY)
🌾 **AGRICULTURE SCHEMES**: PM-KISAN Samman Nidhi  
🏥 **HEALTHCARE SCHEMES**: Ayushman Bharat PM-JAY
💼 **BUSINESS & EMPLOYMENT**: Pradhan Mantri Mudra Yojana
📚 **EDUCATION SCHEMES**: Scholarship Programs

**What would you like assistance with today?**
You can ask me in your preferred language!""",
                    "action_plan": ["Browse available schemes", "Check eligibility", "Get application guidance"],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "Tell me which category interests you or ask in your preferred language"
                }
            },
            'bengali': {
                'greeting': {
                    "category": "ASK",
                    "intent": "শুভেচ্ছা",
                    "confidence": 0.9, 
                    "language_detected": "bengali",
                    "response": """👋 হ্যালো! AGSA-তে স্বাগতম - আপনার সরকারি সেবা সহায়ক!

আমি আপনাকে সরকারি যোজনা এবং সেবা নেভিগেট করতে সাহায্য করতে এখানে আছি। আমি একাধিক ভাষায় সহায়তা প্রদান করতে পারি।

🏠 **আবাসন যোজনা**: প্রধানমন্ত্রী আবাস যোজনা (PMAY)
🌾 **কৃষি যোজনা**: PM-KISAN সম্মান নিধি
🏥 **স্বাস্থ্যসেবা যোজনা**: আয়ুষ্মান ভারত PM-JAY  
💼 **ব্যবসা ও কর্মসংস্থান**: প্রধানমন্ত্রী মুদ্রা যোজনা
📚 **শিক্ষা যোজনা**: বৃত্তি কর্মসূচি

**আজ আপনার কী সাহায্য প্রয়োজন?**
আপনি বাংলায় আমাকে জিজ্ঞাসা করতে পারেন!""",
                    "action_plan": ["উপলব্ধ যোজনা দেখুন", "যোগ্যতা পরীক্ষা করুন", "আবেদনের নির্দেশনা পান"],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "কোন বিভাগে আপনার আগ্রহ আছে তা বলুন"
                }
            },
            'malayalam': {
                'greeting': {
                    "category": "ASK",
                    "intent": "അഭിവാദനം",
                    "confidence": 0.9,
                    "language_detected": "malayalam", 
                    "response": """👋 ഹലോ! AGSA-യിൽ സ്വാഗതം - നിങ്ങളുടെ സർക്കാർ സേവന സഹായി!

സർക്കാർ പദ്ധതികളും സേവനങ്ങളും നാവിഗേറ്റ് ചെയ്യാൻ ഞാൻ ഇവിടെയുണ്ട്. എനിക്ക് ഒന്നിലധികം ഭാഷകളിൽ സഹായം നൽകാൻ കഴിയും.

🏠 **ഭവന പദ്ധതികൾ**: പ്രധാനമന്ത്രി ആവാസ് യോജന (PMAY)
🌾 **കാർഷിക പദ്ധതികൾ**: PM-KISAN സമ്മാൻ നിധി
🏥 **ആരോഗ്യ പദ്ധതികൾ**: ആയുഷ്മാൻ ഭാരത് PM-JAY
💼 **ബിസിനസ്സ് & തൊഴിൽ**: പ്രധാനമന്ത്രി മുദ്ര യോജന  
📚 **വിദ്യാഭ്യാസ പദ്ധതികൾ**: സ്കോളർഷിപ്പ് പ്രോഗ്രാമുകൾ

**ഇന്ന് നിങ്ങൾക്ക് എന്ത് സഹായം വേണം?**
മലയാളത്തിൽ എന്നോട് ചോദിക്കാവുന്നതാണ്!""",
                    "action_plan": ["ലഭ്യമായ പദ്ധതികൾ കാണുക", "യോഗ്യത പരിശോധിക്കുക", "അപേക്ഷാ മാർഗ്ഗനിർദ്ദേശം നേടുക"],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "ഏത് വിഭാഗത്തിൽ നിങ്ങൾക്ക് താൽപ്പര്യമുണ്ടെന്ന് പറയുക"
                }
            },
            'hindi': {
                'greeting': {
                    "category": "ASK", 
                    "intent": "नमस्कार",
                    "confidence": 0.9,
                    "language_detected": "hindi",
                    "response": """👋 नमस्ते! AGSA में स्वागत है - आपका सरकारी सेवा सहायक!

मैं यहाँ सरकारी योजनाओं और सेवाओं में आपकी मदद करने के लिए हूँ। मैं कई भाषाओं में सहायता प्रदान कर सकता हूँ।

🏠 **आवास योजनाएं**: प्रधानमंत्री आवास योजना (PMAY)
🌾 **कृषि योजनाएं**: PM-KISAN सम्मान निधि
🏥 **स्वास्थ्य योजनाएं**: आयुष्मान भारत PM-JAY
💼 **व्यापार और रोजगार**: प्रधानमंत्री मुद्रा योजना
📚 **शिक्षा योजनाएं**: छात्रवृत्ति कार्यक्रम

**आज आपको किस चीज़ में सहायता चाहिए?**
आप हिंदी में मुझसे पूछ सकते हैं!""",
                    "action_plan": ["उपलब्ध योजनाएं देखें", "पात्रता जांचें", "आवेदन मार्गदर्शन प्राप्त करें"],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "बताएं कि आपको किस श्रेणी में रुचि है"
                }
            },
            'tamil': {
                'greeting': {
                    "category": "ASK",
                    "intent": "வணக்கம்",
                    "confidence": 0.9,
                    "language_detected": "tamil",
                    "response": """👋 வணக்கம்! AGSA-வில் வரவேற்கிறோம் - உங்கள் அரசு சேவை உதவியாளர்!

அரசு திட்டங்கள் மற்றும் சேவைகளை navigateசெய்ய உங்களுக்கு உதவ நான் இங்கே இருக்கிறேன். நான் பல மொழிகளில் உதவி வழங்க முடியும்.

🏠 **வீட்டு வசதி திட்டங்கள்**: பிரதமர் ஆவாஸ் யோஜனா (PMAY)  
🌾 **விவசாய திட்டங்கள்**: PM-KISAN சம்மான் நிதி
🏥 **சுகாதார திட்டங்கள்**: ஆயுஷ்மான் பாரத் PM-JAY
💼 **வணிகம் & வேலைவாய்ப்பு**: பிரதமர் முத்ரா யோஜனா
📚 **கல்வி திட்டங்கள்**: உதவித்தொகை திட்டங்கள்

**இன்று உங்களுக்கு என்ன உதவி தேவை?**
நீங்கள் தமிழில் என்னிடம் கேட்கலாம்!""",
                    "action_plan": ["கிடைக்கும் திட்டங்களைப் பார்க்கவும்", "தகுதியை சரிபார்க்கவும்", "விண்ணப்ப வழிகாட்டுதலைப் பெறவும்"],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "எந்த பிரிவில் உங்களுக்கு ஆர்வம் உள்ளது என்று சொல்லுங்கள்"
                }
            },
            'telugu': {
                'greeting': {
                    "category": "ASK",
                    "intent": "నమస్కారం", 
                    "confidence": 0.9,
                    "language_detected": "telugu",
                    "response": """👋 నమస్కారం! AGSA-కి స్వాగతం - మీ ప్రభుత్వ సేవల సహాయకుడు!

ప్రభుత్వ పథకాలు మరియు సేవలను navigate చేయడంలో మీకు సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను. నేను అనేక భాషలలో సహాయం అందించగలను.

🏠 **గృహ పథకాలు**: ప్రధాన మంత్రి ఆవాస్ యోజన (PMAY)
🌾 **వ్యవసాయ పథకాలు**: PM-KISAN సమ్మాన్ నిధి  
🏥 **ఆరోగ్య పథకాలు**: ఆయుష్మాన్ భారత్ PM-JAY
💼 **వ్యాపారం & ఉపాధి**: ప్రధాన మంత్రి ముద్ర యోజన
📚 **విద్యా పథకాలు**: స్కాలర్‌షిప్ ప్రోగ్రామ్‌లు

**ఈరోజు మీకు ఏ విధమైన సహాయం కావాలి?**
మీరు తెలుగులో నన్ను అడగవచ్చు!""",
                    "action_plan": ["అందుబాటులో ఉన్న పథకాలను చూడండి", "అర్హతను తనిఖీ చేయండి", "దరఖాస్తు మార్గదర్శకత్వం పొందండి"],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "మీకు ఏ విభాగంలో ఆసక్తి ఉందో చెప్పండి"
                }
            }
        }
        
    def detect_language(self, text: str) -> str:
        """Detect language from user input."""
        text_lower = text.lower()
        
        # Check for language patterns
        for language, patterns in self.language_patterns.items():
            if any(pattern in text for pattern in patterns):
                return language
                
        # Check for English patterns (fallback)
        english_patterns = ['hello', 'hi', 'how', 'what', 'where', 'when', 'help', 'scheme', 'government']
        if any(pattern in text_lower for pattern in english_patterns):
            return 'english'
            
        # Default to English if no language detected
        return 'english'
    
    def _ensure_initialized(self):
        """Ensure the service is initialized before use."""
        if self._initialized:
            return
            
        try:
            from django.conf import settings
            
            api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
            if not api_key:
                logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")
                self.model = None
                self._initialized = True
                return
            
            genai.configure(api_key=api_key)
            
            # Configure for optimal performance with multi-language support
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,  # Slightly higher for better language diversity
                top_p=0.8,
                top_k=40,
                max_output_tokens=512,  # Increased for multi-language responses
                candidate_count=1,
            )
            
            self.request_timeout = 12  # Increased timeout for multi-language processing
            
            self.model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config=generation_config,
                system_instruction=self.system_prompt
            )
            logger.info("Gemini model initialized with multi-language support")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
            
        self._initialized = True

    def analyze_user_message(self, message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user message in multiple languages and generate appropriate response.
        """
        ai_start_time = time.time()
        ai_timestamp = datetime.now().isoformat()
        
        logger.info(f"[AI_MULTILANG] ===== MULTI-LANGUAGE AI ANALYSIS STARTED =====")
        logger.info(f"[AI_MULTILANG] Started at: {ai_timestamp}")
        logger.info(f"[AI_MULTILANG] Message: {message[:100]}...")
        
        # Step 1: Detect language
        detected_language = self.detect_language(message)
        logger.info(f"[AI_MULTILANG] Detected language: {detected_language}")
        
        # Step 2: Ensure service is initialized
        self._ensure_initialized()
        
        if not self.model:
            logger.warning("[AI_MULTILANG] Gemini model not available, using fallback")
            fallback_result = self._get_multilang_fallback_response(message, detected_language)
            total_duration = (time.time() - ai_start_time) * 1000
            logger.info(f"[AI_MULTILANG] FALLBACK RESPONSE TIME: {total_duration:.2f}ms")
            return fallback_result
        
        try:
            # Step 3: Prepare multi-language prompt
            prompt_start = time.time()
            
            # Enhanced prompt with language instructions
            prompt = f'''User Message: "{message}"

Detected Language: {detected_language}

Instructions:
1. Detect the user's primary language from the message
2. Respond in the SAME language as the user's input
3. If the message is in Bengali, respond in Bengali
4. If the message is in Malayalam, respond in Malayalam  
5. If the message is in Hindi, respond in Hindi
6. If the message is in Tamil, respond in Tamil
7. If the message is in Telugu, respond in Telugu
8. If the message is in English, respond in English

Provide JSON response in the user's language.'''

            prompt_duration = (time.time() - prompt_start) * 1000
            logger.info(f"[AI_MULTILANG] Prompt preparation: {prompt_duration:.2f}ms")
            
            # Step 4: Make Gemini API call with timeout
            api_start = time.time()
            logger.info(f"[AI_MULTILANG] Making Gemini API call for {detected_language}...")
            
            try:
                # Threading approach for timeout
                import threading
                result = [None]
                exception = [None]
                
                def api_call():
                    try:
                        result[0] = self.model.generate_content(prompt)
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=api_call)
                thread.daemon = True
                thread.start()
                thread.join(timeout=15)  # 15 second timeout for multi-language
                
                if thread.is_alive():
                    api_duration = (time.time() - api_start) * 1000
                    logger.error(f"[AI_MULTILANG] API call TIMED OUT after {api_duration:.2f}ms")
                    raise TimeoutError(f"Gemini API call timed out for {detected_language}")
                
                if exception[0]:
                    raise exception[0]
                
                response = result[0]
                if response is None:
                    raise Exception("Gemini API returned None response")
                
                api_duration = (time.time() - api_start) * 1000
                logger.info(f"[AI_MULTILANG] API response received: {api_duration:.2f}ms")
                
            except Exception as e:
                api_duration = (time.time() - api_start) * 1000
                logger.error(f"[AI_MULTILANG] API ERROR after {api_duration:.2f}ms: {e}")
                raise e
            
            # Step 5: Parse response
            parse_start = time.time()
            try:
                response_text = response.text.strip()
                logger.info(f"[AI_MULTILANG] Raw response length: {len(response_text)} characters")
                
                # Handle JSON wrapped in markdown
                if response_text.startswith('```json') and response_text.endswith('```'):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith('```') and response_text.endswith('```'):
                    response_text = response_text[3:-3].strip()
                
                result = json.loads(response_text)
                
                # Ensure language_detected field is set
                if 'language_detected' not in result:
                    result['language_detected'] = detected_language
                
                parse_duration = (time.time() - parse_start) * 1000
                logger.info(f"[AI_MULTILANG] JSON parsing successful: {parse_duration:.2f}ms")
                
                total_duration = (time.time() - ai_start_time) * 1000
                logger.info(f"[AI_MULTILANG] ===== MULTI-LANGUAGE AI ANALYSIS COMPLETED =====")
                logger.info(f"[AI_MULTILANG] TOTAL TIME: {total_duration:.2f}ms for {detected_language}")
                logger.info(f"[AI_MULTILANG] ======================================================")
                
                return result
                
            except json.JSONDecodeError as e:
                parse_duration = (time.time() - parse_start) * 1000
                logger.warning(f"[AI_MULTILANG] JSON parsing failed: {parse_duration:.2f}ms")
                
                # Wrap non-JSON response
                fallback_result = {
                    "category": "ASK",
                    "intent": "general_inquiry" if detected_language == 'english' else "সাধারণ জিজ্ঞাসা" if detected_language == 'bengali' else "सामान्य पूछताछ" if detected_language == 'hindi' else "সাধারণ জিজ্ঞাসা",
                    "confidence": 0.7,
                    "language_detected": detected_language,
                    "response": response.text.strip(),
                    "action_plan": [],
                    "required_documents": [],
                    "eligible_schemes": [],
                    "next_steps": "Please provide more specific information." if detected_language == 'english' else "অনুগ্রহ করে আরও নির্দিষ্ট তথ্য প্রদান করুন।" if detected_language == 'bengali' else "कृपया अधिक विशिष्ट जानकारी प्रदान करें।" if detected_language == 'hindi' else "Please provide more specific information."
                }
                
                total_duration = (time.time() - ai_start_time) * 1000
                logger.info(f"[AI_MULTILANG] FALLBACK RESPONSE TIME: {total_duration:.2f}ms")
                return fallback_result
                
        except Exception as e:
            error_duration = (time.time() - ai_start_time) * 1000
            logger.error(f"[AI_MULTILANG] Error after {error_duration:.2f}ms: {e}")
            return self._get_multilang_fallback_response(message, detected_language)

    def _get_multilang_fallback_response(self, message: str, detected_language: str) -> Dict[str, Any]:
        """Get fallback response in the detected language."""
        message_lower = message.lower().strip()
        
        # Check for greetings in any language
        greeting_patterns = ['hello', 'hi', 'hey', 'start', 'help', 'হ্যালো', 'হাই', 'সাহায্য', 
                           'ഹലോ', 'ഹായ്', 'സഹായം', 'नमस्ते', 'हैलो', 'सहायता',
                           'வணக்கம்', 'ஹலோ', 'உதவி', 'నమస్కారం', 'హలో', 'సహాయం']
        
        if any(pattern in message_lower for pattern in greeting_patterns):
            # Return greeting response in detected language
            if detected_language in self.fallback_responses:
                return self.fallback_responses[detected_language]['greeting']
            else:
                return self.fallback_responses['english']['greeting']
        
        # Default fallback for unrecognized queries
        if detected_language == 'bengali':
            return {
                "category": "ASK",
                "intent": "সাধারণ জিজ্ঞাসা",
                "confidence": 0.7,
                "language_detected": "bengali",
                "response": "দুঃখিত, আমি বর্তমানে AI সেবা সংযোগ করতে পারছি না। অনুগ্রহ করে পরে আবার চেষ্টা করুন। তাৎক্ষণিক সাহায্যের জন্য, সাপোর্টের সাথে যোগাযোগ করুন।",
                "action_plan": [],
                "required_documents": [],
                "eligible_schemes": [],
                "next_steps": "AI সেবা উপলব্ধ হলে অনুগ্রহ করে আবার চেষ্টা করুন।"
            }
        elif detected_language == 'malayalam':
            return {
                "category": "ASK", 
                "intent": "പൊതു അന്വേഷണം",
                "confidence": 0.7,
                "language_detected": "malayalam",
                "response": "ക്ഷമിക്കണം, എനിക്ക് ഇപ്പോൾ AI സേവനവുമായി ബന്ധപ്പെടാൻ കഴിയുന്നില്ല. പിന്നീട് വീണ്ടും ശ്രമിക്കുക. ഉടനടി സഹായത്തിന്, സപ്പോർട്ടിനെ ബന്ധപ്പെടുക.",
                "action_plan": [],
                "required_documents": [],
                "eligible_schemes": [],
                "next_steps": "AI സേവനം ലഭ്യമാകുമ്പോൾ ദയവായി വീണ്ടും ശ്രമിക്കുക."
            }
        elif detected_language == 'hindi':
            return {
                "category": "ASK",
                "intent": "सामान्य पूछताछ", 
                "confidence": 0.7,
                "language_detected": "hindi",
                "response": "क्षमा करें, मैं वर्तमान में AI सेवा से कनेक्ट नहीं हो पा रहा हूँ। कृपया बाद में पुनः प्रयास करें। तत्काल सहायता के लिए, सपोर्ट से संपर्क करें।",
                "action_plan": [],
                "required_documents": [],
                "eligible_schemes": [],
                "next_steps": "जब AI सेवा उपलब्ध हो तो कृपया पुनः प्रयास करें।"
            }
        elif detected_language == 'tamil':
            return {
                "category": "ASK",
                "intent": "பொதுவான விசாரணை",
                "confidence": 0.7, 
                "language_detected": "tamil",
                "response": "மன்னிக்கவும், தற்போது நான் AI சேவையுடன் இணைக்க முடியவில்லை. பின்னர் மீண்டும் முயற்சி செய்யுங்கள். உடனடி உதவிக்கு, ஆதரவைத் தொடர்பு கொள்ளுங்கள்.",
                "action_plan": [],
                "required_documents": [],
                "eligible_schemes": [],
                "next_steps": "AI சேவை கிடைக்கும் போது தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
            }
        elif detected_language == 'telugu':
            return {
                "category": "ASK",
                "intent": "సాధారణ విచారణ",
                "confidence": 0.7,
                "language_detected": "telugu", 
                "response": "క్షమించండి, నేను ప్రస్తుతం AI సేవతో కనెక్ట్ చేయలేకపోతున్నాను. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి. తక్షణ సహాయం కోసం, సపోర్ట్‌ని సంప్రదించండి.",
                "action_plan": [],
                "required_documents": [],
                "eligible_schemes": [],
                "next_steps": "AI సేవ అందుబాటులో ఉన్నప్పుడు దయచేసి మళ్లీ ప్రయత్నించండి."
            }
        else:  # Default to English
            return {
                "category": "ASK",
                "intent": "general_inquiry",
                "confidence": 0.7,
                "language_detected": "english",
                "response": "I'm currently unable to connect to the AI service. Please check your internet connection or try again later. For immediate assistance, please contact support.",
                "action_plan": [],
                "required_documents": [],
                "eligible_schemes": [],
                "next_steps": "Please try again later when the AI service is available."
            }

    def generate_multilang_form_assistance(self, scheme_name: str, user_data: Dict[str, Any], language: str = 'english') -> Dict[str, Any]:
        """Generate form filling assistance in specified language."""
        if not self.model:
            return self._fallback_form_assistance_multilang(scheme_name, language)
        
        try:
            # Language-specific prompts
            language_prompts = {
                'english': f'Help fill out the application form for "{scheme_name}" in English.',
                'bengali': f'"{scheme_name}" এর জন্য আবেদন ফরম পূরণে বাংলায় সাহায্য করুন।',
                'malayalam': f'"{scheme_name}" എന്ന പദ്ধതിക്കായുള്ള അപേക്ഷാ ഫോം മലയാളത്തിൽ പൂരിപ്പിക്കാൻ സഹായിക്കുക।',
                'hindi': f'"{scheme_name}" के लिए आवेदन फॉर्म भरने में हिंदी में सहायता करें।',
                'tamil': f'"{scheme_name}" க்கான விண்ணப்ப படிவத்தை தமிழில் நிரப்ப உதவுங்கள்।',
                'telugu': f'"{scheme_name}" కోసం దరఖాస్తు ఫారం తెలుగులో పూరించడంలో సహాయం చేయండి।'
            }
            
            prompt = f"""{language_prompts.get(language, language_prompts['english'])}

User Data Available:
{json.dumps(user_data, indent=2)}

Respond in {language} language with JSON format containing:
- pre_filled_data: Fields that can be pre-filled
- missing_fields: Information still needed  
- completion_steps: Step-by-step guidance
- warnings: Important notes and common mistakes
- documents_required: Required supporting documents

All content should be in {language} language."""

            response = self.model.generate_content(prompt)
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return self._fallback_form_assistance_multilang(scheme_name, language)
                
        except Exception as e:
            logger.error(f"Error in multilang form assistance: {e}")
            return self._fallback_form_assistance_multilang(scheme_name, language)

    def _fallback_form_assistance_multilang(self, scheme_name: str, language: str = 'english') -> Dict[str, Any]:
        """Fallback form assistance in multiple languages."""
        messages = {
            'english': f"Form assistance for {scheme_name} is currently unavailable. Please try again later.",
            'bengali': f"{scheme_name} এর জন্য ফর্ম সহায়তা বর্তমানে উপলব্ধ নয়। অনুগ্রহ করে পরে আবার চেষ্টা করুন।",
            'malayalam': f"{scheme_name} എന്നതിനുള്ള ഫോം സഹായം നിലവിൽ ലഭ്യമല്ല. പിന്നീട് വീണ്ടും ശ്രമിക്കുക.",
            'hindi': f"{scheme_name} के लिए फॉर्म सहायता वर्तमान में अनुपलब्ध है। कृपया बाद में पुनः प्रयास करें।",
            'tamil': f"{scheme_name} க்கான படிவ உதவி தற்போது கிடைக்கவில்லை. பின்னர் மீண்டும் முயற்சி செய்யுங்கள்.",
            'telugu': f"{scheme_name} కోసం ఫారం సహాయం ప్రస్తుతం అందుబాటులో లేదు. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి."
        }
        
        return {
            "error": "AI service unavailable",
            "message": messages.get(language, messages['english']),
            "pre_filled_data": {},
            "missing_fields": [],
            "completion_steps": [],
            "warnings": [],
            "documents_required": []
        }


# Global instance
gemini_multilang_service = MultiLangGeminiChatService()
# For backward compatibility
gemini_service = gemini_multilang_service



# Example usage function for testing
def test_multilang_service():
    """Test function to demonstrate multi-language capabilities."""
    
    test_messages = [
        "Hello, what are you?",  # English
        "হ্যালো, আপনি কি?",  # Bengali
        "ഹലോ, നിങ്ങൾ എന്താണ്?",  # Malayalam  
        "नमस्ते, आप क्या हैं?",  # Hindi
        "வணக்கம், நீங்கள் என்ன?",  # Tamil
        "హలో, మీరు ఏమిటి?"  # Telugu
    ]
    
    for message in test_messages:
        print(f"\n--- Testing: {message} ---")
        result = gemini_multilang_service.analyze_user_message(message)
        print(f"Language detected: {result.get('language_detected', 'unknown')}")
        print(f"Response: {result.get('response', 'No response')[:100]}...")
        print("---")


if __name__ == "__main__":
    # Run test if script is executed directly
    test_multilang_service() 