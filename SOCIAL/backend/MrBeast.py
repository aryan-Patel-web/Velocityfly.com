"""
mrbeast_automation_IMPROVED.py - PRODUCTION-READY WITH FALLBACKS
================================================================
✅ 4 download methods with retry logic
✅ Android/iOS/Web client fallbacks
✅ Cobalt API as last resort
✅ Comprehensive error logging
✅ Works on Render (cloud platform optimized)
================================================================
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
import subprocess
from typing import List, Dict, Optional
import tempfile
import shutil
import gc
from datetime import datetime
import yt_dlp

logger = logging.getLogger("MrBeast")
logger.setLevel(logging.INFO)

# ============================================================================
# CONFIGURATION
# ============================================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GOOGLE_VERTEX_API_KEY = os.getenv("GOOGLE_VERTEX_API_KEY", "AIzaSyAb8RN6KKt384GXtEg7vxZnhXZNxhoTrXw3mcoe7RevLa881bSw")
MONGODB_URI = os.getenv("MONGODB_URI")

FFMPEG_TIMEOUT = 300
FPS = 30
VIDEO_WIDTH = 720
VIDEO_HEIGHT = 1280

VERTEX_AI_HINDI_VOICES = [
    {"name": "hi-IN-Standard-A", "gender": "FEMALE", "description": "Natural Female"},
    {"name": "hi-IN-Standard-B", "gender": "MALE", "description": "Deep Male"},
    {"name": "hi-IN-Standard-C", "gender": "FEMALE", "description": "Clear Female"}
]

BACKGROUND_MUSIC_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/VIOLENTO%20(Slowed).mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/DNA%20-%20Slowed.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/PASSO%20BEM%20SOLTO%20(Slowed).mp3"
]

# ============================================================================
# UTILITIES
# ============================================================================

def force_cleanup(*filepaths):
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
        except:
            pass
    gc.collect()

def get_size_mb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0.0

def run_ffmpeg(cmd: list, timeout: int = 300) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        return result.returncode == 0
    except:
        return False

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# ============================================================================
# DOWNLOAD METHODS
# ============================================================================

async def download_with_android_client(url: str, temp_dir: str) -> tuple:
    """Method 1: Android client (most reliable for bypassing restrictions)"""
    logger.info("📱 Method 1: Android client...")
    
    try:
        ydl_opts = {
            'format': 'best[height<=1080][ext=mp4]/best[ext=mp4]/best',
            'outtmpl': os.path.join(temp_dir, 'source_video.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'hi'],
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['hls', 'dash', 'translated_subs']
                }
            },
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            title = info.get('title', 'Unknown')
            description = info.get('description', '')
            duration = info.get('duration', 0)
            
            # Extract transcript
            transcript = extract_transcript_from_srt(video_path)
            
            logger.info(f"✅ Android method SUCCESS")
            logger.info(f"   Title: {title[:50]}")
            logger.info(f"   Duration: {duration}s | Size: {get_size_mb(video_path):.1f}MB")
            
            return video_path, title, description, transcript
            
    except Exception as e:
        logger.warning(f"⚠️ Android method failed: {str(e)[:150]}")
        return None, None, None, None


async def download_with_ios_client(url: str, temp_dir: str) -> tuple:
    """Method 2: iOS client"""
    logger.info("📱 Method 2: iOS client...")
    
    try:
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/worst',
            'outtmpl': os.path.join(temp_dir, 'source_video.%(ext)s'),
            'quiet': False,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)',
            },
            'socket_timeout': 30,
            'retries': 2,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            title = info.get('title', 'Unknown')
            description = info.get('description', '')
            transcript = extract_transcript_from_srt(video_path)
            
            logger.info(f"✅ iOS method SUCCESS")
            return video_path, title, description, transcript
            
    except Exception as e:
        logger.warning(f"⚠️ iOS method failed: {str(e)[:150]}")
        return None, None, None, None


async def download_with_web_embed(url: str, temp_dir: str) -> tuple:
    """Method 3: Web embedded player"""
    logger.info("🌐 Method 3: Web embedded player...")
    
    try:
        ydl_opts = {
            'format': 'worst[ext=mp4]/worst',
            'outtmpl': os.path.join(temp_dir, 'source_video.%(ext)s'),
            'quiet': False,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_embedded'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.youtube.com/',
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            title = info.get('title', 'Unknown')
            description = info.get('description', '')
            transcript = extract_transcript_from_srt(video_path)
            
            logger.info(f"✅ Web embed method SUCCESS")
            return video_path, title, description, transcript
            
    except Exception as e:
        logger.warning(f"⚠️ Web embed failed: {str(e)[:150]}")
        return None, None, None, None


async def download_with_cobalt_api(url: str, video_id: str, temp_dir: str) -> tuple:
    """Method 4: Cobalt.tools API (third-party fallback)"""
    logger.info("🔄 Method 4: Cobalt API (third-party)...")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.cobalt.tools/api/json",
                json={
                    "url": url,
                    "vCodec": "h264",
                    "vQuality": "720",
                    "aFormat": "mp3",
                    "isAudioOnly": False
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            if resp.status_code == 200:
                data = resp.json()
                
                if data.get("status") in ["redirect", "stream"]:
                    download_url = data.get("url")
                    
                    if download_url:
                        video_resp = await client.get(download_url, follow_redirects=True)
                        
                        if video_resp.status_code == 200:
                            video_path = os.path.join(temp_dir, "source_video.mp4")
                            with open(video_path, 'wb') as f:
                                f.write(video_resp.content)
                            
                            logger.info(f"✅ Cobalt API SUCCESS: {get_size_mb(video_path):.1f}MB")
                            return video_path, f"Video {video_id}", "", ""
            
        logger.warning("⚠️ Cobalt API failed")
        
    except Exception as e:
        logger.warning(f"⚠️ Cobalt API error: {str(e)[:150]}")
    
    return None, None, None, None


def extract_transcript_from_srt(video_path: str) -> str:
    """Extract transcript from SRT subtitle file"""
    for lang in ['en', 'hi']:
        subtitle_path = video_path.replace('.mp4', f'.{lang}.srt')
        if os.path.exists(subtitle_path):
            try:
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    subtitle_text = f.read()
                    lines = subtitle_text.split('\n')
                    transcript = ' '.join([
                        line for line in lines 
                        if not line.strip().isdigit() 
                        and '-->' not in line 
                        and line.strip()
                    ])
                    if transcript:
                        logger.info(f"✅ Extracted {lang} transcript ({len(transcript)} chars)")
                        return transcript
            except Exception as e:
                logger.warning(f"Subtitle read error: {e}")
    return ""


async def download_youtube_video(url: str, temp_dir: str) -> tuple:
    """
    Download with multiple fallback methods
    Returns: (video_path, title, description, transcript)
    """
    
    logger.info(f"🎬 Downloading: {url}")
    
    video_id = extract_video_id(url)
    if not video_id:
        logger.error("❌ Invalid YouTube URL")
        return None, None, None, None
    
    logger.info(f"📺 Video ID: {video_id}")
    
    # Try methods in order
    methods = [
        download_with_android_client,
        download_with_ios_client,
        download_with_web_embed,
        lambda u, t: download_with_cobalt_api(u, video_id, t)
    ]
    
    for idx, method in enumerate(methods, 1):
        logger.info(f"🔄 Attempt {idx}/4")
        
        result = await method(url, temp_dir)
        
        if result[0]:  # Success
            logger.info(f"🎉 Download SUCCESS with method {idx}")
            return result
        
        if idx < len(methods):
            logger.info(f"   Trying next method...")
            await asyncio.sleep(2)
    
    logger.error("❌ ALL DOWNLOAD METHODS FAILED")
    return None, None, None, None

# ============================================================================
# AI FUNCTIONS (Same as before)
# ============================================================================

async def generate_ai_title_description(original_title: str, transcript: str, description: str) -> dict:
    """Generate viral Hindi title and SEO description"""
    
    logger.info("🤖 Generating AI metadata...")
    
    content_text = f"{original_title}\n{transcript[:1000]}\n{description[:500]}"
    
    prompt = f"""Create VIRAL Hindi/Hinglish YouTube Shorts metadata:

Content: {content_text}

Generate JSON:
{{
    "title": "Viral Hinglish title 40-60 chars with emoji",
    "description": "Engaging 150-200 char description with keywords",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
}}"""
    
    try:
        if MISTRAL_API_KEY:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Create viral Hinglish titles. Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.9,
                        "max_tokens": 500
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if match:
                        data = json.loads(match.group(0))
                        logger.info(f"✅ AI title: {data.get('title')}")
                        return data
    except Exception as e:
        logger.error(f"AI generation error: {e}")
    
    return {
        "title": f"{original_title[:40]}... | Viral 🔥",
        "description": "Amazing viral content! #Shorts #Viral",
        "hashtags": ["#Shorts", "#Viral", "#Trending"]
    }


async def generate_hindi_script(transcript: str, target_duration: int = 30) -> str:
    """Generate Hindi script from transcript"""
    
    logger.info("📝 Generating Hindi script...")
    
    prompt = f"""Convert to engaging Hindi voiceover script for {target_duration}s:

English: {transcript[:1000]}

Requirements:
- Natural conversational Hindi
- Energetic and exciting
- NO timestamps
- Plain text only

Hindi script:"""
    
    try:
        if MISTRAL_API_KEY:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Hindi translator. Create engaging scripts."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 800
                    }
                )
                
                if resp.status_code == 200:
                    hindi_script = resp.json()["choices"][0]["message"]["content"].strip()
                    logger.info(f"✅ Hindi script: {len(hindi_script)} chars")
                    return hindi_script
    except Exception as e:
        logger.error(f"Script error: {e}")
    
    return transcript[:300]

# ============================================================================
# VIDEO PROCESSING (Same as before - resize, overlay, captions, etc.)
# ============================================================================

def resize_video_to_shorts(input_video: str, temp_dir: str) -> Optional[str]:
    output_video = os.path.join(temp_dir, "resized_video.mp4")
    logger.info(f"📐 Resizing to {VIDEO_WIDTH}x{VIDEO_HEIGHT}...")
    
    filter_complex = f"[0:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT},fps={FPS}[v]"
    
    cmd = [
        "ffmpeg", "-i", input_video,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-y", output_video
    ]
    
    if run_ffmpeg(cmd, FFMPEG_TIMEOUT):
        logger.info(f"✅ Resized: {get_size_mb(output_video):.1f}MB")
        return output_video
    return None


def add_overlay_effect(input_video: str, temp_dir: str) -> Optional[str]:
    output_video = os.path.join(temp_dir, "overlay_video.mp4")
    logger.info("🎨 Adding overlay...")
    
    cmd = [
        "ffmpeg", "-i", input_video,
        "-vf", "eq=brightness=0.05:contrast=1.1,vignette=PI/4",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "copy",
        "-y", output_video
    ]
    
    if run_ffmpeg(cmd, FFMPEG_TIMEOUT):
        logger.info(f"✅ Overlay added")
        return output_video
    return None


def generate_subtitles_from_script(script_text: str, duration: float, temp_dir: str) -> Optional[str]:
    srt_path = os.path.join(temp_dir, "subtitles.srt")
    logger.info("📝 Generating subtitles...")
    
    try:
        sentences = re.split(r'[।\.\!]', script_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return None
        
        time_per_sentence = duration / len(sentences)
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for idx, sentence in enumerate(sentences):
                start_time = idx * time_per_sentence
                end_time = (idx + 1) * time_per_sentence
                
                start_str = format_srt_time(start_time)
                end_str = format_srt_time(end_time)
                
                f.write(f"{idx + 1}\n{start_str} --> {end_str}\n{sentence}\n\n")
        
        logger.info(f"✅ Subtitles: {len(sentences)} segments")
        return srt_path
    except Exception as e:
        logger.error(f"Subtitle error: {e}")
        return None


def format_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def add_captions_to_video(input_video: str, srt_path: str, temp_dir: str) -> Optional[str]:
    output_video = os.path.join(temp_dir, "captioned_video.mp4")
    logger.info("💬 Adding captions...")
    
    srt_escaped = srt_path.replace('\\', '/').replace(':', '\\:')
    subtitles_filter = f"subtitles={srt_escaped}:force_style='Fontsize=24,PrimaryColour=&H00FFFF&,Bold=1,Outline=2,Shadow=1'"
    
    cmd = [
        "ffmpeg", "-i", input_video,
        "-vf", subtitles_filter,
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "copy",
        "-y", output_video
    ]
    
    if run_ffmpeg(cmd, FFMPEG_TIMEOUT):
        logger.info("✅ Captions added")
        return output_video
    return None


async def generate_voice_vertex_ai(text: str, temp_dir: str) -> Optional[str]:
    if not GOOGLE_VERTEX_API_KEY:
        return None
    
    try:
        import random, base64
        
        voice_config = random.choice(VERTEX_AI_HINDI_VOICES)
        logger.info(f"🔊 Vertex AI: {voice_config['description']}")
        
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
                "speakingRate": 1.15
            }
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload)
            
            if resp.status_code == 200:
                result = resp.json()
                
                if "audioContent" in result:
                    audio_content = base64.b64decode(result["audioContent"])
                    output_path = os.path.join(temp_dir, "vertex_voice.mp3")
                    
                    with open(output_path, 'wb') as f:
                        f.write(audio_content)
                    
                    logger.info(f"✅ Vertex AI voice: {get_size_mb(output_path):.2f}MB")
                    return output_path
    except Exception as e:
        logger.error(f"Vertex AI error: {e}")
    
    return None


async def generate_voice_tts(text: str, temp_dir: str) -> Optional[str]:
    # Try Vertex AI first
    logger.info("🎙️ Generating voice...")
    vertex_voice = await generate_voice_vertex_ai(text, temp_dir)
    if vertex_voice:
        return vertex_voice
    
    # Fallback to Edge TTS
    logger.info("🔄 Using Edge TTS...")
    try:
        import edge_tts
        
        output_path = os.path.join(temp_dir, "edge_voice.mp3")
        await edge_tts.Communicate(text[:1500], "hi-IN-MadhurNeural", rate="+15%").save(output_path)
        
        logger.info(f"✅ Edge TTS voice")
        return output_path
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
    
    return None


async def download_music(temp_dir: str, duration: float) -> Optional[str]:
    import random
    music_url = random.choice(BACKGROUND_MUSIC_URLS)
    logger.info("🎵 Downloading music...")
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.get(music_url)
            
            if resp.status_code == 200:
                raw_path = os.path.join(temp_dir, "music_raw.mp3")
                with open(raw_path, 'wb') as f:
                    f.write(resp.content)
                
                output_path = os.path.join(temp_dir, "music.mp3")
                cmd = ["ffmpeg", "-i", raw_path, "-t", str(min(duration, 60)), "-acodec", "copy", "-y", output_path]
                
                if run_ffmpeg(cmd, 60):
                    force_cleanup(raw_path)
                    logger.info(f"✅ Music ready")
                    return output_path
                
                return raw_path if os.path.exists(raw_path) else None
    except Exception as e:
        logger.error(f"Music error: {e}")
    
    return None


async def mix_video_audio(video_path: str, voice_path: str, music_path: Optional[str], temp_dir: str) -> Optional[str]:
    output_path = os.path.join(temp_dir, "final_video.mp4")
    logger.info("🎛️ Mixing audio...")
    
    try:
        if music_path:
            cmd = [
                "ffmpeg", "-i", video_path, "-i", voice_path, "-i", music_path,
                "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-y", output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-i", video_path, "-i", voice_path,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac",
                "-shortest", "-y", output_path
            ]
        
        if run_ffmpeg(cmd, FFMPEG_TIMEOUT):
            logger.info(f"✅ Final: {get_size_mb(output_path):.1f}MB")
            return output_path
    except Exception as e:
        logger.error(f"Mix error: {e}")
    
    return None


async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], user_id: str, database_manager) -> dict:
    try:
        logger.info("📤 Uploading to YouTube...")
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db or not yt_db.youtube.client:
            await yt_db.connect()
        
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not credentials_raw:
            return {"success": False, "error": "No YouTube credentials"}
        
        credentials = {
            "access_token": credentials_raw.get("access_token"),
            "refresh_token": credentials_raw.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": credentials_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": credentials_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        }
        
        from mainY import youtube_scheduler
        
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=description,
            video_url=video_path,
        )
        
        if upload_result.get("success"):
            video_id = upload_result.get("video_id")
            logger.info(f"✅ Uploaded: {video_id}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {"success": False, "error": upload_result.get("error", "Upload failed")}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def generate_mrbeast_short(youtube_url: str, user_id: str, database_manager, target_duration: int = 30) -> dict:
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="mrbeast_")
        logger.info(f"🎬 START: {youtube_url}")
        
        # Download video
        source_video, original_title, original_desc, transcript = await download_youtube_video(youtube_url, temp_dir)
        
        if not source_video:
            return {"success": False, "error": "Video download failed - all methods exhausted"}
        
        # Generate metadata
        ai_metadata = await generate_ai_title_description(original_title, transcript, original_desc)
        title = ai_metadata["title"]
        description = ai_metadata["description"]
        hashtags = ai_metadata["hashtags"]
        
        logger.info(f"📝 Title: {title}")
        
        # Generate script
        hindi_script = await generate_hindi_script(transcript, target_duration)
        
        # Process video
        resized_video = resize_video_to_shorts(source_video, temp_dir)
        if not resized_video:
            return {"success": False, "error": "Resize failed"}
        
        force_cleanup(source_video)
        
        overlay_video = add_overlay_effect(resized_video, temp_dir)
        if overlay_video:
            force_cleanup(resized_video)
            resized_video = overlay_video
        
        script_duration = len(hindi_script.split()) / 2.75
        srt_path = generate_subtitles_from_script(hindi_script, script_duration, temp_dir)
        
        if srt_path:
            captioned_video = add_captions_to_video(resized_video, srt_path, temp_dir)
            if captioned_video:
                force_cleanup(resized_video)
                resized_video = captioned_video
        
        voice_file = await generate_voice_tts(hindi_script, temp_dir)
        if not voice_file:
            return {"success": False, "error": "Voice generation failed"}
        
        music_file = await download_music(temp_dir, script_duration)
        
        final_video = await mix_video_audio(resized_video, voice_file, music_file, temp_dir)
        if not final_video:
            return {"success": False, "error": "Audio mixing failed"}
        
        final_size = get_size_mb(final_video)
        logger.info(f"✅ FINAL: {final_size:.1f}MB")
        
        # Upload
        upload_result = await upload_to_youtube(video_path=final_video, title=title, description=description, tags=hashtags, user_id=user_id, database_manager=database_manager)
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if upload_result.get("success"):
            return {
                "success": True,
                "video_id": upload_result["video_id"],
                "video_url": upload_result["video_url"],
                "title": title,
                "description": description,
                "hashtags": hashtags,
                "duration": f"{script_duration:.1f}s",
                "size_mb": f"{final_size:.1f}MB"
            }
        else:
            return {"success": False, "error": upload_result.get("error", "Upload failed")}
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTES
# ============================================================================

router = APIRouter()

@router.post("/api/mrbeast/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})
        
        youtube_url = data.get("youtube_url", "").strip()
        if not youtube_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "youtube_url required"})
        
        if not ("youtube.com" in youtube_url or "youtu.be" in youtube_url):
            return JSONResponse(status_code=400, content={"success": False, "error": "Invalid YouTube URL"})
        
        target_duration = max(20, min(data.get("target_duration", 30), 60))
        
        logger.info(f"📝 Request: url={youtube_url}, duration={target_duration}s, user={user_id}")
        
        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            generate_mrbeast_short(youtube_url, user_id, database_manager, target_duration),
            timeout=1800
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Request timeout"})
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']