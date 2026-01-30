"""
china_api.py - DOUYIN API-BASED SCRAPING
===========================================================================
✅ Uses Douyin's internal API (more reliable than HTML parsing)
✅ Profile-specific scraping (not random)
✅ Detailed step-by-step logging
✅ Works with 2 niches: Funny & Animals
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
import subprocess
from typing import Optional
import tempfile
import shutil
import gc

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Config
MAX_VIDEO_SIZE_MB = 50
TARGET_DURATION = 50

# Profile configurations
PROFILES = {
    "funny": {
        "name": "Funny/Comedy",
        "sec_uid": "MS4wLjABAAAAe-jjss5iSv02OGU_kOaQCc4jOSuHiCb3NlmA7koeoC7ISTKHLMtVTt-ELmNLkHfV",
        "user_id": "56007218020",
        "fallback_keyword": "搞笑"
    },
    "animals": {
        "name": "Animals/Pets",
        "sec_uid": "MS4wLjABAAAA424aSWu0zdBbu6sTR0wIo-okI65xkC9dEltXycuVo0f3WdUTVbA1j8Hbi6Jvqwt1",
        "user_id": "78632067601",
        "fallback_keyword": "萌宠"
    }
}

def log_step(step: str, status: str, message: str):
    """Detailed logging with step tracking"""
    symbols = {"START": "🔵", "SUCCESS": "✅", "ERROR": "❌", "INFO": "ℹ️", "WARNING": "⚠️"}
    symbol = symbols.get(status, "•")
    logger.info(f"{symbol} [{step}] {message}")
    print(f"{symbol} [{step}] {message}")  # Also print to console

def cleanup(*files):
    """Cleanup files"""
    for f in files:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except:
            pass
    gc.collect()

def run_ffmpeg(cmd, timeout=60):
    """Run FFmpeg"""
    try:
        subprocess.run(cmd, capture_output=True, timeout=timeout, check=True)
        return True
    except:
        return False

async def scrape_douyin_api(profile: dict) -> Optional[str]:
    """
    Scrape using Douyin's internal API
    More reliable than HTML parsing
    """
    step = "API_SCRAPE"
    log_step(step, "START", f"Scraping profile: {profile['name']}")
    
    try:
        # Douyin's API endpoint for user posts
        api_url = "https://www.douyin.com/aweme/v1/web/aweme/post/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.douyin.com/',
            'Accept': 'application/json',
        }
        
        params = {
            'sec_user_id': profile['sec_uid'],
            'count': '10',
            'max_cursor': '0',
        }
        
        log_step(step, "INFO", f"Calling API with sec_uid: {profile['sec_uid'][:30]}...")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(api_url, headers=headers, params=params)
            
            log_step(step, "INFO", f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract video list
                aweme_list = data.get('aweme_list', [])
                log_step(step, "INFO", f"Found {len(aweme_list)} videos in response")
                
                if aweme_list:
                    # Get first video's ID
                    first_video = aweme_list[0]
                    aweme_id = first_video.get('aweme_id')
                    
                    if aweme_id:
                        video_url = f"https://www.douyin.com/video/{aweme_id}"
                        log_step(step, "SUCCESS", f"Found video: {video_url}")
                        return video_url
                    else:
                        log_step(step, "ERROR", "No aweme_id in video data")
                else:
                    log_step(step, "ERROR", "Empty aweme_list in response")
            else:
                log_step(step, "ERROR", f"API returned {response.status_code}")
        
        return None
        
    except Exception as e:
        log_step(step, "ERROR", f"Exception: {str(e)[:100]}")
        return None

async def scrape_douyin_web(profile: dict) -> Optional[str]:
    """
    Fallback: Scrape using web page with better selectors
    """
    step = "WEB_SCRAPE"
    log_step(step, "START", "Trying web scraping fallback")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        import time
        
        log_step(step, "INFO", "Initializing Chrome...")
        
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,720")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)
        
        profile_url = f"https://www.douyin.com/user/{profile['sec_uid']}"
        log_step(step, "INFO", f"Loading: {profile_url[:60]}...")
        
        driver.get(profile_url)
        time.sleep(8)
        
        # Scroll
        log_step(step, "INFO", "Scrolling page...")
        for i in range(2):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1.5)
        
        # Updated selectors based on your screenshots
        selectors = [
            # From your screenshots, I see these patterns:
            "a[href*='/video/']",
            "div[class*='douyin'] a",
            "li a[href*='douyin.com']",
        ]
        
        log_step(step, "INFO", "Searching for video links...")
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_step(step, "INFO", f"Selector '{selector}': {len(elements)} elements")
            
            for elem in elements:
                try:
                    href = elem.get_attribute('href')
                    if href and 'video' in href and 'douyin.com' in href:
                        driver.quit()
                        log_step(step, "SUCCESS", f"Found: {href[:60]}...")
                        return href
                except:
                    continue
        
        driver.quit()
        log_step(step, "ERROR", "No videos found with any selector")
        return None
        
    except Exception as e:
        log_step(step, "ERROR", f"Exception: {str(e)[:100]}")
        return None

async def download_video(url: str, temp_dir: str) -> Optional[str]:
    """Download video with detailed logging"""
    step = "DOWNLOAD"
    log_step(step, "START", f"Downloading from: {url[:60]}...")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            log_step(step, "INFO", "Fetching video page HTML...")
            
            response = await client.get(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)'},
                follow_redirects=True
            )
            
            log_step(step, "INFO", f"Page status: {response.status_code}")
            
            if response.status_code != 200:
                log_step(step, "ERROR", f"Failed to load page: {response.status_code}")
                return None
            
            html = response.text
            log_step(step, "INFO", f"HTML length: {len(html)} chars")
            
            # Extract video URL from HTML
            patterns = [
                r'"playAddr"[^"]*"(https://[^"]+\.mp4[^"]*)"',
                r'playUrl[^"]*"(https://[^"]+\.mp4[^"]*)"',
                r'"play_addr"[^{]+url_list[^[]+\["([^"]+)"',
            ]
            
            video_url = None
            for i, pattern in enumerate(patterns, 1):
                log_step(step, "INFO", f"Trying pattern {i}/{len(patterns)}...")
                matches = re.findall(pattern, html)
                
                if matches:
                    video_url = matches[0].replace('\\/', '/')
                    log_step(step, "SUCCESS", f"Pattern {i} matched!")
                    log_step(step, "INFO", f"Video URL: {video_url[:60]}...")
                    break
            
            if not video_url:
                log_step(step, "ERROR", "No video URL found in HTML")
                return None
            
            # Download video
            log_step(step, "INFO", "Downloading video file...")
            
            video_resp = await client.get(
                video_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                follow_redirects=True,
                timeout=90
            )
            
            if video_resp.status_code != 200:
                log_step(step, "ERROR", f"Video download failed: {video_resp.status_code}")
                return None
            
            size_mb = len(video_resp.content) / (1024 * 1024)
            log_step(step, "INFO", f"Downloaded {size_mb:.2f} MB")
            
            if not (0.1 < size_mb < MAX_VIDEO_SIZE_MB):
                log_step(step, "ERROR", f"Invalid size: {size_mb:.2f} MB")
                return None
            
            path = os.path.join(temp_dir, "video.mp4")
            with open(path, 'wb') as f:
                f.write(video_resp.content)
            
            log_step(step, "SUCCESS", f"Saved to: {path}")
            return path
            
    except Exception as e:
        log_step(step, "ERROR", f"Exception: {str(e)[:100]}")
        traceback.print_exc()
        return None

async def process_video(video_path: str, temp_dir: str) -> Optional[str]:
    """Process video for YouTube Shorts"""
    step = "PROCESS"
    log_step(step, "START", "Processing for YouTube Shorts (1080x1920)")
    
    try:
        output = os.path.join(temp_dir, "processed.mp4")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-t", str(TARGET_DURATION),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264", "-crf", "28", "-preset", "ultrafast",
            "-an",
            "-y", output
        ]
        
        log_step(step, "INFO", "Running FFmpeg...")
        
        if run_ffmpeg(cmd, 60):
            size_mb = os.path.getsize(output) / (1024 * 1024)
            log_step(step, "SUCCESS", f"Processed: {size_mb:.1f} MB")
            cleanup(video_path)
            return output
        else:
            log_step(step, "ERROR", "FFmpeg failed")
            return None
            
    except Exception as e:
        log_step(step, "ERROR", f"Exception: {str(e)[:100]}")
        return None

async def upload_to_youtube(video_path: str, niche: str, user_id: str, db_manager) -> dict:
    """Upload to YouTube"""
    step = "UPLOAD"
    log_step(step, "START", "Uploading to YouTube...")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        from mainY import youtube_scheduler
        
        log_step(step, "INFO", "Fetching YouTube credentials...")
        
        yt_db = get_yt_db()
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds_raw = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds_raw:
            log_step(step, "ERROR", "No YouTube credentials found")
            return {"success": False, "error": "No credentials"}
        
        log_step(step, "INFO", "Building credentials...")
        
        creds = {
            "access_token": creds_raw.get("access_token"),
            "refresh_token": creds_raw.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
        }
        
        # Simple titles
        titles = {
            "funny": "मजेदार वीडियो 😂 | Funny Video",
            "animals": "प्यारा जानवर 🐶 | Cute Animal"
        }
        
        title = titles.get(niche, "वीडियो | Video")
        description = f"{niche.title()} video from Douyin"
        hashtags = [niche, "viral", "shorts"]
        
        log_step(step, "INFO", f"Title: {title}")
        log_step(step, "INFO", "Calling YouTube upload API...")
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=creds,
            content_type="shorts",
            title=title,
            description=description + "\n\n#" + " #".join(hashtags),
            video_url=video_path
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            video_url = f"https://youtube.com/shorts/{video_id}"
            log_step(step, "SUCCESS", f"Uploaded: {video_url}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
        else:
            log_step(step, "ERROR", f"Upload failed: {result.get('error')}")
            return {"success": False, "error": result.get("error")}
            
    except Exception as e:
        log_step(step, "ERROR", f"Exception: {str(e)[:100]}")
        return {"success": False, "error": str(e)}

async def process_one_video(niche: str, user_id: str, db_manager) -> dict:
    """
    Complete pipeline for ONE video with detailed logging
    """
    log_step("PIPELINE", "START", f"=== STARTING {niche.upper()} VIDEO ===")
    
    temp_dir = None
    
    try:
        # Get profile config
        profile = PROFILES.get(niche)
        if not profile:
            return {"success": False, "error": f"Invalid niche: {niche}"}
        
        log_step("PIPELINE", "INFO", f"Profile: {profile['name']}")
        log_step("PIPELINE", "INFO", f"User ID: {profile['user_id']}")
        
        temp_dir = tempfile.mkdtemp(prefix=f"douyin_{niche}_")
        log_step("PIPELINE", "INFO", f"Temp dir: {temp_dir}")
        
        # STEP 1: Scrape for video URL
        log_step("PIPELINE", "INFO", "Step 1/4: Scraping...")
        
        video_url = await scrape_douyin_api(profile)
        
        if not video_url:
            log_step("PIPELINE", "WARNING", "API scraping failed, trying web scraping...")
            video_url = await scrape_douyin_web(profile)
        
        if not video_url:
            log_step("PIPELINE", "ERROR", "All scraping methods failed")
            return {"success": False, "error": "No videos found"}
        
        # STEP 2: Download
        log_step("PIPELINE", "INFO", "Step 2/4: Downloading...")
        
        video_path = await download_video(video_url, temp_dir)
        
        if not video_path:
            return {"success": False, "error": "Download failed"}
        
        # STEP 3: Process
        log_step("PIPELINE", "INFO", "Step 3/4: Processing...")
        
        processed = await process_video(video_path, temp_dir)
        
        if not processed:
            return {"success": False, "error": "Processing failed"}
        
        # STEP 4: Upload
        log_step("PIPELINE", "INFO", "Step 4/4: Uploading...")
        
        result = await upload_to_youtube(processed, niche, user_id, db_manager)
        
        # Cleanup
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if result.get("success"):
            log_step("PIPELINE", "SUCCESS", "=== PIPELINE COMPLETE ===")
            return {
                "success": True,
                "video_url": result["video_url"],
                "video_id": result["video_id"],
                "source": video_url
            }
        else:
            log_step("PIPELINE", "ERROR", "Upload failed")
            return result
            
    except Exception as e:
        log_step("PIPELINE", "ERROR", f"Exception: {str(e)}")
        traceback.print_exc()
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# API Router
router = APIRouter()

@router.post("/api/china/generate")
async def generate(request: Request):
    """Generate videos"""
    try:
        data = await request.json()
        
        niche = data.get("niche", "animals")
        user_id = data.get("user_id")
        num_videos = data.get("num_videos", 1)
        
        log_step("API", "START", f"Request: {niche} / {num_videos} videos / user: {user_id}")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"error": "user_id required"})
        
        if niche not in PROFILES:
            return JSONResponse(status_code=400, content={
                "error": f"Invalid niche. Use: {list(PROFILES.keys())}"
            })
        
        from Supermain import database_manager
        
        results = []
        success_count = 0
        
        for i in range(num_videos):
            log_step("API", "INFO", f"\n{'='*60}\nVIDEO {i+1}/{num_videos}\n{'='*60}")
            
            result = await asyncio.wait_for(
                process_one_video(niche, user_id, database_manager),
                timeout=600
            )
            
            results.append(result)
            
            if result.get("success"):
                success_count += 1
                log_step("API", "SUCCESS", f"Video {i+1} uploaded: {result['video_url']}")
            else:
                log_step("API", "ERROR", f"Video {i+1} failed: {result.get('error')}")
            
            if i < num_videos - 1:
                await asyncio.sleep(3)
        
        log_step("API", "INFO", f"FINAL: {success_count}/{num_videos} successful")
        
        return JSONResponse(content={
            "success": True,
            "total": num_videos,
            "successful": success_count,
            "failed": num_videos - success_count,
            "results": results
        })
        
    except Exception as e:
        log_step("API", "ERROR", f"API error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/api/china/test")
async def test():
    return {
        "success": True,
        "message": "Douyin API Scraper",
        "niches": list(PROFILES.keys()),
        "profiles": {
            k: {
                "name": v["name"],
                "user_id": v["user_id"]
            }
            for k, v in PROFILES.items()
        }
    }

__all__ = ['router']