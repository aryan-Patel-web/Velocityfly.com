"""
Complete Social Media Automation Backend - Part 1
REAL WhatsApp API Integration - Production Ready
Core imports, environment setup, and WhatsApp classes
"""

# Standard library imports
import asyncio
import json
import logging
import os
import sys
import threading
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import hmac
import hashlib

# Third-party imports
import bcrypt
import jwt
import requests
import schedule
import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

# Load environment variables first
load_dotenv()

# WhatsApp Configuration - Environment with hardcoded fallbacks for testing
WHATSAPP_ACCESS_TOKEN = (
    os.getenv('WHATSAPP_TOKEN') or 
    os.getenv('WHATSAPP_ACCESS_TOKEN') or
    "EAALNGPo4t80BPVCNDAKG9VCphy4OmQxVkZCsZCPAvYZCrHgRfSCmZAcLnRNiOM8MD97IjQNl0p7z2A5WDt3IxjmDRzdJOr1AZCwOr7kVZAZAe81MGsVMbRQks2cSv2jq49LlSa4HFlSLZAbhM8uYezRUNukGcm9oZALUj1u0ACxzZCZCZB9voYbCApSaoZCjA4egSjv45YwZDZD"
)

WHATSAPP_PHONE_NUMBER_ID = (
    os.getenv('WHATSAPP_PHONE_NUMBER_ID') or
    "842943155558927"
)

WHATSAPP_BUSINESS_ACCOUNT_ID = (
    os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID') or
    "1582621679368728"
)

META_APP_SECRET = (
    os.getenv('META_APP_SECRET') or
    "3a6fba32779a94c001b274ab91c026ee"
)

WEBHOOK_VERIFY_TOKEN = (
    os.getenv('WEBHOOK_VERIFY_TOKEN') or
    "whatsapp_webhook_verify_2024_secure_velocity"
)

print(f"WhatsApp Token loaded: {WHATSAPP_ACCESS_TOKEN[:20]}..." if WHATSAPP_ACCESS_TOKEN else "No token")
print(f"Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}")
print(f"Business Account ID: {WHATSAPP_BUSINESS_ACCOUNT_ID}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Global Variables
user_whatsapp_tokens = {}
user_facebook_tokens = {}
user_instagram_tokens = {}
oauth_states = {}

# Try to import custom modules with error handling
try:
    from ai_service1 import EnhancedAIService
    AI_AVAILABLE = True
    logger.info("AI Service imported successfully")
except ImportError as e:
    AI_AVAILABLE = False
    logger.warning(f"AI Service not available: {e}")

try:
    from database1 import MultiUserSocialDatabase
    DB_AVAILABLE = True
    logger.info("Database module imported successfully")
except ImportError as e:
    DB_AVAILABLE = False
    logger.warning(f"Database not available: {e}")

try:
    from whatsapp import WhatsAppCloudAPI, WhatsAppWebhookHandler, WhatsAppAutomationScheduler, WhatsAppConfig
    WHATSAPP_AVAILABLE = True
    logger.info("WhatsApp module imported successfully")
except ImportError as e:
    WHATSAPP_AVAILABLE = False
    logger.warning(f"WhatsApp module not available: {e}")

# Pydantic Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AutoPostingRequest(BaseModel):
    platform: str
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 3
    posting_times: List[str] = []

class ManualPostRequest(BaseModel):
    platform: str
    title: str
    content: str
    page_id: str = ""
    image_url: str = ""

class WhatsAppMessageRequest(BaseModel):
    to: str
    message: str
    message_type: str = "text"

class WhatsAppBroadcastRequest(BaseModel):
    recipient_list: List[str]
    message: str
    media_url: str = ""
    media_type: str = ""

class TestPostRequest(BaseModel):
    platform: str
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    content_style: str = "engaging"

class WhatsAppSetupRequest(BaseModel):
    phone_number_id: str
    access_token: str
    business_name: str = ""
    auto_reply_enabled: bool = True
    campaign_enabled: bool = True
    business_hours: Dict[str, str] = {"start": "09:00", "end": "18:00"}
    timezone: str = "Asia/Kolkata"

# Real WhatsApp Cloud API Implementation
class RealWhatsAppCloudAPI:
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def validate_credentials(self) -> Dict[str, Any]:
        """Validate WhatsApp credentials by testing API access"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": "Credentials valid",
                    "phone_number_id": self.phone_number_id,
                    "business_profile": data
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid access token",
                    "code": "INVALID_TOKEN"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Phone number ID not found",
                    "code": "INVALID_PHONE_ID"
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": error_data.get("error", {}).get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"WhatsApp credential validation failed: {e}")
            return {"success": False, "error": f"Validation failed: {str(e)}"}
    
    async def send_message(self, to: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Send WhatsApp message"""
        try:
            # Clean phone number (remove + and spaces)
            to_clean = to.replace("+", "").replace(" ", "").replace("-", "")
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_clean,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": "Message sent successfully",
                    "message_id": result.get("messages", [{}])[0].get("id", ""),
                    "to": to_clean,
                    "content": message,
                    "whatsapp_response": result
                }
            else:
                error_data = response.json() if response.content else {}
                logger.error(f"WhatsApp message failed: {response.status_code} - {error_data}")
                return {
                    "success": False,
                    "error": f"Message failed: {response.status_code}",
                    "details": error_data.get("error", {}).get("message", "Unknown error"),
                    "to": to_clean
                }
                
        except Exception as e:
            logger.error(f"WhatsApp message error: {e}")
            return {"success": False, "error": f"Send failed: {str(e)}", "to": to}
    
    async def send_broadcast(self, recipient_list: List[str], message: str) -> Dict[str, Any]:
        """Send broadcast message to multiple recipients"""
        try:
            results = []
            successful = 0
            failed = 0
            
            for recipient in recipient_list:
                result = await self.send_message(recipient, message)
                results.append({
                    "recipient": recipient,
                    "success": result.get("success", False),
                    "message_id": result.get("message_id", ""),
                    "error": result.get("error", "") if not result.get("success") else None
                })
                
                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
                
                # Add delay between messages to avoid rate limiting
                await asyncio.sleep(1.0)
            
            return {
                "success": True,
                "message": "Broadcast completed",
                "broadcast_results": {
                    "total_recipients": len(recipient_list),
                    "successful": successful,
                    "failed": failed,
                    "results": results
                }
            }
            
        except Exception as e:
            logger.error(f"WhatsApp broadcast error: {e}")
            return {"success": False, "error": f"Broadcast failed: {str(e)}"}

# Real WhatsApp Automation Scheduler
class RealWhatsAppAutomationScheduler:
    def __init__(self, ai_service, database_manager):
        self.ai_service = ai_service
        self.database_manager = database_manager
        self.user_configs = {}
        self.whatsapp_apis = {}
        
    async def setup_whatsapp_automation(self, user_id: str, phone_number_id: str, access_token: str, config) -> Dict[str, Any]:
        """Setup real WhatsApp automation for user"""
        try:
            # Create real WhatsApp API instance
            whatsapp_api = RealWhatsAppCloudAPI(access_token, phone_number_id)
            
            # Validate credentials first
            validation_result = await whatsapp_api.validate_credentials()
            if not validation_result.get("success"):
                logger.error(f"WhatsApp validation failed for user {user_id}: {validation_result}")
                return {
                    "success": False,
                    "error": "WhatsApp credential validation failed",
                    "details": validation_result.get("error"),
                    "code": validation_result.get("code")
                }
            
            # Store API instance and config
            self.whatsapp_apis[user_id] = whatsapp_api
            self.user_configs[user_id] = {
                "phone_number_id": phone_number_id,
                "access_token": access_token,
                "config": config.__dict__ if hasattr(config, '__dict__') else config,
                "enabled": True,
                "setup_time": datetime.now().isoformat()
            }
            
            logger.info(f"Real WhatsApp automation setup successful for user {user_id}")
            
            return {
                "success": True,
                "message": "WhatsApp automation enabled successfully (Production Mode)!",
                "config": {
                    "business_name": getattr(config, 'business_name', 'WhatsApp Business'),
                    "phone_number_id": phone_number_id,
                    "auto_reply_enabled": getattr(config, 'auto_reply_enabled', True),
                    "campaign_enabled": getattr(config, 'campaign_enabled', True),
                    "business_hours": getattr(config, 'business_hours', {"start": "09:00", "end": "18:00"})
                },
                "business_profile": validation_result.get("business_profile", {}),
                "scheduler_status": "Active",
                "mode": "Production"
            }
            
        except Exception as e:
            logger.error(f"Real WhatsApp automation setup failed for user {user_id}: {e}")
            return {
                "success": False, 
                "error": f"Setup failed: {str(e)}",
                "suggestion": "Check WhatsApp Business API configuration"
            }
    
    async def send_message(self, user_id: str, to: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Send message using real WhatsApp API"""
        try:
            if user_id not in self.whatsapp_apis:
                return {"success": False, "error": "WhatsApp not configured for user"}
            
            whatsapp_api = self.whatsapp_apis[user_id]
            result = await whatsapp_api.send_message(to, message, message_type)
            
            # Update stats
            if user_id in self.user_configs:
                config = self.user_configs[user_id]
                config["last_message_time"] = datetime.now().isoformat()
                config["total_messages"] = config.get("total_messages", 0) + 1
                if result.get("success"):
                    config["successful_messages"] = config.get("successful_messages", 0) + 1
                else:
                    config["failed_messages"] = config.get("failed_messages", 0) + 1
            
            return result
            
        except Exception as e:
            logger.error(f"Real WhatsApp message error for user {user_id}: {e}")
            return {"success": False, "error": f"Message failed: {str(e)}"}
    
    async def send_broadcast(self, user_id: str, recipient_list: List[str], message: str, media_url: str = None, media_type: str = None) -> Dict[str, Any]:
        """Send broadcast using real WhatsApp API"""
        try:
            if user_id not in self.whatsapp_apis:
                return {"success": False, "error": "WhatsApp not configured for user"}
            
            whatsapp_api = self.whatsapp_apis[user_id]
            result = await whatsapp_api.send_broadcast(recipient_list, message)
            
            # Update stats
            if user_id in self.user_configs and result.get("success"):
                config = self.user_configs[user_id]
                broadcast_results = result.get("broadcast_results", {})
                config["last_broadcast_time"] = datetime.now().isoformat()
                config["total_broadcasts"] = config.get("total_broadcasts", 0) + 1
                config["total_broadcast_messages"] = config.get("total_broadcast_messages", 0) + broadcast_results.get("total_recipients", 0)
            
            return result
            
        except Exception as e:
            logger.error(f"Real WhatsApp broadcast error for user {user_id}: {e}")
            return {"success": False, "error": f"Broadcast failed: {str(e)}"}
    
    async def get_automation_status(self, user_id: str) -> Dict[str, Any]:
        """Get real automation status"""
        config = self.user_configs.get(user_id, {})
        return {
            "whatsapp_automation": {
                "enabled": config.get("enabled", False),
                "mode": "Production",
                "config": config.get("config", {}),
                "stats": {
                    "total_messages": config.get("total_messages", 0),
                    "successful_messages": config.get("successful_messages", 0),
                    "failed_messages": config.get("failed_messages", 0),
                    "total_broadcasts": config.get("total_broadcasts", 0),
                    "last_activity": config.get("last_message_time") or config.get("last_broadcast_time")
                }
            }
        }

# Real WhatsApp Config
class RealWhatsAppConfig:
    def __init__(self, user_id: str, business_name: str, phone_number_id: str, access_token: str, **kwargs):
        self.user_id = user_id
        self.business_name = business_name
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.auto_reply_enabled = kwargs.get('auto_reply_enabled', True)
        self.campaign_enabled = kwargs.get('campaign_enabled', True)
        self.business_hours = kwargs.get('business_hours', {"start": "09:00", "end": "18:00"})
        self.timezone = kwargs.get('timezone', "Asia/Kolkata")

# Real WhatsApp Webhook Handler
class RealWhatsAppWebhookHandler:
    def __init__(self, verify_token: str, app_secret: str):
        self.verify_token = verify_token
        self.app_secret = app_secret
    
    def verify_webhook(self, mode: str, token: str, challenge: str):
        """Verify webhook subscription"""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook verified successfully")
            return challenge
        logger.warning("Webhook verification failed")
        return None
    
    def verify_signature(self, body: bytes, signature: str):
        """Verify webhook signature"""
        try:
            expected_signature = hmac.new(
                self.app_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            received_signature = signature.replace("sha256=", "")
            return hmac.compare_digest(expected_signature, received_signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def parse_webhook_event(self, webhook_data: dict) -> List[Dict[str, Any]]:
        """Parse incoming webhook events"""
        events = []
        try:
            entry = webhook_data.get("entry", [])
            for entry_item in entry:
                changes = entry_item.get("changes", [])
                for change in changes:
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        messages = value.get("messages", [])
                        for message in messages:
                            events.append({
                                "type": "message",
                                "phone_number_id": value.get("metadata", {}).get("phone_number_id"),
                                "from": message.get("from"),
                                "message_id": message.get("id"),
                                "timestamp": message.get("timestamp"),
                                "text": message.get("text", {}).get("body", ""),
                                "message_type": message.get("type", "text")
                            })
        except Exception as e:
            logger.error(f"Webhook parsing failed: {e}")
        
        return events
    

# Mock Classes for Fallback
class MockWhatsAppWebhookHandler:
    def __init__(self, verify_token: str, app_secret: str):
        self.verify_token = verify_token
        self.app_secret = app_secret
    
    def verify_webhook(self, mode: str, token: str, challenge: str):
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def verify_signature(self, body: bytes, signature: str):
        return True
    
    def parse_webhook_event(self, webhook_data: dict):
        return []

class MockWhatsAppAutomationScheduler:
    def __init__(self, ai_service, database_manager):
        self.ai_service = ai_service
        self.database_manager = database_manager
        self.user_configs = {}
        
    async def setup_whatsapp_automation(self, user_id: str, phone_number_id: str, access_token: str, config):
        self.user_configs[user_id] = {
            "phone_number_id": phone_number_id,
            "access_token": access_token,
            "config": config.__dict__ if hasattr(config, '__dict__') else config,
            "enabled": True,
            "setup_time": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "WhatsApp automation setup successful (Mock Mode)!",
            "config": {
                "business_name": getattr(config, 'business_name', 'Test Business'),
                "phone_number_id": phone_number_id,
                "auto_reply_enabled": getattr(config, 'auto_reply_enabled', True),
                "campaign_enabled": getattr(config, 'campaign_enabled', True),
                "business_hours": getattr(config, 'business_hours', {"start": "09:00", "end": "18:00"})
            },
            "business_profile": {"verified_name": "Test Business", "display_phone_number": "+1234567890"},
            "scheduler_status": "Active",
            "mode": "Mock"
        }
    
    async def send_message(self, user_id: str, to: str, message: str, message_type: str = "text"):
        if user_id not in self.user_configs:
            return {"success": False, "error": "WhatsApp not configured for user"}
        
        return {
            "success": True,
            "message": "Message sent successfully (Mock Mode)",
            "message_id": f"mock_msg_{uuid.uuid4().hex[:8]}",
            "to": to,
            "content": message,
            "mode": "mock"
        }
    
    async def send_broadcast(self, user_id: str, recipient_list: List[str], message: str, media_url: str = None, media_type: str = None):
        if user_id not in self.user_configs:
            return {"success": False, "error": "WhatsApp not configured for user"}
        
        return {
            "success": True,
            "message": "Broadcast sent successfully (Mock Mode)",
            "broadcast_results": {
                "total_recipients": len(recipient_list),
                "successful": len(recipient_list),
                "failed": 0,
                "results": [{"recipient": r, "success": True, "message_id": f"msg_{i}"} for i, r in enumerate(recipient_list)]
            },
            "mode": "mock"
        }
    
    async def get_automation_status(self, user_id: str):
        config = self.user_configs.get(user_id, {})
        return {
            "whatsapp_automation": {
                "enabled": config.get("enabled", False),
                "mode": "Mock",
                "config": config.get("config", {}),
                "stats": {
                    "total_messages": 5,
                    "successful_messages": 5,
                    "failed_messages": 0,
                    "last_activity": datetime.now().isoformat()
                }
            }
        }

class MockAIService:
    async def generate_social_content(self, **kwargs):
        return {
            "success": False,
            "error": "Mock AI Service - Configure MISTRAL_API_KEY or GROQ_API_KEY",
            "content": "Sample content for testing. Please configure AI service.",
            "ai_service": "mock"
        }
    
    async def test_ai_services(self):
        return {"success": False, "error": "Mock AI", "primary_service": "mock"}

class MockDatabaseManager:
    def __init__(self):
        self.users = {}
        self.tokens = {}
        
    async def connect(self):
        return True
    
    async def disconnect(self):
        return True
    
    async def register_user(self, email: str, password: str, name: str):
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        token = jwt.encode({
            "user_id": user_id,
            "email": email,
            "name": name,
            "exp": datetime.utcnow() + timedelta(days=30)
        }, "secret", algorithm="HS256")
        
        self.users[user_id] = {"id": user_id, "email": email, "name": name}
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "name": name,
            "token": token
        }
    
    async def login_user(self, email: str, password: str):
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        name = email.split('@')[0].title()
        token = jwt.encode({
            "user_id": user_id,
            "email": email,
            "name": name,
            "exp": datetime.utcnow() + timedelta(days=30)
        }, "secret", algorithm="HS256")
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "name": name,
            "token": token
        }
    
    async def get_user_by_token(self, token: str):
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            return {
                "id": payload["user_id"],
                "email": payload["email"],
                "name": payload["name"]
            }
        except:
            return None

    async def store_platform_tokens(self, user_id: str, platform: str, token_data: Dict[str, Any]):
        return {"success": True, "message": f"{platform} tokens stored for {user_id}"}

    async def store_automation_config(self, user_id: str, platform: str, config_data: Dict[str, Any]):
        return {"success": True, "message": f"{platform} automation configured for {user_id}"}

# Facebook OAuth Connector
class FacebookOAuthConnector:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.is_configured = bool(app_id and app_secret)
        
    def generate_oauth_url(self, state: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'pages_manage_posts,pages_read_engagement,public_profile,email',
            'response_type': 'code'
        }
        
        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return {"success": True, "authorization_url": auth_url, "state": state}
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        try:
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': code
            }
            
            response = requests.post(token_url, data=params, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                
                # Get user info
                user_response = requests.get(
                    f"https://graph.facebook.com/v18.0/me?fields=id,name,email&access_token={access_token}",
                    timeout=15
                )
                user_info = user_response.json() if user_response.status_code == 200 else {}
                
                # Get pages
                pages_response = requests.get(
                    f"https://graph.facebook.com/v18.0/me/accounts?fields=id,name,access_token&access_token={access_token}",
                    timeout=15
                )
                pages = pages_response.json().get('data', []) if pages_response.status_code == 200 else []
                
                return {
                    "success": True,
                    "access_token": access_token,
                    "expires_in": token_data.get('expires_in', 3600),
                    "user_info": user_info,
                    "pages": pages
                }
            else:
                return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"OAuth error: {str(e)}"}
    
    async def post_content(self, access_token: str, page_id: str, title: str, content: str, image_url: str = "") -> Dict[str, Any]:
        try:
            post_data = {
                'message': f"{title}\n\n{content}",
                'access_token': access_token
            }
            
            if image_url:
                post_data['link'] = image_url
            
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            response = requests.post(url, data=post_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "post_id": result.get('id', ''),
                    "post_url": f"https://facebook.com/{result.get('id', '')}",
                    "message": "Posted to Facebook successfully"
                }
            else:
                return {"success": False, "error": f"Facebook API error: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Posting failed: {str(e)}"}

# Instagram OAuth Connector
class InstagramOAuthConnector:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.is_configured = bool(app_id and app_secret)
        
    def generate_oauth_url(self, state: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {"success": False, "error": "Instagram credentials not configured"}
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user_profile,user_media',
            'response_type': 'code',
            'state': state
        }
        
        auth_url = f"https://api.instagram.com/oauth/authorize?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return {"success": True, "authorization_url": auth_url, "state": state}
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        try:
            # Get short-lived token
            token_url = "https://api.instagram.com/oauth/access_token"
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code
            }
            
            response = requests.post(token_url, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                short_token = token_data.get('access_token')
                
                # Exchange for long-lived token
                long_token_url = "https://graph.instagram.com/access_token"
                long_params = {
                    'grant_type': 'ig_exchange_token',
                    'client_secret': self.app_secret,
                    'access_token': short_token
                }
                
                long_response = requests.get(long_token_url, params=long_params, timeout=30)
                
                if long_response.status_code == 200:
                    long_data = long_response.json()
                    access_token = long_data.get('access_token')
                    
                    # Get user info
                    user_response = requests.get(
                        f"https://graph.instagram.com/me?fields=id,username,account_type&access_token={access_token}",
                        timeout=15
                    )
                    user_info = user_response.json() if user_response.status_code == 200 else {}
                    
                    return {
                        "success": True,
                        "access_token": access_token,
                        "expires_in": long_data.get('expires_in', 5184000),
                        "user_info": user_info
                    }
                else:
                    return {"success": False, "error": f"Long-lived token failed: {long_response.text}"}
            else:
                return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"OAuth error: {str(e)}"}

    async def post_content(self, access_token: str, user_id: str, caption: str, image_url: str) -> Dict[str, Any]:
        try:
            # Create media object
            create_url = f"https://graph.instagram.com/v18.0/{user_id}/media"
            create_data = {
                'image_url': image_url,
                'caption': caption,
                'access_token': access_token
            }
            
            create_response = requests.post(create_url, data=create_data, timeout=30)
            
            if create_response.status_code == 200:
                media_id = create_response.json().get('id')
                
                # Publish media
                publish_url = f"https://graph.instagram.com/v18.0/{user_id}/media_publish"
                publish_data = {
                    'creation_id': media_id,
                    'access_token': access_token
                }
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=30)
                
                if publish_response.status_code == 200:
                    result = publish_response.json()
                    return {
                        "success": True,
                        "post_id": result.get('id', ''),
                        "message": "Posted to Instagram successfully"
                    }
                else:
                    return {"success": False, "error": f"Instagram publish failed: {publish_response.text}"}
            else:
                return {"success": False, "error": f"Instagram media creation failed: {create_response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Instagram posting failed: {str(e)}"}

# Global Variables
database_manager = None
ai_service = None
facebook_connector = None
instagram_connector = None
whatsapp_handler = None
whatsapp_scheduler = None

# Authentication
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        logger.info(f"Authenticating token: {token[:20]}...")
        
        user = await database_manager.get_user_by_token(token)
        if not user:
            logger.warning("Token validation failed")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        logger.info(f"User authenticated: {user.get('email')}")
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Application Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global database_manager, ai_service, facebook_connector, instagram_connector, whatsapp_handler, whatsapp_scheduler
    
    logger.info("Starting Complete Social Media Automation System with REAL WhatsApp API...")
    
    # Initialize Database
    try:
        if DB_AVAILABLE:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            database_manager = MultiUserSocialDatabase(mongodb_uri)
            await database_manager.connect()
            logger.info("Real database connected")
        else:
            database_manager = MockDatabaseManager()
            await database_manager.connect()
            logger.info("Mock database connected")
    except Exception as e:
        logger.error(f"Database failed: {e}")
        database_manager = MockDatabaseManager()
        await database_manager.connect()
    
    # Initialize AI Service
    try:
        if AI_AVAILABLE:
            ai_service = EnhancedAIService()
            test_result = await ai_service.test_ai_services()
            if test_result.get("success"):
                logger.info(f"Real AI service ready: {test_result.get('primary_service')}")
            else:
                ai_service = MockAIService()
                logger.warning("AI service test failed, using mock")
        else:
            ai_service = MockAIService()
            logger.info("AI service not available, using mock")
    except Exception as e:
        logger.error(f"AI service failed: {e}")
        ai_service = MockAIService()
    
    # Initialize Facebook Connector
    facebook_connector = FacebookOAuthConnector(
        app_id=os.getenv('FB_APP_ID', '788457114351565'),
        app_secret=os.getenv('FB_APP_SECRET', '3a6fba32779a94c001b274ab91c026ee'),
        redirect_uri=os.getenv('FB_REDIRECT_URI', 'https://velocityfly.onrender.com/api/oauth/facebook/callback')
    )
    
    # Initialize Instagram Connector
    instagram_connector = InstagramOAuthConnector(
        app_id=os.getenv('INSTAGRAM_APP_ID', '2247747609000742'),
        app_secret=os.getenv('INSTAGRAM_APP_SECRET', '55d50918f00e10f38a64c5e7b8dabdc8'),
        redirect_uri=os.getenv('INSTAGRAM_REDIRECT_URI', 'https://velocityfly.onrender.com/api/oauth/instagram/callback')
    )
    
    # Initialize WhatsApp Handler with Fallback Logic
    logger.info("Initializing WhatsApp services...")
    
    if WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID:
        try:
            # Test credentials first
            test_api = RealWhatsAppCloudAPI(WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID)
            test_result = await test_api.validate_credentials()
            
            if test_result.get("success"):
                # Use real WhatsApp services
                whatsapp_handler = RealWhatsAppWebhookHandler(
                    verify_token=WEBHOOK_VERIFY_TOKEN,
                    app_secret=META_APP_SECRET
                )
                whatsapp_scheduler = RealWhatsAppAutomationScheduler(ai_service, database_manager)
                logger.info("REAL WhatsApp services initialized successfully")
                logger.info(f"WhatsApp Business Profile: {test_result.get('business_profile', {})}")
            else:
                logger.error(f"WhatsApp credentials invalid: {test_result}")
                # Fallback to mock instead of None
                whatsapp_handler = MockWhatsAppWebhookHandler(WEBHOOK_VERIFY_TOKEN, META_APP_SECRET)
                whatsapp_scheduler = MockWhatsAppAutomationScheduler(ai_service, database_manager)
                logger.warning("Using Mock WhatsApp services as fallback")
        except Exception as e:
            logger.error(f"Real WhatsApp initialization failed: {e}")
            # Fallback to mock instead of None
            whatsapp_handler = MockWhatsAppWebhookHandler(WEBHOOK_VERIFY_TOKEN, META_APP_SECRET)
            whatsapp_scheduler = MockWhatsAppAutomationScheduler(ai_service, database_manager)
            logger.warning("Using Mock WhatsApp services as fallback")
    else:
        logger.warning("WhatsApp credentials missing - using mock services")
        # Use mock instead of None
        whatsapp_handler = MockWhatsAppWebhookHandler(WEBHOOK_VERIFY_TOKEN, META_APP_SECRET)
        whatsapp_scheduler = MockWhatsAppAutomationScheduler(ai_service, database_manager)
    
    logger.info("Application startup completed successfully")
    yield
    
    # Cleanup
    if database_manager:
        await database_manager.disconnect()


# Create FastAPI App
app = FastAPI(
    title="Complete Social Media Automation API - REAL WhatsApp",
    description="WhatsApp, Facebook & Instagram automation with REAL WhatsApp API integration",
    version="3.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://velocityfly-ai.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

















# Basic Routes
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Complete Social Media Automation API - REAL WhatsApp Integration",
        "platforms": ["whatsapp", "facebook", "instagram"],
        "features": ["real_whatsapp_api", "oauth", "automation", "ai_content", "webhooks", "campaigns"],
        "version": "3.0.0",
        "whatsapp_mode": "Production" if isinstance(whatsapp_scheduler, RealWhatsAppAutomationScheduler) else "Mock",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "services": {
            "database": database_manager is not None,
            "ai": ai_service is not None and not isinstance(ai_service, MockAIService),
            "facebook": facebook_connector is not None and facebook_connector.is_configured,
            "instagram": instagram_connector is not None and instagram_connector.is_configured,
            "whatsapp": whatsapp_handler is not None,
            "whatsapp_mode": "Real API" if isinstance(whatsapp_scheduler, RealWhatsAppAutomationScheduler) else "Mock"
        },
        "timestamp": datetime.now().isoformat()
    }

# Authentication Routes
@app.post("/api/auth/register")
async def register_user(user_data: RegisterRequest):
    try:
        result = await database_manager.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login_user(login_data: LoginRequest):
    try:
        result = await database_manager.login_user(
            email=login_data.email,
            password=login_data.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}

# WhatsApp Routes
@app.get("/api/debug/whatsapp")
async def debug_whatsapp():
    return {
        "whatsapp_available": whatsapp_scheduler is not None,
        "whatsapp_mode": "Real API" if isinstance(whatsapp_scheduler, RealWhatsAppAutomationScheduler) else "Mock",
        "models_available": "WhatsAppSetupRequest" in globals(),
        "scheduler_exists": whatsapp_scheduler is not None,
        "token_present": bool(WHATSAPP_ACCESS_TOKEN),
        "phone_id_present": bool(WHATSAPP_PHONE_NUMBER_ID),
        "token_prefix": WHATSAPP_ACCESS_TOKEN[:10] if WHATSAPP_ACCESS_TOKEN else None,
        "using_mock": isinstance(whatsapp_scheduler, MockWhatsAppAutomationScheduler),
        "credentials_hardcoded": True,
        "api_version": "v18.0"
    }

@app.post("/api/whatsapp/setup")
async def setup_whatsapp(
    setup_data: WhatsAppSetupRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        user_name = current_user.get("name", "User")
        
        if not whatsapp_scheduler:
            return {
                "success": False,
                "error": "WhatsApp service not available",
                "suggestion": "Service is starting up, please try again"
            }
        
        logger.info(f"WhatsApp setup initiated for user {user_id}")
        logger.info(f"Using credentials - Phone ID: {setup_data.phone_number_id}")
        logger.info(f"Using credentials - Token prefix: {setup_data.access_token[:20]}...")
        
        # Validate required fields
        if not setup_data.phone_number_id or not setup_data.access_token:
            logger.error("Missing required fields: phone_number_id or access_token")
            return {
                "success": False, 
                "error": "Phone number ID and access token are required"
            }
        
        # Validate token format
        if len(setup_data.access_token) < 50:
            logger.error("Invalid token format - too short")
            return {
                "success": False,
                "error": "Invalid access token format"
            }

        # Create business name with fallback
        business_name = setup_data.business_name or f"{user_name}'s Business"
        
        # Use appropriate WhatsApp configuration based on scheduler type
        if isinstance(whatsapp_scheduler, RealWhatsAppAutomationScheduler):
            config = RealWhatsAppConfig(
                user_id=user_id,
                business_name=business_name,
                phone_number_id=setup_data.phone_number_id,
                access_token=setup_data.access_token,
                auto_reply_enabled=setup_data.auto_reply_enabled,
                campaign_enabled=setup_data.campaign_enabled,
                business_hours=setup_data.business_hours,
                timezone=setup_data.timezone
            )
        else:
            # Mock configuration
            config = type('MockConfig', (), {
                'user_id': user_id,
                'business_name': business_name,
                'phone_number_id': setup_data.phone_number_id,
                'access_token': setup_data.access_token,
                'auto_reply_enabled': setup_data.auto_reply_enabled,
                'campaign_enabled': setup_data.campaign_enabled,
                'business_hours': setup_data.business_hours,
                'timezone': setup_data.timezone
            })()
        
        logger.info(f"WhatsApp config created for user {user_id}")

        # Setup automation
        result = await whatsapp_scheduler.setup_whatsapp_automation(
            user_id=user_id,
            phone_number_id=setup_data.phone_number_id,
            access_token=setup_data.access_token,
            config=config
        )
        
        logger.info(f"WhatsApp setup result: {result}")

        if result.get("success"):
            # Store user's WhatsApp tokens
            try:
                if hasattr(database_manager, 'store_platform_tokens'):
                    await database_manager.store_platform_tokens(
                        user_id=user_id,
                        platform="whatsapp",
                        token_data={
                            "access_token": setup_data.access_token,
                            "phone_number_id": setup_data.phone_number_id,
                            "business_name": business_name,
                            "user_id": user_id,
                            "setup_date": datetime.now().isoformat(),
                            "mode": "production" if isinstance(whatsapp_scheduler, RealWhatsAppAutomationScheduler) else "mock"
                        }
                    )
                    logger.info(f"Database storage successful for user {user_id}")
            except Exception as db_error:
                logger.warning(f"Database storage failed but continuing: {db_error}")

            # Store in memory for quick access
            user_whatsapp_tokens[user_id] = {
                "phone_number_id": setup_data.phone_number_id,
                "access_token": setup_data.access_token,
                "business_name": business_name,
                "setup_date": datetime.now().isoformat(),
                "mode": "production" if isinstance(whatsapp_scheduler, RealWhatsAppAutomationScheduler) else "mock"
            }
            logger.info(f"Memory storage successful for user {user_id}")

            logger.info(f"WhatsApp setup completed successfully for user {user_id}")
            return result
        else:
            logger.error(f"WhatsApp setup failed for user {user_id}: {result}")
            return result

    except Exception as e:
        user_id_for_log = locals().get('user_id', 'unknown')
        logger.error(f"WhatsApp setup exception for user {user_id_for_log}: {str(e)}")
        
        return {
            "success": False,
            "error": f"Setup failed: {str(e)}",
            "suggestion": "Check your WhatsApp Business API credentials"
        }

@app.post("/api/whatsapp/send-message")
async def send_whatsapp_message(message_data: WhatsAppMessageRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if not whatsapp_scheduler:
            return {"success": False, "error": "WhatsApp service not available"}
        
        logger.info(f"Sending WhatsApp message from user {user_id} to {message_data.to}")
        
        result = await whatsapp_scheduler.send_message(
            user_id=user_id,
            to=message_data.to,
            message=message_data.message,
            message_type=message_data.message_type
        )
        
        logger.info(f"WhatsApp message result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"WhatsApp message error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/whatsapp/broadcast")
async def send_whatsapp_broadcast(broadcast_data: WhatsAppBroadcastRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if not whatsapp_scheduler:
            return {"success": False, "error": "WhatsApp service not available"}
        
        logger.info(f"Sending WhatsApp broadcast from user {user_id} to {len(broadcast_data.recipient_list)} recipients")
        
        result = await whatsapp_scheduler.send_broadcast(
            user_id=user_id,
            recipient_list=broadcast_data.recipient_list,
            message=broadcast_data.message,
            media_url=broadcast_data.media_url if broadcast_data.media_url else None,
            media_type=broadcast_data.media_type if broadcast_data.media_type else None
        )
        
        logger.info(f"WhatsApp broadcast result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"WhatsApp broadcast error: {e}")
        return {"success": False, "error": str(e)}

# Connection Status Routes
@app.get("/api/{platform}/connection-status")
async def get_connection_status(platform: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if platform == "facebook":
            tokens = user_facebook_tokens.get(user_id)
            if tokens:
                return {
                    "success": True,
                    "connected": True,
                    "username": tokens.get("facebook_username"),
                    "pages": tokens.get("pages", [])
                }
        elif platform == "instagram":
            tokens = user_instagram_tokens.get(user_id)
            if tokens:
                return {
                    "success": True,
                    "connected": True,
                    "username": tokens.get("instagram_username")
                }
        elif platform == "whatsapp":
            tokens = user_whatsapp_tokens.get(user_id)
            if tokens:
                return {
                    "success": True,
                    "connected": True,
                    "phone_number": tokens.get("phone_number_id"),
                    "business_name": tokens.get("business_name", "WhatsApp Business"),
                    "mode": tokens.get("mode", "production")
                }
        
        return {"success": True, "connected": False}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Status Routes
@app.get("/api/automation/status")
async def get_automation_status(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        # Check if user has WhatsApp tokens
        whatsapp_active = False
        whatsapp_stats = {}
        
        if user_id in user_whatsapp_tokens and whatsapp_scheduler:
            whatsapp_active = True
            # Get stats from scheduler
            status_result = await whatsapp_scheduler.get_automation_status(user_id)
            whatsapp_stats = status_result.get("whatsapp_automation", {}).get("stats", {})
        
        return {
            "success": True,
            "automations": {
                "whatsapp": {
                    "status": "active" if whatsapp_active else "inactive",
                    "last_run": whatsapp_stats.get("last_activity"),
                    "messages_sent": whatsapp_stats.get("total_messages", 0),
                    "successful_messages": whatsapp_stats.get("successful_messages", 0),
                    "failed_messages": whatsapp_stats.get("failed_messages", 0),
                    "enabled": whatsapp_active,
                    "mode": "Production" if isinstance(whatsapp_scheduler, RealWhatsAppAutomationScheduler) else "Mock"
                },
                "facebook": {
                    "status": "inactive",
                    "last_run": None,
                    "enabled": False
                },
                "instagram": {
                    "status": "inactive", 
                    "last_run": None,
                    "enabled": False
                }
            },
            "total_active": 1 if whatsapp_active else 0,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Automation status error: {e}")
        return {
            "success": False,
            "error": "Failed to fetch automation status",
            "automations": {}
        }
    
# OAuth Routes
@app.get("/api/oauth/{platform}/authorize")
async def oauth_authorize(platform: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        state = f"{platform}_{user_id}_{uuid.uuid4().hex[:12]}"
        oauth_states[state] = user_id
        
        if platform == "facebook":
            result = facebook_connector.generate_oauth_url(state)
        elif platform == "instagram":
            result = instagram_connector.generate_oauth_url(state)
        else:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        if result["success"]:
            return {"success": True, "redirect_url": result["authorization_url"], "state": state}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/oauth/{platform}/callback")
async def oauth_callback(platform: str, code: str, state: str):
    try:
        user_id = oauth_states.get(state)
        if not user_id:
            return RedirectResponse(
                url="https://velocityfly-ai.onrender.com/?error=invalid_state",
                status_code=302
            )
        
        if platform == "facebook":
            result = await facebook_connector.exchange_code_for_token(code)
            if result["success"]:
                user_facebook_tokens[user_id] = {
                    "access_token": result["access_token"],
                    "facebook_username": result["user_info"].get("name", "Unknown"),
                    "pages": result.get("pages", [])
                }
                
                # Store in database if available
                if hasattr(database_manager, 'store_platform_tokens'):
                    await database_manager.store_platform_tokens(
                        user_id=user_id,
                        platform="facebook",
                        token_data={
                            "access_token": result["access_token"],
                            "expires_in": result.get("expires_in", 3600),
                            "username": result["user_info"].get("name", "Unknown"),
                            "user_id": result["user_info"].get("id", ""),
                            "pages": result.get("pages", [])
                        }
                    )
                    
        elif platform == "instagram":
            result = await instagram_connector.exchange_code_for_token(code)
            if result["success"]:
                user_instagram_tokens[user_id] = {
                    "access_token": result["access_token"],
                    "instagram_username": result["user_info"].get("username", "Unknown"),
                    "instagram_user_id": result["user_info"].get("id", "")
                }
                
                # Store in database if available
                if hasattr(database_manager, 'store_platform_tokens'):
                    await database_manager.store_platform_tokens(
                        user_id=user_id,
                        platform="instagram",
                        token_data={
                            "access_token": result["access_token"],
                            "expires_in": result.get("expires_in", 5184000),
                            "username": result["user_info"].get("username", "Unknown"),
                            "user_id": result["user_info"].get("id", "")
                        }
                    )
        
        oauth_states.pop(state, None)
        
        if result["success"]:
            username = result["user_info"].get("name" if platform == "facebook" else "username", "User")
            return RedirectResponse(
                url=f"https://velocityfly-ai.onrender.com/?{platform}_connected=true&username={username}",
                status_code=302
            )
        else:
            return RedirectResponse(
                url=f"https://velocityfly-ai.onrender.com/?error={platform}_auth_failed",
                status_code=302
            )
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return RedirectResponse(
            url="https://velocityfly-ai.onrender.com/?error=oauth_failed",
            status_code=302
        )

# Manual Posting Routes
@app.post("/api/post/manual")
async def manual_post(post_data: ManualPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        platform = post_data.platform
        
        if platform == "facebook":
            tokens = user_facebook_tokens.get(user_id)
            if not tokens:
                return {"success": False, "error": "Facebook not connected"}
            
            page_id = post_data.page_id or (tokens.get("pages", [{}])[0].get("id", "") if tokens.get("pages") else "")
            page_token = next(
                (p.get("access_token") for p in tokens.get("pages", []) if p.get("id") == page_id),
                tokens.get("access_token")
            )
            
            result = await facebook_connector.post_content(
                access_token=page_token,
                page_id=page_id,
                title=post_data.title,
                content=post_data.content,
                image_url=post_data.image_url
            )
            
        elif platform == "instagram":
            tokens = user_instagram_tokens.get(user_id)
            if not tokens:
                return {"success": False, "error": "Instagram not connected"}
            
            if not post_data.image_url:
                return {"success": False, "error": "Instagram posts require an image"}
            
            result = await instagram_connector.post_content(
                access_token=tokens["access_token"],
                user_id=tokens["instagram_user_id"],
                caption=f"{post_data.title}\n\n{post_data.content}",
                image_url=post_data.image_url
            )
        else:
            return {"success": False, "error": "Platform not supported"}
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# Webhook Routes
@app.get("/webhook/{platform}")
async def webhook_verify(platform: str, request: Request):
    """Handle webhook verification for all platforms"""
    try:
        if platform == "whatsapp" and whatsapp_handler:
            mode = request.query_params.get("hub.mode")
            token = request.query_params.get("hub.verify_token")
            challenge = request.query_params.get("hub.challenge")
            
            result = whatsapp_handler.verify_webhook(mode, token, challenge)
            if result:
                return Response(content=result, media_type="text/plain")
        
        return Response(content="Forbidden", status_code=403)
        
    except Exception as e:
        logger.error(f"Webhook verification failed: {e}")
        return Response(content="Error", status_code=500)

@app.post("/webhook/{platform}")
async def webhook_handler(platform: str, request: Request):
    """Handle incoming webhook events for all platforms"""
    try:
        body = await request.body()
        
        if platform == "whatsapp" and whatsapp_handler:
            # Verify signature if configured
            signature = request.headers.get("x-hub-signature-256", "")
            if not whatsapp_handler.verify_signature(body, signature):
                return Response(content="Forbidden", status_code=403)
            
            # Parse webhook data
            webhook_data = json.loads(body.decode())
            events = whatsapp_handler.parse_webhook_event(webhook_data)
            
            # Process each event
            for event in events:
                if event["type"] == "message":
                    # Find user by phone number ID
                    user_id = None
                    for uid, tokens in user_whatsapp_tokens.items():
                        if tokens.get("phone_number_id") == event["phone_number_id"]:
                            user_id = uid
                            break
                    
                    if user_id and hasattr(whatsapp_scheduler, 'handle_incoming_message'):
                        # Handle incoming message
                        await whatsapp_scheduler.handle_incoming_message(user_id, event)
            
            return {"status": "ok"}
        
        return Response(content="Not Found", status_code=404)
        
    except Exception as e:
        logger.error(f"Webhook handling failed: {e}")
        return Response(content="Error", status_code=500)

# AI Content Generation Routes
@app.post("/api/automation/test-auto-post")
async def test_auto_post(test_data: TestPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"AI Service Type: {type(ai_service)}")
        
        if isinstance(ai_service, MockAIService):
            return {
                "success": False,
                "error": "Mock AI service active - configure API keys",
                "message": "Add MISTRAL_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY to .env file"
            }
        
        content_result = await ai_service.generate_social_content(
            platform=test_data.platform,
            domain=test_data.domain,
            business_type=test_data.business_type,
            business_description=test_data.business_description,
            target_audience=test_data.target_audience,
            content_style=test_data.content_style
        )
        
        logger.info(f"AI Result: {content_result}")
        
        if not content_result.get("success", True):
            return {
                "success": False,
                "error": f"AI content generation failed: {content_result.get('error')}"
            }
        
        return {
            "success": True,
            "message": f"Content generated using {content_result.get('ai_service')}!",
            "post_details": {
                "platform": test_data.platform,
                "content": content_result.get("content"),
                "word_count": content_result.get("word_count", 0)
            },
            "content_preview": content_result.get("content"),
            "ai_service": content_result.get("ai_service"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"AI test error: {e}")
        return {"success": False, "error": str(e)}

# Automation Setup Routes
@app.post("/api/automation/setup-auto-posting")
async def setup_auto_posting(config_data: AutoPostingRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        platform = config_data.platform
        
        # Check connections
        if platform == "facebook" and user_id not in user_facebook_tokens:
            return {"success": False, "error": "Facebook account not connected"}
        elif platform == "instagram" and user_id not in user_instagram_tokens:
            return {"success": False, "error": "Instagram account not connected"}
        elif platform == "whatsapp" and user_id not in user_whatsapp_tokens:
            return {"success": False, "error": "WhatsApp account not connected"}
        
        if isinstance(ai_service, MockAIService):
            return {"success": False, "error": "AI service not configured"}
        
        # Test AI service
        test_content = await ai_service.generate_social_content(
            platform=platform,
            domain=config_data.domain,
            business_type=config_data.business_type,
            business_description=config_data.business_description,
            target_audience=config_data.target_audience
        )
        
        if not test_content.get("success", True):
            return {"success": False, "error": "AI service not working properly"}
        
        # Store automation config in database if available
        if hasattr(database_manager, 'store_automation_config'):
            await database_manager.store_automation_config(
                user_id=user_id,
                platform=platform,
                config_data=config_data.dict()
            )
        
        return {
            "success": True,
            "message": f"{platform} auto-posting configured successfully",
            "config": config_data.dict(),
            "ai_service": test_content.get("ai_service", "unknown")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Disconnect Routes
@app.post("/api/{platform}/disconnect")
async def disconnect_platform(platform: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if platform == "facebook" and user_id in user_facebook_tokens:
            del user_facebook_tokens[user_id]
        elif platform == "instagram" and user_id in user_instagram_tokens:
            del user_instagram_tokens[user_id]
        elif platform == "whatsapp" and user_id in user_whatsapp_tokens:
            del user_whatsapp_tokens[user_id]
        
        return {"success": True, "message": f"{platform.title()} disconnected successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Test and Debug Routes
@app.get("/api/ai/test")
async def test_ai_service():
    try:
        if isinstance(ai_service, MockAIService):
            return {
                "success": False,
                "error": "Mock AI service active",
                "solution": "Add API keys to .env file",
                "required_keys": ["MISTRAL_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY"]
            }
        
        test_result = await ai_service.test_ai_services()
        return {
            "success": True,
            "ai_status": test_result,
            "available_services": test_result.get("available_services", [])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(ai_service).__name__
        }

@app.get("/api/debug/tokens")
async def debug_tokens(current_user: dict = Depends(get_current_user)):
    """Debug endpoint to check token status"""
    user_id = current_user["id"]
    return {
        "user_id": user_id,
        "facebook_tokens": bool(user_facebook_tokens.get(user_id)),
        "instagram_tokens": bool(user_instagram_tokens.get(user_id)),
        "whatsapp_tokens": bool(user_whatsapp_tokens.get(user_id)),
        "oauth_states": len(oauth_states),
        "services": {
            "ai_service": type(ai_service).__name__,
            "database": type(database_manager).__name__,
            "whatsapp_scheduler": type(whatsapp_scheduler).__name__ if whatsapp_scheduler else None
        }
    }



@app.get("/api/test-route")
async def test_route():
    return {"message": "Test route works", "timestamp": datetime.now().isoformat()}

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    """Privacy policy page required for Meta app approval"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VelocityAgent Privacy Policy</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
            p { margin-bottom: 16px; }
        </style>
    </head>
    <body>
        <h1>Privacy Policy</h1>
        <p><strong>Last updated:</strong> September 19, 2025</p>
        
        <h2>Information We Collect</h2>
        <p>We collect information you provide when using our social media automation services, including account credentials and content preferences.</p>
        
        <h2>How We Use Information</h2>
        <p>We use information to provide and improve our automation services, generate content, and manage your social media accounts as requested.</p>
        
        <h2>Data Security</h2>
        <p>We implement appropriate security measures to protect your information and use encryption for sensitive data like access tokens.</p>
        
        <h2>Third-Party Services</h2>
        <p>Our service integrates with Facebook, Instagram, and WhatsApp APIs. Please review their privacy policies for information about how they handle data.</p>
        
        <h2>Contact Us</h2>
        <p>Questions about this policy: aryanpatel77462@gmail.com</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Main execution
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    uvicorn.run("mainFBINSTA:app", host="0.0.0.0", port=PORT, reload=False)
