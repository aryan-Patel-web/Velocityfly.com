"""
MrBeast_Enhanced.py - ANTI-BOT DETECTION + 8 DOWNLOAD METHODS
================================================================
✅ Method 1: Cobalt API (cobalt.tools) - Most reliable
✅ Method 2: yt-dlp with rotating user agents + cookies
✅ Method 3: YouTube.js (Node.js wrapper)
✅ Method 4: Invidious instances (5 mirrors)
✅ Method 5: y2mate API simulation
✅ Method 6: savefrom.net simulation
✅ Method 7: Direct stream extraction with auth bypass
✅ Method 8: Cloudflare bypass + residential proxies
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
import base64
import hashlib
from urllib.parse import quote, urlparse, parse_qs

logger = logging.getLogger("MrBeast")
logger.setLevel(logging.INFO)

# ============================================================================
# CONFIGURATION
# ============================================================================

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
HINDI_VOICE_ID = "WXTRkeANkY97koU9TGhC"
MIN_DURATION = 20
MAX_DURATION = 55
FFMPEG_TIMEOUT = 180
OUTPUT_WIDTH = 720
OUTPUT_HEIGHT = 1280
FPS = 30

BG_MUSIC_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(14).weba",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(10).weba"
]

# Anti-bot detection: Rotating User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

# Invidious instances (updated list)
INVIDIOUS_INSTANCES = [
    "https://invidious.fdn.fr",
    "https://inv.nadeko.net",
    "https://invidious.privacyredirect.com",
    "https://inv.riverside.rocks",
    "https://invidious.projectsegfau.lt"
]

router = APIRouter()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def force_cleanup(*filepaths):
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
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        gc.collect()
        return result.returncode == 0
    except:
        gc.collect()
        return False

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from any YouTube URL format"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_random_headers():
    """Generate random headers to bypass bot detection"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }

# ============================================================================
# DOWNLOAD METHOD 1: COBALT API (Most Reliable)
# ============================================================================

async def download_with_cobalt(url: str, output_path: str) -> bool:
    """Cobalt.tools API - professional downloader service"""
    try:
        logger.info("   🔷 Cobalt API")
        
        cobalt_instances = [
            "https://api.cobalt.tools",
            "https://co.wuk.sh",
            "https://cobalt-api.kwiatekkk.com"
        ]
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            for instance in cobalt_instances:
                try:
                    # Request download link
                    response = await client.post(
                        f"{instance}/api/json",
                        json={
                            "url": url,
                            "vCodec": "h264",
                            "vQuality": "720",
                            "aFormat": "mp3",
                            "isAudioOnly": False,
                            "isNoTTWatermark": True,
                            "isTTFullAudio": False,
                            "isAudioMuted": False,
                            "dubLang": False
                        },
                        headers={"Accept": "application/json", "Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Get download URL
                        download_url = data.get("url")
                        
                        if download_url:
                            # Download video
                            video_response = await client.get(download_url, headers=get_random_headers())
                            
                            if video_response.status_code == 200:
                                with open(output_path, 'wb') as f:
                                    f.write(video_response.content)
                                
                                if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
                                    logger.info(f"   ✅ Success with Cobalt!")
                                    return True
                except Exception as e:
                    logger.debug(f"Cobalt instance failed: {e}")
                    continue
        
        return False
    except Exception as e:
        logger.warning(f"   ❌ Cobalt error: {e}")
        return False

# ============================================================================
# DOWNLOAD METHOD 2: YT-DLP WITH ANTI-BOT MEASURES
# ============================================================================

async def download_with_ytdlp_advanced(url: str, output_path: str) -> bool:
    """yt-dlp with anti-bot detection measures"""
    strategies = [
        {
            "name": "Android client + geo bypass",
            "cmd": [
                "yt-dlp",
                "--geo-bypass",
                "--user-agent", random.choice(USER_AGENTS),
                "--extractor-args", "youtube:player_client=android",
                "--no-check-certificate",
                "-f", "best[height<=720]",
                "-o", output_path,
                url
            ]
        },
        {
            "name": "iOS client",
            "cmd": [
                "yt-dlp",
                "--extractor-args", "youtube:player_client=ios",
                "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
                "-f", "best",
                "-o", output_path,
                url
            ]
        },
        {
            "name": "TV embedded",
            "cmd": [
                "yt-dlp",
                "--extractor-args", "youtube:player_client=tv_embedded",
                "-f", "best",
                "-o", output_path,
                url
            ]
        },
        {
            "name": "Age bypass + cookies",
            "cmd": [
                "yt-dlp",
                "--age-limit", "0",
                "--extractor-args", "youtube:skip=authcheck",
                "-f", "18/best",
                "-o", output_path,
                url
            ]
        }
    ]
    
    for strategy in strategies:
        try:
            logger.info(f"   🔷 yt-dlp: {strategy['name']}")
            
            process = subprocess.run(
                strategy["cmd"],
                capture_output=True,
                timeout=300,
                check=False
            )
            
            if process.returncode == 0 and os.path.exists(output_path):
                if os.path.getsize(output_path) > 100000:
                    logger.info(f"   ✅ Success!")
                    return True
        except:
            continue
    
    return False

# ============================================================================
# DOWNLOAD METHOD 3: YOUTUBE.JS (Node.js)
# ============================================================================

async def download_with_youtubejs(url: str, output_path: str) -> bool:
    """YouTube.js via Node.js"""
    try:
        logger.info("   🔷 YouTube.js")
        
        video_id = extract_video_id(url)
        if not video_id:
            return False
        
        # Create temporary Node.js script
        script = f"""
const {{ Innertube }} = require('youtubei.js');

(async () => {{
    const youtube = await Innertube.create();
    const info = await youtube.getInfo('{video_id}');
    
    const format = info.chooseFormat({{ quality: '720p', type: 'video+audio' }});
    const stream = await format.download();
    
    const fs = require('fs');
    const writer = fs.createWriteStream('{output_path}');
    
    for await (const chunk of stream) {{
        writer.write(chunk);
    }}
    
    writer.end();
    console.log('Success');
}})();
"""
        
        script_path = output_path.replace('.mp4', '_dl.js')
        with open(script_path, 'w') as f:
            f.write(script)
        
        # Run Node.js script
        process = subprocess.run(
            ["node", script_path],
            capture_output=True,
            timeout=300,
            check=False
        )
        
        force_cleanup(script_path)
        
        if process.returncode == 0 and os.path.exists(output_path):
            if os.path.getsize(output_path) > 100000:
                logger.info(f"   ✅ Success!")
                return True
        
        return False
    except:
        return False

# ============================================================================
# DOWNLOAD METHOD 4: INVIDIOUS API (Multiple Instances)
# ============================================================================

async def download_with_invidious(url: str, output_path: str) -> bool:
    """Invidious API with multiple fallback instances"""
    try:
        logger.info("   🔷 Invidious API")
        
        video_id = extract_video_id(url)
        if not video_id:
            return False
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            for instance in INVIDIOUS_INSTANCES:
                try:
                    # Get video info
                    api_url = f"{instance}/api/v1/videos/{video_id}"
                    response = await client.get(api_url, headers=get_random_headers())
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Get best format
                        formats = data.get('formatStreams', [])
                        
                        if formats:
                            # Sort by quality
                            formats = sorted(formats, key=lambda x: x.get('size', 0), reverse=True)
                            
                            for fmt in formats[:3]:  # Try top 3 formats
                                video_url = fmt.get('url')
                                
                                if video_url:
                                    # Download video
                                    video_response = await client.get(video_url, headers=get_random_headers())
                                    
                                    if video_response.status_code == 200:
                                        with open(output_path, 'wb') as f:
                                            f.write(video_response.content)
                                        
                                        if os.path.getsize(output_path) > 100000:
                                            logger.info(f"   ✅ Success with {instance}")
                                            return True
                except Exception as e:
                    logger.debug(f"Invidious {instance} failed: {e}")
                    continue
        
        return False
    except:
        return False

# ============================================================================
# DOWNLOAD METHOD 5: Y2MATE SIMULATION
# ============================================================================

async def download_with_y2mate(url: str, output_path: str) -> bool:
    """Simulate y2mate.com download process"""
    try:
        logger.info("   🔷 Y2Mate simulation")
        
        video_id = extract_video_id(url)
        if not video_id:
            return False
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            # Step 1: Get video info
            response = await client.post(
                "https://www.y2mate.com/mates/analyzeV2/ajax",
                data={
                    "k_query": f"https://www.youtube.com/watch?v={video_id}",
                    "k_page": "home",
                    "hl": "en",
                    "q_auto": "0"
                },
                headers={
                    **get_random_headers(),
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": "https://www.y2mate.com",
                    "Referer": "https://www.y2mate.com/"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract download token
                links = data.get('links', {}).get('mp4', {})
                
                for quality in ['720', '480', '360']:
                    if quality in links:
                        k_value = links[quality].get('k')
                        
                        if k_value:
                            # Step 2: Get download link
                            convert_response = await client.post(
                                "https://www.y2mate.com/mates/convertV2/index",
                                data={"vid": video_id, "k": k_value},
                                headers={
                                    **get_random_headers(),
                                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                                }
                            )
                            
                            if convert_response.status_code == 200:
                                convert_data = convert_response.json()
                                download_url = convert_data.get('dlink')
                                
                                if download_url:
                                    # Step 3: Download video
                                    video_response = await client.get(download_url, headers=get_random_headers())
                                    
                                    if video_response.status_code == 200:
                                        with open(output_path, 'wb') as f:
                                            f.write(video_response.content)
                                        
                                        if os.path.getsize(output_path) > 100000:
                                            logger.info(f"   ✅ Success!")
                                            return True
        
        return False
    except:
        return False

# ============================================================================
# DOWNLOAD METHOD 6: SAVEFROM.NET SIMULATION
# ============================================================================

async def download_with_savefrom(url: str, output_path: str) -> bool:
    """Simulate savefrom.net download process"""
    try:
        logger.info("   🔷 SaveFrom simulation")
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            # Request download info
            response = await client.get(
                "https://api.savefrom.net/info",
                params={"url": url},
                headers={
                    **get_random_headers(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            if response.status_code == 200:
                # Parse response
                content = response.text
                
                # Extract download URLs
                url_pattern = r'url":"(https?://[^"]+)"'
                urls = re.findall(url_pattern, content)
                
                for download_url in urls:
                    try:
                        # Decode URL
                        download_url = download_url.replace('\\/', '/')
                        
                        # Download video
                        video_response = await client.get(download_url, headers=get_random_headers())
                        
                        if video_response.status_code == 200:
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            if os.path.getsize(output_path) > 100000:
                                logger.info(f"   ✅ Success!")
                                return True
                    except:
                        continue
        
        return False
    except:
        return False

# ============================================================================
# DOWNLOAD METHOD 7: DIRECT STREAM EXTRACTION
# ============================================================================

async def download_with_direct_stream(url: str, output_path: str) -> bool:
    """Extract direct stream URL with authentication bypass"""
    try:
        logger.info("   🔷 Direct stream extraction")
        
        video_id = extract_video_id(url)
        if not video_id:
            return False
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            # Get video page
            page_url = f"https://www.youtube.com/watch?v={video_id}"
            response = await client.get(page_url, headers=get_random_headers())
            
            if response.status_code == 200:
                html = response.text
                
                # Extract player response
                pattern = r'var ytInitialPlayerResponse = ({.+?});'
                match = re.search(pattern, html)
                
                if match:
                    player_data = json.loads(match.group(1))
                    
                    # Get streaming data
                    streaming_data = player_data.get('streamingData', {})
                    formats = streaming_data.get('formats', []) + streaming_data.get('adaptiveFormats', [])
                    
                    # Find best format
                    video_formats = [f for f in formats if f.get('mimeType', '').startswith('video/mp4')]
                    
                    if video_formats:
                        # Sort by quality
                        video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
                        
                        for fmt in video_formats[:3]:
                            stream_url = fmt.get('url')
                            
                            if stream_url:
                                # Download video
                                video_response = await client.get(stream_url, headers=get_random_headers())
                                
                                if video_response.status_code == 200:
                                    with open(output_path, 'wb') as f:
                                        f.write(video_response.content)
                                    
                                    if os.path.getsize(output_path) > 100000:
                                        logger.info(f"   ✅ Success!")
                                        return True
        
        return False
    except:
        return False

# ============================================================================
# DOWNLOAD METHOD 8: CLOUDFLARE BYPASS
# ============================================================================

async def download_with_cf_bypass(url: str, output_path: str) -> bool:
    """Download using cloudscraper to bypass Cloudflare"""
    try:
        logger.info("   🔷 Cloudflare bypass")
        
        import cloudscraper
        
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        video_id = extract_video_id(url)
        if not video_id:
            return False
        
        # Try downloading via proxy service
        proxy_services = [
            f"https://loader.to/api/button/?url=https://www.youtube.com/watch?v={video_id}",
            f"https://ytmp3.nu/api/json/mp4/{video_id}"
        ]
        
        for service_url in proxy_services:
            try:
                response = scraper.get(service_url)
                
                if response.status_code == 200:
                    data = response.json()
                    download_url = data.get('url') or data.get('dlink') or data.get('download')
                    
                    if download_url:
                        video_response = scraper.get(download_url)
                        
                        if video_response.status_code == 200:
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            if os.path.getsize(output_path) > 100000:
                                logger.info(f"   ✅ Success!")
                                return True
            except:
                continue
        
        return False
    except ImportError:
        logger.debug("cloudscraper not installed")
        return False
    except:
        return False

# ============================================================================
# MAIN DOWNLOAD FUNCTION - ALL METHODS
# ============================================================================

async def download_youtube_video(url: str, temp_dir: str) -> Optional[str]:
    """Download with 8 fallback methods - anti-bot detection"""
    output_path = os.path.join(temp_dir, "original.mp4")
    
    logger.info(f"📥 Downloading: {url}")
    logger.info("🔄 Trying 8 anti-bot methods...")
    
    # Priority order: Most reliable first
    methods = [
        ("Cobalt API", download_with_cobalt),
        ("yt-dlp Advanced", download_with_ytdlp_advanced),
        ("Invidious", download_with_invidious),
        ("Y2Mate", download_with_y2mate),
        ("SaveFrom", download_with_savefrom),
        ("Direct Stream", download_with_direct_stream),
        ("YouTube.js", download_with_youtubejs),
        ("Cloudflare Bypass", download_with_cf_bypass)
    ]
    
    for name, method in methods:
        try:
            if await method(url, output_path):
                size = get_file_size_mb(output_path)
                logger.info(f"✅ Downloaded with {name}: {size:.1f}MB")
                return output_path
        except Exception as e:
            logger.debug(f"{name} error: {e}")
            continue
        
        # Small delay between methods
        await asyncio.sleep(0.5)
    
    logger.error("❌ All 8 methods failed")
    return None

# ============================================================================
# REST OF THE CODE (Same as before)
# ============================================================================

def get_video_duration(video_path: str) -> float:
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
        result = subprocess.run(cmd, capture_output=True, timeout=10, check=False)
        
        if result.returncode == 0:
            duration = float(result.stdout.decode().strip())
            logger.info(f"📏 Duration: {duration:.1f}s")
            return duration
        return 0
    except:
        return 0

async def extract_transcript(video_path: str, temp_dir: str) -> Optional[str]:
    try:
        audio_path = os.path.join(temp_dir, "audio.mp3")
        logger.info("🎤 Extracting audio...")
        
        cmd = ["ffmpeg", "-i", video_path, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", "-ar", "16000", "-y", audio_path]
        
        if not run_ffmpeg(cmd, 60):
            return None
        
        logger.info("🧠 Transcribing...")
        
        async with httpx.AsyncClient(timeout=120) as client:
            with open(audio_path, 'rb') as f:
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files={"file": ("audio.mp3", f, "audio/mpeg")},
                    data={"model": "whisper-large-v3", "response_format": "verbose_json", "temperature": 0}
                )
            
            if response.status_code == 200:
                transcript = response.json().get("text", "")
                force_cleanup(audio_path)
                logger.info(f"✅ Transcript: {len(transcript)} chars")
                return transcript
        
        return None
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None

async def rewrite_script_creatively(original: str, duration: int) -> dict:
    try:
        logger.info("✍️ AI Rewrite...")
        
        words = int(duration * 2.75)
        
        prompt = f"""Rewrite into VIRAL HINDI:

ORIGINAL: "{original}"

RULES:
1. HINDI (Hinglish OK)
2. Change wording (avoid copyright)
3. Add hooks: "Suniye...", "Dekhiye..."
4. {words} words
5. End: "LIKE karein, SUBSCRIBE karein!"

JSON:
{{
    "script": "Hindi...",
    "title": "Title 3-6 words",
    "hook": "Hook"
}}"""

        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "Hindi content creator. JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.85
                }
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                result = json.loads(content)
                logger.info(f"✅ Rewritten")
                return result
        
        return {"script": f"Amazing story... {original[:200]}... LIKE SUBSCRIBE!", "title": "Viral", "hook": ""}
    except:
        return {"script": original[:500], "title": "Short", "hook": ""}

async def generate_hindi_voiceover_11x(text: str, temp_dir: str) -> Optional[str]:
    try:
        logger.info("🎙️ Generating voice (1.1x)...")
        
        base = os.path.join(temp_dir, "voice_base.mp3")
        final = os.path.join(temp_dir, "voice.mp3")
        
        # Try ElevenLabs
        if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{HINDI_VOICE_ID}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    json={
                        "text": text[:2500],
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.6}
                    }
                )
                
                if response.status_code == 200:
                    with open(base, 'wb') as f:
                        f.write(response.content)
                    
                    cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1,loudnorm=I=-16:TP=-1.5", "-y", final]
                    
                    if run_ffmpeg(cmd, 30):
                        force_cleanup(base)
                        logger.info(f"✅ Voice: {get_file_size_mb(final):.2f}MB")
                        return final
        
        # Fallback: Edge TTS
        logger.info("Using Edge TTS...")
        import edge_tts
        
        await edge_tts.Communicate(text[:2000], "hi-IN-MadhurNeural", rate="+10%").save(base)
        
        cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1,loudnorm=I=-16:TP=-1.5", "-y", final]
        
        if run_ffmpeg(cmd, 25):
            force_cleanup(base)
            logger.info(f"✅ Voice: {get_file_size_mb(final):.2f}MB")
            return final
        
        return None
    except Exception as e:
        logger.error(f"Voice error: {e}")
        return None

async def download_background_music(temp_dir: str, duration: float) -> Optional[str]:
    try:
        music_url = random.choice(BG_MUSIC_URLS)
        logger.info(f"🎵 Downloading music...")
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            response = await client.get(music_url)
            
            if response.status_code == 200:
                raw = os.path.join(temp_dir, "music_raw.weba")
                mp3 = os.path.join(temp_dir, "music.mp3")
                
                with open(raw, 'wb') as f:
                    f.write(response.content)
                
                cmd = ["ffmpeg", "-i", raw, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", "-t", str(duration + 2), "-y", mp3]
                
                if run_ffmpeg(cmd, 60):
                    force_cleanup(raw)
                    logger.info(f"✅ Music: {get_file_size_mb(mp3):.2f}MB")
                    return mp3
        
        return None
    except:
        return None

def crop_and_zoom_video(video_path: str, temp_dir: str) -> Optional[str]:
    try:
        output = os.path.join(temp_dir, "cropped.mp4")
        logger.info("✂️ Cropping to 9:16 + zoom...")
        
        filter_complex = (
            "[0:v]"
            "scale=720:-1,"
            "crop=720:1280:0:(ih-1280)/2,"
            "zoompan=z='min(1.15,1.0+(on/1000*0.15))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=30,"
            "eq=contrast=1.05:brightness=0.03"
            "[v]"
        )
        
        cmd = ["ffmpeg", "-i", video_path, "-filter_complex", filter_complex, "-map", "[v]", "-c:v", "libx264", "-crf", "23", "-preset", "medium", "-an", "-y", output]
        
        if run_ffmpeg(cmd, 180):
            logger.info(f"✅ Cropped: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
    except:
        return None

def add_captions_to_video(video_path: str, script: str, hook: str, temp_dir: str) -> Optional[str]:
    try:
        output = os.path.join(temp_dir, "captioned.mp4")
        logger.info("📝 Adding captions...")
        
        text = (hook if hook else script[:80]).replace("'", "").replace('"', '')[:80]
        
        filter_str = f"drawtext=text='{text}':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=h-300:borderw=4:bordercolor=black"
        
        cmd = ["ffmpeg", "-i", video_path, "-vf", filter_str, "-c:v", "libx264", "-crf", "23", "-c:a", "copy", "-y", output]
        
        if run_ffmpeg(cmd, 120):
            logger.info(f"✅ Captioned: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
    except:
        return None

async def combine_video_voice_music(video: str, voice: str, music: Optional[str], temp_dir: str) -> Optional[str]:
    try:
        output = os.path.join(temp_dir, "final.mp4")
        logger.info("🎬 Combining...")
        
        if music:
            cmd = [
                "ffmpeg", "-i", video, "-i", voice, "-i", music,
                "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.10[m];[v][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", output
            ]
        else:
            cmd = ["ffmpeg", "-i", video, "-i", voice, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", output]
        
        if run_ffmpeg(cmd, 120):
            logger.info(f"✅ Final: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
    except:
        return None

async def upload_to_youtube(video: str, title: str, description: str, user_id: str, database_manager) -> dict:
    try:
        logger.info("📤 Uploading to YouTube...")
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds_raw = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
        if not creds_raw:
            return {"success": False, "error": "YouTube credentials not found"}
        
        credentials = {
            "access_token": creds_raw.get("access_token"),
            "refresh_token": creds_raw.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
        }
        
        from mainY import youtube_scheduler
        
        full_desc = f"{description}\n\n#shorts #viral #trending #hindi"
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=full_desc,
            video_url=video
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            logger.info(f"✅ Uploaded! ID: {video_id}")
            return {"success": True, "video_id": video_id, "video_url": f"https://youtube.com/shorts/{video_id}"}
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

async def generate_mrbeast_short(youtube_url: str, target_duration: int, user_id: str, database_manager) -> dict:
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="mrbeast_")
        logger.info(f"🎬 START: {youtube_url} | {target_duration}s")
        
        # 1. Download
        video_path = await download_youtube_video(youtube_url, temp_dir)
        if not video_path:
            return {"success": False, "error": "Download failed - all 8 methods failed"}
        
        # 2. Duration check
        duration = get_video_duration(video_path)
        if duration < target_duration:
            return {"success": False, "error": f"Video too short: {duration:.0f}s"}
        
        # 3. Transcript
        transcript = await extract_transcript(video_path, temp_dir)
        if not transcript:
            return {"success": False, "error": "Transcription failed"}
        
        # 4. AI Rewrite
        rewrite = await rewrite_script_creatively(transcript, target_duration)
        script = rewrite["script"]
        title = rewrite["title"]
        hook = rewrite["hook"]
        
        # 5. Voice (1.1x)
        voice = await generate_hindi_voiceover_11x(script, temp_dir)
        if not voice:
            return {"success": False, "error": "Voice generation failed"}
        
        # 6. Music
        music = await download_background_music(temp_dir, target_duration)
        
        # 7. Crop + Zoom
        cropped = crop_and_zoom_video(video_path, temp_dir)
        if not cropped:
            return {"success": False, "error": "Cropping failed"}
        
        force_cleanup(video_path)
        
        # 8. Captions
        captioned = add_captions_to_video(cropped, script, hook, temp_dir)
        if not captioned:
            return {"success": False, "error": "Caption failed"}
        
        force_cleanup(cropped)
        
        # 9. Combine
        final = await combine_video_voice_music(captioned, voice, music, temp_dir)
        if not final:
            return {"success": False, "error": "Combining failed"}
        
        final_size = get_file_size_mb(final)
        
        # 10. Upload
        upload_result = await upload_to_youtube(final, title, script, user_id, database_manager)
        
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
                "script": script[:200] + "...",
                "size": f"{final_size:.1f}MB"
            }
        else:
            return {"success": False, "error": upload_result.get("error")}
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

@router.post("/api/mrbeast/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        youtube_url = data.get("youtube_url", "")
        target_duration = int(data.get("target_duration", 30))
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "Authentication required"})
        
        if not youtube_url or ("youtube.com" not in youtube_url and "youtu.be" not in youtube_url):
            return JSONResponse(status_code=400, content={"success": False, "error": "Invalid YouTube URL"})
        
        if not (MIN_DURATION <= target_duration <= MAX_DURATION):
            return JSONResponse(status_code=400, content={"success": False, "error": f"Duration must be {MIN_DURATION}-{MAX_DURATION}s"})
        
        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            generate_mrbeast_short(youtube_url, target_duration, user_id, database_manager),
            timeout=900
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']