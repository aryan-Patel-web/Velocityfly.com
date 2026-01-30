"""
china_enhanced.py - SIMPLIFIED DOUYIN AUTOMATION
===========================================================================
✅ Scrapes Douyin videos using HTTP requests (NO Selenium)
✅ Downloads videos directly
✅ Adds background music
✅ Uploads to YouTube Shorts
✅ NO ElevenLabs, Whisper, or Mistral (simplified)
===========================================================================
"""

import os
import logging
import requests
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("china")

# Router for FastAPI
router = APIRouter()

# ============================================================================
# CONFIGURATION
# ============================================================================

TEMP_DIR = Path("/tmp/china_videos")
TEMP_DIR.mkdir(exist_ok=True)

# Background music URL
BACKGROUND_MUSIC_URL = "https://github.com/aryan-Patel-web/audio-collections/raw/main/videoplayback%20(6).weba"

# Niche configuration with REAL Douyin profile URLs
NICHE_CONFIG = {
    "funny": {
        "name": "Funny / Comedy / Memes",
        "profile_urls": [
            "https://www.douyin.com/user/56007218020",  # From your screenshot
            "https://www.douyin.com/search/搞笑",
            "https://www.douyin.com/search/comedy"
        ],
        "hashtags": "#Funny #Comedy #Memes #Viral #Shorts"
    },
    "animals": {
        "name": "Cute Animals / Pets",
        "profile_urls": [
            "https://www.douyin.com/search/萌宠",
            "https://www.douyin.com/search/宠物",
            "https://www.douyin.com/search/cute%20animals"
        ],
        "hashtags": "#Animals #Pets #Cute #Dogs #Shorts"
    },
    "kids": {
        "name": "Kids / Cartoon / Children",
        "profile_urls": [
            "https://www.douyin.com/search/儿童",
            "https://www.douyin.com/search/卡通",
            "https://www.douyin.com/search/kids"
        ],
        "hashtags": "#Kids #Cartoon #Children #Shorts"
    },
    "stories": {
        "name": "Story / Motivation / Facts",
        "profile_urls": [
            "https://www.douyin.com/user/209973957",  # AI Story from your screenshot
            "https://www.douyin.com/search/ai%20story",
            "https://www.douyin.com/search/motivation"
        ],
        "hashtags": "#Story #Motivation #Facts #Shorts"
    },
    "satisfying": {
        "name": "Satisfying / ASMR / Oddly Satisfying",
        "profile_urls": [
            "https://www.douyin.com/search/解压",
            "https://www.douyin.com/search/治愈",
            "https://www.douyin.com/search/satisfying"
        ],
        "hashtags": "#Satisfying #ASMR #Shorts"
    }
}

# ============================================================================
# REQUEST MODELS
# ============================================================================

class ChinaGenerateRequest(BaseModel):
    user_id: str
    niche: str = "animals"
    num_videos: int = 1
    show_captions: bool = True

# ============================================================================
# STEP 1: SCRAPE DOUYIN VIDEOS (NO SELENIUM - HTTP ONLY)
# ============================================================================

def scrape_douyin_videos(url: str, max_videos: int = 10) -> List[str]:
    """
    Scrape Douyin using HTTP requests (NO Selenium)
    Returns list of video URLs
    """
    try:
        logger.info(f"📱 Scraping Douyin: {url}")
        
        # User agent to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.douyin.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        # Get the page
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html = response.text
        logger.info(f"✅ Page loaded: {len(html)} chars")
        
        # Extract video IDs from HTML using regex
        # Douyin video URLs are like: /video/7598419068546948017
        video_ids = re.findall(r'/video/(\d{19})', html)
        
        # Remove duplicates
        video_ids = list(set(video_ids))[:max_videos]
        
        # Convert to full URLs
        video_urls = [f"https://www.douyin.com/video/{vid}" for vid in video_ids]
        
        logger.info(f"✅ Found {len(video_urls)} video URLs")
        
        return video_urls
        
    except Exception as e:
        logger.error(f"❌ Scraping error: {e}")
        return []

# ============================================================================
# STEP 2: DOWNLOAD VIDEO FROM DOUYIN
# ============================================================================

def download_douyin_video(video_url: str, output_path: Path) -> bool:
    """
    Download Douyin video using ssstik.io API (reliable downloader)
    """
    try:
        logger.info(f"📥 Downloading video from: {video_url}")
        
        # Method 1: Try ssstik.io
        try:
            # ssstik.io API endpoint
            api_url = "https://ssstik.io/abc"
            
            params = {'url': 'dl'}
            
            data = {
                'id': video_url,
                'locale': 'en',
                'tt': 'temp_token'  # This changes but ssstik usually works without it
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            response = requests.post(api_url, params=params, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Parse HTML response to find download link
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find download link
                download_link = None
                for a_tag in soup.find_all('a'):
                    href = a_tag.get('href', '')
                    if 'download' in href or '.mp4' in href:
                        download_link = href
                        break
                
                if download_link:
                    # Download the video
                    video_response = requests.get(download_link, stream=True, timeout=60)
                    
                    with open(output_path, 'wb') as f:
                        for chunk in video_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = output_path.stat().st_size / (1024 * 1024)
                    logger.info(f"✅ Downloaded: {file_size:.2f}MB")
                    return True
        
        except Exception as e:
            logger.error(f"ssstik.io failed: {e}")
        
        # Method 2: Try direct Douyin video extraction
        try:
            logger.info("Trying direct Douyin page extraction...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(video_url, headers=headers, timeout=30)
            html = response.text
            
            # Look for video URLs in the HTML
            # Douyin embeds video URLs in the page
            video_patterns = [
                r'"play_addr":\{"uri":"[^"]+","url_list":\["([^"]+)"',
                r'"video":\{[^}]*"play_addr":\{[^}]*"url_list":\["([^"]+)"',
                r'playAddr":"([^"]+)"',
            ]
            
            video_download_url = None
            for pattern in video_patterns:
                match = re.search(pattern, html)
                if match:
                    video_download_url = match.group(1)
                    # Unescape the URL
                    video_download_url = video_download_url.replace('\\u002F', '/')
                    break
            
            if video_download_url:
                logger.info(f"Found video URL: {video_download_url[:50]}...")
                
                # Download the video
                video_response = requests.get(video_download_url, headers=headers, stream=True, timeout=60)
                
                with open(output_path, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = output_path.stat().st_size / (1024 * 1024)
                
                # Validate file size
                if file_size < 0.1 or file_size > 30:
                    logger.error(f"Invalid file size: {file_size:.2f}MB")
                    return False
                
                logger.info(f"✅ Downloaded: {file_size:.2f}MB")
                return True
        
        except Exception as e:
            logger.error(f"Direct extraction failed: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False

# ============================================================================
# STEP 3: DOWNLOAD BACKGROUND MUSIC
# ============================================================================

def download_background_music(output_path: Path) -> bool:
    """Download background music from GitHub"""
    try:
        logger.info(f"🎵 Downloading background music...")
        
        response = requests.get(BACKGROUND_MUSIC_URL, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"✅ Music downloaded")
        return True
        
    except Exception as e:
        logger.error(f"❌ Music download failed: {e}")
        return False

# ============================================================================
# STEP 4: ADD BACKGROUND MUSIC TO VIDEO
# ============================================================================

def add_background_music(video_path: Path, music_path: Path, output_path: Path) -> bool:
    """
    Add background music to video using FFmpeg
    - Original video audio: 70% volume
    - Background music: 30% volume (quieter)
    """
    try:
        logger.info(f"🎬 Adding background music to video...")
        
        # FFmpeg command to mix audio
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(music_path),
            "-filter_complex",
            "[0:a]volume=0.7[a1];[1:a]volume=0.3,aloop=loop=-1:size=2e9[a2];[a1][a2]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ Background music added")
            return True
        else:
            logger.error(f"❌ FFmpeg failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to add music: {e}")
        return False

# ============================================================================
# STEP 5: CONVERT TO YOUTUBE SHORTS FORMAT (9:16)
# ============================================================================

def convert_to_shorts_format(input_path: Path, output_path: Path) -> bool:
    """Convert video to 9:16 aspect ratio for YouTube Shorts"""
    try:
        logger.info(f"📱 Converting to Shorts format (9:16)...")
        
        # FFmpeg command to convert to 1080x1920 (9:16)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "copy",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ Converted to Shorts format")
            return True
        else:
            logger.error(f"❌ Conversion failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to convert: {e}")
        return False

# ============================================================================
# STEP 6: UPLOAD TO YOUTUBE
# ============================================================================

def upload_to_youtube(video_path: Path, user_id: str, niche: str) -> Optional[str]:
    """Upload video to YouTube Shorts"""
    try:
        logger.info(f"📺 Uploading to YouTube...")
        
        # Get YouTube credentials from database (you'll need to implement this)
        # For now, using placeholder
        credentials_dict = get_user_youtube_credentials(user_id)
        
        if not credentials_dict:
            logger.error("No YouTube credentials found")
            return None
        
        credentials = Credentials.from_authorized_user_info(credentials_dict)
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Get niche info
        niche_info = NICHE_CONFIG.get(niche, NICHE_CONFIG['animals'])
        
        # Create title and description
        title = f"{niche_info['name']} #Shorts"
        description = f"Amazing {niche_info['name']} content! {niche_info['hashtags']}"
        
        # Upload metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': niche_info['hashtags'].replace('#', '').split(),
                'categoryId': '24'  # Entertainment
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Upload video
        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        video_url = f"https://www.youtube.com/shorts/{video_id}"
        
        logger.info(f"✅ Uploaded to YouTube: {video_url}")
        return video_url
        
    except Exception as e:
        logger.error(f"❌ YouTube upload failed: {e}")
        return None

def get_user_youtube_credentials(user_id: str) -> Optional[Dict]:
    """Get user's YouTube credentials from database"""
    # TODO: Implement database lookup
    # This is a placeholder
    return None

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def process_video(video_url: str, user_id: str, niche: str) -> Dict:
    """
    Main pipeline: Download → Add Music → Convert → Upload
    """
    try:
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"🎬 Processing video {request_id}: {video_url}")
        
        # Create temp directory for this video
        video_dir = TEMP_DIR / request_id
        video_dir.mkdir(exist_ok=True)
        
        # Step 1: Download video
        original_video = video_dir / "original.mp4"
        if not download_douyin_video(video_url, original_video):
            return {"success": False, "error": "Failed to download video"}
        
        # Step 2: Download background music
        music_file = video_dir / "music.weba"
        if not download_background_music(music_file):
            return {"success": False, "error": "Failed to download music"}
        
        # Step 3: Add background music
        video_with_music = video_dir / "with_music.mp4"
        if not add_background_music(original_video, music_file, video_with_music):
            return {"success": False, "error": "Failed to add music"}
        
        # Step 4: Convert to Shorts format
        final_video = video_dir / "final.mp4"
        if not convert_to_shorts_format(video_with_music, final_video):
            return {"success": False, "error": "Failed to convert to Shorts format"}
        
        # Step 5: Upload to YouTube
        youtube_url = upload_to_youtube(final_video, user_id, niche)
        if not youtube_url:
            return {"success": False, "error": "Failed to upload to YouTube"}
        
        # Cleanup
        try:
            import shutil
            shutil.rmtree(video_dir)
        except:
            pass
        
        logger.info(f"✅ Video {request_id} complete!")
        
        return {
            "success": True,
            "youtube_url": youtube_url,
            "video_url": video_url
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTES
# ============================================================================

@router.get("/api/china/niches")
async def get_niches():
    """Get available niches"""
    return {
        "niches": [
            {
                "id": key,
                "name": value["name"],
                "profile_urls": value["profile_urls"],
                "hashtags": value["hashtags"]
            }
            for key, value in NICHE_CONFIG.items()
        ]
    }

@router.post("/api/china/generate")
async def generate_videos(request: ChinaGenerateRequest):
    """
    Main endpoint: Scrape Douyin → Add Music → Upload to YouTube
    """
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"📨 Request: {request_id} / {request.niche} / {request.num_videos} videos")
        
        # Get niche config
        niche_config = NICHE_CONFIG.get(request.niche, NICHE_CONFIG['animals'])
        profile_urls = niche_config['profile_urls']
        
        logger.info(f"   Profile URLs: {profile_urls}")
        
        # Step 1: Scrape videos from all profile URLs
        all_video_urls = []
        for url in profile_urls:
            videos = scrape_douyin_videos(url, max_videos=10)
            all_video_urls.extend(videos)
            
            if len(all_video_urls) >= request.num_videos * 3:
                break
        
        if not all_video_urls:
            raise HTTPException(status_code=500, detail="No videos found")
        
        logger.info(f"✅ Found {len(all_video_urls)} total videos")
        
        # Step 2: Process videos one by one
        results = []
        for i in range(min(request.num_videos, len(all_video_urls))):
            video_url = all_video_urls[i]
            logger.info(f"\n🎬 Processing video {i+1}/{request.num_videos}")
            
            result = process_video(video_url, request.user_id, request.niche)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.get('success'))
        failed = len(results) - successful
        
        logger.info(f"\n📊 Summary: {successful} successful, {failed} failed")
        
        return {
            "success": True,
            "request_id": request_id,
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": failed
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/china/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "status": "ok",
        "message": "China video automation is running",
        "niches": list(NICHE_CONFIG.keys())
    }

# Export router
__all__ = ['router']