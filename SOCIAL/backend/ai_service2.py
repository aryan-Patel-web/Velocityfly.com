"""
AI Service Module for YouTube & WhatsApp Content Generation
Enhanced AI content generation with multi-platform and multilingual support
"""

import os
import asyncio
import logging
import json
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import random

logger = logging.getLogger(__name__)

class AIService2:
    """Enhanced AI service for YouTube and WhatsApp content generation with multilingual support"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.primary_service = None
        self.is_mock = False
        
        # Initialize available services
        self.services = {
            "groq": bool(self.groq_api_key),
            "mistral": bool(self.mistral_api_key)
        }
        
        # Set primary service
        if self.groq_api_key:
            self.primary_service = "groq"
        elif self.mistral_api_key:
            self.primary_service = "mistral"
        else:
            self.is_mock = True
            self.primary_service = "mock"
            logger.warning("No AI API keys found - using mock service")
        
        # Multilingual support configuration
        self.supported_languages = {
            "english": {
                "name": "English",
                "native_name": "English",
                "code": "en",
                "direction": "ltr"
            },
            "hindi": {
                "name": "Hindi",
                "native_name": "हिन्दी",
                "code": "hi",
                "direction": "ltr"
            },
            "tamil": {
                "name": "Tamil",
                "native_name": "தமிழ்",
                "code": "ta",
                "direction": "ltr"
            },
            "telugu": {
                "name": "Telugu",
                "native_name": "తెలుగు",
                "code": "te",
                "direction": "ltr"
            },
            "bengali": {
                "name": "Bengali",
                "native_name": "বাংলা",
                "code": "bn",
                "direction": "ltr"
            },
            "marathi": {
                "name": "Marathi",
                "native_name": "मराठी",
                "code": "mr",
                "direction": "ltr"
            },
            "gujarati": {
                "name": "Gujarati",
                "native_name": "ગુજરાતી",
                "code": "gu",
                "direction": "ltr"
            },
            "malayalam": {
                "name": "Malayalam",
                "native_name": "മലയാളം",
                "code": "ml",
                "direction": "ltr"
            },
            "kannada": {
                "name": "Kannada",
                "native_name": "ಕನ್ನಡ",
                "code": "kn",
                "direction": "ltr"
            },
            "punjabi": {
                "name": "Punjabi",
                "native_name": "ਪੰਜਾਬੀ",
                "code": "pa",
                "direction": "ltr"
            },
            "assamese": {
                "name": "Assamese",
                "native_name": "অসমীয়া",
                "code": "as",
                "direction": "ltr"
            },
            "hinglish": {
                "name": "Hinglish",
                "native_name": "Hinglish (हिन्दी + English)",
                "code": "hi-en",
                "direction": "ltr"
            }
        }
        
        logger.info(f"AI Service initialized - Primary: {self.primary_service}")
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages"""
        return {
            "success": True,
            "languages": self.supported_languages,
            "default_language": "english",
            "total_languages": len(self.supported_languages)
        }
    
    async def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI service connection"""
        try:
            if self.is_mock:
                return {
                    "success": False,
                    "primary_service": "mock",
                    "services": self.services,
                    "error": "No API keys configured"
                }
            
            # Test primary service
            test_result = await self._test_service(self.primary_service)
            
            return {
                "success": test_result,
                "primary_service": self.primary_service,
                "services": self.services,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "primary_service": self.primary_service
            }
    
    async def _test_service(self, service_name: str) -> bool:
        """Test specific AI service"""
        try:
            if service_name == "groq":
                return await self._test_groq()
            elif service_name == "mistral":
                return await self._test_mistral()
            return False
        except Exception as e:
            logger.error(f"Service test failed for {service_name}: {e}")
            return False
    
    async def _test_groq(self) -> bool:
        """Test Groq API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": [{"role": "user", "content": "Test"}],
                        "model": "mixtral-8x7b-32768",
                        "max_tokens": 10
                    },
                    timeout=30
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def _test_mistral(self) -> bool:
        """Test Mistral API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.mistral_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-medium",
                        "messages": [{"role": "user", "content": "Test"}],
                        "max_tokens": 10
                    },
                    timeout=30
                )
                return response.status_code == 200
        except Exception:
            return False
    # dcdcdc
    
    
    # async def generate_youtube_content(
        async def generate_youtube_content(
        self,
        content_type: str = "shorts",
        topic: str = "general",
        target_audience: str = "general",
        duration_seconds: int = 30,
        style: str = "engaging",
        language: str = "english",
        region: str = "india",
        trending_context: dict = None
    ) -> Dict[str, Any]:
        """Generate YouTube content (title, description, script) with multilingual support"""
        try:
            if self.is_mock:
                return self._get_mock_youtube_content(content_type, topic, language)
            
            prompt = self._create_multilingual_youtube_prompt(
                content_type, topic, target_audience, duration_seconds, style, language, region, trending_context
            )
            
            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                content = result.get("content", "")
                parsed_content = self._parse_youtube_content(content, content_type)
                
                return {
                    "success": True,
                    "title": parsed_content.get("title"),
                    "description": parsed_content.get("description"),
                    "script": parsed_content.get("script"),
                    "tags": parsed_content.get("tags", []),
                    "content_type": content_type,
                    "language": language,
                    "region": region,
                    "ai_service": self.primary_service,
                    "word_count": len(content.split()),
                    "estimated_duration": duration_seconds,
                    "cultural_context": self._get_cultural_context(language, region)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"YouTube content generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_product_promo_content(
        self,
        product_data: Dict,
        target_audience: str = "young_adults",
        style: str = "trendy"
    ) -> Dict:
        """
        Generate promotional content for product
        
        Args:
            product_data: Scraped product data
            target_audience: young_adults, professionals, students
            style: trendy, professional, casual, energetic
        """
        try:
            product_name = product_data.get("product_name", "")
            brand = product_data.get("brand", "")
            price = product_data.get("price", 0)
            discount = product_data.get("discount", "")
            colors = product_data.get("colors", [])
            sizes = product_data.get("sizes", [])
            
            prompt = f"""Create promotional content for YouTube Short:

Product: {product_name}
Brand: {brand}
Price: ₹{price} {discount}
Available: {', '.join(colors[:3])} colors, {', '.join(sizes)} sizes
Target: {target_audience}, Style: {style}

Generate:
1. Catchy title (max 60 chars) with product name and brand
2. Engaging description with:
   - Hook line
   - Product features
   - Price and discount highlight
   - Call-to-action
   - Product link placeholder: {{{{PRODUCT_URL}}}}
3. 15 trending hashtags related to product category, style, and audience

Format as JSON:
{{
  "title": "...",
  "description": "...",
  "hashtags": ["fashion", "trending", ...]
}}
"""
            
            # Use existing _generate_with_primary_service method
            result = await self._generate_with_primary_service(prompt)
            
            if not result.get("success"):
                return result
            
            # Parse JSON response
            import json
            import re
            
            content_text = result.get("content", "")
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_text, re.DOTALL)
            if json_match:
                content_text = json_match.group(1)
            
            try:
                content = json.loads(content_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "success": False,
                    "error": "Failed to parse AI response as JSON"
                }
            
            # Add product details to description
            final_desc = f"""{content.get('description', '')}

🛒 Product Details:
Brand: {brand}
Price: ₹{price}
{f'💰 Save {discount}!' if discount else ''}
{f'Colors: {", ".join(colors[:3])}' if colors else ''}
{f'Sizes: {", ".join(sizes)}' if sizes else ''}

🔗 Buy Now: {{{{PRODUCT_URL}}}}

{' '.join(['#' + tag for tag in content.get('hashtags', [])[:15]])}
"""
            
            return {
                "success": True,
                "title": content.get('title', product_name),
                "description": final_desc,
                "hashtags": content.get('hashtags', [])
            }
            
        except Exception as e:
            logger.error(f"Product content generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

        


    
    
    def _create_multilingual_youtube_prompt(
        self,
        content_type: str,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        style: str,
        language: str,
        region: str,
        trending_context: dict = None
    ) -> str:
        """Create multilingual optimized prompt for YouTube content generation"""
        duration_text = "under 60 seconds" if content_type == "shorts" else f"approximately {duration_seconds} seconds"
        
        lang_info = self.supported_languages.get(language, self.supported_languages["english"])
        lang_name = lang_info["native_name"]
        
        cultural_context = self._get_cultural_context(language, region)
        festival_context = self._get_festival_context(region)
        
        base_prompt = f"""Create engaging YouTube {content_type} content about {topic} in {lang_name} language.

IMPORTANT LANGUAGE & CULTURAL REQUIREMENTS:
- Primary Language: {lang_name} ({lang_info["name"]})
- Target Region: {region.title()}
- Cultural Context: {cultural_context}
- Festival Context: {festival_context}
- Target Audience: {target_audience}
- Duration: {duration_text}
- Style: {style}
"""

        if language == "hinglish":
            base_prompt += """
HINGLISH SPECIFIC REQUIREMENTS:
- Mix Hindi and English naturally (60% Hindi, 40% English)
- Use popular Hinglish phrases: "bhai", "yaar", "kya baat hai", "main bolunga"
- Include trending social media terms: "trending", "viral", "subscribe karo"
- Write in Roman script but with Hindi grammar structure
- Examples: "Aaj main bataunga amazing cooking tips", "Ye video dekh kar tum shock ho jaoge"
"""
        elif language == "hindi":
            base_prompt += """
HINDI SPECIFIC REQUIREMENTS:
- Use pure Hindi with Devanagari script
- Include respectful terms: "आप", "जी", "धन्यवाद"
- Use cultural references familiar to Hindi speakers
- Include traditional greetings appropriate to context
"""
        elif language in ["tamil", "telugu", "bengali", "marathi", "gujarati", "malayalam", "kannada", "punjabi", "assamese"]:
            base_prompt += f"""
{lang_info["name"].upper()} SPECIFIC REQUIREMENTS:
- Use authentic {lang_info["name"]} script and grammar
- Include regional cultural references and phrases
- Use respectful forms of address appropriate to the language
- Include traditional elements familiar to {lang_info["name"]} speakers
"""

        base_prompt += f"""
Please provide:
1. TITLE: Catchy, SEO-optimized title in {lang_name} (60 chars max)
2. DESCRIPTION: Detailed description with keywords in {lang_name} (200-300 words)
3. SCRIPT: {"Short, punchy script for vertical video" if content_type == "shorts" else "Full video script with timestamps"} in {lang_name}
4. TAGS: 10 relevant tags mixing {lang_name} and English for better reach

Format your response as:
TITLE: [title in {lang_name}]
DESCRIPTION: [description in {lang_name}]
SCRIPT: [script in {lang_name}]
TAGS: [mix of {lang_name} and English tags]

CULTURAL NOTES: Include appropriate cultural references, festivals, or regional elements that would resonate with {target_audience} in {region}."""

        return base_prompt
    
    def _get_cultural_context(self, language: str, region: str) -> str:
        """Get cultural context for content generation"""
        contexts = {
            "hindi": "Include references to Indian festivals, family values, traditional cooking, Bollywood",
            "tamil": "Include references to Tamil culture, classical music, traditional festivals like Pongal",
            "telugu": "Include references to Telugu traditions, classical dance, festivals like Ugadi",
            "bengali": "Include references to Bengali culture, Durga Puja, fish curry, Rabindranath Tagore",
            "marathi": "Include references to Marathi culture, Ganesh Chaturthi, vada pav, regional pride",
            "gujarati": "Include references to Gujarati business culture, vegetarian food, Navratri",
            "malayalam": "Include references to Kerala culture, monsoons, coconut, classical arts",
            "kannada": "Include references to Karnataka culture, Mysore, classical music, festivals",
            "punjabi": "Include references to Punjab culture, Vaisakhi, farming, energetic lifestyle",
            "assamese": "Include references to Assam culture, Bihu festival, tea culture, silk",
            "hinglish": "Mix modern urban Indian culture with traditional values, use trendy social media language"
        }
        return contexts.get(language, "Include relevant Indian cultural context")
    
    def _get_festival_context(self, region: str) -> str:
        """Get current festival context"""
        current_month = datetime.now().month
        
        festival_calendar = {
            1: "Makar Sankranti, Pongal season",
            2: "Vasant Panchami, Maha Shivratri season",
            3: "Holi season, spring festivals",
            4: "Chaitra Navratri, Ram Navami season",
            5: "Akshaya Tritiya, Buddha Purnima season",
            6: "Rath Yatra season",
            7: "Guru Purnima season",
            8: "Raksha Bandhan, Krishna Janmashtami season",
            9: "Ganesh Chaturthi, Pitru Paksha season",
            10: "Navratri, Dussehra season",
            11: "Diwali, Karwa Chauth season",
            12: "Winter festivals season"
        }
        
        return festival_calendar.get(current_month, "Festival season")
    
    async def generate_community_post(
        self,
        post_type: str = "text",
        topic: str = "general",
        target_audience: str = "general",
        language: str = "english",
        region: str = "india"
    ) -> Dict[str, Any]:
        """Generate community post content with multilingual support"""
        try:
            if self.is_mock:
                return self._generate_mock_community_post(post_type, topic, target_audience, language)
            
            lang_info = self.supported_languages.get(language, self.supported_languages["english"])
            cultural_context = self._get_cultural_context(language, region)
            
            prompt = f"""Create a {post_type} community post about {topic} for {target_audience} in {lang_info["native_name"]} language.
            
            Requirements:
            - Language: {lang_info["native_name"]} ({lang_info["name"]})
            - Engaging and relevant to {target_audience}
            - Include appropriate emojis and call-to-action
            - For polls/quizzes: provide 4 options in {lang_info["native_name"]}
            - Keep content under 300 characters for posts
            - Cultural Context: {cultural_context}
            
            Topic: {topic}
            Post Type: {post_type}
            Target Audience: {target_audience}
            
            Format response as:
            CONTENT: [main post content in {lang_info["native_name"]}]
            OPTION1: [first option if poll/quiz in {lang_info["native_name"]}]
            OPTION2: [second option if poll/quiz in {lang_info["native_name"]}]
            OPTION3: [third option if poll/quiz in {lang_info["native_name"]}]
            OPTION4: [fourth option if poll/quiz in {lang_info["native_name"]}]
            """
            
            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                content = result.get("content", "")
                parsed = self._parse_community_post_content(content, post_type)
                
                return {
                    "success": True,
                    "content": parsed.get("content"),
                    "options": parsed.get("options", []),
                    "post_type": post_type,
                    "language": language,
                    "ai_service": self.primary_service
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Community post generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_community_post_content(self, content: str, post_type: str) -> Dict[str, Any]:
        """Parse AI-generated community post content"""
        try:
            lines = content.strip().split('\n')
            result = {
                "content": "",
                "options": []
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('CONTENT:'):
                    result['content'] = line[8:].strip()
                elif line.startswith('OPTION1:'):
                    result['options'].append(line[8:].strip())
                elif line.startswith('OPTION2:'):
                    result['options'].append(line[8:].strip())
                elif line.startswith('OPTION3:'):
                    result['options'].append(line[8:].strip())
                elif line.startswith('OPTION4:'):
                    result['options'].append(line[8:].strip())
            
            # Fallback if structured format not found
            if not result['content']:
                result['content'] = content.strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Community post parsing failed: {e}")
            return {
                "content": content.strip() if content else "AI generated community post",
                "options": []
            }
    
    def _generate_mock_community_post(self, post_type: str, topic: str, target_audience: str, language: str) -> Dict[str, Any]:
        """Generate mock community post content with multilingual support"""
        
        if language == "hindi":
            mock_templates = {
                "text": f"{topic} के बारे में कुछ अद्भुत जानकारी मिली! 🚀\n\nआपका {topic} के साथ क्या अनुभव है? नीचे कमेंट करें! 👇",
                "text_poll": {
                    "content": f"हमारे {target_audience} समुदाय के लिए एक त्वरित प्रश्न! 🤔\n\n{topic} के साथ आपकी सबसे बड़ी चुनौती क्या है?",
                    "options": [
                        f"{topic} की शुरुआत करना",
                        f"{topic} की उन्नत तकनीकें",
                        f"सही {topic} उपकरण खोजना",
                        f"{topic} के नवीनतम अपडेट"
                    ]
                }
            }
        elif language == "hinglish":
            mock_templates = {
                "text": f"Yaar, {topic} ke bare mein kya amazing cheez pata chali! 🚀\n\nTumhara {topic} ke saath kya experience hai? Comment mein batao! 👇",
                "text_poll": {
                    "content": f"Quick question hamare {target_audience} friends ke liye! 🤔\n\n{topic} mein tumhari biggest challenge kya hai?",
                    "options": [
                        f"{topic} start karna",
                        f"{topic} ke advanced tips",
                        f"Best {topic} tools dhundhna",
                        f"{topic} ke latest trends"
                    ]
                }
            }
        else:
            mock_templates = {
                "text": f"Just discovered something amazing about {topic}! 🚀\n\nWhat's your experience with {topic}? Share below! 👇",
                "text_poll": {
                    "content": f"Quick question for our {target_audience} community! 🤔\n\nWhat's your biggest {topic} challenge?",
                    "options": [
                        f"Getting started with {topic}",
                        f"Advanced {topic} techniques",
                        f"Finding the right {topic} tools",
                        f"Staying updated with {topic} trends"
                    ]
                }
            }
        
        if post_type in ['text_poll', 'image_poll', 'quiz']:
            template = mock_templates.get("text_poll", mock_templates['text_poll'])
            return {
                "success": True,
                "content": template["content"],
                "options": template["options"],
                "language": language,
                "ai_service": "mock"
            }
        else:
            return {
                "success": True,
                "content": mock_templates["text"],
                "options": [],
                "language": language,
                "ai_service": "mock"
            }
    
    async def generate_whatsapp_content(
        self,
        message_type: str = "promotional",
        business_type: str = "general",
        target_audience: str = "customers",
        occasion: str = None,
        call_to_action: str = None,
        language: str = "english",
        region: str = "india"
    ) -> Dict[str, Any]:
        """Generate WhatsApp message content with multilingual support"""
        try:
            if self.is_mock:
                return self._get_mock_whatsapp_content(message_type, business_type, language)
            
            lang_info = self.supported_languages.get(language, self.supported_languages["english"])
            cultural_context = self._get_cultural_context(language, region)
            
            prompt = self._create_whatsapp_prompt(
                message_type, business_type, target_audience, occasion, call_to_action, language, cultural_context
            )
            
            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                content = result.get("content", "")
                parsed_content = self._parse_whatsapp_content(content, message_type)
                
                return {
                    "success": True,
                    "message": parsed_content.get("message"),
                    "subject": parsed_content.get("subject"),
                    "call_to_action": parsed_content.get("call_to_action"),
                    "emojis": parsed_content.get("emojis", []),
                    "message_type": message_type,
                    "language": language,
                    "ai_service": self.primary_service,
                    "char_count": len(parsed_content.get("message", "")),
                    "estimated_read_time": len(parsed_content.get("message", "").split()) // 3
                }
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp content generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_whatsapp_reply(
        self,
        incoming_message: str,
        business_context: Dict[str, Any] = None,
        language: str = "english"
    ) -> Dict[str, Any]:
        """Generate WhatsApp auto-reply with multilingual support"""
        try:
            if self.is_mock:
                mock_replies = {
                    "hindi": "आपके संदेश के लिए धन्यवाद! हम जल्द ही आपसे संपर्क करेंगे।",
                    "hinglish": "Thank you for your message! Hum jaldi hi aapse contact karenge.",
                    "english": "Thank you for your message! We'll get back to you soon."
                }
                return {
                    "success": True,
                    "reply": mock_replies.get(language, mock_replies["english"]),
                    "language": language,
                    "ai_service": "mock"
                }
            
            lang_info = self.supported_languages.get(language, self.supported_languages["english"])
            business_name = business_context.get("business_name", "our business") if business_context else "our business"
            business_type = business_context.get("business_type", "customer service") if business_context else "customer service"
            
            prompt = f"""Generate a professional and helpful WhatsApp auto-reply for {business_name} ({business_type}) in {lang_info["native_name"]} language.

Incoming message: "{incoming_message}"

Requirements:
- Language: {lang_info["native_name"]} ({lang_info["name"]})
- Professional but friendly tone
- Acknowledge their message
- Provide helpful response if possible
- Keep it concise (under 100 words)
- Include business name if appropriate
- Use appropriate emojis sparingly
- Cultural context appropriate for Indian businesses

Generate only the reply message in {lang_info["native_name"]}, no extra text."""

            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                reply = result.get("content", "").strip()
                
                return {
                    "success": True,
                    "reply": reply,
                    "language": language,
                    "ai_service": self.primary_service,
                    "original_message": incoming_message
                }
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp reply generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_comment_reply(
        self,
        comment_text: str,
        video_title: str = "",
        reply_style: str = "friendly",
        language: str = "english",
        custom_prompt: str = ""
    ) -> Dict[str, Any]:
        """Generate YouTube comment reply using AI with emotion detection"""
        try:
            if self.is_mock:
                emotion = self._detect_comment_emotion(comment_text)
                return self._generate_mock_comment_reply(comment_text, language, emotion)
            
            # Detect emotion from comment
            emotion = self._detect_comment_emotion(comment_text)
            
            lang_info = self.supported_languages.get(language, self.supported_languages["english"])
            
            # Create emotion-aware prompt
            base_prompt = f"""Generate a friendly YouTube comment reply in {lang_info["native_name"]}.

Comment: "{comment_text}"
Emotion: {emotion}
Style: {reply_style}
Rules:
- Reply in {lang_info["native_name"]} only
- Maximum 30 words
- Use 1-2 appropriate emojis
- Match the emotion: love=❤️😊, funny=😂🤣, angry=😇🙏, question=👍

Generate only the reply text:"""

            if custom_prompt:
                base_prompt += f"\nExtra: {custom_prompt}"

            result = await self._generate_with_primary_service(base_prompt)
            
            if result.get("success"):
                reply_text = result.get("content", "").strip()
                reply_text = self._clean_reply_text(reply_text)
                
                return {
                    "success": True,
                    "reply": reply_text,
                    "language": language,
                    "emotion": emotion,
                    "ai_service": self.primary_service
                }
            else:
                emotion = self._detect_comment_emotion(comment_text)
                return self._generate_mock_comment_reply(comment_text, language, emotion)
        
        except Exception as e:
            logger.error(f"Comment reply generation failed: {e}")
            emotion = self._detect_comment_emotion(comment_text)
            return self._generate_mock_comment_reply(comment_text, language, emotion)

    def _detect_comment_emotion(self, text: str) -> str:
        """Detect emotion from comment text"""
        text_lower = text.lower()
        
        # Love/positive
        if any(word in text_lower for word in ["love", "amazing", "great", "❤️", "😍", "👍", "बहुत अच्छा", "शानदार"]):
            return "love"
        
        # Funny
        if any(word in text_lower for word in ["lol", "haha", "funny", "😂", "🤣", "हंसी", "मज़ेदार"]):
            return "funny"
        
        # Angry/negative
        if any(word in text_lower for word in ["hate", "bad", "stupid", "😠", "😡", "बुरा"]):
            return "angry"
        
        # Question
        if "?" in text or any(word in text_lower for word in ["how", "what", "why", "कैसे", "क्या"]):
            return "question"
        
        return "neutral"

    def _clean_reply_text(self, text: str) -> str:
        """Clean AI response"""
        # Remove prefixes
        prefixes = ["Reply:", "Response:", "Answer:", "उत्तर:", "जवाब:"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Remove quotes and limit length
        text = text.strip('"\'')
        if len(text) > 100:
            text = text[:97] + "..."
        
        return text

    def _generate_mock_comment_reply(self, comment_text: str, language: str, emotion: str = "neutral") -> Dict[str, Any]:
        """Generate mock replies"""
        
        if language == "hindi":
            replies = {
                "love": "आपके प्यार के लिए धन्यवाद! ❤️😊",
                "funny": "हंसाने के लिए शुक्रिया! 😂🤣",
                "angry": "समझ सकते हैं। बेहतर बनाने की कोशिश करेंगे 😇🙏",
                "question": "अच्छा सवाल! जवाब जल्दी मिलेगा 👍",
                "neutral": "कमेंट के लिए धन्यवाद! 😊"
            }
        elif language == "hinglish":
            replies = {
                "love": "Thank you yaar! Bahut khushi hui ❤️😊",
                "funny": "Haha, accha laga tumhe funny laga! 😂🤣", 
                "angry": "Sorry yaar, better karne ki koshish karenge 😇🙏",
                "question": "Good question! Answer milega soon 👍",
                "neutral": "Thanks for commenting! 😊"
            }
        else:
            replies = {
                "love": "Thank you so much! ❤️😊",
                "funny": "Glad it made you laugh! 😂🤣",
                "angry": "Sorry about that. We'll improve 😇🙏", 
                "question": "Great question! Answer coming soon 👍",
                "neutral": "Thanks for watching! 😊"
            }
        
        return {
            "success": True,
            "reply": replies.get(emotion, replies["neutral"]),
            "language": language,
            "emotion": emotion,
            "ai_service": "mock"
        }
    
    async def _generate_with_primary_service(self, prompt: str) -> Dict[str, Any]:
        """Generate content with primary AI service"""
        try:
            if self.primary_service == "groq":
                return await self._generate_with_groq(prompt)
            elif self.primary_service == "mistral":
                return await self._generate_with_mistral(prompt)
            else:
                return {"success": False, "error": "No AI service available"}
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_with_groq(self, prompt: str) -> Dict[str, Any]:
        """Generate content using Groq API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert multilingual content creator specializing in social media and digital marketing. You can create engaging, authentic, and platform-optimized content in multiple Indian languages including Hindi, Tamil, Telugu, Bengali, Marathi, and Hinglish. Always maintain cultural sensitivity and use appropriate regional context."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "model": "llama-3.3-70b-versatile",
                        "max_tokens": 2000,
                        "temperature": 0.8,
                        "top_p": 0.9
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "content": content.strip(),
                        "ai_service": "groq",
                        "model": "llama-3.3-70b-versatile",
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        "success": False,
                        "error": f"Groq API error: {response.status_code}",
                        "details": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_with_mistral(self, prompt: str) -> Dict[str, Any]:
        """Generate content using Mistral API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.mistral_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-medium",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert multilingual content creator specializing in social media and digital marketing. You can create engaging, authentic, and platform-optimized content in multiple Indian languages including Hindi, Tamil, Telugu, Bengali, Marathi, and Hinglish. Always maintain cultural sensitivity and use appropriate regional context."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.8,
                        "top_p": 0.9
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "content": content.strip(),
                        "ai_service": "mistral",
                        "model": "mistral-medium",
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        "success": False,
                        "error": f"Mistral API error: {response.status_code}",
                        "details": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"Mistral generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_whatsapp_prompt(
        self,
        message_type: str,
        business_type: str,
        target_audience: str,
        occasion: str = None,
        call_to_action: str = None,
        language: str = "english",
        cultural_context: str = ""
    ) -> str:
        """Create optimized prompt for WhatsApp content generation"""
        lang_info = self.supported_languages.get(language, self.supported_languages["english"])
        occasion_text = f" for {occasion}" if occasion else ""
        cta_text = f"\n- Call to action: {call_to_action}" if call_to_action else ""
        
        return f"""Create a {message_type} WhatsApp message for a {business_type} business{occasion_text} in {lang_info["native_name"]} language.

Requirements:
- Language: {lang_info["native_name"]} ({lang_info["name"]})
- Target audience: {target_audience}
- Message type: {message_type}
- Keep under 160 characters for SMS compatibility
- Professional but friendly tone
- Use appropriate emojis (2-3 max)
- Clear and actionable{cta_text}
- Cultural Context: {cultural_context}

Format your response as:
SUBJECT: [subject line if needed in {lang_info["native_name"]}]
MESSAGE: [main message content in {lang_info["native_name"]}]
CTA: [call to action in {lang_info["native_name"]}]
EMOJIS: [list of suggested emojis]"""
    
    def _parse_youtube_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Parse AI-generated YouTube content"""
        try:
            lines = content.strip().split('\n')
            result = {
                "title": "",
                "description": "",
                "script": "",
                "tags": []
            }
            
            current_section = None
            section_content = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('TITLE:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'title'
                    section_content = [line[6:].strip()]
                elif line.startswith('DESCRIPTION:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'description'
                    section_content = [line[12:].strip()]
                elif line.startswith('SCRIPT:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'script'
                    section_content = [line[7:].strip()]
                elif line.startswith('TAGS:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'tags'
                    tags_text = line[5:].strip()
                    result['tags'] = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                elif current_section and line:
                    section_content.append(line)
            
            # Handle last section
            if current_section and current_section != 'tags':
                result[current_section] = '\n'.join(section_content).strip()
            
            # Fallback parsing if structured format not found
            if not result['title'] and content:
                lines = content.split('\n')
                result['title'] = lines[0][:60] if lines else "AI Generated Content"
                result['description'] = content[:300] if len(content) > 60 else content
                result['script'] = content
            
            return result
            
        except Exception as e:
            logger.error(f"YouTube content parsing failed: {e}")
            return {
                "title": "AI Generated Content",
                "description": content[:300] if content else "AI generated description",
                "script": content or "AI generated script",
                "tags": ["AI", "generated", "content"]
            }
    
    def _parse_whatsapp_content(self, content: str, message_type: str) -> Dict[str, Any]:
        """Parse AI-generated WhatsApp content"""
        try:
            lines = content.strip().split('\n')
            result = {
                "subject": "",
                "message": "",
                "call_to_action": "",
                "emojis": []
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('SUBJECT:'):
                    result['subject'] = line[8:].strip()
                elif line.startswith('MESSAGE:'):
                    result['message'] = line[8:].strip()
                elif line.startswith('CTA:'):
                    result['call_to_action'] = line[4:].strip()
                elif line.startswith('EMOJIS:'):
                    emojis_text = line[7:].strip()
                    result['emojis'] = [emoji.strip() for emoji in emojis_text.split(',') if emoji.strip()]
            
            # Fallback if structured format not found
            if not result['message'] and content:
                result['message'] = content.strip()
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp content parsing failed: {e}")
            return {
                "subject": "",
                "message": content.strip() if content else "AI generated message",
                "call_to_action": "",
                "emojis": []
            }
    
    def _get_mock_youtube_content(self, content_type: str, topic: str, language: str) -> Dict[str, Any]:
        """Generate mock YouTube content for testing with multilingual support"""
        
        if language == "hindi":
            mock_titles = [
                f"अद्भुत {topic} टिप्स जो आपको जानने चाहिए!",
                f"शुरुआती लोगों के लिए अंतिम {topic} गाइड",
                f"5 आश्चर्यजनक {topic} तथ्य जो आपको चौंका देंगे"
            ]
        elif language == "hinglish":
            mock_titles = [
                f"Amazing {topic} tips jo tumhe pata hone chahiye!",
                f"Beginners ke liye ultimate {topic} guide",
                f"5 mind-blowing {topic} facts jo tumhe shock kar denge"
            ]
        else:
            mock_titles = [
                f"Amazing {topic} Tips You Need to Know!",
                f"The Ultimate {topic} Guide for Beginners",
                f"5 Mind-Blowing {topic} Facts That Will Surprise You"
            ]
        
        return {
            "success": True,
            "title": random.choice(mock_titles),
            "description": f"Mock description for {content_type} about {topic} in {language}. This is generated by the mock AI service for testing purposes.",
            "script": f"Mock script for {content_type} in {language}:\n1. Introduction about {topic}\n2. Main content points\n3. Call to action",
            "tags": ["mock", topic.lower(), content_type, "ai", "generated", language],
            "content_type": content_type,
            "language": language,
            "ai_service": "mock",
            "word_count": 25,
            "estimated_duration": 30 if content_type == "shorts" else 180
        }
    
    def _get_mock_whatsapp_content(self, message_type: str, business_type: str, language: str) -> Dict[str, Any]:
        """Generate mock WhatsApp content for testing with multilingual support"""
        
        if language == "hindi":
            mock_messages = {
                "promotional": f"🎉 आपके पसंदीदा {business_type} से विशेष ऑफर! सीमित समय के लिए। विवरण के लिए संपर्क करें!",
                "customer_service": f"{business_type} से संपर्क करने के लिए धन्यवाद! हम 24 घंटे के भीतर वापस संपर्क करेंगे।",
                "notification": f"📢 {business_type} से महत्वपूर्ण अपडेट। हमारी नवीनतम समाचार और अपडेट देखें।"
            }
        elif language == "hinglish":
            mock_messages = {
                "promotional": f"🎉 Special offer from your favorite {business_type}! Limited time only. Details ke liye contact karo!",
                "customer_service": f"Thank you for contacting {business_type}! Hum 24 hours mein wapis contact karenge.",
                "notification": f"📢 Important update from {business_type}. Latest news aur updates check karo."
            }
        else:
            mock_messages = {
                "promotional": f"🎉 Special offer from your favorite {business_type}! Limited time only. Contact us for details!",
                "customer_service": f"Thank you for contacting {business_type}! We'll get back to you within 24 hours.",
                "notification": f"📢 Important update from {business_type}. Check our latest news and updates."
            }
        
        message = mock_messages.get(message_type, f"Mock {message_type} message for {business_type} in {language}")
        
        return {
            "success": True,
            "message": message,
            "subject": f"Mock {message_type} subject",
            "call_to_action": "Contact us for more information",
            "emojis": ["🎉", "📢", "✨"],
            "message_type": message_type,
            "language": language,
            "ai_service": "mock",
            "char_count": len(message),
            "estimated_read_time": 3
        }
    
    async def generate_reddit_domain_content(self, **kwargs) -> Dict[str, Any]:
        """Backward compatibility with existing Reddit AI service"""
        try:
            domain = kwargs.get('domain', 'general')
            business_type = kwargs.get('business_type', 'Business')
            content_style = kwargs.get('content_style', 'engaging')
            language = kwargs.get('language', 'english')
            
            if self.is_mock:
                return {
                    "success": True,
                    "title": f"Mock {domain} content for {business_type}",
                    "content": f"Mock content generated for {business_type} in {domain} domain with {content_style} style in {language}.",
                    "language": language,
                    "ai_service": "mock",
                    "word_count": 15
                }
            
            lang_info = self.supported_languages.get(language, self.supported_languages["english"])
            
            prompt = f"""Create engaging {content_style} content for a {business_type} in the {domain} domain in {lang_info["native_name"]} language.
            
Requirements:
- Language: {lang_info["native_name"]} ({lang_info["name"]})
- Professional and informative
- Engaging for social media
- Include valuable insights
- Keep it concise but informative
- Cultural context appropriate for Indian audience

Format:
TITLE: [engaging title in {lang_info["native_name"]}]
CONTENT: [main content in {lang_info["native_name"]}]"""

            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                content = result.get("content", "")
                lines = content.split('\n')
                
                title = ""
                main_content = ""
                
                for line in lines:
                    if line.startswith('TITLE:'):
                        title = line[6:].strip()
                    elif line.startswith('CONTENT:'):
                        main_content = line[8:].strip()
                    elif not title and line.strip():
                        title = line.strip()
                    elif title and line.strip():
                        main_content += line + "\n"
                
                return {
                    "success": True,
                    "title": title or f"AI Generated {domain} Content",
                    "content": main_content.strip() or content,
                    "language": language,
                    "ai_service": self.primary_service,
                    "word_count": len(content.split())
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Backward compatibility content generation failed: {e}")
            return {"success": False, "error": str(e)}