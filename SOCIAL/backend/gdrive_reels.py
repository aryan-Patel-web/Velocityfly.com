"""
gdrive_reels.py – Single Video Re-Voicer with Golden Captions
================================================================
CORRECT FLOW:
1. Download video from Google Drive (public link)
2. Extract audio → Transcribe (Whisper/AssemblyAI/Deepgram)
3. Send to Mistral AI → 20% rephrase (keep sequence + story)
4. Strip original audio from video
5. Generate new Hindi voiceover (Edge TTS)
6. Burn GOLDEN captions with emojis (moving subtitles)
7. Mix voiceover + optional BGM
8. Upload to YouTube (same logic as Pixabay)

MULTIPLE LOGS for error tracking at every step.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio, logging, os, traceback
import httpx, json, re, random, subprocess
from typing import List, Optional
import tempfile, shutil, gc, base64
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# ENHANCED LOGGING SETUP
# ══════════════════════════════════════════════════════════════════════════════
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.DEBUG)  # Changed to DEBUG for maximum detail

# Console handler with detailed format
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")  # Free tier: 100 min/month
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")      # Free tier: $200 credit

EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "hi-IN-RaviNeural"]

STORY_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
]

COLLECTION = "gdrive_reels_tracker"
FFMPEG_TIMEOUT = 300
DOWNLOAD_TIMEOUT = 180

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def force_cleanup(*paths):
    """Cleanup files with logging"""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
                logger.debug(f"🗑️  Cleaned up: {p}")
        except Exception as e:
            logger.warning(f"⚠️  Cleanup failed for {p}: {e}")
    gc.collect()


def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT, step_name: str = "ffmpeg") -> bool:
    """Run ffmpeg with detailed logging"""
    logger.info(f"🎬 {step_name} START")
    logger.debug(f"   Command: {' '.join(cmd[:5])}...")
    
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        
        if r.returncode != 0:
            stderr = r.stderr.decode(errors='replace')
            logger.error(f"❌ {step_name} FAILED (exit code {r.returncode})")
            logger.error(f"   stderr: {stderr[-500:]}")
            return False
        
        logger.info(f"✅ {step_name} SUCCESS")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {step_name} TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"❌ {step_name} EXCEPTION: {e}")
        logger.error(traceback.format_exc())
        return False


def get_size_mb(fp: str) -> float:
    try:
        size = os.path.getsize(fp) / (1024 * 1024)
        logger.debug(f"📏 File size: {fp} = {size:.2f} MB")
        return size
    except Exception as e:
        logger.warning(f"⚠️  Size check failed: {e}")
        return 0.0


# ══════════════════════════════════════════════════════════════════════════════
# FILE ID EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

def extract_file_id(url: str) -> Optional[str]:
    """Extract file ID from any Google Drive URL format"""
    logger.info(f"📎 Extracting file ID from URL: {url[:60]}...")
    
    if not url:
        logger.error("❌ Empty URL provided")
        return None
    
    # Pattern A: /file/d/<ID>/…
    m = re.search(r"/file/d/([A-Za-z0-9_-]{15,})", url)
    if m:
        file_id = m.group(1)
        logger.info(f"✅ File ID extracted (pattern A): {file_id}")
        return file_id
    
    # Pattern B: ?id=<ID> or &id=<ID>
    m = re.search(r"[?&]id=([A-Za-z0-9_-]{15,})", url)
    if m:
        file_id = m.group(1)
        logger.info(f"✅ File ID extracted (pattern B): {file_id}")
        return file_id
    
    logger.error("❌ No file ID found in URL")
    return None


# ══════════════════════════════════════════════════════════════════════════════
# MONGODB
# ══════════════════════════════════════════════════════════════════════════════

async def _next_serial(db, user_id: str) -> int:
    logger.debug(f"🔢 Getting next serial for user: {user_id}")
    try:
        doc = await db[COLLECTION].find_one({"user_id": user_id}, sort=[("serial", -1)])
        if doc:
            next_num = doc["serial"] + 1
            logger.info(f"✅ Next serial: {next_num}")
            return next_num
    except Exception as e:
        logger.warning(f"⚠️  MongoDB serial query failed: {e}")
    
    logger.info("✅ Next serial: 1 (first video)")
    return 1


async def _save(db, record: dict):
    logger.info(f"💾 Saving record to MongoDB (serial={record.get('serial')})")
    try:
        await db[COLLECTION].insert_one(record)
        logger.info(f"✅ MongoDB save SUCCESS")
    except Exception as e:
        logger.error(f"❌ MongoDB save FAILED: {e}")
        logger.error(traceback.format_exc())


async def _history(db, user_id: str) -> list:
    logger.debug(f"📋 Fetching history for user: {user_id}")
    try:
        rows = []
        async for d in db[COLLECTION].find({"user_id": user_id}).sort("serial", -1).limit(50):
            d.pop("_id", None)
            rows.append(d)
        logger.info(f"✅ Found {len(rows)} history records")
        return rows
    except Exception as e:
        logger.error(f"❌ History fetch FAILED: {e}")
        return []


async def _mark_uploaded(db, user_id: str, serial: int, video_id: str, video_url: str):
    logger.info(f"🎯 Marking serial {serial} as uploaded")
    try:
        await db[COLLECTION].update_one(
            {"user_id": user_id, "serial": serial},
            {"$set": {"video_id": video_id, "video_url": video_url,
                      "uploaded": True, "uploaded_at": datetime.utcnow().isoformat()}}
        )
        logger.info(f"✅ Upload status updated")
    except Exception as e:
        logger.error(f"❌ Upload marking FAILED: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD VIDEO
# ══════════════════════════════════════════════════════════════════════════════

async def download_video(file_id: str, dest: str) -> bool:
    """Download video from Google Drive with detailed logging"""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    logger.info(f"⬇️  DOWNLOAD START: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as c:
            logger.debug("   Making initial request...")
            resp = await c.get(url)
            logger.debug(f"   Response status: {resp.status_code}, size: {len(resp.content)} bytes")

            # Handle confirmation page for large files
            if resp.status_code == 200 and len(resp.content) < 50000:
                txt = resp.text
                if "<html" in txt.lower()[:500]:
                    logger.info("   Detected confirmation page (large file)")
                    m = re.search(r'href="(/uc\?[^"]*&confirm=[^"]*)"', txt)
                    if m:
                        real_url = "https://drive.google.com" + m.group(1).replace("&amp;", "&")
                        logger.info(f"   Following confirmation URL...")
                        resp = await c.get(real_url)
                        logger.debug(f"   Final response: {resp.status_code}, {len(resp.content)} bytes")

            if resp.status_code == 200 and len(resp.content) > 2048:
                logger.info(f"   Writing {len(resp.content)} bytes to disk...")
                with open(dest, "wb") as f:
                    f.write(resp.content)
                
                size_mb = get_size_mb(dest)
                logger.info(f"✅ DOWNLOAD SUCCESS: {size_mb:.2f} MB")
                return True
            else:
                logger.error(f"❌ DOWNLOAD FAILED: status={resp.status_code}, size={len(resp.content)}")
                return False

    except httpx.TimeoutException:
        logger.error(f"⏱️  DOWNLOAD TIMEOUT after {DOWNLOAD_TIMEOUT}s")
        return False
    except Exception as e:
        logger.error(f"❌ DOWNLOAD EXCEPTION: {e}")
        logger.error(traceback.format_exc())
        return False


# ══════════════════════════════════════════════════════════════════════════════
# VIDEO DURATION
# ══════════════════════════════════════════════════════════════════════════════

async def get_duration(path: str) -> float:
    """Get video duration with logging"""
    logger.info(f"⏱️  Getting duration of: {path}")
    
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, timeout=30
        )
        
        if r.returncode == 0:
            duration = float(r.stdout.decode().strip())
            logger.info(f"✅ Duration: {duration:.2f}s")
            return duration
        else:
            logger.error(f"❌ ffprobe failed: {r.stderr.decode()}")
            return 0.0
            
    except Exception as e:
        logger.error(f"❌ Duration check EXCEPTION: {e}")
        return 0.0


# ══════════════════════════════════════════════════════════════════════════════
# AUDIO EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════

async def extract_audio(video: str, wav: str) -> bool:
    """Extract audio as WAV with logging"""
    logger.info("🔊 EXTRACTING AUDIO")
    return run_ffmpeg(
        ["ffmpeg", "-i", video, "-vn", "-acodec", "pcm_s16le",
         "-ar", "16000", "-ac", "1", "-y", wav],
        timeout=60,
        step_name="Audio Extraction"
    )


# ══════════════════════════════════════════════════════════════════════════════
# TRANSCRIPTION (3 METHODS)
# ══════════════════════════════════════════════════════════════════════════════

async def transcribe_whisper_local(wav: str) -> Optional[str]:
    """Try local Whisper CLI"""
    logger.info("🎙️  TRANSCRIBE METHOD 1: Whisper CLI (local)")
    
    try:
        out_dir = os.path.dirname(wav)
        logger.debug(f"   Running whisper on: {wav}")
        
        r = subprocess.run(
            ["whisper", wav, "--language", "hi", "--model", "small",
             "--output_dir", out_dir, "--output_format", "txt"],
            capture_output=True, timeout=300
        )
        
        if r.returncode == 0:
            txt_file = wav.rsplit(".", 1)[0] + ".txt"
            logger.debug(f"   Looking for output: {txt_file}")
            
            if os.path.exists(txt_file):
                text = open(txt_file, encoding='utf-8').read().strip()
                if text:
                    logger.info(f"✅ Whisper SUCCESS: {len(text)} chars")
                    return text
                else:
                    logger.warning("⚠️  Whisper output file empty")
            else:
                logger.warning(f"⚠️  Whisper output file not found: {txt_file}")
        else:
            stderr = r.stderr.decode(errors='replace')
            logger.warning(f"⚠️  Whisper failed: {stderr[:200]}")
            
    except FileNotFoundError:
        logger.info("   Whisper CLI not installed")
    except subprocess.TimeoutExpired:
        logger.warning("⏱️  Whisper timeout")
    except Exception as e:
        logger.warning(f"⚠️  Whisper exception: {e}")
    
    return None


async def transcribe_assemblyai(wav: str) -> Optional[str]:
    """Try AssemblyAI (free tier: 100 min/month)"""
    logger.info("🎙️  TRANSCRIBE METHOD 2: AssemblyAI")
    
    if not ASSEMBLYAI_API_KEY:
        logger.info("   AssemblyAI API key not set")
        return None
    
    try:
        logger.debug("   Uploading audio to AssemblyAI...")
        
        # Step 1: Upload file
        async with httpx.AsyncClient(timeout=120) as client:
            with open(wav, 'rb') as f:
                upload_resp = await client.post(
                    "https://api.assemblyai.com/v2/upload",
                    headers={"authorization": ASSEMBLYAI_API_KEY},
                    content=f.read()
                )
            
            if upload_resp.status_code != 200:
                logger.warning(f"⚠️  Upload failed: {upload_resp.status_code}")
                return None
            
            audio_url = upload_resp.json()["upload_url"]
            logger.debug(f"   Audio uploaded: {audio_url}")
            
            # Step 2: Request transcription
            logger.debug("   Requesting transcription...")
            transcript_resp = await client.post(
                "https://api.assemblyai.com/v2/transcript",
                headers={"authorization": ASSEMBLYAI_API_KEY},
                json={"audio_url": audio_url, "language_code": "hi"}
            )
            
            if transcript_resp.status_code != 200:
                logger.warning(f"⚠️  Transcription request failed: {transcript_resp.status_code}")
                return None
            
            transcript_id = transcript_resp.json()["id"]
            logger.debug(f"   Transcript ID: {transcript_id}")
            
            # Step 3: Poll for result
            logger.debug("   Polling for result...")
            for attempt in range(60):  # Max 5 minutes
                await asyncio.sleep(5)
                
                result_resp = await client.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers={"authorization": ASSEMBLYAI_API_KEY}
                )
                
                status = result_resp.json().get("status")
                logger.debug(f"   Status: {status} (attempt {attempt + 1})")
                
                if status == "completed":
                    text = result_resp.json().get("text", "")
                    if text:
                        logger.info(f"✅ AssemblyAI SUCCESS: {len(text)} chars")
                        return text
                    else:
                        logger.warning("⚠️  AssemblyAI completed but text empty")
                        return None
                
                elif status == "error":
                    error = result_resp.json().get("error")
                    logger.warning(f"⚠️  AssemblyAI error: {error}")
                    return None
            
            logger.warning("⏱️  AssemblyAI timeout after 5 minutes")
            
    except Exception as e:
        logger.warning(f"⚠️  AssemblyAI exception: {e}")
        logger.debug(traceback.format_exc())
    
    return None


async def transcribe_deepgram(wav: str) -> Optional[str]:
    """Try Deepgram (free tier: $200 credit)"""
    logger.info("🎙️  TRANSCRIBE METHOD 3: Deepgram")
    
    if not DEEPGRAM_API_KEY:
        logger.info("   Deepgram API key not set")
        return None
    
    try:
        logger.debug("   Uploading to Deepgram...")
        
        async with httpx.AsyncClient(timeout=120) as client:
            with open(wav, 'rb') as f:
                resp = await client.post(
                    "https://api.deepgram.com/v1/listen",
                    params={"language": "hi", "model": "nova-2"},
                    headers={
                        "Authorization": f"Token {DEEPGRAM_API_KEY}",
                        "Content-Type": "audio/wav"
                    },
                    content=f.read()
                )
            
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                
                if text:
                    logger.info(f"✅ Deepgram SUCCESS: {len(text)} chars")
                    return text
                else:
                    logger.warning("⚠️  Deepgram response has no text")
            else:
                logger.warning(f"⚠️  Deepgram failed: {resp.status_code} - {resp.text[:200]}")
                
    except Exception as e:
        logger.warning(f"⚠️  Deepgram exception: {e}")
        logger.debug(traceback.format_exc())
    
    return None


async def transcribe(wav: str) -> str:
    """Try all transcription methods in order"""
    logger.info("=" * 80)
    logger.info("📝 TRANSCRIPTION START")
    logger.info("=" * 80)
    
    # Method 1: Whisper CLI (local, free, unlimited)
    text = await transcribe_whisper_local(wav)
    if text:
        return text
    
    # Method 2: AssemblyAI (100 min/month free)
    text = await transcribe_assemblyai(wav)
    if text:
        return text
    
    # Method 3: Deepgram ($200 credit)
    text = await transcribe_deepgram(wav)
    if text:
        return text
    
    logger.error("❌ ALL TRANSCRIPTION METHODS FAILED")
    return ""


# ══════════════════════════════════════════════════════════════════════════════
# MISTRAL AI - 20% REPHRASE
# ══════════════════════════════════════════════════════════════════════════════

async def mistral_rephrase_seo(transcript: str, duration: float) -> dict:
    """Rephrase with Mistral AI - keep 80% same, change 20%"""
    logger.info("=" * 80)
    logger.info("🤖 MISTRAL AI REPHRASE START")
    logger.info("=" * 80)
    
    if not MISTRAL_API_KEY:
        logger.error("❌ MISTRAL_API_KEY not set")
        raise Exception("MISTRAL_API_KEY not set")

    max_words = int(duration * 2.8)
    logger.info(f"   Target: {max_words} words for {duration:.1f}s video")
    
    prompt = (
        "You are a YouTube Shorts editor. Rephrase this Hindi transcript.\n\n"
        "STRICT RULES:\n"
        "1. Keep EXACT SAME sequence/story order - do NOT reorganize\n"
        "2. Change ONLY ~20% of words (synonyms, slight rewording)\n"
        "3. Keep ALL character names, places, events EXACTLY as is\n"
        f"4. Target word count: {max_words} words (fits {duration:.1f}s)\n"
        "5. Natural Hindi flow with commas for pauses\n"
        "6. Viral Hinglish title with power words + 1-2 emojis\n"
        "7. 2-line Hinglish description\n"
        "8. EXACTLY 15 SEO keywords (real YouTube searches)\n"
        "9. EXACTLY 6 hashtags (include #Shorts)\n\n"
        f"TRANSCRIPT:\n{transcript}\n\n"
        "Return ONLY valid JSON (no markdown):\n"
        '{"script":"...","title":"...","description":"...","keywords":[...],"tags":[...]}'
    )
    
    try:
        logger.debug("   Calling Mistral API...")
        
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "Output ONLY valid JSON. No markdown."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.45,
                    "max_tokens": 1400
                }
            )
        
        if r.status_code != 200:
            logger.error(f"❌ Mistral API failed: {r.status_code}")
            logger.error(f"   Response: {r.text[:300]}")
            raise Exception(f"Mistral {r.status_code}: {r.text[:300]}")

        logger.debug("   Parsing response...")
        raw = r.json()["choices"][0]["message"]["content"]
        raw = re.sub(r"```json\s*|```", "", raw).strip()
        
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            logger.error("❌ No JSON found in Mistral response")
            logger.debug(f"   Raw response: {raw[:500]}")
            raise Exception("No JSON in Mistral response")
        
        data = json.loads(m.group(0))
        
        script = data.get("script", transcript)
        title = data.get("title", "Amazing Story 🔥")
        desc = data.get("description", script[:150])
        keywords = data.get("keywords", [])
        tags = data.get("tags", [])

        # Ensure minimums
        while len(keywords) < 15:
            keywords.append(f"hindi story shorts {len(keywords)}")
        while len(tags) < 6:
            tags.append("#Shorts")

        word_count = len(script.split())
        logger.info(f"✅ MISTRAL SUCCESS")
        logger.info(f"   Title: {title}")
        logger.info(f"   Script: {word_count}/{max_words} words")
        logger.info(f"   Keywords: {len(keywords[:15])}, Tags: {len(tags[:6])}")
        
        return {
            "script": script,
            "title": title,
            "description": desc,
            "keywords": keywords[:15],
            "tags": tags[:6]
        }
        
    except Exception as e:
        logger.error(f"❌ MISTRAL EXCEPTION: {e}")
        logger.error(traceback.format_exc())
        raise


# ══════════════════════════════════════════════════════════════════════════════
# EDGE TTS VOICEOVER
# ══════════════════════════════════════════════════════════════════════════════

async def generate_voiceover(script: str, temp_dir: str) -> Optional[str]:
    """Generate Hindi voiceover with Edge TTS"""
    logger.info("=" * 80)
    logger.info("🎙️  EDGE TTS VOICEOVER START")
    logger.info("=" * 80)
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        out = os.path.join(temp_dir, "voiceover.mp3")
        
        logger.info(f"   Voice: {voice}")
        logger.info(f"   Script length: {len(script)} chars")
        logger.debug("   Generating speech...")
        
        await edge_tts.Communicate(script[:2500], voice, rate="+10%").save(out)
        
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            size = get_size_mb(out)
            logger.info(f"✅ VOICEOVER SUCCESS: {size:.2f} MB")
            return out
        else:
            logger.error("❌ VOICEOVER file empty or missing")
            return None
            
    except ImportError:
        logger.error("❌ edge_tts not installed: pip install edge-tts")
        return None
    except Exception as e:
        logger.error(f"❌ VOICEOVER EXCEPTION: {e}")
        logger.error(traceback.format_exc())
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SRT GOLDEN CAPTIONS (with emojis)
# ══════════════════════════════════════════════════════════════════════════════

def _ts(sec: float) -> str:
    """Convert seconds to SRT timestamp"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def build_srt_with_emojis(script: str, total_dur: float) -> str:
    """Build SRT with 5-word phrases + emojis"""
    logger.info("📝 BUILDING GOLDEN CAPTIONS")
    
    words = script.split()
    logger.info(f"   Total words: {len(words)}")
    
    # Group into 5-word phrases
    phrases = []
    for i in range(0, len(words), 5):
        phrase = " ".join(words[i:i+5])
        
        # Add emojis based on keywords
        if any(x in phrase.lower() for x in ["krishna", "कृष्ण", "भगवान"]):
            phrase = f"🕉️ {phrase}"
        elif any(x in phrase.lower() for x in ["shiv", "शिव", "महादेव"]):
            phrase = f"🔱 {phrase}"
        elif any(x in phrase.lower() for x in ["ram", "राम"]):
            phrase = f"🏹 {phrase}"
        elif any(x in phrase.lower() for x in ["love", "प्यार", "प्रेम"]):
            phrase = f"❤️ {phrase}"
        elif any(x in phrase.lower() for x in ["war", "युद्ध", "fight"]):
            phrase = f"⚔️ {phrase}"
        
        phrases.append(phrase)
    
    if not phrases:
        logger.warning("⚠️  No phrases generated")
        return ""
    
    dur_each = total_dur / len(phrases)
    logger.info(f"   Phrases: {len(phrases)} @ {dur_each:.2f}s each")
    
    blocks = []
    for i, ph in enumerate(phrases):
        t0 = i * dur_each
        t1 = t0 + dur_each
        blocks.append(f"{i+1}\n{_ts(t0)} --> {_ts(t1)}\n{ph}\n")
    
    logger.info(f"✅ SRT BUILT: {len(blocks)} subtitle blocks")
    return "\n".join(blocks)


# ══════════════════════════════════════════════════════════════════════════════
# FFMPEG PIPELINES
# ══════════════════════════════════════════════════════════════════════════════

async def strip_audio(vin: str, vout: str) -> bool:
    """Remove original audio from video"""
    logger.info("🔇 STRIPPING ORIGINAL AUDIO")
    return run_ffmpeg(
        ["ffmpeg", "-i", vin, "-vcodec", "copy", "-an", "-y", vout],
        timeout=60,
        step_name="Strip Audio"
    )


async def download_bgm(temp_dir: str, duration: float) -> Optional[str]:
    """Download and trim BGM"""
    logger.info("🎵 DOWNLOADING BGM")
    
    url = random.choice(STORY_BGM_URLS)
    logger.debug(f"   URL: {url[:60]}...")
    
    raw = os.path.join(temp_dir, "bgm_raw.mp3")
    out = os.path.join(temp_dir, "bgm.mp3")
    
    try:
        logger.debug("   Fetching...")
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as c:
            r = await c.get(url)
            
            if r.status_code == 200 and len(r.content) > 500:
                open(raw, "wb").write(r.content)
                logger.debug(f"   Downloaded: {get_size_mb(raw):.2f} MB")
                
                logger.debug(f"   Trimming to {duration:.1f}s...")
                if run_ffmpeg(
                    ["ffmpeg", "-i", raw, "-t", str(duration), "-acodec", "copy", "-y", out],
                    timeout=60,
                    step_name="BGM Trim"
                ):
                    force_cleanup(raw)
                    logger.info(f"✅ BGM READY: {get_size_mb(out):.2f} MB")
                    return out
                else:
                    logger.warning("⚠️  BGM trim failed, using raw file")
                    return raw if os.path.exists(raw) else None
            else:
                logger.warning(f"⚠️  BGM download failed: {r.status_code}")
                
    except Exception as e:
        logger.warning(f"⚠️  BGM exception: {e}")
    
    return None


async def composite(silent_video: str, voiceover: str, srt_path: str,
                    bgm: Optional[str], final: str) -> bool:
    """Burn GOLDEN CAPTIONS + mix audio"""
    logger.info("=" * 80)
    logger.info("✨ FINAL COMPOSITE START")
    logger.info("=" * 80)
    
    captioned = final.replace(".mp4", "_cap.mp4")

    # Escape SRT path for ffmpeg
    srt_esc = srt_path.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")
    
    # GOLDEN CAPTION STYLE (dark golden #B8860B with black outline)
    sub_filter = (
        f"subtitles='{srt_esc}':"
        "force_style="
        "Fontname=Arial Black,"
        "Fontsize=32,"
        "PrimaryColour=&H000B86B8,"    # BGR format for #B8860B (dark golden)
        "OutlineColour=&H00000000,"    # Black outline
        "BackColour=&H80000000,"       # Semi-transparent black bg
        "Bold=1,"
        "Outline=3,"                   # Thick outline
        "Shadow=2,"                    # Shadow depth
        "Alignment=2,"                 # Bottom center
        "MarginL=40,"
        "MarginR=40,"
        "MarginV=80"                   # Higher margin from bottom
    )
    
    logger.info("   STEP 1/2: Burning golden captions...")
    if not run_ffmpeg(
        ["ffmpeg", "-i", silent_video, "-vf", sub_filter,
         "-c:v", "libx264", "-crf", "22", "-preset", "fast",
         "-pix_fmt", "yuv420p", "-y", captioned],
        timeout=FFMPEG_TIMEOUT,
        step_name="Burn Captions"
    ):
        logger.error("❌ CAPTION BURN FAILED")
        return False

    # Audio mix
    logger.info("   STEP 2/2: Mixing audio...")
    
    if bgm and os.path.exists(bgm):
        logger.debug("   Mixing: voiceover (100%) + BGM (8%)")
        cmd = [
            "ffmpeg",
            "-i", captioned, "-i", voiceover, "-i", bgm,
            "-filter_complex",
            "[1:a]volume=1.0[v];[2:a]volume=0.08[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-y", final
        ]
    else:
        logger.debug("   Mixing: voiceover only (no BGM)")
        cmd = [
            "ffmpeg",
            "-i", captioned, "-i", voiceover,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-y", final
        ]

    ok = run_ffmpeg(cmd, timeout=FFMPEG_TIMEOUT, step_name="Audio Mix")
    force_cleanup(captioned)
    
    if ok:
        logger.info(f"✅ COMPOSITE SUCCESS: {get_size_mb(final):.2f} MB")
    else:
        logger.error("❌ COMPOSITE FAILED")
    
    return ok


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD (PIXABAY LOGIC)
# ══════════════════════════════════════════════════════════════════════════════

async def upload_youtube(video_path: str, title: str, description: str,
                         keywords: List[str], tags: List[str],
                         user_id: str, db) -> dict:
    """Upload to YouTube using exact Pixabay working logic"""
    logger.info("=" * 80)
    logger.info("📤 YOUTUBE UPLOAD START")
    logger.info("=" * 80)
    
    try:
        logger.debug("   Importing YouTube database manager...")
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            logger.error("❌ YouTube database unavailable")
            return {"success": False, "error": "YouTube database not available"}
        
        if not yt_db.youtube.client:
            logger.debug("   Connecting to database...")
            await yt_db.connect()
        
        logger.info(f"   Fetching credentials for user: {user_id}")
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            logger.error("❌ YouTube credentials not found")
            return {"success": False, "error": "YouTube credentials not found"}
        
        logger.debug("   Building credential object...")
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
        
        full_desc = description + "\n\n" + "\n".join(keywords) + "\n\n" + "\n".join(tags)
        
        logger.info("   Calling upload scheduler...")
        from mainY import youtube_scheduler
        
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=full_desc,
            video_url=video_path,
        )
        
        if upload_result.get("success"):
            video_id = upload_result.get("video_id")
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            logger.info(f"✅ UPLOAD SUCCESS!")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
        else:
            error = upload_result.get("error", "Upload failed")
            logger.error(f"❌ UPLOAD FAILED: {error}")
            return {"success": False, "error": error}
            
    except Exception as e:
        logger.error(f"❌ UPLOAD EXCEPTION: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

async def process_video(drive_url: str, user_id: str, db) -> dict:
    """Full processing pipeline"""
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " " * 20 + "GDRIVE REEL PROCESSING START" + " " * 30 + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    temp_dir = tempfile.mkdtemp(prefix="gdrive_reel_")
    logger.info(f"📁 Temp directory: {temp_dir}")
    
    try:
        # STEP 1: Extract file ID
        file_id = extract_file_id(drive_url)
        if not file_id:
            return {"success": False, "error": "Could not extract file ID"}

        # STEP 2: Get serial number
        serial = await _next_serial(db, user_id)

        # STEP 3: Download video
        video_src = os.path.join(temp_dir, "source.mp4")
        if not await download_video(file_id, video_src):
            return {"success": False, "error": "Download failed. Make sure link is public."}

        # STEP 4: Get duration
        duration = await get_duration(video_src)
        if duration <= 0:
            return {"success": False, "error": "Could not read video duration."}

        # STEP 5: Extract audio
        wav = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video_src, wav):
            return {"success": False, "error": "Audio extraction failed."}

        # STEP 6: Transcribe (try 3 methods)
        transcript = await transcribe(wav)
        if not transcript or len(transcript.strip()) < 8:
            return {"success": False, "error": "Transcription failed. Video must have clear speech."}

        # STEP 7: Mistral AI rephrase
        meta = await mistral_rephrase_seo(transcript, duration)
        script = meta["script"]
        title = meta["title"]
        desc = meta["description"]
        keywords = meta["keywords"]
        tags = meta["tags"]

        # STEP 8: Generate voiceover
        voiceover = await generate_voiceover(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Voiceover generation failed."}

        # STEP 9: Strip original audio
        silent = os.path.join(temp_dir, "silent.mp4")
        if not await strip_audio(video_src, silent):
            return {"success": False, "error": "Stripping audio failed."}

        # STEP 10: Build golden captions
        srt_path = os.path.join(temp_dir, "captions.srt")
        srt_content = build_srt_with_emojis(script, duration)
        open(srt_path, "w", encoding="utf-8").write(srt_content)

        # STEP 11: Download BGM
        bgm = await download_bgm(temp_dir, duration)

        # STEP 12: Composite (captions + audio)
        final = os.path.join(temp_dir, "final_reel.mp4")
        if not await composite(silent, voiceover, srt_path, bgm, final):
            return {"success": False, "error": "Final composite failed."}

        # STEP 13: Save to MongoDB
        record = {
            "user_id": user_id,
            "serial": serial,
            "drive_url": drive_url,
            "drive_file_id": file_id,
            "transcript": transcript,
            "ai_script": script,
            "title": title,
            "description": desc,
            "keywords": keywords,
            "tags": tags,
            "duration": round(duration, 2),
            "uploaded": False,
            "video_id": None,
            "video_url": None,
            "processed_at": datetime.utcnow().isoformat(),
        }
        await _save(db, record)

        logger.info("╔" + "═" * 78 + "╗")
        logger.info("║" + " " * 25 + "🎉 PROCESSING COMPLETE!" + " " * 29 + "║")
        logger.info("╚" + "═" * 78 + "╝")

        return {
            "success": True,
            "serial": serial,
            "title": title,
            "description": desc,
            "keywords": keywords,
            "tags": tags,
            "duration": round(duration, 2),
            "ai_script": script,
            "transcript": transcript,
            "uploaded": False,
        }

    except Exception as e:
        logger.error(f"╔{'═' * 78}╗")
        logger.error(f"║{' ' * 28}❌ FATAL ERROR{' ' * 36}║")
        logger.error(f"╚{'═' * 78}╝")
        logger.error(f"{e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}
    
    finally:
        logger.info(f"🧹 Cleaning up temp directory...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()


async def reprocess_and_upload(serial: int, doc: dict, user_id: str, db) -> dict:
    """Re-process saved reel and upload to YouTube"""
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " " * 22 + "RE-PROCESS & UPLOAD START" + " " * 31 + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    temp_dir = tempfile.mkdtemp(prefix="gdrive_upload_")
    
    try:
        file_id = doc["drive_file_id"]
        video_src = os.path.join(temp_dir, "source.mp4")

        if not await download_video(file_id, video_src):
            return {"success": False, "error": "Re-download failed."}

        duration = await get_duration(video_src)
        script = doc["ai_script"]
        title = doc["title"]
        desc = doc["description"]
        keywords = doc["keywords"]
        tags = doc["tags"]

        # Generate fresh voiceover
        voiceover = await generate_voiceover(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Voiceover failed."}

        # Strip + captions + bgm + composite
        silent = os.path.join(temp_dir, "silent.mp4")
        await strip_audio(video_src, silent)

        srt_path = os.path.join(temp_dir, "captions.srt")
        srt_content = build_srt_with_emojis(script, duration)
        open(srt_path, "w", encoding="utf-8").write(srt_content)

        bgm = await download_bgm(temp_dir, duration)
        final = os.path.join(temp_dir, "final_reel.mp4")
        
        if not await composite(silent, voiceover, srt_path, bgm, final):
            return {"success": False, "error": "Composite failed."}

        # Upload to YouTube
        up = await upload_youtube(final, title, desc, keywords, tags, user_id, db)
        
        if not up.get("success"):
            return {"success": False, "error": up.get("error", "Upload failed")}

        await _mark_uploaded(db, user_id, serial, up["video_id"], up["video_url"])
        
        logger.info("╔" + "═" * 78 + "╗")
        logger.info("║" + " " * 28 + "🎉 UPLOAD COMPLETE!" + " " * 30 + "║")
        logger.info("╚" + "═" * 78 + "╝")
        
        return {
            "success": True,
            "serial": serial,
            "video_id": up["video_id"],
            "video_url": up["video_url"]
        }

    except Exception as e:
        logger.error(f"❌ Reprocess/upload exception: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()


# ══════════════════════════════════════════════════════════════════════════════
# API ROUTES
# ══════════════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.get("/api/gdrive-reels/status")
async def status_endpoint(request: Request):
    try:
        user_id = request.query_params.get("user_id")
        if not user_id:
            return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
        from Supermain import database_manager
        return JSONResponse(content={
            "success": True,
            "next_serial": await _next_serial(database_manager.db, user_id),
            "total_processed": len(await _history(database_manager.db, user_id)),
            "history": await _history(database_manager.db, user_id)
        })
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})

        drive_url = (data.get("drive_url") or "").strip()
        
        if not drive_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "drive_url required"})
        
        if "drive.google.com" not in drive_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Must be a Google Drive URL"})

        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            process_video(drive_url, user_id, database_manager.db),
            timeout=600
        )
        
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        logger.error("⏱️  Process endpoint timeout")
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout (10 min)"})
    except Exception as e:
        logger.error(f"Process endpoint error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/api/gdrive-reels/upload-to-youtube")
async def upload_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        serial = data.get("serial")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})
        
        if serial is None:
            return JSONResponse(status_code=400, content={"success": False, "error": "serial required"})

        from Supermain import database_manager
        
        doc = await database_manager.db[COLLECTION].find_one({"user_id": user_id, "serial": serial})
        
        if not doc:
            return JSONResponse(status_code=404, content={"success": False, "error": f"Serial {serial} not found"})
        
        if doc.get("uploaded"):
            return JSONResponse(content={
                "success": True,
                "message": "Already uploaded",
                "video_id": doc.get("video_id"),
                "video_url": doc.get("video_url")
            })

        result = await asyncio.wait_for(
            reprocess_and_upload(serial, doc, user_id, database_manager.db),
            timeout=600
        )
        
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        logger.error("⏱️  Upload endpoint timeout")
        return JSONResponse(status_code=408, content={"success": False, "error": "Upload timeout"})
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


__all__ = ["router"]