"""
gdrive_reels_optimized.py - OPTIMIZED FOR RENDER 512MB FREE TIER
==================================================================
✅ Memory optimized for 512MB limit
✅ Aggressive cleanup after each step
✅ Streaming downloads (no full load in memory)
✅ Local transcription only (faster-whisper tiny model)
✅ No video storage in DB
✅ Direct YouTube upload

STRICT MEMORY MANAGEMENT:
- Download in chunks
- Process in streaming mode
- Delete files immediately after use
- Force garbage collection
- Use smallest models
==================================================================
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
from typing import Optional
import tempfile
import shutil
import gc
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)  # Changed to INFO to reduce memory

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

# FREE Royalty-free BGM URLs
BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
]

COLLECTION = "gdrive_reels_tracker"
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for streaming

# ═══════════════════════════════════════════════════════════════════════
# MEMORY CLEANUP
# ═══════════════════════════════════════════════════════════════════════

def force_cleanup(*paths):
    """Aggressive file cleanup + garbage collection"""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
                logger.info(f"🗑️  Deleted: {os.path.basename(p)}")
        except Exception as e:
            logger.warning(f"⚠️  Cleanup failed: {e}")
    
    # Force garbage collection
    gc.collect()
    gc.collect()  # Second pass for cyclic references


def run_ffmpeg(cmd: list, timeout: int = 180) -> bool:
    """Run ffmpeg with memory optimization"""
    try:
        # Use pipe to avoid storing output in memory
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        
        if result.returncode != 0:
            logger.error(f"❌ FFmpeg failed: {result.stderr.decode()[:200]}")
            return False
        
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  FFmpeg timeout")
        return False
    except Exception as e:
        logger.error(f"❌ FFmpeg error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════
# GOOGLE DRIVE URL HANDLING
# ═══════════════════════════════════════════════════════════════════════

def extract_file_id(url: str) -> Optional[str]:
    """Extract file ID from Google Drive URL
    
    Handles formats:
    - https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/open?id=FILE_ID
    """
    logger.info(f"📎 Extracting file ID from URL...")
    
    if not url:
        logger.error("❌ Empty URL")
        return None
    
    # Pattern 1: /file/d/FILE_ID/
    match = re.search(r'/file/d/([a-zA-Z0-9_-]{25,})', url)
    if match:
        file_id = match.group(1)
        logger.info(f"✅ File ID: {file_id}")
        return file_id
    
    # Pattern 2: ?id=FILE_ID or &id=FILE_ID
    match = re.search(r'[?&]id=([a-zA-Z0-9_-]{25,})', url)
    if match:
        file_id = match.group(1)
        logger.info(f"✅ File ID: {file_id}")
        return file_id
    
    logger.error("❌ Could not extract file ID")
    return None


# ═══════════════════════════════════════════════════════════════════════
# MONGODB (METADATA ONLY)
# ═══════════════════════════════════════════════════════════════════════

async def _next_serial(db, user_id: str) -> int:
    try:
        doc = await db[COLLECTION].find_one({"user_id": user_id}, sort=[("serial", -1)])
        return doc["serial"] + 1 if doc else 1
    except:
        return 1


async def _save_metadata(db, record: dict):
    """Save ONLY metadata - NO video"""
    try:
        await db[COLLECTION].insert_one(record)
        logger.info(f"💾 Metadata saved (serial {record.get('serial')})")
    except Exception as e:
        logger.error(f"❌ DB save failed: {e}")


async def _mark_uploaded(db, user_id: str, serial: int, video_id: str, video_url: str):
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
    except Exception as e:
        logger.error(f"❌ DB update failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# STREAMING DOWNLOAD (MEMORY EFFICIENT)
# ═══════════════════════════════════════════════════════════════════════

async def download_video_streaming(file_id: str, dest: str) -> bool:
    """Stream download in chunks to avoid memory overflow"""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    logger.info(f"⬇️  Downloading (streaming mode)...")
    
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            # Initial request
            async with client.stream("GET", url) as response:
                
                # Check if it's a confirmation page (large files)
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    
                    # If HTML, it's likely a confirmation page
                    if "text/html" in content_type:
                        # Read confirmation page
                        html = await response.aread()
                        html = html.decode(errors='replace')
                        
                        # Extract confirmation URL
                        match = re.search(r'href="(/uc\?[^"]*&confirm=[^"]*)"', html)
                        if match:
                            confirm_url = "https://drive.google.com" + match.group(1).replace("&amp;", "&")
                            logger.info("   Detected large file, following confirmation...")
                            
                            # Download with confirmation
                            async with client.stream("GET", confirm_url) as confirm_response:
                                if confirm_response.status_code == 200:
                                    with open(dest, 'wb') as f:
                                        async for chunk in confirm_response.aiter_bytes(chunk_size=CHUNK_SIZE):
                                            f.write(chunk)
                                    
                                    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
                                        size_mb = os.path.getsize(dest) / (1024 * 1024)
                                        logger.info(f"✅ Downloaded: {size_mb:.1f} MB")
                                        return True
                        
                        logger.error("❌ Could not find download link")
                        return False
                    
                    # Direct download (small files)
                    else:
                        with open(dest, 'wb') as f:
                            async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                                f.write(chunk)
                        
                        if os.path.exists(dest) and os.path.getsize(dest) > 10000:
                            size_mb = os.path.getsize(dest) / (1024 * 1024)
                            logger.info(f"✅ Downloaded: {size_mb:.1f} MB")
                            return True
                
                logger.error(f"❌ Download failed: HTTP {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        return False


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
    """Extract audio - optimized"""
    logger.info("🔊 Extracting audio...")
    return run_ffmpeg([
        "ffmpeg", "-i", video,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", wav
    ], timeout=60)


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION - TINY MODEL FOR MEMORY EFFICIENCY
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_local(wav: str) -> Optional[str]:
    """Use faster-whisper TINY model (lowest memory)"""
    logger.info("🎙️  Transcribing (tiny model for memory)...")
    
    try:
        from faster_whisper import WhisperModel
        
        # Use TINY model (39MB) for 512MB constraint
        logger.info("   Loading tiny model...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        
        logger.info("   Processing audio...")
        segments, info = model.transcribe(
            wav,
            language="hi",
            beam_size=1,  # Reduce memory
            vad_filter=True  # Filter silence
        )
        
        text = " ".join([seg.text for seg in segments])
        
        # Delete model from memory immediately
        del model
        gc.collect()
        
        if text and len(text) > 8:
            logger.info(f"✅ Transcribed: {len(text)} chars")
            return text.strip()
        
        logger.warning("⚠️  Transcription too short")
        return None
        
    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# MISTRAL AI - MINIMAL CHANGES
# ═══════════════════════════════════════════════════════════════════════

async def mistral_minimal_changes(transcript: str, duration: float) -> dict:
    """Mistral API - few word changes only"""
    logger.info("🤖 AI processing...")
    
    if not MISTRAL_API_KEY:
        raise Exception("MISTRAL_API_KEY not set")

    words = int(duration * 2.5)
    
    prompt = f"""Rephrase this Hindi text minimally (change few words only):

ORIGINAL: "{transcript}"

RULES:
1. Keep story EXACT same
2. Change only 10-15% words (synonyms)
3. {words} words max
4. Add catchy title (4-6 words + emoji)
5. Description (1-2 lines)

Return JSON only:
{{"script":"...","title":"...","description":"..."}}"""

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-small-latest",  # Smaller model
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 800
                }
            )
        
        if response.status_code != 200:
            raise Exception(f"Mistral failed: {response.status_code}")

        content = response.json()["choices"][0]["message"]["content"]
        content = re.sub(r'```json\s*|```', '', content).strip()
        
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match:
            raise Exception("No JSON in response")
        
        data = json.loads(match.group(0))
        
        logger.info(f"✅ AI done")
        
        return {
            "script": data.get("script", transcript)[:2000],
            "title": data.get("title", "Amazing Video 🔥")[:100],
            "description": data.get("description", transcript[:200])[:500]
        }
        
    except Exception as e:
        logger.error(f"❌ Mistral error: {e}")
        # Fallback
        return {
            "script": transcript[:2000],
            "title": "Amazing Story 🔥",
            "description": transcript[:200]
        }


# ═══════════════════════════════════════════════════════════════════════
# VOICEOVER
# ═══════════════════════════════════════════════════════════════════════

async def generate_voiceover(script: str, temp_dir: str) -> Optional[str]:
    """Generate Hindi voiceover"""
    logger.info("🎙️  Generating voiceover...")
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        output = os.path.join(temp_dir, "voice.mp3")
        
        await edge_tts.Communicate(script[:2000], voice, rate="+5%").save(output)
        
        if os.path.exists(output) and os.path.getsize(output) > 1000:
            logger.info(f"✅ Voiceover ready")
            return output
        
        return None
    except Exception as e:
        logger.error(f"❌ Voiceover error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# GOLDEN CAPTIONS
# ═══════════════════════════════════════════════════════════════════════

def build_srt(script: str, duration: float) -> str:
    """Simple SRT captions"""
    words = script.split()
    phrases = []
    
    for i in range(0, len(words), 4):
        phrases.append(" ".join(words[i:i+4]))
    
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
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove original audio"""
    logger.info("🔇 Removing original audio...")
    return run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an",
        "-y", video_out
    ], timeout=60)


async def download_bgm(temp_dir: str, duration: float) -> Optional[str]:
    """Download royalty-free BGM"""
    logger.info("🎵 Downloading BGM...")
    
    url = random.choice(BGM_URLS)
    raw = os.path.join(temp_dir, "bgm_raw.mp3")
    output = os.path.join(temp_dir, "bgm.mp3")
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(raw, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                            f.write(chunk)
                    
                    # Trim to duration
                    if run_ffmpeg([
                        "ffmpeg", "-i", raw,
                        "-t", str(duration + 2),
                        "-acodec", "copy",
                        "-y", output
                    ], timeout=45):
                        force_cleanup(raw)
                        return output
                    
                    return raw if os.path.exists(raw) else None
    except:
        pass
    
    return None


async def composite_final(silent_video: str, voiceover: str, srt_path: str,
                          bgm: Optional[str], output: str) -> bool:
    """Burn captions + mix audio"""
    logger.info("✨ Creating final video...")
    
    captioned = output.replace(".mp4", "_cap.mp4")
    srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
    # Burn captions
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
    ], timeout=180):
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
        ], timeout=120)
    else:
        success = run_ffmpeg([
            "ffmpeg",
            "-i", captioned, "-i", voiceover,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], timeout=90)

    force_cleanup(captioned)
    return success


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video_path: str, title: str, description: str,
                            user_id: str) -> dict:
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
        
        full_desc = f"{description}\n\n#Shorts #Viral #Hindi"
        
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
            logger.info(f"✅ Uploaded! ID: {video_id}")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE - MEMORY OPTIMIZED
# ═══════════════════════════════════════════════════════════════════════

async def process_gdrive_video(drive_url: str, user_id: str, db) -> dict:
    """Memory-optimized processing pipeline"""
    logger.info("=" * 80)
    logger.info("🎬 PROCESSING START (Memory Optimized for 512MB)")
    logger.info("=" * 80)
    
    temp_dir = tempfile.mkdtemp(prefix="reel_")
    logger.info(f"📁 Temp: {temp_dir}")
    
    try:
        # Extract file ID
        file_id = extract_file_id(drive_url)
        if not file_id:
            return {"success": False, "error": "Invalid Google Drive URL"}

        serial = await _next_serial(db, user_id)

        # Download video (streaming)
        video_path = os.path.join(temp_dir, "video.mp4")
        if not await download_video_streaming(file_id, video_path):
            return {"success": False, "error": "Download failed. Ensure link is public: File > Share > Anyone with link"}

        # Get duration
        duration = await get_duration(video_path)
        if duration <= 0:
            return {"success": False, "error": "Invalid video file"}

        # Extract audio
        audio_path = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video_path, audio_path):
            return {"success": False, "error": "Audio extraction failed"}

        # Transcribe
        transcript = await transcribe_local(audio_path)
        force_cleanup(audio_path)  # Delete audio immediately
        
        if not transcript or len(transcript) < 8:
            return {"success": False, "error": "Transcription failed. Video needs clear Hindi speech."}

        # AI processing
        meta = await mistral_minimal_changes(transcript, duration)
        script = meta["script"]
        title = meta["title"]
        description = meta["description"]

        # Generate voiceover
        voiceover = await generate_voiceover(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Voiceover generation failed"}

        # Remove original audio
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(video_path, silent_video):
            return {"success": False, "error": "Audio removal failed"}
        
        force_cleanup(video_path)  # Delete original

        # Create captions
        srt_path = os.path.join(temp_dir, "subs.srt")
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(build_srt(script, duration))

        # Download BGM
        bgm = await download_bgm(temp_dir, duration)

        # Create final video
        final_path = os.path.join(temp_dir, "final.mp4")
        if not await composite_final(silent_video, voiceover, srt_path, bgm, final_path):
            return {"success": False, "error": "Video composition failed"}

        force_cleanup(silent_video, voiceover, bgm, srt_path)  # Cleanup intermediates

        logger.info("📤 Uploading directly to YouTube (no storage)...")
        
        # Upload
        upload_result = await upload_to_youtube(final_path, title, description, user_id)
        
        if not upload_result.get("success"):
            return {"success": False, "error": upload_result.get("error")}

        # Save metadata only
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

        logger.info("=" * 80)
        logger.info("✅ SUCCESS!")
        logger.info("=" * 80)

        return {
            "success": True,
            "serial": serial,
            "title": title,
            "description": description,
            "duration": round(duration, 2),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"]
        }

    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}
    
    finally:
        # Aggressive cleanup
        logger.info("🧹 Cleanup...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        gc.collect()


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request):
    """Process Google Drive video and upload to YouTube"""
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

        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            process_gdrive_video(drive_url, user_id, database_manager.db),
            timeout=600
        )
        
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={"success": False, "error": "Processing timeout (10 min limit)"}
        )
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


__all__ = ["router"]