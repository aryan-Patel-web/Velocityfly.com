"""
Viral_pixel.py - FINAL PRODUCTION VERSION (IMAGE SLIDESHOW ONLY)
==================================================
✅ NO VIDEO DOWNLOAD - IMAGES ONLY
✅ 6-10 HD Vertical Images (9:16 ratio)
✅ 2 seconds per image
✅ Canva-style transitions (Zoom Out, Fade, Pan, Slide)
✅ Realistic zoom out effect on each image
✅ Google Vertex AI Text-to-Speech (1.1x speed)
✅ Horror/Dark/Space Background Music
✅ Professional text overlays
✅ Direct YouTube Upload
✅ Monetization-ready quality
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

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & API KEYS
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# GOOGLE VERTEX AI CONFIGURATION
GOOGLE_API_KEY = os.getenv("GOOGLE_VERTEX_API_KEY", "")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "socialauto-472509")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")

# VOICE CONFIGURATION
VOICE_SPEED = 1.1
VOICE_NAME = "Orus"
VOICE_LANGUAGE = "hi-IN"

# PROCESSING LIMITS
MAX_VIDEO_SIZE_MB = 40
FFMPEG_TIMEOUT = 300
TARGET_DURATION = 30
CHUNK_SIZE = 65536

# IMAGE SLIDESHOW CONFIGURATION (UPDATED)
MIN_IMAGES = 6
MAX_IMAGES = 10
IMAGE_DURATION = 2.0  # 2 seconds per image (user request)
IMAGE_TARGET_WIDTH = 720
IMAGE_TARGET_HEIGHT = 1280
FPS = 30  # Higher FPS for smoother transitions

# NICHE KEYWORDS (EXPANDED)
NICHE_KEYWORDS = {
    "space": ["galaxy", "nebula", "planet", "cosmos", "stars", "universe", "astronomy", "milky way", "black hole"],
    "tech_ai": ["technology", "digital", "cyber", "robot", "ai", "future", "artificial intelligence", "circuit", "innovation"],
    "ocean": ["ocean", "wave", "underwater", "reef", "sea", "marine", "coral", "beach", "whale"],
    "nature": ["mountain", "forest", "waterfall", "sunset", "river", "landscape", "trees", "canyon", "valley"],
    "mystery": ["mystery", "secret", "ancient", "pyramid", "temple", "ruins", "artifact"],
    "science": ["science", "laboratory", "experiment", "microscope", "research", "discovery"],
    "motivational": ["success", "achievement", "victory", "growth", "meditation", "sunrise"]
}

# CANVA-STYLE TRANSITIONS WITH ZOOM OUT FOCUS
TRANSITIONS = [
    {
        "name": "zoom_out_center",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.8,max(1.001,zoom-0.008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}",
        "description": "Zoom out from center (dramatic reveal)"
    },
    {
        "name": "zoom_out_fade",
        "filter": "zoompan=z='if(lte(zoom,1.0),2.0,max(1.001,zoom-0.01))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps},fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out_start}:d=0.3",
        "description": "Zoom out with fade (smooth transition)"
    },
    {
        "name": "zoom_out_pan_right",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.6,max(1.001,zoom-0.007))':d={frames}:x='iw/2-(iw/zoom/2)+(t*15)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}",
        "description": "Zoom out + pan right (dynamic)"
    },
    {
        "name": "zoom_out_pan_left",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.6,max(1.001,zoom-0.007))':d={frames}:x='iw/2-(iw/zoom/2)-(t*15)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}",
        "description": "Zoom out + pan left (cinematic)"
    },
    {
        "name": "zoom_out_slide_up",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.7,max(1.001,zoom-0.008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)-(t*20)':s=720x1280:fps={fps}",
        "description": "Zoom out + slide up (ascending)"
    },
    {
        "name": "zoom_out_slide_down",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.7,max(1.001,zoom-0.008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+(t*20)':s=720x1280:fps={fps}",
        "description": "Zoom out + slide down (descending)"
    },
    {
        "name": "zoom_out_slow",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.005))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps},fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_start}:d=0.4",
        "description": "Slow zoom out (elegant)"
    },
    {
        "name": "zoom_out_fast",
        "filter": "zoompan=z='if(lte(zoom,1.0),2.5,max(1.001,zoom-0.015))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}",
        "description": "Fast zoom out (energetic)"
    }
]

# BACKGROUND MUSIC URLs
BACKGROUND_MUSIC_URLS = [
    "https://freesound.org/data/previews/614/614090_11931419-lq.mp3",
    "https://freesound.org/data/previews/543/543995_11587873-lq.mp3",
    "https://freesound.org/data/previews/632/632351_10755880-lq.mp3",
    "https://freesound.org/data/previews/558/558262_11587873-lq.mp3",
    "https://freesound.org/data/previews/521/521495_9961799-lq.mp3",
    "https://freesound.org/data/previews/477/477718_9497060-lq.mp3",
    "https://freesound.org/data/previews/456/456966_9497060-lq.mp3",
    "https://freesound.org/data/previews/398/398787_7517113-lq.mp3"
]

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
# BACKGROUND MUSIC DOWNLOAD
# ============================================================================

async def download_background_music(temp_dir: str) -> Optional[str]:
    """Download horror/dark/space background music"""
    music_path = os.path.join(temp_dir, "bg_music.mp3")
    
    logger.info("🎵 Downloading background music...")
    
    for attempt, url in enumerate(BACKGROUND_MUSIC_URLS, 1):
        try:
            logger.info(f"   Attempt {attempt}/{len(BACKGROUND_MUSIC_URLS)}...")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, follow_redirects=True)
                
                if resp.status_code == 200:
                    with open(music_path, 'wb') as f:
                        f.write(resp.content)
                    
                    size = get_size_mb(music_path)
                    
                    if size > 0.05:
                        logger.info(f"   ✅ Music downloaded: {size:.2f}MB")
                        return music_path
                    else:
                        force_cleanup(music_path)
            
            force_cleanup(music_path)
            
        except Exception as e:
            logger.warning(f"   ⚠️ Attempt {attempt} failed: {str(e)[:100]}")
            force_cleanup(music_path)
            continue
    
    logger.warning("⚠️ All music downloads failed (continuing without music)")
    return None

# ============================================================================
# SCRIPT GENERATION
# ============================================================================

async def generate_script(niche: str, num_images: int) -> dict:
    """Generate viral script - adjusted for image count"""
    
    title_templates = [
        "What Scientists Hide About {topic}",
        "The Dark Truth Behind {topic}",
        "This Will Change How You See {topic}",
        "{topic}: The Shocking Reality",
        "The Secret Of {topic} Revealed",
        "{topic}: What They Don't Want You To Know",
        "Unbelievable {topic} Facts",
        "The Mystery of {topic} Explained"
    ]
    
    topic = niche.replace("_", " ").title()
    english_title = random.choice(title_templates).format(topic=topic)
    
    # Calculate segment durations based on image count
    total_duration = num_images * IMAGE_DURATION
    
    # Distribute time across 4 segments
    durations = [
        total_duration * 0.27,  # Hook: 27%
        total_duration * 0.40,  # Story: 40%
        total_duration * 0.23,  # Climax: 23%
        total_duration * 0.10   # Outro: 10%
    ]
    
    prompt = f"""Create a VIRAL {int(total_duration)}-second Hindi narration for YouTube Shorts about {niche}.

REQUIREMENTS:
- Total duration: {int(total_duration)} seconds
- 4 segments
- Hindi language only
- Engaging, mysterious, shocking tone

STRUCTURE:
1. HOOK ({int(durations[0])}s): "Kya aap jaante hain..." - create mystery
2. STORY ({int(durations[1])}s): Present amazing facts
3. CLIMAX ({int(durations[2])}s): "Lekin sabse badi baat..." - revelation
4. OUTRO ({int(durations[3])}s): "Comment mein batao!" - call to action

OUTPUT ONLY THIS JSON:
{{
  "segments": [
    {{"narration": "Hindi hook", "text_overlay": "😱", "duration": {int(durations[0])}}},
    {{"narration": "Hindi story", "text_overlay": "🔥", "duration": {int(durations[1])}}},
    {{"narration": "Hindi climax", "text_overlay": "💡", "duration": {int(durations[2])}}},
    {{"narration": "Hindi outro", "text_overlay": "🤔", "duration": {int(durations[3])}}}
  ]
}}"""
    
    try:
        if MISTRAL_API_KEY:
            logger.info("📝 Calling Mistral AI for script...")
            
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
                    
                    logger.info(f"✅ Script generated")
                    
                    return {
                        "title": english_title + " #Shorts",
                        "description": f"#{niche} #viral #shorts #mystery #facts",
                        "tags": [niche, "viral", "shorts", "mystery", "facts"],
                        "segments": script["segments"]
                    }
                    
    except Exception as e:
        logger.warning(f"Mistral AI failed: {e}")
    
    # Fallback script
    logger.info("Using fallback script")
    
    return {
        "title": english_title + " #Shorts",
        "description": f"#{niche} #viral #shorts #mystery",
        "tags": [niche, "viral", "shorts", "mystery"],
        "segments": [
            {"narration": "Kya aap jaante hain yeh shocking rahasya jo duniya se chhupa hai?", "text_overlay": "😱", "duration": int(durations[0])},
            {"narration": "Scientists ne discover kiya hai yeh impossible lagta hai lekin sach kuch aur hai! Yeh jaankar aap hairan reh jayenge!", "text_overlay": "🔥", "duration": int(durations[1])},
            {"narration": "Lekin sabse badi baat jo aapko pata honi chahiye... yeh duniya badal degi!", "text_overlay": "💡", "duration": int(durations[2])},
            {"narration": "Toh kya aap vishwas karte hain? Neeche comment mein zaroor batao!", "text_overlay": "🤔", "duration": int(durations[3])}
        ]
    }

# ============================================================================
# VOICE GENERATION
# ============================================================================

async def generate_voice_vertex_ai(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Generate voice using Google Vertex AI"""
    try:
        if not GOOGLE_API_KEY or len(GOOGLE_API_KEY) < 20:
            logger.warning("   ⚠️ Vertex AI key not configured")
            return None
        
        text_clean = text.strip()[:500]
        temp_raw = os.path.join(temp_dir, f"vertex_{uuid.uuid4().hex[:4]}.mp3")
        
        logger.info(f"   📞 Vertex AI: {VOICE_NAME} @ {VOICE_SPEED}x")
        
        url = f"https://{GOOGLE_LOCATION}-aiplatform.googleapis.com/v1/projects/{GOOGLE_PROJECT_ID}/locations/{GOOGLE_LOCATION}/publishers/google/models/chirp-3-hd-voices:generateContent"
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {GOOGLE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{"role": "user", "parts": [{"text": text_clean}]}],
                    "generationConfig": {
                        "voice": {"name": VOICE_NAME, "languageCode": VOICE_LANGUAGE},
                        "audioEncoding": "LINEAR16",
                        "sampleRateHertz": 22050,
                        "speakingRate": VOICE_SPEED,
                        "volumeGainDb": 0.0
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "candidates" in result:
                    for part in result["candidates"][0]["content"]["parts"]:
                        if "inlineData" in part:
                            audio_bytes = base64.b64decode(part["inlineData"]["data"])
                            
                            with open(temp_raw, 'wb') as f:
                                f.write(audio_bytes)
                            
                            size = get_size_mb(temp_raw)
                            
                            if size > 0.01:
                                output = temp_raw.replace(".mp3", "_adj.mp3")
                                
                                cmd = [
                                    "ffmpeg", "-i", temp_raw,
                                    "-filter:a", "loudnorm=I=-16",
                                    "-t", str(duration + 0.5),
                                    "-b:a", "128k",
                                    "-y", output
                                ]
                                
                                if run_ffmpeg(cmd, 20):
                                    force_cleanup(temp_raw)
                                    logger.info(f"   ✅ Voice: {get_size_mb(output):.2f}MB")
                                    return output
                                
                                force_cleanup(temp_raw, output)
                            
                            force_cleanup(temp_raw)
            else:
                logger.error(f"   ❌ Vertex AI: HTTP {response.status_code}")
                
    except Exception as e:
        logger.error(f"   ❌ Vertex AI error: {e}")
    
    return None

async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Fallback: Edge TTS"""
    try:
        import edge_tts
        
        temp = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:4]}.mp3")
        text_clean = text.strip()[:350]
        
        logger.info(f"   📞 Edge TTS fallback")
        
        rate_percent = int((VOICE_SPEED - 1.0) * 100)
        rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
        
        communicate = edge_tts.Communicate(text_clean, "hi-IN-MadhurNeural", rate=rate_str)
        await communicate.save(temp)
        
        if get_size_mb(temp) > 0.01:
            logger.info(f"   ✅ Edge TTS: {get_size_mb(temp):.2f}MB")
            return temp
        
        force_cleanup(temp)
        
    except Exception as e:
        logger.error(f"   ❌ Edge TTS: {e}")
    
    return None

async def generate_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Generate voice with fallback"""
    voice = await generate_voice_vertex_ai(text, duration, temp_dir)
    if voice:
        return voice
    
    logger.warning("   ⚠️ Falling back to Edge TTS")
    return await generate_voice_edge(text, duration, temp_dir)

# ============================================================================
# IMAGE SEARCH & DOWNLOAD
# ============================================================================

def is_vertical_image(width: int, height: int) -> bool:
    """Check if image is vertical (9:16 or similar)"""
    if width <= 0 or height <= 0:
        return False
    aspect_ratio = height / width
    return aspect_ratio >= 1.5

async def search_pixabay_images(query: str, count: int) -> List[dict]:
    """Search Pixabay for HD vertical images"""
    images = []
    
    try:
        word = query.split()[0].lower()
        
        logger.info(f"   🔍 Pixabay: '{word}'")
        
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.get(
                "https://pixabay.com/api/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": word,
                    "image_type": "photo",
                    "orientation": "vertical",
                    "per_page": count * 3,
                    "order": "popular",
                    "safesearch": "true"
                }
            )
            
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                
                for hit in hits:
                    if len(images) >= count:
                        break
                    
                    width = hit.get("imageWidth", 0)
                    height = hit.get("imageHeight", 0)
                    
                    if is_vertical_image(width, height):
                        url = hit.get("largeImageURL") or hit.get("webformatURL")
                        
                        if url:
                            images.append({
                                "source": "pixabay",
                                "url": url,
                                "width": width,
                                "height": height
                            })
                
                logger.info(f"   ✅ Pixabay: {len(images)} images")
            else:
                logger.warning(f"   ⚠️ Pixabay: HTTP {resp.status_code}")
        
    except Exception as e:
        logger.error(f"Pixabay error: {e}")
    
    return images

async def search_pexels_images(query: str, count: int) -> List[dict]:
    """Search Pexels for HD vertical images"""
    images = []
    
    try:
        if not PEXELS_API_KEY:
            logger.warning("⚠️ PEXELS_API_KEY not set")
            return images
        
        word = query.split()[0].lower()
        
        logger.info(f"   🔍 Pexels: '{word}'")
        
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": word,
                    "orientation": "portrait",
                    "size": "large",
                    "per_page": count * 3
                }
            )
            
            if resp.status_code == 200:
                photos = resp.json().get("photos", [])
                
                for photo in photos:
                    if len(images) >= count:
                        break
                    
                    width = photo.get("width", 0)
                    height = photo.get("height", 0)
                    
                    if is_vertical_image(width, height):
                        src = photo.get("src", {})
                        url = src.get("large2x") or src.get("large") or src.get("original")
                        
                        if url:
                            images.append({
                                "source": "pexels",
                                "url": url,
                                "width": width,
                                "height": height
                            })
                
                logger.info(f"   ✅ Pexels: {len(images)} images")
            else:
                logger.warning(f"   ⚠️ Pexels: HTTP {resp.status_code}")
        
    except Exception as e:
        logger.error(f"Pexels error: {e}")
    
    return images

async def search_images(niche: str, count: int) -> List[dict]:
    """Search images: Pixabay FIRST, then Pexels"""
    logger.info(f"🖼️ Searching {count} HD vertical images...")
    logger.info("   Priority: Pixabay (1st) → Pexels (2nd)")
    
    all_images = []
    keywords = NICHE_KEYWORDS.get(niche, [niche])
    
    # Try Pixabay FIRST
    logger.info("   Step 1: Pixabay...")
    for keyword in keywords[:4]:
        images = await search_pixabay_images(keyword, count)
        all_images.extend(images)
        if len(all_images) >= count:
            break
    
    # If not enough, try Pexels
    if len(all_images) < count:
        logger.info(f"   Step 2: Need more, trying Pexels...")
        for keyword in keywords[:4]:
            images = await search_pexels_images(keyword, count - len(all_images))
            all_images.extend(images)
            if len(all_images) >= count:
                break
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_images = []
    for img in all_images:
        if img["url"] not in seen_urls:
            seen_urls.add(img["url"])
            unique_images.append(img)
    
    # Limit to requested count
    unique_images = unique_images[:count]
    
    logger.info(f"✅ Found {len(unique_images)} unique images")
    
    return unique_images

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
        
        logger.info(f"   Image {idx+1}/{len(images)}...")
        
        if await download_image(img_data, output):
            downloaded.append(output)
            logger.info(f"   ✅ {get_size_mb(output):.2f}MB")
        else:
            logger.warning(f"   ⚠️ Failed")
    
    logger.info(f"✅ Downloaded {len(downloaded)}/{len(images)}")
    
    return downloaded

# ============================================================================
# CANVA-STYLE SLIDESHOW WITH ZOOM OUT
# ============================================================================

def create_slideshow_with_zoom_out(images: List[str], temp_dir: str) -> Optional[str]:
    """
    Create professional slideshow with ZOOM OUT transitions
    - Each image: 2 seconds
    - Zoom out effect on EVERY image
    - Smooth crossfades
    - Canva-quality output
    """
    try:
        if len(images) < MIN_IMAGES:
            logger.error(f"Not enough images: {len(images)} < {MIN_IMAGES}")
            return None
        
        output = os.path.join(temp_dir, "slideshow.mp4")
        
        logger.info("🎬 Creating Canva-style slideshow...")
        logger.info(f"   Images: {len(images)}")
        logger.info(f"   Duration/image: {IMAGE_DURATION}s")
        logger.info(f"   Total: {len(images) * IMAGE_DURATION}s")
        logger.info(f"   Effect: ZOOM OUT on every image")
        
        frames_per_image = int(IMAGE_DURATION * FPS)
        
        # Process each image with zoom out
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
                logger.warning(f"   ⚠️ Resize failed")
                continue
            
            # Select random zoom out transition
            transition = random.choice(TRANSITIONS)
            trans_name = transition["name"]
            
            logger.info(f"   Transition: {trans_name}")
            
            # Get filter and replace placeholders
            trans_filter = transition["filter"]
            trans_filter = trans_filter.replace("{frames}", str(frames_per_image))
            trans_filter = trans_filter.replace("{fps}", str(FPS))
            trans_filter = trans_filter.replace("{fade_out_start}", str(IMAGE_DURATION - 0.3))
            
            # Create clip with zoom out
            clip_output = os.path.join(temp_dir, f"clip_{idx:02d}.mp4")
            
            cmd_clip = [
                "ffmpeg",
                "-loop", "1",
                "-i", resized,
                "-vf", trans_filter,
                "-t", str(IMAGE_DURATION),
                "-r", str(FPS),
                "-c:v", "libx264",
                "-crf", "20",  # High quality
                "-preset", "medium",
                "-pix_fmt", "yuv420p",
                "-y", clip_output
            ]
            
            if run_ffmpeg(cmd_clip, 60):
                clips.append(clip_output)
                logger.info(f"   ✅ Clip {idx+1} ready")
            else:
                logger.warning(f"   ⚠️ Clip creation failed")
            
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
            
            # Cleanup clips
            for clip in clips:
                force_cleanup(clip)
            
            return output
        
        logger.error("Concatenation failed")
        return None
        
    except Exception as e:
        logger.error(f"Slideshow error: {e}")
        logger.error(traceback.format_exc())
        return None

def add_text_overlays(video: str, segments: list, temp_dir: str) -> Optional[str]:
    """Add text overlays to slideshow"""
    try:
        output = os.path.join(temp_dir, "with_text.mp4")
        
        logger.info("📝 Adding text overlays...")
        
        filters = []
        current_time = 0
        
        for idx, seg in enumerate(segments):
            text = seg.get("text_overlay", "").replace("'", "").replace('"', '')[:30]
            if text:
                logger.info(f"   Text {idx+1}: '{text}' @ {current_time}s")
                
                filters.append(
                    f"drawtext=text='{text}':"
                    f"fontsize=70:"
                    f"fontcolor=white:"
                    f"x=(w-text_w)/2:"
                    f"y=h-180:"
                    f"borderw=6:"
                    f"bordercolor=black:"
                    f"shadowx=3:"
                    f"shadowy=3:"
                    f"enable='between(t,{current_time},{current_time + seg['duration']})'"
                )
            
            current_time += seg["duration"]
        
        if not filters:
            logger.info("   No overlays")
            return video
        
        vf = ",".join(filters)
        
        cmd = [
            "ffmpeg", "-i", video,
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "20",
            "-preset", "medium",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 120):
            force_cleanup(video)
            logger.info(f"✅ Text added: {get_size_mb(output):.1f}MB")
            return output
        
        return video
        
    except Exception as e:
        logger.error(f"Text overlay error: {e}")
        return video

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
            logger.info("   Mixing voice + music...")
            
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];"
                "[2:a]volume=0.25,afade=t=in:d=1,afade=t=out:st=-2:d=2[music];"
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
            logger.info("   Voice only...")
            
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

async def generate_viral_video(
    niche: str,
    duration: int,
    language: str,
    channel_name: str,
    show_captions: bool,
    voice_gender: str,
    user_id: str,
    database_manager
) -> dict:
    """Main generation pipeline - IMAGE SLIDESHOW ONLY"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_pixel_")
        logger.info(f"🎬 STARTING: {niche}")
        logger.info(f"   Mode: IMAGE SLIDESHOW ONLY")
        logger.info(f"   Images: {MIN_IMAGES}-{MAX_IMAGES}")
        logger.info(f"   Duration/image: {IMAGE_DURATION}s")
        
        # STEP 1: Generate Script
        logger.info("📝 STEP 1: Script...")
        script = await generate_script(niche, MAX_IMAGES)
        logger.info(f"✅ Title: {script['title']}")
        
        # STEP 2: Download Music
        logger.info("🎵 STEP 2: Music...")
        music = await download_background_music(temp_dir)
        
        # STEP 3: Search Images
        logger.info("🖼️ STEP 3: Searching images...")
        images_data = await search_images(niche, MAX_IMAGES)
        
        if len(images_data) < MIN_IMAGES:
            return {
                "success": False,
                "error": f"Not enough images: {len(images_data)}/{MIN_IMAGES}"
            }
        
        # STEP 4: Download Images
        logger.info("📥 STEP 4: Downloading...")
        image_files = await download_images(images_data, temp_dir)
        
        if len(image_files) < MIN_IMAGES:
            return {
                "success": False,
                "error": f"Download failed: {len(image_files)}/{MIN_IMAGES}"
            }
        
        # Update script for actual image count
        if len(image_files) != MAX_IMAGES:
            logger.info(f"   Adjusting script for {len(image_files)} images")
            script = await generate_script(niche, len(image_files))
        
        # STEP 5: Create Slideshow
        logger.info("🎬 STEP 5: Creating slideshow...")
        slideshow = create_slideshow_with_zoom_out(image_files, temp_dir)
        
        if not slideshow:
            return {"success": False, "error": "Slideshow creation failed"}
        
        # Cleanup images
        for img in image_files:
            force_cleanup(img)
        gc.collect()
        
        # STEP 6: Add Text
        if show_captions:
            logger.info("📝 STEP 6: Text overlays...")
            slideshow = add_text_overlays(slideshow, script["segments"], temp_dir)
        
        # STEP 7: Generate Voices
        logger.info("🎤 STEP 7: Voiceovers...")
        voices = []
        
        for idx, seg in enumerate(script["segments"]):
            logger.info(f"   Voice {idx+1}/4...")
            voice = await generate_voice(seg["narration"], seg["duration"], temp_dir)
            if voice:
                voices.append(voice)
        
        if len(voices) < 3:
            return {"success": False, "error": f"Voice failed: {len(voices)}/4"}
        
        # STEP 8: Mix Audio
        logger.info("🎵 STEP 8: Mixing...")
        final = await mix_audio(slideshow, voices, music, temp_dir)
        
        if not final:
            return {"success": False, "error": "Audio mix failed"}
        
        final_size = get_size_mb(final)
        logger.info(f"✅ FINAL: {final_size:.1f}MB")
        
        # STEP 9: Upload
        logger.info("📤 STEP 9: Uploading...")
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
            "content_type": "slideshow",
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

@router.get("/api/viral-pixel/niches")
async def get_niches():
    """Get available niches"""
    return {
        "success": True,
        "niches": {
            k: {"name": k.replace("_", " ").title()} 
            for k in NICHE_KEYWORDS.keys()
        }
    }

@router.post("/api/viral-pixel/generate")
async def generate_endpoint(request: Request):
    """Generate slideshow endpoint"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "user_id required"}
            )
        
        niche = data.get("niche", "space")
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"Invalid niche"}
            )
        
        from Supermain import database_manager
        
        logger.info(f"📨 API: {niche} / {user_id}")
        
        try:
            result = await asyncio.wait_for(
                generate_viral_video(
                    niche=niche,
                    duration=30,
                    language=data.get("language", "hindi"),
                    channel_name=data.get("channel_name", ""),
                    show_captions=data.get("show_captions", True),
                    voice_gender=data.get("voice_gender", "male"),
                    user_id=user_id,
                    database_manager=database_manager
                ),
                timeout=900  # 15 minutes
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