"""
MrBeast_Shorts_Generator.py - COMPLETE VIRAL SHORTS AUTOMATION
================================================================
✅ Download YouTube Short/Video
✅ Extract transcript using Whisper (Groq)
✅ AI Creative Rewrite (avoid copyright)
✅ Generate Hindi voiceover (ElevenLabs 1.1x speed)
✅ Add dynamic captions & text overlays
✅ Crop + Zoom effects (9:16 vertical)
✅ Add background music from GitHub
✅ Auto-upload to YouTube Shorts
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
import textwrap

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# Voice Configuration
HINDI_VOICE_ID = "WXTRkeANkY97koU9TGhC"  # Male Energetic Hindi

# Video Settings
MIN_DURATION = 20
MAX_DURATION = 55
FFMPEG_TIMEOUT = 180

# Output Format (9:16 for Shorts)
OUTPUT_WIDTH = 720
OUTPUT_HEIGHT = 1280
FPS = 30

# Background Music URLs (GitHub)
BG_MUSIC_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(14).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(10).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(13).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(15).weba"
]

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def force_cleanup(*filepaths):
    """Delete files and free memory"""
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
    """Run FFmpeg command with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        gc.collect()
        return result.returncode == 0
    except:
        gc.collect()
        return False

# ============================================================================
# STEP 1: DOWNLOAD YOUTUBE VIDEO
# ============================================================================

async def download_youtube_video(url: str, temp_dir: str) -> Optional[str]:
    """Download YouTube video/short using yt-dlp"""
    try:
        output_path = os.path.join(temp_dir, "original.mp4")
        
        logger.info(f"📥 Downloading from: {url}")
        
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            url
        ]
        
        process = subprocess.run(cmd, capture_output=True, timeout=300, check=False)
        
        if process.returncode != 0:
            logger.error(f"yt-dlp error: {process.stderr.decode()}")
            return None
        
        if not os.path.exists(output_path):
            return None
        
        size_mb = get_file_size_mb(output_path)
        logger.info(f"✅ Downloaded: {size_mb:.1f}MB")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None

# ============================================================================
# STEP 2: GET VIDEO DURATION
# ============================================================================

def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=10, check=False)
        
        if result.returncode == 0:
            duration = float(result.stdout.decode().strip())
            logger.info(f"📏 Duration: {duration:.1f}s")
            return duration
        
        return 0
        
    except Exception as e:
        logger.error(f"Duration check error: {e}")
        return 0

# ============================================================================
# STEP 3: EXTRACT TRANSCRIPT USING WHISPER
# ============================================================================

async def extract_transcript(video_path: str, temp_dir: str) -> Optional[str]:
    """Extract audio and transcribe using Groq Whisper"""
    try:
        # Extract audio
        audio_path = os.path.join(temp_dir, "audio.mp3")
        
        logger.info("🎤 Extracting audio...")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "libmp3lame",
            "-b:a", "128k", "-ar", "16000",
            "-y", audio_path
        ]
        
        if not run_ffmpeg(cmd, 60):
            logger.error("Audio extraction failed")
            return None
        
        logger.info("🧠 Transcribing with Whisper...")
        
        if not GROQ_API_KEY:
            logger.error("GROQ_API_KEY not set")
            return None
        
        async with httpx.AsyncClient(timeout=120) as client:
            with open(audio_path, 'rb') as audio_file:
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files={"file": ("audio.mp3", audio_file, "audio/mpeg")},
                    data={
                        "model": "whisper-large-v3",
                        "response_format": "verbose_json",
                        "temperature": 0
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("text", "")
                
                force_cleanup(audio_path)
                
                logger.info(f"✅ Transcript: {len(transcript)} chars")
                logger.info(f"📝 Preview: {transcript[:200]}...")
                
                return transcript
            else:
                logger.error(f"Whisper API error: {response.status_code}")
                return None
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None

# ============================================================================
# STEP 4: AI CREATIVE REWRITE (AVOID COPYRIGHT)
# ============================================================================

async def rewrite_script_creatively(original_transcript: str, target_duration: int) -> dict:
    """Use AI to creatively rewrite script to avoid copyright"""
    try:
        logger.info("✍️ AI Creative Rewrite...")
        
        # Calculate word count based on duration
        target_words = int(target_duration * 2.75)  # ~2.75 words per second
        
        prompt = f"""Rewrite this transcript into VIRAL HINDI script for YouTube Shorts:

ORIGINAL TRANSCRIPT:
"{original_transcript}"

TARGET DURATION: {target_duration} seconds (~{target_words} words)

REWRITE RULES:
1. Convert to HINDI language (Hinglish OK for modern terms)
2. Keep the core story/message but CHANGE WORDING completely
3. Make it MORE engaging and dramatic
4. Add hooks at start: "Suniye kya hua...", "Dekhiye kaise...", "Yeh dekh kar yakeen nahi hoga..."
5. Use emotional words: "amazing", "shocking", "unbelievable"
6. Natural Hindi flow with commas for pauses
7. NO word "pause" - use commas/exclamations
8. End with CTA: "LIKE karein, SUBSCRIBE karein aur SHARE karein!"
9. Keep length around {target_words} words

IMPORTANT: This is a CREATIVE REWRITE, not translation. Change sentence structure, use different examples, add dramatic flair!

Output ONLY valid JSON:
{{
    "script": "Hindi rewritten script here...",
    "title": "Viral Hindi Title (3-6 words)",
    "hook": "Opening hook line"
}}"""

        # Try Mistral first (better for creative rewrites)
        if MISTRAL_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=45) as client:
                    response = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {MISTRAL_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a viral content creator. Rewrite scripts creatively in Hindi. Output ONLY valid JSON."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.85
                        }
                    )
                    
                    if response.status_code == 200:
                        content = response.json()["choices"][0]["message"]["content"]
                        content = re.sub(r'```json\n?|\n?```', '', content).strip()
                        
                        result = json.loads(content)
                        
                        script = result.get("script", "")
                        title = result.get("title", "Viral Short")
                        hook = result.get("hook", "")
                        
                        logger.info(f"✅ Rewritten: {len(script)} chars")
                        logger.info(f"📌 Title: {title}")
                        
                        return {
                            "script": script,
                            "title": title,
                            "hook": hook
                        }
            
            except Exception as e:
                logger.warning(f"Mistral error: {e}")
        
        # Fallback to Groq
        if GROQ_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=45) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Rewrite scripts creatively in Hindi. Output ONLY JSON."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.85
                        }
                    )
                    
                    if response.status_code == 200:
                        content = response.json()["choices"][0]["message"]["content"]
                        content = re.sub(r'```json\n?|\n?```', '', content).strip()
                        
                        result = json.loads(content)
                        
                        return {
                            "script": result.get("script", ""),
                            "title": result.get("title", "Viral Short"),
                            "hook": result.get("hook", "")
                        }
            
            except Exception as e:
                logger.warning(f"Groq error: {e}")
        
        # Final fallback
        return {
            "script": f"Suniye yeh amazing story... {original_transcript[:200]}... LIKE karein aur SUBSCRIBE karein!",
            "title": "Viral Short",
            "hook": "Suniye yeh amazing story"
        }
        
    except Exception as e:
        logger.error(f"Rewrite error: {e}")
        return {
            "script": original_transcript[:500],
            "title": "Short Video",
            "hook": ""
        }

# ============================================================================
# STEP 5: GENERATE HINDI VOICEOVER (1.1x SPEED)
# ============================================================================

async def generate_hindi_voiceover_11x(text: str, temp_dir: str) -> Optional[str]:
    """Generate Hindi voiceover at 1.1x speed using ElevenLabs"""
    try:
        logger.info("🎙️ Generating Hindi voiceover (1.1x)...")
        
        # Try ElevenLabs
        if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
            output_base = os.path.join(temp_dir, "voice_base.mp3")
            output_final = os.path.join(temp_dir, "voice.mp3")
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{HINDI_VOICE_ID}",
                    headers={
                        "xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text[:2500],
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.8,
                            "style": 0.6,
                            "use_speaker_boost": True
                        }
                    }
                )
                
                if response.status_code == 200:
                    with open(output_base, 'wb') as f:
                        f.write(response.content)
                    
                    # Apply 1.1x speed + normalize audio
                    cmd = [
                        "ffmpeg", "-i", output_base,
                        "-filter:a", "atempo=1.1,loudnorm=I=-16:TP=-1.5",
                        "-y", output_final
                    ]
                    
                    if run_ffmpeg(cmd, 30):
                        force_cleanup(output_base)
                        logger.info(f"✅ ElevenLabs voice (1.1x): {get_file_size_mb(output_final):.2f}MB")
                        return output_final
                    
                    force_cleanup(output_base)
        
        # Fallback to Edge TTS
        logger.info("Using Edge TTS (free fallback)...")
        return await generate_edge_tts_11x(text, temp_dir)
        
    except Exception as e:
        logger.error(f"Voiceover error: {e}")
        return await generate_edge_tts_11x(text, temp_dir)

async def generate_edge_tts_11x(text: str, temp_dir: str) -> Optional[str]:
    """Free Hindi TTS at 1.1x speed using Edge"""
    try:
        import edge_tts
        
        output_base = os.path.join(temp_dir, "edge_base.mp3")
        output_final = os.path.join(temp_dir, "edge_voice.mp3")
        
        # Use Hindi male voice
        communicate = edge_tts.Communicate(
            text[:2000],
            "hi-IN-MadhurNeural",
            rate="+10%",
            pitch="+2Hz"
        )
        await communicate.save(output_base)
        
        # Apply 1.1x speed
        cmd = [
            "ffmpeg", "-i", output_base,
            "-filter:a", "atempo=1.1,loudnorm=I=-16:TP=-1.5",
            "-y", output_final
        ]
        
        if run_ffmpeg(cmd, 25):
            force_cleanup(output_base)
            logger.info(f"✅ Edge TTS (1.1x): {get_file_size_mb(output_final):.2f}MB")
            return output_final
        
        return None
        
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
        return None

# ============================================================================
# STEP 6: DOWNLOAD & PROCESS BACKGROUND MUSIC
# ============================================================================

async def download_background_music(temp_dir: str, duration: float) -> Optional[str]:
    """Download and process background music from GitHub"""
    try:
        music_url = random.choice(BG_MUSIC_URLS)
        logger.info(f"🎵 Downloading music: {music_url}")
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            response = await client.get(music_url)
            
            if response.status_code == 200:
                raw_path = os.path.join(temp_dir, "music_raw.weba")
                with open(raw_path, 'wb') as f:
                    f.write(response.content)
                
                # Convert .weba to .mp3
                mp3_path = os.path.join(temp_dir, "music.mp3")
                
                cmd = [
                    "ffmpeg", "-i", raw_path,
                    "-vn", "-acodec", "libmp3lame",
                    "-b:a", "128k",
                    "-t", str(duration + 2),
                    "-y", mp3_path
                ]
                
                if run_ffmpeg(cmd, 60):
                    force_cleanup(raw_path)
                    logger.info(f"✅ Music: {get_file_size_mb(mp3_path):.2f}MB")
                    return mp3_path
                
                return None
        
    except Exception as e:
        logger.error(f"Music download error: {e}")
        return None

# ============================================================================
# STEP 7: CROP VIDEO TO 9:16 WITH ZOOM EFFECTS
# ============================================================================

def crop_and_zoom_video(video_path: str, temp_dir: str) -> Optional[str]:
    """Crop video from top/bottom to 9:16 format with zoom effects"""
    try:
        output_path = os.path.join(temp_dir, "cropped_zoomed.mp4")
        
        logger.info("✂️ Cropping to 9:16 with zoom effects...")
        
        # Complex filter:
        # 1. Scale to fit width
        # 2. Crop from top/bottom to 9:16
        # 3. Add zoom animation (1.0 to 1.15x gradually)
        # 4. Apply slight Ken Burns effect
        
        filter_complex = (
            "[0:v]"
            "scale=720:-1,"  # Scale to 720px width
            "crop=720:1280:0:(ih-1280)/2,"  # Crop to 9:16 from center
            "zoompan=z='min(1.15,1.0+(on/1000*0.15))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=30,"  # Gradual zoom
            "eq=contrast=1.05:brightness=0.03:saturation=1.1"  # Enhance colors
            "[v]"
        )
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "medium",
            "-r", "30",
            "-an",  # Remove audio (we'll add it later)
            "-y", output_path
        ]
        
        if run_ffmpeg(cmd, 180):
            logger.info(f"✅ Cropped & zoomed: {get_file_size_mb(output_path):.1f}MB")
            return output_path
        
        return None
        
    except Exception as e:
        logger.error(f"Crop/zoom error: {e}")
        return None

# ============================================================================
# STEP 8: ADD CAPTIONS & TEXT OVERLAYS
# ============================================================================

def add_captions_to_video(video_path: str, script_text: str, hook: str, temp_dir: str) -> Optional[str]:
    """Add dynamic captions and text overlays to video"""
    try:
        output_path = os.path.join(temp_dir, "captioned.mp4")
        
        logger.info("📝 Adding captions & text overlays...")
        
        # Clean text for FFmpeg
        clean_text = script_text.replace("'", "").replace('"', '').replace(':', ' -')
        
        # Split into chunks for scrolling effect
        words = clean_text.split()
        chunks = [' '.join(words[i:i+8]) for i in range(0, len(words), 8)]
        
        # Use first chunk or hook as main text
        main_text = hook if hook else chunks[0] if chunks else clean_text[:60]
        main_text = main_text[:80]  # Limit length
        
        # Create filter with text overlay
        # Position: bottom third of screen
        # Style: White text with black border
        filter_str = (
            f"drawtext="
            f"text='{main_text}':"
            f"fontsize=42:"
            f"fontcolor=white:"
            f"x=(w-text_w)/2:"
            f"y=h-300:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"shadowcolor=black@0.8:"
            f"shadowx=3:"
            f"shadowy=3:"
            f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        )
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", filter_str,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "medium",
            "-c:a", "copy",
            "-y", output_path
        ]
        
        if run_ffmpeg(cmd, 120):
            logger.info(f"✅ Captions added: {get_file_size_mb(output_path):.1f}MB")
            return output_path
        
        return None
        
    except Exception as e:
        logger.error(f"Caption error: {e}")
        return None

# ============================================================================
# STEP 9: COMBINE VIDEO + VOICEOVER + MUSIC
# ============================================================================

async def combine_video_voice_music(
    video_path: str,
    voice_path: str,
    music_path: Optional[str],
    temp_dir: str
) -> Optional[str]:
    """Combine video with voiceover and background music"""
    try:
        output_path = os.path.join(temp_dir, "final.mp4")
        
        logger.info("🎬 Combining video + voice + music...")
        
        if music_path:
            # Mix voiceover (loud) + background music (quiet)
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-i", voice_path,
                "-i", music_path,
                "-filter_complex",
                "[1:a]volume=1.0[voice];[2:a]volume=0.10[music];[voice][music]amix=inputs=2:duration=first[audio]",
                "-map", "0:v",
                "-map", "[audio]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", output_path
            ]
        else:
            # Just add voiceover
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-i", voice_path,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-y", output_path
            ]
        
        if run_ffmpeg(cmd, 120):
            logger.info(f"✅ Final video: {get_file_size_mb(output_path):.1f}MB")
            return output_path
        
        return None
        
    except Exception as e:
        logger.error(f"Combine error: {e}")
        return None

# ============================================================================
# STEP 10: UPLOAD TO YOUTUBE
# ============================================================================

async def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    user_id: str,
    database_manager
) -> dict:
    """Upload video to YouTube using Viral Pixel's working logic"""
    try:
        logger.info("📤 Connecting to YouTube...")
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db or not yt_db.youtube.client:
            await yt_db.connect()
        
        # Get credentials
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            return {"success": False, "error": "YouTube credentials not found"}
        
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
        
        # Add hashtags to description
        full_description = f"{description}\n\n#shorts #viral #trending #hindi"
        
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=full_description,
            video_url=video_path
        )
        
        if upload_result.get("success"):
            video_id = upload_result.get("video_id")
            
            logger.info(f"✅ Uploaded! Video ID: {video_id}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {
            "success": False,
            "error": upload_result.get("error", "Upload failed")
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

async def generate_mrbeast_short(
    youtube_url: str,
    target_duration: int,
    user_id: str,
    database_manager
) -> dict:
    """Main function to generate MrBeast-style short"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="mrbeast_")
        logger.info(f"🎬 MrBeast Short Generator Started")
        logger.info(f"URL: {youtube_url}")
        logger.info(f"Duration: {target_duration}s")
        
        # Step 1: Download video
        video_path = await download_youtube_video(youtube_url, temp_dir)
        if not video_path:
            return {"success": False, "error": "Failed to download video"}
        
        # Step 2: Get duration
        duration = get_video_duration(video_path)
        if duration < target_duration:
            return {"success": False, "error": f"Video too short: {duration:.0f}s"}
        
        # Step 3: Extract transcript
        transcript = await extract_transcript(video_path, temp_dir)
        if not transcript:
            return {"success": False, "error": "Failed to extract transcript"}
        
        # Step 4: AI Creative Rewrite
        rewrite_result = await rewrite_script_creatively(transcript, target_duration)
        script_text = rewrite_result["script"]
        title = rewrite_result["title"]
        hook = rewrite_result["hook"]
        
        # Step 5: Generate voiceover (1.1x speed)
        voice_path = await generate_hindi_voiceover_11x(script_text, temp_dir)
        if not voice_path:
            return {"success": False, "error": "Voiceover generation failed"}
        
        # Step 6: Download background music
        music_path = await download_background_music(temp_dir, target_duration)
        
        # Step 7: Crop & zoom video to 9:16
        cropped_path = crop_and_zoom_video(video_path, temp_dir)
        if not cropped_path:
            return {"success": False, "error": "Video cropping failed"}
        
        force_cleanup(video_path)  # Remove original
        
        # Step 8: Add captions & text overlays
        captioned_path = add_captions_to_video(cropped_path, script_text, hook, temp_dir)
        if not captioned_path:
            return {"success": False, "error": "Caption addition failed"}
        
        force_cleanup(cropped_path)
        
        # Step 9: Combine video + voice + music
        final_video = await combine_video_voice_music(
            captioned_path,
            voice_path,
            music_path,
            temp_dir
        )
        
        if not final_video:
            return {"success": False, "error": "Final video creation failed"}
        
        final_size = get_file_size_mb(final_video)
        logger.info(f"✅ Final video ready: {final_size:.1f}MB")
        
        # Step 10: Upload to YouTube
        upload_result = await upload_to_youtube(
            final_video,
            title,
            script_text,
            user_id,
            database_manager
        )
        
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
                "script": script_text[:200] + "...",
                "duration": f"{target_duration}s",
                "size": f"{final_size:.1f}MB"
            }
        else:
            return {
                "success": False,
                "error": upload_result.get("error", "Upload failed")
            }
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/api/mrbeast/generate")
async def generate_endpoint(request: Request):
    """Generate MrBeast-style viral short"""
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        youtube_url = data.get("youtube_url", "")
        target_duration = int(data.get("target_duration", 30))
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        if not youtube_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "YouTube URL required"}
            )
        
        # Validate URL
        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid YouTube URL"}
            )
        
        # Validate duration
        if not (MIN_DURATION <= target_duration <= MAX_DURATION):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Duration must be {MIN_DURATION}-{MAX_DURATION}s"
                }
            )
        
        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            generate_mrbeast_short(
                youtube_url=youtube_url,
                target_duration=target_duration,
                user_id=user_id,
                database_manager=database_manager
            ),
            timeout=900  # 15 minutes
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={"success": False, "error": "Generation timeout"}
        )
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Export router
__all__ = ['router']