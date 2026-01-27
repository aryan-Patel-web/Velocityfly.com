"""
pixabay_enhanced.py - AI-POWERED IMAGE SLIDESHOW GENERATOR V2
==================================================
✅ Multi-keyword smart image search (no repetition)
✅ Niche-specific ElevenLabs voices
✅ Single unified script (no segments - token optimization)
✅ Retry logic for image downloads
✅ Dynamic image timing (covers full script)
✅ Text overlays on images (1-2 words)
✅ Professional transitions & effects
✅ Horror/Dark/Upbeat background music
✅ YouTube-optimized titles & descriptions
✅ Direct YouTube upload with CTA
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
MIN_IMAGES = 5
MAX_IMAGES = 9
IMAGE_DURATION_BASE = 3.5  # Base duration per image
IMAGE_TARGET_WIDTH = 720
IMAGE_TARGET_HEIGHT = 1280
FPS = 30

# RETRY CONFIGURATION
MAX_IMAGE_RETRIES = 3
MAX_TOTAL_IMAGE_ATTEMPTS = 20

# ============================================================================
# NICHE KEYWORDS & ELEVENLABS VOICE MAPPING
# ============================================================================
NICHE_KEYWORDS = {
    "space": {
        "keywords": ["galaxy", "nebula", "planet", "cosmos", "stars", "universe", 
                    "black hole", "milky way", "supernova", "asteroid"],
        "emotion": "wonder",
        "music_style": "epic",
        "voice_id": "oABbH1EqNQfpzYZZOAPR",  # Space facts voice
        "voice_name": "Space Narrator"
    },
    "horror": {
        "keywords": ["dark forest", "abandoned", "scary", "creepy", "haunted", 
                    "mystery", "shadows", "nightmare", "eerie", "gothic"],
        "emotion": "suspense",
        "music_style": "horror",
        "voice_id": "t1bT2r4IHulx2q9wwEUy",  # Horror/suspense voice
        "voice_name": "Dark Storyteller"
    },
    "nature": {
        "keywords": ["mountain", "forest", "waterfall", "sunset", "river", 
                    "landscape", "wildlife", "canyon", "valley", "ocean"],
        "emotion": "peace",
        "music_style": "calm",
        "voice_id": "repzAAjoKlgcT2oOAIWt",  # Nature voice
        "voice_name": "Nature Guide"
    },
    "mystery": {
        "keywords": ["ancient", "mystery", "secret", "temple", "ruins", 
                    "artifact", "history", "legend", "treasure", "adventure"],
        "emotion": "curiosity",
        "music_style": "cinematic",
        "voice_id": "u7y54ruSDBB05ueK084X",  # Mystery storyteller
        "voice_name": "Mystery Narrator"
    },
    "spiritual": {
        "keywords": ["krishna", "shiva", "meditation", "temple", "divine", 
                    "spiritual", "yoga", "peace", "mantra", "devotion"],
        "emotion": "devotion",
        "music_style": "calm",
        "voice_id": "yD0Zg2jxgfQLY8I2MEHO",  # Spiritual/god stories
        "voice_name": "Spiritual Voice"
    },
    "motivation": {
        "keywords": ["success", "achievement", "victory", "growth", "workout", 
                    "sunrise", "focus", "strength", "mindset", "excellence"],
        "emotion": "inspiration",
        "music_style": "energetic",
        "voice_id": "CX1mcqJxcZzy2AsgaBjn",  # Motivation voice
        "voice_name": "Motivational Speaker"
    },
    "funny": {
        "keywords": ["funny animals", "cute pets", "comedy", "hilarious", "meme", 
                    "pranks", "bloopers", "fun", "smile", "laugh"],
        "emotion": "joy",
        "music_style": "upbeat",
        "voice_id": "3xDpHJYZLpyrp8I8ILUO",  # Funny voice
        "voice_name": "Comedy Narrator"
    }
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

# BACKGROUND MUSIC URLs
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
# SMART IMAGE SEARCH - WITH RETRY LOGIC
# ============================================================================

async def search_pixabay_smart(niche: str, count: int) -> List[dict]:
    """
    Smart multi-keyword search with retry logic
    Ensures we get MIN_IMAGES to MAX_IMAGES
    """
    logger.info(f"🔍 Smart search for niche: {niche}")
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    keywords = niche_data["keywords"]
    
    all_images = []
    seen_urls = set()
    
    # Randomize keyword order
    shuffled_keywords = random.sample(keywords, len(keywords))
    
    images_per_keyword = max(2, count // len(keywords))
    total_attempts = 0
    
    for keyword in shuffled_keywords:
        if len(all_images) >= count or total_attempts >= MAX_TOTAL_IMAGE_ATTEMPTS:
            break
        
        logger.info(f"   🔍 Searching: '{keyword}'")
        
        for attempt in range(MAX_IMAGE_RETRIES):
            try:
                total_attempts += 1
                
                async with httpx.AsyncClient(timeout=25) as client:
                    resp = await client.get(
                        "https://pixabay.com/api/",
                        params={
                            "key": PIXABAY_API_KEY,
                            "q": keyword,
                            "image_type": "photo",
                            "orientation": "vertical",
                            "per_page": images_per_keyword * 3,  # Get more for filtering
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
                                
                                # Accept both vertical and horizontal (we'll crop)
                                if height > 0 and width > 0:
                                    all_images.append({
                                        "source": "pixabay",
                                        "url": url,
                                        "width": width,
                                        "height": height,
                                        "keyword": keyword
                                    })
                                    seen_urls.add(url)
                        
                        logger.info(f"   ✅ Found {len([i for i in all_images if i['keyword'] == keyword])} from '{keyword}'")
                        break  # Success, move to next keyword
                    
                    elif resp.status_code == 429:
                        logger.warning(f"   ⚠️ Rate limit, retrying in 2s...")
                        await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error searching '{keyword}' (attempt {attempt+1}): {e}")
                if attempt < MAX_IMAGE_RETRIES - 1:
                    await asyncio.sleep(1)
                continue
    
    logger.info(f"✅ Total unique images: {len(all_images)}")
    
    # Ensure we have at least MIN_IMAGES
    if len(all_images) < MIN_IMAGES:
        logger.warning(f"⚠️ Only found {len(all_images)} images, need {MIN_IMAGES}")
    
    return all_images[:MAX_IMAGES]

# ============================================================================
# UNIFIED SCRIPT GENERATION (SINGLE OUTPUT)
# ============================================================================

async def generate_unified_script(niche: str, num_images: int) -> dict:
    """
    Generate SINGLE unified script (not segments)
    Saves tokens and simplifies voiceover
    """
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    emotion = niche_data["emotion"]
    
    # Calculate duration based on actual image count
    if num_images <= 5:
        image_duration = 5.0  # Longer duration for fewer images
    elif num_images <= 7:
        image_duration = 4.0
    else:
        image_duration = 3.5
    
    total_duration = num_images * image_duration
    
    prompt = f"""Create a VIRAL {int(total_duration)}-second Hindi narration for YouTube Shorts about {niche}.

NICHE: {niche}
EMOTION: {emotion}
IMAGES: {num_images}
DURATION: {int(total_duration)} seconds

REQUIREMENTS:
- ONE continuous Hindi script (NOT segments)
- {emotion.upper()} tone throughout
- Hook (first 5s) → Story → Climax → CTA
- Must end with: "Agar aapko yeh video achhi lagi ho toh LIKE karein, SUBSCRIBE karein, aur SHARE karein, taaki aage bhi aisi updates milti rahein!"

OUTPUT ONLY THIS JSON:
{{
  "script": "Complete Hindi narration here...",
  "title": "English YouTube title (max 100 chars)",
  "keywords": ["keyword1", "keyword2", ... "keyword15"]
}}

TITLE MUST BE:
- Hinglish style (not pure English)
- Clickbait but relevant
- Example: "Space Ki Sabse Badi Mystery 🌌 | Aapko Pata Hona Chahiye!"

KEYWORDS MUST BE:
- Top 15 YouTube search terms
- Mix of Hindi & English
- Niche-specific
- Example: ["space facts", "universe mystery", "galaxy hindi", "cosmos secrets"]"""
    
    try:
        if MISTRAL_API_KEY:
            logger.info("📝 Calling Mistral AI for unified script...")
            
            async with httpx.AsyncClient(timeout=35) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {MISTRAL_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "You are a viral YouTube Shorts creator. Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.85,
                        "max_tokens": 800
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(0)
                    
                    script_data = json.loads(content)
                    
                    # Generate description from script
                    script_text = script_data.get("script", "")
                    description = f"{script_text[:300]}...\n\n#{niche} #viral #shorts"
                    
                    logger.info(f"✅ Unified script generated: {len(script_text)} chars")
                    
                    return {
                        "script": script_text,
                        "title": script_data.get("title", f"{niche.title()} Facts #Shorts"),
                        "description": description,
                        "keywords": script_data.get("keywords", [niche, "viral", "shorts"])[:15],
                        "image_duration": image_duration
                    }
                    
    except Exception as e:
        logger.warning(f"Mistral AI failed: {e}")
    
    # Fallback script
    logger.info("Using fallback unified script")
    
    fallback_scripts = {
        "space": "Kya aap jaante hain universe ka sabse bada raaz? Scientists ne discover kiya hai ki har galaxy mein ek supermassive black hole hai! Yeh itna powerful hai ki light bhi iske gravity se nahi nikal sakti! Aur sabse amazing baat - humara Milky Way galaxy bhi ek massive black hole ke around ghoom rahi hai! Agar aapko yeh video achhi lagi ho toh LIKE karein, SUBSCRIBE karein, aur SHARE karein, taaki aage bhi aisi updates milti rahein!",
        "horror": "Raat ke andhere mein ek ajeeb si awaaz aayi... Jo log uss jagah gaye, woh kabhi wapas nahi aaye! Local log kehte hain ki wahan kuch hai jo dikhta nahi, par mehsoos hota hai! Kya aap jaan na chahte hain ki aakhir hua kya tha? Agar aapko yeh video achhi lagi ho toh LIKE karein, SUBSCRIBE karein, aur SHARE karein, taaki aage bhi aisi updates milti rahein!",
        "funny": "Dekho kya ho raha hai! Yeh dekhne ke baad aap control nahi kar paoge apni hansi! Sabse funny moment jo maine dekha! Har koi hasa hasa ke laut gaya! Agar aapko yeh video achhi lagi ho toh LIKE karein, SUBSCRIBE karein, aur SHARE karein, taaki aage bhi aisi updates milti rahein!"
    }
    
    script_text = fallback_scripts.get(niche, fallback_scripts["space"])
    
    return {
        "script": script_text,
        "title": f"{niche.title()} Amazing Facts 🔥 | Must Watch!",
        "description": f"{script_text}\n\n#{niche} #viral #shorts",
        "keywords": [niche, "viral", "shorts", "amazing", "facts", "hindi", "trending", "must watch"],
        "image_duration": image_duration
    }

# ============================================================================
# ELEVENLABS VOICE GENERATION (NICHE-SPECIFIC)
# ============================================================================

async def generate_voice_elevenlabs(text: str, niche: str, temp_dir: str) -> Optional[str]:
    """Generate voice using niche-specific ElevenLabs voice"""
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            logger.warning("   ⚠️ ElevenLabs key not configured")
            return None
        
        niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
        voice_id = niche_data["voice_id"]
        voice_name = niche_data["voice_name"]
        
        text_clean = text.strip()[:1000]
        temp_file = os.path.join(temp_dir, f"elevenlabs_{uuid.uuid4().hex[:4]}.mp3")
        
        logger.info(f"   🎙️ ElevenLabs: {voice_name}")
        
        async with httpx.AsyncClient(timeout=50) as client:
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
                        "style": 0.6,
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

async def generate_voice_edge(text: str, temp_dir: str) -> Optional[str]:
    """Fallback: Edge TTS (Free)"""
    try:
        import edge_tts
        
        temp = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:4]}.mp3")
        text_clean = text.strip()[:1000]
        
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

async def generate_voice(text: str, niche: str, temp_dir: str) -> Optional[str]:
    """Generate voice with ElevenLabs priority"""
    # Try ElevenLabs first
    voice = await generate_voice_elevenlabs(text, niche, temp_dir)
    if voice:
        return voice
    
    logger.warning("   ⚠️ Falling back to Edge TTS")
    return await generate_voice_edge(text, temp_dir)

# ============================================================================
# IMAGE DOWNLOAD WITH RETRY
# ============================================================================

async def download_image(image_data: dict, output_path: str, retry: int = 0) -> bool:
    """Download single image with retry logic"""
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
                
                if size > 0.05:  # At least 50KB
                    return True
                else:
                    force_cleanup(output_path)
        
        return False
        
    except Exception as e:
        if retry < MAX_IMAGE_RETRIES - 1:
            logger.warning(f"   ⚠️ Retry {retry+1}/{MAX_IMAGE_RETRIES}")
            await asyncio.sleep(1)
            return await download_image(image_data, output_path, retry + 1)
        
        logger.error(f"Image download error: {e}")
        force_cleanup(output_path)
        return False

async def download_images(images: List[dict], temp_dir: str) -> List[str]:
    """Download all images with retry logic"""
    logger.info(f"📥 Downloading {len(images)} images...")
    
    downloaded = []
    
    for idx, img_data in enumerate(images):
        output = os.path.join(temp_dir, f"img_{idx:02d}.jpg")
        
        logger.info(f"   Image {idx+1}/{len(images)} ({img_data['keyword']})...")
        
        if await download_image(img_data, output):
            downloaded.append(output)
            logger.info(f"   ✅ {get_size_mb(output):.2f}MB")
        else:
            logger.warning(f"   ⚠️ Skipped (copyright/error)")
    
    logger.info(f"✅ Downloaded {len(downloaded)}/{len(images)}")
    
    return downloaded

# ============================================================================
# TEXT OVERLAY ON IMAGES (SIMPLIFIED)
# ============================================================================

def add_text_overlay_to_image(image_path: str, text: str, output_path: str) -> bool:
    """Add simple text overlay - skip if too complex to avoid errors"""
    try:
        # For Hindi text, use simple overlay without special fonts
        # to avoid FFmpeg errors
        if not text or len(text.split()) > 3:
            shutil.copy(image_path, output_path)
            return True
        
        # Clean text (ASCII only to avoid font issues)
        text_clean = re.sub(r'[^\x00-\x7F]+', '', text).strip()
        
        if not text_clean:
            shutil.copy(image_path, output_path)
            return True
        
        cmd = [
            "ffmpeg", "-i", image_path,
            "-vf", f"drawtext=text='{text_clean[:20]}':"
                   f"fontsize=60:"
                   f"fontcolor=white:"
                   f"x=(w-text_w)/2:"
                   f"y=h-180:"
                   f"borderw=6:"
                   f"bordercolor=black",
            "-q:v", "2",
            "-y", output_path
        ]
        
        if run_ffmpeg(cmd, 10):
            return True
        
        # Fallback: copy without overlay
        shutil.copy(image_path, output_path)
        return True
        
    except Exception as e:
        logger.warning(f"Text overlay skipped: {e}")
        shutil.copy(image_path, output_path)
        return True

# ============================================================================
# SLIDESHOW WITH EFFECTS
# ============================================================================

def create_slideshow_with_effects(images: List[str], image_duration: float, temp_dir: str) -> Optional[str]:
    """Create slideshow with zoom effects"""
    try:
        if len(images) < MIN_IMAGES:
            logger.error(f"Not enough images: {len(images)}")
            return None
        
        output = os.path.join(temp_dir, "slideshow.mp4")
        
        logger.info("🎬 Creating slideshow with effects...")
        
        frames_per_image = int(image_duration * FPS)
        
        # Process each image
        clips = []
        
        for idx, img_path in enumerate(images):
            logger.info(f"   Processing {idx+1}/{len(images)}...")
            
            # Resize to 9:16
            resized = os.path.join(temp_dir, f"resized_{idx:02d}.jpg")
            
            cmd_resize = [
                "ffmpeg", "-i", img_path,
                "-vf", f"scale={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}:force_original_aspect_ratio=increase,crop={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}",
                "-q:v", "2",
                "-y", resized
            ]
            
            if not run_ffmpeg(cmd_resize, 15):
                logger.warning(f"   ⚠️ Resize failed, skipping")
                continue
            
            # Add zoom effect
            transition = random.choice(TRANSITIONS)
            trans_filter = transition["filter"]
            trans_filter = trans_filter.replace("{frames}", str(frames_per_image))
            trans_filter = trans_filter.replace("{fps}", str(FPS))
            trans_filter = trans_filter.replace("{fade_out_start}", str(image_duration - 0.3))
            
            clip_output = os.path.join(temp_dir, f"clip_{idx:02d}.mp4")
            
            cmd_clip = [
                "ffmpeg",
                "-loop", "1",
                "-i", resized,
                "-vf", trans_filter,
                "-t", str(image_duration),
                "-r", str(FPS),
                "-c:v", "libx264",
                "-crf", "22",
                "-preset", "medium",
                "-pix_fmt", "yuv420p",
                "-y", clip_output
            ]
            
            if run_ffmpeg(cmd_clip, 60):
                clips.append(clip_output)
                logger.info(f"   ✅ Clip {idx+1} ready")
            
            force_cleanup(resized)
        
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
    
    logger.warning("⚠️ Music download failed (continuing without)")
    return None

# ============================================================================
# AUDIO MIXING
# ============================================================================

async def mix_audio(video: str, voice: str, music: Optional[str], temp_dir: str) -> Optional[str]:
    """Mix voice with background music"""
    try:
        logger.info("🎵 Mixing audio...")
        
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice,
                "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];"
                "[2:a]volume=0.15,afade=t=in:d=1,afade=t=out:st=-2:d=2[music];"
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
                "-i", voice,
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

async def upload_to_youtube(video_path: str, title: str, description: str, keywords: List[str], 
                           user_id: str, database_manager) -> dict:
    """Upload to YouTube with optimized metadata"""
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
        
        # Format description with keywords in vertical format
        full_description = f"{description}\n\n"
        full_description += "Keywords:\n"
        for keyword in keywords:
            full_description += f"#{keyword}\n"
        
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
    """Main generation pipeline with all improvements"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="pixabay_")
        logger.info(f"🎬 STARTING: {niche}")
        
        # STEP 1: Smart Image Search with Retry
        logger.info("🔍 STEP 1: Smart image search...")
        images_data = await search_pixabay_smart(niche, MAX_IMAGES)
        
        if len(images_data) < MIN_IMAGES:
            return {
                "success": False,
                "error": f"Not enough images: {len(images_data)}/{MIN_IMAGES}"
            }
        
        # STEP 2: Generate Unified Script
        logger.info("📝 STEP 2: Generating unified script...")
        script_result = await generate_unified_script(niche, len(images_data))
        
        # STEP 3: Download Images with Retry
        logger.info("📥 STEP 3: Downloading images...")
        image_files = await download_images(images_data, temp_dir)
        
        if len(image_files) < MIN_IMAGES:
            return {
                "success": False,
                "error": f"Download failed: {len(image_files)}/{MIN_IMAGES}"
            }
        
        # Recalculate duration based on actual downloaded images
        if len(image_files) != len(images_data):
            logger.info(f"Adjusting for {len(image_files)} images...")
            script_result = await generate_unified_script(niche, len(image_files))
        
        image_duration = script_result["image_duration"]
        
        # STEP 4: Download Music
        logger.info("🎵 STEP 4: Downloading music...")
        music = await download_background_music(niche, temp_dir)
        
        # STEP 5: Create Slideshow with Effects
        logger.info("🎬 STEP 5: Creating slideshow...")
        slideshow = create_slideshow_with_effects(image_files, image_duration, temp_dir)
        
        if not slideshow:
            return {"success": False, "error": "Slideshow creation failed"}
        
        # Cleanup images
        for img in image_files:
            force_cleanup(img)
        gc.collect()
        
        # STEP 6: Generate Single Voice
        logger.info("🎤 STEP 6: Generating voiceover...")
        voice = await generate_voice(script_result["script"], niche, temp_dir)
        
        if not voice:
            return {"success": False, "error": "Voice generation failed"}
        
        # STEP 7: Mix Audio
        logger.info("🎵 STEP 7: Mixing audio...")
        final = await mix_audio(slideshow, voice, music, temp_dir)
        
        if not final:
            return {"success": False, "error": "Audio mix failed"}
        
        final_size = get_size_mb(final)
        logger.info(f"✅ FINAL: {final_size:.1f}MB")
        
        # STEP 8: Upload to YouTube
        logger.info("📤 STEP 8: Uploading to YouTube...")
        upload_result = await upload_to_youtube(
            final, 
            script_result["title"], 
            script_result["description"],
            script_result["keywords"], 
            user_id, 
            database_manager
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
            "title": script_result["title"],
            "description": script_result["description"],
            "keywords": script_result["keywords"],
            "size_mb": f"{final_size:.1f}MB",
            "niche": niche,
            "language": language,
            "image_count": len(image_files),
            "duration": len(image_files) * image_duration,
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
                "music_style": v["music_style"],
                "voice_name": v["voice_name"]
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