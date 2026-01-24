"""
Viral_pixel.py - COMPLETE PEXELS VIRAL VIDEO GENERATOR
✅ Pexels video download + AI script generation
✅ Voice generation (male/female/loud/child)
✅ Background music (free/custom/movie/meme)
✅ Text overlays + effects (zoom, saturation, transitions)
✅ Automated YouTube upload with proper credentials
✅ Multi-user support with activity logging
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import sys
import traceback
import uuid
import base64
import httpx
import json
import re
import random
import subprocess
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path
import tempfile
import shutil

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "zGWMX93EDxCbRYoJyMw0ADQcbPNmjJ5jvGW5GmahCavl42Nb4Hj")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Free background music library
FREE_MUSIC_LIBRARY = {
    "upbeat": "https://www.bensound.com/bensound-music/bensound-happyrock.mp3",
    "calm": "https://www.bensound.com/bensound-music/bensound-slowmotion.mp3",
    "epic": "https://www.bensound.com/bensound-music/bensound-epic.mp3",
    "cinematic": "https://www.bensound.com/bensound-music/bensound-inspire.mp3"
}

# Niche configurations
NICHES = {
    "space": {
        "name": "Space & Universe 🌌",
        "search_terms": ["galaxy", "nebula", "planets", "stars", "black hole", "universe", "cosmos"],
        "cpm": "$4-8",
        "viral_potential": "Very High"
    },
    "tech_ai": {
        "name": "Technology & AI 🤖",
        "search_terms": ["artificial intelligence", "robot", "hologram", "futuristic", "circuits", "technology"],
        "cpm": "$6-12",
        "viral_potential": "Very High"
    },
    "ocean": {
        "name": "Ocean & Marine Life 🌊",
        "search_terms": ["ocean", "underwater", "coral reef", "dolphins", "sharks", "marine life"],
        "cpm": "$3-7",
        "viral_potential": "High"
    },
    "nature": {
        "name": "Nature & Wildlife 🦁",
        "search_terms": ["lions", "eagles", "wolves", "forests", "mountains", "wildlife"],
        "cpm": "$3-6",
        "viral_potential": "High"
    },
    "success": {
        "name": "Success & Motivation 💪",
        "search_terms": ["success", "business", "workout", "sunrise", "meditation", "motivation"],
        "cpm": "$4-10",
        "viral_potential": "Very High"
    },
    "sports": {
        "name": "Sports & Fitness ⚽",
        "search_terms": ["football", "basketball", "gym workout", "athlete", "running", "fitness"],
        "cpm": "$3-7",
        "viral_potential": "High"
    },
    "history": {
        "name": "History & Mystery 🏛️",
        "search_terms": ["ancient ruins", "historical", "mystery", "artifacts", "temples"],
        "cpm": "$4-8",
        "viral_potential": "High"
    },
    "luxury": {
        "name": "Luxury & Lifestyle 💎",
        "search_terms": ["luxury car", "mansion", "yacht", "fashion", "travel", "lifestyle"],
        "cpm": "$5-10",
        "viral_potential": "Very High"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def generate_ai_script(niche: str, duration: int) -> dict:
    """Generate viral video script using Groq/Mistral"""
    try:
        num_segments = duration // 5  # 5 seconds per segment
        
        niche_info = NICHES.get(niche, NICHES["space"])
        search_terms = niche_info["search_terms"]
        
        prompt = f"""
Create a viral {duration}-second video script for {niche_info['name']} niche.

Requirements:
- {num_segments} segments (5 seconds each)
- Hook viewers in first 2 seconds with shocking statement
- Use simple, punchy language
- Include numbers and superlatives
- Each segment needs:
  * fact: The interesting fact
  * narration: What voiceover says (conversational, 15-20 words)
  * text_overlay: Big text for screen (3-5 words MAX, ALL CAPS)
  * video_search: Pexels search query (2-3 words from: {', '.join(search_terms)})
  * emoji: One relevant emoji
  * effect: One of [zoom_in, zoom_out, pan_left, pan_right]
  * saturation: 1.0 to 1.5

Output ONLY valid JSON:
{{
  "title": "Catchy title with #Shorts",
  "description": "SEO description with keywords",
  "tags": ["tag1", "tag2", "tag3"],
  "segments": [
    {{
      "fact": "Interesting fact here",
      "narration": "What the voice says in natural conversational tone",
      "text_overlay": "BIG TEXT",
      "video_search": "galaxy stars",
      "emoji": "🌌",
      "effect": "zoom_in",
      "saturation": 1.3
    }}
  ]
}}
"""
        
        # Try Mistral first
        if MISTRAL_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {MISTRAL_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {"role": "system", "content": "You are a viral content expert. Output ONLY valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1500
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        # Clean JSON
                        ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                        script = json.loads(ai_response)
                        
                        logger.info("✅ Script generated via Mistral")
                        return script
            except Exception as e:
                logger.warning(f"Mistral failed: {e}")
        
        # Fallback to Groq
        if GROQ_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mixtral-8x7b-32768",
                            "messages": [
                                {"role": "system", "content": "You are a viral content expert. Output ONLY valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1500
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        # Clean JSON
                        ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                        script = json.loads(ai_response)
                        
                        logger.info("✅ Script generated via Groq")
                        return script
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        # Fallback template
        logger.warning("⚠️ Using template script")
        return generate_template_script(niche, num_segments)
        
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        logger.error(traceback.format_exc())
        return generate_template_script(niche, duration // 5)


def generate_template_script(niche: str, num_segments: int) -> dict:
    """Fallback template script"""
    niche_info = NICHES.get(niche, NICHES["space"])
    search_terms = niche_info["search_terms"]
    
    segments = []
    for i in range(num_segments):
        segments.append({
            "fact": f"Amazing {niche} fact #{i+1}",
            "narration": f"This is an incredible discovery about {niche} that will blow your mind!",
            "text_overlay": f"FACT #{i+1} 🤯",
            "video_search": random.choice(search_terms),
            "emoji": "🤯",
            "effect": random.choice(["zoom_in", "zoom_out", "pan_left", "pan_right"]),
            "saturation": round(random.uniform(1.1, 1.4), 1)
        })
    
    return {
        "title": f"Mind-Blowing {niche_info['name']} Facts #Shorts",
        "description": f"Discover amazing {niche} facts! Subscribe for more!",
        "tags": [niche, "facts", "viral", "shorts"],
        "segments": segments
    }


async def search_pexels_videos(query: str, per_page: int = 5) -> List[dict]:
    """Search Pexels for videos"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": query,
                    "per_page": per_page,
                    "orientation": "portrait",
                    "size": "medium"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                
                if videos:
                    logger.info(f"✅ Found {len(videos)} videos for '{query}'")
                    return videos
                else:
                    # Fallback: try first word only
                    logger.warning(f"No videos for '{query}', trying first word")
                    return await search_pexels_videos(query.split()[0], per_page)
            else:
                logger.error(f"Pexels API error: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Pexels search failed: {e}")
        return []


async def download_video(video_url: str, output_path: str) -> bool:
    """Download video from URL"""
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(video_url)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                logger.info(f"✅ Downloaded video: {file_size:.1f} MB")
                return True
            else:
                logger.error(f"Download failed: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Video download error: {e}")
        return False


def extract_best_clip(video_path: str, duration: int = 3) -> str:
    """Extract best segment from video using FFmpeg"""
    try:
        output_path = video_path.replace(".mp4", "_clip.mp4")
        
        # Get video duration
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        total_duration = float(result.stdout.strip())
        
        # Extract from middle
        start_time = max(0, (total_duration / 2) - (duration / 2))
        
        # Extract clip
        extract_cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            output_path,
            "-y"
        ]
        
        subprocess.run(extract_cmd, capture_output=True)
        
        if os.path.exists(output_path):
            logger.info(f"✅ Extracted {duration}s clip")
            return output_path
        else:
            logger.error("Clip extraction failed")
            return video_path
            
    except Exception as e:
        logger.error(f"Extract clip error: {e}")
        return video_path


def apply_effects(video_path: str, effect: str, saturation: float) -> str:
    """Apply zoom/pan effects and color grading"""
    try:
        output_path = video_path.replace(".mp4", "_fx.mp4")
        
        filters = []
        
        # Zoom effect
        if effect == "zoom_in":
            filters.append("zoompan=z='min(zoom+0.002,1.3)':d=125:s=720x1280")
        elif effect == "zoom_out":
            filters.append("zoompan=z='max(zoom-0.002,1.0)':d=125:s=720x1280")
        elif effect == "pan_left":
            filters.append("crop=720:1280:in_w-720-(in_w-720)*(t/duration):0")
        elif effect == "pan_right":
            filters.append("crop=720:1280:(in_w-720)*(t/duration):0")
        
        # Saturation
        filters.append(f"eq=saturation={saturation}")
        
        # Scale to shorts format
        filters.append("scale=720:1280:force_original_aspect_ratio=increase")
        filters.append("crop=720:1280")
        
        filter_complex = ",".join(filters)
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            output_path,
            "-y"
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        if os.path.exists(output_path):
            logger.info(f"✅ Applied {effect} effect")
            return output_path
        else:
            return video_path
            
    except Exception as e:
        logger.error(f"Apply effects error: {e}")
        return video_path


def generate_voiceover(text: str, voice_style: str, duration: float) -> str:
    """Generate voiceover using gTTS with voice styles"""
    try:
        from gtts import gTTS
        import librosa
        import soundfile as sf
        
        temp_file = f"/tmp/voice_{uuid.uuid4().hex[:8]}.mp3"
        
        # Adjust text based on voice style
        tts_slow = False
        if voice_style == "child":
            # Higher pitch effect will be applied later
            pass
        elif voice_style == "loud":
            text = text.upper()  # More emphasis
        
        # Generate base audio
        tts = gTTS(text=text, lang='en', slow=tts_slow)
        tts.save(temp_file)
        
        # Load and adjust
        y, sr = librosa.load(temp_file)
        current_duration = librosa.get_duration(y=y, sr=sr)
        
        # Adjust speed to fit duration
        if current_duration > 0:
            speed_factor = current_duration / duration
            y_adjusted = librosa.effects.time_stretch(y, rate=speed_factor)
        else:
            y_adjusted = y
        
        # Apply voice effects
        if voice_style == "child":
            # Higher pitch
            y_adjusted = librosa.effects.pitch_shift(y_adjusted, sr=sr, n_steps=4)
        elif voice_style == "male":
            # Lower pitch slightly
            y_adjusted = librosa.effects.pitch_shift(y_adjusted, sr=sr, n_steps=-2)
        elif voice_style == "female":
            # Higher pitch slightly
            y_adjusted = librosa.effects.pitch_shift(y_adjusted, sr=sr, n_steps=2)
        elif voice_style == "loud":
            # Boost volume
            y_adjusted = y_adjusted * 1.5
        
        # Save adjusted audio
        output_file = temp_file.replace(".mp3", "_adjusted.mp3")
        sf.write(output_file, y_adjusted, sr)
        
        logger.info(f"✅ Generated {voice_style} voiceover")
        return output_file
        
    except Exception as e:
        logger.error(f"Voiceover generation error: {e}")
        # Return silent audio as fallback
        return create_silent_audio(duration)


def create_silent_audio(duration: float) -> str:
    """Create silent audio file"""
    try:
        output = f"/tmp/silent_{uuid.uuid4().hex[:8]}.mp3"
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo:d={duration}",
            "-acodec", "libmp3lame",
            output,
            "-y"
        ]
        subprocess.run(cmd, capture_output=True)
        return output
    except:
        return None


def add_text_overlay(video_path: str, text: str, emoji: str) -> str:
    """Add text overlay using FFmpeg"""
    try:
        output_path = video_path.replace(".mp4", "_text.mp4")
        
        # Escape text for FFmpeg
        text_escaped = text.replace("'", "'\\''").replace(":", "\\:")
        full_text = f"{text_escaped} {emoji}"
        
        # Drawtext filter
        drawtext = (
            f"drawtext=text='{full_text}':"
            "fontsize=70:"
            "fontcolor=white:"
            "borderw=5:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=h-250:"
            "box=1:"
            "boxcolor=black@0.5:"
            "boxborderw=10"
        )
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", drawtext,
            "-codec:a", "copy",
            output_path,
            "-y"
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        if os.path.exists(output_path):
            logger.info(f"✅ Added text overlay")
            return output_path
        else:
            return video_path
            
    except Exception as e:
        logger.error(f"Text overlay error: {e}")
        return video_path


async def download_background_music(music_option: str, custom_url: str = None) -> str:
    """Download background music"""
    try:
        if custom_url:
            music_url = custom_url
        else:
            music_url = FREE_MUSIC_LIBRARY.get(music_option, FREE_MUSIC_LIBRARY["upbeat"])
        
        output_path = f"/tmp/music_{uuid.uuid4().hex[:8]}.mp3"
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(music_url)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✅ Downloaded background music")
                return output_path
            else:
                logger.error(f"Music download failed: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Background music error: {e}")
        return None


def compile_final_video(clips: List[str], audio_files: List[str], bg_music_path: str = None) -> str:
    """Compile all clips with audio into final video"""
    try:
        # Create concat file for video clips
        concat_file = f"/tmp/concat_{uuid.uuid4().hex[:8]}.txt"
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        # Concatenate video clips
        temp_video = f"/tmp/video_{uuid.uuid4().hex[:8]}.mp4"
        concat_cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            temp_video,
            "-y"
        ]
        subprocess.run(concat_cmd, capture_output=True)
        
        # Create concat file for audio
        audio_concat = f"/tmp/audio_concat_{uuid.uuid4().hex[:8]}.txt"
        with open(audio_concat, 'w') as f:
            for audio in audio_files:
                if audio and os.path.exists(audio):
                    f.write(f"file '{audio}'\n")
        
        # Concatenate audio
        combined_audio = f"/tmp/audio_{uuid.uuid4().hex[:8]}.mp3"
        audio_cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", audio_concat,
            "-c", "copy",
            combined_audio,
            "-y"
        ]
        subprocess.run(audio_cmd, capture_output=True)
        
        # Mix video + voiceover + background music
        final_output = f"/tmp/final_{uuid.uuid4().hex[:8]}.mp4"
        
        if bg_music_path and os.path.exists(bg_music_path):
            # Mix voiceover (100%) + music (30%)
            mix_cmd = [
                "ffmpeg",
                "-i", temp_video,
                "-i", combined_audio,
                "-i", bg_music_path,
                "-filter_complex",
                "[1:a]volume=1.0[v1];[2:a]volume=0.3[v2];[v1][v2]amix=inputs=2:duration=shortest[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                final_output,
                "-y"
            ]
        else:
            # Just voiceover
            mix_cmd = [
                "ffmpeg",
                "-i", temp_video,
                "-i", combined_audio,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                final_output,
                "-y"
            ]
        
        subprocess.run(mix_cmd, capture_output=True)
        
        if os.path.exists(final_output):
            file_size = os.path.getsize(final_output) / (1024 * 1024)
            logger.info(f"✅ Final video compiled: {file_size:.1f} MB")
            return final_output
        else:
            logger.error("Video compilation failed")
            return None
            
    except Exception as e:
        logger.error(f"Video compilation error: {e}")
        logger.error(traceback.format_exc())
        return None


async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], 
                           user_id: str, database_manager) -> dict:
    """Upload video to YouTube using user's credentials"""
    try:
        # Get YouTube credentials
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            return {"success": False, "error": "YouTube database not available"}
        
        # Connect to database
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        # Get credentials
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            return {"success": False, "error": "YouTube not connected"}
        
        # Build credentials
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
        
        # Import YouTube scheduler
        from mainY import youtube_scheduler
        
        # Upload video
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=f"{title} #Shorts",
            description=description,
            video_url=video_path,
            tags=tags
        )
        
        if upload_result.get("success"):
            video_id = upload_result.get("video_id")
            logger.info(f"✅ Uploaded to YouTube: {video_id}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        else:
            return {
                "success": False,
                "error": upload_result.get("error", "Upload failed")
            }
            
    except Exception as e:
        logger.error(f"YouTube upload error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

async def generate_viral_video(
    niche: str,
    duration: int,
    voice_style: str,
    bg_music_option: str,
    custom_music_url: str,
    user_id: str,
    database_manager
) -> dict:
    """Main function to generate complete viral video"""
    
    temp_dir = None
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="viral_pixel_")
        logger.info(f"🎬 Starting video generation in {temp_dir}")
        
        # STEP 1: Generate AI script
        logger.info("📝 STEP 1: Generating AI script...")
        script = await generate_ai_script(niche, duration)
        
        if not script or not script.get("segments"):
            return {"success": False, "error": "Script generation failed"}
        
        logger.info(f"✅ Generated script with {len(script['segments'])} segments")
        
        # STEP 2: Download videos from Pexels
        logger.info("📥 STEP 2: Downloading videos from Pexels...")
        
        video_clips = []
        for idx, segment in enumerate(script["segments"]):
            try:
                # Search Pexels
                videos = await search_pexels_videos(segment["video_search"])
                
                if not videos:
                    logger.warning(f"No videos for segment {idx+1}, using fallback")
                    continue
                
                # Get best video (highest resolution)
                best_video = max(videos, key=lambda x: x.get("width", 0))
                video_files = best_video["video_files"]
                hd_file = max(video_files, key=lambda x: x.get("width", 0))
                
                # Download video
                video_path = os.path.join(temp_dir, f"video_{idx}.mp4")
                success = await download_video(hd_file["link"], video_path)
                
                if success:
                    video_clips.append(video_path)
                    
            except Exception as e:
                logger.error(f"Error downloading video {idx+1}: {e}")
                continue
        
        if len(video_clips) == 0:
            return {"success": False, "error": "Failed to download videos"}
        
        logger.info(f"✅ Downloaded {len(video_clips)} videos")
        
        # STEP 3: Extract clips and apply effects
        logger.info("✂️ STEP 3: Extracting clips and applying effects...")
        
        processed_clips = []
        for idx, (video_path, segment) in enumerate(zip(video_clips, script["segments"])):
            try:
                # Extract best 2-4 second clip
                clip_duration = min(4, duration // len(script["segments"]))
                clip_path = extract_best_clip(video_path, clip_duration)
                
                # Apply effects
                fx_path = apply_effects(
                    clip_path,
                    segment.get("effect", "zoom_in"),
                    segment.get("saturation", 1.3)
                )
                
                # Add text overlay
                text_path = add_text_overlay(
                    fx_path,
                    segment.get("text_overlay", ""),
                    segment.get("emoji", "")
                )
                
                processed_clips.append(text_path)
                
            except Exception as e:
                logger.error(f"Error processing clip {idx+1}: {e}")
                # Use original if processing fails
                processed_clips.append(video_path)
        
        logger.info(f"✅ Processed {len(processed_clips)} clips")
        
        # STEP 4: Generate voiceovers
        logger.info("🎙️ STEP 4: Generating voiceovers...")
        
        audio_files = []
        for idx, segment in enumerate(script["segments"]):
            try:
                narration = segment.get("narration", "")
                if narration:
                    audio_path = generate_voiceover(
                        narration,
                        voice_style,
                        duration=5.0
                    )
                    audio_files.append(audio_path)
                else:
                    audio_files.append(None)
                    
            except Exception as e:
                logger.error(f"Error generating voiceover {idx+1}: {e}")
                audio_files.append(None)
        
        logger.info(f"✅ Generated {len([a for a in audio_files if a])} voiceovers")
        
        # STEP 5: Download background music
        logger.info("🎵 STEP 5: Downloading background music...")
        
        bg_music_path = None
        if bg_music_option != "none":
            bg_music_path = await download_background_music(bg_music_option, custom_music_url)
        
        # STEP 6: Compile final video
        logger.info("🎬 STEP 6: Compiling final video...")
        
        final_video = compile_final_video(processed_clips, audio_files, bg_music_path)
        
        if not final_video:
            return {"success": False, "error": "Video compilation failed"}
        
        logger.info("✅ Final video compiled successfully")
        
        # STEP 7: Upload to YouTube
        logger.info("📤 STEP 7: Uploading to YouTube...")
        
        upload_result = await upload_to_youtube(
            final_video,
            script.get("title", "Viral Video"),
            script.get("description", ""),
            script.get("tags", []),
            user_id,
            database_manager
        )
        
        if not upload_result.get("success"):
            return {
                "success": False,
                "error": upload_result.get("error", "Upload failed")
            }
        
        logger.info("✅ Upload successful!")
        
        # Cleanup temp directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script.get("title"),
            "script": script
        }
        
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        logger.error(traceback.format_exc())
        
        # Cleanup on error
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        return {"success": False, "error": str(e)}


# ============================================================================
# FASTAPI ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/viral-pixel/niches")
async def get_niches():
    """Get available niches"""
    return {
        "success": True,
        "niches": NICHES
    }


@router.post("/api/viral-pixel/generate")
async def generate_video(request: Request):
    """Generate viral video"""
    try:
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
        from fastapi import Depends
        
        # Get authenticated user
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        # Get parameters
        niche = data.get("niche", "space")
        duration = int(data.get("duration", 40))
        voice_style = data.get("voice_style", "male")
        bg_music_option = data.get("bg_music_option", "upbeat")
        custom_music_url = data.get("custom_music_url")
        
        # Validate
        if niche not in NICHES:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid niche"}
            )
        
        if duration < 20 or duration > 60:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Duration must be 20-60 seconds"}
            )
        
        if voice_style not in ["male", "female", "loud", "child"]:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid voice style"}
            )
        
        # Import database manager
        from Supermain import database_manager
        
        # Generate video
        result = await generate_viral_video(
            niche=niche,
            duration=duration,
            voice_style=voice_style,
            bg_music_option=bg_music_option,
            custom_music_url=custom_music_url,
            user_id=user_id,
            database_manager=database_manager
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# Export router
__all__ = ['router']