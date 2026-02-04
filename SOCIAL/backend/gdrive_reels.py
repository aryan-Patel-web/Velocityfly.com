"""
gdrive_reels.py - FIXED GROQ API VERSION
==========================================
✅ FIXED: Removed 'proxies' parameter from Groq client
✅ Groq Whisper API (fastest transcription)
✅ Multiple fallbacks for every step
✅ Works on Render 512MB free tier
✅ Extensive logging
==========================================
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
from typing import Optional
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
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "hi-IN-RaviNeural"]

BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
]

COLLECTION = "gdrive_reels_tracker"
PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════

def cleanup(*paths):
    """Cleanup files and GC"""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except:
            pass
    gc.collect()


def run_ffmpeg(cmd: list, timeout: int = 180, name: str = "FFmpeg") -> bool:
    """Run FFmpeg with logging"""
    logger.info(f"🎬 {name}...")
    try:
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout)
        if r.returncode == 0:
            logger.info(f"✅ {name} - SUCCESS")
            return True
        logger.error(f"❌ {name} - FAILED (exit {r.returncode})")
        return False
    except:
        return False


def extract_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID"""
    if not url:
        return None
    for pattern in [r'/file/d/([a-zA-Z0-9_-]{25,})', r'[?&]id=([a-zA-Z0-9_-]{25,})']:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


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
                        async for chunk in response.aiter_bytes(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
                        logger.info(f"✅ Downloaded: {os.path.getsize(dest)/(1024*1024):.1f} MB")
                        return True
        return False
    except:
        return False


# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def get_duration(path: str) -> float:
    """Get video duration"""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, timeout=15, text=True
        )
        if r.returncode == 0:
            duration = float(r.stdout.strip())
            logger.info(f"⏱️  Duration: {duration:.1f}s")
            return duration
        return 0.0
    except:
        return 0.0


async def extract_audio(video: str, audio: str) -> bool:
    """Extract audio to WAV"""
    return run_ffmpeg([
        "ffmpeg", "-i", video,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", audio
    ], timeout=60, name="Extract Audio")


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION - GROQ API (FIXED!)
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_groq_v3(audio_path: str) -> Optional[str]:
    """Method 1: Groq Whisper Large v3 (FIXED - no proxies!)"""
    if not GROQ_API_KEY:
        return None
    
    logger.info("🎙️  Method 1: Groq Whisper Large v3")
    
    try:
        from groq import Groq
        
        # FIXED: Don't pass proxies parameter!
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3",
                response_format="text",
                language="hi"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"✅ Method 1 SUCCESS: {len(transcription)} chars")
            return transcription.strip()
        
        return None
    except Exception as e:
        logger.error(f"❌ Method 1 failed: {e}")
        return None


async def transcribe_groq_turbo(audio_path: str) -> Optional[str]:
    """Method 2: Groq Whisper Turbo (FIXED - no proxies!)"""
    if not GROQ_API_KEY:
        return None
    
    logger.info("🎙️  Method 2: Groq Whisper Large v3 Turbo")
    
    try:
        from groq import Groq
        
        # FIXED: Don't pass proxies parameter!
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3-turbo",
                response_format="text",
                language="hi"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"✅ Method 2 SUCCESS: {len(transcription)} chars")
            return transcription.strip()
        
        return None
    except Exception as e:
        logger.error(f"❌ Method 2 failed: {e}")
        return None


async def transcribe_groq_distil(audio_path: str) -> Optional[str]:
    """Method 3: Groq Distil Whisper (FALLBACK - fastest!)"""
    if not GROQ_API_KEY:
        return None
    
    logger.info("🎙️  Method 3: Groq Distil Whisper (fastest)")
    
    try:
        from groq import Groq
        
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(audio_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=f,
                model="distil-whisper-large-v3-en",  # Fastest model
                response_format="text"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"✅ Method 3 SUCCESS: {len(transcription)} chars")
            return transcription.strip()
        
        return None
    except Exception as e:
        logger.error(f"❌ Method 3 failed: {e}")
        return None


async def transcribe_audio(audio_path: str) -> Optional[str]:
    """Transcribe with 3 Groq fallback methods"""
    logger.info("=" * 80)
    logger.info("📝 TRANSCRIBING AUDIO (GROQ WHISPER API)")
    logger.info("=" * 80)
    
    # Try all 3 methods
    for method in [transcribe_groq_v3, transcribe_groq_turbo, transcribe_groq_distil]:
        text = await method(audio_path)
        if text:
            logger.info("=" * 80)
            logger.info("✅ TRANSCRIPTION SUCCESS")
            logger.info("=" * 80)
            return text
        
        logger.info("   Trying fallback method...")
        await asyncio.sleep(1)
    
    logger.error("=" * 80)
    logger.error("❌ ALL TRANSCRIPTION METHODS FAILED")
    logger.error("   Check: 1) GROQ_SPEECH_API is set")
    logger.error("          2) Audio file has speech")
    logger.error("          3) Groq API quota not exceeded")
    logger.error("=" * 80)
    return None


# ═══════════════════════════════════════════════════════════════════════
# AI SCRIPT - 3 FALLBACKS
# ═══════════════════════════════════════════════════════════════════════

async def ai_groq_llama(transcript: str, words: int) -> Optional[dict]:
    """Method 1: Groq Llama 3.3 70B"""
    if not GROQ_API_KEY:
        return None
    
    logger.info("🤖 AI Method 1: Groq Llama 3.3 70B")
    
    try:
        from groq import Groq
        
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"""Rewrite this Hindi transcript into {words} words. Keep the same story.

Original: {transcript}

Return ONLY JSON:
{{"script":"","title":"","description":""}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            logger.info("✅ Groq Llama SUCCESS")
            return {
                "script": data.get("script", transcript)[:2000],
                "title": data.get("title", "Amazing Story 🔥")[:100],
                "description": data.get("description", transcript[:200])[:500]
            }
        
        return None
    except Exception as e:
        logger.error(f"❌ Groq Llama failed: {e}")
        return None


async def ai_mistral(transcript: str, words: int) -> Optional[dict]:
    """Method 2: Mistral AI"""
    if not MISTRAL_API_KEY:
        return None
    
    logger.info("🤖 AI Method 2: Mistral Small")
    
    try:
        prompt = f"""Rewrite in Hindi ({words} words): {transcript}
JSON: {{"script":"","title":"","description":""}}"""

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-small-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 800
                }
            )
            
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                match = re.search(r'\{.*\}', content, re.DOTALL)
                
                if match:
                    data = json.loads(match.group(0))
                    logger.info("✅ Mistral SUCCESS")
                    return {
                        "script": data.get("script", transcript)[:2000],
                        "title": data.get("title", "Amazing Story 🔥")[:100],
                        "description": data.get("description", transcript[:200])[:500]
                    }
        
        return None
    except Exception as e:
        logger.error(f"❌ Mistral failed: {e}")
        return None


async def ai_fallback(transcript: str, words: int) -> dict:
    """Method 3: Simple fallback (always works)"""
    logger.info("🤖 AI Method 3: Simple fallback")
    
    script_words = transcript.split()[:words]
    script = " ".join(script_words)
    
    return {
        "script": script,
        "title": f"{' '.join(script_words[:5])}... 🔥",
        "description": " ".join(script_words[:30])
    }


async def generate_script(transcript: str, duration: float) -> dict:
    """Generate script with 3 fallbacks"""
    logger.info("=" * 80)
    logger.info("🤖 AI SCRIPT GENERATION")
    logger.info("=" * 80)
    
    words = int(duration * 2.5)
    
    # Try all 3 methods
    for method in [ai_groq_llama, ai_mistral, ai_fallback]:
        result = await method(transcript, words)
        if result:
            logger.info("=" * 80)
            logger.info("✅ SCRIPT GENERATION COMPLETE")
            logger.info("=" * 80)
            return result
        
        await asyncio.sleep(0.5)
    
    # Should never reach here
    return await ai_fallback(transcript, words)


# ═══════════════════════════════════════════════════════════════════════
# VOICEOVER - 2 FALLBACKS
# ═══════════════════════════════════════════════════════════════════════

async def voiceover_edge_tts(script: str, output: str) -> bool:
    """Method 1: Edge TTS"""
    logger.info("🎙️  Voiceover Method 1: Edge TTS")
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        await edge_tts.Communicate(script[:2000], voice, rate="+5%").save(output)
        
        if os.path.exists(output) and os.path.getsize(output) > 1000:
            logger.info("✅ Edge TTS SUCCESS")
            return True
        
        return False
    except Exception as e:
        logger.error(f"❌ Edge TTS failed: {e}")
        return False


async def voiceover_gtts(script: str, output: str) -> bool:
    """Method 2: gTTS fallback"""
    logger.info("🎙️  Voiceover Method 2: gTTS")
    
    try:
        from gtts import gTTS
        
        tts = gTTS(text=script[:2000], lang='hi', slow=False)
        tts.save(output)
        
        if os.path.exists(output) and os.path.getsize(output) > 1000:
            logger.info("✅ gTTS SUCCESS")
            return True
        
        return False
    except Exception as e:
        logger.error(f"❌ gTTS failed: {e}")
        return False


async def generate_voiceover(script: str, output: str) -> bool:
    """Generate voiceover with 2 fallbacks"""
    logger.info("=" * 80)
    logger.info("🎙️  VOICEOVER GENERATION")
    logger.info("=" * 80)
    
    for method in [voiceover_edge_tts, voiceover_gtts]:
        if await method(script, output):
            logger.info("=" * 80)
            logger.info("✅ VOICEOVER COMPLETE")
            logger.info("=" * 80)
            return True
        
        await asyncio.sleep(0.5)
    
    logger.error("❌ ALL VOICEOVER METHODS FAILED")
    return False


# ═══════════════════════════════════════════════════════════════════════
# VIDEO COMPOSITING
# ═══════════════════════════════════════════════════════════════════════

def generate_srt(script: str, duration: float) -> str:
    """Generate SRT captions"""
    words = script.split()
    phrases = [" ".join(words[i:i+4]) for i in range(0, len(words), 4) if words[i:i+4]]
    
    if not phrases:
        return ""
    
    time_per = duration / len(phrases)
    blocks = []
    
    for i, phrase in enumerate(phrases):
        t0, t1 = i * time_per, (i + 1) * time_per
        h0, m0, s0 = int(t0//3600), int((t0%3600)//60), t0%60
        h1, m1, s1 = int(t1//3600), int((t1%3600)//60), t1%60
        
        blocks.append(
            f"{i+1}\n"
            f"{h0:02d}:{m0:02d}:{s0:06.3f}".replace(".", ",") + " --> " +
            f"{h1:02d}:{m1:02d}:{s1:06.3f}".replace(".", ",") + "\n"
            f"{phrase}\n"
        )
    
    return "\n".join(blocks)


async def remove_audio(vin: str, vout: str) -> bool:
    """Remove audio from video"""
    return run_ffmpeg([
        "ffmpeg", "-i", vin, "-c:v", "copy", "-an", "-y", vout
    ], timeout=60, name="Remove Original Audio")


async def download_bgm(output: str) -> bool:
    """Download BGM"""
    logger.info("🎵 Downloading BGM...")
    
    try:
        url = random.choice(BGM_URLS)
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            async with client.stream("GET", url) as r:
                if r.status_code == 200:
                    with open(output, 'wb') as f:
                        async for chunk in r.aiter_bytes(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    logger.info("✅ BGM downloaded")
                    return True
        
        return False
    except:
        return False


async def create_final(silent: str, voice: str, srt: str, bgm: Optional[str], output: str) -> bool:
    """Create final video"""
    logger.info("=" * 80)
    logger.info("✨ CREATING FINAL VIDEO")
    logger.info("=" * 80)
    
    captioned = output.replace(".mp4", "_cap.mp4")
    srt_esc = srt.replace("\\", "\\\\").replace(":", "\\:")
    
    logger.info("   Step 1/2: Burning captions...")
    if not run_ffmpeg([
        "ffmpeg", "-i", silent,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial Black,FontSize=28,PrimaryColour=&H00FFFF00,Bold=1,Outline=2,Alignment=2,MarginV=60'",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-y", captioned
    ], timeout=180, name="Burn Captions"):
        return False
    
    cleanup(silent)
    
    logger.info("   Step 2/2: Mixing audio...")
    if bgm and os.path.exists(bgm):
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voice, "-i", bgm,
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.06[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=120, name="Mix Audio")
    else:
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voice,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=90, name="Add Voiceover")
    
    cleanup(captioned)
    
    if success:
        logger.info("=" * 80)
        logger.info(f"✅ FINAL VIDEO READY: {os.path.getsize(output)/(1024*1024):.1f} MB")
        logger.info("=" * 80)
    
    return success


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_youtube(video: str, title: str, desc: str, user_id: str) -> dict:
    """Upload to YouTube"""
    logger.info("=" * 80)
    logger.info("📤 UPLOADING TO YOUTUBE")
    logger.info("=" * 80)
    
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
            description=f"{desc}\n\n#Shorts #Viral #Hindi",
            video_url=video
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            logger.info("=" * 80)
            logger.info(f"✅ UPLOADED: https://youtube.com/shorts/{video_id}")
            logger.info("=" * 80)
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
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_video(drive_url: str, user_id: str, task_id: str):
    """Main processing pipeline"""
    temp_dir = None
    start = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting..."
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"[{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="gdrive_reel_")
        logger.info(f"📁 Temp dir: {temp_dir}")
        
        # Extract file ID
        update(5, "Extracting file ID...")
        file_id = extract_file_id(drive_url)
        if not file_id:
            raise ValueError("Invalid Google Drive URL")
        logger.info(f"   File ID: {file_id}")
        
        # Download
        update(10, "Downloading video from Google Drive...")
        video = os.path.join(temp_dir, "video.mp4")
        if not await download_video(file_id, video):
            raise Exception("Download failed")
        
        # Get duration
        update(20, "Analyzing video...")
        duration = await get_duration(video)
        if duration <= 0:
            raise ValueError("Invalid video")
        
        # Extract audio
        update(25, "Extracting audio...")
        audio = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video, audio):
            raise Exception("Audio extraction failed")
        
        # Transcribe
        update(30, "Transcribing audio with Groq Whisper API (10-20s)...")
        transcript = await transcribe_audio(audio)
        cleanup(audio)
        
        if not transcript:
            raise Exception("Transcription failed - no speech detected in video")
        
        logger.info(f"   Transcript: {transcript[:100]}...")
        
        # Generate script
        update(50, "Generating viral script...")
        meta = await generate_script(transcript, duration)
        logger.info(f"   Title: {meta['title']}")
        
        # Voiceover
        update(60, "Generating voiceover...")
        voice = os.path.join(temp_dir, "voice.mp3")
        if not await generate_voiceover(meta["script"], voice):
            raise Exception("Voiceover failed")
        
        # Remove audio
        update(70, "Removing original audio...")
        silent = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(video, silent):
            raise Exception("Remove audio failed")
        cleanup(video)
        
        # Captions
        update(75, "Creating captions...")
        srt_path = os.path.join(temp_dir, "subs.srt")
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_srt(meta["script"], duration))
        
        # BGM
        update(80, "Downloading background music...")
        bgm = os.path.join(temp_dir, "bgm.mp3")
        bgm_ok = await download_bgm(bgm)
        
        # Final video
        update(85, "Creating final video...")
        final = os.path.join(temp_dir, "final.mp4")
        if not await create_final(silent, voice, srt_path, bgm if bgm_ok else None, final):
            raise Exception("Final video creation failed")
        
        cleanup(voice, srt_path, bgm)
        
        # Upload
        update(90, "Uploading to YouTube...")
        result = await upload_youtube(final, meta["title"], meta["description"], user_id)
        
        if not result.get("success"):
            raise Exception(result.get("error", "Upload failed"))
        
        # Success
        elapsed = (datetime.now() - start).total_seconds()
        
        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   URL: {result['video_url']}")
        logger.info("=" * 80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Successfully uploaded!",
            "result": {
                "success": True,
                "title": meta["title"],
                "description": meta["description"],
                "video_id": result["video_id"],
                "video_url": result["video_url"],
                "processing_time": round(elapsed, 1),
                "transcript": transcript[:200]
            }
        }
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ PROCESSING FAILED: {e}")
        logger.error("=" * 80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "message": str(e),
            "error": str(e)
        }
    
    finally:
        if temp_dir:
            logger.info("🧹 Cleaning up temp directory...")
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("✅ Cleanup complete")
            except:
                pass
        gc.collect()


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request, background_tasks: BackgroundTasks):
    """Process Google Drive video"""
    logger.info("🌐 API REQUEST: /api/gdrive-reels/process")
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        
        if not user_id:
            return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
        if not drive_url or "drive.google.com" not in drive_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Valid Google Drive URL required"})
        
        task_id = str(uuid.uuid4())
        
        background_tasks.add_task(process_video, drive_url, user_id, task_id)
        
        logger.info(f"✅ Task started: {task_id}")
        
        return JSONResponse(content={
            "success": True,
            "task_id": task_id,
            "message": "Processing started"
        })
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.get("/api/gdrive-reels/status/{task_id}")
async def status_endpoint(task_id: str):
    """Check status"""
    status = PROCESSING_STATUS.get(task_id)
    
    if not status:
        return JSONResponse(status_code=404, content={"success": False, "error": "Task not found"})
    
    return JSONResponse(content=status)


@router.get("/api/gdrive-reels/health")
async def health_endpoint():
    """Health check"""
    return JSONResponse(content={
        "status": "ok",
        "groq_configured": bool(GROQ_API_KEY),
        "method": "Groq Whisper API (no local model)"
    })


__all__ = ["router"]