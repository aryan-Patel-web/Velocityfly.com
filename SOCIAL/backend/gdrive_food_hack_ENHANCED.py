"""
gdrive_food_hack_ENHANCED.py - FOOD HACK AI VIDEO PROCESSOR (RENDER-OPTIMIZED)
===================================================================
✅ Multi-character AI voices (ElevenLabs 3-4 voices)
✅ 1.1x voiceover speed for all TTS platforms
✅ Trending kids BGM (ringtone style) at 10-20% volume
✅ Live captions with multiple open-source libraries (fallback system)
✅ Emotional connection: "Bye bye mere dosto" in every script
✅ Smart AI script: minimal changes to transcript (time-synced)
✅ Video enhancements: saturation, contrast, vibrance, sharpness, brightness
✅ SEO: 35-45 keywords + 7-9 hashtags + 2-3 hashtags in title
✅ Direct YouTube upload with all metadata
✅ COMPREHENSIVE FALLBACK SYSTEM - Never fails completely
===================================================================
"""

from fastapi import APIRouter, Request
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
from typing import Optional, List, Dict
from datetime import datetime
import uuid
import hashlib

try:
    import psutil
    HAS_PSUTIL = True
except:
    HAS_PSUTIL = False

# ═══════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("FoodHackAI")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def log_memory(step: str):
    """Log memory usage"""
    if HAS_PSUTIL:
        try:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
            if mem_mb > 450:
                logger.warning(f"⚠️ HIGH: {mem_mb:.1f}MB")
                gc.collect()
                gc.collect()
                gc.collect()
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
GROQ_API_KEY = os.getenv("GROQ_SPEECH_API")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Edge TTS Hindi voices for fallback
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

# ElevenLabs MULTI-CHARACTER Voice IDs (4 voices for natural conversation)
ELEVENLABS_VOICE_IDS = [
    "FZkK3TvQ0pjyDmT8fzIW",  # Character 1
    "siw1N9V8LmYeEWKyWBxv",  # Character 1
    "uB7ZNdedZ982ZAoaaf0W",  # Character 2
    "Icov0pR6jgWuaZhmlmtO",  # Character 3
    "gHu9GtaHOXcSqFTK06ux"   # Character 4
]

# ═══════════════════════════════════════════════════════════════════════
# TRENDING KIDS BGM (RINGTONE STYLE - ROYALTY FREE)
# ═══════════════════════════════════════════════════════════════════════
KIDS_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Twinkle%20Twinkle%20Little%20Star%20Instrumental%20-%20Kids%20Ringtone.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Happy%20Birthday%20Instrumental%20-%20Celebration%20Ringtone.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Baby%20Shark%20Instrumental%20-%20Viral%20Kids%20BGM.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Johny%20Johny%20Yes%20Papa%20Instrumental.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Wheels%20On%20The%20Bus%20Instrumental.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Old%20MacDonald%20Had%20a%20Farm%20Instrumental.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/If%20You're%20Happy%20and%20You%20Know%20It%20Instrumental.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Row%20Row%20Row%20Your%20Boat%20Instrumental.mp3",
]

PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════

def cleanup(*paths):
    """Delete files and force garbage collection"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                size = os.path.getsize(path) / (1024 * 1024)
                os.remove(path)
                logger.info(f"   🗑️ {os.path.basename(path)} ({size:.1f}MB)")
        except:
            pass
    gc.collect()
    gc.collect()
    gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# FFMPEG
# ═══════════════════════════════════════════════════════════════════════

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg command"""
    logger.info(f"🎬 {step}...")
    log_memory(f"before-{step}")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )
        
        success = result.returncode == 0
        
        if success:
            logger.info(f"✅ {step}")
        else:
            logger.error(f"❌ {step} failed")
            if result.stderr:
                logger.error(f"   Error: {result.stderr[-200:]}")
        
        gc.collect()
        log_memory(f"after-{step}")
        return success
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ {step} timeout")
        gc.collect()
        return False
    except Exception as e:
        logger.error(f"❌ {step} error: {e}")
        gc.collect()
        return False

# ═══════════════════════════════════════════════════════════════════════
# GOOGLE DRIVE DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════

def extract_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID"""
    if not url or "drive.google.com" not in url:
        return None
    
    patterns = [r'/file/d/([a-zA-Z0-9_-]{25,})', r'[?&]id=([a-zA-Z0-9_-]{25,})']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def download_chunked(url: str, output: str) -> bool:
    """Download file in chunks"""
    try:
        async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    return False
                
                total = 0
                with open(output, 'wb') as f:
                    async for chunk in response.aiter_bytes(1024*1024):
                        f.write(chunk)
                        total += len(chunk)
                        if total % (5*1024*1024) < 1024*1024:
                            logger.info(f"   📥 {total/(1024*1024):.1f}MB")
                
                if total > 10000:
                    logger.info(f"   ✅ {total/(1024*1024):.1f}MB")
                    return True
        return False
    except Exception as e:
        logger.error(f"   ❌ {e}")
        return False

async def download_from_gdrive(file_id: str, output: str) -> tuple[bool, str]:
    """Download from Google Drive with fallbacks"""
    logger.info("⬇️ Downloading...")
    log_memory("download-start")
    
    urls = [
        f"https://drive.google.com/uc?export=download&id={file_id}",
        f"https://drive.usercontent.google.com/download?id={file_id}&export=download",
    ]
    
    for idx, url in enumerate(urls, 1):
        logger.info(f"📥 Method {idx}/{len(urls)}")
        if await download_chunked(url, output):
            logger.info(f"✅ Downloaded")
            log_memory("download-done")
            return True, ""
        await asyncio.sleep(1)
    
    return False, "Download failed"

# ═══════════════════════════════════════════════════════════════════════
# VIDEO COMPRESSION (WITH FALLBACK)
# ═══════════════════════════════════════════════════════════════════════

async def try_compress_video(input_path: str, output_path: str, timeout: int = 60) -> bool:
    """Try to compress video to 720p with fallback"""
    logger.info("🔧 Trying to compress to 720p...")
    log_memory("compress-start")
    
    # METHOD 1: Standard 720p compression
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", "scale=720:-2",
        "-c:v", "libx264",
        "-crf", "28",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-b:a", "96k",
        "-y", output_path
    ], timeout=timeout, step="Compress-720p")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        cleanup(input_path)
        size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Compressed: {size:.1f}MB")
        log_memory("compress-done")
        return True
    
    # METHOD 2: Fallback - Just copy codec (faster)
    logger.warning("⚠️ Trying copy codec fallback...")
    cleanup(output_path)
    
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-c:v", "copy",
        "-c:a", "copy",
        "-y", output_path
    ], timeout=30, step="Compress-Copy")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        cleanup(input_path)
        size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Copied: {size:.1f}MB")
        log_memory("compress-done")
        return True
    
    # METHOD 3: Final fallback - use original
    cleanup(output_path)
    logger.warning("⚠️ Compression failed, using original video")
    log_memory("compress-failed")
    return False

# ═══════════════════════════════════════════════════════════════════════
# VIDEO INFO
# ═══════════════════════════════════════════════════════════════════════

async def get_duration(video_path: str) -> float:
    """Get video duration"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, timeout=15, text=True
        )
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"⏱️ {duration:.1f}s")
            return duration
        return 0.0
    except:
        return 0.0

# ═══════════════════════════════════════════════════════════════════════
# AUDIO EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

async def extract_audio(video_path: str, audio_path: str) -> bool:
    """Extract audio from video"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ], timeout=60, step="Extract-Audio")
    
    return success

# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_audio(audio_path: str) -> tuple[Optional[str], str]:
    """Transcribe audio with Groq Whisper"""
    logger.info("📝 Transcribing...")
    log_memory("transcribe-start")
    
    if not GROQ_API_KEY:
        return None, "No API key"
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            with open(audio_path, "rb") as f:
                files = {"file": ("audio.wav", f, "audio/wav")}
                data = {"model": "whisper-large-v3", "language": "hi", "response_format": "text"}
                
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    transcript = response.text.strip()
                    if len(transcript) > 5:
                        logger.info(f"✅ Transcribed ({len(transcript)} chars)")
                        logger.info(f"   {transcript[:100]}...")
                        log_memory("transcribe-done")
                        
                        cleanup(audio_path)
                        return transcript, ""
        
        cleanup(audio_path)
        return None, "Empty response"
    except Exception as e:
        cleanup(audio_path)
        logger.error(f"❌ Transcription error: {e}")
        return None, str(e)

# ═══════════════════════════════════════════════════════════════════════
# SMART AI SCRIPT (MINIMAL CHANGES + EMOTIONAL CONNECTION)
# ═══════════════════════════════════════════════════════════════════════

async def generate_food_hack_script(transcript: str, duration: float) -> dict:
    """
    Generate SMART script for food hack videos with fallback
    """
    logger.info("🤖 AI Script (Smart + Emotional)...")
    log_memory("ai-start")
    
    words = int(duration * 2.5)
    emotional_ending = "Bye bye mere dosto! Agar aapko yeh hack pasand aayi ho toh LIKE karein, SUBSCRIBE karein aur apne doston ko SHARE karein!"
    
    # Try Mistral AI for smart script generation
    if MISTRAL_API_KEY:
        try:
            logger.info("   Using Mistral AI for smart food hack script...")
            
            prompt = f"""Generate a SMART food hack script with MINIMAL changes to transcript:

ORIGINAL TRANSCRIPT: {transcript}
DURATION: {duration} seconds (approximately {words} words)

CRITICAL RULES:
1. Keep 80-90% of the original transcript UNCHANGED
2. Only improve clarity, fix grammar, and add connectors
3. If multiple speakers detected, label them as [Character 1], [Character 2], etc.
4. Add emotional ending: "{emotional_ending}"
5. MUST fit within {duration} seconds (strict timing)
6. Natural conversational Hindi (food hack style)

SEO REQUIREMENTS:
7. Generate a VIRAL Hinglish TITLE with 2-3 hashtags:
You are a viral YouTube Shorts title generator for AI food videos.

TASK:
Generate ONE Hinglish YouTube Shorts title for a short video (≤30s) that may contain MULTIPLE food items.

IMPORTANT LOGIC (MUST FOLLOW):
a. Identify the SINGLE “HERO FOOD”:
   - The food shown first OR
   - The food shown longest OR
   - The most common / visually strong food OR
   - The food most relatable to a general audience
b. Ignore all other foods for the TITLE.
c. Never list multiple foods in the title unless they are a famous combo.

RULES (STRICT):
- Mention ONLY the HERO FOOD naturally
- Use a curiosity gap using ONE of:
  "Galti", "Aaj Tak", "99% Log", "Bas 1"
- 6–10 words total
- Use EXACTLY 2 matching food emojis
- End with EXACTLY: #Shorts #Viral
- No health, medical, or guarantee claims
- Do NOT explain the recipe or ingredients
- Title must feel natural, not promotional

OPTIONAL BOOST (USE ONLY IF IT FITS):
- You may subtly mention AI once (e.g., "AI Ne Bataya") to increase curiosity

OUTPUT FORMAT:
- Output ONLY the title
- No quotes
- No explanations

EXAMPLES (STYLE ONLY):

99% Log Banana Ke Saath Yeh Galti Karte Hain 🍌🔥 #Shorts #Viral 
Aaj Tak Pizza Ka Yeh Sach Nahi Pata Tha 🍕😳 #Shorts #Viral
AI Ne Bataya Burger Ki Yeh Galti 🍔😳 #Shorts #Viral
Bas 1 Trick, Fries Aur Bhi Better 🍟🔥 #Shorts #Viral

Now generate the title.


8. Write Hinglish DESCRIPTION (2 paragraphs + 35-45 keywords):
   - First paragraph: Hook about the food hack
   - Second paragraph: Benefits/results
   - Keywords section: 35-45 food-related keywords (vertical format)

9. Generate 7-9 HASHTAGS:
   - Must include: #Shorts, #FoodHack, #Viral
   - 4-6 food-specific tags

10. CHARACTER DETECTION:
   - If 2+ speakers detected, split script by character
   - Format: [{{"character": 1, "text": "..."}}, {{"character": 2, "text": "..."}}]

Generate in JSON format:
{{
    "script": "Complete Hindi script...",
    "characters": [{{"character": 1, "text": "..."}}],
    "title": "Viral title with hashtags",
    "description": "Description with keywords",
    "hashtags": ["#FoodHack", "#Shorts", "#Viral"],
    "num_characters": 1
}}"""
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "You are a food content creator. Make MINIMAL changes to transcripts. Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1500
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if match:
                        data = json.loads(match.group(0))
                        script_text = data.get("script", transcript)
                        
                        if "Bye bye mere dosto" not in script_text:
                            script_text += " " + emotional_ending
                        
                        characters = data.get("characters", [{"character": 1, "text": script_text}])
                        num_characters = data.get("num_characters", len(characters))
                        title = data.get("title", "Amazing Food Hack! 🍕🔥 #FoodHack #Viral #Shorts")
                        description = data.get("description", f"{transcript[:200]}\\n\\nKeywords: food hack, easy recipe, quick food, viral shorts")
                        hashtags = data.get("hashtags", ["#FoodHack", "#Shorts", "#Viral", "#EasyRecipe", "#Hindi"])
                        
                        logger.info(f"✅ AI Script Generated ({num_characters} characters)")
                        logger.info(f"   Title: {title}")
                        log_memory("ai-done")
                        
                        return {
                            "script": script_text,
                            "characters": characters,
                            "num_characters": num_characters,
                            "title": title,
                            "description": description,
                            "hashtags": hashtags
                        }
        except Exception as e:
            logger.warning(f"   Mistral failed: {e}")
    
    # FALLBACK: Use transcript with basic modifications
    logger.info("   Using transcript (fallback with basic SEO)")
    script = " ".join(transcript.split()[:words]) + " " + emotional_ending
    
    title_base = " ".join(transcript.split()[:5])
    title = f"{title_base}... 🍕🔥 #FoodHack #Viral #Shorts"
    
    description = f"{transcript[:150]}...\n\nKeywords: food hack, easy recipe, quick food, viral shorts, hindi food, cooking tips, kitchen hacks, food tips, instant recipe, trending food"
    hashtags = ["#FoodHack", "#Shorts", "#Viral", "#EasyRecipe", "#QuickFood", "#Hindi", "#Trending"]
    
    log_memory("ai-done")
    
    return {
        "script": script,
        "characters": [{"character": 1, "text": script}],
        "num_characters": 1,
        "title": title,
        "description": description,
        "hashtags": hashtags
    }

# ═══════════════════════════════════════════════════════════════════════
# MULTI-CHARACTER VOICEOVER (WITH COMPREHENSIVE FALLBACK)
# ═══════════════════════════════════════════════════════════════════════

async def generate_multi_character_voiceover(characters: List[Dict], output: str) -> tuple[bool, str]:
    """Generate voiceover with ElevenLabs + Edge TTS fallback"""
    logger.info(f"🎙️ Multi-Character Voiceover ({len(characters)} characters, 1.1x speed)...")
    log_memory("voice-start")
    
    # METHOD 1: Try ElevenLabs
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        try:
            temp_audio_files = []
            
            for idx, char_data in enumerate(characters):
                character_num = char_data.get("character", 1)
                text = char_data.get("text", "")
                
                if not text.strip():
                    continue
                
                voice_id = ELEVENLABS_VOICE_IDS[(character_num - 1) % len(ELEVENLABS_VOICE_IDS)]
                logger.info(f"   Generating Character {character_num} with voice {voice_id[:8]}...")
                
                try:
                    async with httpx.AsyncClient(timeout=60) as client:
                        resp = await client.post(
                            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                            headers={"xi-api-key": ELEVENLABS_API_KEY},
                            json={"text": text[:2000], "model_id": "eleven_multilingual_v2"}
                        )
                        
                        if resp.status_code == 200:
                            temp_audio = output.replace(".mp3", f"_char{character_num}_base.mp3")
                            with open(temp_audio, 'wb') as f:
                                f.write(resp.content)
                            
                            speed_audio = output.replace(".mp3", f"_char{character_num}_speed.mp3")
                            if run_ffmpeg(["ffmpeg", "-i", temp_audio, "-filter:a", "atempo=1.1", "-y", speed_audio], 30):
                                temp_audio_files.append(speed_audio)
                                cleanup(temp_audio)
                            else:
                                temp_audio_files.append(temp_audio)
                except Exception as e:
                    logger.warning(f"   Character {character_num} ElevenLabs failed: {e}")
                    continue
            
            if temp_audio_files:
                if len(temp_audio_files) == 1:
                    os.rename(temp_audio_files[0], output)
                else:
                    logger.info(f"   Merging {len(temp_audio_files)} character audios...")
                    concat_file = output.replace(".mp3", "_concat.txt")
                    with open(concat_file, 'w') as f:
                        for audio_file in temp_audio_files:
                            f.write(f"file '{audio_file}'\n")
                    
                    if run_ffmpeg(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", "-y", output], 60):
                        cleanup(concat_file, *temp_audio_files)
                    else:
                        cleanup(concat_file, *temp_audio_files)
                        raise Exception("Merge failed")
                
                size = os.path.getsize(output) / 1024
                logger.info(f"✅ Multi-Character Voiceover (1.1x): {size:.1f}KB")
                log_memory("voice-done")
                return True, ""
        except Exception as e:
            logger.warning(f"   ElevenLabs failed: {e}")
    
    # METHOD 2: Fallback to Edge TTS
    return await fallback_single_voiceover(" ".join([c["text"] for c in characters]), output)

async def fallback_single_voiceover(script: str, output: str) -> tuple[bool, str]:
    """Fallback to Edge TTS for single voice"""
    logger.info("🔄 Falling back to Edge TTS (single voice)...")
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        logger.info(f"   Using {voice}")
        
        base = output.replace(".mp3", "_edge_base.mp3")
        await edge_tts.Communicate(script[:2000], voice, rate="+20%").save(base)
        
        if run_ffmpeg(["ffmpeg", "-i", base, "-filter:a", "atempo=1.1", "-y", output], 30):
            cleanup(base)
            size = os.path.getsize(output) / 1024
            logger.info(f"✅ Edge TTS Voiceover (1.1x): {size:.1f}KB")
            log_memory("voice-done")
            return True, ""
        
        if os.path.exists(base):
            os.rename(base, output)
            size = os.path.getsize(output) / 1024
            logger.info(f"✅ Edge TTS Voiceover (base): {size:.1f}KB")
            log_memory("voice-done")
            return True, ""
    except Exception as e:
        logger.error(f"❌ Edge TTS error: {e}")
    
    logger.error("❌ All voiceover methods failed!")
    return False, "Voiceover generation failed"

# ═══════════════════════════════════════════════════════════════════════
# LIVE CAPTIONS (WITH COMPREHENSIVE FALLBACK)
# ═══════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════
# IMPROVED LIVE CAPTIONS - SMALL, PROFESSIONAL, KEY WORDS ONLY
# ═══════════════════════════════════════════════════════════════════════

def generate_srt(script: str, duration: float) -> str:
    """
    Generate SRT subtitle file with SMALL, KEY WORDS ONLY
    - Only 2-3 words per caption (most important words)
    - Removes filler words (hai, ka, ki, etc.)
    - Short, punchy captions like professional food reels
    """
    words = script.split()
    
    # Hindi filler words to remove
    filler_words = {
        'hai', 'hain', 'ka', 'ki', 'ko', 'se', 'me', 'mein', 'aur', 
        'par', 'yeh', 'woh', 'tha', 'thi', 'the', 'ke', 'kya', 'kaise',
        'jo', 'ji', 'toh', 'to', 'na', 'ne', 'hi', 'bhi', 'ek', 'do'
    }
    
    # Extract only important words (nouns, verbs, adjectives)
    important_words = [w for w in words if w.lower() not in filler_words and len(w) > 2]
    
    # Create short 2-3 word captions (KEY PHRASES ONLY)
    phrases = []
    i = 0
    while i < len(important_words):
        # Take only 2 important words per caption for clean look
        phrase = " ".join(important_words[i:i+2])
        if phrase:
            phrases.append(phrase)
        i += 2
    
    # Fallback: if no important words found, use original in pairs
    if not phrases:
        phrases = [" ".join(words[i:i+2]) for i in range(0, len(words), 2) if words[i:i+2]]
    
    if not phrases:
        return ""
    
    # Distribute captions evenly across video duration
    time_per = duration / len(phrases)
    blocks = []
    
    for i, phrase in enumerate(phrases):
        start = i * time_per
        end = start + time_per
        
        sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
        eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
        blocks.append(
            f"{i+1}\n"
            f"{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
            f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + 
            f"\n{phrase}\n"
        )
    
    return "\n".join(blocks)


async def apply_live_captions(video_path: str, script: str, duration: float, output_path: str) -> tuple[bool, str]:
    """
    Apply PROFESSIONAL live captions with PROPER STYLING
    - Small text size (18-20 instead of 24-26)
    - Yellow/white color for visibility
    - Proper font (Noto Sans for Hindi support)
    - Clean outline for readability
    """
    logger.info("✨ Live Captions (Small, Professional Style)...")
    log_memory("caption-start")
    
    srt_path = output_path.replace(".mp4", "_captions.srt")
    
    try:
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_srt(script, duration))
    except Exception as e:
        logger.warning(f"⚠️ SRT generation failed: {e}, skipping captions")
        if os.path.exists(video_path):
            shutil.copy(video_path, output_path)
        return True, ""
    
    # Escape path for FFmpeg
    srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
    # METHOD 1: Professional Yellow Captions (SMALL SIZE, CLEAN)
    logger.info("   Method 1: Professional yellow captions (small size)...")
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFF00,Bold=1,Outline=2,OutlineColour=&H00000000,BorderStyle=3,Alignment=2,MarginV=40'",
        "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
        "-y", output_path
    ], 120, "Captions-Yellow-Small")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        cleanup(srt_path)
        logger.info("✅ Professional yellow captions applied (small)")
        log_memory("caption-done")
        return True, ""
    
    # METHOD 2: White Captions (FALLBACK, SMALL SIZE)
    logger.warning("⚠️ Trying white captions (small size)...")
    cleanup(output_path)
    
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,Bold=1,Outline=2,OutlineColour=&H00000000,BorderStyle=3,Alignment=2,MarginV=40'",
        "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
        "-y", output_path
    ], 120, "Captions-White-Small")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        cleanup(srt_path)
        logger.info("✅ White captions applied (small)")
        log_memory("caption-done")
        return True, ""
    
    # METHOD 3: Simple Captions (MINIMAL STYLE)
    logger.warning("⚠️ Trying minimal captions...")
    cleanup(output_path)
    
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_esc}:force_style='FontSize=16,Bold=1,Outline=1,Alignment=2,MarginV=30'",
        "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
        "-y", output_path
    ], 120, "Captions-Minimal")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        cleanup(srt_path)
        logger.info("✅ Minimal captions applied")
        log_memory("caption-done")
        return True, ""
    
    # METHOD 4: No captions fallback (ALWAYS SUCCEEDS)
    logger.warning("⚠️ All caption methods failed, continuing without captions")
    cleanup(srt_path, output_path)
    
    if os.path.exists(video_path):
        shutil.copy(video_path, output_path)
        logger.info("✅ Video copied (no captions)")
        log_memory("caption-done")
        return True, ""
    
    return False, "Caption processing failed"


# ═══════════════════════════════════════════════════════════════════════
# CAPTION STYLING GUIDE
# ═══════════════════════════════════════════════════════════════════════






# ═══════════════════════════════════════════════════════════════════════
# VIDEO ENHANCEMENTS (RENDER-OPTIMIZED WITH FALLBACK)
# ═══════════════════════════════════════════════════════════════════════

async def enhance_video_quality(input_path: str, output_path: str) -> tuple[bool, str]:
    """Apply video enhancements with COMPREHENSIVE FALLBACK"""
    logger.info("🎨 Video Enhancement (Render-optimized)...")
    log_memory("enhance-start")
    
    # METHOD 1: Simple enhancement (RENDER-OPTIMIZED)
    filter_complex = "eq=saturation=1.2:contrast=1.1"  # Reduced complexity
    
    logger.info("   Applying: Saturation +20%, Contrast +10% (cloud-optimized)")
    
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", filter_complex,
        "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
        "-c:a", "copy",
        "-y", output_path
    ], 90, "Video-Enhancement")  # Reduced from 180 to 90
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Enhanced: {size:.1f}MB")
        log_memory("enhance-done")
        return True, ""
    
    # METHOD 2: Just copy (ALWAYS SUCCEEDS)
    logger.warning("⚠️ Enhancement failed, using original video")
    cleanup(output_path)
    
    if os.path.exists(input_path):
        shutil.copy(input_path, output_path)
        size = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Original video: {size:.1f}MB")
        log_memory("enhance-done")
        return True, ""
    
    return False, "Enhancement failed"

# ═══════════════════════════════════════════════════════════════════════
# AUDIO MIXING (WITH FALLBACK)
# ═══════════════════════════════════════════════════════════════════════

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove audio from video"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an",
        "-y", video_out
    ], timeout=60, step="Remove-Audio")
    
    if success:
        cleanup(video_in)
    
    return success

async def download_kids_bgm(output: str) -> bool:
    """Download kids BGM (ringtone style)"""
    logger.info("🎵 Kids BGM (Trending Ringtone Style)...")
    log_memory("bgm-start")
    
    bgm_url = random.choice(KIDS_BGM_URLS)
    logger.info(f"   Selected: {bgm_url.split('/')[-1][:50]}...")
    
    try:
        success = await download_chunked(bgm_url, output)
        
        if success:
            logger.info("✅ Kids BGM Downloaded")
            log_memory("bgm-done")
            return True
        
        logger.warning("⚠️ BGM download failed")
        return False
    except:
        logger.warning("⚠️ BGM error")
        return False

async def mix_audio_with_bgm(video_path: str, voice_path: str, bgm_path: Optional[str], output_path: str) -> tuple[bool, str]:
    """Mix voiceover with BGM with COMPREHENSIVE FALLBACK"""
    logger.info("🎵 Mixing Audio (Voice + Kids BGM at 15%)...")
    log_memory("mix-start")
    
    # METHOD 1: Try mixing with BGM
    if bgm_path and os.path.exists(bgm_path):
        logger.info("   Mixing voice + BGM (BGM volume: 15%)...")
        success = run_ffmpeg([
            "ffmpeg", "-i", video_path, "-i", voice_path, "-i", bgm_path,
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output_path
        ], 120, "Mix-Voice-BGM")
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            cleanup(video_path, voice_path, bgm_path)
            log_memory("mix-done")
            return True, ""
        
        logger.warning("⚠️ Mix with BGM failed, trying without BGM...")
        cleanup(output_path)
    
    # METHOD 2: Voice only (no BGM)
    logger.info("   Adding voice only (no BGM)...")
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path, "-i", voice_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
        "-shortest", "-y", output_path
    ], 90, "Add-Voice")
    
    cleanup(video_path, voice_path, bgm_path)
    
    if not success:
        return False, "Audio mix failed"
    
    log_memory("mix-done")
    return True, ""

# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload to YouTube with SEO metadata"""
    logger.info("📤 YouTube Upload...")
    log_memory("upload-start")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds:
            return {"success": False, "error": "No YouTube credentials"}
        
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
            video_id = result.get("video_id")
            logger.info(f"✅ Uploaded: {video_id}")
            log_memory("upload-done")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        logger.error(f"❌ {e}")
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE (WITH COMPREHENSIVE ERROR HANDLING)
# ═══════════════════════════════════════════════════════════════════════

async def process_food_hack_video(drive_url: str, user_id: str, task_id: str):
    """Main pipeline with COMPREHENSIVE FALLBACK at every step"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start_time.isoformat()
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"[{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="food_hack_")
        logger.info(f"📁 {temp_dir}")
        log_memory("START")
        
        # Extract ID
        update(5, "Extracting Google Drive ID...")
        file_id = extract_file_id(drive_url)
        if not file_id:
            raise ValueError("Invalid Google Drive URL")
        
        # Download
        update(10, "Downloading video...")
        raw_video = os.path.join(temp_dir, "raw.mp4")
        success, error = await download_from_gdrive(file_id, raw_video)
        if not success:
            raise Exception(error)
        
        # Compress (with fallback)
        update(15, "Compressing video...")
        compressed_video = os.path.join(temp_dir, "compressed.mp4")
        compression_success = await try_compress_video(raw_video, compressed_video, timeout=90)
        
        working_video = compressed_video if compression_success else raw_video
        
        # Get duration
        update(20, "Analyzing video...")
        duration = await get_duration(working_video)
        if duration <= 0:
            raise ValueError("Invalid video")
        if duration > 180:
            raise ValueError(f"Video too long ({duration:.0f}s)")
        
        # Extract audio
        update(25, "Extracting audio...")
        audio_path = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(working_video, audio_path):
            raise Exception("Audio extraction failed")
        
        # Transcribe
        update(30, "Transcribing with Groq Whisper...")
        transcript, error = await transcribe_audio(audio_path)
        if not transcript:
            raise Exception(error)
        
        # Smart AI script (with fallback)
        update(40, "AI script generation (smart + emotional)...")
        metadata = await generate_food_hack_script(transcript, duration)
        logger.info(f"   Characters detected: {metadata['num_characters']}")
        logger.info(f"   Title: {metadata['title']}")
        
        # Multi-character voiceover (with fallback)
        update(55, f"Generating {metadata['num_characters']}-character voiceover (1.1x)...")
        voiceover = os.path.join(temp_dir, "voice.mp3")
        success, error = await generate_multi_character_voiceover(metadata["characters"], voiceover)
        if not success:
            raise Exception(error)
        
        # Video enhancements (with fallback - NEVER FAILS)
        update(65, "Enhancing video quality...")
        enhanced_video = os.path.join(temp_dir, "enhanced.mp4")
        success, error = await enhance_video_quality(working_video, enhanced_video)
        # Always continues even if enhancement fails
        
        # Remove original audio
        update(70, "Removing original audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(enhanced_video, silent_video):
            raise Exception("Remove audio failed")
        
        # Apply live captions (with fallback - NEVER FAILS)
        update(75, "Applying live captions...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        success, error = await apply_live_captions(silent_video, metadata["script"], duration, captioned_video)
        # Always continues even if captions fail
        
        # Download kids BGM (optional - failure OK)
        update(80, "Downloading kids BGM...")
        bgm_path = os.path.join(temp_dir, "kids_bgm.mp3")
        bgm_success = await download_kids_bgm(bgm_path)
        if not bgm_success:
            bgm_path = None
            logger.warning("⚠️ BGM download failed, continuing without BGM")
        
        # Mix audio (with fallback)
        update(85, "Mixing voice + BGM...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await mix_audio_with_bgm(captioned_video, voiceover, bgm_path, final_video)
        if not success:
            raise Exception(error)
        
        if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
            raise Exception("Invalid final video")
        
        size_mb = os.path.getsize(final_video) / (1024 * 1024)
        logger.info(f"   Final video: {size_mb:.1f}MB")
        
        # Upload to YouTube
        update(95, "Uploading to YouTube with SEO...")
        full_description = f"{metadata['description']}\n\n{' '.join(metadata['hashtags'])}"
        
        upload_result = await upload_to_youtube(final_video, metadata["title"], full_description, user_id)
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        # SUCCESS
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("✅ FOOD HACK VIDEO SUCCESS!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video ID: {upload_result['video_id']}")
        logger.info(f"   Characters: {metadata['num_characters']}")
        logger.info("="*80)
        log_memory("COMPLETE")
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "message": "Uploaded!",
            "title": metadata["title"],
            "description": full_description,
            "hashtags": metadata["hashtags"],
            "num_characters": metadata["num_characters"],
            "duration": round(duration, 1),
            "processing_time": round(elapsed, 1),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error("="*80)
        logger.error(f"❌ FAILED: {error_msg}")
        logger.error("="*80)
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": error_msg,
            "message": error_msg,
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir and os.path.exists(temp_dir):
            logger.info("🧹 Cleanup...")
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("✅ Clean")
            except:
                pass
        
        gc.collect()
        gc.collect()
        gc.collect()
        log_memory("FINAL")

# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()

@router.post("/api/food-hack-ai/process")
async def process_endpoint(request: Request):
    """Process food hack video (synchronous)"""
    logger.info("🌐 FOOD HACK AI REQUEST")
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        
        if not user_id:
            return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
        if not drive_url or "drive.google.com" not in drive_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Valid Google Drive URL required"})
        
        task_id = str(uuid.uuid4())
        logger.info(f"✅ Task ID: {task_id}")
        
        # RENDER-OPTIMIZED: Increased timeout
        await asyncio.wait_for(process_food_hack_video(drive_url, user_id, task_id), timeout=900)  # 15 minutes
        
        result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout (900s exceeded - video processing took too long)"})
    except Exception as e:
        logger.error(f"❌ API Error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/api/food-hack-ai/status/{task_id}")
async def status_endpoint(task_id: str):
    """Get processing status"""
    status = PROCESSING_STATUS.get(task_id)
    if not status:
        return JSONResponse(status_code=404, content={"success": False, "error": "Task not found"})
    return JSONResponse(content=status)

@router.get("/api/food-hack-ai/health")
async def health_endpoint():
    """Health check"""
    log_memory("health")
    return JSONResponse(content={
        "status": "ok",
        "groq_configured": bool(GROQ_API_KEY),
        "elevenlabs_configured": bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20),
        "mistral_configured": bool(MISTRAL_API_KEY),
        "active_tasks": len([s for s in PROCESSING_STATUS.values() if s["status"] == "processing"]),
        "features": {
            "multi_character_voices": len(ELEVENLABS_VOICE_IDS),
            "voiceover_speed": "1.1x",
            "bgm_volume": "15% (10-20% range)",
            "bgm_type": "Kids ringtone style",
            "caption_libraries": "FFmpeg subtitles + fallback system",
            "video_enhancements": "Saturation +20%, Contrast +10% (Render-optimized)",
            "emotional_ending": "Bye bye mere dosto!",
            "seo_optimization": "35-45 keywords + 7-9 hashtags + 2-3 hashtags in title",
            "render_optimized": True,
            "comprehensive_fallbacks": True
        }
    })

@router.get("/api/food-hack-ai/bgm-list")
async def bgm_list_endpoint():
    """Get list of kids BGM tracks"""
    return JSONResponse(content={
        "success": True,
        "total_tracks": len(KIDS_BGM_URLS),
        "bgm_type": "Kids ringtone style (trending)",
        "tracks": [
            {
                "index": idx + 1,
                "name": url.split('/')[-1].replace('%20', ' ').replace('.mp3', ''),
                "url": url
            }
            for idx, url in enumerate(KIDS_BGM_URLS)
        ]
    })

async def initialize():
    """Startup initialization"""
    logger.info("="*80)
    logger.info("🚀 FOOD HACK AI VIDEO PROCESSOR (RENDER-OPTIMIZED)")
    logger.info("="*80)
    logger.info("✅ Multi-character AI voices (4 ElevenLabs voices + Edge TTS fallback)")
    logger.info("✅ 1.1x voiceover speed for all TTS")
    logger.info("✅ Kids BGM at 15% volume (optional - fallback without BGM)")
    logger.info("✅ Live captions with fallback system (golden/white/none)")
    logger.info("✅ Emotional connection: 'Bye bye mere dosto!'")
    logger.info("✅ Smart AI script: minimal changes to transcript")
    logger.info("✅ Video enhancements (Render-optimized + fallback)")
    logger.info("✅ SEO: 35-45 keywords + 7-9 hashtags + title hashtags")
    logger.info("✅ COMPREHENSIVE FALLBACK SYSTEM - Never fails completely!")
    logger.info("="*80)
    
    if GROQ_API_KEY:
        logger.info("✅ Groq Whisper configured")
    else:
        logger.error("❌ No GROQ_SPEECH_API")
    
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        logger.info(f"✅ ElevenLabs configured ({len(ELEVENLABS_VOICE_IDS)} voices)")
    else:
        logger.warning("⚠️ ElevenLabs not configured (will use Edge TTS)")
    
    if MISTRAL_API_KEY:
        logger.info("✅ Mistral AI configured (smart script + SEO)")
    else:
        logger.warning("⚠️ Mistral AI not configured (basic script)")
    
    log_memory("startup")
    logger.info("="*80)

__all__ = ["router", "initialize"]