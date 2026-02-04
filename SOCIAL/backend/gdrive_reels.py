"""
gdrive_reels.py - Production with Multiple Fallbacks & Extensive Logging
=========================================================================
✅ Multiple fallbacks for EVERY critical step
✅ Extensive logging for easy error tracking
✅ Optimized for Render 512MB free tier
✅ Compatible with existing build command
✅ No video storage in MongoDB
=========================================================================
"""

from fastapi import APIRouter, Request
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
from typing import List, Optional
import tempfile
import shutil
import gc
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "hi-IN-RaviNeural"]

STORY_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
]

COLLECTION = "gdrive_reels_tracker"
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def force_cleanup(*paths):
    """Aggressive cleanup + GC"""
    logger.info(f"🧹 Cleaning up {len(paths)} files...")
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
                logger.info(f"   ✅ Deleted: {os.path.basename(p)}")
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to delete {os.path.basename(p)}: {e}")
    gc.collect()
    gc.collect()
    logger.info("   ✅ Garbage collection completed")


def run_ffmpeg(cmd: list, timeout: int = 180, step_name: str = "FFmpeg") -> bool:
    """Run FFmpeg with logging"""
    logger.info(f"🎬 {step_name} - Starting...")
    logger.debug(f"   Command: {' '.join(cmd[:10])}...")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        
        if result.returncode != 0:
            stderr = result.stderr.decode(errors='replace')[:500]
            logger.error(f"❌ {step_name} - FAILED")
            logger.error(f"   Exit code: {result.returncode}")
            logger.error(f"   Error: {stderr}")
            return False
        
        logger.info(f"✅ {step_name} - SUCCESS")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {step_name} - TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"❌ {step_name} - EXCEPTION: {e}")
        return False


def extract_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID with logging"""
    logger.info("📎 Extracting file ID from URL...")
    logger.debug(f"   URL: {url[:100]}...")
    
    if not url:
        logger.error("❌ Empty URL provided")
        return None
    
    # Try multiple patterns
    patterns = [
        (r'/file/d/([a-zA-Z0-9_-]{25,})', "Pattern 1: /file/d/ID"),
        (r'[?&]id=([a-zA-Z0-9_-]{25,})', "Pattern 2: ?id=ID"),
        (r'/open\?id=([a-zA-Z0-9_-]{25,})', "Pattern 3: /open?id=ID"),
    ]
    
    for pattern, desc in patterns:
        logger.debug(f"   Trying {desc}...")
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            logger.info(f"✅ File ID extracted: {file_id}")
            logger.debug(f"   Method: {desc}")
            return file_id
    
    logger.error("❌ Could not extract file ID from URL")
    logger.error("   Make sure URL is in format: https://drive.google.com/file/d/FILE_ID/view")
    return None


# ═══════════════════════════════════════════════════════════════════════
# MONGODB (METADATA ONLY)
# ═══════════════════════════════════════════════════════════════════════

async def _next_serial(db, user_id: str) -> int:
    logger.info(f"🔢 Getting next serial for user: {user_id}")
    try:
        doc = await db[COLLECTION].find_one({"user_id": user_id}, sort=[("serial", -1)])
        serial = doc["serial"] + 1 if doc else 1
        logger.info(f"✅ Next serial: {serial}")
        return serial
    except Exception as e:
        logger.warning(f"⚠️  DB query failed: {e}, defaulting to serial 1")
        return 1


async def _save_metadata(db, record: dict):
    """Save ONLY metadata"""
    logger.info(f"💾 Saving metadata to MongoDB...")
    logger.debug(f"   Serial: {record.get('serial')}")
    logger.debug(f"   User: {record.get('user_id')}")
    logger.info("   ⚠️  NOTE: Video NOT stored, only metadata")
    
    try:
        await db[COLLECTION].insert_one(record)
        logger.info("✅ Metadata saved successfully")
    except Exception as e:
        logger.error(f"❌ Failed to save metadata: {e}")


async def _mark_uploaded(db, user_id: str, serial: int, video_id: str, video_url: str):
    logger.info(f"🎯 Marking serial {serial} as uploaded...")
    try:
        await db[COLLECTION].update_one(
            {"user_id": user_id, "serial": serial},
            {"$set": {
                "video_id": video_id,
                "video_url": video_url,
                "uploaded": True,
                "uploaded_at": datetime.utcnow().isoformat()
            }}
        )
        logger.info(f"✅ Upload status updated in DB")
    except Exception as e:
        logger.error(f"❌ Failed to update DB: {e}")


# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD - 3 FALLBACK METHODS
# ═══════════════════════════════════════════════════════════════════════

async def download_method_1_direct(file_id: str, dest: str) -> bool:
    """Method 1: Direct download with streaming"""
    logger.info("📥 DOWNLOAD METHOD 1: Direct streaming")
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    logger.debug(f"   URL: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            logger.debug("   Making request...")
            async with client.stream("GET", url) as response:
                logger.debug(f"   Status: {response.status_code}")
                logger.debug(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    
                    # Check if HTML (confirmation page)
                    if "text/html" in content_type:
                        logger.info("   Detected confirmation page for large file")
                        html = await response.aread()
                        html = html.decode(errors='replace')
                        
                        match = re.search(r'href="(/uc\?[^"]*&confirm=[^"]*)"', html)
                        if match:
                            confirm_url = "https://drive.google.com" + match.group(1).replace("&amp;", "&")
                            logger.info("   Following confirmation URL...")
                            logger.debug(f"   Confirm URL: {confirm_url[:100]}...")
                            
                            async with client.stream("GET", confirm_url) as confirm_response:
                                if confirm_response.status_code == 200:
                                    logger.info("   Downloading in chunks...")
                                    with open(dest, 'wb') as f:
                                        chunk_count = 0
                                        async for chunk in confirm_response.aiter_bytes(chunk_size=CHUNK_SIZE):
                                            f.write(chunk)
                                            chunk_count += 1
                                            if chunk_count % 10 == 0:
                                                logger.debug(f"      Downloaded {chunk_count} MB...")
                                    
                                    size_mb = os.path.getsize(dest) / (1024 * 1024)
                                    logger.info(f"✅ Method 1 SUCCESS: {size_mb:.1f} MB")
                                    return True
                        
                        logger.warning("   ⚠️  Could not find confirmation link")
                        return False
                    
                    # Direct download
                    else:
                        logger.info("   Direct download (small file)...")
                        with open(dest, 'wb') as f:
                            chunk_count = 0
                            async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                                f.write(chunk)
                                chunk_count += 1
                                if chunk_count % 10 == 0:
                                    logger.debug(f"      Downloaded {chunk_count} MB...")
                        
                        size_mb = os.path.getsize(dest) / (1024 * 1024)
                        logger.info(f"✅ Method 1 SUCCESS: {size_mb:.1f} MB")
                        return True
                
                logger.warning(f"   ⚠️  HTTP {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Method 1 FAILED: {e}")
        return False


async def download_method_2_usercontent(file_id: str, dest: str) -> bool:
    """Method 2: Try usercontent domain"""
    logger.info("📥 DOWNLOAD METHOD 2: usercontent domain")
    
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
    logger.debug(f"   URL: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    logger.info("   Downloading...")
                    with open(dest, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                            f.write(chunk)
                    
                    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
                        size_mb = os.path.getsize(dest) / (1024 * 1024)
                        logger.info(f"✅ Method 2 SUCCESS: {size_mb:.1f} MB")
                        return True
                
                logger.warning(f"   ⚠️  HTTP {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Method 2 FAILED: {e}")
        return False


async def download_method_3_wget(file_id: str, dest: str) -> bool:
    """Method 3: Use wget as fallback"""
    logger.info("📥 DOWNLOAD METHOD 3: wget fallback")
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        logger.debug("   Running wget...")
        result = subprocess.run(
            ["wget", "--no-check-certificate", "-O", dest, url],
            capture_output=True,
            timeout=180
        )
        
        if result.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 10000:
            size_mb = os.path.getsize(dest) / (1024 * 1024)
            logger.info(f"✅ Method 3 SUCCESS: {size_mb:.1f} MB")
            return True
        
        logger.warning(f"   ⚠️  wget failed with code {result.returncode}")
        return False
    except Exception as e:
        logger.error(f"❌ Method 3 FAILED: {e}")
        return False


async def download_video(file_id: str, dest: str) -> bool:
    """Download with 3 fallback methods"""
    logger.info("=" * 80)
    logger.info("⬇️  DOWNLOADING VIDEO (3 methods available)")
    logger.info("=" * 80)
    
    methods = [
        ("Direct Streaming", download_method_1_direct),
        ("UserContent Domain", download_method_2_usercontent),
        ("Wget Fallback", download_method_3_wget),
    ]
    
    for idx, (name, method) in enumerate(methods, 1):
        logger.info(f"Trying method {idx}/3: {name}")
        
        try:
            if await method(file_id, dest):
                logger.info("=" * 80)
                logger.info(f"✅ DOWNLOAD COMPLETE using {name}")
                logger.info("=" * 80)
                return True
        except Exception as e:
            logger.error(f"   Method {idx} exception: {e}")
        
        if idx < len(methods):
            logger.info(f"   Moving to next method...")
            await asyncio.sleep(1)
    
    logger.error("=" * 80)
    logger.error("❌ ALL DOWNLOAD METHODS FAILED")
    logger.error("=" * 80)
    return False


# ═══════════════════════════════════════════════════════════════════════
# VIDEO INFO & AUDIO EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

async def get_duration(path: str) -> float:
    """Get video duration with logging"""
    logger.info("⏱️  Getting video duration...")
    
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True,
            timeout=15
        )
        
        if result.returncode == 0:
            duration = float(result.stdout.decode().strip())
            logger.info(f"✅ Duration: {duration:.2f}s ({duration/60:.1f} minutes)")
            return duration
        
        logger.error(f"❌ ffprobe failed: {result.stderr.decode()[:200]}")
        return 0.0
    except Exception as e:
        logger.error(f"❌ Duration check failed: {e}")
        return 0.0


async def extract_audio(video: str, wav: str) -> bool:
    """Extract audio with logging"""
    logger.info("🔊 Extracting audio from video...")
    logger.debug(f"   Input: {os.path.basename(video)}")
    logger.debug(f"   Output: {os.path.basename(wav)}")
    
    success = run_ffmpeg([
        "ffmpeg", "-i", video,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", wav
    ], timeout=60, step_name="Audio Extraction")
    
    if success and os.path.exists(wav):
        size_mb = os.path.getsize(wav) / (1024 * 1024)
        logger.info(f"✅ Audio extracted: {size_mb:.2f} MB")
        return True
    
    logger.error("❌ Audio extraction failed")
    return False


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION - 3 FALLBACK METHODS
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_method_1_faster_whisper(wav: str) -> Optional[str]:
    """Method 1: faster-whisper (tiny model)"""
    logger.info("🎙️  TRANSCRIPTION METHOD 1: faster-whisper (tiny)")
    
    try:
        from faster_whisper import WhisperModel
        
        logger.info("   Loading tiny model (39MB, optimized for 512MB RAM)...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        
        logger.info("   Transcribing audio...")
        logger.debug("   Settings: language=hi, beam_size=1, vad_filter=True")
        
        segments, info = model.transcribe(
            wav,
            language="hi",
            beam_size=1,
            vad_filter=True
        )
        
        logger.info(f"   Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        text = " ".join([seg.text for seg in segments])
        
        # Clean up model from memory
        del model
        gc.collect()
        logger.debug("   Model removed from memory")
        
        if text and len(text) > 8:
            logger.info(f"✅ Method 1 SUCCESS: {len(text)} characters")
            logger.debug(f"   Preview: {text[:100]}...")
            return text.strip()
        
        logger.warning("⚠️  Method 1: Output too short")
        return None
        
    except ImportError:
        logger.error("❌ Method 1 FAILED: faster-whisper not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Method 1 FAILED: {e}")
        logger.debug(traceback.format_exc())
        return None


async def transcribe_method_2_speech_recognition(wav: str) -> Optional[str]:
    """Method 2: SpeechRecognition with Google"""
    logger.info("🎙️  TRANSCRIPTION METHOD 2: SpeechRecognition + Google")
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        logger.info("   Loading audio file...")
        with sr.AudioFile(wav) as source:
            audio = recognizer.record(source)
        
        logger.info("   Recognizing speech (Google API)...")
        text = recognizer.recognize_google(audio, language="hi-IN")
        
        if text and len(text) > 8:
            logger.info(f"✅ Method 2 SUCCESS: {len(text)} characters")
            logger.debug(f"   Preview: {text[:100]}...")
            return text.strip()
        
        logger.warning("⚠️  Method 2: Output too short")
        return None
        
    except ImportError:
        logger.error("❌ Method 2 FAILED: SpeechRecognition not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Method 2 FAILED: {e}")
        return None


async def transcribe_method_3_whisper_cli(wav: str) -> Optional[str]:
    """Method 3: Whisper CLI (if installed)"""
    logger.info("🎙️  TRANSCRIPTION METHOD 3: Whisper CLI")
    
    try:
        out_dir = os.path.dirname(wav)
        logger.info("   Running whisper command...")
        
        result = subprocess.run(
            ["whisper", wav, "--language", "hi", "--model", "tiny",
             "--output_dir", out_dir, "--output_format", "txt"],
            capture_output=True,
            timeout=300
        )
        
        if result.returncode == 0:
            txt_file = wav.rsplit(".", 1)[0] + ".txt"
            logger.debug(f"   Looking for: {txt_file}")
            
            if os.path.exists(txt_file):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                
                if text and len(text) > 8:
                    logger.info(f"✅ Method 3 SUCCESS: {len(text)} characters")
                    logger.debug(f"   Preview: {text[:100]}...")
                    return text
                
                logger.warning("⚠️  Method 3: Output file empty")
            else:
                logger.warning(f"⚠️  Method 3: Output file not found")
        else:
            logger.warning(f"⚠️  Method 3: Command failed with code {result.returncode}")
        
        return None
        
    except FileNotFoundError:
        logger.error("❌ Method 3 FAILED: Whisper CLI not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Method 3 FAILED: {e}")
        return None


async def transcribe_audio(wav: str) -> Optional[str]:
    """Transcribe with 3 fallback methods"""
    logger.info("=" * 80)
    logger.info("📝 TRANSCRIBING AUDIO (3 methods available)")
    logger.info("=" * 80)
    
    methods = [
        ("faster-whisper", transcribe_method_1_faster_whisper),
        ("SpeechRecognition", transcribe_method_2_speech_recognition),
        ("Whisper CLI", transcribe_method_3_whisper_cli),
    ]
    
    for idx, (name, method) in enumerate(methods, 1):
        logger.info(f"Trying method {idx}/3: {name}")
        
        try:
            text = await method(wav)
            if text:
                logger.info("=" * 80)
                logger.info(f"✅ TRANSCRIPTION COMPLETE using {name}")
                logger.info("=" * 80)
                return text
        except Exception as e:
            logger.error(f"   Method {idx} exception: {e}")
        
        if idx < len(methods):
            logger.info(f"   Moving to next method...")
            await asyncio.sleep(0.5)
    
    logger.error("=" * 80)
    logger.error("❌ ALL TRANSCRIPTION METHODS FAILED")
    logger.error("   Suggestions:")
    logger.error("   1. Ensure video has clear Hindi speech")
    logger.error("   2. Check audio is not too quiet")
    logger.error("   3. Try a different video")
    logger.error("=" * 80)
    return None


# ═══════════════════════════════════════════════════════════════════════
# AI SCRIPT GENERATION - 2 FALLBACK METHODS
# ═══════════════════════════════════════════════════════════════════════

async def ai_method_1_mistral(transcript: str, duration: float) -> Optional[dict]:
    """Method 1: Mistral AI"""
    logger.info("🤖 AI METHOD 1: Mistral API")
    
    if not MISTRAL_API_KEY:
        logger.error("❌ MISTRAL_API_KEY not set")
        return None
    
    words = int(duration * 2.5)
    logger.info(f"   Target: {words} words for {duration:.1f}s video")
    
    prompt = f"""Rephrase this Hindi transcript minimally (change few words only):

ORIGINAL: "{transcript}"

RULES:
1. Keep story EXACT same order
2. Change only 10-15% words (use synonyms)
3. Target: {words} words max
4. Add catchy title (4-6 words + 1 emoji)
5. Add description (1-2 lines)

Return ONLY JSON:
{{"script":"...","title":"...","description":"..."}}"""

    try:
        logger.info("   Calling Mistral API...")
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
        
        if response.status_code != 200:
            logger.error(f"   ⚠️  API returned {response.status_code}")
            logger.error(f"   Response: {response.text[:200]}")
            return None

        content = response.json()["choices"][0]["message"]["content"]
        logger.debug(f"   Raw response: {content[:200]}...")
        
        # Clean JSON
        content = re.sub(r'```json\s*|```', '', content).strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if not match:
            logger.error("   ⚠️  No JSON found in response")
            return None
        
        data = json.loads(match.group(0))
        
        logger.info(f"✅ Method 1 SUCCESS")
        logger.info(f"   Title: {data.get('title', 'N/A')}")
        logger.info(f"   Script length: {len(data.get('script', ''))} chars")
        
        return {
            "script": data.get("script", transcript)[:2000],
            "title": data.get("title", "Amazing Story 🔥")[:100],
            "description": data.get("description", transcript[:200])[:500]
        }
        
    except Exception as e:
        logger.error(f"❌ Method 1 FAILED: {e}")
        return None


async def ai_method_2_fallback(transcript: str, duration: float) -> dict:
    """Method 2: Simple fallback (no API)"""
    logger.info("🤖 AI METHOD 2: Fallback (no API)")
    
    logger.info("   Using transcript as-is with basic processing...")
    
    # Simple word limit
    words = transcript.split()[:int(duration * 2.5)]
    script = " ".join(words)
    
    # Generate simple title
    title_words = " ".join(words[:5])
    title = f"{title_words}... 🔥"
    
    # Simple description
    description = " ".join(words[:30])
    
    logger.info(f"✅ Method 2 SUCCESS (fallback)")
    logger.info(f"   Title: {title}")
    logger.info(f"   Script length: {len(script)} chars")
    
    return {
        "script": script,
        "title": title,
        "description": description
    }


async def generate_ai_script(transcript: str, duration: float) -> dict:
    """Generate script with 2 fallback methods"""
    logger.info("=" * 80)
    logger.info("🤖 AI SCRIPT GENERATION (2 methods available)")
    logger.info("=" * 80)
    
    methods = [
        ("Mistral AI", ai_method_1_mistral),
        ("Simple Fallback", ai_method_2_fallback),
    ]
    
    for idx, (name, method) in enumerate(methods, 1):
        logger.info(f"Trying method {idx}/2: {name}")
        
        try:
            result = await method(transcript, duration)
            if result:
                logger.info("=" * 80)
                logger.info(f"✅ AI SCRIPT COMPLETE using {name}")
                logger.info("=" * 80)
                return result
        except Exception as e:
            logger.error(f"   Method {idx} exception: {e}")
        
        if idx < len(methods):
            logger.info(f"   Moving to next method...")
            await asyncio.sleep(0.5)
    
    # This should never happen as fallback always succeeds
    logger.warning("Using emergency fallback...")
    return {
        "script": transcript[:2000],
        "title": "Amazing Story 🔥",
        "description": transcript[:200]
    }


# ═══════════════════════════════════════════════════════════════════════
# VOICEOVER GENERATION - 2 FALLBACK METHODS
# ═══════════════════════════════════════════════════════════════════════

async def voiceover_method_1_edge_tts(script: str, temp_dir: str) -> Optional[str]:
    """Method 1: Edge TTS"""
    logger.info("🎙️  VOICEOVER METHOD 1: Edge TTS")
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        output = os.path.join(temp_dir, "voice.mp3")
        
        logger.info(f"   Voice: {voice}")
        logger.info(f"   Script length: {len(script)} chars")
        logger.info("   Generating speech...")
        
        await edge_tts.Communicate(script[:2000], voice, rate="+5%").save(output)
        
        if os.path.exists(output) and os.path.getsize(output) > 1000:
            size_mb = os.path.getsize(output) / (1024 * 1024)
            logger.info(f"✅ Method 1 SUCCESS: {size_mb:.2f} MB")
            return output
        
        logger.warning("⚠️  Method 1: Output file empty or missing")
        return None
        
    except ImportError:
        logger.error("❌ Method 1 FAILED: edge_tts not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Method 1 FAILED: {e}")
        return None


async def voiceover_method_2_gtts(script: str, temp_dir: str) -> Optional[str]:
    """Method 2: gTTS fallback"""
    logger.info("🎙️  VOICEOVER METHOD 2: gTTS")
    
    try:
        from gtts import gTTS
        
        output = os.path.join(temp_dir, "voice.mp3")
        
        logger.info("   Generating speech with gTTS...")
        tts = gTTS(text=script[:2000], lang='hi', slow=False)
        tts.save(output)
        
        if os.path.exists(output) and os.path.getsize(output) > 1000:
            size_mb = os.path.getsize(output) / (1024 * 1024)
            logger.info(f"✅ Method 2 SUCCESS: {size_mb:.2f} MB")
            return output
        
        logger.warning("⚠️  Method 2: Output file empty or missing")
        return None
        
    except ImportError:
        logger.error("❌ Method 2 FAILED: gtts not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Method 2 FAILED: {e}")
        return None


async def generate_voiceover(script: str, temp_dir: str) -> Optional[str]:
    """Generate voiceover with 2 fallback methods"""
    logger.info("=" * 80)
    logger.info("🎙️  VOICEOVER GENERATION (2 methods available)")
    logger.info("=" * 80)
    
    methods = [
        ("Edge TTS", voiceover_method_1_edge_tts),
        ("gTTS", voiceover_method_2_gtts),
    ]
    
    for idx, (name, method) in enumerate(methods, 1):
        logger.info(f"Trying method {idx}/2: {name}")
        
        try:
            output = await method(script, temp_dir)
            if output:
                logger.info("=" * 80)
                logger.info(f"✅ VOICEOVER COMPLETE using {name}")
                logger.info("=" * 80)
                return output
        except Exception as e:
            logger.error(f"   Method {idx} exception: {e}")
        
        if idx < len(methods):
            logger.info(f"   Moving to next method...")
            await asyncio.sleep(0.5)
    
    logger.error("=" * 80)
    logger.error("❌ ALL VOICEOVER METHODS FAILED")
    logger.error("=" * 80)
    return None


# ═══════════════════════════════════════════════════════════════════════
# GOLDEN CAPTIONS
# ═══════════════════════════════════════════════════════════════════════

def build_srt(script: str, duration: float) -> str:
    """Build SRT captions with logging"""
    logger.info("📝 Building golden captions...")
    
    words = script.split()
    logger.info(f"   Total words: {len(words)}")
    
    # Group into 4-word phrases
    phrases = []
    for i in range(0, len(words), 4):
        phrases.append(" ".join(words[i:i+4]))
    
    if not phrases:
        logger.warning("   ⚠️  No phrases generated")
        return ""
    
    dur_per = duration / len(phrases)
    logger.info(f"   Phrases: {len(phrases)}, Duration per phrase: {dur_per:.2f}s")
    
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
    
    logger.info(f"✅ SRT built: {len(blocks)} subtitle blocks")
    return "\n".join(blocks)


# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove original audio"""
    logger.info("🔇 Removing original audio from video...")
    
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an",
        "-y", video_out
    ], timeout=60, step_name="Audio Removal")
    
    if success and os.path.exists(video_out):
        size_mb = os.path.getsize(video_out) / (1024 * 1024)
        logger.info(f"✅ Silent video created: {size_mb:.2f} MB")
        return True
    
    return False


async def download_bgm(temp_dir: str, duration: float) -> Optional[str]:
    """Download BGM with logging"""
    logger.info("🎵 Downloading background music...")
    
    url = random.choice(STORY_BGM_URLS)
    logger.debug(f"   URL: {url[:80]}...")
    
    raw = os.path.join(temp_dir, "bgm_raw.mp3")
    output = os.path.join(temp_dir, "bgm.mp3")
    
    try:
        logger.info("   Fetching BGM...")
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(raw, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                            f.write(chunk)
                    
                    logger.info(f"   Downloaded: {os.path.getsize(raw)/(1024*1024):.2f} MB")
                    logger.info(f"   Trimming to {duration:.1f}s...")
                    
                    if run_ffmpeg([
                        "ffmpeg", "-i", raw,
                        "-t", str(duration + 2),
                        "-acodec", "copy",
                        "-y", output
                    ], timeout=45, step_name="BGM Trim"):
                        force_cleanup(raw)
                        logger.info(f"✅ BGM ready: {os.path.getsize(output)/(1024*1024):.2f} MB")
                        return output
                    
                    return raw if os.path.exists(raw) else None
    except Exception as e:
        logger.error(f"❌ BGM download failed: {e}")
    
    logger.warning("⚠️  BGM unavailable, will proceed without background music")
    return None


async def composite_final(silent_video: str, voiceover: str, srt_path: str,
                          bgm: Optional[str], output: str) -> bool:
    """Composite final video with logging"""
    logger.info("=" * 80)
    logger.info("✨ CREATING FINAL VIDEO")
    logger.info("=" * 80)
    
    captioned = output.replace(".mp4", "_cap.mp4")
    srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
    logger.info("STEP 1/2: Burning golden captions...")
    subtitle_filter = (
        f"subtitles={srt_esc}:"
        "force_style='FontName=Arial Black,FontSize=28,PrimaryColour=&H00FFFF00,"
        "OutlineColour=&H00000000,Bold=1,Outline=2,Alignment=2,MarginV=60'"
    )
    
    if not run_ffmpeg([
        "ffmpeg", "-i", silent_video,
        "-vf", subtitle_filter,
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-y", captioned
    ], timeout=180, step_name="Caption Burn"):
        logger.error("❌ Caption burning failed")
        return False
    
    logger.info(f"   Captioned video: {os.path.getsize(captioned)/(1024*1024):.2f} MB")

    logger.info("STEP 2/2: Mixing audio...")
    if bgm and os.path.exists(bgm):
        logger.info("   Mixing: voiceover + BGM (6% volume)")
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voiceover, "-i", bgm,
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.06[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=120, step_name="Audio Mix (with BGM)")
    else:
        logger.info("   Mixing: voiceover only (no BGM)")
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voiceover,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=90, step_name="Audio Mix (no BGM)")

    force_cleanup(captioned)
    
    if success and os.path.exists(output):
        size_mb = os.path.getsize(output) / (1024 * 1024)
        logger.info("=" * 80)
        logger.info(f"✅ FINAL VIDEO CREATED: {size_mb:.2f} MB")
        logger.info("=" * 80)
        return True
    
    logger.error("❌ Final video creation failed")
    return False


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD - 2 FALLBACK METHODS
# ═══════════════════════════════════════════════════════════════════════

async def upload_method_1_scheduler(video_path: str, title: str, description: str, user_id: str) -> Optional[dict]:
    """Method 1: Use youtube_scheduler"""
    logger.info("📤 UPLOAD METHOD 1: YouTube scheduler")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            logger.info("   Connecting to YouTube database...")
            await yt_db.connect()
        
        logger.info(f"   Fetching credentials for user: {user_id}")
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds:
            logger.error("   ⚠️  YouTube credentials not found")
            return None
        
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
        
        full_desc = f"{description}\n\n#Shorts #Viral #Hindi"
        
        logger.info("   Uploading to YouTube...")
        logger.debug(f"   Title: {title}")
        logger.debug(f"   Description length: {len(full_desc)} chars")
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=full_desc,
            video_url=video_path
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            logger.info(f"✅ Method 1 SUCCESS")
            logger.info(f"   Video ID: {video_id}")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        logger.warning(f"   ⚠️  Upload failed: {result.get('error', 'Unknown error')}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Method 1 FAILED: {e}")
        logger.debug(traceback.format_exc())
        return None


async def upload_method_2_direct(video_path: str, title: str, description: str, user_id: str) -> Optional[dict]:
    """Method 2: Direct API call (if available)"""
    logger.info("📤 UPLOAD METHOD 2: Direct API")
    logger.warning("   ⚠️  Direct API upload not implemented yet")
    logger.warning("   This would require google-api-python-client")
    return None


async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload with 2 fallback methods"""
    logger.info("=" * 80)
    logger.info("📤 UPLOADING TO YOUTUBE (2 methods available)")
    logger.info("=" * 80)
    
    methods = [
        ("YouTube Scheduler", upload_method_1_scheduler),
        ("Direct API", upload_method_2_direct),
    ]
    
    for idx, (name, method) in enumerate(methods, 1):
        logger.info(f"Trying method {idx}/2: {name}")
        
        try:
            result = await method(video_path, title, description, user_id)
            if result and result.get("success"):
                logger.info("=" * 80)
                logger.info(f"✅ UPLOAD COMPLETE using {name}")
                logger.info(f"   Video URL: {result['video_url']}")
                logger.info("=" * 80)
                return result
        except Exception as e:
            logger.error(f"   Method {idx} exception: {e}")
        
        if idx < len(methods):
            logger.info(f"   Moving to next method...")
            await asyncio.sleep(0.5)
    
    logger.error("=" * 80)
    logger.error("❌ ALL UPLOAD METHODS FAILED")
    logger.error("=" * 80)
    return {"success": False, "error": "All upload methods failed"}


# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_gdrive_video(drive_url: str, user_id: str, db) -> dict:
    """Main processing pipeline with extensive logging"""
    logger.info("╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 15 + "GDRIVE REEL PROCESSING START" + " " * 35 + "║")
    logger.info("║" + " " * 20 + "Memory Optimized for 512MB" + " " * 32 + "║")
    logger.info("╚" + "=" * 78 + "╝")
    
    temp_dir = tempfile.mkdtemp(prefix="reel_")
    logger.info(f"📁 Temp directory: {temp_dir}")
    
    start_time = datetime.now()
    
    try:
        # STEP 1: Extract file ID
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1/11: Extract file ID")
        logger.info("=" * 80)
        
        file_id = extract_file_id(drive_url)
        if not file_id:
            return {"success": False, "error": "Invalid Google Drive URL. Format: https://drive.google.com/file/d/FILE_ID/view"}

        # STEP 2: Get serial
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2/11: Get serial number")
        logger.info("=" * 80)
        
        serial = await _next_serial(db, user_id)

        # STEP 3: Download video
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3/11: Download video from Google Drive")
        logger.info("=" * 80)
        
        video_path = os.path.join(temp_dir, "video.mp4")
        if not await download_video(file_id, video_path):
            return {"success": False, "error": "Download failed. Make sure: 1) Link is public (Share > Anyone with link), 2) File is a video, 3) File size < 100MB"}

        # STEP 4: Get duration
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4/11: Get video duration")
        logger.info("=" * 80)
        
        duration = await get_duration(video_path)
        if duration <= 0:
            return {"success": False, "error": "Invalid video file or could not read duration"}

        # STEP 5: Extract audio
        logger.info("\n" + "=" * 80)
        logger.info("STEP 5/11: Extract audio")
        logger.info("=" * 80)
        
        audio_path = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video_path, audio_path):
            return {"success": False, "error": "Audio extraction failed. Video may be corrupted."}

        # STEP 6: Transcribe
        logger.info("\n" + "=" * 80)
        logger.info("STEP 6/11: Transcribe audio to text")
        logger.info("=" * 80)
        
        transcript = await transcribe_audio(audio_path)
        force_cleanup(audio_path)  # Clean up immediately
        
        if not transcript or len(transcript) < 8:
            return {"success": False, "error": "Transcription failed. Video must have clear Hindi speech. Try a video with clear audio."}

        # STEP 7: AI script
        logger.info("\n" + "=" * 80)
        logger.info("STEP 7/11: Generate AI script")
        logger.info("=" * 80)
        
        meta = await generate_ai_script(transcript, duration)
        script = meta["script"]
        title = meta["title"]
        description = meta["description"]

        # STEP 8: Voiceover
        logger.info("\n" + "=" * 80)
        logger.info("STEP 8/11: Generate Hindi voiceover")
        logger.info("=" * 80)
        
        voiceover = await generate_voiceover(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Voiceover generation failed. All TTS methods failed."}

        # STEP 9: Remove audio
        logger.info("\n" + "=" * 80)
        logger.info("STEP 9/11: Remove original audio")
        logger.info("=" * 80)
        
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(video_path, silent_video):
            return {"success": False, "error": "Failed to remove original audio"}
        
        force_cleanup(video_path)  # Clean up immediately

        # STEP 10: Create captions
        logger.info("\n" + "=" * 80)
        logger.info("STEP 10/11: Create golden captions")
        logger.info("=" * 80)
        
        srt_path = os.path.join(temp_dir, "subs.srt")
        srt_content = build_srt(script, duration)
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        logger.info(f"   SRT file created: {len(srt_content)} bytes")

        # STEP 11: Download BGM
        logger.info("\n" + "=" * 80)
        logger.info("STEP 11/11: Download background music (optional)")
        logger.info("=" * 80)
        
        bgm = await download_bgm(temp_dir, duration)

        # STEP 12: Composite
        logger.info("\n" + "=" * 80)
        logger.info("STEP 12/11: Create final video")
        logger.info("=" * 80)
        
        final_path = os.path.join(temp_dir, "final.mp4")
        if not await composite_final(silent_video, voiceover, srt_path, bgm, final_path):
            return {"success": False, "error": "Final video composition failed"}

        force_cleanup(silent_video, voiceover, bgm, srt_path)  # Cleanup intermediates

        # STEP 13: Upload
        logger.info("\n" + "=" * 80)
        logger.info("STEP 13/11: Upload to YouTube")
        logger.info("   ⚠️  Video will NOT be stored in database")
        logger.info("=" * 80)
        
        upload_result = await upload_to_youtube(final_path, title, description, user_id)
        
        if not upload_result.get("success"):
            return {"success": False, "error": upload_result.get("error", "Upload failed")}

        # STEP 14: Save metadata
        logger.info("\n" + "=" * 80)
        logger.info("STEP 14/11: Save metadata to database")
        logger.info("=" * 80)
        
        metadata = {
            "user_id": user_id,
            "serial": serial,
            "drive_url": drive_url,
            "drive_file_id": file_id,
            "transcript": transcript[:500],
            "script": script[:500],
            "title": title,
            "description": description,
            "duration": round(duration, 2),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "uploaded": True,
            "processed_at": datetime.utcnow().isoformat()
        }
        await _save_metadata(db, metadata)

        # Success summary
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("\n" + "╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 30 + "✅ SUCCESS!" + " " * 36 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        logger.info(f"⏱️  Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        logger.info(f"📊 Serial: {serial}")
        logger.info(f"🎬 Title: {title}")
        logger.info(f"🔗 YouTube: {upload_result['video_url']}")
        logger.info("=" * 80)

        return {
            "success": True,
            "serial": serial,
            "title": title,
            "description": description,
            "duration": round(duration, 2),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "processing_time": round(elapsed, 1)
        }

    except Exception as e:
        logger.error("\n" + "╔" + "=" * 78 + "╗")
        logger.error("║" + " " * 30 + "❌ FATAL ERROR" + " " * 33 + "║")
        logger.error("╚" + "=" * 78 + "╝")
        logger.error(f"Error: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        return {"success": False, "error": str(e)}
    
    finally:
        logger.info("\n" + "=" * 80)
        logger.info("🧹 CLEANUP")
        logger.info("=" * 80)
        logger.info(f"   Removing temp directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        gc.collect()
        logger.info("   ✅ Cleanup complete")
        logger.info("=" * 80)


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request):
    """Process Google Drive video and upload to YouTube"""
    logger.info("\n" + "🌐" + "=" * 78 + "🌐")
    logger.info("API REQUEST RECEIVED")
    logger.info("🌐" + "=" * 78 + "🌐")
    
    try:
        data = await request.json()
        logger.info(f"Request data keys: {list(data.keys())}")
        
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        
        logger.info(f"User ID: {user_id}")
        logger.info(f"Drive URL: {drive_url[:100]}...")
        
        if not user_id:
            logger.error("❌ Missing user_id")
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "user_id required"}
            )

        if not drive_url or "drive.google.com" not in drive_url:
            logger.error("❌ Invalid Drive URL")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Valid Google Drive URL required"}
            )

        from Supermain import database_manager
        
        logger.info("Starting video processing...")
        result = await asyncio.wait_for(
            process_gdrive_video(drive_url, user_id, database_manager.db),
            timeout=600
        )
        
        logger.info(f"Processing complete: success={result.get('success')}")
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        logger.error("⏱️  REQUEST TIMEOUT (10 minutes)")
        return JSONResponse(
            status_code=408,
            content={"success": False, "error": "Processing timeout (10 minute limit). Try a shorter video."}
        )
    except Exception as e:
        logger.error(f"❌ API ERROR: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@router.get("/api/gdrive-reels/status")
async def status_endpoint(request: Request):
    """Get processing status and history"""
    try:
        user_id = request.query_params.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id required"}
            )
        
        from Supermain import database_manager
        
        serial = await _next_serial(database_manager.db, user_id)
        
        # Get history
        history = []
        try:
            async for doc in database_manager.db[COLLECTION].find(
                {"user_id": user_id}
            ).sort("serial", -1).limit(20):
                doc.pop("_id", None)
                history.append(doc)
        except:
            pass
        
        return JSONResponse(content={
            "success": True,
            "next_serial": serial,
            "total_processed": len(history),
            "history": history,
            "note": "Videos not stored in database - only metadata"
        })
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


__all__ = ["router"]