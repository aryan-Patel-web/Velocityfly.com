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
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from enum import Enum

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
    """Custom handler for 422 validation errors with detailed logging"""
    
    # Log the detailed error for debugging
    logger.error(f"=== 422 VALIDATION ERROR ===")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Request headers: {dict(request.headers)}")
    logger.error(f"Validation errors: {exc.errors()}")
    logger.error(f"Request body received: {exc.body}")
    logger.error(f"================================")
    
    # Return detailed error response for debugging
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed - check request format",
            "details": exc.errors(),
            "request_body_received": exc.body,
            "expected_format": "Check API documentation",
            "timestamp": datetime.now().isoformat()
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

# FIXED OAuth callback endpoint
@app.get("/api/youtube/oauth-callback")
async def youtube_oauth_callback_get(code: str, state: str):
    """Handle YouTube OAuth callback from Google - FIXED GET endpoint"""
    try:
        logger.info(f"YouTube OAuth callback received - state: {state}, code: {code[:20]}...")
        
        if "youtube_oauth_" in state:
            user_id = state.replace("youtube_oauth_", "")
            logger.info(f"Extracted user_id from state: {user_id}")
        else:
            logger.error(f"Invalid state format: {state}")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/youtube?error=invalid_state",
                status_code=302
            )
        
        if not youtube_connector:
            logger.error("YouTube connector not available")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/youtube?error=service_unavailable",
                status_code=302
            )
        
        backend_redirect_uri = "https://agentic-u5lx.onrender.com/api/youtube/oauth-callback"
        logger.info(f"Token exchange with redirect_uri: {backend_redirect_uri}")
            
        token_result = await youtube_connector.exchange_code_for_token(
            code=code,
            redirect_uri=backend_redirect_uri
        )
        
        if not token_result["success"]:
            logger.error(f"Token exchange failed: {token_result.get('error')}")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/youtube?error=token_exchange_failed",
                status_code=302
            )
        
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
        
        try:
            success = await database_manager.store_youtube_credentials(
                user_id=user_id,
                credentials=youtube_credentials
            )
            
            if success:
                logger.info(f"YouTube credentials stored for user {user_id}")
            else:
                logger.error(f"Failed to store YouTube credentials for user {user_id}")
                
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
        
        channel_title = token_result["channel_info"].get("title", "Unknown Channel")
        logger.info(f"YouTube OAuth SUCCESS - Channel: {channel_title}")
        
        return RedirectResponse(
            url=f"https://frontend-agentic-bnc2.onrender.com/youtube?youtube_connected=true&channel={channel_title}",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"YouTube OAuth callback failed: {e}")
        return RedirectResponse(
            url="https://frontend-agentic-bnc2.onrender.com/youtube?error=oauth_failed",
            status_code=302
        )

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
async def youtube_status(user_id: str):
    """Get YouTube connection and automation status with persistent token check"""
    try:
        logger.info(f"Checking YouTube status for user: {user_id}")
        
        youtube_connected = False
        channel_info = None
        credentials_valid = False
        credentials = None
        
        try:
            credentials = await database_manager.get_youtube_credentials(user_id)
            if credentials and credentials.get("is_active"):
                youtube_connected = True
                channel_info = credentials.get("channel_info")
                
                expires_at = credentials.get("expires_at")
                if expires_at and isinstance(expires_at, datetime):
                    credentials_valid = datetime.now() < expires_at
                else:
                    credentials_valid = True
                
                logger.info(f"YouTube credentials found for user {user_id}, valid: {credentials_valid}")
            else:
                logger.info(f"No active YouTube credentials found for user {user_id}")
        except Exception as db_error:
            logger.error(f"Database error fetching YouTube status: {db_error}")
        
        # Get automation status if scheduler is available
        automation_status = {}
        if youtube_scheduler and youtube_connected:
            automation_status = await youtube_scheduler.get_automation_status(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "youtube_connected": youtube_connected and credentials_valid,
            "channel_info": channel_info,
            "connected_at": credentials.get("created_at") if credentials else None,
            "last_updated": credentials.get("updated_at") if credentials else None,
            "youtube_automation": automation_status.get("youtube_automation", {
                "enabled": False,
                "config": None,
                "stats": {
                    "total_uploads": 0,
                    "successful_uploads": 0,
                    "failed_uploads": 0
                }
            })
        }
        
    except Exception as e:
        logger.error(f"YouTube status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
async def youtube_analytics(user_id: str, days: int = 30):
    """Get YouTube channel analytics - FIXED"""
    try:
        logger.info(f"Fetching YouTube analytics for user {user_id}, days: {days}")
        
        # Check if user has YouTube connected
        try:
            credentials = await database_manager.get_youtube_credentials(user_id)
            if not credentials:
                raise HTTPException(status_code=400, detail="YouTube not connected")
            
            # Try to get real analytics using YouTube connector
            if youtube_connector:
                try:
                    analytics_result = await youtube_connector.get_channel_analytics(credentials, days)
                    if analytics_result.get("success"):
                        logger.info(f"Real analytics returned for user {user_id}")
                        return {
                            "success": True,
                            "analytics": analytics_result,
                            "period_days": days,
                            "user_id": user_id,
                            "data_source": "youtube_api"
                        }
                except Exception as api_error:
                    logger.warning(f"YouTube API analytics failed: {api_error}")
                    
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
        
        # Fallback to mock analytics (enhanced with realistic data)
        mock_analytics = {
            "success": True,
            "analytics": {
                "channel_stats": {
                    "subscribers": 1,
                    "total_views": 17,
                    "total_videos": 1,
                    "average_view_duration": "2:15",
                    "subscriber_growth": 0,
                    "view_growth": 0
                },
                "recent_videos": [
                    {
                        "video_id": "mock_video_1",
                        "title": "Bajaj claim adviser",
                        "views": 17,
                        "likes": 0,
                        "comments": 0,
                        "published_at": "2 months ago",
                        "duration": "4:33",
                        "performance": "below_average"
                    }
                ],
                "performance": {
                    "views_last_30_days": 17,
                    "subscribers_gained": 0,
                    "estimated_minutes_watched": 38,
                    "top_traffic_source": "YouTube search",
                    "engagement_rate": "0.0%",
                    "click_through_rate": "0.5%"
                },
                "demographics": {
                    "top_countries": ["India"],
                    "age_groups": {
                        "18-24": 50,
                        "25-34": 30,
                        "35-44": 20
                    },
                    "gender_split": {
                        "male": 60,
                        "female": 40
                    }
                },
                "revenue": {
                    "estimated_earnings": "$0.00",
                    "rpm": "$0.00",
                    "monetization_status": "not_eligible"
                }
            },
            "period_days": days,
            "user_id": user_id,
            "data_source": "mock",
            "note": "This is mock data. Connect your channel and wait 24-48 hours for real analytics."
        }
        
        logger.info(f"Mock analytics returned for user {user_id}")
        return mock_analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")




@app.post("/api/youtube/upload")
async def youtube_upload_video(request: dict):
    """Upload video to YouTube with thumbnail support"""
    try:
        logger.info(f"YouTube upload request: {request}")
        
        user_id = request.get("user_id")
        title = request.get("title", "Untitled Video")
        video_url = request.get("video_url", "")
        description = request.get("description", "")
        tags = request.get("tags", [])
        privacy_status = request.get("privacy_status", "public")
        content_type = request.get("content_type", "video")
        thumbnail_url = request.get("thumbnail_url")  # ← ADDED THIS LINE
        
        # DEBUG: Log thumbnail info
        logger.info(f"🔍 Thumbnail URL present: {thumbnail_url is not None}")
        if thumbnail_url:
            logger.info(f"🔍 Thumbnail data length: {len(thumbnail_url)} chars")
            logger.info(f"🔍 Thumbnail preview: {thumbnail_url[:100]}")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        if not video_url:
            raise HTTPException(status_code=400, detail="video_url is required")
        
        # Validate video URL format
        if not video_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="video_url must be a valid HTTP/HTTPS URL")
        
        # Check if user has YouTube connected
        try:
            credentials = await database_manager.get_youtube_credentials(user_id)
            if not credentials:
                raise HTTPException(status_code=400, detail="YouTube not connected")
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            return {
                "success": False,
                "error": "Database connection error"
            }
        
        # Try real upload using YouTube connector and scheduler
        if youtube_connector and youtube_scheduler:
            try:
                upload_result = await youtube_scheduler.generate_and_upload_content(
                    user_id=user_id,
                    credentials_data=credentials,
                    content_type=content_type,
                    title=title,
                    description=description,
                    video_url=video_url,
                    thumbnail_url=thumbnail_url  # ← ADDED THIS LINE
                )
                
                if upload_result.get("success"):
                    # Log successful upload to database
                    await database_manager.log_video_upload(
                        user_id=user_id,
                        video_data={
                            "video_id": upload_result.get("video_id", f"upload_{int(datetime.now().timestamp())}"),
                            "video_url": upload_result.get("video_url", video_url),
                            "title": title,
                            "description": description,
                            "tags": tags,
                            "privacy_status": privacy_status,
                            "content_type": content_type,
                            "ai_generated": False,
                            "thumbnail_uploaded": upload_result.get("thumbnail_uploaded", False)  # ← ADDED THIS
                        }
                    )
                    
                    logger.info(f"Real upload successful for user {user_id}")
                    logger.info(f"📊 Thumbnail uploaded: {upload_result.get('thumbnail_uploaded', False)}")
                    return upload_result
                else:
                    logger.warning(f"Upload failed via scheduler: {upload_result.get('error')}")
                    
            except Exception as upload_error:
                logger.error(f"Upload via scheduler failed: {upload_error}")
        
        # Fallback to mock upload response
        mock_video_id = f"mock_video_{user_id}_{int(datetime.now().timestamp())}"
        upload_result = {
            "success": True,
            "message": "Video upload initiated successfully (Mock Mode)",
            "video_details": {
                "title": title,
                "description": description,
                "video_url": video_url,
                "upload_status": "processing",
                "estimated_processing_time": "5-10 minutes",
                "video_id": mock_video_id,
                "watch_url": f"https://youtube.com/watch?v={mock_video_id}",
                "privacy_status": privacy_status,
                "content_type": content_type,
                "tags": tags
            },
            "user_id": user_id,
            "upload_method": "mock",
            "note": "This is a mock upload. Real uploads require proper YouTube API setup."
        }
        
        # Log mock upload to database
        try:
            await database_manager.log_video_upload(
                user_id=user_id,
                video_data={
                    "video_id": mock_video_id,
                    "video_url": video_url,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "privacy_status": privacy_status,
                    "content_type": content_type,
                    "ai_generated": False
                }
            )
        except Exception as log_error:
            logger.warning(f"Failed to log mock upload: {log_error}")
        
        logger.info(f"Mock upload successful for user {user_id}")
        return upload_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube upload failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Upload failed"
        }
    


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


@app.get("/api/youtube/scheduled-posts/{user_id}")
async def get_scheduled_posts(user_id: str, status: str = None):
    """Get scheduled posts for a user"""
    try:
        if not database_manager:
            return {
                "success": False,
                "error": "Database not available",
                "scheduled_posts": [],
                "count": 0
            }
        
        posts = await database_manager.get_scheduled_posts_by_user(user_id, status)
        
        # Format posts for frontend
        formatted_posts = []
        for post in posts:
            try:
                formatted_posts.append({
                    "id": str(post["_id"]),
                    "title": post.get("video_data", {}).get("title", "Untitled"),
                    "video_url": post.get("video_data", {}).get("video_url", ""),
                    "scheduled_for": post["scheduled_for"].isoformat() if post.get("scheduled_for") else None,
                    "status": post.get("status", "unknown"),
                    "created_at": post["created_at"].isoformat() if post.get("created_at") else None,
                    "execution_attempts": post.get("execution_attempts", 0),
                    "last_error": post.get("last_error")
                })
            except Exception as format_error:
                logger.warning(f"Failed to format post {post.get('_id')}: {format_error}")
                continue
        
        return {
            "success": True,
            "scheduled_posts": formatted_posts,
            "count": len(formatted_posts)
        }
        
    except Exception as e:
        logger.error(f"Get scheduled posts failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e),
            "scheduled_posts": [],
            "count": 0
        }


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