



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
from datetime import time as time_type, timezone

from mainY import app
from YTscrapADS import get_product_scraper
from YTvideoGenerator import get_video_generator
# That's it! The automation task starts automatically from mainY.py
from YTdatabase import database_manager

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
        self.scrape_urls = None
        
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
            self.scrape_urls = self.db.scrape_urls
            
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


    # async def health_check(self) -> dict:
    #     """Check database health"""
    #     try:
    #         if not self.connected:
    #             return {
    #                 "status": "disconnected",
    #                 "error": "Database not connected"
    #             }
            
    #         await self.client.admin.command('ping')
    #         return {
    #             "status": "healthy",
    #             "database": "connected",
    #             "collections": {
    #                 "users": await self.users_collection.count_documents({}),
    #                 "youtube_credentials": await self.youtube_credentials.count_documents({}),
    #                 "reddit_tokens": await self.reddit_tokens.count_documents({})
    #             }
    #         }
    #     except Exception as e:
    #         return {
    #             "status": "unhealthy",
    #             "error": str(e)
    #         }

    # ============================================================================
    # PRODUCT URL QUEUE MANAGEMENT - ADD THESE NEW METHODS
    # ============================================================================







    async def save_scrape_url(self, user_id: str, url: str) -> bool:
        """Save website URL to scrape (replaces any existing URL)"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return False
            
            collection = self.db.scrape_urls
            await collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "url": url,
                        "created_at": datetime.now(),
                        "last_scraped": None,
                        "total_products_found": 0,
                        "products_processed": 0
                    }
                },
                upsert=True
            )
            logger.info(f"✅ Scrape URL saved for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Save scrape URL failed: {e}")
            return False

    async def get_scrape_url(self, user_id: str) -> dict:
        """Get saved scrape URL for user"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return None
            
            collection = self.db.scrape_urls
            url_doc = await collection.find_one({"user_id": user_id})
            return url_doc if url_doc else None
        except Exception as e:
            logger.error(f"❌ Get scrape URL failed: {e}")
            return None

    async def delete_scrape_url(self, user_id: str) -> bool:
        """Delete scrape URL"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return False
            
            collection = self.db.scrape_urls
            await collection.delete_one({"user_id": user_id})
            logger.info(f"✅ Scrape URL deleted for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Delete scrape URL failed: {e}")
            return False

    async def update_scrape_progress(self, user_id: str, total_found: int, processed: int) -> bool:
        """Update scraping progress"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return False
            
            collection = self.db.scrape_urls
            await collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "total_products_found": total_found,
                        "products_processed": processed,
                        "last_scraped": datetime.now()
                    }
                }
            )
            return True
        except Exception as e:
            logger.error(f"❌ Update scrape progress failed: {e}")
            return False

    async def get_next_unprocessed_product(self, user_id: str) -> dict:
        """Get next product that hasn't been processed yet"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return None
            
            collection = self.db.scrape_urls
            url_doc = await collection.find_one({"user_id": user_id})
            
            if not url_doc:
                return None
            
            if url_doc.get("products_processed", 0) >= url_doc.get("total_products_found", 0):
                await collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"products_processed": 0}}
                )
            
            return url_doc
            
        except Exception as e:
            logger.error(f"❌ Get next product failed: {e}")
            return None

    async def get_automation_posts_count(self, user_id: str, date) -> int:
        """Get number of automation posts for a specific date"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return 0
            
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            collection = self.db.automation_logs
            count = await collection.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day},
                "success": True
            })
            
            
            return count
        except Exception as e:
            logger.error(f"Get automation posts count failed: {e}")
            return 0
        












    async def get_all_automation_configs_by_type(self, config_type: str) -> list:
        """Get all active automation configs of a specific type"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return []
            
            cursor = self.automation_configs.find({
                "config_type": config_type,
                "enabled": True
            })
            
            configs = []
            async for doc in cursor:
                configs.append({
                    "user_id": doc["user_id"],
                    "config_data": doc["config_data"],
                    "enabled": doc.get("enabled", False)
                })
            
            return configs
            
        except Exception as e:
            logger.error(f"Get automation configs failed: {e}")
            return []

    async def disable_automation(self, user_id: str, config_type: str) -> bool:
        """Disable automation for a user"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return False
            
            result = await self.automation_configs.update_one(
                {"user_id": user_id, "config_type": config_type},
                {"$set": {"enabled": False, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Disable automation failed: {e}")
            return False
    
    async def log_automation_post(self, user_id: str, post_data: dict) -> bool:
        """Log automated post to database"""
        try:
            if not self.connected:
                logger.error("Database not connected")
                return False
            
            collection = self.db.automation_logs
            log_doc = {
                "user_id": user_id,
                "product_url": post_data.get("product_url"),
                "video_id": post_data.get("video_id"),
                "timestamp": post_data.get("timestamp", datetime.now()),
                "success": post_data.get("success", True),
                "error": post_data.get("error")
            }
            
            await collection.insert_one(log_doc)
            return True
        except Exception as e:
            logger.error(f"Log automation post failed: {e}")
            return False


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================       


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================
# GLOBAL INSTANCES
# ✅ WITH THIS:
database_manager = None
youtube_services = {}
reddit_services = {}
youtube_scheduler = None  # ← ADD THIS LINE
youtube_connector = None  # ← ADD THIS LINE
# ============================================================================


# ✅ CRITICAL FIX: Import YouTube database manager
from YTdatabase import get_database_manager as get_yt_db_manager# ============================================================================


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
# ============================================================================
# CRITICAL FIX: Around line 830-840 in your initialize_all_services() function
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
            
            # ✅ FIX: Check if attribute exists first
            if not hasattr(database_manager, 'reddit_tokens'):
                logger.error("❌ database_manager missing reddit_tokens collection")
                # Initialize it manually if needed
                database_manager.reddit_tokens = database_manager.db.reddit_tokens
            
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
                # youtube_connector,
                youtube_connector as yt_connector,
                # youtube_scheduler,
                youtube_scheduler as yt_scheduler,
                youtube_background_scheduler,
                ai_service as youtube_ai
            )
                        # ✅ Assign to global variables
            youtube_connector = yt_connector
            youtube_scheduler = yt_scheduler
            
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
            # Provide fallback class definitions to ensure type safety
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
# Global variable for background task
automation_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global automation_task
    
    # Startup
    success = await initialize_all_services()
    if not success:
        logger.error("⚠️ Service initialization incomplete - some features may not work")
    
    # ✅ START AUTOMATION BACKGROUND TASK
    logger.info("🤖 Starting product automation background task...")
    automation_task = asyncio.create_task(run_product_automation_tasks())
    logger.info("✅ Background automation task started")
    
    yield
    
    # Shutdown
    if automation_task:
        automation_task.cancel()
        try:
            await automation_task
        except asyncio.CancelledError:
            logger.info("Background task cancelled")
    
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

# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# import os

# FRONTEND_BUILD_PATH = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
# )

# # Serve React static files
# if os.path.exists(FRONTEND_BUILD_PATH):
#     app.mount(
#         "/",
#         StaticFiles(directory=FRONTEND_BUILD_PATH, html=True),
#         name="frontend"
#     )

# # React Router fallback
# @app.get("/{full_path:path}")
# async def react_fallback(full_path: str):
#     index_path = os.path.join(FRONTEND_BUILD_PATH, "index.html")
#     if os.path.exists(index_path):
#         return FileResponse(index_path)
#     return {"error": "React build not found"}



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
        disconnect_reddit_account,
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
    app.post("/api/reddit/disconnect")(disconnect_reddit_account)
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

# /////////////////////auto-post of 3 image --

# ============================================================================
# FIXED PRODUCT AUTOMATION ENDPOINTS - REPLACE YOUR EXISTING ONES
# ============================================================================

# @app.post("/api/product-automation/start")
# async def start_product_automation(request: Request, current_user: dict = Depends(get_current_user)):
#     """Start automated product scraping + video generation + upload"""
#     try:
#         body = await request.json()
        
#         # ✅ FIX: Use authenticated user's ID from JWT token
#         user_id = current_user.get("id") or current_user.get("user_id")
#         user_email = current_user.get("email", "Unknown")
        
#         if not user_id:
#             return JSONResponse(
#                 status_code=401,
#                 content={"success": False, "error": "Authentication required"}
#             )
        
#         config = body.get('config', {})
        
#         # Validate required fields
#         base_url = config.get('base_url', '')
#         search_query = config.get('search_query', '')
#         upload_times = config.get('upload_times', [])
        
#         if not base_url or not search_query:
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": "base_url and search_query required"}
#             )
        
#         if len(upload_times) == 0:
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": "At least one upload time required"}
#             )
        
#         # ✅ CRITICAL: Verify YouTube is connected for THIS authenticated user
#         youtube_creds = await database_manager.get_youtube_credentials(user_id)
        
#         if not youtube_creds:
#             logger.error(f"❌ No YouTube credentials found for user: {user_email} ({user_id})")
#             return JSONResponse(
#                 status_code=403,
#                 content={
#                     "success": False, 
#                     "error": "YouTube not connected. Please connect your YouTube account first.",
#                     "action_required": "connect_youtube",
#                     "user_info": {
#                         "email": user_email,
#                         "user_id": user_id
#                     }
#                 }
#             )
        
#         logger.info(f"✅ YouTube credentials verified for user: {user_email}")
        
#         # Store automation config with ENABLED = TRUE
#         success = await database_manager.store_automation_config(
#             user_id=user_id,  # ✅ Use authenticated user_id
#             config_type="product_automation",
#             config_data={
#                 "enabled": True,  # ✅ CRITICAL: Must be True
#                 "base_url": base_url,
#                 "search_query": search_query,
#                 "max_posts_per_day": config.get('max_posts_per_day', 200),
#                 "upload_times": upload_times,
#                 "auto_scrape": config.get('auto_scrape', True),
#                 "auto_generate_video": config.get('auto_generate_video', True),
#                 "auto_upload": config.get('auto_upload', True),
#                 "created_at": datetime.now().isoformat(),
#                 "updated_at": datetime.now().isoformat()
#             }
#         )
        
#         if not success:
#             return JSONResponse(
#                 status_code=500,
#                 content={"success": False, "error": "Failed to store config"}
#             )
        
#         logger.info(f"✅ Product automation STARTED for user: {user_email} ({user_id})")
#         logger.info(f"   Base URL: {base_url}")
#         logger.info(f"   Search: {search_query}")
#         logger.info(f"   Times: {upload_times}")
        
#         return JSONResponse(content={
#             "success": True,
#             "message": "Product automation started successfully! Videos will be uploaded to your connected YouTube channel.",
#             "config": {
#                 "base_url": base_url,
#                 "search_query": search_query,
#                 "upload_times": upload_times,
#                 "max_posts_per_day": config.get('max_posts_per_day', 200)
#             },
#             "next_run": upload_times[0] if upload_times else "Not set",
#             "user_info": {
#                 "email": user_email,
#                 "youtube_connected": True,
#                 "channel_name": youtube_creds.get('channel_info', {}).get('title', 'Your Channel')
#             }
#         })
        
#     except Exception as e:
#         logger.error(f"❌ Start automation failed: {e}")
#         import traceback
#         logger.error(traceback.format_exc())
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "error": str(e)}
#         )



@app.post("/api/product-automation/start")
async def start_product_automation(request: Request, current_user: dict = Depends(get_current_user)):
    """Start automated product scraping + video generation + upload"""
    try:
        body = await request.json()
        
        # ✅ Use authenticated user from JWT token
        user_id = current_user.get("id") or current_user.get("user_id")
        user_email = current_user.get("email", "Unknown")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        config = body.get('config', {})
        
        # Validate required fields
        base_url = config.get('base_url', '')
        search_query = config.get('search_query', '')
        upload_times = config.get('upload_times', [])
        
        if not base_url or not search_query:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "base_url and search_query required"}
            )
        
        if len(upload_times) == 0:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "At least one upload time required"}
            )
        
        logger.info(f"🔍 Starting automation for user {user_email} ({user_id})")
        
        # ✅ CRITICAL FIX: Use the GLOBAL database_manager that's already connected
        try:
            # Check if global database_manager is connected
            if not database_manager or not database_manager.connected:
                logger.error("Global database manager not connected")
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": "Database not connected. Please try again in a moment."
                    }
                )
            
            # ✅ Get credentials from the ALREADY CONNECTED youtube database
            # Access the youtube manager's collection directly
            if not hasattr(database_manager, 'youtube_credentials'):
                # Initialize if missing
                database_manager.youtube_credentials = database_manager.db.youtube_credentials
            
            youtube_creds = await database_manager.youtube_credentials.find_one({
                "user_id": user_id
            })
            
            if not youtube_creds:
                logger.error(f"❌ No YouTube credentials found for user: {user_email} ({user_id})")
                
                # Debug: Show what's in the database
                try:
                    all_creds_cursor = database_manager.youtube_credentials.find({})
                    all_users = []
                    async for cred in all_creds_cursor:
                        all_users.append({
                            "user_id": cred.get("user_id"),
                            "channel": cred.get("channel_info", {}).get("title", "Unknown")
                        })
                    logger.error(f"Available credentials: {all_users}")
                except Exception as debug_err:
                    logger.error(f"Debug query failed: {debug_err}")
                
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "error": "YouTube not connected. Please connect your YouTube account first.",
                        "action_required": "connect_youtube",
                        "user_info": {
                            "email": user_email,
                            "user_id": user_id
                        }
                    }
                )
            
            logger.info(f"✅ YouTube credentials verified for user: {user_email}")
            logger.info(f"   Channel: {youtube_creds.get('channel_info', {}).get('title', 'Unknown')}")
            
        except Exception as cred_check_error:
            logger.error(f"Credential check failed: {cred_check_error}")
            import traceback
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Failed to verify YouTube connection: {str(cred_check_error)}"
                }
            )
        
        # Store automation config with ENABLED = TRUE
        success = await database_manager.store_automation_config(
            user_id=user_id,
            config_type="product_automation",
            config_data={
                "enabled": True,
                "base_url": base_url,
                "search_query": search_query,
                "max_posts_per_day": config.get('max_posts_per_day', 100),
                "upload_times": upload_times,
                "auto_scrape": config.get('auto_scrape', True),
                "auto_generate_video": config.get('auto_generate_video', True),
                "auto_upload": config.get('auto_upload', True),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        )
        
        if not success:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to store config"}
            )
        
        logger.info(f"✅ Product automation STARTED for user: {user_email} ({user_id})")
        logger.info(f"   Base URL: {base_url}")
        logger.info(f"   Search: {search_query}")
        logger.info(f"   Times: {upload_times}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Product automation started successfully! Videos will be uploaded to your connected YouTube channel.",
            "config": {
                "base_url": base_url,
                "search_query": search_query,
                "upload_times": upload_times,
                "max_posts_per_day": config.get('max_posts_per_day', 100)
            },
            "next_run": upload_times[0] if upload_times else "Not set",
            "user_info": {
                "email": user_email,
                "youtube_connected": True,
                "channel_name": youtube_creds.get('channel_info', {}).get('title', 'Your Channel')
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Start automation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )



@app.post("/api/product-automation/stop")
async def stop_product_automation(request: Request, current_user: dict = Depends(get_current_user)):
    """Stop automated product scraping"""
    try:
        # ✅ Use authenticated user from JWT token
        user_id = current_user.get("id") or current_user.get("user_id")
        user_email = current_user.get("email", "Unknown")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        # Disable automation by setting enabled = False
        success = await database_manager.disable_automation(user_id, "product_automation")
        
        if not success:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to disable automation"}
            )
        
        logger.info(f"⏹️ Product automation STOPPED for user: {user_email} ({user_id})")
        
        return JSONResponse(content={
            "success": True,
            "message": "Product automation stopped successfully",
            "user_info": {
                "email": user_email,
                "user_id": user_id
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Stop automation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )



# Background task runner (runs every hour)
# ============================================================================
# FIXED BACKGROUND TASK - REPLACE run_product_automation_tasks()
# ============================================================================





async def run_product_automation_tasks():
    """Background task with detailed logging"""
    logger.info("=" * 70)
    logger.info("🚀 PRODUCT AUTOMATION BACKGROUND TASK STARTED")
    logger.info("=" * 70)
    
    while True:
        try:
            # current_time = datetime.now().strftime('%H:%M')
            IST = timezone(timedelta(hours=5, minutes=30))
            current_time = datetime.now(IST).strftime('%H:%M')
            logger.info(f"🕐 Current IST time: {current_time}")
            current_minute = datetime.now().minute
            
            # Log every 5 minutes
            if current_minute % 5 == 0:
                logger.info(f"🤖 Automation check at {current_time}")
            
            if not database_manager or not database_manager.connected:
                if current_minute % 5 == 0:
                    logger.warning("⚠️ Database not connected")
                await asyncio.sleep(60)
                continue
            
            # Get all configs
            configs = await database_manager.get_all_automation_configs_by_type("product_automation")
            
            if current_minute % 5 == 0:
                logger.info(f"📋 Found {len(configs)} total automation configs")
            
            active_count = 0
            for config in configs:
                try:
                    user_id = config.get("user_id")
                    config_data = config.get("config_data", {})
                    enabled = config_data.get("enabled", False)
                    
                    # Log config details every 5 minutes
                    if current_minute % 5 == 0:
                        logger.info(f"   User {user_id[:8]}... | enabled={enabled}")
                        logger.info(f"      base_url: {config_data.get('base_url', 'NOT SET')}")
                        logger.info(f"      search_query: {config_data.get('search_query', 'NOT SET')}")
                        logger.info(f"      upload_times: {config_data.get('upload_times', [])}")
                    
                    if not enabled:
                        if current_minute % 5 == 0:
                            logger.warning(f"      ❌ SKIPPED: Disabled")
                        continue
                    
                    active_count += 1
                    
                    upload_times = config_data.get("upload_times", [])
                    base_url = config_data.get("base_url", "")
                    search_query = config_data.get("search_query", "")
                    
                    if current_minute % 5 == 0:
                        logger.info(f"      ✅ ACTIVE automation")
                    
                    # Check time match
                    if current_time in upload_times:
                        logger.info("=" * 70)
                        logger.info(f"🔔 TIME MATCH! TRIGGERING AUTOMATION")
                        logger.info(f"   User: {user_id}")
                        logger.info(f"   Current: {current_time}")
                        logger.info(f"   Scheduled: {upload_times}")
                        logger.info(f"   URL: {base_url}")
                        logger.info(f"   Search: {search_query}")
                        logger.info("=" * 70)
                        
                        # Check daily limit
                        posts_today = await database_manager.get_automation_posts_count(
                            user_id,
                            date=datetime.now().date()
                        )
                        
                        max_posts = config_data.get("max_posts_per_day", 200)
                        
                        logger.info(f"   Posts today: {posts_today}/{max_posts}")
                        
                        if posts_today >= max_posts:
                            logger.warning(f"   ❌ Daily limit reached")
                            continue
                        
                        logger.info(f"   ✅ EXECUTING AUTOMATION NOW!")
                        
                        # Execute (non-blocking)
                        asyncio.create_task(execute_product_automation(user_id, config_data))
                    else:
                        # Log mismatch every 5 min
                        if current_minute % 5 == 0:
                            logger.info(f"      ⏰ No match: {current_time} vs {upload_times}")
                    
                except Exception as e:
                    logger.error(f"❌ Config error: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue
            
            if current_minute % 5 == 0:
                logger.info(f"📊 Summary: {active_count} active / {len(configs)} total")
                logger.info("-" * 70)
            
            # Wait 60 seconds
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"❌ Task error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await asyncio.sleep(60)

# ============================================================================
# BACKGROUND AUTOMATION TASK - REPLACE execute_product_automation
# ============================================================================



async def log_step(step: str, success: bool, details: str = "", error: str = ""):
    """Log automation step to database"""
    try:
        await database_manager.db.automation_logs.insert_one({
            "user_id": user_id,
            "timestamp": datetime.now(),
            "step": step,
            "success": success,
            "details": details,
            "error": error,
            "product_url": "",
            "video_id": ""
        })
    except Exception as e:
        logger.error(f"Failed to log step: {e}")


      




# ============================================================================
# FIXED: execute_product_automation function in Supermain.py
# PASTE THIS TO REPLACE THE EXISTING execute_product_automation FUNCTION
# ============================================================================
# async def execute_product_automation(user_id: str, config: dict):
#     """
#     Execute automation with detailed logging and proper YouTube credential handling
#     COMPLETE FIXED VERSION - Ready to replace in Supermain.py
#     """
    
#     # ✅ CRITICAL: Declare global variables at the very top
#     global youtube_scheduler
    
#     # Helper function to log each step
#     async def log_step(step: str, success: bool, details: str = "", error: str = ""):
#         """Log automation step to database"""
#         try:
#             await database_manager.db.automation_logs.insert_one({
#                 "user_id": user_id,
#                 "timestamp": datetime.now(),
#                 "step": step,
#                 "success": success,
#                 "details": details,
#                 "error": error,
#                 "product_url": "",
#                 "video_id": ""
#             })
#         except Exception as e:
#             logger.error(f"Failed to log step: {e}")
    
#     try:
#         logger.info("=" * 70)
#         logger.info(f"🔄 EXECUTING AUTOMATION FOR USER: {user_id}")
#         logger.info("=" * 70)
        
#         # Get config
#         base_url = config.get("base_url", "https://www.flipkart.com")
#         search_query = config.get("search_query", "")
        
#         if not base_url or not search_query:
#             error_msg = "Missing base_url or search_query in config"
#             logger.error(f"❌ {error_msg}")
#             await log_step("validation", False, error=error_msg)
#             return
        
#         logger.info(f"🔍 Search Config:")
#         logger.info(f"   URL: {base_url}")
#         logger.info(f"   Query: {search_query}")
        
#         await log_step("start", True, f"Starting automation for: {search_query}")
        
#         # STEP 1: Scrape search results
#         logger.info(f"📍 STEP 1: Scraping search results page...")
        
#         from YTscrapADS import get_product_scraper
#         scraper = get_product_scraper()
        
#         product_links = await scraper.scrape_category_page(
#             base_url,
#             max_products=50,
#             search_query=search_query
#         )
        
#         if not product_links or len(product_links) == 0:
#             error_msg = f"No products found for: {search_query}"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("scrape_search", False, error=error_msg)
#             return
        
#         logger.info(f"   ✅ Found {len(product_links)} products")
#         await log_step("scrape_search", True, f"Found {len(product_links)} products")
        
#         # STEP 2: Get next product to process
#         logger.info(f"📍 STEP 2: Selecting next product...")
        
#         url_doc = await database_manager.scrape_urls.find_one({"user_id": user_id})
        
#         if not url_doc:
#             await database_manager.scrape_urls.insert_one({
#                 "user_id": user_id,
#                 "url": base_url,
#                 "search_query": search_query,
#                 "total_products_found": len(product_links),
#                 "products_processed": 0,
#                 "created_at": datetime.now()
#             })
#             processed_count = 0
#         else:
#             processed_count = url_doc.get('products_processed', 0)
            
#             if processed_count >= len(product_links):
#                 processed_count = 0
#                 await database_manager.scrape_urls.update_one(
#                     {"user_id": user_id},
#                     {"$set": {"products_processed": 0}}
#                 )
        
#         next_product = product_links[processed_count]
#         product_url = next_product.get('url')
        
#         logger.info(f"   ✅ Selected product {processed_count + 1}/{len(product_links)}")
#         logger.info(f"   URL: {product_url}")
#         await log_step("select_product", True, f"Product {processed_count + 1}/{len(product_links)}")
        
#         # STEP 3: Scrape product details
#         logger.info(f"📍 STEP 3: Scraping product details...")
        
#         product_data = await scraper.scrape_product(product_url)
        
#         if not product_data.get("success"):
#             error_msg = f"Scraping failed: {product_data.get('error', 'Unknown error')}"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("scrape_product", False, error=error_msg)
#             return
        
#         product_name = product_data.get('product_name', 'Product')
#         brand = product_data.get('brand', 'Brand')
#         price = product_data.get('price', 0)
        
#         logger.info(f"   ✅ Product: {brand} - {product_name}")
#         logger.info(f"   Price: Rs.{price}")
#         await log_step("scrape_product", True, f"{brand} - {product_name} (Rs.{price})")
        
#         # STEP 4: Download images and convert to base64
#         logger.info(f"📍 STEP 4: Downloading product images...")
        
#         images = product_data.get("images", [])[:6]
        
#         if len(images) < 3:
#             error_msg = "No images found"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("download_images", False, error=error_msg)
#             return
        
#         logger.info(f"   Found {len(images)} images")
        
#         # Convert to base64
#         base64_images = []
#         async with httpx.AsyncClient(timeout=30) as client:
#             for i, img_url in enumerate(images):
#                 try:
#                     logger.info(f"   Downloading image {i+1}/{len(images)}...")
#                     response = await client.get(img_url)
#                     if response.status_code == 200:
#                         img_base64 = base64.b64encode(response.content).decode()
#                         base64_images.append(f"data:image/jpeg;base64,{img_base64}")
#                         logger.info(f"      ✅ Image {i+1} downloaded")
#                 except Exception as e:
#                     logger.warning(f"      ⚠️ Image {i+1} failed: {e}")
#                     continue
        
#         if not base64_images:
#             error_msg = "Failed to download images"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("download_images", False, error=error_msg)
#             return
        
#         logger.info(f"   ✅ Downloaded {len(base64_images)} images")
#         await log_step("download_images", True, f"{len(base64_images)} images downloaded")
        
#         # STEP 5: Generate video slideshow
#         logger.info(f"📍 STEP 5: Generating video slideshow...")

#         from slideshow_generator import get_slideshow_generator
        
#         slideshow_gen = get_slideshow_generator()
        
#         video_result = await slideshow_gen.generate_slideshow(
#             images=base64_images,
#             title=product_name,
#             language='english',
#             duration_per_image=2.0,
#             transition='fade',
#             add_text=True,
#             aspect_ratio="9:16",
#             product_data=product_data,
#             add_music=True,
#             music_style='upbeat'
#         )
        
#         if not video_result.get("success"):
#             error_msg = f"Video generation failed: {video_result.get('error', 'Unknown')}"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("generate_video", False, error=error_msg)
#             return
        
#         video_path = video_result.get('local_path')
#         logger.info(f"   ✅ Video generated: {video_path}")
#         await log_step("generate_video", True, f"Video: {video_path}")
        
#         # STEP 6: Get YouTube credentials
#         logger.info(f"📍 STEP 6: Getting YouTube credentials...")
        
#         credentials = await database_manager.get_youtube_credentials(user_id)
        
#         if not credentials:
#             error_msg = "No YouTube credentials found"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("upload_youtube", False, error=error_msg)
#             return
        
#         logger.info(f"   ✅ YouTube credentials found")
        
#         # STEP 7: Upload to YouTube
#         logger.info(f"📍 STEP 7: Uploading to YouTube...")
        
#         # ✅ CRITICAL CHECK: Verify youtube_scheduler is available
#         if youtube_scheduler is None:
#             error_msg = "youtube_scheduler not initialized"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("upload_youtube", False, error=error_msg)
            
#             # ✅ Try to recover by re-importing
#             try:
#                 logger.info("   ⚠️ Attempting to re-import youtube_scheduler...")
#                 from mainY import youtube_scheduler as yt_scheduler
#                 youtube_scheduler = yt_scheduler
#                 logger.info("   ✅ Successfully re-imported youtube_scheduler")
#             except Exception as import_err:
#                 logger.error(f"   ❌ Re-import failed: {import_err}")
#                 return
        
#         # Import helper functions from mainY.py
#         from mainY import generate_professional_youtube_description, shorten_url_async
        
#         # Generate title
#         title = f"{brand} - {product_name[:30]}"
        
#         # Shorten URL
#         short_url = await shorten_url_async(product_url)
        
#         # Generate professional description with affiliate link
#         description = generate_professional_youtube_description(product_data, short_url)
        
#         logger.info(f"   Title: {title}")
#         logger.info(f"   Short URL: {short_url}")
#         logger.info(f"   Uploading to YouTube...")
        
#         # ✅ UPLOAD TO YOUTUBE
#         upload_result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             credentials_data=credentials,
#             content_type="shorts",
#             title=title,
#             description=description,
#             video_url=video_path  # Local video file path
#         )
        
#         if upload_result.get("success"):
#             video_id = upload_result.get("video_id")
#             logger.info(f"   ✅ Uploaded! Video ID: {video_id}")
#             logger.info(f"   URL: https://youtube.com/shorts/{video_id}")
            
#             await log_step("upload_youtube", True, f"Video ID: {video_id}")
            
#             # Final success log
#             await database_manager.log_automation_post(user_id, {
#                 "product_url": product_url,
#                 "video_id": video_id,
#                 "timestamp": datetime.now(),
#                 "success": True
#             })
            
#             # Update processed count
#             await database_manager.scrape_urls.update_one(
#                 {"user_id": user_id},
#                 {"$set": {"products_processed": processed_count + 1}}
#             )
            
#             logger.info("=" * 70)
#             logger.info("✅ AUTOMATION COMPLETED SUCCESSFULLY!")
#             logger.info("=" * 70)
            
#         else:
#             error_msg = f"Upload failed: {upload_result.get('error', 'Unknown')}"
#             logger.error(f"   ❌ {error_msg}")
#             await log_step("upload_youtube", False, error=error_msg)
        
#     except Exception as e:
#         logger.error(f"❌ AUTOMATION FAILED: {e}")
#         import traceback
#         logger.error(traceback.format_exc())
#         await log_step("fatal_error", False, error=str(e))




async def execute_product_automation(user_id: str, config: dict):
    """
    ✅ FIXED: Execute automation with direct database access for credentials
    """
    
    # ✅ CRITICAL: Declare global variables at the very top
    global youtube_scheduler
    
    # Helper function to log each step
    async def log_step(step: str, success: bool, details: str = "", error: str = ""):
        """Log automation step to database"""
        try:
            await database_manager.db.automation_logs.insert_one({
                "user_id": user_id,
                "timestamp": datetime.now(),
                "step": step,
                "success": success,
                "details": details,
                "error": error,
                "product_url": "",
                "video_id": ""
            })
        except Exception as e:
            logger.error(f"Failed to log step: {e}")
    
    try:
        logger.info("=" * 70)
        logger.info(f"🔄 EXECUTING AUTOMATION FOR USER: {user_id}")
        logger.info("=" * 70)
        
        # ✅ CRITICAL FIX: Validate user_id is not None/empty
        if not user_id or user_id == "undefined" or user_id == "null":
            error_msg = f"Invalid user_id: {user_id}"
            logger.error(f"❌ {error_msg}")
            await log_step("validation", False, error=error_msg)
            return
        
        # ============================================================
        # ✅ STEP 0: VERIFY YOUTUBE CREDENTIALS FIRST (USE GLOBAL DATABASE)
        # ============================================================
        logger.info(f"📍 STEP 0: Verifying YouTube connection for user: {user_id}")
        
        try:
            # ✅ CRITICAL FIX: Use the GLOBAL database_manager that's already connected
            if not database_manager or not getattr(database_manager, "connected", False):
                error_msg = "Database not connected"
                logger.error(f"   ❌ {error_msg}")
                await log_step("youtube_check", False, error=error_msg)
                return
            
            # ✅ Ensure youtube_credentials collection exists
            if not hasattr(database_manager, "youtube_credentials"):
                database_manager.youtube_credentials = database_manager.db.youtube_credentials
            
            # ✅ Fetch credentials
            credentials_raw = await database_manager.youtube_credentials.find_one({
                "user_id": user_id
            })
            
            if not credentials_raw:
                error_msg = f"❌ No YouTube credentials found for user_id: {user_id}"
                logger.error(error_msg)
                logger.error("   💡 User must connect YouTube account first!")
                await log_step("youtube_check", False, error=error_msg)
                return
            
            credentials = {
                "access_token": credentials_raw.get("access_token"),
                "refresh_token": credentials_raw.get("refresh_token"),
                "token_uri": credentials_raw.get("token_uri"),
                "client_id": credentials_raw.get("client_id"),
                "client_secret": credentials_raw.get("client_secret"),
                "scopes": credentials_raw.get("scopes"),
                "expires_at": credentials_raw.get("expires_at"),
                "channel_info": credentials_raw.get("channel_info", {})
            }
            
            if not credentials.get("access_token"):
                error_msg = "YouTube credentials missing access_token"
                logger.error(f"   ❌ {error_msg}")
                await log_step("youtube_check", False, error=error_msg)
                return
            
            channel_name = credentials.get("channel_info", {}).get("title", "Unknown")
            logger.info("   ✅ YouTube credentials verified!")
            logger.info(f"   ✅ Channel: {channel_name}")
            await log_step("youtube_check", True, f"Channel: {channel_name}")
        
        except Exception as cred_error:
            error_msg = f"Failed to retrieve credentials: {cred_error}"
            logger.error(f"   ❌ {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            await log_step("youtube_check", False, error=error_msg)
            return
        
        # ============================================================
        # STEP 1: Verify user exists
        # ============================================================
        try:
            user_data = await database_manager.get_user_by_id(user_id)
            if not user_data:
                error_msg = f"User not found in database: {user_id}"
                logger.error(f"❌ {error_msg}")
                await log_step("validation", False, error=error_msg)
                return
            
            user_email = user_data.get("email", "Unknown")
            logger.info(f"✅ User verified: {user_email} (ID: {user_id})")
            
        except Exception as user_error:
            error_msg = f"Failed to verify user: {user_error}"
            logger.error(f"❌ {error_msg}")
            await log_step("validation", False, error=error_msg)
            return
        
        # ============================================================
        # STEP 2: Validate config
        # ============================================================
        base_url = config.get("base_url", "https://www.flipkart.com")
        search_query = config.get("search_query", "")
        
        if not base_url or not search_query:
            error_msg = "Missing base_url or search_query in config"
            logger.error(f"❌ {error_msg}")
            await log_step("validation", False, error=error_msg)
            return
        
        logger.info("🔍 Search Config:")
        logger.info(f"   URL: {base_url}")
        logger.info(f"   Query: {search_query}")
        logger.info(f"   User: {user_email}")
        logger.info(f"   Channel: {channel_name}")
        
        await log_step("start", True, f"Starting automation for: {search_query}")
        
        # ============================================================
        # STEP 3: Scrape search results
        # ============================================================
        from YTscrapADS import get_product_scraper
        scraper = get_product_scraper()
        
        product_links = await scraper.scrape_category_page(
            base_url,
            max_products=50,
            search_query=search_query
        )
        
        if not product_links:
            error_msg = f"No products found for: {search_query}"
            logger.error(f"❌ {error_msg}")
            await log_step("scrape_search", False, error=error_msg)
            return
        
        await log_step("scrape_search", True, f"Found {len(product_links)} products")
        
        # ============================================================
        # STEP 4: Select product
        # ============================================================
        url_doc = await database_manager.scrape_urls.find_one({"user_id": user_id})
        
        if not url_doc:
            await database_manager.scrape_urls.insert_one({
                "user_id": user_id,
                "url": base_url,
                "search_query": search_query,
                "total_products_found": len(product_links),
                "products_processed": 0,
                "created_at": datetime.now()
            })
            processed_count = 0
        else:
            processed_count = url_doc.get("products_processed", 0)
            if processed_count >= len(product_links):
                processed_count = 0
                await database_manager.scrape_urls.update_one(
                    {"user_id": user_id},
                    {"$set": {"products_processed": 0}}
                )
        
        next_product = product_links[processed_count]
        product_url = next_product.get("url")
        
        await log_step("select_product", True, f"Product {processed_count + 1}")
        
        # ============================================================
        # STEP 5: Scrape product
        # ============================================================
        product_data = await scraper.scrape_product(product_url)
        
        if not product_data.get("success"):
            error_msg = product_data.get("error", "Scrape failed")
            await log_step("scrape_product", False, error=error_msg)
            return
        
        product_name = product_data.get("product_name", "Product")
        brand = product_data.get("brand", "Brand")
        
        await log_step("scrape_product", True, product_name)
        
        # ============================================================
        # STEP 6: Download images
        # ============================================================
        images = product_data.get("images", [])[:6]
        if len(images) < 3:
            await log_step("download_images", False, error="Not enough images")
            return
        
        base64_images = []
        async with httpx.AsyncClient(timeout=30) as client:
            for img in images:
                r = await client.get(img)
                if r.status_code == 200:
                    base64_images.append(
                        f"data:image/jpeg;base64,{base64.b64encode(r.content).decode()}"
                    )
        
        await log_step("download_images", True, f"{len(base64_images)} images")
        
        # ============================================================
        # STEP 7: Generate video
        # ============================================================
        from slideshow_generator import get_slideshow_generator
        slideshow_gen = get_slideshow_generator()
        
        video_result = await slideshow_gen.generate_slideshow(
            images=base64_images,
            title=product_name,
            language="english",
            duration_per_image=2.0,
            transition="fade",
            add_text=True,
            aspect_ratio="9:16",
            product_data=product_data,
            add_music=True,
            music_style="upbeat"
        )
        
        if not video_result.get("success"):
            await log_step("generate_video", False, error=video_result.get("error"))
            return
        
        video_path = video_result["local_path"]
        await log_step("generate_video", True, video_path)
        
        # ============================================================
        # STEP 8: Upload to YouTube
        # ============================================================
        from mainY import generate_professional_youtube_description, shorten_url_async
        
        title = f"{brand} - {product_name[:30]}"
        short_url = await shorten_url_async(product_url)
        description = generate_professional_youtube_description(product_data, short_url)
        
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=description,
            video_url=video_path
        )
        
        if upload_result.get("success"):
            video_id = upload_result["video_id"]
            await log_step("upload_youtube", True, video_id)
            
            await database_manager.scrape_urls.update_one(
                {"user_id": user_id},
                {"$set": {"products_processed": processed_count + 1}}
            )
        else:
            await log_step("upload_youtube", False, error=upload_result.get("error"))
    
    except Exception as e:
        logger.error(f"❌ AUTOMATION FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await log_step("fatal_error", False, error=str(e))





# ============================================================================
# ALSO ADD THIS HELPER FUNCTION IF NOT PRESENT
# ============================================================================

async def shorten_url_async(long_url: str) -> str:
    """Shorten URL using TinyURL (async version)"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"http://tinyurl.com/api-create.php?url={long_url}"
            )
            if response.status_code == 200:
                return response.text.strip()
    except Exception as e:
        logger.warning(f"URL shortening failed: {e}")
    return long_url





async def get_next_product_url(user_id: str) -> str:
    """Get next product URL from user's queue"""
    try:
        # This should fetch from a user's URL queue in database
        # For now, return None (you need to implement URL queue management)
        return None
    except:
        return None

# Start automation background task

# @app.on_event("startup")
# async def start_automation_background():
#     """Start automation checker on app startup"""
#     asyncio.create_task(run_product_automation_tasks())
#     logger.info("✅ Product automation background task started")

    
# ============================================================================
# ✅ IMPROVED CATCH-ALL ROUTE - PASTE THIS (REPLACE OLD VERSION)
# ============================================================================
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Configuration - ✅ FIXED PATH
REACT_BUILD_DIR = Path("SOCIAL/frontend/build")  # ✅ Changed this line
REACT_INDEX = REACT_BUILD_DIR / "index.html"

# Try to mount static files
try:
    if REACT_BUILD_DIR.exists() and REACT_INDEX.exists():
        # Mount static assets (JS, CSS, images)
        static_assets = REACT_BUILD_DIR / "static"
        if static_assets.exists():
            app.mount("/static", StaticFiles(directory=str(static_assets)), name="static")
            logger.info(f"✅ Serving React static files from {REACT_BUILD_DIR}")
        
        # Catch-all route - MUST be defined LAST
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            """
            Serve React app for all non-API routes.
            This fixes the refresh issue by always serving index.html.
            """
            # Don't interfere with API routes
            if full_path.startswith("api/"):
                logger.warning(f"❌ API route not found: /{full_path}")
                raise HTTPException(status_code=404, detail=f"API endpoint not found: /{full_path}")
            
            # Health/debug routes should still work
            if full_path in ["health", "debug", "keep-alive"]:
                raise HTTPException(status_code=404, detail="Route not found")
            
            # Serve index.html for all other routes (React Router handles the rest)
            logger.info(f"📄 Serving index.html for route: /{full_path}")
            return FileResponse(REACT_INDEX)
            
        logger.info(f"✅ SPA routing enabled - React app will handle all non-API routes")
    else:
        # Build folder doesn't exist - show helpful error page
        logger.error(f"❌ React build directory not found at {REACT_BUILD_DIR}")
        logger.error(f"❌ Expected index.html at: {REACT_INDEX}")
        logger.error("❌ SPA routing will NOT work!")
        
        @app.get("/{full_path:path}")
        async def build_not_found(full_path: str):
            """Show error when build folder is missing"""
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail=f"API endpoint not found: /{full_path}")
            
            # Show helpful error page
            return HTMLResponse(
                content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Build Not Found</title>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            background: white;
                            border-radius: 20px;
                            padding: 48px;
                            max-width: 600px;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        }}
                        h1 {{ color: #dc2626; margin: 0 0 16px 0; }}
                        p {{ color: #666; line-height: 1.6; margin: 12px 0; }}
                        code {{
                            background: #f3f4f6;
                            padding: 2px 8px;
                            border-radius: 4px;
                            font-family: 'Courier New', monospace;
                            color: #dc2626;
                        }}
                        .solution {{
                            background: #fef3c7;
                            border-left: 4px solid #f59e0b;
                            padding: 16px;
                            margin: 20px 0;
                            border-radius: 4px;
                        }}
                        .command {{
                            background: #1f2937;
                            color: #10b981;
                            padding: 16px;
                            border-radius: 8px;
                            margin: 12px 0;
                            font-family: 'Courier New', monospace;
                            overflow-x: auto;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>⚠️ React Build Not Found</h1>
                        <p>The React app hasn't been built yet. The server is looking for:</p>
                        <code>{REACT_BUILD_DIR.absolute()}/index.html</code>
                        
                        <div class="solution">
                            <strong>🔧 Solution:</strong>
                            <p>You need to build your React app and configure Render to include the build folder.</p>
                        </div>
                        
                        <p><strong>Option 1: Local Build (Testing)</strong></p>
                        <div class="command">
                            cd frontend<br>
                            npm install<br>
                            npm run build<br>
                            cd ..<br>
                            mv frontend/build ./build
                        </div>
                        
                        <p><strong>Option 2: Configure Render Build Command</strong></p>
                        <div class="command">
                            pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && mv frontend/build ./build
                        </div>
                        
                        <p style="margin-top: 24px; padding-top: 24px; border-top: 2px solid #e5e7eb;">
                            <strong>Current route:</strong> <code>/{full_path}</code><br>
                            <strong>API endpoints still work:</strong> <a href="/health">/health</a>, <a href="/api/debug/services">/api/debug/services</a>
                        </p>
                    </div>
                </body>
                </html>
                """,
                status_code=503
            )
        
        logger.warning("⚠️ Registered fallback error page for missing build folder")
        
except Exception as e:
    logger.error(f"❌ Failed to setup React serving: {e}")
    import traceback
    logger.error(traceback.format_exc())




# ============================================================================
# PRODUCT AUTOMATION ROUTES
# ============================================================================
# ============================================================================
# PASTE THIS IN YOUR Supermain.py - REPLACE THE EXISTING AUTOMATION ROUTES
# ============================================================================
@app.get("/api/debug/automation-credentials/{user_id}")
async def debug_automation_credentials(user_id: str):
    """Debug automation credentials for a user"""
    try:
        if not database_manager or not database_manager.connected:
            return {
                "success": False,
                "error": "Database not connected"
            }
        
        # Get user info
        user = await database_manager.get_user_by_id(user_id)
        
        # Get YouTube credentials
        youtube_creds = await database_manager.get_youtube_credentials(user_id)
        
        # Get automation config
        automation_config = await database_manager.get_automation_config(user_id, "product_automation")
        
        # Get ALL YouTube credentials in DB
        all_youtube_creds = []
        cursor = database_manager.youtube_credentials.find({})
        async for cred in cursor:
            all_youtube_creds.append({
                "user_id": cred.get("user_id"),
                "channel": cred.get("channel_info", {}).get("title", "Unknown"),
                "has_access_token": bool(cred.get("access_token")),
                "created_at": cred.get("created_at", "Unknown")
            })
        
        return {
            "success": True,
            "query_user_id": user_id,
            "user_exists": user is not None,
            "user_email": user.get("email") if user else None,
            "youtube_credentials_found": youtube_creds is not None,
            "youtube_channel": youtube_creds.get("channel_info", {}).get("title") if youtube_creds else None,
            "automation_config_exists": automation_config is not None,
            "automation_enabled": automation_config.get("config_data", {}).get("enabled") if automation_config else False,
            "all_youtube_credentials_in_db": all_youtube_creds,
            "total_youtube_accounts": len(all_youtube_creds)
        }
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
# ============================================================================
# FIXED PRODUCT AUTOMATION ROUTES - PASTE THIS IN Supermain.py
# ============================================================================

@app.post("/api/automation/save-url")
async def save_scrape_url_route(request: Request, current_user: dict = Depends(get_current_user)):
    """Save URL and intelligently detect if it's a category or product page"""
    try:
        body = await request.json()
        
        # ✅ Use authenticated user from JWT token
        user_id = current_user.get("id") or current_user.get("user_id")
        user_email = current_user.get("email", "Unknown")
        url = body.get('url')
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        if not url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "URL required"}
            )
        
        if not url.startswith('http'):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid URL format. Must start with http:// or https://"}
            )
        
        logger.info(f"🔍 Analyzing URL for user {user_email} ({user_id}): {url}")
        
        # ✅ SMART URL DETECTION
        scraper = get_product_scraper()
        url_lower = url.lower()
        
        # Detect if it's a single product or category page
        is_product_page = (
            '/p/' in url_lower or 
            '/product/' in url_lower or 
            '/dp/' in url_lower or  # Amazon
            '/buy/' in url_lower or  # Myntra
            '-p-' in url_lower
        )
        
        if is_product_page:
            # ✅ SINGLE PRODUCT PAGE
            logger.info(f"📦 Detected PRODUCT page, scraping single product...")
            
            product_data = await scraper.scrape_product(url)
            
            if not product_data.get('success'):
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": f"Failed to scrape product: {product_data.get('error', 'Unknown error')}"
                    }
                )
            
            # Save as single-product automation
            success = await database_manager.save_scrape_url(user_id, url)
            
            if not success:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Failed to save URL to database"}
                )
            
            # Set total to 1 (this is a single product that will repeat)
            await database_manager.update_scrape_progress(
                user_id, 
                total_found=1, 
                processed=0
            )
            
            logger.info(f"✅ Single product saved for user {user_email}")
            
            return JSONResponse(content={
                "success": True,
                "type": "single_product",
                "message": "Product saved! This product will be used for automated videos.",
                "data": {
                    "total_products": 1,
                    "url": url,
                    "product_name": product_data.get('product_name', 'Product'),
                    "brand": product_data.get('brand', 'Brand'),
                    "price": product_data.get('price', 0),
                    "images": len(product_data.get('images', [])),
                    "sample_product": {
                        "title": product_data.get('product_name'),
                        "image": product_data.get('images', [None])[0],
                        "url": url
                    }
                },
                "user_info": {
                    "email": user_email,
                    "user_id": user_id
                }
            })
        
        else:
            # ✅ CATEGORY/LISTING PAGE
            logger.info(f"📋 Detected CATEGORY page, scraping product links...")
            
            product_links = await scraper.scrape_category_page(url, max_products=200)
            
            if not product_links:
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False, 
                        "error": "No products found at this URL. Please check the URL and try again."
                    }
                )
            
            # Save URL to database
            success = await database_manager.save_scrape_url(user_id, url)
            
            if not success:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Failed to save URL to database"}
                )
            
            # Update progress
            await database_manager.update_scrape_progress(
                user_id, 
                total_found=len(product_links), 
                processed=0
            )
            
            logger.info(f"✅ Found {len(product_links)} products for user {user_email}")
            
            return JSONResponse(content={
                "success": True,
                "type": "category",
                "message": f"Successfully found {len(product_links)} products!",
                "data": {
                    "total_products": len(product_links),
                    "url": url,
                    "sample_products": product_links[:5]  # Show first 5 as preview
                },
                "user_info": {
                    "email": user_email,
                    "user_id": user_id
                }
            })
        
    except Exception as e:
        logger.error(f"❌ Save URL failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/api/automation/generate-video-now")
async def generate_video_now(request: Request):
    """Generate video for next product in queue"""
    try:
        body = await request.json()
        user_id = body.get('user_id')
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id required"}
            )
        
        logger.info(f"🎬 Generating video for user {user_id}")
        
        # Get saved URL
        url_doc = await database_manager.get_scrape_url(user_id)
        
        if not url_doc:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "No automation URL found. Please save a URL first."}
            )
        
        base_url = url_doc.get('url')
        total_products = url_doc.get('total_products_found', 0)
        processed = url_doc.get('products_processed', 0)
        
        if total_products == 0:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "No products available"}
            )
        
        scraper = get_product_scraper()
        
        # Check if it's a single product or category
        if total_products == 1:
            # ✅ SINGLE PRODUCT - always scrape the same URL
            logger.info(f"📦 Scraping single product: {base_url}")
            product_data = await scraper.scrape_product(base_url)
            
        else:
            # ✅ CATEGORY - scrape category page and get next product
            logger.info(f"📋 Scraping category for next product...")
            product_links = await scraper.scrape_category_page(base_url, max_products=200)
            
            if not product_links or processed >= len(product_links):
                # Reset to first product if we've gone through all
                processed = 0
                await database_manager.update_scrape_progress(user_id, total_products, 0)
            
            # Get next product URL
            next_product_url = product_links[processed]['url']
            logger.info(f"📦 Scraping product {processed + 1}/{len(product_links)}: {next_product_url}")
            
            product_data = await scraper.scrape_product(next_product_url)
        
        if not product_data.get('success'):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Failed to scrape product: {product_data.get('error', 'Unknown error')}"
                }
            )
        
        # Get images
        images = product_data.get('images', [])[:3]  # Take 3 images
        
        if len(images) < 3:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No images found for this product"}
            )
        
        logger.info(f"🖼️ Found {len(images)} images, converting to base64...")
        
        # Convert URLs to base64
        base64_images = []
        async with httpx.AsyncClient(timeout=30) as client:
            for img_url in images:
                try:
                    response = await client.get(img_url)
                    if response.status_code == 200:
                        img_base64 = base64.b64encode(response.content).decode()
                        base64_images.append(f"data:image/jpeg;base64,{img_base64}")
                except Exception as img_error:
                    logger.warning(f"Failed to fetch image: {img_error}")
                    continue
        
        if not base64_images:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Failed to download product images"}
            )
        
        logger.info(f"✅ Converted {len(base64_images)} images to base64")
        
        # Generate slideshow video
        logger.info(f"🎥 Generating slideshow video...")
        video_gen = get_video_generator()
        
        video_result = await video_gen.generate_slideshow(
            images=base64_images,
            title=product_data.get('product_name', 'Product'),
            language='english',
            duration_per_image=2.0,
            transition='fade',
            add_text=True,
            aspect_ratio="9:16"  # YouTube Shorts
        )
        
        if not video_result.get('success'):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Video generation failed: {video_result.get('error', 'Unknown error')}"
                }
            )
        
        logger.info(f"✅ Video generated successfully!")
        
        # Update processed count
        await database_manager.update_scrape_progress(
            user_id,
            total_products,
            processed + 1
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Video generated successfully!",
            "data": {
                "video_path": video_result.get('local_path'),
                "product_name": product_data.get('product_name'),
                "brand": product_data.get('brand'),
                "price": product_data.get('price'),
                "images_used": len(base64_images),
                "progress": {
                    "current": processed + 1,
                    "total": total_products
                }
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Generate video failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/api/automation/upload-video-now")
async def upload_video_now(request: Request):
    """Generate video + upload to YouTube in one step"""
    try:
        body = await request.json()
        user_id = body.get('user_id')
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id required"}
            )
        
        logger.info(f"🚀 Full automation for user {user_id}: scrape → video → upload")
        
        # Step 1: Check YouTube credentials
        youtube_creds = await database_manager.get_youtube_credentials(user_id)
        
        if not youtube_creds:
            return JSONResponse(
                status_code=403,
                content={"success": False, "error": "YouTube not connected. Please connect your YouTube account first."}
            )
        
        # Step 2: Generate video (reuse the generate_video_now logic)
        from fastapi import Request as FastAPIRequest
        
        # Create a mock request with user_id
        mock_request_data = {"user_id": user_id}
        
        # Call generate_video_now endpoint
        video_response = await generate_video_now(
            Request(scope={"type": "http", "method": "POST"}, receive=None)
        )
        
        # Parse the response
        import json
        video_result = json.loads(video_response.body.decode())
        
        if not video_result.get('success'):
            return JSONResponse(
                status_code=400,
                content=video_result
            )
        
        video_data = video_result.get('data', {})
        video_path = video_data.get('video_path')
        product_name = video_data.get('product_name', 'Product')
        brand = video_data.get('brand', 'Brand')
        price = video_data.get('price', 0)
        
        # Step 3: Upload to YouTube
        logger.info(f"📤 Uploading to YouTube...")
        
        # Get YouTube services
        from mainY import youtube_scheduler
        
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=youtube_creds,
            content_type="shorts",
            title=f"{brand} - {product_name}",
            description=f"Check out this amazing product!\n\n{brand} - {product_name}\nPrice: ₹{price}\n\n#shorts #product #shopping",
            video_url=video_path,
            tags=["shorts", "product", brand.lower(), "shopping"]
        )
        
        if not upload_result.get('success'):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Upload failed: {upload_result.get('error', 'Unknown error')}"
                }
            )
        
        # Log to database
        await database_manager.log_automation_post(user_id, {
            "product_name": product_name,
            "video_id": upload_result.get('video_id'),
            "timestamp": datetime.now(),
            "success": True
        })
        
        logger.info(f"✅ Full automation complete! Video ID: {upload_result.get('video_id')}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Video uploaded to YouTube successfully!",
            "data": {
                "video_id": upload_result.get('video_id'),
                "video_url": f"https://youtube.com/shorts/{upload_result.get('video_id')}",
                "product_name": product_name,
                "brand": brand,
                "price": price
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Upload video failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# @app.delete("/api/automation/delete-url/{user_id}")
# async def delete_scrape_url_route(user_id: str):
#     """Stop automation and delete saved URL"""
#     try:
#         success = await database_manager.delete_scrape_url(user_id)
        
#         if success:
#             logger.info(f"✅ Automation stopped for user {user_id}")
        
#         return JSONResponse(content={
#             "success": success,
#             "message": "Automation stopped successfully" if success else "Failed to stop automation"
#         })
        
#     except Exception as e:
#         logger.error(f"❌ Delete URL failed: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "error": str(e)}
#         )


@app.post("/api/automation/scrape-single-product")
async def scrape_single_product_route(request: Request):
    """Scrape detailed info for a single product"""
    try:
        body = await request.json()
        product_url = body.get('product_url')
        
        if not product_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "product_url required"}
            )
        
        logger.info(f"🔍 Scraping single product: {product_url}")
        
        scraper = get_product_scraper()
        product_data = await scraper.scrape_product(product_url)
        
        if not product_data.get('success'):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False, 
                    "error": product_data.get('error', 'Failed to scrape product')
                }
            )
        
        logger.info(f"✅ Product scraped: {product_data.get('product_name')}")
        
        return JSONResponse(content={
            "success": True,
            "product": product_data
        })
        
    except Exception as e:
        logger.error(f"❌ Single product scrape failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# ============================================================================
# PRODUCT AUTOMATION ENDPOINTS - PASTE BEFORE get_automation_status
# ============================================================================
@app.get("/api/automation/config/{user_id}")
async def get_automation_config_endpoint(user_id: str):
    """Get saved automation configuration"""
    try:
        if not database_manager or not database_manager.connected:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Database not connected"}
            )
        
        config = await database_manager.get_automation_config(user_id, "product_automation")
        
        if config:
            config_data = config.get("config_data", {})
            return JSONResponse(content={
                "success": True,
                "config": {
                    "enabled": config_data.get("enabled", False),
                    "base_url": config_data.get("base_url", ""),
                    "search_query": config_data.get("search_query", ""),
                    "upload_times": config_data.get("upload_times", []),
                    "max_posts_per_day": config_data.get("max_posts_per_day", 200)
                }
            })
        
        return JSONResponse(content={
            "success": False,
            "error": "No config found"
        })
        
    except Exception as e:
        logger.error(f"Get config failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# @app.post("/api/automation/save-url")
# async def save_scrape_url_route(request: Request):
#     """Save URL for scraping (category or product page)"""
#     try:
#         body = await request.json()
#         user_id = body.get('user_id')
#         url = body.get('url')
        
#         if not user_id or not url:
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": "user_id and url required"}
#             )
        
#         if not url.startswith('http'):
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": "Invalid URL format"}
#             )
        
#         logger.info(f"🔍 Saving URL for user {user_id}: {url}")
        
#         # Save URL to database
#         success = await database_manager.save_scrape_url(user_id, url)
        
#         if not success:
#             return JSONResponse(
#                 status_code=500,
#                 content={"success": False, "error": "Failed to save URL"}
#             )
        
#         # Get product scraper
#         scraper = get_product_scraper()
        
#         # Check if it's a product or category page
#         url_lower = url.lower()
#         is_product_page = (
#             '/p/' in url_lower or 
#             '/product/' in url_lower or 
#             '/dp/' in url_lower or
#             '/buy/' in url_lower or
#             '-p-' in url_lower
#         )
        
#         if is_product_page:
#             # Single product page
#             product_data = await scraper.scrape_product(url)
            
#             if not product_data.get('success'):
#                 return JSONResponse(
#                     status_code=400,
#                     content={
#                         "success": False,
#                         "error": f"Failed to scrape product: {product_data.get('error')}"
#                     }
#                 )
            
#             # Set as 1 product (will repeat)
#             await database_manager.update_scrape_progress(user_id, 1, 0)
            
#             return JSONResponse(content={
#                 "success": True,
#                 "type": "single_product",
#                 "message": "Product saved for automation!",
#                 "data": {
#                     "total_products": 1,
#                     "url": url,
#                     "product_name": product_data.get('product_name'),
#                     "price": product_data.get('price'),
#                     "images": len(product_data.get('images', []))
#                 }
#             })
        
#         else:
#             # Category page - scrape product links
#             product_links = await scraper.scrape_category_page(url, max_products=100)
            
#             if not product_links:
#                 return JSONResponse(
#                     status_code=404,
#                     content={
#                         "success": False,
#                         "error": "No products found at this URL"
#                     }
#                 )
            
#             await database_manager.update_scrape_progress(
#                 user_id, 
#                 len(product_links), 
#                 0
#             )
            
#             return JSONResponse(content={
#                 "success": True,
#                 "type": "category",
#                 "message": f"Found {len(product_links)} products!",
#                 "data": {
#                     "total_products": len(product_links),
#                     "url": url,
#                     "sample_products": product_links[:5]
#                 }
#             })
        
#     except Exception as e:
#         logger.error(f"❌ Save URL failed: {e}")
#         import traceback
#         logger.error(traceback.format_exc())
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "error": str(e)}
#         )


@app.delete("/api/automation/delete-url/{user_id}")
async def delete_scrape_url_route(user_id: str):
    """Stop automation and delete saved URL"""
    try:
        success = await database_manager.delete_scrape_url(user_id)
        
        return JSONResponse(content={
            "success": success,
            "message": "Automation stopped" if success else "Failed to stop"
        })
        
    except Exception as e:
        logger.error(f"❌ Delete URL failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# ✅ ADD THIS ENDPOINT BEFORE @app.get("/api/automation/status/{user_id}")
@app.get("/api/automation/logs/{user_id}")
async def get_automation_logs(user_id: str, limit: int = 20):
    """Get automation activity logs"""
    try:
        if not database_manager or not database_manager.connected:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Database not connected"}
            )
        
        logs = []
        cursor = database_manager.db.automation_logs.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        async for log in cursor:
            logs.append({
                "timestamp": log.get("timestamp").isoformat() if log.get("timestamp") else "",
                "step": log.get("step", ""),
                "success": log.get("success", False),
                "details": log.get("details", ""),
                "error": log.get("error", ""),
                "product_url": log.get("product_url", ""),
                "video_id": log.get("video_id", "")
            })
        
        return JSONResponse(content={
            "success": True,
            "logs": logs
        })
        
    except Exception as e:
        logger.error(f"Get logs failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.get("/api/automation/status/{user_id}")
async def get_automation_status_endpoint(user_id: str):
    """Get automation status and today's post count"""
    try:
        if not database_manager or not database_manager.connected:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Database not connected"}
            )
        
        # Get config
        config = await database_manager.get_automation_config(user_id, "product_automation")
        
        # Get today's posts count
        from datetime import datetime
        today_posts = await database_manager.get_automation_posts_count(
            user_id,
            date=datetime.now().date()
        )
        
        if not config:
            return JSONResponse(content={
                "success": True,
                "active": False,
                "posts_today": today_posts,
                "config": None
            })
        
        config_data = config.get("config_data", {})
        enabled = config_data.get("enabled", False)
        
        return JSONResponse(content={
            "success": True,
            "active": enabled,
            "posts_today": today_posts,
            "config": {
                "base_url": config_data.get("base_url", ""),
                "search_query": config_data.get("search_query", ""),
                "upload_times": config_data.get("upload_times", []),
                "max_posts_per_day": config_data.get("max_posts_per_day", 200),
                "daily_limit": config_data.get("max_posts_per_day", 200),
                "remaining_today": max(0, config_data.get("max_posts_per_day", 200) - today_posts)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get automation status failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/automation/test-scraper")
async def test_scraper_route(request: Request):
    """Test scraper with a URL to see if it works"""
    try:
        body = await request.json()
        url = body.get('url')
        scrape_type = body.get('type', 'category')  # 'category' or 'product'
        
        if not url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "url required"}
            )
        
        logger.info(f"🧪 Testing scraper - Type: {scrape_type}, URL: {url}")
        
        scraper = get_product_scraper()
        
        if scrape_type == 'category':
            # Test category page scraping
            products = await scraper.scrape_category_page(url, max_products=5)
            
            return JSONResponse(content={
                "success": len(products) > 0,
                "type": "category",
                "products_found": len(products),
                "sample_products": products[:3],
                "message": f"Found {len(products)} products" if products else "No products found"
            })
        else:
            # Test single product scraping
            product_data = await scraper.scrape_product(url)
            
            return JSONResponse(content={
                "success": product_data.get('success', False),
                "type": "product",
                "product": product_data,
                "message": "Product scraped successfully" if product_data.get('success') else "Scraping failed"
            })
        
    except Exception as e:
        logger.error(f"❌ Test scraper failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
    

# ============================================================================
# AI VIRAL TITLE & DESCRIPTION GENERATOR FOR YOUTUBE
# ============================================================================
# ============================================================================
# AI VIRAL TITLE GENERATOR FOR YOUTUBE SHORTS (SHORT TITLES = MORE VIEWS)
# ============================================================================
@app.post("/api/youtube/generate-viral-titles")
async def generate_viral_titles(request: Request):
    """Generate 5 SHORT viral YouTube title options (2-5 words max) with scores"""
    try:
        data = await request.json()
        topic = data.get("topic", "")
        niche = data.get("niche", "shorts")
        
        if not topic or len(topic.split()) < 2:
            return {
                "success": False,
                "error": "Please provide at least 2-3 words about your video"
            }
        
        logger.info(f"🎯 Generating SHORT viral titles for: {topic}")
        
        # Get AI service keys
        mistral_key = os.getenv("MISTRAL_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        if not mistral_key and not groq_key:
            return {
                "success": False,
                "error": "AI API keys not configured"
            }
        
        # Build prompt for SHORT titles
        prompt = f"""Generate 5 SHORT viral YouTube Shorts titles for: "{topic}"

CRITICAL RULES:
1. MAXIMUM 5 WORDS per title (2-5 words only!)
2. MINIMUM 2 WORDS per title
3. Use 1 emoji max (at end)
4. Create curiosity gap
5. Use power words: Wait, POV, Rare, Never, Secret, Watch

SHORT TITLE EXAMPLES (these get 1000+ views):
- "Rare vulture 🦅"
- "Wait for it 😱"
- "This went wrong 💀"
- "POV: You discover 🤯"
- "Never do this ⚠️"

BAD (too long):
- "Everyone Does Chill Life, WRONG... Try THIS Instead" ❌
- "POV: You Never Leave Eat Sleep Office 🏢 #Corporate" ❌

Output format (PURE JSON, no markdown):
{{
  "titles": [
    {{
      "title": "Rare {topic.split()[0]} 🦅",
      "word_count": 2,
      "score": 9.5,
      "reason": "Short + curiosity + emoji"
    }},
    {{
      "title": "Wait for it 😱",
      "word_count": 3,
      "score": 9.2,
      "reason": "Universal hook + suspense"
    }},
    {{
      "title": "This is insane 🤯",
      "word_count": 3,
      "score": 9.0,
      "reason": "Emotion + shock value"
    }},
    {{
      "title": "POV: {topic.split()[0]} life 🎯",
      "word_count": 3,
      "score": 8.8,
      "reason": "Trending format + relatable"
    }},
    {{
      "title": "Never ignore this ⚠️",
      "word_count": 3,
      "score": 8.5,
      "reason": "Warning + urgency"
    }}
  ],
  "analysis": {{
    "best_length": "2-5 words",
    "reason": "Short titles get 10x more views on Shorts - proven by your 'Rare vulture' getting 1,858 views"
  }},
  "description": "Engaging description with emojis and CTAs",
  "tags": ["viral", "shorts", "{topic.split()[0].lower()}"]
}}

Topic: {topic}
Target: Indian audience on YouTube Shorts

REMEMBER: MAX 5 WORDS PER TITLE! Generate NOW in PURE JSON:"""
        
        # Try Mistral first
        ai_response = None
        service_used = None
        
        if mistral_key:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {mistral_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {
                                    "role": "system", 
                                    "content": "You are a viral YouTube Shorts expert. Generate ONLY SHORT titles (2-5 words max). Output ONLY valid JSON without markdown."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1500
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        service_used = "mistral"
                        logger.info("✅ Mistral API success")
                    elif response.status_code == 429:
                        logger.warning("⚠️ Mistral rate limit, trying Groq...")
                    else:
                        logger.error(f"Mistral error: {response.status_code}")
            except Exception as e:
                logger.error(f"Mistral error: {e}")
        
        # Fallback to Groq
        if not ai_response and groq_key:
            try:
                await asyncio.sleep(1)
                
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {groq_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "messages": [
                                {
                                    "role": "system", 
                                    "content": "You are a viral YouTube Shorts expert. Generate ONLY SHORT titles (2-5 words max). Output ONLY valid JSON."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1500
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        service_used = "groq"
                        logger.info("✅ Groq API success")
                    else:
                        logger.error(f"Groq error: {response.status_code}")
            except Exception as e:
                logger.error(f"Groq error: {e}")
        
        if not ai_response:
            logger.warning("⚠️ Both AI services failed, using fallback")
            service_used = "fallback"
        
        # Parse JSON response
        import json
        import re
        
        if ai_response:
            # Clean response
            ai_response_clean = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
            
            try:
                parsed = json.loads(ai_response_clean)
                titles = parsed.get("titles", [])
                
                # FILTER: Remove titles longer than 5 words
                filtered_titles = []
                for t in titles:
                    title_text = t.get("title", "")
                    # Count words (exclude emojis)
                    word_count = len(re.sub(r'[^\w\s]', '', title_text).split())
                    
                    if 2 <= word_count <= 5:
                        t["word_count"] = word_count
                        filtered_titles.append(t)
                
                # If we have enough filtered titles
                if len(filtered_titles) >= 3:
                    logger.info(f"✅ Generated {len(filtered_titles)} SHORT titles using {service_used}")
                    
                    return {
                        "success": True,
                        "titles": filtered_titles[:5],  # Max 5
                        "analysis": parsed.get("analysis", {
                            "best_length": "2-5 words",
                            "reason": "Short titles proven to get 10x more views"
                        }),
                        "description": parsed.get("description", ""),
                        "tags": parsed.get("tags", []),
                        "service": service_used,
                        "message": f"{len(filtered_titles[:5])} SHORT viral titles generated!"
                    }
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"JSON parse error: {e}")
        
        # FALLBACK: Short template-based titles
        logger.info("📝 Using SHORT fallback templates")
        
        topic_words = topic.split()
        first_word = topic_words[0].title()
        
        return {
            "success": True,
            "titles": [
                {
                    "title": f"Rare {first_word} 🦅",
                    "word_count": 2,
                    "score": 9.5,
                    "reason": "Proven winner - mirrors your 1.8k view video"
                },
                {
                    "title": "Wait for it 😱",
                    "word_count": 3,
                    "score": 9.3,
                    "reason": "Universal suspense hook"
                },
                {
                    "title": f"POV: {first_word} life 🎯",
                    "word_count": 3,
                    "score": 9.0,
                    "reason": "Trending POV format"
                },
                {
                    "title": "This is insane 🤯",
                    "word_count": 3,
                    "score": 8.8,
                    "reason": "Shock value + emotion"
                },
                {
                    "title": f"Never ignore {first_word} ⚠️",
                    "word_count": 3,
                    "score": 8.5,
                    "reason": "Warning + urgency"
                }
            ],
            "analysis": {
                "best_length": "2-5 words",
                "reason": "Your 'Rare vulture #Shorts' (3 words) got 1,858 views while longer titles got <150 views. SHORT = VIRAL for Shorts.",
                "proof": "Rare vulture = 1,858 views vs long titles = 42-137 views"
            },
            "description": f"🔥 Check this out!\n\n👇 LIKE if you enjoyed\n🔔 SUBSCRIBE for more\n💬 Comment below\n\n#{topic.replace(' ', '')} #viral #shorts #trending",
            "tags": ["viral", "shorts", "trending", first_word.lower(), "youtube"],
            "service": "fallback",
            "message": "5 SHORT viral titles generated (proven strategy)"
        }
        
    except Exception as e:
        logger.error(f"❌ Generate viral titles error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# SMART COMMENT AUTO-REPLY WITH WEB SEARCH & CONTEXT AWARENESS
# ============================================================================
# ============================================================================
# ENHANCED SMART COMMENT AUTO-REPLY WITH WEB SEARCH & NATURAL RESPONSES
# ============================================================================
@app.post("/api/youtube/smart-auto-reply")
async def smart_auto_reply(request: Request):
    """Generate highly human-like, context-aware replies with web search"""
    try:
        data = await request.json()
        
        comment_text = data.get("comment_text", "")
        video_title = data.get("video_title", "")
        video_description = data.get("video_description", "")
        channel_name = data.get("channel_name", "")
        
        if not comment_text:
            return {"success": False, "error": "Comment text required"}
        
        logger.info(f"💬 Smart reply for: '{comment_text[:60]}...'")
        
        # Advanced intent detection with tone analysis
        comment_lower = comment_text.lower()
        
        # Detect tone (casual/formal/excited/questioning)
        is_casual = any(x in comment_lower for x in ['bro', 'dude', 'yaar', 'bhai', 'mate'])
        is_excited = '!' in comment_text or any(x in comment_lower for x in ['wow', 'amazing', 'awesome', 'omg'])
        is_question = '?' in comment_text
        
        # Detect language hints
        has_hindi = any(word in comment_text for word in ['hai', 'kya', 'kahan', 'kaise', 'bhai', 'yaar'])
        
        # Enhanced intent detection
        if any(word in comment_lower for word in ['where', 'location', 'place', 'kaha', 'kahaan', 'कहां', 'address', 'exact location']):
            intent = "location"
        elif any(word in comment_lower for word in ['distance', 'far', 'kitna dur', 'कितना दूर', 'how to reach', 'route', 'travel time', 'train', 'bus', 'flight']):
            intent = "distance"
        elif any(word in comment_lower for word in ['music', 'song', 'track', 'background music', 'bgm', 'गाना', 'soundtrack', 'tune']):
            intent = "music"
        elif any(word in comment_lower for word in ['price', 'cost', 'kitna', 'कितना', 'expensive', 'cheap', 'budget', 'paisa', 'rupees']):
            intent = "price"
        elif any(word in comment_lower for word in ['camera', 'shot', 'edit', 'filming', 'gear', 'equipment']):
            intent = "production"
        elif any(word in comment_lower for word in ['nice', 'good', 'amazing', 'beautiful', 'awesome', 'great', 'love', 'best', 'superb', 'fantastic']):
            intent = "compliment"
        elif any(word in comment_lower for word in ['bad', 'worst', 'disappointed', 'fake', 'boring', 'waste', 'clickbait']):
            intent = "negative"
        elif any(word in comment_lower for word in ['how', 'why', 'when', 'what', 'kaise', 'kyun', 'kab']):
            intent = "question"
        else:
            intent = "general"
        
        logger.info(f"🔍 Intent: {intent} | Tone: {'casual' if is_casual else 'formal'} | Excited: {is_excited}")
        
        # Web search for factual queries
        search_context = ""
        if intent in ["location", "distance", "price"]:
            try:
                # Extract key entities for search
                search_query = f"{video_title} {comment_text[:50]}"
                
                logger.info(f"🌐 Searching web for context: {search_query}")
                
                async with httpx.AsyncClient(timeout=15) as client:
                    # Use a search API (you can use SerpAPI, Google Custom Search, etc.)
                    # For this example, I'll show the structure
                    search_response = await client.get(
                        f"https://api.search-engine.com/search",  # Replace with actual API
                        params={"q": search_query, "limit": 3}
                    )
                    
                    if search_response.status_code == 200:
                        results = search_response.json()
                        search_context = f"\n\nWeb search results: {results.get('snippet', '')}"
                        logger.info("✅ Web search context added")
            except Exception as e:
                logger.warning(f"Web search failed: {e}")
        
        # Get AI service keys
        mistral_key = os.getenv("MISTRAL_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")
        
        # Build enhanced, human-like prompts
        system_prompt = """You are a real Indian YouTuber responding to comments. Rules:
1. Match the commenter's tone EXACTLY (casual/formal/excited)
2. Use Hinglish if they use Hindi words
3. Be brief - max 2 short sentences (like real YouTube replies)
4. Use emojis naturally (1-2 max, not every sentence)
5. Never be robotic or template-like
6. Add personality - use "bro", "yaar" if they do
7. Don't always end with subscribe requests - vary responses
8. Sound like you're typing quickly, not writing an essay"""

        if intent == "location":
            prompt = f"""Comment: "{comment_text}"
Video: "{video_title}"
{search_context}

Reply naturally about the location. If you know it from the video title, mention it. If not, say you'll pin the location in comments or description.

Match their tone: {'casual/friendly' if is_casual else 'helpful'}.
Reply as if you're quickly typing on your phone:"""
        
        elif intent == "distance":
            import re
            cities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', comment_text)
            
            if len(cities) >= 2:
                prompt = f"""Comment: "{comment_text}"
They're asking about distance from {cities[0]} to {cities[1]}.

Give a quick, helpful reply with:
- Approximate distance (use real-world knowledge)
- Travel time estimate
- Best transport mode

Be conversational like: "Around 530km bro, takes 12-13 hours by road. Totally worth it! 🚗"

Match their tone: {'casual' if is_casual else 'helpful'}.
Quick reply:"""
            else:
                prompt = f"""Comment: "{comment_text}"

They're asking about distance/travel. Reply naturally suggesting Google Maps or saying you'll share route details.

Keep it brief and friendly:"""
        
        elif intent == "music":
            prompt = f"""Comment: "{comment_text}"

They want to know the music. Reply like:
- "Track name is [song if you know] 🎵"
- Or "I'll drop the link in description"
- Or "It's from YouTube Audio Library"

Be quick and casual:"""
        
        elif intent == "price":
            prompt = f"""Comment: "{comment_text}"
Video: "{video_title}"
{search_context}

Give realistic price estimate if you can tell from video title. Otherwise say approximate range or "check description for details".

Match their vibe: {'casual' if is_casual else 'helpful'}.
Quick reply:"""
        
        elif intent == "production":
            prompt = f"""Comment: "{comment_text}"

They're asking about camera/editing. Reply naturally:
- Mention gear if asked
- Or "Shot on [phone/camera]"
- Keep it real and brief

{'Casual tone' if is_casual else 'Helpful tone'}:"""
        
        elif intent == "compliment":
            gratitude_variations = [
                "Thanks so much! 🙏",
                "Really appreciate it! ❤️",
                "Thank you bro! 😊",
                "Means a lot! 🙏",
                "Glad you liked it! ✨"
            ]
            
            prompt = f"""Comment: "{comment_text}"

Reply warmly. Variations:
- Just thank them
- Ask what they liked most
- Mention next video topic

Use one of: {', '.join(gratitude_variations[:3])}

{'Be casual and friendly' if is_casual else 'Be warm and genuine'}.
Keep it SHORT (1-2 sentences):"""
        
        elif intent == "negative":
            prompt = f"""Comment: "{comment_text}"

Handle criticism gracefully:
- Thank them for feedback
- Stay positive, don't be defensive
- Maybe ask what they'd like to see

Professional but human:"""
        
        elif intent == "question":
            prompt = f"""Comment: "{comment_text}"
Video: "{video_title}"

Answer their question directly if you can tell from video context. If not, say you'll reply with details or make a video on it.

Be helpful and conversational:"""
        
        else:
            prompt = f"""Comment: "{comment_text}"
Video: "{video_title}"

Reply naturally to engage them. Could be:
- Answer their point
- Ask them something back
- Share a quick thought

Match their energy. Be BRIEF:"""
        
        # Call AI with improved parameters
        ai_reply = None
        service_used = None
        
        if mistral_key:
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    response = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {mistral_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.85,  # Higher for more natural variation
                            "max_tokens": 100,  # Shorter for brevity
                            "top_p": 0.9
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_reply = result["choices"][0]["message"]["content"].strip()
                        # Clean up any quotes or formatting
                        ai_reply = ai_reply.strip('"\'')
                        service_used = "mistral"
                        logger.info("✅ Mistral reply generated")
            except Exception as e:
                logger.error(f"Mistral error: {e}")
        
        # Fallback to Groq
        if not ai_reply and groq_key:
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {groq_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.85,
                            "max_tokens": 100,
                            "top_p": 0.9
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_reply = result["choices"][0]["message"]["content"].strip()
                        ai_reply = ai_reply.strip('"\'')
                        service_used = "groq"
                        logger.info("✅ Groq reply generated")
            except Exception as e:
                logger.error(f"Groq error: {e}")
        
        # Enhanced fallback replies (more human)
        if not ai_reply:
            logger.info("📝 Using enhanced fallback")
            service_used = "fallback"
            
            # Multiple variations for each intent
            import random
            
            fallback_replies = {
                "location": [
                    f"It's mentioned in the video title! 📍 DM if you need exact location",
                    "Check description for location details! 🗺️",
                    f"Near {video_title.split()[0] if video_title else 'here'}! Let me know if you need directions"
                ],
                "distance": [
                    "Check Google Maps for exact distance bro! 🚗 It's a great trip though",
                    "Takes about a day by road. Totally worth it! ✨",
                    "Not too far! Best to check Maps for current route 🗺️"
                ],
                "music": [
                    "I'll add the track name in description! 🎵",
                    "It's from YouTube Audio Library. Lemme find the exact name",
                    "Will pin the music details! 🎶 Stay tuned"
                ],
                "price": [
                    "Check description for price details! 💰",
                    "Quite affordable honestly! Details in description 👇",
                    "Budget-friendly! Around 2-3k range"
                ],
                "compliment": [
                    "Thank you so much! 🙏 Really appreciate it",
                    "Means a lot! ❤️ Which part did you like most?",
                    "Thanks bro! 😊 More content coming soon"
                ],
                "negative": [
                    "Thanks for the feedback! 🙏 What would you improve?",
                    "Appreciate your honesty! Will work on it",
                    "Sorry it didn't meet expectations. What should I change?"
                ],
                "question": [
                    "Good question! Let me make a video on this",
                    "I'll explain this in detail soon! Stay subscribed 🔔",
                    "Great point! Will cover this in next video"
                ],
                "general": [
                    "Thanks for watching! 😊",
                    "Appreciate the support! 🙏",
                    "Glad you're here! More content coming soon ✨"
                ]
            }
            
            ai_reply = random.choice(fallback_replies.get(intent, fallback_replies["general"]))
        
        # Post-processing: ensure brevity
        sentences = ai_reply.split('.')
        if len(sentences) > 3:
            ai_reply = '. '.join(sentences[:2]) + '.'
        
        logger.info(f"✅ Generated {intent} reply via {service_used}")
        
        return {
            "success": True,
            "reply": ai_reply,
            "intent": intent,
            "tone": "casual" if is_casual else "formal",
            "service": service_used,
            "has_search_context": bool(search_context)
        }
        
    except Exception as e:
        logger.error(f"❌ Smart reply error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Even error fallback should be natural
        casual_fallbacks = [
            "Thanks for your comment! 😊",
            "Appreciate the support! 🙏",
            "Thanks for watching! ❤️"
        ]
        import random
        
        return {
            "success": False,
            "error": str(e),
            "reply": random.choice(casual_fallbacks)
        }

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