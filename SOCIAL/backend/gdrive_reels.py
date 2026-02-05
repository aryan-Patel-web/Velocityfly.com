"""
gdrive_reels.py - FIXED ERROR HANDLING
========================================
✅ Proper error messages (no "undefined")
✅ Better validation
✅ Detailed logging
✅ Direct YouTube upload
========================================
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
from typing import Optional
from datetime import datetime
import traceback

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
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "hi-IN-RaviNeural"]

BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
]

# ═══════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════

def cleanup(*paths):
    """Cleanup files"""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except:
            pass
    gc.collect()


def run_ffmpeg(cmd: list, timeout: int = 180) -> bool:
    """Run FFmpeg"""
    try:
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout)
        return r.returncode == 0
    except Exception as e:
        logger.error(f"FFmpeg error: {e}")
        return False


def extract_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID"""
    if not url:
        logger.error("Empty URL provided")
        return None
    
    logger.info(f"Extracting file ID from: {url[:100]}...")
    
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]{25,})',
        r'[?&]id=([a-zA-Z0-9_-]{25,})',
        r'/open\?id=([a-zA-Z0-9_-]{25,})'
    ]
    
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            file_id = m.group(1)
            logger.info(f"✅ File ID extracted: {file_id}")
            return file_id
    
    logger.error("Could not extract file ID from URL")
    return None


# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════

async def download_video(file_id: str, dest: str) -> bool:
    """Download from Google Drive"""
    logger.info("⬇️  Downloading from Google Drive...")
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            logger.info("   Making HTTP request...")
            async with client.stream("GET", url) as r:
                logger.info(f"   Status: {r.status_code}")
                
                if r.status_code != 200:
                    logger.error(f"   HTTP error: {r.status_code}")
                    return False
                
                with open(dest, 'wb') as f:
                    async for chunk in r.aiter_bytes(chunk_size=1024*1024):
                        f.write(chunk)
                
                if os.path.exists(dest):
                    size = os.path.getsize(dest)
                    size_mb = size / (1024 * 1024)
                    logger.info(f"✅ Downloaded: {size_mb:.1f} MB")
                    
                    if size < 10000:
                        logger.error("File too small (< 10KB)")
                        return False
                    
                    return True
                else:
                    logger.error("Downloaded file not found")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        logger.error(traceback.format_exc())
        return False


# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def get_duration(path: str) -> float:
    """Get duration"""
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
        else:
            logger.error(f"ffprobe failed: {r.stderr}")
            return 0.0
    except Exception as e:
        logger.error(f"Duration check failed: {e}")
        return 0.0


async def extract_audio(video: str, audio: str) -> bool:
    """Extract audio"""
    logger.info("🔊 Extracting audio...")
    success = run_ffmpeg([
        "ffmpeg", "-i", video,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", audio
    ], timeout=60)
    
    if success and os.path.exists(audio):
        logger.info("✅ Audio extracted")
        return True
    else:
        logger.error("❌ Audio extraction failed")
        return False


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_audio(audio_path: str) -> Optional[str]:
    """Transcribe with Groq"""
    logger.info("📝 Transcribing with Groq Whisper...")
    
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_SPEECH_API environment variable not set")
        return None
    
    try:
        from groq import Groq
        
        logger.info("   Initializing Groq client...")
        client = Groq(api_key=GROQ_API_KEY)
        
        logger.info("   Sending audio to Groq API...")
        with open(audio_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3",
                response_format="text",
                language="hi"
            )
        
        if transcription and len(transcription) > 5:
            logger.info(f"✅ Transcription: {len(transcription)} chars")
            logger.info(f"   Preview: {transcription[:100]}...")
            return transcription.strip()
        else:
            logger.error("❌ Transcription returned empty or too short")
            return None
        
    except ImportError:
        logger.error("❌ groq library not installed. Run: pip install groq")
        return None
    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        logger.error(traceback.format_exc())
        return None


# ═══════════════════════════════════════════════════════════════════════
# AI SCRIPT
# ═══════════════════════════════════════════════════════════════════════

async def generate_script(transcript: str, duration: float) -> dict:
    """Generate script"""
    logger.info("🤖 Generating AI script...")
    
    words = int(duration * 2.5)
    
    # Try Groq Llama
    if GROQ_API_KEY:
        try:
            from groq import Groq
            
            client = Groq(api_key=GROQ_API_KEY)
            
            prompt = f"""Rewrite this Hindi transcript into {words} words.

Original: {transcript}

Return ONLY JSON:
{{"script":"","title":"","description":"","keywords":[],"tags":[]}}"""

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
                logger.info("✅ AI script generated")
                
                return {
                    "script": data.get("script", transcript)[:2000],
                    "title": data.get("title", "Amazing Story 🔥")[:100],
                    "description": data.get("description", transcript[:200])[:500],
                    "keywords": (data.get("keywords", []) + ["hindi"]*15)[:15],
                    "tags": (data.get("tags", []) + ["#Shorts"]*6)[:6]
                }
        except Exception as e:
            logger.warning(f"Groq Llama failed: {e}")
    
    # Fallback
    logger.info("Using fallback script generation")
    script_words = transcript.split()[:words]
    script = " ".join(script_words)
    
    return {
        "script": script,
        "title": f"{' '.join(script_words[:5])}... 🔥",
        "description": " ".join(script_words[:30]),
        "keywords": ["hindi", "story", "shorts"] * 5,
        "tags": ["#Shorts", "#Hindi", "#Viral", "#Story", "#Reel", "#Trending"]
    }


# ═══════════════════════════════════════════════════════════════════════
# VOICEOVER
# ═══════════════════════════════════════════════════════════════════════

async def generate_voiceover(script: str, output: str) -> bool:
    """Generate voiceover"""
    logger.info("🎙️  Generating voiceover...")
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        logger.info(f"   Voice: {voice}")
        
        await edge_tts.Communicate(script[:2000], voice, rate="+15%").save(output)
        
        if os.path.exists(output) and os.path.getsize(output) > 1000:
            logger.info("✅ Voiceover generated")
            return True
        else:
            logger.error("Voiceover file missing or too small")
            return False
        
    except ImportError:
        logger.error("edge_tts not installed. Run: pip install edge-tts")
        return False
    except Exception as e:
        logger.error(f"❌ Voiceover failed: {e}")
        logger.error(traceback.format_exc())
        return False


# ═══════════════════════════════════════════════════════════════════════
# VIDEO COMPOSITING
# ═══════════════════════════════════════════════════════════════════════

def generate_srt(script: str, duration: float) -> str:
    """Generate SRT"""
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
    """Remove audio"""
    logger.info("🔇 Removing audio...")
    return run_ffmpeg([
        "ffmpeg", "-i", vin, "-c:v", "copy", "-an", "-y", vout
    ], timeout=60)


async def download_bgm(output: str, duration: float) -> bool:
    """Download BGM"""
    logger.info("🎵 Downloading BGM...")
    
    try:
        url = random.choice(BGM_URLS)
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            async with client.stream("GET", url) as r:
                if r.status_code == 200:
                    raw = output.replace(".mp3", "_raw.mp3")
                    
                    with open(raw, 'wb') as f:
                        async for chunk in r.aiter_bytes(chunk_size=1024*1024):
                            f.write(chunk)
                    
                    if run_ffmpeg([
                        "ffmpeg", "-i", raw, "-t", str(duration + 2),
                        "-acodec", "copy", "-y", output
                    ], timeout=45):
                        cleanup(raw)
                        logger.info("✅ BGM ready")
                        return True
        
        return False
    except Exception as e:
        logger.warning(f"BGM download failed: {e}")
        return False


async def create_final(silent: str, voice: str, srt: str, bgm: Optional[str], output: str) -> bool:
    """Create final video"""
    logger.info("✨ Creating final video...")
    
    captioned = output.replace(".mp4", "_cap.mp4")
    srt_esc = srt.replace("\\", "\\\\").replace(":", "\\:")
    
    logger.info("   Burning captions...")
    if not run_ffmpeg([
        "ffmpeg", "-i", silent,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial Black,FontSize=28,PrimaryColour=&H000B86B8,OutlineColour=&H00000000,Bold=1,Outline=2,Alignment=2,MarginV=60'",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-y", captioned
    ], timeout=180):
        logger.error("Caption burning failed")
        return False
    
    cleanup(silent)
    
    logger.info("   Mixing audio...")
    if bgm and os.path.exists(bgm):
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voice, "-i", bgm,
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.08[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=120)
    else:
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voice,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=90)
    
    cleanup(captioned)
    
    if success:
        logger.info(f"✅ Final video: {os.path.getsize(output)/(1024*1024):.1f} MB")
    else:
        logger.error("Final video creation failed")
    
    return success


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video: str, title: str, desc: str, keywords: list, tags: list, user_id: str) -> dict:
    """Upload to YouTube"""
    logger.info("📤 Uploading to YouTube...")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds:
            logger.error("YouTube credentials not found")
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
        
        full_desc = f"{desc}\n\n{' '.join(keywords)}\n\n{' '.join(tags)}"
        
        logger.info("   Calling YouTube upload service...")
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=full_desc,
            video_url=video
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            logger.info(f"✅ Uploaded: {video_id}")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        else:
            error_msg = result.get("error", "Upload failed")
            logger.error(f"Upload failed: {error_msg}")
            return {"success": False, "error": error_msg}
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return {"success": False, "error": "YouTube upload module not available"}
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_and_upload(drive_url: str, user_id: str) -> dict:
    """Process video and upload directly to YouTube"""
    temp_dir = None
    start = datetime.now()
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="gdrive_reel_")
        logger.info("=" * 80)
        logger.info("🎬 PROCESSING START")
        logger.info("=" * 80)
        logger.info(f"   User: {user_id}")
        logger.info(f"   URL: {drive_url[:80]}...")
        logger.info(f"   Temp: {temp_dir}")
        
        # Extract file ID
        logger.info("\n[STEP 1/9] Extracting file ID...")
        file_id = extract_file_id(drive_url)
        if not file_id:
            return {
                "success": False, 
                "error": "Invalid Google Drive URL. Make sure URL is in format: https://drive.google.com/file/d/FILE_ID/view"
            }
        
        # Download
        logger.info("\n[STEP 2/9] Downloading video...")
        video = os.path.join(temp_dir, "video.mp4")
        if not await download_video(file_id, video):
            return {
                "success": False, 
                "error": "Download failed. Please check:\n1. Link is public (Share > Anyone with link can view)\n2. File is a video\n3. File size < 100MB"
            }
        
        # Get duration
        logger.info("\n[STEP 3/9] Getting video info...")
        duration = await get_duration(video)
        if duration <= 0:
            return {"success": False, "error": "Could not read video file. File may be corrupted."}
        if duration > 180:
            return {"success": False, "error": f"Video too long ({duration:.0f}s). Maximum is 180s (3 minutes)."}
        
        # Extract audio
        logger.info("\n[STEP 4/9] Extracting audio...")
        audio = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video, audio):
            return {"success": False, "error": "Audio extraction failed. Video may not have audio track."}
        
        # Transcribe
        logger.info("\n[STEP 5/9] Transcribing audio...")
        transcript = await transcribe_audio(audio)
        cleanup(audio)
        
        if not transcript:
            return {
                "success": False, 
                "error": "Transcription failed. Video must have clear Hindi speech. Please check:\n1. Video has Hindi audio\n2. Audio is not too quiet\n3. Speech is clear"
            }
        
        # Generate script
        logger.info("\n[STEP 6/9] Generating AI script...")
        meta = await generate_script(transcript, duration)
        
        # Voiceover
        logger.info("\n[STEP 7/9] Generating voiceover...")
        voice = os.path.join(temp_dir, "voice.mp3")
        if not await generate_voiceover(meta["script"], voice):
            return {"success": False, "error": "Voiceover generation failed. Please try again."}
        
        # Remove audio
        logger.info("\n[STEP 8/9] Processing video...")
        silent = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(video, silent):
            return {"success": False, "error": "Video processing failed."}
        cleanup(video)
        
        # Captions
        srt_path = os.path.join(temp_dir, "subs.srt")
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_srt(meta["script"], duration))
        
        # BGM
        bgm = os.path.join(temp_dir, "bgm.mp3")
        bgm_ok = await download_bgm(bgm, duration)
        
        # Final video
        final = os.path.join(temp_dir, "final.mp4")
        if not await create_final(silent, voice, srt_path, bgm if bgm_ok else None, final):
            return {"success": False, "error": "Final video creation failed."}
        
        cleanup(voice, srt_path, bgm)
        
        # Upload to YouTube
        logger.info("\n[STEP 9/9] Uploading to YouTube...")
        upload_result = await upload_to_youtube(
            final,
            meta["title"],
            meta["description"],
            meta["keywords"],
            meta["tags"],
            user_id
        )
        
        if not upload_result.get("success"):
            error_msg = upload_result.get("error", "YouTube upload failed")
            return {"success": False, "error": error_msg}
        
        # Success
        elapsed = (datetime.now() - start).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ SUCCESS!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video ID: {upload_result['video_id']}")
        logger.info(f"   URL: {upload_result['video_url']}")
        logger.info("=" * 80)
        
        return {
            "success": True,
            "title": meta["title"],
            "description": meta["description"],
            "keywords": meta["keywords"],
            "tags": meta["tags"],
            "duration": round(duration, 2),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "processing_time": round(elapsed, 1)
        }
        
    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": f"Processing error: {str(e)}"}
    
    finally:
        if temp_dir:
            logger.info("\n🧹 Cleanup...")
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("   ✅ Temp files deleted")
            except:
                pass
        gc.collect()


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request):
    """
    Process Google Drive video and upload to YouTube
    """
    logger.info("\n" + "🌐" * 40)
    logger.info("API REQUEST: /api/gdrive-reels/process")
    logger.info("🌐" * 40)
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        
        logger.info(f"User ID: {user_id}")
        logger.info(f"Drive URL: {drive_url[:100]}...")
        
        # Validation
        if not user_id:
            logger.error("Missing user_id")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id is required"}
            )
        
        if not drive_url:
            logger.error("Missing drive_url")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "drive_url is required"}
            )
        
        if "drive.google.com" not in drive_url:
            logger.error("Invalid URL")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "URL must be a Google Drive link"}
            )
        
        # Process with timeout
        result = await asyncio.wait_for(
            process_and_upload(drive_url, user_id),
            timeout=600  # 10 min max
        )
        
        logger.info(f"Result: success={result.get('success')}")
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        logger.error("⏱️  Request timeout (10 minutes)")
        return JSONResponse(
            status_code=408,
            content={"success": False, "error": "Processing timeout. Video may be too long or complex."}
        )
    except Exception as e:
        logger.error(f"❌ API error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Server error: {str(e)}"}
        )


@router.get("/api/gdrive-reels/status")
async def status_endpoint(request: Request):
    """Get status"""
    try:
        user_id = request.query_params.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "user_id required"}
            )
        
        return JSONResponse(content={
            "success": True,
            "note": "Direct YouTube upload - no history saved"
        })
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@router.get("/api/gdrive-reels/health")
async def health_endpoint():
    """Health check"""
    groq_ok = bool(GROQ_API_KEY)
    
    return JSONResponse(content={
        "status": "ok",
        "groq_configured": groq_ok,
        "mode": "Direct YouTube upload",
        "method": "Groq Whisper API",
        "warning": None if groq_ok else "GROQ_SPEECH_API not configured"
    })


__all__ = ["router"]