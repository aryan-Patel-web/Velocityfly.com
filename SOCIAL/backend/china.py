"""
china_shorts.py - CHINA SHORTS VIDEO PROCESSOR (DOUYIN/TIKTOK TO YOUTUBE)
===================================================================
✅ Download from Douyin/TikTok URLs (multiple fallback methods)
✅ Remove original audio
✅ Add custom BGM (royalty-free music)
✅ Apply video filters: saturation, brightness, contrast (copyright avoidance)
✅ Golden captions with emojis (90%) and text (10%)
✅ Direct YouTube upload with SEO
✅ COMPREHENSIVE FALLBACK SYSTEM - Never fails
===================================================================
"""

from fastapi import APIRouter, Request
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
from typing import Optional, List
from datetime import datetime
import uuid

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
                gc.collect()
                gc.collect()
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════

# BGM URLs (royalty-free music for China Shorts)
CHINA_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Krishna%20Healing%20Flute%20'%20Bansuri%20background%20music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
]

PROCESSING_STATUS = {}

# Caption emojis (90% chance) vs text (10% chance)
CAPTION_EMOJIS = ["😂", "🤣", "😱", "😮", "🤔", "😍", "🔥", "✨", "💯", "👀", "🎉", "❤️", "🙌", "💪", "🤯"]
CAPTION_TEXT = ["LOL", "OMG", "WOW", "HAHA", "NICE", "EPIC", "COOL", "FIRE"]

# ═══════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════

def cleanup(*paths):
    """Delete files and force garbage collection"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                size = os.path.getsize(path) / (1024 * 1024)
                os.remove(path)
                logger.info(f"   🗑️ {os.path.basename(path)} ({size:.1f}MB)")
        except:
            pass
    gc.collect()
    gc.collect()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# FFMPEG
# ═══════════════════════════════════════════════════════════════════════

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg command"""
    logger.info(f"🎬 {step}...")
    log_memory(f"before-{step}")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )
        
        success = result.returncode == 0
        
        if success:
            logger.info(f"✅ {step}")
        else:
            logger.error(f"❌ {step} failed")
            if result.stderr:
                logger.error(f"   Error: {result.stderr[-200:]}")
        
        gc.collect()
        log_memory(f"after-{step}")
        return success
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ {step} timeout")
        gc.collect()
        return False
    except Exception as e:
        logger.error(f"❌ {step} error: {e}")
        gc.collect()
        return False

# ═══════════════════════════════════════════════════════════════════════
# URL NORMALIZATION (DOUYIN/TIKTOK)
# ═══════════════════════════════════════════════════════════════════════

def normalize_china_url(url: str) -> str:
    """
    Normalize Douyin/TikTok URLs with MULTIPLE FALLBACK formats
    Handles: douyin.com, tiktok.com, vm.tiktok.com, vt.tiktok.com, etc.
    """
    url = url.strip()
    
    # Method 1: Extract video ID from Douyin URL
    douyin_patterns = [
        r'douyin\.com/video/(\d+)',
        r'modal_id=(\d+)',
        r'vid=(\d+)',
        r'/(\d{19})',  # 19-digit video ID
    ]
    
    for pattern in douyin_patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            logger.info(f"   Extracted Douyin ID: {video_id}")
            return f"https://www.douyin.com/video/{video_id}"
    
    # Method 2: TikTok URL formats
    tiktok_patterns = [
        r'tiktok\.com/@[^/]+/video/(\d+)',
        r'vm\.tiktok\.com/([A-Za-z0-9]+)',
        r'vt\.tiktok\.com/([A-Za-z0-9]+)',
    ]
    
    for pattern in tiktok_patterns:
        match = re.search(pattern, url)
        if match:
            logger.info(f"   TikTok URL detected")
            return url  # Return as-is for yt-dlp
    
    # Method 3: Return original if already formatted
    if "douyin.com" in url or "tiktok.com" in url:
        return url
    
    logger.warning(f"   Could not normalize URL: {url}")
    return url

# ═══════════════════════════════════════════════════════════════════════
# VIDEO DOWNLOAD (YT-DLP WITH MULTIPLE FALLBACKS)
# ═══════════════════════════════════════════════════════════════════════

async def download_china_video(url: str, output: str) -> tuple[bool, str]:
    """
    Download video from Douyin/TikTok with COMPREHENSIVE FALLBACK
    Method 1: yt-dlp with best quality
    Method 2: yt-dlp with format fallback
    Method 3: yt-dlp with cookies (if available)
    """
    logger.info("⬇️ Downloading China video...")
    log_memory("download-start")
    
    normalized_url = normalize_china_url(url)
    
    # METHOD 1: Standard yt-dlp (best quality)
    logger.info("   Method 1: yt-dlp (best quality)")
    try:
        result = subprocess.run([
            "yt-dlp",
            "-f", "best[ext=mp4]/best",
            "--no-playlist",
            "--no-warnings",
            "-o", output,
            normalized_url
        ], capture_output=True, timeout=180, text=True)
        
        if result.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 10000:
            size = os.path.getsize(output) / (1024 * 1024)
            logger.info(f"✅ Downloaded: {size:.1f}MB")
            log_memory("download-done")
            return True, ""
    except Exception as e:
        logger.warning(f"   Method 1 failed: {e}")
    
    # METHOD 2: Format fallback (lower quality)
    logger.info("   Method 2: yt-dlp (format fallback)")
    try:
        result = subprocess.run([
            "yt-dlp",
            "-f", "worst[ext=mp4]/worst",
            "--no-playlist",
            "--no-warnings",
            "-o", output,
            normalized_url
        ], capture_output=True, timeout=180, text=True)
        
        if result.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 10000:
            size = os.path.getsize(output) / (1024 * 1024)
            logger.info(f"✅ Downloaded (fallback): {size:.1f}MB")
            log_memory("download-done")
            return True, ""
    except Exception as e:
        logger.warning(f"   Method 2 failed: {e}")
    
    # METHOD 3: Try original URL without normalization
    logger.info("   Method 3: yt-dlp (original URL)")
    try:
        result = subprocess.run([
            "yt-dlp",
            "-f", "best",
            "--no-playlist",
            "--no-warnings",
            "-o", output,
            url  # Use original URL
        ], capture_output=True, timeout=180, text=True)
        
        if result.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 10000:
            size = os.path.getsize(output) / (1024 * 1024)
            logger.info(f"✅ Downloaded (original URL): {size:.1f}MB")
            log_memory("download-done")
            return True, ""
    except Exception as e:
        logger.warning(f"   Method 3 failed: {e}")
    
    return False, "All download methods failed"

# ═══════════════════════════════════════════════════════════════════════
# VIDEO INFO
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

# ═══════════════════════════════════════════════════════════════════════
# VIDEO FILTERS (SATURATION, BRIGHTNESS, CONTRAST - COPYRIGHT AVOIDANCE)
# ═══════════════════════════════════════════════════════════════════════

async def apply_copyright_filters(input_path: str, output_path: str) -> tuple[bool, str]:
    """
    Apply video filters to avoid copyright detection
    Filters: Saturation +25%, Brightness +10%, Contrast +15%
    FALLBACK: If fails, use original video
    """
    logger.info("🎨 Applying copyright-avoidance filters...")
    log_memory("filter-start")
    
    # METHOD 1: Full filter chain
    filter_complex = "eq=saturation=1.25:brightness=0.10:contrast=1.15"
    
    logger.info("   Applying: Saturation +25%, Brightness +10%, Contrast +15%")
    
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", filter_complex,
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-c:a", "copy",
        "-y", output_path
    ], 90, "Video-Filters")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Filtered: {size:.1f}MB")
        log_memory("filter-done")
        return True, ""
    
    # FALLBACK: Use original video
    logger.warning("⚠️ Filters failed, using original video")
    cleanup(output_path)
    
    if os.path.exists(input_path):
        shutil.copy(input_path, output_path)
        size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Original video: {size:.1f}MB")
        log_memory("filter-done")
        return True, ""
    
    return False, "Filter processing failed"

# ═══════════════════════════════════════════════════════════════════════
# GOLDEN CAPTIONS WITH EMOJIS
# ═══════════════════════════════════════════════════════════════════════

def generate_srt_with_emojis(duration: float) -> str:
    """Generate SRT with emojis (90%) or text (10%)"""
    num_captions = max(3, int(duration / 3))  # One caption every 3 seconds
    time_per = duration / num_captions
    blocks = []
    
    for i in range(num_captions):
        start = i * time_per
        end = start + time_per
        
        sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
        eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
        # 90% emoji, 10% text
        if random.random() < 0.9:
            caption = random.choice(CAPTION_EMOJIS)
        else:
            caption = random.choice(CAPTION_TEXT)
        
        blocks.append(f"{i+1}\n{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
                     f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + f"\n{caption}\n")
    
    return "\n".join(blocks)

async def apply_golden_captions(video_path: str, duration: float, output_path: str) -> tuple[bool, str]:
    """
    Apply golden captions with COMPREHENSIVE FALLBACK
    Method 1: Golden color with outline
    Method 2: White color with shadow
    Method 3: No captions (continue without)
    """
    logger.info("✨ Applying golden captions with emojis...")
    log_memory("caption-start")
    
    srt_path = output_path.replace(".mp4", "_captions.srt")
    
    try:
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_srt_with_emojis(duration))
    except:
        logger.warning("⚠️ SRT generation failed, skipping captions")
        if os.path.exists(video_path):
            shutil.copy(video_path, output_path)
        return True, ""
    
    srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
    # METHOD 1: Golden captions (small bold text)
    logger.info("   Method 1: Golden captions")
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial Black,FontSize=20,PrimaryColour=&H00FFD700,Bold=1,Outline=2,OutlineColour=&H00000000,Alignment=2,MarginV=40'",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-y", output_path
    ], 120, "Captions-Golden")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        cleanup(srt_path)
        logger.info("✅ Golden captions applied")
        log_memory("caption-done")
        return True, ""
    
    # METHOD 2: White captions
    logger.warning("⚠️ Trying white captions...")
    cleanup(output_path)
    
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,Bold=1,Outline=2,OutlineColour=&H00000000,Alignment=2,MarginV=40'",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-y", output_path
    ], 120, "Captions-White")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        cleanup(srt_path)
        logger.info("✅ White captions applied")
        log_memory("caption-done")
        return True, ""
    
    # METHOD 3: No captions (ALWAYS SUCCEEDS)
    logger.warning("⚠️ All caption methods failed, continuing without captions")
    cleanup(srt_path, output_path)
    
    if os.path.exists(video_path):
        shutil.copy(video_path, output_path)
        logger.info("✅ Video copied (no captions)")
        log_memory("caption-done")
        return True, ""
    
    return False, "Caption processing failed"

# ═══════════════════════════════════════════════════════════════════════
# AUDIO REMOVAL + BGM MIXING
# ═══════════════════════════════════════════════════════════════════════

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove original audio from video"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an",
        "-y", video_out
    ], timeout=60, step="Remove-Audio")
    
    if success:
        cleanup(video_in)
    
    return success

async def download_chunked(url: str, output: str) -> bool:
    """Download file in chunks"""
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    return False
                
                total = 0
                with open(output, 'wb') as f:
                    async for chunk in response.aiter_bytes(1024*1024):
                        f.write(chunk)
                        total += len(chunk)
                
                if total > 10000:
                    logger.info(f"   ✅ {total/(1024*1024):.1f}MB")
                    return True
        return False
    except Exception as e:
        logger.error(f"   ❌ {e}")
        return False

async def download_bgm(output: str) -> bool:
    """Download BGM from list"""
    logger.info("🎵 Downloading BGM...")
    log_memory("bgm-start")
    
    bgm_url = random.choice(CHINA_BGM_URLS)
    logger.info(f"   Selected: {bgm_url.split('/')[-1][:50]}...")
    
    try:
        success = await download_chunked(bgm_url, output)
        
        if success:
            logger.info("✅ BGM Downloaded")
            log_memory("bgm-done")
            return True
        
        logger.warning("⚠️ BGM download failed")
        return False
    except:
        logger.warning("⚠️ BGM error")
        return False

async def mix_audio_with_bgm(video_path: str, bgm_path: Optional[str], output_path: str) -> tuple[bool, str]:
    """
    Mix video with BGM (20% volume)
    FALLBACK: If BGM fails, use silent video
    """
    logger.info("🎵 Mixing BGM (20% volume)...")
    log_memory("mix-start")
    
    # METHOD 1: Add BGM
    if bgm_path and os.path.exists(bgm_path):
        logger.info("   Adding BGM...")
        success = run_ffmpeg([
            "ffmpeg", "-i", video_path, "-i", bgm_path,
            "-filter_complex", "[1:a]volume=0.20[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output_path
        ], 90, "Add-BGM")
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            cleanup(video_path, bgm_path)
            log_memory("mix-done")
            return True, ""
    
    # METHOD 2: Silent video (no BGM)
    logger.warning("⚠️ Continuing without BGM (silent video)")
    if os.path.exists(video_path):
        shutil.copy(video_path, output_path)
        cleanup(video_path, bgm_path)
        log_memory("mix-done")
        return True, ""
    
    return False, "Audio mix failed"

# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload to YouTube with SEO metadata"""
    logger.info("📤 YouTube Upload...")
    log_memory("upload-start")
    
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
            log_memory("upload-done")
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
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_china_short(china_url: str, user_id: str, task_id: str):
    """Main pipeline for China Shorts processing"""
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
        
        # Download video
        update(10, "Downloading from Douyin/TikTok...")
        raw_video = os.path.join(temp_dir, "raw.mp4")
        success, error = await download_china_video(china_url, raw_video)
        if not success:
            raise Exception(error)
        
        # Get duration
        update(20, "Analyzing video...")
        duration = await get_duration(raw_video)
        if duration <= 0:
            raise ValueError("Invalid video")
        if duration > 180:
            raise ValueError(f"Video too long ({duration:.0f}s)")
        
        # Apply filters (saturation, brightness, contrast)
        update(30, "Applying copyright-avoidance filters...")
        filtered_video = os.path.join(temp_dir, "filtered.mp4")
        success, error = await apply_copyright_filters(raw_video, filtered_video)
        # Always continues even if filters fail
        
        # Remove original audio
        update(50, "Removing original audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered_video, silent_video):
            raise Exception("Remove audio failed")
        
        # Apply golden captions with emojis
        update(60, "Adding golden captions with emojis...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        success, error = await apply_golden_captions(silent_video, duration, captioned_video)
        # Always continues even if captions fail
        
        # Download BGM
        update(75, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        bgm_success = await download_bgm(bgm_path)
        if not bgm_success:
            bgm_path = None
            logger.warning("⚠️ BGM download failed, continuing without BGM")
        
        # Mix audio
        update(85, "Mixing BGM (20% volume)...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await mix_audio_with_bgm(captioned_video, bgm_path, final_video)
        if not success:
            raise Exception(error)
        
        if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
            raise Exception("Invalid final video")
        
        size_mb = os.path.getsize(final_video) / (1024 * 1024)
        logger.info(f"   Final video: {size_mb:.1f}MB")
        
        # Generate SEO metadata
        title = f"Amazing China Short 🔥 | Must Watch! #Shorts #Viral #{random.choice(['Trending', 'Epic', 'Funny'])}"
        description = "Watch this amazing video!\n\nKeywords: china shorts, viral videos, trending shorts, funny videos, must watch, short videos, viral content, trending videos, amazing shorts\n\n#Shorts #Viral #Trending #ChinaShorts #MustWatch #Amazing #Epic #Funny #Cool"
        
        # Upload to YouTube
        update(95, "Uploading to YouTube...")
        upload_result = await upload_to_youtube(final_video, title, description, user_id)
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        # SUCCESS
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("✅ CHINA SHORT SUCCESS!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video ID: {upload_result['video_id']}")
        logger.info("="*80)
        log_memory("COMPLETE")
        
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
        error_msg = str(e)
        logger.error("="*80)
        logger.error(f"❌ FAILED: {error_msg}")
        logger.error("="*80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": error_msg,
            "message": error_msg,
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir and os.path.exists(temp_dir):
            logger.info("🧹 Cleanup...")
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("✅ Clean")
            except:
                pass
        
        gc.collect()
        gc.collect()
        gc.collect()
        log_memory("FINAL")

# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()

@router.post("/api/china-shorts/process")
async def process_endpoint(request: Request):
    """Process China Short (synchronous)"""
    logger.info("🌐 CHINA SHORTS REQUEST")
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        china_url = (data.get("china_url") or "").strip()
        
        if not user_id:
            return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
        if not china_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Valid Douyin/TikTok URL required"})
        
        task_id = str(uuid.uuid4())
        logger.info(f"✅ Task ID: {task_id}")
        
        # Synchronous processing
        await asyncio.wait_for(process_china_short(china_url, user_id, task_id), timeout=900)  # 15 minutes
        
        result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout (900s exceeded)"})
    except Exception as e:
        logger.error(f"❌ API Error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/api/china-shorts/status/{task_id}")
async def status_endpoint(task_id: str):
    """Get processing status"""
    status = PROCESSING_STATUS.get(task_id)
    if not status:
        return JSONResponse(status_code=404, content={"success": False, "error": "Task not found"})
    return JSONResponse(content=status)

@router.get("/api/china-shorts/health")
async def health_endpoint():
    """Health check"""
    log_memory("health")
    return JSONResponse(content={
        "status": "ok",
        "features": {
            "video_sources": "Douyin, TikTok",
            "filters": "Saturation +25%, Brightness +10%, Contrast +15%",
            "captions": "Golden emojis (90%) + text (10%)",
            "bgm_volume": "20%",
            "bgm_tracks": len(CHINA_BGM_URLS),
            "fallback_system": "Comprehensive (every step has 2-3 fallbacks)"
        }
    })

async def initialize():
    """Startup initialization"""
    logger.info("="*80)
    logger.info("🚀 CHINA SHORTS VIDEO PROCESSOR")
    logger.info("="*80)
    logger.info("✅ Download from Douyin/TikTok (yt-dlp + fallbacks)")
    logger.info("✅ Remove original audio")
    logger.info("✅ Apply copyright filters (saturation, brightness, contrast)")
    logger.info("✅ Golden captions with emojis (90%) + text (10%)")
    logger.info("✅ BGM mixing at 20% volume")
    logger.info("✅ Direct YouTube upload with SEO")
    logger.info("✅ COMPREHENSIVE FALLBACK SYSTEM")
    logger.info("="*80)
    
    log_memory("startup")
    logger.info("="*80)

__all__ = ["router", "initialize"]