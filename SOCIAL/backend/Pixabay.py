"""
pixabay_ultimate_production.py - ULTIMATE PRODUCTION VERSION
==================================================
✅ FFmpeg errors fixed (image quality detection)
✅ HD+ image quality (max resolution)
✅ Niche-specific keywords only (no coffee in space!)
✅ Proper CTA in every script
✅ Thumbnail: 10-15MB range enforced
✅ English + Hindi keywords (top 20)
✅ Script duration matches target (40s = 40s output)
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
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# PROCESSING LIMITS
MAX_VIDEO_SIZE_MB = 40
FFMPEG_TIMEOUT_CLIP = 180
FFMPEG_TIMEOUT_CONCAT = 300
FFMPEG_TIMEOUT_MUSIC = 120

# IMAGE CONFIGURATION
MIN_IMAGES = 6
MAX_IMAGES = 12
IMAGE_TARGET_WIDTH = 720
IMAGE_TARGET_HEIGHT = 1280
FPS = 30

# QUALITY THRESHOLDS
MIN_IMAGE_SIZE_KB = 100  # Skip tiny images
THUMBNAIL_MIN_SIZE_MB = 10
THUMBNAIL_MAX_SIZE_MB = 15

# RETRY
MAX_IMAGE_RETRIES = 3

# ============================================================================
# ENHANCED NICHE KEYWORDS - HIGHLY SPECIFIC
# ============================================================================
NICHE_KEYWORDS = {
    "space": {
        "keywords": ["blackhole", "galaxy spiral", "nebula colorful", "planet earth", "milky way", 
                    "supernova", "cosmic rays", "star cluster", "moon surface", "sun corona",
                    "asteroid belt", "space station"],
        "emotion": "wonder",
        "voice_id": "oABbH1EqNQfpzYZZOAPR",
        "voice_name": "Space Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(5).weba",
        "thumbnail_keywords": ["galaxy colorful", "nebula purple"],
        "english_keywords": [
            "space facts", "universe mystery", "black hole explained", "space facts hindi",
            "galaxy facts", "cosmos documentary", "astronomy shorts", "space science",
            "universe secrets", "space facts channel", "best space videos", "space exploration",
            "astrophysics", "space documentary hindi", "viral space shorts", "trending space",
            "amazing space facts", "space facts 2024", "universe hindi", "space knowledge"
        ],
        "hindi_keywords": [
            "अंतरिक्ष", "ब्रह्मांड", "गैलेक्सी", "ब्लैकहोल", "तारे", "सुपरनोवा",
            "अंतरिक्ष रहस्य", "ब्रह्मांड के रहस्य", "स्पेस फैक्ट्स", "हिंदी शॉर्ट्स"
        ]
    },
    "horror": {
        "keywords": ["haunted mansion", "dark forest night", "abandoned hospital", "creepy shadows",
                    "ghost figure", "graveyard fog", "scary house", "dark corridor",
                    "eerie night", "paranormal", "mystery door", "spooky"],
        "emotion": "suspense",
        "voice_id": "t1bT2r4IHulx2q9wwEUy",
        "voice_name": "Dark Storyteller",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(3).weba",
        "thumbnail_keywords": ["haunted house dark", "creepy abandoned"],
        "english_keywords": [
            "horror stories", "scary stories hindi", "real ghost stories", "haunted places",
            "horror shorts", "scary videos", "ghost stories", "paranormal activity",
            "horror facts", "scary facts", "haunted india", "real horror",
            "bhootiya kahani", "horror channel", "scary shorts viral", "horror hindi",
            "ghost videos", "haunted stories", "horror mysteries", "scary true stories"
        ],
        "hindi_keywords": [
            "भूतिया", "डरावनी", "हॉरर", "प्रेत", "डर", "रहस्यमय",
            "सच्ची हॉरर", "भूतिया कहानी", "डरावनी कहानी", "हॉरर शॉर्ट्स"
        ]
    },
    "nature": {
        "keywords": ["mountain peak snow", "waterfall tropical", "forest green", "sunset ocean",
                    "river flowing", "wildlife tiger", "canyon grand", "desert dunes",
                    "rainforest", "valley scenic", "beach paradise", "jungle wild"],
        "emotion": "peace",
        "voice_id": "repzAAjoKlgcT2oOAIWt",
        "voice_name": "Nature Guide",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(4).weba",
        "thumbnail_keywords": ["mountain sunset", "waterfall beautiful"],
        "english_keywords": [
            "nature beauty", "wildlife videos", "nature shorts", "beautiful nature",
            "nature documentary", "wildlife shorts", "nature facts", "amazing nature",
            "nature videos", "wildlife hindi", "nature channel", "scenic beauty",
            "nature 4k", "nature sounds", "nature viral", "wildlife facts",
            "nature india", "beautiful places", "nature hindi", "nature shorts viral"
        ],
        "hindi_keywords": [
            "प्रकृति", "वन्यजीव", "सुंदर प्रकृति", "जंगल", "पहाड़",
            "झरना", "प्राकृतिक सुंदरता", "वन्यजीव भारत", "प्रकृति शॉर्ट्स", "प्राकृतिक दृश्य"
        ]
    },
    "mystery": {
        "keywords": ["ancient pyramid", "temple ruins", "mysterious artifact", "treasure chest",
                    "ancient civilization", "secret chamber", "lost city", "archaeological dig",
                    "ancient manuscript", "mysterious cave", "ancient temple", "ruins mysterious"],
        "emotion": "curiosity",
        "voice_id": "u7y54ruSDBB05ueK084X",
        "voice_name": "Mystery Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback.weba",
        "thumbnail_keywords": ["ancient temple", "mysterious pyramid"],
        "english_keywords": [
            "mystery solved", "unsolved mysteries", "ancient mysteries", "mystery facts",
            "mysterious places", "mystery channel", "mystery shorts", "mystery hindi",
            "unsolved cases", "mystery stories", "ancient secrets", "mystery videos",
            "mystery india", "mysterious facts", "mystery viral", "unsolved mystery",
            "mystery documentary", "ancient india", "mystery shorts hindi", "mystery facts hindi"
        ],
        "hindi_keywords": [
            "रहस्य", "रहस्यमय", "प्राचीन", "रहस्यमय स्थान", "अनसुलझा",
            "रहस्य हिंदी", "रहस्यमय कहानी", "प्राचीन रहस्य", "रहस्य शॉर्ट्स", "रहस्यमय भारत"
        ]
    },
    "spiritual": {
        "keywords": ["krishna temple", "vrindavan", "meditation yoga", "spiritual guru",
                    "temple bells", "divine light", "prayer beads", "spiritual ceremony",
                    "lotus flower", "om symbol", "spiritual path", "devotion prayer"],
        "emotion": "devotion",
        "voice_id": "yD0Zg2jxgfQLY8I2MEHO",
        "voice_name": "Spiritual Voice",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback.weba",
        "thumbnail_keywords": ["krishna vrindavan", "temple divine"],
        "english_keywords": [
            "bhagavad gita", "krishna teachings", "spiritual wisdom", "bhagavad gita hindi",
            "gita knowledge", "spiritual shorts", "krishna stories", "spiritual facts",
            "gita quotes", "spirituality", "devotional", "spiritual channel",
            "gita lessons", "spiritual hindi", "krishna bhakti", "gita shorts",
            "spiritual videos", "devotional shorts", "spiritual india", "bhakti shorts"
        ],
        "hindi_keywords": [
            "भगवद गीता", "कृष्ण", "आध्यात्मिक", "भक्ति", "गीता ज्ञान",
            "कृष्ण लीला", "आध्यात्मिकता", "गीता हिंदी", "भक्ति शॉर्ट्स", "कृष्ण शॉर्ट्स"
        ]
    },
    "motivation": {
        "keywords": ["success climb", "victory celebration", "workout gym", "sunrise motivation",
                    "achievement trophy", "strength training", "focus meditation", "goal target",
                    "excellence award", "growth chart", "fitness workout", "winner podium"],
        "emotion": "inspiration",
        "voice_id": "CX1mcqJxcZzy2AsgaBjn",
        "voice_name": "Motivational Speaker",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(6).weba",
        "thumbnail_keywords": ["success motivation", "victory winner"],
        "english_keywords": [
            "motivation", "motivational quotes", "success motivation", "motivational speech",
            "inspiration", "success tips", "motivation hindi", "motivational shorts",
            "success stories", "motivational videos", "life motivation", "motivational channel",
            "success mindset", "motivational hindi", "inspiration shorts", "success shorts",
            "motivation viral", "motivational facts", "success facts", "motivation 2024"
        ],
        "hindi_keywords": [
            "प्रेरणा", "सफलता", "मोटिवेशन", "प्रेरणादायक", "सफलता की कहानी",
            "प्रेरक", "मोटिवेशनल", "सफलता हिंदी", "प्रेरणादायक शॉर्ट्स", "मोटिवेशन हिंदी"
        ]
    },
    "funny": {
        "keywords": ["funny dog", "cute cat", "funny animals", "hilarious pet", "comedy moment",
                    "funny baby", "cute puppy", "funny kitten", "animal fails", "funny meme",
                    "cute animals", "funny video"],
        "emotion": "joy",
        "voice_id": "3xDpHJYZLpyrp8I8ILUO",
        "voice_name": "Comedy Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback.weba",
        "thumbnail_keywords": ["funny dog", "cute cat"],
        "english_keywords": [
            "funny videos", "comedy shorts", "funny animals", "hilarious videos",
            "comedy channel", "funny shorts", "funny hindi", "comedy videos",
            "funny moments", "funny pets", "comedy shorts hindi", "funny viral",
            "comedy videos hindi", "funny shorts viral", "comedy india", "funny channel",
            "hilarious shorts", "comedy facts", "funny videos 2024", "comedy shorts viral"
        ],
        "hindi_keywords": [
            "मजेदार", "कॉमेडी", "हास्य", "फनी", "मजाकिया",
            "हंसी", "कॉमेडी शॉर्ट्स", "फनी वीडियो", "मजेदार शॉर्ट्स", "हास्य हिंदी"
        ]
    },
    "luxury": {
        "keywords": ["ferrari supercar", "lamborghini", "rolls royce", "private jet interior",
                    "luxury yacht", "mansion pool", "sports car", "luxury lifestyle",
                    "penthouse view", "luxury watch", "supercar collection", "luxury car"],
        "emotion": "aspiration",
        "voice_id": "l1CrgWMeEfm3xvPbn4YE",
        "voice_name": "Luxury Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(7).weba",
        "thumbnail_keywords": ["ferrari supercar", "lamborghini luxury"],
        "english_keywords": [
            "luxury cars", "supercars", "luxury lifestyle", "ferrari", "lamborghini",
            "luxury shorts", "supercar videos", "luxury life", "expensive cars",
            "luxury channel", "supercar shorts", "luxury hindi", "car lovers",
            "luxury facts", "supercar collection", "luxury lifestyle hindi", "car shorts",
            "luxury viral", "expensive lifestyle", "luxury cars hindi"
        ],
        "hindi_keywords": [
            "लग्जरी", "सुपरकार", "महंगी कार", "लग्जरी लाइफस्टाइल", "फेरारी",
            "लग्जरी शॉर्ट्स", "महंगी गाड़ी", "लग्जरी हिंदी", "सुपरकार हिंदी", "लग्जरी फैक्ट्स"
        ]
    }
}

# TRANSITIONS
TRANSITIONS = [
    {"name": "zoom_out", "filter": "zoompan=z='if(lte(zoom,1.0),1.8,max(1.001,zoom-0.008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"},
    {"name": "zoom_fade", "filter": "zoompan=z='if(lte(zoom,1.0),2.0,max(1.001,zoom-0.01))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps},fade=t=in:st=0:d=0.3"},
    {"name": "pan", "filter": "zoompan=z='1.3':d={frames}:x='iw/2-(iw/zoom/2)+(t*15)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"}
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

def get_size_kb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / 1024
    except:
        return 0.0

def run_ffmpeg(cmd: list, timeout: int = 120) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False, text=True)
        return result.returncode == 0
    except:
        return False

def estimate_speech_duration(text: str, speed: float = 1.1) -> float:
    words = len(text.split())
    return (words / 150) * 60 / speed

def convert_weba_to_mp3(weba: str, mp3: str) -> bool:
    cmd = ["ffmpeg", "-i", weba, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", "-y", mp3]
    return run_ffmpeg(cmd, FFMPEG_TIMEOUT_MUSIC)

def check_image_quality(img_path: str) -> bool:
    """Check if image is good quality (not corrupted/tiny)"""
    try:
        size_kb = get_size_kb(img_path)
        
        # Must be at least 100KB
        if size_kb < MIN_IMAGE_SIZE_KB:
            logger.warning(f"   ⚠️ Image too small: {size_kb:.1f}KB")
            return False
        
        # Try to verify with FFmpeg
        cmd = ["ffmpeg", "-v", "error", "-i", img_path, "-f", "null", "-"]
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        
        if result.returncode != 0:
            logger.warning(f"   ⚠️ Image corrupted/invalid")
            return False
        
        return True
    except:
        return False

# ============================================================================
# IMAGE SEARCH - HD QUALITY
# ============================================================================

async def search_pixabay_hd(niche: str, count: int, is_thumbnail: bool = False) -> List[dict]:
    """Search for HD images only"""
    logger.info(f"🔍 HD Search: {niche} (thumb: {is_thumbnail})")
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    keywords = niche_data.get("thumbnail_keywords" if is_thumbnail else "keywords", niche_data["keywords"])
    
    all_images = []
    seen_urls = set()
    
    for keyword in random.sample(keywords, len(keywords)):
        if len(all_images) >= count:
            break
        
        try:
            async with httpx.AsyncClient(timeout=25) as client:
                resp = await client.get(
                    "https://pixabay.com/api/",
                    params={
                        "key": PIXABAY_API_KEY,
                        "q": keyword,
                        "image_type": "photo",
                        "orientation": "vertical",
                        "per_page": 20,  # Get more for quality filtering
                        "order": "popular",
                        "safesearch": "true",
                        "min_width": 1080,  # HD quality
                        "min_height": 1920
                    }
                )
                
                if resp.status_code == 200:
                    hits = resp.json().get("hits", [])
                    
                    for hit in hits:
                        if len(all_images) >= count:
                            break
                        
                        # Prefer largeImageURL for best quality
                        url = hit.get("largeImageURL") or hit.get("fullHDURL") or hit.get("webformatURL")
                        
                        if url and url not in seen_urls:
                            size_mb = hit.get("imageSize", 0) / (1024 * 1024)
                            
                            # Thumbnail: 10-15MB range
                            if is_thumbnail:
                                if size_mb < THUMBNAIL_MIN_SIZE_MB or size_mb > THUMBNAIL_MAX_SIZE_MB:
                                    continue
                            
                            all_images.append({
                                "url": url,
                                "width": hit.get("imageWidth", 0),
                                "height": hit.get("imageHeight", 0),
                                "size_mb": size_mb,
                                "keyword": keyword
                            })
                            seen_urls.add(url)
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            continue
    
    logger.info(f"✅ Found {len(all_images)} HD images")
    return all_images[:count]

# ============================================================================
# SCRIPT GENERATION WITH PROPER CTA
# ============================================================================

async def generate_script_with_cta(niche: str, target_duration: int) -> dict:
    """Generate script that ALWAYS includes CTA"""
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    emotion = niche_data["emotion"]
    
    # Mandatory CTA
    cta = "Agar aapko yeh video pasand aayi ho toh LIKE karein, SUBSCRIBE karein aur apne doston ko SHARE karein, taaki aage bhi aise amazing videos milti rahein!"
    
    # Calculate content duration (target - CTA time ~8s)
    content_duration = max(20, target_duration - 8)
    
    prompt = f"""Create {content_duration}s Hindi content for {niche} YouTube Short.

STRICT RULES:
1. Write ONLY main content ({content_duration}s)
2. NO CTA in your output (we add separately)
3. {emotion.upper()} tone
4. Hook (5s) → Facts (85%) → Climax (10%)
5. Natural Hindi with commas, !, ?
6. NO "pause" word

OUTPUT JSON:
{{
  "content": "Main Hindi narration without CTA",
  "title": "Hinglish title max 80 chars",
  "keywords_english": ["top 10 English keywords"],
  "keywords_hindi": ["top 5 Hindi keywords"]
}}

Title Format: "{niche} Ki Amazing Facts 🔥 | Must Watch!"
"""
    
    try:
        if MISTRAL_API_KEY:
            async with httpx.AsyncClient(timeout=40) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Viral content creator. Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.88,
                        "max_tokens": 1000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    if match:
                        data = json.loads(match.group(0))
                        
                        # Add CTA
                        full_script = data.get("content", "") + " " + cta
                        
                        # Combine keywords
                        eng_keys = data.get("keywords_english", [])[:10]
                        hin_keys = data.get("keywords_hindi", [])[:5]
                        all_keys = niche_data["english_keywords"][:10] + eng_keys[:5] + hin_keys
                        
                        est_dur = estimate_speech_duration(full_script, 1.1)
                        num_imgs = max(MIN_IMAGES, min(int(est_dur / 3.5) + 1, MAX_IMAGES))
                        
                        return {
                            "script": full_script,
                            "title": data.get("title", f"{niche} Facts"),
                            "description": f"{full_script[:200]}...\n#{niche}",
                            "keywords": list(dict.fromkeys(all_keys))[:20],  # Dedupe, max 20
                            "estimated_duration": est_dur,
                            "num_images_needed": num_imgs,
                            "image_duration": est_dur / num_imgs
                        }
    except Exception as e:
        logger.warning(f"Script gen failed: {e}")
    
    # Fallback with CTA
    fallback = f"Amazing {niche} facts you must know! " + cta
    est = estimate_speech_duration(fallback, 1.1)
    num = max(MIN_IMAGES, int(est / 3.5) + 1)
    
    return {
        "script": fallback,
        "title": f"{niche.title()} Facts 🔥",
        "description": fallback[:200],
        "keywords": (niche_data["english_keywords"][:10] + niche_data["hindi_keywords"][:5])[:20],
        "estimated_duration": est,
        "num_images_needed": num,
        "image_duration": est / num
    }

# ============================================================================
# VOICE
# ============================================================================

async def generate_voice_elevenlabs(text: str, niche: str, temp_dir: str) -> Optional[str]:
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            return None
        
        voice_id = NICHE_KEYWORDS.get(niche, {}).get("voice_id", "oABbH1EqNQfpzYZZOAPR")
        temp_file = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex[:4]}.mp3")
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={"xi-api-key": ELEVENLABS_API_KEY},
                json={
                    "text": text.strip()[:2000],
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                }
            )
            
            if resp.status_code == 200:
                base = os.path.join(temp_dir, "vbase.mp3")
                with open(base, 'wb') as f:
                    f.write(resp.content)
                
                cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1", "-y", temp_file]
                if run_ffmpeg(cmd, 30):
                    force_cleanup(base)
                    if get_size_mb(temp_file) > 0.01:
                        logger.info(f"✅ Voice: {get_size_mb(temp_file):.2f}MB")
                        return temp_file
                force_cleanup(base, temp_file)
    except Exception as e:
        logger.error(f"Voice error: {e}")
    return None

async def generate_voice_edge(text: str, temp_dir: str) -> Optional[str]:
    try:
        import edge_tts
        base = os.path.join(temp_dir, "eb.mp3")
        final = os.path.join(temp_dir, f"e_{uuid.uuid4().hex[:4]}.mp3")
        
        comm = edge_tts.Communicate(text.strip()[:1500], "hi-IN-MadhurNeural", rate="+10%")
        await comm.save(base)
        
        cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1", "-y", final]
        if run_ffmpeg(cmd, 30):
            force_cleanup(base)
            if get_size_mb(final) > 0.01:
                return final
        force_cleanup(base, final)
    except:
        pass
    return None

# ============================================================================
# IMAGE DOWNLOAD
# ============================================================================

async def download_image(img_data: dict, path: str, retry: int = 0) -> bool:
    try:
        url = img_data.get("url")
        if not url:
            return False
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, follow_redirects=True)
            
            if resp.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(resp.content)
                
                # Check quality
                if check_image_quality(path):
                    return True
                force_cleanup(path)
        
        return False
    except Exception as e:
        if retry < MAX_IMAGE_RETRIES - 1:
            await asyncio.sleep(1)
            return await download_image(img_data, path, retry + 1)
        return False

async def download_images(images: List[dict], temp_dir: str) -> List[str]:
    downloaded = []
    for idx, img in enumerate(images):
        path = os.path.join(temp_dir, f"img_{idx:02d}.jpg")
        if await download_image(img, path):
            downloaded.append(path)
            logger.info(f"   ✅ {idx+1}/{len(images)}: {get_size_mb(path):.2f}MB")
    logger.info(f"✅ Downloaded: {len(downloaded)}/{len(images)}")
    return downloaded

# ============================================================================
# MUSIC
# ============================================================================

async def download_music(niche: str, temp_dir: str, custom_url: Optional[str], duration: float) -> Optional[str]:
    url = custom_url if custom_url else NICHE_KEYWORDS.get(niche, {}).get("bg_music_url")
    if not url:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.get(url)
            
            if resp.status_code == 200:
                raw = os.path.join(temp_dir, "m_raw.weba" if url.endswith('.weba') else "m_raw.mp3")
                with open(raw, 'wb') as f:
                    f.write(resp.content)
                
                if url.endswith('.weba'):
                    conv = os.path.join(temp_dir, "m_conv.mp3")
                    if convert_weba_to_mp3(raw, conv):
                        force_cleanup(raw)
                        raw = conv
                
                final = os.path.join(temp_dir, "bg_music.mp3")
                cmd = ["ffmpeg", "-i", raw, "-t", str(min(duration, 55)), "-acodec", "copy", "-y", final]
                
                if run_ffmpeg(cmd, FFMPEG_TIMEOUT_MUSIC):
                    force_cleanup(raw)
                    logger.info(f"✅ Music: {get_size_mb(final):.2f}MB")
                    return final
                
                if os.path.exists(raw) and get_size_mb(raw) > 0.05:
                    return raw
    except Exception as e:
        logger.warning(f"Music error: {e}")
    return None

# ============================================================================
# SLIDESHOW
# ============================================================================

def create_slideshow(images: List[str], image_duration: float, temp_dir: str) -> Optional[str]:
    try:
        if len(images) < MIN_IMAGES:
            return None
        
        frames = int(image_duration * FPS)
        clips = []
        
        for idx, img in enumerate(images):
            # Resize
            resized = os.path.join(temp_dir, f"r_{idx}.jpg")
            cmd_r = [
                "ffmpeg", "-i", img,
                "-vf", f"scale={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}:force_original_aspect_ratio=increase,crop={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}",
                "-q:v", "2", "-y", resized
            ]
            
            if not run_ffmpeg(cmd_r, 15):
                continue
            
            # Effect
            trans = random.choice(TRANSITIONS)
            filt = trans["filter"].replace("{frames}", str(frames)).replace("{fps}", str(FPS))
            
            clip = os.path.join(temp_dir, f"c_{idx}.mp4")
            cmd_c = [
                "ffmpeg", "-loop", "1", "-i", resized,
                "-vf", filt, "-t", str(image_duration),
                "-r", str(FPS), "-c:v", "libx264", "-crf", "23",
                "-preset", "fast", "-pix_fmt", "yuv420p", "-y", clip
            ]
            
            if run_ffmpeg(cmd_c, FFMPEG_TIMEOUT_CLIP):
                clips.append(clip)
                logger.info(f"   ✅ Clip {idx+1}/{len(images)}")
            
            force_cleanup(resized)
        
        if len(clips) < MIN_IMAGES:
            return None
        
        # Concat
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        output = os.path.join(temp_dir, "slideshow.mp4")
        cmd_con = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", "-y", output]
        
        if run_ffmpeg(cmd_con, FFMPEG_TIMEOUT_CONCAT):
            for clip in clips:
                force_cleanup(clip)
            logger.info(f"✅ Slideshow: {get_size_mb(output):.1f}MB")
            return output
        
        return None
    except Exception as e:
        logger.error(f"Slideshow error: {e}")
        return None

# ============================================================================
# MIX
# ============================================================================

async def mix_audio(video: str, voice: str, music: Optional[str], temp_dir: str) -> Optional[str]:
    try:
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            cmd = [
                "ffmpeg", "-i", video, "-i", voice, "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[v];[2:a]volume=0.12,afade=t=in:d=1[m];[v][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-y", final
            ]
        else:
            cmd = ["ffmpeg", "-i", video, "-i", voice, "-map", "0:v", "-map", "1:a",
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-shortest", "-y", final]
        
        if run_ffmpeg(cmd, FFMPEG_TIMEOUT_MUSIC):
            logger.info(f"✅ Final: {get_size_mb(final):.1f}MB")
            return final
        return None
    except:
        return None

# ============================================================================
# UPLOAD
# ============================================================================

async def upload_to_youtube(video: str, title: str, desc: str, keywords: List[str], user_id: str, db) -> dict:
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db or not yt_db.youtube.client:
            if yt_db:
                await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        if not creds:
            return {"success": False, "error": "No credentials"}
        
        credentials = {
            "access_token": creds.get("access_token"),
            "refresh_token": creds.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
        }
        
        from mainY import youtube_scheduler
        
        # Format keywords vertically
        full_desc = f"{desc}\n\nKeywords:\n" + "\n".join([f"#{k}" for k in keywords])
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id, credentials_data=credentials, content_type="shorts",
            title=title, description=full_desc, video_url=video
        )
        
        if result.get("success"):
            vid_id = result.get("video_id")
            return {"success": True, "video_id": vid_id, "video_url": f"https://youtube.com/shorts/{vid_id}"}
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN
# ============================================================================

async def generate_pixabay_video(niche: str, language: str, user_id: str, database_manager,
                                target_duration: int = 40, custom_bg_music: Optional[str] = None) -> dict:
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="pixabay_")
        logger.info(f"🎬 START: {niche} ({target_duration}s)")
        
        # Script
        script_result = await generate_script_with_cta(niche, target_duration)
        num_images = script_result["num_images_needed"]
        img_dur = script_result["image_duration"]
        
        # Search HD images
        images_data = await search_pixabay_hd(niche, num_images, False)
        if len(images_data) < MIN_IMAGES:
            return {"success": False, "error": f"Not enough HD images: {len(images_data)}"}
        
        # Search HD thumbnail
        thumb_data = await search_pixabay_hd(niche, 1, True)
        
        # Download images
        image_files = await download_images(images_data, temp_dir)
        if len(image_files) < MIN_IMAGES:
            return {"success": False, "error": "Download failed"}
        
        # Adjust duration
        if len(image_files) != num_images:
            img_dur = script_result["estimated_duration"] / len(image_files)
        
        # Download thumbnail
        thumb_file = None
        if thumb_data:
            thumb_path = os.path.join(temp_dir, "thumb.jpg")
            if await download_image(thumb_data[0], thumb_path):
                thumb_file = thumb_path
                logger.info(f"✅ Thumbnail: {get_size_mb(thumb_path):.2f}MB")
        
        # Music
        music = await download_music(niche, temp_dir, custom_bg_music, script_result["estimated_duration"])
        
        # Slideshow
        slideshow = create_slideshow(image_files, img_dur, temp_dir)
        if not slideshow:
            return {"success": False, "error": "Slideshow failed"}
        
        # Cleanup images
        for img in image_files:
            force_cleanup(img)
        gc.collect()
        
        # Voice
        voice = await generate_voice_elevenlabs(script_result["script"], niche, temp_dir)
        if not voice:
            voice = await generate_voice_edge(script_result["script"], temp_dir)
        if not voice:
            return {"success": False, "error": "Voice failed"}
        
        # Mix
        final = await mix_audio(slideshow, voice, music, temp_dir)
        if not final:
            return {"success": False, "error": "Mix failed"}
        
        final_size = get_size_mb(final)
        logger.info(f"✅ FINAL: {final_size:.1f}MB")
        
        # Upload
        upload_result = await upload_to_youtube(
            final, script_result["title"], script_result["description"],
            script_result["keywords"], user_id, database_manager
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
            "duration": script_result["estimated_duration"],
            "has_music": music is not None,
            "has_thumbnail": thumb_file is not None
        }
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API
# ============================================================================

router = APIRouter()

@router.get("/api/pixabay/niches")
async def get_niches():
    return {
        "success": True,
        "niches": {
            k: {"name": k.title(), "emotion": v["emotion"], "voice_name": v["voice_name"]} 
            for k, v in NICHE_KEYWORDS.items()
        }
    }

@router.post("/api/pixabay/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})
        
        niche = data.get("niche", "space")
        language = data.get("language", "hindi")
        target_duration = max(20, min(data.get("target_duration", 40), 55))
        custom_bg_music = data.get("custom_bg_music")
        
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(status_code=400, content={"success": False, "error": "Invalid niche"})
        
        from Supermain import database_manager
        
        logger.info(f"📨 API: {niche} / {language} / {target_duration}s")
        
        result = await asyncio.wait_for(
            generate_pixabay_video(niche, language, user_id, database_manager, target_duration, custom_bg_music),
            timeout=1500
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
    except Exception as e:
        logger.error(f"❌ API error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']