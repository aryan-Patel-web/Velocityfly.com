"""
china_shorts.py - CHINA SHORTS VIDEO PROCESSOR V3.1 (PRODUCTION + MANUAL UPLOAD)
===================================================================
✅ 5 WORKING URL DOWNLOAD METHODS (Based on real SaveTik.co analysis)
✅ NEW: Manual File Upload Processing
✅ All same filters, captions, BGM, and YouTube upload
===================================================================
"""

from fastapi import APIRouter, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import subprocess
import tempfile
import shutil
import gc
import httpx
import json
import re
import random
import base64
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from urllib.parse import urlparse, parse_qs, urlencode
import aiofiles

try:
    import psutil
    HAS_PSUTIL = True
except:
    HAS_PSUTIL = False

# ═══════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("ChinaShorts")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def log_memory(step: str):
    """Log memory usage"""
    if HAS_PSUTIL:
        try:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
            if mem_mb > 450:
                logger.warning(f"⚠️ HIGH: {mem_mb:.1f}MB")
                gc.collect()
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════

CHINA_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3"
]

PROCESSING_STATUS = {}

CAPTION_EMOJIS = ["😂", "🤣", "😱", "😮", "🤔", "😍", "🔥", "✨", "💯", "👀", "🎉", "❤️", "🙌", "💪", "🤯"]
CAPTION_TEXT = ["LOL", "OMG", "WOW", "HAHA", "NICE", "EPIC", "COOL", "FIRE"]

# Douyin/TikTok headers (Critical for success)
DOUYIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cookie": "ttwid=1%7C; __ac_nonce=0; __ac_signature=_02B4Z6wo00f01; odin_tt=0",
}

MOBILE_HEADERS = {
    "User-Agent": "com.ss.android.ugc.aweme/260801 (Linux; U; Android 11; zh_CN; SM-G991B; Build/RP1A.200720.012; Cronet/TTNetVersion:d2f6e1a7 2021-06-15 QuicVersion:0144d358 2021-03-09)",
    "Accept-Encoding": "gzip, deflate",
}

# ═══════════════════════════════════════════════════════════════════════
# CLEANUP & FFMPEG
# ═══════════════════════════════════════════════════════════════════════

def cleanup(*paths):
    """Delete files and force garbage collection"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except:
            pass
    gc.collect()

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg command"""
    logger.info(f"🎬 {step}...")
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout, text=True)
        if result.returncode == 0:
            logger.info(f"✅ {step}")
            return True
        else:
            logger.error(f"❌ {step} failed: {result.stderr[-200:]}")
            return False
    except Exception as e:
        logger.error(f"❌ {step} error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# URL EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from Douyin/TikTok URL"""
    patterns = [
        r'modal_id=(\d+)',
        r'video/(\d{19})',
        r'vid=(\d+)',
        r'/(\d{19})',
        r'item_ids=(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            logger.info(f"   ✅ Extracted Video ID: {video_id}")
            return video_id
    
    return None

# ═══════════════════════════════════════════════════════════════════════
# METHOD 1: DOUYIN INTERNAL API (ITEMINFO) - BEST METHOD
# ═══════════════════════════════════════════════════════════════════════

async def download_douyin_api(video_id: str, output: str) -> bool:
    """
    Method 1: Douyin Internal API (iteminfo)
    This is what SaveTik.co uses primarily
    """
    logger.info("   📥 Method 1: Douyin Internal API (iteminfo)")
    
    if not video_id:
        logger.warning("   ❌ No video ID")
        return False
    
    # Douyin iteminfo API endpoint
    api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            logger.info(f"   → Calling Douyin API: item_ids={video_id}")
            
            response = await client.get(api_url, headers=DOUYIN_HEADERS)
            
            if response.status_code != 200:
                logger.warning(f"   ❌ API returned {response.status_code}")
                return False
            
            data = response.json()
            
            # Navigate response structure
            if "item_list" not in data or not data["item_list"]:
                logger.warning("   ❌ No item_list in response")
                return False
            
            item = data["item_list"][0]
            
            # Extract video URLs (multiple quality options)
            video_urls = []
            
            # Try play_addr first (best quality)
            if "video" in item and "play_addr" in item["video"]:
                play_addr = item["video"]["play_addr"]
                
                if "url_list" in play_addr:
                    video_urls.extend(play_addr["url_list"])
            
            # Try download_addr (no watermark)
            if "video" in item and "download_addr" in item["video"]:
                download_addr = item["video"]["download_addr"]
                
                if "url_list" in download_addr:
                    video_urls.extend(download_addr["url_list"])
            
            # Try bit_rate array (different qualities)
            if "video" in item and "bit_rate" in item["video"]:
                for bit_rate in item["video"]["bit_rate"]:
                    if "play_addr" in bit_rate and "url_list" in bit_rate["play_addr"]:
                        video_urls.extend(bit_rate["play_addr"]["url_list"])
            
            if not video_urls:
                logger.warning("   ❌ No video URLs found in API response")
                return False
            
            logger.info(f"   → Found {len(video_urls)} video URL(s)")
            
            # Try each URL until one works
            for i, video_url in enumerate(video_urls):
                try:
                    logger.info(f"   → Trying URL {i+1}/{len(video_urls)}: {video_url[:60]}...")
                    
                    # Download video
                    download_headers = {**DOUYIN_HEADERS}
                    
                    async with client.stream("GET", video_url, headers=download_headers, timeout=180) as stream:
                        if stream.status_code == 200:
                            content_type = stream.headers.get("content-type", "")
                            
                            if "video" in content_type or "octet-stream" in content_type:
                                total = 0
                                with open(output, 'wb') as f:
                                    async for chunk in stream.aiter_bytes(1024*1024):
                                        f.write(chunk)
                                        total += len(chunk)
                                
                                if total > 10000:
                                    size = total / (1024 * 1024)
                                    logger.info(f"   ✅ Method 1 SUCCESS: {size:.1f}MB")
                                    return True
                            else:
                                logger.warning(f"   ❌ Wrong content-type: {content_type}")
                
                except Exception as e:
                    logger.warning(f"   → URL {i+1} failed: {e}")
                    continue
            
            logger.warning("   ❌ All URLs failed")
            return False
    
    except Exception as e:
        logger.warning(f"   ❌ Method 1 ERROR: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# METHOD 2: MOBILE API WITH PROPER HEADERS
# ═══════════════════════════════════════════════════════════════════════

async def download_mobile_api(video_id: str, output: str) -> bool:
    """Method 2: Mobile API (pretend to be Android app)"""
    logger.info("   📥 Method 2: Mobile API (Android app simulation)")
    
    if not video_id:
        logger.warning("   ❌ No video ID")
        return False
    
    # Mobile API endpoints
    mobile_endpoints = [
        f"https://aweme.snssdk.com/aweme/v1/play/?video_id={video_id}&ratio=default&line=0",
        f"https://api-va.tiktokv.com/aweme/v1/play/?video_id={video_id}",
    ]
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            for endpoint in mobile_endpoints:
                try:
                    logger.info(f"   → Trying: {endpoint[:60]}...")
                    
                    response = await client.get(endpoint, headers=MOBILE_HEADERS, timeout=120)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "")
                        
                        if "video" in content_type or "octet-stream" in content_type:
                            with open(output, 'wb') as f:
                                f.write(response.content)
                            
                            if os.path.getsize(output) > 10000:
                                size = os.path.getsize(output) / (1024 * 1024)
                                logger.info(f"   ✅ Method 2 SUCCESS: {size:.1f}MB")
                                return True
                
                except Exception as e:
                    logger.warning(f"   → Endpoint failed: {e}")
                    continue
            
            logger.warning("   ❌ All mobile endpoints failed")
            return False
    
    except Exception as e:
        logger.warning(f"   ❌ Method 2 ERROR: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# METHOD 3: YT-DLP WITH COOKIES (Enhanced)
# ═══════════════════════════════════════════════════════════════════════

async def download_ytdlp_enhanced(url: str, output: str) -> bool:
    """Method 3: yt-dlp with Douyin-specific settings"""
    logger.info("   📥 Method 3: yt-dlp (enhanced with cookies)")
    
    try:
        # Create temporary cookies file
        cookies_content = """# Netscape HTTP Cookie File
.douyin.com	TRUE	/	FALSE	0	ttwid	1%7C
.douyin.com	TRUE	/	FALSE	0	__ac_nonce	0
.douyin.com	TRUE	/	FALSE	0	odin_tt	0
"""
        
        cookies_file = output + ".cookies"
        with open(cookies_file, 'w') as f:
            f.write(cookies_content)
        
        # Try with cookies
        result = subprocess.run([
            "yt-dlp",
            "-f", "best[ext=mp4]/best",
            "--no-playlist",
            "--no-warnings",
            "--cookies", cookies_file,
            "--user-agent", DOUYIN_HEADERS["User-Agent"],
            "--referer", "https://www.douyin.com/",
            "-o", output,
            url
        ], capture_output=True, timeout=180, text=True)
        
        cleanup(cookies_file)
        
        if result.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 10000:
            size = os.path.getsize(output) / (1024 * 1024)
            logger.info(f"   ✅ Method 3 SUCCESS: {size:.1f}MB")
            return True
        
        logger.warning(f"   ❌ Method 3 FAILED: {result.stderr[-200:] if result.stderr else 'Unknown error'}")
        return False
    
    except Exception as e:
        logger.warning(f"   ❌ Method 3 ERROR: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# METHOD 4: M3U8 STREAM CAPTURE (For streaming videos)
# ═══════════════════════════════════════════════════════════════════════

async def download_m3u8_stream(video_id: str, output: str) -> bool:
    """Method 4: M3U8 stream capture and conversion"""
    logger.info("   📥 Method 4: M3U8 stream capture")
    
    if not video_id:
        return False
    
    try:
        # Get m3u8 URL from API
        api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(api_url, headers=DOUYIN_HEADERS)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Look for m3u8 URL
            m3u8_url = None
            
            if "item_list" in data and data["item_list"]:
                item = data["item_list"][0]
                
                # Check for m3u8 in play_addr
                if "video" in item and "play_addr" in item["video"]:
                    play_addr = item["video"]["play_addr"]
                    
                    if "url_list" in play_addr:
                        for url in play_addr["url_list"]:
                            if ".m3u8" in url:
                                m3u8_url = url
                                break
            
            if not m3u8_url:
                logger.warning("   ❌ No m3u8 URL found")
                return False
            
            logger.info(f"   → Found m3u8: {m3u8_url[:60]}...")
            
            # Use ffmpeg to download and convert m3u8
            logger.info("   → Converting m3u8 to mp4...")
            
            result = subprocess.run([
                "ffmpeg",
                "-i", m3u8_url,
                "-c", "copy",
                "-bsf:a", "aac_adtstoasc",
                "-y", output
            ], capture_output=True, timeout=180)
            
            if result.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 10000:
                size = os.path.getsize(output) / (1024 * 1024)
                logger.info(f"   ✅ Method 4 SUCCESS: {size:.1f}MB")
                return True
            
            logger.warning("   ❌ m3u8 conversion failed")
            return False
    
    except Exception as e:
        logger.warning(f"   ❌ Method 4 ERROR: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# METHOD 5: TIKTOK GLOBAL API (For TikTok URLs)
# ═══════════════════════════════════════════════════════════════════════

async def download_tiktok_global(video_id: str, output: str) -> bool:
    """Method 5: TikTok Global API (for non-Douyin URLs)"""
    logger.info("   📥 Method 5: TikTok Global API")
    
    if not video_id:
        return False
    
    # TikTok API endpoint
    api_url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}"
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            headers = {
                "User-Agent": "TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet",
            }
            
            response = await client.get(api_url, headers=headers)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            # Extract video URL
            video_url = None
            
            if "aweme_list" in data and data["aweme_list"]:
                item = data["aweme_list"][0]
                
                if "video" in item and "play_addr" in item["video"]:
                    play_addr = item["video"]["play_addr"]
                    if "url_list" in play_addr and play_addr["url_list"]:
                        video_url = play_addr["url_list"][0]
            
            if not video_url:
                return False
            
            # Download video
            async with client.stream("GET", video_url, headers=headers, timeout=180) as stream:
                if stream.status_code == 200:
                    total = 0
                    with open(output, 'wb') as f:
                        async for chunk in stream.aiter_bytes(1024*1024):
                            f.write(chunk)
                            total += len(chunk)
                    
                    if total > 10000:
                        size = total / (1024 * 1024)
                        logger.info(f"   ✅ Method 5 SUCCESS: {size:.1f}MB")
                        return True
            
            return False
    
    except Exception as e:
        logger.warning(f"   ❌ Method 5 ERROR: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# MASTER DOWNLOAD FUNCTION (5 METHODS)
# ═══════════════════════════════════════════════════════════════════════

async def download_china_video(url: str, output: str) -> tuple[bool, str]:
    """
    Master download function with 5 methods:
    1. Douyin Internal API (iteminfo) - BEST
    2. Mobile API (Android simulation)
    3. yt-dlp with cookies
    4. M3U8 stream capture
    5. TikTok Global API
    """
    logger.info("⬇️ Downloading China video...")
    logger.info(f"   Original URL: {url[:80]}...")
    log_memory("download-start")
    
    # Extract video ID
    video_id = extract_video_id(url)
    
    if not video_id:
        logger.error("   ❌ Could not extract video ID from URL")
        return False, "Could not extract video ID"
    
    # Try all 5 methods
    methods = [
        ("Douyin API", lambda: download_douyin_api(video_id, output)),
        ("Mobile API", lambda: download_mobile_api(video_id, output)),
        ("yt-dlp Enhanced", lambda: download_ytdlp_enhanced(url, output)),
        ("M3U8 Stream", lambda: download_m3u8_stream(video_id, output)),
        ("TikTok Global", lambda: download_tiktok_global(video_id, output)),
    ]
    
    for method_name, method_func in methods:
        logger.info(f"\n{'='*60}")
        logger.info(f"   TRYING: {method_name}")
        logger.info(f"{'='*60}")
        
        try:
            success = await method_func()
            
            if success and os.path.exists(output) and os.path.getsize(output) > 10000:
                size = os.path.getsize(output) / (1024 * 1024)
                logger.info(f"\n✅ DOWNLOAD SUCCESS ({method_name}): {size:.1f}MB")
                log_memory("download-done")
                return True, ""
            
            logger.warning(f"   ❌ {method_name} failed, trying next...")
            
            if os.path.exists(output):
                os.remove(output)
        
        except Exception as e:
            logger.error(f"   ❌ {method_name} critical error: {e}")
            if os.path.exists(output):
                os.remove(output)
            continue
    
    logger.error("\n" + "="*60)
    logger.error("❌ ALL 5 DOWNLOAD METHODS FAILED")
    logger.error("="*60)
    
    return False, "All download methods failed"

# ═══════════════════════════════════════════════════════════════════════
# MANUAL FILE UPLOAD FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

async def save_uploaded_file(upload_file: UploadFile, output_path: str) -> tuple[bool, str]:
    """
    Save uploaded file to disk
    Returns: (success, error_message)
    """
    logger.info(f"💾 Saving uploaded file: {upload_file.filename}")
    
    try:
        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        
        # Read and save file in chunks
        total_bytes = 0
        async with aiofiles.open(output_path, 'wb') as f:
            while True:
                chunk = await upload_file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                
                total_bytes += len(chunk)
                
                # Check size limit
                if total_bytes > max_size:
                    logger.error(f"❌ File too large: {total_bytes / (1024*1024):.1f}MB")
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return False, f"File too large: {total_bytes / (1024*1024):.1f}MB (max 100MB)"
                
                await f.write(chunk)
        
        # Verify file was saved
        if not os.path.exists(output_path):
            return False, "File save failed"
        
        file_size = os.path.getsize(output_path)
        if file_size < 10000:  # Less than 10KB
            logger.error(f"❌ File too small: {file_size} bytes")
            os.remove(output_path)
            return False, "File too small or corrupted"
        
        logger.info(f"✅ File saved: {file_size / (1024*1024):.2f}MB")
        return True, ""
    
    except Exception as e:
        logger.error(f"❌ File save error: {e}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        return False, str(e)


async def validate_video_file(video_path: str) -> tuple[bool, str]:
    """
    Validate uploaded video file using ffprobe
    Returns: (is_valid, error_message)
    """
    logger.info("🔍 Validating video file...")
    
    try:
        # Use ffprobe to check if it's a valid video
        result = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_type,duration",
            "-of", "json",
            video_path
        ], capture_output=True, timeout=30, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Not a valid video file")
            return False, "Invalid video file format"
        
        # Parse output
        try:
            data = json.loads(result.stdout)
            
            if not data.get("streams"):
                return False, "No video stream found"
            
            # Check duration
            duration_str = data["streams"][0].get("duration", "0")
            duration = float(duration_str)
            
            if duration <= 0:
                return False, "Invalid video duration"
            
            if duration > 180:  # Max 3 minutes
                return False, f"Video too long: {duration:.0f}s (max 180s)"
            
            logger.info(f"✅ Valid video: {duration:.1f}s")
            return True, ""
        
        except Exception as e:
            logger.error(f"❌ Parse error: {e}")
            return False, "Could not parse video metadata"
    
    except subprocess.TimeoutExpired:
        return False, "Video validation timeout"
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        return False, str(e)

# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

async def get_duration(video_path: str) -> float:
    """Get video duration"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, timeout=15, text=True
        )
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"⏱️ {duration:.1f}s")
            return duration
        return 0.0
    except:
        return 0.0

async def apply_copyright_filters(input_path: str, output_path: str) -> tuple[bool, str]:
    """Apply copyright-avoidance filters"""
    logger.info("🎨 Applying filters...")
    
    filter_complex = "eq=saturation=1.25:brightness=0.10:contrast=1.15"
    
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", filter_complex,
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-c:a", "copy",
        "-y", output_path
    ], 90, "Filters")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        return True, ""
    
    # Fallback: copy original
    if os.path.exists(input_path):
        shutil.copy(input_path, output_path)
        return True, ""
    
    return False, "Filter failed"

def generate_srt_with_emojis(duration: float) -> str:
    """Generate SRT with emojis"""
    num_captions = max(3, int(duration / 3))
    time_per = duration / num_captions
    blocks = []
    
    for i in range(num_captions):
        start = i * time_per
        end = start + time_per
        
        sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
        eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
        caption = random.choice(CAPTION_EMOJIS) if random.random() < 0.9 else random.choice(CAPTION_TEXT)
        
        blocks.append(f"{i+1}\n{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
                     f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + f"\n{caption}\n")
    
    return "\n".join(blocks)

async def apply_golden_captions(video_path: str, duration: float, output_path: str) -> tuple[bool, str]:
    """Apply golden captions"""
    logger.info("✨ Adding captions...")
    
    srt_path = output_path.replace(".mp4", ".srt")
    
    try:
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_srt_with_emojis(duration))
    except:
        shutil.copy(video_path, output_path)
        return True, ""
    
    srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial Black,FontSize=20,PrimaryColour=&H00FFD700,Bold=1,Outline=2,OutlineColour=&H00000000,Alignment=2,MarginV=40'",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-y", output_path
    ], 120, "Captions")
    
    cleanup(srt_path)
    
    if success:
        return True, ""
    
    shutil.copy(video_path, output_path)
    return True, ""

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove audio"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an",
        "-y", video_out
    ], 60, "Remove-Audio")
    
    if success:
        cleanup(video_in)
    
    return success

async def download_bgm(output: str) -> bool:
    """Download BGM"""
    logger.info("🎵 Downloading BGM...")
    
    bgm_url = random.choice(CHINA_BGM_URLS)
    
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            async with client.stream("GET", bgm_url) as response:
                if response.status_code == 200:
                    total = 0
                    with open(output, 'wb') as f:
                        async for chunk in response.aiter_bytes(1024*1024):
                            f.write(chunk)
                            total += len(chunk)
                    
                    if total > 10000:
                        logger.info("✅ BGM Downloaded")
                        return True
        return False
    except:
        return False

async def mix_audio_with_bgm(video_path: str, bgm_path: Optional[str], output_path: str) -> tuple[bool, str]:
    """Mix BGM"""
    logger.info("🎵 Mixing BGM...")
    
    if bgm_path and os.path.exists(bgm_path):
        success = run_ffmpeg([
            "ffmpeg", "-i", video_path, "-i", bgm_path,
            "-filter_complex", "[1:a]volume=0.20[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output_path
        ], 90, "Mix-BGM")
        
        if success:
            cleanup(video_path, bgm_path)
            return True, ""
    
    # Fallback
    if os.path.exists(video_path):
        shutil.copy(video_path, output_path)
        cleanup(video_path, bgm_path)
        return True, ""
    
    return False, "Mix failed"

async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload to YouTube"""
    logger.info("📤 YouTube Upload...")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds:
            return {"success": False, "error": "No YouTube credentials"}
        
        credentials = {
            "access_token": creds.get("access_token"),
            "refresh_token": creds.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        }
        
        from mainY import youtube_scheduler
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=description,
            video_url=video_path
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            logger.info(f"✅ Uploaded: {video_id}")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        logger.error(f"❌ {e}")
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINES
# ═══════════════════════════════════════════════════════════════════════

async def process_china_short(china_url: str, user_id: str, task_id: str):
    """Main processing pipeline for URL downloads"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start_time.isoformat()
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"[{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="china_short_")
        logger.info(f"📁 {temp_dir}")
        log_memory("START")
        
        # Download (5 methods)
        update(10, "Downloading (5 fallback methods)...")
        raw_video = os.path.join(temp_dir, "raw.mp4")
        success, error = await download_china_video(china_url, raw_video)
        if not success:
            raise Exception(error)
        
        # Duration
        update(20, "Analyzing...")
        duration = await get_duration(raw_video)
        if duration <= 0 or duration > 180:
            raise ValueError(f"Invalid duration: {duration:.0f}s")
        
        # Filters
        update(30, "Applying filters...")
        filtered_video = os.path.join(temp_dir, "filtered.mp4")
        await apply_copyright_filters(raw_video, filtered_video)
        
        # Remove audio
        update(50, "Removing audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered_video, silent_video):
            raise Exception("Remove audio failed")
        
        # Captions
        update(60, "Adding captions...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        await apply_golden_captions(silent_video, duration, captioned_video)
        
        # BGM
        update(75, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        await download_bgm(bgm_path)
        
        update(85, "Mixing BGM...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await mix_audio_with_bgm(captioned_video, bgm_path, final_video)
        if not success:
            raise Exception(error)
        
        # Upload
        title = f"Amazing China Short 🔥 #{random.choice(['Trending', 'Epic', 'Viral'])} #Shorts"
        description = "Amazing short video!\n\n#Shorts #Viral #Trending #ChinaShorts #MustWatch"
        
        update(95, "Uploading...")
        upload_result = await upload_to_youtube(final_video, title, description, user_id)
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        # Success
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("✅ SUCCESS!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video: {upload_result['video_id']}")
        logger.info("="*80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "message": "Uploaded!",
            "title": title,
            "description": description,
            "duration": round(duration, 1),
            "processing_time": round(elapsed, 1),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": str(e),
            "message": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir and os.path.exists(temp_dir):
            logger.info("🧹 Cleanup...")
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        gc.collect()
        log_memory("FINAL")


async def process_uploaded_video(video_path: str, user_id: str, task_id: str):
    """
    Process manually uploaded video file
    Same pipeline as URL processing, but skips download step
    """
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start_time.isoformat()
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"[{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="china_upload_")
        logger.info(f"📁 {temp_dir}")
        log_memory("START-UPLOAD")
        
        # Copy uploaded file to temp directory
        update(10, "Processing uploaded file...")
        raw_video = os.path.join(temp_dir, "uploaded.mp4")
        shutil.copy(video_path, raw_video)
        
        # Validate video
        update(15, "Validating video...")
        is_valid, error = await validate_video_file(raw_video)
        if not is_valid:
            raise ValueError(error)
        
        # Get duration
        update(20, "Analyzing video...")
        duration = await get_duration(raw_video)
        if duration <= 0 or duration > 180:
            raise ValueError(f"Invalid duration: {duration:.0f}s")
        
        logger.info(f"✅ Video duration: {duration:.1f}s")
        
        # Apply filters
        update(30, "Applying filters...")
        filtered_video = os.path.join(temp_dir, "filtered.mp4")
        success, error = await apply_copyright_filters(raw_video, filtered_video)
        if not success:
            raise Exception(error)
        
        # Remove audio
        update(50, "Removing audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered_video, silent_video):
            raise Exception("Remove audio failed")
        
        # Add captions
        update(60, "Adding golden captions...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        success, error = await apply_golden_captions(silent_video, duration, captioned_video)
        if not success:
            raise Exception(error)
        
        # Download BGM
        update(75, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        await download_bgm(bgm_path)
        
        # Mix audio
        update(85, "Mixing BGM...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await mix_audio_with_bgm(captioned_video, bgm_path, final_video)
        if not success:
            raise Exception(error)
        
        # Upload to YouTube
        update(95, "Uploading to YouTube...")
        title = f"Amazing China Short 🔥 #{random.choice(['Trending', 'Epic', 'Viral'])} #Shorts"
        description = "Amazing short video!\n\n#Shorts #Viral #Trending #ChinaShorts #MustWatch"
        
        upload_result = await upload_to_youtube(final_video, title, description, user_id)
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        # Success
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("✅ UPLOAD SUCCESS!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video: {upload_result['video_id']}")
        logger.info("="*80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "message": "Uploaded!",
            "title": title,
            "description": description,
            "duration": round(duration, 1),
            "processing_time": round(elapsed, 1),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ UPLOAD FAILED: {e}")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": str(e),
            "message": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        # Clean up temp directory
        if temp_dir and os.path.exists(temp_dir):
            logger.info("🧹 Cleanup...")
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Clean up uploaded file
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
            except:
                pass
        
        gc.collect()
        log_memory("FINAL-UPLOAD")

# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()

@router.post("/api/china-shorts/process")
async def process_endpoint(request: Request):
    """Process China Short from URL"""
    logger.info("🌐 URL PROCESS REQUEST")
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        china_url = (data.get("china_url") or "").strip()
        
        if not user_id:
            return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
        if not china_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "URL required"})
        
        task_id = str(uuid.uuid4())
        logger.info(f"✅ Task: {task_id}")
        
        await asyncio.wait_for(process_china_short(china_url, user_id, task_id), timeout=900)
        
        result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown"})
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
    except Exception as e:
        logger.error(f"❌ {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/api/china-shorts/process-upload")
async def process_upload_endpoint(
    user_id: str = Form(...),
    video_file: UploadFile = File(...)
):
    """
    NEW ENDPOINT: Process manually uploaded video file
    Accepts multipart/form-data with user_id and video_file
    """
    logger.info("🌐 UPLOAD REQUEST")
    logger.info(f"   User: {user_id}")
    logger.info(f"   File: {video_file.filename}")
    logger.info(f"   Type: {video_file.content_type}")
    
    uploaded_file_path = None
    
    try:
        # Validate user_id
        if not user_id:
            return JSONResponse(
                status_code=400, 
                content={"success": False, "error": "user_id required"}
            )
        
        # Validate file
        if not video_file:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No video file provided"}
            )
        
        # Check content type
        if not video_file.content_type or not video_file.content_type.startswith("video/"):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"Invalid file type: {video_file.content_type}. Must be a video file."}
            )
        
        # Create unique filename
        task_id = str(uuid.uuid4())
        file_ext = os.path.splitext(video_file.filename)[1] or ".mp4"
        uploaded_file_path = f"/tmp/china_upload_{task_id}{file_ext}"
        
        logger.info(f"✅ Task: {task_id}")
        logger.info(f"📂 Saving to: {uploaded_file_path}")
        
        # Save uploaded file
        success, error = await save_uploaded_file(video_file, uploaded_file_path)
        if not success:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": error}
            )
        
        # Process the uploaded video (with timeout)
        await asyncio.wait_for(
            process_uploaded_video(uploaded_file_path, user_id, task_id),
            timeout=900  # 15 minutes
        )
        
        # Get result
        result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
        return JSONResponse(content=result)
    
    except asyncio.TimeoutError:
        logger.error("❌ Processing timeout")
        return JSONResponse(
            status_code=408,
            content={"success": False, "error": "Processing timeout (max 15 minutes)"}
        )
    
    except Exception as e:
        logger.error(f"❌ Upload endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
    
    finally:
        # Cleanup uploaded file if still exists
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            try:
                os.remove(uploaded_file_path)
                logger.info(f"🧹 Cleaned up: {uploaded_file_path}")
            except:
                pass


@router.get("/api/china-shorts/status/{task_id}")
async def status_endpoint(task_id: str):
    """Get processing status for a task"""
    status = PROCESSING_STATUS.get(task_id)
    if not status:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Task not found"}
        )
    return JSONResponse(content=status)


@router.get("/api/china-shorts/health")
async def health_endpoint():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "ok",
        "version": "3.1",
        "features": {
            "url_download": {
                "enabled": True,
                "methods": [
                    "Douyin Internal API (iteminfo)",
                    "Mobile API (Android simulation)",
                    "yt-dlp Enhanced",
                    "M3U8 Stream Capture",
                    "TikTok Global API"
                ]
            },
            "manual_upload": {
                "enabled": True,
                "max_file_size": "100MB",
                "max_duration": "180 seconds",
                "supported_formats": ["mp4", "mov", "avi", "mkv", "webm", "flv"]
            },
            "processing": {
                "filters": "Saturation +25%, Brightness +10%, Contrast +15%",
                "audio": "Original removed, BGM added at 20%",
                "captions": "Golden captions with emojis",
                "upload": "Direct to YouTube"
            }
        }
    })


async def initialize():
    """Startup initialization"""
    logger.info("="*80)
    logger.info("🚀 CHINA SHORTS V3.1 (PRODUCTION + MANUAL UPLOAD)")
    logger.info("="*80)
    logger.info("✅ URL Download Methods:")
    logger.info("   1. Douyin Internal API (iteminfo)")
    logger.info("   2. Mobile API (Android)")
    logger.info("   3. yt-dlp Enhanced")
    logger.info("   4. M3U8 Stream Capture")
    logger.info("   5. TikTok Global API")
    logger.info("")
    logger.info("✅ NEW: Manual File Upload")
    logger.info("   • Direct video file upload (max 100MB)")
    logger.info("   • Same processing pipeline")
    logger.info("   • Validation & error handling")
    logger.info("="*80)
    log_memory("startup")


__all__ = ["router", "initialize"]

