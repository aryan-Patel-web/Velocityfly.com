"""
MrBeast_Complete_Working.py - FULL CODE WITH 4 DOWNLOAD METHODS
================================================================
✅ Method 1: yt-dlp (5 strategies)
✅ Method 2: pytubefix (modern pytube)
✅ Method 3: Direct URL extraction
✅ Method 4: Invidious API
✅ Complete: Download → Transcript → AI Rewrite → Voice → Crop → Upload
================================================================
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import traceback
import uuid
import httpx
import json
import re
import random
import subprocess
from typing import List, Dict, Optional
import tempfile
import shutil
import gc
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("MrBeast")
logger.setLevel(logging.INFO)

# ============================================================================
# CONFIGURATION
# ============================================================================

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
HINDI_VOICE_ID = "WXTRkeANkY97koU9TGhC"
MIN_DURATION = 20
MAX_DURATION = 55
FFMPEG_TIMEOUT = 180
OUTPUT_WIDTH = 720
OUTPUT_HEIGHT = 1280
FPS = 30

BG_MUSIC_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(14).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(10).weba"
]

router = APIRouter()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def force_cleanup(*filepaths):
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
        except:
            pass
    gc.collect()

def get_file_size_mb(filepath: str) -> float:
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        gc.collect()
        return result.returncode == 0
    except:
        gc.collect()
        return False

# ============================================================================
# DOWNLOAD METHOD 1: YT-DLP WITH 5 STRATEGIES
# ============================================================================

async def download_with_ytdlp(url: str, output_path: str) -> bool:
    """yt-dlp with 5 different strategies"""
    strategies = [
        {
            "name": "Chrome cookies",
            "cmd": ["yt-dlp", "--cookies-from-browser", "chrome", "-f", "best", "-o", output_path, url]
        },
        {
            "name": "Firefox cookies",
            "cmd": ["yt-dlp", "--cookies-from-browser", "firefox", "-f", "best", "-o", output_path, url]
        },
        {
            "name": "Android client",
            "cmd": ["yt-dlp", "--extractor-args", "youtube:player_client=android", "-f", "18/best", "-o", output_path, url]
        },
        {
            "name": "iOS client",
            "cmd": ["yt-dlp", "--extractor-args", "youtube:player_client=ios", "-f", "best", "-o", output_path, url]
        },
        {
            "name": "Web embedded",
            "cmd": ["yt-dlp", "--extractor-args", "youtube:player_client=web_embedded", "-f", "worst", "-o", output_path, url]
        }
    ]
    
    for strategy in strategies:
        try:
            logger.info(f"   Trying: {strategy['name']}")
            process = subprocess.run(strategy["cmd"], capture_output=True, timeout=300, check=False)
            
            if process.returncode == 0 and os.path.exists(output_path):
                logger.info(f"   ✅ Success!")
                return True
        except:
            continue
    
    return False

# ============================================================================
# DOWNLOAD METHOD 2: PYTUBEFIX
# ============================================================================

async def download_with_pytubefix(url: str, output_path: str) -> bool:
    """pytubefix (modern pytube fork)"""
    try:
        logger.info("   Trying: pytubefix")
        from pytubefix import YouTube
        
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        
        if not stream:
            stream = yt.streams.filter(file_extension='mp4').first()
        
        if stream:
            temp = output_path.replace('.mp4', '_temp.mp4')
            stream.download(filename=temp)
            shutil.move(temp, output_path)
            logger.info("   ✅ Success!")
            return True
            
    except ImportError:
        logger.info("   ⚠️ pytubefix not installed")
    except Exception as e:
        logger.warning(f"   ❌ Error: {e}")
    
    return False

# ============================================================================
# DOWNLOAD METHOD 3: DIRECT URL EXTRACTION
# ============================================================================

async def download_with_direct_url(url: str, output_path: str) -> bool:
    """Extract direct video URL"""
    try:
        logger.info("   Trying: Direct URL extraction")
        
        video_id = None
        if "shorts/" in url:
            video_id = url.split("shorts/")[1].split("?")[0]
        elif "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        
        if not video_id:
            return False
        
        async with httpx.AsyncClient(timeout=30) as client:
            info_url = f"https://www.youtube.com/get_video_info?video_id={video_id}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = await client.get(info_url, headers=headers)
            
            if response.status_code == 200:
                from urllib.parse import parse_qs, unquote
                data = parse_qs(response.text)
                
                if 'url_encoded_fmt_stream_map' in data:
                    streams = data['url_encoded_fmt_stream_map'][0].split(',')
                    
                    for stream in streams:
                        stream_data = parse_qs(stream)
                        
                        if 'url' in stream_data:
                            video_url = unquote(stream_data['url'][0])
                            video_response = await client.get(video_url, headers=headers, follow_redirects=True)
                            
                            if video_response.status_code == 200:
                                with open(output_path, 'wb') as f:
                                    f.write(video_response.content)
                                logger.info("   ✅ Success!")
                                return True
        
    except Exception as e:
        logger.warning(f"   ❌ Error: {e}")
    
    return False

# ============================================================================
# DOWNLOAD METHOD 4: INVIDIOUS API
# ============================================================================

async def download_with_invidious(url: str, output_path: str) -> bool:
    """Invidious API (YouTube alternative frontend)"""
    try:
        logger.info("   Trying: Invidious API")
        
        video_id = None
        if "shorts/" in url:
            video_id = url.split("shorts/")[1].split("?")[0]
        elif "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        
        if not video_id:
            return False
        
        instances = ["https://yewtu.be", "https://invidious.snopyta.org", "https://invidious.kavin.rocks"]
        
        async with httpx.AsyncClient(timeout=30) as client:
            for instance in instances:
                try:
                    api_url = f"{instance}/api/v1/videos/{video_id}"
                    response = await client.get(api_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        formats = data.get('formatStreams', [])
                        
                        if formats:
                            best_format = max(formats, key=lambda x: x.get('size', 0))
                            video_url = best_format.get('url')
                            
                            if video_url:
                                video_response = await client.get(video_url, follow_redirects=True)
                                
                                if video_response.status_code == 200:
                                    with open(output_path, 'wb') as f:
                                        f.write(video_response.content)
                                    logger.info(f"   ✅ Success with {instance}")
                                    return True
                except:
                    continue
        
    except Exception as e:
        logger.warning(f"   ❌ Error: {e}")
    
    return False

# ============================================================================
# MAIN DOWNLOAD FUNCTION
# ============================================================================

async def download_youtube_video(url: str, temp_dir: str) -> Optional[str]:
    """Download with 4 fallback methods"""
    output_path = os.path.join(temp_dir, "original.mp4")
    
    logger.info(f"📥 Downloading: {url}")
    logger.info("🔄 Trying 4 methods...")
    
    # Try all methods
    methods = [
        ("yt-dlp", download_with_ytdlp),
        ("pytubefix", download_with_pytubefix),
        ("Direct URL", download_with_direct_url),
        ("Invidious", download_with_invidious)
    ]
    
    for name, method in methods:
        try:
            if await method(url, output_path):
                size = get_file_size_mb(output_path)
                logger.info(f"✅ Downloaded with {name}: {size:.1f}MB")
                return output_path
        except Exception as e:
            logger.warning(f"{name} failed: {e}")
            continue
    
    logger.error("❌ All methods failed")
    return None

# ============================================================================
# GET VIDEO DURATION
# ============================================================================

def get_video_duration(video_path: str) -> float:
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        result = subprocess.run(cmd, capture_output=True, timeout=10, check=False)
        
        if result.returncode == 0:
            duration = float(result.stdout.decode().strip())
            logger.info(f"📏 Duration: {duration:.1f}s")
            return duration
        return 0
    except:
        return 0

# ============================================================================
# EXTRACT TRANSCRIPT
# ============================================================================

async def extract_transcript(video_path: str, temp_dir: str) -> Optional[str]:
    try:
        audio_path = os.path.join(temp_dir, "audio.mp3")
        logger.info("🎤 Extracting audio...")
        
        cmd = ["ffmpeg", "-i", video_path, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", "-ar", "16000", "-y", audio_path]
        
        if not run_ffmpeg(cmd, 60):
            return None
        
        logger.info("🧠 Transcribing...")
        
        async with httpx.AsyncClient(timeout=120) as client:
            with open(audio_path, 'rb') as f:
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files={"file": ("audio.mp3", f, "audio/mpeg")},
                    data={"model": "whisper-large-v3", "response_format": "verbose_json", "temperature": 0}
                )
            
            if response.status_code == 200:
                transcript = response.json().get("text", "")
                force_cleanup(audio_path)
                logger.info(f"✅ Transcript: {len(transcript)} chars")
                return transcript
        
        return None
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None

# ============================================================================
# AI CREATIVE REWRITE
# ============================================================================

async def rewrite_script_creatively(original: str, duration: int) -> dict:
    try:
        logger.info("✍️ AI Rewrite...")
        
        words = int(duration * 2.75)
        
        prompt = f"""Rewrite into VIRAL HINDI:

ORIGINAL: "{original}"

RULES:
1. HINDI (Hinglish OK)
2. Change wording (avoid copyright)
3. Add hooks: "Suniye...", "Dekhiye..."
4. {words} words
5. End: "LIKE karein, SUBSCRIBE karein!"

JSON:
{{
    "script": "Hindi...",
    "title": "Title 3-6 words",
    "hook": "Hook"
}}"""

        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "Hindi content creator. JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.85
                }
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                result = json.loads(content)
                logger.info(f"✅ Rewritten")
                return result
        
        return {"script": f"Amazing story... {original[:200]}... LIKE SUBSCRIBE!", "title": "Viral", "hook": ""}
    except:
        return {"script": original[:500], "title": "Short", "hook": ""}

# ============================================================================
# GENERATE HINDI VOICEOVER (1.1x)
# ============================================================================

async def generate_hindi_voiceover_11x(text: str, temp_dir: str) -> Optional[str]:
    try:
        logger.info("🎙️ Generating voice (1.1x)...")
        
        base = os.path.join(temp_dir, "voice_base.mp3")
        final = os.path.join(temp_dir, "voice.mp3")
        
        # Try ElevenLabs
        if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{HINDI_VOICE_ID}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    json={
                        "text": text[:2500],
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.6}
                    }
                )
                
                if response.status_code == 200:
                    with open(base, 'wb') as f:
                        f.write(response.content)
                    
                    cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1,loudnorm=I=-16:TP=-1.5", "-y", final]
                    
                    if run_ffmpeg(cmd, 30):
                        force_cleanup(base)
                        logger.info(f"✅ Voice: {get_file_size_mb(final):.2f}MB")
                        return final
        
        # Fallback: Edge TTS
        logger.info("Using Edge TTS...")
        import edge_tts
        
        await edge_tts.Communicate(text[:2000], "hi-IN-MadhurNeural", rate="+10%").save(base)
        
        cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1,loudnorm=I=-16:TP=-1.5", "-y", final]
        
        if run_ffmpeg(cmd, 25):
            force_cleanup(base)
            logger.info(f"✅ Voice: {get_file_size_mb(final):.2f}MB")
            return final
        
        return None
    except Exception as e:
        logger.error(f"Voice error: {e}")
        return None

# ============================================================================
# DOWNLOAD BACKGROUND MUSIC
# ============================================================================

async def download_background_music(temp_dir: str, duration: float) -> Optional[str]:
    try:
        music_url = random.choice(BG_MUSIC_URLS)
        logger.info(f"🎵 Downloading music...")
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            response = await client.get(music_url)
            
            if response.status_code == 200:
                raw = os.path.join(temp_dir, "music_raw.weba")
                mp3 = os.path.join(temp_dir, "music.mp3")
                
                with open(raw, 'wb') as f:
                    f.write(response.content)
                
                cmd = ["ffmpeg", "-i", raw, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", "-t", str(duration + 2), "-y", mp3]
                
                if run_ffmpeg(cmd, 60):
                    force_cleanup(raw)
                    logger.info(f"✅ Music: {get_file_size_mb(mp3):.2f}MB")
                    return mp3
        
        return None
    except:
        return None

# ============================================================================
# CROP & ZOOM VIDEO (9:16)
# ============================================================================

def crop_and_zoom_video(video_path: str, temp_dir: str) -> Optional[str]:
    try:
        output = os.path.join(temp_dir, "cropped.mp4")
        logger.info("✂️ Cropping to 9:16 + zoom...")
        
        filter_complex = (
            "[0:v]"
            "scale=720:-1,"
            "crop=720:1280:0:(ih-1280)/2,"
            "zoompan=z='min(1.15,1.0+(on/1000*0.15))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=30,"
            "eq=contrast=1.05:brightness=0.03"
            "[v]"
        )
        
        cmd = ["ffmpeg", "-i", video_path, "-filter_complex", filter_complex, "-map", "[v]", "-c:v", "libx264", "-crf", "23", "-preset", "medium", "-an", "-y", output]
        
        if run_ffmpeg(cmd, 180):
            logger.info(f"✅ Cropped: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
    except:
        return None

# ============================================================================
# ADD CAPTIONS
# ============================================================================

def add_captions_to_video(video_path: str, script: str, hook: str, temp_dir: str) -> Optional[str]:
    try:
        output = os.path.join(temp_dir, "captioned.mp4")
        logger.info("📝 Adding captions...")
        
        text = (hook if hook else script[:80]).replace("'", "").replace('"', '')[:80]
        
        filter_str = f"drawtext=text='{text}':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=h-300:borderw=4:bordercolor=black"
        
        cmd = ["ffmpeg", "-i", video_path, "-vf", filter_str, "-c:v", "libx264", "-crf", "23", "-c:a", "copy", "-y", output]
        
        if run_ffmpeg(cmd, 120):
            logger.info(f"✅ Captioned: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
    except:
        return None

# ============================================================================
# COMBINE VIDEO + VOICE + MUSIC
# ============================================================================

async def combine_video_voice_music(video: str, voice: str, music: Optional[str], temp_dir: str) -> Optional[str]:
    try:
        output = os.path.join(temp_dir, "final.mp4")
        logger.info("🎬 Combining...")
        
        if music:
            cmd = [
                "ffmpeg", "-i", video, "-i", voice, "-i", music,
                "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.10[m];[v][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", output
            ]
        else:
            cmd = ["ffmpeg", "-i", video, "-i", voice, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", output]
        
        if run_ffmpeg(cmd, 120):
            logger.info(f"✅ Final: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
    except:
        return None

# ============================================================================
# UPLOAD TO YOUTUBE
# ============================================================================

async def upload_to_youtube(video: str, title: str, description: str, user_id: str, database_manager) -> dict:
    try:
        logger.info("📤 Uploading to YouTube...")
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds_raw = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds_raw:
            return {"success": False, "error": "YouTube credentials not found"}
        
        credentials = {
            "access_token": creds_raw.get("access_token"),
            "refresh_token": creds_raw.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
        }
        
        from mainY import youtube_scheduler
        
        full_desc = f"{description}\n\n#shorts #viral #trending #hindi"
        
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
            logger.info(f"✅ Uploaded! ID: {video_id}")
            return {"success": True, "video_id": video_id, "video_url": f"https://youtube.com/shorts/{video_id}"}
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

async def generate_mrbeast_short(youtube_url: str, target_duration: int, user_id: str, database_manager) -> dict:
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="mrbeast_")
        logger.info(f"🎬 START: {youtube_url} | {target_duration}s")
        
        # 1. Download
        video_path = await download_youtube_video(youtube_url, temp_dir)
        if not video_path:
            return {"success": False, "error": "Download failed"}
        
        # 2. Duration check
        duration = get_video_duration(video_path)
        if duration < target_duration:
            return {"success": False, "error": f"Video too short: {duration:.0f}s"}
        
        # 3. Transcript
        transcript = await extract_transcript(video_path, temp_dir)
        if not transcript:
            return {"success": False, "error": "Transcription failed"}
        
        # 4. AI Rewrite
        rewrite = await rewrite_script_creatively(transcript, target_duration)
        script = rewrite["script"]
        title = rewrite["title"]
        hook = rewrite["hook"]
        
        # 5. Voice (1.1x)
        voice = await generate_hindi_voiceover_11x(script, temp_dir)
        if not voice:
            return {"success": False, "error": "Voice generation failed"}
        
        # 6. Music
        music = await download_background_music(temp_dir, target_duration)
        
        # 7. Crop + Zoom
        cropped = crop_and_zoom_video(video_path, temp_dir)
        if not cropped:
            return {"success": False, "error": "Cropping failed"}
        
        force_cleanup(video_path)
        
        # 8. Captions
        captioned = add_captions_to_video(cropped, script, hook, temp_dir)
        if not captioned:
            return {"success": False, "error": "Caption failed"}
        
        force_cleanup(cropped)
        
        # 9. Combine
        final = await combine_video_voice_music(captioned, voice, music, temp_dir)
        if not final:
            return {"success": False, "error": "Combining failed"}
        
        final_size = get_file_size_mb(final)
        
        # 10. Upload
        upload_result = await upload_to_youtube(final, title, script, user_id, database_manager)
        
        # Cleanup
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if upload_result.get("success"):
            return {
                "success": True,
                "video_id": upload_result["video_id"],
                "video_url": upload_result["video_url"],
                "title": title,
                "script": script[:200] + "...",
                "size": f"{final_size:.1f}MB"
            }
        else:
            return {"success": False, "error": upload_result.get("error")}
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ENDPOINT
# ============================================================================

@router.post("/api/mrbeast/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        youtube_url = data.get("youtube_url", "")
        target_duration = int(data.get("target_duration", 30))
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "Authentication required"})
        
        if not youtube_url or ("youtube.com" not in youtube_url and "youtu.be" not in youtube_url):
            return JSONResponse(status_code=400, content={"success": False, "error": "Invalid YouTube URL"})
        
        if not (MIN_DURATION <= target_duration <= MAX_DURATION):
            return JSONResponse(status_code=400, content={"success": False, "error": f"Duration must be {MIN_DURATION}-{MAX_DURATION}s"})
        
        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            generate_mrbeast_short(youtube_url, target_duration, user_id, database_manager),
            timeout=900
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']