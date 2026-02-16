"""
split_screen_reels.py - PRODUCTION SPLIT-SCREEN REELS v2.0
============================================================
✅ Google Drive + Manual Upload support
✅ Smart video resizing (any aspect ratio → 720x640)
✅ Intelligent zoom/crop for cinematic effect
✅ Extended timeouts for large files
✅ Advanced Mistral SEO generation
✅ Comprehensive error handling
✅ Production-ready logging
============================================================
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
from typing import Optional, List, Dict, Any
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
logger = logging.getLogger("SplitScreenReels")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)

def log_memory(step: str):
    """Log memory usage"""
    if HAS_PSUTIL:
        try:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
            if mem_mb > 450:
                logger.warning(f"⚠️  HIGH MEMORY: {mem_mb:.1f}MB")
                gc.collect()
        except:
            pass

def log_step(step: str, status: str = "START", details: str = ""):
    """Structured logging"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    if status == "START":
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 [{timestamp}] {step}")
        if details:
            logger.info(f"   {details}")
        logger.info(f"{'='*80}")
    elif status == "SUCCESS":
        logger.info(f"✅ [{timestamp}] {step} - SUCCESS")
        if details:
            logger.info(f"   {details}")
    elif status == "FAILED":
        logger.error(f"❌ [{timestamp}] {step} - FAILED")
        if details:
            logger.error(f"   {details}")
    elif status == "FALLBACK":
        logger.warning(f"⚠️  [{timestamp}] {step} - FALLBACK")
        if details:
            logger.warning(f"   {details}")

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
    "https://i.imgur.com/KJLw3uM.jpg",
]

BGM_URL = "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3"
BGM_VOLUME = 0.25

ELEVENLABS_VOICES = ["21m00Tcm4TlvDq8ikWAM", "AZnzlk1XvdvUeBnXmlld", "EXAVITQu4vr4xnSDxMaL"]
VOICEOVER_TEMPLATES = [
    "Watch this hilarious moment! You won't believe what happens next!",
    "This is absolutely insane! Check out this crazy scene!",
    "Wait for it... this is going to blow your mind!",
]

PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════
def cleanup(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.info(f"🗑️  Cleaned: {os.path.basename(path)}")
        except:
            pass
    gc.collect()

def run_ffmpeg(cmd: list, timeout: int = 240, step: str = "FFmpeg") -> bool:
    """Run FFmpeg with extended timeout"""
    logger.info(f"🎬 {step} (max {timeout}s)")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )
        if result.returncode == 0:
            logger.info(f"✅ {step} completed")
            return True
        else:
            logger.error(f"❌ {step} failed: {result.stderr[-300:]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {step} timeout ({timeout}s)")
        return False
    except Exception as e:
        logger.error(f"❌ {step} error: {e}")
        return False

async def get_video_info(video_path: str) -> Dict[str, Any]:
    """Get video metadata"""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-show_entries", "format=duration",
            "-of", "json",
            video_path
        ], capture_output=True, timeout=30, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            stream = data.get("streams", [{}])[0]
            format_data = data.get("format", {})
            
            duration = float(stream.get("duration") or format_data.get("duration") or "0")
            width = int(stream.get("width", 0))
            height = int(stream.get("height", 0))
            
            return {
                "duration": duration,
                "width": width,
                "height": height,
                "valid": duration > 0 and width > 0 and height > 0
            }
        return {"valid": False, "error": "ffprobe failed"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════
async def download_file(url: str, output_path: str, desc: str = "file") -> tuple[bool, str]:
    """Download with progress"""
    log_step(f"Download {desc}", "START", url[:80])
    
    try:
        async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    return False, f"HTTP {response.status_code}"
                
                total = 0
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(1024 * 1024):
                        f.write(chunk)
                        total += len(chunk)
                
                if total < 1000:
                    cleanup(output_path)
                    return False, "File too small"
                
                log_step(f"Download {desc}", "SUCCESS", f"{total/(1024*1024):.2f}MB")
                return True, ""
    except Exception as e:
        return False, str(e)

async def download_reaction_video_robust(temp_dir: str) -> tuple[Optional[str], bool]:
    """Download reaction with fallbacks"""
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
        image_path = os.path.join(temp_dir, f"meme_{idx}.jpg")
        success, _ = await download_file(img_url, image_path, f"image {idx}")
        
        if success:
            video_path = os.path.join(temp_dir, "reaction_img.mp4")
            success = run_ffmpeg([
                "ffmpeg", "-loop", "1", "-i", image_path,
                "-t", "10", "-vf", "scale=720:720",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-y", video_path
            ], 60, "Image-to-Video")
            
            cleanup(image_path)
            if success:
                log_step("Reaction Video", "FALLBACK", "Image converted")
                return video_path, True
    
    return None, False

async def download_from_gdrive(file_id: str, output_path: str) -> tuple[bool, str]:
    """Google Drive download"""
    logger.info(f"   📥 Google Drive: {file_id}")
    
    # Try gdown
    try:
        import gdown
        url = f"https://drive.google.com/uc?id={file_id}"
        result = gdown.download(url, output_path, quiet=False)
        
        if result and os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            info = await get_video_info(output_path)
            if info.get("valid"):
                return True, ""
            cleanup(output_path)
    except Exception as e:
        logger.warning(f"   gdown failed: {e}")
    
    # Try direct URL
    try:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    total = 0
                    with open(output_path, 'wb') as f:
                        async for chunk in response.aiter_bytes(1024 * 1024):
                            f.write(chunk)
                            total += len(chunk)
                    
                    if total > 100000:
                        info = await get_video_info(output_path)
                        if info.get("valid"):
                            return True, ""
                    cleanup(output_path)
    except Exception as e:
        logger.warning(f"   Direct URL failed: {e}")
    
    return False, "All Google Drive methods failed"

async def download_main_video(url: str, output_path: str) -> tuple[bool, str]:
    """Download main video with all methods"""
    log_step("Main Video Download", "START")
    
    # Check for Google Drive
    if "drive.google.com" in url:
        patterns = [r'/file/d/([a-zA-Z0-9_-]+)', r'id=([a-zA-Z0-9_-]+)']
        gdrive_id = None
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                gdrive_id = match.group(1)
                break
        
        if gdrive_id:
            success, error = await download_from_gdrive(gdrive_id, output_path)
            if success:
                log_step("Main Video Download", "SUCCESS", "Google Drive")
                return True, ""
    
    # Try direct download
    success, _ = await download_file(url, output_path, "main video")
    if success:
        info = await get_video_info(output_path)
        if info.get("valid"):
            log_step("Main Video Download", "SUCCESS", "Direct")
            return True, ""
        cleanup(output_path)
    
    # Try yt-dlp
    try:
        result = subprocess.run([
            "yt-dlp", "-f", "best[height<=720]",
            "-o", output_path, "--no-warnings", url
        ], capture_output=True, timeout=180, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            info = await get_video_info(output_path)
            if info.get("valid"):
                log_step("Main Video Download", "SUCCESS", "yt-dlp")
                return True, ""
    except:
        pass
    
    return False, "All download methods failed"

async def save_uploaded_file(upload_file: UploadFile, output_path: str) -> tuple[bool, str]:
    """Save upload"""
    log_step("File Upload", "START", upload_file.filename)
    
    try:
        total = 0
        max_size = 200 * 1024 * 1024
        
        async with aiofiles.open(output_path, 'wb') as f:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_size:
                    cleanup(output_path)
                    return False, "File > 200MB"
                await f.write(chunk)
        
        if os.path.getsize(output_path) < 10000:
            cleanup(output_path)
            return False, "File too small"
        
        log_step("File Upload", "SUCCESS", f"{total/(1024*1024):.2f}MB")
        return True, ""
    except Exception as e:
        cleanup(output_path)
        return False, str(e)

# ═══════════════════════════════════════════════════════════════════════
# SMART VIDEO SCALING WITH ZOOM/CROP
# ═══════════════════════════════════════════════════════════════════════
async def scale_video_smart(
    input_path: str,
    output_path: str,
    target_w: int,
    target_h: int,
    apply_zoom: bool = True,
    description: str = "video"
) -> tuple[bool, str]:
    """
    Smart scaling with intelligent zoom/crop
    - Detects video aspect ratio
    - Applies cinematic crop (removes 2cm top/bottom equivalent)
    - Scales to exact dimensions
    """
    log_step(f"Scale {description}", "START", f"{target_w}x{target_h}")
    
    # Get input info
    info = await get_video_info(input_path)
    if not info.get("valid"):
        return False, "Invalid input video"
    
    in_w, in_h = info["width"], info["height"]
    logger.info(f"   📊 Input: {in_w}x{in_h}")
    
    # Calculate aspect ratios
    in_aspect = in_w / in_h
    target_aspect = target_w / target_h
    
    # Build filter chain
    filters = []
    
    # STEP 1: Apply cinematic crop if requested (zoom effect)
    if apply_zoom:
        # Crop 5% from top and bottom (cinematic effect)
        crop_h = int(in_h * 0.90)  # Keep 90% height
        crop_y = int(in_h * 0.05)   # Start 5% down
        
        filters.append(f"crop={in_w}:{crop_h}:0:{crop_y}")
        logger.info(f"   🔍 Applying zoom: crop to {in_w}x{crop_h}")
    
    # STEP 2: Scale to fit target, maintaining aspect ratio
    filters.append(f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease")
    
    # STEP 3: Pad to exact dimensions
    filters.append(f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2")
    
    # STEP 4: Set pixel format
    filters.append("format=yuv420p")
    filters.append("setsar=1")
    
    filter_string = ",".join(filters)
    
    # METHOD 1: Fast preset with filters
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", filter_string,
        "-c:v", "libx264",
        "-preset", "veryfast",  # Faster than ultrafast but better quality
        "-crf", "26",           # Slightly lower quality for speed
        "-pix_fmt", "yuv420p",
        "-an",
        "-y", output_path
    ]
    
    success = run_ffmpeg(cmd, 240, f"Scale-{description}-Fast")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        # Verify dimensions
        verify = await get_video_info(output_path)
        if verify.get("width") == target_w and verify.get("height") == target_h:
            log_step(f"Scale {description}", "SUCCESS", f"{target_w}x{target_h}")
            return True, ""
        else:
            logger.warning(f"   Wrong dimensions: {verify.get('width')}x{verify.get('height')}")
            cleanup(output_path)
    
    # METHOD 2: Ultra-fast preset (lower quality, faster)
    logger.warning(f"   🔄 Trying faster preset...")
    
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-an",
        "-y", output_path
    ]
    
    success = run_ffmpeg(cmd, 180, f"Scale-{description}-Ultra")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        log_step(f"Scale {description}", "SUCCESS", "Fast method")
        return True, ""
    
    cleanup(output_path)
    return False, f"Failed to scale {description}"

async def create_split_screen_v2(
    reaction_video: str,
    main_video: str,
    output_path: str
) -> tuple[bool, str]:
    """
    Create split-screen with smart scaling
    """
    log_step("Split-Screen Creation", "START")
    
    # Get durations
    main_info = await get_video_info(main_video)
    reaction_info = await get_video_info(reaction_video)
    
    if not main_info.get("valid"):
        return False, "Invalid main video"
    
    main_dur = main_info["duration"]
    reaction_dur = reaction_info.get("duration", 10)
    
    logger.info(f"   Main: {main_dur:.1f}s, Reaction: {reaction_dur:.1f}s")
    
    temp_dir = os.path.dirname(output_path)
    
    # Scale reaction (with loop if needed)
    reaction_scaled = os.path.join(temp_dir, "reaction_scaled.mp4")
    
    if reaction_dur < main_dur:
        logger.info(f"   🔄 Looping reaction")
        loop_count = int(main_dur / reaction_dur) + 2
        reaction_looped = os.path.join(temp_dir, "reaction_loop.mp4")
        
        success = run_ffmpeg([
            "ffmpeg", "-stream_loop", str(loop_count), "-i", reaction_video,
            "-t", str(main_dur),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
            "-an", "-y", reaction_looped
        ], 180, "Loop-Reaction")
        
        if not success:
            return False, "Failed to loop reaction"
        
        # Scale looped video
        success, error = await scale_video_smart(
            reaction_looped, reaction_scaled, 720, 640, False, "reaction"
        )
        cleanup(reaction_looped)
    else:
        # Just scale (no zoom for reaction)
        success, error = await scale_video_smart(
            reaction_video, reaction_scaled, 720, 640, False, "reaction"
        )
    
    if not success:
        return False, f"Reaction scaling failed: {error}"
    
    # Scale main video (WITH ZOOM for cinematic effect)
    main_scaled = os.path.join(temp_dir, "main_scaled.mp4")
    
    success, error = await scale_video_smart(
        main_video, main_scaled, 720, 640, True, "main"  # apply_zoom=True
    )
    
    if not success:
        cleanup(reaction_scaled)
        return False, f"Main scaling failed: {error}"
    
    # Stack vertically
    log_step("Vertical Stack", "START")
    
    success = run_ffmpeg([
        "ffmpeg",
        "-i", reaction_scaled,
        "-i", main_scaled,
        "-filter_complex", "[0:v][1:v]vstack=inputs=2[v]",
        "-map", "[v]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-t", str(main_dur),
        "-y", output_path
    ], 180, "VStack")
    
    cleanup(reaction_scaled, main_scaled)
    
    if success and os.path.exists(output_path):
        log_step("Split-Screen Creation", "SUCCESS")
        return True, ""
    
    return False, "Stacking failed"

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED SEO GENERATION
# ═══════════════════════════════════════════════════════════════════════
async def generate_advanced_seo() -> dict:
    """Generate SEO with Mistral AI"""
    log_step("SEO Generation", "START")
    
    if MISTRAL_API_KEY and len(MISTRAL_API_KEY) > 20:
        try:
            logger.info("   🤖 Using Mistral AI...")
            
            prompt = """You are a VIRAL YouTube Shorts SEO expert for SPLIT-SCREEN REACTION VIDEOS.

VIDEO FORMAT:
- Top half: Funny reaction/laughing clip
- Bottom half: Main comedy/viral content
- Audio: Background music + optional voiceover
- Duration: 30-180 seconds
- Platform: YouTube Shorts
- Goal: Maximum views, engagement, virality

AUDIENCE: Global (US, India, UK, International)

TITLE REQUIREMENTS:
- 5-8 words maximum
- MUST be attention-grabbing and curiosity-inducing
- Include 3-4 hashtags at END (space-separated)
- NO emojis in title
- Use power words: "Insane", "Hilarious", "Epic", "Crazy", "Unbelievable"
- Examples:
  * "This Guy Did The Impossible #funny #viral #shorts"
  * "Wait For The Ending #comedy #reaction #trending"
  * "She Had No Idea What Happened #shocking #shorts #fyp"

DESCRIPTION:
- 2 concise paragraphs (3-4 sentences each)
- First paragraph: Hook the viewer, describe what happens
- Second paragraph: Call-to-action (like, subscribe, comment)
- Natural, conversational tone
- NO excessive emojis

KEYWORDS:
- EXACTLY 45 keywords
- Mix of:
  * Broad: "funny video", "comedy", "viral", "trending"
  * Specific: "reaction video", "split screen", "hilarious moment"
  * Platform: "youtube shorts", "short video", "shorts feed"
  * Engagement: "must watch", "viral video", "trending now"

HASHTAGS:
- 10 hashtags total
- MUST include: #Shorts, #Viral, #Trending
- Mix of popular and niche tags
- Format: #Foryou #Fyp #Explore #Reach #Shorts #Viral #Trending #Comedy #Funny #Reaction

OUTPUT ONLY VALID JSON (no markdown, no code blocks):
{
  "title": "Title Here #tag1 #tag2 #tag3",
  "description": "First paragraph here.\\n\\nSecond paragraph here.",
  "keywords": ["keyword1", "keyword2", ... exactly 45 keywords],
  "hashtags": ["#Shorts", "#Viral", ... exactly 10 hashtags]
}"""
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "You are a YouTube SEO expert. Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.9,
                        "max_tokens": 2000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    # Clean response
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if match:
                        data = json.loads(match.group(0))
                        
                        # Ensure 45 keywords
                        keywords = data.get("keywords", [])
                        while len(keywords) < 45:
                            keywords.extend(["funny video", "viral", "comedy", "trending"])
                        keywords = keywords[:45]
                        
                        # Ensure 10 hashtags
                        hashtags = data.get("hashtags", [])
                        while len(hashtags) < 10:
                            hashtags.extend(["#Shorts", "#Viral", "#Trending"])
                        hashtags = list(dict.fromkeys(hashtags))[:10]  # Remove duplicates
                        
                        log_step("SEO Generation", "SUCCESS", f"Title: {data.get('title')}")
                        return {
                            "title": data.get("title", "Epic Reaction Moment #funny #shorts #viral"),
                            "description": data.get("description", "Watch this!"),
                            "keywords": keywords,
                            "hashtags": hashtags,
                            "ai_generated": True
                        }
        except Exception as e:
            logger.warning(f"   Mistral failed: {e}")
    
    # FALLBACK
    log_step("SEO Generation", "FALLBACK", "Using template")
    return {
        "title": "This Is Crazy #funny #viral #shorts",
        "description": "You have to see this!\n\nLike and subscribe for more!",
        "keywords": ["funny", "viral", "comedy", "shorts"] * 11 + ["trending"],
        "hashtags": ["#Shorts", "#Viral", "#Trending", "#Funny", "#Comedy", "#Reaction", "#LOL", "#OMG", "#Fyp", "#Foryou"],
        "ai_generated": False
    }

# ═══════════════════════════════════════════════════════════════════════
# REMAINING FUNCTIONS (Audio, Text, Upload) - KEEP FROM ORIGINAL
# ═══════════════════════════════════════════════════════════════════════
async def apply_copyright_filters(input_path: str, output_path: str) -> tuple[bool, str]:
    """Apply filters"""
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", "eq=saturation=1.25:brightness=0.08:contrast=1.15",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "copy", "-y", output_path
    ]
    
    if run_ffmpeg(cmd, 120, "Filters"):
        return True, ""
    
    try:
        shutil.copy(input_path, output_path)
        return True, ""
    except:
        return False, "Filter failed"

async def remove_audio(video_in: str, video_out: str) -> bool:
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an", "-y", video_out
    ], 90, "Remove-Audio")
    if success:
        cleanup(video_in)
    return success

async def generate_voiceover(text: str, output: str) -> bool:
    if not ELEVENLABS_API_KEY:
        return False
    
    try:
        voice = random.choice(ELEVENLABS_VOICES)
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
                headers={"xi-api-key": ELEVENLABS_API_KEY},
                json={"text": text, "model_id": "eleven_monolingual_v1"}
            )
            if resp.status_code == 200:
                with open(output, 'wb') as f:
                    f.write(resp.content)
                return True
    except:
        pass
    return False

async def add_audio_track(video: str, bgm: Optional[str], vo: Optional[str], output: str) -> tuple[bool, str]:
    info = await get_video_info(video)
    dur = info.get("duration", 30)
    
    if bgm and os.path.exists(bgm):
        cmd = [
            "ffmpeg", "-i", video, "-i", bgm,
            "-filter_complex", f"[1:a]volume={BGM_VOLUME},aloop=loop=-1:size=2e+09[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-t", str(dur), "-shortest", "-y", output
        ]
        
        if run_ffmpeg(cmd, 90, "Audio-Mix"):
            cleanup(video, bgm, vo)
            return True, ""
    
    try:
        shutil.copy(video, output)
        cleanup(video, bgm, vo)
        return True, ""
    except:
        return False, "Audio failed"

async def add_text_overlay(video: str, text: str, output: str) -> tuple[bool, str]:
    safe = text.replace("'", "\\'").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-i", video,
        "-vf", f"drawtext=text='{safe}':fontsize=32:fontcolor=white:bordercolor=black:borderw=3:x=(w-text_w)/2:y=h-100",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "copy", "-y", output
    ]
    
    if run_ffmpeg(cmd, 90, "Text"):
        cleanup(video)
        return True, ""
    
    try:
        shutil.copy(video, output)
        cleanup(video)
        return True, ""
    except:
        return False, "Text failed"

async def upload_to_youtube(video: str, title: str, desc: str, user_id: str) -> dict:
    try:
        from YTdatabase import get_database_manager
        yt_db = get_database_manager()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        if not creds:
            return {"success": False, "error": "No credentials"}
        
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
            return {
                "success": True,
                "video_id": result["video_id"],
                "video_url": f"https://youtube.com/shorts/{result['video_id']}"
            }
        return {"success": False, "error": result.get("error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
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
        log_memory("START")
        
        update(5, "Getting reaction...")
        reaction, _ = await download_reaction_video_robust(temp_dir)
        if not reaction:
            raise Exception("Reaction failed")
        
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
            raise ValueError("Invalid video")
        
        duration = info["duration"]
        if duration > 180:
            raise ValueError(f"Video too long ({duration:.0f}s)")
        
        update(25, "Creating split-screen...")
        split = os.path.join(temp_dir, "split.mp4")
        success, err = await create_split_screen_v2(reaction, main, split)
        if not success:
            raise Exception(f"Split failed: {err}")
        
        cleanup(reaction, main)
        log_memory("SPLIT-DONE")
        
        update(45, "Applying filters...")
        filtered = os.path.join(temp_dir, "filtered.mp4")
        success, err = await apply_copyright_filters(split, filtered)
        if not success:
            raise Exception(err)
        cleanup(split)
        
        update(55, "Removing audio...")
        silent = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered, silent):
            raise Exception("Remove audio failed")
        
        update(65, "Generating voiceover...")
        vo = os.path.join(temp_dir, "vo.mp3")
        await generate_voiceover(random.choice(VOICEOVER_TEMPLATES), vo)
        
        update(70, "Downloading BGM...")
        bgm = os.path.join(temp_dir, "bgm.mp3")
        await download_file(BGM_URL, bgm, "BGM")
        
        update(75, "Mixing audio...")
        audio_mixed = os.path.join(temp_dir, "with_audio.mp4")
        success, err = await add_audio_track(silent, bgm, vo, audio_mixed)
        if not success:
            raise Exception(err)
        
        update(82, "Adding text...")
        final = os.path.join(temp_dir, "final.mp4")
        success, err = await add_text_overlay(audio_mixed, "WATCH THIS! 🔥", final)
        if not success:
            raise Exception(err)
        
        update(88, "Generating SEO...")
        seo = await generate_advanced_seo()
        
        update(92, "Uploading to YouTube...")
        full_desc = f"{seo['description']}\n\n{', '.join(seo['keywords'][:20])}\n\n{' '.join(seo['hashtags'])}"
        
        result = await upload_to_youtube(final, seo['title'], full_desc, user_id)
        if not result.get("success"):
            raise Exception(result.get("error"))
        
        elapsed = (datetime.now() - start).total_seconds()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🎉 SUCCESS! {elapsed:.1f}s")
        logger.info(f"{'='*80}\n")
        
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
        logger.error(f"\n{'='*80}")
        logger.error(f"❌ FAILED: {e}")
        logger.error(f"{'='*80}\n")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "success": False,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        log_memory("END")

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
        "version": "2.0",
        "features": {
            "smart_scaling": "enabled",
            "zoom_crop": "enabled",
            "google_drive": "enabled",
            "mistral_seo": bool(MISTRAL_API_KEY)
        }
    })

async def initialize():
    logger.info("\n" + "="*80)
    logger.info("🚀 SPLIT-SCREEN REELS v2.0")
    logger.info("="*80)
    logger.info(f"✅ Smart scaling with zoom")
    logger.info(f"✅ Google Drive support")
    logger.info(f"✅ Advanced SEO: {bool(MISTRAL_API_KEY)}")
    logger.info("="*80 + "\n")

__all__ = ["router", "initialize"]