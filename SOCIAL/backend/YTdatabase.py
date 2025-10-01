"""
YouTube Database Manager - MongoDB operations for YouTube automation
Handles user credentials, automation configs, and analytics
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, ConnectionFailure

logger = logging.getLogger(__name__)

class YouTubeDatabaseManager:
    """MongoDB database manager specifically for YouTube automation"""
    
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.database_name = os.getenv("MONGODB_DATABASE", "youtube_automation")
        self.client = None
        self.db = None
        
        # Collections
        self.users_collection = None
        self.youtube_credentials_collection = None
        self.automation_configs_collection = None
        self.upload_history_collection = None
        self.analytics_collection = None
        self.scheduled_posts_collection = None
        
        logger.info("YouTube Database Manager initialized")
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            
            # Initialize collections
            self.users_collection = self.db["users"]
            self.youtube_credentials_collection = self.db["youtube_credentials"]
            self.automation_configs_collection = self.db["automation_configs"]
            self.upload_history_collection = self.db["upload_history"]
            self.analytics_collection = self.db["analytics"]
            self.scheduled_posts_collection = self.db["scheduled_posts"]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to YouTube MongoDB: {self.database_name}")
            return True
            
        except Exception as e:
            logger.error(f"YouTube MongoDB connection failed: {e}")
            return False
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            await self.users_collection.create_index("email", unique=True)
            await self.users_collection.create_index("created_at")
            await self.youtube_credentials_collection.create_index("user_id", unique=True)
            await self.youtube_credentials_collection.create_index("channel_id")
            await self.automation_configs_collection.create_index("user_id")
            await self.automation_configs_collection.create_index("config_type")
            await self.upload_history_collection.create_index("user_id")
            await self.upload_history_collection.create_index("video_id", unique=True)
            await self.upload_history_collection.create_index("upload_date")
            await self.analytics_collection.create_index("user_id")
            await self.analytics_collection.create_index("date")
            await self.scheduled_posts_collection.create_index("user_id")
            await self.scheduled_posts_collection.create_index("scheduled_for")
            await self.scheduled_posts_collection.create_index("status")
            await self.scheduled_posts_collection.create_index([
                ("user_id", 1),
                ("status", 1),
                ("scheduled_for", 1)
            ])
            
            logger.info("YouTube database indexes created")
            
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("YouTube database connection closed")

    async def log_community_post(self, user_id: str, post_data: Dict) -> bool:
        """Log community post to database"""
        try:
            post_doc = {
                "user_id": user_id,
                "platform": "youtube",
                "post_type": post_data.get("post_type", "text"),
                "content": post_data.get("content", ""),
                "image_url": post_data.get("image_url"),
                "options": post_data.get("options", []),
                "correct_answer": post_data.get("correct_answer"),
                "status": post_data.get("status", "published"),
                "scheduled_for": post_data.get("scheduled_for"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            if not hasattr(self, 'community_posts_collection'):
                self.community_posts_collection = self.db.community_posts
                await self.community_posts_collection.create_index("user_id")
            
            await self.community_posts_collection.insert_one(post_doc)
            logger.info(f"Community post logged for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log community post: {e}")
            return False

    async def log_video_upload(self, user_id: str, video_data: Dict) -> bool:
        """Log video upload to database"""
        try:
            video_doc = {
                "user_id": user_id,
                "platform": "youtube",
                "video_id": video_data.get("video_id"),
                "video_url": video_data.get("video_url"),
                "title": video_data.get("title"),
                "description": video_data.get("description"),
                "tags": video_data.get("tags", []),
                "privacy_status": video_data.get("privacy_status", "public"),
                "content_type": video_data.get("content_type", "video"),
                "ai_generated": video_data.get("ai_generated", False),
                "upload_status": "completed",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            if not hasattr(self, 'video_uploads_collection'):
                self.video_uploads_collection = self.db.video_uploads
                await self.video_uploads_collection.create_index("user_id")
            
            await self.video_uploads_collection.insert_one(video_doc)
            logger.info(f"Video upload logged for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log video upload: {e}")
            return False
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user_data["created_at"] = datetime.now()
            user_data["youtube_connected"] = False
            user_data["automation_enabled"] = False
            
            result = await self.users_collection.insert_one(user_data)
            
            return {
                "success": True,
                "user_id": str(result.inserted_id),
                "message": "User created successfully"
            }
            
        except pymongo.errors.DuplicateKeyError:
            return {"success": False, "error": "Email already exists"}
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = await self.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            logger.error(f"Get user by email failed: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = await self.users_collection.find_one({"_id": user_id})
            return user
        except Exception as e:
            logger.error(f"Get user by ID failed: {e}")
            return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data["updated_at"] = datetime.now()
            result = await self.users_collection.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"User update failed: {e}")
            return False

    async def store_youtube_credentials(self, user_id: str, credentials: Dict[str, Any]) -> bool:
        """Store YouTube OAuth credentials for user"""
        try:
            credential_data = {
                "user_id": user_id,
                "access_token": credentials.get("access_token"),
                "refresh_token": credentials.get("refresh_token"),
                "token_uri": credentials.get("token_uri"),
                "client_id": credentials.get("client_id"),
                "client_secret": credentials.get("client_secret"),
                "scopes": credentials.get("scopes"),
                "expires_at": credentials.get("expires_at"),
                "channel_info": credentials.get("channel_info", {}),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True,
                "platform": "youtube"
            }
            
            await self.youtube_credentials_collection.replace_one(
                {"user_id": user_id},
                credential_data,
                upsert=True
            )
            
            await self.update_user(user_id, {
                "youtube_connected": True,
                "youtube_connected_at": datetime.now()
            })
            
            logger.info(f"YouTube credentials stored for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Store YouTube credentials failed: {e}")
            return False
    
    async def get_youtube_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get YouTube credentials for user"""
        try:
            credentials = await self.youtube_credentials_collection.find_one(
                {"user_id": user_id}
            )
            return credentials
        except Exception as e:
            logger.error(f"Get YouTube credentials failed: {e}")
            return None
    
    async def refresh_youtube_token(self, user_id: str, new_access_token: str, expires_at: datetime) -> bool:
        """Update YouTube access token after refresh"""
        try:
            result = await self.youtube_credentials_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "access_token": new_access_token,
                        "expires_at": expires_at,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"YouTube token refresh failed: {e}")
            return False
    
    async def revoke_youtube_access(self, user_id: str) -> bool:
        """Revoke YouTube access for user"""
        try:
            await self.youtube_credentials_collection.delete_one({"user_id": user_id})
            await self.update_user(user_id, {
                "youtube_connected": False,
                "automation_enabled": False
            })
            await self.automation_configs_collection.delete_many({
                "user_id": user_id,
                "platform": "youtube"
            })
            
            logger.info(f"YouTube access revoked for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Revoke YouTube access failed: {e}")
            return False
    
    async def store_automation_config(self, user_id: str, config_type: str, config_data: Dict[str, Any]) -> bool:
        """Store automation configuration"""
        try:
            config_document = {
                "user_id": user_id,
                "platform": "youtube",
                "config_type": config_type,
                "config_data": config_data,
                "enabled": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            await self.automation_configs_collection.replace_one(
                {"user_id": user_id, "config_type": config_type},
                config_document,
                upsert=True
            )
            
            await self.update_user(user_id, {"automation_enabled": True})
            
            return True
            
        except Exception as e:
            logger.error(f"Store automation config failed: {e}")
            return False
    
    async def get_automation_config(self, user_id: str, config_type: str) -> Optional[Dict[str, Any]]:
        """Get automation configuration"""
        try:
            config = await self.automation_configs_collection.find_one({
                "user_id": user_id,
                "config_type": config_type
            })
            return config
        except Exception as e:
            logger.error(f"Get automation config failed: {e}")
            return None
    
    async def get_all_automation_configs(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all automation configurations for user"""
        try:
            configs = []
            async for config in self.automation_configs_collection.find({"user_id": user_id}):
                configs.append(config)
            return configs
        except Exception as e:
            logger.error(f"Get all automation configs failed: {e}")
            return []
    
    async def disable_automation(self, user_id: str, config_type: str) -> bool:
        """Disable specific automation"""
        try:
            result = await self.automation_configs_collection.update_one(
                {"user_id": user_id, "config_type": config_type},
                {
                    "$set": {
                        "enabled": False,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Disable automation failed: {e}")
            return False
    
    async def get_upload_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's upload history"""
        try:
            uploads = []
            async for upload in self.upload_history_collection.find(
                {"user_id": user_id}
            ).sort("upload_date", -1).limit(limit):
                uploads.append(upload)
            return uploads
        except Exception as e:
            logger.error(f"Get upload history failed: {e}")
            return []
    
    async def get_upload_stats(self, user_id: str) -> Dict[str, Any]:
        """Get upload statistics for user"""
        try:
            total_uploads = await self.upload_history_collection.count_documents(
                {"user_id": user_id}
            )
            
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_uploads = await self.upload_history_collection.count_documents({
                "user_id": user_id,
                "upload_date": {"$gte": thirty_days_ago}
            })
            
            shorts_count = await self.upload_history_collection.count_documents({
                "user_id": user_id,
                "content_type": "shorts"
            })
            
            videos_count = total_uploads - shorts_count
            
            return {
                "total_uploads": total_uploads,
                "recent_uploads": recent_uploads,
                "shorts_count": shorts_count,
                "videos_count": videos_count,
                "success_rate": 100.0
            }
            
        except Exception as e:
            logger.error(f"Get upload stats failed: {e}")
            return {
                "total_uploads": 0,
                "recent_uploads": 0,
                "shorts_count": 0,
                "videos_count": 0,
                "success_rate": 0.0
            }
    
    async def store_channel_analytics(self, user_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Store channel analytics data"""
        try:
            analytics_record = {
                "user_id": user_id,
                "date": datetime.now().date(),
                "channel_statistics": analytics_data.get("channel_statistics", {}),
                "recent_videos": analytics_data.get("recent_videos", []),
                "period_days": analytics_data.get("period_days", 30),
                "created_at": datetime.now()
            }
            
            await self.analytics_collection.replace_one(
                {
                    "user_id": user_id,
                    "date": datetime.now().date()
                },
                analytics_record,
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Store channel analytics failed: {e}")
            return False
    
    async def get_channel_analytics(self, user_id: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get latest channel analytics"""
        try:
            analytics = await self.analytics_collection.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            return analytics
        except Exception as e:
            logger.error(f"Get channel analytics failed: {e}")
            return None
    
    async def get_user_credentials(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get user credentials for any platform"""
        if platform == "youtube":
            return await self.get_youtube_credentials(user_id)
        return None
    
    async def store_user_credentials(self, user_id: str, platform: str, credentials: Dict[str, Any], channel_info: Dict[str, Any] = None) -> bool:
        """Store user credentials for any platform"""
        if platform == "youtube":
            if channel_info:
                credentials["channel_info"] = channel_info
            return await self.store_youtube_credentials(user_id, credentials)
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            await self.client.admin.command('ping')
            
            users_count = await self.users_collection.count_documents({})
            credentials_count = await self.youtube_credentials_collection.count_documents({})
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": {
                    "users": users_count,
                    "youtube_credentials": credentials_count
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def store_scheduled_post(self, user_id: str, video_data: Dict[str, Any], scheduled_for: datetime) -> bool:
        """Store a scheduled video post"""
        try:
            if not self.scheduled_posts_collection:
                logger.error("scheduled_posts_collection not initialized")
                return False
            
            scheduled_post = {
                "user_id": user_id,
                "video_data": video_data,
                "scheduled_for": scheduled_for,
                "status": "scheduled",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "execution_attempts": 0,
                "last_error": None
            }

            result = await self.scheduled_posts_collection.insert_one(scheduled_post)
            logger.info(f"Scheduled post stored for user {user_id} at {scheduled_for} with ID: {result.inserted_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store scheduled post: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    async def get_due_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Get posts scheduled to be published now"""
        try:
            current_time = datetime.now()
            time_window_start = current_time - timedelta(minutes=1)
            time_window_end = current_time + timedelta(minutes=2)
            
            logger.info(f"Querying scheduled posts between {time_window_start.strftime('%H:%M')} and {time_window_end.strftime('%H:%M')}")
            
            if not self.scheduled_posts_collection:
                logger.error("scheduled_posts_collection not initialized")
                return []
            
            posts = []
            cursor = self.scheduled_posts_collection.find({
                "status": "scheduled",
                "scheduled_for": {
                    "$gte": time_window_start,
                    "$lte": time_window_end
                }
            })
            
            async for post in cursor:
                posts.append(post)
                logger.info(f"Found post: {post.get('video_data', {}).get('title')} @ {post.get('scheduled_for')}")
            
            return posts
            
        except Exception as e:
            logger.error(f"get_due_scheduled_posts failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def update_scheduled_post_status(self, post_id, status: str, error_message: str = None) -> bool:
        """Update scheduled post status"""
        try:
            if not self.scheduled_posts_collection:
                logger.error("scheduled_posts_collection not initialized")
                return False
            
            update_data = {
                "status": status,
                "updated_at": datetime.now()
            }
            
            if status == "processing":
                update_data["processing_started_at"] = datetime.now()
            elif status == "published":
                update_data["published_at"] = datetime.now()
            elif status == "failed":
                update_data["failed_at"] = datetime.now()
                if error_message:
                    update_data["error_message"] = error_message
            
            result = await self.scheduled_posts_collection.update_one(
                {"_id": post_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Post {post_id} status updated to: {status}")
                return True
            else:
                logger.warning(f"No post found with ID: {post_id}")
                return False
                
        except Exception as e:
            logger.error(f"update_scheduled_post_status failed: {e}")
            return False

    async def get_scheduled_posts_by_user(self, user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get scheduled posts for a user"""
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status

            posts = []
            async for post in self.scheduled_posts_collection.find(query).sort("scheduled_for", 1):
                posts.append(post)

            return posts

        except Exception as e:
            logger.error(f"Failed to get user scheduled posts: {e}")
            return []

    async def delete_scheduled_post(self, post_id) -> bool:
        """Delete a scheduled post"""
        try:
            result = await self.scheduled_posts_collection.delete_one({"_id": post_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete scheduled post: {e}")
            return False


# Global instance
youtube_db_manager = None

def get_youtube_database() -> YouTubeDatabaseManager:
    """Get global YouTube database instance"""
    global youtube_db_manager
    if not youtube_db_manager:
        youtube_db_manager = YouTubeDatabaseManager()
    return youtube_db_manager