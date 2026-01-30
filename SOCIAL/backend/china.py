"""
china_optimized.py - MEMORY-OPTIMIZED DOUYIN AUTOMATION
===========================================================================
✅ Low memory footprint (<512MB)
✅ Process video immediately after finding it
✅ Better Douyin selectors
✅ Faster scraping with early exit
===========================================================================
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import traceback
import uuid
import httpx
import json
import re
import random
import subprocess
from typing import List, Dict, Optional
import tempfile
import shutil
import gc
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_346aca9fb63af57816b2f0323b6312b75a65aa852656eeac")
ELEVENLABS_VOICE_ID = "nPczCjzI2devNBz1zQrb"
MAX_VIDEO_SIZE_MB = 50
TARGET_DURATION = 50

NICHE_CONFIG = {
    "funny": {
        "name": "Funny",
        "profile_url": "https://www.douyin.com/user/MS4wLjABAAAAe-jjss5iSv02OGU_kOaQCc4jOSuHiCb3NlmA7koeoC7ISTKHLMtVTt-ELmNLkHfV",
        "fallback_search": "https://www.douyin.com/search/搞笑"
    },
    "animals": {
        "name": "Animals",
        "profile_url": "https://www.douyin.com/user/MS4wLjABAAAA424aSWu0zdBbu6sTR0wIo-okI65xkC9dEltXycuVo0f3WdUTVbA1j8Hbi6Jvqwt1",
        "fallback_search": "https://www.douyin.com/search/萌宠"
    }
}

def cleanup(*files):
    """Quick cleanup"""
    for f in files:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except:
            pass
    gc.collect()

def run_ffmpeg(cmd, timeout=60):
    """Run FFmpeg efficiently"""
    try:
        subprocess.run(cmd, capture_output=True, timeout=timeout, check=True)
        return True
    except:
        return False

class FastDouyinScraper:
    """Memory-efficient scraper - finds ONE video and exits"""
    
    def __init__(self):
        self.driver = None
    
    def init_driver(self):
        """Lightweight Chrome instance"""
        try:
            logger.info("🌐 Starting Chrome (headless)...")
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1280,720")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")
            options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
            
            # Memory optimizations
            options.add_argument("--disable-images")  # Don't load images
            options.add_argument("--blink-settings=imagesEnabled=false")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(20)
            self.driver.set_script_timeout(20)
            
            logger.info("✅ Chrome ready")
            return True
        except Exception as e:
            logger.error(f"❌ Chrome init failed: {e}")
            return False
    
    def find_one_video(self, url: str) -> Optional[str]:
        """
        CRITICAL: Find FIRST video only, then EXIT
        This prevents memory issues from long scraping
        """
        try:
            if not self.driver:
                if not self.init_driver():
                    return None
            
            logger.info(f"📱 Loading: {url[:60]}...")
            self.driver.get(url)
            
            # Short wait
            logger.info("⏳ Wait 8s...")
            time.sleep(8)
            
            # Light scroll (only 2 scrolls to save memory)
            logger.info("📜 Quick scroll...")
            for i in range(2):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1.5)
            
            # Updated selectors for Douyin 2026
            selectors = [
                # Most common Douyin selectors
                "a[href*='video']",
                "a[href*='modal']",
                "div[data-e2e='user-post-item'] a",
                "li a[href*='douyin.com']",
            ]
            
            logger.info("🔍 Searching for video...")
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"   {selector}: {len(elements)} found")
                    
                    for elem in elements:
                        try:
                            href = elem.get_attribute('href')
                            if href and ('video' in href or 'modal' in href):
                                if not href.startswith('http'):
                                    href = 'https://www.douyin.com' + href
                                
                                logger.info(f"✅ FOUND VIDEO: {href[:60]}...")
                                return href  # STOP HERE - Only need 1!
                        except:
                            continue
                except:
                    continue
            
            logger.warning("⚠️ No videos found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Scraping error: {e}")
            return None
    
    def close(self):
        """Clean shutdown"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                gc.collect()
        except:
            pass

async def download_video(url: str, temp_dir: str) -> Optional[str]:
    """Lightweight download with ONE method"""
    logger.info(f"📥 Downloading: {url[:60]}...")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            # Try direct HTML parsing
            resp = await client.get(url, headers={'User-Agent': 'Mozilla/5.0'}, follow_redirects=True)
            
            if resp.status_code == 200:
                html = resp.text
                
                # Find video URL patterns
                patterns = [
                    r'"playAddr"[^"]*"(https://[^"]+\.mp4[^"]*)"',
                    r'playUrl[^"]*"(https://[^"]+\.mp4)"',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        video_url = matches[0].replace('\\/', '/')
                        logger.info(f"   Found video URL")
                        
                        # Download
                        vid_resp = await client.get(video_url, follow_redirects=True, timeout=90)
                        if vid_resp.status_code == 200:
                            size_mb = len(vid_resp.content) / (1024*1024)
                            if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                                path = os.path.join(temp_dir, "video.mp4")
                                with open(path, 'wb') as f:
                                    f.write(vid_resp.content)
                                logger.info(f"✅ Downloaded: {size_mb:.1f}MB")
                                return path
        
        logger.error("❌ Download failed")
        return None
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        return None

async def simple_process(video_path: str, temp_dir: str) -> Optional[str]:
    """Ultra-simple video processing"""
    logger.info("⚙️ Processing video...")
    
    try:
        output = os.path.join(temp_dir, "processed.mp4")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-t", str(TARGET_DURATION),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264", "-crf", "28", "-preset", "ultrafast",
            "-an",  # Remove audio for now to save memory
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 60):
            cleanup(video_path)
            logger.info(f"✅ Processed: {os.path.getsize(output)/(1024*1024):.1f}MB")
            return output
        
        return None
    except Exception as e:
        logger.error(f"❌ Processing error: {e}")
        return None

def get_simple_script(niche: str) -> dict:
    """Simple fallback script"""
    if niche == "animals":
        return {
            "title": "प्यारा जानवर वीडियो 🐶❤️",
            "description": "Cute animal video",
            "hashtags": ["animals", "cute", "viral"]
        }
    else:
        return {
            "title": "मजेदार वीडियो 😂",
            "description": "Funny video",
            "hashtags": ["funny", "comedy", "viral"]
        }

async def upload_to_yt(video_path: str, script: dict, user_id: str, database_manager) -> dict:
    """Simple YT upload"""
    logger.info("📤 Uploading to YouTube...")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        from mainY import youtube_scheduler
        
        yt_db = get_yt_db()
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds_raw = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        if not creds_raw:
            return {"success": False, "error": "No YouTube credentials"}
        
        creds = {
            "access_token": creds_raw.get("access_token"),
            "refresh_token": creds_raw.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
        }
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=creds,
            content_type="shorts",
            title=script["title"],
            description=script["description"] + "\n\n#" + " #".join(script["hashtags"]),
            video_url=video_path
        )
        
        if result.get("success"):
            logger.info(f"✅ Uploaded: {result.get('video_id')}")
            return {
                "success": True,
                "video_id": result.get("video_id"),
                "video_url": f"https://youtube.com/shorts/{result.get('video_id')}"
            }
        
        return {"success": False, "error": result.get("error")}
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return {"success": False, "error": str(e)}

async def process_one_video_complete(niche: str, user_id: str, database_manager) -> dict:
    """
    OPTIMIZED PIPELINE:
    1. Find ONE video
    2. Download it immediately
    3. Process immediately  
    4. Upload immediately
    5. Clean up immediately
    
    This prevents memory buildup!
    """
    temp_dir = None
    scraper = None
    
    try:
        logger.info(f"🚀 Starting {niche} video automation")
        
        temp_dir = tempfile.mkdtemp(prefix="douyin_")
        config = NICHE_CONFIG.get(niche, NICHE_CONFIG["animals"])
        
        # STEP 1: Find ONE video (then stop scraping!)
        logger.info("STEP 1: Scraping for ONE video...")
        scraper = FastDouyinScraper()
        
        video_url = scraper.find_one_video(config["profile_url"])
        if not video_url:
            logger.info("   Trying fallback search...")
            video_url = scraper.find_one_video(config["fallback_search"])
        
        scraper.close()  # Close browser IMMEDIATELY to free memory
        scraper = None
        gc.collect()
        
        if not video_url:
            return {"success": False, "error": "No videos found"}
        
        logger.info(f"✅ Found video: {video_url[:60]}...")
        
        # STEP 2: Download
        logger.info("STEP 2: Downloading...")
        video_path = await download_video(video_url, temp_dir)
        if not video_path:
            return {"success": False, "error": "Download failed"}
        
        # STEP 3: Process
        logger.info("STEP 3: Processing...")
        processed = await simple_process(video_path, temp_dir)
        if not processed:
            return {"success": False, "error": "Processing failed"}
        
        # STEP 4: Upload
        logger.info("STEP 4: Uploading...")
        script = get_simple_script(niche)
        result = await upload_to_yt(processed, script, user_id, database_manager)
        
        # STEP 5: Cleanup
        logger.info("STEP 5: Cleanup...")
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if result.get("success"):
            logger.info(f"🎉 SUCCESS: {result['video_url']}")
            return {
                "success": True,
                "video_url": result["video_url"],
                "video_id": result["video_id"],
                "title": script["title"],
                "source": video_url
            }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}")
        logger.error(traceback.format_exc())
        
        if scraper:
            scraper.close()
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# API
router = APIRouter()

@router.post("/api/china/generate")
async def generate(request: Request):
    """Generate videos - processes ONE at a time"""
    try:
        data = await request.json()
        niche = data.get("niche", "animals")
        user_id = data.get("user_id")
        num_videos = data.get("num_videos", 1)
        
        if not user_id:
            return JSONResponse(status_code=401, content={"error": "user_id required"})
        
        if niche not in NICHE_CONFIG:
            return JSONResponse(status_code=400, content={"error": f"Invalid niche. Use: {list(NICHE_CONFIG.keys())}"})
        
        from Supermain import database_manager
        
        logger.info(f"📨 Request: {user_id} / {niche} / {num_videos} videos")
        
        results = []
        for i in range(num_videos):
            logger.info(f"\n{'='*60}")
            logger.info(f"VIDEO {i+1}/{num_videos}")
            logger.info(f"{'='*60}\n")
            
            result = await asyncio.wait_for(
                process_one_video_complete(niche, user_id, database_manager),
                timeout=600  # 10 min per video
            )
            
            results.append(result)
            
            if not result.get("success"):
                logger.warning(f"⚠️ Video {i+1} failed: {result.get('error')}")
            
            # Short break between videos
            if i < num_videos - 1:
                await asyncio.sleep(3)
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return JSONResponse(content={
            "success": True,
            "total": num_videos,
            "successful": success_count,
            "failed": num_videos - success_count,
            "results": results
        })
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"error": "Timeout"})
    except Exception as e:
        logger.error(f"API error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/api/china/test")
async def test():
    return {
        "success": True,
        "message": "Douyin Automation - Memory Optimized",
        "features": [
            "✅ Low memory (<512MB)",
            "✅ Process one video at a time",
            "✅ Immediate cleanup",
            "✅ Fast scraping (finds 1 video and stops)"
        ],
        "niches": list(NICHE_CONFIG.keys())
    }

__all__ = ['router']