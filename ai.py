from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

class RiverwoodAI:
    def __init__(self):
        self.client = None
        self.available_models = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile", 
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        self.current_model = self.available_models[0]
        self.initialize_groq_client()
        self.conversation_context = []
        
        self.construction_updates = {
            "current_status": {
                "foundation": "100% completed",
                "structural": "85% completed", 
                "electrical": "60% completed",
                "plumbing": "55% completed",
                "next_milestone": "Structural completion by next Friday",
                "site_visits": "Monday-Saturday, 10 AM - 5 PM"
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Simple and reliable language detection"""
        text_lower = text.lower().strip()
        
        # Check for ANY Hindi characters first (most reliable indicator)
        if re.search(r'[\u0900-\u097F]', text):
            print("🔍 Detected: Hindi (Hindi characters found)")
            return "hindi"
        
        # Check for common Hindi words in Roman script
        hindi_roman_words = [
            'kaise', 'kya', 'hai', 'mein', 'ki', 'ka', 'se', 'par', 'ho', 'raha', 'rahi',
            'chahta', 'chahti', 'nahi', 'kyun', 'kahan', 'kaun', 'kis', 'kisi', 'apna',
            'mera', 'tera', 'hamara', 'tumhara', 'accha', 'bura', 'sahi', 'galat'
        ]
        
        for word in hindi_roman_words:
            if word in text_lower:
                print(f"🔍 Detected: Hindi (Hindi word '{word}' found)")
                return "hindi"
        
        # Check for specific Hindi phrases in mixed input
        hindi_phrases = [
            'tell me about', 'construction site', 'site status', 'progress kya', 'kaise hai',
            'kya hai', 'mein kya', 'ki progress', 'ka status'
        ]
        
        for phrase in hindi_phrases:
            if phrase in text_lower:
                print(f"🔍 Detected: Hindi (Hindi phrase pattern '{phrase}' found)")
                return "hindi"
        
        # If no Hindi indicators found, it's English
        print("🔍 Detected: English (no Hindi indicators found)")
        return "english"
    
    def initialize_groq_client(self):
        """Initialize Groq client with proper error handling and model fallback"""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key == "your_groq_api_key_here":
                print("❌ GROQ_API_KEY not found or not set in .env file")
                self.client = None
                return
            
            self.client = Groq(api_key=api_key)
            working_model = self._find_working_model()
            if working_model:
                self.current_model = working_model
                print(f"✅ Groq client initialized with model: {self.current_model}")
            else:
                print("❌ No working Groq models found")
                self.client = None
            
        except Exception as e:
            print(f"❌ Groq initialization failed: {e}")
            self.client = None
    
    def _find_working_model(self):
        """Find a working model from the available list"""
        for model in self.available_models:
            try:
                print(f"🔄 Testing model: {model}")
                test_response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Say 'Hello' in Hindi"}],
                    max_tokens=20
                )
                print(f"✅ Model {model} is working!")
                return model
            except Exception as e:
                print(f"❌ Model {model} failed: {e}")
                continue
        return None
    
    def generate_response(self, user_input: str, conversation_history: list = None):
        """Generate contextual response using Groq LLM with fallback"""
        # Detect user's language
        user_language = self.detect_language(user_input)
        print(f"🗣️ User language detected: {user_language}")
        print(f"📝 User input: {user_input}")
        
        # First, try Groq API
        groq_response = self._try_groq_api(user_input, user_language, conversation_history)
        if groq_response:
            return groq_response
        
        # If Groq fails, use fallback responses in the same language
        return self._fallback_response(user_input, user_language)
    
    def _try_groq_api(self, user_input: str, user_language: str, conversation_history: list = None):
        """Try to get response from Groq API"""
        if not self.client:
            print("❌ Groq client not available")
            return None
        
        try:
            print(f"🔄 Sending request to Groq ({self.current_model}): {user_input[:50]}...")
            
            # Build conversation context with STRICT language guidance
            messages = self._build_prompt(user_input, user_language, conversation_history or [])
            
            # Get response from Groq
            completion = self.client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                top_p=1,
                stream=False
            )
            
            response = completion.choices[0].message.content.strip()
            print(f"✅ Groq response received: {response}")
            return response
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return None
    
    def _fallback_response(self, user_input: str, user_language: str) -> str:
        """Provide fallback responses in the same language as user"""
        if user_language == "hindi":
            return "नमस्ते सर। कंस्ट्रक्शन प्रगति पर है। फाउंडेशन पूरा, स्ट्रक्चरल 85% पूरा। विजिट: सोम-शनि, 10-5 बजे।"
        else:
            return "Hello Sir. Construction is progressing well. Foundation complete, structural 85% done. Visits: Mon-Sat, 10AM-5PM."
    
    def _build_prompt(self, user_input: str, user_language: str, conversation_history: list):
        """Build the prompt with STRICT language enforcement"""
        
        updates = self.construction_updates["current_status"]
        
        if user_language == "hindi":
            system_prompt = f"""आप रिवरवुड प्रोजेक्ट्स के लिए एक पेशेवर AI वॉइस असिस्टेंट हैं।

**भाषा निर्देश:**
- उपयोगकर्ता हिंदी में बोल रहा है
- आपको केवल और केवल हिंदी में जवाब देना है
- अंग्रेजी में बिल्कुल भी जवाब नहीं देना है

**प्रतिक्रिया निर्देश:**
- संक्षिप्त रहें (2-3 वाक्य)
- पेशेवर रहें
- केवल तथ्यात्मक जानकारी दें

**कंस्ट्रक्शन विवरण:**
- फाउंडेशन: {updates['foundation']}
- संरचनात्मक: {updates['structural']}
- विद्युत: {updates['electrical']}
- प्लंबिंग: {updates['plumbing']}
- अगला लक्ष्य: {updates['next_milestone']}
- साइट विजिट: {updates['site_visits']}

**उदाहरण प्रतिक्रियाएं (हिंदी में ही):**
- "नमस्ते सर। कंस्ट्रक्शन प्रगति पर है। फाउंडेशन पूरा, स्ट्रक्चरल 85% पूरा।"
- "साइट विजिट सोमवार से शनिवार, 10-5 बजे तक है।"
- "विद्युत कार्य 60% और प्लंबिंग 55% पूरा हो चुका है।"

**याद रखें: केवल हिंदी में जवाब दें। अंग्रेजी में नहीं।**"""
        
        else:
            system_prompt = f"""You are a professional AI Voice Assistant for Riverwood Projects.

**LANGUAGE INSTRUCTION:**
- The user is speaking in English
- You MUST respond ONLY in English
- Do NOT respond in Hindi at all

**RESPONSE INSTRUCTIONS:**
- Keep it brief (2-3 sentences)
- Stay professional
- Provide only factual information

**Construction Details:**
- Foundation: {updates['foundation']}
- Structural: {updates['structural']}
- Electrical: {updates['electrical']}
- Plumbing: {updates['plumbing']}
- Next Milestone: {updates['next_milestone']}
- Site Visits: {updates['site_visits']}

**Example Responses (English only):**
- "Hello Sir. Construction is progressing well. Foundation complete, structural 85% done."
- "Site visits are Monday to Saturday, 10AM to 5PM."
- "Electrical work is 60% and plumbing is 55% complete."

**REMEMBER: Respond ONLY in English. NOT in Hindi.**"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history for context
        for conv in conversation_history[-2:]:
            messages.append({"role": "user", "content": conv["user"]})
            messages.append({"role": "assistant", "content": conv["ai"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def get_construction_update(self):
        """Get current construction status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "updates": self.construction_updates
        }