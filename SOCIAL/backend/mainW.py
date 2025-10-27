# """
# Complete Multi-Platform Social Media Automation System
# YouTube, WhatsApp, Instagram, Facebook with unified API
# Real AI content generation and multi-user support
# """

# from fastapi import FastAPI, HTTPException, Request, Query, BackgroundTasks, Header, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.responses import JSONResponse, RedirectResponse, Response
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from contextlib import asynccontextmanager
# import asyncio
# import logging
# from typing import Dict, List, Optional, Any
# from datetime import datetime, timedelta
# import uvicorn
# import json
# import threading
# import random
# from pydantic import BaseModel, EmailStr
# import sys
# import traceback
# import uuid
# import os
# import requests
# import base64

# # Load environment variables
# from dotenv import load_dotenv
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(sys.stdout),
#         logging.FileHandler("multiplatform_automation.log")
#     ]
# )
# logger = logging.getLogger(__name__)

# # Import custom modules
# try:
#     from youtube import YouTubeOAuthConnector, YouTubeAutomationScheduler, YouTubeConfig
#     YOUTUBE_AVAILABLE = True
#     logger.info("YouTube module loaded successfully")
# except ImportError as e:
#     logger.warning(f"YouTube module not available: {e}")
#     YOUTUBE_AVAILABLE = False

# try:
#     from whatsapp import WhatsAppCloudAPI, WhatsAppAutomationScheduler, WhatsAppConfig, WhatsAppWebhookHandler
#     WHATSAPP_AVAILABLE = True
#     logger.info("WhatsApp module loaded successfully")
# except ImportError as e:
#     logger.warning(f"WhatsApp module not available: {e}")
#     WHATSAPP_AVAILABLE = False

# try:
#     from ai_service2 import AIService2
#     AI_SERVICE_AVAILABLE = True
#     logger.info("AI Service 2 loaded successfully")
# except ImportError as e:
#     logger.warning(f"AI Service 2 not available: {e}")
#     AI_SERVICE_AVAILABLE = False

# try:
#     from database2 import MultiPlatformDatabaseManager
#     DATABASE_AVAILABLE = True
#     logger.info("Multi-platform database loaded successfully")
# except ImportError as e:
#     logger.warning(f"Multi-platform database not available: {e}")
#     DATABASE_AVAILABLE = False

# # Global instances
# database_manager = None
# ai_service = None
# youtube_connector = None
# youtube_scheduler = None
# whatsapp_scheduler = None
# webhook_handler = None

# # Multi-user management
# user_platform_tokens = {}  # user_id -> {platform: tokens}
# oauth_states = {}          # oauth_state -> user_id
# automation_configs = {}    # user_id -> {platform: configs}

# # Authentication setup
# security = HTTPBearer()





# # Add these imports to the top of your main2.py file
# from datetime import datetime, timedelta
# from youtube import initialize_youtube_service, youtube_connector, youtube_scheduler
# from pydantic import BaseModel
# from typing import Optional

# # Add these Pydantic models after your existing models in main2.py
# class YouTubeOAuthRequest(BaseModel):
#     user_id: str
#     state: str = "youtube_oauth"
#     redirect_uri: Optional[str] = None

# class YouTubeOAuthCallback(BaseModel):
#     user_id: str
#     code: str
#     state: Optional[str] = None
#     redirect_uri: Optional[str] = None

# class YouTubeSetupRequest(BaseModel):
#     user_id: str
#     config: dict

# class YouTubeUploadRequest(BaseModel):
#     user_id: str
#     title: str
#     description: str
#     video_url: str
#     content_type: str = "shorts"

# class YouTubeContentRequest(BaseModel):
#     content_type: str = "shorts"
#     topic: str = "general"
#     target_audience: str = "general"

# # Initialize YouTube service (add this after your database and ai_service initialization)
# # Place this after: database_manager = DatabaseManager() and ai_service = AIService2()
# try:
#     if not initialize_youtube_service(database_manager, ai_service):
#         logger.warning("YouTube service initialization failed - OAuth endpoints will not work")
#     else:
#         logger.info("YouTube service initialized successfully")
# except Exception as e:
#     logger.error(f"YouTube service initialization error: {e}")





# # Request Models
# class RegisterRequest(BaseModel):
#     email: EmailStr
#     password: str
#     name: str

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# class YouTubeUploadRequest(BaseModel):
#     title: str
#     description: str
#     video_url: str
#     tags: List[str] = []
#     privacy_status: str = "public"

# class WhatsAppMessageRequest(BaseModel):
#     to: str
#     message: str
#     message_type: str = "text"

# class WhatsAppMediaRequest(BaseModel):
#     to: str
#     media_url: str
#     media_type: str = "image"
#     caption: str = None

# class YouTubeAutomationRequest(BaseModel):
#     content_type: str = "shorts"
#     upload_schedule: List[str]
#     content_categories: List[str] = []
#     auto_generate_titles: bool = True
#     privacy_status: str = "public"
#     shorts_per_day: int = 3

# class WhatsAppAutomationRequest(BaseModel):
#     business_name: str
#     auto_reply_enabled: bool = False
#     campaign_enabled: bool = False
#     business_hours: Dict[str, str] = {"start": "09:00", "end": "18:00"}

# class BroadcastRequest(BaseModel):
#     platform: str
#     recipient_list: List[str]
#     message: str
#     media_url: str = None
#     media_type: str = None





















# # Authentication dependency
# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Get current authenticated user from JWT token"""
#     try:
#         token = credentials.credentials
#         if not database_manager:
#             raise HTTPException(status_code=500, detail="Database not available")
        
#         user = await database_manager.get_user_by_token(token)
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid or expired token")
        
#         return user
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Authentication failed: {e}")
#         raise HTTPException(status_code=401, detail="Authentication failed")

# # Mock classes for fallback
# class MockAIService:
#     def __init__(self):
#         self.is_mock = True
        
#     async def generate_youtube_content(self, **kwargs):
#         return {
#             "success": True,
#             "title": f"Mock YouTube {kwargs.get('content_type', 'content')}",
#             "description": "Mock description - configure AI keys for real content",
#             "script": "Mock script content",
#             "tags": ["mock", "test"],
#             "ai_service": "mock"
#         }
    
#     async def generate_whatsapp_content(self, **kwargs):
#         return {
#             "success": True,
#             "message": f"Mock WhatsApp {kwargs.get('message_type', 'message')}",
#             "ai_service": "mock"
#         }

# class MockDatabase:
#     def __init__(self):
#         self.users = {}
#         self.tokens = {}
        
#     async def connect(self):
#         return True
        
#     async def register_user(self, email, password, name):
#         user_id = f"mock_{uuid.uuid4().hex[:8]}"
#         self.users[user_id] = {"email": email, "name": name}
#         return {
#             "success": True,
#             "user_id": user_id,
#             "email": email,
#             "name": name,
#             "token": f"mock_token_{user_id}",
#             "message": "Mock registration successful"
#         }
    
#     async def login_user(self, email, password):
#         for user_id, user in self.users.items():
#             if user["email"] == email:
#                 return {
#                     "success": True,
#                     "user_id": user_id,
#                     "email": email,
#                     "name": user["name"],
#                     "token": f"mock_token_{user_id}",
#                     "message": "Mock login successful"
#                 }
#         # Create new user for demo
#         return await self.register_user(email, password, email.split('@')[0])
    
#     async def get_user_by_token(self, token):
#         user_id = token.replace("mock_token_", "")
#         if user_id in self.users:
#             user = self.users[user_id]
#             return {
#                 "id": user_id,
#                 "email": user["email"],
#                 "name": user["name"]
#             }
#         return None

# # Application lifespan management
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application startup and shutdown"""
#     global database_manager, ai_service, youtube_connector, youtube_scheduler, whatsapp_scheduler, webhook_handler
    
#     logger.info("Starting Multi-Platform Social Media Automation System...")
#     print("🚀 Initializing Multi-Platform Automation System...")
    
#     # Initialize Database
#     try:
#         if DATABASE_AVAILABLE:
#             database_manager = MultiPlatformDatabaseManager(
#                 mongodb_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017/social_automation"),
#                 encryption_key=os.getenv("TOKEN_ENCRYPTION_KEY")
#             )
#             await database_manager.connect()
#             logger.info("Multi-platform database connected")
#             print("✅ Database: Connected")
#         else:
#             database_manager = MockDatabase()
#             await database_manager.connect()
#             print("⚠️  Database: Mock mode")
#     except Exception as e:
#         logger.warning(f"Database initialization failed: {e}")
#         database_manager = MockDatabase()
#         await database_manager.connect()
#         print("⚠️  Database: Mock fallback")
    
#     # Initialize AI Service
#     try:
#         if AI_SERVICE_AVAILABLE:
#             ai_service = AIService2()
#             test_result = await ai_service.test_ai_connection()
#             if test_result.get("success"):
#                 logger.info(f"AI Service initialized: {test_result.get('primary_service')}")
#                 print(f"✅ AI Service: {test_result.get('primary_service').upper()}")
#             else:
#                 raise Exception("AI test failed")
#         else:
#             raise Exception("AI service not available")
#     except Exception as e:
#         logger.warning(f"AI service initialization failed: {e}")
#         ai_service = MockAIService()
#         print("⚠️  AI Service: Mock mode")
    
#     # Initialize YouTube
#     try:
#         if YOUTUBE_AVAILABLE:
#             google_client_id = os.getenv("GOOGLE_CLIENT_ID")
#             google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
#             google_redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "https://agentic-u5lx.onrender.com/api/oauth/google/callback")
            
#             if google_client_id and google_client_secret:
#                 youtube_connector = YouTubeOAuthConnector(
#                     client_id=google_client_id,
#                     client_secret=google_client_secret,
#                     redirect_uri=google_redirect_uri
#                 )
                
#                 youtube_scheduler = YouTubeAutomationScheduler(
#                     youtube_connector=youtube_connector,
#                     ai_service=ai_service,
#                     database_manager=database_manager,
#                     user_tokens=user_platform_tokens
#                 )
                
#                 logger.info("YouTube automation initialized")
#                 print("✅ YouTube: Ready")
#             else:
#                 raise Exception("YouTube credentials missing")
#         else:
#             raise Exception("YouTube module not available")
#     except Exception as e:
#         logger.warning(f"YouTube initialization failed: {e}")
#         print("⚠️  YouTube: Not configured")
    
#     # Initialize WhatsApp
#     try:
#         if WHATSAPP_AVAILABLE:
#             whatsapp_scheduler = WhatsAppAutomationScheduler(
#                 ai_service=ai_service,
#                 database_manager=database_manager
#             )
            
#             webhook_verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "default_verify_token")
#             webhook_handler = WhatsAppWebhookHandler(verify_token=webhook_verify_token)
            
#             logger.info("WhatsApp automation initialized")
#             print("✅ WhatsApp: Ready")
#         else:
#             raise Exception("WhatsApp module not available")
#     except Exception as e:
#         logger.warning(f"WhatsApp initialization failed: {e}")
#         print("⚠️  WhatsApp: Not configured")
    
#     # Final status
#     real_components = []
#     mock_components = []
    
#     if not isinstance(ai_service, MockAIService):
#         real_components.append("AI Content Generation")
#     else:
#         mock_components.append("AI Service")
        
#     if DATABASE_AVAILABLE and not isinstance(database_manager, MockDatabase):
#         real_components.append("Database")
#     else:
#         mock_components.append("Database")
        
#     if youtube_connector:
#         real_components.append("YouTube")
#     else:
#         mock_components.append("YouTube")
        
#     if whatsapp_scheduler:
#         real_components.append("WhatsApp")
#     else:
#         mock_components.append("WhatsApp")
    
#     print(f"\n🎯 Real Components: {', '.join(real_components) if real_components else 'None'}")
#     print(f"🔧 Mock Components: {', '.join(mock_components) if mock_components else 'None'}")
#     print("🚀 Multi-Platform System Ready!\n")
    
#     yield
    
#     # Cleanup
#     logger.info("Shutting down multi-platform system...")
#     if database_manager and hasattr(database_manager, 'disconnect'):
#         await database_manager.disconnect()

# # Create FastAPI app
# app = FastAPI(
#     title="Multi-Platform Social Media Automation",
#     description="Complete automation system for YouTube, WhatsApp, Instagram, and Facebook",
#     version="2.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc",
#     lifespan=lifespan
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:5173",
#         "https://velocitypost-ai.onrender.com",
#         "https://agentic-u5lx.onrender.com",
#         "*"
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=[
#         "Content-Type", 
#         "Authorization", 
#         "X-User-Token",
#         "Accept",
#         "Origin",
#         "X-Requested-With"
#     ],
#     expose_headers=["*"],
#     max_age=3600
# )

# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# # Preflight OPTIONS handler
# @app.options("/{path:path}")
# async def options_handler(request: Request):
#     return Response(
#         content="",
#         status_code=200,
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
#             "Access-Control-Allow-Headers": "Content-Type, Authorization, X-User-Token",
#             "Access-Control-Max-Age": "3600"
#         }
#     )

# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Global exception on {request.url}: {exc}")
#     logger.error(traceback.format_exc())
#     return JSONResponse(
#         status_code=500,
#         content={
#             "success": False,
#             "error": str(exc),
#             "message": "An unexpected error occurred.",
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# # Health check endpoints
# @app.get("/")
# async def root():
#     """Root endpoint with system status"""
#     return {
#         "success": True,
#         "message": "Multi-Platform Social Media Automation System",
#         "version": "2.0.0",
#         "platforms": {
#             "youtube": youtube_connector is not None,
#             "whatsapp": whatsapp_scheduler is not None,
#             "instagram": False,  # TODO: Add Instagram
#             "facebook": False    # TODO: Add Facebook
#         },
#         "services": {
#             "ai": not isinstance(ai_service, MockAIService),
#             "database": DATABASE_AVAILABLE and not isinstance(database_manager, MockDatabase)
#         },
#         "timestamp": datetime.now().isoformat()
#     }




# @app.get("/health")
# async def health_check():
#     """Comprehensive health check"""
#     try:
#         health_data = {
#             "status": "healthy",
#             "timestamp": datetime.now().isoformat(),
#             "version": "2.0.0",
#             "services": {
#                 "database": {
#                     "available": database_manager is not None,
#                     "type": type(database_manager).__name__,
#                     "real": DATABASE_AVAILABLE and not isinstance(database_manager, MockDatabase)
#                 },
#                 "ai_service": {
#                     "available": ai_service is not None,
#                     "type": type(ai_service).__name__,
#                     "real": not isinstance(ai_service, MockAIService)
#                 },
#                 "youtube": {
#                     "available": youtube_connector is not None,
#                     "scheduler": youtube_scheduler is not None
#                 },
#                 "whatsapp": {
#                     "available": whatsapp_scheduler is not None,
#                     "webhook": webhook_handler is not None
#                 }
#             },
#             "stats": {
#                 "active_users": len(user_platform_tokens),
#                 "oauth_states": len(oauth_states),
#                 "automation_configs": len(automation_configs)
#             }
#         }
        
#         # Test database if available
#         if hasattr(database_manager, 'health_check'):
#             try:
#                 db_health = await database_manager.health_check()
#                 health_data["database_health"] = db_health
#             except Exception as e:
#                 health_data["database_health"] = {"error": str(e)}
        
#         return health_data
        
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         return {
#             "status": "unhealthy",
#             "error": str(e),
#             "timestamp": datetime.now().isoformat()
#         }

# # Authentication endpoints
# @app.post("/api/auth/register")
# async def register_user(user_data: RegisterRequest):
#     """Register new user"""
#     try:
#         result = await database_manager.register_user(
#             email=user_data.email,
#             password=user_data.password,
#             name=user_data.name
#         )
        
#         if result.get("success"):
#             logger.info(f"User registered: {user_data.email}")
        
#         return result
        
#     except Exception as e:
#         logger.error(f"Registration failed: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/api/auth/login")
# async def login_user(login_data: LoginRequest):
#     """Login user"""
#     try:
#         result = await database_manager.login_user(
#             email=login_data.email,
#             password=login_data.password
#         )
        
#         if result.get("success"):
#             logger.info(f"User logged in: {login_data.email}")
        
#         return result
        
#     except Exception as e:
#         logger.error(f"Login failed: {e}")
#         raise HTTPException(status_code=401, detail="Invalid credentials")

# @app.get("/api/auth/me")
# async def get_current_user_info(current_user: dict = Depends(get_current_user)):
#     """Get current user information"""
#     return {
#         "success": True,
#         "user": current_user
#     }

# # YouTube OAuth endpoints
# @app.get("/api/oauth/youtube/authorize")
# async def youtube_oauth_authorize(current_user: dict = Depends(get_current_user)):
#     """Start YouTube OAuth flow"""
#     try:
#         if not youtube_connector:
#             raise HTTPException(status_code=500, detail="YouTube not configured")
        
#         user_id = current_user["id"]
#         state = f"youtube_{user_id}_{uuid.uuid4().hex[:12]}"
#         oauth_states[state] = user_id
        
#         result = youtube_connector.generate_oauth_url(state=state)
        
#         if result.get("success"):
#             logger.info(f"YouTube OAuth started for user {user_id}")
#             return {
#                 "success": True,
#                 "redirect_url": result["authorization_url"],
#                 "state": state
#             }
        
#         return result
        
#     except Exception as e:
#         logger.error(f"YouTube OAuth failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/oauth/youtube/callback")
# async def youtube_oauth_callback(code: str, state: str):
#     """Handle YouTube OAuth callback"""
#     try:
#         user_id = oauth_states.get(state)
#         if not user_id:
#             return RedirectResponse(
#                 url=f"{os.getenv('FRONTEND_URL')}?error=invalid_state",
#                 status_code=302
#             )
        
#         # Exchange code for token
#         result = await youtube_connector.exchange_code_for_token(code)
        
#         if result.get("success"):
#             # Store tokens
#             user_platform_tokens[user_id] = user_platform_tokens.get(user_id, {})
#             user_platform_tokens[user_id]["youtube"] = result
            
#             # Store in database
#             if hasattr(database_manager, 'store_platform_tokens'):
#                 await database_manager.store_platform_tokens(
#                     user_id=user_id,
#                     platform="youtube",
#                     token_data=result
#                 )
            
#             channel_name = result.get('channel_info', {}).get('channel_name', 'Unknown')
#             logger.info(f"YouTube connected for user {user_id}: {channel_name}")
            
#             oauth_states.pop(state, None)
            
#             return RedirectResponse(
#                 url=f"{os.getenv('FRONTEND_URL')}?youtube_connected=true&channel={channel_name}",
#                 status_code=302
#             )
#         else:
#             return RedirectResponse(
#                 url=f"{os.getenv('FRONTEND_URL')}?error=youtube_auth_failed",
#                 status_code=302
#             )
            
#     except Exception as e:
#         logger.error(f"YouTube callback failed: {e}")
#         return RedirectResponse(
#             url=f"{os.getenv('FRONTEND_URL')}?error=callback_failed",
#             status_code=302
#         )

# # YouTube endpoints
# @app.get("/api/youtube/connection-status")
# async def get_youtube_connection_status(current_user: dict = Depends(get_current_user)):
#     """Get YouTube connection status"""
#     try:
#         user_id = current_user["id"]
        
#         if hasattr(database_manager, 'check_platform_connection'):
#             status = await database_manager.check_platform_connection(user_id, "youtube")
#             return {"success": True, **status}
        
#         # Fallback to memory
#         if user_id in user_platform_tokens and "youtube" in user_platform_tokens[user_id]:
#             tokens = user_platform_tokens[user_id]["youtube"]
#             channel_info = tokens.get("channel_info", {})
#             return {
#                 "success": True,
#                 "connected": True,
#                 "channel_name": channel_info.get("channel_name"),
#                 "channel_id": channel_info.get("channel_id"),
#                 "subscriber_count": channel_info.get("subscriber_count", "0")
#             }
        
#         return {
#             "success": True,
#             "connected": False,
#             "message": "YouTube not connected"
#         }
        
#     except Exception as e:
#         logger.error(f"YouTube status check failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/youtube/upload")
# async def upload_youtube_video(
#     upload_data: YouTubeUploadRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Upload video to YouTube"""
#     try:
#         user_id = current_user["id"]
        
#         if not youtube_scheduler:
#             raise HTTPException(status_code=500, detail="YouTube scheduler not available")
        
#         result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             content_type="video",
#             title=upload_data.title,
#             description=upload_data.description,
#             video_url=upload_data.video_url
#         )
        
#         # Log activity
#         if hasattr(database_manager, 'log_content_activity'):
#             await database_manager.log_content_activity(
#                 user_id=user_id,
#                 platform="youtube",
#                 activity_type="upload",
#                 activity_data={
#                     "success": result.get("success", False),
#                     "title": upload_data.title,
#                     "video_url": result.get("video_url"),
#                     "manual": True
#                 }
#             )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"YouTube upload failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/youtube/automation/setup")
# async def setup_youtube_automation(
#     config_data: YouTubeAutomationRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Setup YouTube automation"""
#     try:
#         user_id = current_user["id"]
        
#         if not youtube_scheduler:
#             return {"success": False, "error": "YouTube scheduler not available"}
        
#         config = YouTubeConfig(
#             user_id=user_id,
#             content_type=config_data.content_type,
#             upload_schedule=config_data.upload_schedule,
#             content_categories=config_data.content_categories,
#             auto_generate_titles=config_data.auto_generate_titles,
#             privacy_status=config_data.privacy_status,
#             shorts_per_day=config_data.shorts_per_day
#         )
        
#         result = await youtube_scheduler.setup_youtube_automation(config)
        
#         if result.get("success"):
#             automation_configs[user_id] = automation_configs.get(user_id, {})
#             automation_configs[user_id]["youtube"] = {
#                 "config": config,
#                 "enabled": True,
#                 "created_at": datetime.now()
#             }
        
#         return result
        
#     except Exception as e:
#         logger.error(f"YouTube automation setup failed: {e}")
#         return {"success": False, "error": str(e)}

# # WhatsApp endpoints
# @app.post("/api/whatsapp/setup")
# async def setup_whatsapp(
#     config_data: WhatsAppAutomationRequest,
#     current_user: dict = Depends(get_current_user),
#     phone_number_id: str = Query(..., description="WhatsApp Phone Number ID"),
#     access_token: str = Query(..., description="WhatsApp Access Token")
# ):
#     """Setup WhatsApp automation"""
#     try:
#         user_id = current_user["id"]
        
#         if not whatsapp_scheduler:
#             return {"success": False, "error": "WhatsApp scheduler not available"}
        
#         config = WhatsAppConfig(
#             user_id=user_id,
#             business_name=config_data.business_name,
#             phone_number_id=phone_number_id,
#             access_token=access_token,
#             auto_reply_enabled=config_data.auto_reply_enabled,
#             campaign_enabled=config_data.campaign_enabled,
#             business_hours=config_data.business_hours
#         )
        
#         result = await whatsapp_scheduler.setup_whatsapp_automation(
#             user_id=user_id,
#             phone_number_id=phone_number_id,
#             access_token=access_token,
#             config=config
#         )
        
#         if result.get("success"):
#             # Store tokens for user
#             user_platform_tokens[user_id] = user_platform_tokens.get(user_id, {})
#             user_platform_tokens[user_id]["whatsapp"] = {
#                 "phone_number_id": phone_number_id,
#                 "access_token": access_token,
#                 "business_name": config_data.business_name
#             }
            
#             # Store in database
#             if hasattr(database_manager, 'store_platform_tokens'):
#                 await database_manager.store_platform_tokens(
#                     user_id=user_id,
#                     platform="whatsapp",
#                     token_data={
#                         "phone_number_id": phone_number_id,
#                         "access_token": access_token,
#                         "business_name": config_data.business_name
#                     }
#                 )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"WhatsApp setup failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/whatsapp/send-message")
# async def send_whatsapp_message(
#     message_data: WhatsAppMessageRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Send WhatsApp message"""
#     try:
#         user_id = current_user["id"]
        
#         if not whatsapp_scheduler:
#             return {"success": False, "error": "WhatsApp not configured"}
        
#         result = await whatsapp_scheduler.send_message(
#             user_id=user_id,
#             to=message_data.to,
#             message=message_data.message,
#             message_type=message_data.message_type
#         )
        
#         # Log activity
#         if hasattr(database_manager, 'log_content_activity'):
#             await database_manager.log_content_activity(
#                 user_id=user_id,
#                 platform="whatsapp",
#                 activity_type="message",
#                 activity_data={
#                     "success": result.get("success", False),
#                     "to": message_data.to,
#                     "message_type": message_data.message_type,
#                     "manual": True
#                 }
#             )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"WhatsApp message send failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/whatsapp/send-media")
# async def send_whatsapp_media(
#     media_data: WhatsAppMediaRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Send WhatsApp media message"""
#     try:
#         user_id = current_user["id"]
        
#         if not whatsapp_scheduler:
#             return {"success": False, "error": "WhatsApp not configured"}
        
#         result = await whatsapp_scheduler.send_media_message(
#             user_id=user_id,
#             to=media_data.to,
#             media_url=media_data.media_url,
#             media_type=media_data.media_type,
#             caption=media_data.caption
#         )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"WhatsApp media send failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/whatsapp/broadcast")
# async def send_whatsapp_broadcast(
#     broadcast_data: BroadcastRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Send WhatsApp broadcast message"""
#     try:
#         user_id = current_user["id"]
        
#         if not whatsapp_scheduler:
#             return {"success": False, "error": "WhatsApp not configured"}
        
#         result = await whatsapp_scheduler.send_broadcast(
#             user_id=user_id,
#             recipient_list=broadcast_data.recipient_list,
#             message=broadcast_data.message,
#             media_url=broadcast_data.media_url,
#             media_type=broadcast_data.media_type
#         )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"WhatsApp broadcast failed: {e}")
#         return {"success": False, "error": str(e)}

# # WhatsApp webhook endpoints
# @app.get("/api/webhooks/whatsapp")
# async def whatsapp_webhook_verify(
#     hub_mode: str = Query(alias="hub.mode"),
#     hub_verify_token: str = Query(alias="hub.verify_token"),
#     hub_challenge: str = Query(alias="hub.challenge")
# ):
#     """Verify WhatsApp webhook"""
#     try:
#         if webhook_handler:
#             challenge = webhook_handler.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
#             if challenge:
#                 return Response(content=challenge, media_type="text/plain")
        
#         raise HTTPException(status_code=403, detail="Webhook verification failed")
        
#     except Exception as e:
#         logger.error(f"Webhook verification failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/webhooks/whatsapp")
# async def whatsapp_webhook_handler(request: Request):
#     """Handle WhatsApp webhook events"""
#     try:
#         payload = await request.body()
#         webhook_data = await request.json()
        
#         # Verify signature if configured
#         signature = request.headers.get("x-hub-signature-256", "")
#         if webhook_handler and not webhook_handler.verify_signature(payload, signature):
#             raise HTTPException(status_code=403, detail="Invalid signature")
        
#         # Parse webhook events
#         if webhook_handler:
#             events = webhook_handler.parse_webhook_event(webhook_data)
            
#             for event in events:
#                 if event["type"] == "message":
#                     # Handle incoming message
#                     # Find user by phone_number_id
#                     phone_number_id = event.get("phone_number_id")
                    
#                     # Find user with this phone number ID
#                     for user_id, tokens in user_platform_tokens.items():
#                         if tokens.get("whatsapp", {}).get("phone_number_id") == phone_number_id:
#                             await whatsapp_scheduler.handle_incoming_message(user_id, event)
#                             break
        
#         return {"success": True}
        
#     except Exception as e:
#         logger.error(f"Webhook handling failed: {e}")
#         return {"success": False, "error": str(e)}

# # AI Content Generation endpoints
# @app.post("/api/ai/generate-youtube-content")
# async def generate_youtube_content(
#     content_type: str = "shorts",
#     topic: str = "general",
#     current_user: dict = Depends(get_current_user)
# ):
#     """Generate YouTube content using AI"""
#     try:
#         result = await ai_service.generate_youtube_content(
#             content_type=content_type,
#             topic=topic,
#             target_audience="general",
#             style="engaging"
#         )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"YouTube content generation failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/ai/generate-whatsapp-content")
# async def generate_whatsapp_content(
#     message_type: str = "promotional",
#     business_type: str = "general",
#     current_user: dict = Depends(get_current_user)
# ):
#     """Generate WhatsApp content using AI"""
#     try:
#         result = await ai_service.generate_whatsapp_content(
#             message_type=message_type,
#             business_type=business_type,
#             target_audience="customers"
#         )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"WhatsApp content generation failed: {e}")
#         return {"success": False, "error": str(e)}

# # Analytics and Dashboard endpoints
# @app.get("/api/user/dashboard")
# async def get_user_dashboard(current_user: dict = Depends(get_current_user)):
#     """Get user dashboard data"""
#     try:
#         user_id = current_user["id"]
        
#         if hasattr(database_manager, 'get_user_dashboard'):
#             dashboard_data = await database_manager.get_user_dashboard(user_id)
#             return {
#                 "success": True,
#                 "dashboard": dashboard_data,
#                 "user": current_user
#             }
        
#         # Fallback dashboard
#         return {
#             "success": True,
#             "dashboard": {
#                 "platforms": {
#                     "youtube": user_id in user_platform_tokens and "youtube" in user_platform_tokens[user_id],
#                     "whatsapp": user_id in user_platform_tokens and "whatsapp" in user_platform_tokens[user_id]
#                 },
#                 "activity_summary": {
#                     "posts_today": 0,
#                     "total_posts": 0,
#                     "success_rate": 0
#                 }
#             },
#             "user": current_user
#         }
        
#     except Exception as e:
#         logger.error(f"Dashboard data failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.get("/api/automation/status")
# async def get_automation_status(current_user: dict = Depends(get_current_user)):
#     """Get automation status across all platforms"""
#     try:
#         user_id = current_user["id"]
        
#         status = {
#             "success": True,
#             "user_id": user_id,
#             "platforms": {}
#         }
        
#         # YouTube status
#         if youtube_scheduler:
#             youtube_status = await youtube_scheduler.get_automation_status(user_id)
#             status["platforms"]["youtube"] = youtube_status
        
#         # WhatsApp status
#         if whatsapp_scheduler:
#             whatsapp_status = await whatsapp_scheduler.get_automation_status(user_id)
#             status["platforms"]["whatsapp"] = whatsapp_status
        
#         return status
        
#     except Exception as e:
#         logger.error(f"Automation status failed: {e}")
#         return {"success": False, "error": str(e)}

# # System information endpoints
# @app.get("/api/system/info")
# async def get_system_info():
#     """Get system information"""
#     return {
#         "success": True,
#         "system": {
#             "name": "Multi-Platform Social Media Automation",
#             "version": "2.0.0",
#             "platforms": {
#                 "youtube": {
#                     "available": youtube_connector is not None,
#                     "scheduler": youtube_scheduler is not None
#                 },
#                 "whatsapp": {
#                     "available": whatsapp_scheduler is not None,
#                     "webhook": webhook_handler is not None
#                 },
#                 "instagram": {"available": False},
#                 "facebook": {"available": False}
#             },
#             "services": {
#                 "ai": {
#                     "available": ai_service is not None,
#                     "real": not isinstance(ai_service, MockAIService),
#                     "type": type(ai_service).__name__
#                 },
#                 "database": {
#                     "available": database_manager is not None,
#                     "real": DATABASE_AVAILABLE and not isinstance(database_manager, MockDatabase),
#                     "type": type(database_manager).__name__
#                 }
#             }
#         },
#         "timestamp": datetime.now().isoformat()
#     }



# @app.post("/api/youtube/oauth-url")
# async def youtube_oauth_url(request: YouTubeOAuthRequest):
#     """Generate YouTube OAuth URL"""
#     try:
#         if not youtube_connector:
#             raise HTTPException(status_code=503, detail="YouTube service not available")
        
#         # Use frontend domain as redirect URI if not provided
#         redirect_uri = request.redirect_uri
#         if not redirect_uri:
#             frontend_url = os.getenv("FRONTEND_URL", "https://frontend-agentic.onrender.com")
#             redirect_uri = f"{frontend_url}/youtube"
        
#         result = youtube_connector.generate_oauth_url(
#             state=request.state,
#             redirect_uri=redirect_uri
#         )
        
#         if result["success"]:
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube OAuth URL generation failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/youtube/oauth-callback")
# async def youtube_oauth_callback(request: YouTubeOAuthCallback):
#     """Handle YouTube OAuth callback and store tokens"""
#     try:
#         if not youtube_connector:
#             raise HTTPException(status_code=503, detail="YouTube service not available")
        
#         # Exchange code for tokens
#         redirect_uri = request.redirect_uri
#         if not redirect_uri:
#             frontend_url = os.getenv("FRONTEND_URL", "https://frontend-agentic.onrender.com")
#             redirect_uri = f"{frontend_url}/youtube"
            
#         token_result = await youtube_connector.exchange_code_for_token(
#             code=request.code,
#             redirect_uri=redirect_uri
#         )
        
#         if not token_result["success"]:
#             raise HTTPException(status_code=400, detail=token_result["error"])
        
#         # Store YouTube tokens in database for user
#         user_id = request.user_id
        
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
        
#         # Store in database
#         try:
#             # Update user document with YouTube credentials
#             users_collection = database_manager.db["users"]
#             await users_collection.update_one(
#                 {"_id": user_id},
#                 {
#                     "$set": {
#                         "youtube_credentials": youtube_credentials,
#                         "youtube_connected": True,
#                         "youtube_connected_at": datetime.now()
#                     }
#                 }
#             )
#         except Exception as db_error:
#             logger.error(f"Database error storing YouTube credentials: {db_error}")
        
#         logger.info(f"YouTube OAuth successful for user {user_id}")
        
#         return {
#             "success": True,
#             "message": "YouTube connected successfully",
#             "channel_info": token_result["channel_info"]
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube OAuth callback failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/youtube/status/{user_id}")
# async def youtube_status(user_id: str):
#     """Get YouTube connection and automation status"""
#     try:
#         # Check if user has YouTube credentials stored
#         youtube_connected = False
#         channel_info = None
#         youtube_credentials = None
        
#         try:
#             users_collection = database_manager.db["users"]
#             user = await users_collection.find_one({"_id": user_id})
            
#             if user and user.get("youtube_credentials"):
#                 youtube_connected = True
#                 youtube_credentials = user["youtube_credentials"]
#                 channel_info = youtube_credentials.get("channel_info")
#         except Exception as db_error:
#             logger.error(f"Database error fetching YouTube status: {db_error}")
        
#         # Get automation status if scheduler is available
#         automation_status = {}
#         if youtube_scheduler:
#             automation_status = await youtube_scheduler.get_automation_status(user_id)
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "youtube_connected": youtube_connected,
#             "channel_info": channel_info,
#             "youtube_automation": automation_status.get("youtube_automation", {
#                 "enabled": False,
#                 "config": None,
#                 "stats": {
#                     "total_uploads": 0,
#                     "successful_uploads": 0,
#                     "failed_uploads": 0
#                 }
#             })
#         }
        
#     except Exception as e:
#         logger.error(f"YouTube status check failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/youtube/setup-automation")
# async def youtube_setup_automation(request: YouTubeSetupRequest):
#     """Setup YouTube automation configuration"""
#     try:
#         if not youtube_scheduler:
#             raise HTTPException(status_code=503, detail="YouTube scheduler not available")
        
#         user_id = request.user_id
        
#         # Check if user has YouTube connected
#         try:
#             users_collection = database_manager.db["users"]
#             user = await users_collection.find_one({"_id": user_id})
            
#             if not user or not user.get("youtube_credentials"):
#                 raise HTTPException(status_code=400, detail="YouTube not connected")
#         except Exception as db_error:
#             logger.error(f"Database error checking YouTube connection: {db_error}")
#             raise HTTPException(status_code=500, detail="Database error")
        
#         result = await youtube_scheduler.setup_youtube_automation(user_id, request.config)
        
#         if result["success"]:
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube automation setup failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/youtube/upload")
# async def youtube_upload_video(request: YouTubeUploadRequest):
#     """Upload video to YouTube"""
#     try:
#         if not youtube_scheduler:
#             raise HTTPException(status_code=503, detail="YouTube service not available")
        
#         user_id = request.user_id
        
#         # Get user's YouTube credentials
#         try:
#             users_collection = database_manager.db["users"]
#             user = await users_collection.find_one({"_id": user_id})
            
#             if not user or not user.get("youtube_credentials"):
#                 raise HTTPException(status_code=400, detail="YouTube not connected")
                
#             credentials = user["youtube_credentials"]
#         except Exception as db_error:
#             logger.error(f"Database error fetching YouTube credentials: {db_error}")
#             raise HTTPException(status_code=500, detail="Database error")
        
#         # Upload video
#         result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             credentials_data=credentials,
#             content_type=request.content_type,
#             title=request.title,
#             description=request.description,
#             video_url=request.video_url
#         )
        
#         if result["success"]:
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube upload failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/youtube/analytics/{user_id}")
# async def youtube_analytics(user_id: str, days: int = 30):
#     """Get YouTube channel analytics"""
#     try:
#         if not youtube_connector:
#             raise HTTPException(status_code=503, detail="YouTube service not available")
        
#         # Get user's YouTube credentials
#         try:
#             users_collection = database_manager.db["users"]
#             user = await users_collection.find_one({"_id": user_id})
            
#             if not user or not user.get("youtube_credentials"):
#                 raise HTTPException(status_code=400, detail="YouTube not connected")
                
#             credentials = user["youtube_credentials"]
#         except Exception as db_error:
#             logger.error(f"Database error fetching YouTube credentials: {db_error}")
#             raise HTTPException(status_code=500, detail="Database error")
        
#         # Get analytics
#         result = await youtube_connector.get_channel_analytics(credentials, days)
        
#         if result["success"]:
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except Exception as e:
#         logger.error(f"YouTube analytics failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/ai/generate-youtube-content")
# async def generate_youtube_content(request: YouTubeContentRequest):
#     """Generate YouTube content using AI"""
#     try:
#         # Generate content based on request parameters
#         if hasattr(ai_service, 'generate_youtube_content'):
#             result = await ai_service.generate_youtube_content(
#                 content_type=request.content_type,
#                 topic=request.topic,
#                 target_audience=request.target_audience,
#                 duration_seconds=60 if request.content_type == "shorts" else 300,
#                 style="engaging"
#             )
#         else:
#             # Fallback mock content generation
#             result = {
#                 "success": True,
#                 "title": f"AI Generated {request.content_type.title()} - {request.topic}",
#                 "description": f"This is an AI-generated {request.content_type} about {request.topic} for {request.target_audience} audience. Perfect for engaging your YouTube audience!",
#                 "tags": ["AI", "generated", request.content_type, request.topic, request.target_audience],
#                 "thumbnail_suggestions": [
#                     "Bold text with bright colors",
#                     "Emotional expression face",
#                     "Question mark or arrow graphics"
#                 ]
#             }
        
#         return result
        
#     except Exception as e:
#         logger.error(f"YouTube content generation failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# # Add CORS middleware configuration for YouTube routes (if not already present)





# # Application startup
# if __name__ == "__main__":
#     PORT = int(os.getenv("PORT", 10000))
#     print("🚀 Starting Multi-Platform Social Media Automation System...")
#     uvicorn.run(
#         "main2:app",
#         host="0.0.0.0",
#         port=PORT,
#         reload=False,
#         log_level="info"
#     )