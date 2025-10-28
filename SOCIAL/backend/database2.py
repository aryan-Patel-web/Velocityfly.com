"""
Multi-Platform Database Manager - YouTube, WhatsApp, Instagram, Facebook
Enhanced database operations with multi-user support and platform-specific data handling
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
import json
import bcrypt
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class MultiPlatformDatabaseManager:
    """Enhanced database manager for multi-platform social media automation"""
    
    def __init__(self, mongodb_uri: str, encryption_key: str = None):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.db = None
        self.encryption_key = encryption_key or os.getenv("TOKEN_ENCRYPTION_KEY", "default_key_change_this")
        self.cipher_suite = Fernet(self._ensure_key_format(self.encryption_key))
        
        # Collection names
        self.collections = {
            'users': 'users',
            'platform_tokens': 'platform_tokens',  # Unified token storage
            'youtube_data': 'youtube_data',
            'whatsapp_data': 'whatsapp_data', 
            'instagram_data': 'instagram_data',
            'facebook_data': 'facebook_data',
            'automation_configs': 'automation_configs',
            'content_history': 'content_history',
            'analytics_data': 'analytics_data',
            'campaign_data': 'campaign_data'
        }
    
    def _ensure_key_format(self, key: str) -> bytes:
        """Ensure encryption key is in proper format"""
        try:
            if len(key) == 32:
                import base64
                return base64.urlsafe_b64encode(key.encode()[:32])
            elif len(key) == 44:  # Already base64 encoded
                return key.encode()
            else:
                # Generate a new key
                return Fernet.generate_key()
        except Exception:
            return Fernet.generate_key()
    
    async def connect(self) -> bool:
        """Connect to MongoDB database"""
        try:
            self.client = AsyncIOMotorClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                maxPoolSize=50
            )
            
            self.db = self.client.social_automation
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("Multi-platform database connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from database"""
        try:
            if self.client:
                self.client.close()
            logger.info("Database disconnected")
            return True
        except Exception as e:
            logger.error(f"Database disconnect failed: {e}")
            return False
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            collections_indexes = {
                'users': [
                    [("email", 1)],
                    [("created_at", -1)]
                ],
                'platform_tokens': [
                    [("user_id", 1), ("platform", 1)],
                    [("expires_at", 1)],
                    [("is_active", 1)]
                ],
                'automation_configs': [
                    [("user_id", 1), ("platform", 1), ("config_type", 1)],
                    [("enabled", 1)],
                    [("created_at", -1)]
                ],
                'content_history': [
                    [("user_id", 1), ("platform", 1)],
                    [("created_at", -1)],
                    [("success", 1)]
                ],
                'analytics_data': [
                    [("user_id", 1), ("platform", 1)],
                    [("date", -1)],
                    [("metric_type", 1)]
                ]
            }
            
            for collection_name, indexes in collections_indexes.items():
                collection = self.db[collection_name]
                for index in indexes:
                    try:
                        await collection.create_index(index, background=True)
                    except Exception as e:
                        logger.warning(f"Index creation failed for {collection_name}: {e}")
                        
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
    


    # User Management
    async def register_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register new user"""
        try:
            # Check if user exists
            existing_user = await self.db.users.find_one({"email": email})
            if existing_user:
                return {
                    "success": False,
                    "error": "User already exists",
                    "message": "An account with this email already exists"
                }
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user document
            user_doc = {
                "email": email,
                "name": name,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True,
                "platforms": {
                    "youtube": {"connected": False, "connected_at": None},
                    "whatsapp": {"connected": False, "connected_at": None},
                    "instagram": {"connected": False, "connected_at": None},
                    "facebook": {"connected": False, "connected_at": None}
                },
                "subscription": {
                    "plan": "free",
                    "expires_at": None
                }
            }
            
            result = await self.db.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
            
            # Generate JWT token
            token_payload = {
                "user_id": user_id,
                "email": email,
                "name": name,
                "exp": datetime.utcnow() + timedelta(days=30)
            }
            
            token = jwt.encode(token_payload, self.encryption_key, algorithm="HS256")
            
            logger.info(f"User registered successfully: {email}")
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "name": name,
                "token": token,
                "message": "User registered successfully"
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            # Find user
            user = await self.db.users.find_one({"email": email, "is_active": True})
            if not user:
                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "message": "Email or password is incorrect"
                }
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "message": "Email or password is incorrect"
                }
            
            user_id = str(user['_id'])
            
            # Generate JWT token
            token_payload = {
                "user_id": user_id,
                "email": user['email'],
                "name": user['name'],
                "exp": datetime.utcnow() + timedelta(days=30)
            }
            
            token = jwt.encode(token_payload, self.encryption_key, algorithm="HS256")
            
            # Update last login
            await self.db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            logger.info(f"User logged in successfully: {email}")
            
            return {
                "success": True,
                "user_id": user_id,
                "email": user['email'],
                "name": user['name'],
                "token": token,
                "platforms": user.get('platforms', {}),
                "message": "Login successful"
            }
            
        except Exception as e:
            logger.error(f"User login failed: {e}")
            return {"success": False, "error": str(e)}
        

        
    
    async def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by JWT token"""
        try:
            # Decode token
            payload = jwt.decode(token, self.encryption_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            # Get user from database
            from bson import ObjectId
            user = await self.db.users.find_one({"_id": ObjectId(user_id), "is_active": True})
            
            if user:
                return {
                    "id": str(user['_id']),
                    "email": user['email'],
                    "name": user['name'],
                    "platforms": user.get('platforms', {}),
                    "subscription": user.get('subscription', {})
                }
                
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token provided")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token provided")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            
        return None
    
    # Platform Token Management
    async def store_platform_tokens(
        self,
        user_id: str,
        platform: str,
        token_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store encrypted platform tokens"""
        try:
            # Encrypt sensitive token data
            encrypted_tokens = {}
            for key, value in token_data.items():
                if key in ['access_token', 'refresh_token', 'client_secret']:
                    encrypted_tokens[key] = self.cipher_suite.encrypt(str(value).encode()).decode()
                else:
                    encrypted_tokens[key] = value
            
            # Prepare token document
            token_doc = {
                "user_id": user_id,
                "platform": platform,
                "token_data": encrypted_tokens,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "expires_at": None,
                "is_active": True
            }
            
            # Calculate expiry if available
            if token_data.get('expires_in'):
                token_doc['expires_at'] = datetime.utcnow() + timedelta(seconds=int(token_data['expires_in']))
            
            # Upsert token document
            await self.db.platform_tokens.replace_one(
                {"user_id": user_id, "platform": platform},
                token_doc,
                upsert=True
            )
            
            # Update user platforms status
            from bson import ObjectId
            await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        f"platforms.{platform}.connected": True,
                        f"platforms.{platform}.connected_at": datetime.utcnow(),
                        f"platforms.{platform}.username": token_data.get('username') or token_data.get('channel_name')
                    }
                }
            )
            
            logger.info(f"Platform tokens stored for user {user_id}: {platform}")
            
            return {
                "success": True,
                "message": f"{platform.title()} tokens stored successfully"
            }
            
        except Exception as e:
            logger.error(f"Token storage failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_platform_tokens(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get and decrypt platform tokens"""
        try:
            token_doc = await self.db.platform_tokens.find_one({
                "user_id": user_id,
                "platform": platform,
                "is_active": True
            })
            
            if not token_doc:
                return None
            
            # Check if tokens are expired
            # Check if tokens are expired
            if token_doc.get('expires_at') and token_doc['expires_at'] < datetime.utcnow():
                logger.warning(f"Expired tokens found for user {user_id} on {platform}")
                return None
            
            # Decrypt sensitive token data
            decrypted_tokens = {}
            for key, value in token_doc['token_data'].items():
                if key in ['access_token', 'refresh_token', 'client_secret']:
                    try:
                        decrypted_tokens[key] = self.cipher_suite.decrypt(value.encode()).decode()
                    except Exception:
                        decrypted_tokens[key] = value  # Fallback if not encrypted
                else:
                    decrypted_tokens[key] = value
            
            return {
                "is_valid": True,
                "tokens": decrypted_tokens,
                "created_at": token_doc['created_at'],
                "expires_at": token_doc.get('expires_at')
            }
            
        except Exception as e:
            logger.error(f"Token retrieval failed: {e}")
            return None
    
    async def check_platform_connection(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Check if user has active platform connection"""
        try:
            token_data = await self.get_platform_tokens(user_id, platform)
            
            if token_data and token_data.get('is_valid'):
                tokens = token_data['tokens']
                return {
                    "connected": True,
                    "username": tokens.get('username') or tokens.get('channel_name'),
                    "user_id": tokens.get('user_id') or tokens.get('channel_id'),
                    "connected_at": token_data['created_at'].isoformat() if token_data.get('created_at') else None,
                    "expires_at": token_data['expires_at'].isoformat() if token_data.get('expires_at') else None
                }
            
            return {
                "connected": False,
                "username": None
            }
            
        except Exception as e:
            logger.error(f"Connection status check failed: {e}")
            return {"connected": False, "username": None}
    
    async def revoke_platform_connection(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Revoke platform connection for user"""
        try:
            # Get username before deletion
            token_data = await self.get_platform_tokens(user_id, platform)
            username = None
            if token_data and token_data.get('tokens'):
                username = token_data['tokens'].get('username') or token_data['tokens'].get('channel_name')
            
            # Deactivate tokens
            await self.db.platform_tokens.update_one(
                {"user_id": user_id, "platform": platform},
                {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
            )
            
            # Update user platforms status
            from bson import ObjectId
            await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        f"platforms.{platform}.connected": False,
                        f"platforms.{platform}.disconnected_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Platform connection revoked for user {user_id}: {platform}")
            
            return {
                "success": True,
                "message": f"{platform.title()} connection revoked successfully",
                "username": username
            }
            
        except Exception as e:
            logger.error(f"Connection revocation failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Automation Configuration Management
    async def store_automation_config(
        self,
        user_id: str,
        platform: str,
        config_type: str,
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store automation configuration"""
        try:
            config_doc = {
                "user_id": user_id,
                "platform": platform,
                "config_type": config_type,
                "config_data": config_data,
                "enabled": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Upsert configuration
            await self.db.automation_configs.replace_one(
                {
                    "user_id": user_id,
                    "platform": platform,
                    "config_type": config_type
                },
                config_doc,
                upsert=True
            )
            
            logger.info(f"Automation config stored for user {user_id}: {platform}/{config_type}")
            
            return {
                "success": True,
                "message": f"{platform.title()} {config_type} configuration saved"
            }
            
        except Exception as e:
            logger.error(f"Automation config storage failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_automation_config(
        self,
        user_id: str,
        platform: str,
        config_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get automation configuration"""
        try:
            config_doc = await self.db.automation_configs.find_one({
                "user_id": user_id,
                "platform": platform,
                "config_type": config_type,
                "enabled": True
            })
            
            return config_doc
            
        except Exception as e:
            logger.error(f"Automation config retrieval failed: {e}")
            return None
    
    async def get_all_active_automations(self, config_type: str = None) -> List[Dict[str, Any]]:
        """Get all active automation configurations"""
        try:
            query = {"enabled": True}
            if config_type:
                query["config_type"] = config_type
                
            configs = []
            async for doc in self.db.automation_configs.find(query):
                configs.append(doc)
            
            return configs
            
        except Exception as e:
            logger.error(f"Active automations retrieval failed: {e}")
            return []
    
    # Content History Management
    async def log_content_activity(
        self,
        user_id: str,
        platform: str,
        activity_type: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log content creation/posting activity"""
        try:
            activity_doc = {
                "user_id": user_id,
                "platform": platform,
                "activity_type": activity_type,
                "activity_data": activity_data,
                "success": activity_data.get("success", False),
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            await self.db.content_history.insert_one(activity_doc)
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Content activity logging failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_content_history(
        self,
        user_id: str,
        platform: str = None,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's content history"""
        try:
            query = {
                "user_id": user_id,
                "timestamp": {"$gte": datetime.utcnow() - timedelta(days=days)}
            }
            
            if platform:
                query["platform"] = platform
            
            activities = []
            async for doc in self.db.content_history.find(query).sort("timestamp", -1).limit(limit):
                doc["_id"] = str(doc["_id"])
                activities.append(doc)
            
            return activities
            
        except Exception as e:
            logger.error(f"Content history retrieval failed: {e}")
            return []
    
    # Analytics Data Management
    async def store_analytics_data(
        self,
        user_id: str,
        platform: str,
        metric_type: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store analytics/performance data"""
        try:
            analytics_doc = {
                "user_id": user_id,
                "platform": platform,
                "metric_type": metric_type,
                "metrics": metrics,
                "date": datetime.utcnow().date(),
                "timestamp": datetime.utcnow()
            }
            
            # Upsert daily analytics
            await self.db.analytics_data.replace_one(
                {
                    "user_id": user_id,
                    "platform": platform,
                    "metric_type": metric_type,
                    "date": datetime.utcnow().date()
                },
                analytics_doc,
                upsert=True
            )
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Analytics data storage failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_analytics(
        self,
        user_id: str,
        platform: str = None,
        metric_type: str = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get user's analytics data"""
        try:
            query = {
                "user_id": user_id,
                "date": {"$gte": (datetime.utcnow() - timedelta(days=days)).date()}
            }
            
            if platform:
                query["platform"] = platform
            if metric_type:
                query["metric_type"] = metric_type
            
            analytics = []
            async for doc in self.db.analytics_data.find(query).sort("date", -1):
                doc["_id"] = str(doc["_id"])
                analytics.append(doc)
            
            # Aggregate data
            aggregated = {
                "total_records": len(analytics),
                "platforms": {},
                "summary": {},
                "time_series": analytics
            }
            
            # Group by platform
            for record in analytics:
                platform_name = record["platform"]
                if platform_name not in aggregated["platforms"]:
                    aggregated["platforms"][platform_name] = []
                aggregated["platforms"][platform_name].append(record)
            
            return {
                "success": True,
                "analytics": aggregated,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Analytics data retrieval failed: {e}")
            return {"success": False, "error": str(e)}
    
    # User Dashboard Data
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user"""
        try:
            # Get user info
            from bson import ObjectId
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                return {"error": "User not found"}
            
            # Get platform connections
            platforms = {}
            for platform in ['youtube', 'whatsapp', 'instagram', 'facebook']:
                connection = await self.check_platform_connection(user_id, platform)
                platforms[platform] = connection
            
            # Get recent activity
            recent_activity = await self.get_user_content_history(user_id, days=7, limit=10)
            
            # Get basic analytics
            today = datetime.utcnow().date()
            week_ago = today - timedelta(days=7)
            
            # Count activities by type
            posts_today = len([a for a in recent_activity 
                              if a['timestamp'].date() == today and a['activity_type'] == 'post'])
            
            total_posts = len([a for a in recent_activity if a['activity_type'] == 'post'])
            successful_posts = len([a for a in recent_activity 
                                  if a['activity_type'] == 'post' and a['success']])
            
            dashboard_data = {
                "user_info": {
                    "name": user['name'],
                    "email": user['email'],
                    "member_since": user['created_at'].isoformat() if user.get('created_at') else None,
                    "subscription": user.get('subscription', {})
                },
                "platform_connections": platforms,
                "activity_summary": {
                    "posts_today": posts_today,
                    "total_posts_week": total_posts,
                    "success_rate": (successful_posts / total_posts * 100) if total_posts > 0 else 0,
                    "active_platforms": len([p for p in platforms.values() if p.get('connected')])
                },
                "recent_activity": recent_activity[:5],  # Latest 5 activities
                "quick_stats": {
                    "youtube_connected": platforms.get('youtube', {}).get('connected', False),
                    "whatsapp_connected": platforms.get('whatsapp', {}).get('connected', False),
                    "instagram_connected": platforms.get('instagram', {}).get('connected', False),
                    "facebook_connected": platforms.get('facebook', {}).get('connected', False)
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Dashboard data retrieval failed: {e}")
            return {"error": str(e)}
    
    # Health Check and Maintenance
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            # Test connection
            await self.client.admin.command('ping')
            
            # Get collection counts
            counts = {}
            for collection_name in self.collections.values():
                try:
                    count = await self.db[collection_name].count_documents({})
                    counts[collection_name] = count
                except Exception as e:
                    counts[collection_name] = f"Error: {e}"
            
            # Get recent activity count
            recent_activity_count = await self.db.content_history.count_documents({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            })
            
            return {
                "status": "healthy",
                "database_name": self.db.name,
                "collection_counts": counts,
                "recent_activity_24h": recent_activity_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup_expired_data(self, days_old: int = 90) -> Dict[str, Any]:
        """Clean up old data to maintain database performance"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            cleanup_results = {}
            
            # Clean up old content history
            result = await self.db.content_history.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            cleanup_results["content_history_deleted"] = result.deleted_count
            
            # Clean up old analytics data
            result = await self.db.analytics_data.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            cleanup_results["analytics_deleted"] = result.deleted_count
            
            # Clean up expired tokens
            result = await self.db.platform_tokens.delete_many({
                "expires_at": {"$lt": datetime.utcnow()},
                "is_active": False
            })
            cleanup_results["expired_tokens_deleted"] = result.deleted_count
            
            logger.info(f"Database cleanup completed: {cleanup_results}")
            
            return {
                "success": True,
                "cleanup_results": cleanup_results,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database cleanup failed: {e}")
            return {"success": False, "error": str(e)}