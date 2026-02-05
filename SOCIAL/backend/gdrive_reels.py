"""
gdrive_reels_optimized.py - PRODUCTION READY WITH FALLBACKS
============================================================
✅ Multiple Google Drive download methods (3 fallbacks)
✅ Groq Whisper API for transcription
✅ Detailed error messages for frontend
✅ Handles all URL formats (including ?usp=drive_link)
✅ Memory optimized for Render free tier
============================================================
"""

from fastapi import APIRouter, Request, BackgroundTasks
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
from typing import Optional, Dict
from datetime import datetime
import uuid

# ═══════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
GROQ_API_KEY = os.getenv("GROQ_SPEECH_API")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
]

# Processing status tracking
PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# MEMORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

def aggressive_cleanup(*paths):
    """Delete files and force garbage collection"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.debug(f"   🗑️  Deleted: {os.path.basename(path)}")
        except Exception as e:
            logger.debug(f"   ⚠️  Failed to delete {path}: {e}")
    
    gc.collect()


# ═══════════════════════════════════════════════════════════════════════
# FFMPEG HELPERS
# ═══════════════════════════════════════════════════════════════════════

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg command with timeout"""
    logger.info(f"🎬 {step}...")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {step} - SUCCESS")
            return True
        else:
            logger.error(f"❌ {step} - FAILED (exit {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {step} - TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        logger.error(f"❌ {step} - ERROR: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════
# GOOGLE DRIVE FILE ID EXTRACTION (MULTIPLE PATTERNS)
# ═══════════════════════════════════════════════════════════════════════

def extract_gdrive_file_id(url: str) -> Optional[str]:
    """
    Extract Google Drive file ID from any URL format
    
    Supports:
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    - https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
    - https://drive.google.com/open?id=FILE_ID
    - https://drive.google.com/uc?id=FILE_ID
    """
    if not url or "drive.google.com" not in url:
        return None
    
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]{25,})',  # Most common
        r'[?&]id=([a-zA-Z0-9_-]{25,})',   # ?id= format
        r'/open\?id=([a-zA-Z0-9_-]{25,})', # /open?id= format
        r'/d/([a-zA-Z0-9_-]{25,})/',      # Alternative
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            logger.info(f"   Extracted file ID: {file_id}")
            return file_id
    
    logger.error(f"   Could not extract file ID from: {url}")
    return None


# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD VIDEO - MULTIPLE FALLBACK METHODS
# ═══════════════════════════════════════════════════════════════════════

async def download_method_1_direct(file_id: str, output_path: str) -> bool:
    """Method 1: Direct download via uc endpoint"""
    logger.info("   Method 1: Direct download (uc endpoint)")
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                        size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        logger.info(f"   ✅ Downloaded: {size_mb:.1f} MB")
                        return True
        
        return False
    except Exception as e:
        logger.error(f"   ❌ Method 1 failed: {e}")
        return False


async def download_method_2_confirm(file_id: str, output_path: str) -> bool:
    """Method 2: Handle virus scan confirmation"""
    logger.info("   Method 2: Download with virus scan bypass")
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            # First request to get confirmation token
            url1 = f"https://drive.google.com/uc?export=download&id={file_id}"
            response1 = await client.get(url1)
            
            # Look for confirmation token
            confirm_token = None
            if "download_warning" in response1.text:
                match = re.search(r'confirm=([0-9A-Za-z_-]+)', response1.text)
                if match:
                    confirm_token = match.group(1)
            
            # Download with confirmation
            url2 = f"https://drive.google.com/uc?export=download&id={file_id}"
            if confirm_token:
                url2 += f"&confirm={confirm_token}"
            
            async with client.stream("GET", url2) as response:
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                        size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        logger.info(f"   ✅ Downloaded: {size_mb:.1f} MB")
                        return True
        
        return False
    except Exception as e:
        logger.error(f"   ❌ Method 2 failed: {e}")
        return False


async def download_method_3_usercontent(file_id: str, output_path: str) -> bool:
    """Method 3: Direct usercontent domain"""
    logger.info("   Method 3: Usercontent domain download")
    
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                        size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        logger.info(f"   ✅ Downloaded: {size_mb:.1f} MB")
                        return True
        
        return False
    except Exception as e:
        logger.error(f"   ❌ Method 3 failed: {e}")
        return False


async def download_video_from_gdrive(file_id: str, output_path: str) -> tuple[bool, str]:
    """
    Download video from Google Drive with 3 fallback methods
    
    Returns: (success: bool, error_message: str)
    """
    logger.info("⬇️  Downloading video from Google Drive...")
    logger.info(f"   File ID: {file_id}")
    
    # Try all 3 methods
    methods = [
        ("Direct download", download_method_1_direct),
        ("With confirmation", download_method_2_confirm),
        ("Usercontent domain", download_method_3_usercontent),
    ]
    
    for idx, (name, method) in enumerate(methods, 1):
        logger.info(f"📥 Trying download method {idx}/3: {name}")
        
        try:
            success = await method(file_id, output_path)
            if success:
                logger.info(f"✅ Download successful using method {idx}")
                return True, ""
        except Exception as e:
            logger.error(f"   Method {idx} exception: {e}")
        
        if idx < len(methods):
            await asyncio.sleep(1)
    
    error_msg = "Failed to download video. Please check: 1) Link is public ('Anyone with the link can view'), 2) File size is under 100MB, 3) File is a valid video"
    logger.error(f"❌ All download methods failed")
    return False, error_msg


# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def get_video_duration(video_path: str) -> float:
    """Get video duration using ffprobe"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ],
            capture_output=True,
            timeout=15,
            text=True
        )
        
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"⏱️  Duration: {duration:.1f}s")
            return duration
        
        return 0.0
    except Exception as e:
        logger.error(f"❌ Failed to get duration: {e}")
        return 0.0


async def extract_audio_from_video(video_path: str, audio_path: str) -> bool:
    """Extract audio to 16kHz mono WAV for Whisper"""
    return run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-y", audio_path
    ], timeout=60, step="Extract Audio")


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION - GROQ WHISPER API
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_audio(audio_path: str) -> tuple[Optional[str], str]:
    """
    Transcribe audio using Groq Whisper API
    
    Returns: (transcript: str, error_message: str)
    """
    logger.info("📝 TRANSCRIBING AUDIO (GROQ WHISPER API)")
    
    if not GROQ_API_KEY:
        error_msg = "GROQ_SPEECH_API key not configured on server"
        logger.error(f"❌ {error_msg}")
        return None, error_msg
    
    try:
        from groq import Groq
        
        client = Groq(api_key=GROQ_API_KEY)
        
        logger.info("   Using: Groq Whisper Large v3")
        
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="text",
                language="hi"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"✅ Transcription SUCCESS: {len(transcription)} chars")
            logger.info(f"   Preview: {transcription[:100]}...")
            return transcription.strip(), ""
        else:
            error_msg = "Transcription returned empty text - video may not have Hindi audio"
            logger.error(f"❌ {error_msg}")
            return None, error_msg
        
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return None, error_msg


# ═══════════════════════════════════════════════════════════════════════
# AI SCRIPT GENERATION
# ═══════════════════════════════════════════════════════════════════════

async def generate_ai_script(transcript: str, duration: float) -> dict:
    """Generate viral reel script using AI (with fallback)"""
    logger.info("🤖 Generating AI script...")
    
    target_words = int(duration * 2.5)
    
    # Try Claude first
    if ANTHROPIC_API_KEY:
        try:
            prompt = f"""Rewrite this Hindi transcript into a viral {target_words}-word script for YouTube Shorts.

TRANSCRIPT: {transcript}

Create:
1. Catchy Hinglish title (under 70 chars)
2. Viral script (exactly {target_words} words in Hindi)
3. SEO description (under 200 chars)

Return JSON:
{{"script": "...", "title": "...", "description": "..."}}"""

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": ANTHROPIC_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                
                if response.status_code == 200:
                    content = response.json()["content"][0]["text"]
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        logger.info("✅ Claude AI script generated")
                        return {
                            "script": data.get("script", transcript)[:2000],
                            "title": data.get("title", "Amazing Story 🔥")[:100],
                            "description": data.get("description", transcript[:200])[:500]
                        }
        except Exception as e:
            logger.warning(f"   Claude failed: {e}")
    
    # Try Mistral
    if MISTRAL_API_KEY:
        try:
            prompt = f"""Rewrite in Hindi ({target_words} words): {transcript}
JSON: {{"script":"","title":"","description":""}}"""

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-small-latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 800
                    }
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        logger.info("✅ Mistral AI script generated")
                        return {
                            "script": data.get("script", transcript)[:2000],
                            "title": data.get("title", "Amazing Story 🔥")[:100],
                            "description": data.get("description", transcript[:200])[:500]
                        }
        except Exception as e:
            logger.warning(f"   Mistral failed: {e}")
    
    # Fallback
    logger.info("   Using fallback (simple trim)")
    words = transcript.split()[:target_words]
    script = " ".join(words)
    
    return {
        "script": script,
        "title": f"{' '.join(words[:5])}... 🔥",
        "description": " ".join(words[:30])
    }


# ═══════════════════════════════════════════════════════════════════════
# VOICEOVER
# ═══════════════════════════════════════════════════════════════════════

async def generate_voiceover(script: str, output_path: str) -> tuple[bool, str]:
    """
    Generate Hindi voiceover using Edge TTS
    
    Returns: (success: bool, error_message: str)
    """
    logger.info("🎙️  Generating voiceover with Edge TTS...")
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        logger.info(f"   Voice: {voice}")
        
        communicate = edge_tts.Communicate(
            script[:2000],
            voice,
            rate="+5%"
        )
        
        await communicate.save(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            logger.info(f"✅ Voiceover generated: {os.path.getsize(output_path)/1024:.1f} KB")
            return True, ""
        else:
            error_msg = "Voiceover file too small or missing"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Voiceover generation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg


# ═══════════════════════════════════════════════════════════════════════
# CAPTIONS
# ═══════════════════════════════════════════════════════════════════════

def generate_srt_captions(script: str, duration: float) -> str:
    """Generate SRT captions"""
    words = script.split()
    
    phrases = []
    for i in range(0, len(words), 4):
        phrase = " ".join(words[i:i+4])
        if phrase:
            phrases.append(phrase)
    
    if not phrases:
        return ""
    
    time_per_phrase = duration / len(phrases)
    
    srt_blocks = []
    for i, phrase in enumerate(phrases):
        start_time = i * time_per_phrase
        end_time = start_time + time_per_phrase
        
        start_h = int(start_time // 3600)
        start_m = int((start_time % 3600) // 60)
        start_s = start_time % 60
        
        end_h = int(end_time // 3600)
        end_m = int((end_time % 3600) // 60)
        end_s = end_time % 60
        
        srt_blocks.append(
            f"{i+1}\n"
            f"{start_h:02d}:{start_m:02d}:{start_s:06.3f}".replace(".", ",") + " --> " +
            f"{end_h:02d}:{end_m:02d}:{end_s:06.3f}".replace(".", ",") + "\n"
            f"{phrase}\n"
        )
    
    return "\n".join(srt_blocks)


# ═══════════════════════════════════════════════════════════════════════
# VIDEO COMPOSITING
# ═══════════════════════════════════════════════════════════════════════

async def remove_original_audio(video_in: str, video_out: str) -> bool:
    """Remove original audio from video"""
    return run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy",
        "-an",
        "-y", video_out
    ], timeout=60, step="Remove Original Audio")


async def download_bgm(output_path: str) -> bool:
    """Download background music"""
    logger.info("🎵 Downloading BGM...")
    
    try:
        url = random.choice(BGM_URLS)
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    if os.path.exists(output_path):
                        logger.info("✅ BGM downloaded")
                        return True
        
        return False
    except Exception as e:
        logger.error(f"❌ BGM download failed: {e}")
        return False


async def create_final_video(silent_video: str, voiceover: str, srt_file: str,
                             bgm: Optional[str], output: str) -> tuple[bool, str]:
    """
    Create final video with captions, voiceover, and BGM
    
    Returns: (success: bool, error_message: str)
    """
    logger.info("✨ Creating final video...")
    
    captioned_video = output.replace(".mp4", "_captioned.mp4")
    srt_escaped = srt_file.replace("\\", "\\\\").replace(":", "\\:")
    
    if not run_ffmpeg([
        "ffmpeg", "-i", silent_video,
        "-vf", f"subtitles={srt_escaped}:force_style='FontName=Arial Black,FontSize=28,PrimaryColour=&H00FFFF00,Bold=1,Outline=2,Shadow=1,Alignment=2,MarginV=60'",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-y", captioned_video
    ], timeout=180, step="Burn Captions"):
        return False, "Failed to burn captions into video"
    
    aggressive_cleanup(silent_video)
    
    if bgm and os.path.exists(bgm):
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned_video,
            "-i", voiceover,
            "-i", bgm,
            "-filter_complex", "[1:a]volume=1.0[voice];[2:a]volume=0.06[music];[voice][music]amix=inputs=2:duration=first[audio]",
            "-map", "0:v",
            "-map", "[audio]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "96k",
            "-shortest",
            "-y", output
        ], timeout=120, step="Mix Audio (Voice + BGM)")
    else:
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned_video,
            "-i", voiceover,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "96k",
            "-shortest",
            "-y", output
        ], timeout=90, step="Add Voiceover")
    
    aggressive_cleanup(captioned_video)
    
    if not success:
        return False, "Failed to mix audio and create final video"
    
    return True, ""


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload video to YouTube"""
    logger.info("📤 Uploading to YouTube...")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds:
            return {"success": False, "error": "YouTube credentials not found. Please connect your YouTube account first."}
        
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
            description=f"{description}\n\n#Shorts #Viral #Hindi #Reels",
            video_url=video_path
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            logger.info(f"✅ Uploaded to YouTube: {video_id}")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        else:
            return {"success": False, "error": result.get("error", "YouTube upload failed")}
            
    except Exception as e:
        logger.error(f"❌ YouTube upload failed: {e}")
        return {"success": False, "error": f"YouTube upload error: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════════
# MAIN PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_gdrive_reel(drive_url: str, user_id: str, task_id: str):
    """Main processing pipeline with detailed error handling"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "success": False,
        "message": "Starting...",
        "started_at": start_time.isoformat()
    }
    
    def update_status(progress: int, message: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = message
        logger.info(f"[{progress}%] {message}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="gdrive_reel_")
        logger.info(f"📁 Temp dir: {temp_dir}")
        
        # Step 1: Extract file ID
        update_status(5, "Extracting file ID...")
        file_id = extract_gdrive_file_id(drive_url)
        if not file_id:
            raise ValueError("Invalid Google Drive URL. Please check the link format.")
        
        # Step 2: Download video
        update_status(10, "Downloading video from Google Drive...")
        video_path = os.path.join(temp_dir, "original.mp4")
        
        success, error = await download_video_from_gdrive(file_id, video_path)
        if not success:
            raise Exception(error)
        
        # Step 3: Get video info
        update_status(20, "Analyzing video...")
        duration = await get_video_duration(video_path)
        
        if duration <= 0:
            raise ValueError("Invalid video file or corrupted download")
        if duration > 180:
            raise ValueError(f"Video too long ({duration:.0f}s). Maximum is 180 seconds (3 minutes)")
        
        # Step 4: Extract audio
        update_status(25, "Extracting audio...")
        audio_path = os.path.join(temp_dir, "audio.wav")
        
        if not await extract_audio_from_video(video_path, audio_path):
            raise Exception("Failed to extract audio from video")
        
        # Step 5: Transcribe
        update_status(30, "Transcribing audio with Groq Whisper...")
        transcript, error = await transcribe_audio(audio_path)
        
        aggressive_cleanup(audio_path)
        
        if not transcript:
            raise Exception(error or "Transcription failed - no Hindi audio detected")
        
        logger.info(f"   Transcript: {transcript[:100]}...")
        
        # Step 6: Generate AI script
        update_status(50, "Generating AI script...")
        metadata = await generate_ai_script(transcript, duration)
        
        logger.info(f"   Title: {metadata['title']}")
        
        # Step 7: Generate voiceover
        update_status(60, "Generating voiceover...")
        voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
        
        success, error = await generate_voiceover(metadata["script"], voiceover_path)
        if not success:
            raise Exception(error)
        
        # Step 8: Remove original audio
        update_status(70, "Removing original audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        
        if not await remove_original_audio(video_path, silent_video):
            raise Exception("Failed to remove original audio")
        
        aggressive_cleanup(video_path)
        
        # Step 9: Generate captions
        update_status(75, "Creating captions...")
        srt_path = os.path.join(temp_dir, "captions.srt")
        
        srt_content = generate_srt_captions(metadata["script"], duration)
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # Step 10: Download BGM
        update_status(80, "Downloading background music...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        
        bgm_downloaded = await download_bgm(bgm_path)
        if not bgm_downloaded:
            logger.warning("   BGM download failed, continuing without BGM")
            bgm_path = None
        
        # Step 11: Create final video
        update_status(85, "Creating final video...")
        final_video = os.path.join(temp_dir, "final.mp4")
        
        success, error = await create_final_video(silent_video, voiceover_path, srt_path, bgm_path, final_video)
        if not success:
            raise Exception(error)
        
        aggressive_cleanup(voiceover_path, srt_path, bgm_path)
        
        if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
            raise Exception("Final video is invalid or too small")
        
        final_size_mb = os.path.getsize(final_video) / (1024 * 1024)
        logger.info(f"   Final video: {final_size_mb:.1f} MB")
        
        # Step 12: Upload to YouTube
        update_status(90, "Uploading to YouTube...")
        
        upload_result = await upload_to_youtube(
            final_video,
            metadata["title"],
            metadata["description"],
            user_id
        )
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error", "YouTube upload failed"))
        
        # SUCCESS!
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video ID: {upload_result['video_id']}")
        logger.info(f"   URL: {upload_result['video_url']}")
        logger.info("=" * 80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "message": "Successfully uploaded to YouTube!",
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": ["#Shorts", "#Viral", "#Hindi", "#Reels"],
            "duration": round(duration, 1),
            "processing_time": round(elapsed, 1),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "transcript": transcript[:200],
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error("=" * 80)
        logger.error(f"❌ PROCESSING FAILED: {error_msg}")
        logger.error("=" * 80)
        
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
            logger.info("🧹 Cleaning up temp directory...")
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("✅ Cleanup complete")
            except Exception as e:
                logger.error(f"⚠️  Cleanup failed: {e}")
        
        gc.collect()


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Start processing a Google Drive video"""
    logger.info("🌐 API REQUEST: /api/gdrive-reels/process")
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        wait_for_result = data.get("wait", False)
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id is required"}
            )
        
        if not drive_url or "drive.google.com" not in drive_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Valid Google Drive URL is required"}
            )
        
        task_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            process_gdrive_reel,
            drive_url,
            user_id,
            task_id
        )
        
        logger.info(f"✅ Task started: {task_id}")
        
        if wait_for_result:
            # Frontend wants to wait for result
            max_wait = 300  # 5 minutes
            poll_interval = 2
            waited = 0
            
            while waited < max_wait:
                await asyncio.sleep(poll_interval)
                waited += poll_interval
                
                status = PROCESSING_STATUS.get(task_id)
                if not status:
                    continue
                
                if status["status"] == "completed":
                    return JSONResponse(content=status)
                elif status["status"] == "failed":
                    return JSONResponse(
                        status_code=500,
                        content=status
                    )
            
            return JSONResponse(
                status_code=504,
                content={
                    "success": False,
                    "error": "Processing timeout - video may be too large"
                }
            )
        else:
            return JSONResponse(content={
                "success": True,
                "task_id": task_id,
                "message": "Processing started"
            })
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@router.get("/api/gdrive-reels/status/{task_id}")
async def status_endpoint(task_id: str):
    """Check processing status"""
    status = PROCESSING_STATUS.get(task_id)
    
    if not status:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Task not found"}
        )
    
    return JSONResponse(content=status)


@router.get("/api/gdrive-reels/health")
async def health_endpoint():
    """Check if service is ready"""
    groq_ready = bool(GROQ_API_KEY)
    
    return JSONResponse(content={
        "status": "ok",
        "groq_api_configured": groq_ready,
        "stt_method": "Groq Whisper API",
        "active_tasks": len([s for s in PROCESSING_STATUS.values() if s["status"] == "processing"])
    })


# ═══════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════

async def initialize():
    """Initialize service"""
    logger.info("=" * 80)
    logger.info("🚀 INITIALIZING GDRIVE REELS SERVICE (GROQ API)")
    logger.info("=" * 80)
    
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_SPEECH_API not set!")
    else:
        logger.info("✅ Groq API configured")
        logger.info("   STT: Groq Whisper Large v3")
        logger.info("   Download: 3 fallback methods")
        logger.info("   Ready!")
    
    logger.info("=" * 80)


__all__ = ["router", "initialize"]