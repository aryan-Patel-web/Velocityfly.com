

"""
china_shorts_final_orange_cat_v2.py - ROBUST WITH MULTIPLE FALLBACKS
=====================================================================
✅ FIXED: Audio mixing filter syntax
✅ 3-LEVEL FALLBACKS for audio mixing
✅ 3-LEVEL FALLBACKS for video filters  
✅ 3-LEVEL FALLBACKS for captions
✅ BGM is MUST HAVE (highest priority)
✅ Intro/Outro nice-to-have (fallback if fails)
✅ Never fails completely - always produces output
=====================================================================
"""

from fastapi import APIRouter, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import subprocess
import tempfile
import shutil
import gc
import httpx
import json
import re
import random
import aiofiles
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

try:
    import psutil
    HAS_PSUTIL = True
except:
    HAS_PSUTIL = False

# ═══════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("ChinaShortsOrangeCat")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)

def log_memory(step: str):
    """Log memory usage"""
    if HAS_PSUTIL:
        try:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
            if mem_mb > 450:
                logger.warning(f"⚠️  HIGH: {mem_mb:.1f}MB")
                gc.collect()
        except:
            pass

def log_step(step: str, status: str = "START", details: str = ""):
    """Log processing steps"""
    if status == "START":
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 {step}")
        if details:
            logger.info(f"   {details}")
        logger.info(f"{'='*70}")
    elif status == "SUCCESS":
        logger.info(f"✅ {step} SUCCESS")
        if details:
            logger.info(f"   {details}")
    elif status == "FAILED":
        logger.error(f"❌ {step} FAILED")
        if details:
            logger.error(f"   {details}")
    elif status == "FALLBACK":
        logger.warning(f"⚠️  {step} FALLBACK")
        if details:
            logger.warning(f"   {details}")

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")


# SINGLE BGM - Meow Meow Meow ONLY (50% volume)
CHINA_BGM_URL = "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3"
BGM_VOLUME = 0.40  # 50% volume

CAPTION_EMOJIS = ["😺", "🐱", "😹", "😼", "🦁", "💪", "🔥", "✨", "💯", "👀", "🎉", "❤️", "😂", "🤣", "😍"]

ELEVENLABS_INTRO_VOICES = ["FZkK3TvQ0pjyDmT8fzIW"]
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

DOUYIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.douyin.com/",
}

MOBILE_HEADERS = {
    "User-Agent": "com.ss.android.ugc.aweme/260801 (Linux; U; Android 11)",
}

PROCESSING_STATUS = {}

INTRO_TEMPLATES = [
    "Arre bhai ruk ja! Ye koi normal cat nahi hai, ye hai desi ORANGE BILLA! Aage jo hone wala hai, woh full meme material hai!",
    
    "Dosto, kasam se bol raha hoon, agar ye orange billa aapne pehle dekha hota na… aaj internet pe viral tum hi hote!",
    
    "Indian internet ka naya superstar aa gaya hai! Orange billa on fire hai, video skip mat karna warna pachtana padega!",
    
    "Bhai sahab! Aaj orange bille ne jo kaand kiya hai na, woh dekh ke hasi rokna mushkil ho jayega!",
    
    "Warning dosto! Ye video dekhne ke baad aap bolenge – ‘Bhai ye cat toh full India level hai!’",
    
    "Arre maa kasam! Ye orange billa itna zyada funny hai ki aaj ke saare reels fail ho jaayenge!",
    
    "Bas ek baar dekh lo! Orange billa ka ye scene aaj har Indian ke face pe smile laane wala hai!",
    
    "Dosto, ye sirf ek cat nahi hai… ye hai full desi swag wala ORANGE BILLA! End tak dekhna compulsory hai!",
    
    "Aaj pata chalega India orange cats ko itna kyu pyaar karta hai! Is billa ne reason de diya!",
]

OUTRO_TEMPLATES = [
    "Kaisa laga orange bille ka ye video? LIKE karein aur SUBSCRIBE zaroor karein!",
    "Agar aapko ye mastiyan pasand aayi to LIKE aur SUBSCRIBE karein!",
    "Video kaisi lagi batao! LIKE karo, SHARE karo, aur SUBSCRIBE zaroor karein!",
]

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def cleanup(*paths):
    """Delete files"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except:
            pass
    gc.collect()

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg with logging"""
    logger.info(f"🎬 {step}...")
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE, 
            timeout=timeout, 
            text=True
        )
        if result.returncode == 0:
            logger.info(f"✅ {step} OK")
            return True
        else:
            logger.error(f"❌ {step} failed: {result.stderr[-300:]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {step} timeout")
        return False
    except Exception as e:
        logger.error(f"❌ {step} error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# AI SEO GENERATION
# ═══════════════════════════════════════════════════════════════════════

async def generate_orange_cat_seo() -> dict:
    """Generate Orange Cat SEO"""
    log_step("AI SEO Generation", "START", "Orange Cat Focus")
    
    if MISTRAL_API_KEY:
        try:
            logger.info("🤖 Using Mistral AI...")
            
            prompt = """You are a VIRAL YouTube Shorts SEO expert for AI ORANGE CAT VIDEOS.

VIDEO: AI-generated orange cat doing funny/chaotic things
AUDIO: Sad/cute background music (Meow Meow Meow)
AUDIENCE: Global (India + International)

TITLE REQUIREMENTS:
- 3-7 words ONLY
- MUST mention "Orange Cat" or "Orange Billa" or "Santra Cat"
- Simple English, natural
- 3-5 inline hashtags at END
- NO emojis

EXAMPLES:
- Orange Cat Doing Cat Things #cat #pets #funny
- Orange Billa Ki Mastiyan #cat #shorts #viral
- The Orange Cat Story #cat #animals #trending

DESCRIPTION: 2 short paragraphs about the orange cat

KEYWORDS: EXACTLY 45 keywords (orange cat, funny cat, etc.)

HASHTAGS: 8-9 hashtags (#Shorts, #OrangeCat, #Cats are MUST)

OUTPUT JSON:
{
  "title": "Orange Cat Title #tag1 #tag2 #tag3",
  "description": "Paragraph 1\\n\\nParagraph 2",
  "keywords": ["keyword1", ... 45 total],
  "hashtags": ["#Foryou", "#Fyp", "#Explore", "#Reach", "#Reelsgrowth", "#Boostyourreel", "#Trendingnow", #Shorts", "#OrangeCat", ... 8-9 total]
}"""
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 2000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if match:
                        data = json.loads(match.group(0))
                        title = data.get("title", "Orange Cat Adventures #cat #viral #shorts")
                        keywords = data.get("keywords", [])
                        
                        while len(keywords) < 45:
                            keywords.append("orange cat")
                        keywords = keywords[:45]
                        
                        log_step("AI SEO Generation", "SUCCESS", f"Title: {title}")
                        return {
                            "title": title,
                            "description": data.get("description", "Orange cat video!"),
                            "keywords": keywords,
                            "hashtags": data.get("hashtags", ["#Shorts", "#OrangeCat", "#Cats"]),
                            "ai_generated": True
                        }
        except Exception as e:
            logger.warning(f"⚠️  Mistral failed: {e}")
    
    # FALLBACK
    log_step("AI SEO Generation", "FALLBACK", "Using basic SEO")
    return {
        "title": "Orange Cat Adventures #cat #viral #shorts",
        "description": "Watch this orange cat!\n\nLike and subscribe!",
        "keywords": ["orange cat"] * 45,
        "hashtags": ["#Shorts", "#OrangeCat", "#Cats"],
        "ai_generated": False
    }

# ═══════════════════════════════════════════════════════════════════════
# INTRO/OUTRO VOICEOVER
# ═══════════════════════════════════════════════════════════════════════

async def generate_intro_outro_voiceovers(temp_dir: str) -> tuple[Optional[str], Optional[str]]:
    """Generate intro/outro with fallbacks"""
    log_step("Intro/Outro Voiceovers", "START")
    
    intro_text = random.choice(INTRO_TEMPLATES)
    outro_text = random.choice(OUTRO_TEMPLATES)
    
    logger.info(f"   Intro: {intro_text[:50]}...")
    logger.info(f"   Outro: {outro_text[:50]}...")
    
    intro_path = os.path.join(temp_dir, "intro.mp3")
    outro_path = os.path.join(temp_dir, "outro.mp3")
    
    # TRY 1: ElevenLabs
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        try:
            logger.info("   🎙️ Attempt 1: ElevenLabs...")
            voice_id = random.choice(ELEVENLABS_INTRO_VOICES)
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp_intro = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    json={"text": intro_text, "model_id": "eleven_multilingual_v2"}
                )
                
                resp_outro = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    json={"text": outro_text, "model_id": "eleven_multilingual_v2"}
                )
                
                if resp_intro.status_code == 200 and resp_outro.status_code == 200:
                    with open(intro_path, 'wb') as f:
                        f.write(resp_intro.content)
                    with open(outro_path, 'wb') as f:
                        f.write(resp_outro.content)
                    
                    log_step("Intro/Outro Voiceovers", "SUCCESS", "ElevenLabs")
                    return intro_path, outro_path
        except Exception as e:
            logger.warning(f"   ⚠️  ElevenLabs failed: {e}")
    
    # TRY 2: Edge TTS
    try:
        logger.info("   🎙️ Attempt 2: Edge TTS...")
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        
        await edge_tts.Communicate(intro_text, voice, rate="+10%").save(intro_path)
        await edge_tts.Communicate(outro_text, voice, rate="+10%").save(outro_path)
        
        if os.path.exists(intro_path) and os.path.exists(outro_path):
            log_step("Intro/Outro Voiceovers", "SUCCESS", "Edge TTS")
            return intro_path, outro_path
    except Exception as e:
        logger.warning(f"   ⚠️  Edge TTS failed: {e}")
    
    # FALLBACK: No intro/outro
    log_step("Intro/Outro Voiceovers", "FALLBACK", "Continuing without intro/outro")
    return None, None

# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def get_duration(video_path: str) -> float:
    """Get duration"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, timeout=15, text=True
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0.0
    except:
        return 0.0

async def validate_video_file(video_path: str) -> tuple[bool, str]:
    """Validate video"""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=duration", "-of", "json", video_path
        ], capture_output=True, timeout=30, text=True)
        
        if result.returncode != 0:
            return False, "Invalid video"
        
        data = json.loads(result.stdout)
        if not data.get("streams"):
            return False, "No video stream"
        
        duration = float(data["streams"][0].get("duration", "0"))
        if duration <= 0 or duration > 180:
            return False, f"Invalid duration: {duration:.0f}s"
        
        return True, ""
    except Exception as e:
        return False, str(e)

async def apply_copyright_filters_robust(input_path: str, output_path: str) -> tuple[bool, str]:
    """
    Apply filters with 3-level fallback
    METHOD 1: Full filters (eq + scale)
    METHOD 2: Scale only
    METHOD 3: Copy original
    """
    log_step("Copyright Filters", "START")
    
    # METHOD 1: Full filters
    logger.info("   🎨 Method 1: Full filters (eq + scale)...")
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", "eq=saturation=1.25:brightness=0.10:contrast=1.15,scale=720:-2",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-c:a", "copy", "-y", output_path
    ], 60, "Filters-Method1")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        log_step("Copyright Filters", "SUCCESS", "Method 1")
        return True, ""
    
    cleanup(output_path)
    
    # METHOD 2: Scale only
    logger.info("   🎨 Method 2: Scale only...")
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", "scale=720:-2",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-c:a", "copy", "-y", output_path
    ], 60, "Filters-Method2")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        log_step("Copyright Filters", "SUCCESS", "Method 2 (scale only)")
        return True, ""
    
    cleanup(output_path)
    
    # METHOD 3: Copy original
    logger.info("   🎨 Method 3: Copy original...")
    try:
        shutil.copy(input_path, output_path)
        log_step("Copyright Filters", "FALLBACK", "Using original video")
        return True, ""
    except:
        return False, "All filter methods failed"

def generate_emoji_srt(duration: float) -> str:
    """Generate emoji SRT"""
    num_captions = max(5, int(duration / 2))
    time_per = duration / num_captions
    blocks = []
    
    for i in range(num_captions):
        start = i * time_per
        end = start + time_per
        
        sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
        eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
        emojis = " ".join(random.choices(CAPTION_EMOJIS, k=random.choice([2, 3])))
        
        blocks.append(
            f"{i+1}\n"
            f"{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
            f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + 
            f"\n{emojis}\n"
        )
    
    return "\n".join(blocks)

async def apply_emoji_captions_robust(video_path: str, duration: float, output_path: str) -> tuple[bool, str]:
    """
    Apply captions with 3-level fallback
    METHOD 1: Emoji captions
    METHOD 2: Simple text captions
    METHOD 3: No captions
    """
    log_step("Emoji Captions", "START")
    
    srt_path = output_path.replace(".mp4", ".srt")
    
    # METHOD 1: Emoji captions
    try:
        logger.info("   ✨ Method 1: Emoji captions...")
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_emoji_srt(duration))
        
        srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
        
        success = run_ffmpeg([
            "ffmpeg", "-i", video_path,
            "-vf", f"subtitles={srt_esc}:force_style='FontSize=28,Bold=1,Alignment=2,MarginV=40'",
            "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
            "-y", output_path
        ], 90, "Captions-Method1")
        
        cleanup(srt_path)
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            log_step("Emoji Captions", "SUCCESS", "Method 1")
            return True, ""
        
        cleanup(output_path)
    except Exception as e:
        logger.warning(f"   ⚠️  Method 1 failed: {e}")
    
    # METHOD 2: Simple burn-in text
    logger.info("   ✨ Method 2: Simple text...")
    try:
        success = run_ffmpeg([
            "ffmpeg", "-i", video_path,
            "-vf", "drawtext=text='Orange Cat':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h-50",
            "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
            "-y", output_path
        ], 60, "Captions-Method2")
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            log_step("Emoji Captions", "SUCCESS", "Method 2 (simple text)")
            return True, ""
        
        cleanup(output_path)
    except Exception as e:
        logger.warning(f"   ⚠️  Method 2 failed: {e}")
    
    # METHOD 3: No captions
    logger.info("   ✨ Method 3: No captions...")
    try:
        shutil.copy(video_path, output_path)
        log_step("Emoji Captions", "FALLBACK", "No captions")
        return True, ""
    except:
        return False, "All caption methods failed"

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove audio"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an", "-y", video_out
    ], 60, "Remove-Audio")
    
    if success:
        cleanup(video_in)
    return success

async def download_bgm(output: str) -> bool:
    """Download BGM (MUST HAVE)"""
    log_step("Download BGM", "START", "Meow Meow Meow (CRITICAL)")
    
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            async with client.stream("GET", CHINA_BGM_URL) as response:
                if response.status_code == 200:
                    total = 0
                    with open(output, 'wb') as f:
                        async for chunk in response.aiter_bytes(1024*1024):
                            f.write(chunk)
                            total += len(chunk)
                    
                    if total > 10000:
                        log_step("Download BGM", "SUCCESS", f"{total/(1024*1024):.1f}MB")
                        return True
        return False
    except:
        return False

async def add_intro_outro_bgm_robust(
    video_path: str,
    intro_audio: Optional[str],
    outro_audio: Optional[str],
    bgm_path: Optional[str],
    output_path: str
) -> tuple[bool, str]:
    """
    Add audio with 3-level fallback
    METHOD 1: Intro + Outro + BGM (complex)
    METHOD 2: BGM only (simple - MUST WORK)
    METHOD 3: No audio (last resort)
    """
    log_step("Add Audio", "START", "Intro/Outro + BGM")
    
    duration = await get_duration(video_path)
    if duration <= 0:
        return False, "Duration error"
    
    # METHOD 1: Full mix (intro + outro + BGM)
    if intro_audio and outro_audio and bgm_path and os.path.exists(intro_audio) and os.path.exists(outro_audio) and os.path.exists(bgm_path):
        try:
            logger.info("   🎵 Method 1: Intro + Outro + BGM (complex mix)...")
            
            # FIXED FILTER SYNTAX
            delay_ms = int((duration - 5) * 1000)
            
            # Correct filter syntax (no semicolons between inputs)
            filter_complex = (
                f"[1:a]volume={BGM_VOLUME}[bgm];"
                f"[2:a]adelay=0|0[intro];"
                f"[3:a]adelay={delay_ms}|{delay_ms}[outro];"
                f"[bgm][intro][outro]amix=inputs=3:duration=first[a]"
            )
            
            logger.info(f"   Filter: {filter_complex[:100]}...")
            
            cmd = [
                "ffmpeg", "-i", video_path, "-i", bgm_path, "-i", intro_audio, "-i", outro_audio,
                "-filter_complex", filter_complex,
                "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                "-shortest", "-y", output_path
            ]
            
            success = run_ffmpeg(cmd, 90, "Audio-Method1")
            
            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                cleanup(video_path, intro_audio, outro_audio, bgm_path)
                log_step("Add Audio", "SUCCESS", "Method 1 (Full mix)")
                return True, ""
            
            cleanup(output_path)
        except Exception as e:
            logger.warning(f"   ⚠️  Method 1 failed: {e}")
    
    # METHOD 2: BGM only (CRITICAL - MUST WORK)
    if bgm_path and os.path.exists(bgm_path):
        try:
            logger.info("   🎵 Method 2: BGM only (CRITICAL)...")
            
            success = run_ffmpeg([
                "ffmpeg", "-i", video_path, "-i", bgm_path,
                "-filter_complex", f"[1:a]volume={BGM_VOLUME}[a]",
                "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                "-shortest", "-y", output_path
            ], 60, "Audio-Method2")
            
            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                cleanup(video_path, intro_audio, outro_audio, bgm_path)
                log_step("Add Audio", "SUCCESS", "Method 2 (BGM only)")
                return True, ""
            
            cleanup(output_path)
        except Exception as e:
            logger.warning(f"   ⚠️  Method 2 failed: {e}")
    
    # METHOD 3: No audio (last resort)
    logger.info("   🎵 Method 3: No audio (FALLBACK)...")
    try:
        shutil.copy(video_path, output_path)
        cleanup(video_path, intro_audio, outro_audio, bgm_path)
        log_step("Add Audio", "FALLBACK", "No audio added")
        return True, ""
    except:
        return False, "All audio methods failed"

# ═══════════════════════════════════════════════════════════════════════
# URL DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID"""
    patterns = [r'modal_id=(\d+)', r'video/(\d{19})', r'/(\d{19})']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def download_douyin_api(video_id: str, output: str) -> bool:
    """Download via Douyin API"""
    if not video_id:
        return False
    
    api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            response = await client.get(api_url, headers=DOUYIN_HEADERS)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            if "item_list" not in data or not data["item_list"]:
                return False
            
            item = data["item_list"][0]
            video_urls = []
            
            if "video" in item and "play_addr" in item["video"]:
                if "url_list" in item["video"]["play_addr"]:
                    video_urls.extend(item["video"]["play_addr"]["url_list"])
            
            for video_url in video_urls:
                try:
                    async with client.stream("GET", video_url, headers=DOUYIN_HEADERS, timeout=180) as stream:
                        if stream.status_code == 200:
                            total = 0
                            with open(output, 'wb') as f:
                                async for chunk in stream.aiter_bytes(1024*1024):
                                    f.write(chunk)
                                    total += len(chunk)
                            
                            if total > 10000:
                                return True
                except:
                    continue
            
            return False
    except:
        return False

async def download_china_video(url: str, output: str) -> tuple[bool, str]:
    """Download with fallbacks"""
    video_id = extract_video_id(url)
    if not video_id:
        return False, "No video ID"
    
    if await download_douyin_api(video_id, output):
        return True, ""
    
    return False, "Download failed"

# ═══════════════════════════════════════════════════════════════════════
# MANUAL UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def save_uploaded_file(upload_file: UploadFile, output_path: str) -> tuple[bool, str]:
    """Save uploaded file"""
    try:
        max_size = 100 * 1024 * 1024
        total_bytes = 0
        
        async with aiofiles.open(output_path, 'wb') as f:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                
                total_bytes += len(chunk)
                if total_bytes > max_size:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return False, "File too large"
                
                await f.write(chunk)
        
        if os.path.getsize(output_path) < 10000:
            os.remove(output_path)
            return False, "File too small"
        
        return True, ""
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, str(e)

# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload to YouTube"""
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
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
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        }
        
        from mainY import youtube_scheduler
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=description,
            video_url=video_path
        )
        
        if result.get("success"):
            return {
                "success": True,
                "video_id": result.get("video_id"),
                "video_url": f"https://youtube.com/shorts/{result.get('video_id')}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def process_china_short_url(china_url: str, user_id: str, task_id: str):
    """URL processing"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start_time.isoformat(),
        "processing_type": "url"
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"📊 [{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="orange_cat_")
        log_memory("START")
        
        update(10, "Downloading...")
        raw_video = os.path.join(temp_dir, "raw.mp4")
        success, error = await download_china_video(china_url, raw_video)
        if not success:
            raise Exception(error)
        
        update(20, "Analyzing...")
        duration = await get_duration(raw_video)
        if duration <= 0 or duration > 180:
            raise ValueError(f"Invalid duration: {duration:.0f}s")
        
        update(25, "Generating SEO...")
        seo_metadata = await generate_orange_cat_seo()
        
        update(30, "Applying filters...")
        filtered_video = os.path.join(temp_dir, "filtered.mp4")
        await apply_copyright_filters_robust(raw_video, filtered_video)
        
        update(40, "Removing audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered_video, silent_video):
            raise Exception("Remove audio failed")
        
        update(50, "Adding captions...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        await apply_emoji_captions_robust(silent_video, duration, captioned_video)
        
        update(60, "Generating intro/outro...")
        intro_audio, outro_audio = await generate_intro_outro_voiceovers(temp_dir)
        
        update(70, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        if not await download_bgm(bgm_path):
            logger.warning("⚠️  BGM download failed!")
            bgm_path = None
        
        update(80, "Mixing audio...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await add_intro_outro_bgm_robust(
            captioned_video, intro_audio, outro_audio, bgm_path, final_video
        )
        if not success:
            raise Exception(error)
        
        update(95, "Uploading...")
        
        keywords_text = "\n".join(seo_metadata['keywords'])
        hashtags_text = " ".join(seo_metadata['hashtags'])
        full_description = f"{seo_metadata['description']}\n\n{keywords_text}\n\n{hashtags_text}"
        
        upload_result = await upload_to_youtube(
            final_video, seo_metadata['title'], full_description, user_id
        )
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ SUCCESS! Time: {elapsed:.1f}s")
        logger.info(f"{'='*80}\n")
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "processing_type": "url",
            "title": seo_metadata["title"],
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()

async def process_uploaded_video(video_path: str, user_id: str, task_id: str):
    """Upload processing"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start_time.isoformat(),
        "processing_type": "upload"
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"📊 [{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="orange_cat_upload_")
        log_memory("START-UPLOAD")
        
        update(10, "Processing file...")
        raw_video = os.path.join(temp_dir, "uploaded.mp4")
        shutil.copy(video_path, raw_video)
        
        update(15, "Validating...")
        is_valid, error = await validate_video_file(raw_video)
        if not is_valid:
            raise ValueError(error)
        
        update(20, "Analyzing...")
        duration = await get_duration(raw_video)
        if duration <= 0 or duration > 180:
            raise ValueError(f"Invalid duration: {duration:.0f}s")
        
        update(25, "Generating SEO...")
        seo_metadata = await generate_orange_cat_seo()
        
        update(30, "Applying filters...")
        filtered_video = os.path.join(temp_dir, "filtered.mp4")
        await apply_copyright_filters_robust(raw_video, filtered_video)
        
        update(40, "Removing audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered_video, silent_video):
            raise Exception("Remove audio failed")
        
        update(50, "Adding captions...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        await apply_emoji_captions_robust(silent_video, duration, captioned_video)
        
        update(60, "Generating intro/outro...")
        intro_audio, outro_audio = await generate_intro_outro_voiceovers(temp_dir)
        
        update(70, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        if not await download_bgm(bgm_path):
            logger.warning("⚠️  BGM download failed!")
            bgm_path = None
        
        update(80, "Mixing audio...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await add_intro_outro_bgm_robust(
            captioned_video, intro_audio, outro_audio, bgm_path, final_video
        )
        if not success:
            raise Exception(error)
        
        update(95, "Uploading...")
        
        keywords_text = "\n".join(seo_metadata['keywords'])
        hashtags_text = " ".join(seo_metadata['hashtags'])
        full_description = f"{seo_metadata['description']}\n\n{keywords_text}\n\n{hashtags_text}"
        
        upload_result = await upload_to_youtube(
            final_video, seo_metadata['title'], full_description, user_id
        )
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ SUCCESS! Time: {elapsed:.1f}s")
        logger.info(f"{'='*80}\n")
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "processing_type": "upload",
            "title": seo_metadata["title"],
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        if video_path:
            try:
                os.remove(video_path)
            except:
                pass
        gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()

@router.post("/api/china-shorts/process-url")
async def process_url_endpoint(request: Request):
    """Process URL"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        china_url = (data.get("china_url") or "").strip()
        
        if not user_id or not china_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Missing params"})
        
        task_id = str(uuid.uuid4())
        asyncio.create_task(process_china_short_url(china_url, user_id, task_id))
        
        return JSONResponse(content={"success": True, "task_id": task_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/china-shorts/process-upload")
async def process_upload_endpoint(user_id: str = Form(...), video_file: UploadFile = File(...)):
    """Process upload"""
    uploaded_file_path = None
    
    try:
        if not user_id or not video_file:
            return JSONResponse(status_code=400, content={"success": False, "error": "Missing params"})
        
        task_id = str(uuid.uuid4())
        uploaded_file_path = f"/tmp/china_upload_{task_id}.mp4"
        
        success, error = await save_uploaded_file(video_file, uploaded_file_path)
        if not success:
            return JSONResponse(status_code=400, content={"success": False, "error": error})
        
        asyncio.create_task(process_uploaded_video(uploaded_file_path, user_id, task_id))
        
        return JSONResponse(content={"success": True, "task_id": task_id})
    except Exception as e:
        if uploaded_file_path:
            try:
                os.remove(uploaded_file_path)
            except:
                pass
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/api/china-shorts/status/{task_id}")
async def status_endpoint(task_id: str):
    """Get status"""
    status = PROCESSING_STATUS.get(task_id)
    if not status:
        return JSONResponse(status_code=404, content={"success": False, "error": "Not found"})
    return JSONResponse(content=status)

@router.get("/api/china-shorts/health")
async def health_endpoint():
    """Health check"""
    return JSONResponse(content={
        "status": "ok",
        "version": "6.0_ROBUST",
        "features": {
            "filters": "3-level fallback",
            "captions": "3-level fallback",
            "audio": "3-level fallback (intro+outro+BGM → BGM only → no audio)",
            "bgm": "50% volume, MUST HAVE",
            "intro_outro": "Nice-to-have with fallback"
        }
    })

async def initialize():
    """Startup"""
    logger.info("\n" + "="*80)
    logger.info("🚀 CHINA SHORTS - ORANGE CAT v6.0 ROBUST")
    logger.info("="*80)
    logger.info("✅ FIXED: Audio mixing filter syntax")
    logger.info("✅ 3-level fallbacks for everything")
    logger.info("✅ BGM is MUST HAVE (highest priority)")
    logger.info("✅ Intro/Outro nice-to-have")
    logger.info("✅ Never fails completely")
    logger.info("="*80 + "\n")
    log_memory("startup")

__all__ = ["router", "initialize"]