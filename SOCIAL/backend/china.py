"""
china_enhanced.py - PROFILE-BASED VIDEO AUTOMATION WITH BULK SCRAPING
===========================================================================
✅ SCRAPES: TikTok/Douyin profiles by niche
✅ PROCESSES: One video at a time (download → edit → upload → repeat)
✅ SMART: Uses real profile URLs for each niche
✅ AUTOMATED: Sequential pipeline with proper cleanup
===========================================================================
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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_346aca9fb63af57816b2f0323b6312b75a65aa852656eeac")
ELEVENLABS_VOICE_ID = "nPczCjzI2devNBz1zQrb"

MAX_VIDEO_SIZE_MB = 30
FFMPEG_TIMEOUT = 120
TARGET_DURATION = 30
DOWNLOAD_TIMEOUT = 60

# ============================================================================
# NICHE CONFIGURATION WITH PROFILE URLS
# ============================================================================

NICHE_KEYWORDS = {
    "funny": {
        "name": "Funny / Comedy / Memes",
        "icon": "😂",
        "english": ["funny", "comedy", "meme", "prank", "fail", "joke", "hilarious", "laugh"],
        "chinese": ["搞笑", "幽默", "段子", "娱乐", "爆笑", "喜剧", "笑话", "有趣", "搞笑视频"],
        "emoji": "😂🤣💀",
        # Default profile URLs for funny/comedy content
        "profile_urls": [
            "https://www.tiktok.com/@zachking",
            "https://www.tiktok.com/@khaby.lame",
            "https://www.tiktok.com/@spencerx"
        ]
    },
    "animals": {
        "name": "Cute Animals / Pets",
        "icon": "🐶",
        "english": ["cute animals", "pets", "dogs", "cats", "puppies", "kittens", "funny animals", "animal"],
        "chinese": ["萌宠", "宠物", "狗狗", "猫咪", "可爱动物", "小猫", "小狗", "动物", "宠物视频"],
        "emoji": "🐶🐱❤️",
        # Default profile URLs for cute animals/pets
        "profile_urls": [
            "https://www.tiktok.com/@jiffpom",
            "https://www.tiktok.com/@mayapolarbear",
            "https://www.tiktok.com/@tuckerbudzyn"
        ]
    },
    "kids": {
        "name": "Kids / Cartoon / Children",
        "icon": "👶",
        "english": ["kids", "children", "cartoon", "baby", "funny kids", "cute baby", "toddler", "child"],
        "chinese": ["儿童", "宝宝", "小孩", "可爱宝宝", "萌娃", "动画", "幼儿", "孩子", "宝宝视频"],
        "emoji": "👶😊🌟",
        # Default profile URLs for kids/family content
        "profile_urls": [
            "https://www.tiktok.com/@likenastya",
            "https://www.tiktok.com/@vlad.super.vlad",
            "https://www.tiktok.com/@txunamy"
        ]
    },
    "stories": {
        "name": "Story / Motivation / Facts",
        "icon": "📖",
        "english": ["story", "motivation", "inspiration", "facts", "amazing story", "life lesson", "wisdom"],
        "chinese": ["故事", "励志", "感人", "真实故事", "人生", "智慧", "道理", "鼓舞", "励志视频"],
        "emoji": "📖💡✨",
        # Default profile URLs for stories/motivation
        "profile_urls": [
            "https://www.tiktok.com/@storytime",
            "https://www.tiktok.com/@thefactsite",
            "https://www.tiktok.com/@motivationmafia"
        ]
    },
    "satisfying": {
        "name": "Satisfying / ASMR / Oddly Satisfying",
        "icon": "✨",
        "english": ["satisfying", "oddly satisfying", "asmr", "relaxing", "soap cutting", "slime", "perfect"],
        "chinese": ["解压", "治愈", "舒适", "完美", "切割", "史莱姆", "放松", "减压", "解压视频"],
        "emoji": "✨😌🎯",
        # Default profile URLs for satisfying/ASMR content
        "profile_urls": [
            "https://www.tiktok.com/@satisfying",
            "https://www.tiktok.com/@oddlysatisfying",
            "https://www.tiktok.com/@asmr"
        ]
    }
}

# Background music URLs
BACKGROUND_MUSIC_URLS = [
    "https://freesound.org/data/previews/456/456966_5121236-lq.mp3",
    "https://freesound.org/data/previews/391/391660_7181322-lq.mp3",
    "https://freesound.org/data/previews/398/398513_7181322-lq.mp3",
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def force_cleanup(*filepaths):
    """Force cleanup with garbage collection"""
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
                logger.info(f"🗑️ Cleaned: {os.path.basename(fp)}")
        except:
            pass
    gc.collect()

def get_size_mb(fp: str) -> float:
    """Get file size in MB"""
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0.0

def matches_niche(text: str, niche: str) -> bool:
    """Check if text matches niche keywords"""
    if not text:
        return True  # Accept any video if no text
    
    text_lower = text.lower()
    niche_config = NICHE_KEYWORDS.get(niche, {})
    
    # Check English keywords
    for keyword in niche_config.get("english", []):
        if keyword.lower() in text_lower:
            return True
    
    # Check Chinese keywords
    for keyword in niche_config.get("chinese", []):
        if keyword in text:
            return True
    
    return True  # Be lenient - accept most videos

def get_random_user_agent():
    """Generate random user agent"""
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    ]
    return random.choice(agents)

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
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ FFmpeg timeout after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"FFmpeg exception: {e}")
        return False

# ============================================================================
# PROFILE SCRAPING WITH SELENIUM
# ============================================================================

class ProfileScraper:
    """Scrapes TikTok/Douyin profiles for video URLs"""
    
    def __init__(self):
        self.driver = None
    
    def init_driver(self):
        """Initialize Selenium WebDriver"""
        try:
            logger.info("🌐 Initializing Chrome driver...")
            
            options = Options()
            options.add_argument("--headless")  # Run headless for server
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ Chrome driver initialized")
            return True
            
        except Exception as e:
            logger.error(f"Driver init failed: {e}")
            return False
    
    def scrape_profile_videos(self, profile_url: str, max_videos: int = 10) -> List[str]:
        """
        Scrape video URLs from a TikTok/Douyin profile
        Returns list of video URLs
        """
        try:
            if not self.driver:
                if not self.init_driver():
                    return []
            
            logger.info(f"📱 Scraping profile: {profile_url}")
            
            # Load profile page
            self.driver.get(profile_url)
            
            # Wait for captcha if needed (give 30 seconds)
            logger.info("⏳ Waiting for page load (handle captcha if appears)...")
            time.sleep(5)  # Initial wait
            
            # Scroll to load more videos
            logger.info("📜 Scrolling to load videos...")
            scroll_pause_time = 1.5
            screen_height = self.driver.execute_script("return window.screen.height;")
            i = 1
            
            # Scroll down page to load videos
            for _ in range(5):  # Scroll 5 times
                self.driver.execute_script(f"window.scrollTo(0, {screen_height}*{i});")
                i += 1
                time.sleep(scroll_pause_time)
            
            # Extract video URLs
            logger.info("🔍 Extracting video URLs...")
            
            # Multiple selectors to try (TikTok changes these frequently)
            video_selectors = [
                "div[data-e2e='user-post-item'] a",
                "div.tiktok-x6y88p-DivItemContainerV2 a",
                "div[class*='DivItemContainer'] a",
                "a[href*='/video/']"
            ]
            
            video_urls = []
            
            for selector in video_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/video/' in href and href not in video_urls:
                            video_urls.append(href)
                            if len(video_urls) >= max_videos:
                                break
                    
                    if video_urls:
                        break
                        
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            logger.info(f"✅ Found {len(video_urls)} video URLs")
            return video_urls[:max_videos]
            
        except Exception as e:
            logger.error(f"Profile scraping error: {e}")
            return []
    
    def close(self):
        """Close the driver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("🔒 Chrome driver closed")
        except:
            pass

# ============================================================================
# VIDEO DOWNLOAD FROM TIKTOK/DOUYIN
# ============================================================================

async def download_video_from_url(video_url: str, video_id: str, temp_dir: str) -> Optional[str]:
    """
    Download video from TikTok/Douyin URL using ssstik.io API
    """
    try:
        logger.info(f"📥 Downloading video {video_id}...")
        logger.info(f"   URL: {video_url}")
        
        # Use ssstik.io API to get download link
        async with httpx.AsyncClient(timeout=60) as client:
            
            # Step 1: Get the download link from ssstik.io
            response = await client.post(
                'https://ssstik.io/abc',
                params={'url': 'dl'},
                headers={
                    'User-Agent': get_random_user_agent(),
                    'Accept': '*/*',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Origin': 'https://ssstik.io',
                    'Referer': 'https://ssstik.io/en',
                },
                data={
                    'id': video_url,
                    'locale': 'en',
                    'tt': 'NE9MVmM4'  # This token may need updating
                }
            )
            
            if response.status_code != 200:
                logger.warning(f"   ssstik.io returned {response.status_code}")
                return None
            
            # Parse response to get download link
            soup = BeautifulSoup(response.text, "html.parser")
            download_link_tag = soup.find('a')
            
            if not download_link_tag or 'href' not in download_link_tag.attrs:
                logger.warning("   No download link found")
                return None
            
            download_link = download_link_tag['href']
            logger.info(f"   ✅ Got download link")
            
            # Step 2: Download the actual video
            video_response = await client.get(
                download_link,
                headers={'User-Agent': get_random_user_agent()},
                follow_redirects=True
            )
            
            if video_response.status_code != 200:
                logger.warning(f"   Video download failed: {video_response.status_code}")
                return None
            
            # Save video
            video_content = video_response.content
            size_mb = len(video_content) / (1024 * 1024)
            
            if size_mb > MAX_VIDEO_SIZE_MB:
                logger.warning(f"   Video too large: {size_mb:.1f}MB")
                return None
            
            if size_mb < 0.1:
                logger.warning(f"   Video too small: {size_mb:.2f}MB")
                return None
            
            # Save to file
            video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
            
            with open(video_path, 'wb') as f:
                f.write(video_content)
            
            logger.info(f"   ✅ Downloaded: {size_mb:.1f}MB")
            return video_path
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None

# ============================================================================
# AUDIO & TRANSCRIPTION
# ============================================================================

async def extract_audio(video_path: str, temp_dir: str) -> Optional[str]:
    """Extract audio from video"""
    try:
        audio_path = os.path.join(temp_dir, "original_audio.mp3")
        
        logger.info("🎵 Extracting audio...")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "libmp3lame",
            "-b:a", "128k",
            "-y", audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(audio_path):
            logger.info(f"✅ Audio: {get_size_mb(audio_path):.2f}MB")
            return audio_path
        
        return None
        
    except Exception as e:
        logger.error(f"Audio extraction error: {e}")
        return None


async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio - returns placeholder if fails"""
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key:
            logger.info("🎤 Transcribing with Whisper...")
            
            async with httpx.AsyncClient(timeout=120) as client:
                with open(audio_path, 'rb') as audio_file:
                    files = {'file': ('audio.mp3', audio_file, 'audio/mpeg')}
                    data = {'model': 'whisper-1', 'language': 'zh'}
                    
                    response = await client.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {openai_key}"},
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        transcript = result.get('text', '').strip()
                        logger.info(f"✅ Transcribed: {len(transcript)} chars")
                        return transcript
        
        logger.warning("⚠️ Using placeholder text")
        return "这是一个有趣的视频内容"
        
    except Exception as e:
        logger.warning(f"Transcription failed: {e}")
        return "精彩视频内容"


async def translate_to_hindi(chinese_text: str) -> str:
    """Translate Chinese to Hindi using Mistral"""
    try:
        if not MISTRAL_API_KEY:
            return chinese_text
        
        logger.info("🌏 Translating to Hindi...")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-large-latest",
                    "messages": [{
                        "role": "user",
                        "content": f"Translate to Hindi naturally:\n\n{chinese_text}\n\nProvide ONLY the Hindi translation."
                    }],
                    "temperature": 0.3,
                    "max_tokens": 300
                }
            )
            
            if response.status_code == 200:
                hindi_text = response.json()["choices"][0]["message"]["content"].strip()
                logger.info(f"✅ Translated: {hindi_text[:50]}...")
                return hindi_text
        
        return chinese_text
        
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return chinese_text

# ============================================================================
# CREATIVE SCRIPT GENERATION
# ============================================================================

async def generate_creative_script(hindi_text: str, niche: str, original_title: str) -> dict:
    """Generate viral Hindi script"""
    
    niche_config = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["funny"])
    
    if not MISTRAL_API_KEY:
        return generate_fallback_script(hindi_text, niche)
    
    prompt = f"""Create viral Hindi YouTube Shorts script (30s).

NICHE: {niche_config['name']}
STYLE: {niche_config.get('emoji', '🔥')}

ORIGINAL: {original_title}
CONTENT: {hindi_text}

Make it 10x more engaging for Indian audience!

4 segments with timing:
1. HOOK (8s) - Grab attention
2. BUILD (12s) - Develop content  
3. CLIMAX (7s) - Peak moment
4. OUTRO (3s) - Call to action

OUTPUT ONLY JSON:
{{
  "segments": [
    {{"narration": "Hindi text", "text_overlay": "EMOJI", "duration": 8}},
    {{"narration": "Hindi text", "text_overlay": "TEXT", "duration": 12}},
    {{"narration": "Hindi text", "text_overlay": "TEXT", "duration": 7}},
    {{"narration": "Hindi CTA", "text_overlay": "🔥", "duration": 3}}
  ],
  "title": "Viral Hindi title",
  "hashtags": ["{niche}", "viral", "shorts"]
}}"""
    
    try:
        logger.info("🤖 Generating script...")
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "Output ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.9,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                
                script = json.loads(content)
                logger.info("✅ Script generated")
                return script
    
    except Exception as e:
        logger.warning(f"Script generation failed: {e}")
    
    return generate_fallback_script(hindi_text, niche)


def generate_fallback_script(text: str, niche: str) -> dict:
    """Fallback script templates"""
    
    templates = {
        "funny": {
            "segments": [
                {"narration": f"Dekho yaar! {text[:40]}", "text_overlay": "😂", "duration": 8},
                {"narration": "Yeh toh kamal ka hai! Dekhte raho!", "text_overlay": "🤣", "duration": 12},
                {"narration": "Ending toh epic hai! Must watch!", "text_overlay": "💀", "duration": 7},
                {"narration": "Like karo! Comment karo!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "यह वीडियो देखकर हंसी नहीं रुकेगी 😂 #Shorts",
            "hashtags": ["funny", "comedy", "viral"]
        },
        "animals": {
            "segments": [
                {"narration": f"Kitna pyara hai! {text[:40]}", "text_overlay": "🐶", "duration": 8},
                {"narration": "Animals ka pyaar dekho! So cute!", "text_overlay": "🐱", "duration": 12},
                {"narration": "Yeh moment toh heartwarming hai!", "text_overlay": "❤️", "duration": 7},
                {"narration": "Share karo sabko!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "सबसे प्यारा जानवर 🐶❤️ #Shorts",
            "hashtags": ["animals", "cute", "viral"]
        },
        "kids": {
            "segments": [
                {"narration": f"Dekho yeh bachhe! {text[:40]}", "text_overlay": "👶", "duration": 8},
                {"narration": "Kitna cute hai! Kids are amazing!", "text_overlay": "😊", "duration": 12},
                {"narration": "Perfect family content hai yeh!", "text_overlay": "🌟", "duration": 7},
                {"narration": "Share karo family mein!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "बच्चों की मस्ती 👶😊 #Shorts",
            "hashtags": ["kids", "family", "viral"]
        },
        "stories": {
            "segments": [
                {"narration": f"Suno yeh kahani! {text[:40]}", "text_overlay": "📖", "duration": 8},
                {"narration": "Bahut inspiring hai! Life lesson hai yeh!", "text_overlay": "💡", "duration": 12},
                {"narration": "Ending mind-blowing hai! Must know!", "text_overlay": "✨", "duration": 7},
                {"narration": "Comment mein batao thoughts!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "जीवन बदल देने वाली कहानी 📖✨ #Shorts",
            "hashtags": ["story", "motivation", "viral"]
        },
        "satisfying": {
            "segments": [
                {"narration": f"Dekho kitna satisfying! {text[:40]}", "text_overlay": "✨", "duration": 8},
                {"narration": "Bilkul perfect hai! Relaxing feel!", "text_overlay": "😌", "duration": 12},
                {"narration": "Oddly satisfying moment! Pure perfection!", "text_overlay": "🎯", "duration": 7},
                {"narration": "Loop mein dekho! Save karo!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "सबसे Satisfying वीडियो ✨😌 #Shorts",
            "hashtags": ["satisfying", "asmr", "viral"]
        }
    }
    
    return templates.get(niche, templates["funny"])

# ============================================================================
# BACKGROUND MUSIC
# ============================================================================

async def download_background_music(temp_dir: str) -> Optional[str]:
    """Download background music"""
    
    music_path = os.path.join(temp_dir, "bg_music.mp3")
    
    logger.info("🎵 Downloading background music...")
    
    for url in BACKGROUND_MUSIC_URLS:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, follow_redirects=True)
                
                if resp.status_code == 200:
                    with open(music_path, 'wb') as f:
                        f.write(resp.content)
                    
                    if get_size_mb(music_path) > 0.05:
                        logger.info(f"✅ Music downloaded: {get_size_mb(music_path):.2f}MB")
                        return music_path
                    
                    force_cleanup(music_path)
            
        except:
            continue
    
    logger.warning("⚠️ No background music")
    return None

# ============================================================================
# VOICE GENERATION
# ============================================================================

async def generate_hindi_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Generate Hindi voiceover using ElevenLabs"""
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            logger.warning("⚠️ ElevenLabs API key not configured")
            return None
        
        text_clean = text.strip()[:500]
        temp_audio = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex[:6]}.mp3")
        
        logger.info(f"   🎤 Generating voice: {text_clean[:30]}...")
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text_clean,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.4,
                        "similarity_boost": 0.8,
                        "style": 0.3,
                        "use_speaker_boost": True
                    }
                }
            )
            
            if response.status_code == 200:
                with open(temp_audio, 'wb') as f:
                    f.write(response.content)
                
                if get_size_mb(temp_audio) > 0.01:
                    output = temp_audio.replace(".mp3", "_adj.mp3")
                    
                    cmd = [
                        "ffmpeg",
                        "-i", temp_audio,
                        "-filter:a", "atempo=1.15,loudnorm=I=-16",
                        "-t", str(duration + 0.5),
                        "-b:a", "128k",
                        "-y", output
                    ]
                    
                    if run_ffmpeg(cmd, 20):
                        force_cleanup(temp_audio)
                        logger.info(f"   ✅ Voice: {get_size_mb(output):.2f}MB")
                        return output
                
                force_cleanup(temp_audio)
                
    except Exception as e:
        logger.error(f"Voice error: {e}")
    
    return None

# ============================================================================
# VIDEO PROCESSING
# ============================================================================

async def remove_original_audio(video_path: str, temp_dir: str) -> Optional[str]:
    """Remove original audio"""
    try:
        output = os.path.join(temp_dir, "video_no_audio.mp4")
        
        logger.info("🔇 Removing original audio...")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-an",
            "-c:v", "copy",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 30):
            logger.info(f"✅ Audio removed: {get_size_mb(output):.1f}MB")
            return output
        
        return None
        
    except Exception as e:
        logger.error(f"Audio removal error: {e}")
        return None


async def process_video_for_shorts(video_path: str, target_duration: int, temp_dir: str) -> Optional[str]:
    """Process video for Reels: 1080x1920 (9:16 vertical format)"""
    try:
        output = os.path.join(temp_dir, "processed.mp4")
        
        logger.info(f"⚙️ Processing for Reels: {target_duration}s, 1080x1920 (9:16)")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-t", str(target_duration),
            # Scale to 1080x1920 (perfect 9:16 for Reels)
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264",
            "-crf", "23",  # Better quality
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 90):
            logger.info(f"✅ Processed: {get_size_mb(output):.1f}MB (1080x1920)")
            return output
        
        return None
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return None


async def add_text_overlays(video: str, segments: list, temp_dir: str) -> Optional[str]:
    """Add text overlays"""
    try:
        output = os.path.join(temp_dir, "with_text.mp4")
        
        logger.info("📝 Adding text overlays...")
        
        filters = []
        current_time = 0
        
        for seg in segments:
            text = seg.get("text_overlay", "").replace("'", "").replace('"', '')
            if text:
                filters.append(
                    f"drawtext=text='{text}':"
                    f"fontsize=60:"
                    f"fontcolor=white:"
                    f"x=(w-text_w)/2:"
                    f"y=h-150:"
                    f"borderw=5:"
                    f"bordercolor=black:"
                    f"enable='between(t,{current_time},{current_time + seg['duration']})'"
                )
            
            current_time += seg["duration"]
        
        if not filters:
            return video
        
        vf = ",".join(filters)
        
        cmd = [
            "ffmpeg",
            "-i", video,
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "fast",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 60):
            force_cleanup(video)
            logger.info(f"✅ Text added: {get_size_mb(output):.1f}MB")
            return output
        
        return video
        
    except Exception as e:
        logger.error(f"Text overlay error: {e}")
        return video


async def mix_audio_with_music(video: str, voices: List[str], music: Optional[str], temp_dir: str) -> Optional[str]:
    """Mix voices with background music"""
    try:
        logger.info("🎵 Mixing audio...")
        
        vlist = os.path.join(temp_dir, "voices.txt")
        with open(vlist, 'w') as f:
            for v in voices:
                f.write(f"file '{v}'\n")
        
        voice_combined = os.path.join(temp_dir, "voice_all.mp3")
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", vlist,
            "-c", "copy",
            "-y", voice_combined
        ]
        
        if not run_ffmpeg(cmd, 30):
            return None
        
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];"
                "[2:a]volume=0.25,afade=t=in:d=1,afade=t=out:st=28:d=2[music];"
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
                "-b:a", "128k",
                "-shortest",
                "-y", final
            ]
        
        if run_ffmpeg(cmd, 60):
            logger.info(f"✅ Final: {get_size_mb(final):.1f}MB")
            return final
        
        return None
        
    except Exception as e:
        logger.error(f"Mixing error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, 
                           hashtags: List[str], user_id: str, database_manager) -> dict:
    """Upload to YouTube"""
    try:
        logger.info("📤 Uploading to YouTube...")
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            return {"success": False, "error": "YouTube database not available"}
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
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
        
        full_description = f"{description}\n\n#{' #'.join(hashtags)}"
        
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
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            logger.info(f"✅ Uploaded: {video_url}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
        
        return {"success": False, "error": upload_result.get("error", "Upload failed")}
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN PROCESSING PIPELINE
# ============================================================================

async def process_single_video(
    video_url: str,
    niche: str,
    user_id: str,
    show_captions: bool,
    database_manager,
    video_index: int,
    total_videos: int
) -> dict:
    """
    Process a single video: download → edit → upload
    Sequential processing to avoid resource issues
    """
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"video_{video_index}_")
        logger.info(f"🎬 Processing video {video_index}/{total_videos}")
        logger.info(f"   URL: {video_url}")
        
        # STEP 1: Download video
        logger.info("📥 STEP 1: Downloading video...")
        video_id = f"{niche}_{video_index}_{uuid.uuid4().hex[:6]}"
        video_path = await download_video_from_url(video_url, video_id, temp_dir)
        
        if not video_path:
            return {"success": False, "error": "Download failed", "video_url": video_url}
        
        # STEP 2: Extract audio
        logger.info("🎵 STEP 2: Extracting audio...")
        audio_path = await extract_audio(video_path, temp_dir)
        
        if not audio_path:
            return {"success": False, "error": "Audio extraction failed"}
        
        # STEP 3: Transcribe
        logger.info("🎤 STEP 3: Transcribing...")
        transcript = await transcribe_audio(audio_path)
        
        # STEP 4: Translate
        logger.info("🌏 STEP 4: Translating to Hindi...")
        hindi_text = await translate_to_hindi(transcript)
        
        # STEP 5: Generate creative script
        logger.info("🤖 STEP 5: Generating script...")
        script = await generate_creative_script(hindi_text, niche, f"Video {video_index}")
        
        # STEP 6: Download background music
        logger.info("🎵 STEP 6: Getting background music...")
        music = await download_background_music(temp_dir)
        
        # STEP 7: Remove original audio
        logger.info("🔇 STEP 7: Removing original audio...")
        video_no_audio = await remove_original_audio(video_path, temp_dir)
        
        if not video_no_audio:
            return {"success": False, "error": "Audio removal failed"}
        
        force_cleanup(video_path, audio_path)
        
        # STEP 8: Process for Shorts
        logger.info("⚙️ STEP 8: Processing for Shorts...")
        processed_video = await process_video_for_shorts(video_no_audio, TARGET_DURATION, temp_dir)
        
        if not processed_video:
            return {"success": False, "error": "Video processing failed"}
        
        force_cleanup(video_no_audio)
        
        # STEP 9: Add text overlays
        if show_captions:
            logger.info("📝 STEP 9: Adding text overlays...")
            processed_video = await add_text_overlays(processed_video, script["segments"], temp_dir)
        
        # STEP 10: Generate voiceovers
        logger.info("🎤 STEP 10: Generating Hindi voiceovers...")
        voices = []
        
        for idx, seg in enumerate(script["segments"]):
            logger.info(f"   Voice {idx+1}/{len(script['segments'])}")
            voice = await generate_hindi_voice(seg["narration"], seg["duration"], temp_dir)
            if voice:
                voices.append(voice)
        
        if len(voices) < 3:
            logger.warning(f"⚠️ Only {len(voices)} voices generated")
        
        # STEP 11: Mix audio
        logger.info("🎬 STEP 11: Mixing audio...")
        final_video = await mix_audio_with_music(processed_video, voices, music, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Audio mixing failed"}
        
        # STEP 12: Upload to YouTube
        logger.info("📤 STEP 12: Uploading to YouTube...")
        
        upload_result = await upload_to_youtube(
            final_video,
            script["title"],
            f"Video {video_index} - {niche} content with Hindi voiceover",
            script["hashtags"],
            user_id,
            database_manager
        )
        
        # Cleanup temp directory
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        logger.info(f"✅ Video {video_index}/{total_videos} complete!")
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script["title"],
            "source_url": video_url,
            "index": video_index
        }
        
    except Exception as e:
        logger.error(f"❌ Video {video_index} failed: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e), "index": video_index}


async def process_profile_based_videos(
    niche: str,
    profile_urls: List[str],
    num_videos: int,
    user_id: str,
    show_captions: bool,
    database_manager
) -> dict:
    """
    Main pipeline: Scrape profiles → Process videos sequentially
    """
    
    try:
        logger.info(f"🚀 Starting profile-based automation")
        logger.info(f"   Niche: {niche}")
        logger.info(f"   Profiles: {len(profile_urls)}")
        logger.info(f"   Videos to generate: {num_videos}")
        
        # Step 1: Scrape all profiles for video URLs
        scraper = ProfileScraper()
        all_video_urls = []
        
        for profile_url in profile_urls:
            logger.info(f"📱 Scraping profile: {profile_url}")
            video_urls = scraper.scrape_profile_videos(profile_url, max_videos=10)
            all_video_urls.extend(video_urls)
            logger.info(f"   Found {len(video_urls)} videos")
            
            if len(all_video_urls) >= num_videos * 2:
                break  # Have enough videos
        
        scraper.close()
        
        if not all_video_urls:
            return {
                "success": False,
                "error": "No videos found in profiles. Please check profile URLs."
            }
        
        logger.info(f"✅ Total videos found: {len(all_video_urls)}")
        
        # Shuffle and limit to requested number
        random.shuffle(all_video_urls)
        videos_to_process = all_video_urls[:num_videos]
        
        # Step 2: Process videos sequentially (one at a time)
        results = []
        success_count = 0
        
        for idx, video_url in enumerate(videos_to_process, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"PROCESSING VIDEO {idx}/{num_videos}")
            logger.info(f"{'='*80}\n")
            
            result = await process_single_video(
                video_url=video_url,
                niche=niche,
                user_id=user_id,
                show_captions=show_captions,
                database_manager=database_manager,
                video_index=idx,
                total_videos=num_videos
            )
            
            results.append(result)
            
            if result.get("success"):
                success_count += 1
            
            # Small delay between videos
            if idx < num_videos:
                logger.info("⏸️ Waiting 5 seconds before next video...")
                await asyncio.sleep(5)
        
        logger.info(f"\n🎉 BATCH COMPLETE: {success_count}/{num_videos} successful")
        
        return {
            "success": True,
            "total_requested": num_videos,
            "successful": success_count,
            "failed": num_videos - success_count,
            "results": results,
            "niche": niche
        }
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        logger.error(traceback.format_exc())
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/china/niches")
async def get_niches():
    """Get available niches with default profile URLs"""
    return {
        "success": True,
        "niches": {
            key: {
                "name": config["name"],
                "icon": config["icon"],
                "english_keywords": config["english"][:3],
                "chinese_keywords": config["chinese"][:3],
                "default_profiles": config["profile_urls"]
            }
            for key, config in NICHE_KEYWORDS.items()
        }
    }

@router.post("/api/china/generate")
async def generate_endpoint(request: Request):
    """
    Generate videos from profile URLs
    
    Body:
    {
        "niche": "funny",
        "user_id": "user123",
        "num_videos": 3,
        "show_captions": true,
        "profile_urls": ["url1", "url2", "url3"]  // Optional, uses defaults if not provided
    }
    """
    try:
        data = await request.json()
        
        niche = data.get("niche", "funny")
        user_id = data.get("user_id")
        num_videos = data.get("num_videos", 1)
        show_captions = data.get("show_captions", True)
        custom_profile_urls = data.get("profile_urls", [])
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "user_id required"}
            )
        
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Invalid niche. Choose from: {list(NICHE_KEYWORDS.keys())}"
                }
            )
        
        # Use custom URLs or default ones
        if custom_profile_urls:
            profile_urls = custom_profile_urls
        else:
            profile_urls = NICHE_KEYWORDS[niche]["profile_urls"]
        
        # Validate num_videos
        if num_videos < 1 or num_videos > 10:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "num_videos must be between 1 and 10"}
            )
        
        from Supermain import database_manager
        
        logger.info(f"📨 Request: {user_id} / {niche} / {num_videos} videos")
        logger.info(f"   Profile URLs: {profile_urls}")
        
        try:
            result = await asyncio.wait_for(
                process_profile_based_videos(
                    niche=niche,
                    profile_urls=profile_urls,
                    num_videos=num_videos,
                    user_id=user_id,
                    show_captions=show_captions,
                    database_manager=database_manager
                ),
                timeout=1800  # 30 minutes for multiple videos
            )
            
            return JSONResponse(content=result)
            
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Timeout (30 min)"}
            )
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.post("/api/china/update-profiles")
async def update_profile_urls(request: Request):
    """
    Update profile URLs for a specific niche
    
    Body:
    {
        "niche": "funny",
        "profile_urls": ["url1", "url2", "url3"]
    }
    """
    try:
        data = await request.json()
        niche = data.get("niche")
        profile_urls = data.get("profile_urls", [])
        
        if not niche or niche not in NICHE_KEYWORDS:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid niche"}
            )
        
        if not profile_urls or not isinstance(profile_urls, list):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "profile_urls must be a non-empty list"}
            )
        
        # Update the profile URLs (in production, save to database)
        NICHE_KEYWORDS[niche]["profile_urls"] = profile_urls
        
        return JSONResponse(content={
            "success": True,
            "message": f"Updated {len(profile_urls)} profile URLs for {niche}",
            "niche": niche,
            "profile_urls": profile_urls
        })
        
    except Exception as e:
        logger.error(f"Update profiles error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.get("/api/china/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "success": True,
        "message": "China Video Automation - Profile Based Scraping",
        "niches": list(NICHE_KEYWORDS.keys()),
        "features": [
            "Profile URL scraping with Selenium",
            "Sequential video processing",
            "Automatic Hindi translation",
            "ElevenLabs voiceover",
            "YouTube Shorts upload (1080x1920)"
        ]
    }

__all__ = ['router']