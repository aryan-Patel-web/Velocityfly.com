"""
pixabay_enhanced.py - AI-POWERED IMAGE SLIDESHOW GENERATOR
==================================================
✅ Multi-keyword smart image search (no repetition)
✅ ElevenLabs Premium Voice (Hindi/English)
✅ Niche-based emotional storytelling
✅ Text overlays on images (1-2 words)
✅ Professional transitions & effects
✅ Horror/Dark/Upbeat background music
✅ Direct YouTube upload
==================================================
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
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & API KEYS
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ ELEVENLABS API KEY
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# GOOGLE VERTEX AI (FALLBACK)
GOOGLE_API_KEY = os.getenv("GOOGLE_VERTEX_API_KEY", "")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "socialauto-472509")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")

# PROCESSING LIMITS
MAX_VIDEO_SIZE_MB = 40
FFMPEG_TIMEOUT = 300
TARGET_DURATION = 30
CHUNK_SIZE = 65536

# IMAGE SLIDESHOW CONFIGURATION
MIN_IMAGES = 6
MAX_IMAGES = 8
IMAGE_DURATION = 3.5  # 3.5 seconds per image
IMAGE_TARGET_WIDTH = 720
IMAGE_TARGET_HEIGHT = 1280
FPS = 30

# ============================================================================
# NICHE KEYWORDS - MULTI-KEYWORD STRATEGY
# ============================================================================
NICHE_KEYWORDS = {
    "space": {
        "keywords": ["galaxy", "nebula", "planet", "cosmos", "stars", "universe", 
                    "black hole", "milky way", "supernova", "asteroid"],
        "emotion": "wonder",
        "music_style": "epic",
        "voice_style": "mysterious"
    },
    "funny": {
        "keywords": ["funny animals", "cute pets", "comedy", "hilarious", "meme", 
                    "pranks", "bloopers", "fun", "smile", "laugh"],
        "emotion": "joy",
        "music_style": "upbeat",
        "voice_style": "cheerful"
    },
    "nature": {
        "keywords": ["mountain", "forest", "waterfall", "sunset", "river", 
                    "landscape", "wildlife", "canyon", "valley", "ocean"],
        "emotion": "peace",
        "music_style": "calm",
        "voice_style": "soothing"
    },
    "motivation": {
        "keywords": ["success", "achievement", "victory", "growth", "meditation", 
                    "sunrise", "workout", "focus", "strength", "mindset"],
        "emotion": "inspiration",
        "music_style": "energetic",
        "voice_style": "powerful"
    },
    "storytelling": {
        "keywords": ["ancient", "mystery", "secret", "temple", "ruins", 
                    "artifact", "history", "legend", "treasure", "adventure"],
        "emotion": "curiosity",
        "music_style": "cinematic",
        "voice_style": "dramatic"
    }
}

# ============================================================================
# ELEVENLABS VOICE CONFIGURATION
# ============================================================================
ELEVENLABS_VOICES = {
    "hindi_male": "pNInz6obpgDQGcFmaJgB",  # Adam - clear, energetic
    "hindi_female": "21m00Tcm4TlvDq8ikWAM",  # Rachel - warm, friendly
    "english_male": "TxGEqnHWrfWFTfGW9XjX",  # Josh - deep, authoritative
    "english_female": "jsCqWAovK2LkecY7zXl4",  # Freya - cheerful
}

# CANVA-STYLE TRANSITIONS
TRANSITIONS = [
    {
        "name": "zoom_out_center",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.8,max(1.001,zoom-0.008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"
    },
    {
        "name": "zoom_out_fade",
        "filter": "zoompan=z='if(lte(zoom,1.0),2.0,max(1.001,zoom-0.01))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps},fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out_start}:d=0.3"
    },
    {
        "name": "zoom_out_pan_right",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.6,max(1.001,zoom-0.007))':d={frames}:x='iw/2-(iw/zoom/2)+(t*15)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"
    }
]

# BACKGROUND MUSIC URLs (expanded)
BACKGROUND_MUSIC_URLS = {
    "horror": [
        "https://freesound.org/data/previews/614/614090_11931419-lq.mp3",
        "https://freesound.org/data/previews/543/543995_11587873-lq.mp3"
    ],
    "epic": [
        "https://freesound.org/data/previews/632/632351_10755880-lq.mp3",
        "https://freesound.org/data/previews/558/558262_11587873-lq.mp3"
    ],
    "upbeat": [
        "https://freesound.org/data/previews/521/521495_9961799-lq.mp3",
        "https://freesound.org/data/previews/477/477718_9497060-lq.mp3"
    ],
    "calm": [
        "https://freesound.org/data/previews/456/456966_9497060-lq.mp3",
        "https://freesound.org/data/previews/398/398787_7517113-lq.mp3"
    ],
    "energetic": [
        "https://freesound.org/data/previews/521/521495_9961799-lq.mp3"
    ],
    "cinematic": [
        "https://freesound.org/data/previews/632/632351_10755880-lq.mp3"
    ]
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def force_cleanup(*filepaths):
    """Force cleanup of files with garbage collection"""
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
                logger.info(f"🗑️ Cleaned: {os.path.basename(fp)}")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
    gc.collect()

def get_size_mb(fp: str) -> float:
    """Get file size in megabytes"""
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0.0

def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """Run FFmpeg command with timeout"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            timeout=timeout, 
            check=False, 
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error (code {result.returncode})")
            logger.error(f"FFmpeg stderr: {result.stderr[:500]}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ FFmpeg timeout after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"FFmpeg exception: {e}")
        return False

# ============================================================================
# SMART IMAGE SEARCH - NO REPETITION
# ============================================================================

async def search_pixabay_smart(niche: str, count: int) -> List[dict]:
    """
    Smart multi-keyword search to avoid repetition
    Example: space → [galaxy, nebula, planet, black hole, ...]
    """
    logger.info(f"🔍 Smart search for niche: {niche}")
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    keywords = niche_data["keywords"]
    
    all_images = []
    seen_urls = set()
    
    # Randomize keyword order
    shuffled_keywords = random.sample(keywords, len(keywords))
    
    images_per_keyword = max(2, count // len(keywords))
    
    for keyword in shuffled_keywords:
        if len(all_images) >= count:
            break
        
        logger.info(f"   🔍 Searching: '{keyword}'")
        
        try:
            async with httpx.AsyncClient(timeout=25) as client:
                resp = await client.get(
                    "https://pixabay.com/api/",
                    params={
                        "key": PIXABAY_API_KEY,
                        "q": keyword,
                        "image_type": "photo",
                        "orientation": "vertical",
                        "per_page": images_per_keyword * 2,
                        "order": "popular",
                        "safesearch": "true"
                    }
                )
                
                if resp.status_code == 200:
                    hits = resp.json().get("hits", [])
                    
                    for hit in hits:
                        if len(all_images) >= count:
                            break
                        
                        url = hit.get("largeImageURL") or hit.get("webformatURL")
                        
                        if url and url not in seen_urls:
                            width = hit.get("imageWidth", 0)
                            height = hit.get("imageHeight", 0)
                            
                            if height / width >= 1.3:  # Vertical images
                                all_images.append({
                                    "source": "pixabay",
                                    "url": url,
                                    "width": width,
                                    "height": height,
                                    "keyword": keyword
                                })
                                seen_urls.add(url)
                    
                    logger.info(f"   ✅ Found {len([i for i in all_images if i['keyword'] == keyword])} from '{keyword}'")
        
        except Exception as e:
            logger.error(f"Error searching '{keyword}': {e}")
            continue
    
    logger.info(f"✅ Total unique images: {len(all_images)}")
    
    return all_images[:count]

# ============================================================================
# EMOTIONAL SCRIPT GENERATION
# ============================================================================

async def generate_emotional_script(niche: str, num_images: int) -> dict:
    """Generate human emotion-based script for storytelling"""
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    emotion = niche_data["emotion"]
    
    total_duration = num_images * IMAGE_DURATION
    
    # Segment durations
    durations = [
        total_duration * 0.27,  # Hook: 27%
        total_duration * 0.40,  # Story: 40%
        total_duration * 0.23,  # Climax: 23%
        total_duration * 0.10   # Outro: 10%
    ]
    
    prompt = f"""Create a VIRAL {int(total_duration)}-second Hindi narration for YouTube Shorts about {niche}.

NICHE: {niche}
EMOTION: {emotion}
IMAGES: {num_images}
DURATION: {int(total_duration)}s

REQUIREMENTS:
- Total duration: {int(total_duration)} seconds
- 4 segments with emotional arc
- Hindi language only
- {emotion.upper()} tone throughout
- Each segment has 1-2 word text overlay

STRUCTURE:
1. HOOK ({int(durations[0])}s): Create {emotion} + mystery
2. STORY ({int(durations[1])}s): Build {emotion} with facts
3. CLIMAX ({int(durations[2])}s): Peak {emotion} revelation
4. OUTRO ({int(durations[3])}s): {emotion} call to action

OUTPUT ONLY THIS JSON:
{{
  "segments": [
    {{"narration": "Hindi hook", "text_overlay": "1-2 words", "duration": {int(durations[0])}}},
    {{"narration": "Hindi story", "text_overlay": "1-2 words", "duration": {int(durations[1])}}},
    {{"narration": "Hindi climax", "text_overlay": "1-2 words", "duration": {int(durations[2])}}},
    {{"narration": "Hindi outro", "text_overlay": "1-2 words", "duration": {int(durations[3])}}}
  ]
}}"""
    
    try:
        if MISTRAL_API_KEY:
            logger.info("📝 Calling Mistral AI for emotional script...")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {MISTRAL_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "You are a viral content creator. Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.9,
                        "max_tokens": 1000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(0)
                    
                    script = json.loads(content)
                    
                    logger.info(f"✅ Emotional script generated for {niche}")
                    
                    return {
                        "title": f"{niche.title()} - {emotion.title()} #Shorts",
                        "description": f"#{niche} #viral #shorts #{emotion}",
                        "tags": [niche, "viral", "shorts", emotion],
                        "segments": script["segments"]
                    }
                    
    except Exception as e:
        logger.warning(f"Mistral AI failed: {e}")
    
    # Fallback script
    logger.info("Using fallback emotional script")
    
    fallback_scripts = {
        "space": {
            "segments": [
                {"narration": "Kya aap jaante hain yeh adbhut raaz jo duniya ke corner mein chhupa hai?", "text_overlay": "Raaz", "duration": int(durations[0])},
                {"narration": "Scientists ne discover kiya hai yeh impossiblelagta hai lekin sach kuch aur hai! Yeh dekh kar aap hairan reh jayenge!", "text_overlay": "Sach", "duration": int(durations[1])},
                {"narration": "Lekin sabse badi baat jo aapko pata honi chahiye... yeh universe ka secret!", "text_overlay": "Secret", "duration": int(durations[2])},
                {"narration": "Toh kya aap vishwas karte hain? Comment mein zaroor batao!", "text_overlay": "Comment", "duration": int(durations[3])}
            ]
        },
        "funny": {
            "segments": [
                {"narration": "Dekho kya ho raha hai! Yeh dekhne ke baad aap control nahi kar paoge apni hansi!", "text_overlay": "Hansi", "duration": int(durations[0])},
                {"narration": "Yeh sabse funny moment hai jo maine dekha! Har koi hasa hasa ke laut gaya!", "text_overlay": "Funny", "duration": int(durations[1])},
                {"narration": "Lekin wait karo... sabse mast twist abhi baaki hai!", "text_overlay": "Twist", "duration": int(durations[2])},
                {"narration": "Agar pasand aaya toh like karo aur apne doston ko tag karo!", "text_overlay": "Like", "duration": int(durations[3])}
            ]
        }
    }
    
    segments = fallback_scripts.get(niche, fallback_scripts["space"])["segments"]
    
    return {
        "title": f"{niche.title()} - Amazing #Shorts",
        "description": f"#{niche} #viral #shorts",
        "tags": [niche, "viral", "shorts"],
        "segments": segments
    }

# ============================================================================
# ELEVENLABS VOICE GENERATION
# ============================================================================

async def generate_voice_elevenlabs(text: str, language: str, temp_dir: str) -> Optional[str]:
    """Generate voice using ElevenLabs (Premium Quality)"""
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            logger.warning("   ⚠️ ElevenLabs key not configured")
            return None
        
        # Select voice based on language
        if language == "hindi":
            voice_id = ELEVENLABS_VOICES["hindi_male"]
        elif language == "english":
            voice_id = ELEVENLABS_VOICES["english_male"]
        else:
            voice_id = ELEVENLABS_VOICES["hindi_male"]
        
        text_clean = text.strip()[:500]
        temp_file = os.path.join(temp_dir, f"elevenlabs_{uuid.uuid4().hex[:4]}.mp3")
        
        logger.info(f"   🎙️ ElevenLabs: {language} voice")
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text_clean,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                        "style": 0.5,
                        "use_speaker_boost": True
                    }
                }
            )
            
            if response.status_code == 200:
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                
                size = get_size_mb(temp_file)
                
                if size > 0.01:
                    logger.info(f"   ✅ ElevenLabs Voice: {size:.2f}MB")
                    return temp_file
                
                force_cleanup(temp_file)
            else:
                logger.error(f"   ❌ ElevenLabs: HTTP {response.status_code}")
                
    except Exception as e:
        logger.error(f"   ❌ ElevenLabs error: {e}")
    
    return None

async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Fallback: Edge TTS (Free)"""
    try:
        import edge_tts
        
        temp = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:4]}.mp3")
        text_clean = text.strip()[:350]
        
        logger.info(f"   📞 Edge TTS fallback")
        
        communicate = edge_tts.Communicate(text_clean, "hi-IN-MadhurNeural", rate="+10%")
        await communicate.save(temp)
        
        if get_size_mb(temp) > 0.01:
            logger.info(f"   ✅ Edge TTS: {get_size_mb(temp):.2f}MB")
            return temp
        
        force_cleanup(temp)
        
    except Exception as e:
        logger.error(f"   ❌ Edge TTS: {e}")
    
    return None

async def generate_voice(text: str, duration: float, language: str, temp_dir: str) -> Optional[str]:
    """Generate voice with ElevenLabs priority"""
    # Try ElevenLabs first
    voice = await generate_voice_elevenlabs(text, language, temp_dir)
    if voice:
        return voice
    
    logger.warning("   ⚠️ Falling back to Edge TTS")
    return await generate_voice_edge(text, duration, temp_dir)

# ============================================================================
# IMAGE DOWNLOAD
# ============================================================================

async def download_image(image_data: dict, output_path: str) -> bool:
    """Download single image"""
    try:
        url = image_data.get("url")
        if not url:
            return False
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, follow_redirects=True)
            
            if resp.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                
                size = get_size_mb(output_path)
                
                if size > 0.1:
                    return True
                else:
                    force_cleanup(output_path)
        
        return False
        
    except Exception as e:
        logger.error(f"Image download error: {e}")
        force_cleanup(output_path)
        return False

async def download_images(images: List[dict], temp_dir: str) -> List[str]:
    """Download all images"""
    logger.info(f"📥 Downloading {len(images)} images...")
    
    downloaded = []
    
    for idx, img_data in enumerate(images):
        output = os.path.join(temp_dir, f"img_{idx:02d}.jpg")
        
        logger.info(f"   Image {idx+1}/{len(images)} ({img_data['keyword']})...")
        
        if await download_image(img_data, output):
            downloaded.append(output)
            logger.info(f"   ✅ {get_size_mb(output):.2f}MB")
        else:
            logger.warning(f"   ⚠️ Failed")
    
    logger.info(f"✅ Downloaded {len(downloaded)}/{len(images)}")
    
    return downloaded

# ============================================================================
# TEXT OVERLAY ON IMAGES
# ============================================================================

def add_text_overlay_to_image(image_path: str, text: str, output_path: str) -> bool:
    """Add 1-2 word text overlay to image using FFmpeg"""
    try:
        if not text or len(text.split()) > 3:
            # If text too long, skip overlay
            shutil.copy(image_path, output_path)
            return True
        
        # Clean text (remove emojis, special chars)
        text_clean = re.sub(r'[^\w\s]', '', text).strip()[:20]
        
        cmd = [
            "ffmpeg", "-i", image_path,
            "-vf", f"drawtext=text='{text_clean}':"
                   f"fontsize=80:"
                   f"fontcolor=white:"
                   f"x=(w-text_w)/2:"
                   f"y=h-200:"
                   f"borderw=8:"
                   f"bordercolor=black:"
                   f"shadowx=4:"
                   f"shadowy=4",
            "-q:v", "2",
            "-y", output_path
        ]
        
        if run_ffmpeg(cmd, 15):
            return True
        
        # Fallback: copy without overlay
        shutil.copy(image_path, output_path)
        return True
        
    except Exception as e:
        logger.error(f"Text overlay error: {e}")
        shutil.copy(image_path, output_path)
        return True

# ============================================================================
# SLIDESHOW WITH EFFECTS
# ============================================================================

def create_slideshow_with_effects(images: List[str], segments: list, temp_dir: str) -> Optional[str]:
    """Create slideshow with zoom effects and text overlays"""
    try:
        if len(images) < MIN_IMAGES:
            logger.error(f"Not enough images: {len(images)}")
            return None
        
        output = os.path.join(temp_dir, "slideshow.mp4")
        
        logger.info("🎬 Creating slideshow with effects...")
        
        frames_per_image = int(IMAGE_DURATION * FPS)
        
        # Process each image
        clips = []
        
        for idx, img_path in enumerate(images):
            # Get text overlay for this segment
            segment_idx = min(idx, len(segments) - 1)
            text_overlay = segments[segment_idx].get("text_overlay", "")
            
            logger.info(f"   Processing {idx+1}/{len(images)}: '{text_overlay}'")
            
            # Add text overlay
            overlayed = os.path.join(temp_dir, f"overlayed_{idx:02d}.jpg")
            add_text_overlay_to_image(img_path, text_overlay, overlayed)
            
            # Resize to 9:16
            resized = os.path.join(temp_dir, f"resized_{idx:02d}.jpg")
            
            cmd_resize = [
                "ffmpeg", "-i", overlayed,
                "-vf", f"scale={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}:force_original_aspect_ratio=increase,crop={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}",
                "-q:v", "2",
                "-y", resized
            ]
            
            if not run_ffmpeg(cmd_resize, 15):
                logger.warning(f"   ⚠️ Resize failed")
                continue
            
            # Add zoom effect
            transition = random.choice(TRANSITIONS)
            trans_filter = transition["filter"]
            trans_filter = trans_filter.replace("{frames}", str(frames_per_image))
            trans_filter = trans_filter.replace("{fps}", str(FPS))
            trans_filter = trans_filter.replace("{fade_out_start}", str(IMAGE_DURATION - 0.3))
            
            clip_output = os.path.join(temp_dir, f"clip_{idx:02d}.mp4")
            
            cmd_clip = [
                "ffmpeg",
                "-loop", "1",
                "-i", resized,
                "-vf", trans_filter,
                "-t", str(IMAGE_DURATION),
                "-r", str(FPS),
                "-c:v", "libx264",
                "-crf", "20",
                "-preset", "medium",
                "-pix_fmt", "yuv420p",
                "-y", clip_output
            ]
            
            if run_ffmpeg(cmd_clip, 60):
                clips.append(clip_output)
                logger.info(f"   ✅ Clip {idx+1} ready")
            
            force_cleanup(overlayed, resized)
        
        if len(clips) < MIN_IMAGES:
            logger.error(f"Not enough clips: {len(clips)}")
            return None
        
        # Concatenate clips
        logger.info("🎞️ Joining clips...")
        
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        cmd_concat = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-y", output
        ]
        
        if run_ffmpeg(cmd_concat, 90):
            size = get_size_mb(output)
            logger.info(f"✅ Slideshow: {size:.1f}MB")
            
            for clip in clips:
                force_cleanup(clip)
            
            return output
        
        return None
        
    except Exception as e:
        logger.error(f"Slideshow error: {e}")
        logger.error(traceback.format_exc())
        return None

# ============================================================================
# BACKGROUND MUSIC DOWNLOAD
# ============================================================================

async def download_background_music(niche: str, temp_dir: str) -> Optional[str]:
    """Download background music based on niche"""
    music_path = os.path.join(temp_dir, "bg_music.mp3")
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    music_style = niche_data.get("music_style", "epic")
    
    urls = BACKGROUND_MUSIC_URLS.get(music_style, BACKGROUND_MUSIC_URLS["epic"])
    
    logger.info(f"🎵 Downloading {music_style} music...")
    
    for attempt, url in enumerate(urls, 1):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, follow_redirects=True)
                
                if resp.status_code == 200:
                    with open(music_path, 'wb') as f:
                        f.write(resp.content)
                    
                    size = get_size_mb(music_path)
                    
                    if size > 0.05:
                        logger.info(f"   ✅ Music: {size:.2f}MB")
                        return music_path
                    
                    force_cleanup(music_path)
        
        except Exception as e:
            logger.warning(f"   ⚠️ Attempt {attempt} failed: {e}")
            continue
    
    logger.warning("⚠️ Music download failed")
    return None

# ============================================================================
# AUDIO MIXING
# ============================================================================

async def mix_audio(video: str, voices: List[str], music: Optional[str], temp_dir: str) -> Optional[str]:
    """Mix voices with background music"""
    try:
        logger.info("🎵 Mixing audio...")
        
        # Concatenate voices
        vlist = os.path.join(temp_dir, "voices.txt")
        with open(vlist, 'w') as f:
            for v in voices:
                f.write(f"file '{v}'\n")
        
        voice_combined = os.path.join(temp_dir, "voice_all.mp3")
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", vlist, "-c", "copy", "-y", voice_combined
        ]
        
        if not run_ffmpeg(cmd, 30):
            return None
        
        logger.info(f"   ✅ Voices: {get_size_mb(voice_combined):.2f}MB")
        
        # Mix with video
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];"
                "[2:a]volume=0.2,afade=t=in:d=1,afade=t=out:st=-2:d=2[music];"
                "[voice][music]amix=inputs=2:duration=first[audio]",
                "-map", "0:v",
                "-map", "[audio]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", final
            ]
        else:
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "96k",
                "-shortest",
                "-y", final
            ]
        
        if run_ffmpeg(cmd, 90):
            logger.info(f"✅ Final: {get_size_mb(final):.1f}MB")
            return final
        
        return None
        
    except Exception as e:
        logger.error(f"Audio mix error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], 
                           user_id: str, database_manager) -> dict:
    """Upload to YouTube"""
    try:
        logger.info("📤 Uploading to YouTube...")
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            return {"success": False, "error": "YouTube DB unavailable"}
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            return {"success": False, "error": "Credentials not found"}
        
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
        
        full_description = f"{description}\n\n#{' #'.join(tags)}"
        
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
# MAIN PIPELINE
# ============================================================================

async def generate_pixabay_video(
    niche: str,
    language: str,
    user_id: str,
    database_manager
) -> dict:
    """Main generation pipeline"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="pixabay_")
        logger.info(f"🎬 STARTING: {niche}")
        
        # STEP 1: Smart Image Search
        logger.info("🔍 STEP 1: Smart image search...")
        images_data = await search_pixabay_smart(niche, MAX_IMAGES)
        
        if len(images_data) < MIN_IMAGES:
            return {
                "success": False,
                "error": f"Not enough images: {len(images_data)}/{MIN_IMAGES}"
            }
        
        # STEP 2: Generate Emotional Script
        logger.info("📝 STEP 2: Generating script...")
        script = await generate_emotional_script(niche, len(images_data))
        
        # STEP 3: Download Images
        logger.info("📥 STEP 3: Downloading images...")
        image_files = await download_images(images_data, temp_dir)
        
        if len(image_files) < MIN_IMAGES:
            return {
                "success": False,
                "error": f"Download failed: {len(image_files)}/{MIN_IMAGES}"
            }
        
        # STEP 4: Download Music
        logger.info("🎵 STEP 4: Downloading music...")
        music = await download_background_music(niche, temp_dir)
        
        # STEP 5: Create Slideshow with Effects
        logger.info("🎬 STEP 5: Creating slideshow...")
        slideshow = create_slideshow_with_effects(image_files, script["segments"], temp_dir)
        
        if not slideshow:
            return {"success": False, "error": "Slideshow creation failed"}
        
        # Cleanup images
        for img in image_files:
            force_cleanup(img)
        gc.collect()
        
        # STEP 6: Generate Voices
        logger.info("🎤 STEP 6: Voiceovers...")
        voices = []
        
        for idx, seg in enumerate(script["segments"]):
            logger.info(f"   Voice {idx+1}/4...")
            voice = await generate_voice(seg["narration"], seg["duration"], language, temp_dir)
            if voice:
                voices.append(voice)
        
        if len(voices) < 3:
            return {"success": False, "error": f"Voice failed: {len(voices)}/4"}
        
        # STEP 7: Mix Audio
        logger.info("🎵 STEP 7: Mixing...")
        final = await mix_audio(slideshow, voices, music, temp_dir)
        
        if not final:
            return {"success": False, "error": "Audio mix failed"}
        
        final_size = get_size_mb(final)
        logger.info(f"✅ FINAL: {final_size:.1f}MB")
        
        # STEP 8: Upload
        logger.info("📤 STEP 8: Uploading...")
        upload_result = await upload_to_youtube(
            final, script["title"], script["description"],
            script["tags"], user_id, database_manager
        )
        
        # Cleanup
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        logger.info("🎉 COMPLETE!")
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script["title"],
            "description": script["description"],
            "size_mb": f"{final_size:.1f}MB",
            "niche": niche,
            "language": language,
            "image_count": len(image_files),
            "duration": len(image_files) * IMAGE_DURATION,
            "has_music": music is not None
        }
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/pixabay/niches")
async def get_niches():
    """Get available niches"""
    return {
        "success": True,
        "niches": {
            k: {
                "name": k.replace("_", " ").title(),
                "emotion": v["emotion"],
                "music_style": v["music_style"]
            } 
            for k, v in NICHE_KEYWORDS.items()
        }
    }

@router.post("/api/pixabay/generate")
async def generate_endpoint(request: Request):
    """Generate Pixabay slideshow endpoint"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "user_id required"}
            )
        
        niche = data.get("niche", "space")
        language = data.get("language", "hindi")
        
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"Invalid niche"}
            )
        
        from Supermain import database_manager
        
        logger.info(f"📨 API: {niche} / {language} / {user_id}")
        
        try:
            result = await asyncio.wait_for(
                generate_pixabay_video(
                    niche=niche,
                    language=language,
                    user_id=user_id,
                    database_manager=database_manager
                ),
                timeout=900
            )
            
            return JSONResponse(content=result)
            
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Timeout"}
            )
        
    except Exception as e:
        logger.error(f"❌ API error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

__all__ = ['router']