"""
YouTube Automation Module - Complete YouTube Shorts & Video Automation
Multi-user support with OAuth, content generation, and scheduling
Robust MongoDB Atlas integration for token storage
"""

import os
import asyncio
import logging
import json
import base64
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
    
    async def upload_video(
        self,
        credentials_data: Dict,
        video_file_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public",
        thumbnail_data: str = None
    ) -> Dict[str, Any]:
        """Upload video to YouTube"""
        try:
            logger.info(f"Starting video upload: {title}")
            
            # Reconstruct credentials
            credentials = Credentials(
                token=credentials_data.get('access_token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=credentials_data.get('scopes')
            )
            
            # Refresh if needed
            if credentials.expired:
                logger.info("Refreshing expired credentials")
                credentials.refresh(Request())
            
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Prepare video metadata
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
            
            # Check if it's a YouTube Short (< 60 seconds)
            if self._is_youtube_short(video_file_path):
                body['snippet']['title'] = f"{title} #Shorts"
                logger.info("Detected YouTube Short format")
            
            # Upload video
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
                            
                            logger.info(f"YouTube upload successful: {video_url}")
                            if thumbnail_data:
                                try:
                                    logger.info(f"🎨 Setting custom thumbnail for video: {video_id}")
                                    if thumbnail_data.startswith('data:image'):
                                        base64_data = thumbnail_data.split(',')[1]
                                        thumbnail_bytes = base64.b64decode(base64_data)
                                        temp_thumb = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                                        temp_thumb.write(thumbnail_bytes)
                                        temp_thumb.close()


                                        youtube.thumbnails().set(
                                            videoId=video_id,
                                            media_body=temp_thumb.name
                                            ).execute()
                                        os.unlink(temp_thumb.name)
                                        logger.info(f"✅ Custom thumbnail set successfully for video: {video_id}")

                                    else:
                                        logger.warning("⚠️ Invalid thumbnail data format")
                                except Exception as e:
                                             logger.error(f"❌ Thumbnail upload failed: {str(e)}")
                            

                                            









                            


                            

                            return {
                                "success": True,
                                "video_id": video_id,
                                "video_url": video_url,
                                "title": title,
                                "privacy_status": privacy_status
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
            return {"success": False, "error": str(e)}
    
    def _is_youtube_short(self, video_file_path: str) -> bool:
        """Check if video is eligible for YouTube Shorts (< 60 seconds)"""
        try:
            file_size = os.path.getsize(video_file_path)
            return file_size < 50 * 1024 * 1024  # Less than 50MB
        except:
            return False
        



    
    async def get_channel_analytics(self, credentials_data: Dict, days: int = 30) -> Dict[str, Any]:
        """Get YouTube channel analytics"""
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
        


        # ➜ ADD THIS METHOD AFTER: return {"success": False, "error": str(e)}

    async def create_community_post(
        self,
        credentials_data: Dict,
        post_data: Dict
    ) -> Dict[str, Any]:
        """Create YouTube community post"""
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

    # ➜ YOUR EXISTING METHODS CONTINUE HERE
        





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
    
    async def setup_youtube_automation(self, user_id: str, config_data: Dict) -> Dict[str, Any]:
        """Setup YouTube automation for user"""
        try:
            # Create config object
            config = YouTubeConfig(user_id=user_id, **config_data)
            
            # Store configuration in memory
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
            
            # Save to database
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
        thumbnail_url: str = None
    ) -> Dict[str, Any]:
        """Generate and upload YouTube content"""
        try:
            # Generate content using AI if not provided

            
            if not title or not description:
                ai_content = await self._generate_video_content(user_id, content_type)
                if not ai_content.get("success"):
                    return ai_content
                
                title = title or ai_content.get("title")
                description = description or ai_content.get("description")
                tags = ai_content.get("tags", [])
            else:
                tags = []
            
            # Handle video upload if video_url is provided
            if video_url:
                # Download video temporarily
                temp_video_path = await self._download_video_temporarily(video_url)
                
                if not temp_video_path:
                    return {
                        "success": False,
                        "error": "Failed to download video"
                    }
                
                # Upload to YouTube
                upload_result = await self.youtube_connector.upload_video(
                    credentials_data=credentials_data,
                    video_file_path=temp_video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    privacy_status="public",
                    thumbnail_data=thumbnail_url
                )
                
                # Clean up temp file
                try:
                    os.unlink(temp_video_path)
                except:
                    pass
                
                # Update statistics
                if user_id in self.active_configs:
                    config = self.active_configs[user_id].get("youtube_automation", {})
                    if upload_result.get("success"):
                        config["successful_uploads"] = config.get("successful_uploads", 0) + 1
                    else:
                        config["failed_uploads"] = config.get("failed_uploads", 0) + 1
                    config["total_uploads"] = config.get("total_uploads", 0) + 1
                
                return upload_result
            else:
                return {
                    "success": False,
                    "error": "Video URL required for upload",
                    "message": "Please provide a video URL or file to upload"
                }
                
        except Exception as e:
            logger.error(f"YouTube content generation/upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_video_content(self, user_id: str, content_type: str) -> Dict[str, Any]:
        """Generate video title, description, and tags using AI"""
        try:
            if self.ai_service and hasattr(self.ai_service, 'generate_youtube_content'):
                content_result = await self.ai_service.generate_youtube_content(
                    content_type=content_type,
                    topic="general",
                    target_audience="general",
                    duration_seconds=60 if content_type == "shorts" else 300,
                    style="engaging"
                )
            else:
                # Fallback content generation
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
        """Download video to temporary file for uploading"""
        try:
            async with httpx.AsyncClient(timeout=30.0,follow_redirects=True) as client:
                response = await client.get(video_url)
                
                if response.status_code == 200:
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix='.mp4'
                    )
                    
                    temp_file.write(response.content)
                    temp_file.close()
                    
                    logger.info(f"Video downloaded temporarily: {temp_file.name}")
                    return temp_file.name
                else:
                    logger.error(f"Download failed with status: {response.status_code}")

                    
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
            
            if config_obj and hasattr(config_obj, '__dict__'):
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

# Global instances
youtube_database = None
youtube_connector = None
youtube_scheduler = None

def get_youtube_database() -> YouTubeDatabase:
    """Get global YouTube database instance"""
    global youtube_database
    if not youtube_database:
        youtube_database = YouTubeDatabase()
    return youtube_database






async def initialize_youtube_service(database_manager=None, ai_service=None) -> bool:
    """Initialize YouTube service with required dependencies"""
    global youtube_connector, youtube_scheduler, youtube_database
    
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
        
        logger.info("YouTube service initialized successfully")
        logger.info(f"OAuth redirect URI: {redirect_uri}")
        return True
        
    except Exception as e:
        logger.error(f"YouTube service initialization failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False








# Export functions for main app
def get_youtube_connector():
    """Get YouTube connector instance"""
    return youtube_connector

def get_youtube_scheduler():
    """Get YouTube scheduler instance"""
    return youtube_scheduler