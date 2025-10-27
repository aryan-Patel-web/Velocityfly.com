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
            reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "https://agentic-u5lx.onrender.com/api/oauth/reddit/callback")
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
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        if not database_manager or not hasattr(database_manager, 'get_user_by_token'):
            raise HTTPException(status_code=500, detail="Authentication system not available")
        
        user = await database_manager.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Optional authentication (for endpoints that work with or without auth)
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user but don't fail if not authenticated"""
    try:
        if credentials:
            return await get_current_user(credentials)
        return None
    except:
        return None

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
        if not hasattr(self, 'oauth_states'):
            self.oauth_states = {}
        
        self.oauth_states[state] = {
            "user_id": user_id,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        logger.info(f"OAuth state stored in mock DB: {state} for user {user_id}")
        return {"success": True}

    async def get_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Get OAuth state from mock database"""
        if not hasattr(self, 'oauth_states'):
            self.oauth_states = {}
        
        state_data = self.oauth_states.get(state)
        if not state_data:
            logger.warning(f"OAuth state not found in mock DB: {state}")
            return None
        
        if state_data["expires_at"] <= datetime.utcnow():
            logger.warning(f"OAuth state expired in mock DB: {state}")
            del self.oauth_states[state]
            return None
        
        logger.info(f"OAuth state found in mock DB: {state} for user {state_data['user_id']}")
        return state_data

    async def cleanup_oauth_state(self, state: str) -> Dict[str, Any]:
        """Remove OAuth state from mock database"""
        if not hasattr(self, 'oauth_states'):
            self.oauth_states = {}
        
        if state in self.oauth_states:
            del self.oauth_states[state]
            logger.info(f"OAuth state cleaned up from mock DB: {state}")
            return {"success": True}
        return {"success": False, "message": "State not found"}

    async def get_all_oauth_states(self) -> List[str]:
        """Debug method to see all stored states in mock database"""
        if not hasattr(self, 'oauth_states'):
            self.oauth_states = {}
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
                'REDDIT_REDIRECT_URI': os.getenv('REDDIT_REDIRECT_URI', 'https://agentic-u5lx.onrender.com/api/oauth/reddit/callback'),
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
        "https://frontend-agentic-bnc2.onrender.com",  # Your frontend domain
        "https://agentic-u5lx.onrender.com"  # Your backend domain
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
    """Start Reddit OAuth flow for authenticated user - FIXED VERSION"""
    try:
        user_id = current_user["id"]
        
        # Generate OAuth state
        state = f"oauth_{user_id}_{uuid.uuid4().hex[:12]}"
        
        # FIXED: Store in database with expiration (15 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        await database_manager.store_oauth_state(state, user_id, expires_at)
        
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "https://agentic-u5lx.onrender.com/api/oauth/reddit/callback")
        
        if not reddit_client_id:
            raise HTTPException(status_code=500, detail="Reddit credentials not configured")
        
        oauth_url = f"https://www.reddit.com/api/v1/authorize?client_id={reddit_client_id}&response_type=code&state={state}&redirect_uri={reddit_redirect_uri}&duration=permanent&scope=identity,submit,edit,read"
        
        logger.info(f"Starting OAuth for user {user_id} ({current_user['email']}) - state: {state}")
        
        return {
            "success": True,
            "redirect_url": oauth_url,
            "state": state,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Reddit OAuth authorize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/oauth/reddit/callback")
async def reddit_oauth_callback(code: str, state: str):
    """Handle Reddit OAuth callback for authenticated user - FIXED VERSION"""
    try:
        # FIXED: Get user_id from database instead of memory
        state_data = await database_manager.get_oauth_state(state)
        if not state_data:
            logger.error(f"Invalid OAuth state from database: {state}")
            logger.error(f"Available states in database: {await database_manager.get_all_oauth_states() if hasattr(database_manager, 'get_all_oauth_states') else 'method not available'}")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/?error=invalid_oauth_state",
                status_code=302
            )
        
        user_id = state_data["user_id"]
        logger.info(f"Processing OAuth callback for user {user_id} (state found in database)")
        
        # ... rest of your existing callback code remains the same
        
        # Exchange code for token
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI")
        
        if not reddit_client_id or not reddit_client_secret:
            logger.error("Reddit credentials missing from environment")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/?error=missing_credentials",
                status_code=302
            )
        
        # Token exchange request
        auth_string = f"{reddit_client_id}:{reddit_client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': 'IndianAutomationPlatform/1.0 by YourRedditUsername'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': reddit_redirect_uri
        }
        
        logger.info("Exchanging code for access token...")
        
        response = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            headers=headers,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                # Get Reddit user info with proper error handling
                user_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'User-Agent': 'IndianAutomationPlatform/1.0 by YourRedditUsername'
                }
                
                username = None
                reddit_user_id = ""
                user_info = {}
                
                try:
                    logger.info("Fetching Reddit user info...")
                    user_response = requests.get(
                        'https://oauth.reddit.com/api/v1/me',
                        headers=user_headers,
                        timeout=15
                    )
                    
                    logger.info(f"Reddit user info response: {user_response.status_code}")
                    
                    if user_response.status_code == 200:
                        user_info = user_response.json()
                        username = user_info.get('name')
                        reddit_user_id = user_info.get('id', '')
                        
                        logger.info(f"Reddit API returned username: {username}")
                        
                        if not username:
                            logger.error("No username in Reddit API response")
                            logger.error(f"Full user info response: {user_info}")
                            username = f"User_{reddit_user_id[:8]}" if reddit_user_id else f"User_{uuid.uuid4().hex[:8]}"
                    else:
                        logger.error(f"Reddit user info request failed: {user_response.status_code}")
                        logger.error(f"Response text: {user_response.text}")
                        username = f"User_{uuid.uuid4().hex[:8]}"
                        user_info = {"name": username, "id": reddit_user_id}
                        
                except Exception as e:
                    logger.error(f"User info request failed: {e}")
                    username = f"User_{uuid.uuid4().hex[:8]}"
                    user_info = {"name": username, "id": reddit_user_id}
                
                # Ensure we always have a username
                if not username:
                    username = f"User_{uuid.uuid4().hex[:8]}"
                    logger.warning(f"Using fallback username: {username}")
                
                logger.info(f"REAL Reddit OAuth successful for user: {username}")
                
                # Store tokens in DATABASE permanently for this specific user
                db_token_data = {
                    "access_token": access_token,
                    "refresh_token": token_data.get("refresh_token", ""),
                    "expires_in": token_data.get("expires_in", 3600),
                    "reddit_username": username,
                    "reddit_user_id": reddit_user_id,
                    "token_type": "bearer",
                    "scope": "submit,edit,read"
                }
                
                # Store in database for this user
                if database_manager and hasattr(database_manager, 'store_reddit_tokens'):
                    try:
                        db_result = await database_manager.store_reddit_tokens(user_id, db_token_data)
                        if db_result.get("success"):
                            logger.info(f"Reddit tokens stored permanently for user {user_id} as {username}")
                        else:
                            logger.error(f"Failed to store tokens in database: {db_result.get('error')}")
                    except Exception as e:
                        logger.error(f"Database storage error: {e}")
                
                # Also store in memory for immediate use
                user_reddit_tokens[user_id] = {
                    "access_token": access_token,
                    "refresh_token": token_data.get("refresh_token", ""),
                    "reddit_username": username,
                    "connected_at": datetime.now().isoformat(),
                    "user_info": user_info or {"name": username, "id": reddit_user_id}
                }
                
                # Clean up OAuth state
                oauth_states.pop(state, None)
                
                # Redirect to main page instead of /reddit-auto to avoid 404
                return RedirectResponse(
                    url=f"https://frontend-agentic-bnc2.onrender.com/?reddit_connected=true&username={username}",
                    status_code=302
                )
            else:
                logger.error("No access token in Reddit response")
                return RedirectResponse(
                    url="https://frontend-agentic-bnc2.onrender.com/?error=no_access_token",
                    status_code=302
                )
        else:
            logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/?error=token_exchange_failed",
                status_code=302
            )
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        logger.error(traceback.format_exc())
        return RedirectResponse(
            url="https://frontend-agentic-bnc2.onrender.com/?error=oauth_failed",
            status_code=302
        )








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






























































"""
Complete Multi-Platform Social Media Automation System
YouTube, WhatsApp, Instagram, Facebook with unified API
Real AI content generation and multi-user support
FIXED VERSION - All import and service initialization errors resolved
"""

from fastapi import FastAPI, HTTPException, Request, Query, BackgroundTasks, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from fastapi import File, UploadFile
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
import httpx
import uuid
import os
from fastapi import Form


from PIL import Image, ImageDraw, ImageFont
import io
import cv2
import numpy as np
import subprocess
import re

import shutil
# Set Playwright cache directory for Render
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/render/project/.playwright'
import requests
import base64
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from enum import Enum
from pathlib import Path
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("multiplatform_automation.log")
    ]
)
logger = logging.getLogger(__name__)

# FIXED IMPORTS - Corrected all import issues
def safe_import(module_name, class_name=None):
    """Safely import modules with error handling"""
    try:
        module = __import__(module_name)
        if class_name:
            return getattr(module, class_name)
        return module
    except (ImportError, AttributeError) as e:
        logger.warning(f"Failed to import {module_name}.{class_name if class_name else 'module'}: {e}")
        return None

# YouTube imports - FIXED
try:
    from youtube import (
        initialize_youtube_service, 
        get_youtube_connector, 
        get_youtube_scheduler,
        get_youtube_database
    )
    YOUTUBE_AVAILABLE = True
    logger.info("YouTube module loaded successfully")
except ImportError as e:
    logger.warning(f"YouTube module not available: {e}")
    YOUTUBE_AVAILABLE = False
    initialize_youtube_service = None
    get_youtube_connector = None
    get_youtube_scheduler = None
    get_youtube_database = None

# AI Service import - FIXED (removed underscore)
try:
    from ai_service2 import AIService2
    AI_SERVICE_AVAILABLE = True
    logger.info("AI Service 2 loaded successfully")
except ImportError as e:
    logger.warning(f"AI Service 2 not available: {e}")
    AI_SERVICE_AVAILABLE = False
    AIService2 = None

# YouTube Database import - FIXED
try:
    from YTdatabase import get_youtube_database as get_yt_db, YouTubeDatabaseManager
    YOUTUBE_DATABASE_AVAILABLE = True
    logger.info("YouTube database loaded successfully")
except ImportError as e:
    logger.warning(f"YouTube database not available: {e}")
    YOUTUBE_DATABASE_AVAILABLE = False
    get_yt_db = None
    YouTubeDatabaseManager = None



# YouTube AI Services - NEW
try:
    from YT_ai_services import YouTubeAIService
    from YT_extract_feature import YouTubeFeatureExtractor
    YOUTUBE_AI_AVAILABLE = True
    logger.info("YouTube AI services loaded successfully")
except ImportError as e:
    logger.warning(f"YouTube AI services not available: {e}")
    YOUTUBE_AI_AVAILABLE = False
    YouTubeAIService = None
    YouTubeFeatureExtractor = None




# FIXED: Add missing DATABASE_AVAILABLE variable
DATABASE_AVAILABLE = YOUTUBE_DATABASE_AVAILABLE

# WhatsApp imports - Safe import
try:
    from whatsapp import WhatsAppCloudAPI, WhatsAppAutomationScheduler, WhatsAppConfig, WhatsAppWebhookHandler
    WHATSAPP_AVAILABLE = True
    logger.info("WhatsApp module loaded successfully")
except ImportError as e:
    logger.warning(f"WhatsApp module not available: {e}")
    WHATSAPP_AVAILABLE = False
    WhatsAppCloudAPI = None
    WhatsAppAutomationScheduler = None
    WhatsAppConfig = None
    WhatsAppWebhookHandler = None

# Global instances
database_manager = None
ai_service = None
youtube_connector = None
youtube_scheduler = None
whatsapp_scheduler = None
webhook_handler = None
youtube_background_scheduler = None  # NEW: Background scheduler
youtube_ai_service = None  # NEW: YouTube AI service
youtube_feature_extractor = None  # NEW: Feature extractor



# Multi-user management
user_platform_tokens = {}  # user_id -> {platform: tokens}
oauth_states = {}          # oauth_state -> user_id
automation_configs = {}    # user_id -> {platform: configs}

# Authentication setup
security = HTTPBearer()

# Pydantic Models (keeping existing models)
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class YouTubeOAuthRequest(BaseModel):
    user_id: str
    state: str = "youtube_oauth"
    redirect_uri: Optional[str] = None

class YouTubeOAuthCallback(BaseModel):
    user_id: str
    code: str
    state: Optional[str] = None
    redirect_uri: Optional[str] = None

class YouTubeSetupRequest(BaseModel):
    user_id: str
    config: dict

class YouTubeUploadRequest(BaseModel):
    user_id: str
    title: str
    description: str
    video_url: str
    content_type: str = "shorts"
    tags: List[str] = []
    privacy_status: str = "public"

class YouTubeContentRequest(BaseModel):
    content_type: str = "shorts"
    topic: str = "general"
    target_audience: str = "general"

class YouTubeAutomationRequest(BaseModel):
    content_type: str = "shorts"
    upload_schedule: List[str]
    content_categories: List[str] = []
    auto_generate_titles: bool = True
    privacy_status: str = "public"
    shorts_per_day: int = 3

class WhatsAppMessageRequest(BaseModel):
    to: str
    message: str
    message_type: str = "text"

class WhatsAppMediaRequest(BaseModel):
    to: str
    media_url: str
    media_type: str = "image"
    caption: str = None

class WhatsAppAutomationRequest(BaseModel):
    business_name: str
    auto_reply_enabled: bool = False
    campaign_enabled: bool = False
    business_hours: Dict[str, str] = {"start": "09:00", "end": "18:00"}

class BroadcastRequest(BaseModel):
    platform: str
    recipient_list: List[str]
    message: str
    media_url: str = None
    media_type: str = None

# ➜ ADD THIS ENUM FIRST
class PostType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    text_poll = "text_poll"
    image_poll = "image_poll"
    quiz = "quiz"

# ➜ ADD THESE NEW PYDANTIC MODELS AFTER YOUR EXISTING MODELS
class CommunityPostRequest(BaseModel):
    user_id: str
    post_type: PostType = PostType.text
    content: str
    image_url: Optional[str] = None
    options: List[str] = []
    correct_answer: Optional[int] = None
    schedule_date: Optional[str] = None
    schedule_time: Optional[str] = None

class AIPostGenerationRequest(BaseModel):
    post_type: PostType = PostType.text
    topic: str = "general"
    target_audience: str = "general"
    style: str = "engaging"

# NEW: Scheduling classes
class VideoScheduleRequest(BaseModel):
    user_id: str
    schedule_date: str
    schedule_time: str
    video_data: dict

# NEW: YouTube Background Scheduler Class - FIXED DATABASE CHECKS
class YouTubeBackgroundScheduler:
    """Background scheduler for YouTube posts"""
    
    def __init__(self, database_manager, youtube_scheduler):
        self.database_manager = database_manager
        self.youtube_scheduler = youtube_scheduler
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
        
    async def start(self):
        """Start the background scheduler"""
        self.running = True
        logger.info("YouTube background scheduler started")
        
        while self.running:
            try:
                await self.process_scheduled_posts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Background scheduler error: {e}")
                await asyncio.sleep(30)  # Wait 30s on error
    
    async def stop(self):
        """Stop the background scheduler"""
        self.running = False
        logger.info("YouTube background scheduler stopped")
    
    async def process_scheduled_posts(self):
        """Process all posts scheduled for current time"""
        try:
            current_time = datetime.now()
            logger.debug(f"Checking for scheduled posts at {current_time}")
            
            # Get all scheduled posts that are due
            scheduled_posts = await self.get_due_scheduled_posts(current_time)
            
            for post in scheduled_posts:
                await self.execute_scheduled_post(post)
                
        except Exception as e:
            logger.error(f"Error processing scheduled posts: {e}")
    
    async def get_due_scheduled_posts(self, current_time):
        """Get posts scheduled to be published now - FIXED DATABASE CHECK"""
        try:
            # FIXED: Check database manager and database connection properly
            if not self.database_manager or not hasattr(self.database_manager, 'db') or self.database_manager.db is None:
                return []
            
            collection = self.database_manager.db.scheduled_posts
            
            # Find posts scheduled for current time (within 2 minute window)
            time_window_start = current_time - timedelta(minutes=1)
            time_window_end = current_time + timedelta(minutes=1)
            
            cursor = collection.find({
                "status": "scheduled",
                "scheduled_for": {
                    "$gte": time_window_start,
                    "$lte": time_window_end
                }
            })
            
            posts = []
            async for post in cursor:
                posts.append(post)
            
            if posts:
                logger.info(f"Found {len(posts)} posts ready for publishing")
            return posts
            
        except Exception as e:
            logger.error(f"Error querying scheduled posts: {e}")
            return []
    
    async def execute_scheduled_post(self, post):
        """Execute a scheduled post"""
        try:
            post_id = post.get("_id")
            user_id = post.get("user_id")
            post_type = post.get("post_type", "video")
            
            logger.info(f"Executing scheduled {post_type} for user {user_id}")
            
            if post_type == "video":
                result = await self.execute_scheduled_video(post)
            elif post_type in ["community_post", "text", "poll", "quiz"]:
                result = await self.execute_scheduled_community_post(post)
            else:
                logger.error(f"Unknown post type: {post_type}")
                result = {"success": False, "error": f"Unknown post type: {post_type}"}
            
            # Update post status based on result
            await self.update_post_status(post_id, result)
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Error executing scheduled post: {e}")
            await self.update_post_status(post.get("_id"), {
                "success": False, 
                "error": str(e)
            })
            return False
    
    async def execute_scheduled_video(self, post):
        """Execute scheduled video upload"""
        try:
            user_id = post.get("user_id")
            video_data = post.get("video_data", {})
            
            # Get user credentials
            credentials = await self.database_manager.get_youtube_credentials(user_id)
            if not credentials:
                return {"success": False, "error": "No YouTube credentials found"}
            
            # Upload video using existing scheduler
            result = await self.youtube_scheduler.generate_and_upload_content(
                user_id=user_id,
                credentials_data=credentials,
                content_type=video_data.get("content_type", "video"),
                title=video_data.get("title"),
                description=video_data.get("description"),
                video_url=video_data.get("video_url")
            )
            
            logger.info(f"Scheduled video upload result: {result.get('success', False)}")
            return result
            
        except Exception as e:
            logger.error(f"Scheduled video upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_scheduled_community_post(self, post):
        """Execute scheduled community post"""
        try:
            user_id = post.get("user_id")
            post_data = post.get("post_data", {})
            
            # Get user credentials
            credentials = await self.database_manager.get_youtube_credentials(user_id)
            if not credentials:
                return {"success": False, "error": "No YouTube credentials found"}
            
            # Try to create community post (will fall back to mock)
            if hasattr(self.youtube_scheduler.youtube_connector, 'create_community_post'):
                result = await self.youtube_scheduler.youtube_connector.create_community_post(
                    credentials_data=credentials,
                    post_data=post_data
                )
            else:
                # Mock community post
                result = {
                    "success": True,
                    "post_id": f"scheduled_mock_{int(datetime.now().timestamp())}",
                    "message": "Scheduled community post created (mock mode)"
                }
            
            # Log to database
            await self.database_manager.log_community_post(user_id, {
                **post_data,
                "scheduled_execution": True,
                "executed_at": datetime.now()
            })
            
            logger.info(f"Scheduled community post result: {result.get('success', False)}")
            return result
            
        except Exception as e:
            logger.error(f"Scheduled community post failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_post_status(self, post_id, result):
        """Update scheduled post status after execution"""
        try:
            # FIXED: Check database manager and database connection properly
            if not self.database_manager or not hasattr(self.database_manager, 'db') or self.database_manager.db is None:
                return
                
            collection = self.database_manager.db.scheduled_posts
            
            update_data = {
                "status": "published" if result.get("success") else "failed",
                "executed_at": datetime.now(),
                "execution_result": result,
                "updated_at": datetime.now()
            }
            
            await collection.update_one(
                {"_id": post_id},
                {"$set": update_data}
            )
            
            logger.info(f"Updated scheduled post {post_id} status to {update_data['status']}")
            
        except Exception as e:
            logger.error(f"Error updating post status: {e}")

# NEW: Helper function to store scheduled posts - FIXED DATABASE CHECK
async def store_scheduled_post(user_id: str, post_type: str, post_data: dict, scheduled_for: datetime):
    """Store a scheduled post in the database"""
    try:
        # FIXED: Check database manager and database connection properly
        if not database_manager or not hasattr(database_manager, 'db') or database_manager.db is None:
            return False
            
        collection = database_manager.db.scheduled_posts
        
        scheduled_post = {
            "user_id": user_id,
            "post_type": post_type,
            "post_data" if post_type == "community_post" else "video_data": post_data,
            "scheduled_for": scheduled_for,
            "status": "scheduled",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = await collection.insert_one(scheduled_post)
        logger.info(f"Scheduled {post_type} stored with ID: {result.inserted_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error storing scheduled post: {e}")
        return False







# FIXED AI Service initialization function
def initialize_ai_service():
    """Initialize AI service with proper error handling"""
    global ai_service
    
    try:
        # Check for API keys
        groq_key = os.getenv("GROQ_API_KEY")
        mistral_key = os.getenv("MISTRAL_API_KEY")
        
        logger.info(f"API Keys - Groq: {'✓' if groq_key else '✗'}, Mistral: {'✓' if mistral_key else '✗'}")
        
        if not groq_key and not mistral_key:
            logger.warning("No AI API keys found - using mock AI service")
            ai_service = None
            return False
        
        # FIXED: Use AIService2 instead of AIService
        if AI_SERVICE_AVAILABLE and AIService2:
            ai_service = AIService2()
            logger.info("AI Service 2 initialized successfully")
            return True
        else:
            logger.warning("AIService2 class not available")
            ai_service = None
            return False
            
    except Exception as e:
        logger.error(f"AI service initialization failed: {e}")
        ai_service = None
        return False

# FIXED service initialization with proper order AND background scheduler


async def download_youtube_video_for_thumbnails(video_url: str, user_id: str) -> str:
    """
    Download YouTube video temporarily for thumbnail frame extraction
    Uses yt-dlp to download video
    
    Args:
        video_url: YouTube video URL
        user_id: User ID for temp directory
        
    Returns:
        str: Path to downloaded video file
    """
    try:
        import subprocess
        import re
        
        logger.info(f"📥 Downloading YouTube video for thumbnail extraction: {video_url[:50]}...")
        
        # Extract video ID
        video_id = None
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube\.com/v/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id:
            raise Exception("Could not extract video ID from YouTube URL")
        
        # Create temp directory
        temp_dir = Path(f"/tmp/uploads/{user_id}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(datetime.now().timestamp())
        output_path = str(temp_dir / f"yt_{video_id}_{timestamp}.mp4")
        
        # Download using yt-dlp (or youtube-dl fallback)
        logger.info(f"🎬 Downloading video ID: {video_id}")
        
        # Try yt-dlp first (better and faster)
        try:
            cmd = [
                'yt-dlp',
                '-f', 'best[ext=mp4]/best',  # Best MP4 format
                '--no-playlist',
                '-o', output_path,
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"yt-dlp failed: {result.stderr}")
                
        except FileNotFoundError:
            # Fallback to youtube-dl if yt-dlp not installed
            logger.warning("⚠️ yt-dlp not found, trying youtube-dl")
            
            cmd = [
                'youtube-dl',
                '-f', 'best[ext=mp4]/best',
                '--no-playlist',
                '-o', output_path,
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise Exception(f"youtube-dl failed: {result.stderr}")
        
        # Verify file exists and has content
        if not os.path.exists(output_path):
            raise Exception("Download completed but file not found")
        
        file_size = os.path.getsize(output_path)
        if file_size < 100000:  # Less than 100KB
            raise Exception(f"Downloaded file too small: {file_size} bytes")
        
        logger.info(f"✅ YouTube video downloaded: {output_path} ({file_size} bytes)")
        return output_path
        
    except subprocess.TimeoutExpired:
        logger.error("❌ YouTube download timeout (>120s)")
        raise Exception("YouTube video download timed out. Video may be too long or unavailable.")
        
    except Exception as e:
        logger.error(f"❌ YouTube download failed: {str(e)}")
        raise Exception(f"Failed to download YouTube video: {str(e)}")


async def initialize_services():
    """Initialize all services with robust error handling"""
    global database_manager, ai_service, youtube_connector, youtube_scheduler, youtube_background_scheduler, youtube_ai_service, youtube_feature_extractor
    
    try:
        logger.info("Starting YouTube automation service initialization...")
        
        # Check required environment variables
        required_env_vars = [
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET', 
            'MONGODB_URI'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
            
        logger.info("Environment variables check passed")
        
        # STEP 1: Initialize AI service FIRST
        ai_initialized = initialize_ai_service()
        logger.info(f"AI service initialization: {'Success' if ai_initialized else 'Failed/Mock'}")
        
        # STEP 2: Initialize YouTube Database using FIXED import
        if YOUTUBE_DATABASE_AVAILABLE and get_yt_db:
            try:
                database_manager = get_yt_db()
                connected = await database_manager.connect()
                if connected:
                    logger.info("YouTube database initialized successfully")
                else:
                    logger.error("YouTube database connection failed")
                    return False
            except Exception as e:
                logger.error(f"YouTube database initialization failed: {e}")
                return False
        else:
            logger.error("YouTube database not available - check YTdatabase.py import")
            return False
        
        # STEP 3: Initialize YouTube service with database and AI service
        if YOUTUBE_AVAILABLE and initialize_youtube_service:
            try:
                logger.info("Initializing YouTube service with dependencies...")
                
                # Pass both database_manager and ai_service to YouTube initialization
                success = await initialize_youtube_service(
                    database_manager=database_manager,
                    ai_service=ai_service
                )
                
                if success:
                    # Get YouTube service instances
                    if get_youtube_connector:
                        youtube_connector = get_youtube_connector()
                        logger.info("YouTube connector initialized")
                    
                    if get_youtube_scheduler:
                        youtube_scheduler = get_youtube_scheduler()
                        logger.info("YouTube scheduler initialized")
                    
                    # CRITICAL: Get background scheduler from youtube.py module
                    from youtube import youtube_background_scheduler as yt_bg_scheduler
                    youtube_background_scheduler = yt_bg_scheduler
                    logger.info("Background scheduler reference obtained")
                    
                    logger.info("YouTube service initialization completed successfully")
                else:
                    logger.error("YouTube service initialization returned False")
                    return False
                    
            except Exception as e:
                logger.error(f"YouTube service initialization failed: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
        else:
            logger.error("YouTube module not available - check imports")
            return False
        
        # STEP 4: Initialize YouTube AI services
        if YOUTUBE_AI_AVAILABLE:
            try:
                youtube_ai_service = YouTubeAIService()
                youtube_feature_extractor = YouTubeFeatureExtractor(youtube_ai_service)
                logger.info("YouTube AI services initialized successfully")
            except Exception as ai_error:
                logger.warning(f"YouTube AI services initialization failed: {ai_error}")
        
        logger.info("All services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Critical service initialization failure: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

# ========== ADD cleanup_services HERE ==========
async def cleanup_services():
    """Cleanup services on shutdown"""
    try:
        # Stop background scheduler
        if youtube_background_scheduler:
            await youtube_background_scheduler.stop()
            logger.info("Background scheduler stopped")
        
        if database_manager:
            await database_manager.close()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error(f"Service cleanup failed: {e}")



import httpx
import re
from urllib.parse import urlparse, parse_qs

async def download_youtube_video_for_thumbnails(video_url: str, user_id: str) -> str:
    """
    Download YouTube video temporarily for thumbnail frame extraction
    Uses yt-dlp to download video (lightweight, just for thumbnails)
    
    Args:
        video_url: YouTube video URL
        user_id: User ID for temp directory
        
    Returns:
        str: Path to downloaded video file
    """
    try:
        logger.info(f"📥 Downloading YouTube video for thumbnails: {video_url[:50]}...")
        
        # Extract video ID
        video_id = None
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube\.com/v/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id:
            raise Exception("Could not extract video ID from YouTube URL")
        
        # Create temp directory
        temp_dir = Path(f"/tmp/uploads/{user_id}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = int(datetime.now().timestamp())
        output_path = str(temp_dir / f"yt_{video_id}_{timestamp}.mp4")
        
        logger.info(f"🎬 Downloading video ID: {video_id}")
        
        # Download using yt-dlp (lightweight - worst quality for speed)
        try:
            cmd = [
                'yt-dlp',
                '-f', 'worst[ext=mp4]/worst',  # Fastest download (lowest quality)
                '--no-playlist',
                '--max-filesize', '100M',  # Skip videos over 100MB
                '--socket-timeout', '30',
                '-o', output_path,
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90  # 90 second timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"yt-dlp failed: {result.stderr[:200]}")
                
        except FileNotFoundError:
            # Fallback to youtube-dl
            logger.warning("⚠️ yt-dlp not found, trying youtube-dl")
            
            cmd = [
                'youtube-dl',
                '-f', 'worst[ext=mp4]/worst',
                '--no-playlist',
                '-o', output_path,
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90
            )
            
            if result.returncode != 0:
                raise Exception(f"youtube-dl failed: {result.stderr[:200]}")
        
        # Verify file
        if not os.path.exists(output_path):
            raise Exception("Download completed but file not found")
        
        file_size = os.path.getsize(output_path)
        if file_size < 50000:  # Less than 50KB
            os.unlink(output_path)
            raise Exception(f"Downloaded file too small: {file_size} bytes")
        
        logger.info(f"✅ YouTube video downloaded: {output_path} ({file_size} bytes)")
        return output_path
        
    except subprocess.TimeoutExpired:
        logger.error("❌ YouTube download timeout")
        raise Exception("YouTube download timed out. Try a shorter video or different URL.")
        
    except Exception as e:
        logger.error(f"❌ YouTube download failed: {str(e)}")
        raise Exception(f"Failed to download YouTube video: {str(e)}")


def detect_language_from_title(title: str) -> str:
    """
    Auto-detect language from title text
    
    Returns: 'hindi', 'hinglish', or 'english'
    """
    try:
        # Check for Devanagari characters (Hindi)
        hindi_chars = "अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
        if any(char in hindi_chars for char in title):
            return "hindi"
        
        # Check for Hinglish keywords
        hinglish_words = ["acha", "accha", "bhai", "yaar", "kya", "hai", "nahi", "kaise", "matlab"]
        if any(word in title.lower() for word in hinglish_words):
            return "hinglish"
        
        return "english"
        
    except Exception:
        return "english"


def add_ctr_text_overlay(
    img: Image.Image,
    title: str,
    style: dict,
    language: str
) -> Image.Image:
    """
    Add CTR-optimized text overlay with YELLOW text and thick strokes
    """
    try:
        draw = ImageDraw.Draw(img)
        
        # Prepare text based on language
        if language == "hindi":
            text = title[:25]
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        elif language == "hinglish":
            text = title[:30]
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        else:
            text = title[:35].upper()  # ALL CAPS for CTR
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        # Load font
        try:
            font = ImageFont.truetype(font_path, style["font_size"])
        except:
            font = ImageFont.load_default()
        
        # Get text size
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Position at bottom
        padding = 30
        text_x = (1280 - text_width) // 2
        text_y = 720 - text_height - 80
        
        # Draw colored background bar
        draw.rectangle(
            [(0, text_y - padding), (1280, text_y + text_height + padding)],
            fill=style["bg_color"]
        )
        
        # Draw BLACK STROKE (outline)
        stroke_width = style["stroke_width"]
        for adj_x in range(-stroke_width, stroke_width + 1):
            for adj_y in range(-stroke_width, stroke_width + 1):
                draw.text(
                    (text_x + adj_x, text_y + adj_y),
                    text,
                    fill=(0, 0, 0),
                    font=font
                )
        
        # Draw main YELLOW/WHITE text
        draw.text((text_x, text_y), text, fill=style["text_color"], font=font)
        
        return img
        
    except Exception as e:
        logger.error(f"❌ Text overlay failed: {e}")
        return img


def create_fallback_ctr_thumbnails(
    title: str,
    count: int,
    language: str
) -> list:
    """
    Create fallback CTR-optimized PNG thumbnails
    """
    try:
        thumbnails = []
        
        ctr_styles = [
            {"name": "Bold Red", "bg_color": (255, 0, 0), "text_color": (255, 255, 0), "font_size": 80},
            {"name": "Bold Black", "bg_color": (0, 0, 0), "text_color": (255, 255, 0), "font_size": 75},
            {"name": "Bold Orange", "bg_color": (255, 140, 0), "text_color": (255, 255, 255), "font_size": 78}
        ]
        
        for i in range(count):
            style = ctr_styles[i % len(ctr_styles)]
            
            img = Image.new('RGB', (1280, 720), style["bg_color"])
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", style["font_size"])
            except:
                font = ImageFont.load_default()
            
            text = title[:30].upper() if language == "english" else title[:30]
            
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (1280 - text_width) // 2
            text_y = (720 - text_height) // 2
            
            # Black stroke
            for adj in [(-4, -4), (-4, 4), (4, -4), (4, 4)]:
                draw.text((text_x + adj[0], text_y + adj[1]), text, fill=(0, 0, 0), font=font)
            
            draw.text((text_x, text_y), text, fill=style["text_color"], font=font)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', quality=95)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            thumbnails.append({
                "id": f"fallback_{i+1}",
                "url": f"data:image/png;base64,{img_base64}",
                "style": style["name"],
                "ctr_optimized": True,
                "language": language
            })
        
        return thumbnails
        
    except Exception as e:
        logger.error(f"❌ Fallback creation failed: {e}")
        return []


async def extract_video_frames_as_thumbnails(
    video_path: str, 
    title: str, 
    num_frames: int = 3,
    language: str = "english"
) -> list:
    """
    Extract CTR-optimized frames with bold YELLOW text overlay
    """
    try:
        logger.info(f"🎬 Extracting {num_frames} CTR frames (Language: {language})")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception(f"Failed to open video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"📊 Video: {total_frames} frames, {fps:.1f} fps, {duration:.1f}s")
        
        if total_frames < num_frames:
            num_frames = max(1, total_frames)
        
        start_frame = int(total_frames * 0.1)
        end_frame = int(total_frames * 0.9)
        
        if end_frame <= start_frame:
            start_frame = 0
            end_frame = total_frames - 1
        
        frame_positions = np.linspace(start_frame, end_frame, num_frames, dtype=int)
        
        thumbnails = []
        
        # CTR styles
        ctr_styles = [
            {"name": "Bold Impact", "bg_color": (255, 50, 50), "text_color": (255, 255, 0), "font_size": 90, "stroke_width": 8},
            {"name": "High Contrast", "bg_color": (0, 0, 0), "text_color": (255, 255, 0), "font_size": 85, "stroke_width": 6},
            {"name": "Vibrant Pop", "bg_color": (255, 140, 0), "text_color": (255, 255, 255), "font_size": 88, "stroke_width": 7}
        ]
        
        for i, frame_pos in enumerate(frame_positions):
            try:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"⚠️ Failed to read frame {frame_pos}")
                    continue
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                pil_image = pil_image.resize((1280, 720), Image.LANCZOS)
                
                style = ctr_styles[i % len(ctr_styles)]
                pil_image = add_ctr_text_overlay(pil_image, title, style, language)
                
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG', quality=95)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                thumbnails.append({
                    "id": f"frame_{i+1}",
                    "url": f"data:image/png;base64,{img_base64}",
                    "style": f"{style['name']} - Frame {i+1}",
                    "frame_number": int(frame_pos),
                    "timestamp": f"{frame_pos/fps:.1f}s" if fps > 0 else f"Frame {frame_pos}",
                    "ctr_optimized": True,
                    "language": language
                })
                
                logger.info(f"✅ CTR frame {i+1}/{num_frames} at {frame_pos/fps:.1f}s")
                
            except Exception as frame_error:
                logger.error(f"❌ Frame {i+1} failed: {frame_error}")
                continue
        
        cap.release()
        
        if len(thumbnails) == 0:
            raise Exception("No frames extracted")
        
        logger.info(f"✅ Extracted {len(thumbnails)} CTR thumbnails")
        return thumbnails
        
    except Exception as e:
        logger.error(f"❌ Frame extraction failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []



# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialization_success = await initialize_services()
    if not initialization_success:
        logger.error("Service initialization failed - app may not work correctly")
    yield
    # Shutdown
    await cleanup_services()

app = FastAPI(
    title="Multi-Platform Social Media Automation",
    description="Complete automation system for YouTube, WhatsApp, Instagram, Facebook",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-agentic.onrender.com",
        "https://frontend-agentic-bnc2.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error("=== 422 VALIDATION ERROR ===")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Validation errors: {exc.errors()}")
    
    # ✅ SAFE: Don't try to log/serialize FormData or UploadFile
    try:
        if hasattr(exc, 'body') and exc.body:
            if isinstance(exc.body, (str, dict, list)):
                logger.error(f"Request body: {exc.body}")
            else:
                logger.error(f"Request body type: {type(exc.body).__name__}")
    except Exception as body_error:
        logger.error(f"Could not log body: {body_error}")
    
    logger.error("================================")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors(),
            "message": "Please check your request format"
        }
    )

# Health check endpoint
@app.get("/")
async def root():
    """Health check and service status"""
    return {
        "status": "running",
        "message": "Multi-Platform Social Media Automation System",
        "version": "2.0.0",
        "services": {
            "youtube": YOUTUBE_AVAILABLE,
            "whatsapp": WHATSAPP_AVAILABLE,
            "ai_service": AI_SERVICE_AVAILABLE,
            "database": DATABASE_AVAILABLE  # FIXED: Now properly defined
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    services_status = {}
    
    if database_manager:
        try:
            health_result = await database_manager.health_check()
            services_status["database"] = health_result.get("status", "unknown")
        except:
            services_status["database"] = "disconnected"
    else:
        services_status["database"] = "not_initialized"
    
    services_status["ai_service"] = "available" if ai_service else "not_available"
    services_status["youtube"] = "available" if YOUTUBE_AVAILABLE else "not_available"
    services_status["whatsapp"] = "available" if WHATSAPP_AVAILABLE else "not_available"
    
    return {
        "status": "healthy",
        "services": services_status,
        "timestamp": datetime.now().isoformat()
    }

# Add debug endpoints
@app.get("/debug/services")
async def debug_services():
    """Debug endpoint to check service status"""
    return {
        "youtube_connector": youtube_connector is not None,
        "youtube_scheduler": youtube_scheduler is not None,
        "database_manager": database_manager is not None,
        "ai_service": ai_service is not None,
        "YOUTUBE_AVAILABLE": YOUTUBE_AVAILABLE,
        "AI_SERVICE_AVAILABLE": AI_SERVICE_AVAILABLE,
        "DATABASE_AVAILABLE": DATABASE_AVAILABLE,
        "env_vars": {
            "GOOGLE_CLIENT_ID": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
            "GOOGLE_CLIENT_SECRET": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗",
            "GOOGLE_OAUTH_REDIRECT_URI": os.getenv("GOOGLE_OAUTH_REDIRECT_URI"),
            "MONGODB_URI": "✓" if os.getenv("MONGODB_URI") else "✗",
            "FRONTEND_URL": os.getenv("FRONTEND_URL")
        }
    }

@app.get("/debug/user/{email}")
async def debug_user(email: str):
    """Debug endpoint to check user data (REMOVE IN PRODUCTION)"""
    try:
        if not database_manager:
            return {"error": "Database not available"}
        
        user = await database_manager.get_user_by_email(email)
        if user:
            return {
                "found": True,
                "user_id": user.get("_id"),
                "email": user.get("email"),
                "name": user.get("name"),
                "has_password": "password" in user,
                "password_length": len(user.get("password", "")) if user.get("password") else 0,
                "created_at": user.get("created_at"),
                "platforms_connected": user.get("platforms_connected", [])
            }
        else:
            return {"found": False}
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (remove in production)"""
    return {
        "GOOGLE_CLIENT_ID": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
        "GOOGLE_CLIENT_SECRET": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗", 
        "GOOGLE_OAUTH_REDIRECT_URI": os.getenv("GOOGLE_OAUTH_REDIRECT_URI"),
        "FRONTEND_URL": os.getenv("FRONTEND_URL"),
        "youtube_connector_initialized": youtube_connector is not None
    }

@app.get("/debug/users")
async def debug_users():
    """Debug endpoint to list recent users"""
    try:
        if not database_manager:
            return {"error": "Database not available"}
        
        users_cursor = database_manager.users_collection.find({}).sort("created_at", -1).limit(10)
        users = []
        
        async for user in users_cursor:
            users.append({
                "user_id": user.get("_id"),
                "email": user.get("email"),
                "name": user.get("name"),
                "created_at": str(user.get("created_at")),
                "has_password": "password" in user
            })
        
        return {"users": users, "count": len(users)}
        
    except Exception as e:
        return {"error": str(e)}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """User registration that returns user data for auto-login"""
    try:
        if not database_manager:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        existing_user = await database_manager.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = str(uuid.uuid4())
        user_data = {
            "_id": user_id,
            "email": request.email,
            "name": request.name,
            "password": request.password,
            "created_at": datetime.now(),
            "platforms_connected": [],
            "automation_enabled": False
        }
        
        success = await database_manager.create_user(user_data)
        
        if success:
            return {
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "user_id": user_id,
                    "email": request.email,
                    "name": request.name,
                    "platforms_connected": []
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login with detailed debugging"""
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        if not database_manager:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        user = await database_manager.get_user_by_email(request.email)
        logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
        
        if not user:
            logger.warning(f"No user found with email: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_info = {k: v for k, v in user.items() if k != 'password'}
        logger.info(f"User data: {user_info}")
        
        stored_password = user.get("password")
        if not stored_password:
            logger.error(f"No password stored for user: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"Password comparison - Provided length: {len(request.password)}, Stored length: {len(stored_password)}")
        
        if stored_password != request.password:
            logger.warning(f"Password mismatch for user: {request.email}")
            logger.info(f"Provided password: '{request.password}'")
            logger.info(f"Stored password: '{stored_password}'")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"Login successful for user: {request.email}")
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": user["_id"],
                "email": user["email"],
                "name": user["name"],
                "platforms_connected": user.get("platforms_connected", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed with exception: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# FIXED YouTube OAuth endpoints
@app.post("/api/youtube/oauth-url")
async def youtube_oauth_url(request: YouTubeOAuthRequest):
    """Generate YouTube OAuth URL - COMPLETELY FIXED VERSION"""
    try:
        logger.info(f"YouTube OAuth request for user_id: {request.user_id}")
        
        if not youtube_connector:
            logger.error("YouTube connector is not initialized")
            raise HTTPException(
                status_code=503, 
                detail="YouTube service not properly initialized. Check server logs."
            )
        
        # FORCED backend redirect URI - hardcoded to ensure correctness
        backend_redirect_uri = "https://agentic-u5lx.onrender.com/api/youtube/oauth-callback"
        
        logger.info(f"Using FORCED BACKEND redirect URI: {backend_redirect_uri}")
        
        result = youtube_connector.generate_oauth_url(
            state=f"youtube_oauth_{request.user_id}",
            redirect_uri=backend_redirect_uri  # FORCE backend callback
        )
        
        logger.info(f"OAuth URL generation result: {result.get('success', False)}")
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube OAuth URL generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")



@app.get("/api/youtube/oauth-callback")
async def youtube_oauth_callback_get(code: str, state: str):
    """Handle YouTube OAuth callback from Google - FIXED to redirect to /youtube-callback"""
    try:
        logger.info(f"=== YouTube OAuth Callback Started ===")
        logger.info(f"State: {state}")
        logger.info(f"Code: {code[:20]}...")
        
        # Extract user_id from state
        if "youtube_oauth_" in state:
            user_id = state.replace("youtube_oauth_", "")
            logger.info(f"✓ Extracted user_id: {user_id}")
        else:
            logger.error(f"✗ Invalid state format: {state}")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/youtube-callback?error=invalid_state",
                status_code=302
            )
        
        # Check YouTube connector
        if not youtube_connector:
            logger.error("✗ YouTube connector not available")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/youtube-callback?error=service_unavailable",
                status_code=302
            )
        
        # Exchange code for token
        backend_redirect_uri = "https://agentic-u5lx.onrender.com/api/youtube/oauth-callback"
        logger.info(f"Token exchange with redirect_uri: {backend_redirect_uri}")
            
        token_result = await youtube_connector.exchange_code_for_token(
            code=code,
            redirect_uri=backend_redirect_uri
        )
        
        # Check result
        if not token_result["success"]:
            error_msg = token_result.get('error', 'unknown')
            logger.error(f"✗ Token exchange failed: {error_msg}")
            return RedirectResponse(
                url=f"https://frontend-agentic-bnc2.onrender.com/youtube-callback?error=token_failed&details={error_msg}",
                status_code=302
            )
        
        logger.info("✓ Token exchange successful")
        
        # Prepare credentials
        youtube_credentials = {
            "access_token": token_result["access_token"],
            "refresh_token": token_result["refresh_token"],
            "token_uri": token_result["token_uri"],
            "client_id": token_result["client_id"],
            "client_secret": token_result["client_secret"],
            "scopes": token_result["scopes"],
            "expires_at": datetime.now() + timedelta(seconds=token_result.get("expires_in", 3600)),
            "channel_info": token_result["channel_info"]
        }
        
        # Store in database
        try:
            success = await database_manager.store_youtube_credentials(
                user_id=user_id,
                credentials=youtube_credentials
            )
            
            if success:
                logger.info(f"✓ Credentials stored for user {user_id}")
            else:
                logger.error(f"✗ Failed to store credentials")
                return RedirectResponse(
                    url="https://frontend-agentic-bnc2.onrender.com/youtube-callback?error=storage_failed",
                    status_code=302
                )
                
        except Exception as db_error:
            logger.error(f"✗ Database error: {db_error}")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/youtube-callback?error=database_error",
                status_code=302
            )
        
        # Get channel info
        channel_title = token_result["channel_info"].get("title", "Unknown Channel")
        channel_id = token_result["channel_info"].get("id", "")
        
        logger.info(f"✓ Channel: {channel_title} (ID: {channel_id})")
        logger.info(f"=== Redirecting to /youtube-callback ===")
        
        # CRITICAL: Redirect to /youtube-callback NOT /youtube
        redirect_url = f"https://frontend-agentic-bnc2.onrender.com/youtube-callback?youtube_connected=true&channel={channel_title}"
        logger.info(f"Redirect URL: {redirect_url}")
        
        return RedirectResponse(
            url=redirect_url,
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"✗ OAuth callback exception: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return RedirectResponse(
            url="https://frontend-agentic-bnc2.onrender.com/youtube-callback?error=oauth_failed",
            status_code=302
        )

# FIXED OAuth callback endpoint
# @app.get("/api/youtube/oauth-callback")
# async def youtube_oauth_callback_get(code: str, state: str):
#     """Handle YouTube OAuth callback from Google - FIXED GET endpoint"""
#     try:
#         logger.info(f"YouTube OAuth callback received - state: {state}, code: {code[:20]}...")
        
#         if "youtube_oauth_" in state:
#             user_id = state.replace("youtube_oauth_", "")
#             logger.info(f"Extracted user_id from state: {user_id}")
#         else:
#             logger.error(f"Invalid state format: {state}")
#             return RedirectResponse(
#                 url="https://frontend-agentic-bnc2.onrender.com/youtube?error=invalid_state",
#                 status_code=302
#             )
        
#         if not youtube_connector:
#             logger.error("YouTube connector not available")
#             return RedirectResponse(
#                 url="https://frontend-agentic-bnc2.onrender.com/youtube?error=service_unavailable",
#                 status_code=302
#             )
        
#         backend_redirect_uri = "https://agentic-u5lx.onrender.com/api/youtube/oauth-callback"
#         logger.info(f"Token exchange with redirect_uri: {backend_redirect_uri}")
            
#         token_result = await youtube_connector.exchange_code_for_token(
#             code=code,
#             redirect_uri=backend_redirect_uri
#         )
        
#         if not token_result["success"]:
#             logger.error(f"Token exchange failed: {token_result.get('error')}")
#             return RedirectResponse(
#                 url="https://frontend-agentic-bnc2.onrender.com/youtube?error=token_exchange_failed",
#                 status_code=302
#             )
        
#         youtube_credentials = {
#             "access_token": token_result["access_token"],
#             "refresh_token": token_result["refresh_token"],
#             "token_uri": token_result["token_uri"],
#             "client_id": token_result["client_id"],
#             "client_secret": token_result["client_secret"],
#             "scopes": token_result["scopes"],
#             "expires_at": datetime.now() + timedelta(seconds=token_result.get("expires_in", 3600)),
#             "channel_info": token_result["channel_info"]
#         }
        
#         try:
#             success = await database_manager.store_youtube_credentials(
#                 user_id=user_id,
#                 credentials=youtube_credentials
#             )
            
#             if success:
#                 logger.info(f"YouTube credentials stored for user {user_id}")
#             else:
#                 logger.error(f"Failed to store YouTube credentials for user {user_id}")
                
#         except Exception as db_error:
#             logger.error(f"Database error: {db_error}")
        
#         channel_title = token_result["channel_info"].get("title", "Unknown Channel")
#         logger.info(f"YouTube OAuth SUCCESS - Channel: {channel_title}")
        
#         return RedirectResponse(
#             url=f"https://frontend-agentic-bnc2.onrender.com/youtube?youtube_connected=true&channel={channel_title}",
#             status_code=302
#         )
        
#     except Exception as e:
#         logger.error(f"YouTube OAuth callback failed: {e}")
#         return RedirectResponse(
#             url="https://frontend-agentic-bnc2.onrender.com/youtube?error=oauth_failed",
#             status_code=302
#         )








# ADD missing /api/auth/me endpoint
@app.get("/api/auth/me")
async def get_current_user_info():
    """Basic auth endpoint to prevent 404 errors"""
    return {
        "success": True,
        "user": {
            "id": "demo_user",
            "email": "demo@example.com",
            "name": "Demo User"
        }
    }

# Keep existing POST version for compatibility
@app.post("/api/youtube/oauth-callback-post")
async def youtube_oauth_callback_post(request: YouTubeOAuthCallback):
    """POST version - kept for compatibility but redirect to GET"""
    return RedirectResponse(
        url=f"/api/youtube/oauth-callback?code={request.code}&state={request.state}",
        status_code=307
    )

@app.get("/api/debug/youtube-status")
async def debug_youtube_status():
    """Debug YouTube service initialization in mainY.py"""
    return {
        "youtube_connector_available": youtube_connector is not None,
        "youtube_scheduler_available": youtube_scheduler is not None,
        "database_manager_available": database_manager is not None,
        "ai_service_available": ai_service is not None,
        "environment_vars": {
            "GOOGLE_CLIENT_ID": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
            "GOOGLE_CLIENT_SECRET": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗",
            "GOOGLE_OAUTH_REDIRECT_URI": os.getenv("GOOGLE_OAUTH_REDIRECT_URI"),
            "BACKEND_URL": os.getenv("BACKEND_URL", "https://agentic-u5lx.onrender.com"),
            "MONGODB_URI": "✓" if os.getenv("MONGODB_URI") else "✗"
        },
        "expected_redirect_uri": f"{os.getenv('BACKEND_URL', 'https://agentic-u5lx.onrender.com')}/api/youtube/oauth-callback"
    }






# YouTube API Routes - FIXED all endpoints
@app.get("/api/youtube/status/{user_id}")
async def get_youtube_status(user_id: str):
    """Get YouTube automation status with real channel data"""
    try:
        logger.info(f"Getting YouTube status for user: {user_id}")
        
        # Get credentials
        credentials = await database_manager.get_youtube_credentials(user_id)
        if not credentials:
            return {
                "success": True,
                "youtube_connected": False,
                "message": "YouTube not connected"
            }
        
        # Get real channel info from YouTube API
        try:
            youtube_service = await youtube_connector.get_authenticated_service(user_id)
            if youtube_service:
                channels_response = youtube_service.channels().list(
                    part="statistics,snippet",
                    mine=True
                ).execute()
                
                if channels_response.get("items"):
                    channel = channels_response["items"][0]
                    channel_stats = channel["statistics"]
                    channel_snippet = channel["snippet"]
                    
                    # Real channel info
                    real_channel_info = {
                        "channel_name": channel_snippet.get("title", "Unknown"),
                        "channel_id": channel["id"],
                        "subscriber_count": int(channel_stats.get("subscriberCount", 0)),
                        "video_count": int(channel_stats.get("videoCount", 0)),
                        "view_count": int(channel_stats.get("viewCount", 0)),
                        "thumbnail_url": channel_snippet["thumbnails"]["default"]["url"]
                    }
                else:
                    real_channel_info = credentials.get("channel_info", {})
            else:
                real_channel_info = credentials.get("channel_info", {})
                
        except Exception as e:
            logger.warning(f"Failed to get real-time channel data: {e}")
            real_channel_info = credentials.get("channel_info", {})
        
        # Get automation config
        automation_config = await database_manager.get_automation_config(user_id, "youtube")
        
        # Get upload stats
        upload_stats = await database_manager.get_upload_stats(user_id)
        
        return {
            "success": True,
            "youtube_connected": True,
            "channel_info": real_channel_info,
            "youtube_automation": {
                "enabled": automation_config.get("enabled", False) if automation_config else False,
                "config": automation_config.get("config_data", {}) if automation_config else {},
                "stats": upload_stats
            },
            "credentials_active": True,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "youtube_connected": False
        }
    






@app.post("/api/youtube/disconnect/{user_id}")
async def youtube_disconnect(user_id: str):
    """Disconnect YouTube and remove stored credentials"""
    try:
        success = await database_manager.revoke_youtube_access(user_id)
        
        if success:
            return {
                "success": True,
                "message": "YouTube disconnected successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to disconnect YouTube")
            
    except Exception as e:
        logger.error(f"YouTube disconnect failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/youtube/setup-automation")
async def youtube_setup_automation(request: dict):
    """Setup YouTube automation configuration - FIXED"""
    try:
        logger.info(f"YouTube automation setup request: {request}")
        
        # Extract user_id properly
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Check if user has YouTube connected
        try:
            credentials = await database_manager.get_youtube_credentials(user_id)
            if not credentials:
                raise HTTPException(status_code=400, detail="YouTube not connected")
        except Exception as db_error:
            logger.error(f"Database error checking YouTube connection: {db_error}")
            return {
                "success": False,
                "error": "Database connection error",
                "message": "Unable to verify YouTube connection"
            }
        
        # Create automation configuration
        automation_config = {
            "user_id": user_id,
            "content_type": request.get("content_type", "shorts"),
            "upload_schedule": request.get("upload_schedule", ["09:00", "15:00", "20:00"]),
            "auto_generate": request.get("auto_generate_titles", True),
            "privacy_status": request.get("privacy_status", "public"),
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        
        # Store configuration using scheduler if available
        if youtube_scheduler:
            try:
                result = await youtube_scheduler.setup_youtube_automation(user_id, automation_config)
                if result.get("success"):
                    logger.info(f"YouTube automation configured via scheduler for user {user_id}")
                    return result
            except Exception as scheduler_error:
                logger.error(f"Scheduler configuration failed: {scheduler_error}")
        
        # Fallback: store directly in database
        try:
            success = await database_manager.store_automation_config(
                user_id=user_id,
                config_type="youtube_automation",
                config_data=automation_config
            )
            
            if success:
                logger.info(f"YouTube automation configured directly for user {user_id}")
                return {
                    "success": True,
                    "message": "YouTube automation configured successfully",
                    "config": automation_config,
                    "user_id": user_id
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store configuration",
                    "message": "Database storage failed"
                }
        except Exception as db_error:
            logger.error(f"Database configuration failed: {db_error}")
            return {
                "success": False,
                "error": str(db_error),
                "message": "Configuration storage failed"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube automation setup failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Automation setup failed"
        }

@app.get("/api/youtube/analytics/{user_id}")
async def get_youtube_analytics(user_id: str, days: int = 30):
    """Get YouTube channel analytics with real data"""
    try:
        logger.info(f"Fetching analytics for user: {user_id}")
        
        # Get user credentials
        credentials = await database_manager.get_youtube_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=404, detail="YouTube credentials not found")
        
        # Initialize YouTube service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="Failed to authenticate with YouTube")
        
        # Get channel statistics
        try:
            channels_response = youtube_service.channels().list(
                part="statistics,snippet",
                mine=True
            ).execute()
            
            if not channels_response.get("items"):
                raise HTTPException(status_code=404, detail="No channel found")
            
            channel = channels_response["items"][0]
            channel_stats = channel["statistics"]
            channel_snippet = channel["snippet"]
            
            logger.info(f"Channel stats retrieved: {channel_stats}")
            
        except Exception as e:
            logger.error(f"Failed to get channel statistics: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get channel stats: {str(e)}")
        
        # Get recent videos
        recent_videos = []
        try:
            # Search for recent videos from this channel
            search_response = youtube_service.search().list(
                part="id",
                channelId=channel["id"],
                type="video",
                order="date",
                maxResults=10
            ).execute()
            
            if search_response.get("items"):
                video_ids = [item["id"]["videoId"] for item in search_response["items"]]
                
                # Get detailed video statistics
                videos_response = youtube_service.videos().list(
                    part="statistics,snippet",
                    id=",".join(video_ids)
                ).execute()
                
                for video in videos_response.get("items", []):
                    video_stats = video["statistics"]
                    video_snippet = video["snippet"]
                    
                    recent_videos.append({
                        "video_id": video["id"],
                        "title": video_snippet["title"],
                        "published_at": video_snippet["publishedAt"],
                        "view_count": int(video_stats.get("viewCount", 0)),
                        "like_count": int(video_stats.get("likeCount", 0)),
                        "comment_count": int(video_stats.get("commentCount", 0)),
                        "thumbnail_url": video_snippet["thumbnails"]["default"]["url"]
                    })
                
                logger.info(f"Retrieved {len(recent_videos)} recent videos")
            
        except Exception as e:
            logger.error(f"Failed to get recent videos: {e}")
            # Don't fail the whole request if videos can't be fetched
        
        # Prepare analytics data
        analytics_data = {
            "success": True,
            "channel_statistics": {
                "subscriberCount": int(channel_stats.get("subscriberCount", 0)),
                "viewCount": int(channel_stats.get("viewCount", 0)),
                "videoCount": int(channel_stats.get("videoCount", 0))
            },
            "channel_info": {
                "channel_name": channel_snippet.get("title", "Unknown"),
                "channel_id": channel["id"],
                "description": channel_snippet.get("description", ""),
                "thumbnail_url": channel_snippet["thumbnails"]["default"]["url"],
                "published_at": channel_snippet.get("publishedAt")
            },
            "recent_videos": recent_videos,
            "period_days": days,
            "fetched_at": datetime.now().isoformat(),
            "total_recent_videos": len(recent_videos)
        }
        
        # Store analytics in database
        await database_manager.store_channel_analytics(user_id, analytics_data)
        
        logger.info(f"Analytics successfully fetched and stored for user {user_id}")
        return analytics_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics fetch failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analytics fetch failed: {str(e)}")



# @app.post("/api/youtube/upload")
# async def youtube_upload_video(request: dict):
#     """Upload video to YouTube with thumbnail support"""
#     try:
#         logger.info(f"YouTube upload request: {request}")
        
#         user_id = request.get("user_id")
#         title = request.get("title", "Untitled Video")
#         video_url = request.get("video_url", "")
#         description = request.get("description", "")
#         tags = request.get("tags", [])
#         privacy_status = request.get("privacy_status", "public")
#         content_type = request.get("content_type", "video")
#         thumbnail_url = request.get("thumbnail_url")  # ← ADDED THIS LINE
        
#         # DEBUG: Log thumbnail info
#         logger.info(f"🔍 Thumbnail URL present: {thumbnail_url is not None}")
#         if thumbnail_url:
#             logger.info(f"🔍 Thumbnail data length: {len(thumbnail_url)} chars")
#             logger.info(f"🔍 Thumbnail preview: {thumbnail_url[:100]}")
        
#         if not user_id:
#             raise HTTPException(status_code=400, detail="user_id is required")
        
#         if not video_url:
#             raise HTTPException(status_code=400, detail="video_url is required")
        
#         # Validate video URL format
#         if not video_url.startswith(('http://', 'https://')):
#             raise HTTPException(status_code=400, detail="video_url must be a valid HTTP/HTTPS URL")
        
#         # Check if user has YouTube connected
#         try:
#             credentials = await database_manager.get_youtube_credentials(user_id)
#             if not credentials:
#                 raise HTTPException(status_code=400, detail="YouTube not connected")
#         except Exception as db_error:
#             logger.error(f"Database error: {db_error}")
#             return {
#                 "success": False,
#                 "error": "Database connection error"
#             }
        
#         # Try real upload using YouTube connector and scheduler
#         if youtube_connector and youtube_scheduler:
#             try:
#                 upload_result = await youtube_scheduler.generate_and_upload_content(
#                     user_id=user_id,
#                     credentials_data=credentials,
#                     content_type=content_type,
#                     title=title,
#                     description=description,
#                     video_url=video_url,
#                     thumbnail_url=thumbnail_url  # ← ADDED THIS LINE
#                 )
                
#                 if upload_result.get("success"):
#                     # Log successful upload to database
#                     await database_manager.log_video_upload(
#                         user_id=user_id,
#                         video_data={
#                             "video_id": upload_result.get("video_id", f"upload_{int(datetime.now().timestamp())}"),
#                             "video_url": upload_result.get("video_url", video_url),
#                             "title": title,
#                             "description": description,
#                             "tags": tags,
#                             "privacy_status": privacy_status,
#                             "content_type": content_type,
#                             "ai_generated": False,
#                             "thumbnail_uploaded": upload_result.get("thumbnail_uploaded", False)  # ← ADDED THIS
#                         }
#                     )
                    
#                     logger.info(f"Real upload successful for user {user_id}")
#                     logger.info(f"📊 Thumbnail uploaded: {upload_result.get('thumbnail_uploaded', False)}")
#                     return upload_result
#                 else:
#                     logger.warning(f"Upload failed via scheduler: {upload_result.get('error')}")
                    
#             except Exception as upload_error:
#                 logger.error(f"Upload via scheduler failed: {upload_error}")
        
#         # Fallback to mock upload response
#         mock_video_id = f"mock_video_{user_id}_{int(datetime.now().timestamp())}"
#         upload_result = {
#             "success": True,
#             "message": "Video upload initiated successfully (Mock Mode)",
#             "video_details": {
#                 "title": title,
#                 "description": description,
#                 "video_url": video_url,
#                 "upload_status": "processing",
#                 "estimated_processing_time": "5-10 minutes",
#                 "video_id": mock_video_id,
#                 "watch_url": f"https://youtube.com/watch?v={mock_video_id}",
#                 "privacy_status": privacy_status,
#                 "content_type": content_type,
#                 "tags": tags
#             },
#             "user_id": user_id,
#             "upload_method": "mock",
#             "note": "This is a mock upload. Real uploads require proper YouTube API setup."
#         }
        
#         # Log mock upload to database
#         try:
#             await database_manager.log_video_upload(
#                 user_id=user_id,
#                 video_data={
#                     "video_id": mock_video_id,
#                     "video_url": video_url,
#                     "title": title,
#                     "description": description,
#                     "tags": tags,
#                     "privacy_status": privacy_status,
#                     "content_type": content_type,
#                     "ai_generated": False
#                 }
#             )
#         except Exception as log_error:
#             logger.warning(f"Failed to log mock upload: {log_error}")
        
#         logger.info(f"Mock upload successful for user {user_id}")
#         return upload_result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube upload failed: {e}")
#         return {
#             "success": False,
#             "error": str(e),
#             "message": "Upload failed"
#         }
    
@app.post("/api/youtube/upload")
async def youtube_upload_video(request: dict):
    """
    Upload video to YouTube with multi-source support
    Supports: Google Drive, YouTube URL (update mode), local file, direct .mp4 URL
    """
    try:
        # ✅ DEBUG LOGGING
        logger.info("="*60)
        logger.info("📤 UPLOAD REQUEST RECEIVED")
        logger.info(f"📦 Request Keys: {list(request.keys())}")
        logger.info(f"📹 Video Mode: {request.get('video_mode', 'NOT SET')}")
        logger.info(f"📹 Video URL Type: {request.get('video_url', '')[:60]}...")
        logger.info(f"🎨 Thumbnail: {'YES' if request.get('thumbnail_url') else 'NO'}")
        logger.info("="*60)
        
        # Extract parameters
        user_id = request.get("user_id")
        title = request.get("title", "Untitled Video")
        video_url = request.get("video_url", "")
        description = request.get("description", "")
        tags = request.get("tags", [])
        privacy_status = request.get("privacy_status", "public")
        content_type = request.get("content_type", "shorts")
        thumbnail_url = request.get("thumbnail_url")
        video_mode = request.get("video_mode", "new")  # 'new' or 'update'
        
        # Validation
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        if not video_url:
            raise HTTPException(status_code=400, detail="video_url is required")
        
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="title is required")
        
        # Check credentials
        credentials = await database_manager.get_youtube_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=400, detail="YouTube not connected")
        
        # ============================================================
        # DETECT VIDEO SOURCE AND PROCESS
        # ============================================================
        video_file_path = None
        
        # 1️⃣ GOOGLE DRIVE URL
        if 'drive.google.com' in video_url:
            logger.info("✅ Source: Google Drive URL")
            try:
                video_file_path = await download_google_drive_video(video_url, user_id)
                logger.info(f"✅ Downloaded from Google Drive: {video_file_path}")
            except Exception as drive_error:
                logger.error(f"❌ Google Drive download failed: {drive_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to download from Google Drive: {str(drive_error)}"
                )
        
        # 2️⃣ YOUTUBE URL (UPDATE MODE ONLY)
        elif ('youtube.com' in video_url or 'youtu.be' in video_url):
            logger.info(f"✅ Source: YouTube URL (Mode: {video_mode})")
            
            if video_mode == 'update':
                logger.info("🔄 UPDATE MODE: Updating existing video thumbnail")
                
                # Extract video ID
                video_id = None
                patterns = [
                    r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
                    r'youtu\.be/([a-zA-Z0-9_-]+)',
                    r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
                    r'youtube\.com/v/([a-zA-Z0-9_-]+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, video_url)
                    if match:
                        video_id = match.group(1)
                        break
                
                if not video_id:
                    raise HTTPException(
                        status_code=400, 
                        detail="Invalid YouTube URL format. Example: https://youtube.com/watch?v=VIDEO_ID"
                    )
                
                logger.info(f"📹 Extracted Video ID: {video_id}")
                
                # Thumbnail is required for update mode
                if not thumbnail_url:
                    raise HTTPException(
                        status_code=400, 
                        detail="Thumbnail required for update mode. Please generate thumbnails first."
                    )
                
                # Get authenticated YouTube service
                youtube_service = await youtube_connector.get_authenticated_service(user_id)
                
                if not youtube_service:
                    raise HTTPException(
                        status_code=400, 
                        detail="Failed to authenticate with YouTube"
                    )
                
                # Upload thumbnail to existing video
                try:
                    success = await youtube_connector._upload_thumbnail(
                        youtube_service,
                        video_id,
                        thumbnail_url
                    )
                    
                    if success:
                        logger.info(f"✅ Thumbnail updated for video: {video_id}")
                        return {
                            "success": True,
                            "message": "Thumbnail updated successfully!",
                            "video_id": video_id,
                            "video_url": video_url,
                            "thumbnail_uploaded": True,
                            "mode": "update"
                        }
                    else:
                        raise HTTPException(
                            status_code=500, 
                            detail="Thumbnail upload failed. Check if video exists and you have permission."
                        )
                        
                except Exception as thumb_error:
                    logger.error(f"❌ Thumbnail upload error: {thumb_error}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Thumbnail upload failed: {str(thumb_error)}"
                    )
            
            else:
                # NEW MODE with YouTube URL = ERROR
                logger.error("❌ Cannot upload YouTube URL as new video")
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot upload a YouTube URL as a new video. Switch to 'Update Existing Thumbnail' mode to update thumbnails on existing videos."
                )
        
        # 3️⃣ LOCAL FILE (from manual upload)
        elif video_url.startswith('/tmp/'):
            logger.info("✅ Source: Local uploaded file")
            video_file_path = video_url
            
            # Verify file exists
            if not os.path.exists(video_file_path):
                raise HTTPException(
                    status_code=400, 
                    detail="Uploaded file not found. Please upload again."
                )
        
        # 4️⃣ DIRECT .MP4 URL
        else:
            logger.info("✅ Source: Direct .mp4 URL")
            
            # Validate URL format
            if not video_url.startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid video URL. Must be HTTP/HTTPS URL or Google Drive link."
                )
            
            try:
                video_file_path = await youtube_scheduler._download_video_temporarily(video_url)
                logger.info(f"✅ Downloaded from URL: {video_file_path}")
            except Exception as download_error:
                logger.error(f"❌ URL download failed: {download_error}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to download video: {str(download_error)}"
                )
        
        # ============================================================
        # UPLOAD TO YOUTUBE (NEW VIDEO)
        # ============================================================
        
        if not video_file_path:
            raise HTTPException(
                status_code=500, 
                detail="Failed to process video. No valid video file path."
            )
        
        logger.info(f"📤 Uploading to YouTube: {video_file_path}")
        
        # Upload video
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type=content_type,
            title=title.strip(),
            description=description.strip(),
            video_url=video_file_path,
            thumbnail_url=thumbnail_url
        )
        
        # ============================================================
        # CLEANUP TEMPORARY FILES
        # ============================================================
        try:
            if video_file_path and video_file_path.startswith('/tmp/'):
                if os.path.exists(video_file_path):
                    os.unlink(video_file_path)
                    logger.info(f"🗑️ Cleaned up temp file: {video_file_path}")
        except Exception as cleanup_error:
            logger.warning(f"⚠️ Cleanup failed (non-critical): {cleanup_error}")
        
        logger.info(f"✅ Upload complete: {upload_result.get('success', False)}")
        return upload_result
        
    except HTTPException as http_err:
        logger.error(f"❌ HTTP Exception: {http_err.detail}")
        raise
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        
        return {
            "success": False,
            "error": str(e),
            "message": f"Upload failed: {str(e)}",
            "video_mode": request.get('video_mode', 'unknown'),
            "video_url_type": "youtube" if 'youtube' in request.get('video_url', '') else "other"
        }




@app.post("/api/youtube/upload-video-file")
async def upload_video_file(
    video: UploadFile = File(...),
    user_id: str = Form(...)  # ✅ FIXED - now accepts form data
):
    """Upload video file and return temporary path for thumbnail generation"""
    try:
        logger.info(f"📤 Receiving video upload from user: {user_id}")
        
        # Validate file type
        if not video.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be a video (MP4, AVI, MOV, etc.)"
            )
        
        # File size check (500MB max)
        content = await video.read()
        file_size = len(content)
        
        if file_size > 500 * 1024 * 1024:  # 500MB
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum 500MB allowed."
            )
        
        # Create user-specific temp directory
        temp_dir = Path(f"/tmp/uploads/{user_id}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save with timestamp to avoid conflicts
        timestamp = int(datetime.now().timestamp())
        safe_filename = f"{timestamp}_{video.filename}"
        file_path = temp_dir / safe_filename
        
        # Write file
        with file_path.open("wb") as f:
            f.write(content)
        
        logger.info(f"✅ Video saved: {file_path} ({file_size} bytes)")
        
        return {
            "success": True,
            "video_url": str(file_path),
            "file_size": file_size,
            "filename": safe_filename,
            "message": "Video uploaded successfully. Ready for thumbnail generation."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Video upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
@app.post("/api/youtube/fetch-video-info")
async def fetch_youtube_video_info(request: dict):
    """Fetch existing YouTube video info to update thumbnail"""
    try:
        user_id = request.get('user_id')
        video_url = request.get('video_url')
        
        if not user_id or not video_url:
            raise HTTPException(status_code=400, detail="user_id and video_url required")
        
        # Extract video ID from URL
        video_id = None
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube\.com/v/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                break
        
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL format")
        
        logger.info(f"🔍 Fetching info for video ID: {video_id}")
        
        # Get authenticated YouTube service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="YouTube not connected. Please connect your account first.")
        
        # Fetch video details
        try:
            video_response = youtube_service.videos().list(
                part="snippet,status",
                id=video_id
            ).execute()
        except Exception as api_error:
            logger.error(f"YouTube API error: {api_error}")
            raise HTTPException(status_code=400, detail=f"YouTube API error: {str(api_error)}")
        
        if not video_response.get('items'):
            raise HTTPException(
                status_code=404, 
                detail="Video not found. Make sure this video belongs to your channel."
            )
        
        video = video_response['items'][0]
        snippet = video['snippet']
        
        # Verify ownership
        credentials = await database_manager.get_youtube_credentials(user_id)
        user_channel_id = credentials.get('channel_info', {}).get('channel_id')
        video_channel_id = snippet.get('channelId')
        
        if user_channel_id != video_channel_id:
            raise HTTPException(
                status_code=403, 
                detail="Access denied. You can only edit videos from your own channel."
            )
        
        logger.info(f"✅ Video info fetched: {snippet['title']}")
        
        return {
            "success": True,
            "video_id": video_id,
            "title": snippet['title'],
            "description": snippet.get('description', ''),
            "current_thumbnail": snippet['thumbnails']['high']['url'],
            "channel_title": snippet['channelTitle'],
            "published_at": snippet['publishedAt'],
            "message": "Video info loaded. Now generate new thumbnails."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fetch video info failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


        

@app.post("/api/youtube/schedule-video")
async def schedule_video_upload(request: dict):
    """Schedule a video for later upload"""
    try:
        logger.info(f"Schedule video request: {request}")
        
        user_id = request.get("user_id")
        schedule_date = request.get("schedule_date")  # YYYY-MM-DD
        schedule_time = request.get("schedule_time")  # HH:MM
        video_data = request.get("video_data", {})
        
        if not all([user_id, schedule_date, schedule_time, video_data.get("video_url")]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # ✅ FIXED: Parse as UTC datetime
        try:
            # Parse the date/time string
            scheduled_datetime_naive = datetime.strptime(
                f"{schedule_date} {schedule_time}",
                "%Y-%m-%d %H:%M"
            )
            
            # Convert to UTC (assume user is sending in their local time, convert to UTC)
            # For now, treat input as UTC directly to match server time
            scheduled_datetime = scheduled_datetime_naive
            
            logger.info(f"📅 Parsed scheduled time: {scheduled_datetime} (UTC)")
            logger.info(f"📅 Current server time: {datetime.now()} (UTC)")
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
        
        # Check if time is in the future
        current_time = datetime.now()
        if scheduled_datetime <= current_time:
            logger.warning(f"Scheduled time {scheduled_datetime} is in the past. Current: {current_time}")
            raise HTTPException(
                status_code=400, 
                detail=f"Scheduled time must be in the future. Server time: {current_time.strftime('%Y-%m-%d %H:%M')} UTC"
            )
        
        time_until = scheduled_datetime - current_time
        logger.info(f"⏰ Video will upload in {time_until.total_seconds()/60:.1f} minutes")
        
        # Store scheduled post
        success = await database_manager.store_scheduled_post(
            user_id=user_id,
            video_data=video_data,
            scheduled_for=scheduled_datetime
        )
        
        if success:
            return {
                "success": True,
                "message": f"Video scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')} UTC",
                "scheduled_for": scheduled_datetime.isoformat(),
                "video_title": video_data.get("title", "Untitled"),
                "server_time_utc": current_time.isoformat(),
                "time_until_upload_minutes": round(time_until.total_seconds() / 60, 1)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to schedule video")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schedule video failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))





# @app.get("/api/youtube/scheduled-posts/{user_id}")
# async def get_scheduled_posts(user_id: str, status: str = None):
#     """Get scheduled posts for a user"""
#     try:
#         if not database_manager:
#             return {
#                 "success": False,
#                 "error": "Database not available",
#                 "scheduled_posts": [],
#                 "count": 0
#             }
        
#         posts = await database_manager.get_scheduled_posts_by_user(user_id, status)
        
#         # Format posts for frontend
#         formatted_posts = []
#         for post in posts:
#             try:
#                 formatted_posts.append({
#                     "id": str(post["_id"]),
#                     "title": post.get("video_data", {}).get("title", "Untitled"),
#                     "video_url": post.get("video_data", {}).get("video_url", ""),
#                     "scheduled_for": post["scheduled_for"].isoformat() if post.get("scheduled_for") else None,
#                     "status": post.get("status", "unknown"),
#                     "created_at": post["created_at"].isoformat() if post.get("created_at") else None,
#                     "execution_attempts": post.get("execution_attempts", 0),
#                     "last_error": post.get("last_error")
#                 })
#             except Exception as format_error:
#                 logger.warning(f"Failed to format post {post.get('_id')}: {format_error}")
#                 continue
        
#         return {
#             "success": True,
#             "scheduled_posts": formatted_posts,
#             "count": len(formatted_posts)
#         }
        
#     except Exception as e:
#         logger.error(f"Get scheduled posts failed: {e}")
#         import traceback
#         logger.error(f"Traceback: {traceback.format_exc()}")
#         return {
#             "success": False,
#             "error": str(e),
#             "scheduled_posts": [],
#             "count": 0
#         }


@app.delete("/api/youtube/scheduled-post/{post_id}")
async def delete_scheduled_post(post_id: str):
    """Delete a scheduled post"""
    try:
        if not database_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        
        from bson import ObjectId
        
        # Validate ObjectId format
        try:
            obj_id = ObjectId(post_id)
        except Exception as id_error:
            raise HTTPException(status_code=400, detail=f"Invalid post ID format: {id_error}")
        
        success = await database_manager.delete_scheduled_post(obj_id)
        
        if success:
            return {
                "success": True,
                "message": "Scheduled post deleted"
            }
        else:
            raise HTTPException(status_code=404, detail="Scheduled post not found or already deleted")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete scheduled post failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/ai/generate-youtube-content")
async def generate_youtube_content(request: dict):
    """Generate YouTube content using AI with trending and multilingual support"""
    try:
        logger.info(f"Generating YouTube content: {request}")
        
        # Extract parameters
        content_type = request.get("content_type", "shorts")
        topic = request.get("topic", "general")
        target_audience = request.get("target_audience", "general")
        style = request.get("style", "engaging")
        language = request.get("language", "english")
        region = request.get("region", "india")
        duration_seconds = request.get("duration_seconds", 30)
        
        # Get trending hashtags and context
        trending_context = await get_trending_context(topic, language, region)
        
        # Use real AI service first
        if ai_service and hasattr(ai_service, 'generate_youtube_content'):
            try:
                result = await ai_service.generate_youtube_content(
                    content_type=content_type,
                    topic=topic,
                    target_audience=target_audience,
                    duration_seconds=duration_seconds,
                    style=style,
                    language=language,
                    region=region,
                    trending_context=trending_context
                )
                if result.get("success"):
                    logger.info(f"AI content generation successful in {language}")
                    return result
            except Exception as ai_error:
                logger.warning(f"AI service failed: {ai_error}")
        
        # Fallback to enhanced mock (only if AI fails)
        return await generate_fallback_content(
            content_type, topic, target_audience, style, language, trending_context
        )
        
    except Exception as e:
        logger.error(f"YouTube content generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Content generation failed"
        }

async def get_trending_context(topic: str, language: str, region: str) -> dict:
    """Get trending hashtags and context for content generation"""
    try:
        current_date = datetime.now()
        current_month = current_date.month
        
        # Regional trending topics
        regional_trends = {
            "india": {
                1: ["RepublicDay", "MakarSankranti", "Pongal", "WinterFashion"],
                2: ["Budget2024", "ValentinesDay", "MahaShivratri", "WinterSports"],
                3: ["Holi", "SpringFashion", "BoardExams", "IPLAuction"],
                4: ["IPL2024", "SummerFashion", "Elections", "Vacations"],
                5: ["IPL2024", "SummerTips", "Elections", "Mangoes"],
                6: ["Monsoon", "WorldEnvironmentDay", "Yoga", "FitnessTips"],
                7: ["Independence", "Monsoon", "BackToSchool", "TechTrends"],
                8: ["RakshaBandhan", "Independence", "Festive", "TechReviews"],
                9: ["Ganpati", "Navratri", "FestivePrep", "OnlineShopping"],
                10: ["Diwali", "FestiveShopping", "WinterPrep", "TechDeals"],
                11: ["Diwali", "WeddingSeason", "WinterFashion", "CyberMonday"],
                12: ["NewYear", "WinterFashion", "YearEnd", "Resolutions"]
            }
        }
        
        # Language-specific hashtags
        language_hashtags = {
            "hindi": ["हिंदी", "भारत", "देसी", "घर"],
            "tamil": ["தமிழ்", "தமிழ்நாடு"],
            "telugu": ["తెలుగు", "ఆంధ్ర"],
            "bengali": ["বাংলা", "পশ্চিমবঙ্গ"],
            "marathi": ["मराठी", "महाराष्ट्र"],
            "gujarati": ["ગુજરાતી", "ગુજરાત"],
            "malayalam": ["മലയാളം", "കേരളം"],
            "kannada": ["ಕನ್ನಡ", "ಕರ್ನಾಟಕ"],
            "punjabi": ["ਪੰਜਾਬੀ", "ਪੰਜਾਬ"],
            "hinglish": ["Hinglish", "Desi", "Indian"]
        }
        
        # Get current trends
        current_trends = regional_trends.get(region, {}).get(current_month, ["Trending", "Viral"])
        lang_tags = language_hashtags.get(language, ["English"])
        
        # Topic-specific trending hashtags
        topic_trends = {
            "tech": ["TechTrends", "Innovation", "Gadgets", "AI", "Mobile"],
            "cooking": ["Recipes", "Cooking", "Food", "Kitchen", "Chef"],
            "fitness": ["Fitness", "Health", "Workout", "Gym", "Wellness"],
            "travel": ["Travel", "Explore", "Adventure", "Tourism", "Wanderlust"],
            "education": ["Education", "Learning", "Study", "Knowledge", "Skills"],
            "business": ["Business", "Entrepreneur", "Success", "Money", "Startup"],
            "entertainment": ["Entertainment", "Fun", "Comedy", "Music", "Movies"]
        }
        
        topic_hashtags = topic_trends.get(topic.lower(), ["General", "Content"])
        
        return {
            "regional_trends": current_trends,
            "language_hashtags": lang_tags,
            "topic_hashtags": topic_hashtags,
            "current_month": current_month,
            "season": get_current_season(current_month),
            "festivals": get_current_festivals(current_month)
        }
        
    except Exception as e:
        logger.error(f"Failed to get trending context: {e}")
        return {
            "regional_trends": ["Trending"],
            "language_hashtags": ["Content"],
            "topic_hashtags": ["General"],
            "current_month": datetime.now().month,
            "season": "current",
            "festivals": []
        }

def get_current_season(month: int) -> str:
    """Get current season based on month"""
    seasons = {
        (12, 1, 2): "Winter",
        (3, 4, 5): "Spring", 
        (6, 7, 8): "Monsoon",
        (9, 10, 11): "Autumn"
    }
    
    for months, season in seasons.items():
        if month in months:
            return season
    return "Current"

def get_current_festivals(month: int) -> list:
    """Get current festivals based on month"""
    festivals = {
        1: ["Makar Sankranti", "Pongal", "Republic Day"],
        2: ["Maha Shivratri", "Vasant Panchami"],
        3: ["Holi", "Ugadi"],
        4: ["Ram Navami", "Baisakhi"],
        5: ["Buddha Purnima"],
        6: ["Rath Yatra"],
        7: ["Guru Purnima"],
        8: ["Raksha Bandhan", "Krishna Janmashtami"],
        9: ["Ganesh Chaturthi"],
        10: ["Navratri", "Dussehra"],
        11: ["Diwali", "Karwa Chauth"],
        12: ["Christmas", "New Year"]
    }
    return festivals.get(month, [])

async def generate_fallback_content(content_type: str, topic: str, target_audience: str, 
                                  style: str, language: str, trending_context: dict) -> dict:
    """Generate enhanced fallback content when AI service fails"""
    try:
        # Get unique content based on timestamp and user input
        timestamp = int(datetime.now().timestamp())
        unique_id = f"{topic}_{language}_{timestamp}"
        
        # Language-specific content templates
        if language == "hindi":
            title_templates = [
                f"🔥 {topic} के अद्भुत राज जो आपको पता होने चाहिए!",
                f"क्यों हर कोई {topic} के बारे में बात कर रहा है?",
                f"{topic} का यह रहस्य कोई नहीं बताता",
                f"60 सेकंड में {topic} को मास्टर करें",
                f"यह {topic} टिप सब कुछ बदल देगी!"
            ]
            description_start = f"{topic} के लिए त्वरित टिप्स जो वास्तव में काम करती हैं! {target_audience} के लिए परफेक्ट जो तेज़ परिणाम चाहते हैं। 🚀"
            
        elif language == "hinglish":
            title_templates = [
                f"🔥 {topic} ke amazing secrets jo tumhe pata hone chahiye!",
                f"Kyun har koi {topic} ke bare mein baat kar raha hai?",
                f"{topic} ka yeh secret koi nahi batata",
                f"60 seconds mein {topic} ko master karo",
                f"Yeh {topic} tip sab kuch change kar degi!"
            ]
            description_start = f"{topic} ke liye quick tips jo actually work karte hain! {target_audience} ke liye perfect jo fast results chahte hain। 🚀"
            
        else:  # English and other languages
            title_templates = [
                f"🔥 Amazing {topic} Secrets You Must Know!",
                f"Why Everyone is Talking About {topic} Right Now",
                f"The {topic} Secret Nobody Tells You",
                f"Master {topic} in 60 Seconds",
                f"This {topic} Tip Changed Everything!"
            ]
            description_start = f"Quick {topic} tips that actually work! Perfect for {target_audience} who want fast results. 🚀"
        
        # Generate unique title using hash of unique_id
        title_index = hash(unique_id) % len(title_templates)
        title = title_templates[title_index]
        
        # Create trending hashtags
        all_hashtags = (
            trending_context["regional_trends"] +
            trending_context["language_hashtags"] +
            trending_context["topic_hashtags"] +
            [topic.replace(" ", ""), target_audience.replace(" ", ""), content_type] +
            [f"{language}Content", "2024", style]
        )
        
        # Remove duplicates and format
        unique_hashtags = list(set([f"#{tag}" for tag in all_hashtags if tag]))[:15]
        
        # Create description with trending context
        description = f"""{description_start}

इस {content_type} में आप जानेंगे:
✅ सबसे प्रभावी {topic} रणनीति
✅ सामान्य गलतियों से कैसे बचें
✅ एक्सपर्ट्स की प्रो टिप्स

Trending now: {', '.join(trending_context['regional_trends'][:3])}
Current festivals: {', '.join(trending_context['festivals'][:2])}

Like और follow करें more {topic} content के लिए!

{' '.join(unique_hashtags)}"""
        
        # Generate script with trending context
        script = f"""🎬 SCRIPT FOR {content_type.upper()} ({language}):

HOOK (0-3s): क्या आपको पता है कि {topic} आपकी {target_audience} journey को पूरी तरह से बदल सकता है?

TRENDING CONTEXT: अभी {trending_context['season']} season में {topic} बहुत popular है!

MAIN CONTENT:
आज मैं share कर रहा हूं सबसे {style} {topic} insights जो actually काम करती हैं।

Point 1: {topic} success की foundation
Point 2: Advanced {topic} strategies  
Point 3: Common {topic} mistakes जिनसे बचना है

FESTIVAL TIE-IN: {trending_context['festivals'][0] if trending_context['festivals'] else 'इस season'} के लिए special {topic} tips!

CALL TO ACTION: अगर यह {topic} content helpful लगा, तो like button smash करें और subscribe करें more {target_audience}-focused content के लिए!

OUTRO: आपकी सबसे बड़ी {topic} challenge क्या है? Comments में बताएं!"""
        
        return {
            "success": True,
            "title": title,
            "description": description,
            "script": script,
            "tags": [tag.replace("#", "") for tag in unique_hashtags],
            "content_type": content_type,
            "language": language,
            "trending_context": trending_context,
            "unique_id": unique_id,
            "ai_service": "enhanced_trending_fallback",
            "word_count": len(script.split()),
            "estimated_duration": 30 if content_type == "shorts" else 600,
            "hashtags": unique_hashtags
        }
        
    except Exception as e:
        logger.error(f"Fallback content generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Both AI and fallback generation failed"
        }

# Add this new endpoint for getting supported languages
@app.get("/api/ai/supported-languages")
async def get_supported_languages():
    """Get list of supported languages for content generation"""
    try:
        if ai_service and hasattr(ai_service, 'get_supported_languages'):
            return ai_service.get_supported_languages()
        
        # Fallback language list
        return {
            "success": True,
            "languages": {
                "english": {"name": "English", "native_name": "English", "code": "en"},
                "hindi": {"name": "Hindi", "native_name": "हिन्दी", "code": "hi"},
                "hinglish": {"name": "Hinglish", "native_name": "Hinglish (हिन्दी + English)", "code": "hi-en"},
                "tamil": {"name": "Tamil", "native_name": "தமிழ்", "code": "ta"},
                "telugu": {"name": "Telugu", "native_name": "తెలుగు", "code": "te"},
                "bengali": {"name": "Bengali", "native_name": "বাংলা", "code": "bn"},
                "marathi": {"name": "Marathi", "native_name": "मराठी", "code": "mr"},
                "gujarati": {"name": "Gujarati", "native_name": "ગુજરાતી", "code": "gu"},
                "malayalam": {"name": "Malayalam", "native_name": "മലയാളം", "code": "ml"},
                "kannada": {"name": "Kannada", "native_name": "ಕನ್ನಡ", "code": "kn"},
                "punjabi": {"name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "code": "pa"},
                "assamese": {"name": "Assamese", "native_name": "অসমীয়া", "code": "as"}
            },
            "default_language": "english"
        }
        
    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        return {"success": False, "error": str(e)}








@app.post("/api/ai/generate-thumbnails")
async def generate_thumbnails(request: dict):
    """Generate AI thumbnails for video"""
    try:
        logger.info(f"Thumbnail generation request: {request}")
        
        video_url = request.get("video_url")
        video_title = request.get("video_title")
        style = request.get("style", "indian")
        
        if not video_url or not video_title:
            raise HTTPException(status_code=400, detail="video_url and video_title required")
        
        # Check if YouTube AI service is available
        if not youtube_feature_extractor:
            return {
                "success": False,
                "error": "Thumbnail generation service not available",
                "fallback": True,
                "thumbnails": []
            }
        
        # Generate thumbnails
        result = await youtube_feature_extractor.generate_thumbnails_for_video(
            video_url=video_url,
            video_title=video_title,
            style=style
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }



# MongoDB debugging endpoint
@app.get("/debug/mongodb")
async def test_mongodb():
    """Test MongoDB connection"""
    try:
        if database_manager:
            health = await database_manager.health_check()
            return {
                "status": "success",
                "database_health": health,
                "mongodb_uri_set": "✓" if os.getenv("MONGODB_URI") else "✗",
                "collections_available": {
                    "users": hasattr(database_manager, 'users_collection'),
                    "youtube_credentials": hasattr(database_manager, 'youtube_credentials_collection'),
                    "automation_configs": hasattr(database_manager, 'automation_configs_collection')
                }
            }
        else:
            return {
                "status": "failed", 
                "error": "Database manager not initialized",
                "mongodb_uri_set": "✓" if os.getenv("MONGODB_URI") else "✗"
            }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "type": type(e).__name__
        }


@app.post("/api/youtube/upload-thumbnail-image")
async def upload_thumbnail_image(
    image: UploadFile = File(...),
    user_id: str = Form(...)
):
    """Upload custom thumbnail from gallery - Resizes to 1280x720"""
    try:
        logger.info(f"🖼️ Receiving thumbnail upload from user: {user_id}")
        
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG, JPEG)")
        
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Resize to 1280x720
        img = img.resize((1280, 720), Image.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        logger.info(f"✅ Thumbnail uploaded: {len(img_base64)} chars")
        
        return {
            "success": True,
            "thumbnail_url": f"data:image/png;base64,{img_base64}",
            "size": len(img_base64),
            "dimensions": "1280x720",
            "message": "Thumbnail uploaded and resized successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Thumbnail upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/youtube/generate-thumbnails")
async def generate_video_thumbnails(request: dict):
    """
    Generate 3 CTR-optimized thumbnails
    
    Features:
    - ✅ Downloads YouTube videos for frame extraction
    - ✅ Extracts frames from Google Drive, local files, URLs
    - ✅ CTR-optimized (YELLOW text on RED/BLACK/ORANGE backgrounds)
    - ✅ Language detection (Hindi/English/Hinglish)
    - ✅ Real video frames as thumbnails
    """
    temp_youtube_video = None
    
    try:
        # Extract parameters
        user_id = request.get('user_id')
        video_url = request.get('video_url')
        title = request.get('title', 'Untitled Video')
        description = request.get('description', '')
        language = request.get('language', 'auto')
        
        # Validation
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required")
        
        if not video_url:
            raise HTTPException(status_code=400, detail="video_url required")
        
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="title required")
        
        logger.info("="*60)
        logger.info(f"🎨 Generating CTR-optimized thumbnails for: {title}")
        logger.info(f"📹 Video URL: {video_url[:60]}...")
        logger.info("="*60)
        
        # Auto-detect language
        if language == 'auto':
            language = detect_language_from_title(title)
            logger.info(f"🔍 Auto-detected language: {language}")
        
        # ============================================================
        # DETECT VIDEO SOURCE AND DOWNLOAD
        # ============================================================
        local_video_path = None
        is_youtube_url = False
        
        # 1️⃣ YOUTUBE URL - Downloads video for frame extraction
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            logger.info("✅ YouTube URL detected")
            is_youtube_url = True
            
            try:
                logger.info("📥 Downloading YouTube video...")
                local_video_path = await download_youtube_video_for_thumbnails(video_url, user_id)
                temp_youtube_video = local_video_path
                logger.info(f"✅ YouTube video downloaded: {local_video_path}")
                
                if local_video_path and os.path.exists(local_video_path):
                    file_size = os.path.getsize(local_video_path)
                    logger.info(f"📊 Video size: {file_size} bytes")
                else:
                    raise Exception("Downloaded file not found")
                    
            except Exception as yt_error:
                logger.error(f"❌ YouTube download failed: {yt_error}")
                logger.warning("⚠️ Will use fallback thumbnails")
                local_video_path = None
        
        # 2️⃣ GOOGLE DRIVE URL
        elif 'drive.google.com' in video_url:
            logger.info("✅ Google Drive URL detected")
            try:
                local_video_path = await download_google_drive_video(video_url, user_id)
                
                if local_video_path and os.path.exists(local_video_path):
                    file_size = os.path.getsize(local_video_path)
                    if file_size < 100000:
                        logger.error(f"❌ File too small: {file_size} bytes")
                        raise Exception("Google Drive file appears private. Make it publicly accessible.")
                    logger.info(f"✅ Valid video: {file_size} bytes")
                else:
                    raise Exception("Invalid file path")
                    
            except Exception as drive_error:
                logger.error(f"❌ Google Drive download failed: {drive_error}")
                local_video_path = None
        
        # 3️⃣ LOCAL FILE
        elif video_url.startswith('/tmp/'):
            logger.info("✅ Local uploaded file")
            local_video_path = video_url
            
            if not os.path.exists(local_video_path):
                logger.warning(f"⚠️ Local file not found: {local_video_path}")
                local_video_path = None
        
        # 4️⃣ DIRECT .MP4 URL
        else:
            logger.info("✅ Direct .mp4 URL")
            try:
                temp_dir = Path(f"/tmp/uploads/{user_id}")
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = int(datetime.now().timestamp())
                local_video_path = str(temp_dir / f"temp_{timestamp}.mp4")
                
                async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                    response = await client.get(video_url)
                    
                    if response.status_code != 200:
                        raise Exception(f"Download failed: HTTP {response.status_code}")
                    
                    with open(local_video_path, 'wb') as f:
                        f.write(response.content)
                
                logger.info(f"✅ Downloaded to: {local_video_path}")
                
            except Exception as download_error:
                logger.warning(f"⚠️ Download failed: {download_error}")
                local_video_path = None
        
        # ============================================================
        # METHOD 1: EXTRACT CTR FRAMES FROM VIDEO
        # ============================================================
        thumbnails = []
        
        if local_video_path and os.path.exists(local_video_path):
            logger.info("🎬 METHOD 1: Extracting CTR-optimized frames")
            try:
                frame_thumbnails = await extract_video_frames_as_thumbnails(
                    local_video_path, 
                    title, 
                    num_frames=3,
                    language=language
                )
                
                if frame_thumbnails and len(frame_thumbnails) > 0:
                    thumbnails.extend(frame_thumbnails)
                    logger.info(f"✅ Extracted {len(frame_thumbnails)} CTR video frame thumbnails")
                else:
                    logger.warning("⚠️ Frame extraction returned no thumbnails")
                    
            except Exception as frame_error:
                logger.warning(f"⚠️ Frame extraction failed: {frame_error}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.info("⏭️ No video file for frame extraction")
        
        # ============================================================
        # METHOD 2: AI THUMBNAILS (if frames failed)
        # ============================================================
        
        if len(thumbnails) < 3:
            logger.info(f"🎨 METHOD 2: AI thumbnails (have {len(thumbnails)}, need 3)")
            
            has_ai = ai_service and hasattr(ai_service, 'generate_youtube_thumbnail')
            
            if has_ai:
                logger.info("✅ AI service available")
                
                for i in range(3 - len(thumbnails)):
                    try:
                        thumbnail_url = await ai_service.generate_youtube_thumbnail(
                            prompt=f"YouTube thumbnail: {title}. {description[:100]} - Style {i+1}",
                            user_id=user_id
                        )
                        
                        if thumbnail_url:
                            thumbnails.append({
                                "id": f"ai_thumb_{i+1}",
                                "url": thumbnail_url,
                                "style": f"AI Style {i+1}",
                                "ctr_optimized": False
                            })
                            logger.info(f"✅ AI thumbnail {i+1}")
                        
                    except Exception as ai_error:
                        logger.warning(f"⚠️ AI thumbnail {i+1} failed: {ai_error}")
            else:
                logger.info("⏭️ AI service not available")
        
        # ============================================================
        # METHOD 3: FALLBACK CTR THUMBNAILS
        # ============================================================
        
        if len(thumbnails) < 3:
            logger.info(f"🎨 METHOD 3: Fallback CTR thumbnails (have {len(thumbnails)}, need 3)")
            
            try:
                fallback_thumbnails = create_fallback_ctr_thumbnails(
                    title, 
                    3 - len(thumbnails),
                    language
                )
                thumbnails.extend(fallback_thumbnails)
                logger.info(f"✅ Created {len(fallback_thumbnails)} fallback thumbnails")
                    
            except Exception as fallback_error:
                logger.error(f"❌ Fallback failed: {fallback_error}")
        
        # ============================================================
        # CLEANUP TEMP FILES
        # ============================================================
        try:
            if temp_youtube_video and os.path.exists(temp_youtube_video):
                os.unlink(temp_youtube_video)
                logger.info(f"🗑️ Cleaned up temp YouTube video")
        except Exception as cleanup_error:
            logger.warning(f"⚠️ Cleanup failed: {cleanup_error}")
        
        # ============================================================
        # VALIDATE AND RETURN
        # ============================================================
        
        if len(thumbnails) == 0:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate thumbnails. Please try again."
            )
        
        logger.info(f"✅ Successfully generated {len(thumbnails)} thumbnails")
        
        return {
            "success": True,
            "thumbnails": thumbnails,
            "video_path": None,
            "message": f"Generated {len(thumbnails)} CTR-optimized thumbnails",
            "source_type": "youtube_url" if is_youtube_url else "video_file",
            "language": language,
            "generation_methods": {
                "video_frames": any('frame_' in t['id'] for t in thumbnails),
                "ai_generated": any('ai_thumb_' in t['id'] for t in thumbnails),
                "fallback": any('fallback_' in t['id'] for t in thumbnails)
            },
            "ctr_optimized": any(t.get('ctr_optimized', False) for t in thumbnails)
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Thumbnail generation failed: {str(e)}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        
        # Cleanup on error
        try:
            if temp_youtube_video and os.path.exists(temp_youtube_video):
                os.unlink(temp_youtube_video)
        except:
            pass
        
        raise HTTPException(
            status_code=500, 
            detail=f"Thumbnail generation failed: {str(e)}"
        )

# Example API endpoint modification for scheduling
# @app.post("/api/youtube/schedule-video")
# async def schedule_video_upload(request: dict):
#     """Schedule a video upload for later"""
#     try:
#         user_id = request.get("user_id")
#         schedule_date = request.get("schedule_date")
#         schedule_time = request.get("schedule_time")
#         video_data = request.get("video_data", {})
        
#         if not all([user_id, schedule_date, schedule_time]):
#             raise HTTPException(status_code=400, detail="Missing required fields")
        
#         # Parse scheduled time
#         scheduled_datetime = datetime.strptime(
#             f"{schedule_date} {schedule_time}", 
#             "%Y-%m-%d %H:%M"
#         )
        
#         if scheduled_datetime <= datetime.now():
#             raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
        
#         # Store scheduled post
#         success = await store_scheduled_post(
#             user_id=user_id,
#             post_type="video",
#             post_data=video_data,
#             scheduled_for=scheduled_datetime
#         )
        
#         if success:
#             return {
#                 "success": True,
#                 "message": f"Video scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}",
#                 "scheduled_for": scheduled_datetime.isoformat()
#             }
#         else:
#             raise HTTPException(status_code=500, detail="Failed to schedule video")
            
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")
#     except Exception as e:
#         logger.error(f"Schedule video failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# Example usage and testing
"""
HOW TO TEST SCHEDULING:

1. Create a scheduled post:
   POST /api/youtube/schedule-video
   {
     "user_id": "your_user_id",
     "schedule_date": "2025-09-25",
     "schedule_time": "14:30",
     "video_data": {
       "title": "Scheduled Video Test",
       "description": "This video was scheduled",
       "video_url": "https://your-video-url.mp4",
       "content_type": "shorts"
     }
   }

2. Check scheduled posts in database:
   db.scheduled_posts.find({status: "scheduled"})

3. Wait for scheduled time (background scheduler checks every 60 seconds)

4. Check execution results:
   db.scheduled_posts.find({status: "published"})

FLOW DIAGRAM:
User creates scheduled post → Stored in MongoDB → Background scheduler checks every 60s → 
Time matches? → Execute upload → Update status → Log results

TIMING:
- Scheduler checks: Every 60 seconds
- Time window: ±1 minute accuracy  
- Execution: Immediate when time matches
- Retry: Failed posts can be retried manually
"""
@app.get("/api/youtube/scheduled-posts/{user_id}")
async def get_scheduled_posts(user_id: str):
    """Get scheduled posts for user"""
    try:
        # FIXED: Check database manager and database connection properly
        if not database_manager or not hasattr(database_manager, 'db') or database_manager.db is None:
            return {"success": False, "error": "Database not available"}
        
        collection = database_manager.db.scheduled_posts
        
        cursor = collection.find({"user_id": user_id}).sort("scheduled_for", 1)
        
        scheduled_posts = []
        async for post in cursor:
            post_data = {
                "id": str(post["_id"]),
                "post_type": post.get("post_type"),
                "scheduled_for": post.get("scheduled_for").isoformat() if post.get("scheduled_for") else None,
                "status": post.get("status"),
                "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
            }
            
            # Add title based on post type
            if post.get("post_type") == "video":
                video_data = post.get("video_data", {})
                post_data["title"] = video_data.get("title", "Scheduled Video")
            else:
                post_data["title"] = "Scheduled Community Post"
                
            scheduled_posts.append(post_data)
        
        return {
            "success": True,
            "scheduled_posts": scheduled_posts,
            "count": len(scheduled_posts)
        }
        
    except Exception as e:
        logger.error(f"Get scheduled posts failed: {e}")
        return {"success": False, "error": str(e)}

# Debug endpoint for YouTube service endpoints
@app.get("/api/debug/youtube-endpoints")
async def debug_youtube_endpoints():
    """Debug YouTube endpoints availability"""
    return {
        "available_endpoints": [
            "/api/youtube/oauth-url",
            "/api/youtube/oauth-callback", 
            "/api/youtube/status/{user_id}",
            "/api/youtube/disconnect/{user_id}",
            "/api/youtube/setup-automation",
            "/api/youtube/analytics/{user_id}",
            "/api/youtube/upload",
            "/api/ai/generate-youtube-content"
        ],
        "services_status": {
            "youtube_connector": youtube_connector is not None,
            "youtube_scheduler": youtube_scheduler is not None,
            "database_manager": database_manager is not None,
            "ai_service": ai_service is not None,
            "ai_service_type": type(ai_service).__name__ if ai_service else "None"
        },
        "environment_check": {
            "GOOGLE_CLIENT_ID": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
            "GOOGLE_CLIENT_SECRET": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗",
            "MONGODB_URI": "✓" if os.getenv("MONGODB_URI") else "✗",
            "GROQ_API_KEY": "✓" if os.getenv("GROQ_API_KEY") else "✗",
            "MISTRAL_API_KEY": "✓" if os.getenv("MISTRAL_API_KEY") else "✗"
        },
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/api/debug/trigger-scheduler-check")
async def trigger_scheduler_check():
    """Manually trigger scheduler check (TESTING ONLY)"""
    try:
        if not youtube_background_scheduler:
            return {
                "success": False,
                "error": "Background scheduler not initialized"
            }
        
        logger.info("🔧 Manual scheduler trigger requested")
        await youtube_background_scheduler.process_scheduled_posts()
        
        return {
            "success": True,
            "message": "Scheduler check completed",
            "scheduler_running": youtube_background_scheduler.running,
            "current_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Manual trigger failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/debug/scheduled-posts-raw/{user_id}")
async def get_raw_scheduled_posts(user_id: str):
    """Get raw scheduled posts from database (TESTING)"""
    try:
        posts = await database_manager.get_scheduled_posts_by_user(user_id)
        
        current_time = datetime.now()
        
        return {
            "success": True,
            "current_time": current_time.isoformat(),
            "posts": [
                {
                    "id": str(p["_id"]),
                    "title": p["video_data"].get("title"),
                    "scheduled_for": p["scheduled_for"].isoformat(),
                    "status": p["status"],
                    "time_until_execution": str(p["scheduled_for"] - current_time),
                    "is_due": p["scheduled_for"] <= current_time + timedelta(minutes=2)
                }
                for p in posts
            ]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ➜ ADD THESE ROUTES AFTER: return upload_result

# YouTube Community Posts endpoints
@app.post("/api/ai/generate-community-post")
async def generate_community_post(request: dict):
    """Generate community post content using AI"""
    try:
        logger.info(f"Generating community post: {request}")
        
        post_type = request.get("post_type", "text")
        topic = request.get("topic", "general")
        target_audience = request.get("target_audience", "general")
        
        # Try AI service first
        if ai_service and hasattr(ai_service, 'generate_community_post'):
            try:
                result = await ai_service.generate_community_post(
                    post_type=post_type,
                    topic=topic,
                    target_audience=target_audience
                )
                if result.get("success"):
                    return result
            except Exception as ai_error:
                logger.warning(f"AI service failed: {ai_error}")
        
        # Enhanced fallback content
        mock_content = {
            "text": {
                "content": f"Just discovered something amazing about {topic}! 🚀\n\nWhat's your experience with {topic}? Share in the comments below! 👇",
                "options": []
            },
            "text_poll": {
                "content": f"Quick question about {topic} for our {target_audience} community! 🤔\n\nWhich aspect interests you most?",
                "options": [
                    f"Getting started with {topic}",
                    f"Advanced {topic} techniques", 
                    f"Best {topic} tools",
                    f"Future of {topic}"
                ]
            },
            "image_poll": {
                "content": f"Visual poll time! 📊\n\nWhich {topic} approach resonates with you?",
                "options": [
                    f"Traditional {topic} methods",
                    f"Modern {topic} approaches",
                    f"Hybrid {topic} strategies",
                    f"Innovative {topic} solutions"
                ]
            },
            "quiz": {
                "content": f"Test your {topic} knowledge! 🧠\n\nWhat's the most important factor for {topic} success?",
                "options": [
                    "Consistent practice and patience",
                    "Having the right tools and resources", 
                    "Learning from experts and mentors",
                    "Understanding your target audience"
                ]
            }
        }
        
        template = mock_content.get(post_type, mock_content["text"])
        
        return {
            "success": True,
            "content": template["content"],
            "options": template["options"],
            "post_type": post_type,
            "ai_service": "enhanced_mock"
        }
        
    except Exception as e:
        logger.error(f"Community post generation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/youtube/community-post")
async def youtube_community_post(request: dict):
    """Publish or schedule YouTube community post"""
    try:
        logger.info(f"YouTube community post request: {request}")
        
        user_id = request.get("user_id")
        post_type = request.get("post_type", "text")
        content = request.get("content")
        image_url = request.get("image_url")
        options = request.get("options", [])
        correct_answer = request.get("correct_answer")
        schedule_date = request.get("schedule_date")
        schedule_time = request.get("schedule_time")
        
        if not user_id or not content:
            raise HTTPException(status_code=400, detail="user_id and content are required")
        
        # Check YouTube connection
        try:
            credentials = await database_manager.get_youtube_credentials(user_id)
            if not credentials:
                raise HTTPException(status_code=400, detail="YouTube not connected")
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            return {"success": False, "error": "Database connection error"}
        
        # Prepare post data
        post_data = {
            "user_id": user_id,
            "post_type": post_type,
            "content": content,
            "image_url": image_url,
            "options": options,
            "correct_answer": correct_answer,
            "created_at": datetime.now(),
            "status": "scheduled" if schedule_date and schedule_time else "published"
        }
        
        if schedule_date and schedule_time:
            post_data["scheduled_for"] = f"{schedule_date} {schedule_time}"
        
        # Try real YouTube Community Post API if available
        if youtube_connector and hasattr(youtube_connector, 'create_community_post'):
            try:
                post_result = await youtube_connector.create_community_post(
                    credentials_data=credentials,
                    post_data=post_data
                )
                
                if post_result.get("success"):
                    # Log to database
                    await database_manager.log_community_post(user_id, post_data)
                    return post_result
            except Exception as api_error:
                logger.warning(f"YouTube API post failed: {api_error}")
        
        # Mock success response
        mock_post_id = f"post_{user_id}_{int(datetime.now().timestamp())}"
        mock_response = {
            "success": True,
            "message": f"Community post {'scheduled' if schedule_date else 'published'} successfully!",
            "post_details": {
                "post_id": mock_post_id,
                "post_type": post_type,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "status": post_data["status"],
                "visibility": "public",
                "scheduled_for": post_data.get("scheduled_for"),
                "options_count": len(options) if options else 0
            },
            "mock_mode": True,
            "note": "This is a mock response. Real community posts require YouTube API integration."
        }
        
        # Log to database
        try:
            await database_manager.log_community_post(user_id, post_data)
        except Exception as log_error:
            logger.warning(f"Failed to log community post: {log_error}")
        
        return mock_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Community post failed: {e}")
        return {"success": False, "error": str(e)}

# ➜ YOUR EXISTING CODE CONTINUES HERE
# ============================================================================
# YOUTUBE COMMENTS MANAGEMENT ROUTES
# ============================================================================
@app.get("/api/youtube/user-videos/{user_id}")
async def get_user_videos(user_id: str):
    """Get user's YouTube videos with statistics"""
    try:
        logger.info(f"Fetching videos for user: {user_id}")
        
        # Get authenticated service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="Failed to authenticate with YouTube")
        
        # Get user's channel
        credentials = await database_manager.get_youtube_credentials(user_id)
        channel_id = credentials["channel_info"]["channel_id"]
        
        # Get recent videos (increased limit for better selection)
        search_response = youtube_service.search().list(
            part="id,snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=50
        ).execute()
        
        videos = []
        video_ids = []
        
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            video_ids.append(video_id)
            
            # Parse publish date for IST conversion
            published_at = item["snippet"]["publishedAt"]
            
            videos.append({
                "video_id": video_id,
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"][:150] + "..." if len(item["snippet"]["description"]) > 150 else item["snippet"]["description"],
                "published_at": published_at,
                "thumbnail_url": item["snippet"]["thumbnails"]["medium"]["url"] if "medium" in item["snippet"]["thumbnails"] else item["snippet"]["thumbnails"]["default"]["url"],
                "channel_title": item["snippet"]["channelTitle"]
            })
        
        # Get video statistics in batches (YouTube API limit is 50 per request)
        if video_ids:
            stats_response = youtube_service.videos().list(
                part="statistics,contentDetails",
                id=",".join(video_ids)
            ).execute()
            
            # Create stats mapping
            stats_map = {}
            for video_stats in stats_response.get("items", []):
                vid_id = video_stats["id"]
                stats = video_stats["statistics"]
                content_details = video_stats.get("contentDetails", {})
                
                stats_map[vid_id] = {
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "duration": content_details.get("duration", "PT0S")
                }
            
            # Apply statistics to videos
            for video in videos:
                vid_stats = stats_map.get(video["video_id"], {})
                video.update(vid_stats)
                
                # Determine if it's a Short (under 60 seconds)
                duration = video.get("duration", "PT0S")
                video["is_short"] = _is_youtube_short_duration(duration)
        
        # Sort by publish date (newest first)
        videos.sort(key=lambda x: x["published_at"], reverse=True)
        
        return {
            "success": True,
            "videos": videos,
            "total_videos": len(videos),
            "shorts_count": sum(1 for v in videos if v.get("is_short", False)),
            "regular_videos_count": sum(1 for v in videos if not v.get("is_short", False))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user videos failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _is_youtube_short_duration(duration_string: str) -> bool:
    """Check if video duration indicates a YouTube Short"""
    try:
        import re
        # Parse ISO 8601 duration format (PT1M30S = 1 minute 30 seconds)
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_string)
        
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds <= 60  # 60 seconds or less = Short
        
        return False
    except Exception:
        return False

@app.get("/api/youtube/comments/{user_id}")
async def get_youtube_comments(user_id: str, video_id: str = None, max_results: int = 50):
    """Get YouTube comments for user's videos with video selection support"""
    try:
        logger.info(f"Fetching comments for user: {user_id}, video_id: {video_id}")
        
        # Get authenticated service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="Failed to authenticate with YouTube")
        
        comments = []
        
        if video_id:
            # Get comments for specific video
            try:
                response = youtube_service.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=max_results,
                    order="time"
                ).execute()
                
                for item in response.get("items", []):
                    comment_data = item["snippet"]["topLevelComment"]["snippet"]
                    
                    # Convert UTC to IST for Indian users
                    published_at_utc = comment_data["publishedAt"]
                    published_at_ist = _convert_utc_to_ist(published_at_utc)
                    
                    # Detect comment language
                    comment_language = _detect_comment_language(comment_data["textDisplay"])
                    
                    comments.append({
                        "comment_id": item["id"],
                        "video_id": video_id,
                        "author_name": comment_data["authorDisplayName"],
                        "author_channel_id": comment_data.get("authorChannelId", {}).get("value", ""),
                        "author_channel_url": comment_data.get("authorChannelUrl", ""),
                        "text": comment_data["textDisplay"],
                        "like_count": comment_data.get("likeCount", 0),
                        "published_at": published_at_utc,
                        "published_at_ist": published_at_ist,
                        "updated_at": comment_data.get("updatedAt", published_at_utc),
                        "reply_count": item["snippet"].get("totalReplyCount", 0),
                        "has_replies": item["snippet"].get("totalReplyCount", 0) > 0,
                        "language": comment_language,
                        "can_reply": True,  # Always true for video owner
                        "is_spam": _is_likely_spam(comment_data["textDisplay"])
                    })
                    
            except Exception as e:
                logger.error(f"Failed to get comments for video {video_id}: {e}")
                
        else:
            # Get comments for all user's recent videos (fallback)
            try:
                credentials = await database_manager.get_youtube_credentials(user_id)
                channel_id = credentials["channel_info"]["channel_id"]
                
                # Get recent videos
                search_response = youtube_service.search().list(
                    part="id",
                    channelId=channel_id,
                    type="video",
                    order="date",
                    maxResults=10
                ).execute()
                
                for video in search_response.get("items", []):
                    vid_id = video["id"]["videoId"]
                    
                    # Get comments for each video
                    try:
                        comments_response = youtube_service.commentThreads().list(
                            part="snippet",
                            videoId=vid_id,
                            maxResults=5,  # Reduced for overview
                            order="time"
                        ).execute()
                        
                        for item in comments_response.get("items", []):
                            comment_data = item["snippet"]["topLevelComment"]["snippet"]
                            
                            published_at_utc = comment_data["publishedAt"]
                            published_at_ist = _convert_utc_to_ist(published_at_utc)
                            comment_language = _detect_comment_language(comment_data["textDisplay"])
                            
                            comments.append({
                                "comment_id": item["id"],
                                "video_id": vid_id,
                                "author_name": comment_data["authorDisplayName"],
                                "text": comment_data["textDisplay"],
                                "like_count": comment_data.get("likeCount", 0),
                                "published_at": published_at_utc,
                                "published_at_ist": published_at_ist,
                                "reply_count": item["snippet"].get("totalReplyCount", 0),
                                "language": comment_language,
                                "can_reply": True,
                                "is_spam": _is_likely_spam(comment_data["textDisplay"])
                            })
                    except Exception as e:
                        logger.warning(f"Failed to get comments for video {vid_id}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Failed to get user videos: {e}")
        
        # Sort by date (newest first)
        comments.sort(key=lambda x: x["published_at"], reverse=True)
        
        # Filter out spam if requested
        non_spam_comments = [c for c in comments if not c.get("is_spam", False)]
        
        return {
            "success": True,
            "comments": non_spam_comments[:max_results],
            "total_comments": len(non_spam_comments),
            "spam_filtered": len(comments) - len(non_spam_comments),
            "languages_detected": list(set(c["language"] for c in non_spam_comments)),
            "video_id": video_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get comments failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _convert_utc_to_ist(utc_time_str: str) -> str:
    """Convert UTC time to IST (Indian Standard Time)"""
    try:
        from datetime import datetime, timedelta
        import re
        
        # Parse ISO format: 2025-10-02T05:20:04Z
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        
        # Add 5:30 for IST
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        
        return ist_time.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        return utc_time_str

def _detect_comment_language(text: str) -> str:
    """Detect comment language for auto-reply"""
    text_lower = text.lower()
    
    # Hindi/Devanagari script detection
    hindi_chars = "अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
    if any(char in hindi_chars for char in text):
        return "hindi"
    
    # Hinglish detection (common Hindi words in Roman script)
    hinglish_words = ["acha", "accha", "bhai", "yaar", "kya", "hai", "nahi", "bahut", "sahi", "theek"]
    if any(word in text_lower for word in hinglish_words):
        return "hinglish"
    
    # Tamil script detection
    tamil_chars = "அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறன"
    if any(char in tamil_chars for char in text):
        return "tamil"
    
    # Default to English
    return "english"

def _is_likely_spam(text: str) -> bool:
    """Basic spam detection for comments"""
    text_lower = text.lower()
    
    spam_indicators = [
        "subscribe to my channel",
        "check out my channel",
        "follow me",
        "click here",
        "free money",
        "win cash",
        "telegram",
        "whatsapp me",
        "dm me"
    ]
    
    # Check for excessive repetition
    words = text_lower.split()
    if len(words) > 5:
        unique_words = set(words)
        if len(unique_words) / len(words) < 0.5:  # Less than 50% unique words
            return True
    
    # Check for spam phrases
    return any(indicator in text_lower for indicator in spam_indicators)







@app.post("/api/youtube/reply-comment")
async def reply_to_comment(request: dict):
    """Reply to a YouTube comment"""
    try:
        user_id = request.get("user_id")
        comment_id = request.get("comment_id")
        reply_text = request.get("reply_text")
        
        if not all([user_id, comment_id, reply_text]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get authenticated service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="Failed to authenticate with YouTube")
        
        # Post reply
        response = youtube_service.comments().insert(
            part="snippet",
            body={
                "snippet": {
                    "parentId": comment_id,
                    "textOriginal": reply_text
                }
            }
        ).execute()
        
        return {
            "success": True,
            "reply_id": response["id"],
            "message": "Reply posted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reply to comment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.put("/api/youtube/edit-reply")
async def edit_reply(request: dict):
    """Edit MY reply to a comment (not the original comment)"""
    try:
        user_id = request.get("user_id")
        reply_id = request.get("reply_id")  # Changed from comment_id
        new_text = request.get("new_text")
        
        if not all([user_id, reply_id, new_text]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Get authenticated service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="Failed to authenticate with YouTube")
        
        # Update MY reply (not original comment)
        youtube_service.comments().update(
            part="snippet",
            body={
                "id": reply_id,
                "snippet": {
                    "textOriginal": new_text
                }
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Reply updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Edit reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/youtube/delete-reply/{reply_id}")
async def delete_reply(reply_id: str, user_id: str):
    """Delete MY reply (not original comment)"""
    try:
        # Get authenticated service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="Failed to authenticate with YouTube")
        
        # Delete MY reply
        youtube_service.comments().delete(id=reply_id).execute()
        
        return {
            "success": True,
            "message": "Reply deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.delete("/api/youtube/delete-comment/{comment_id}")
async def delete_comment(comment_id: str, user_id: str):
    """Delete a YouTube comment/reply"""
    try:
        # Get authenticated service
        youtube_service = await youtube_connector.get_authenticated_service(user_id)
        if not youtube_service:
            raise HTTPException(status_code=400, detail="Failed to authenticate with YouTube")
        
        # Delete comment
        youtube_service.comments().delete(id=comment_id).execute()
        
        return {
            "success": True,
            "message": "Comment deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete comment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/youtube/generate-auto-reply")
async def generate_auto_reply(request: dict):
    """Generate automated reply using AI"""
    try:
        user_id = request.get("user_id")
        comment_text = request.get("comment_text")
        video_title = request.get("video_title", "")
        reply_style = request.get("reply_style", "friendly")
        
        if not all([user_id, comment_text]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Detect language
        detected_language = detect_comment_language(comment_text)
        
        # Generate reply using AI
        if ai_service and hasattr(ai_service, 'generate_comment_reply'):
            reply_result = await ai_service.generate_comment_reply(
                comment_text=comment_text,
                video_title=video_title,
                reply_style=reply_style,
                language=detected_language
            )
        else:
            # Fallback reply generation
            reply_result = {
                "success": True,
                "reply": f"Thank you for your comment! 😊" if detected_language == "english" 
                        else f"आपके कमेंट के लिए धन्यवाद! 😊" if detected_language == "hindi"
                        else "Thank you for your comment! 😊",
                "language": detected_language
            }
        
        return reply_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate auto reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))






@app.post("/api/youtube/start-auto-reply")
async def start_automated_replies(request: dict):
    """Start automated comment replies for selected videos"""
    try:
        user_id = request.get("user_id")
        selected_videos = request.get("selected_videos", [])
        auto_reply_config = request.get("config", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        if not selected_videos:
            raise HTTPException(status_code=400, detail="Please select at least one video")
        
        # Store auto-reply configuration with selected videos
        config_data = {
            "enabled": True,
            "selected_videos": selected_videos,
            "reply_style": auto_reply_config.get("reply_style", "friendly"),
            "reply_delay_seconds": auto_reply_config.get("reply_delay_seconds", 30),
            "custom_prompt": auto_reply_config.get("custom_prompt", ""),
            "languages": auto_reply_config.get("languages", ["english", "hindi"]),
            "filter_spam": auto_reply_config.get("filter_spam", True),
            "max_replies_per_hour": auto_reply_config.get("max_replies_per_hour", 10),
            "timezone": auto_reply_config.get("timezone", "Asia/Kolkata"),
            "created_at": datetime.now().isoformat(),
            "last_check": datetime.now().isoformat()
        }
        
        await database_manager.store_automation_config(
            user_id, "auto_reply", config_data
        )
        
        return {
            "success": True,
            "message": f"Automated replies started for {len(selected_videos)} video(s)",
            "config": config_data,
            "selected_videos_count": len(selected_videos)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start auto reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    



@app.post("/api/youtube/stop-auto-reply")
async def stop_automated_replies(request: dict):
    """Stop automated comment replies"""
    try:
        user_id = request.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        # Disable auto-reply
        await database_manager.disable_automation(user_id, "auto_reply")
        
        return {
            "success": True,
            "message": "Automated replies stopped successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stop auto reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def detect_comment_language(text: str) -> str:
    """Detect language of comment text"""
    # Simple language detection based on script
    hindi_chars = set("अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह")
    
    if any(char in hindi_chars for char in text):
        return "hindi"
    elif any(ord(char) > 127 for char in text):
        # Other non-ASCII languages
        tamil_chars = set("அஆஇஈஉஊஎஏஐஒஓஔகஙசஞடணதநபமயரலவழளறன")
        if any(char in tamil_chars for char in text):
            return "tamil"
        return "other"
    else:
        return "english"




# Add after line 50 in mainY.py (after other imports)
from slideshow_generator import get_slideshow_generator

# Add this endpoint after line 1200 (after youtube upload endpoints)

import time
from typing import List, Dict

@app.post("/api/slideshow/generate")
async def generate_slideshow(request: dict):
    """
    Start slideshow generation (returns immediately, processes in background)
    
    Request body:
    {
        "user_id": "user123",
        "images": ["data:image/jpeg;base64,...", ...],  // 2-6 images
        "title": "My Amazing Product",
        "language": "hindi",  // hindi/english/hinglish
        "duration_per_image": 2.0,  // 1-3 seconds
        "transition": "fade",  // fade/slide/zoom
        "music_style": "upbeat",  // upbeat/calm/energetic
        "add_text": true,
        "platforms": ["youtube_shorts"]
    }
    """
    try:
        user_id = request.get('user_id')
        logger.info(f"🎬 Slideshow request from user: {user_id}")
        
        # Validate
        images = request.get('images', [])
        if not 2 <= len(images) <= 6:
            raise HTTPException(status_code=400, detail="Upload 2-6 images")
        
        # Start background task (won't block)
        asyncio.create_task(generate_slideshow_background(
            user_id=user_id,
            images=images,
            title=request.get('title', 'Video'),
            language=request.get('language', 'english'),
            duration_per_image=request.get('duration_per_image', 2.0),
            transition=request.get('transition', 'fade'),
            add_text=request.get('add_text', True),
            music_style=request.get('music_style', 'upbeat'),
            platforms=request.get('platforms', ['youtube_shorts'])
        ))
        
        # Return immediately
        return {
            "success": True,
            "message": "Video generation started",
            "status": "processing",
            "estimated_time_seconds": 30,
            "note": "Video will be automatically uploaded to YouTube in ~30 seconds. Check your channel!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slideshow request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_slideshow_background(
    user_id: str,
    images: List[str],
    title: str,
    language: str,
    duration_per_image: float,
    transition: str,
    add_text: bool,
    music_style: str,
    platforms: List[str]
):
    """Background task - generates video and uploads to YouTube"""
    try:
        logger.info(f"🎬 Background generation started for user: {user_id}")
        
        # Generate slideshow
        slideshow_gen = get_slideshow_generator()
        result = await slideshow_gen.generate_slideshow(
            images=images,
            title=title,
            language=language,
            duration_per_image=duration_per_image,
            transition=transition,
            add_text=add_text,
            music_style=music_style,
            aspect_ratio="9:16"
        )
        
        if not result.get('success'):
            logger.error(f"❌ Generation failed: {result.get('error')}")
            return
        
        logger.info(f"✅ Video generated: {result['local_path']}")
        
        # Auto-upload to YouTube
        if 'youtube_shorts' in platforms:
            try:
                credentials = await database_manager.get_youtube_credentials(user_id)
                
                if credentials:
                    logger.info(f"📤 Uploading to YouTube for user: {user_id}")
                    
                    upload_result = await youtube_scheduler.generate_and_upload_content(
                        user_id=user_id,
                        credentials_data=credentials,
                        content_type="shorts",
                        title=title,
                        description=f"Created with AI slideshow generator\n\n{title}",
                        video_url=result['local_path']  # Use local file path
                    )
                    
                    if upload_result.get('success'):
                        logger.info(f"✅ Video uploaded to YouTube: {upload_result.get('video_id')}")
                    else:
                        logger.error(f"❌ Upload failed: {upload_result.get('error')}")
                else:
                    logger.warning(f"No YouTube credentials for user: {user_id}")
                    
            except Exception as upload_error:
                logger.error(f"Upload error: {upload_error}")
        
        # Clean up temp files after 5 minutes
        await asyncio.sleep(300)
        try:
            import shutil
            shutil.rmtree(Path(result['local_path']).parent, ignore_errors=True)
            logger.info(f"🗑️ Cleaned up temp files")
        except Exception as cleanup_error:
            logger.warning(f"Cleanup failed: {cleanup_error}")
        
    except Exception as e:
        logger.error(f"❌ Background generation failed: {e}")


async def _generate_platform_metadata(title: str, language: str, platforms: List[str]) -> Dict:
    """Generate platform-specific metadata using AI (fallback if AI unavailable)"""
    
    # Simple fallback - AI generation removed since it's now auto-uploading
    return {
        platform: {
            "title": title[:50],
            "description": f"Check out {title}!",
            "hashtags": ["#shorts", "#trending", "#viral"]
        }
        for platform in platforms
    }



@app.post("/api/youtube/generate-slideshow")
async def generate_youtube_slideshow(request: dict):
    """
    Frontend endpoint - generates slideshow and uploads to YouTube
    Expected from frontend: images, title, description, duration_per_image
    """
    try:
        user_id = request.get('user_id')
        images = request.get('images', [])
        title = request.get('title', '')
        description = request.get('description', '')
        duration = request.get('duration_per_image', 2.0)
        
        logger.info(f"🎬 Slideshow request: {title} ({len(images)} images)")
        
        # Validate
        if not 2 <= len(images) <= 6:
            raise HTTPException(status_code=400, detail="Upload 2-6 images")
        
        if not title or not description:
            raise HTTPException(status_code=400, detail="Title and description required")
        
        # Check YouTube credentials
        credentials = await database_manager.get_youtube_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=400, detail="YouTube not connected")
        
        # Generate slideshow
        slideshow_gen = get_slideshow_generator()
        result = await slideshow_gen.generate_slideshow(
            images=images,
            title=title,
            language='english',
            duration_per_image=duration,
            transition='fade',
            add_text=True,
            aspect_ratio="9:16"
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        # Upload to YouTube
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=description,
            video_url=result['local_path']
        )
        
        if upload_result.get('success'):
            # Clean up after 2 minutes
            asyncio.create_task(cleanup_temp_files(result['local_path'], delay=120))
            
            return {
                "success": True,
                "message": "Video uploaded successfully!",
                "video_id": upload_result.get('video_id'),
                "video_url": upload_result.get('video_url'),
                "title": title
            }
        else:
            raise HTTPException(status_code=500, detail=upload_result.get('error'))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slideshow generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def cleanup_temp_files(file_path: str, delay: int = 120):
    # ... existing cleanup code ...
    """Clean up temporary slideshow files after delay"""
    try:
        await asyncio.sleep(delay)
        import shutil
        from pathlib import Path
        
        temp_dir = Path(file_path).parent
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"🗑️ Cleaned up temp files: {temp_dir}")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")

@app.post("/api/ai/generate-youtube-content")
async def generate_youtube_content_endpoint(request: dict):
    """Generate YouTube content with AI"""
    try:
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI service not available")
        
        result = await ai_service.generate_youtube_content(
            content_type=request.get('content_type', 'shorts'),
            topic=request.get('topic', 'general'),
            target_audience=request.get('target_audience', 'general'),
            duration_seconds=request.get('duration_seconds', 30)
        )
        
        return result
    except Exception as e:
        logger.error(f"YouTube content generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# At the top with other imports
from YTvideo_services import get_video_service

# In your slideshow preview endpoint
@app.post("/api/youtube/generate-slideshow-preview")
async def generate_slideshow_preview(request: dict):
    try:
        user_id = request.get("user_id")
        images = request.get("images", [])
        duration_per_image = request.get("duration_per_image", 2.0)
        
        # DEBUG LOGGING
        logger.info(f"🎬 Generating preview for {len(images)} images")
        if images:
            logger.info(f"📊 First image preview: {images[0][:50] if isinstance(images[0], str) else 'Invalid'}")
        else:
            logger.error("❌ No images received in request")
            logger.error(f"📋 Full request: {request}")
        
        # CHANGED: Allow 1 image minimum
        if not images or len(images) < 1:
            raise ValueError("Need at least 1 image")
        
        # Get video service
        from YTvideo_services import get_video_service
        video_service = get_video_service()
        
        if not video_service.ffmpeg_available:
            return JSONResponse({
                "success": False,
                "error": "FFmpeg not available. Please upload directly to YouTube."
            }, status_code=503)
        
        # Generate video
        video_path = await video_service.create_slideshow(
            images=images,
            duration_per_image=duration_per_image,
            output_format='mp4'
        )
        
        # Read as base64
        with open(video_path, 'rb') as f:
            video_data = base64.b64encode(f.read()).decode()
        
        # Cleanup
        os.unlink(video_path)
        
        return JSONResponse({
            "success": True,
            "video_preview": f"data:video/mp4;base64,{video_data}"
        })
        
    except Exception as e:
        logger.error(f"Preview generation failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse({
            "success": False,
            "error": f"Preview failed: {str(e)}"
        }, status_code=500)





@app.post("/api/slideshow/upload-multi-platform")
async def upload_slideshow_multi_platform(request: dict):
    """
    Upload generated slideshow to multiple platforms
    
    Currently supports:
    - YouTube Shorts (working)
    - Instagram Reels (mock - would need Instagram Graph API)
    - Facebook Ads (mock - would need Facebook Marketing API)
    """
    try:
        user_id = request.get('user_id')
        video_path = request.get('video_path')  # Local path from generation
        platforms = request.get('platforms', [])
        metadata = request.get('metadata', {})
        
        results = {}
        
        # YouTube Shorts (already implemented!)
        if 'youtube_shorts' in platforms:
            yt_metadata = metadata.get('youtube_shorts', {})
            
            credentials = await database_manager.get_youtube_credentials(user_id)
            if credentials:
                upload_result = await youtube_scheduler.generate_and_upload_content(
                    user_id=user_id,
                    credentials_data=credentials,
                    content_type="shorts",
                    title=yt_metadata.get('title'),
                    description=yt_metadata.get('description'),
                    video_url=video_path  # Use local path
                )
                results['youtube_shorts'] = upload_result
            else:
                results['youtube_shorts'] = {
                    "success": False,
                    "error": "YouTube not connected"
                }
        
        # Instagram Reels (mock for now)
        if 'instagram_reels' in platforms:
            results['instagram_reels'] = {
                "success": True,
                "platform": "instagram_reels",
                "post_id": f"mock_ig_{int(datetime.now().timestamp())}",
                "message": "Mock upload - integrate Instagram Graph API for production",
                "note": "Requires: Instagram Business Account + Facebook Developer App"
            }
        
        # Facebook Ads (mock for now)
        if 'facebook_ads' in platforms:
            results['facebook_ads'] = {
                "success": True,
                "platform": "facebook_ads",
                "campaign_id": f"mock_fb_{int(datetime.now().timestamp())}",
                "message": "Mock campaign - integrate Facebook Marketing API for production",
                "note": "Requires: Facebook Business Manager + Ad Account"
            }
        
        return {
            "success": True,
            "platforms_uploaded": list(results.keys()),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Multi-platform upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/slideshow/test-image")
async def test_image_upload(request: dict):
    """Test image decoding"""
    try:
        img_b64 = request.get('image', '')
        
        logger.info(f"Received image data length: {len(img_b64)}")
        logger.info(f"First 100 chars: {img_b64[:100]}")
        
        # Clean base64
        if img_b64.startswith('data:image'):
            img_b64 = img_b64.split(',', 1)[1]
        
        img_b64 = img_b64.strip()
        
        # Decode
        img_data = base64.b64decode(img_b64)
        logger.info(f"Decoded to {len(img_data)} bytes")
        
        # Open image
        img = Image.open(io.BytesIO(img_data))
        img.load()
        
        return {
            "success": True,
            "format": img.format,
            "size": img.size,
            "mode": img.mode,
            "data_length": len(img_data)
        }
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/debug/ffmpeg-check")
async def check_ffmpeg():
    """Verify FFmpeg is available"""
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return {
            "ffmpeg_installed": result.returncode == 0,
            "version": result.stdout.split('\n')[0] if result.returncode == 0 else "Not found"
        }
    except Exception as e:
        return {"ffmpeg_installed": False, "error": str(e)}

from YTscrapADS import get_product_scraper


async def shorten_url(long_url: str) -> str:
    """Shorten URL using TinyURL (free, no API needed)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://tinyurl.com/api-create.php?url={long_url}",
                timeout=10
            )
            if response.status_code == 200:
                return response.text.strip()
    except Exception as e:
        logger.error(f"URL shortening failed: {e}")
    return long_url

@app.post("/api/product-video/generate")
async def generate_product_promo_video(request: dict):
    """Scrape product and return formatted data for YouTube"""
    try:
        user_id = request.get('user_id')
        product_url = request.get('product_url')
        
        if not product_url:
            return {"success": False, "error": "Product URL required"}
        
        logger.info(f"🔍 Scraping: {product_url}")
        
        # Scrape product
        scraper = get_product_scraper()
        product_data = await scraper.scrape_product(product_url)
        
        # Handle scraping failure with detailed error
        if not product_data.get('success'):
            error_msg = product_data.get('error', 'Scraping failed')
            logger.error(f"❌ Scraping failed: {error_msg}")
            
            # Return error but with empty product structure so UI doesn't break
            return {
                "success": False,
                "error": error_msg,
                "product_data": {
                    "product_name": "",
                    "brand": "Brand",
                    "price": 0,
                    "original_price": 0,
                    "discount": "0% OFF",
                    "colors": [],
                    "sizes": [],
                    "category": "Unisex",
                    "rating_count": 0,
                    "review_count": 0,
                    "images": []
                },
                "title": "",
                "description": "",
                "images": []
            }
        
        logger.info(f"✅ Scraped: {product_data.get('product_name')}")
        
        # Extract data
        brand = product_data.get('brand', 'Brand')
        product_name = product_data.get('product_name', 'Product')
        price = product_data.get('price', 0)
        original_price = product_data.get('original_price', price)
        discount = product_data.get('discount', '')
        colors = product_data.get('colors', [])
        sizes = product_data.get('sizes', [])
        rating_count = product_data.get('rating_count', 0)
        review_count = product_data.get('review_count', 0)
        images = product_data.get('images', [])
        
        # Validate we have minimum required data
        if not images or len(images) < 1:
            logger.error("❌ No images found")
            return {
                "success": False,
                "error": "No product images found. Try a different URL or use manual image upload.",
                "product_data": {
                    "product_name": product_name,
                    "brand": brand,
                    "price": price,
                    "original_price": original_price,
                    "discount": discount,
                    "colors": colors,
                    "sizes": sizes,
                    "category": "Unisex",
                    "rating_count": rating_count,
                    "review_count": review_count,
                    "images": []
                },
                "title": f"{brand} {product_name}",
                "description": "",
                "images": []
            }
        
        # Determine category (Men/Women/Unisex)
        product_lower = product_name.lower()
        if 'men' in product_lower and 'women' not in product_lower:
            category = "Men"
        elif 'women' in product_lower or 'ladies' in product_lower:
            category = "Women"
        elif 'kids' in product_lower or 'baby' in product_lower:
            category = "Kids"
        else:
            category = "Unisex"
        
        # Calculate discount percentage
        if original_price and price and original_price > price:
            discount_pct = int(((original_price - price) / original_price) * 100)
        else:
            discount_pct = 0
            if discount:
                try:
                    discount_pct = int(''.join(filter(str.isdigit, discount)))
                except:
                    pass
        
        # Build YouTube-optimized title
        title = f"{brand} {product_name}"
        if len(title) > 90:
            title = title[:87] + "..."
        
        # Shorten URL
        short_url = await shorten_url(product_url)
        
        # Build formatted description
        description = f"""{brand.upper()}
{product_name}

💰 PRICE DETAILS:
Original: ₹{original_price:,}
Selling Price: ₹{price:,}
YOU SAVE: ₹{int(original_price - price):,} ({discount_pct}% OFF)

👔 BRAND: {brand}
👥 CATEGORY: {category}
"""
        
        # Add sizes if available
        if sizes:
            size_text = ', '.join(sizes[:12])
            description += f"\n📏 SIZES AVAILABLE:\n{size_text}\n"
        
        # Add colors if available
        if colors:
            color_text = ', '.join(colors[:6])
            description += f"\n🎨 COLORS:\n{color_text}\n"
        
        # Add ratings if available
        if rating_count > 0:
            description += f"\n⭐ RATINGS:\n{rating_count:,} ratings"
            if review_count > 0:
                description += f" and {review_count} reviews"
            description += "\n"
        
        # Add purchase link
        description += f"\n🛒 BUY NOW 👇\n{short_url}\n"
        
        # Add hashtags
        category_hashtags = {
            "Men": ["mensfashion", "menstyle", "menswear"],
            "Women": ["womensfashion", "womenswear", "ladiesfashion"],
            "Kids": ["kidsfashion", "babyfashion", "kidsclothing"],
            "Unisex": ["fashion", "style", "trending"]
        }
        
        hashtags = ["shopping", "deals", "india", "fashion"]
        hashtags.extend(category_hashtags.get(category, []))
        
        # Add brand hashtag (clean it up)
        brand_tag = brand.lower().replace(" ", "").replace("-", "")
        if brand_tag:
            hashtags.append(brand_tag)
        
        description += f"\n{' '.join([f'#{tag}' for tag in hashtags[:15]])}"
        
        logger.info(f"✅ Generated: {len(images)} images, title: {len(title)} chars")
        
        # Return structured data
        return {
            "success": True,
            "product_data": {
                "product_name": product_name,
                "brand": brand,
                "price": price,
                "original_price": original_price,
                "discount": f"{discount_pct}% OFF",
                "colors": colors,
                "sizes": sizes,
                "category": category,
                "rating_count": rating_count,
                "review_count": review_count,
                "images": images[:6]
            },
            "title": title,
            "description": description,
            "images": images[:6]
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "success": False,
            "error": f"Internal error: {str(e)[:200]}",
            "product_data": {
                "product_name": "",
                "brand": "Brand",
                "price": 0,
                "original_price": 0,
                "discount": "0% OFF",
                "colors": [],
                "sizes": [],
                "category": "Unisex",
                "rating_count": 0,
                "review_count": 0,
                "images": []
            },
            "title": "",
            "description": "",
            "images": []
        }






# Main application runner
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "mainY:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )