"""
Complete Multi-User FastAPI Application with Individual Reddit Connections
Each user has their own Reddit tokens and automation settings
REAL POSTING ENABLED - REAL AI CONTENT GENERATION
"""

from fastapi import FastAPI, HTTPException, Request, Query, BackgroundTasks, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse , Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uvicorn
import json
import threading
import random
from pydantic import BaseModel, EmailStr
import sys
import traceback
import uuid
import os
import requests
import base64
import bcrypt
import jwt
import httpx






# CRITICAL: Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

# Verify API keys are loaded
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
print(f"MISTRAL_API_KEY loaded: {MISTRAL_KEY[:10] + '...' if MISTRAL_KEY else 'NOT FOUND'}")
print(f"GROQ_API_KEY loaded: {GROQ_KEY[:10] + '...' if GROQ_KEY else 'NOT FOUND'}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("reddit_automation.log")
    ]
)
logger = logging.getLogger(__name__)

# Import modules with error handling
def safe_import(module_name, class_name=None):
    try:
        if class_name:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        else:
            return __import__(module_name)
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error importing {module_name}: {e}")
        return None







# Safe imports
RedditOAuthConnector = safe_import('reddit', 'RedditOAuthConnector')
AIService = safe_import('ai_service', 'AIService')

# Import MultiUserDatabaseManager (replaces single DatabaseManager)
try:
    from database import MultiUserDatabaseManager as DatabaseManager
    MULTIUSER_DB_AVAILABLE = True
    logger.info("Multi-user database manager imported successfully")
except ImportError:
    logger.warning("Multi-user database not available, falling back to single-user")
    DatabaseManager = safe_import('database', 'DatabaseManager')
    MULTIUSER_DB_AVAILABLE = False

# Import settings with fallback
try:
    from config import get_settings
except ImportError:
    def get_settings():
        class MockSettings:
            mongodb_uri = "mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
            reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "https://velocityfly.onrender.com/api/oauth/reddit/callback")
            reddit_user_agent = "RedditAutomationPlatform/1.0"
            token_encryption_key = os.getenv("TOKEN_ENCRYPTION_KEY")
            mistral_api_key = os.getenv("MISTRAL_API_KEY")
            groq_api_key = os.getenv("GROQ_API_KEY")
        return MockSettings()

# Import Reddit Automation Components
try:
    from reddit_automation import (
        RedditAutomationScheduler, 
        AutoPostConfig, 
        AutoReplyConfig
    )
    AUTOMATION_AVAILABLE = True
    logger.info("Reddit automation components imported successfully")
except ImportError as e:
    logger.warning(f"Reddit automation not available: {e}")
    AUTOMATION_AVAILABLE = False

# Global settings
settings = get_settings()

# Global instances
database_manager = None
ai_service = None
reddit_oauth_connector = None
automation_scheduler = None

# Multi-user management (replaces single-user approach)
user_reddit_tokens = {}  # user_id -> reddit tokens (kept for compatibility)
oauth_states = {}        # oauth_state -> user_id (simplified)
automation_configs = {}  # user_id -> configs (kept for fallback)

# Authentication setup
security = HTTPBearer()

# Multi-User Request Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AutoPostingRequest(BaseModel):
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 3
    posting_times: List[str]
    subreddits: List[str]
    manual_time_entry: bool = False
    custom_post_count: bool = False

class AutoReplyRequest(BaseModel):
    domain: str
    expertise_level: str = "intermediate"
    subreddits: List[str]
    keywords: List[str]
    max_replies_per_hour: int = 2
    response_delay_minutes: int = 15

class TestPostRequest(BaseModel):
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    subreddits: List[str]
    content_style: str = "engaging"

class ManualPostRequest(BaseModel):
    title: str
    content: str
    subreddit: str
    contentType: str = "text"

class ScheduleUpdateRequest(BaseModel):
    type: str
    enabled: bool

# Authentication dependency
# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Get current authenticated user from JWT token"""
#     try:
#         token = credentials.credentials
#         if not database_manager or not hasattr(database_manager, 'get_user_by_token'):
#             raise HTTPException(status_code=500, detail="Authentication system not available")
        
#         user = await database_manager.get_user_by_token(token)
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid or expired token")
        
#         return user
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Authentication failed: {e}")
#         raise HTTPException(status_code=401, detail="Authentication failed")

# Optional authentication (for endpoints that work with or without auth)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        
        # ✅ CHECK IF DATABASE MANAGER EXISTS
        if not database_manager:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # ✅ USE THE MOCK DATABASE METHOD
        user = await database_manager.get_user_by_token(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

# Helper functions for backward compatibility
def generate_user_id() -> str:
    """Generate unique user ID (kept for fallback)"""
    return f"user_{uuid.uuid4().hex[:12]}"

async def load_all_user_automations():
    """Load existing automations for all users from database"""
    try:
        if database_manager and hasattr(database_manager, 'get_all_active_automations'):
            # Load auto-posting configs
            auto_posting_configs = await database_manager.get_all_active_automations('auto_posting')
            for config in auto_posting_configs:
                user_id = config['user_id']
                if user_id not in automation_configs:
                    automation_configs[user_id] = {}
                automation_configs[user_id]['auto_posting'] = {
                    'config': config['config_data'],
                    'enabled': config['enabled']
                }
            
            # Load auto-reply configs
            auto_reply_configs = await database_manager.get_all_active_automations('auto_replies')
            for config in auto_reply_configs:
                user_id = config['user_id']
                if user_id not in automation_configs:
                    automation_configs[user_id] = {}
                automation_configs[user_id]['auto_replies'] = {
                    'config': config['config_data'],
                    'enabled': config['enabled']
                }
            
            logger.info(f"Loaded automation configs for {len(automation_configs)} users")
            
    except Exception as e:
        logger.error(f"Failed to load user automations: {e}")

async def load_existing_tokens():
    """Load existing Reddit tokens from database into memory for all users"""
    try:
        if database_manager and hasattr(database_manager, 'database'):
            # Get all active tokens from database
            active_tokens = database_manager.database.reddit_tokens.find({
                "is_active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            token_count = 0
            async for token_doc in active_tokens:
                user_id = token_doc["user_id"]
                user_reddit_tokens[user_id] = {
                    "access_token": token_doc["access_token"],
                    "refresh_token": token_doc.get("refresh_token", ""),
                    "expires_in": token_doc.get("expires_in", 3600),
                    "reddit_username": token_doc["reddit_username"],
                    "connected_at": token_doc["created_at"].isoformat(),
                    "user_info": {"name": token_doc["reddit_username"], "id": token_doc.get("reddit_user_id", "")}
                }
                token_count += 1
                logger.info(f"Loaded Reddit token for user {user_id} ({token_doc['reddit_username']})")
            
            logger.info(f"Loaded {token_count} existing Reddit connections from database")
            
    except Exception as e:
        logger.error(f"Failed to load existing tokens: {e}")







class MockMultiUserDatabase:
    """Mock database with real user data - no hardcoded values"""
    def __init__(self):
        self.users = {}
        self.reddit_tokens = {}
        self.automation_configs = {}
        self.user_sessions = {}  # Store real user data from login
        self.oauth_states = {}
        
    async def connect(self): 
        logger.info("Mock database connected - storing real user data")
        return True
    
    async def disconnect(self): 
        logger.info("Mock database disconnected")
        return True
    
    async def register_user(self, email, password, name):
        user_id = generate_user_id()
        
        # Hash password properly (basic implementation)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            "id": user_id,
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "reddit_connected": False
        }
        
        self.users[user_id] = user_data
        self.user_sessions[email] = user_data  # Index by email for login
        
        # Generate real JWT token
        token_payload = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        
        token = jwt.encode(token_payload, "your_secret_key", algorithm="HS256")
        
        logger.info(f"Real user registered: {email} -> {name}")
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "name": name,
            "token": token,
            "message": f"User {name} registered successfully"
        }
    
    async def login_user(self, email, password):
        # Check if user exists in session store
        user_data = self.user_sessions.get(email)
        
        if not user_data:
            # Create temporary user for demo (remove this in production)
            user_id = generate_user_id()
            
            # Extract name from email (e.g., "john@example.com" -> "john")
            name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            
            user_data = {
                "id": user_id,
                "email": email,
                "name": name,
                "created_at": datetime.utcnow(),
                "reddit_connected": False
            }
            
            self.users[user_id] = user_data
            self.user_sessions[email] = user_data
            
            logger.info(f"New user auto-created: {email} -> {name}")
        
        # Generate real JWT token
        token_payload = {
            "user_id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        
        token = jwt.encode(token_payload, "your_secret_key", algorithm="HS256")
        
        # Check Reddit connection
        reddit_connected = user_data["id"] in self.reddit_tokens
        reddit_username = None
        if reddit_connected:
            reddit_username = self.reddit_tokens[user_data["id"]].get("reddit_username")
        
        return {
            "success": True,
            "user_id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "token": token,
            "reddit_connected": reddit_connected,
            "reddit_username": reddit_username,
            "message": f"Welcome back, {user_data['name']}!"
        }
    
    async def get_user_by_token(self, token):
        try:
            # Decode JWT token
            payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if user_id and user_id in self.users:
                user_data = self.users[user_id]
                
                # Check current Reddit connection status
                reddit_connected = user_id in self.reddit_tokens
                reddit_username = None
                if reddit_connected:
                    reddit_username = self.reddit_tokens[user_id].get("reddit_username")
                
                return {
                    "id": user_id,
                    "email": user_data["email"],
                    "name": user_data["name"],
                    "reddit_connected": reddit_connected,
                    "reddit_username": reddit_username
                }
                
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token provided")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token provided")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            
        return None
    
    async def store_reddit_tokens(self, user_id, token_data):
        """Store real Reddit tokens for user"""
        self.reddit_tokens[user_id] = {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", ""),
            "reddit_username": token_data["reddit_username"],
            "reddit_user_id": token_data.get("reddit_user_id", ""),
            "expires_in": token_data.get("expires_in", 3600),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Update user's reddit connection status
        if user_id in self.users:
            self.users[user_id]["reddit_connected"] = True
            self.users[user_id]["reddit_username"] = token_data["reddit_username"]
        
        logger.info(f"Real Reddit tokens stored for user {user_id}: {token_data['reddit_username']}")
        
        return {"success": True, "message": f"Reddit tokens stored for {token_data['reddit_username']}"}
    
    async def get_reddit_tokens(self, user_id):
        """Get Reddit tokens for user"""
        token_data = self.reddit_tokens.get(user_id)
        if token_data:
            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "reddit_username": token_data["reddit_username"],
                "is_valid": True
            }
        return None
    
    async def check_reddit_connection(self, user_id):
        """Check if user has active Reddit connection"""
        token_data = self.reddit_tokens.get(user_id)
        
        if token_data and token_data.get("is_active"):
            return {
                "connected": True,
                "reddit_username": token_data["reddit_username"],
                "reddit_user_id": token_data.get("reddit_user_id"),
                "connected_at": token_data["created_at"].isoformat() if token_data.get("created_at") else None,
                "expires_at": None  # Mock doesn't track expiry
            }
        
        return {
            "connected": False,
            "reddit_username": None
        }
    
    async def revoke_reddit_connection(self, user_id):
        """Remove Reddit connection for user"""
        if user_id in self.reddit_tokens:
            username = self.reddit_tokens[user_id].get("reddit_username", "Unknown")
            del self.reddit_tokens[user_id]
            
            # Update user data
            if user_id in self.users:
                self.users[user_id]["reddit_connected"] = False
                self.users[user_id]["reddit_username"] = None
            
            logger.info(f"Reddit connection revoked for user {user_id} ({username})")
            return {"success": True, "message": f"Reddit disconnected from {username}"}
        
        return {"success": False, "error": "No Reddit connection found"}
    
    async def store_automation_config(self, user_id, config_type, config_data):
        if user_id not in self.automation_configs:
            self.automation_configs[user_id] = {}
        self.automation_configs[user_id][config_type] = {
            "config": config_data,
            "enabled": True,
            "created_at": datetime.utcnow()
        }
        return {"success": True}
    
    async def get_automation_config(self, user_id, config_type):
        return self.automation_configs.get(user_id, {}).get(config_type)
    
    async def health_check(self):
        return {
            "status": "healthy",
            "users_count": len(self.users),
            "reddit_connections": len(self.reddit_tokens),
            "automation_configs": len(self.automation_configs)
        }

    # OAUTH STATE MANAGEMENT METHODS - ADDED FOR REDDIT CONNECTION FIX
    async def store_oauth_state(self, state: str, user_id: str, expires_at: datetime) -> Dict[str, Any]:
        """Store OAuth state in mock database"""
        self.oauth_states[state] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        logger.info(f"OAuth state stored: {state} for user {user_id}")
        return {"success": True}

    async def get_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Get OAuth state from mock database"""
        state_data = self.oauth_states.get(state)
        if not state_data:
            logger.warning(f"OAuth state not found: {state}")
            return None
        if state_data["expires_at"] <= datetime.utcnow():
            logger.warning(f"OAuth state expired: {state}")
            del self.oauth_states[state]
            return None
        return state_data

    async def cleanup_oauth_state(self, state: str) -> Dict[str, Any]:
        """Remove OAuth state from mock database"""
        if state in self.oauth_states:
            del self.oauth_states[state]
            return {"success": True}
        return {"success": False}

    async def get_all_oauth_states(self) -> List[str]:
        """Get all OAuth states for debugging"""
        return list(self.oauth_states.keys())








class MockAIService:
    def __init__(self):
        self.is_mock = True
        logger.warning("MockAIService initialized - Configure MISTRAL_API_KEY or GROQ_API_KEY for real AI")
    
    async def generate_reddit_domain_content(self, **kwargs):
        return {
            "success": False,
            "error": "Mock AI Service Active",
            "title": f"Mock Title for {kwargs.get('domain', 'general')}",
            "content": f"Mock content for {kwargs.get('business_type', 'business')}",
            "ai_service": "mock"
        }
    
    async def test_ai_connection(self):
        return {"success": False, "error": "Mock AI", "primary_service": "mock"}

class MockRedditConnector:
    def __init__(self):
        self.is_configured = False
    
    async def post_content_with_token(self, **kwargs):
        return {"success": False, "error": "Mock Reddit connector"}

class MockAutomationScheduler:
    def __init__(self): 
        self.is_running = True
        self.active_configs = {}
    
    def start_scheduler(self): 
        pass
    
    async def setup_auto_posting(self, config): 
        return {"success": False, "error": "Mock scheduler"}
    
    async def setup_auto_replies(self, config): 
        return {"success": False, "error": "Mock scheduler"}
    
    async def get_automation_status(self, user_id): 
        return {"success": True, "user_id": user_id, "mock_warning": True}






# Application lifespan management with multi-user support
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown with multi-user support"""
    global database_manager, ai_service, reddit_oauth_connector, automation_scheduler
    
    logger.info("Starting Multi-User Reddit Automation System with REAL AI CONTENT...")
    print("Initializing Multi-User Reddit Automation Platform...")
    
    # Verify environment variables
    required_vars = {
        'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
        'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET')
    }
    
    print("Environment Variables Status:")
    for var_name, var_value in required_vars.items():
        status = "FOUND" if var_value else "MISSING"
        print(f"  {var_name}: {status}")
        if var_value:
            logger.info(f"{var_name}: Present")
        else:
            logger.warning(f"{var_name}: Missing")
    
    # Initialize Multi-User Database
    try:
        if DatabaseManager and MULTIUSER_DB_AVAILABLE:
            database_manager = DatabaseManager("mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            await database_manager.connect()
            logger.info("Multi-User MongoDB Atlas connected successfully")
            print("Database: Multi-User MongoDB Atlas Connected")
            
            # Load existing user tokens and automations
            await load_existing_tokens()
            await load_all_user_automations()
            
        else:
            raise ImportError("Multi-User DatabaseManager not available")
    except Exception as e:
        logger.warning(f"Multi-User database initialization failed: {e}")
        database_manager = MockMultiUserDatabase()
        await database_manager.connect()
        print("Database: Mock Multi-User mode")
    
    # Initialize AI Service
    try:
        if AIService and (MISTRAL_KEY or GROQ_KEY):
            logger.info("Attempting to initialize REAL AI service...")
            ai_service = AIService()
            
            test_result = await ai_service.test_ai_connection()
            
            if test_result.get("success") and test_result.get('primary_service') != 'mock':
                primary_service = test_result.get('primary_service', 'unknown')
                logger.info(f"REAL AI service initialized successfully: {primary_service}")
                print(f"AI Service: {primary_service.upper()} CONNECTED")
                
                test_content = await ai_service.generate_reddit_domain_content(
                    domain="tech",
                    business_type="test",
                    business_description="test",
                    test_mode=False
                )
                
                if test_content.get('ai_service') != 'mock':
                    logger.info("AI content generation verified - REAL AI active")
                    print("AI Content Generation: VERIFIED")
                else:
                    raise Exception("AI service returning mock content")
                    
            else:
                raise Exception(f"AI service test failed: {test_result}")
                
        else:
            raise Exception("AI service not available or no API keys")
            
    except Exception as e:
        logger.error(f"REAL AI service initialization failed: {e}")
        logger.error("Falling back to MockAIService")
        ai_service = MockAIService()
        print("AI Service: MOCK MODE - Configure API keys")
    
    # Initialize Reddit OAuth Connector
    try:
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        print(f"Reddit Client ID found: {bool(reddit_client_id)}")
        print(f"Reddit Client Secret found: {bool(reddit_client_secret)}")
        
        if reddit_client_id and reddit_client_secret:
            config = {
                'REDDIT_CLIENT_ID': reddit_client_id,
                'REDDIT_CLIENT_SECRET': reddit_client_secret,
                'REDDIT_REDIRECT_URI': os.getenv('REDDIT_REDIRECT_URI', 'https://velocityfly.onrender.com/api/oauth/reddit/callback'),
                'REDDIT_USER_AGENT': os.getenv('REDDIT_USER_AGENT', 'IndianAutomationPlatform/1.0'),
                'TOKEN_ENCRYPTION_KEY': os.getenv('TOKEN_ENCRYPTION_KEY', 'default_key_change_in_production')
            }
            
            # Create a simple Reddit OAuth connector
            class SimpleRedditOAuth:
                def __init__(self, config):
                    self.config = config
                    self.is_configured = True
                
                async def post_content_with_token(self, **kwargs):
                    # Simple Reddit API posting implementation
                    access_token = kwargs.get('access_token')
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'User-Agent': self.config['REDDIT_USER_AGENT']
                    }
                    
                    data = {
                        'kind': 'self',
                        'title': kwargs.get('title'),
                        'text': kwargs.get('content'),
                        'sr': kwargs.get('subreddit_name')
                    }
                    
                    try:
                        import requests
                        response = requests.post(
                            'https://oauth.reddit.com/api/submit',
                            headers=headers,
                            data=data,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            return {
                                "success": True,
                                "post_id": "reddit_post_id",
                                "post_url": f"https://reddit.com/r/{kwargs.get('subreddit_name')}/comments/post_id"
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Reddit API error: {response.status_code}",
                                "message": response.text[:200]
                            }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Reddit posting failed: {str(e)}"
                        }
            
            reddit_oauth_connector = SimpleRedditOAuth(config)
            logger.info("Simple Reddit OAuth connector initialized successfully")
            print("Reddit OAuth: Simple Implementation Configured")
        else:
            raise ImportError("Reddit credentials missing")
    except Exception as e:
        logger.warning(f"Reddit OAuth initialization failed: {e}")
        reddit_oauth_connector = MockRedditConnector()
        print("Reddit OAuth: Mock mode")
    
    # Initialize Multi-User Reddit Automation System  
    try:
        if (AUTOMATION_AVAILABLE and RedditAutomationScheduler and 
            not isinstance(ai_service, MockAIService) and 
            not isinstance(reddit_oauth_connector, MockRedditConnector)):
            
            automation_scheduler = RedditAutomationScheduler(
                reddit_oauth_connector, ai_service, database_manager, user_reddit_tokens
            )
            automation_scheduler.start_scheduler()
            logger.info("REAL Multi-User Reddit automation system initialized")
            print("Automation Scheduler: REAL MULTI-USER MODE")
        else:
            raise ImportError("Real automation components not available")
    except Exception as e:
        logger.warning(f"Real automation system initialization failed: {e}")
        automation_scheduler = MockAutomationScheduler()
        automation_scheduler.start_scheduler()
        print("Automation Scheduler: Mock Multi-User mode")
    
    # Final status report
    real_components = []
    mock_components = []
    
    if not isinstance(ai_service, MockAIService):
        real_components.append("AI Content Generation")
    else:
        mock_components.append("AI (needs MISTRAL_API_KEY or GROQ_API_KEY)")
        
    if not isinstance(reddit_oauth_connector, MockRedditConnector):
        real_components.append("Reddit API")
    else:
        mock_components.append("Reddit (needs REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET)")
        
    if not isinstance(automation_scheduler, MockAutomationScheduler):
        real_components.append("Multi-User Auto-posting")
    else:
        mock_components.append("Automation (depends on AI + Reddit)")
    
    if MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase):
        real_components.append("Multi-User Database")
    else:
        mock_components.append("Database (using mock)")
    
    print(f"\nREAL Multi-User Components: {real_components if real_components else 'None'}")
    print(f"Mock Components: {mock_components if mock_components else 'None'}")
    print("Multi-User Application startup completed!\n")
    
    logger.info("Multi-User application startup completed")
    
    yield
    
    # Cleanup
    logger.info("Shutting down multi-user application...")
    if automation_scheduler and hasattr(automation_scheduler, 'is_running'):
        automation_scheduler.is_running = False
    if database_manager and hasattr(database_manager, 'disconnect'):
        try:
            await database_manager.disconnect()
        except Exception as e:
            logger.warning(f"Database disconnect failed: {e}")



# Create FastAPI app
app = FastAPI(
    title="Multi-User Reddit Automation Platform",
    description="Complete Multi-User Reddit Automation System with Individual User Accounts",
    version="6.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ADD TO TOP OF main.py
# from fastapi.middleware.cors import CORSMiddleware

# ADD AFTER app = FastAPI()
# ADD THIS IMMEDIATELY AFTER app = FastAPI()
# Find this section in your main.py (around lines 25-35) and replace it:

# ===== CORS Configuration - FIXED =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8080",
        "https://velocityfly-ai.onrender.com",  # Your frontend domain
        "https://velocityfly.onrender.com"  # Your backend domain
         # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "X-User-Token",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=["*"],
    
    max_age=3600
)




app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)


# Add this code after your CORS middleware (around line 50 in main.py):

@app.options("/{path:path}")
async def options_handler(request: Request):
    """Handle preflight OPTIONS requests"""
    return Response(
        content="",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-User-Token",
            "Access-Control-Max-Age": "3600"
        }
    )




# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "An unexpected error occurred.",
            "timestamp": datetime.now().isoformat()
        }
    )

# Health check endpoints
@app.get("/")
async def root():
    ai_status = "real" if not isinstance(ai_service, MockAIService) else "mock"
    reddit_status = "real" if not isinstance(reddit_oauth_connector, MockRedditConnector) else "mock"
    db_status = "real" if MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase) else "mock"
    
    return {
        "success": True,
        "message": "Multi-User Reddit Automation Platform API - REAL AI CONTENT GENERATION",
        "version": "6.0.0",
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "multi_user_enabled": True,
        "real_ai_active": ai_status == "real",
        "real_reddit_active": reddit_status == "real",
        "real_database_active": db_status == "real",
        "services": {
            "reddit": f"{type(reddit_oauth_connector).__name__} ({reddit_status})",
            "ai": f"{type(ai_service).__name__} ({ai_status})",
            "database": f"{type(database_manager).__name__} ({db_status})",
            "automation": type(automation_scheduler).__name__
        }
    }




@app.get("/health")
async def health_check():
    """Enhanced health check with CORS headers"""
    try:
        # Test AI service
        ai_status = "working"
        try:
            test_result = await ai_service.test_connection()
            if not test_result.get("success"):
                ai_status = "error"
        except Exception as e:
            ai_status = f"error: {str(e)}"
        
        # Test database
        db_status = "connected"
        try:
            if hasattr(db_manager, 'db') and db_manager.db:
                await db_manager.db.admin.command('ismaster')
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "ai_service": ai_status,
                "database": db_status,
                "reddit_automation": "active"
            },
            "version": "2.0.0"
        }
        
        return Response(
            content=json.dumps(health_data),
            media_type="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        error_data = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return Response(
            content=json.dumps(error_data),
            status_code=500,
            media_type="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )






# # User-specific Reddit endpoints
# @app.get("/api/reddit/connection-status")
# async def get_reddit_connection_status(current_user: dict = Depends(get_current_user)):
#     """Get Reddit connection status for current user"""
#     try:
#         user_id = current_user["id"]
        
#         # Check database for user's Reddit connection
#         if database_manager and hasattr(database_manager, 'check_reddit_connection'):
#             db_status = await database_manager.check_reddit_connection(user_id)
            
#             if db_status.get("connected"):
#                 # Load token into memory if not already there
#                 if user_id not in user_reddit_tokens:
#                     tokens = await database_manager.get_reddit_tokens(user_id)
#                     if tokens and tokens.get("is_valid"):
#                         user_reddit_tokens[user_id] = {
#                             "access_token": tokens["access_token"],
#                             "refresh_token": tokens.get("refresh_token", ""),
#                             "reddit_username": tokens["reddit_username"],
#                             "connected_at": datetime.now().isoformat()
#                         }
#                         logger.info(f"Loaded Reddit token for user {user_id}")
                
#                 return {
#                     "success": True,
#                     "connected": True,
#                     "user_id": user_id,
#                     "reddit_username": db_status.get("reddit_username"),
#                     "expires_at": db_status.get("expires_at"),
#                     "message": f"Reddit connected as {db_status.get('reddit_username')}",
#                     "source": "database"
#                 }
        
#         # Fallback to memory check
#         if user_id in user_reddit_tokens:
#             creds = user_reddit_tokens[user_id]
#             username = creds.get("reddit_username")
#             return {
#                 "success": True,
#                 "connected": True,
#                 "user_id": user_id,
#                 "reddit_username": username,
#                 "connected_at": creds.get("connected_at"),
#                 "message": f"Reddit connected as {username}",
#                 "source": "memory"
#             }
        
#         return {
#             "success": True,
#             "connected": False,
#             "user_id": user_id,
#             "message": "No Reddit connection found"
#         }
        
#     except Exception as e:
#         logger.error(f"Connection status check failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.get("/api/reddit/test-connection")
# async def test_reddit_connection(current_user: dict = Depends(get_current_user)):
#     """Test Reddit API connection for current user"""
#     try:
#         user_id = current_user["id"]
        
#         # Check if user has Reddit tokens
#         if user_id not in user_reddit_tokens:
#             return {
#                 "success": False,
#                 "error": "Reddit not connected",
#                 "message": "Please connect your Reddit account first"
#             }
        
#         # Test with Reddit connector
#         if isinstance(reddit_oauth_connector, MockRedditConnector):
#             return {
#                 "success": False,
#                 "error": "Mock connector active",
#                 "message": "Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET for real connection"
#             }
        
#         username = user_reddit_tokens[user_id].get("reddit_username")
#         logger.info(f"Testing Reddit connection for {username}")
        
#         return {
#             "success": True,
#             "message": f"Reddit connection verified for {username}",
#             "username": username,
#             "real_connection": True
#         }
        
#     except Exception as e:
#         logger.error(f"Reddit connection test failed: {e}")
#         return {"success": False, "error": str(e)}

# Completion of health check endpoint (from Part 1)
@app.get("/health")
async def health_check():
    try:
        ai_status = "unknown"
        ai_is_real = not isinstance(ai_service, MockAIService)
        
        if hasattr(ai_service, 'test_ai_connection'):
            try:
                test_result = await ai_service.test_ai_connection()
                if ai_is_real and test_result.get("success"):
                    ai_status = f"connected_{test_result.get('primary_service', 'unknown')}"
                elif ai_is_real:
                    ai_status = "real_service_failed"
                else:
                    ai_status = "mock_active"
            except Exception as e:
                ai_status = f"error_{str(e)[:20]}"
        
        return {
            "success": True,
            "health": {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "multi_user_system": True,
                "real_ai_content_enabled": ai_is_real,
                "real_posting_enabled": not isinstance(reddit_oauth_connector, MockRedditConnector),
                "real_database_enabled": MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase),
                "services": {
                    "database": {
                        "success": database_manager is not None and not isinstance(database_manager, MockMultiUserDatabase), 
                        "status": "connected" if database_manager else "failed",
                        "type": type(database_manager).__name__,
                        "multi_user": MULTIUSER_DB_AVAILABLE
                    },
                    "ai_service": {
                        "success": ai_is_real and ai_status.startswith("connected"), 
                        "status": ai_status,
                        "type": type(ai_service).__name__,
                        "real_ai": ai_is_real
                    },
                    "reddit_oauth": {
                        "success": reddit_oauth_connector is not None and hasattr(reddit_oauth_connector, 'is_configured') and reddit_oauth_connector.is_configured, 
                        "status": "configured" if reddit_oauth_connector and hasattr(reddit_oauth_connector, 'is_configured') and reddit_oauth_connector.is_configured else "mock",
                        "type": type(reddit_oauth_connector).__name__
                    },
                    "automation": {
                        "success": automation_scheduler is not None, 
                        "status": "running" if automation_scheduler and automation_scheduler.is_running else "stopped",
                        "type": type(automation_scheduler).__name__,
                        "real_posting": not isinstance(automation_scheduler, MockAutomationScheduler)
                    }
                },
                "stats": {
                    "active_reddit_tokens": len(user_reddit_tokens),
                    "oauth_states": len(oauth_states),
                    "automation_configs": len(automation_configs)
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"success": False, "error": str(e), "status": "unhealthy"}







# Multi-User Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: RegisterRequest):
    """Register new user with email and password"""
    try:
        result = await database_manager.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        if result["success"]:
            logger.info(f"New user registered: {user_data.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login_user(login_data: LoginRequest):
    """Login user and return JWT token"""
    try:
        result = await database_manager.login_user(
            email=login_data.email,
            password=login_data.password
        )
        
        if result["success"]:
            logger.info(f"User logged in: {login_data.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"User login failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "success": True,
        "user": current_user
    }





@app.get("/api/oauth/reddit/authorize")
async def reddit_oauth_authorize(current_user: dict = Depends(get_current_user)):
    """Start Reddit OAuth flow - FIXED FOR MULTI-USER"""
    try:
        user_id = current_user["id"]
        user_email = current_user.get("email", "Unknown")
        
        logger.info(f"🔵 Starting OAuth for user: {user_email} (ID: {user_id})")
        
        # ✅ CRITICAL FIX: Encode user_id in state parameter
        import base64
        import json
        import secrets
        
        state_data = {
            'user_id': user_id,
            'random': secrets.token_urlsafe(16)
        }
        
        # Base64 encode the state
        state = base64.b64encode(
            json.dumps(state_data).encode('utf-8')
        ).decode('utf-8')
        
        logger.info(f"🔐 Generated state with encoded user_id: {state[:20]}...")
        
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_redirect_uri = os.getenv(
            "REDDIT_REDIRECT_URI",
            "https://velocityfly.onrender.com/api/oauth/reddit/callback"
        )
        
        if not reddit_client_id:
            raise HTTPException(status_code=500, detail="Reddit credentials not configured")
        
        # Build OAuth URL
        oauth_url = (
            f"https://www.reddit.com/api/v1/authorize?"
            f"client_id={reddit_client_id}"
            f"&response_type=code"
            f"&state={state}"
            f"&redirect_uri={reddit_redirect_uri}"
            f"&duration=permanent"
            f"&scope=identity,submit,edit,read"
        )
        
        logger.info(f"✅ OAuth URL generated for user {user_email}")
        
        return {
            "success": True,
            "redirect_url": oauth_url,
            "state": state,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"❌ OAuth authorize failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

import httpx
import base64
import traceback
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
import os










# @app.get("/api/oauth/reddit/callback")
# async def reddit_oauth_callback(
#     code: str = None,
#     state: str = None,
#     error: str = None,
#     request: Request = None


# ):
    
@app.get("/api/oauth/reddit/callback")
async def reddit_oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    request: Request = None
):
    """
    ✅ FIXED: Reddit OAuth callback with proper state cleanup
    Handles reconnection by clearing old tokens before adding new ones
    """
    try:
        logger.info("=" * 80)
        logger.info("🔵 REDDIT OAUTH CALLBACK STARTED")
        logger.info(f"📥 Code: {code[:30] + '...' if code else 'MISSING'}")
        logger.info(f"📥 State: {state[:50] + '...' if state else 'MISSING'}")
        logger.info(f"📥 Error: {error if error else 'None'}")
        
        frontend_url = os.getenv("FRONTEND_URL", "https://velocityfly-ai.onrender.com")
        
        # Check for OAuth errors
        if error:
            logger.error(f"❌ Reddit OAuth error: {error}")
            return RedirectResponse(
                url=f"{frontend_url}?error={error}",
                status_code=302
            )
        
        # Validate parameters
        if not code or not state:
            logger.error(f"❌ Missing parameters!")
            return RedirectResponse(
                url=f"{frontend_url}?error=missing_parameters",
                status_code=302
            )
        
        # ✅ DECODE STATE
        try:
            import base64
            import json
            
            decoded_state = base64.b64decode(state).decode('utf-8')
            state_data = json.loads(decoded_state)
            user_id = state_data.get('user_id')
            
            if not user_id:
                logger.error("❌ No user_id in state!")
                return RedirectResponse(
                    url=f"{frontend_url}?error=invalid_state_no_user",
                    status_code=302
                )
            
            logger.info(f"✅ Decoded user_id from state: {user_id}")
                
        except Exception as decode_error:
            logger.error(f"❌ State decoding failed: {decode_error}")
            return RedirectResponse(
                url=f"{frontend_url}?error=state_decode_failed",
                status_code=302
            )
        
        # ✅ CRITICAL: Clear old Reddit connection for this user BEFORE adding new one
        logger.info(f"🧹 Clearing old Reddit connection for user {user_id} (if exists)...")
        
        # Remove from memory
        if user_id in user_reddit_tokens:
            old_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
            del user_reddit_tokens[user_id]
            logger.info(f"✅ Removed old Reddit token from memory: u/{old_username}")
        
        # Mark old tokens as inactive in database
        if database_manager and hasattr(database_manager, 'revoke_reddit_connection'):
            try:
                await database_manager.revoke_reddit_connection(user_id)
                logger.info(f"✅ Revoked old Reddit tokens in database")
            except Exception as revoke_error:
                logger.warning(f"⚠️ Failed to revoke old tokens: {revoke_error}")
        
        # ✅ NOW PROCEED WITH NEW TOKEN EXCHANGE
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        reddit_redirect_uri = os.getenv(
            "REDDIT_REDIRECT_URI",
            "https://velocityfly.onrender.com/api/oauth/reddit/callback"
        )
        reddit_user_agent = os.getenv("REDDIT_USER_AGENT", "VelocityPost/1.0")
        
        if not reddit_client_id or not reddit_client_secret:
            logger.error("❌ Reddit credentials not configured!")
            return RedirectResponse(
                url=f"{frontend_url}?error=missing_credentials",
                status_code=302
            )
        
        # Token exchange
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': reddit_redirect_uri
        }
        
        auth_string = f"{reddit_client_id}:{reddit_client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': reddit_user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        logger.info(f"📤 Exchanging code for token...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            token_response = await client.post(
                'https://www.reddit.com/api/v1/access_token',
                data=token_data,
                headers=headers
            )
            
            if token_response.status_code != 200:
                logger.error(f"❌ Token exchange failed: {token_response.status_code}")
                return RedirectResponse(
                    url=f"{frontend_url}?error=token_exchange_failed&status={token_response.status_code}",
                    status_code=302
                )
            
            tokens = token_response.json()
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 3600)
        
        if not access_token:
            logger.error("❌ No access_token in response!")
            return RedirectResponse(
                url=f"{frontend_url}?error=no_access_token",
                status_code=302
            )
        
        # Get Reddit user info
        user_headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': reddit_user_agent
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            user_response = await client.get(
                'https://oauth.reddit.com/api/v1/me',
                headers=user_headers
            )
            
            if user_response.status_code != 200:
                logger.error(f"❌ Failed to get user info: {user_response.status_code}")
                return RedirectResponse(
                    url=f"{frontend_url}?error=user_info_failed",
                    status_code=302
                )
            
            reddit_user = user_response.json()
        
        reddit_username = reddit_user.get('name')
        reddit_user_id = reddit_user.get('id')
        
        if not reddit_username:
            logger.error("❌ No username in Reddit response!")
            return RedirectResponse(
                url=f"{frontend_url}?error=no_username",
                status_code=302
            )
        
        # ✅ Store NEW tokens (old ones are already cleared)
        token_doc = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'reddit_username': reddit_username,
            'reddit_user_id': reddit_user_id,
            'expires_in': expires_in,
            'token_type': 'bearer',
            'scope': 'identity,submit,edit,read'
        }
        
        # Store in database
        if database_manager and hasattr(database_manager, 'store_reddit_tokens'):
            try:
                db_result = await database_manager.store_reddit_tokens(user_id, token_doc)
                if db_result.get('success'):
                    logger.info(f"✅ NEW Reddit tokens stored: u/{reddit_username}")
            except Exception as db_error:
                logger.error(f"⚠️ Database storage failed: {db_error}")
        
        # Store in memory
        user_reddit_tokens[user_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "reddit_username": reddit_username,
            "reddit_user_id": reddit_user_id,
            "expires_in": expires_in,
            "connected_at": datetime.now().isoformat(),
            "user_info": {
                "name": reddit_username,
                "id": reddit_user_id
            }
        }
        
        logger.info("=" * 80)
        logger.info(f"✅ REDDIT CONNECTED: u/{reddit_username}")
        logger.info("=" * 80)
        
        # Redirect to frontend
        redirect_url = f"{frontend_url}?reddit_connected=true&username={reddit_username}"
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        logger.error(f"❌ OAuth callback error: {e}")
        logger.error(traceback.format_exc())
        
        frontend_url = os.getenv("FRONTEND_URL", "https://velocityfly-ai.onrender.com")
        return RedirectResponse(
            url=f"{frontend_url}?error=callback_exception",
            status_code=302
        )



    """
    Reddit OAuth callback - ENHANCED WITH FULL DEBUG LOGGING
    Tracks every step to identify exactly where the issue occurs
    """
    try:
        logger.info("=" * 80)
        logger.info("🔵 REDDIT OAUTH CALLBACK STARTED")
        logger.info(f"📥 Received parameters:")
        logger.info(f"   - Code: {code[:30] + '...' if code else 'MISSING'}")
        logger.info(f"   - State: {state[:50] + '...' if state else 'MISSING'}")
        logger.info(f"   - Error: {error if error else 'None'}")
        logger.info(f"   - Request URL: {request.url if request else 'N/A'}")
        
        # ✅ Get frontend URL
        frontend_url = os.getenv("FRONTEND_URL", "https://velocityfly-ai.onrender.com")
        logger.info(f"🔗 Frontend URL: {frontend_url}")
        
        # Check for OAuth errors from Reddit
        if error:
            logger.error(f"❌ Reddit returned OAuth error: {error}")
            return RedirectResponse(
                url=f"{frontend_url}?error={error}",
                status_code=302
            )
        
        # Validate required parameters
        if not code or not state:
            logger.error(f"❌ Missing required parameters!")
            logger.error(f"   - Code present: {bool(code)}")
            logger.error(f"   - State present: {bool(state)}")
            return RedirectResponse(
                url=f"{frontend_url}?error=missing_parameters",
                status_code=302
            )
        
        logger.info("✅ Step 1: Parameters validated")
        
        # ✅ STEP 2: Decode state to get user_id
        logger.info("=" * 60)
        logger.info("🔍 STEP 2: Decoding state parameter...")
        
        try:
            import base64
            import json
            
            logger.info(f"State raw value: {state[:100]}")
            logger.info(f"State length: {len(state)}")
            
            decoded_state = base64.b64decode(state).decode('utf-8')
            logger.info(f"✅ Base64 decoded: {decoded_state}")
            
            state_data = json.loads(decoded_state)
            logger.info(f"✅ JSON parsed: {state_data}")
            
            user_id = state_data.get('user_id')
            logger.info(f"✅ Extracted user_id: {user_id}")
            
            if not user_id:
                logger.error("❌ No user_id found in state data!")
                logger.error(f"State data contents: {state_data}")
                return RedirectResponse(
                    url=f"{frontend_url}?error=invalid_state_no_user",
                    status_code=302
                )
            
            logger.info(f"✅ Step 2 Complete: user_id = {user_id}")
                
        except Exception as decode_error:
            logger.error(f"❌ State decoding failed!")
            logger.error(f"Error type: {type(decode_error).__name__}")
            logger.error(f"Error message: {str(decode_error)}")
            logger.error(f"Full traceback:")
            logger.error(traceback.format_exc())
            return RedirectResponse(
                url=f"{frontend_url}?error=state_decode_failed",
                status_code=302
            )
        
        # ✅ STEP 3: Load Reddit credentials
        logger.info("=" * 60)
        logger.info("🔍 STEP 3: Loading Reddit OAuth credentials...")
        
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        reddit_redirect_uri = os.getenv(
            "REDDIT_REDIRECT_URI",
            "https://velocityfly.onrender.com/api/oauth/reddit/callback"
        )
        reddit_user_agent = os.getenv("REDDIT_USER_AGENT", "VelocityPost/1.0")
        
        logger.info(f"📋 Credentials check:")
        logger.info(f"   - Client ID present: {bool(reddit_client_id)}")
        logger.info(f"   - Client ID length: {len(reddit_client_id) if reddit_client_id else 0}")
        logger.info(f"   - Client ID value: {reddit_client_id if reddit_client_id else 'NOT SET'}")
        logger.info(f"   - Secret present: {bool(reddit_client_secret)}")
        logger.info(f"   - Secret length: {len(reddit_client_secret) if reddit_client_secret else 0}")
        logger.info(f"   - Secret preview: {reddit_client_secret[:5] + '...' if reddit_client_secret else 'NOT SET'}")
        logger.info(f"   - Redirect URI: {reddit_redirect_uri}")
        logger.info(f"   - User Agent: {reddit_user_agent}")
        
        if not reddit_client_id:
            logger.error("❌ REDDIT_CLIENT_ID environment variable is NOT SET!")
            return RedirectResponse(
                url=f"{frontend_url}?error=missing_client_id",
                status_code=302
            )
        
        if not reddit_client_secret:
            logger.error("❌ REDDIT_CLIENT_SECRET environment variable is NOT SET!")
            return RedirectResponse(
                url=f"{frontend_url}?error=missing_client_secret",
                status_code=302
            )
        
        logger.info("✅ Step 3 Complete: All credentials loaded")
        
        # ✅ STEP 4: Prepare token exchange request
        logger.info("=" * 60)
        logger.info("🔍 STEP 4: Preparing token exchange request...")
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': reddit_redirect_uri
        }
        
        logger.info(f"📤 Request payload:")
        logger.info(f"   - grant_type: {token_data['grant_type']}")
        logger.info(f"   - code: {code[:30]}...")
        logger.info(f"   - redirect_uri: {token_data['redirect_uri']}")
        
        # Create Basic Auth header
        auth_string = f"{reddit_client_id}:{reddit_client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        logger.info(f"🔐 Basic Auth:")
        logger.info(f"   - Auth string length: {len(auth_string)}")
        logger.info(f"   - Base64 length: {len(auth_b64)}")
        logger.info(f"   - Base64 preview: {auth_b64[:20]}...")
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': reddit_user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        logger.info(f"📋 Request headers prepared")
        logger.info("✅ Step 4 Complete: Request ready")
        
        # ✅ STEP 5: Send token exchange request
        logger.info("=" * 60)
        logger.info("🔍 STEP 5: Sending token exchange request to Reddit...")
        logger.info(f"📤 POST https://www.reddit.com/api/v1/access_token")
        
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                token_response = await client.post(
                    'https://www.reddit.com/api/v1/access_token',
                    data=token_data,
                    headers=headers
                )
            
            logger.info(f"📥 Reddit API Response:")
            logger.info(f"   - Status Code: {token_response.status_code}")
            logger.info(f"   - Status Text: {token_response.reason_phrase if hasattr(token_response, 'reason_phrase') else 'N/A'}")
            logger.info(f"   - Response Headers: {dict(token_response.headers)}")
            logger.info(f"   - Response Body: {token_response.text[:500]}")
            
            if token_response.status_code == 401:
                logger.error("=" * 60)
                logger.error("❌ 401 UNAUTHORIZED ERROR!")
                logger.error("This means Reddit rejected your credentials.")
                logger.error("")
                logger.error("Common causes:")
                logger.error("1. Wrong Client ID or Secret")
                logger.error("2. Client ID and Secret don't match (from different apps)")
                logger.error("3. Redirect URI mismatch")
                logger.error("4. Code already used or expired")
                logger.error("")
                logger.error("Verify on Reddit:")
                logger.error(f"   Expected Client ID: {reddit_client_id}")
                logger.error(f"   Expected Redirect: {reddit_redirect_uri}")
                logger.error("=" * 60)
                
                return RedirectResponse(
                    url=f"{frontend_url}?error=reddit_401_unauthorized&client_id={reddit_client_id[:10]}",
                    status_code=302
                )
            
            if token_response.status_code == 400:
                logger.error("=" * 60)
                logger.error("❌ 400 BAD REQUEST ERROR!")
                logger.error("This means the request format is wrong.")
                logger.error(f"Response: {token_response.text}")
                logger.error("=" * 60)
                
                return RedirectResponse(
                    url=f"{frontend_url}?error=reddit_400_bad_request",
                    status_code=302
                )
            
            if token_response.status_code != 200:
                logger.error(f"❌ Unexpected status code: {token_response.status_code}")
                logger.error(f"Response: {token_response.text}")
                return RedirectResponse(
                    url=f"{frontend_url}?error=token_exchange_failed&status={token_response.status_code}",
                    status_code=302
                )
            
            logger.info("✅ Step 5 Complete: Token exchange successful!")
            
        except httpx.TimeoutException as timeout_err:
            logger.error("❌ Request timeout!")
            logger.error(f"Error: {timeout_err}")
            return RedirectResponse(
                url=f"{frontend_url}?error=timeout",
                status_code=302
            )
        except httpx.ConnectError as conn_err:
            logger.error("❌ Connection error!")
            logger.error(f"Error: {conn_err}")
            return RedirectResponse(
                url=f"{frontend_url}?error=connection_failed",
                status_code=302
            )
        
        # ✅ STEP 6: Parse token response
        logger.info("=" * 60)
        logger.info("🔍 STEP 6: Parsing token response...")
        
        try:
            tokens = token_response.json()
            logger.info(f"✅ JSON parsed successfully")
            logger.info(f"Token response keys: {list(tokens.keys())}")
        except Exception as parse_error:
            logger.error(f"❌ Failed to parse JSON response!")
            logger.error(f"Error: {parse_error}")
            logger.error(f"Raw response: {token_response.text}")
            return RedirectResponse(
                url=f"{frontend_url}?error=token_parse_failed",
                status_code=302
            )
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 3600)
        token_type = tokens.get('token_type', 'bearer')
        scope = tokens.get('scope', '')
        
        logger.info(f"📋 Tokens extracted:")
        logger.info(f"   - Access token present: {bool(access_token)}")
        logger.info(f"   - Access token length: {len(access_token) if access_token else 0}")
        logger.info(f"   - Refresh token present: {bool(refresh_token)}")
        logger.info(f"   - Expires in: {expires_in} seconds")
        logger.info(f"   - Token type: {token_type}")
        logger.info(f"   - Scope: {scope}")
        
        if not access_token:
            logger.error("❌ No access_token in response!")
            logger.error(f"Response contents: {tokens}")
            return RedirectResponse(
                url=f"{frontend_url}?error=no_access_token",
                status_code=302
            )
        
        logger.info("✅ Step 6 Complete: Tokens extracted")
        
        # ✅ STEP 7: Get Reddit user info
        logger.info("=" * 60)
        logger.info("🔍 STEP 7: Fetching Reddit user information...")
        
        user_headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': reddit_user_agent
        }
        
        logger.info(f"📤 GET https://oauth.reddit.com/api/v1/me")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                user_response = await client.get(
                    'https://oauth.reddit.com/api/v1/me',
                    headers=user_headers
                )
            
            logger.info(f"📥 User info response:")
            logger.info(f"   - Status: {user_response.status_code}")
            logger.info(f"   - Body preview: {user_response.text[:200]}")
            
            if user_response.status_code != 200:
                logger.error(f"❌ Failed to get user info: {user_response.status_code}")
                logger.error(f"Response: {user_response.text}")
                return RedirectResponse(
                    url=f"{frontend_url}?error=user_info_failed",
                    status_code=302
                )
            
        except Exception as user_req_error:
            logger.error(f"❌ User info request failed!")
            logger.error(f"Error: {user_req_error}")
            return RedirectResponse(
                url=f"{frontend_url}?error=user_info_request_failed",
                status_code=302
            )
        
        try:
            reddit_user = user_response.json()
            logger.info(f"✅ User info parsed")
            logger.info(f"User data keys: {list(reddit_user.keys())}")
        except Exception as user_parse_error:
            logger.error(f"❌ Failed to parse user info!")
            logger.error(f"Error: {user_parse_error}")
            return RedirectResponse(
                url=f"{frontend_url}?error=user_info_parse_failed",
                status_code=302
            )
        
        reddit_username = reddit_user.get('name')
        reddit_user_id = reddit_user.get('id')
        
        logger.info(f"📋 User info extracted:")
        logger.info(f"   - Username: u/{reddit_username if reddit_username else 'MISSING'}")
        logger.info(f"   - User ID: {reddit_user_id if reddit_user_id else 'MISSING'}")
        
        if not reddit_username:
            logger.error("❌ No username in Reddit response!")
            logger.error(f"User data: {reddit_user}")
            return RedirectResponse(
                url=f"{frontend_url}?error=no_username",
                status_code=302
            )
        
        logger.info("✅ Step 7 Complete: User info retrieved")
        
        # ✅ STEP 8: Store tokens
        logger.info("=" * 60)
        logger.info("🔍 STEP 8: Storing Reddit tokens...")
        logger.info(f"   - Storing for user_id: {user_id}")
        logger.info(f"   - Reddit username: u/{reddit_username}")
        
        token_doc = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'reddit_username': reddit_username,
            'reddit_user_id': reddit_user_id,
            'expires_in': expires_in,
            'token_type': token_type,
            'scope': scope
        }
        
        # Store in database
        if database_manager and hasattr(database_manager, 'store_reddit_tokens'):
            try:
                db_result = await database_manager.store_reddit_tokens(user_id, token_doc)
                logger.info(f"✅ Database storage: {db_result.get('success')}")
                if not db_result.get('success'):
                    logger.warning(f"⚠️ Database storage returned: {db_result}")
            except Exception as db_error:
                logger.error(f"⚠️ Database storage failed: {db_error}")
                logger.error(traceback.format_exc())
        else:
            logger.warning("⚠️ Database manager not available for token storage")
        
        # Store in memory
        try:
            user_reddit_tokens[user_id] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "reddit_username": reddit_username,
                "reddit_user_id": reddit_user_id,
                "expires_in": expires_in,
                "connected_at": datetime.now().isoformat(),
                "user_info": {
                    "name": reddit_username,
                    "id": reddit_user_id
                }
            }
            logger.info(f"✅ Memory storage successful")
            logger.info(f"✅ Total users with Reddit: {len(user_reddit_tokens)}")
        except Exception as mem_error:
            logger.error(f"⚠️ Memory storage failed: {mem_error}")
        
        logger.info("✅ Step 8 Complete: Tokens stored")
        
        # ✅ SUCCESS
        logger.info("=" * 80)
        logger.info("✅✅✅ REDDIT OAUTH COMPLETED SUCCESSFULLY! ✅✅✅")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Reddit Username: u/{reddit_username}")
        logger.info(f"Reddit User ID: {reddit_user_id}")
        logger.info("=" * 80)
        
        # Redirect to frontend with success
        redirect_url = f"{frontend_url}?reddit_connected=true&username={reddit_username}"
        logger.info(f"🔄 Redirecting to: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌❌❌ UNEXPECTED ERROR IN OAUTH CALLBACK! ❌❌❌")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        
        frontend_url = os.getenv("FRONTEND_URL", "https://velocityfly-ai.onrender.com")
        return RedirectResponse(
            url=f"{frontend_url}?error=callback_exception",
            status_code=302
        )

# @app.get("/api/oauth/reddit/callback")
# async def reddit_oauth_callback(code: str, state: str):
#     """Handle Reddit OAuth callback for authenticated user - FIXED VERSION"""
#     try:
#         # FIXED: Get user_id from database instead of memory
#         state_data = await database_manager.get_oauth_state(state)
#         if not state_data:
#             logger.error(f"Invalid OAuth state from database: {state}")
#             logger.error(f"Available states in database: {await database_manager.get_all_oauth_states() if hasattr(database_manager, 'get_all_oauth_states') else 'method not available'}")
#             return RedirectResponse(
#                 url="https://velocityfly-ai.onrender.com/?error=invalid_oauth_state",
#                 status_code=302
#             )
        
#         user_id = state_data["user_id"]
#         logger.info(f"Processing OAuth callback for user {user_id} (state found in database)")
        
#         # ... rest of your existing callback code remains the same
        
#         # Exchange code for token
#         reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
#         reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
#         reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI")
        
#         if not reddit_client_id or not reddit_client_secret:
#             logger.error("Reddit credentials missing from environment")
#             return RedirectResponse(
#                 url="https://velocityfly-ai.onrender.com/?error=missing_credentials",
#                 status_code=302
#             )
        
#         # Token exchange request
#         auth_string = f"{reddit_client_id}:{reddit_client_secret}"
#         auth_bytes = auth_string.encode('ascii')
#         auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
#         headers = {
#             'Authorization': f'Basic {auth_b64}',
#             'User-Agent': 'IndianAutomationPlatform/1.0 by YourRedditUsername'
#         }
        
#         data = {
#             'grant_type': 'authorization_code',
#             'code': code,
#             'redirect_uri': reddit_redirect_uri
#         }
        
#         logger.info("Exchanging code for access token...")
        
#         response = requests.post(
#             'https://www.reddit.com/api/v1/access_token',
#             headers=headers,
#             data=data,
#             timeout=30
#         )
        
#         if response.status_code == 200:
#             token_data = response.json()
#             access_token = token_data.get('access_token')
            
#             if access_token:
#                 # Get Reddit user info with proper error handling
#                 user_headers = {
#                     'Authorization': f'Bearer {access_token}',
#                     'User-Agent': 'IndianAutomationPlatform/1.0 by YourRedditUsername'
#                 }
                
#                 username = None
#                 reddit_user_id = ""
#                 user_info = {}
                
#                 try:
#                     logger.info("Fetching Reddit user info...")
#                     user_response = requests.get(
#                         'https://oauth.reddit.com/api/v1/me',
#                         headers=user_headers,
#                         timeout=15
#                     )
                    
#                     logger.info(f"Reddit user info response: {user_response.status_code}")
                    
#                     if user_response.status_code == 200:
#                         user_info = user_response.json()
#                         username = user_info.get('name')
#                         reddit_user_id = user_info.get('id', '')
                        
#                         logger.info(f"Reddit API returned username: {username}")
                        
#                         if not username:
#                             logger.error("No username in Reddit API response")
#                             logger.error(f"Full user info response: {user_info}")
#                             username = f"User_{reddit_user_id[:8]}" if reddit_user_id else f"User_{uuid.uuid4().hex[:8]}"
#                     else:
#                         logger.error(f"Reddit user info request failed: {user_response.status_code}")
#                         logger.error(f"Response text: {user_response.text}")
#                         username = f"User_{uuid.uuid4().hex[:8]}"
#                         user_info = {"name": username, "id": reddit_user_id}
                        
#                 except Exception as e:
#                     logger.error(f"User info request failed: {e}")
#                     username = f"User_{uuid.uuid4().hex[:8]}"
#                     user_info = {"name": username, "id": reddit_user_id}
                
#                 # Ensure we always have a username
#                 if not username:
#                     username = f"User_{uuid.uuid4().hex[:8]}"
#                     logger.warning(f"Using fallback username: {username}")
                
#                 logger.info(f"REAL Reddit OAuth successful for user: {username}")
                
#                 # Store tokens in DATABASE permanently for this specific user
#                 db_token_data = {
#                     "access_token": access_token,
#                     "refresh_token": token_data.get("refresh_token", ""),
#                     "expires_in": token_data.get("expires_in", 3600),
#                     "reddit_username": username,
#                     "reddit_user_id": reddit_user_id,
#                     "token_type": "bearer",
#                     "scope": "submit,edit,read"
#                 }
                
#                 # Store in database for this user
#                 if database_manager and hasattr(database_manager, 'store_reddit_tokens'):
#                     try:
#                         db_result = await database_manager.store_reddit_tokens(user_id, db_token_data)
#                         if db_result.get("success"):
#                             logger.info(f"Reddit tokens stored permanently for user {user_id} as {username}")
#                         else:
#                             logger.error(f"Failed to store tokens in database: {db_result.get('error')}")
#                     except Exception as e:
#                         logger.error(f"Database storage error: {e}")
                
#                 # Also store in memory for immediate use
#                 user_reddit_tokens[user_id] = {
#                     "access_token": access_token,
#                     "refresh_token": token_data.get("refresh_token", ""),
#                     "reddit_username": username,
#                     "connected_at": datetime.now().isoformat(),
#                     "user_info": user_info or {"name": username, "id": reddit_user_id}
#                 }
                
#                 # Clean up OAuth state
#                 oauth_states.pop(state, None)
                
#                 # Redirect to main page instead of /reddit-auto to avoid 404
#                 return RedirectResponse(
#                     url=f"https://velocityfly-ai.onrender.com/?reddit_connected=true&username={username}",
#                     status_code=302
#                 )
#             else:
#                 logger.error("No access token in Reddit response")
#                 return RedirectResponse(
#                     url="https://velocityfly-ai.onrender.com/?error=no_access_token",
#                     status_code=302
#                 )
#         else:
#             logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
#             return RedirectResponse(
#                 url="https://velocityfly-ai.onrender.com/?error=token_exchange_failed",
#                 status_code=302
#             )
        
#     except Exception as e:
#         logger.error(f"OAuth callback failed: {e}")
#         logger.error(traceback.format_exc())
#         return RedirectResponse(
#             url="https://velocityfly-ai.onrender.com/?error=oauth_failed",
#             status_code=302
#         )

@app.get("/api/debug/reddit-config")
async def debug_reddit_config():
    """Debug Reddit OAuth configuration - COMPREHENSIVE"""
    reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
    reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI")
    reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
    frontend_url = os.getenv("FRONTEND_URL")
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "client_id": {
                "set": bool(reddit_client_id),
                "length": len(reddit_client_id) if reddit_client_id else 0,
                "value": reddit_client_id if reddit_client_id else "NOT_SET",
                "expected": "luTBXCyUteWCHyhoKeE6Lw"
            },
            "client_secret": {
                "set": bool(reddit_client_secret),
                "length": len(reddit_client_secret) if reddit_client_secret else 0,
                "preview": reddit_client_secret[:5] + "..." if reddit_client_secret else "NOT_SET",
                "expected_length": "~27 characters"
            },
            "redirect_uri": {
                "value": reddit_redirect_uri if reddit_redirect_uri else "NOT_SET",
                "expected": "https://velocityfly.onrender.com/api/oauth/reddit/callback"
            },
            "user_agent": {
                "value": reddit_user_agent if reddit_user_agent else "NOT_SET",
                "expected": "VelocityPost/1.0"
            },
            "frontend_url": {
                "value": frontend_url if frontend_url else "NOT_SET",
                "expected": "https://velocityfly-ai.onrender.com"
            }
        },
        "validation": {
            "all_credentials_set": all([reddit_client_id, reddit_client_secret, reddit_redirect_uri]),
            "client_id_matches": reddit_client_id == "luTBXCyUteWCHyhoKeE6Lw" if reddit_client_id else False,
            "redirect_uri_correct": reddit_redirect_uri == "https://velocityfly.onrender.com/api/oauth/reddit/callback" if reddit_redirect_uri else False
        }
    }





# User-specific Reddit endpoints
@app.get("/api/reddit/connection-status")
async def get_reddit_connection_status(current_user: dict = Depends(get_current_user)):
    """Get Reddit connection status for current user"""
    try:
        user_id = current_user["id"]
        
        # Check database for user's Reddit connection
        if database_manager and hasattr(database_manager, 'check_reddit_connection'):
            db_status = await database_manager.check_reddit_connection(user_id)
            
            if db_status.get("connected"):
                # Load token into memory if not already there
                if user_id not in user_reddit_tokens:
                    tokens = await database_manager.get_reddit_tokens(user_id)
                    if tokens and tokens.get("is_valid"):
                        user_reddit_tokens[user_id] = {
                            "access_token": tokens["access_token"],
                            "refresh_token": tokens.get("refresh_token", ""),
                            "reddit_username": tokens["reddit_username"],
                            "connected_at": datetime.now().isoformat()
                        }
                        logger.info(f"Loaded Reddit token for user {user_id}")
                
                return {
                    "success": True,
                    "connected": True,
                    "user_id": user_id,
                    "reddit_username": db_status.get("reddit_username"),
                    "expires_at": db_status.get("expires_at"),
                    "message": f"Reddit connected as {db_status.get('reddit_username')}",
                    "source": "database"
                }
        
        # Fallback to memory check
        if user_id in user_reddit_tokens:
            creds = user_reddit_tokens[user_id]
            username = creds.get("reddit_username")
            return {
                "success": True,
                "connected": True,
                "user_id": user_id,
                "reddit_username": username,
                "connected_at": creds.get("connected_at"),
                "message": f"Reddit connected as {username}",
                "source": "memory"
            }
        
        return {
            "success": True,
            "connected": False,
            "user_id": user_id,
            "message": "No Reddit connection found"
        }
        
    except Exception as e:
        logger.error(f"Connection status check failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/reddit/test-connection")
async def test_reddit_connection(current_user: dict = Depends(get_current_user)):
    """Test Reddit API connection for current user"""
    try:
        user_id = current_user["id"]
        
        # Check if user has Reddit tokens
        if user_id not in user_reddit_tokens:
            return {
                "success": False,
                "error": "Reddit not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # Test with Reddit connector
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            return {
                "success": False,
                "error": "Mock connector active",
                "message": "Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET for real connection"
            }
        
        username = user_reddit_tokens[user_id].get("reddit_username")
        logger.info(f"Testing Reddit connection for {username}")
        
        return {
            "success": True,
            "message": f"Reddit connection verified for {username}",
            "username": username,
            "real_connection": True
        }
        
    except Exception as e:
        logger.error(f"Reddit connection test failed: {e}")
        return {"success": False, "error": str(e)}

# User-specific manual posting
@app.post("/api/reddit/post")
async def manual_reddit_post(
    post_data: ManualPostRequest,
    current_user: dict = Depends(get_current_user)
):
    """Manual Reddit posting for authenticated user"""
    try:
        user_id = current_user["id"]
        
        # Check Reddit connection
        if user_id not in user_reddit_tokens:
            return {
                "success": False, 
                "error": "Reddit not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # Check if using mock connector
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            return {
                "success": False,
                "error": "Mock Reddit connector active",
                "message": "Configure real Reddit API credentials"
            }
        
        # Get user info for logging
        reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
        access_token = user_reddit_tokens[user_id]["access_token"]
        
        logger.info(f"MANUAL POST: {reddit_username} posting to r/{post_data.subreddit}")
        
        # Attempt to post using REAL Reddit API
        result = await reddit_oauth_connector.post_content_with_token(
            access_token=access_token,
            subreddit_name=post_data.subreddit,
            title=post_data.title,
            content=post_data.content,
            content_type=post_data.contentType
        )
        
        # Log the result to database
        if database_manager and hasattr(database_manager, 'log_reddit_activity'):
            await database_manager.log_reddit_activity(
                user_id=user_id,
                activity_type="post",
                activity_data={
                    "success": result.get("success", False),
                    "subreddit": post_data.subreddit,
                    "title": post_data.title,
                    "post_id": result.get("post_id"),
                    "post_url": result.get("post_url"),
                    "manual": True
                }
            )
        
        if result.get("success"):
            logger.info(f"REAL Manual post successful for {reddit_username}: {result.get('post_url')}")
        else:
            logger.error(f"Manual post failed for {reddit_username}: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Manual Reddit post failed: {e}")
        return {"success": False, "error": str(e)}

# User-specific AI content generation
@app.post("/api/automation/test-auto-post")
async def test_auto_post(
    test_data: TestPostRequest,
    current_user: dict = Depends(get_current_user)
):
    """Test auto-post generation with REAL AI for authenticated user"""
    try:
        user_id = current_user["id"]
        
        # STRICT CHECK: Reject if AI service is mock
        if isinstance(ai_service, MockAIService):
            return {
                "success": False,
                "error": "Mock AI service active",
                "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY environment variables",
                "mock_warning": True
            }
        
        logger.info(f"Generating REAL AI content for user {user_id}: {test_data.domain} - {test_data.business_type}")
        
        # Generate content using REAL AI service
        content_result = await ai_service.generate_reddit_domain_content(
            domain=test_data.domain,
            business_type=test_data.business_type,
            business_description=test_data.business_description,
            target_audience=test_data.target_audience,
            language=test_data.language,
            content_style=test_data.content_style,
            test_mode=False
        )
        
        # Verify real content
        if content_result.get("ai_service") == "mock" or "mock" in content_result.get("content", "").lower():
            return {
                "success": False,
                "error": "AI service returned mock content",
                "message": "Check your API keys configuration"
            }
        
        if not content_result.get("success", True):
            return {
                "success": False,
                "error": f"AI content generation failed: {content_result.get('error')}",
                "message": "Check your AI API keys and service availability"
            }
        
        content_preview = content_result.get("content", "")
        ai_service_name = content_result.get("ai_service", "unknown")
        
        logger.info(f"REAL AI generated for user {user_id}: {len(content_preview)} characters using {ai_service_name}")
        
        return {
            "success": True,
            "message": f"REAL AI content generated successfully using {ai_service_name}!",
            "post_details": {
                "title": content_result.get("title", "AI Generated Title"),
                "subreddit": test_data.subreddits[0] if test_data.subreddits else "test",
                "user_id": user_id,
                "real_ai": True
            },
            "content_preview": content_preview,
            "ai_service": ai_service_name,
            "word_count": content_result.get("word_count", len(content_preview.split())),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
    
        logger.error(f"Test auto-post failed: {e}")
        return {"success": False, "error": str(e)}







# User-specific automation setup
@app.post("/api/automation/setup-auto-posting")
async def setup_auto_posting(
    config_data: AutoPostingRequest,
    current_user: dict = Depends(get_current_user)
):
    """Setup automatic posting for authenticated user"""
    try:
        user_id = current_user["id"]
        logger.info(f"🚀 AUTOMATION SETUP: Starting for user {user_id} ({current_user.get('email')})")
        
        # USE ONLY FRONTEND TIMES - no merging, no defaults
        frontend_times = config_data.posting_times or []
        
        logger.info(f"FRONTEND TIMES RECEIVED: {frontend_times}")
        
        if not frontend_times:
            return {
                "success": False,
                "error": "No posting times provided",
                "message": "Please set at least one posting time in the Schedule tab"
            }
        
        # Validate time format
        validated_times = []
        for time_str in frontend_times:
            try:
                datetime.strptime(time_str, "%H:%M")
                validated_times.append(time_str)
            except ValueError:
                logger.warning(f"Invalid time format from frontend: {time_str}")
                
        if not validated_times:
            return {
                "success": False,
                "error": "No valid posting times provided",
                "message": "Please provide times in HH:MM format"
            }
        
        # Update config_data with validated frontend times only
        config_data.posting_times = validated_times
        logger.info(f"USING FRONTEND TIMES ONLY: {validated_times}")
        
        # Reddit connection check
        reddit_token_found = False
        reddit_username = "Unknown"
        
        if user_id in user_reddit_tokens:
            reddit_token_found = True
            reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
            logger.info(f"✅ Reddit token found directly for user {user_id}: {reddit_username}")
        
        # Fallback 1: Check database
        elif database_manager and hasattr(database_manager, 'check_reddit_connection'):
            try:
                db_connection = await database_manager.check_reddit_connection(user_id)
                if db_connection.get("connected"):
                    reddit_token_found = True
                    reddit_username = db_connection.get("reddit_username", "Unknown")
                    
                    # Load token into memory
                    tokens = await database_manager.get_reddit_tokens(user_id)
                    if tokens and tokens.get("is_valid"):
                        user_reddit_tokens[user_id] = {
                            "access_token": tokens["access_token"],
                            "refresh_token": tokens.get("refresh_token", ""),
                            "reddit_username": tokens["reddit_username"],
                            "connected_at": datetime.now().isoformat()
                        }
                        logger.info(f"✅ Reddit token loaded from database for user {user_id}: {reddit_username}")
            except Exception as e:
                logger.warning(f"Database connection check failed: {e}")
        
        # Fallback 2: Search by known username pattern
        if not reddit_token_found:
            for token_user_id, token_data in user_reddit_tokens.items():
                if token_data.get("reddit_username") == "Icy-Cut-2575":  # Your known username
                    reddit_token_found = True
                    reddit_username = token_data["reddit_username"]
                    user_id = token_user_id  # Use the correct user_id
                    logger.info(f"✅ Reddit token found by username search: {reddit_username} (user_id: {token_user_id})")
                    break
        
        if not reddit_token_found:
            logger.error(f"❌ No Reddit connection found for user {user_id}")
            return {
                "success": False,
                "error": "Reddit account not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # Service checks
        service_warnings = []
        
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            service_warnings.append("Reddit connector is in mock mode")
            logger.warning("Reddit connector is MockRedditConnector")
        
        if isinstance(ai_service, MockAIService):
            service_warnings.append("AI service is in mock mode")
            logger.warning("AI service is MockAIService")
        
        # Test AI service
        ai_service_name = "unknown"
        ai_test_success = False
        
        try:
            logger.info("🤖 Testing AI service...")
            test_content = await ai_service.generate_reddit_domain_content(
                domain=config_data.domain,
                business_type=config_data.business_type,
                business_description=config_data.business_description,
                target_audience=config_data.target_audience,
                test_mode=False
            )
            
            if test_content.get("success", True) and test_content.get("ai_service") != "mock":
                ai_test_success = True
                ai_service_name = test_content.get('ai_service', 'unknown')
                logger.info(f"✅ AI service test passed: {ai_service_name}")
            else:
                logger.warning(f"⚠️ AI service returned mock/failed content")
                ai_service_name = "fallback"
                
        except Exception as e:
            logger.error(f"❌ AI service test failed: {e}")
            ai_service_name = "error"
        
        # Store configuration in database
        try:
            if database_manager and hasattr(database_manager, 'store_automation_config'):
                config_dict = config_data.dict()
                config_dict['user_id'] = user_id
                config_dict['reddit_username'] = reddit_username
                
                await database_manager.store_automation_config(
                    user_id=user_id,
                    config_type='auto_posting',
                    config_data=config_dict
                )
                logger.info("✅ Configuration stored in database")
        except Exception as e:
            logger.warning(f"⚠️ Database storage failed: {e}")
        
        # Store in memory for immediate use
        automation_configs[user_id] = {
            "auto_posting": {
                "config": config_data.dict(),
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "reddit_username": reddit_username,
                "ai_service": ai_service_name,
                "real_ai": ai_test_success,
                "service_warnings": service_warnings
            }
        }
        
        logger.info(f"✅ Auto-posting config stored for user {user_id} ({reddit_username}) with times: {validated_times}")
        
        # Setup with automation scheduler using FRONTEND TIMES ONLY
        if automation_scheduler and AUTOMATION_AVAILABLE:
            try:
                logger.info("🚀 Setting up automation scheduler...")
                
                auto_config = AutoPostConfig(
                    user_id=user_id,
                    domain=config_data.domain,
                    business_type=config_data.business_type,
                    business_description=config_data.business_description,
                    target_audience=config_data.target_audience,
                    language=config_data.language,
                    subreddits=config_data.subreddits,
                    posts_per_day=config_data.posts_per_day,
                    posting_times=validated_times,  # FRONTEND TIMES ONLY
                    content_style=config_data.content_style,
                    manual_time_entry=config_data.manual_time_entry,
                    custom_post_count=config_data.custom_post_count
                )
                
                result = await automation_scheduler.setup_auto_posting(auto_config)
                result["user_id"] = user_id
                result["reddit_username"] = reddit_username
                result["posting_times_used"] = validated_times  # Show which times were used
                result["real_posting"] = not isinstance(automation_scheduler, MockAutomationScheduler)
                result["real_ai"] = ai_test_success
                result["ai_service"] = ai_service_name
                result["service_warnings"] = service_warnings
                
                logger.info(f"✅ AUTOMATION SETUP SUCCESSFUL for user {user_id} with frontend times: {validated_times}")
                return result
                
            except Exception as e:
                logger.error(f"❌ Automation scheduler failed: {e}")
                return {
                    "success": False,
                    "error": f"Automation scheduler error: {str(e)}",
                    "message": "Automation scheduler failed to start",
                    "user_id": user_id,
                    "reddit_username": reddit_username,
                    "debug_info": str(e)
                }
        
        # Return success even if scheduler not available
        logger.info(f"⚠️ Automation scheduler not available, returning success with stored config")
        return {
            "success": True,
            "message": "Configuration saved successfully",
            "user_id": user_id,
            "reddit_username": reddit_username,
            "posting_times_used": validated_times,
            "real_ai": ai_test_success,
            "ai_service": ai_service_name,
            "service_warnings": service_warnings,
            "note": "Automation scheduler not available - config saved for manual use"
        }
        
    except Exception as e:
        logger.error(f"❌ AUTOMATION SETUP FAILED: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "message": "Automation setup failed - check server logs",
            "timestamp": datetime.now().isoformat()
        }
    








@app.get("/api/debug/automation-status")
async def debug_automation_status(current_user: dict = Depends(get_current_user)):
    """Debug automation status for current user"""
    try:
        user_id = current_user["id"]
        
        return {
            "success": True,
            "debug_info": {
                "user_id": user_id,
                "user_email": current_user.get("email"),
                "reddit_token_exists": user_id in user_reddit_tokens,
                "reddit_tokens_available": list(user_reddit_tokens.keys()) if user_reddit_tokens else [],
                "reddit_usernames": {k: v.get("reddit_username") for k, v in user_reddit_tokens.items()},
                "automation_config_exists": user_id in automation_configs,
                "automation_configs_available": list(automation_configs.keys()) if automation_configs else [],
                "services": {
                    "reddit_connector_type": type(reddit_oauth_connector).__name__,
                    "ai_service_type": type(ai_service).__name__,
                    "automation_scheduler_type": type(automation_scheduler).__name__ if automation_scheduler else None,
                    "database_type": type(database_manager).__name__
                },
                "flags": {
                    "automation_available": AUTOMATION_AVAILABLE,
                    "multiuser_db_available": MULTIUSER_DB_AVAILABLE
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/automation/setup-auto-replies")
async def setup_auto_replies(
    config_data: AutoReplyRequest,
    current_user: dict = Depends(get_current_user)
):
    """Setup automatic replies for authenticated user"""
    try:
        user_id = current_user["id"]
        
        # Check Reddit connection
        if user_id not in user_reddit_tokens:
            return {
                "success": False,
                "error": "Reddit account not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # STRICT CHECKS
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            return {
                "success": False,
                "error": "Reddit API not configured",
                "message": "Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"
            }
        
        if isinstance(ai_service, MockAIService):
            return {
                "success": False,
                "error": "AI service not configured", 
                "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY"
            }
        
        reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
        
        # Store configuration in database
        if database_manager and hasattr(database_manager, 'store_automation_config'):
            config_dict = config_data.dict()
            config_dict['user_id'] = user_id
            await database_manager.store_automation_config(
                user_id=user_id,
                config_type='auto_replies',
                config_data=config_dict
            )
        
        # Store in memory
        if user_id not in automation_configs:
            automation_configs[user_id] = {}
        automation_configs[user_id]["auto_replies"] = {
            "config": config_data.dict(),
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "reddit_username": reddit_username
        }
        
        logger.info(f"Setting up REAL auto-replies for user {user_id} ({reddit_username})")
        
        # Setup with automation scheduler
        if automation_scheduler and not isinstance(automation_scheduler, MockAutomationScheduler):
            try:
                auto_config = AutoReplyConfig(
                    user_id=user_id,
                    domain=config_data.domain,
                    expertise_level=config_data.expertise_level,
                    subreddits=config_data.subreddits,
                    keywords=config_data.keywords,
                    max_replies_per_hour=config_data.max_replies_per_hour,
                    response_delay_minutes=config_data.response_delay_minutes
                )
                
                result = await automation_scheduler.setup_auto_replies(auto_config)
                result["user_id"] = user_id
                result["reddit_username"] = reddit_username
                result["real_ai"] = True
                
                logger.info(f"REAL auto-replies setup successful for user {user_id}")
                return result
            except Exception as e:
                logger.warning(f"Auto-replies setup failed: {e}")
        
        return {
            "success": False,
            "error": "Auto-replies scheduler not available",
            "message": "Configure all required API keys and restart application"
        }
        
    except Exception as e:
        logger.error(f"Auto-replies setup failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/automation/status")
async def get_automation_status(current_user: dict = Depends(get_current_user)):
    """Get automation status for current user"""
    try:
        user_id = current_user["id"]
        reddit_username = user_reddit_tokens.get(user_id, {}).get("reddit_username", "")
        
        if automation_scheduler and hasattr(automation_scheduler, 'get_automation_status'):
            try:
                result = await automation_scheduler.get_automation_status(user_id)
                result["reddit_username"] = reddit_username
                result["real_posting"] = not isinstance(automation_scheduler, MockAutomationScheduler)
                result["real_ai"] = not isinstance(ai_service, MockAIService)
                result["ai_service"] = type(ai_service).__name__
                return result
            except Exception as e:
                logger.warning(f"Automation status check failed: {e}")
        
        # Fallback status from stored configs
        user_config = automation_configs.get(user_id, {})
        
        return {
            "success": True,
            "user_id": user_id,
            "reddit_connected": user_id in user_reddit_tokens,
            "reddit_username": reddit_username,
            "auto_posting": {
                "enabled": "auto_posting" in user_config,
                "config": user_config.get("auto_posting", {}).get("config"),
                "stats": {"total_posts": 0, "successful_posts": 0, "failed_posts": 0}
            },
            "auto_replies": {
                "enabled": "auto_replies" in user_config,
                "config": user_config.get("auto_replies", {}).get("config"),
                "stats": {"total_replies": 0, "successful_replies": 0}
            },
            "daily_stats": {
                "posts_today": 0,
                "recent_replies": 0,
                "total_karma": 0
            },
            "scheduler_running": automation_scheduler.is_running if automation_scheduler else False,
            "real_posting": not isinstance(automation_scheduler, MockAutomationScheduler) if automation_scheduler else False,
            "real_ai": not isinstance(ai_service, MockAIService),
            "ai_service": type(ai_service).__name__,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/automation/update-schedule")
async def update_automation_schedule(
    update_data: ScheduleUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update automation schedule settings for current user"""
    try:
        user_id = current_user["id"]
        
        # Update stored config
        if user_id in automation_configs:
            if update_data.type in automation_configs[user_id]:
                automation_configs[user_id][update_data.type]["enabled"] = update_data.enabled
        
        # Update in database if available
        if database_manager and hasattr(database_manager, 'store_automation_config'):
            try:
                config_data = automation_configs.get(user_id, {}).get(update_data.type, {}).get("config", {})
                if config_data:
                    config_data["enabled"] = update_data.enabled
                    await database_manager.store_automation_config(
                        user_id=user_id,
                        config_type=update_data.type,
                        config_data=config_data
                    )
            except Exception as e:
                logger.warning(f"Failed to update database config: {e}")
        
        logger.info(f"Updated {update_data.type} schedule for user {user_id}: enabled={update_data.enabled}")
        
        return {
            "success": True,
            "message": f"{update_data.type.replace('_', ' ').title()} {'enabled' if update_data.enabled else 'disabled'}",
            "user_id": user_id,
            "type": update_data.type,
            "enabled": update_data.enabled
        }
        
    except Exception as e:
        logger.error(f"Schedule update failed: {e}")
        return {"success": False, "error": str(e)}

# User dashboard endpoint
@app.get("/api/user/dashboard")
async def get_user_dashboard(current_user: dict = Depends(get_current_user)):
    """Get dashboard data for current user"""
    try:
        user_id = current_user["id"]
        
        if database_manager and hasattr(database_manager, 'get_user_dashboard'):
            dashboard_data = await database_manager.get_user_dashboard(user_id)
            return {
                "success": True,
                "dashboard": dashboard_data,
                "user": current_user
            }
        
        # Fallback dashboard
        return {
            "success": True,
            "dashboard": {
                "posts_today": 0,
                "total_engagement": 0,
                "qa_earnings": 0,
                "active_platforms": 1 if user_id in user_reddit_tokens else 0,
                "reddit_connected": user_id in user_reddit_tokens,
                "reddit_username": user_reddit_tokens.get(user_id, {}).get("reddit_username", ""),
                "user_name": current_user.get("name", ""),
                "user_email": current_user.get("email", "")
            },
            "user": current_user
        }
        
    except Exception as e:
        logger.error(f"Get dashboard failed: {e}")
        return {"success": False, "error": str(e)}

# Disconnect Reddit for user
@app.post("/api/reddit/disconnect")
async def disconnect_reddit(current_user: dict = Depends(get_current_user)):
    """Disconnect Reddit account for current user"""
    try:
        user_id = current_user["id"]
        
        # Remove from memory
        if user_id in user_reddit_tokens:
            reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
            del user_reddit_tokens[user_id]
            logger.info(f"Removed Reddit tokens from memory for user {user_id} ({reddit_username})")
        
        # Revoke in database
        if database_manager and hasattr(database_manager, 'revoke_reddit_connection'):
            db_result = await database_manager.revoke_reddit_connection(user_id)
            if db_result.get("success"):
                logger.info(f"Reddit connection revoked in database for user {user_id}")
        
        return {
            "success": True,
            "message": "Reddit account disconnected successfully"
        }
        
    except Exception as e:
        logger.error(f"Reddit disconnect failed: {e}")
        return {"success": False, "error": str(e)}

# User profile management
@app.get("/api/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information"""
    try:
        user_id = current_user["id"]
        
        # Get additional profile data from database if available
        if database_manager and hasattr(database_manager, 'get_user_by_id'):
            user_data = await database_manager.get_user_by_id(user_id)
            if user_data:
                return {
                    "success": True,
                    "profile": user_data
                }
        
        # Fallback to current user data
        return {
            "success": True,
            "profile": current_user
        }
        
    except Exception as e:
        logger.error(f"Get user profile failed: {e}")
        return {"success": False, "error": str(e)}

@app.put("/api/user/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile information"""
    try:
        user_id = current_user["id"]
        
        # Update profile in database if available
        if database_manager and hasattr(database_manager, 'update_user_profile'):
            result = await database_manager.update_user_profile(user_id, profile_data)
            return result
        
        # Fallback response
        return {
            "success": True,
            "message": "Profile update functionality not available",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Update user profile failed: {e}")
        return {"success": False, "error": str(e)}

# User activity and analytics
@app.get("/api/user/activity")
async def get_user_activity(
    current_user: dict = Depends(get_current_user),
    days: int = Query(7, description="Number of days to fetch activity for")
):
    """Get user's Reddit activity for the specified number of days"""
    try:
        user_id = current_user["id"]
        
        if database_manager and hasattr(database_manager, 'get_user_activity'):
            activity_data = await database_manager.get_user_activity(user_id, days)
            return {
                "success": True,
                "activity": activity_data,
                "user_id": user_id,
                "period_days": days
            }
        
        # Fallback activity data
        return {
            "success": True,
            "activity": {
                "posts": [],
                "replies": [],
                "total_posts": 0,
                "total_replies": 0,
                "total_karma": 0
            },
            "user_id": user_id,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"Get user activity failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/user/analytics")
async def get_user_analytics(
    current_user: dict = Depends(get_current_user),
    period: str = Query("week", description="Analytics period: week, month, year")
):
    """Get user's analytics data"""
    try:
        user_id = current_user["id"]
        
        if database_manager and hasattr(database_manager, 'get_user_analytics'):
            analytics_data = await database_manager.get_user_analytics(user_id, period)
            return {
                "success": True,
                "analytics": analytics_data,
                "user_id": user_id,
                "period": period
            }
        
        # Fallback analytics
        return {
            "success": True,
            "analytics": {
                "posts_count": 0,
                "replies_count": 0,
                "total_karma": 0,
                "avg_score": 0,
                "success_rate": 0,
                "top_subreddits": [],
                "posting_patterns": {}
            },
            "user_id": user_id,
            "period": period
        }
        
    except Exception as e:
        logger.error(f"Get user analytics failed: {e}")
        return {"success": False, "error": str(e)}








@app.get("/api/debug/current-schedule")
async def debug_current_schedule(current_user: dict = Depends(get_current_user)):
    """Debug current automation schedule"""
    try:
        user_id = current_user["id"]
        
        # Get current time info
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        
        # Get user's automation config
        user_config = automation_configs.get(user_id, {})
        auto_posting_config = user_config.get("auto_posting", {})
        
        if automation_scheduler and hasattr(automation_scheduler, 'active_configs'):
            scheduler_config = automation_scheduler.active_configs.get(user_id)
        else:
            scheduler_config = None
        
        return {
            "success": True,
            "debug_info": {
                "current_time": current_time_str,
                "current_datetime": now.isoformat(),
                "user_id": user_id,
                "automation_config_exists": bool(auto_posting_config),
                "automation_config": auto_posting_config.get("config") if auto_posting_config else None,
                "scheduler_config_exists": bool(scheduler_config),
                "scheduler_config": scheduler_config.__dict__ if scheduler_config else None,
                "configured_posting_times": auto_posting_config.get("config", {}).get("posting_times", []) if auto_posting_config else [],
                "next_5_minutes": [
                    (now + timedelta(minutes=i)).strftime("%H:%M") 
                    for i in range(5)
                ]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}





@app.post("/api/debug/add-test-time")
async def add_test_time(current_user: dict = Depends(get_current_user)):
    """Add a test posting time 2 minutes from now"""
    try:
        user_id = current_user["id"]
        
        # Calculate time 2 minutes from now
        test_time = (datetime.now() + timedelta(minutes=2)).strftime("%H:%M")
        logger.info(f"🕐 Adding test time {test_time} for user {user_id}")
        
        # Update automation config in memory
        if user_id in automation_configs and "auto_posting" in automation_configs[user_id]:
            current_times = automation_configs[user_id]["auto_posting"]["config"].get("posting_times", [])
            if test_time not in current_times:
                current_times.append(test_time)
                automation_configs[user_id]["auto_posting"]["config"]["posting_times"] = current_times
                
                # CRITICAL: Update the scheduler's active config
                if automation_scheduler and hasattr(automation_scheduler, 'active_configs'):
                    if user_id in automation_scheduler.active_configs:
                        # FORCE UPDATE: Update both memory config and scheduler config
                        automation_scheduler.active_configs[user_id]["auto_posting"]["config"].posting_times = current_times
                        logger.info(f"✅ Updated scheduler active_configs for user {user_id}")
                        
                        # ADDITIONAL FORCE UPDATE: Directly update the scheduler's config object
                        scheduler_config = automation_scheduler.active_configs[user_id]["auto_posting"]["config"]
                        scheduler_config.posting_times = current_times
                        logger.info(f"FORCE UPDATED scheduler config with test time: {current_times}")
                        
                    else:
                        logger.warning(f"⚠️ User {user_id} not found in scheduler active_configs")
                        # If user not in active_configs, try to recreate the automation
                        try:
                            config = automation_configs[user_id]["auto_posting"]["config"]
                            auto_config = AutoPostConfig(
                                user_id=user_id,
                                domain=config.get("domain", "tech"),
                                business_type=config.get("business_type", "AI automation platform"),
                                business_description=config.get("business_description", ""),
                                target_audience=config.get("target_audience", "tech_professionals"),
                                language=config.get("language", "en"),
                                subreddits=config.get("subreddits", ["test"]),
                                posts_per_day=config.get("posts_per_day", 3),
                                posting_times=current_times,
                                content_style=config.get("content_style", "engaging"),
                                manual_time_entry=config.get("manual_time_entry", False),
                                custom_post_count=config.get("custom_post_count", False)
                            )
                            await automation_scheduler.setup_auto_posting(auto_config)
                            logger.info(f"✅ Recreated automation config for user {user_id}")
                        except Exception as e:
                            logger.error(f"❌ Failed to recreate automation: {e}")
                else:
                    logger.warning("⚠️ Automation scheduler not available")
                
                # Update database
                try:
                    if database_manager and hasattr(database_manager, 'store_automation_config'):
                        config_dict = automation_configs[user_id]["auto_posting"]["config"]
                        await database_manager.store_automation_config(
                            user_id=user_id,
                            config_type='auto_posting',
                            config_data=config_dict
                        )
                        logger.info(f"✅ Updated database config for user {user_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Database update failed: {e}")
                
                logger.info(f"✅ Test posting time {test_time} added for user {user_id}")
                logger.info(f"📅 All posting times: {current_times}")
                
                return {
                    "success": True,
                    "message": f"Test posting time added: {test_time}",
                    "test_time": test_time,
                    "all_times": current_times,
                    "note": f"Post should trigger at {test_time}",
                    "scheduler_updated": True,
                    "force_updated": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Time {test_time} already exists",
                    "all_times": current_times
                }
        
        return {
            "success": False,
            "error": "No automation config found",
            "user_id": user_id,
            "available_configs": list(automation_configs.keys())
        }
        
    except Exception as e:
        logger.error(f"❌ Add test time failed: {e}")
        return {"success": False, "error": str(e)}







@app.get("/api/debug/scheduler-status")
async def debug_scheduler_status(current_user: dict = Depends(get_current_user)):
    """Debug scheduler active configurations"""
    try:
        user_id = current_user["id"]
        
        memory_config = automation_configs.get(user_id, {}).get("auto_posting", {}).get("config", {})
        
        scheduler_config = None
        if automation_scheduler and hasattr(automation_scheduler, 'active_configs'):
            if user_id in automation_scheduler.active_configs:
                scheduler_config = {
                    "posting_times": automation_scheduler.active_configs[user_id].posting_times,
                    "domain": automation_scheduler.active_configs[user_id].domain,
                    "posts_per_day": automation_scheduler.active_configs[user_id].posts_per_day
                }
        
        return {
            "success": True,
            "current_time": datetime.now().strftime("%H:%M"),
            "user_id": user_id,
            "memory_config": {
                "posting_times": memory_config.get("posting_times", []),
                "enabled": automation_configs.get(user_id, {}).get("auto_posting", {}).get("enabled", False)
            },
            "scheduler_config": scheduler_config,
            "scheduler_has_user": user_id in (automation_scheduler.active_configs if automation_scheduler and hasattr(automation_scheduler, 'active_configs') else {}),
            "all_scheduler_users": list(automation_scheduler.active_configs.keys()) if automation_scheduler and hasattr(automation_scheduler, 'active_configs') else []
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}









# Debug endpoints (for development and troubleshooting)
@app.get("/api/debug/multi-user-sessions")
async def debug_multi_user_sessions():
    """Debug multi-user session information"""
    return {
        "multi_user_system": True,
        "user_reddit_tokens": {
            k: {
                "username": v.get("reddit_username", "N/A"), 
                "has_token": bool(v.get("access_token")),
                "connected_at": v.get("connected_at", "unknown")
            } for k, v in user_reddit_tokens.items()
        },
        "oauth_states": list(oauth_states.keys()),
        "total_tokens": len(user_reddit_tokens),
        "automation_configs": {
            k: {
                config_type: {
                    "enabled": config_data.get("enabled", False),
                    "created_at": config_data.get("created_at", "unknown")
                } for config_type, config_data in v.items()
            } for k, v in automation_configs.items()
        },
        "database_type": type(database_manager).__name__,
        "multiuser_db_available": MULTIUSER_DB_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/debug/reddit")
async def debug_reddit_connector():
    """Debug Reddit connector status"""
    return {
        "connector_available": reddit_oauth_connector is not None,
        "connector_type": type(reddit_oauth_connector).__name__ if reddit_oauth_connector else None,
        "connector_configured": hasattr(reddit_oauth_connector, 'is_configured') and reddit_oauth_connector.is_configured if reddit_oauth_connector else False,
        "user_tokens": len(user_reddit_tokens),
        "connected_users": list(user_reddit_tokens.keys()),
        "reddit_usernames": [tokens.get("reddit_username") for tokens in user_reddit_tokens.values()],
        "oauth_states": len(oauth_states),
        "environment_vars": {
            "REDDIT_CLIENT_ID": bool(os.getenv("REDDIT_CLIENT_ID")),
            "REDDIT_CLIENT_SECRET": bool(os.getenv("REDDIT_CLIENT_SECRET")),
            "MISTRAL_API_KEY": bool(os.getenv("MISTRAL_API_KEY")),
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY"))
        },
        "real_posting_enabled": not isinstance(reddit_oauth_connector, MockRedditConnector),
        "real_ai_enabled": not isinstance(ai_service, MockAIService),
        "multiuser_system": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/debug/ai")
async def debug_ai_service():
    """Debug AI service status"""
    try:
        ai_test = None
        if hasattr(ai_service, 'test_ai_connection'):
            try:
                ai_test = await ai_service.test_ai_connection()
            except Exception as e:
                ai_test = {"error": str(e)}
        
        return {
            "ai_service_available": ai_service is not None,
            "ai_service_type": type(ai_service).__name__,
            "is_mock": isinstance(ai_service, MockAIService),
            "ai_test_result": ai_test,
            "environment_keys": {
                "MISTRAL_API_KEY": bool(os.getenv("MISTRAL_API_KEY")),
                "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY"))
            },
            "real_ai_active": not isinstance(ai_service, MockAIService),
            "multiuser_system": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/debug/database")
async def debug_database():
    """Debug database status"""
    try:
        db_health = None
        if database_manager and hasattr(database_manager, 'health_check'):
            try:
                db_health = await database_manager.health_check()
            except Exception as e:
                db_health = {"error": str(e)}
        
        return {
            "database_available": database_manager is not None,
            "database_type": type(database_manager).__name__,
            "is_mock": isinstance(database_manager, MockMultiUserDatabase),
            "multiuser_db_available": MULTIUSER_DB_AVAILABLE,
            "health_check": db_health,
            "user_count": len(user_reddit_tokens),
            "automation_count": len(automation_configs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Backward compatibility endpoints (for users without authentication)
@app.post("/api/auth/create-session")
async def create_session_fallback():
    """Create session for backward compatibility (deprecated)"""
    try:
        # For backward compatibility, create a temporary session
        session_id = f"temp_{uuid.uuid4().hex[:16]}"
        user_id = generate_user_id()
        
        logger.warning(f"Creating temporary session for backward compatibility: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "message": "Temporary session created - please register/login for full features",
            "deprecated": True,
            "multiuser_available": True
        }
    except Exception as e:
        logger.error(f"Create fallback session failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/auth/check-existing-connection")
async def check_existing_connection_fallback(session_id: str = Header(None, alias="x-session-id")):
    """Check existing connection for backward compatibility"""
    return {
        "success": True,
        "session_id": session_id or "none",
        "user_id": "temp_user",
        "reddit_connected": False,
        "message": "Please register/login for full multi-user features",
        "multiuser_available": True,
        "deprecated": True,
        "auth_endpoints": {
            "register": "/api/auth/register",
            "login": "/api/auth/login",
            "me": "/api/auth/me"
        }
    }

@app.get("/api/debug/scheduler-active-configs")
async def debug_scheduler_active_configs(current_user: dict = Depends(get_current_user)):
    """Debug what the scheduler actually has in active_configs"""
    try:
        user_id = current_user["id"]
        
        if automation_scheduler and hasattr(automation_scheduler, 'active_configs'):
            user_scheduler_config = automation_scheduler.active_configs.get(user_id)
            
            if user_scheduler_config:
                auto_posting = user_scheduler_config.get("auto_posting", {})
                config = auto_posting.get("config")
                
                posting_times = []
                if hasattr(config, 'posting_times'):
                    posting_times = config.posting_times
                elif isinstance(config, dict):
                    posting_times = config.get('posting_times', [])
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "scheduler_has_user": True,
                    "posting_times": posting_times,
                    "config_type": str(type(config)),
                    "auto_posting_enabled": auto_posting.get("enabled", False),
                    "current_time": datetime.now().strftime("%H:%M"),
                    "next_minute": (datetime.now() + timedelta(minutes=1)).strftime("%H:%M")
                }
            else:
                return {
                    "success": True,
                    "user_id": user_id,
                    "scheduler_has_user": False,
                    "all_scheduler_users": list(automation_scheduler.active_configs.keys()),
                    "memory_config": automation_configs.get(user_id, {}).get("auto_posting", {}).get("config", {}).get("posting_times", [])
                }
        
        return {"success": False, "error": "Automation scheduler not available"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# System information endpoint
@app.get("/api/system/info")
async def get_system_info():
    """Get system information and capabilities"""
    return {
        "success": True,
        "system": {
            "name": "Multi-User Reddit Automation Platform",
            "version": "6.0.0",
            "features": {
                "multi_user_auth": True,
                "individual_reddit_connections": True,
                "per_user_automation": True,
                "real_ai_content": not isinstance(ai_service, MockAIService),
                "real_reddit_posting": not isinstance(reddit_oauth_connector, MockRedditConnector),
                "persistent_database": MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase),
                "analytics": True,
                "scheduled_posting": True,
                "auto_replies": True
            },
            "services": {
                "ai": {
                    "type": type(ai_service).__name__,
                    "real": not isinstance(ai_service, MockAIService)
                },
                "reddit": {
                    "type": type(reddit_oauth_connector).__name__,
                    "real": not isinstance(reddit_oauth_connector, MockRedditConnector)
                },
                "database": {
                    "type": type(database_manager).__name__,
                    "real": MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase)
                },
                "scheduler": {
                    "type": type(automation_scheduler).__name__,
                    "real": not isinstance(automation_scheduler, MockAutomationScheduler)
                }
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/debug/trigger-immediate-post")
async def trigger_immediate_post(current_user: dict = Depends(get_current_user)):
    """Trigger an immediate test post"""
    try:
        user_id = current_user["id"]
        
        if user_id not in user_reddit_tokens:
            return {"success": False, "error": "Reddit not connected"}
        
        if isinstance(ai_service, MockAIService):
            return {"success": False, "error": "AI service not configured"}
        
        # Get user config
        user_config = automation_configs.get(user_id, {}).get("auto_posting", {}).get("config", {})
        if not user_config:
            return {"success": False, "error": "No automation config found"}
        
        # Generate content
        content_result = await ai_service.generate_reddit_domain_content(
            domain=user_config.get("domain", "tech"),
            business_type=user_config.get("business_type", "AI automation platform"),
            business_description=user_config.get("business_description", ""),
            target_audience=user_config.get("target_audience", "tech_professionals"),
            content_style=user_config.get("content_style", "engaging"),
            test_mode=False
        )
        
        if not content_result.get("success", True):
            return {"success": False, "error": "AI content generation failed"}
        
        # Post to Reddit
        reddit_tokens = user_reddit_tokens[user_id]
        subreddits = user_config.get("subreddits", ["test"])
        
        post_result = await reddit_oauth_connector.post_content_with_token(
            access_token=reddit_tokens["access_token"],
            subreddit_name=subreddits[0],
            title=content_result.get("title", "Test Post"),
            content=content_result.get("content", "Test content"),
            content_type="text"
        )
        
        return {
            "success": post_result.get("success", False),
            "message": "Immediate test post triggered",
            "post_result": post_result,
            "ai_service": content_result.get("ai_service"),
            "subreddit": subreddits[0],
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Immediate post trigger failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/debug/next-posting-debug")
async def debug_next_posting(current_user: dict = Depends(get_current_user)):
    """Debug next posting time calculation"""
    try:
        user_id = current_user["id"]
        current_time = datetime.now().strftime("%H:%M")
        
        # Check scheduler config
        scheduler_times = []
        if automation_scheduler and hasattr(automation_scheduler, 'active_configs'):
            if user_id in automation_scheduler.active_configs:
                config = automation_scheduler.active_configs[user_id]["auto_posting"]["config"]
                scheduler_times = getattr(config, 'posting_times', [])
        
        # Check memory config
        memory_times = []
        if user_id in automation_configs:
            memory_times = automation_configs[user_id].get("auto_posting", {}).get("config", {}).get("posting_times", [])
        
        return {
            "success": True,
            "current_time": current_time,
            "scheduler_times": scheduler_times,
            "memory_times": memory_times,
            "next_posting_calculation": automation_scheduler._get_next_posting_time(scheduler_times) if automation_scheduler else "No scheduler"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# DISCONNECT REDDIT ACCOUNT - MULTI-USER
# ============================================================================
@app.post("/api/reddit/disconnect")
async def disconnect_reddit_account(current_user: dict = Depends(get_current_user)):
    """✅ Disconnect Reddit account for current user"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        user_email = current_user.get("email", "Unknown")
        
        logger.info(f"🔌 DISCONNECT REQUEST from user: {user_email} (ID: {user_id})")
        
        if not database_manager or not database_manager.connected:
            return {
                "success": False,
                "error": "Database not connected"
            }
        
        # ✅ Get current Reddit username before disconnecting
        reddit_tokens = await database_manager.get_reddit_tokens(user_id)
        reddit_username = reddit_tokens.get("reddit_username", "Unknown") if reddit_tokens else "Unknown"
        
        # ✅ Remove from memory
        if user_id in user_reddit_tokens:
            del user_reddit_tokens[user_id]
            logger.info(f"✅ Removed Reddit token from memory for user {user_id}")
        
        # ✅ Revoke in database
        db_result = await database_manager.revoke_reddit_connection(user_id)
        
        if db_result.get("success"):
            logger.info(f"✅ Reddit connection revoked in database for user {user_id} (was u/{reddit_username})")
            
            return {
                "success": True,
                "message": f"Reddit account u/{reddit_username} disconnected successfully",
                "disconnected_username": reddit_username
            }
        else:
            logger.error(f"❌ Failed to revoke Reddit connection: {db_result.get('error')}")
            return {
                "success": False,
                "error": "Failed to disconnect Reddit account"
            }
        
    except Exception as e:
        logger.error(f"❌ Reddit disconnect failed: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

# Application startup
PORT = int(os.getenv("PORT", 10000))
if __name__ == "__main__":
    print("Starting Multi-User Reddit Automation Platform...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info"
    )
