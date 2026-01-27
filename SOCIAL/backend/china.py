"""
china_enhanced.py - MULTI-NICHE CHINESE VIDEO AUTOMATION
==================================================
✅ 5 Viral Niches: Funny, Animals, Kids, Stories, Satisfying
✅ Smart keyword search (English + Chinese fallback)
✅ Multiple fallback options for every method
✅ ElevenLabs Hindi voiceover
✅ Auto-upload to YouTube Shorts
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

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & API KEYS
# ============================================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_346aca9fb63af57816b2f0323b6312b75a65aa852656eeac")
ELEVENLABS_VOICE_ID = "nPczCjzI2devNBz1zQrb"
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")

MAX_VIDEO_SIZE_MB = 50
FFMPEG_TIMEOUT = 180
TARGET_DURATION = 30
CHUNK_SIZE = 65536

# ============================================================================
# MULTI-NICHE CONFIGURATION WITH FALLBACKS
# ============================================================================

NICHE_KEYWORDS = {
    "funny": {
        "name": "Funny / Comedy / Memes",
        "icon": "😂",
        "english_keywords": [
            "funny", "comedy", "meme", "prank", "fail", "joke", "hilarious"
        ],
        "chinese_keywords": [
            "搞笑", "幽默", "段子", "娱乐", "爆笑", "喜剧", "笑话"
        ],
        "script_style": "super funny and comedic with Indian humor",
        "emoji": "😂🤣💀"
    },
    "animals": {
        "name": "Cute Animals / Pets",
        "icon": "🐶",
        "english_keywords": [
            "cute animals", "pets", "dogs", "cats", "puppies", "kittens", "funny animals"
        ],
        "chinese_keywords": [
            "萌宠", "宠物", "狗狗", "猫咪", "可爱动物", "小猫", "小狗"
        ],
        "script_style": "cute and heartwarming with emotional appeal",
        "emoji": "🐶🐱❤️"
    },
    "kids": {
        "name": "Kids / Cartoon / Children",
        "icon": "👶",
        "english_keywords": [
            "kids", "children", "cartoon", "baby", "funny kids", "cute baby", "toddler"
        ],
        "chinese_keywords": [
            "儿童", "宝宝", "小孩", "可爱宝宝", "萌娃", "动画", "幼儿"
        ],
        "script_style": "family-friendly and wholesome with positive energy",
        "emoji": "👶😊🌟"
    },
    "stories": {
        "name": "Story / Motivation / Facts",
        "icon": "📖",
        "english_keywords": [
            "story", "motivation", "inspiration", "facts", "amazing story", "life lesson", "wisdom"
        ],
        "chinese_keywords": [
            "故事", "励志", "感人", "真实故事", "人生", "智慧", "道理"
        ],
        "script_style": "engaging and thought-provoking with storytelling flow",
        "emoji": "📖💡✨"
    },
    "satisfying": {
        "name": "Satisfying / ASMR / Oddly Satisfying",
        "icon": "✨",
        "english_keywords": [
            "satisfying", "oddly satisfying", "asmr", "relaxing", "soap cutting", "slime", "perfect"
        ],
        "chinese_keywords": [
            "解压", "治愈", "舒适", "完美", "切割", "史莱姆", "放松"
        ],
        "script_style": "calming and descriptive with sensory details",
        "emoji": "✨😌🎯"
    }
}

# Fallback search keywords if niche-specific search fails
UNIVERSAL_FALLBACK_KEYWORDS = {
    "english": ["trending", "viral", "popular", "best", "top"],
    "chinese": ["热门", "流行", "精选", "推荐", "最火"]
}

# Background music by niche
BACKGROUND_MUSIC_BY_NICHE = {
    "funny": [
        "https://freesound.org/data/previews/456/456966_5121236-lq.mp3",
        "https://freesound.org/data/previews/391/391660_7181322-lq.mp3",
    ],
    "animals": [
        "https://freesound.org/data/previews/398/398513_7181322-lq.mp3",
        "https://freesound.org/data/previews/456/456966_5121236-lq.mp3",
    ],
    "kids": [
        "https://freesound.org/data/previews/412/412210_7181322-lq.mp3",
        "https://freesound.org/data/previews/398/398513_7181322-lq.mp3",
    ],
    "stories": [
        "https://freesound.org/data/previews/521/521488_9961799-lq.mp3",
        "https://freesound.org/data/previews/477/477718_9497060-lq.mp3",
    ],
    "satisfying": [
        "https://freesound.org/data/previews/412/412210_7181322-lq.mp3",
        "https://freesound.org/data/previews/398/398513_7181322-lq.mp3",
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
            pass
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
        logger.info(f"Running FFmpeg with {timeout}s timeout...")
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
# SMART VIDEO SEARCH WITH MULTIPLE FALLBACKS
# ============================================================================

def matches_niche(info: dict, niche: str) -> bool:
    """Check if video matches the niche based on keywords"""
    text = (
        (info.get("title") or "") +
        (info.get("description") or "") +
        " ".join(info.get("tags") or [])
    ).lower()
    
    niche_config = NICHE_KEYWORDS.get(niche, {})
    english_keywords = niche_config.get("english_keywords", [])
    chinese_keywords = niche_config.get("chinese_keywords", [])
    
    # Check if any keyword matches
    all_keywords = english_keywords + chinese_keywords
    return any(keyword in text for keyword in all_keywords)

async def search_chinese_video_smart(niche: str, temp_dir: str) -> Optional[dict]:
    """
    Smart video search with multiple fallback strategies:
    1. Try English keywords
    2. Try Chinese keywords
    3. Try universal fallback keywords
    4. Try trending/popular content
    """
    try:
        import yt_dlp
        
        niche_config = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["funny"])
        
        logger.info(f"🔍 Searching for {niche} videos...")
        logger.info(f"   Niche: {niche_config['name']}")
        
        # Strategy 1: Try English keywords
        logger.info("   Strategy 1: English keywords")
        for keyword in niche_config["english_keywords"]:
            logger.info(f"      Trying: {keyword}")
            
            search_url = f"ytsearch10:{keyword} chinese shorts"
            
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "extract_flat": True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(search_url, download=False)
                    
                    if result and result.get("entries"):
                        # Filter by duration (10-120s) and niche match
                        for entry in result["entries"]:
                            duration = entry.get("duration", 0)
                            
                            if 10 <= duration <= 120:
                                # Get full info
                                try:
                                    full_info = ydl.extract_info(entry["url"], download=False)
                                    
                                    if matches_niche(full_info, niche):
                                        logger.info(f"      ✅ Found matching video: {full_info.get('title', '')[:50]}")
                                        return {
                                            "url": entry["url"],
                                            "title": full_info.get("title", "Unknown"),
                                            "duration": duration,
                                            "uploader": full_info.get("uploader", "Unknown"),
                                            "description": full_info.get("description", "")
                                        }
                                except:
                                    continue
            except Exception as e:
                logger.warning(f"      Failed: {e}")
                continue
        
        # Strategy 2: Try Chinese keywords
        logger.info("   Strategy 2: Chinese keywords")
        for keyword in niche_config["chinese_keywords"][:3]:  # Try first 3
            logger.info(f"      Trying: {keyword}")
            
            search_url = f"ytsearch10:{keyword}"
            
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "extract_flat": True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(search_url, download=False)
                    
                    if result and result.get("entries"):
                        for entry in result["entries"]:
                            duration = entry.get("duration", 0)
                            
                            if 10 <= duration <= 120:
                                try:
                                    full_info = ydl.extract_info(entry["url"], download=False)
                                    
                                    if matches_niche(full_info, niche):
                                        logger.info(f"      ✅ Found matching video")
                                        return {
                                            "url": entry["url"],
                                            "title": full_info.get("title", "Unknown"),
                                            "duration": duration,
                                            "uploader": full_info.get("uploader", "Unknown"),
                                            "description": full_info.get("description", "")
                                        }
                                except:
                                    continue
            except Exception as e:
                logger.warning(f"      Failed: {e}")
                continue
        
        # Strategy 3: Universal fallback
        logger.info("   Strategy 3: Universal fallback keywords")
        for keyword in UNIVERSAL_FALLBACK_KEYWORDS["english"][:2]:
            search_url = f"ytsearch5:{keyword} {niche} chinese"
            
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "extract_flat": True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(search_url, download=False)
                    
                    if result and result.get("entries"):
                        for entry in result["entries"]:
                            duration = entry.get("duration", 0)
                            
                            if 10 <= 120:
                                try:
                                    full_info = ydl.extract_info(entry["url"], download=False)
                                    logger.info(f"      ✅ Using fallback video")
                                    return {
                                        "url": entry["url"],
                                        "title": full_info.get("title", "Unknown"),
                                        "duration": duration,
                                        "uploader": full_info.get("uploader", "Unknown"),
                                        "description": full_info.get("description", "")
                                    }
                                except:
                                    continue
            except Exception as e:
                continue
        
        logger.error("❌ No suitable video found after all fallback attempts")
        return None
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        logger.error(traceback.format_exc())
        return None

async def download_chinese_video(video_info: dict, temp_dir: str) -> Optional[str]:
    """Download video from URL"""
    try:
        import yt_dlp
        
        logger.info(f"📥 Downloading video...")
        logger.info(f"   Title: {video_info['title'][:50]}...")
        logger.info(f"   Duration: {video_info['duration']}s")
        
        video_path = os.path.join(temp_dir, "source_video.mp4")
        
        ydl_opts = {
            "format": "best[height<=720]",
            "outtmpl": video_path,
            "quiet": True,
            "no_warnings": True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_info["url"]])
        
        if not os.path.exists(video_path):
            logger.error("❌ Download failed")
            return None
        
        size = get_size_mb(video_path)
        logger.info(f"✅ Downloaded: {size:.1f}MB")
        
        return video_path
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None

# ============================================================================
# AUDIO EXTRACTION & TRANSCRIPTION WITH FALLBACKS
# ============================================================================

async def extract_audio(video_path: str, temp_dir: str) -> Optional[str]:
    """Extract audio from video"""
    try:
        audio_path = os.path.join(temp_dir, "original_audio.mp3")
        
        logger.info("🎵 Extracting audio...")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-b:a", "128k",
            "-y", audio_path
        ]
        
        if run_ffmpeg(cmd, 30):
            logger.info(f"✅ Audio extracted: {get_size_mb(audio_path):.2f}MB")
            return audio_path
        
        return None
        
    except Exception as e:
        logger.error(f"Audio extraction error: {e}")
        return None

async def transcribe_audio_with_fallback(audio_path: str) -> Optional[str]:
    """
    Transcribe audio with multiple fallback options:
    1. OpenAI Whisper API
    2. Local Whisper
    3. Placeholder text
    """
    try:
        logger.info("🎤 Transcribing audio...")
        
        # Method 1: OpenAI Whisper API
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key:
            logger.info("   Method 1: OpenAI Whisper API")
            
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    with open(audio_path, 'rb') as audio_file:
                        files = {
                            'file': ('audio.mp3', audio_file, 'audio/mpeg')
                        }
                        data = {
                            'model': 'whisper-1',
                            'language': 'zh',
                            'response_format': 'text'
                        }
                        
                        response = await client.post(
                            "https://api.openai.com/v1/audio/transcriptions",
                            headers={"Authorization": f"Bearer {openai_key}"},
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            transcript = response.text.strip()
                            logger.info(f"   ✅ Transcribed: {len(transcript)} chars")
                            return transcript
            except Exception as e:
                logger.warning(f"   Whisper API failed: {e}")
        
        # Method 2: Local Whisper
        logger.info("   Method 2: Local Whisper")
        try:
            import whisper
            
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language="zh")
            transcript = result["text"].strip()
            
            logger.info(f"   ✅ Local transcription: {len(transcript)} chars")
            return transcript
            
        except ImportError:
            logger.warning("   Whisper not installed")
        except Exception as e:
            logger.warning(f"   Local Whisper failed: {e}")
        
        # Method 3: Placeholder
        logger.warning("   Using placeholder text")
        return "这是一个精彩的视频内容"
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "这是一个有趣的视频"

# ============================================================================
# TRANSLATION WITH FALLBACKS
# ============================================================================

async def translate_to_hindi_with_fallback(chinese_text: str) -> str:
    """
    Translate Chinese to Hindi with fallbacks:
    1. DeepL API
    2. Mistral AI
    3. Simple placeholder
    """
    try:
        logger.info("🌏 Translating to Hindi...")
        
        # Method 1: DeepL
        if DEEPL_API_KEY:
            logger.info("   Method 1: DeepL API")
            
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api-free.deepl.com/v2/translate",
                        data={
                            "auth_key": DEEPL_API_KEY,
                            "text": chinese_text,
                            "source_lang": "ZH",
                            "target_lang": "HI"
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        hindi_text = result["translations"][0]["text"]
                        logger.info(f"   ✅ DeepL: {hindi_text[:50]}...")
                        return hindi_text
            except Exception as e:
                logger.warning(f"   DeepL failed: {e}")
        
        # Method 2: Mistral AI
        if MISTRAL_API_KEY:
            logger.info("   Method 2: Mistral AI")
            
            try:
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
                                {
                                    "role": "user",
                                    "content": f"Translate this Chinese text to Hindi naturally:\n\n{chinese_text}\n\nProvide ONLY the Hindi translation."
                                }
                            ],
                            "temperature": 0.3,
                            "max_tokens": 500
                        }
                    )
                    
                    if response.status_code == 200:
                        hindi_text = response.json()["choices"][0]["message"]["content"].strip()
                        logger.info(f"   ✅ Mistral: {hindi_text[:50]}...")
                        return hindi_text
            except Exception as e:
                logger.warning(f"   Mistral failed: {e}")
        
        # Method 3: Return original (will be handled by creative script)
        logger.warning("   Using original text (will be enhanced by creative script)")
        return chinese_text
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return chinese_text

# ============================================================================
# CREATIVE SCRIPT GENERATION
# ============================================================================

async def generate_creative_script(hindi_translation: str, niche: str, original_title: str) -> dict:
    """Generate creative viral script based on niche"""
    
    niche_config = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["funny"])
    
    prompt = f"""You are a viral content creator for YouTube Shorts in India.

NICHE: {niche_config['name']}
STYLE: {niche_config['script_style']}
EMOJI STYLE: {niche_config['emoji']}

ORIGINAL CONTENT:
Title: {original_title}
Content: {hindi_translation}

CREATE A VIRAL HINDI SCRIPT FOR YOUTUBE SHORTS (30 seconds)

REQUIREMENTS:
- Match the {niche} niche perfectly
- Make it 10x more engaging than original
- Use {niche_config['script_style']}
- Total duration: 30 seconds
- 4 segments with timing

STRUCTURE:
1. HOOK (8s): Grab attention immediately - use {niche_config['emoji']}
2. BUILD (12s): Develop the content with engagement
3. CLIMAX (7s): Peak moment - emotional/funny/surprising
4. OUTRO (3s): Strong call to action

OUTPUT ONLY THIS JSON:
{{
  "segments": [
    {{"narration": "Hindi hook text", "text_overlay": "{niche_config['emoji'].split()[0]}", "duration": 8}},
    {{"narration": "Hindi build text", "text_overlay": "{niche_config['emoji'].split()[1] if len(niche_config['emoji'].split()) > 1 else niche_config['emoji'].split()[0]}", "duration": 12}},
    {{"narration": "Hindi climax text", "text_overlay": "{niche_config['emoji'].split()[2] if len(niche_config['emoji'].split()) > 2 else niche_config['emoji'].split()[0]}", "duration": 7}},
    {{"narration": "Hindi outro text", "text_overlay": "🔥", "duration": 3}}
  ],
  "title": "Viral Hindi/English mix title for {niche}",
  "hashtags": ["{niche}", "viral", "shorts", "hindi", "trending"]
}}

Make it SUPER VIRAL!"""

    try:
        if not MISTRAL_API_KEY:
            return generate_fallback_script(hindi_translation, niche)
        
        logger.info(f"🤖 Generating {niche} script with Mistral...")
        
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
                        {"role": "system", "content": "You are a viral content creator. Output ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.95,
                    "max_tokens": 1500
                }
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                script = json.loads(content)
                logger.info(f"✅ Script generated: {script.get('title', '')[:50]}")
                return script
                
    except Exception as e:
        logger.warning(f"Mistral failed: {e}")
    
    return generate_fallback_script(hindi_translation, niche)

def generate_fallback_script(hindi_text: str, niche: str) -> dict:
    """Fallback script templates by niche"""
    
    niche_config = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["funny"])
    
    templates = {
        "funny": {
            "segments": [
                {"narration": f"Dekho yaar, yeh video dekh ke main pagal ho gaya! {hindi_text[:40]}...", "text_overlay": "😂", "duration": 8},
                {"narration": "Aur phir jo hua, yeh dekhte hi meri hasi nahi ruk rahi! Matlab kamal ka content hai!", "text_overlay": "🤣", "duration": 12},
                {"narration": "Lekin sabse mast twist abhi baaki hai! Yeh ending toh literally epic hai!", "text_overlay": "💀", "duration": 7},
                {"narration": "Toh dosto, kaisa laga? Comment mein batao!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "यह वीडियो देखकर हंसी नहीं रुकेगी! 😂 #Shorts",
            "hashtags": ["funny", "comedy", "viral", "hindi"]
        },
        "animals": {
            "segments": [
                {"narration": f"Dekho kitna pyara hai yeh! {hindi_text[:40]}...", "text_overlay": "🐶", "duration": 8},
                {"narration": "Yeh moment itna cute hai ki dil khush ho gaya! Animals ka pyaar dekho!", "text_overlay": "🐱", "duration": 12},
                {"narration": "Aur yeh sabse heartwarming part hai! Pure feel good vibes!", "text_overlay": "❤️", "duration": 7},
                {"narration": "Aapko kaisa laga? Like aur share karo!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "इतना प्यारा जानवर देखा है? 🐶❤️ #Shorts",
            "hashtags": ["animals", "cute", "pets", "viral"]
        },
        "kids": {
            "segments": [
                {"narration": f"Bachon ki yeh harkat dekho! {hindi_text[:40]}...", "text_overlay": "👶", "duration": 8},
                {"narration": "Kitna masoom aur pyara moment hai! Kids bahut sweet hain!", "text_overlay": "😊", "duration": 12},
                {"narration": "Yeh innocence aur cuteness perfect hai! Family ke saath dekho!", "text_overlay": "🌟", "duration": 7},
                {"narration": "Apne bacchon ko dikhao! Share karo!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "बच्चों की मस्ती देखो! 👶😊 #Shorts",
            "hashtags": ["kids", "children", "family", "wholesome"]
        },
        "stories": {
            "segments": [
                {"narration": f"Suno yeh amazing story! {hindi_text[:40]}...", "text_overlay": "📖", "duration": 8},
                {"narration": "Yeh kahani bahut inspiring hai! Life ke lessons milte hain!", "text_overlay": "💡", "duration": 12},
                {"narration": "Aur yeh twist toh mind-blowing hai! Yeh message powerful hai!", "text_overlay": "✨", "duration": 7},
                {"narration": "Aapke kya thoughts hain? Comment karo!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "यह कहानी सुनकर जीवन बदल जाएगा! 📖✨ #Shorts",
            "hashtags": ["story", "motivation", "inspiration", "facts"]
        },
        "satisfying": {
            "segments": [
                {"narration": f"Dekho kitna satisfying hai! {hindi_text[:40]}...", "text_overlay": "✨", "duration": 8},
                {"narration": "Yeh perfect hai! Dekh ke bahut relaxing feel aata hai!", "text_overlay": "😌", "duration": 12},
                {"narration": "Aur yeh ending toh oddly satisfying hai! Pure perfection!", "text_overlay": "🎯", "duration": 7},
                {"narration": "Loop pe dekho! Save aur share karo!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "इतना Satisfying Video कभी नहीं देखा! ✨😌 #Shorts",
            "hashtags": ["satisfying", "asmr", "relaxing", "oddlysatisfying"]
        }
    }
    
    return templates.get(niche, templates["funny"])

# ============================================================================
# BACKGROUND MUSIC WITH FALLBACKS
# ============================================================================

async def download_background_music(niche: str, temp_dir: str) -> Optional[str]:
    """Download background music for specific niche"""
    
    music_urls = BACKGROUND_MUSIC_BY_NICHE.get(niche, BACKGROUND_MUSIC_BY_NICHE["funny"])
    music_path = os.path.join(temp_dir, "bg_music.mp3")
    
    logger.info(f"🎵 Downloading {niche} background music...")
    
    for attempt, url in enumerate(music_urls, 1):
        try:
            logger.info(f"   Attempt {attempt}/{len(music_urls)}...")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, follow_redirects=True)
                
                if resp.status_code == 200:
                    with open(music_path, 'wb') as f:
                        f.write(resp.content)
                    
                    size = get_size_mb(music_path)
                    
                    if size > 0.05:
                        logger.info(f"   ✅ Music downloaded: {size:.2f}MB")
                        return music_path
                    
                    force_cleanup(music_path)
            
        except Exception as e:
            logger.warning(f"   Failed: {str(e)[:100]}")
            continue
    
    logger.warning("⚠️ No background music (continuing without)")
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
                
                size = get_size_mb(temp_audio)
                
                if size > 0.01:
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
# VIDEO PROCESSING (from Viral_pixel.py pattern)
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
    """Process video for Shorts: 720x1280, loop/trim to duration"""
    try:
        output = os.path.join(temp_dir, "processed.mp4")
        
        logger.info(f"⚙️ Processing for Shorts: {target_duration}s, 720x1280")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-t", str(target_duration),
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "fast",
            "-movflags", "+faststart",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 90):
            logger.info(f"✅ Processed: {get_size_mb(output):.1f}MB")
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
# MAIN PIPELINE
# ============================================================================

async def process_chinese_video_by_niche(
    niche: str,
    user_id: str,
    show_captions: bool,
    database_manager
) -> dict:
    """Main processing pipeline for Chinese videos by niche"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"china_{niche}_")
        logger.info(f"🚀 Starting {niche} video processing...")
        
        # STEP 1: Search and Download
        logger.info("📥 STEP 1: Searching for video...")
        video_info = await search_chinese_video_smart(niche, temp_dir)
        
        if not video_info:
            return {"success": False, "error": f"No {niche} video found"}
        
        video_path = await download_chinese_video(video_info, temp_dir)
        
        if not video_path:
            return {"success": False, "error": "Video download failed"}
        
        # STEP 2: Extract Audio
        logger.info("🎵 STEP 2: Extracting audio...")
        audio_path = await extract_audio(video_path, temp_dir)
        
        if not audio_path:
            return {"success": False, "error": "Audio extraction failed"}
        
        # STEP 3: Transcribe
        logger.info("🎤 STEP 3: Transcribing...")
        transcript = await transcribe_audio_with_fallback(audio_path)
        
        # STEP 4: Translate
        logger.info("🌏 STEP 4: Translating...")
        hindi_text = await translate_to_hindi_with_fallback(transcript)
        
        # STEP 5: Generate Script
        logger.info("🤖 STEP 5: Generating creative script...")
        script = await generate_creative_script(hindi_text, niche, video_info["title"])
        
        # STEP 6: Background Music
        logger.info("🎵 STEP 6: Downloading music...")
        music = await download_background_music(niche, temp_dir)
        
        # STEP 7: Remove Audio
        logger.info("🔇 STEP 7: Removing original audio...")
        video_no_audio = await remove_original_audio(video_path, temp_dir)
        
        if not video_no_audio:
            return {"success": False, "error": "Audio removal failed"}
        
        force_cleanup(video_path, audio_path)
        
        # STEP 8: Process Video
        logger.info("⚙️ STEP 8: Processing video...")
        processed_video = await process_video_for_shorts(video_no_audio, 30, temp_dir)
        
        if not processed_video:
            return {"success": False, "error": "Video processing failed"}
        
        force_cleanup(video_no_audio)
        
        # STEP 9: Text Overlays
        if show_captions:
            logger.info("📝 STEP 9: Adding text overlays...")
            processed_video = await add_text_overlays(processed_video, script["segments"], temp_dir)
        
        # STEP 10: Generate Voices
        logger.info("🎤 STEP 10: Generating voiceovers...")
        voices = []
        
        for idx, seg in enumerate(script["segments"]):
            logger.info(f"   Voice {idx+1}/{len(script['segments'])}...")
            voice = await generate_hindi_voice(seg["narration"], seg["duration"], temp_dir)
            if voice:
                voices.append(voice)
        
        if len(voices) < 3:
            return {"success": False, "error": f"Voice generation failed ({len(voices)}/4)"}
        
        # STEP 11: Mix Audio
        logger.info("🎬 STEP 11: Mixing audio...")
        final_video = await mix_audio_with_music(processed_video, voices, music, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Audio mixing failed"}
        
        # STEP 12: Upload
        logger.info("📤 STEP 12: Uploading...")
        
        upload_result = await upload_to_youtube(
            final_video,
            script["title"],
            f"Chinese {niche} video recreated with Hindi voiceover!",
            script["hashtags"],
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
            "title": script["title"],
            "niche": niche,
            "original_title": video_info["title"],
            "voice_segments": len(voices)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/china/niches")
async def get_niches():
    """Get available niches"""
    return {
        "success": True,
        "niches": {
            key: {
                "name": config["name"],
                "icon": config["icon"],
                "english_keywords": config["english_keywords"][:3],
                "chinese_keywords": config["chinese_keywords"][:3]
            }
            for key, config in NICHE_KEYWORDS.items()
        }
    }

@router.post("/api/china/generate")
async def generate_endpoint(request: Request):
    """Generate Chinese video by niche"""
    try:
        data = await request.json()
        
        niche = data.get("niche", "funny")
        user_id = data.get("user_id")
        
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
        
        from Supermain import database_manager
        
        logger.info(f"📨 Request: {user_id} / {niche}")
        
        try:
            result = await asyncio.wait_for(
                process_chinese_video_by_niche(
                    niche=niche,
                    user_id=user_id,
                    show_captions=data.get("show_captions", True),
                    database_manager=database_manager
                ),
                timeout=900
            )
            
            return JSONResponse(content=result)
            
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Timeout (15 min)"}
            )
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.get("/api/china/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "success": True,
        "message": "China Multi-Niche API Running",
        "niches": list(NICHE_KEYWORDS.keys())
    }

__all__ = ['router']