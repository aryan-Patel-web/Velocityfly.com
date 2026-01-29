"""
YouTube Automation Module - Complete YouTube Shorts & Video Automation
Multi-user support with OAuth, content generation, and scheduling
Robust MongoDB Atlas integration for token storage

FEATURES:
- OAuth2 authentication with Google
- Video upload with custom thumbnail support
- YouTube Shorts detection (under 60 seconds)
- Channel analytics
- Community posts
- Automated content scheduling
"""

import os
import asyncio
import logging
import json
import base64
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import httpx
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import tempfile
import motor.motor_asyncio
from pymongo.errors import DuplicateKeyError, ConnectionFailure

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class YouTubeDatabase:
    """MongoDB Atlas database manager for YouTube authentication"""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.users_collection = None
        self.credentials_collection = None
        self.configs_collection = None
        self.connected = False
        
        # MongoDB connection string
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.database_name = os.getenv("MONGODB_DATABASE", "youtube_automation")
        
        if not self.mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is required")
        
        logger.info(f"YouTube Database initialized for: {self.database_name}")
    
    async def connect(self) -> bool:
        """Connect to MongoDB Atlas"""
        try:
            if self.connected:
                return True
                
            logger.info("Connecting to MongoDB Atlas...")
            
            # Create MongoDB client
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                maxPoolSize=10,
                retryWrites=True
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Set up database and collections
            self.database = self.client[self.database_name]
            self.users_collection = self.database.users
            self.credentials_collection = self.database.youtube_credentials
            self.configs_collection = self.database.automation_configs
            
            # Create indexes for better performance
            await self.users_collection.create_index("email", unique=True)
            await self.credentials_collection.create_index("user_id", unique=True)
            await self.configs_collection.create_index("user_id")
            
            self.connected = True
            logger.info("Successfully connected to MongoDB Atlas")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.connected = False
            return False
    
    async def create_user(self, user_data: Dict) -> bool:
        """Create a new user"""
        try:
            user_data['created_at'] = datetime.now()
            user_data['platforms_connected'] = []
            user_data['automation_enabled'] = False
            
            await self.users_collection.insert_one(user_data)
            logger.info(f"User created successfully: {user_data['email']}")
            return True
            
        except DuplicateKeyError:
            logger.warning(f"User already exists: {user_data['email']}")
            return False
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            user = await self.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def store_youtube_credentials(self, user_id: str, credentials: Dict) -> bool:
        """Store YouTube OAuth credentials for a user"""
        try:
            # Prepare credentials document
            cred_doc = {
                "user_id": user_id,
                "platform": "youtube",
                "access_token": credentials.get("access_token"),
                "refresh_token": credentials.get("refresh_token"),
                "token_uri": credentials.get("token_uri"),
                "client_id": credentials.get("client_id"),
                "client_secret": credentials.get("client_secret"),
                "scopes": credentials.get("scopes"),
                "expires_at": credentials.get("expires_at"),
                "channel_info": credentials.get("channel_info"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Upsert credentials (update if exists, insert if not)
            await self.credentials_collection.replace_one(
                {"user_id": user_id, "platform": "youtube"},
                cred_doc,
                upsert=True
            )
            
            # Update user's connected platforms
            await self.users_collection.update_one(
                {"_id": user_id},
                {
                    "$addToSet": {"platforms_connected": "youtube"},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            
            logger.info(f"YouTube credentials stored for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store YouTube credentials: {e}")
            return False
    
    async def get_youtube_credentials(self, user_id: str) -> Optional[Dict]:
        """Get YouTube credentials for a user"""
        try:
            credentials = await self.credentials_collection.find_one({
                "user_id": user_id,
                "platform": "youtube"
            })
            
            if credentials:
                # Check if token is expired
                expires_at = credentials.get("expires_at")
                if expires_at and isinstance(expires_at, datetime):
                    if datetime.now() >= expires_at:
                        # Token is expired, try to refresh
                        refreshed = await self._refresh_youtube_token(user_id, credentials)
                        if refreshed:
                            # Get updated credentials
                            credentials = await self.credentials_collection.find_one({
                                "user_id": user_id,
                                "platform": "youtube"
                            })
                
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to get YouTube credentials: {e}")
            return None
    
    async def _refresh_youtube_token(self, user_id: str, credentials: Dict) -> bool:
        """Refresh expired YouTube token"""
        try:
            logger.info(f"Refreshing YouTube token for user: {user_id}")
            
            refresh_token = credentials.get("refresh_token")
            if not refresh_token:
                logger.error("No refresh token available")
                return False
            
            # Create credentials object
            creds = Credentials(
                token=credentials.get("access_token"),
                refresh_token=refresh_token,
                token_uri=credentials.get("token_uri"),
                client_id=credentials.get("client_id"),
                client_secret=credentials.get("client_secret")
            )
            
            # Refresh the token
            creds.refresh(Request())
            
            # Update database with new token
            await self.credentials_collection.update_one(
                {"user_id": user_id, "platform": "youtube"},
                {
                    "$set": {
                        "access_token": creds.token,
                        "expires_at": datetime.now() + timedelta(seconds=3600),
                        "updated_at": datetime.now()
                    }
                }
            )
            
            logger.info(f"YouTube token refreshed successfully for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh YouTube token: {e}")
            return False
    
    async def store_automation_config(self, user_id: str, config_type: str, config_data: Dict) -> bool:
        """Store automation configuration"""
        try:
            config_doc = {
                "user_id": user_id,
                "config_type": config_type,
                "config_data": config_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "enabled": True
            }
            
            await self.configs_collection.replace_one(
                {"user_id": user_id, "config_type": config_type},
                config_doc,
                upsert=True
            )
            
            logger.info(f"Automation config stored: {config_type} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store automation config: {e}")
            return False
    
    async def get_automation_config(self, user_id: str, config_type: str) -> Optional[Dict]:
        """Get automation configuration"""
        try:
            config = await self.configs_collection.find_one({
                "user_id": user_id,
                "config_type": config_type
            })
            return config
        except Exception as e:
            logger.error(f"Failed to get automation config: {e}")
            return None
    
    async def health_check(self) -> Dict[str, str]:
        """Check database health"""
        try:
            if not self.connected:
                return {"status": "disconnected"}
            
            # Test with a simple ping
            await self.client.admin.command('ping')
            return {"status": "connected"}
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Database connection closed")

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class YouTubeConfig:
    """Configuration for YouTube automation"""
    user_id: str
    channel_name: str = ""
    content_type: str = "shorts"  # shorts, videos, both
    upload_schedule: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    auto_generate_titles: bool = True
    auto_generate_descriptions: bool = True
    auto_add_tags: bool = True
    privacy_status: str = "public"  # private, unlisted, public
    shorts_per_day: int = 3
    videos_per_week: int = 2

# ============================================================================
# OAUTH CONNECTOR
# ============================================================================

class YouTubeOAuthConnector:
    """YouTube OAuth and API connector"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
        logger.info("YouTube OAuth Connector initialized")
    
    # ------------------------------------------------------------------------
    # OAUTH METHODS
    # ------------------------------------------------------------------------
    
    def generate_oauth_url(self, state: str = None, redirect_uri: str = None) -> Dict[str, str]:
        """Generate OAuth URL for YouTube authorization"""
        try:
            final_redirect_uri = redirect_uri or self.redirect_uri
            
            logger.info(f"Generating OAuth URL with redirect: {final_redirect_uri}")
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [final_redirect_uri]
                    }
                },
                scopes=self.scopes,
                state=state
            )
            flow.redirect_uri = final_redirect_uri
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            logger.info("OAuth URL generated successfully")
            return {
                "success": True,
                "authorization_url": authorization_url,
                "state": state
            }
            
        except Exception as e:
            logger.error(f"YouTube OAuth URL generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            final_redirect_uri = redirect_uri or self.redirect_uri
            
            logger.info(f"Exchanging code for token with redirect: {final_redirect_uri}")
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [final_redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = final_redirect_uri
            
            # Exchange code for token
            flow.fetch_token(code=code)
            
            # Get user info and channel information
            credentials = flow.credentials
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Get channel information
            channels_response = youtube.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                return {
                    "success": False,
                    "error": "No YouTube channel found for this account"
                }
            
            channel_info = channels_response['items'][0]
            
            logger.info("Token exchange successful")
            return {
                "success": True,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "expires_in": 3600,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "channel_info": {
                    "channel_id": channel_info['id'],
                    "channel_name": channel_info['snippet']['title'],
                    "subscriber_count": channel_info['statistics'].get('subscriberCount', '0'),
                    "video_count": channel_info['statistics'].get('videoCount', '0'),
                    "view_count": channel_info['statistics'].get('viewCount', '0')
                }
            }
            
        except Exception as e:
            logger.error(f"YouTube token exchange failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ------------------------------------------------------------------------
    # VIDEO UPLOAD METHODS
    # ------------------------------------------------------------------------
    
    # async def upload_video(
    async def upload_video(
        self,
        credentials_data: Dict,
        video_file_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category_id: str = "22",
        privacy_status: str = "public",
        thumbnail_data: str = None
    ) -> Dict[str, Any]:
        """Upload video to YouTube with optional thumbnail"""
        try:
            # ===== VALIDATE TITLE =====
            if not title or not title.strip():
                return {
                    "success": False,
                    "error": "Title is required and cannot be empty"
                }
            
            title = title.strip()
            logger.info(f"Starting video upload: {title}")
            
            # ===== RECONSTRUCT CREDENTIALS =====
            credentials = Credentials(
                token=credentials_data.get('access_token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=credentials_data.get('scopes')
            )
            
            if credentials.expired:
                logger.info("Refreshing expired credentials")
                credentials.refresh(Request())
            
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # ===== CHECK IF YOUTUBE SHORT & ADD TAG BEFORE TRUNCATING =====
            is_short = self._is_youtube_short(video_file_path)
            if is_short:
                if '#Shorts' not in title and '#shorts' not in title.lower():
                    title = f"{title} #Shorts"
                logger.info("Detected YouTube Short format")
            
            # ===== TRUNCATE TITLE AFTER ADDING #SHORTS =====
            if len(title) > 100:
                logger.warning(f"Title too long ({len(title)} chars), truncating to 100")
                title = title[:97] + "..."
            
            logger.info(f"Final title: '{title}' ({len(title)} chars)")
            
            # ===== PREPARE VIDEO METADATA =====
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # ===== UPLOAD VIDEO =====
            media = MediaFileUpload(
                video_file_path,
                chunksize=-1,
                resumable=True
            )
            
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            retry = 0
            
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    
                    if response is not None:
                        if 'id' in response:
                            video_id = response['id']
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            logger.info(f"✅ Video uploaded successfully: {video_url}")
                            
                            # ===== UPLOAD THUMBNAIL IF PROVIDED =====
                            thumbnail_success = False
                            
                            if thumbnail_data:
                                logger.info(f"🔍 THUMBNAIL DEBUG - Data length: {len(thumbnail_data)}")
                                thumbnail_success = await self._upload_thumbnail(
                                    youtube,
                                    video_id,
                                    thumbnail_data
                                )
                                logger.info(f"📊 Thumbnail upload result: {thumbnail_success}")
                            else:
                                logger.warning("⚠️ No thumbnail data provided")
                            
                            return {
                                "success": True,
                                "video_id": video_id,
                                "video_url": video_url,
                                "title": title,
                                "privacy_status": privacy_status,
                                "thumbnail_uploaded": thumbnail_success
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Upload failed: {response}"
                            }
                
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        retry += 1
                        if retry > 5:
                            return {
                                "success": False,
                                "error": f"Upload failed after retries: {e}"
                            }
                        await asyncio.sleep(2 ** retry)
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP error: {e}"
                        }
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}













    # async def _upload_thumbnail(
    # async def _upload_thumbnail(
    async def _upload_thumbnail(
        self,
        youtube,
        video_id: str,
        thumbnail_data: str
    ) -> bool:
        """
        Upload custom thumbnail to YouTube video
        
        Args:
            youtube: Authenticated YouTube API client
            video_id: YouTube video ID
            thumbnail_data: Base64 encoded image (data:image/jpeg;base64,...)
            
        Returns:
            bool: True if successful, False otherwise
        """
        temp_thumb_path = None
        try:
            logger.info(f"🎨 Setting custom thumbnail for video: {video_id}")
            
            # Validate thumbnail data format
            if not thumbnail_data or not isinstance(thumbnail_data, str):
                logger.warning("⚠️ Invalid thumbnail data - not a string")
                return False
            
            if not thumbnail_data.startswith('data:image'):
                logger.error(f"⚠️ Invalid thumbnail format. Starts with: {thumbnail_data[:30]}")
                return False
            
            # Extract base64 data (remove "data:image/jpeg;base64," prefix)
            try:
                base64_data = thumbnail_data.split(',')[1]
                thumbnail_bytes = base64.b64decode(base64_data)
                logger.info(f"📦 Thumbnail decoded: {len(thumbnail_bytes)} bytes")
            except Exception as decode_error:
                logger.error(f"❌ Base64 decode failed: {decode_error}")
                return False
            
            # Validate image size (YouTube requires 2MB max)
            if len(thumbnail_bytes) > 2 * 1024 * 1024:
                logger.error(f"❌ Thumbnail too large: {len(thumbnail_bytes)} bytes (max 2MB)")
                return False
            
            # Create temporary file
            temp_thumb = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_thumb.write(thumbnail_bytes)
            temp_thumb.close()
            temp_thumb_path = temp_thumb.name
            logger.info(f"💾 Temp thumbnail saved: {temp_thumb_path}")
            
            # Upload thumbnail to YouTube API
            try:
                response = youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=temp_thumb_path
                ).execute()
                
                logger.info(f"✅ Thumbnail API response: {response}")
                logger.info(f"✅ Custom thumbnail set successfully for video: {video_id}")
                return True
                
            except HttpError as http_err:
                logger.error(f"❌ YouTube API error: {http_err.resp.status} - {http_err.content}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Thumbnail upload failed: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
            
        finally:
            # Clean up temporary file
            if temp_thumb_path:
                try:
                    os.unlink(temp_thumb_path)
                    logger.info(f"🗑️ Temp file deleted: {temp_thumb_path}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Failed to delete temp file: {cleanup_error}")

        




        
    
    def _is_youtube_short(self, video_file_path: str) -> bool:
        """
        Check if video is eligible for YouTube Shorts (< 60 seconds)
        
        Args:
            video_file_path: Path to video file
            
        Returns:
            bool: True if video is under 60 seconds
        """
        try:
            # Try to get duration using ffprobe
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                logger.info(f"Video duration: {duration}s")
                return duration < 60
            
        except Exception as e:
            logger.warning(f"Could not determine video duration using ffprobe: {e}")
        
        # Fallback: check file size (rough heuristic)
        try:
            file_size = os.path.getsize(video_file_path)
            # Shorts are typically < 10MB for 60 seconds
            is_short = file_size < 10 * 1024 * 1024
            logger.info(f"Using file size fallback: {file_size} bytes, is_short={is_short}")
            return is_short
        except Exception as e:
            logger.error(f"Could not determine file size: {e}")
            return False
    
    # ------------------------------------------------------------------------
    # ANALYTICS METHODS
    # ------------------------------------------------------------------------
    
    async def get_channel_analytics(
        self,
        credentials_data: Dict,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get YouTube channel analytics
        
        Args:
            credentials_data: User's OAuth credentials
            days: Number of days to analyze
            
        Returns:
            Dict with channel statistics and recent videos
        """
        try:
            credentials = Credentials(
                token=credentials_data.get('access_token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=credentials_data.get('scopes')
            )
            
            if credentials.expired:
                credentials.refresh(Request())
            
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Get recent videos
            videos_response = youtube.search().list(
                part='snippet',
                forMine=True,
                type='video',
                order='date',
                maxResults=10
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video_id = item['id']['videoId']
                
                # Get video statistics
                stats_response = youtube.videos().list(
                    part='statistics',
                    id=video_id
                ).execute()
                
                stats = stats_response['items'][0]['statistics'] if stats_response.get('items') else {}
                
                videos.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': stats.get('viewCount', '0'),
                    'like_count': stats.get('likeCount', '0'),
                    'comment_count': stats.get('commentCount', '0')
                })
            
            # Get channel statistics
            channels_response = youtube.channels().list(
                part='statistics',
                mine=True
            ).execute()
            
            channel_stats = {}
            if channels_response.get('items'):
                channel_stats = channels_response['items'][0]['statistics']
            
            return {
                "success": True,
                "channel_statistics": channel_stats,
                "recent_videos": videos,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"YouTube analytics failed: {e}")
            return {"success": False, "error": str(e)}
        

    async def get_authenticated_service(self, user_id: str):
        """Get authenticated YouTube service for API calls"""
        try:
            # This method should be in YTdatabase, not here
            # But we'll create a bridge method
            from YTdatabase import get_youtube_database
            
            database_manager = get_youtube_database()
            credentials = await database_manager.get_youtube_credentials(user_id)
            
            if not credentials:
                logger.error(f"No credentials found for user {user_id}")
                return None
            
            # Build credentials object
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            
            creds = Credentials(
                token=credentials["access_token"],
                refresh_token=credentials["refresh_token"],
                token_uri=credentials["token_uri"],
                client_id=credentials["client_id"],
                client_secret=credentials["client_secret"],
                scopes=credentials["scopes"]
            )
            
            # Check if token needs refresh
            if creds.expired:
                logger.info(f"Refreshing token for user {user_id}")
                creds.refresh(Request())
                
                # Update token in database
                await database_manager.refresh_youtube_token(
                    user_id, 
                    creds.token, 
                    creds.expiry
                )
            
            # Build YouTube service
            youtube_service = build('youtube', 'v3', credentials=creds)
            logger.info(f"YouTube service authenticated for user {user_id}")
            return youtube_service
            
        except Exception as e:
            logger.error(f"Failed to authenticate YouTube service: {e}")
            return None
    
    # ------------------------------------------------------------------------
    # COMMUNITY POST METHODS
    # ------------------------------------------------------------------------
    
    async def create_community_post(
        self,
        credentials_data: Dict,
        post_data: Dict
    ) -> Dict[str, Any]:
        """
        Create YouTube community post
        
        Args:
            credentials_data: User's OAuth credentials
            post_data: Dict containing:
                - content: Post text
                - post_type: text, poll, quiz, image
                - options: List of poll/quiz options
                - correct_answer: Correct answer index for quiz
                - image_url: Image URL for image posts
                
        Returns:
            Dict with success status and post URL
        """
        try:
            logger.info(f"Creating community post: {post_data.get('post_type', 'text')}")
            
            credentials = Credentials(
                token=credentials_data.get('access_token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=credentials_data.get('scopes')
            )
            
            if credentials.expired:
                credentials.refresh(Request())
            
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Prepare community post body
            body = {
                'snippet': {
                    'text': post_data.get('content', '')
                }
            }
            
            # Add poll/quiz data if present
            if post_data.get('options') and len(post_data['options']) >= 2:
                if post_data.get('post_type') == 'quiz':
                    body['snippet']['poll'] = {
                        'question': post_data.get('content', ''),
                        'choices': [{'text': opt} for opt in post_data['options'][:4]],
                        'correctAnswer': int(post_data.get('correct_answer', 0))
                    }
                else:
                    body['snippet']['poll'] = {
                        'question': post_data.get('content', ''),
                        'choices': [{'text': opt} for opt in post_data['options'][:4]]
                    }
            
            # Add image if present
            if post_data.get('image_url'):
                body['snippet']['images'] = [{
                    'url': post_data['image_url']
                }]
            
            # Create the community post
            response = youtube.communityPosts().insert(
                part='snippet',
                body=body
            ).execute()
            
            if response.get('id'):
                return {
                    "success": True,
                    "post_id": response['id'],
                    "post_url": f"https://www.youtube.com/post/{response['id']}",
                    "status": "published"
                }
            else:
                return {"success": False, "error": "Post creation failed"}
                
        except Exception as e:
            logger.error(f"Community post creation failed: {e}")
            return {"success": False, "error": str(e)}

# ============================================================================
# AUTOMATION SCHEDULER
# ============================================================================



# ============================================================================
# AUTOMATION SCHEDULER
# ============================================================================
# ============================================================================
# AUTOMATION SCHEDULER
# ============================================================================

class YouTubeAutomationScheduler:
    """YouTube content automation scheduler"""
    
    def __init__(self, youtube_connector, ai_service, database_manager):
        self.youtube_connector = youtube_connector
        self.ai_service = ai_service
        self.database = database_manager
        self.active_configs = {}
        self.is_running = False
        self.upload_queue = {}
        
        logger.info("YouTube Automation Scheduler initialized")
    
    async def setup_youtube_automation(
        self,
        user_id: str,
        config_data: Dict
    ) -> Dict[str, Any]:
        """Setup YouTube automation for user"""
        try:
            config = YouTubeConfig(user_id=user_id, **config_data)
            
            self.active_configs[user_id] = {
                "youtube_automation": {
                    "config": config,
                    "enabled": True,
                    "created_at": datetime.now(),
                    "total_uploads": 0,
                    "successful_uploads": 0,
                    "failed_uploads": 0
                }
            }
            
            if self.database:
                await self.database.store_automation_config(
                    user_id=user_id,
                    config_type='youtube_automation',
                    config_data=config.__dict__
                )
            
            logger.info(f"YouTube automation setup successful for user {user_id}")
            
            return {
                "success": True,
                "message": "YouTube automation enabled successfully!",
                "config": config.__dict__,
                "next_upload_time": self._get_next_upload_time(config.upload_schedule),
                "content_type": config.content_type,
                "scheduler_status": "Active"
            }
            
        except Exception as e:
            logger.error(f"YouTube automation setup failed: {e}")
            return {"success": False, "error": str(e)}
    







    
async def generate_and_upload_content(
    self,
    user_id: str,
    credentials_data: Dict,
    content_type: str = "shorts",
    title: str = None,
    description: str = None,
    video_url: str = None,
    thumbnail_url: str = None,
    thumbnail_path: str = None
) -> Dict[str, Any]:
    """Generate and upload YouTube content with thumbnail support"""

    try:
        # ==============================
        # Generate AI title/description if missing
        # ==============================
        if not title or not description:
            ai_content = await self._generate_video_content(user_id, content_type)

            if not ai_content.get("success"):
                return ai_content

            title = title or ai_content.get("title")
            description = description or ai_content.get("description")
            tags = ai_content.get("tags", [])
        else:
            tags = []

        # ==============================
        # Validate video input
        # ==============================
        if not video_url:
            return {
                "success": False,
                "error": "Video URL required",
                "message": "Provide a video URL or file to upload"
            }

        # ==============================
        # Download video temporarily
        # ==============================
        temp_video_path = await self._download_video_temporarily(video_url)

        if not temp_video_path:
            return {"success": False, "error": "Failed to download video"}

        # ==============================
        # Upload Video
        # ==============================
        upload_result = await self.youtube_connector.upload_video(
            credentials_data=credentials_data,
            video_file_path=temp_video_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status="public"
        )

        # ==============================
        # Cleanup temp file
        # ==============================
        try:
            import os
            os.unlink(temp_video_path)
        except Exception as e:
            logger.warning(f"Temp delete failed: {e}")

        # ==============================
        # Upload Thumbnail (if video upload succeeded)
        # ==============================
        if upload_result.get("success") and (thumbnail_url or thumbnail_path):
            try:
                video_id = upload_result.get("video_id")

                thumbnail_source = thumbnail_path if thumbnail_path else thumbnail_url

                success = await self.youtube_connector._upload_thumbnail(
                    credentials_data=credentials_data,
                    video_id=video_id,
                    thumbnail_input=thumbnail_source
                )

                upload_result["thumbnail_uploaded"] = bool(success)

                if success:
                    logger.info(f"✅ Thumbnail uploaded: {video_id}")
                else:
                    logger.warning("⚠️ Thumbnail upload failed")

            except Exception as thumb_err:
                logger.error(f"❌ Thumbnail upload error: {thumb_err}")
                upload_result["thumbnail_uploaded"] = False

        # ==============================
        # Update user automation stats
        # ==============================
        if user_id in self.active_configs:
            config = self.active_configs[user_id].get("youtube_automation", {})

            if upload_result.get("success"):
                config["successful_uploads"] = config.get("successful_uploads", 0) + 1
            else:
                config["failed_uploads"] = config.get("failed_uploads", 0) + 1

            config["total_uploads"] = config.get("total_uploads", 0) + 1

        return upload_result

    except Exception as e:
        logger.error(f"YouTube upload failed: {e}")
        return {"success": False, "error": str(e)}


async def _generate_video_content(
    self,
    user_id: str,
    content_type: str
) -> Dict[str, Any]:
    """Generate video title, description, and tags using AI"""

    try:
        if self.ai_service and hasattr(self.ai_service, "generate_youtube_content"):
            content_result = await self.ai_service.generate_youtube_content(
                content_type=content_type,
                topic="general",
                target_audience="general",
                duration_seconds=60 if content_type == "shorts" else 300,
                style="engaging"
            )
        else:
            content_result = {
                "success": True,
                "title": f"AI Generated {content_type.title()} Video",
                "description": f"This is an AI-generated {content_type} video for your YouTube channel.",
                "tags": ["AI", "generated", "content", content_type]
            }

        return content_result

    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        return {
            "success": False,
            "error": f"AI content generation failed: {str(e)}"
        }


async def _download_video_temporarily(self, video_url: str) -> Optional[str]:
    """
    Download video to temporary file or use local file directly
    """

    try:
        import os
        import tempfile
        import httpx

        # ==============================
        # If local file path → return directly
        # ==============================
        if video_url.startswith("/tmp/") or os.path.exists(video_url):
            logger.info(f"Using local file directly: {video_url}")
            return video_url

        # ==============================
        # Download remote video
        # ==============================
        logger.info(f"Downloading video from: {video_url}")

        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(video_url)

            if response.status_code == 200:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                )
                temp_file.write(response.content)
                temp_file.close()

                logger.info(f"Video downloaded temporarily: {temp_file.name}")
                return temp_file.name

            else:
                logger.error(f"Download failed with status: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Video download failed: {e}")
        return None


def _get_next_upload_time(self, upload_schedule: List[str]) -> str:
    """Get next scheduled upload time"""

    if not upload_schedule:
        return "No schedule set"

    try:
        current_time = datetime.now().time()

        for time_str in sorted(upload_schedule):
            upload_time = datetime.strptime(time_str, "%H:%M").time()
            if upload_time > current_time:
                return f"Today at {time_str}"

        return f"Tomorrow at {sorted(upload_schedule)[0]}"

    except Exception:
        return "Schedule error"


async def get_automation_status(self, user_id: str) -> Dict[str, Any]:
    """Get YouTube automation status for user"""

    try:
        user_config = self.active_configs.get(user_id, {})

        youtube_config = user_config.get("youtube_automation", {})
        config_obj = youtube_config.get("config")

        if config_obj and hasattr(config_obj, "__dict__"):
            config_data = config_obj.__dict__
        elif isinstance(config_obj, dict):
            config_data = config_obj
        else:
            config_data = None

        return {
            "success": True,
            "user_id": user_id,
            "youtube_automation": {
                "enabled": "youtube_automation" in user_config,
                "config": config_data,
                "stats": {
                    "total_uploads": youtube_config.get("total_uploads", 0),
                    "successful_uploads": youtube_config.get("successful_uploads", 0),
                    "failed_uploads": youtube_config.get("failed_uploads", 0)
                }
            },
            "scheduler_running": self.is_running,
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"YouTube status check failed: {e}")
        return {"success": False, "error": str(e)}



# ============================================================================
# BACKGROUND SCHEDULER
# ============================================================================


    # ============================================================================
# BACKGROUND SCHEDULER
# ============================================================================

class YouTubeBackgroundScheduler:
    """Background scheduler that checks and executes scheduled posts"""
    
    def __init__(self, database_manager, youtube_scheduler):
        self.database = database_manager
        self.youtube_scheduler = youtube_scheduler
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
        self.task = None
        logger.info("YouTubeBackgroundScheduler initialized")
    
    async def start(self):
        """Start the background scheduler loop"""
        if self.running:
            logger.warning("Background scheduler already running")
            return
        
        self.running = True
        logger.info("🚀 Background scheduler started - will check every 60 seconds")
        
        while self.running:
            try:
                current_time = datetime.now()
                logger.info(f"🔍 Checking for scheduled posts at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                await self.process_scheduled_posts()
                
                logger.debug(f"✅ Check complete - next check in {self.check_interval} seconds")
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Background scheduler error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                await asyncio.sleep(30)  # Wait 30s on error
    
    async def stop(self):
        """Stop the background scheduler"""
        self.running = False
        logger.info("Background scheduler stopped")
    
    async def process_scheduled_posts(self):
        """Check and execute posts that are due"""
        try:
            # Check database connection
            if not self.database or not hasattr(self.database, 'scheduled_posts_collection'):
                logger.error("❌ Database or collection not available")
                return
            
            due_posts = await self.database.get_due_scheduled_posts()
            
            if due_posts:
                logger.info(f"📤 Found {len(due_posts)} posts ready for execution")
                for post in due_posts:
                    await self.execute_scheduled_post(post)
            else:
                logger.debug("No posts due at this time")
                
        except Exception as e:
            logger.error(f"❌ Error processing scheduled posts: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    async def execute_scheduled_post(self, post):
        """Execute a single scheduled post"""
        try:
            post_id = post["_id"]
            user_id = post["user_id"]
            video_data = post["video_data"]
            
            logger.info(f"🎬 Executing scheduled post {post_id} for user {user_id}")
            logger.info(f"📹 Video: {video_data.get('title', 'Untitled')}")
            
            # Mark as processing
            await self.database.update_scheduled_post_status(post_id, "processing")
            
            # Get user credentials
            credentials = await self.database.get_youtube_credentials(user_id)
            if not credentials:
                raise Exception("No YouTube credentials found")
            
            # Execute upload
            result = await self.youtube_scheduler.generate_and_upload_content(
                user_id=user_id,
                credentials_data=credentials,
                content_type=video_data.get("content_type", "video"),
                title=video_data.get("title"),
                description=video_data.get("description"),
                video_url=video_data.get("video_url"),
                thumbnail_url=video_data.get("thumbnail_url")
            )
            
            if result.get("success"):
                await self.database.update_scheduled_post_status(post_id, "published")
                logger.info(f"✅ Scheduled post {post_id} published successfully")
                logger.info(f"🔗 Video URL: {result.get('video_url', 'N/A')}")
            else:
                error_msg = result.get("error", "Unknown error")
                await self.database.update_scheduled_post_status(post_id, "failed", error_msg)
                logger.error(f"❌ Scheduled post {post_id} failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ Failed to execute scheduled post: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            await self.database.update_scheduled_post_status(
                post.get("_id"), 
                "failed", 
                str(e)
            )











class AutoReplyScheduler:
    """Automated comment reply scheduler with video selection and IST timezone support"""
    
    def __init__(self, database_manager, youtube_connector, ai_service):
        self.database = database_manager
        self.youtube_connector = youtube_connector
        self.ai_service = ai_service
        self.running = False
        self.check_interval = 300  # Check every 5 minutes
        self.rate_limit_tracker = {}  # Track rate limits per user
        logger.info("AutoReplyScheduler initialized with video selection support")
    
    async def start(self):
        """Start auto-reply checking"""
        if self.running:
            logger.warning("Auto-reply scheduler already running")
            return
        
        self.running = True
        logger.info("🤖 Auto-reply scheduler started - checking every 5 minutes")
        
        while self.running:
            try:
                await self.process_auto_replies()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Auto-reply scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def stop(self):
        """Stop auto-reply scheduler"""
        self.running = False
        logger.info("Auto-reply scheduler stopped")

    async def process_auto_replies(self):
        """Check for new comments and auto-reply based on selected videos"""
        try:
            # Get users with auto-reply enabled
            configs = await self.database.get_all_automation_configs_by_type("auto_reply")
            
            if not configs:
                logger.debug("No auto-reply configs found")
                return
            
            logger.info(f"🤖 Processing auto-replies for {len(configs)} users")
            
            for config in configs:
                if config.get("enabled", False):
                    try:
                        await self.reply_to_user_comments(
                            config["user_id"], 
                            config.get("config_data", {})
                        )
                        # Small delay between users to avoid API rate limits
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Failed processing user {config['user_id']}: {e}")
                        continue
                    
        except Exception as e:
            logger.error(f"Process auto-replies failed: {e}")
    
    async def reply_to_user_comments(self, user_id: str, config: dict):
        """Auto-reply to new comments for selected videos"""
        try:
            logger.info(f"🎯 Checking comments for user: {user_id}")
            
            # Check rate limits first
            if not await self._check_rate_limit(user_id, config):
                logger.info(f"Rate limit reached for user {user_id}")
                return
            
            # Get authenticated YouTube service
            youtube_service = await self.youtube_connector.get_authenticated_service(user_id)
            if not youtube_service:
                logger.warning(f"No YouTube service for user {user_id}")
                return
            
            # Get selected videos from config
            selected_videos = config.get("selected_videos", [])
            if not selected_videos:
                logger.info(f"No selected videos for user {user_id}")
                return
            
            reply_delay = config.get("reply_delay_seconds", 30)
            logger.info(f"🔍 Checking {len(selected_videos)} selected videos for new comments")
            
            comments_processed = 0
            replies_sent = 0
            
            # Process each selected video
            for video_id in selected_videos[:10]:  # Limit to 10 videos per check
                try:
                    video_result = await self._process_video_comments(
                        youtube_service, user_id, video_id, config, reply_delay
                    )
                    
                    comments_processed += video_result.get("comments_checked", 0)
                    replies_sent += video_result.get("replies_sent", 0)
                    
                    # Stop if we've sent enough replies
                    max_replies = config.get("max_replies_per_hour", 10)
                    if replies_sent >= max_replies:
                        logger.info(f"Reached reply limit ({max_replies}) for user {user_id}")
                        break
                        
                except Exception as e:
                    logger.error(f"Failed to process video {video_id}: {e}")
                    continue
            
            # Log session results
            await self._log_auto_reply_session(user_id, {
                "videos_processed": selected_videos[:10],
                "comments_found": comments_processed,
                "replies_sent": replies_sent,
                "config_used": config
            })
            
            logger.info(f"✅ Session complete for {user_id}: {replies_sent} replies sent from {comments_processed} comments")
                    
        except Exception as e:
            logger.error(f"Auto-reply for user {user_id} failed: {e}")
    
    async def _process_video_comments(self, youtube_service, user_id: str, video_id: str, config: dict, reply_delay: int):
        """Process comments for a single video"""
        try:
            # Get comments for this video
            comments_response = youtube_service.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                order="time",
                maxResults=5
            ).execute()
            
            comments_checked = 0
            replies_sent = 0
            
            for comment_item in comments_response.get("items", []):
                comment = comment_item["snippet"]["topLevelComment"]["snippet"]
                comment_id = comment_item["id"]
                comment_text = comment["textDisplay"]
                
                comments_checked += 1
                
                # Check if comment is recent and needs reply
                if (self._is_recent_comment(comment["publishedAt"]) and 
                    not await self._already_replied_to_comment(user_id, comment_id) and
                    not self._is_spam_comment(comment_text)):
                    
                    logger.info(f"💬 New comment found: {comment_text[:50]}...")
                    
                    # Wait for configured delay (convert to IST awareness)
                    await asyncio.sleep(reply_delay)
                    
                    # Generate and post reply
                    reply_success = await self._generate_and_post_reply(
                        user_id, comment_id, comment_text, config, video_id
                    )
                    
                    if reply_success:
                        replies_sent += 1
                        # Rate limiting gap between replies
                        await asyncio.sleep(10)
                    
                    # Only one reply per video per check to avoid spam
                    break
            
            return {
                "comments_checked": comments_checked,
                "replies_sent": replies_sent
            }
                
        except Exception as e:
            logger.error(f"Failed to process video {video_id}: {e}")
            return {"comments_checked": 0, "replies_sent": 0}
    
    def _is_recent_comment(self, published_at: str, hours_back: int = 24) -> bool:
        """Check if comment is recent (within specified hours)"""
        try:
            from datetime import datetime, timedelta
            
            # Parse UTC time from YouTube API
            comment_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now(comment_time.tzinfo)
            
            # Check if within time window
            is_recent = (now - comment_time) < timedelta(hours=hours_back)
            
            if is_recent:
                # Convert to IST for logging
                ist_time = comment_time + timedelta(hours=5, minutes=30)
                logger.debug(f"Recent comment from {ist_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
            
            return is_recent
        except Exception as e:
            logger.warning(f"Failed to parse comment time: {e}")
            return True  # Default to processing if can't parse
    
    async def _already_replied_to_comment(self, user_id: str, comment_id: str) -> bool:
        """Check if we already replied to this specific comment"""
        try:
            # Check database for existing reply
            replied = await self.database.check_comment_already_replied(user_id, comment_id)
            return replied
        except Exception as e:
            logger.warning(f"Failed to check reply status: {e}")
            return False
    
    def _is_spam_comment(self, comment_text: str) -> bool:
        """Basic spam detection for comments"""
        try:
            text_lower = comment_text.lower()
            
            # Spam indicators
            spam_keywords = [
                "subscribe to my channel", "check out my channel", "follow me",
                "click here", "free money", "win cash", "telegram", "whatsapp me",
                "dm me", "bot", "scam", "hack"
            ]
            
            # Check for spam patterns
            if any(keyword in text_lower for keyword in spam_keywords):
                return True
            
            # Check for excessive repetition
            words = text_lower.split()
            if len(words) > 5:
                unique_words = set(words)
                if len(unique_words) / len(words) < 0.4:  # Less than 40% unique words
                    return True
        
            # Check for excessive special characters
            special_chars = sum(1 for char in comment_text if not char.isalnum() and char != ' ')
            if special_chars / len(comment_text) > 0.3:  # More than 30% special chars
                return True
            
            return False
            
        except Exception:
            return False  # Default to not spam if check fails
    
    async def _generate_and_post_reply(self, user_id: str, comment_id: str, comment_text: str, config: dict, video_id: str = None):
        """Generate and post auto-reply with enhanced error handling"""
        try:
            logger.info(f"🤖 Generating reply for: {comment_text[:30]}...")
            
            reply_text = None
            ai_service_used = "fallback"
            
            # Try AI generation first
            if self.ai_service and hasattr(self.ai_service, 'generate_comment_reply'):
                try:
                    reply_result = await self.ai_service.generate_comment_reply(
                        comment_text=comment_text,
                        reply_style=config.get("reply_style", "friendly"),
                        language="english",  # Auto-detect within the method
                        custom_prompt=config.get("custom_prompt", "")
                    )
                    
                    if reply_result.get("success"):
                        reply_text = reply_result["reply"]
                        ai_service_used = reply_result.get("ai_service", "ai")
                        logger.info(f"AI generated reply: {reply_text}")
                    else:
                        logger.warning(f"AI reply generation failed: {reply_result.get('error')}")
                        
                except Exception as ai_error:
                    logger.error(f"AI service error: {ai_error}")
            
            # Fallback to simple reply if AI fails
            if not reply_text:
                language = self._detect_comment_language(comment_text)
                reply_text = self._get_fallback_reply(language, config.get("reply_style", "friendly"))
                ai_service_used = "fallback"
                logger.info(f"Using fallback reply: {reply_text}")
            
            # Post reply to YouTube
            youtube_service = await self.youtube_connector.get_authenticated_service(user_id)
            if not youtube_service:
                logger.error("No YouTube service available")
                return False
            
            response = youtube_service.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": comment_id,
                        "textOriginal": reply_text
                    }
                }
            ).execute()
            
            reply_id = response.get("id")
            logger.info(f"✅ Auto-replied successfully: {reply_text}")
            
            # Log the reply to database
            await self.database.log_comment_reply(user_id, {
                "comment_id": comment_id,
                "video_id": video_id,
                "reply_id": reply_id,
                "reply_text": reply_text,
                "original_comment": comment_text,
                "reply_type": "auto",
                "ai_service_used": ai_service_used,
                "language_detected": self._detect_comment_language(comment_text)
            })
            
            return True
                    
        except Exception as e:
            logger.error(f"Generate and post reply failed: {e}")
            return False
    
    def _detect_comment_language(self, text: str) -> str:
        """Detect language of comment for appropriate reply"""
        text_lower = text.lower()
        
        # Hindi/Devanagari detection
        hindi_chars = "अआइईउऊएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
        if any(char in hindi_chars for char in text):
            return "hindi"
        
        # Hinglish detection
        hinglish_words = ["acha", "accha", "bhai", "yaar", "kya", "hai", "nahi", "bahut"]
        if any(word in text_lower for word in hinglish_words):
            return "hinglish"
        
        return "english"
    
    def _get_fallback_reply(self, language: str, style: str) -> str:
        """Get fallback reply based on language and style"""
        replies = {
            "hindi": {
                "friendly": "टिप्पणी के लिए धन्यवाद! 😊",
                "professional": "आपकी टिप्पणी के लिए धन्यवाद।",
                "casual": "Thanks yaar! 😄",
                "enthusiastic": "वाह! बहुत बढ़िया कमेंट! 🔥"
            },
            "hinglish": {
                "friendly": "Thank you for comment! Bahut accha laga 😊",
                "professional": "Thanks for your feedback!",
                "casual": "Thanks bhai! 😄",
                "enthusiastic": "Wow! Amazing comment! 🔥"
            },
            "english": {
                "friendly": "Thank you for your comment! 😊",
                "professional": "Thank you for your feedback.",
                "casual": "Thanks for watching! 😄",
                "enthusiastic": "Awesome comment! Thanks! 🔥"
            }
        }
        
        return replies.get(language, replies["english"]).get(style, replies["english"]["friendly"])
    
    async def _check_rate_limit(self, user_id: str, config: dict) -> bool:
        """Check if user has exceeded rate limits"""
        try:
            rate_info = await self.database.get_auto_reply_rate_limit(user_id, hours=1)
            return rate_info.get("can_send", True)
        except Exception as e:
            logger.warning(f"Rate limit check failed: {e}")
            return True  # Allow if check fails
    
    async def _log_auto_reply_session(self, user_id: str, session_data: dict):
        """Log auto-reply session to database"""
        try:
            await self.database.log_auto_reply_session(user_id, session_data)
        except Exception as e:
            logger.warning(f"Failed to log session: {e}")


# Add to global instances
auto_reply_scheduler = None

def get_auto_reply_scheduler():
    """Get auto-reply scheduler instance"""
    return auto_reply_scheduler



# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

youtube_database = None
youtube_connector = None
youtube_scheduler = None
youtube_background_scheduler = None
auto_reply_scheduler = None  # NEW: Background scheduler instance

def get_youtube_database() -> YouTubeDatabase:
    """Get global YouTube database instance"""
    global youtube_database
    if not youtube_database:
        youtube_database = YouTubeDatabase()
    return youtube_database

# ============================================================================
# INITIALIZATION
# ============================================================================



# async def initialize_youtube_service(

async def initialize_youtube_service(
    database_manager=None,
    ai_service=None
) -> bool:
    """
    Initialize YouTube service with required dependencies
    """
    global youtube_connector, youtube_scheduler, youtube_database, youtube_background_scheduler, auto_reply_scheduler
    
    try:
        logger.info("Initializing YouTube service...")
        
        # Check required environment variables
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET") 
        redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
        
        if not all([client_id, client_secret, redirect_uri]):
            missing = []
            if not client_id: missing.append("GOOGLE_CLIENT_ID")
            if not client_secret: missing.append("GOOGLE_CLIENT_SECRET")
            if not redirect_uri: missing.append("GOOGLE_OAUTH_REDIRECT_URI")
            
            logger.error(f"Missing required environment variables: {missing}")
            return False
        
        # Import and use the YTdatabase manager
        from YTdatabase import get_youtube_database
        
        if not database_manager:
            youtube_database = get_youtube_database()
            connected = await youtube_database.connect()
            if not connected:
                logger.error("Failed to connect to YouTube database")
                return False
            database_manager = youtube_database
        
        # Initialize YouTube connector
        youtube_connector = YouTubeOAuthConnector(client_id, client_secret, redirect_uri)
        
        # Initialize YouTube scheduler
        youtube_scheduler = YouTubeAutomationScheduler(
            youtube_connector, 
            ai_service, 
            database_manager
        )
        
        # Initialize background scheduler for video uploads
        logger.info("Initializing background scheduler...")
        youtube_background_scheduler = YouTubeBackgroundScheduler(
            database_manager,
            youtube_scheduler
        )
        
        # Start video upload scheduler in background task
        asyncio.create_task(youtube_background_scheduler.start())
        logger.info("✅ Background scheduler initialized and task created")
        
        # Initialize auto-reply scheduler for comments
        logger.info("Initializing auto-reply scheduler...")
        auto_reply_scheduler = AutoReplyScheduler(
            database_manager,
            youtube_connector, 
            ai_service
        )
        
        # Start auto-reply scheduler in background task
        asyncio.create_task(auto_reply_scheduler.start())
        logger.info("✅ Auto-reply scheduler initialized and task created")
        
        logger.info("YouTube service initialized successfully")
        logger.info(f"OAuth redirect URI: {redirect_uri}")
        return True
        
    except Exception as e:
        logger.error(f"YouTube service initialization failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

    



# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def get_youtube_connector():
    """Get YouTube connector instance"""
    return youtube_connector

def get_youtube_scheduler():
    """Get YouTube scheduler instance"""
    return youtube_scheduler