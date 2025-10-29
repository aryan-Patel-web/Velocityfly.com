"""
Supermain.py - COMPLETE PRODUCTION VERSION
✅ All database fixes included
✅ Consistent Playwright path: /opt/render/project/.playwright
✅ YouTube (mainY.py) + Reddit (main.py) integration
✅ All routes, functions, and features working
✅ Error-free for Render deployment
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

# ============================================================================
# ✅ CRITICAL: SET PLAYWRIGHT PATH BEFORE ANY IMPORTS (matches mainY.py)
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
# UNIFIED DATABASE MANAGER - COMPLETE WITH ALL FIXES
# ============================================================================
class UnifiedDatabaseManager:
    """
    Single database manager for YouTube + Reddit + All platforms
    ✅ All fixes included: get_user_by_token, connected tracking, etc.
    """
    
    def __init__(self, mongodb_uri: str):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.db = None
        self.connected = False  # ✅ Track connection status
        
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
            
            self.connected = True  # ✅ Mark as connected
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
    
    # ✅ CRITICAL: get_user_by_token method (was missing - caused "Database not initialized" error)
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
    
    # ========== REDDIT TOKENS ==========
    async def store_reddit_tokens(self, user_id: str, token_data: dict) -> dict:
        """Store Reddit OAuth tokens"""
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
                    "expires_at": datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
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
            
            logger.info(f"Reddit tokens stored for user {user_id}")
            return {"success": True, "message": "Reddit tokens stored"}
        except Exception as e:
            logger.error(f"Store Reddit tokens failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_reddit_tokens(self, user_id: str) -> Optional[dict]:
        """Get Reddit tokens"""
        try:
            if not self.connected:
                return None
            
            result = await self.reddit_tokens.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if result and result.get("expires_at") > datetime.now():
                return {
                    "access_token": result["access_token"],
                    "refresh_token": result.get("refresh_token", ""),
                    "reddit_username": result["reddit_username"],
                    "is_valid": True
                }
            return None
        except Exception as e:
            logger.error(f"Get Reddit tokens failed: {e}")
            return None
    
    async def check_reddit_connection(self, user_id: str) -> dict:
        """Check Reddit connection status"""
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
                "_id": state,  # Use state as ID for fast lookup
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
# AUTHENTICATION DEPENDENCY - FIXED
# ============================================================================
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token - FIXED"""
    try:
        token = credentials.credentials
        
        # ✅ CHECK IF DATABASE EXISTS AND IS CONNECTED
        if not database_manager:
            logger.error("Database manager not initialized")
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        if not database_manager.connected:
            logger.error("Database not connected")
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # ✅ USE UNIFIED DATABASE METHOD
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
# SERVICE INITIALIZATION - FIXED
# ============================================================================
async def initialize_all_services():
    """Initialize YouTube and Reddit services - FIXED"""
    global database_manager, youtube_services, reddit_services
    
    logger.info("="*60)
    logger.info("🚀 STARTING UNIFIED AUTOMATION PLATFORM")
    logger.info("="*60)
    
    # ✅ CRITICAL: Initialize database FIRST
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
        
        # ✅ Import main.py module
        import main as reddit_main
        
        # ✅ CRITICAL: Patch main.py's database_manager BEFORE importing functions
        reddit_main.database_manager = database_manager
        logger.info("✅ Patched main.py database_manager")
        
        # Import Reddit classes
        from main import (
            RedditOAuthConnector,
            AIService,
            RedditAutomationScheduler
        )
        
        # Initialize Reddit OAuth
        reddit_config = {
            'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
            'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET'),
            'REDDIT_REDIRECT_URI': os.getenv('REDDIT_REDIRECT_URI', 'https://velocitypost-984x.onrender.com/api/oauth/reddit/callback'),
            'REDDIT_USER_AGENT': os.getenv('REDDIT_USER_AGENT', 'VelocityPost/1.0')
        }
        
        if reddit_config['REDDIT_CLIENT_ID'] and reddit_config['REDDIT_CLIENT_SECRET']:
            reddit_oauth = RedditOAuthConnector(reddit_config)
            
            # Initialize Reddit AI (can share with YouTube if same API keys)
            reddit_ai = youtube_services.get("ai_service") or AIService()
            
            # Initialize Reddit scheduler
            reddit_scheduler = RedditAutomationScheduler(
                reddit_oauth,
                reddit_ai,
                database_manager,
                {}  # user_reddit_tokens managed by database
            )
            reddit_scheduler.start_scheduler()
            
            reddit_services = {
                "oauth": reddit_oauth,
                "ai_service": reddit_ai,
                "scheduler": reddit_scheduler
            }
            
            # ✅ CRITICAL: Patch main.py's service instances
            reddit_main.reddit_oauth_connector = reddit_oauth
            reddit_main.ai_service = reddit_ai
            reddit_main.automation_scheduler = reddit_scheduler
            
            logger.info("✅ Reddit services initialized and patched")
        else:
            logger.warning("⚠️ Reddit credentials missing")
            
    except Exception as e:
        logger.error(f"❌ Reddit initialization error: {e}")
        logger.error(traceback.format_exc())
    
    logger.info("="*60)
    logger.info("✅ SERVICE INITIALIZATION COMPLETE")
    logger.info(f"Database: {'✓' if database_manager and database_manager.connected else '✗'}")
    logger.info(f"YouTube: {'✓' if youtube_services else '✗'}")
    logger.info(f"Reddit: {'✓' if reddit_services else '✗'}")
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
    version="3.1.0 - Production Ready",
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
        "version": "3.1.0",
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
        debug_scheduler_active_configs
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
    
    logger.info("✅ Reddit routes registered")
    
except Exception as e:
    logger.error(f"❌ Reddit routes registration failed: {e}")
    logger.error(traceback.format_exc())

# ============================================================================
# PLATFORM STATUS ENDPOINT
# ============================================================================
@app.get("/api/platforms/status")
async def get_platform_status(current_user: dict = Depends(get_current_user)):
    """Get connection status for all platforms"""
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
        
        # Check Reddit
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
                    "username": reddit_username,
                    "available": bool(reddit_services)
                }
            },
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Platform status check failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# DEBUG ENDPOINT
# ============================================================================




@app.post("/api/reddit/generate-ai-post")
async def generate_reddit_ai_post(request: Request, current_user: dict = Depends(get_current_user)):
    """Generate subreddit + title + content with human-like imperfections"""
    try:
        data = await request.json()
        
        # Get parameters
        post_type = data.get("post_type", "discussion")
        tone = data.get("tone", "casual")
        length = data.get("length", "medium")
        domain = data.get("domain", "tech")
        business_type = data.get("business_type", "business")
        business_description = data.get("business_description", "")
        target_audience = data.get("target_audience", "general_users")
        content_style = data.get("content_style", "casual")
        
        # Domain to subreddit mapping
        domain_subreddits = {
            "education": ["learnprogramming", "studying", "college", "education", "test"],
            "restaurant": ["food", "FoodPorn", "Cooking", "recipes", "test"],
            "tech": ["technology", "programming", "learnprogramming", "startups", "test"],
            "health": ["fitness", "HealthyFood", "loseit", "nutrition", "test"],
            "business": ["Entrepreneur", "smallbusiness", "startups", "business", "test"]
        }
        
        # Get topic based on domain
        domain_topics = {
            "education": f"my experience with {business_type}",
            "restaurant": f"discovered this amazing {business_type}",
            "tech": f"thoughts on {business_type}",
            "health": f"my journey with {business_type}",
            "business": f"lessons from running {business_type}"
        }
        
        topic = domain_topics.get(domain, business_type)
        subreddit_options = domain_subreddits.get(domain, ["test"])
        
        length_map = {
            "short": "2-3 sentences total",
            "medium": "2 short paragraphs",
            "long": "3-4 paragraphs"
        }
        
        # ✅ IMPROVED PROMPT - Forces better JSON
        prompt = f"""Create a Reddit {post_type} post about: {topic}

Context: {business_type} - {business_description}
Tone: {tone}
Length: {length_map.get(length, 'medium')}
Subreddit options: {', '.join(subreddit_options)}

RESPONSE FORMAT - Return EXACTLY this structure with no extra text:
SUBREDDIT: choose_one_subreddit
TITLE: write_engaging_title_here
CONTENT: write_post_content_here

CONTENT REQUIREMENTS:
- Add 1-2 typos (teh, recieve, definately)
- Use casual: kinda, gonna, tbh, imo, idk
- Personal: "i recently", "has anyone"
- Add question marks
- Use lowercase
- NO hashtags
- Sound like texting a friend

Example:
SUBREDDIT: food
TITLE: tried this new indian place and wow
CONTENT: so i went to this restaurant yesterday and honestly the food was amazing. like teh butter chicken was perfect and service was pretty good too. has anyone else been there? would love to hear thoughts tbh"""

        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        ai_response = None
        
        # ✅ TRY MISTRAL FIRST (Primary)
        if mistral_api_key:
            try:
                import httpx
                
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    response = await http_client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {mistral_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {"role": "system", "content": "You are a casual Reddit user. Return responses in SUBREDDIT/TITLE/CONTENT format only."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.8,
                            "max_tokens": 1500
                        }
                    )
                    
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    logger.info("✅ Mistral API success")
            except Exception as e:
                logger.error(f"Mistral API error: {e}")
        
        # ✅ FALLBACK TO GROQ (if Mistral fails)
        if not ai_response and groq_api_key:
            try:
                import httpx
                
                # Use httpx instead of Groq client to avoid proxies issue
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    response = await http_client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {groq_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "messages": [
                                {"role": "system", "content": "You are a casual Reddit user. Return responses in SUBREDDIT/TITLE/CONTENT format only."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.8,
                            "max_tokens": 1500
                        }
                    )
                    
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    logger.info("✅ Groq API success")
            except Exception as e:
                logger.error(f"Groq API error: {e}")
        
        if not ai_response:
            raise HTTPException(status_code=500, detail="No AI service available")
        
        # ✅ PARSE RESPONSE (Structure-based, not JSON)
        import re
        
        logger.info(f"Raw AI response: {ai_response[:300]}")
        
        # Extract fields using regex
        subreddit_match = re.search(r'SUBREDDIT:\s*([^\n]+)', ai_response, re.IGNORECASE)
        title_match = re.search(r'TITLE:\s*([^\n]+)', ai_response, re.IGNORECASE)
        content_match = re.search(r'CONTENT:\s*(.+?)(?:$|SUBREDDIT:|TITLE:)', ai_response, re.IGNORECASE | re.DOTALL)
        
        subreddit = subreddit_match.group(1).strip() if subreddit_match else subreddit_options[0]
        title = title_match.group(1).strip() if title_match else "Check this out"
        content = content_match.group(1).strip() if content_match else "Interesting thoughts..."
        
        # Clean up content
        content = content.replace('\\n', '\n').strip()
        
        # Add extra human touches
        content = add_human_touches(content)
        
        # Calculate human score
        human_score = calculate_enhanced_human_score(content)
        
        logger.info(f"✅ Generated - Sub: {subreddit}, Score: {human_score}/100")
        
        return {
            "success": True,
            "subreddit": subreddit,
            "title": title,
            "content": content,
            "human_score": human_score
        }
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


def add_human_touches(content: str) -> str:
    """Add human-like imperfections"""
    import random
    
    # Add typos (10% chance)
    typos = {
        " the ": " teh ",
        "receive": "recieve",
        "definitely": "definately"
    }
    
    for correct, typo in typos.items():
        if correct in content.lower() and random.random() < 0.1:
            content = content.replace(correct, typo, 1)
    
    # Add casual language (15% chance)
    casual = {
        " really ": " rly ",
        " though ": " tho ",
        "kind of": "kinda",
        "going to": "gonna"
    }
    
    for formal, cas in casual.items():
        if formal in content.lower() and random.random() < 0.15:
            content = content.replace(formal, cas, 1)
    
    return content


def calculate_enhanced_human_score(content: str) -> int:
    """Calculate human-like score"""
    score = 50
    
    # Rewards
    if "teh" in content or "recieve" in content or "definately" in content:
        score += 20
    if any(w in content.lower() for w in ["kinda", "gonna", "tbh", "imo", "idk"]):
        score += 15
    if any(w in content.lower() for w in [" i ", " my ", " me "]):
        score += 10
    if "?" in content:
        score += 10
    
    # Penalties
    if any(w in content.lower() for w in ["delve", "utilize", "leverage", "comprehensive"]):
        score -= 20
    if content.count("!") > 3:
        score -= 15
    
    return max(20, min(score, 100))

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