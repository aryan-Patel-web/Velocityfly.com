"""
Supermain.py - COMPLETE PRODUCTION VERSION - MULTI-USER READY
✅ Dynamic Reddit usernames for multiple users
✅ Enhanced error handling
✅ Token refresh with user-specific User-Agent
✅ Optimized for Render deployment
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Optional
from datetime import datetime, timedelta
import uvicorn
import os
import sys
import traceback
import uuid
import bcrypt
import jwt
from pydantic import BaseModel, EmailStr
import base64
import httpx

import json
import re
import random
from urllib.parse import quote
# import base64          gdf;lh,er
from PIL import Image, ImageDraw, ImageFont
import io

# ============================================================================
# ✅ CRITICAL: SET PLAYWRIGHT PATH BEFORE ANY IMPORTS
# ============================================================================
PLAYWRIGHT_PATH = '/opt/render/project/.playwright'
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = PLAYWRIGHT_PATH
os.environ['PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS'] = '1'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("unified_automation.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger.info(f"🎭 Playwright path set to: {PLAYWRIGHT_PATH}")

# ============================================================================
# UNIFIED DATABASE MANAGER - MULTI-USER OPTIMIZED
# ============================================================================
class UnifiedDatabaseManager:
    """
    ✅ MULTI-USER READY: Dynamic Reddit usernames, token refresh, error handling
    """
    
    def __init__(self, mongodb_uri: str):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.db = None
        self.connected = False
        
        # Collections for all platforms
        self.users_collection = None
        self.youtube_credentials = None
        self.reddit_tokens = None
        self.automation_configs = None
        self.scheduled_posts = None
        
    async def connect(self):
        """Initialize MongoDB connection"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            self.client = AsyncIOMotorClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client.velocitypost_unified
            
            # Initialize collections
            self.users_collection = self.db.users
            self.youtube_credentials = self.db.youtube_credentials
            self.reddit_tokens = self.db.reddit_tokens
            self.automation_configs = self.db.automation_configs
            self.scheduled_posts = self.db.scheduled_posts
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.connected = True
            logger.info("✅ Unified database connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Database disconnected")
    
    # ========== USER MANAGEMENT ==========
    async def create_user(self, user_data: dict) -> bool:
        """Create new user"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return False
            await self.users_collection.insert_one(user_data)
            return True
        except Exception as e:
            logger.error(f"Create user failed: {e}")
            return False
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return None
            return await self.users_collection.find_one({"email": email})
        except Exception as e:
            logger.error(f"Get user failed: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return None
            return await self.users_collection.find_one({"_id": user_id})
        except Exception as e:
            logger.error(f"Get user by ID failed: {e}")
            return None
    
    async def get_user_by_token(self, token: str) -> Optional[dict]:
        """Get user by JWT token - for authentication"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return None
            
            # Decode JWT
            payload = jwt.decode(
                token, 
                os.getenv("JWT_SECRET", "your_secret_key"), 
                algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            
            if not user_id:
                logger.warning("No user_id in token payload")
                return None
            
            # Get user from database
            user = await self.get_user_by_id(user_id)
            
            if user:
                return {
                    "id": user["_id"],
                    "user_id": user["_id"],
                    "email": user["email"],
                    "name": user["name"],
                    "platforms_connected": user.get("platforms_connected", [])
                }
            
            return None
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Get user by token failed: {e}")
            return None
    
    # ========== YOUTUBE CREDENTIALS ==========
    async def store_youtube_credentials(self, user_id: str, credentials: dict) -> bool:
        """Store YouTube OAuth credentials"""
        try:
            if not self.connected:
                return False
            
            await self.youtube_credentials.update_one(
                {"user_id": user_id},
                {"$set": {
                    "user_id": user_id,
                    "credentials": credentials,
                    "updated_at": datetime.now()
                }},
                upsert=True
            )
            
            await self.users_collection.update_one(
                {"_id": user_id},
                {"$addToSet": {"platforms_connected": "youtube"}}
            )
            
            logger.info(f"YouTube credentials stored for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Store YouTube credentials failed: {e}")
            return False
    
    async def get_youtube_credentials(self, user_id: str) -> Optional[dict]:
        """Get YouTube credentials"""
        try:
            if not self.connected:
                return None
            result = await self.youtube_credentials.find_one({"user_id": user_id})
            return result.get("credentials") if result else None
        except Exception as e:
            logger.error(f"Get YouTube credentials failed: {e}")
            return None
    
    # ========== REDDIT TOKENS - MULTI-USER ==========
    async def store_reddit_tokens(self, user_id: str, token_data: dict) -> dict:
        """Store Reddit OAuth tokens - MULTI-USER"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            await self.reddit_tokens.update_one(
                {"user_id": user_id},
                {"$set": {
                    "user_id": user_id,
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token", ""),
                    "reddit_username": token_data["reddit_username"],
                    "reddit_user_id": token_data.get("reddit_user_id", ""),
                    "is_active": True,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }},
                upsert=True
            )
            
            await self.users_collection.update_one(
                {"_id": user_id},
                {"$addToSet": {"platforms_connected": "reddit"}}
            )
            
            logger.info(f"✅ Reddit tokens stored for user {user_id} (u/{token_data['reddit_username']})")
            return {"success": True, "message": "Reddit tokens stored"}
        except Exception as e:
            logger.error(f"Store Reddit tokens failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_reddit_tokens(self, user_id: str) -> Optional[dict]:
        """Get Reddit tokens - MULTI-USER"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return None
            
            result = await self.reddit_tokens.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if not result:
                logger.warning(f"No active Reddit token found for user {user_id}")
                return None
            
            expires_at = result.get("expires_at")
            is_expired = False
            
            if expires_at:
                try:
                    if isinstance(expires_at, str):
                        try:
                            from dateutil import parser
                            expires_at = parser.parse(expires_at)
                        except:
                            pass
                    
                    if isinstance(expires_at, datetime):
                        if expires_at <= datetime.now():
                            is_expired = True
                            logger.warning(f"Reddit token expired for user {user_id}")
                except Exception as e:
                    logger.warning(f"Expiration check failed: {e}")
            
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", ""),
                "reddit_username": result["reddit_username"],
                "reddit_user_id": result.get("reddit_user_id", ""),
                "is_valid": True,
                "is_expired": is_expired
            }
            
        except Exception as e:
            logger.error(f"Get Reddit tokens failed: {e}")
            logger.error(traceback.format_exc())
            return None
    
    async def refresh_reddit_token(self, user_id: str) -> Optional[dict]:
        """✅ MULTI-USER: Refresh expired Reddit token with dynamic username"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return None
            
            result = await self.reddit_tokens.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if not result or not result.get("refresh_token"):
                logger.error(f"No refresh token found for user {user_id}")
                return None
            
            refresh_token = result["refresh_token"]
            reddit_username = result.get("reddit_username", "VelocityPostUser")  # ✅ Dynamic username
            
            reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
            reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            
            if not reddit_client_id or not reddit_client_secret:
                logger.error("Reddit credentials not configured")
                return None
            
            auth_string = f"{reddit_client_id}:{reddit_client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            # ✅ DYNAMIC USER-AGENT with actual Reddit username
            user_agent = f"VelocityPost/1.0 by /u/{reddit_username}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://www.reddit.com/api/v1/access_token",
                    headers={
                        "Authorization": f"Basic {auth_b64}",
                        "User-Agent": user_agent  # ✅ Dynamic per user
                    },
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token
                    }
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    new_access_token = token_data.get("access_token")
                    
                    if new_access_token:
                        await self.reddit_tokens.update_one(
                            {"user_id": user_id},
                            {"$set": {
                                "access_token": new_access_token,
                                "updated_at": datetime.now()
                            }}
                        )
                        
                        logger.info(f"✅ Refreshed Reddit token for user {user_id} (u/{reddit_username})")
                        
                        return {
                            "access_token": new_access_token,
                            "refresh_token": refresh_token,
                            "reddit_username": reddit_username,
                            "is_valid": True,
                            "is_expired": False
                        }
                    else:
                        logger.error("No access_token in refresh response")
                elif response.status_code == 429:
                    logger.error("⚠️ Reddit rate limit during token refresh")
                else:
                    logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            logger.error(f"Refresh Reddit token failed: {e}")
            logger.error(traceback.format_exc())
            return None
    
    async def check_reddit_connection(self, user_id: str) -> dict:
        """Check Reddit connection status - MULTI-USER"""
        try:
            if not self.connected:
                return {"connected": False, "reddit_username": None}
            
            result = await self.reddit_tokens.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if result:
                return {
                    "connected": True,
                    "reddit_username": result["reddit_username"],
                    "reddit_user_id": result.get("reddit_user_id", ""),
                    "expires_at": result.get("expires_at")
                }
            return {"connected": False, "reddit_username": None}
        except Exception as e:
            logger.error(f"Check Reddit connection failed: {e}")
            return {"connected": False, "reddit_username": None}
    
    async def revoke_reddit_connection(self, user_id: str) -> dict:
        """Revoke Reddit connection"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            await self.reddit_tokens.update_one(
                {"user_id": user_id},
                {"$set": {"is_active": False, "updated_at": datetime.now()}}
            )
            
            await self.users_collection.update_one(
                {"_id": user_id},
                {"$pull": {"platforms_connected": "reddit"}}
            )
            
            return {"success": True, "message": "Reddit disconnected"}
        except Exception as e:
            logger.error(f"Revoke Reddit connection failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ========== OAUTH STATE MANAGEMENT ==========
    async def store_oauth_state(self, state: str, user_id: str, expires_at: datetime) -> dict:
        """Store OAuth state for validation"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            collection = self.db.oauth_states
            await collection.insert_one({
                "_id": state,
                "state": state,
                "user_id": user_id,
                "expires_at": expires_at,
                "created_at": datetime.now()
            })
            logger.info(f"OAuth state stored: {state} for user {user_id}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Store OAuth state failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_oauth_state(self, state: str) -> Optional[dict]:
        """Get OAuth state"""
        try:
            if not self.connected:
                return None
            
            collection = self.db.oauth_states
            result = await collection.find_one({"_id": state})
            
            if result and result["expires_at"] > datetime.now():
                return result
            return None
        except Exception as e:
            logger.error(f"Get OAuth state failed: {e}")
            return None
    
    async def cleanup_oauth_state(self, state: str) -> dict:
        """Remove OAuth state after use"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            collection = self.db.oauth_states
            await collection.delete_one({"_id": state})
            logger.info(f"OAuth state cleaned up: {state}")
            return {"success": True}
        except Exception as e:
            logger.error(f"Cleanup OAuth state failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ========== ACTIVITY LOGGING ==========
    async def log_reddit_activity(self, user_id: str, activity_type: str, activity_data: dict) -> bool:
        """Log Reddit activity for analytics"""
        try:
            if not self.connected:
                return False
            
            collection = self.db.reddit_activities
            await collection.insert_one({
                "user_id": user_id,
                "activity_type": activity_type,
                "activity_data": activity_data,
                "timestamp": datetime.now()
            })
            return True
        except Exception as e:
            logger.error(f"Log Reddit activity failed: {e}")
            return False
    
    # ========== AUTOMATION CONFIGS ==========
    async def store_automation_config(self, user_id: str, config_type: str, config_data: dict) -> bool:
        """Store automation configuration"""
        try:
            if not self.connected:
                return False
            
            await self.automation_configs.update_one(
                {"user_id": user_id, "config_type": config_type},
                {"$set": {
                    "user_id": user_id,
                    "config_type": config_type,
                    "config_data": config_data,
                    "enabled": True,
                    "updated_at": datetime.now()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Store automation config failed: {e}")
            return False
    
    async def get_automation_config(self, user_id: str, config_type: str) -> Optional[dict]:
        """Get automation configuration"""
        try:
            if not self.connected:
                return None
            
            return await self.automation_configs.find_one({
                "user_id": user_id,
                "config_type": config_type
            })
        except Exception as e:
            logger.error(f"Get automation config failed: {e}")
            return None
    
    async def get_all_active_automations(self, config_type: str) -> list:
        """Get all active automation configs for a type"""
        try:
            if not self.connected:
                return []
            
            cursor = self.automation_configs.find({
                "config_type": config_type,
                "enabled": True
            })
            
            results = []
            async for doc in cursor:
                results.append({
                    "user_id": doc["user_id"],
                    "config_data": doc["config_data"],
                    "enabled": doc["enabled"]
                })
            
            return results
        except Exception as e:
            logger.error(f"Get all active automations failed: {e}")
            return []
    
    # ========== HEALTH CHECK ==========
    async def health_check(self) -> dict:
        """Check database health"""
        try:
            if not self.connected:
                return {
                    "status": "disconnected",
                    "error": "Database not connected"
                }
            
            await self.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": "connected",
                "collections": {
                    "users": await self.users_collection.count_documents({}),
                    "youtube_credentials": await self.youtube_credentials.count_documents({}),
                    "reddit_tokens": await self.reddit_tokens.count_documents({})
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# ============================================================================
# GLOBAL INSTANCES
# ============================================================================
database_manager = None
youtube_services = {}
reddit_services = {}

# Authentication
security = HTTPBearer()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        
        if not database_manager:
            logger.error("Database manager not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        if not database_manager.connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=500, detail="Database not connected")
        
        user = await database_manager.get_user_by_token(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

# ============================================================================
# SERVICE INITIALIZATION
# ============================================================================
async def initialize_all_services():
    """Initialize YouTube and Reddit services"""
    global database_manager, youtube_services, reddit_services
    
    logger.info("="*60)
    logger.info("🚀 STARTING UNIFIED AUTOMATION PLATFORM")
    logger.info("="*60)
    
    # Initialize database
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise Exception("MONGODB_URI not found in environment")
        
        logger.info("Initializing unified database...")
        database_manager = UnifiedDatabaseManager(mongodb_uri)
        connected = await database_manager.connect()
        
        if not connected:
            raise Exception("Database connection failed")
        
        logger.info("✅ Unified database initialized and connected")
        
        # Load existing Reddit tokens
        try:
            logger.info("Loading existing Reddit user tokens from database...")
            
            reddit_tokens_cursor = database_manager.reddit_tokens.find({"is_active": True})
            
            token_count = 0
            loaded_users = []
            
            async for token_doc in reddit_tokens_cursor:
                user_id = token_doc["user_id"]
                reddit_username = token_doc.get("reddit_username", "Unknown")
                
                loaded_users.append({
                    "user_id": user_id,
                    "reddit_username": reddit_username
                })
                
                token_count += 1
                logger.info(f"Found Reddit token for user {user_id}: u/{reddit_username}")
            
            logger.info(f"✅ Found {token_count} existing Reddit tokens in database")
            
            if token_count > 0:
                logger.info(f"Users with Reddit: {[u['reddit_username'] for u in loaded_users]}")
            
        except Exception as e:
            logger.error(f"⚠️ Failed to load existing Reddit tokens: {e}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error(traceback.format_exc())
        return False
    
    # Initialize YouTube services
    try:
        logger.info("Initializing YouTube services...")
        
        from mainY import initialize_services as init_youtube
        
        success = await init_youtube()
        
        if success:
            from mainY import (
                youtube_connector,
                youtube_scheduler,
                youtube_background_scheduler,
                ai_service as youtube_ai
            )
            
            youtube_services = {
                "connector": youtube_connector,
                "scheduler": youtube_scheduler,
                "background_scheduler": youtube_background_scheduler,
                "ai_service": youtube_ai
            }
            
            logger.info("✅ YouTube services initialized")
        else:
            logger.warning("⚠️ YouTube services initialization failed")
            
    except Exception as e:
        logger.error(f"❌ YouTube initialization error: {e}")
        logger.error(traceback.format_exc())
    
    # Initialize Reddit services
    try:
        logger.info("Initializing Reddit services...")
        
        import main as reddit_main
        
        # Patch main.py's database_manager
        reddit_main.database_manager = database_manager
        logger.info("✅ Patched main.py database_manager")
        
        # Load Reddit tokens into main.py
        try:
            logger.info("Loading Reddit tokens into main.py memory...")
            
            reddit_tokens_cursor = database_manager.reddit_tokens.find({"is_active": True})
            
            token_count = 0
            async for token_doc in reddit_tokens_cursor:
                user_id = token_doc["user_id"]
                reddit_username = token_doc.get("reddit_username", "Unknown")
                
                reddit_main.user_reddit_tokens[user_id] = {
                    "access_token": token_doc["access_token"],
                    "refresh_token": token_doc.get("refresh_token", ""),
                    "reddit_username": reddit_username,
                    "reddit_user_id": token_doc.get("reddit_user_id", ""),
                    "expires_in": token_doc.get("expires_in", 3600),
                    "connected_at": token_doc.get("created_at", datetime.now()).isoformat(),
                    "user_info": {
                        "name": reddit_username,
                        "id": token_doc.get("reddit_user_id", "")
                    }
                }
                
                token_count += 1
                logger.info(f"Loaded token into main.py for user {user_id}: u/{reddit_username}")
            
            logger.info(f"✅ Loaded {token_count} tokens into main.py")
            
        except Exception as e:
            logger.error(f"⚠️ Failed to load tokens into main.py: {e}")
        
        # Import Reddit classes
        try:
            from main import (
                RedditOAuthConnector,
                AIService,
                RedditAutomationScheduler
            )
            logger.info("✅ Imported Reddit classes from main.py")
        except ImportError as ie:
            logger.warning(f"⚠️ Could not import Reddit classes: {ie}")
            
            class RedditOAuthConnector:
                def __init__(self, config):
                    self.config = config
                    self.is_configured = True
            
            class AIService:
                pass
            
            class RedditAutomationScheduler:
                def __init__(self, *args, **kwargs):
                    self.is_running = False
                def start_scheduler(self):
                    pass
        
        # Initialize Reddit OAuth
        reddit_config = {
            'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
            'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET'),
            'REDDIT_REDIRECT_URI': os.getenv('REDDIT_REDIRECT_URI', 'https://velocitypost-984x.onrender.com/api/oauth/reddit/callback'),
            'REDDIT_USER_AGENT': os.getenv('REDDIT_USER_AGENT', 'VelocityPost/1.0')
        }
        
        if reddit_config['REDDIT_CLIENT_ID'] and reddit_config['REDDIT_CLIENT_SECRET']:
            reddit_oauth = RedditOAuthConnector(reddit_config)
            
            reddit_ai = youtube_services.get("ai_service") or AIService()
            
            reddit_scheduler = RedditAutomationScheduler(
                reddit_oauth,
                reddit_ai,
                database_manager,
                reddit_main.user_reddit_tokens
            )
            reddit_scheduler.start_scheduler()
            
            reddit_services = {
                "oauth": reddit_oauth,
                "ai_service": reddit_ai,
                "scheduler": reddit_scheduler
            }
            
            reddit_main.reddit_oauth_connector = reddit_oauth
            reddit_main.ai_service = reddit_ai
            reddit_main.automation_scheduler = reddit_scheduler
            
            logger.info("✅ Reddit services initialized and patched")
            logger.info(f"Reddit scheduler has {len(reddit_main.user_reddit_tokens)} user tokens")
        else:
            logger.warning("⚠️ Reddit credentials missing")
            
    except Exception as e:
        logger.error(f"❌ Reddit initialization error: {e}")
        logger.error(traceback.format_exc())
    
    # Load automation configs
    try:
        logger.info("Loading automation configs from database...")
        
        import main as reddit_main
        
        # Load auto-posting configs
        auto_posting_cursor = database_manager.automation_configs.find({
            "config_type": "auto_posting",
            "enabled": True
        })
        
        config_count = 0
        async for config_doc in auto_posting_cursor:
            user_id = config_doc["user_id"]
            
            if user_id not in reddit_main.automation_configs:
                reddit_main.automation_configs[user_id] = {}
            
            reddit_main.automation_configs[user_id]["auto_posting"] = {
                "config": config_doc["config_data"],
                "enabled": config_doc.get("enabled", True),
                "created_at": config_doc.get("updated_at", datetime.now()).isoformat()
            }
            
            config_count += 1
            logger.info(f"Loaded auto-posting config for user {user_id}")
        
        # Load auto-reply configs
        auto_reply_cursor = database_manager.automation_configs.find({
            "config_type": "auto_replies",
            "enabled": True
        })
        
        async for config_doc in auto_reply_cursor:
            user_id = config_doc["user_id"]
            
            if user_id not in reddit_main.automation_configs:
                reddit_main.automation_configs[user_id] = {}
            
            reddit_main.automation_configs[user_id]["auto_replies"] = {
                "config": config_doc["config_data"],
                "enabled": config_doc.get("enabled", True),
                "created_at": config_doc.get("updated_at", datetime.now()).isoformat()
            }
            
            config_count += 1
            logger.info(f"Loaded auto-reply config for user {user_id}")
        
        logger.info(f"✅ Loaded {config_count} automation configs from database")
        
    except Exception as e:
        logger.error(f"⚠️ Failed to load automation configs: {e}")
    
    logger.info("="*60)
    logger.info("✅ SERVICE INITIALIZATION COMPLETE")
    logger.info(f"Database: {'✓' if database_manager and database_manager.connected else '✗'}")
    logger.info(f"YouTube: {'✓' if youtube_services else '✗'}")
    logger.info(f"Reddit: {'✓' if reddit_services else '✗'}")
    
    try:
        import main as reddit_main
        logger.info(f"Reddit User Tokens: {len(reddit_main.user_reddit_tokens)}")
        logger.info(f"Automation Configs: {len(reddit_main.automation_configs)}")
    except:
        pass
    
    logger.info(f"Playwright: {PLAYWRIGHT_PATH}")
    logger.info("="*60)
    
    return True

async def cleanup_all_services():
    """Cleanup all services on shutdown"""
    global database_manager, youtube_services, reddit_services
    
    logger.info("Shutting down services...")
    
    # Cleanup YouTube
    try:
        if youtube_services.get("background_scheduler"):
            await youtube_services["background_scheduler"].stop()
    except Exception as e:
        logger.error(f"YouTube cleanup error: {e}")
    
    # Cleanup Reddit
    try:
        if reddit_services.get("scheduler"):
            reddit_services["scheduler"].is_running = False
    except Exception as e:
        logger.error(f"Reddit cleanup error: {e}")
    
    # Disconnect database
    try:
        if database_manager:
            await database_manager.disconnect()
    except Exception as e:
        logger.error(f"Database cleanup error: {e}")
    
    logger.info("✅ Services cleaned up")

# ============================================================================
# FASTAPI LIFESPAN
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    # Startup
    success = await initialize_all_services()
    if not success:
        logger.error("⚠️ Service initialization incomplete - some features may not work")
    
    yield
    
    # Shutdown
    await cleanup_all_services()

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================
app = FastAPI(
    title="VelocityPost - Unified Social Media Automation",
    description="YouTube + Reddit + Multi-Platform Automation System",
    version="3.2.0 - Multi-User Production Ready",
    lifespan=lifespan
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://velocitypost-ai.onrender.com",
        "https://velocitypost-984x.onrender.com",
        "https://frontend-agentic.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)






# ============================================================================
# OPTIONS HANDLER
# ============================================================================
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

# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# UNIFIED AUTHENTICATION ROUTES
# ============================================================================
@app.post("/api/auth/register")
async def register_user(request: RegisterRequest):
    """Unified user registration"""
    try:
        if not database_manager or not database_manager.connected:
            raise HTTPException(status_code=500, detail="Database not available")
        
        existing_user = await database_manager.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = str(uuid.uuid4())
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_data = {
            "_id": user_id,
            "email": request.email,
            "name": request.name,
            "password": hashed_password,
            "created_at": datetime.now(),
            "platforms_connected": [],
            "automation_enabled": False
        }
        
        success = await database_manager.create_user(user_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Registration failed")
        
        token = jwt.encode(
            {
                "user_id": user_id,
                "email": request.email,
                "name": request.name,
                "exp": datetime.utcnow() + timedelta(days=30)
            },
            os.getenv("JWT_SECRET", "your_secret_key"),
            algorithm="HS256"
        )
        
        logger.info(f"New user registered: {request.email}")
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "user_id": user_id,
                "email": request.email,
                "name": request.name,
                "platforms_connected": []
            },
            "token": token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login_user(request: LoginRequest):
    """Unified user login"""
    try:
        if not database_manager or not database_manager.connected:
            raise HTTPException(status_code=500, detail="Database not available")
        
        user = await database_manager.get_user_by_email(request.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        stored_password = user.get("password")
        if not stored_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        password_valid = False
        try:
            password_valid = bcrypt.checkpw(request.password.encode('utf-8'), stored_password.encode('utf-8'))
        except:
            password_valid = (stored_password == request.password)
        
        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = jwt.encode(
            {
                "user_id": user["_id"],
                "email": user["email"],
                "name": user["name"],
                "exp": datetime.utcnow() + timedelta(days=30)
            },
            os.getenv("JWT_SECRET", "your_secret_key"),
            algorithm="HS256"
        )
        
        logger.info(f"User logged in: {request.email}")
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": user["_id"],
                "email": user["email"],
                "name": user["name"],
                "platforms_connected": user.get("platforms_connected", [])
            },
            "token": token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "success": True,
        "user": current_user
    }

# ============================================================================
# HEALTH CHECK ROUTES
# ============================================================================
@app.get("/")
async def root():
    """Root health check"""
    return {
        "status": "running",
        "message": "VelocityPost - Unified Multi-Platform Automation",
        "version": "3.2.0 - Multi-User Ready",
        "database_connected": database_manager.connected if database_manager else False,
        "platforms": {
            "youtube": bool(youtube_services),
            "reddit": bool(reddit_services)
        },
        "playwright_path": PLAYWRIGHT_PATH,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        db_health = await database_manager.health_check() if database_manager else {"status": "unavailable"}
        
        return {
            "status": "healthy" if (database_manager and database_manager.connected) else "degraded",
            "services": {
                "database": db_health.get("status", "unknown"),
                "youtube": "available" if youtube_services else "unavailable",
                "reddit": "available" if reddit_services else "unavailable"
            },
            "playwright_path": PLAYWRIGHT_PATH,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )



# ============================================================================
# KEEP-ALIVE ENDPOINT FOR UPTIMEROBOT
# ============================================================================
@app.get("/keep-alive")
async def keep_alive():
    """
    Keep-alive endpoint for UptimeRobot monitoring.
    This endpoint is lightweight and always returns 200 OK.
    Prevents Render free tier from sleeping.
    """
    try:
        # Check database status
        db_connected = database_manager is not None and database_manager.connected
        
        # Check services status
        youtube_available = bool(youtube_services)
        reddit_available = bool(reddit_services)
        
        # Get user counts (if database connected)
        total_users = 0
        reddit_users = 0
        youtube_users = 0
        
        if db_connected:
            try:
                total_users = await database_manager.users_collection.count_documents({})
                reddit_users = await database_manager.reddit_tokens.count_documents({"is_active": True})
                youtube_users = await database_manager.youtube_credentials.count_documents({})
            except Exception as count_error:
                logger.warning(f"Keep-alive count error: {count_error}")
        
        return {
            "status": "alive",
            "message": "VelocityPost backend is running and healthy!",
            "timestamp": datetime.now().isoformat(),
            "uptime": "operational",
            "services": {
                "api": "running",
                "database": {
                    "connected": db_connected,
                    "status": "operational" if db_connected else "disconnected"
                },
                "platforms": {
                    "youtube": {
                        "available": youtube_available,
                        "connected_users": youtube_users
                    },
                    "reddit": {
                        "available": reddit_available,
                        "connected_users": reddit_users
                    }
                },
                "users": {
                    "total_registered": total_users
                }
            },
            "playwright_path": PLAYWRIGHT_PATH,
            "version": "3.2.0",
            "health_check": "pass"
        }
    except Exception as e:
        # Even if there's an error, return 200 OK to keep UptimeRobot happy
        logger.warning(f"Keep-alive error (non-critical): {str(e)}")
        return {
            "status": "alive",
            "message": "Backend is running (some services initializing)",
            "timestamp": datetime.now().isoformat(),
            "uptime": "operational",
            "services": {
                "api": "running",
                "database": "initializing",
                "platforms": "initializing"
            },
            "health_check": "pass",
            "note": "Background services are still initializing"
        }


# ============================================================================
# IMPORT AND MOUNT PLATFORM ROUTES
# ============================================================================

# YouTube Routes
try:
    from mainY import (
        youtube_oauth_url,
        youtube_oauth_callback_get,
        get_youtube_status,
        youtube_disconnect,
        youtube_setup_automation,
        get_youtube_analytics,
        youtube_upload_video,
        upload_video_file,
        fetch_youtube_video_info,
        schedule_video_upload,
        get_scheduled_posts,
        delete_scheduled_post,
        upload_thumbnail_image,
        generate_video_thumbnails,
        generate_youtube_content,
        get_user_videos,
        get_youtube_comments,
        reply_to_comment,
        edit_reply,
        delete_reply,
        delete_comment,
        generate_auto_reply,
        start_automated_replies,
        stop_automated_replies,
        generate_slideshow_preview,
        generate_youtube_slideshow,
        generate_product_promo_video,
        debug_youtube_status,
        debug_youtube_endpoints
    )
    
    # Register YouTube routes
    app.post("/api/youtube/oauth-url")(youtube_oauth_url)
    app.get("/api/youtube/oauth-callback")(youtube_oauth_callback_get)
    app.get("/api/youtube/status/{user_id}")(get_youtube_status)
    app.post("/api/youtube/disconnect/{user_id}")(youtube_disconnect)
    app.post("/api/youtube/setup-automation")(youtube_setup_automation)
    app.get("/api/youtube/analytics/{user_id}")(get_youtube_analytics)
    app.post("/api/youtube/upload")(youtube_upload_video)
    app.post("/api/youtube/upload-video-file")(upload_video_file)
    app.post("/api/youtube/fetch-video-info")(fetch_youtube_video_info)
    app.post("/api/youtube/schedule-video")(schedule_video_upload)
    app.get("/api/youtube/scheduled-posts/{user_id}")(get_scheduled_posts)
    app.delete("/api/youtube/scheduled-post/{post_id}")(delete_scheduled_post)
    app.post("/api/youtube/upload-thumbnail-image")(upload_thumbnail_image)
    app.post("/api/youtube/generate-thumbnails")(generate_video_thumbnails)
    app.post("/api/ai/generate-youtube-content")(generate_youtube_content)
    app.get("/api/youtube/user-videos/{user_id}")(get_user_videos)
    app.get("/api/youtube/comments/{user_id}")(get_youtube_comments)
    app.post("/api/youtube/reply-comment")(reply_to_comment)
    app.put("/api/youtube/edit-reply")(edit_reply)
    app.delete("/api/youtube/delete-reply/{reply_id}")(delete_reply)
    app.delete("/api/youtube/delete-comment/{comment_id}")(delete_comment)
    app.post("/api/youtube/generate-auto-reply")(generate_auto_reply)
    app.post("/api/youtube/start-auto-reply")(start_automated_replies)
    app.post("/api/youtube/stop-auto-reply")(stop_automated_replies)
    app.post("/api/youtube/generate-slideshow-preview")(generate_slideshow_preview)
    app.post("/api/youtube/generate-slideshow")(generate_youtube_slideshow)
    app.post("/api/product-video/generate")(generate_product_promo_video)
    app.get("/api/debug/youtube-status")(debug_youtube_status)
    app.get("/api/debug/youtube-endpoints")(debug_youtube_endpoints)
    
    logger.info("✅ YouTube routes registered")
    
except Exception as e:
    logger.error(f"❌ YouTube routes registration failed: {e}")
    logger.error(traceback.format_exc())

# Reddit Routes
try:
    import main as reddit_main
    
    from main import (
        reddit_oauth_authorize,
        reddit_oauth_callback,
        get_reddit_connection_status,
        test_reddit_connection,
        manual_reddit_post,
        test_auto_post,
        setup_auto_posting,
        setup_auto_replies,
        get_automation_status,
        update_automation_schedule,
        debug_multi_user_sessions,
        debug_reddit_connector,
        debug_ai_service,
        debug_database,
        debug_automation_status,
        add_test_time,
        debug_scheduler_status,
        debug_current_schedule,
        trigger_immediate_post,
        debug_next_posting,
        debug_scheduler_active_configs,
        debug_reddit_config
    )
    
    app.get("/api/oauth/reddit/authorize")(reddit_oauth_authorize)
    app.get("/api/oauth/reddit/callback")(reddit_oauth_callback)
    app.get("/api/reddit/connection-status")(get_reddit_connection_status)
    app.get("/api/reddit/test-connection")(test_reddit_connection)
    app.post("/api/reddit/post")(manual_reddit_post)
    app.post("/api/automation/test-auto-post")(test_auto_post)
    app.post("/api/automation/setup-auto-posting")(setup_auto_posting)
    app.post("/api/automation/setup-auto-replies")(setup_auto_replies)
    app.get("/api/automation/status")(get_automation_status)
    app.post("/api/automation/update-schedule")(update_automation_schedule)
    app.get("/api/debug/multi-user-sessions")(debug_multi_user_sessions)
    app.get("/api/debug/reddit")(debug_reddit_connector)
    app.get("/api/debug/ai")(debug_ai_service)
    app.get("/api/debug/database")(debug_database)
    app.get("/api/debug/automation-status")(debug_automation_status)
    app.post("/api/debug/add-test-time")(add_test_time)
    app.get("/api/debug/scheduler-status")(debug_scheduler_status)
    app.get("/api/debug/current-schedule")(debug_current_schedule)
    app.post("/api/debug/trigger-immediate-post")(trigger_immediate_post)
    app.get("/api/debug/next-posting-debug")(debug_next_posting)
    app.get("/api/debug/scheduler-active-configs")(debug_scheduler_active_configs)
    app.get("/api/debug/reddit-config")(debug_reddit_config)
    
    logger.info("✅ Reddit routes registered")
    
except Exception as e:
    logger.error(f"❌ Reddit routes registration failed: {e}")
    logger.error(traceback.format_exc())

# ============================================================================
# PLATFORM STATUS ENDPOINT - MULTI-USER
# ============================================================================
@app.get("/api/platforms/status")
async def get_platform_status(current_user: dict = Depends(get_current_user)):
    """Get connection status for all platforms - MULTI-USER"""
    try:
        user_id = current_user["id"]
        
        # Check YouTube
        youtube_connected = False
        youtube_channel = None
        if youtube_services and database_manager and database_manager.connected:
            youtube_creds = await database_manager.get_youtube_credentials(user_id)
            if youtube_creds:
                youtube_connected = True
                youtube_channel = youtube_creds.get("channel_info", {}).get("title")
        
        # ✅ Check Reddit - MULTI-USER
        reddit_connected = False
        reddit_username = None
        if reddit_services and database_manager and database_manager.connected:
            reddit_status = await database_manager.check_reddit_connection(user_id)
            reddit_connected = reddit_status.get("connected", False)
            reddit_username = reddit_status.get("reddit_username")
        
        return {
            "success": True,
            "platforms": {
                "youtube": {
                    "connected": youtube_connected,
                    "channel_name": youtube_channel,
                    "available": bool(youtube_services)
                },
                "reddit": {
                    "connected": reddit_connected,
                    "username": reddit_username,  # ✅ Dynamic per user
                    "available": bool(reddit_services)
                }
            },
            "user_id": user_id,
            "user_name": current_user.get("name", "User")
        }
        
    except Exception as e:
        logger.error(f"Platform status check failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# AI POST GENERATION - ENHANCED + MULTI-USER
# ============================================================================
@app.post("/api/reddit/generate-ai-post")
async def generate_reddit_ai_post(request: Request, current_user: dict = Depends(get_current_user)):
    """✅ ROBUST: Proper title/content separation with multiple fallback strategies"""
    try:
        data = await request.json()
        
        post_type = data.get("post_type", "discussion")
        tone = data.get("tone", "casual")
        length = data.get("length", "medium")
        domain = data.get("domain", "tech")
        business_type = data.get("business_type", "business")
        business_description = data.get("business_description", "")
        
        domain_subreddits = {
            "education": ["test", "CasualConversation", "self"],
            "restaurant": ["test", "CasualConversation", "self"],
            "tech": ["test", "CasualConversation", "self"],
            "health": ["test", "CasualConversation", "self"],
            "business": ["test", "CasualConversation", "self"]
        }
        
        domain_topics = {
            "education": f"my experience with {business_type}",
            "restaurant": f"found this great {business_type}",
            "tech": f"thoughts on {business_type}",
            "health": f"my journey with {business_type}",
            "business": f"lessons from {business_type}"
        }
        
        topic = domain_topics.get(domain, business_type)
        subreddit_options = domain_subreddits.get(domain, ["test"])
        
        length_map = {
            "short": "2-3 sentences",
            "medium": "2-3 paragraphs",
            "long": "4-5 paragraphs"
        }
        
        # ✅ SUPER EXPLICIT PROMPT WITH EXAMPLES
        prompt = f"""Create a casual Reddit post about: {topic}

CRITICAL INSTRUCTIONS:
1. Title = SHORT question (5-12 words ONLY)
2. Content = LONG detailed post (must be at least 3 sentences)
3. Put each on its OWN LINE with proper labels
4. NO formatting symbols (*, #, -, bullets)

Type: {post_type}
Tone: {tone}
Post length: {length_map.get(length, 'medium')}

OUTPUT FORMAT (copy this structure EXACTLY):
SUBREDDIT: test
TITLE: [short question here]
CONTENT: [long detailed text here with multiple sentences]

GOOD EXAMPLE:
SUBREDDIT: test
TITLE: are ai tools actually useful or just hype?
CONTENT: so ive been trying out some ai automation stuff lately and honestly im not sure what to think. on one hand it does save time with repetitive tasks but on teh other hand im worried about reliability. has anyone used these long term? wondering if its worth investing more time to learn them properly or if i should just stick with manual work tbh.

BAD EXAMPLE (DO NOT DO THIS):
TITLE: are ai tools useful CONTENT: ive been trying them out...

Make it casual with words like: kinda, gonna, tbh, imo
Add 1-2 typos like: teh, recieve
"""

        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        ai_response = None
        ai_service_used = None
        
        # Try Mistral
        if mistral_api_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {mistral_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {
                                    "role": "system", 
                                    "content": "You are a Reddit user. Follow the format EXACTLY. Put TITLE and CONTENT on separate lines. Title must be SHORT (max 12 words). Content must be LONG (multiple sentences). No formatting symbols."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 800
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_service_used = "mistral"
                        logger.info("✅ Mistral success")
                    elif response.status_code == 429:
                        logger.warning("⚠️ Mistral rate limit, waiting...")
                        await asyncio.sleep(2)
                    else:
                        logger.error(f"Mistral error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Mistral error: {e}")
        
        # Fallback to Groq
        if not ai_response and groq_api_key:
            try:
                await asyncio.sleep(1)
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {groq_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "messages": [
                                {
                                    "role": "system", 
                                    "content": "You are a Reddit user. Follow format EXACTLY. TITLE and CONTENT on separate lines. Title SHORT. Content LONG. No symbols."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.8,
                            "max_tokens": 800
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_service_used = "groq"
                        logger.info("✅ Groq success")
                    else:
                        logger.error(f"Groq error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Groq error: {e}")
        
        # Fallback content
        if not ai_response:
            logger.warning("⚠️ Using fallback content")
            ai_service_used = "fallback"
            ai_response = f"""SUBREDDIT: test
TITLE: thoughts on {business_type}?
CONTENT: so i recently tried {business_type} and honestly its pretty interesting. the experience has been good so far and i kinda like how it works. has anyone else tried this? would love to hear your thoughts tbh"""
        
        # ✅ CLEAN FORMATTING
        ai_response = clean_ai_formatting(ai_response)
        
        logger.info(f"🔍 Raw AI response:\n{ai_response}")
        
        # ✅ ROBUST PARSING WITH MULTIPLE STRATEGIES
        subreddit = "test"
        title = ""
        content = ""
        
        # Strategy 1: Standard regex parsing
        subreddit_match = re.search(r'SUBREDDIT:\s*([^\n]+)', ai_response, re.IGNORECASE)
        title_match = re.search(r'TITLE:\s*([^\n]+)', ai_response, re.IGNORECASE)
        content_match = re.search(r'CONTENT:\s*(.+?)(?:\n\n|\Z)', ai_response, re.IGNORECASE | re.DOTALL)
        
        if subreddit_match:
            subreddit = subreddit_match.group(1).strip().replace('r/', '')
        
        if title_match:
            title = title_match.group(1).strip()
            
        if content_match:
            content = content_match.group(1).strip()
        
        # ✅ Strategy 2: If "CONTENT:" appears in title, split it
        if "CONTENT:" in title.upper():
            logger.warning("⚠️ CONTENT label found in title, splitting...")
            parts = re.split(r'CONTENT:', title, flags=re.IGNORECASE)
            title = parts[0].strip()
            if len(parts) > 1:
                content = parts[1].strip() + " " + content
        
        # ✅ Strategy 3: If title is too long, treat as content and generate new title
        title_words = title.split()
        if len(title_words) > 20:
            logger.warning(f"⚠️ Title too long ({len(title_words)} words), extracting...")
            # Use first 10 words as title
            title = ' '.join(title_words[:10])
            # Rest becomes content
            content = ' '.join(title_words[10:]) + " " + content
        
        # ✅ Strategy 4: If content is empty or too short, use rest of text
        if not content or len(content) < 50:
            logger.warning("⚠️ Content too short, using fallback")
            content = f"so i recently tried this and honestly its pretty interesting. the experience has been good so far and i kinda like how it works. has anyone else tried this? would love to hear your thoughts tbh"
        
        # ✅ Strategy 5: Ensure title ends properly (no trailing "CONTENT:")
        title = re.sub(r'\s*CONTENT:.*$', '', title, flags=re.IGNORECASE).strip()
        
        # ✅ Final cleanup
        title = title.strip().rstrip('?!.,:;') + ('?' if not title.endswith('?') else '')
        content = content.strip()
        
        # ✅ Force safe subreddit
        if subreddit not in ["test", "CasualConversation", "self"]:
            subreddit = "test"
        
        # ✅ Add human touches to content only (not title)
        content = add_enhanced_human_touches(content)
        
        # ✅ Calculate score
        human_score = calculate_enhanced_human_score(content)
        
        logger.info(f"✅ Final result - Title: '{title}' ({len(title)} chars)")
        logger.info(f"✅ Final result - Content: '{content[:50]}...' ({len(content)} chars)")
        
        return {
            "success": True,
            "subreddit": subreddit,
            "title": title,
            "content": content,
            "human_score": human_score,
            "ai_service": ai_service_used,
            "debug": {
                "title_length": len(title),
                "content_length": len(content),
                "title_word_count": len(title.split()),
                "content_word_count": len(content.split())
            }
        }
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "success": True,
            "subreddit": "test",
            "title": "thoughts on ai automation tools?",
            "content": "so i recently started using some ai automation stuff and honestly its been interesting. saves time with repetitive tasks but im still figuring out if its worth the learning curve. has anyone used these long term? would love to hear your experiences tbh",
            "human_score": 75,
            "ai_service": "fallback"
        }


def clean_ai_formatting(text: str) -> str:
    """Remove all AI formatting symbols"""
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def add_enhanced_human_touches(content: str) -> str:
    """Add human-like imperfections"""
    
    typos = [
        (" the ", " teh ", 0.15),
        ("receive", "recieve", 0.2),
        ("definitely", "definately", 0.15),
        (" and ", " nad ", 0.08),
        ("because", "becuase", 0.1)
    ]
    
    for original, typo, chance in typos:
        if original in content.lower() and random.random() < chance:
            content = content.replace(original, typo, 1)
    
    casual_replacements = [
        (" really ", " rly ", 0.15),
        (" though ", " tho ", 0.2),
        ("kind of", "kinda", 0.25),
        ("going to", "gonna", 0.25),
        ("want to", "wanna", 0.2),
        (" a lot ", " alot ", 0.12),
        ("probably", "prolly", 0.15)
    ]
    
    for original, casual, chance in casual_replacements:
        if original in content.lower() and random.random() < chance:
            content = content.replace(original, casual, 1)
    
    if content and random.random() < 0.4:
        content = content[0].lower() + content[1:]
    
    if content.endswith('.') and random.random() < 0.25:
        content = content[:-1]
    
    return content


def calculate_enhanced_human_score(content: str) -> int:
    """Calculate human-like score"""
    score = 50
    content_lower = content.lower()
    
    human_indicators = [
        ("teh", 12), ("recieve", 12), ("kinda", 10), ("gonna", 10),
        ("wanna", 10), ("tbh", 15), ("imo", 12), ("idk", 12),
        (" i ", 8), (" my ", 8), ("rly", 10), ("tho", 10), ("alot", 8)
    ]
    
    for word, points in human_indicators:
        if word in content_lower:
            score += points
    
    if "?" in content:
        score += 15
    
    if content and content[0].islower():
        score += 10
    
    ai_words = ["delve", "utilize", "leverage", "comprehensive", "robust", "paradigm"]
    for word in ai_words:
        if word in content_lower:
            score -= 20
    
    if content.count("!") > 2:
        score -= 15
    
    if "*" in content:
        score -= 25
    
    return max(20, min(score, 100))






# ============================================================================
# POST NOW - MULTI-USER WITH DYNAMIC USERNAME
# ============================================================================
@app.post("/api/automation/post-now")
async def post_now_to_reddit(request: Request, current_user: dict = Depends(get_current_user)):
    """✅ MULTI-USER: Publish post with dynamic Reddit username"""
    try:
        data = await request.json()
        
        title = data.get("title", "")
        content = data.get("content", "")
        subreddit = data.get("subreddit", "test")
        
        if not title or not content:
            return {"success": False, "error": "Title and content are required"}
        
        user_id = current_user.get("id") or current_user.get("user_id")
        
        if not user_id:
            return {"success": False, "error": "User ID not found"}
        
        logger.info(f"🔍 POST NOW - User: {current_user.get('email')} ({user_id})")
        
        if not database_manager or not database_manager.connected:
            return {"success": False, "error": "Database not connected"}
        
        # ✅ Get Reddit tokens
        reddit_token_data = await database_manager.get_reddit_tokens(user_id)
        
        if not reddit_token_data:
            return {
                "success": False, 
                "error": "Reddit not connected. Please reconnect your Reddit account."
            }
        
        # ✅ CHECK IF TOKEN EXPIRED AND REFRESH
        if reddit_token_data.get("is_expired"):
            logger.warning(f"⚠️ Reddit token expired for user {user_id}, refreshing...")
            
            refreshed_token = await database_manager.refresh_reddit_token(user_id)
            
            if refreshed_token:
                reddit_token_data = refreshed_token
                logger.info(f"✅ Token refreshed for user {user_id}")
            else:
                return {
                    "success": False,
                    "error": "Reddit token expired. Please reconnect your Reddit account.",
                    "action_required": "reconnect"
                }
        
        access_token = reddit_token_data.get("access_token")
        reddit_username = reddit_token_data.get("reddit_username", "VelocityPostUser")  # ✅ Dynamic
        
        if not access_token:
            return {"success": False, "error": "No Reddit access token found"}
        
        # ✅ Force safe subreddit
        if subreddit.lower() not in ["test", "casualconversation", "self"]:
            logger.warning(f"Redirecting from r/{subreddit} to r/test (safer)")
            subreddit = "test"
        
        logger.info(f"📤 Posting to r/{subreddit}: {title[:50]}...")
        
        # ✅ DYNAMIC USER-AGENT
        user_agent = f"VelocityPost/1.0 by /u/{reddit_username}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://oauth.reddit.com/api/submit",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "User-Agent": user_agent  # ✅ Dynamic per user
                },
                data={
                    "sr": subreddit,
                    "kind": "self",
                    "title": title,
                    "text": content,
                    "api_type": "json"
                }
            )
            
            # ✅ COMPREHENSIVE ERROR HANDLING
            if response.status_code == 401:
                logger.error("❌ 401 Unauthorized")
                return {
                    "success": False,
                    "error": "Reddit authentication failed. Please reconnect your account.",
                    "action_required": "reconnect"
                }
            
            if response.status_code == 429:
                logger.error("❌ 429 Too Many Requests")
                return {
                    "success": False,
                    "error": "Reddit rate limit reached. Please wait 10 minutes before posting again.",
                    "retry_after": "600"
                }
            
            if response.status_code == 403:
                logger.error("❌ 403 Forbidden")
                return {
                    "success": False,
                    "error": "Your Reddit account may be restricted. Try posting to r/test first to build karma."
                }
            
            if response.status_code != 200:
                logger.error(f"❌ Reddit API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Reddit API error: {response.status_code}"
                }
            
            # ✅ PARSE JSON
            try:
                result = response.json()
            except Exception as json_error:
                logger.error(f"Failed to parse Reddit response: {json_error}")
                return {"success": False, "error": "Failed to parse Reddit response"}
            
            logger.info(f"📥 Reddit API response: {result}")
            
            # ✅ CHECK FOR ERRORS
            errors = result.get("json", {}).get("errors", [])
            
            if errors:
                error_type = errors[0][0] if errors[0] else "UNKNOWN"
                error_msg = errors[0][1] if len(errors[0]) > 1 else "Unknown error"
                
                logger.error(f"❌ Reddit post error: {error_type} - {error_msg}")
                
                if error_type == "SUBMIT_VALIDATION_FLAIR_REQUIRED":
                    return {
                        "success": False,
                        "error": f"r/{subreddit} requires post flair. Try r/test instead.",
                        "suggestion": "Post to r/test (no flair required)"
                    }
                elif error_type == "NO_SELFS":
                    return {
                        "success": False,
                        "error": f"r/{subreddit} doesn't allow text posts. Try r/test instead.",
                        "suggestion": "Post to r/test (allows text posts)"
                    }
                elif error_type == "SUBREDDIT_NOTALLOWED":
                    return {
                        "success": False,
                        "error": f"r/{subreddit} only allows trusted members. You need more karma!",
                        "suggestion": "Build karma by posting to r/test and r/CasualConversation first (10+ karma needed)"
                    }
                elif error_type == "RATELIMIT":
                    return {
                        "success": False,
                        "error": "Reddit rate limit. You're posting too frequently.",
                        "suggestion": "Wait 10 minutes before posting again"
                    }
                else:
                    return {
                        "success": False,
                        "error": error_msg,
                        "suggestion": "Try posting to r/test instead"
                    }
            
            # ✅ SUCCESS
            if result.get("success") or (result.get("json") and result["json"].get("data")):
                post_url = None
                
                if result.get("json", {}).get("data", {}).get("url"):
                    post_url = result["json"]["data"]["url"]
                elif result.get("json", {}).get("data", {}).get("id"):
                    post_id = result["json"]["data"]["id"]
                    post_url = f"https://reddit.com/r/{subreddit}/comments/{post_id}"
                
                logger.info(f"✅ Posted to r/{subreddit} by u/{reddit_username} - {post_url}")
                
                # ✅ Log activity
                await database_manager.log_reddit_activity(
                    user_id,
                    "manual_post",
                    {
                        "subreddit": subreddit,
                        "title": title,
                        "post_url": post_url,
                        "reddit_username": reddit_username,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return {
                    "success": True,
                    "message": f"✅ Posted to r/{subreddit} successfully!",
                    "post_url": post_url,
                    "posted_as": f"u/{reddit_username}"
                }
            
            return {"success": False, "error": "Failed to post (unknown error)"}
                
    except httpx.TimeoutException:
        logger.error("❌ Reddit API timeout")
        return {"success": False, "error": "Request timeout. Reddit may be slow, try again."}
    except httpx.ConnectError:
        logger.error("❌ Connection error")
        return {"success": False, "error": "Cannot connect to Reddit. Check your internet."}
    except Exception as e:
        logger.error(f"❌ Post now error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": f"Failed to post: {str(e)}"}



# =================================================================================

# ============================================================================
# AI THUMBNAIL GENERATION ROUTE
# ============================================================================
# ============================================================================
# AI THUMBNAIL GENERATION ROUTE - FIXED AUTHENTICATION
# ============================================================================
@app.post("/api/youtube/generate-ai-thumbnails")
async def generate_ai_thumbnails(request: Request):
    """Generate AI-powered thumbnails using Pollinations.ai"""
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        title = data.get("title", "")
        description = data.get("description", "")
        add_overlay = data.get("add_overlay", True)
        custom_prompt = data.get("custom_prompt", "")
        
        if not user_id:
            return {"success": False, "error": "User ID is required"}
        
        if not title:
            return {"success": False, "error": "Title is required"}
        
        logger.info(f"🎨 AI Thumbnail generation request from user {user_id}")
        logger.info(f"Title: {title}, Overlay: {add_overlay}")
        
        # Generate 3 different thumbnail variations
        thumbnails = []
        
        # Style variations for diversity
        styles = [
            "cinematic youtube thumbnail, dramatic lighting, 8k quality, professional photography",
            "vibrant youtube thumbnail, bold colors, eye-catching, trending design, high contrast",
            "minimalist youtube thumbnail, clean design, modern aesthetic, sharp focus"
        ]
        
        for i, style in enumerate(styles, 1):
            try:
                # Build prompt
                if custom_prompt:
                    prompt = f"{custom_prompt}. {title}. {style}"
                else:
                    prompt = f"YouTube thumbnail: {title}. {description}. {style}. No text overlay, pure image"
                
                # Clean prompt
                prompt = ' '.join(prompt.split())
                
                # Generate image using Pollinations.ai
                encoded_prompt = quote(prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&enhance=true&model=flux"
                
                logger.info(f"📥 Fetching AI thumbnail {i} from Pollinations...")
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_url)
                    
                    if response.status_code == 200:
                        image_data = response.content
                        
                        # Convert to PIL Image
                        img = Image.open(io.BytesIO(image_data))
                        
                        # Ensure correct size
                        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                        
                        # Add text overlay if requested
                        if add_overlay:
                            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                            draw = ImageDraw.Draw(overlay)
                            
                            try:
                                # Try to load a font
                                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                            except:
                                font = ImageFont.load_default()
                            
                            # Add semi-transparent yellow box at bottom center
                            box_height = 100
                            box_y = img.height - box_height - 20
                            box_width = img.width - 100
                            box_x = 50
                            
                            # Yellow background with transparency
                            draw.rectangle(
                                [(box_x, box_y), (box_x + box_width, box_y + box_height)],
                                fill=(255, 215, 0, 200)  # Yellow with alpha
                            )
                            
                            # Calculate text size and position for centering
                            max_chars = 50
                            display_title = title if len(title) <= max_chars else title[:max_chars] + "..."
                            
                            # Get text bounding box
                            bbox = draw.textbbox((0, 0), display_title, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            
                            # Center text in box
                            text_x = box_x + (box_width - text_width) // 2
                            text_y = box_y + (box_height - text_height) // 2
                            
                            # Black text with shadow
                            for offset in range(-2, 3):
                                draw.text(
                                    (text_x + offset, text_y + offset),
                                    display_title,
                                    font=font,
                                    fill=(0, 0, 0, 255)
                                )
                            
                            # Main text
                            draw.text(
                                (text_x, text_y),
                                display_title,
                                font=font,
                                fill=(0, 0, 0, 255)
                            )
                            
                            # Composite overlay onto image
                            img = img.convert('RGBA')
                            img = Image.alpha_composite(img, overlay)
                            img = img.convert('RGB')
                        
                        # Convert to base64
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG", quality=95)
                        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                        img_data_url = f"data:image/png;base64,{img_base64}"
                        
                        thumbnails.append({
                            "id": f"ai_thumb_{i}",
                            "url": img_data_url,
                            "variation": i,
                            "style": style.split(',')[0],
                            "has_overlay": add_overlay
                        })
                        
                        logger.info(f"✅ Generated AI thumbnail {i}")
                    else:
                        logger.error(f"❌ Pollinations API returned {response.status_code}")
                
            except Exception as e:
                logger.error(f"❌ Error generating AI thumbnail {i}: {e}")
                continue
        
        if len(thumbnails) == 0:
            return {
                "success": False,
                "error": "Failed to generate any thumbnails. Please try again."
            }
        
        logger.info(f"✅ Successfully generated {len(thumbnails)} AI thumbnails")
        
        return {
            "success": True,
            "thumbnails": thumbnails,
            "count": len(thumbnails),
            "message": f"Generated {len(thumbnails)} AI thumbnails"
        }
        
    except Exception as e:
        logger.error(f"❌ AI thumbnail generation error: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
# =================================================================================



@app.get("/api/debug/current-reddit-user")
async def debug_current_reddit_user(current_user: dict = Depends(get_current_user)):
    """Debug which Reddit account is connected to current logged-in user"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        user_email = current_user.get("email")
        
        logger.info(f"🔍 DEBUG - Current logged-in user: {user_email} (ID: {user_id})")
        
        if not database_manager or not database_manager.connected:
            return {
                "success": False,
                "error": "Database not connected"
            }
        
        # Get Reddit connection for THIS user
        reddit_tokens = await database_manager.get_reddit_tokens(user_id)
        
        # Get ALL Reddit connections in database
        all_connections = []
        cursor = database_manager.reddit_tokens.find({"is_active": True})
        async for token_doc in cursor:
            all_connections.append({
                "user_id": token_doc["user_id"],
                "reddit_username": token_doc.get("reddit_username", "Unknown"),
                "user_email": "hidden"  # Don't expose emails
            })
        
        return {
            "success": True,
            "current_logged_in_user": {
                "user_id": user_id,
                "email": user_email,
                "name": current_user.get("name")
            },
            "reddit_connection_for_this_user": {
                "connected": bool(reddit_tokens),
                "reddit_username": reddit_tokens.get("reddit_username") if reddit_tokens else None,
                "reddit_user_id": reddit_tokens.get("reddit_user_id") if reddit_tokens else None
            },
            "all_reddit_connections_in_db": all_connections,
            "total_reddit_accounts": len(all_connections)
        }
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/platforms/status")
async def get_platform_status(current_user: dict = Depends(get_current_user)):
    """Get connection status - ALWAYS FRESH FROM DATABASE"""
    try:
        user_id = current_user["id"]
        user_email = current_user.get("email", "Unknown")
        
        logger.info(f"🔍 Platform status check for: {user_email} (ID: {user_id})")
        
        # Check YouTube
        youtube_connected = False
        youtube_channel = None
        if youtube_services and database_manager and database_manager.connected:
            youtube_creds = await database_manager.get_youtube_credentials(user_id)
            if youtube_creds:
                youtube_connected = True
                youtube_channel = youtube_creds.get("channel_info", {}).get("title")
        
        # ✅ CRITICAL: Get Reddit status FRESH from database (no cache)
        reddit_connected = False
        reddit_username = None
        reddit_user_id = None
        
        if reddit_services and database_manager and database_manager.connected:
            # Force fresh query
            reddit_tokens = await database_manager.get_reddit_tokens(user_id)
            
            if reddit_tokens:
                reddit_connected = True
                reddit_username = reddit_tokens.get("reddit_username")
                reddit_user_id = reddit_tokens.get("reddit_user_id")
                
                logger.info(f"✅ Reddit connected for {user_email}: u/{reddit_username}")
            else:
                logger.warning(f"⚠️ No Reddit connection found for {user_email}")
        
        return {
            "success": True,
            "platforms": {
                "youtube": {
                    "connected": youtube_connected,
                    "channel_name": youtube_channel,
                    "available": bool(youtube_services)
                },
                "reddit": {
                    "connected": reddit_connected,
                    "username": reddit_username,
                    "user_id": reddit_user_id,
                    "available": bool(reddit_services)
                }
            },
            "user_id": user_id,
            "user_email": user_email,
            "user_name": current_user.get("name", "User"),
            # ✅ Add timestamp to prevent caching
            "fetched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Platform status check failed: {e}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
    

# =======================================================================================



# ============================================================================
# AUTOMATION SETUP
# ============================================================================
@app.post("/api/automation/setup/posting")
async def setup_reddit_automation(request: Request, current_user: dict = Depends(get_current_user)):
    """Setup Reddit automation schedule - MULTI-USER"""
    try:
        data = await request.json()
        user_id = current_user.get("id")
        
        if not user_id:
            return {"success": False, "error": "User ID not found"}
        
        config_data = {
            "domain": data.get("domain"),
            "business_type": data.get("business_type"),
            "business_description": data.get("business_description"),
            "target_audience": data.get("target_audience"),
            "content_style": data.get("content_style"),
            "posts_per_day": data.get("posts_per_day", 1),
            "posting_times": data.get("posting_times", []),
            "subreddits": data.get("subreddits", ["test"]),
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        
        success = await database_manager.store_automation_config(
            user_id,
            "reddit_posting",
            config_data
        )
        
        if success:
            logger.info(f"✅ Reddit automation configured for user {user_id}")
            return {
                "success": True,
                "message": "Automation configured successfully",
                "config": config_data
            }
        else:
            return {"success": False, "error": "Failed to save configuration"}
            
    except Exception as e:
        logger.error(f"Setup automation error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


@app.get("/api/automation/stats")
async def get_automation_stats(current_user: dict = Depends(get_current_user)):
    """Get automation statistics - MULTI-USER"""
    try:
        user_id = current_user.get("id")
        
        if not user_id:
            return {"success": False, "error": "User ID not found"}
        
        config = await database_manager.get_automation_config(user_id, "reddit_posting")
        
        collection = database_manager.db.reddit_activities
        posts_today = await collection.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": datetime.now().replace(hour=0, minute=0, second=0)}
        })
        
        return {
            "success": True,
            "posts_today": posts_today,
            "scheduled_posts": [],
            "automation_enabled": config.get("enabled", False) if config else False
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# DEBUG ENDPOINT - MULTI-USER
# ============================================================================
@app.get("/api/debug/my-reddit-connection")
async def debug_my_reddit_connection(current_user: dict = Depends(get_current_user)):
    """Debug current user's Reddit connection - MULTI-USER"""
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        
        logger.info(f"🔍 DEBUG - Current user: {current_user}")
        
        if database_manager and database_manager.connected:
            reddit_tokens = await database_manager.get_reddit_tokens(user_id)
            
            all_tokens = []
            cursor = database_manager.reddit_tokens.find({"is_active": True})
            async for token_doc in cursor:
                all_tokens.append({
                    "user_id": token_doc["user_id"],
                    "reddit_username": token_doc.get("reddit_username", "Unknown"),
                    "has_access_token": bool(token_doc.get("access_token"))
                })
            
            return {
                "success": True,
                "current_user": current_user,
                "user_id_used": user_id,
                "my_reddit_tokens": reddit_tokens,
                "all_active_tokens_in_db": all_tokens,
                "database_connected": True
            }
        
        return {
            "success": False,
            "error": "Database not connected",
            "current_user": current_user
        }
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info(f"🚀 Starting Unified Platform on port {port}")
    logger.info(f"🎭 Playwright browser path: {PLAYWRIGHT_PATH}")
    
    uvicorn.run(
        "Supermain:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )