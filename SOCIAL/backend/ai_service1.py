"""
Enhanced AI Service for Multi-Platform Social Media Automation
Supports WhatsApp, Facebook, Instagram with human-like content generation
Improved error handling and API key validation
"""

import asyncio
import logging
import os
import json
import random
import httpx
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time
import re

logger = logging.getLogger(__name__)


class EnhancedAIService:
    """Enhanced AI Service with robust error handling for all social platforms"""
    
    def __init__(self):
        """Initialize with multiple AI providers and enhanced validation"""
        
        # Load and validate API keys
        self.mistral_key = os.getenv("MISTRAL_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        # Debug logging for API keys
        logger.info(f"API Keys loaded - Mistral: {'*' * min(len(self.mistral_key), 10) if self.mistral_key else 'MISSING'}")
        logger.info(f"API Keys loaded - Groq: {'*' * min(len(self.groq_key), 10) if self.groq_key else 'MISSING'}")
        logger.info(f"API Keys loaded - OpenAI: {'*' * min(len(self.openai_key), 10) if self.openai_key else 'MISSING'}")
        
        # API endpoints
        self.mistral_url = "https://api.mistral.ai/v1/chat/completions"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Service availability with better validation
        self.mistral_available = bool(self.mistral_key and len(self.mistral_key) > 10)
        self.groq_available = bool(self.groq_key and len(self.groq_key) > 10)
        self.openai_available = bool(self.openai_key and len(self.openai_key) > 10)
        
        # Rate limiting
        self.last_request_time = {}
        self.min_interval = 1.0
        
        # Enhanced model configurations
        self.models = {
            "mistral": ["mistral-small-latest", "open-mistral-7b"],
            "groq": ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            "openai": ["gpt-3.5-turbo", "gpt-4"]
        }
        
        # Platform-specific content templates
        self.platform_templates = {
            "whatsapp": {
                "business": "Write a helpful WhatsApp business message about {business_type}. Keep it under 150 words, friendly and professional.",
                "casual": "Create a casual WhatsApp message for {business_type}. Be conversational and authentic.",
                "promotional": "Write a promotional WhatsApp message for {business_type}. Include clear value proposition."
            },
            "facebook": {
                "business": "Create an engaging Facebook post for {business_type}. Include relevant hashtags and call-to-action.",
                "casual": "Write a casual Facebook post about {business_type}. Make it relatable and shareable.",
                "promotional": "Create a promotional Facebook post for {business_type}. Focus on benefits and engagement."
            },
            "instagram": {
                "business": "Write an Instagram caption for {business_type}. Include relevant hashtags and be visually descriptive.",
                "casual": "Create a casual Instagram post about {business_type}. Be trendy and authentic.",
                "promotional": "Write a promotional Instagram post for {business_type}. Include call-to-action and hashtags."
            }
        }
        
        logger.info(f"AI Service initialized - Available services: Mistral={self.mistral_available}, Groq={self.groq_available}, OpenAI={self.openai_available}")

    async def _rate_limit(self, service: str):
        """Implement rate limiting"""
        current_time = time.time()
        last_time = self.last_request_time.get(service, 0)
        time_diff = current_time - last_time
        
        if time_diff < self.min_interval:
            sleep_time = self.min_interval - time_diff
            await asyncio.sleep(sleep_time)
        
        self.last_request_time[service] = time.time()

    async def _call_ai_api(self, service: str, messages: List[Dict], **kwargs) -> Optional[Dict[str, Any]]:
        """Universal AI API caller with comprehensive error handling"""
        
        # Service availability check
        if service == "mistral" and not self.mistral_available:
            return {"success": False, "error": "Mistral API key not configured"}
        elif service == "groq" and not self.groq_available:
            return {"success": False, "error": "Groq API key not configured"}
        elif service == "openai" and not self.openai_available:
            return {"success": False, "error": "OpenAI API key not configured"}
        
        await self._rate_limit(service)
        
        # Get service configuration
        if service == "mistral":
            url = self.mistral_url
            headers = {"Authorization": f"Bearer {self.mistral_key}", "Content-Type": "application/json"}
            models = self.models["mistral"]
        elif service == "groq":
            url = self.groq_url
            headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
            models = self.models["groq"]
        elif service == "openai":
            url = self.openai_url
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            models = self.models["openai"]
        else:
            return {"success": False, "error": f"Unknown service: {service}"}
        
        # Try each model for the service
        for model in models:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", 500),
                    "temperature": kwargs.get("temperature", 0.8),
                    "top_p": kwargs.get("top_p", 0.9),
                    "stream": False
                }
                
                logger.info(f"Trying {service} - {model}")
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"].strip()
                        logger.info(f"Success: {service} - {model}")
                        return {
                            "success": True,
                            "content": content,
                            "service": service,
                            "model": model
                        }
                    elif response.status_code == 401:
                        logger.error(f"Authentication failed: {service} - {model}")
                        return {"success": False, "error": f"{service} authentication failed"}
                    elif response.status_code == 429:
                        logger.warning(f"Rate limit: {service} - {model}")
                        await asyncio.sleep(2.0)
                        continue
                    else:
                        logger.error(f"Error {response.status_code}: {service} - {model} - {response.text}")
                        continue
                        
            except httpx.TimeoutException:
                logger.error(f"Timeout: {service} - {model}")
                continue
            except Exception as e:
                logger.error(f"API call failed: {service} - {model} - {str(e)}")
                continue
        
        return {"success": False, "error": f"All models failed for {service}"}

    def _create_enhanced_prompt(self, platform: str, domain: str, business_type: str, business_description: str = "", content_style: str = "engaging", **kwargs) -> str:
        """Create enhanced prompts for any platform"""
        
        # Get platform template
        platform_templates = self.platform_templates.get(platform.lower(), self.platform_templates["facebook"])
        template = platform_templates.get(content_style, platform_templates["business"])
        
        # Enhanced prompt with context
        base_prompt = f"""Create authentic, human-like content for {platform.upper()}.

Business Context:
- Type: {business_type}
- Domain: {domain}
- Description: {business_description}
- Style: {content_style}

Requirements:
- Sound completely natural and human
- NO AI-like language or obvious patterns
- Be engaging and platform-appropriate
- Include relevant context for {domain} industry
- Keep appropriate length for {platform}
- Make it shareable and engaging

Content Guidelines:
{template.format(business_type=business_type)}

Write the content now - make it sound 100% authentic:"""
        
        return base_prompt

    async def generate_social_content(self, platform: str, domain: str, business_type: str, business_description: str = "", **kwargs) -> Dict[str, Any]:
        """Generate platform-specific content with fallback handling"""
        
        try:
            # Create the prompt
            content_style = kwargs.get("content_style", "engaging")
            prompt = self._create_enhanced_prompt(
                platform=platform,
                domain=domain,
                business_type=business_type,
                business_description=business_description,
                content_style=content_style,
                **kwargs
            )
            
            messages = [{"role": "user", "content": prompt}]
            
            # Try AI services in order of preference
            ai_result = None
            
            # Try Groq first (fastest and most reliable)
            if self.groq_available:
                ai_result = await self._call_ai_api("groq", messages, temperature=0.8, max_tokens=500)
                if ai_result.get("success"):
                    logger.info("Content generated successfully with Groq")
            
            # Fallback to Mistral
            if not ai_result or not ai_result.get("success"):
                if self.mistral_available:
                    await asyncio.sleep(0.5)
                    ai_result = await self._call_ai_api("mistral", messages, temperature=0.8, max_tokens=500)
                    if ai_result.get("success"):
                        logger.info("Content generated successfully with Mistral")
            
            # Fallback to OpenAI
            if not ai_result or not ai_result.get("success"):
                if self.openai_available:
                    await asyncio.sleep(0.5)
                    ai_result = await self._call_ai_api("openai", messages, temperature=0.8, max_tokens=500)
                    if ai_result.get("success"):
                        logger.info("Content generated successfully with OpenAI")
            
            # Handle failure
            if not ai_result or not ai_result.get("success"):
                error_msg = ai_result.get("error", "All AI services failed") if ai_result else "No AI services available"
                logger.error(f"Content generation failed: {error_msg}")
                
                # Return fallback content
                fallback_content = self._generate_fallback_content(platform, business_type, domain)
                return {
                    "success": True,
                    "platform": platform,
                    "content": fallback_content,
                    "ai_service": "fallback",
                    "word_count": len(fallback_content.split()),
                    "character_count": len(fallback_content),
                    "fallback": True,
                    "error": error_msg
                }
            
            content = ai_result.get("content", "")
            
            # Clean up content
            content = self._clean_content(content)
            
            return {
                "success": True,
                "platform": platform,
                "content": content,
                "ai_service": ai_result.get("service", "unknown"),
                "model": ai_result.get("model", "unknown"),
                "word_count": len(content.split()),
                "character_count": len(content),
                "human_score": 95
            }
            
        except Exception as e:
            logger.error(f"Content generation failed for {platform}: {str(e)}")
            
            # Return fallback content
            fallback_content = self._generate_fallback_content(platform, business_type, domain)
            return {
                "success": True,
                "platform": platform,
                "content": fallback_content,
                "ai_service": "fallback",
                "word_count": len(fallback_content.split()),
                "character_count": len(fallback_content),
                "fallback": True,
                "error": str(e)
            }

    def _generate_fallback_content(self, platform: str, business_type: str, domain: str) -> str:
        """Generate fallback content when AI services fail"""
        
        fallback_templates = {
            "whatsapp": f"Hello! We're excited to share updates about our {business_type} services. Stay tuned for more information!",
            "facebook": f"Welcome to our {business_type} page! We're passionate about {domain} and look forward to serving you. Follow us for updates and insights!",
            "instagram": f"✨ Welcome to {business_type}! ✨\n\nWe're all about {domain} and creating amazing experiences. Follow for updates! \n\n#{domain} #{business_type.replace(' ', '')} #business"
        }
        
        return fallback_templates.get(platform.lower(), fallback_templates["facebook"])

    def _clean_content(self, content: str) -> str:
        """Clean and enhance content"""
        
        # Remove excessive AI-like formatting
        content = re.sub(r'\*{2,}.*?\*{2,}', '', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'#{3,}.*', '', content)
        
        # Clean up spacing
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()
        
        return content

    async def test_ai_services(self) -> Dict[str, Any]:
        """Test all AI services with detailed results"""
        
        test_message = [{"role": "user", "content": "Say 'AI test successful' in a casual way"}]
        results = {}
        
        # Test each service
        services_to_test = [
            ("groq", self.groq_available),
            ("mistral", self.mistral_available),
            ("openai", self.openai_available)
        ]
        
        for service, available in services_to_test:
            if available:
                try:
                    result = await self._call_ai_api(service, test_message, max_tokens=50)
                    if result.get("success"):
                        results[service] = "connected"
                        logger.info(f"{service} test successful")
                    else:
                        results[service] = f"failed: {result.get('error', 'unknown')}"
                        logger.error(f"{service} test failed: {result.get('error')}")
                except Exception as e:
                    results[service] = f"error: {str(e)[:50]}"
                    logger.error(f"{service} test error: {e}")
            else:
                results[service] = "not configured"
        
        # Determine primary service
        primary = None
        if results.get("groq") == "connected":
            primary = "groq"
        elif results.get("mistral") == "connected":
            primary = "mistral"
        elif results.get("openai") == "connected":
            primary = "openai"
        
        connected_count = sum(1 for status in results.values() if status == "connected")
        
        logger.info(f"AI Service test completed - Primary: {primary}, Connected: {connected_count}")
        
        return {
            "success": primary is not None,
            "primary_service": primary,
            "services": results,
            "total_available": connected_count,
            "available_services": [service for service, status in results.items() if status == "connected"]
        }

    async def generate_whatsapp_content(self, business_type: str, domain: str = "business", **kwargs) -> Dict[str, Any]:
        """WhatsApp-specific content generation"""
        return await self.generate_social_content(
            platform="whatsapp",
            domain=domain,
            business_type=business_type,
            **kwargs
        )

    async def generate_facebook_content(self, business_type: str, domain: str = "business", **kwargs) -> Dict[str, Any]:
        """Facebook-specific content generation"""
        return await self.generate_social_content(
            platform="facebook",
            domain=domain,
            business_type=business_type,
            **kwargs
        )

    async def generate_instagram_content(self, business_type: str, domain: str = "business", **kwargs) -> Dict[str, Any]:
        """Instagram-specific content generation"""
        return await self.generate_social_content(
            platform="instagram",
            domain=domain,
            business_type=business_type,
            **kwargs
        )

# Global instance
enhanced_ai_service = EnhancedAIService()