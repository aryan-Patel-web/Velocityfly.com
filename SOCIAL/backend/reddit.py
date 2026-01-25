"""
Complete Reddit OAuth Connector with REAL WORKING Reddit API Integration
Handles OAuth flow, token management, and ACTUAL Reddit posting
Fixed all Reddit API response handling and error management
"""

import os
import requests
import base64
import json
import logging
import time
import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class RedditOAuthConnector:
    """Complete Reddit OAuth connector with working Reddit API posting"""
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or self._load_config()
        self.is_configured = self._validate_config()
        
        # Reddit API endpoints
        self.auth_url = "https://www.reddit.com/api/v1/authorize"
        self.token_url = "https://www.reddit.com/api/v1/access_token"
        self.api_base = "https://oauth.reddit.com"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests
        
        logger.info(f"Reddit connector initialized: configured={self.is_configured}")
    
    def _load_config(self) -> Dict[str, str]:
        """Load Reddit configuration from environment"""
        return {
            'REDDIT_CLIENT_ID': os.getenv("REDDIT_CLIENT_ID", ""),
            'REDDIT_CLIENT_SECRET': os.getenv("REDDIT_CLIENT_SECRET", ""),
            'REDDIT_REDIRECT_URI': os.getenv("REDDIT_REDIRECT_URI", "https://velocityfly.onrender.com/api/oauth/reddit/callback"),
            'REDDIT_USER_AGENT': os.getenv("REDDIT_USER_AGENT", "RedditAutomationPlatform/1.0")
        }
    
    def _validate_config(self) -> bool:
        """Validate Reddit configuration"""
        required_keys = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
        for key in required_keys:
            if not self.config.get(key):
                logger.error(f"Missing required config: {key}")
                return False
        return True
    
    def generate_oauth_url(self, state: str = None) -> Dict[str, Any]:
        """Generate Reddit OAuth authorization URL"""
        if not self.is_configured:
            return {"success": False, "error": "Reddit not properly configured"}
        
        params = {
            'client_id': self.config['REDDIT_CLIENT_ID'],
            'response_type': 'code',
            'state': state or 'default_state',
            'redirect_uri': self.config['REDDIT_REDIRECT_URI'],
            'duration': 'permanent',
            'scope': 'identity submit edit read'
        }
        
        oauth_url = f"{self.auth_url}?{urlencode(params)}"
        
        return {
            "success": True,
            "authorization_url": oauth_url,
            "state": params['state']
        }
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.is_configured:
            return {"success": False, "error": "Reddit not configured"}
        
        try:
            # Prepare authentication
            auth_string = f"{self.config['REDDIT_CLIENT_ID']}:{self.config['REDDIT_CLIENT_SECRET']}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': self.config['REDDIT_USER_AGENT'],
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.config['REDDIT_REDIRECT_URI']
            }
            
            response = requests.post(
                self.token_url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Get user info
                user_info = await self._get_reddit_user_info(token_data.get('access_token'))
                
                return {
                    "success": True,
                    "access_token": token_data.get('access_token'),
                    "refresh_token": token_data.get('refresh_token'),
                    "expires_in": token_data.get('expires_in', 3600),
                    "user_info": user_info
                }
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_reddit_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Reddit user information"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': self.config['REDDIT_USER_AGENT']
            }
            
            response = requests.get(
                f"{self.api_base}/api/v1/me",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "username": user_data.get('name', 'Unknown'),
                    "id": user_data.get('id', ''),
                    "created_utc": user_data.get('created_utc'),
                    "comment_karma": user_data.get('comment_karma', 0),
                    "link_karma": user_data.get('link_karma', 0)
                }
            else:
                logger.warning(f"User info request failed: {response.status_code}")
                return {"username": "Unknown", "id": ""}
                
        except Exception as e:
            logger.error(f"Get user info error: {e}")
            return {"username": "Unknown", "id": ""}
    
    async def post_content_with_token(self, **kwargs) -> Dict[str, Any]:
        """
        Post content to Reddit using access token - FIXED VERSION
        This is the main method that was causing posting failures
        """
        try:
            access_token = kwargs.get('access_token')
            subreddit_name = kwargs.get('subreddit_name')
            title = kwargs.get('title')
            content = kwargs.get('content')
            content_type = kwargs.get('content_type', 'text')
            
            if not all([access_token, subreddit_name, title, content]):
                return {
                    "success": False,
                    "error": "Missing required parameters"
                }
            
            # Rate limiting
            await self._wait_for_rate_limit()
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': self.config['REDDIT_USER_AGENT'],
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Prepare post data according to Reddit API specifications
            post_data = {
                'api_type': 'json',
                'kind': 'self',  # Text post
                'sr': subreddit_name,
                'title': title[:300],  # Reddit title limit
                'text': content,
                'submit_type': 'text',
                'sendreplies': True,
                'validate_on_submit': True
            }
            
            logger.info(f"Posting to Reddit API: r/{subreddit_name}")
            logger.info(f"Post title: {title[:50]}...")
            
            # Make the API request to Reddit
            response = requests.post(
                f"{self.api_base}/api/submit",
                headers=headers,
                data=post_data,
                timeout=30
            )
            
            logger.info(f"Reddit API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    logger.info(f"Reddit API response: {json.dumps(response_data, indent=2)}")
                    
                    # Parse Reddit's response format
                    if 'json' in response_data:
                        json_data = response_data['json']
                        
                        # Check for errors in Reddit's response
                        if 'errors' in json_data and json_data['errors']:
                            error_msg = json_data['errors'][0][1] if json_data['errors'][0] else "Unknown Reddit error"
                            logger.error(f"Reddit API error: {error_msg}")
                            return {
                                "success": False,
                                "error": f"Reddit API error: {error_msg}",
                                "reddit_errors": json_data['errors']
                            }
                        
                        # Success - extract post information
                        if 'data' in json_data and 'things' in json_data['data']:
                            things = json_data['data']['things']
                            if things and len(things) > 0:
                                post_data_response = things[0]['data']
                                post_id = post_data_response.get('id', '')
                                post_name = post_data_response.get('name', '')
                                post_url = post_data_response.get('url', f"https://reddit.com/r/{subreddit_name}/comments/{post_id}")
                                
                                logger.info(f"✅ POST SUCCESS: {post_url}")
                                
                                return {
                                    "success": True,
                                    "post_id": post_id,
                                    "post_name": post_name,
                                    "post_url": post_url,
                                    "subreddit": subreddit_name,
                                    "title": title,
                                    "message": "Post submitted successfully to Reddit"
                                }
                    
                    # If we get here, the response format was unexpected
                    logger.warning(f"Unexpected Reddit response format: {response_data}")
                    return {
                        "success": False,
                        "error": "Unexpected Reddit API response format",
                        "response_data": response_data
                    }
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON response from Reddit: {response.text}")
                    return {
                        "success": False,
                        "error": "Invalid JSON response from Reddit",
                        "response_text": response.text
                    }
            
            elif response.status_code == 401:
                logger.error("Reddit API authentication failed - token may be expired")
                return {
                    "success": False,
                    "error": "Authentication failed - Reddit token may be expired",
                    "status_code": 401
                }
            
            elif response.status_code == 403:
                logger.error(f"Reddit API forbidden - may be banned from r/{subreddit_name}")
                return {
                    "success": False,
                    "error": f"Forbidden - may be banned from r/{subreddit_name} or insufficient permissions",
                    "status_code": 403
                }
            
            elif response.status_code == 429:
                logger.error("Reddit API rate limit exceeded")
                return {
                    "success": False,
                    "error": "Rate limit exceeded - please wait before posting again",
                    "status_code": 429
                }
            
            else:
                logger.error(f"Reddit API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Reddit API error: HTTP {response.status_code}",
                    "status_code": response.status_code,
                    "response_text": response.text[:500]
                }
                
        except requests.exceptions.Timeout:
            logger.error("Reddit API request timeout")
            return {
                "success": False,
                "error": "Request timeout - Reddit API did not respond in time"
            }
        
        except requests.exceptions.ConnectionError:
            logger.error("Reddit API connection error")
            return {
                "success": False,
                "error": "Connection error - unable to reach Reddit API"
            }
        
        except Exception as e:
            logger.error(f"Unexpected error in Reddit posting: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def _wait_for_rate_limit(self):
        """Implement rate limiting to avoid Reddit API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def test_reddit_connection(self, access_token: str) -> Dict[str, Any]:
        """Test Reddit API connection"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': self.config['REDDIT_USER_AGENT']
            }
            
            response = requests.get(
                f"{self.api_base}/api/v1/me",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "Reddit connection verified",
                    "username": user_data.get('name', 'Unknown'),
                    "karma": {
                        "comment": user_data.get('comment_karma', 0),
                        "link": user_data.get('link_karma', 0)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Reddit API test failed: HTTP {response.status_code}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Reddit connection test failed: {e}")
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }
    
    async def get_user_subreddits(self, access_token: str) -> Dict[str, Any]:
        """Get user's subscribed subreddits"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': self.config['REDDIT_USER_AGENT']
            }
            
            response = requests.get(
                f"{self.api_base}/subreddits/mine/subscriber",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                subreddits = []
                
                if 'data' in data and 'children' in data['data']:
                    for child in data['data']['children']:
                        if 'data' in child:
                            sub_data = child['data']
                            subreddits.append({
                                "name": sub_data.get('display_name', ''),
                                "title": sub_data.get('title', ''),
                                "subscribers": sub_data.get('subscribers', 0),
                                "public_description": sub_data.get('public_description', '')
                            })
                
                return {
                    "success": True,
                    "subreddits": subreddits,
                    "count": len(subreddits)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get subreddits: HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Get user subreddits failed: {e}")
            return {
                "success": False,
                "error": f"Failed to get subreddits: {str(e)}"
            }
    
    def get_posting_guidelines(self, subreddit: str) -> Dict[str, Any]:
        """Get posting guidelines for a subreddit"""
        guidelines = {
            "test": {
                "rules": ["No spam", "Test posts welcome"],
                "posting_allowed": True,
                "difficulty": "easy"
            },
            "casualconversation": {
                "rules": ["Be respectful", "No promotional content", "Keep it casual"],
                "posting_allowed": True,
                "difficulty": "easy"
            },
            "self": {
                "rules": ["Personal posts only", "No external links in title"],
                "posting_allowed": True,
                "difficulty": "easy"
            },
            "blog": {
                "rules": ["Original content preferred", "No excessive self-promotion"],
                "posting_allowed": True,
                "difficulty": "medium"
            }
        }
        
        return guidelines.get(subreddit.lower(), {
            "rules": ["Check subreddit rules before posting"],
            "posting_allowed": True,
            "difficulty": "unknown"
        })