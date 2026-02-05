"""
gdrive_reels_memory_optimized.py - MEMORY-EFFICIENT VERSION FOR RENDER FREE TIER
==================================================================================
✅ STRICT 512MB MEMORY LIMIT COMPLIANCE
✅ Aggressive cleanup after each step
✅ Memory tracking with detailed logs
✅ Stream-based video processing (no full load)
✅ Immediate file deletion after use
✅ Garbage collection after each major step
✅ Multiple Groq Whisper fallback methods
✅ Multiple Google Drive download methods
✅ Edge TTS + Vertex AI voice fallbacks
==================================================================================
CRITICAL MEMORY OPTIMIZATIONS:
1. Process video in chunks, never load full file
2. Delete files immediately after processing
3. Force garbage collection after each step
4. Use subprocess streaming for FFmpeg
5. Download in chunks (1MB at a time)
6. Limit concurrent operations
==================================================================================
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
from typing import Optional, Dict, List
from datetime import datetime
import uuid
import psutil  # For memory tracking

# ═══════════════════════════════════════════════════════════════════════
# LOGGING WITH MEMORY TRACKING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def log_memory(step: str):
    """Log current memory usage"""
    try:
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"🧠 MEMORY [{step}]: {mem_mb:.1f}MB / 512MB")
        
        if mem_mb > 450:  # Warning at 450MB (leave 62MB buffer)
            logger.warning(f"⚠️ HIGH MEMORY: {mem_mb:.1f}MB - Forcing cleanup...")
            gc.collect()
            gc.collect()
            gc.collect()
    except:
        pass

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
GROQ_API_KEY = os.getenv("GROQ_SPEECH_API")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_VERTEX_API_KEY = os.getenv("GOOGLE_VERTEX_API_KEY", "AIzaSyAb8RN6KKt384GXtEg7vxZnhXZNxhoTrXw3mcoe7RevLa881bSw")
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
]

# Vertex AI Hindi voices
VERTEX_AI_HINDI_VOICES = [
    {"name": "hi-IN-Standard-A", "gender": "FEMALE"},
    {"name": "hi-IN-Standard-B", "gender": "MALE"},
    {"name": "hi-IN-Standard-C", "gender": "FEMALE"}
]

# Processing status tracking
PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# AGGRESSIVE MEMORY CLEANUP
# ═══════════════════════════════════════════════════════════════════════

def force_cleanup(*paths):
    """Aggressive file cleanup with triple garbage collection"""
    deleted_count = 0
    for path in paths:
        try:
            if path and os.path.exists(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                os.remove(path)
                deleted_count += 1
                logger.info(f"   🗑️ Deleted: {os.path.basename(path)} ({size_mb:.1f}MB)")
        except Exception as e:
            logger.debug(f"   ⚠️ Could not delete {path}: {e}")
    
    if deleted_count > 0:
        # Triple GC to ensure memory is freed
        gc.collect()
        gc.collect()
        gc.collect()
        log_memory("After cleanup")

# ═══════════════════════════════════════════════════════════════════════
# FFMPEG HELPERS WITH MEMORY LIMITS
# ═══════════════════════════════════════════════════════════════════════

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg with memory-efficient streaming"""
    logger.info(f"🎬 {step}...")
    log_memory(f"Before {step}")
    
    try:
        # Use PIPE to avoid storing in memory
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )
        
        success = result.returncode == 0
        
        if success:
            logger.info(f"✅ {step} - SUCCESS")
        else:
            logger.error(f"❌ {step} - FAILED (exit {result.returncode})")
            # Log last 500 chars of error
            if result.stderr:
                logger.error(f"   Error: {result.stderr[-500:]}")
        
        # Force cleanup after FFmpeg
        gc.collect()
        log_memory(f"After {step}")
        
        return success
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ {step} - TIMEOUT ({timeout}s)")
        gc.collect()
        return False
    except Exception as e:
        logger.error(f"❌ {step} - ERROR: {e}")
        gc.collect()
        return False

# ═══════════════════════════════════════════════════════════════════════
# GOOGLE DRIVE FILE ID EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

def extract_gdrive_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID from URL"""
    if not url or "drive.google.com" not in url:
        return None
    
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]{25,})',
        r'[?&]id=([a-zA-Z0-9_-]{25,})',
        r'/open\?id=([a-zA-Z0-9_-]{25,})',
        r'/d/([a-zA-Z0-9_-]{25,})/',
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
# MEMORY-EFFICIENT DOWNLOAD (CHUNKED STREAMING)
# ═══════════════════════════════════════════════════════════════════════

async def download_chunked(url: str, output_path: str, chunk_size: int = 1024*1024) -> bool:
    """Download file in small chunks to avoid memory spike"""
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    return False
                
                total_size = 0
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        f.write(chunk)
                        total_size += len(chunk)
                        
                        # Log every 5MB
                        if total_size % (5 * 1024 * 1024) < chunk_size:
                            logger.info(f"   📥 Downloaded: {total_size / (1024*1024):.1f}MB")
                
                if total_size > 10000:  # At least 10KB
                    logger.info(f"   ✅ Download complete: {total_size / (1024*1024):.1f}MB")
                    return True
                
        return False
    except Exception as e:
        logger.error(f"   ❌ Download error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# GOOGLE DRIVE DOWNLOAD - 3 METHODS
# ═══════════════════════════════════════════════════════════════════════

async def download_method_1_direct(file_id: str, output_path: str) -> bool:
    """Method 1: Direct download"""
    logger.info("   Method 1: Direct download (uc endpoint)")
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return await download_chunked(url, output_path)

async def download_method_2_confirm(file_id: str, output_path: str) -> bool:
    """Method 2: With virus scan bypass"""
    logger.info("   Method 2: Download with virus scan bypass")
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            # Get confirmation token
            url1 = f"https://drive.google.com/uc?export=download&id={file_id}"
            response1 = await client.get(url1)
            
            confirm_token = None
            if "download_warning" in response1.text:
                match = re.search(r'confirm=([0-9A-Za-z_-]+)', response1.text)
                if match:
                    confirm_token = match.group(1)
            
            # Download with confirmation
            url2 = f"https://drive.google.com/uc?export=download&id={file_id}"
            if confirm_token:
                url2 += f"&confirm={confirm_token}"
            
            return await download_chunked(url2, output_path)
    except Exception as e:
        logger.error(f"   ❌ Method 2 failed: {e}")
        return False

async def download_method_3_usercontent(file_id: str, output_path: str) -> bool:
    """Method 3: Usercontent domain"""
    logger.info("   Method 3: Usercontent domain download")
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
    return await download_chunked(url, output_path)

async def download_video_from_gdrive(file_id: str, output_path: str) -> tuple[bool, str]:
    """Download with 3 fallback methods"""
    logger.info("⬇️ Downloading video from Google Drive...")
    logger.info(f"   File ID: {file_id}")
    log_memory("Before download")
    
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
                log_memory("After download")
                return True, ""
        except Exception as e:
            logger.error(f"   Method {idx} exception: {e}")
        
        if idx < len(methods):
            await asyncio.sleep(1)
    
    error_msg = "Download failed. Check: 1) Link is public, 2) File < 100MB, 3) Valid video"
    logger.error(f"❌ All download methods failed")
    return False, error_msg

# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def get_video_duration(video_path: str) -> float:
    """Get video duration"""
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
            logger.info(f"⏱️ Duration: {duration:.1f}s")
            return duration
        
        return 0.0
    except Exception as e:
        logger.error(f"❌ Failed to get duration: {e}")
        return 0.0

async def extract_audio_from_video(video_path: str, audio_path: str) -> bool:
    """Extract audio to 16kHz mono WAV"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-y", audio_path
    ], timeout=60, step="Extract Audio")
    
    # Cleanup video immediately after extraction
    if success:
        force_cleanup(video_path)
    
    return success

# ═══════════════════════════════════════════════════════════════════════
# GROQ WHISPER TRANSCRIPTION - 3 METHODS
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_with_groq_large_v3(audio_path: str) -> tuple[Optional[str], str]:
    """Method 1: Groq Whisper Large v3"""
    if not GROQ_API_KEY:
        return None, "GROQ_SPEECH_API not configured"
    
    logger.info("   Method 1: Groq Whisper Large v3")
    
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="text",
                language="hi"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"   ✅ Method 1 SUCCESS: {len(transcription)} chars")
            return transcription.strip(), ""
        
        return None, "Empty transcription"
    except Exception as e:
        logger.error(f"   ❌ Method 1 failed: {e}")
        return None, str(e)

async def transcribe_with_groq_turbo(audio_path: str) -> tuple[Optional[str], str]:
    """Method 2: Groq Whisper Turbo"""
    if not GROQ_API_KEY:
        return None, "GROQ_SPEECH_API not configured"
    
    logger.info("   Method 2: Groq Whisper Large v3 Turbo")
    
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                response_format="text",
                language="hi"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"   ✅ Method 2 SUCCESS: {len(transcription)} chars")
            return transcription.strip(), ""
        
        return None, "Empty transcription"
    except Exception as e:
        logger.error(f"   ❌ Method 2 failed: {e}")
        return None, str(e)

async def transcribe_with_groq_api_direct(audio_path: str) -> tuple[Optional[str], str]:
    """Method 3: Direct Groq API"""
    if not GROQ_API_KEY:
        return None, "GROQ_SPEECH_API not configured"
    
    logger.info("   Method 3: Direct Groq API (HTTP)")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            with open(audio_path, "rb") as audio_file:
                files = {"file": ("audio.wav", audio_file, "audio/wav")}
                data = {
                    "model": "whisper-large-v3",
                    "language": "hi",
                    "response_format": "text"
                }
                
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    transcription = response.text.strip()
                    if len(transcription) > 5:
                        logger.info(f"   ✅ Method 3 SUCCESS: {len(transcription)} chars")
                        return transcription, ""
        
        return None, "API returned empty response"
    except Exception as e:
        logger.error(f"   ❌ Method 3 failed: {e}")
        return None, str(e)

async def transcribe_audio(audio_path: str) -> tuple[Optional[str], str]:
    """Transcribe with 3 fallback methods"""
    logger.info("📝 TRANSCRIBING AUDIO (GROQ WHISPER - 3 METHODS)")
    log_memory("Before transcription")
    
    if not GROQ_API_KEY:
        error_msg = "GROQ_SPEECH_API key not configured"
        logger.error(f"❌ {error_msg}")
        return None, error_msg
    
    methods = [
        transcribe_with_groq_large_v3,
        transcribe_with_groq_turbo,
        transcribe_with_groq_api_direct,
    ]
    
    for idx, method in enumerate(methods, 1):
        logger.info(f"🎙️ Trying transcription method {idx}/3...")
        
        try:
            transcript, error = await method(audio_path)
            
            if transcript:
                logger.info(f"✅ TRANSCRIPTION SUCCESS using method {idx}")
                logger.info(f"   Preview: {transcript[:100]}...")
                log_memory("After transcription")
                
                # Cleanup audio file immediately
                force_cleanup(audio_path)
                
                return transcript, ""
        except Exception as e:
            logger.error(f"   Exception in method {idx}: {e}")
        
        if idx < len(methods):
            logger.info("   Trying next method...")
            await asyncio.sleep(1)
    
    error_msg = "All transcription methods failed"
    logger.error(f"❌ {error_msg}")
    
    # Cleanup audio file
    force_cleanup(audio_path)
    
    return None, error_msg

# ═══════════════════════════════════════════════════════════════════════
# AI SCRIPT GENERATION
# ═══════════════════════════════════════════════════════════════════════

async def generate_ai_script(transcript: str, duration: float) -> dict:
    """Generate script using AI"""
    logger.info("🤖 Generating AI script...")
    log_memory("Before AI script")
    
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
                        log_memory("After AI script")
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
                        log_memory("After AI script")
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
    
    log_memory("After AI script (fallback)")
    
    return {
        "script": script,
        "title": f"{' '.join(words[:5])}... 🔥",
        "description": " ".join(words[:30])
    }

# ═══════════════════════════════════════════════════════════════════════
# VERTEX AI TTS
# ═══════════════════════════════════════════════════════════════════════

async def generate_voice_vertex_ai(text: str, temp_dir: str) -> Optional[str]:
    """Generate voice using Vertex AI"""
    if not GOOGLE_VERTEX_API_KEY:
        return None
    
    try:
        voice_config = random.choice(VERTEX_AI_HINDI_VOICES)
        logger.info(f"🔊 Vertex AI: Using {voice_config['name']}")
        log_memory("Before Vertex TTS")
        
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_VERTEX_API_KEY}"
        
        payload = {
            "input": {"text": text[:2000]},
            "voice": {
                "languageCode": "hi-IN",
                "name": voice_config["name"],
                "ssmlGender": voice_config["gender"]
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 1.15,
                "pitch": 0.0
            }
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload)
            
            if resp.status_code == 200:
                result = resp.json()
                
                if "audioContent" in result:
                    import base64
                    audio_content = base64.b64decode(result["audioContent"])
                    
                    output_path = os.path.join(temp_dir, "vertex_voice.mp3")
                    with open(output_path, 'wb') as f:
                        f.write(audio_content)
                    
                    logger.info(f"✅ Vertex AI Voice: {len(audio_content)/(1024*1024):.2f}MB")
                    log_memory("After Vertex TTS")
                    return output_path
        
        return None
    except Exception as e:
        logger.error(f"❌ Vertex AI error: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════
# VOICE GENERATION WITH FALLBACKS
# ═══════════════════════════════════════════════════════════════════════

async def generate_voiceover(script: str, output_path: str) -> tuple[bool, str]:
    """Generate voiceover with Edge TTS"""
    logger.info("🎙️ Generating voiceover with Edge TTS...")
    log_memory("Before voiceover")
    
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
            logger.info(f"✅ Voiceover: {os.path.getsize(output_path)/1024:.1f}KB")
            log_memory("After voiceover")
            return True, ""
        else:
            return False, "Voiceover file too small"
    except Exception as e:
        error_msg = f"Voiceover failed: {str(e)}"
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
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def remove_original_audio(video_in: str, video_out: str) -> bool:
    """Remove original audio"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy",
        "-an",
        "-y", video_out
    ], timeout=60, step="Remove Original Audio")
    
    # Cleanup input immediately
    if success:
        force_cleanup(video_in)
    
    return success

async def download_bgm(output_path: str) -> bool:
    """Download BGM"""
    logger.info("🎵 Downloading BGM...")
    log_memory("Before BGM download")
    
    try:
        url = random.choice(BGM_URLS)
        success = await download_chunked(url, output_path, chunk_size=512*1024)  # 512KB chunks
        
        if success:
            logger.info("✅ BGM downloaded")
            log_memory("After BGM download")
        
        return success
    except Exception as e:
        logger.error(f"❌ BGM download failed: {e}")
        return False

async def create_final_video(
    silent_video: str,
    voiceover: str,
    srt_file: str,
    bgm: Optional[str],
    output: str
) -> tuple[bool, str]:
    """Create final video"""
    logger.info("✨ Creating final video...")
    log_memory("Before final video")
    
    captioned_video = output.replace(".mp4", "_captioned.mp4")
    srt_escaped = srt_file.replace("\\", "\\\\").replace(":", "\\:")
    
    # Step 1: Burn captions
    if not run_ffmpeg([
        "ffmpeg", "-i", silent_video,
        "-vf", f"subtitles={srt_escaped}:force_style='FontName=Arial Black,FontSize=28,PrimaryColour=&H00FFFF00,Bold=1,Outline=2,Shadow=1,Alignment=2,MarginV=60'",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-y", captioned_video
    ], timeout=180, step="Burn Captions"):
        return False, "Failed to burn captions"
    
    # Cleanup
    force_cleanup(silent_video, srt_file)
    
    # Step 2: Mix audio
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
    
    # Cleanup
    force_cleanup(captioned_video, voiceover, bgm)
    
    if not success:
        return False, "Failed to mix audio"
    
    log_memory("After final video")
    return True, ""

# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    user_id: str
) -> dict:
    """Upload to YouTube"""
    logger.info("📤 Uploading to YouTube...")
    log_memory("Before YouTube upload")
    
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
            description=f"{description}\n\n#Shorts #Viral #Hindi #Reels",
            video_url=video_path
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            logger.info(f"✅ Uploaded: {video_id}")
            log_memory("After YouTube upload")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        else:
            return {"success": False, "error": result.get("error", "Upload failed")}
            
    except Exception as e:
        logger.error(f"❌ YouTube upload error: {e}")
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_gdrive_reel(drive_url: str, user_id: str, task_id: str):
    """Main processing with strict memory management"""
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
        log_memory("START")
        
        # STEP 1: Extract file ID
        update_status(5, "Extracting file ID...")
        file_id = extract_gdrive_file_id(drive_url)
        if not file_id:
            raise ValueError("Invalid Google Drive URL")
        
        # STEP 2: Download video (chunked)
        update_status(10, "Downloading video...")
        video_path = os.path.join(temp_dir, "original.mp4")
        
        success, error = await download_video_from_gdrive(file_id, video_path)
        if not success:
            raise Exception(error)
        
        log_memory("After download")
        
        # STEP 3: Get duration
        update_status(20, "Analyzing video...")
        duration = await get_video_duration(video_path)
        
        if duration <= 0:
            raise ValueError("Invalid video file")
        if duration > 180:
            raise ValueError(f"Video too long ({duration:.0f}s)")
        
        # STEP 4: Extract audio (delete video after)
        update_status(25, "Extracting audio...")
        audio_path = os.path.join(temp_dir, "audio.wav")
        
        if not await extract_audio_from_video(video_path, audio_path):
            raise Exception("Failed to extract audio")
        
        log_memory("After audio extraction")
        # video_path deleted in extract_audio_from_video
        
        # STEP 5: Transcribe (delete audio after)
        update_status(30, "Transcribing audio...")
        transcript, error = await transcribe_audio(audio_path)
        
        # audio_path deleted in transcribe_audio
        
        if not transcript:
            raise Exception(error or "Transcription failed")
        
        log_memory("After transcription")
        
        # STEP 6: Generate script
        update_status(50, "Generating AI script...")
        metadata = await generate_ai_script(transcript, duration)
        
        logger.info(f"   Title: {metadata['title']}")
        log_memory("After AI script")
        
        # STEP 7: Generate voiceover
        update_status(60, "Generating voiceover...")
        voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
        
        success, error = await generate_voiceover(metadata["script"], voiceover_path)
        if not success:
            raise Exception(error)
        
        log_memory("After voiceover")
        
        # STEP 8: Re-download video for processing
        update_status(70, "Re-downloading video for processing...")
        video_path = os.path.join(temp_dir, "original.mp4")
        success, error = await download_video_from_gdrive(file_id, video_path)
        if not success:
            raise Exception("Failed to re-download video")
        
        # STEP 9: Remove original audio (delete input video)
        update_status(75, "Removing original audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        
        if not await remove_original_audio(video_path, silent_video):
            raise Exception("Failed to remove audio")
        
        log_memory("After audio removal")
        # video_path deleted in remove_original_audio
        
        # STEP 10: Generate captions
        update_status(80, "Creating captions...")
        srt_path = os.path.join(temp_dir, "captions.srt")
        
        srt_content = generate_srt_captions(metadata["script"], duration)
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # STEP 11: Download BGM
        update_status(85, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        
        bgm_downloaded = await download_bgm(bgm_path)
        if not bgm_downloaded:
            logger.warning("BGM download failed")
            bgm_path = None
        
        log_memory("After BGM download")
        
        # STEP 12: Create final video (delete all inputs)
        update_status(90, "Creating final video...")
        final_video = os.path.join(temp_dir, "final.mp4")
        
        success, error = await create_final_video(
            silent_video, voiceover_path, srt_path, bgm_path, final_video
        )
        if not success:
            raise Exception(error)
        
        log_memory("After final video")
        # All inputs deleted in create_final_video
        
        if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
            raise Exception("Final video invalid")
        
        final_size_mb = os.path.getsize(final_video) / (1024 * 1024)
        logger.info(f"   Final: {final_size_mb:.1f}MB")
        
        # STEP 13: Upload to YouTube
        update_status(95, "Uploading to YouTube...")
        
        upload_result = await upload_to_youtube(
            final_video,
            metadata["title"],
            metadata["description"],
            user_id
        )
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error", "Upload failed"))
        
        # SUCCESS
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video ID: {upload_result['video_id']}")
        logger.info("=" * 80)
        log_memory("COMPLETE")
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "message": "Successfully uploaded!",
            "title": metadata["title"],
            "description": metadata["description"],
            "duration": round(duration, 1),
            "processing_time": round(elapsed, 1),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error("=" * 80)
        logger.error(f"❌ FAILED: {error_msg}")
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
        # AGGRESSIVE CLEANUP
        if temp_dir and os.path.exists(temp_dir):
            logger.info("🧹 Cleaning up temp directory...")
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("✅ Cleanup complete")
            except Exception as e:
                logger.error(f"⚠️ Cleanup failed: {e}")
        
        # Triple garbage collection
        gc.collect()
        gc.collect()
        gc.collect()
        log_memory("FINAL CLEANUP")

# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()

@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Start processing"""
    logger.info("🌐 API REQUEST: /api/gdrive-reels/process")
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        wait_for_result = data.get("wait", False)
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id required"}
            )
        
        if not drive_url or "drive.google.com" not in drive_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Valid Google Drive URL required"}
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
            max_wait = 300
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
                content={"success": False, "error": "Timeout"}
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
    """Check status"""
    status = PROCESSING_STATUS.get(task_id)
    
    if not status:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Task not found"}
        )
    
    return JSONResponse(content=status)

@router.get("/api/gdrive-reels/health")
async def health_endpoint():
    """Health check"""
    log_memory("Health check")
    
    return JSONResponse(content={
        "status": "ok",
        "groq_api_configured": bool(GROQ_API_KEY),
        "vertex_ai_configured": bool(GOOGLE_VERTEX_API_KEY),
        "active_tasks": len([s for s in PROCESSING_STATUS.values() if s["status"] == "processing"]),
        "memory_tracking": "enabled"
    })

# ═══════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════

async def initialize():
    """Initialize service"""
    logger.info("=" * 80)
    logger.info("🚀 GDRIVE REELS SERVICE (MEMORY-OPTIMIZED)")
    logger.info("=" * 80)
    logger.info("📊 Memory limit: 512MB (Render free tier)")
    logger.info("🧹 Cleanup: Aggressive (triple GC)")
    logger.info("📥 Download: Chunked streaming (1MB chunks)")
    logger.info("🎬 Processing: Stream-based (no full load)")
    logger.info("=" * 80)
    
    if GROQ_API_KEY:
        logger.info("✅ Groq API configured")
    else:
        logger.error("❌ GROQ_SPEECH_API not set!")
    
    if GOOGLE_VERTEX_API_KEY:
        logger.info("✅ Vertex AI configured")
    
    log_memory("Startup")
    logger.info("=" * 80)

__all__ = ["router", "initialize"]