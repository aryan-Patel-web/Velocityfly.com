# """
# YouTube Database Manager - MongoDB operations for YouTube automation
# Handles user credentials, automation configs, analytics, and auto-reply management
# """

# import os
# import asyncio
# import logging
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional, Any
# from motor.motor_asyncio import AsyncIOMotorClient
# import pymongo
# from bson import ObjectId
# from pymongo.errors import DuplicateKeyError, ConnectionFailure

# logger = logging.getLogger(__name__)

# class YouTubeDatabaseManager:
#     """MongoDB database manager specifically for YouTube automation"""
    
#     def __init__(self):
#         self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
#         self.database_name = os.getenv("MONGODB_DATABASE", "youtube_automation")
#         self.client = None
#         self.db = None
        
#         # Collections
#         self.users_collection = None
#         self.youtube_credentials_collection = None
#         self.automation_configs_collection = None
#         self.upload_history_collection = None
#         self.analytics_collection = None
#         self.scheduled_posts_collection = None
#         self.community_posts_collection = None
#         self.video_uploads_collection = None
#         self.comment_replies_collection = None
#         self.auto_reply_logs_collection = None
        
#         logger.info("YouTube Database Manager initialized")
    
#     async def connect(self):
#         """Connect to MongoDB"""
#         try:
#             self.client = AsyncIOMotorClient(self.mongo_uri)
#             self.db = self.client[self.database_name]
            
#             # Initialize collections
#             self.users_collection = self.db["users"]
#             self.youtube_credentials_collection = self.db["youtube_credentials"]
#             self.automation_configs_collection = self.db["automation_configs"]
#             self.upload_history_collection = self.db["upload_history"]
#             self.analytics_collection = self.db["analytics"]
#             self.scheduled_posts_collection = self.db["scheduled_posts"]
#             self.community_posts_collection = self.db["community_posts"]
#             self.video_uploads_collection = self.db["video_uploads"]
#             self.comment_replies_collection = self.db["comment_replies"]
#             self.auto_reply_logs_collection = self.db["auto_reply_logs"]
            
#             # Test connection
#             await self.client.admin.command('ping')
            
#             # Create indexes
#             await self._create_indexes()
            
#             logger.info(f"Connected to YouTube MongoDB: {self.database_name}")
#             return True
            
#         except Exception as e:
#             logger.error(f"YouTube MongoDB connection failed: {e}")
#             return False
    
#     async def _create_indexes(self):
#         """Create database indexes for better performance"""
#         try:
#             # User indexes
#             await self.users_collection.create_index("email", unique=True)
#             await self.users_collection.create_index("created_at")
            
#             # YouTube credentials indexes
#             await self.youtube_credentials_collection.create_index("user_id", unique=True)
#             await self.youtube_credentials_collection.create_index("channel_id")
            
#             # Automation config indexes
#             await self.automation_configs_collection.create_index("user_id")
#             await self.automation_configs_collection.create_index("config_type")
#             await self.automation_configs_collection.create_index([("config_type", 1), ("enabled", 1)])
            
#             # Upload history indexes
#             await self.upload_history_collection.create_index("user_id")
#             await self.upload_history_collection.create_index("video_id", unique=True)
#             await self.upload_history_collection.create_index("upload_date")
            
#             # Analytics indexes
#             await self.analytics_collection.create_index("user_id")
#             await self.analytics_collection.create_index("date")
            
#             # Scheduled posts indexes
#             await self.scheduled_posts_collection.create_index("user_id")
#             await self.scheduled_posts_collection.create_index("scheduled_for")
#             await self.scheduled_posts_collection.create_index("status")
#             await self.scheduled_posts_collection.create_index([
#                 ("user_id", 1),
#                 ("status", 1),
#                 ("scheduled_for", 1)
#             ])
            
#             # Comment replies indexes
#             await self.comment_replies_collection.create_index("user_id")
#             await self.comment_replies_collection.create_index("comment_id")
#             await self.comment_replies_collection.create_index("video_id")
#             await self.comment_replies_collection.create_index("reply_id", unique=True)
            
#             # Auto-reply logs indexes
#             await self.auto_reply_logs_collection.create_index("user_id")
#             await self.auto_reply_logs_collection.create_index("video_id")
#             await self.auto_reply_logs_collection.create_index("processed_at")
#             await self.auto_reply_logs_collection.create_index([("user_id", 1), ("processed_at", -1)])
            
#             logger.info("YouTube database indexes created")
            
#         except Exception as e:
#             logger.error(f"Index creation failed: {e}")
    
#     async def close(self):
#         """Close database connection"""
#         if self.client:
#             self.client.close()
#             logger.info("YouTube database connection closed")

#     # ============================================================================
#     # USER MANAGEMENT
#     # ============================================================================

#     async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Create a new user"""
#         try:
#             user_data["created_at"] = datetime.now()
#             user_data["youtube_connected"] = False
#             user_data["automation_enabled"] = False
#             user_data["auto_reply_enabled"] = False
            
#             result = await self.users_collection.insert_one(user_data)
            
#             return {
#                 "success": True,
#                 "user_id": str(result.inserted_id),
#                 "message": "User created successfully"
#             }
            
#         except pymongo.errors.DuplicateKeyError:
#             return {"success": False, "error": "Email already exists"}
#         except Exception as e:
#             logger.error(f"User creation failed: {e}")
#             return {"success": False, "error": str(e)}
    
#     async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
#         """Get user by email"""
#         try:
#             user = await self.users_collection.find_one({"email": email})
#             return user
#         except Exception as e:
#             logger.error(f"Get user by email failed: {e}")
#             return None
    
#     async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
#         """Get user by ID"""
#         try:
#             user = await self.users_collection.find_one({"_id": user_id})
#             return user
#         except Exception as e:
#             logger.error(f"Get user by ID failed: {e}")
#             return None
    
#     async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
#         """Update user data"""
#         try:
#             update_data["updated_at"] = datetime.now()
#             result = await self.users_collection.update_one(
#                 {"_id": user_id},
#                 {"$set": update_data}
#             )
#             return result.modified_count > 0
#         except Exception as e:
#             logger.error(f"User update failed: {e}")
#             return False

#     # ============================================================================
#     # YOUTUBE CREDENTIALS MANAGEMENT
#     # ============================================================================

#     async def store_youtube_credentials(self, user_id: str, credentials: Dict[str, Any]) -> bool:
#         """Store YouTube OAuth credentials for user"""
#         try:
#             credential_data = {
#                 "user_id": user_id,
#                 "access_token": credentials.get("access_token"),
#                 "refresh_token": credentials.get("refresh_token"),
#                 "token_uri": credentials.get("token_uri"),
#                 "client_id": credentials.get("client_id"),
#                 "client_secret": credentials.get("client_secret"),
#                 "scopes": credentials.get("scopes"),
#                 "expires_at": credentials.get("expires_at"),
#                 "channel_info": credentials.get("channel_info", {}),
#                 "created_at": datetime.now(),
#                 "updated_at": datetime.now(),
#                 "is_active": True,
#                 "platform": "youtube"
#             }
            
#             await self.youtube_credentials_collection.replace_one(
#                 {"user_id": user_id},
#                 credential_data,
#                 upsert=True
#             )
            
#             await self.update_user(user_id, {
#                 "youtube_connected": True,
#                 "youtube_connected_at": datetime.now()
#             })
            
#             logger.info(f"YouTube credentials stored for user {user_id}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Store YouTube credentials failed: {e}")
#             return False
    
#     async def get_youtube_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
#         """Get YouTube credentials for user"""
#         try:
#             credentials = await self.youtube_credentials_collection.find_one(
#                 {"user_id": user_id}
#             )
#             return credentials
#         except Exception as e:
#             logger.error(f"Get YouTube credentials failed: {e}")
#             return None
    
#     async def refresh_youtube_token(self, user_id: str, new_access_token: str, expires_at: datetime) -> bool:
#         """Update YouTube access token after refresh"""
#         try:
#             result = await self.youtube_credentials_collection.update_one(
#                 {"user_id": user_id},
#                 {
#                     "$set": {
#                         "access_token": new_access_token,
#                         "expires_at": expires_at,
#                         "updated_at": datetime.now()
#                     }
#                 }
#             )
#             return result.modified_count > 0
#         except Exception as e:
#             logger.error(f"YouTube token refresh failed: {e}")
#             return False
    
#     async def revoke_youtube_access(self, user_id: str) -> bool:
#         """Revoke YouTube access for user"""
#         try:
#             await self.youtube_credentials_collection.delete_one({"user_id": user_id})
#             await self.update_user(user_id, {
#                 "youtube_connected": False,
#                 "automation_enabled": False,
#                 "auto_reply_enabled": False
#             })
#             await self.automation_configs_collection.delete_many({
#                 "user_id": user_id,
#                 "platform": "youtube"
#             })
            
#             logger.info(f"YouTube access revoked for user {user_id}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Revoke YouTube access failed: {e}")
#             return False








#     # ============================================================================
#     # AUTOMATION CONFIGURATION
#     # ============================================================================

#     async def store_automation_config(self, user_id: str, config_type: str, config_data: Dict[str, Any]) -> bool:
#         """Store automation configuration"""
#         try:
#             config_document = {
#                 "user_id": user_id,
#                 "platform": "youtube",
#                 "config_type": config_type,
#                 "config_data": config_data,
#                 "enabled": True,
#                 "created_at": datetime.now(),
#                 "updated_at": datetime.now()
#             }
            
#             await self.automation_configs_collection.replace_one(
#                 {"user_id": user_id, "config_type": config_type},
#                 config_document,
#                 upsert=True
#             )
            
#             # Update user automation status
#             update_data = {"automation_enabled": True}
#             if config_type == "auto_reply":
#                 update_data["auto_reply_enabled"] = True
            
#             await self.update_user(user_id, update_data)
            
#             return True
            
#         except Exception as e:
#             logger.error(f"Store automation config failed: {e}")
#             return False
    
#     async def get_automation_config(self, user_id: str, config_type: str) -> Optional[Dict[str, Any]]:
#         """Get automation configuration"""
#         try:
#             config = await self.automation_configs_collection.find_one({
#                 "user_id": user_id,
#                 "config_type": config_type
#             })
#             return config
#         except Exception as e:
#             logger.error(f"Get automation config failed: {e}")
#             return None
    
#     async def get_all_automation_configs_by_type(self, config_type: str) -> List[Dict[str, Any]]:
#         """Get all automation configs of a specific type"""
#         try:
#             configs = []
#             async for config in self.automation_configs_collection.find({
#                 "config_type": config_type,
#                 "enabled": True
#             }):
#                 configs.append(config)
#             return configs
#         except Exception as e:
#             logger.error(f"Failed to get automation configs: {e}")
#             return []
    
#     async def get_all_automation_configs(self, user_id: str) -> List[Dict[str, Any]]:
#         """Get all automation configurations for user"""
#         try:
#             configs = []
#             async for config in self.automation_configs_collection.find({"user_id": user_id}):
#                 configs.append(config)
#             return configs
#         except Exception as e:
#             logger.error(f"Get all automation configs failed: {e}")
#             return []
    
#     async def disable_automation(self, user_id: str, config_type: str) -> bool:
#         """Disable specific automation"""
#         try:
#             result = await self.automation_configs_collection.update_one(
#                 {"user_id": user_id, "config_type": config_type},
#                 {
#                     "$set": {
#                         "enabled": False,
#                         "updated_at": datetime.now()
#                     }
#                 }
#             )
            
#             # Update user status
#             if config_type == "auto_reply":
#                 await self.update_user(user_id, {"auto_reply_enabled": False})
            
#             return result.modified_count > 0
#         except Exception as e:
#             logger.error(f"Disable automation failed: {e}")
#             return False

#     # ============================================================================
#     # COMMENT REPLY MANAGEMENT
#     # ============================================================================

#     async def log_comment_reply(self, user_id: str, reply_data: Dict[str, Any]) -> bool:
#         """Log a comment reply to database"""
#         try:
#             reply_doc = {
#                 "user_id": user_id,
#                 "comment_id": reply_data.get("comment_id"),
#                 "video_id": reply_data.get("video_id"),
#                 "reply_id": reply_data.get("reply_id"),
#                 "reply_text": reply_data.get("reply_text"),
#                 "original_comment": reply_data.get("original_comment"),
#                 "comment_author": reply_data.get("comment_author"),
#                 "reply_type": reply_data.get("reply_type", "manual"),  # manual, auto
#                 "language_detected": reply_data.get("language_detected", "english"),
#                 "ai_service_used": reply_data.get("ai_service_used"),
#                 "emotion_detected": reply_data.get("emotion_detected"),
#                 "reply_generated_at": reply_data.get("reply_generated_at", datetime.now()),
#                 "reply_posted_at": datetime.now(),
#                 "created_at": datetime.now()
#             }
            
#             await self.comment_replies_collection.insert_one(reply_doc)
#             logger.info(f"Comment reply logged for user: {user_id}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to log comment reply: {e}")
#             return False

#     async def get_comment_reply_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
#         """Get comment reply history for user"""
#         try:
#             replies = []
#             async for reply in self.comment_replies_collection.find(
#                 {"user_id": user_id}
#             ).sort("reply_posted_at", -1).limit(limit):
#                 replies.append(reply)
#             return replies
#         except Exception as e:
#             logger.error(f"Get comment reply history failed: {e}")
#             return []

#     async def get_reply_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
#         """Get reply statistics for user"""
#         try:
#             start_date = datetime.now() - timedelta(days=days)
            
#             # Total replies
#             total_replies = await self.comment_replies_collection.count_documents({
#                 "user_id": user_id,
#                 "reply_posted_at": {"$gte": start_date}
#             })
            
#             # Auto vs manual replies
#             auto_replies = await self.comment_replies_collection.count_documents({
#                 "user_id": user_id,
#                 "reply_type": "auto",
#                 "reply_posted_at": {"$gte": start_date}
#             })
            
#             manual_replies = total_replies - auto_replies
            
#             # Language breakdown
#             language_pipeline = [
#                 {"$match": {
#                     "user_id": user_id,
#                     "reply_posted_at": {"$gte": start_date}
#                 }},
#                 {"$group": {
#                     "_id": "$language_detected",
#                     "count": {"$sum": 1}
#                 }}
#             ]
            
#             language_stats = {}
#             async for lang_stat in self.comment_replies_collection.aggregate(language_pipeline):
#                 language_stats[lang_stat["_id"]] = lang_stat["count"]
            
#             return {
#                 "total_replies": total_replies,
#                 "auto_replies": auto_replies,
#                 "manual_replies": manual_replies,
#                 "language_breakdown": language_stats,
#                 "period_days": days,
#                 "auto_reply_percentage": (auto_replies / total_replies * 100) if total_replies > 0 else 0
#             }
            
#         except Exception as e:
#             logger.error(f"Get reply stats failed: {e}")
#             return {
#                 "total_replies": 0,
#                 "auto_replies": 0,
#                 "manual_replies": 0,
#                 "language_breakdown": {},
#                 "period_days": days,
#                 "auto_reply_percentage": 0
#             }

#     async def log_auto_reply_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
#         """Log auto-reply processing session"""
#         try:
#             session_doc = {
#                 "user_id": user_id,
#                 "session_id": session_data.get("session_id", str(ObjectId())),
#                 "videos_processed": session_data.get("videos_processed", []),
#                 "comments_found": session_data.get("comments_found", 0),
#                 "replies_generated": session_data.get("replies_generated", 0),
#                 "replies_posted": session_data.get("replies_posted", 0),
#                 "errors_encountered": session_data.get("errors_encountered", []),
#                 "processing_duration": session_data.get("processing_duration", 0),
#                 "processed_at": datetime.now(),
#                 "config_used": session_data.get("config_used", {})
#             }
            
#             await self.auto_reply_logs_collection.insert_one(session_doc)
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to log auto-reply session: {e}")
#             return False

#     async def check_comment_already_replied(self, user_id: str, comment_id: str) -> bool:
#         """Check if we already replied to a specific comment"""
#         try:
#             reply = await self.comment_replies_collection.find_one({
#                 "user_id": user_id,
#                 "comment_id": comment_id
#             })
#             return reply is not None
#         except Exception as e:
#             logger.error(f"Check comment replied failed: {e}")
#             return False

#     # ============================================================================
#     # CONTENT LOGGING
#     # ============================================================================

#     async def log_community_post(self, user_id: str, post_data: Dict[str, Any]) -> bool:
#         """Log community post to database"""
#         try:
#             post_doc = {
#                 "user_id": user_id,
#                 "platform": "youtube",
#                 "post_type": post_data.get("post_type", "text"),
#                 "content": post_data.get("content", ""),
#                 "image_url": post_data.get("image_url"),
#                 "options": post_data.get("options", []),
#                 "correct_answer": post_data.get("correct_answer"),
#                 "status": post_data.get("status", "published"),
#                 "scheduled_for": post_data.get("scheduled_for"),
#                 "created_at": datetime.now(),
#                 "updated_at": datetime.now()
#             }
            
#             await self.community_posts_collection.insert_one(post_doc)
#             logger.info(f"Community post logged for user: {user_id}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to log community post: {e}")
#             return False

#     async def log_video_upload(self, user_id: str, video_data: Dict[str, Any]) -> bool:
#         """Log video upload to database"""
#         try:
#             video_doc = {
#                 "user_id": user_id,
#                 "platform": "youtube",
#                 "video_id": video_data.get("video_id"),
#                 "video_url": video_data.get("video_url"),
#                 "title": video_data.get("title"),
#                 "description": video_data.get("description"),
#                 "tags": video_data.get("tags", []),
#                 "privacy_status": video_data.get("privacy_status", "public"),
#                 "content_type": video_data.get("content_type", "video"),
#                 "ai_generated": video_data.get("ai_generated", False),
#                 "thumbnail_uploaded": video_data.get("thumbnail_uploaded", False),
#                 "upload_status": "completed",
#                 "created_at": datetime.now(),
#                 "updated_at": datetime.now()
#             }
            
#             await self.video_uploads_collection.insert_one(video_doc)
#             logger.info(f"Video upload logged for user: {user_id}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to log video upload: {e}")
#             return False

#     # ============================================================================
#     # UPLOAD HISTORY & STATS
#     # ============================================================================

#     async def get_upload_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
#         """Get user's upload history"""
#         try:
#             uploads = []
#             async for upload in self.upload_history_collection.find(
#                 {"user_id": user_id}
#             ).sort("upload_date", -1).limit(limit):
#                 uploads.append(upload)
#             return uploads
#         except Exception as e:
#             logger.error(f"Get upload history failed: {e}")
#             return []
    
#     async def get_upload_stats(self, user_id: str) -> Dict[str, Any]:
#         """Get upload statistics for user"""
#         try:
#             total_uploads = await self.upload_history_collection.count_documents(
#                 {"user_id": user_id}
#             )
            
#             thirty_days_ago = datetime.now() - timedelta(days=30)
#             recent_uploads = await self.upload_history_collection.count_documents({
#                 "user_id": user_id,
#                 "upload_date": {"$gte": thirty_days_ago}
#             })
            
#             shorts_count = await self.upload_history_collection.count_documents({
#                 "user_id": user_id,
#                 "content_type": "shorts"
#             })
            
#             videos_count = total_uploads - shorts_count
            
#             return {
#                 "total_uploads": total_uploads,
#                 "recent_uploads": recent_uploads,
#                 "shorts_count": shorts_count,
#                 "videos_count": videos_count,
#                 "success_rate": 100.0
#             }
            
#         except Exception as e:
#             logger.error(f"Get upload stats failed: {e}")
#             return {
#                 "total_uploads": 0,
#                 "recent_uploads": 0,
#                 "shorts_count": 0,
#                 "videos_count": 0,
#                 "success_rate": 0.0
#             }
#     # sdsgbdbdb
#     async def store_product_promo(self, user_id: str, product_data: dict) -> bool:
#         """Store product promotion data"""
#         try:
#             if not self.db:
#                 logger.error("Database not connected")
#                 return False
            
#             promo_doc = {
#                 "user_id": user_id,
#                 "product_data": product_data,
#                 "video_id": None,  # Updated after upload
#                 "created_at": datetime.now(),
#                 "updated_at": datetime.now(),
#                 "status": "pending"
#             }
            
#             result = await self.db.product_promos.insert_one(promo_doc)
#             logger.info(f"Product promo stored with ID: {result.inserted_id}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to store product promo: {e}")
#             return False
    
#     async def get_product_promos_by_user(self, user_id: str, status: str = None) -> list:
#         """Get product promos for a user"""
#         try:
#             if not self.db:
#                 return []
            
#             query = {"user_id": user_id}
#             if status:
#                 query["status"] = status
            
#             cursor = self.db.product_promos.find(query).sort("created_at", -1)
#             promos = []
#             async for promo in cursor:
#                 promos.append(promo)
            
#             return promos
            
#         except Exception as e:
#             logger.error(f"Failed to get product promos: {e}")
#             return []
    
    

#     # ============================================================================
#     # ANALYTICS
#     # ============================================================================

#     async def store_channel_analytics(self, user_id: str, analytics_data: Dict[str, Any]) -> bool:
#         """Store channel analytics data"""
#         try:
#             analytics_record = {
#                 "user_id": user_id,
#                 "date": datetime.now().date(),
#                 "channel_statistics": analytics_data.get("channel_statistics", {}),
#                 "recent_videos": analytics_data.get("recent_videos", []),
#                 "period_days": analytics_data.get("period_days", 30),
#                 "created_at": datetime.now()
#             }
            
#             await self.analytics_collection.replace_one(
#                 {
#                     "user_id": user_id,
#                     "date": datetime.now().date()
#                 },
#                 analytics_record,
#                 upsert=True
#             )
            
#             return True
            
#         except Exception as e:
#             logger.error(f"Store channel analytics failed: {e}")
#             return False
    
#     async def get_channel_analytics(self, user_id: str, days: int = 30) -> Optional[Dict[str, Any]]:
#         """Get latest channel analytics"""
#         try:
#             analytics = await self.analytics_collection.find_one(
#                 {"user_id": user_id},
#                 sort=[("created_at", -1)]
#             )
#             return analytics
#         except Exception as e:
#             logger.error(f"Get channel analytics failed: {e}")
#             return None
    

#     # ============================================================================
#     # SCHEDULED POSTS
#     # ============================================================================

#     async def store_scheduled_post(self, user_id: str, video_data: Dict[str, Any], scheduled_for: datetime) -> bool:
#         """Store a scheduled video post"""
#         try:
#             if self.scheduled_posts_collection is None:
#                 logger.error("scheduled_posts_collection not initialized")
#                 return False
            
#             scheduled_post = {
#                 "user_id": user_id,
#                 "video_data": video_data,
#                 "scheduled_for": scheduled_for,
#                 "status": "scheduled",
#                 "created_at": datetime.now(),
#                 "updated_at": datetime.now(),
#                 "execution_attempts": 0,
#                 "last_error": None
#             }

#             result = await self.scheduled_posts_collection.insert_one(scheduled_post)
#             logger.info(f"Scheduled post stored for user {user_id} at {scheduled_for} with ID: {result.inserted_id}")
#             return True

#         except Exception as e:
#             logger.error(f"Failed to store scheduled post: {e}")
#             return False

#     async def get_due_scheduled_posts(self) -> List[Dict[str, Any]]:
#         """Get posts scheduled to be published now"""
#         try:
#             current_time = datetime.now()
#             time_window_start = current_time - timedelta(minutes=1)
#             time_window_end = current_time + timedelta(minutes=2)
            
#             logger.info(f"Querying scheduled posts between {time_window_start.strftime('%H:%M')} and {time_window_end.strftime('%H:%M')}")
            
#             if self.scheduled_posts_collection is None:
#                 logger.error("scheduled_posts_collection not initialized")
#                 return []
            
#             posts = []
#             cursor = self.scheduled_posts_collection.find({
#                 "status": "scheduled",
#                 "scheduled_for": {
#                     "$gte": time_window_start,
#                     "$lte": time_window_end
#                 }
#             })
            
#             async for post in cursor:
#                 posts.append(post)
#                 logger.info(f"Found post: {post.get('video_data', {}).get('title')} @ {post.get('scheduled_for')}")
            
#             if not posts:
#                 logger.debug(f"No posts due between {time_window_start.strftime('%H:%M')} and {time_window_end.strftime('%H:%M')}")
            
#             return posts
            
#         except Exception as e:
#             logger.error(f"get_due_scheduled_posts failed: {e}")
#             return []
    
#     async def update_scheduled_post_status(self, post_id, status: str, error_message: str = None) -> bool:
#         """Update scheduled post status"""
#         try:
#             if self.scheduled_posts_collection is None:
#                 logger.error("scheduled_posts_collection not initialized")
#                 return False
            
#             update_data = {
#                 "status": status,
#                 "updated_at": datetime.now()
#             }
            
#             if status == "processing":
#                 update_data["processing_started_at"] = datetime.now()
#             elif status == "published":
#                 update_data["published_at"] = datetime.now()
#             elif status == "failed":
#                 update_data["failed_at"] = datetime.now()
#                 if error_message:
#                     update_data["error_message"] = error_message
            
#             result = await self.scheduled_posts_collection.update_one(
#                 {"_id": post_id},
#                 {"$set": update_data}
#             )
            
#             if result.modified_count > 0:
#                 logger.info(f"Post {post_id} status updated to: {status}")
#                 return True
#             else:
#                 logger.warning(f"No post found with ID: {post_id}")
#                 return False
                
#         except Exception as e:
#             logger.error(f"update_scheduled_post_status failed: {e}")
#             return False

#     async def get_scheduled_posts_by_user(self, user_id: str, status: str = None) -> List[Dict[str, Any]]:
#         """Get scheduled posts for a user"""
#         try:
#             query = {"user_id": user_id}
#             if status:
#                 query["status"] = status

#             posts = []
#             async for post in self.scheduled_posts_collection.find(query).sort("scheduled_for", 1):
#                 posts.append(post)

#             return posts

#         except Exception as e:
#             logger.error(f"Failed to get user scheduled posts: {e}")
#             return []

#     async def delete_scheduled_post(self, post_id) -> bool:
#         """Delete a scheduled post"""
#         try:
#             result = await self.scheduled_posts_collection.delete_one({"_id": post_id})
#             return result.deleted_count > 0
#         except Exception as e:
#             logger.error(f"Failed to delete scheduled post: {e}")
#             return False

#     # ============================================================================
#     # GENERIC CREDENTIAL METHODS
#     # ============================================================================

#     async def get_user_credentials(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
#         """Get user credentials for any platform"""
#         if platform == "youtube":
#             return await self.get_youtube_credentials(user_id)
#         return None
    
#     async def store_user_credentials(self, user_id: str, platform: str, credentials: Dict[str, Any], channel_info: Dict[str, Any] = None) -> bool:
#         """Store user credentials for any platform"""
#         if platform == "youtube":
#             if channel_info:
#                 credentials["channel_info"] = channel_info
#             return await self.store_youtube_credentials(user_id, credentials)
#         return False

#     # ============================================================================
#     # HEALTH CHECK
#     # ============================================================================

#     # async def health_check(self) -> Dict[str, Any]:
#     async def health_check(self) -> Dict[str, Any]:
#         """Check database health"""
#         try:
#             await self.client.admin.command('ping')
            
#             users_count = await self.users_collection.count_documents({})
#             credentials_count = await self.youtube_credentials_collection.count_documents({})
#             configs_count = await self.automation_configs_collection.count_documents({})
#             replies_count = await self.comment_replies_collection.count_documents({})
            
#             return {
#                 "status": "healthy",
#                 "database": self.database_name,
#                 "collections": {
#                     "users": users_count,
#                     "youtube_credentials": credentials_count,
#                     "automation_configs": configs_count,
#                     "comment_replies": replies_count
#                 },
#                 "timestamp": datetime.now().isoformat()
#             }
            
#         except Exception as e:
#             logger.error(f"Database health check failed: {e}")
#             return {
#                 "status": "unhealthy",
#                 "error": str(e),
#                 "timestamp": datetime.now().isoformat()
#             }

#     # ============================================================================
#     # UTILITY METHODS FOR AUTO-REPLY
#     # ============================================================================

#     async def get_recent_comments_for_processing(self, user_id: str, video_ids: List[str], hours_back: int = 24) -> List[Dict[str, Any]]:
#         """Get recent comments that need auto-reply processing"""
#         try:
#             # This would typically involve calling YouTube API
#             # For now, return structure for processed comments
#             cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
#             processed_comments = []
#             async for log in self.auto_reply_logs_collection.find({
#                 "user_id": user_id,
#                 "processed_at": {"$gte": cutoff_time}
#             }):
#                 processed_comments.extend(log.get("comments_processed", []))
            
#             return processed_comments
            
#         except Exception as e:
#             logger.error(f"Get recent comments failed: {e}")
#             return []

#     async def mark_comment_as_processed(self, user_id: str, comment_id: str, video_id: str, processing_result: Dict[str, Any]) -> bool:
#         """Mark a comment as processed for auto-reply"""
#         try:
#             process_doc = {
#                 "user_id": user_id,
#                 "comment_id": comment_id,
#                 "video_id": video_id,
#                 "processed_at": datetime.now(),
#                 "processing_result": processing_result,
#                 "reply_successful": processing_result.get("success", False),
#                 "error_message": processing_result.get("error"),
#                 "ai_service_used": processing_result.get("ai_service"),
#                 "reply_text": processing_result.get("reply_text")
#             }
            
#             # Store in auto_reply_logs collection
#             await self.auto_reply_logs_collection.insert_one(process_doc)
#             return True
            
#         except Exception as e:
#             logger.error(f"Mark comment processed failed: {e}")
#             return False

#     async def get_auto_reply_rate_limit(self, user_id: str, hours: int = 1) -> Dict[str, int]:
#         """Check auto-reply rate limits for user"""
#         try:
#             cutoff_time = datetime.now() - timedelta(hours=hours)
            
#             recent_replies = await self.comment_replies_collection.count_documents({
#                 "user_id": user_id,
#                 "reply_type": "auto",
#                 "reply_posted_at": {"$gte": cutoff_time}
#             })
            
#             # Get user's configured limits
#             config = await self.get_automation_config(user_id, "auto_reply")
#             max_per_hour = config.get("config_data", {}).get("max_replies_per_hour", 10) if config else 10
            
#             return {
#                 "replies_sent": recent_replies,
#                 "max_allowed": max_per_hour,
#                 "remaining": max(0, max_per_hour - recent_replies),
#                 "can_send": recent_replies < max_per_hour
#             }
            
#         except Exception as e:
#             logger.error(f"Get rate limit failed: {e}")
#             return {
#                 "replies_sent": 0,
#                 "max_allowed": 10,
#                 "remaining": 10,
#                 "can_send": True
#             }

#     async def cleanup_old_logs(self, days_to_keep: int = 30) -> bool:
#         """Clean up old logs and data"""
#         try:
#             cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
#             # Clean up old auto-reply logs
#             auto_reply_result = await self.auto_reply_logs_collection.delete_many({
#                 "processed_at": {"$lt": cutoff_date}
#             })
            
#             # Clean up old comment replies (keep stats but remove detailed logs)
#             comment_reply_result = await self.comment_replies_collection.delete_many({
#                 "reply_posted_at": {"$lt": cutoff_date}
#             })
            
#             logger.info(f"Cleanup completed: {auto_reply_result.deleted_count} auto-reply logs, {comment_reply_result.deleted_count} comment replies deleted")
#             return True
            
#         except Exception as e:
#             logger.error(f"Cleanup failed: {e}")
#             return False

#     # ============================================================================
#     # BACKUP AND RESTORE METHODS
#     # ============================================================================

#     async def backup_user_data(self, user_id: str) -> Dict[str, Any]:
#         """Create backup of user's data"""
#         try:
#             backup_data = {
#                 "user_id": user_id,
#                 "backup_created_at": datetime.now(),
#                 "data": {}
#             }
            
#             # Backup user profile
#             user = await self.get_user_by_id(user_id)
#             if user:
#                 backup_data["data"]["user_profile"] = user
            
#             # Backup credentials
#             credentials = await self.get_youtube_credentials(user_id)
#             if credentials:
#                 # Don't backup sensitive tokens, just metadata
#                 safe_credentials = {
#                     "channel_info": credentials.get("channel_info"),
#                     "created_at": credentials.get("created_at"),
#                     "scopes": credentials.get("scopes")
#                 }
#                 backup_data["data"]["credentials"] = safe_credentials
            
#             # Backup automation configs
#             configs = await self.get_all_automation_configs(user_id)
#             backup_data["data"]["automation_configs"] = configs
            
#             # Backup recent upload history
#             uploads = await self.get_upload_history(user_id, 100)
#             backup_data["data"]["upload_history"] = uploads
            
#             # Backup reply stats
#             reply_stats = await self.get_reply_stats(user_id, 90)
#             backup_data["data"]["reply_stats"] = reply_stats
            
#             return backup_data
            
#         except Exception as e:
#             logger.error(f"Backup failed: {e}")
#             return {"error": str(e)}

#     # ============================================================================
#     # ANALYTICS AGGREGATION METHODS
#     # ============================================================================

#     async def get_platform_wide_stats(self) -> Dict[str, Any]:
#         """Get platform-wide statistics"""
#         try:
#             total_users = await self.users_collection.count_documents({})
#             youtube_connected = await self.users_collection.count_documents({"youtube_connected": True})
#             auto_reply_enabled = await self.users_collection.count_documents({"auto_reply_enabled": True})
            
#             # Total replies in last 30 days
#             thirty_days_ago = datetime.now() - timedelta(days=30)
#             total_replies = await self.comment_replies_collection.count_documents({
#                 "reply_posted_at": {"$gte": thirty_days_ago}
#             })
            
#             auto_replies = await self.comment_replies_collection.count_documents({
#                 "reply_type": "auto",
#                 "reply_posted_at": {"$gte": thirty_days_ago}
#             })
            
#             return {
#                 "total_users": total_users,
#                 "youtube_connected_users": youtube_connected,
#                 "auto_reply_enabled_users": auto_reply_enabled,
#                 "total_replies_30_days": total_replies,
#                 "auto_replies_30_days": auto_replies,
#                 "manual_replies_30_days": total_replies - auto_replies,
#                 "connection_rate": (youtube_connected / total_users * 100) if total_users > 0 else 0,
#                 "auto_reply_adoption": (auto_reply_enabled / youtube_connected * 100) if youtube_connected > 0 else 0
#             }
            
#         except Exception as e:
#             logger.error(f"Get platform stats failed: {e}")
#             return {}

#     # ============================================================================
#     # MIGRATION AND MAINTENANCE
#     # ============================================================================

#     async def migrate_legacy_data(self) -> bool:
#         """Migrate legacy data to new schema"""
#         try:
#             # Add any data migration logic here
#             logger.info("Starting data migration...")
            
#             # Example: Add auto_reply_enabled field to users who don't have it
#             await self.users_collection.update_many(
#                 {"auto_reply_enabled": {"$exists": False}},
#                 {"$set": {"auto_reply_enabled": False}}
#             )
            
#             logger.info("Data migration completed")
#             return True
            
#         except Exception as e:
#             logger.error(f"Data migration failed: {e}")
#             return False

#     async def optimize_database(self) -> bool:
#         """Optimize database performance"""
#         try:
#             # Rebuild indexes
#             await self._create_indexes()
            
#             # Compact collections if needed
#             # Note: This would require additional MongoDB admin privileges
            
#             logger.info("Database optimization completed")
#             return True
            
#         except Exception as e:
#             logger.error(f"Database optimization failed: {e}")
#             return False


# # ============================================================================
# # GLOBAL INSTANCE
# # ============================================================================

# youtube_db_manager = None

# def get_youtube_database() -> YouTubeDatabaseManager:
#     """Get global YouTube database instance"""
#     global youtube_db_manager
#     if not youtube_db_manager:
#         youtube_db_manager = YouTubeDatabaseManager()
#     return youtube_db_manager

# # ============================================================================
# # UTILITY FUNCTIONS
# # ============================================================================

# def convert_objectid_to_string(data):
#     """Convert ObjectId fields to strings for JSON serialization"""
#     if isinstance(data, dict):
#         for key, value in data.items():
#             if isinstance(value, ObjectId):
#                 data[key] = str(value)
#             elif isinstance(value, (dict, list)):
#                 data[key] = convert_objectid_to_string(value)
#     elif isinstance(data, list):
#         for i, item in enumerate(data):
#             data[i] = convert_objectid_to_string(item)
#     return data

# def validate_user_id(user_id: str) -> bool:
#     """Validate user ID format"""
#     try:
#         if len(user_id) < 8:
#             return False
#         return True
#     except Exception:
#         return False

# # ============================================================================
# # ERROR HANDLING DECORATORS
# # ============================================================================

# def handle_db_errors(func):
#     """Decorator for database error handling"""
#     async def wrapper(*args, **kwargs):
#         try:
#             return await func(*args, **kwargs)
#         except ConnectionFailure as e:
#             logger.error(f"Database connection failed in {func.__name__}: {e}")
#             return None
#         except Exception as e:
#             logger.error(f"Database error in {func.__name__}: {e}")
#             return None
#     return wrapper



# # ============================================================================
#     # AUTOMATION LOGGING
#     # ============================================================================

# async def get_automation_posts_count(self, user_id: str, date) -> int:
#         """Get number of automation posts for a specific date"""
#         try:
#             start_of_day = datetime.combine(date, datetime.min.time())
#             end_of_day = datetime.combine(date, datetime.max.time())
            
#             count = await self.db.automation_logs.count_documents({
#                 "user_id": user_id,
#                 "timestamp": {"$gte": start_of_day, "$lte": end_of_day},
#                 "success": True
#             })
            
#             return count
#         except Exception as e:
#             logger.error(f"Get automation posts count failed: {e}")
#             return 0
    
# async def log_automation_post(self, user_id: str, post_data: dict) -> bool:
#         """Log automated post to database"""
#         try:
#             log_doc = {
#                 "user_id": user_id,
#                 "product_url": post_data.get("product_url"),
#                 "video_id": post_data.get("video_id"),
#                 "timestamp": post_data.get("timestamp", datetime.now()),
#                 "success": post_data.get("success", True),
#                 "error": post_data.get("error")
#             }
            
#             await self.db.automation_logs.insert_one(log_doc)
#             return True
#         except Exception as e:
#             logger.error(f"Log automation post failed: {e}")
#             return False

# # ============================================================================
#     # PRODUCT URL QUEUE MANAGEMENT
#     # ============================================================================

# async def save_scrape_url(self, user_id: str, url: str) -> bool:
#         """Save website URL to scrape (replaces any existing URL)"""
#         try:
#             await self.db.scrape_urls.update_one(
#                 {"user_id": user_id},
#                 {
#                     "$set": {
#                         "user_id": user_id,
#                         "url": url,
#                         "created_at": datetime.now(),
#                         "last_scraped": None,
#                         "total_products_found": 0,
#                         "products_processed": 0
#                     }
#                 },
#                 upsert=True
#             )
#             logger.info(f"✅ Scrape URL saved for user: {user_id}")
#             return True
#         except Exception as e:
#             logger.error(f"❌ Save scrape URL failed: {e}")
#             return False

# async def get_scrape_url(self, user_id: str) -> dict:
#         """Get saved scrape URL for user"""
#         try:
#             url_doc = await self.scrape_urls.find_one({"user_id": user_id})
#             return url_doc if url_doc else None
#         except Exception as e:
#             logger.error(f"❌ Get scrape URL failed: {e}")
#             return None

# async def delete_scrape_url(self, user_id: str) -> bool:
#         """Delete scrape URL"""
#         try:
#             await self.scrape_urls.delete_one({"user_id": user_id})
#             logger.info(f"✅ Scrape URL deleted for user: {user_id}")
#             return True
#         except Exception as e:
#             logger.error(f"❌ Delete scrape URL failed: {e}")
#             return False

# async def update_scrape_progress(self, user_id: str, total_found: int, processed: int) -> bool:
#         """Update scraping progress"""
#         try:
#             await self.scrape_urls.update_one(
#                 {"user_id": user_id},
#                 {
#                     "$set": {
#                         "total_products_found": total_found,
#                         "products_processed": processed,
#                         "last_scraped": datetime.now()
#                     }
#                 }
#             )
#             return True
#         except Exception as e:
#             logger.error(f"❌ Update scrape progress failed: {e}")
#             return False

# async def get_next_unprocessed_product(self, user_id: str) -> dict:
#         """Get next product that hasn't been processed yet"""
#         try:
#             url_doc = await self.scrape_urls.find_one({"user_id": user_id})
            
#             if not url_doc:
#                 return None
            
#             # Check if we've processed all products
#             if url_doc.get("products_processed", 0) >= url_doc.get("total_products_found", 0):
#                 # Reset counter to loop through products again
#                 await self.scrape_urls.update_one(
#                     {"user_id": user_id},
#                     {"$set": {"products_processed": 0}}
#                 )
            
#             return url_doc
            
#         except Exception as e:
#             logger.error(f"❌ Get next product failed: {e}")
#             return None
        

# # ============================================================================
# # CONSTANTS
# # ============================================================================

# DEFAULT_PAGINATION_LIMIT = 50
# MAX_PAGINATION_LIMIT = 1000
# DEFAULT_ANALYTICS_PERIOD = 30
# MAX_ANALYTICS_PERIOD = 365
# AUTO_REPLY_RATE_LIMIT_WINDOW = 1  # hours
# DEFAULT_AUTO_REPLY_LIMIT = 10  # per hour



"""
YouTube Database Manager - MongoDB operations for YouTube automation
Handles user credentials, automation configs, analytics, and auto-reply management
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
        self.community_posts_collection = None
        self.video_uploads_collection = None
        self.comment_replies_collection = None
        self.auto_reply_logs_collection = None
        self.scrape_urls = None
        
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
            self.community_posts_collection = self.db["community_posts"]
            self.video_uploads_collection = self.db["video_uploads"]
            self.comment_replies_collection = self.db["comment_replies"]
            self.auto_reply_logs_collection = self.db["auto_reply_logs"]
            self.scrape_urls = self.db["scrape_urls"]
            
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
            # User indexes
            await self.users_collection.create_index("email", unique=True)
            await self.users_collection.create_index("created_at")
            
            # YouTube credentials indexes
            await self.youtube_credentials_collection.create_index("user_id", unique=True)
            await self.youtube_credentials_collection.create_index("channel_id")
            
            # Automation config indexes
            await self.automation_configs_collection.create_index("user_id")
            await self.automation_configs_collection.create_index("config_type")
            await self.automation_configs_collection.create_index([("config_type", 1), ("enabled", 1)])
            
            # Upload history indexes
            await self.upload_history_collection.create_index("user_id")
            await self.upload_history_collection.create_index("video_id", unique=True)
            await self.upload_history_collection.create_index("upload_date")
            
            # Analytics indexes
            await self.analytics_collection.create_index("user_id")
            await self.analytics_collection.create_index("date")
            
            # Scheduled posts indexes
            await self.scheduled_posts_collection.create_index("user_id")
            await self.scheduled_posts_collection.create_index("scheduled_for")
            await self.scheduled_posts_collection.create_index("status")
            await self.scheduled_posts_collection.create_index([
                ("user_id", 1),
                ("status", 1),
                ("scheduled_for", 1)
            ])
            
            # Comment replies indexes
            await self.comment_replies_collection.create_index("user_id")
            await self.comment_replies_collection.create_index("comment_id")
            await self.comment_replies_collection.create_index("video_id")
            await self.comment_replies_collection.create_index("reply_id", unique=True)
            
            # Auto-reply logs indexes
            await self.auto_reply_logs_collection.create_index("user_id")
            await self.auto_reply_logs_collection.create_index("video_id")
            await self.auto_reply_logs_collection.create_index("processed_at")
            await self.auto_reply_logs_collection.create_index([("user_id", 1), ("processed_at", -1)])
            
            logger.info("YouTube database indexes created")
            
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("YouTube database connection closed")

    # ============================================================================
    # USER MANAGEMENT
    # ============================================================================

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user_data["created_at"] = datetime.now()
            user_data["youtube_connected"] = False
            user_data["automation_enabled"] = False
            user_data["auto_reply_enabled"] = False
            
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

    # ============================================================================
    # YOUTUBE CREDENTIALS MANAGEMENT
    # ============================================================================

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
                "automation_enabled": False,
                "auto_reply_enabled": False
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

    # ============================================================================
    # AUTOMATION CONFIGURATION
    # ============================================================================

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
            
            # Update user automation status
            update_data = {"automation_enabled": True}
            if config_type == "auto_reply":
                update_data["auto_reply_enabled"] = True
            
            await self.update_user(user_id, update_data)
            
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
    
    async def get_all_automation_configs_by_type(self, config_type: str) -> List[Dict[str, Any]]:
        """Get all automation configs of a specific type"""
        try:
            configs = []
            async for config in self.automation_configs_collection.find({
                "config_type": config_type,
                "enabled": True
            }):
                configs.append(config)
            return configs
        except Exception as e:
            logger.error(f"Failed to get automation configs: {e}")
            return []
    
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
            
            # Update user status
            if config_type == "auto_reply":
                await self.update_user(user_id, {"auto_reply_enabled": False})
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Disable automation failed: {e}")
            return False

    # ============================================================================
    # COMMENT REPLY MANAGEMENT
    # ============================================================================

    async def log_comment_reply(self, user_id: str, reply_data: Dict[str, Any]) -> bool:
        """Log a comment reply to database"""
        try:
            reply_doc = {
                "user_id": user_id,
                "comment_id": reply_data.get("comment_id"),
                "video_id": reply_data.get("video_id"),
                "reply_id": reply_data.get("reply_id"),
                "reply_text": reply_data.get("reply_text"),
                "original_comment": reply_data.get("original_comment"),
                "comment_author": reply_data.get("comment_author"),
                "reply_type": reply_data.get("reply_type", "manual"),
                "language_detected": reply_data.get("language_detected", "english"),
                "ai_service_used": reply_data.get("ai_service_used"),
                "emotion_detected": reply_data.get("emotion_detected"),
                "reply_generated_at": reply_data.get("reply_generated_at", datetime.now()),
                "reply_posted_at": datetime.now(),
                "created_at": datetime.now()
            }
            
            await self.comment_replies_collection.insert_one(reply_doc)
            logger.info(f"Comment reply logged for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log comment reply: {e}")
            return False

    async def get_comment_reply_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get comment reply history for user"""
        try:
            replies = []
            async for reply in self.comment_replies_collection.find(
                {"user_id": user_id}
            ).sort("reply_posted_at", -1).limit(limit):
                replies.append(reply)
            return replies
        except Exception as e:
            logger.error(f"Get comment reply history failed: {e}")
            return []

    async def get_reply_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get reply statistics for user"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Total replies
            total_replies = await self.comment_replies_collection.count_documents({
                "user_id": user_id,
                "reply_posted_at": {"$gte": start_date}
            })
            
            # Auto vs manual replies
            auto_replies = await self.comment_replies_collection.count_documents({
                "user_id": user_id,
                "reply_type": "auto",
                "reply_posted_at": {"$gte": start_date}
            })
            
            manual_replies = total_replies - auto_replies
            
            # Language breakdown
            language_pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "reply_posted_at": {"$gte": start_date}
                }},
                {"$group": {
                    "_id": "$language_detected",
                    "count": {"$sum": 1}
                }}
            ]
            
            language_stats = {}
            async for lang_stat in self.comment_replies_collection.aggregate(language_pipeline):
                language_stats[lang_stat["_id"]] = lang_stat["count"]
            
            return {
                "total_replies": total_replies,
                "auto_replies": auto_replies,
                "manual_replies": manual_replies,
                "language_breakdown": language_stats,
                "period_days": days,
                "auto_reply_percentage": (auto_replies / total_replies * 100) if total_replies > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Get reply stats failed: {e}")
            return {
                "total_replies": 0,
                "auto_replies": 0,
                "manual_replies": 0,
                "language_breakdown": {},
                "period_days": days,
                "auto_reply_percentage": 0
            }

    async def log_auto_reply_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Log auto-reply processing session"""
        try:
            session_doc = {
                "user_id": user_id,
                "session_id": session_data.get("session_id", str(ObjectId())),
                "videos_processed": session_data.get("videos_processed", []),
                "comments_found": session_data.get("comments_found", 0),
                "replies_generated": session_data.get("replies_generated", 0),
                "replies_posted": session_data.get("replies_posted", 0),
                "errors_encountered": session_data.get("errors_encountered", []),
                "processing_duration": session_data.get("processing_duration", 0),
                "processed_at": datetime.now(),
                "config_used": session_data.get("config_used", {})
            }
            
            await self.auto_reply_logs_collection.insert_one(session_doc)
            return True
            
        except Exception as e:
            logger.error(f"Failed to log auto-reply session: {e}")
            return False

    async def check_comment_already_replied(self, user_id: str, comment_id: str) -> bool:
        """Check if we already replied to a specific comment"""
        try:
            reply = await self.comment_replies_collection.find_one({
                "user_id": user_id,
                "comment_id": comment_id
            })
            return reply is not None
        except Exception as e:
            logger.error(f"Check comment replied failed: {e}")
            return False

    # ============================================================================
    # CONTENT LOGGING
    # ============================================================================

    async def log_community_post(self, user_id: str, post_data: Dict[str, Any]) -> bool:
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
            
            await self.community_posts_collection.insert_one(post_doc)
            logger.info(f"Community post logged for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log community post: {e}")
            return False

    async def log_video_upload(self, user_id: str, video_data: Dict[str, Any]) -> bool:
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
                "thumbnail_uploaded": video_data.get("thumbnail_uploaded", False),
                "upload_status": "completed",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            await self.video_uploads_collection.insert_one(video_doc)
            logger.info(f"Video upload logged for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log video upload: {e}")
            return False

    # ============================================================================
    # UPLOAD HISTORY & STATS
    # ============================================================================

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
    
    async def store_product_promo(self, user_id: str, product_data: dict) -> bool:
        """Store product promotion data"""
        try:
            if not self.db:
                logger.error("Database not connected")
                return False
            
            promo_doc = {
                "user_id": user_id,
                "product_data": product_data,
                "video_id": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "status": "pending"
            }
            
            result = await self.db.product_promos.insert_one(promo_doc)
            logger.info(f"Product promo stored with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store product promo: {e}")
            return False
    
    async def get_product_promos_by_user(self, user_id: str, status: str = None) -> list:
        """Get product promos for a user"""
        try:
            if not self.db:
                return []
            
            query = {"user_id": user_id}
            if status:
                query["status"] = status
            
            cursor = self.db.product_promos.find(query).sort("created_at", -1)
            promos = []
            async for promo in cursor:
                promos.append(promo)
            
            return promos
            
        except Exception as e:
            logger.error(f"Failed to get product promos: {e}")
            return []

    # ============================================================================
    # ANALYTICS
    # ============================================================================

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

    # ============================================================================
    # SCHEDULED POSTS
    # ============================================================================

    async def store_scheduled_post(self, user_id: str, video_data: Dict[str, Any], scheduled_for: datetime) -> bool:
        """Store a scheduled video post"""
        try:
            if self.scheduled_posts_collection is None:
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
            return False

    async def get_due_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Get posts scheduled to be published now"""
        try:
            current_time = datetime.now()
            time_window_start = current_time - timedelta(minutes=1)
            time_window_end = current_time + timedelta(minutes=2)
            
            logger.info(f"Querying scheduled posts between {time_window_start.strftime('%H:%M')} and {time_window_end.strftime('%H:%M')}")
            
            if self.scheduled_posts_collection is None:
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
            
            if not posts:
                logger.debug(f"No posts due between {time_window_start.strftime('%H:%M')} and {time_window_end.strftime('%H:%M')}")
            
            return posts
            
        except Exception as e:
            logger.error(f"get_due_scheduled_posts failed: {e}")
            return []
    
    async def update_scheduled_post_status(self, post_id, status: str, error_message: str = None) -> bool:
        """Update scheduled post status"""
        try:
            if self.scheduled_posts_collection is None:
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

    # ============================================================================
    # GENERIC CREDENTIAL METHODS
    # ============================================================================

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

    # ============================================================================
    # HEALTH CHECK
    # ============================================================================

    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            await self.client.admin.command('ping')
            
            users_count = await self.users_collection.count_documents({})
            credentials_count = await self.youtube_credentials_collection.count_documents({})
            configs_count = await self.automation_configs_collection.count_documents({})
            replies_count = await self.comment_replies_collection.count_documents({})
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": {
                    "users": users_count,
                    "youtube_credentials": credentials_count,
                    "automation_configs": configs_count,
                    "comment_replies": replies_count
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

    # ============================================================================
    # UTILITY METHODS FOR AUTO-REPLY
    # ============================================================================

    async def get_recent_comments_for_processing(self, user_id: str, video_ids: List[str], hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get recent comments that need auto-reply processing"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            processed_comments = []
            async for log in self.auto_reply_logs_collection.find({
                "user_id": user_id,
                "processed_at": {"$gte": cutoff_time}
            }):
                processed_comments.extend(log.get("comments_processed", []))
            
            return processed_comments
            
        except Exception as e:
            logger.error(f"Get recent comments failed: {e}")
            return []

    async def mark_comment_as_processed(self, user_id: str, comment_id: str, video_id: str, processing_result: Dict[str, Any]) -> bool:
        """Mark a comment as processed for auto-reply"""
        try:
            process_doc = {
                "user_id": user_id,
                "comment_id": comment_id,
                "video_id": video_id,
                "processed_at": datetime.now(),
                "processing_result": processing_result,
                "reply_successful": processing_result.get("success", False),
                "error_message": processing_result.get("error"),
                "ai_service_used": processing_result.get("ai_service"),
                "reply_text": processing_result.get("reply_text")
            }
            
            await self.auto_reply_logs_collection.insert_one(process_doc)
            return True
            
        except Exception as e:
            logger.error(f"Mark comment processed failed: {e}")
            return False

    async def get_auto_reply_rate_limit(self, user_id: str, hours: int = 1) -> Dict[str, int]:
        """Check auto-reply rate limits for user"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_replies = await self.comment_replies_collection.count_documents({
                "user_id": user_id,
                "reply_type": "auto",
                "reply_posted_at": {"$gte": cutoff_time}
            })
            
            config = await self.get_automation_config(user_id, "auto_reply")
            max_per_hour = config.get("config_data", {}).get("max_replies_per_hour", 10) if config else 10
            
            return {
                "replies_sent": recent_replies,
                "max_allowed": max_per_hour,
                "remaining": max(0, max_per_hour - recent_replies),
                "can_send": recent_replies < max_per_hour
            }
            
        except Exception as e:
            logger.error(f"Get rate limit failed: {e}")
            return {
                "replies_sent": 0,
                "max_allowed": 10,
                "remaining": 10,
                "can_send": True
            }

    async def cleanup_old_logs(self, days_to_keep: int = 30) -> bool:
        """Clean up old logs and data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            auto_reply_result = await self.auto_reply_logs_collection.delete_many({
                "processed_at": {"$lt": cutoff_date}
            })
            
            comment_reply_result = await self.comment_replies_collection.delete_many({
                "reply_posted_at": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleanup completed: {auto_reply_result.deleted_count} auto-reply logs, {comment_reply_result.deleted_count} comment replies deleted")
            return True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

    # ============================================================================
    # BACKUP AND RESTORE METHODS
    # ============================================================================

    async def backup_user_data(self, user_id: str) -> Dict[str, Any]:
        """Create backup of user's data"""
        try:
            backup_data = {
                "user_id": user_id,
                "backup_created_at": datetime.now(),
                "data": {}
            }
            
            user = await self.get_user_by_id(user_id)
            if user:
                backup_data["data"]["user_profile"] = user
            
            credentials = await self.get_youtube_credentials(user_id)
            if credentials:
                safe_credentials = {
                    "channel_info": credentials.get("channel_info"),
                    "created_at": credentials.get("created_at"),
                    "scopes": credentials.get("scopes")
                }
                backup_data["data"]["credentials"] = safe_credentials
            
            configs = await self.get_all_automation_configs(user_id)
            backup_data["data"]["automation_configs"] = configs
            
            uploads = await self.get_upload_history(user_id, 100)
            backup_data["data"]["upload_history"] = uploads
            
            reply_stats = await self.get_reply_stats(user_id, 90)
            backup_data["data"]["reply_stats"] = reply_stats
            
            return backup_data
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {"error": str(e)}

    # ============================================================================
    # ANALYTICS AGGREGATION METHODS
    # ============================================================================

    async def get_platform_wide_stats(self) -> Dict[str, Any]:
        """Get platform-wide statistics"""
        try:
            total_users = await self.users_collection.count_documents({})
            youtube_connected = await self.users_collection.count_documents({"youtube_connected": True})
            auto_reply_enabled = await self.users_collection.count_documents({"auto_reply_enabled": True})
            
            thirty_days_ago = datetime.now() - timedelta(days=30)
            total_replies = await self.comment_replies_collection.count_documents({
                "reply_posted_at": {"$gte": thirty_days_ago}
            })
            
            auto_replies = await self.comment_replies_collection.count_documents({
                "reply_type": "auto",
                "reply_posted_at": {"$gte": thirty_days_ago}
            })
            
            return {
                "total_users": total_users,
                "youtube_connected_users": youtube_connected,
                "auto_reply_enabled_users": auto_reply_enabled,
                "total_replies_30_days": total_replies,
                "auto_replies_30_days": auto_replies,
                "manual_replies_30_days": total_replies - auto_replies,
                "connection_rate": (youtube_connected / total_users * 100) if total_users > 0 else 0,
                "auto_reply_adoption": (auto_reply_enabled / youtube_connected * 100) if youtube_connected > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Get platform stats failed: {e}")
            return {}

    # ============================================================================
    # MIGRATION AND MAINTENANCE
    # ============================================================================

    async def migrate_legacy_data(self) -> bool:
        """Migrate legacy data to new schema"""
        try:
            logger.info("Starting data migration...")
            
            await self.users_collection.update_many(
                {"auto_reply_enabled": {"$exists": False}},
                {"$set": {"auto_reply_enabled": False}}
            )
            
            logger.info("Data migration completed")
            return True
            
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            return False

    async def optimize_database(self) -> bool:
        """Optimize database performance"""
        try:
            await self._create_indexes()
            
            logger.info("Database optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return False

    # ============================================================================
    # AUTOMATION LOGGING
    # ============================================================================

    async def get_automation_posts_count(self, user_id: str, date) -> int:
        """Get number of automation posts for a specific date"""
        try:
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            count = await self.db.automation_logs.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day},
                "success": True
            })
            
            return count
        except Exception as e:
            logger.error(f"Get automation posts count failed: {e}")
            return 0
    
    async def log_automation_post(self, user_id: str, post_data: dict) -> bool:
        """Log automated post to database"""
        try:
            log_doc = {
                "user_id": user_id,
                "product_url": post_data.get("product_url"),
                "video_id": post_data.get("video_id"),
                "timestamp": post_data.get("timestamp", datetime.now()),
                "success": post_data.get("success", True),
                "error": post_data.get("error")
            }
            
            await self.db.automation_logs.insert_one(log_doc)
            return True
        except Exception as e:
            logger.error(f"Log automation post failed: {e}")
            return False

    # ============================================================================
    # PRODUCT URL QUEUE MANAGEMENT
    # ============================================================================

    async def save_scrape_url(self, user_id: str, url: str) -> bool:
        """Save website URL to scrape (replaces any existing URL)"""
        try:
            await self.scrape_urls.update_one(
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
            url_doc = await self.scrape_urls.find_one({"user_id": user_id})
            return url_doc if url_doc else None
        except Exception as e:
            logger.error(f"❌ Get scrape URL failed: {e}")
            return None

    async def delete_scrape_url(self, user_id: str) -> bool:
        """Delete scrape URL"""
        try:
            await self.scrape_urls.delete_one({"user_id": user_id})
            logger.info(f"✅ Scrape URL deleted for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Delete scrape URL failed: {e}")
            return False

    async def update_scrape_progress(self, user_id: str, total_found: int, processed: int) -> bool:
        """Update scraping progress"""
        try:
            await self.scrape_urls.update_one(
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
            url_doc = await self.scrape_urls.find_one({"user_id": user_id})
            
            if not url_doc:
                return None
            
            if url_doc.get("products_processed", 0) >= url_doc.get("total_products_found", 0):
                await self.scrape_urls.update_one(
                    {"user_id": user_id},
                    {"$set": {"products_processed": 0}}
                )
            
            return url_doc
            
        except Exception as e:
            logger.error(f"❌ Get next product failed: {e}")
            return None


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

youtube_db_manager = None

def get_youtube_database() -> YouTubeDatabaseManager:
    """Get global YouTube database instance"""
    global youtube_db_manager
    if not youtube_db_manager:
        youtube_db_manager = YouTubeDatabaseManager()
    return youtube_db_manager

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def convert_objectid_to_string(data):
    """Convert ObjectId fields to strings for JSON serialization"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (dict, list)):
                data[key] = convert_objectid_to_string(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = convert_objectid_to_string(item)
    return data

def validate_user_id(user_id: str) -> bool:
    """Validate user ID format"""
    try:
        if len(user_id) < 8:
            return False
        return True
    except Exception:
        return False

# ============================================================================
# ERROR HANDLING DECORATORS
# ============================================================================

def handle_db_errors(func):
    """Decorator for database error handling"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConnectionFailure as e:
            logger.error(f"Database connection failed in {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            return None
    return wrapper


# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_PAGINATION_LIMIT = 50
MAX_PAGINATION_LIMIT = 1000
DEFAULT_ANALYTICS_PERIOD = 30
MAX_ANALYTICS_PERIOD = 365
AUTO_REPLY_RATE_LIMIT_WINDOW = 1  # hours
DEFAULT_AUTO_REPLY_LIMIT = 10  # per hour