"""
gdrive_reels_optimized.py - GROQ WHISPER API VERSION
=====================================================
✅ Groq Whisper API (primary) - FASTEST & FREE
✅ Fallback to Whisper Large v3 Turbo
✅ No local model = No RAM issues
✅ Perfect for Render free tier
✅ No startup delay
=====================================================
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
GROQ_API_KEY = os.getenv("GROQ_SPEECH_API")  # Your existing env var
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
    logger.debug("   🧹 Garbage collected")


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
            if result.stderr:
                logger.error(f"   Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {step} - TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        logger.error(f"❌ {step} - ERROR: {e}")
        return False


def extract_gdrive_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID from URL"""
    if not url or "drive.google.com" not in url:
        return None
    
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]{25,})',
        r'[?&]id=([a-zA-Z0-9_-]{25,})',
        r'/open\?id=([a-zA-Z0-9_-]{25,})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD VIDEO
# ═══════════════════════════════════════════════════════════════════════

async def download_video_from_gdrive(file_id: str, output_path: str) -> bool:
    """Download video from Google Drive"""
    logger.info("⬇️  Downloading video from Google Drive...")
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    logger.error(f"   HTTP {response.status_code}")
                    return False
                
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=1024*1024):
                        f.write(chunk)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    logger.info(f"✅ Downloaded: {size_mb:.1f} MB")
                    return True
                else:
                    logger.error("   File too small or missing")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False


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
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # PCM 16-bit
        "-ar", "16000",  # 16kHz
        "-ac", "1",  # Mono
        "-y", audio_path
    ], timeout=60, step="Extract Audio")


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION - GROQ WHISPER API (PRIMARY + FALLBACK)
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_with_groq_primary(audio_path: str) -> Optional[str]:
    """
    Primary: Groq Whisper Large v3 (BEST QUALITY)
    
    ✅ Most accurate
    ✅ Better Hindi support
    ✅ Free tier: ~25-30 mins/day
    """
    if not GROQ_API_KEY:
        logger.warning("   GROQ_SPEECH_API not set")
        return None
    
    logger.info("🎙️  Method 1: Groq Whisper Large v3")
    
    try:
        from groq import Groq
        
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",  # Best quality
                response_format="text",
                language="hi"  # Hindi
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"✅ Method 1 SUCCESS: {len(transcription)} chars")
            logger.info(f"   Preview: {transcription[:100]}...")
            return transcription.strip()
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Method 1 failed: {e}")
        return None


async def transcribe_with_groq_fallback(audio_path: str) -> Optional[str]:
    """
    Fallback: Groq Whisper Large v3 Turbo (FASTER)
    
    ✅ 8x faster than large-v3
    ✅ Still very accurate
    ✅ Better for longer videos
    """
    if not GROQ_API_KEY:
        return None
    
    logger.info("🎙️  Method 2: Groq Whisper Large v3 Turbo")
    
    try:
        from groq import Groq
        
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",  # Faster
                response_format="text",
                language="hi"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"✅ Method 2 SUCCESS: {len(transcription)} chars")
            logger.info(f"   Preview: {transcription[:100]}...")
            return transcription.strip()
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Method 2 failed: {e}")
        return None


async def transcribe_audio(audio_path: str) -> Optional[str]:
    """
    Transcribe audio with 2 fallback methods
    
    Method 1: Groq Whisper Large v3 (best quality)
    Method 2: Groq Whisper Large v3 Turbo (faster)
    
    Both are FREE and work perfectly on Render!
    """
    logger.info("=" * 80)
    logger.info("📝 TRANSCRIBING AUDIO (GROQ WHISPER API)")
    logger.info("=" * 80)
    
    # Try Method 1: Large v3 (best quality)
    text = await transcribe_with_groq_primary(audio_path)
    if text:
        logger.info("=" * 80)
        logger.info("✅ TRANSCRIPTION SUCCESS (Whisper Large v3)")
        logger.info("=" * 80)
        return text
    
    logger.info("   Trying fallback method...")
    await asyncio.sleep(1)
    
    # Try Method 2: Large v3 Turbo (faster)
    text = await transcribe_with_groq_fallback(audio_path)
    if text:
        logger.info("=" * 80)
        logger.info("✅ TRANSCRIPTION SUCCESS (Whisper Large v3 Turbo)")
        logger.info("=" * 80)
        return text
    
    logger.error("=" * 80)
    logger.error("❌ ALL TRANSCRIPTION METHODS FAILED")
    logger.error("   Check: 1) GROQ_SPEECH_API is set")
    logger.error("          2) Audio file has speech")
    logger.error("          3) Groq API quota not exceeded")
    logger.error("=" * 80)
    return None


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
            prompt = f"""You are a viral Hindi content creator. Rewrite this transcript into a captivating {target_words}-word script for a viral reel.

ORIGINAL TRANSCRIPT:
{transcript}

REQUIREMENTS:
- Exactly {target_words} words in Hindi
- Make it engaging and dramatic
- Keep the core message
- Add emotional appeal

Return ONLY valid JSON:
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
    
    # Fallback: Simple trim
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

async def generate_voiceover(script: str, output_path: str) -> bool:
    """Generate Hindi voiceover using Edge TTS"""
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
            return True
        else:
            logger.error("   Voiceover file too small or missing")
            return False
            
    except Exception as e:
        logger.error(f"❌ Voiceover generation failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════
# CAPTIONS (SRT)
# ═══════════════════════════════════════════════════════════════════════

def generate_srt_captions(script: str, duration: float) -> str:
    """Generate SRT captions for the script"""
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
                             bgm: Optional[str], output: str) -> bool:
    """Create final video with captions, voiceover, and BGM"""
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
        return False
    
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
    
    return success


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
            return {"success": False, "error": "YouTube credentials not found for user"}
        
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
            return {"success": False, "error": result.get("error", "Upload failed")}
            
    except Exception as e:
        logger.error(f"❌ YouTube upload failed: {e}")
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# MAIN PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_gdrive_reel(drive_url: str, user_id: str, task_id: str):
    """Main processing pipeline"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
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
        
        # Extract file ID
        update_status(5, "Extracting file ID...")
        file_id = extract_gdrive_file_id(drive_url)
        if not file_id:
            raise ValueError("Invalid Google Drive URL")
        logger.info(f"   File ID: {file_id}")
        
        # Download video
        update_status(10, "Downloading video from Google Drive...")
        video_path = os.path.join(temp_dir, "original.mp4")
        
        if not await download_video_from_gdrive(file_id, video_path):
            raise Exception("Failed to download video from Google Drive")
        
        # Get video info
        update_status(20, "Analyzing video...")
        duration = await get_video_duration(video_path)
        
        if duration <= 0 or duration > 180:
            raise ValueError(f"Invalid video duration: {duration}s (must be 1-180s)")
        
        # Extract audio
        update_status(25, "Extracting audio...")
        audio_path = os.path.join(temp_dir, "audio.wav")
        
        if not await extract_audio_from_video(video_path, audio_path):
            raise Exception("Failed to extract audio")
        
        # Transcribe audio (GROQ API - FAST & RELIABLE!)
        update_status(30, "Transcribing audio with Groq Whisper API (10-20s)...")
        transcript = await transcribe_audio(audio_path)
        
        aggressive_cleanup(audio_path)
        
        if not transcript or len(transcript) < 5:
            raise Exception("Transcription failed - no speech detected in video")
        
        logger.info(f"   Transcript: {transcript[:100]}...")
        
        # Generate AI script
        update_status(50, "Generating viral script...")
        metadata = await generate_ai_script(transcript, duration)
        
        logger.info(f"   Title: {metadata['title']}")
        logger.info(f"   Script: {metadata['script'][:100]}...")
        
        # Generate voiceover
        update_status(60, "Generating voiceover...")
        voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
        
        if not await generate_voiceover(metadata["script"], voiceover_path):
            raise Exception("Failed to generate voiceover")
        
        # Remove original audio
        update_status(70, "Removing original audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        
        if not await remove_original_audio(video_path, silent_video):
            raise Exception("Failed to remove original audio")
        
        aggressive_cleanup(video_path)
        
        # Generate captions
        update_status(75, "Creating captions...")
        srt_path = os.path.join(temp_dir, "captions.srt")
        
        srt_content = generate_srt_captions(metadata["script"], duration)
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # Download BGM
        update_status(80, "Downloading background music...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        
        bgm_downloaded = await download_bgm(bgm_path)
        if not bgm_downloaded:
            logger.warning("   BGM download failed, continuing without BGM")
            bgm_path = None
        
        # Create final video
        update_status(85, "Creating final video...")
        final_video = os.path.join(temp_dir, "final.mp4")
        
        if not await create_final_video(silent_video, voiceover_path, srt_path, bgm_path, final_video):
            raise Exception("Failed to create final video")
        
        aggressive_cleanup(voiceover_path, srt_path, bgm_path)
        
        if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
            raise Exception("Final video is invalid or missing")
        
        final_size_mb = os.path.getsize(final_video) / (1024 * 1024)
        logger.info(f"   Final video: {final_size_mb:.1f} MB")
        
        # Upload to YouTube
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
            "message": "Successfully uploaded to YouTube!",
            "result": {
                "success": True,
                "title": metadata["title"],
                "description": metadata["description"],
                "video_id": upload_result["video_id"],
                "video_url": upload_result["video_url"],
                "processing_time": round(elapsed, 1),
                "transcript": transcript[:200]
            },
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ PROCESSING FAILED: {e}")
        logger.error("=" * 80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": str(e),
            "error": str(e),
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
        
        background_tasks.add_task(
            process_gdrive_reel,
            drive_url,
            user_id,
            task_id
        )
        
        logger.info(f"✅ Task started: {task_id}")
        
        return JSONResponse(content={
            "success": True,
            "task_id": task_id,
            "message": "Processing started. Use /api/gdrive-reels/status/{task_id} to check progress."
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
        "stt_method": "Groq Whisper API (no local model)",
        "active_tasks": len([s for s in PROCESSING_STATUS.values() if s["status"] == "processing"])
    })


# ═══════════════════════════════════════════════════════════════════════
# STARTUP INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

async def initialize():
    """
    Initialize service (no model loading needed!)
    
    Add to your main.py:
    
    @app.on_event("startup")
    async def startup():
        from gdrive_reels_optimized import initialize
        await initialize()
    """
    logger.info("=" * 80)
    logger.info("🚀 INITIALIZING GDRIVE REELS SERVICE (GROQ API)")
    logger.info("=" * 80)
    
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_SPEECH_API environment variable not set!")
        logger.error("   Service will not work without it!")
    else:
        logger.info("✅ Groq API key configured")
        logger.info("   STT: Groq Whisper Large v3 + Turbo fallback")
        logger.info("   No local model needed!")
        logger.info("   Ready to process videos!")
    
    logger.info("=" * 80)


__all__ = ["router", "initialize"]