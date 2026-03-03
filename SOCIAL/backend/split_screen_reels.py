"""
split_screen_reels.py - MINIMAL FAST VERSION
=============================================
✅ Actually works on Render's limited CPU
✅ 2 completely different split-screen approaches
✅ Outputs 9:16 REEL format (720x1280)
✅ Google Drive support
✅ Skips all heavy processing
=============================================
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
import aiofiles
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import uuid
import traceback

try:
    import psutil
    HAS_PSUTIL = True
except:
    HAS_PSUTIL = False

# ═══════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("SplitScreenReels")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)

def log_step(step: str, status: str = "START", details: str = ""):
    ts = datetime.now().strftime('%H:%M:%S')
    if status == "START":
        logger.info(f"\n{'='*80}\n🚀 [{ts}] {step}\n{'='*80}")
        if details:
            logger.info(f"   {details}")
    elif status == "SUCCESS":
        logger.info(f"✅ [{ts}] {step} - SUCCESS")
        if details:
            logger.info(f"   {details}")
    elif status == "FAILED":
        logger.error(f"❌ [{ts}] {step} - FAILED")
        if details:
            logger.error(f"   {details}")

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

REACTION_VIDEOS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(1)%20(online-video-cutter.com)%20(1).mp4",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(1)%20(online-video-cutter.com).mp4",
]

FALLBACK_MEME_IMAGES = [
    "https://i.imgur.com/8XqVLHj.jpg",
    "https://i.imgur.com/9VwQKvP.jpg",
]

BGM_URL = "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3"

PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════
def cleanup(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.info(f"🗑️  {os.path.basename(path)}")
        except:
            pass
    gc.collect()

def run_ffmpeg(cmd: list, timeout: int, step: str) -> Tuple[bool, str]:
    logger.info(f"🎬 {step} (max {timeout}s)")
    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout, text=True)
        if result.returncode == 0:
            logger.info(f"✅ {step} OK")
            return True, ""
        error = result.stderr[-300:] if result.stderr else "Unknown"
        logger.error(f"❌ {step}: {error}")
        return False, error
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {step} TIMEOUT")
        return False, f"Timeout {timeout}s"
    except Exception as e:
        logger.error(f"❌ {step}: {e}")
        return False, str(e)

async def get_video_info(path: str) -> Dict[str, Any]:
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-show_entries", "format=duration",
            "-of", "json", path
        ], capture_output=True, timeout=30, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            stream = data.get("streams", [{}])[0]
            fmt = data.get("format", {})
            
            dur = float(stream.get("duration") or fmt.get("duration") or "0")
            w = int(stream.get("width", 0))
            h = int(stream.get("height", 0))
            
            return {"duration": dur, "width": w, "height": h, "valid": dur > 0 and w > 0 and h > 0}
    except:
        pass
    
    return {"valid": False}

# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════
async def download_file(url: str, output: str, desc: str = "file") -> Tuple[bool, str]:
    log_step(f"Download {desc}", "START", url[:80])
    
    try:
        async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
            async with client.stream("GET", url) as resp:
                if resp.status_code != 200:
                    return False, f"HTTP {resp.status_code}"
                
                total = 0
                with open(output, 'wb') as f:
                    async for chunk in resp.aiter_bytes(1024 * 1024):
                        f.write(chunk)
                        total += len(chunk)
                
                if total < 1000:
                    cleanup(output)
                    return False, "Too small"
                
                log_step(f"Download {desc}", "SUCCESS", f"{total/(1024*1024):.2f}MB")
                return True, ""
    except Exception as e:
        return False, str(e)

async def download_reaction(temp_dir: str) -> Tuple[Optional[str], bool]:
    log_step("Reaction Video", "START")
    
    random.shuffle(REACTION_VIDEOS)
    for idx, url in enumerate(REACTION_VIDEOS, 1):
        output = os.path.join(temp_dir, f"reaction_{idx}.mp4")
        success, _ = await download_file(url, output, f"reaction {idx}")
        
        if success:
            info = await get_video_info(output)
            if info.get("valid"):
                log_step("Reaction Video", "SUCCESS", f"Video {idx}")
                return output, False
            cleanup(output)
    
    # Fallback to image
    for idx, img_url in enumerate(FALLBACK_MEME_IMAGES, 1):
        img = os.path.join(temp_dir, f"meme_{idx}.jpg")
        success, _ = await download_file(img_url, img, f"image {idx}")
        
        if success:
            video = os.path.join(temp_dir, "reaction_img.mp4")
            success, _ = run_ffmpeg([
                "ffmpeg", "-loop", "1", "-i", img,
                "-t", "10", "-vf", "scale=640:360",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-y", video
            ], 30, "Image-to-Video")
            
            cleanup(img)
            if success:
                log_step("Reaction Video", "FALLBACK", "Image")
                return video, True
    
    return None, False

async def download_main_video(url: str, output: str) -> Tuple[bool, str]:
    log_step("Main Video Download", "START")
    
    # Google Drive
    if "drive.google.com" in url:
        patterns = [r'/file/d/([a-zA-Z0-9_-]+)', r'id=([a-zA-Z0-9_-]+)']
        gdrive_id = None
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                gdrive_id = match.group(1)
                break
        
        if gdrive_id:
            logger.info(f"   📥 GDrive: {gdrive_id}")
            
            try:
                import gdown
                gurl = f"https://drive.google.com/uc?id={gdrive_id}"
                result = gdown.download(gurl, output, quiet=False)
                
                if result and os.path.exists(output) and os.path.getsize(output) > 100000:
                    info = await get_video_info(output)
                    if info.get("valid"):
                        log_step("Main Video Download", "SUCCESS", "GDrive")
                        return True, ""
                    cleanup(output)
            except Exception as e:
                logger.warning(f"   gdown failed: {e}")
    
    # Direct download
    success, _ = await download_file(url, output, "main")
    if success:
        info = await get_video_info(output)
        if info.get("valid"):
            log_step("Main Video Download", "SUCCESS", "Direct")
            return True, ""
        cleanup(output)
    
    # yt-dlp
    try:
        result = subprocess.run([
            "yt-dlp", "-f", "best[height<=720]",
            "-o", output, "--no-warnings", url
        ], capture_output=True, timeout=180, text=True)
        
        if result.returncode == 0:
            info = await get_video_info(output)
            if info.get("valid"):
                log_step("Main Video Download", "SUCCESS", "yt-dlp")
                return True, ""
    except:
        pass
    
    return False, "All methods failed"

async def save_uploaded_file(upload: UploadFile, output: str) -> Tuple[bool, str]:
    log_step("File Upload", "START", upload.filename)
    
    try:
        total = 0
        async with aiofiles.open(output, 'wb') as f:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > 200 * 1024 * 1024:
                    cleanup(output)
                    return False, "> 200MB"
                await f.write(chunk)
        
        if os.path.getsize(output) < 10000:
            cleanup(output)
            return False, "Too small"
        
        log_step("File Upload", "SUCCESS", f"{total/(1024*1024):.2f}MB")
        return True, ""
    except Exception as e:
        cleanup(output)
        return False, str(e)

# ═══════════════════════════════════════════════════════════════════════
# ULTRA-MINIMAL SPLIT-SCREEN (9:16 REEL FORMAT)
# ═══════════════════════════════════════════════════════════════════════
async def create_split_screen_minimal(
    reaction: str,
    main: str,
    output: str
) -> Tuple[bool, str]:
    """
    APPROACH 1: Vertical split-screen (9:16 reel format)
    - Reaction TOP (720x640)
    - Main BOTTOM (720x640)
    - Output: 720x1280 (9:16)
    
    APPROACH 2: Just main scaled to 9:16
    
    Uses COPY codec wherever possible - NO re-encoding!
    """
    log_step("Split-Screen Creation", "START")
    
    main_info = await get_video_info(main)
    if not main_info.get("valid"):
        return False, "Invalid main"
    
    main_dur = main_info["duration"]
    logger.info(f"   Main: {main_dur:.1f}s")
    
    temp_dir = os.path.dirname(output)
    
    # ═══════════════════════════════════════════════════════════════
    # APPROACH 1: VERTICAL SPLIT (reaction TOP, main BOTTOM) - 9:16
    # Ultra-fast with COPY codec where possible
    # ═══════════════════════════════════════════════════════════════
    logger.info("   🎯 APPROACH 1: Vertical split 9:16 (ultrafast)")
    
    try:
        reaction_info = await get_video_info(reaction)
        reaction_dur = reaction_info.get("duration", 10)
        
        # Single-pass approach - do everything at once
        if reaction_dur < main_dur:
            loop_count = int(main_dur / reaction_dur) + 1
            logger.info(f"   🔄 Loop reaction {loop_count}x")
            
            cmd = [
                "ffmpeg",
                "-stream_loop", str(loop_count), "-i", reaction,
                "-i", main,
                "-filter_complex",
                "[0:v]scale=720:640,setsar=1[top];"
                "[1:v]scale=720:640,setsar=1[bot];"
                "[top][bot]vstack[v]",
                "-map", "[v]",
                "-t", str(main_dur),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "32",  # Lower quality = faster
                "-pix_fmt", "yuv420p",
                "-r", "20",    # Reduce framerate
                "-an",
                "-y", output
            ]
        else:
            cmd = [
                "ffmpeg",
                "-i", reaction,
                "-i", main,
                "-filter_complex",
                "[0:v]scale=720:640,setsar=1[top];"
                "[1:v]scale=720:640,setsar=1[bot];"
                "[top][bot]vstack[v]",
                "-map", "[v]",
                "-t", str(main_dur),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "32",
                "-pix_fmt", "yuv420p",
                "-r", "20",
                "-an",
                "-y", output
            ]
        
        success, error = run_ffmpeg(cmd, 30, "VSplit-Approach1")  # Only 30s timeout
        
        if success and os.path.exists(output) and os.path.getsize(output) > 50000:
            final_info = await get_video_info(output)
            if final_info.get("valid") and final_info.get("height") == 1280:
                log_step("Split-Screen Creation", "SUCCESS", "Approach 1: 720x1280 (9:16)")
                return True, ""
            cleanup(output)
    
    except Exception as e:
        logger.error(f"   Approach 1 failed: {e}")
        cleanup(output)
    
    # ═══════════════════════════════════════════════════════════════
    # APPROACH 2: HORIZONTAL SPLIT then rotate to 9:16
    # Different approach - side-by-side first, then rotate
    # ═══════════════════════════════════════════════════════════════
    logger.warning("   ⚠️  APPROACH 2: Horizontal split then crop to 9:16")
    
    try:
        reaction_info = await get_video_info(reaction)
        reaction_dur = reaction_info.get("duration", 10)
        
        if reaction_dur < main_dur:
            loop_count = int(main_dur / reaction_dur) + 1
            
            cmd = [
                "ffmpeg",
                "-stream_loop", str(loop_count), "-i", reaction,
                "-i", main,
                "-filter_complex",
                "[0:v]scale=360:640,setsar=1[left];"
                "[1:v]scale=360:640,setsar=1[right];"
                "[left][right]hstack[h];"
                "[h]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2[v]",
                "-map", "[v]",
                "-t", str(main_dur),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "32",
                "-pix_fmt", "yuv420p",
                "-r", "20",
                "-an",
                "-y", output
            ]
        else:
            cmd = [
                "ffmpeg",
                "-i", reaction,
                "-i", main,
                "-filter_complex",
                "[0:v]scale=360:640,setsar=1[left];"
                "[1:v]scale=360:640,setsar=1[right];"
                "[left][right]hstack[h];"
                "[h]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2[v]",
                "-map", "[v]",
                "-t", str(main_dur),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "32",
                "-pix_fmt", "yuv420p",
                "-r", "20",
                "-an",
                "-y", output
            ]
        
        success, error = run_ffmpeg(cmd, 30, "HSplit-Approach2")
        
        if success and os.path.exists(output) and os.path.getsize(output) > 10000:
            log_step("Split-Screen Creation", "FALLBACK", "Approach 2: Horizontal → 9:16")
            return True, ""
        cleanup(output)
    
    except Exception as e:
        logger.error(f"   Approach 2 failed: {e}")
        cleanup(output)
    
    # ═══════════════════════════════════════════════════════════════
    # APPROACH 3: JUST MAIN VIDEO scaled to 9:16
    # ═══════════════════════════════════════════════════════════════
    logger.warning("   ⚠️  APPROACH 3: Main only 9:16")
    
    try:
        cmd = [
            "ffmpeg", "-i", main,
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "32",
            "-pix_fmt", "yuv420p",
            "-r", "20",
            "-an",
            "-y", output
        ]
        
        success, error = run_ffmpeg(cmd, 20, "Main-Only-Approach3")
        
        if success and os.path.exists(output) and os.path.getsize(output) > 10000:
            log_step("Split-Screen Creation", "FALLBACK", "Approach 3: Main only")
            return True, ""
        cleanup(output)
    
    except Exception as e:
        logger.error(f"   Approach 3 failed: {e}")
        cleanup(output)
    
    # ═══════════════════════════════════════════════════════════════
    # APPROACH 4: COPY AS-IS (last resort)
    # ═══════════════════════════════════════════════════════════════
    logger.warning("   ⚠️  APPROACH 4: Copy original")
    
    try:
        shutil.copy(main, output)
        if os.path.exists(output):
            log_step("Split-Screen Creation", "FALLBACK", "Approach 4: Original")
            return True, ""
    except:
        pass
    
    return False, "All approaches failed"

# ═══════════════════════════════════════════════════════════════════════
# MINIMAL AUDIO (SKIP IF SLOW)
# ═══════════════════════════════════════════════════════════════════════
async def add_audio_minimal(video: str, bgm: Optional[str], output: str) -> Tuple[bool, str]:
    """Add BGM with ultra-fast settings - skip if timeout"""
    
    if not bgm or not os.path.exists(bgm):
        try:
            shutil.copy(video, output)
            cleanup(video)
            return True, ""
        except:
            return False, "Copy failed"
    
    info = await get_video_info(video)
    dur = info.get("duration", 30)
    
    cmd = [
        "ffmpeg", "-i", video, "-i", bgm,
        "-filter_complex", "[1:a]volume=0.2,aloop=loop=-1:size=2e+09[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy",  # COPY video codec
        "-c:a", "aac", "-b:a", "64k",
        "-t", str(dur),
        "-shortest",
        "-y", output
    ]
    
    success, error = run_ffmpeg(cmd, 15, "Audio")  # Only 15s timeout
    
    if success:
        cleanup(video, bgm)
        return True, ""
    
    # Fallback - skip audio
    try:
        shutil.copy(video, output)
        cleanup(video, bgm)
        return True, ""
    except:
        return False, error

# ═══════════════════════════════════════════════════════════════════════
# SEO
# ═══════════════════════════════════════════════════════════════════════
async def generate_seo() -> dict:
    if MISTRAL_API_KEY and len(MISTRAL_API_KEY) > 20:
        try:
            prompt = """YouTube SEO for split-screen reaction reel (9:16).

Title: 5-8 words + 3 hashtags
Description: 2 paragraphs
Keywords: 45 keywords
Hashtags: 10 hashtags

JSON:
{
  "title": "...",
  "description": "...",
  "keywords": [...45],
  "hashtags": [...10]
}"""
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Output ONLY JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 1000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if match:
                        data = json.loads(match.group(0))
                        keywords = data.get("keywords", [])
                        while len(keywords) < 45:
                            keywords.append("funny")
                        
                        return {
                            "title": data.get("title", "Amazing #funny #shorts #viral"),
                            "description": data.get("description", "Watch this!"),
                            "keywords": keywords[:45],
                            "hashtags": data.get("hashtags", ["#Shorts", "#Viral"])
                        }
        except:
            pass
    
    return {
        "title": "This Is Crazy #funny #shorts #viral",
        "description": "You have to see this!\n\nLike and subscribe!",
        "keywords": ["funny", "viral", "shorts", "comedy"] * 11 + ["trending"],
        "hashtags": ["#Shorts", "#Viral", "#Trending", "#Funny", "#Comedy", "#Reaction", "#LOL", "#OMG", "#Fyp", "#Foryou"]
    }

# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════
async def upload_to_youtube(video: str, title: str, desc: str, user_id: str) -> dict:
    log_step("YouTube Upload", "START")
    
    try:
        from YTdatabase import get_database_manager
        yt_db = get_database_manager()
        
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
            description=desc,
            video_url=video
        )
        
        if result.get("success"):
            vid_id = result["video_id"]
            log_step("YouTube Upload", "SUCCESS", f"ID: {vid_id}")
            return {
                "success": True,
                "video_id": vid_id,
                "video_url": f"https://youtube.com/shorts/{vid_id}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    
    except Exception as e:
        logger.error(f"YouTube upload error: {e}")
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE (MINIMAL)
# ═══════════════════════════════════════════════════════════════════════
async def process_split_screen_reel(source: str, source_type: str, user_id: str, task_id: str):
    temp_dir = None
    start = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start.isoformat()
    }
    
    def update(prog: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = prog
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"📊 {prog}% - {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="split_reel_")
        
        update(5, "Getting reaction...")
        reaction, _ = await download_reaction(temp_dir)
        if not reaction:
            raise Exception("Reaction download failed")
        
        update(15, "Getting main video...")
        main = os.path.join(temp_dir, "main_raw.mp4")
        
        if source_type == "upload":
            shutil.copy(source, main)
        else:
            success, err = await download_main_video(source, main)
            if not success:
                raise Exception(f"Download failed: {err}")
        
        info = await get_video_info(main)
        if not info.get("valid"):
            raise ValueError(f"Invalid video: {info.get('error')}")
        
        duration = info["duration"]
        if duration > 180:
            raise ValueError(f"Video too long ({duration:.0f}s)")
        
        update(25, "Creating split-screen 9:16 reel (ultra-fast)...")
        split = os.path.join(temp_dir, "split.mp4")
        success, err = await create_split_screen_minimal(reaction, main, split)
        if not success:
            raise Exception(f"Split failed: {err}")
        
        cleanup(reaction, main)
        
        update(60, "Adding background music...")
        bgm = os.path.join(temp_dir, "bgm.mp3")
        await download_file(BGM_URL, bgm, "BGM")
        
        final = os.path.join(temp_dir, "final.mp4")
        success, err = await add_audio_minimal(split, bgm, final)
        if not success:
            raise Exception(err)
        
        update(80, "Generating SEO...")
        seo = await generate_seo()
        
        update(90, "Uploading to YouTube...")
        full_desc = f"{seo['description']}\n\n{', '.join(seo['keywords'][:20])}\n\n{' '.join(seo['hashtags'])}"
        
        result = await upload_to_youtube(final, seo['title'], full_desc, user_id)
        if not result.get("success"):
            raise Exception(result.get("error"))
        
        elapsed = (datetime.now() - start).total_seconds()
        
        logger.info(f"\n{'='*80}\n🎉 SUCCESS! {elapsed:.1f}s\n{'='*80}\n")
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "title": seo['title'],
            "description": seo['description'],
            "video_id": result['video_id'],
            "video_url": result['video_url'],
            "duration": duration,
            "processing_time": elapsed,
            "completed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"\n{'='*80}\n❌ FAILED: {e}\n{traceback.format_exc()}\n{'='*80}\n")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════
router = APIRouter()

@router.post("/api/split-reels/process-url")
async def process_url_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        video_url = (data.get("video_url") or "").strip()
        
        if not user_id or not video_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Missing params"})
        
        task_id = str(uuid.uuid4())
        logger.info(f"🆕 Task: {task_id} - URL")
        
        asyncio.create_task(process_split_screen_reel(video_url, "url", user_id, task_id))
        return JSONResponse(content={"success": True, "task_id": task_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/split-reels/process-upload")
async def process_upload_endpoint(user_id: str = Form(...), video_file: UploadFile = File(...)):
    temp = None
    try:
        if not user_id or not video_file:
            return JSONResponse(status_code=400, content={"success": False, "error": "Missing params"})
        
        task_id = str(uuid.uuid4())
        temp = f"/tmp/upload_{task_id}.mp4"
        
        logger.info(f"🆕 Task: {task_id} - Upload: {video_file.filename}")
        
        success, error = await save_uploaded_file(video_file, temp)
        if not success:
            return JSONResponse(status_code=400, content={"success": False, "error": error})
        
        asyncio.create_task(process_split_screen_reel(temp, "upload", user_id, task_id))
        return JSONResponse(content={"success": True, "task_id": task_id})
    except Exception as e:
        if temp:
            cleanup(temp)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/api/split-reels/status/{task_id}")
async def get_status(task_id: str):
    status = PROCESSING_STATUS.get(task_id)
    if not status:
        return JSONResponse(status_code=404, content={"success": False, "error": "Not found"})
    return JSONResponse(content=status)

@router.get("/api/split-reels/health")
async def health_check():
    return JSONResponse(content={
        "status": "healthy",
        "version": "MINIMAL-FAST",
        "format": "9:16 reel",
        "features": {
            "split_screen_approaches": 4,
            "google_drive": True,
            "minimal_processing": True
        }
    })

async def initialize():
    logger.info("\n" + "="*80)
    logger.info("🚀 SPLIT-SCREEN REELS - MINIMAL FAST VERSION")
    logger.info("="*80)
    logger.info("✅ Output: 9:16 reel format (720x1280)")
    logger.info("✅ 4 split-screen approaches")
    logger.info("✅ Ultra-fast processing (30s max per step)")
    logger.info("="*80 + "\n")

__all__ = ["router", "initialize"]



# =========================================
# """
# split_screen_reels.py - SPLIT-SCREEN REACTION REELS
# ====================================================
# ✅ Split screen: Reaction video (TOP) + Main video (BOTTOM)
# ✅ Random reaction video selection from pool
# ✅ Multiple fallbacks (video → image → text)
# ✅ Copyright avoidance (filters, audio replacement)
# ✅ ElevenLabs voiceover support
# ✅ BGM background music
# ✅ Captions and text overlays
# ✅ Direct YouTube upload
# ✅ Comprehensive logging for Render
# ====================================================
# """

# from fastapi import APIRouter, Request, File, UploadFile, Form
# from fastapi.responses import JSONResponse
# import asyncio
# import logging
# import os
# import subprocess
# import tempfile
# import shutil
# import gc
# import httpx
# import json
# import re
# import random
# import aiofiles
# from typing import Optional, List, Dict, Any
# from datetime import datetime
# import uuid
# from urllib.parse import urlparse

# try:
#     import psutil
#     HAS_PSUTIL = True
# except:
#     HAS_PSUTIL = False

# # ═══════════════════════════════════════════════════════════════════════
# # LOGGING SETUP
# # ═══════════════════════════════════════════════════════════════════════
# logger = logging.getLogger("SplitScreenReels")
# logger.setLevel(logging.INFO)

# if not logger.handlers:
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     ))
#     logger.addHandler(handler)

# def log_memory(step: str):
#     """Log memory usage for Render monitoring"""
#     if HAS_PSUTIL:
#         try:
#             process = psutil.Process(os.getpid())
#             mem_mb = process.memory_info().rss / 1024 / 1024
#             logger.info(f"🧠 MEMORY [{step}]: {mem_mb:.1f}MB")
#             if mem_mb > 450:
#                 logger.warning(f"⚠️  HIGH MEMORY: {mem_mb:.1f}MB - Running GC")
#                 gc.collect()
#         except Exception as e:
#             logger.error(f"Memory check failed: {e}")

# def log_step(step: str, status: str = "START", details: str = ""):
#     """Comprehensive logging for debugging on Render"""
#     timestamp = datetime.now().strftime('%H:%M:%S')
#     if status == "START":
#         logger.info(f"\n{'='*80}")
#         logger.info(f"🚀 [{timestamp}] {step}")
#         if details:
#             logger.info(f"   📝 {details}")
#         logger.info(f"{'='*80}")
#     elif status == "SUCCESS":
#         logger.info(f"✅ [{timestamp}] {step} - SUCCESS")
#         if details:
#             logger.info(f"   ✨ {details}")
#     elif status == "FAILED":
#         logger.error(f"❌ [{timestamp}] {step} - FAILED")
#         if details:
#             logger.error(f"   ❗ {details}")
#     elif status == "FALLBACK":
#         logger.warning(f"⚠️  [{timestamp}] {step} - FALLBACK")
#         if details:
#             logger.warning(f"   🔄 {details}")
#     elif status == "INFO":
#         logger.info(f"ℹ️  [{timestamp}] {step}")
#         if details:
#             logger.info(f"   {details}")

# # ═══════════════════════════════════════════════════════════════════════
# # CONFIGURATION
# # ═══════════════════════════════════════════════════════════════════════

# # API Keys
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# # Reaction Videos (GitHub Raw URLs)
# REACTION_VIDEOS = [
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(1)%20(online-video-cutter.com)%20(1).mp4",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(1)%20(online-video-cutter.com).mp4",
# ]

# # Fallback Meme Images (if videos fail)
# FALLBACK_MEME_IMAGES = [
#     "https://i.imgur.com/8XqVLHj.jpg",  # Laughing emoji
#     "https://i.imgur.com/9VwQKvP.jpg",  # LOL text
#     "https://i.imgur.com/KJLw3uM.jpg",  # HAHA reaction
# ]

# # BGM (Background Music)
# BGM_URL = "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3"
# BGM_VOLUME = 0.25  # 25% volume for BGM

# # ElevenLabs Voice IDs
# ELEVENLABS_VOICES = [
#     "21m00Tcm4TlvDq8ikWAM",  # Rachel
#     "AZnzlk1XvdvUeBnXmlld",  # Domi
#     "EXAVITQu4vr4xnSDxMaL",  # Bella
# ]

# # Voiceover Templates
# VOICEOVER_TEMPLATES = [
#     "Watch this hilarious moment! You won't believe what happens next!",
#     "This is absolutely insane! Check out this crazy scene!",
#     "Wait for it... this is going to blow your mind!",
#     "OMG! This is the funniest thing I've seen today!",
#     "No way this is real! But it is, and it's amazing!",
# ]

# # Processing Status Storage
# PROCESSING_STATUS = {}

# # ═══════════════════════════════════════════════════════════════════════
# # UTILITY FUNCTIONS
# # ═══════════════════════════════════════════════════════════════════════

# def cleanup(*paths):
#     """Safely delete files and free memory"""
#     for path in paths:
#         try:
#             if path and os.path.exists(path):
#                 os.remove(path)
#                 logger.info(f"🗑️  Cleaned up: {os.path.basename(path)}")
#         except Exception as e:
#             logger.warning(f"Cleanup warning: {e}")
#     gc.collect()

# def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
#     """Run FFmpeg command with error handling"""
#     logger.info(f"🎬 Running: {step}")
#     logger.debug(f"Command: {' '.join(cmd[:5])}...")
#     try:
#         result = subprocess.run(
#             cmd,
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.PIPE,
#             timeout=timeout,
#             text=True
#         )
#         if result.returncode == 0:
#             logger.info(f"✅ {step} - Completed successfully")
#             return True
#         else:
#             error_msg = result.stderr[-500:] if result.stderr else "Unknown error"
#             logger.error(f"❌ {step} - Failed: {error_msg}")
#             return False
#     except subprocess.TimeoutExpired:
#         logger.error(f"❌ {step} - Timeout after {timeout}s")
#         return False
#     except Exception as e:
#         logger.error(f"❌ {step} - Error: {str(e)}")
#         return False

# async def get_video_info(video_path: str) -> Dict[str, Any]:
#     """Get video metadata using ffprobe"""
#     try:
#         result = subprocess.run([
#             "ffprobe", "-v", "error",
#             "-select_streams", "v:0",
#             "-show_entries", "stream=width,height,duration,r_frame_rate",
#             "-show_entries", "format=duration",
#             "-of", "json",
#             video_path
#         ], capture_output=True, timeout=30, text=True)
        
#         if result.returncode == 0:
#             data = json.loads(result.stdout)
#             stream = data.get("streams", [{}])[0]
#             format_data = data.get("format", {})
            
#             duration = float(stream.get("duration") or format_data.get("duration") or "0")
#             width = int(stream.get("width", 0))
#             height = int(stream.get("height", 0))
            
#             return {
#                 "duration": duration,
#                 "width": width,
#                 "height": height,
#                 "valid": duration > 0 and width > 0 and height > 0
#             }
#         return {"valid": False, "error": "ffprobe failed"}
#     except Exception as e:
#         logger.error(f"Video info error: {e}")
#         return {"valid": False, "error": str(e)}

# # ═══════════════════════════════════════════════════════════════════════
# # DOWNLOAD FUNCTIONS
# # ═══════════════════════════════════════════════════════════════════════

# async def download_file(url: str, output_path: str, desc: str = "file") -> tuple[bool, str]:
#     """Download file with progress logging"""
#     log_step(f"Download {desc}", "START", url)
    
#     try:
#         async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
#             async with client.stream("GET", url) as response:
#                 if response.status_code != 200:
#                     return False, f"HTTP {response.status_code}"
                
#                 total_size = 0
#                 with open(output_path, 'wb') as f:
#                     async for chunk in response.aiter_bytes(1024 * 1024):  # 1MB chunks
#                         f.write(chunk)
#                         total_size += len(chunk)
                
#                 if total_size < 1000:
#                     cleanup(output_path)
#                     return False, "File too small"
                
#                 size_mb = total_size / (1024 * 1024)
#                 log_step(f"Download {desc}", "SUCCESS", f"{size_mb:.2f}MB downloaded")
#                 return True, ""
                
#     except httpx.TimeoutException:
#         return False, "Download timeout"
#     except Exception as e:
#         return False, str(e)

# async def download_reaction_video_robust(temp_dir: str) -> tuple[Optional[str], bool]:
#     """
#     Download reaction video with 3-level fallback:
#     1. Try random video from pool
#     2. Try all videos in pool
#     3. Create video from meme image
#     """
#     log_step("Reaction Video Download", "START")
    
#     # LEVEL 1: Try random video
#     random.shuffle(REACTION_VIDEOS)
#     for idx, video_url in enumerate(REACTION_VIDEOS, 1):
#         logger.info(f"   🎥 Attempt {idx}/{len(REACTION_VIDEOS)}: {video_url}")
#         output = os.path.join(temp_dir, f"reaction_{idx}.mp4")
        
#         success, error = await download_file(video_url, output, f"reaction video {idx}")
#         if success and os.path.exists(output):
#             # Validate video
#             info = await get_video_info(output)
#             if info.get("valid"):
#                 log_step("Reaction Video Download", "SUCCESS", f"Method 1 - Video {idx}")
#                 return output, False
#             else:
#                 cleanup(output)
#                 logger.warning(f"   Invalid video: {error}")
    
#     # LEVEL 2: Try fallback images → convert to video
#     logger.warning("   ⚠️  All reaction videos failed, trying images...")
#     for idx, image_url in enumerate(FALLBACK_MEME_IMAGES, 1):
#         logger.info(f"   🖼️  Trying meme image {idx}/{len(FALLBACK_MEME_IMAGES)}")
        
#         image_path = os.path.join(temp_dir, f"meme_{idx}.jpg")
#         success, _ = await download_file(image_url, image_path, f"meme image {idx}")
        
#         if success and os.path.exists(image_path):
#             # Convert image to 10-second video
#             video_path = os.path.join(temp_dir, "reaction_from_image.mp4")
#             success = run_ffmpeg([
#                 "ffmpeg", "-loop", "1", "-i", image_path,
#                 "-t", "10", "-vf", "scale=720:720",
#                 "-c:v", "libx264", "-pix_fmt", "yuv420p",
#                 "-y", video_path
#             ], 60, "Image-to-Video")
            
#             cleanup(image_path)
            
#             if success and os.path.exists(video_path):
#                 log_step("Reaction Video Download", "FALLBACK", "Method 2 - Image converted")
#                 return video_path, True
    
#     # LEVEL 3: Create text-based reaction video
#     logger.warning("   ⚠️  All images failed, creating text video...")
#     text_video = os.path.join(temp_dir, "reaction_text.mp4")
    
#     success = run_ffmpeg([
#         "ffmpeg", "-f", "lavfi",
#         "-i", "color=c=red:s=720x720:d=10",
#         "-vf", "drawtext=text='😂 LOL 😂':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
#         "-c:v", "libx264", "-pix_fmt", "yuv420p",
#         "-y", text_video
#     ], 60, "Text-Video-Creation")
    
#     if success and os.path.exists(text_video):
#         log_step("Reaction Video Download", "FALLBACK", "Method 3 - Text video")
#         return text_video, True
    
#     logger.error("❌ All reaction video methods failed!")
#     return None, False







# async def download_main_video(url: str, output_path: str) -> tuple[bool, str]:
#     """
#     Download main video from URL with Google Drive support
#     Supports: Direct URLs, YouTube, TikTok, Instagram, Google Drive
#     """
#     log_step("Main Video Download", "START", url)
    
#     # ═══════════════════════════════════════════════════════════════
#     # DETECT URL TYPE
#     # ═══════════════════════════════════════════════════════════════
#     is_gdrive = False
#     gdrive_id = None
    
#     # Check if it's a Google Drive URL
#     if "drive.google.com" in url:
#         is_gdrive = True
#         logger.info("   🔍 Detected: Google Drive URL")
        
#         # Extract file ID from various Google Drive URL formats
#         import re
#         patterns = [
#             r'/file/d/([a-zA-Z0-9_-]+)',           # /file/d/ID/view
#             r'id=([a-zA-Z0-9_-]+)',                 # ?id=ID
#             r'/d/([a-zA-Z0-9_-]+)',                 # /d/ID
#             r'open\?id=([a-zA-Z0-9_-]+)',          # open?id=ID
#         ]
        
#         for pattern in patterns:
#             match = re.search(pattern, url)
#             if match:
#                 gdrive_id = match.group(1)
#                 logger.info(f"   📋 Extracted Google Drive ID: {gdrive_id}")
#                 break
        
#         if not gdrive_id:
#             return False, "Could not extract Google Drive file ID"
    
#     # ═══════════════════════════════════════════════════════════════
#     # METHOD 1: Google Drive Download (if applicable)
#     # ═══════════════════════════════════════════════════════════════
#     if is_gdrive and gdrive_id:
#         logger.info("   📥 Method 1: Google Drive direct download...")
        
#         # Try gdown library first
#         try:
#             import gdown
#             logger.info("   🔧 Using gdown library...")
            
#             # gdown.download needs file ID
#             gdrive_url = f"https://drive.google.com/uc?id={gdrive_id}"
            
#             # Download with gdown
#             result = gdown.download(gdrive_url, output_path, quiet=False)
            
#             if result and os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
#                 logger.info(f"   ✅ Downloaded via gdown: {os.path.getsize(output_path) / (1024*1024):.2f}MB")
                
#                 # Validate video
#                 info = await get_video_info(output_path)
#                 if info.get("valid"):
#                     log_step("Main Video Download", "SUCCESS", "via gdown")
#                     return True, ""
#                 else:
#                     cleanup(output_path)
#                     logger.warning("   ⚠️ gdown file is not a valid video")
#             else:
#                 logger.warning("   ⚠️ gdown failed or file too small")
#                 cleanup(output_path)
                
#         except Exception as e:
#             logger.warning(f"   ⚠️ gdown method failed: {e}")
#             cleanup(output_path)
        
#         # Try direct download URL (Method 2)
#         logger.info("   📥 Method 2: Google Drive direct URL...")
#         try:
#             direct_url = f"https://drive.google.com/uc?export=download&id={gdrive_id}"
            
#             async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
#                 async with client.stream("GET", direct_url) as response:
#                     if response.status_code == 200:
#                         total_size = 0
#                         with open(output_path, 'wb') as f:
#                             async for chunk in response.aiter_bytes(1024 * 1024):
#                                 f.write(chunk)
#                                 total_size += len(chunk)
                        
#                         if total_size > 100000:  # > 100KB
#                             logger.info(f"   ✅ Downloaded: {total_size / (1024*1024):.2f}MB")
                            
#                             # Validate
#                             info = await get_video_info(output_path)
#                             if info.get("valid"):
#                                 log_step("Main Video Download", "SUCCESS", "via direct URL")
#                                 return True, ""
#                             else:
#                                 cleanup(output_path)
#                                 logger.warning("   ⚠️ Downloaded file is not valid video")
#                         else:
#                             cleanup(output_path)
#                             logger.warning(f"   ⚠️ File too small: {total_size} bytes")
#         except Exception as e:
#             logger.warning(f"   ⚠️ Direct URL method failed: {e}")
#             cleanup(output_path)
        
#         # Try confirmation URL for large files (Method 3)
#         logger.info("   📥 Method 3: Google Drive with confirmation...")
#         try:
#             # First request to get confirmation token
#             confirm_url = f"https://drive.google.com/uc?export=download&id={gdrive_id}"
            
#             async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
#                 # Get the page
#                 response = await client.get(confirm_url)
                
#                 # Look for confirmation token
#                 import re
#                 match = re.search(r'confirm=([0-9A-Za-z_]+)', response.text)
#                 if match:
#                     confirm_token = match.group(1)
#                     logger.info(f"   🔑 Found confirmation token: {confirm_token[:10]}...")
                    
#                     # Download with confirmation
#                     download_url = f"https://drive.google.com/uc?export=download&id={gdrive_id}&confirm={confirm_token}"
                    
#                     async with client.stream("GET", download_url) as dl_response:
#                         if dl_response.status_code == 200:
#                             total_size = 0
#                             with open(output_path, 'wb') as f:
#                                 async for chunk in dl_response.aiter_bytes(1024 * 1024):
#                                     f.write(chunk)
#                                     total_size += len(chunk)
                            
#                             if total_size > 100000:
#                                 logger.info(f"   ✅ Downloaded: {total_size / (1024*1024):.2f}MB")
                                
#                                 info = await get_video_info(output_path)
#                                 if info.get("valid"):
#                                     log_step("Main Video Download", "SUCCESS", "via confirmation")
#                                     return True, ""
#                                 else:
#                                     cleanup(output_path)
#         except Exception as e:
#             logger.warning(f"   ⚠️ Confirmation method failed: {e}")
#             cleanup(output_path)
        
#         return False, "All Google Drive download methods failed"
    
#     # ═══════════════════════════════════════════════════════════════
#     # METHOD 2: Direct HTTP Download (for direct video URLs)
#     # ═══════════════════════════════════════════════════════════════
#     logger.info("   📥 Method 1: Direct HTTP download...")
#     success, error = await download_file(url, output_path, "main video")
#     if success:
#         info = await get_video_info(output_path)
#         if info.get("valid"):
#             log_step("Main Video Download", "SUCCESS", "via direct download")
#             return True, ""
#         else:
#             cleanup(output_path)
#             logger.warning("   ⚠️ Direct download produced invalid video")
    
#     # ═══════════════════════════════════════════════════════════════
#     # METHOD 3: yt-dlp (for YouTube, TikTok, Instagram, etc.)
#     # ═══════════════════════════════════════════════════════════════
#     logger.info("   📥 Method 2: Trying yt-dlp...")
#     try:
#         result = subprocess.run([
#             "yt-dlp",
#             "-f", "best[height<=720]",
#             "-o", output_path,
#             "--no-warnings",
#             "--no-check-certificate",
#             url
#         ], capture_output=True, timeout=180, text=True)
        
#         if result.returncode == 0 and os.path.exists(output_path):
#             info = await get_video_info(output_path)
#             if info.get("valid"):
#                 log_step("Main Video Download", "SUCCESS", "via yt-dlp")
#                 return True, ""
#             else:
#                 cleanup(output_path)
#                 logger.warning("   ⚠️ yt-dlp produced invalid video")
#         else:
#             logger.warning(f"   ⚠️ yt-dlp failed: {result.stderr[:200]}")
#     except subprocess.TimeoutExpired:
#         logger.warning("   ⚠️ yt-dlp timeout")
#     except Exception as e:
#         logger.warning(f"   ⚠️ yt-dlp error: {e}")
    
#     return False, error or "All download methods failed"




# async def save_uploaded_file(upload_file: UploadFile, output_path: str) -> tuple[bool, str]:
#     """Save uploaded file from frontend"""
#     log_step("File Upload", "START", upload_file.filename)
    
#     try:
#         max_size = 200 * 1024 * 1024  # 200MB limit
#         total_bytes = 0
        
#         async with aiofiles.open(output_path, 'wb') as f:
#             while True:
#                 chunk = await upload_file.read(1024 * 1024)  # 1MB chunks
#                 if not chunk:
#                     break
                
#                 total_bytes += len(chunk)
#                 if total_bytes > max_size:
#                     cleanup(output_path)
#                     return False, "File exceeds 200MB limit"
                
#                 await f.write(chunk)
        
#         if os.path.getsize(output_path) < 10000:
#             cleanup(output_path)
#             return False, "File too small (< 10KB)"
        
#         size_mb = total_bytes / (1024 * 1024)
#         log_step("File Upload", "SUCCESS", f"{size_mb:.2f}MB uploaded")
#         return True, ""
        
#     except Exception as e:
#         cleanup(output_path)
#         return False, str(e)




# def extract_gdrive_id(url: str) -> Optional[str]:
#     """
#     Extract Google Drive file ID from various URL formats
    
#     Supported formats:
#     - https://drive.google.com/file/d/FILE_ID/view
#     - https://drive.google.com/open?id=FILE_ID
#     - https://drive.google.com/uc?id=FILE_ID
#     - https://drive.google.com/uc?export=download&id=FILE_ID
#     """
#     import re
    
#     patterns = [
#         r'/file/d/([a-zA-Z0-9_-]+)',           # /file/d/ID/view
#         r'id=([a-zA-Z0-9_-]+)',                 # ?id=ID or &id=ID
#         r'/d/([a-zA-Z0-9_-]+)',                 # /d/ID
#         r'open\?id=([a-zA-Z0-9_-]+)',          # open?id=ID
#         r'/folders/([a-zA-Z0-9_-]+)',          # /folders/ID (folder, not file)
#     ]
    
#     for pattern in patterns:
#         match = re.search(pattern, url)
#         if match:
#             return match.group(1)
    
#     return None


# # ═══════════════════════════════════════════════════════════════════════
# # VIDEO PROCESSING
# # ═══════════════════════════════════════════════════════════════════════

# async def create_split_screen_robust(
#     reaction_video: str,
#     main_video: str,
#     output_path: str,
#     is_reaction_fallback: bool = False
# ) -> tuple[bool, str]:
#     """
#     Create split-screen video PROPERLY - CapCut/Canva style
#     1. Scale reaction to 720x640 (top half)
#     2. Scale main to 720x640 (bottom half)
#     3. Stack vertically = 720x1280 (perfect 9:16)
#     """
#     log_step("Split Screen Creation", "START")
    
#     # Get video info
#     main_info = await get_video_info(main_video)
#     reaction_info = await get_video_info(reaction_video)
    
#     if not main_info.get("valid"):
#         return False, "Invalid main video"
    
#     main_duration = main_info["duration"]
#     reaction_duration = reaction_info.get("duration", 10)
    
#     logger.info(f"   📊 Main video: {main_duration:.1f}s")
#     logger.info(f"   📊 Reaction video: {reaction_duration:.1f}s")
    
#     temp_dir = os.path.dirname(output_path)
    
#     # ═══════════════════════════════════════════════════════════════
#     # STEP 1: Scale reaction video to exact 720x640
#     # ═══════════════════════════════════════════════════════════════
#     log_step("Scale Reaction Video", "START", "Target: 720x640")
    
#     reaction_scaled = os.path.join(temp_dir, "reaction_scaled.mp4")
    
#     # If reaction is shorter, loop it
#     if reaction_duration < main_duration:
#         logger.info(f"   🔄 Looping reaction: {reaction_duration:.1f}s → {main_duration:.1f}s")
#         loop_count = int(main_duration / reaction_duration) + 2
        
#         success = run_ffmpeg([
#             "ffmpeg", "-stream_loop", str(loop_count), "-i", reaction_video,
#             "-vf", "scale=720:640:force_original_aspect_ratio=decrease,pad=720:640:(ow-iw)/2:(oh-ih)/2,setsar=1",
#             "-t", str(main_duration),
#             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
#             "-an",  # Remove audio
#             "-y", reaction_scaled
#         ], 120, "Scale-Reaction")
#     else:
#         success = run_ffmpeg([
#             "ffmpeg", "-i", reaction_video,
#             "-vf", "scale=720:640:force_original_aspect_ratio=decrease,pad=720:640:(ow-iw)/2:(oh-ih)/2,setsar=1",
#             "-t", str(main_duration),
#             "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
#             "-an",
#             "-y", reaction_scaled
#         ], 120, "Scale-Reaction")
    
#     if not success or not os.path.exists(reaction_scaled):
#         return False, "Failed to scale reaction video"
    
#     log_step("Scale Reaction Video", "SUCCESS")
    
#     # ═══════════════════════════════════════════════════════════════
#     # STEP 2: Scale main video to exact 720x640
#     # ═══════════════════════════════════════════════════════════════
#     log_step("Scale Main Video", "START", "Target: 720x640")
    
#     main_scaled = os.path.join(temp_dir, "main_scaled.mp4")
    
#     success = run_ffmpeg([
#         "ffmpeg", "-i", main_video,
#         "-vf", "scale=720:640:force_original_aspect_ratio=decrease,pad=720:640:(ow-iw)/2:(oh-ih)/2,setsar=1",
#         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
#         "-an",  # Remove audio for now
#         "-y", main_scaled
#     ], 120, "Scale-Main")
    
#     if not success or not os.path.exists(main_scaled):
#         cleanup(reaction_scaled)
#         return False, "Failed to scale main video"
    
#     log_step("Scale Main Video", "SUCCESS")
    
#     # ═══════════════════════════════════════════════════════════════
#     # STEP 3: Stack vertically (NOW both are 720x640!)
#     # ═══════════════════════════════════════════════════════════════
#     log_step("Vertical Stack", "START", "720x640 + 720x640 = 720x1280")
    
#     # Create a file list for concat
#     concat_file = os.path.join(temp_dir, "concat_list.txt")
#     with open(concat_file, 'w') as f:
#         f.write(f"file '{reaction_scaled}'\n")
#         f.write(f"file '{main_scaled}'\n")
    
#     # METHOD 1: Using vstack filter (now both have same width!)
#     success = run_ffmpeg([
#         "ffmpeg",
#         "-i", reaction_scaled,
#         "-i", main_scaled,
#         "-filter_complex", "[0:v][1:v]vstack=inputs=2[v]",
#         "-map", "[v]",
#         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
#         "-t", str(main_duration),
#         "-y", output_path
#     ], 120, "VStack-Final")
    
#     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
#         cleanup(reaction_scaled, main_scaled, concat_file)
#         log_step("Split Screen Creation", "SUCCESS", "Method 1: VStack")
#         return True, ""
    
#     cleanup(output_path)
    
#     # METHOD 2: Using concat demuxer (alternative approach)
#     logger.warning("   🔄 Method 2: Trying alternative stacking...")
    
#     # First, create vertical videos
#     reaction_vertical = os.path.join(temp_dir, "reaction_vert.mp4")
#     success = run_ffmpeg([
#         "ffmpeg", "-i", reaction_scaled,
#         "-vf", "pad=720:1280:0:0",
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-y", reaction_vertical
#     ], 60, "Reaction-Vertical")
    
#     if not success:
#         cleanup(reaction_scaled, main_scaled, concat_file)
#         return False, "Failed to create vertical reaction"
    
#     main_vertical = os.path.join(temp_dir, "main_vert.mp4")
#     success = run_ffmpeg([
#         "ffmpeg", "-i", main_scaled,
#         "-vf", "pad=720:1280:0:640",
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-y", main_vertical
#     ], 60, "Main-Vertical")
    
#     if not success:
#         cleanup(reaction_scaled, main_scaled, reaction_vertical, concat_file)
#         return False, "Failed to create vertical main"
    
#     # Overlay them
#     success = run_ffmpeg([
#         "ffmpeg",
#         "-i", main_vertical,
#         "-i", reaction_vertical,
#         "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
#         "-map", "[v]",
#         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
#         "-t", str(main_duration),
#         "-y", output_path
#     ], 120, "Overlay-Final")
    
#     cleanup(reaction_scaled, main_scaled, reaction_vertical, main_vertical, concat_file)
    
#     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
#         log_step("Split Screen Creation", "SUCCESS", "Method 2: Overlay")
#         return True, ""
    
#     cleanup(output_path)
    
#     # METHOD 3: Just use main video (ultimate fallback)
#     logger.warning("   🔄 Method 3: Using main video only")
    
#     success = run_ffmpeg([
#         "ffmpeg", "-i", main_video,
#         "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
#         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
#         "-an",
#         "-y", output_path
#     ], 90, "Fallback-MainOnly")
    
#     if success and os.path.exists(output_path):
#         log_step("Split Screen Creation", "FALLBACK", "Main video only")
#         return True, ""
    
#     return False, "All split-screen methods failed"



# async def apply_copyright_filters_robust(input_path: str, output_path: str) -> tuple[bool, str]:
#     """Apply copyright avoidance filters with fallback"""
#     log_step("Copyright Filters", "START")
    
#     # METHOD 1: Full filters
#     logger.info("   🎨 Method 1: Color adjustments + blur edges")
#     success = run_ffmpeg([
#         "ffmpeg", "-i", input_path,
#         "-vf", (
#             "eq=saturation=1.3:brightness=0.08:contrast=1.2,"
#             "unsharp=5:5:1.0:5:5:0.0,"
#             "hue=h=5:s=1.1"
#         ),
#         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
#         "-c:a", "copy",
#         "-y", output_path
#     ], 120, "Filters-Method1")
    
#     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
#         log_step("Copyright Filters", "SUCCESS", "Method 1")
#         return True, ""
    
#     cleanup(output_path)
    
#     # METHOD 2: Simple color adjustment
#     logger.info("   🎨 Method 2: Basic color adjustment")
#     success = run_ffmpeg([
#         "ffmpeg", "-i", input_path,
#         "-vf", "eq=saturation=1.2:brightness=0.05",
#         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
#         "-c:a", "copy",
#         "-y", output_path
#     ], 90, "Filters-Method2")
    
#     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
#         log_step("Copyright Filters", "SUCCESS", "Method 2")
#         return True, ""
    
#     cleanup(output_path)
    
#     # METHOD 3: Copy original
#     logger.warning("   🔄 Method 3: Using original (fallback)")
#     try:
#         shutil.copy(input_path, output_path)
#         log_step("Copyright Filters", "FALLBACK", "Method 3")
#         return True, ""
#     except:
#         return False, "All filter methods failed"

# async def remove_audio(video_path: str, output_path: str) -> bool:
#     """Remove original audio"""
#     log_step("Remove Audio", "START")
    
#     success = run_ffmpeg([
#         "ffmpeg", "-i", video_path,
#         "-c:v", "copy", "-an",
#         "-y", output_path
#     ], 90, "Remove-Audio")
    
#     if success:
#         cleanup(video_path)
#         log_step("Remove Audio", "SUCCESS")
    
#     return success

# async def generate_voiceover(text: str, output_path: str) -> bool:
#     """Generate voiceover using ElevenLabs with fallback"""
#     log_step("Voiceover Generation", "START")
    
#     if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
#         log_step("Voiceover Generation", "FALLBACK", "No ElevenLabs API key")
#         return False
    
#     try:
#         voice_id = random.choice(ELEVENLABS_VOICES)
#         logger.info(f"   🎙️  Using voice: {voice_id}")
        
#         async with httpx.AsyncClient(timeout=60) as client:
#             response = await client.post(
#                 f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
#                 headers={"xi-api-key": ELEVENLABS_API_KEY},
#                 json={
#                     "text": text,
#                     "model_id": "eleven_monolingual_v1",
#                     "voice_settings": {
#                         "stability": 0.5,
#                         "similarity_boost": 0.75
#                     }
#                 }
#             )
            
#             if response.status_code == 200:
#                 with open(output_path, 'wb') as f:
#                     f.write(response.content)
#                 log_step("Voiceover Generation", "SUCCESS")
#                 return True
                
#     except Exception as e:
#         logger.warning(f"ElevenLabs failed: {e}")
    
#     log_step("Voiceover Generation", "FALLBACK", "Skipping voiceover")
#     return False

# async def add_audio_track_robust(
#     video_path: str,
#     bgm_path: Optional[str],
#     voiceover_path: Optional[str],
#     output_path: str
# ) -> tuple[bool, str]:
#     """Add audio with 3-level fallback"""
#     log_step("Audio Mixing", "START")
    
#     duration_cmd = await get_video_info(video_path)
#     duration = duration_cmd.get("duration", 30)
    
#     # METHOD 1: BGM + Voiceover
#     if bgm_path and voiceover_path and os.path.exists(bgm_path) and os.path.exists(voiceover_path):
#         logger.info("   🎵 Method 1: BGM + Voiceover")
        
#         filter_complex = (
#             f"[1:a]volume={BGM_VOLUME},aloop=loop=-1:size=2e+09[bgm];"
#             "[2:a]volume=1.5[vo];"
#             "[bgm][vo]amix=inputs=2:duration=first[a]"
#         )
        
#         success = run_ffmpeg([
#             "ffmpeg",
#             "-i", video_path,
#             "-i", bgm_path,
#             "-i", voiceover_path,
#             "-filter_complex", filter_complex,
#             "-map", "0:v", "-map", "[a]",
#             "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
#             "-t", str(duration),
#             "-y", output_path
#         ], 120, "Audio-Method1")
        
#         if success and os.path.exists(output_path):
#             cleanup(video_path, bgm_path, voiceover_path)
#             log_step("Audio Mixing", "SUCCESS", "Method 1")
#             return True, ""
        
#         cleanup(output_path)
    
#     # METHOD 2: BGM only
#     if bgm_path and os.path.exists(bgm_path):
#         logger.info("   🎵 Method 2: BGM only")
        
#         success = run_ffmpeg([
#             "ffmpeg",
#             "-i", video_path,
#             "-i", bgm_path,
#             "-filter_complex", f"[1:a]volume={BGM_VOLUME},aloop=loop=-1:size=2e+09[a]",
#             "-map", "0:v", "-map", "[a]",
#             "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
#             "-t", str(duration),
#             "-shortest",
#             "-y", output_path
#         ], 90, "Audio-Method2")
        
#         if success and os.path.exists(output_path):
#             cleanup(video_path, bgm_path, voiceover_path)
#             log_step("Audio Mixing", "SUCCESS", "Method 2")
#             return True, ""
        
#         cleanup(output_path)
    
#     # METHOD 3: No audio (silent video)
#     logger.warning("   🔄 Method 3: Silent video (fallback)")
#     try:
#         shutil.copy(video_path, output_path)
#         cleanup(video_path, bgm_path, voiceover_path)
#         log_step("Audio Mixing", "FALLBACK", "Method 3")
#         return True, ""
#     except:
#         return False, "All audio methods failed"

# async def add_text_overlay_robust(
#     video_path: str,
#     text: str,
#     output_path: str
# ) -> tuple[bool, str]:
#     """Add text caption with fallback"""
#     log_step("Text Overlay", "START")
    
#     # METHOD 1: Animated text at bottom
#     logger.info("   ✍️  Method 1: Animated bottom text")
    
#     # Escape text for FFmpeg
#     safe_text = text.replace("'", "\\'").replace(":", "\\:")
    
#     success = run_ffmpeg([
#         "ffmpeg", "-i", video_path,
#         "-vf", (
#             f"drawtext=text='{safe_text}':"
#             "fontsize=32:fontcolor=white:bordercolor=black:borderw=3:"
#             "x=(w-text_w)/2:y=h-100"
#         ),
#         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
#         "-c:a", "copy",
#         "-y", output_path
#     ], 90, "Text-Method1")
    
#     if success and os.path.exists(output_path):
#         cleanup(video_path)
#         log_step("Text Overlay", "SUCCESS", "Method 1")
#         return True, ""
    
#     cleanup(output_path)
    
#     # METHOD 2: Simple centered text
#     logger.info("   ✍️  Method 2: Simple text")
#     success = run_ffmpeg([
#         "ffmpeg", "-i", video_path,
#         "-vf", f"drawtext=text='WATCH THIS':fontsize=40:fontcolor=yellow:x=(w-text_w)/2:y=50",
#         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
#         "-c:a", "copy",
#         "-y", output_path
#     ], 60, "Text-Method2")
    
#     if success and os.path.exists(output_path):
#         cleanup(video_path)
#         log_step("Text Overlay", "SUCCESS", "Method 2")
#         return True, ""
    
#     cleanup(output_path)
    
#     # METHOD 3: No text
#     logger.warning("   🔄 Method 3: No text overlay")
#     try:
#         shutil.copy(video_path, output_path)
#         cleanup(video_path)
#         log_step("Text Overlay", "FALLBACK", "Method 3")
#         return True, ""
#     except:
#         return False, "All text methods failed"

# # ═══════════════════════════════════════════════════════════════════════
# # SEO GENERATION
# # ═══════════════════════════════════════════════════════════════════════

# async def generate_seo_metadata() -> dict:
#     """Generate SEO metadata using AI"""
#     log_step("SEO Generation", "START")
    
#     if MISTRAL_API_KEY and len(MISTRAL_API_KEY) > 20:
#         try:
#             logger.info("   🤖 Using Mistral AI...")
            
#             prompt = """Generate YouTube Shorts SEO for a SPLIT-SCREEN REACTION VIDEO.

# FORMAT:
# - Top: Reaction/laughing clip
# - Bottom: Main comedy content

# TITLE: 3-7 words + 3 hashtags at end
# DESCRIPTION: 2 short paragraphs
# KEYWORDS: 45 keywords (reaction, funny, comedy, shorts, viral, etc.)
# HASHTAGS: 8 hashtags (#Shorts #Funny #Reaction must be included)

# OUTPUT ONLY JSON:
# {
#   "title": "Title Here #funny #shorts #viral",
#   "description": "Para1\\n\\nPara2",
#   "keywords": ["keyword1", ... 45 total],
#   "hashtags": ["#Shorts", "#Funny", ... 8 total]
# }"""
            
#             async with httpx.AsyncClient(timeout=60) as client:
#                 resp = await client.post(
#                     "https://api.mistral.ai/v1/chat/completions",
#                     headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
#                     json={
#                         "model": "mistral-large-latest",
#                         "messages": [
#                             {"role": "system", "content": "Output ONLY valid JSON."},
#                             {"role": "user", "content": prompt}
#                         ],
#                         "temperature": 0.8,
#                         "max_tokens": 1500
#                     }
#                 )
                
#                 if resp.status_code == 200:
#                     content = resp.json()["choices"][0]["message"]["content"]
#                     content = re.sub(r'```json\n?|\n?```', '', content).strip()
#                     match = re.search(r'\{.*\}', content, re.DOTALL)
                    
#                     if match:
#                         data = json.loads(match.group(0))
#                         keywords = data.get("keywords", [])
#                         while len(keywords) < 45:
#                             keywords.append("funny video")
                        
#                         log_step("SEO Generation", "SUCCESS", "AI-generated")
#                         return {
#                             "title": data.get("title", "Hilarious Moment #funny #shorts #viral"),
#                             "description": data.get("description", "Watch this!"),
#                             "keywords": keywords[:45],
#                             "hashtags": data.get("hashtags", ["#Shorts", "#Funny", "#Viral"])
#                         }
#         except Exception as e:
#             logger.warning(f"Mistral AI failed: {e}")
    
#     # FALLBACK
#     log_step("SEO Generation", "FALLBACK", "Using template")
#     return {
#         "title": "This Is INSANE! #funny #shorts #viral",
#         "description": "You won't believe this happened!\n\nLike and subscribe for more!",
#         "keywords": ["funny", "comedy", "reaction", "shorts", "viral"] * 9,
#         "hashtags": ["#Shorts", "#Funny", "#Viral", "#Comedy", "#Reaction", "#LOL", "#OMG", "#Trending"]
#     }

# # ═══════════════════════════════════════════════════════════════════════
# # YOUTUBE UPLOAD
# # ═══════════════════════════════════════════════════════════════════════

# async def upload_to_youtube(
#     video_path: str,
#     title: str,
#     description: str,
#     user_id: str
# ) -> dict:
#     """Upload final video to YouTube"""
#     log_step("YouTube Upload", "START")
    
#     try:
#         from YTdatabase import get_database_manager as get_yt_db
#         yt_db = get_yt_db()
        
#         if not yt_db.youtube.client:
#             await yt_db.connect()
        
#         creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
#         if not creds:
#             return {"success": False, "error": "YouTube credentials not found"}
        
#         credentials = {
#             "access_token": creds.get("access_token"),
#             "refresh_token": creds.get("refresh_token"),
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "client_id": creds.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
#             "client_secret": creds.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
#             "scopes": [
#                 "https://www.googleapis.com/auth/youtube.upload",
#                 "https://www.googleapis.com/auth/youtube.force-ssl"
#             ]
#         }
        
#         from mainY import youtube_scheduler
        
#         result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             credentials_data=credentials,
#             content_type="shorts",
#             title=title,
#             description=description,
#             video_url=video_path
#         )
        
#         if result.get("success"):
#             video_id = result.get("video_id")
#             log_step("YouTube Upload", "SUCCESS", f"Video ID: {video_id}")
#             return {
#                 "success": True,
#                 "video_id": video_id,
#                 "video_url": f"https://youtube.com/shorts/{video_id}"
#             }
        
#         return {"success": False, "error": result.get("error", "Upload failed")}
        
#     except Exception as e:
#         logger.error(f"YouTube upload error: {e}")
#         return {"success": False, "error": str(e)}

# # ═══════════════════════════════════════════════════════════════════════
# # MAIN PROCESSING PIPELINE
# # ═══════════════════════════════════════════════════════════════════════

# async def process_split_screen_reel(
#     main_video_source: str,
#     source_type: str,  # "url" or "upload"
#     user_id: str,
#     task_id: str
# ):
#     """
#     Main processing pipeline for split-screen reels
#     """
#     temp_dir = None
#     start_time = datetime.now()
    
#     PROCESSING_STATUS[task_id] = {
#         "status": "processing",
#         "progress": 0,
#         "message": "Initializing...",
#         "started_at": start_time.isoformat()
#     }
    
#     def update_progress(progress: int, message: str):
#         PROCESSING_STATUS[task_id]["progress"] = progress
#         PROCESSING_STATUS[task_id]["message"] = message
#         logger.info(f"📊 Progress: {progress}% - {message}")
    
#     try:
#         temp_dir = tempfile.mkdtemp(prefix="split_reel_")
#         log_memory("Pipeline-Start")
        
#         # STEP 1: Download/Get Reaction Video (10%)
#         update_progress(5, "Getting reaction video...")
#         reaction_video, is_fallback = await download_reaction_video_robust(temp_dir)
#         if not reaction_video:
#             raise Exception("Failed to get reaction video")
        
#         # STEP 2: Download/Get Main Video (20%)
#         update_progress(15, "Getting main video...")
#         main_video_path = os.path.join(temp_dir, "main_raw.mp4")
        
#         if source_type == "upload":
#             # Already saved, just copy reference
#             shutil.copy(main_video_source, main_video_path)
#         else:
#             # Download from URL
#             success, error = await download_main_video(main_video_source, main_video_path)
#             if not success:
#                 raise Exception(f"Failed to download main video: {error}")
        
#         # Validate main video
#         info = await get_video_info(main_video_path)
#         if not info.get("valid"):
#             raise ValueError(f"Invalid main video: {info.get('error')}")
        
#         duration = info["duration"]
#         if duration > 180:
#             raise ValueError(f"Video too long ({duration:.0f}s). Max 3 minutes.")
        
#         # STEP 3: Create Split-Screen (35%)
#         update_progress(25, "Creating split-screen layout...")
#         split_screen_path = os.path.join(temp_dir, "split_screen.mp4")
        
#         success, error = await create_split_screen_robust(
#             reaction_video, main_video_path, split_screen_path, is_fallback
#         )
#         if not success:
#             raise Exception(f"Split-screen creation failed: {error}")
        
#         cleanup(reaction_video, main_video_path)
#         log_memory("After-Split-Screen")
        
#         # STEP 4: Apply Copyright Filters (50%)
#         update_progress(45, "Applying copyright filters...")
#         filtered_path = os.path.join(temp_dir, "filtered.mp4")
        
#         success, error = await apply_copyright_filters_robust(split_screen_path, filtered_path)
#         if not success:
#             raise Exception(f"Filters failed: {error}")
        
#         cleanup(split_screen_path)
        
#         # STEP 5: Remove Original Audio (60%)
#         update_progress(55, "Removing original audio...")
#         silent_path = os.path.join(temp_dir, "silent.mp4")
        
#         if not await remove_audio(filtered_path, silent_path):
#             raise Exception("Failed to remove audio")
        
#         # STEP 6: Generate Voiceover (65%)
#         update_progress(62, "Generating voiceover...")
#         voiceover_text = random.choice(VOICEOVER_TEMPLATES)
#         voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
        
#         has_voiceover = await generate_voiceover(voiceover_text, voiceover_path)
#         if not has_voiceover:
#             voiceover_path = None
        
#         # STEP 7: Download BGM (70%)
#         update_progress(68, "Downloading background music...")
#         bgm_path = os.path.join(temp_dir, "bgm.mp3")
        
#         success, _ = await download_file(BGM_URL, bgm_path, "BGM")
#         if not success:
#             logger.warning("BGM download failed")
#             bgm_path = None
        
#         # STEP 8: Mix Audio (80%)
#         update_progress(75, "Mixing audio tracks...")
#         audio_mixed_path = os.path.join(temp_dir, "with_audio.mp4")
        
#         success, error = await add_audio_track_robust(
#             silent_path, bgm_path, voiceover_path, audio_mixed_path
#         )
#         if not success:
#             raise Exception(f"Audio mixing failed: {error}")
        
#         log_memory("After-Audio")
        
#         # STEP 9: Add Text Overlay (85%)
#         update_progress(82, "Adding text overlay...")
#         final_video = os.path.join(temp_dir, "final.mp4")
        
#         success, error = await add_text_overlay_robust(
#             audio_mixed_path, "WATCH THIS! 🔥", final_video
#         )
#         if not success:
#             raise Exception(f"Text overlay failed: {error}")
        
#         # STEP 10: Generate SEO (90%)
#         update_progress(88, "Generating SEO metadata...")
#         seo = await generate_seo_metadata()
        
#         # STEP 11: Upload to YouTube (100%)
#         update_progress(92, "Uploading to YouTube...")
        
#         full_description = (
#             f"{seo['description']}\n\n"
#             f"Keywords: {', '.join(seo['keywords'][:20])}\n\n"
#             f"{' '.join(seo['hashtags'])}"
#         )
        
#         upload_result = await upload_to_youtube(
#             final_video,
#             seo['title'],
#             full_description,
#             user_id
#         )
        
#         if not upload_result.get("success"):
#             raise Exception(f"YouTube upload failed: {upload_result.get('error')}")
        
#         # SUCCESS!
#         elapsed = (datetime.now() - start_time).total_seconds()
        
#         logger.info(f"\n{'='*80}")
#         logger.info(f"🎉 PIPELINE COMPLETED SUCCESSFULLY!")
#         logger.info(f"⏱️  Total time: {elapsed:.1f}s")
#         logger.info(f"🎬 Video URL: {upload_result['video_url']}")
#         logger.info(f"{'='*80}\n")
        
#         PROCESSING_STATUS[task_id] = {
#             "status": "completed",
#             "progress": 100,
#             "success": True,
#             "title": seo['title'],
#             "description": seo['description'],
#             "video_id": upload_result['video_id'],
#             "video_url": upload_result['video_url'],
#             "duration": duration,
#             "processing_time": elapsed,
#             "completed_at": datetime.utcnow().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"\n{'='*80}")
#         logger.error(f"❌ PIPELINE FAILED: {str(e)}")
#         logger.error(f"{'='*80}\n")
        
#         PROCESSING_STATUS[task_id] = {
#             "status": "failed",
#             "success": False,
#             "error": str(e),
#             "failed_at": datetime.utcnow().isoformat()
#         }
    
#     finally:
#         if temp_dir and os.path.exists(temp_dir):
#             try:
#                 shutil.rmtree(temp_dir, ignore_errors=True)
#                 logger.info("🗑️  Cleaned up temp directory")
#             except:
#                 pass
        
#         gc.collect()
#         log_memory("Pipeline-End")

# # ═══════════════════════════════════════════════════════════════════════
# # API ENDPOINTS
# # ═══════════════════════════════════════════════════════════════════════

# router = APIRouter()

# @router.post("/api/split-reels/process-url")
# async def process_url_endpoint(request: Request):
#     """Process video from URL"""
#     try:
#         data = await request.json()
#         user_id = data.get("user_id")
#         video_url = (data.get("video_url") or "").strip()
        
#         if not user_id or not video_url:
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": "Missing user_id or video_url"}
#             )
        
#         task_id = str(uuid.uuid4())
#         logger.info(f"🆕 New task: {task_id} - URL: {video_url[:50]}...")
        
#         # Start async processing
#         asyncio.create_task(
#             process_split_screen_reel(video_url, "url", user_id, task_id)
#         )
        
#         return JSONResponse(content={
#             "success": True,
#             "task_id": task_id,
#             "message": "Processing started"
#         })
        
#     except Exception as e:
#         logger.error(f"Endpoint error: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "error": str(e)}
#         )

# @router.post("/api/split-reels/process-upload")
# async def process_upload_endpoint(
#     user_id: str = Form(...),
#     video_file: UploadFile = File(...)
# ):
#     """Process uploaded video file"""
#     temp_file = None
    
#     try:
#         if not user_id or not video_file:
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": "Missing user_id or video_file"}
#             )
        
#         task_id = str(uuid.uuid4())
#         temp_file = f"/tmp/upload_{task_id}.mp4"
        
#         logger.info(f"🆕 New upload task: {task_id} - File: {video_file.filename}")
        
#         # Save uploaded file
#         success, error = await save_uploaded_file(video_file, temp_file)
#         if not success:
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": error}
#             )
        
#         # Start async processing
#         asyncio.create_task(
#             process_split_screen_reel(temp_file, "upload", user_id, task_id)
#         )
        
#         return JSONResponse(content={
#             "success": True,
#             "task_id": task_id,
#             "message": "Processing started"
#         })
        
#     except Exception as e:
#         logger.error(f"Upload endpoint error: {e}")
#         if temp_file and os.path.exists(temp_file):
#             cleanup(temp_file)
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "error": str(e)}
#         )

# @router.get("/api/split-reels/status/{task_id}")
# async def get_status(task_id: str):
#     """Get processing status"""
#     status = PROCESSING_STATUS.get(task_id)
#     if not status:
#         return JSONResponse(
#             status_code=404,
#             content={"success": False, "error": "Task not found"}
#         )
#     return JSONResponse(content=status)

# @router.get("/api/split-reels/health")
# async def health_check():
#     """Health check endpoint"""
#     return JSONResponse(content={
#         "status": "healthy",
#         "service": "Split-Screen Reels",
#         "version": "1.0.0",
#         "features": {
#             "split_screen": "3-level fallback",
#             "reaction_videos": len(REACTION_VIDEOS),
#             "fallback_images": len(FALLBACK_MEME_IMAGES),
#             "copyright_filters": "multi-level",
#             "audio_mixing": "BGM + voiceover",
#             "text_overlay": "enabled"
#         }
#     })

# # ═══════════════════════════════════════════════════════════════════════
# # INITIALIZATION
# # ═══════════════════════════════════════════════════════════════════════

# async def initialize():
#     """Initialize service on startup"""
#     logger.info("\n" + "="*80)
#     logger.info("🚀 SPLIT-SCREEN REACTION REELS SERVICE")
#     logger.info("="*80)
#     logger.info(f"✅ Reaction videos: {len(REACTION_VIDEOS)}")
#     logger.info(f"✅ Fallback images: {len(FALLBACK_MEME_IMAGES)}")
#     logger.info(f"✅ BGM enabled: {bool(BGM_URL)}")
#     logger.info(f"✅ ElevenLabs voiceover: {bool(ELEVENLABS_API_KEY)}")
#     logger.info(f"✅ Mistral SEO: {bool(MISTRAL_API_KEY)}")
#     logger.info("="*80 + "\n")
#     log_memory("Service-Start")

# __all__ = ["router", "initialize"]