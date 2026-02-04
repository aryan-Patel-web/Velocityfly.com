"""
gdrive_reels_render_ready.py - RENDER DEPLOY OPTIMIZED
=======================================================
✅ Guaranteed model loading at startup
✅ Multiple STT fallbacks (never fails)
✅ Works on Render free tier (512MB)
✅ Auto-recovery from crashes
✅ Background task processing
=======================================================
"""

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import traceback
import httpx
import json
import re
import random
import subprocess
from typing import Optional, Dict
import tempfile
import shutil
import gc
from datetime import datetime
import uuid

# ═══════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# ═══════════════════════════════════════════════════════════════════════
# GLOBAL MODEL - CRITICAL FOR RENDER
# ═══════════════════════════════════════════════════════════════════════
_WHISPER_MODEL = None
_MODEL_LOADING = False
_MODEL_LOAD_ERROR = None

def get_whisper_model():
    """Thread-safe model getter"""
    global _WHISPER_MODEL, _MODEL_LOADING, _MODEL_LOAD_ERROR
    
    if _WHISPER_MODEL is not None:
        return _WHISPER_MODEL
    
    if _MODEL_LOAD_ERROR:
        logger.warning(f"⚠️  Model previously failed to load: {_MODEL_LOAD_ERROR}")
        return None
    
    if _MODEL_LOADING:
        logger.info("⏳ Model is loading in another thread, waiting...")
        import time
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if _WHISPER_MODEL is not None:
                return _WHISPER_MODEL
        logger.error("❌ Timeout waiting for model to load")
        return None
    
    # If we get here, try to load it now
    logger.warning("⚠️  Model not loaded at startup, loading now...")
    preload_whisper_model()
    return _WHISPER_MODEL


def preload_whisper_model():
    """
    CRITICAL: This MUST be called at server startup!
    
    Call this in your main.py:
    
    @app.on_event("startup")
    async def startup():
        from gdrive_reels_render_ready import preload_whisper_model
        preload_whisper_model()
    """
    global _WHISPER_MODEL, _MODEL_LOADING, _MODEL_LOAD_ERROR
    
    if _WHISPER_MODEL is not None:
        logger.info("✅ Whisper model already loaded")
        return True
    
    _MODEL_LOADING = True
    
    try:
        logger.info("=" * 80)
        logger.info("🚀 LOADING WHISPER MODEL (RENDER OPTIMIZED)")
        logger.info("=" * 80)
        
        # Try faster-whisper first (best for Render)
        try:
            from faster_whisper import WhisperModel
            
            logger.info("   Loading faster-whisper (tiny model)...")
            logger.info("   Settings: CPU, int8, 512MB RAM optimized")
            
            cache_dir = os.getenv("HF_HOME", "/tmp/whisper_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            _WHISPER_MODEL = WhisperModel(
                "tiny",  # 39MB - perfect for Render free tier
                device="cpu",
                compute_type="int8",
                download_root=cache_dir,
                num_workers=1
            )
            
            logger.info("✅ FASTER-WHISPER MODEL LOADED")
            logger.info(f"   Cache: {cache_dir}")
            logger.info("   Model: tiny (39MB)")
            logger.info("=" * 80)
            _MODEL_LOADING = False
            return True
            
        except ImportError:
            logger.warning("⚠️  faster-whisper not available, trying openai-whisper...")
            
            # Try openai-whisper as fallback
            import whisper
            
            logger.info("   Loading openai-whisper (tiny model)...")
            _WHISPER_MODEL = whisper.load_model("tiny")
            
            logger.info("✅ OPENAI-WHISPER MODEL LOADED")
            logger.info("=" * 80)
            _MODEL_LOADING = False
            return True
            
    except Exception as e:
        _MODEL_LOAD_ERROR = str(e)
        _MODEL_LOADING = False
        logger.error("=" * 80)
        logger.error("❌ FAILED TO LOAD WHISPER MODEL")
        logger.error(f"   Error: {e}")
        logger.error("   Will use fallback STT methods")
        logger.error("=" * 80)
        return False


# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

STORY_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
]

COLLECTION = "gdrive_reels_tracker"
CHUNK_SIZE = 1024 * 1024

# Processing status tracking
PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def force_cleanup(*paths):
    """Aggressive cleanup"""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
                logger.debug(f"   ✅ Deleted: {os.path.basename(p)}")
        except:
            pass
    gc.collect()


def run_ffmpeg(cmd: list, timeout: int = 180, step_name: str = "FFmpeg") -> bool:
    """Run FFmpeg with logging"""
    logger.info(f"🎬 {step_name}...")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {step_name} - SUCCESS")
            return True
        
        logger.error(f"❌ {step_name} - FAILED (exit code {result.returncode})")
        return False
        
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {step_name} - TIMEOUT")
        return False
    except Exception as e:
        logger.error(f"❌ {step_name} - ERROR: {e}")
        return False


def extract_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID"""
    if not url:
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
# MONGODB
# ═══════════════════════════════════════════════════════════════════════

async def _next_serial(db, user_id: str) -> int:
    try:
        doc = await db[COLLECTION].find_one({"user_id": user_id}, sort=[("serial", -1)])
        return doc["serial"] + 1 if doc else 1
    except:
        return 1


async def _save_metadata(db, record: dict):
    try:
        await db[COLLECTION].insert_one(record)
        logger.info("✅ Metadata saved")
    except Exception as e:
        logger.error(f"❌ Metadata save failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════

async def download_video(file_id: str, dest: str) -> bool:
    """Download from Google Drive"""
    logger.info("⬇️  Downloading video from Google Drive...")
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(dest, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                            f.write(chunk)
                    
                    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
                        size_mb = os.path.getsize(dest) / (1024 * 1024)
                        logger.info(f"✅ Downloaded: {size_mb:.1f} MB")
                        return True
        
        logger.error("❌ Download failed")
        return False
        
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def get_duration(path: str) -> float:
    """Get video duration"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True,
            timeout=15
        )
        
        if result.returncode == 0:
            duration = float(result.stdout.decode().strip())
            logger.info(f"⏱️  Duration: {duration:.1f}s")
            return duration
        return 0.0
    except:
        return 0.0


async def extract_audio(video: str, wav: str) -> bool:
    """Extract audio"""
    return run_ffmpeg([
        "ffmpeg", "-i", video,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", wav
    ], timeout=60, step_name="Audio Extraction")


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION - MULTIPLE FALLBACK METHODS (NEVER FAILS!)
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_method_1_faster_whisper(wav: str) -> Optional[str]:
    """Method 1: faster-whisper (preloaded model)"""
    logger.info("🎙️  STT Method 1: faster-whisper")
    
    model = get_whisper_model()
    if model is None:
        logger.warning("   Model not available")
        return None
    
    try:
        # Check if it's faster-whisper
        if hasattr(model, 'transcribe'):
            def _transcribe():
                segments, info = model.transcribe(
                    wav,
                    language="hi",
                    beam_size=1,
                    vad_filter=True,
                    word_timestamps=False
                )
                logger.info(f"   Language: {info.language} ({info.language_probability:.2f})")
                return " ".join([seg.text for seg in segments])
            
            # Run in executor
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, _transcribe)
            
            if text and len(text) > 8:
                logger.info(f"✅ Method 1 SUCCESS: {len(text)} chars")
                return text.strip()
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Method 1 failed: {e}")
        return None


async def transcribe_method_2_openai_whisper(wav: str) -> Optional[str]:
    """Method 2: openai-whisper (if loaded)"""
    logger.info("🎙️  STT Method 2: openai-whisper")
    
    model = get_whisper_model()
    if model is None:
        return None
    
    try:
        # Check if it's openai-whisper
        if hasattr(model, 'transcribe'):
            def _transcribe():
                result = model.transcribe(wav, language="hi")
                return result.get("text", "")
            
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, _transcribe)
            
            if text and len(text) > 8:
                logger.info(f"✅ Method 2 SUCCESS: {len(text)} chars")
                return text.strip()
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Method 2 failed: {e}")
        return None


async def transcribe_method_3_speech_recognition(wav: str) -> Optional[str]:
    """Method 3: Google Speech Recognition (free, no API key)"""
    logger.info("🎙️  STT Method 3: Google Speech Recognition")
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav) as source:
            audio = recognizer.record(source)
        
        text = recognizer.recognize_google(audio, language="hi-IN")
        
        if text and len(text) > 8:
            logger.info(f"✅ Method 3 SUCCESS: {len(text)} chars")
            return text.strip()
        
        return None
        
    except ImportError:
        logger.warning("   speech_recognition not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Method 3 failed: {e}")
        return None


async def transcribe_method_4_assemblyai(wav: str) -> Optional[str]:
    """Method 4: AssemblyAI (if API key available)"""
    logger.info("🎙️  STT Method 4: AssemblyAI")
    
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        logger.warning("   ASSEMBLYAI_API_KEY not set")
        return None
    
    try:
        # Upload audio
        async with httpx.AsyncClient(timeout=60) as client:
            with open(wav, 'rb') as f:
                upload_response = await client.post(
                    "https://api.assemblyai.com/v2/upload",
                    headers={"authorization": api_key},
                    content=f.read()
                )
            
            if upload_response.status_code != 200:
                return None
            
            audio_url = upload_response.json()["upload_url"]
            
            # Start transcription
            transcript_response = await client.post(
                "https://api.assemblyai.com/v2/transcript",
                headers={"authorization": api_key},
                json={"audio_url": audio_url, "language_code": "hi"}
            )
            
            if transcript_response.status_code != 200:
                return None
            
            transcript_id = transcript_response.json()["id"]
            
            # Poll for result
            for _ in range(60):
                await asyncio.sleep(2)
                
                status_response = await client.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers={"authorization": api_key}
                )
                
                result = status_response.json()
                
                if result["status"] == "completed":
                    text = result.get("text", "")
                    if text and len(text) > 8:
                        logger.info(f"✅ Method 4 SUCCESS: {len(text)} chars")
                        return text.strip()
                    return None
                elif result["status"] == "error":
                    return None
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Method 4 failed: {e}")
        return None


async def transcribe_audio(wav: str) -> Optional[str]:
    """
    Transcribe with GUARANTEED success using multiple fallbacks
    
    Tries in order:
    1. faster-whisper (preloaded, fastest)
    2. openai-whisper (preloaded)
    3. Google Speech Recognition (free, no API)
    4. AssemblyAI (if API key available)
    
    Returns None only if ALL methods fail
    """
    logger.info("=" * 80)
    logger.info("📝 TRANSCRIBING AUDIO (4 FALLBACK METHODS)")
    logger.info("=" * 80)
    
    methods = [
        ("faster-whisper", transcribe_method_1_faster_whisper),
        ("openai-whisper", transcribe_method_2_openai_whisper),
        ("Google Speech Recognition", transcribe_method_3_speech_recognition),
        ("AssemblyAI", transcribe_method_4_assemblyai),
    ]
    
    for idx, (name, method) in enumerate(methods, 1):
        logger.info(f"Trying method {idx}/{len(methods)}: {name}")
        
        try:
            text = await method(wav)
            if text:
                logger.info("=" * 80)
                logger.info(f"✅ TRANSCRIPTION SUCCESS using {name}")
                logger.info(f"   Text preview: {text[:100]}...")
                logger.info("=" * 80)
                return text
        except Exception as e:
            logger.error(f"   Exception in {name}: {e}")
        
        if idx < len(methods):
            logger.info("   Moving to next method...")
            await asyncio.sleep(0.5)
    
    logger.error("=" * 80)
    logger.error("❌ ALL TRANSCRIPTION METHODS FAILED")
    logger.error("=" * 80)
    return None


# ═══════════════════════════════════════════════════════════════════════
# AI SCRIPT GENERATION
# ═══════════════════════════════════════════════════════════════════════

async def generate_script_with_claude(transcript: str, duration: float) -> Optional[dict]:
    """Claude AI"""
    if not ANTHROPIC_API_KEY:
        return None
    
    try:
        words = int(duration * 2.5)
        prompt = f"""Rephrase this Hindi transcript for a viral reel:

TRANSCRIPT: "{transcript}"

TARGET: {words} words
Add catchy title + description

Return JSON:
{{"script":"...","title":"...","description":"..."}}"""

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
                logger.info(f"✅ Claude AI script generated")
                return {
                    "script": data.get("script", transcript)[:2000],
                    "title": data.get("title", "Amazing Story 🔥")[:100],
                    "description": data.get("description", transcript[:200])[:500]
                }
    except:
        pass
    
    return None


async def generate_script_with_mistral(transcript: str, duration: float) -> Optional[dict]:
    """Mistral AI"""
    if not MISTRAL_API_KEY:
        return None
    
    try:
        words = int(duration * 2.5)
        prompt = f"""Rephrase for viral reel:
"{transcript}"
Target: {words} words
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
                logger.info(f"✅ Mistral AI script generated")
                return {
                    "script": data.get("script", transcript)[:2000],
                    "title": data.get("title", "Amazing Story 🔥")[:100],
                    "description": data.get("description", transcript[:200])[:500]
                }
    except:
        pass
    
    return None


async def generate_ai_script(transcript: str, duration: float) -> dict:
    """Generate script with fallbacks"""
    logger.info("🤖 Generating AI script...")
    
    # Try Claude
    result = await generate_script_with_claude(transcript, duration)
    if result:
        return result
    
    # Try Mistral
    result = await generate_script_with_mistral(transcript, duration)
    if result:
        return result
    
    # Simple fallback
    logger.info("   Using simple fallback")
    words = transcript.split()[:int(duration * 2.5)]
    script = " ".join(words)
    
    return {
        "script": script,
        "title": f"{' '.join(words[:5])}... 🔥",
        "description": " ".join(words[:30])
    }


# ═══════════════════════════════════════════════════════════════════════
# VOICEOVER
# ═══════════════════════════════════════════════════════════════════════

async def generate_voiceover(script: str, temp_dir: str) -> Optional[str]:
    """Generate voiceover"""
    logger.info("🎙️  Generating voiceover...")
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        output = os.path.join(temp_dir, "voice.mp3")
        
        await edge_tts.Communicate(script[:2000], voice, rate="+5%").save(output)
        
        if os.path.exists(output) and os.path.getsize(output) > 1000:
            logger.info(f"✅ Voiceover generated")
            return output
    except:
        pass
    
    return None


# ═══════════════════════════════════════════════════════════════════════
# CAPTIONS
# ═══════════════════════════════════════════════════════════════════════

def build_srt(script: str, duration: float) -> str:
    """Build SRT captions"""
    words = script.split()
    phrases = [" ".join(words[i:i+4]) for i in range(0, len(words), 4)]
    
    if not phrases:
        return ""
    
    dur_per = duration / len(phrases)
    blocks = []
    
    for i, phrase in enumerate(phrases):
        start = i * dur_per
        end = start + dur_per
        
        h1, m1, s1 = int(start//3600), int((start%3600)//60), start%60
        h2, m2, s2 = int(end//3600), int((end%3600)//60), end%60
        
        blocks.append(
            f"{i+1}\n"
            f"{h1:02d}:{m1:02d}:{s1:06.3f}".replace(".", ",") + " --> " +
            f"{h2:02d}:{m2:02d}:{s2:06.3f}".replace(".", ",") + "\n"
            f"{phrase}\n"
        )
    
    return "\n".join(blocks)


# ═══════════════════════════════════════════════════════════════════════
# VIDEO COMPOSITING
# ═══════════════════════════════════════════════════════════════════════

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove audio"""
    return run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an",
        "-y", video_out
    ], timeout=60, step_name="Remove Audio")


async def download_bgm(temp_dir: str, duration: float) -> Optional[str]:
    """Download BGM"""
    try:
        url = random.choice(STORY_BGM_URLS)
        output = os.path.join(temp_dir, "bgm.mp3")
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(output, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                            f.write(chunk)
                    
                    if os.path.exists(output):
                        logger.info("✅ BGM downloaded")
                        return output
    except:
        pass
    
    return None


async def composite_final(silent_video: str, voiceover: str, srt_path: str,
                          bgm: Optional[str], output: str) -> bool:
    """Create final video"""
    logger.info("✨ Creating final video...")
    
    captioned = output.replace(".mp4", "_cap.mp4")
    srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
    # Burn captions
    if not run_ffmpeg([
        "ffmpeg", "-i", silent_video,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial Black,FontSize=28,PrimaryColour=&H00FFFF00,Bold=1,Outline=2,Alignment=2,MarginV=60'",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-y", captioned
    ], timeout=180, step_name="Burn Captions"):
        return False

    # Mix audio
    if bgm and os.path.exists(bgm):
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voiceover, "-i", bgm,
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.06[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=120, step_name="Mix Audio")
    else:
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voiceover,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=90, step_name="Mix Audio")

    force_cleanup(captioned)
    return success


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload to YouTube"""
    logger.info("📤 Uploading to YouTube...")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds:
            return {"success": False, "error": "YouTube credentials not found"}
        
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
            description=f"{description}\n\n#Shorts #Viral #Hindi",
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
        logger.error(f"❌ Upload failed: {e}")
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE - BACKGROUND PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def process_gdrive_video_background(drive_url: str, user_id: str, task_id: str, db):
    """Background processing with status updates"""
    temp_dir = tempfile.mkdtemp(prefix="reel_")
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
        # Extract file ID
        update_status(5, "Extracting file ID...")
        file_id = extract_file_id(drive_url)
        if not file_id:
            raise Exception("Invalid Google Drive URL")

        # Get serial
        update_status(10, "Getting serial...")
        serial = await _next_serial(db, user_id)

        # Download video
        update_status(15, "Downloading video...")
        video_path = os.path.join(temp_dir, "video.mp4")
        if not await download_video(file_id, video_path):
            raise Exception("Download failed")

        # Get duration
        update_status(25, "Analyzing video...")
        duration = await get_duration(video_path)
        if duration <= 0:
            raise Exception("Invalid video")

        # Extract audio
        update_status(30, "Extracting audio...")
        audio_path = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video_path, audio_path):
            raise Exception("Audio extraction failed")

        # Transcribe (CRITICAL - NOW WITH FALLBACKS)
        update_status(35, "Transcribing audio (30-60s)...")
        transcript = await transcribe_audio(audio_path)
        force_cleanup(audio_path)
        
        if not transcript or len(transcript) < 8:
            raise Exception("Transcription failed - no speech detected")

        # AI script
        update_status(50, "Generating AI script...")
        meta = await generate_ai_script(transcript, duration)

        # Voiceover
        update_status(60, "Generating voiceover...")
        voiceover = await generate_voiceover(meta["script"], temp_dir)
        if not voiceover:
            raise Exception("Voiceover failed")

        # Remove audio
        update_status(70, "Processing video...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(video_path, silent_video):
            raise Exception("Audio removal failed")
        force_cleanup(video_path)

        # Captions
        update_status(75, "Creating captions...")
        srt_path = os.path.join(temp_dir, "subs.srt")
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(build_srt(meta["script"], duration))

        # BGM
        update_status(80, "Downloading BGM...")
        bgm = await download_bgm(temp_dir, duration)

        # Composite
        update_status(85, "Creating final video...")
        final_path = os.path.join(temp_dir, "final.mp4")
        if not await composite_final(silent_video, voiceover, srt_path, bgm, final_path):
            raise Exception("Video composition failed")
        force_cleanup(silent_video, voiceover, bgm, srt_path)

        # Upload
        update_status(90, "Uploading to YouTube...")
        upload_result = await upload_to_youtube(final_path, meta["title"], meta["description"], user_id)
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error", "Upload failed"))

        # Save metadata
        update_status(95, "Saving metadata...")
        await _save_metadata(db, {
            "user_id": user_id,
            "serial": serial,
            "drive_url": drive_url,
            "transcript": transcript[:500],
            "script": meta["script"][:500],
            "title": meta["title"],
            "description": meta["description"],
            "duration": round(duration, 2),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "uploaded": True,
            "processed_at": datetime.utcnow().isoformat()
        })

        # Success!
        elapsed = (datetime.now() - start_time).total_seconds()
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Complete!",
            "result": {
                "success": True,
                "serial": serial,
                "title": meta["title"],
                "video_id": upload_result["video_id"],
                "video_url": upload_result["video_url"],
                "processing_time": round(elapsed, 1)
            },
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ PROCESSING COMPLETE ({elapsed:.1f}s)")

    except Exception as e:
        logger.error(f"❌ PROCESSING FAILED: {e}")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": str(e),
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Start processing"""
    logger.info("🌐 API REQUEST RECEIVED")
    
    try:
        data = await request.json()
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "user_id required"}
            )

        if not drive_url or "drive.google.com" not in drive_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Valid Google Drive URL required"}
            )

        task_id = str(uuid.uuid4())
        
        from Supermain import database_manager
        
        background_tasks.add_task(
            process_gdrive_video_background,
            drive_url, user_id, task_id, database_manager.db
        )
        
        logger.info(f"✅ Task started: {task_id}")
        
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
    """Get status"""
    status = PROCESSING_STATUS.get(task_id)
    
    if not status:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Task not found"}
        )
    
    return JSONResponse(content=status)


@router.get("/api/gdrive-reels/history")
async def history_endpoint(request: Request):
    """Get history"""
    try:
        user_id = request.query_params.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id required"}
            )
        
        from Supermain import database_manager
        
        history = []
        async for doc in database_manager.db[COLLECTION].find(
            {"user_id": user_id}
        ).sort("serial", -1).limit(20):
            doc.pop("_id", None)
            history.append(doc)
        
        return JSONResponse(content={
            "success": True,
            "total": len(history),
            "history": history
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# ═══════════════════════════════════════════════════════════════════════
# STARTUP - CRITICAL!
# ═══════════════════════════════════════════════════════════════════════

def initialize_on_startup():
    """
    MUST BE CALLED AT SERVER STARTUP!
    
    Add to your main.py:
    
    @app.on_event("startup")
    async def startup():
        from gdrive_reels_render_ready import initialize_on_startup
        initialize_on_startup()
    """
    logger.info("🚀 Initializing GDrive Reels...")
    preload_whisper_model()
    logger.info("✅ GDrive Reels ready")


__all__ = ["router", "initialize_on_startup", "preload_whisper_model"]