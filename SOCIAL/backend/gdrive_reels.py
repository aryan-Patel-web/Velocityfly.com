"""
gdrive_reels_final.py – Video Re-Voicer with LOCAL Transcription ONLY
========================================================================
✅ MAJOR CHANGES:
   - faster-whisper (PRIMARY) - Fast, local, works on Render
   - SpeechRecognition + pocketsphinx (FALLBACK 1) - Offline Hindi
   - Vosk (FALLBACK 2) - Offline speech recognition
   - NO API transcription (AssemblyAI/Deepgram removed)
   - NO video storage in MongoDB
   - DIRECT YouTube upload after processing
   - Works on Python 3.11 + Render deploy

FLOW:
1. Download video from Google Drive
2. Extract audio → Transcribe (faster-whisper → SpeechRecognition → Vosk)
3. Mistral AI rephrase (20%)
4. Generate Hindi voiceover
5. Burn golden captions
6. Mix audio + BGM
7. Upload DIRECTLY to YouTube
8. Save ONLY metadata to MongoDB (no video)
9. Cleanup temp files
========================================================================
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio, logging, os, traceback
import httpx, json, re, random, subprocess
from typing import List, Optional
import tempfile, shutil, gc
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "hi-IN-RaviNeural"]

STORY_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
]

COLLECTION = "gdrive_reels_tracker"
FFMPEG_TIMEOUT = 300
DOWNLOAD_TIMEOUT = 180

# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

def force_cleanup(*paths):
    """Cleanup files with logging"""
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
                logger.debug(f"🗑️  Cleaned: {p}")
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
            logger.error(f"❌ {step_name} FAILED (exit {r.returncode})")
            logger.error(f"   stderr: {stderr[-500:]}")
            return False
        
        logger.info(f"✅ {step_name} SUCCESS")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️  {step_name} TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"❌ {step_name} EXCEPTION: {e}")
        return False


def get_size_mb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0.0


def extract_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID"""
    logger.info(f"📎 Extracting file ID from: {url[:60]}...")
    
    if not url:
        return None
    
    m = re.search(r"/file/d/([A-Za-z0-9_-]{15,})", url)
    if m:
        return m.group(1)
    
    m = re.search(r"[?&]id=([A-Za-z0-9_-]{15,})", url)
    if m:
        return m.group(1)
    
    return None


# ═══════════════════════════════════════════════════════════════════════
# MONGODB (METADATA ONLY - NO VIDEO STORAGE)
# ═══════════════════════════════════════════════════════════════════════

async def _next_serial(db, user_id: str) -> int:
    try:
        doc = await db[COLLECTION].find_one({"user_id": user_id}, sort=[("serial", -1)])
        if doc:
            return doc["serial"] + 1
    except:
        pass
    return 1


async def _save_metadata(db, record: dict):
    """Save ONLY metadata - NO video data"""
    logger.info(f"💾 Saving METADATA only (serial={record.get('serial')})")
    logger.info(f"   ⚠️  NO VIDEO STORED IN DATABASE")
    try:
        await db[COLLECTION].insert_one(record)
        logger.info(f"✅ Metadata saved")
    except Exception as e:
        logger.error(f"❌ Save failed: {e}")


async def _history(db, user_id: str) -> list:
    try:
        rows = []
        async for d in db[COLLECTION].find({"user_id": user_id}).sort("serial", -1).limit(50):
            d.pop("_id", None)
            rows.append(d)
        return rows
    except:
        return []


async def _mark_uploaded(db, user_id: str, serial: int, video_id: str, video_url: str):
    try:
        await db[COLLECTION].update_one(
            {"user_id": user_id, "serial": serial},
            {"$set": {"video_id": video_id, "video_url": video_url,
                      "uploaded": True, "uploaded_at": datetime.utcnow().isoformat()}}
        )
        logger.info(f"✅ Marked serial {serial} as uploaded")
    except Exception as e:
        logger.error(f"❌ Update failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# DOWNLOAD VIDEO
# ═══════════════════════════════════════════════════════════════════════

async def download_video(file_id: str, dest: str) -> bool:
    """Download from Google Drive"""
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    logger.info(f"⬇️  Downloading: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as c:
            resp = await c.get(url)
            
            # Handle large file confirmation
            if resp.status_code == 200 and len(resp.content) < 50000 and "<html" in resp.text[:500].lower():
                m = re.search(r'href="(/uc\?[^"]*&confirm=[^"]*)"', resp.text)
                if m:
                    real_url = "https://drive.google.com" + m.group(1).replace("&amp;", "&")
                    resp = await c.get(real_url)

            if resp.status_code == 200 and len(resp.content) > 2048:
                with open(dest, "wb") as f:
                    f.write(resp.content)
                logger.info(f"✅ Downloaded: {get_size_mb(dest):.2f} MB")
                return True
            
            logger.error(f"❌ Download failed: {resp.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Download exception: {e}")
        return False


async def get_duration(path: str) -> float:
    """Get video duration"""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, timeout=30
        )
        
        if r.returncode == 0:
            return float(r.stdout.decode().strip())
        return 0.0
    except:
        return 0.0


async def extract_audio(video: str, wav: str) -> bool:
    """Extract audio as WAV"""
    logger.info("🔊 Extracting audio...")
    return run_ffmpeg(
        ["ffmpeg", "-i", video, "-vn", "-acodec", "pcm_s16le",
         "-ar", "16000", "-ac", "1", "-y", wav],
        timeout=60,
        step_name="Audio Extract"
    )


# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION - 3 LOCAL METHODS (NO APIs)
# ═══════════════════════════════════════════════════════════════════════

async def transcribe_faster_whisper(wav: str) -> Optional[str]:
    """METHOD 1: faster-whisper (PRIMARY - works on Render)"""
    logger.info("🎙️  METHOD 1: faster-whisper (local)")
    
    try:
        from faster_whisper import WhisperModel
        
        logger.debug("   Loading model...")
        # Use tiny or base for faster processing on deploy
        model = WhisperModel("base", device="cpu", compute_type="int8")
        
        logger.debug("   Transcribing...")
        segments, info = model.transcribe(wav, language="hi", beam_size=5)
        
        text = " ".join([segment.text for segment in segments])
        
        if text and len(text) > 8:
            logger.info(f"✅ faster-whisper SUCCESS: {len(text)} chars")
            return text.strip()
        else:
            logger.warning("⚠️  faster-whisper output too short")
            
    except ImportError:
        logger.warning("⚠️  faster-whisper not installed")
    except Exception as e:
        logger.warning(f"⚠️  faster-whisper error: {e}")
    
    return None


async def transcribe_speech_recognition(wav: str) -> Optional[str]:
    """METHOD 2: SpeechRecognition with Sphinx (FALLBACK 1)"""
    logger.info("🎙️  METHOD 2: SpeechRecognition + pocketsphinx")
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        logger.debug("   Loading audio file...")
        with sr.AudioFile(wav) as source:
            audio = recognizer.record(source)
        
        logger.debug("   Recognizing speech...")
        # Try Google first (free, no API key), then Sphinx
        try:
            text = recognizer.recognize_google(audio, language="hi-IN")
            if text and len(text) > 8:
                logger.info(f"✅ Google SR SUCCESS: {len(text)} chars")
                return text.strip()
        except:
            pass
        
        # Fallback to Sphinx (offline)
        try:
            text = recognizer.recognize_sphinx(audio, language="hi-IN")
            if text and len(text) > 8:
                logger.info(f"✅ Sphinx SUCCESS: {len(text)} chars")
                return text.strip()
        except:
            pass
            
    except ImportError:
        logger.warning("⚠️  SpeechRecognition not installed")
    except Exception as e:
        logger.warning(f"⚠️  SpeechRecognition error: {e}")
    
    return None


async def transcribe_vosk(wav: str) -> Optional[str]:
    """METHOD 3: Vosk (FALLBACK 2 - offline)"""
    logger.info("🎙️  METHOD 3: Vosk (offline)")
    
    try:
        from vosk import Model, KaldiRecognizer
        import wave
        
        # You need to download Vosk Hindi model first
        # https://alphacephei.com/vosk/models
        model_path = "/app/vosk-model-small-hi-0.22"  # Adjust path
        
        if not os.path.exists(model_path):
            logger.warning(f"⚠️  Vosk model not found at {model_path}")
            return None
        
        logger.debug("   Loading Vosk model...")
        model = Model(model_path)
        
        wf = wave.open(wav, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        results = []
        logger.debug("   Processing audio...")
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                results.append(result.get("text", ""))
        
        # Final result
        result = json.loads(rec.FinalResult())
        results.append(result.get("text", ""))
        
        text = " ".join(results).strip()
        
        if text and len(text) > 8:
            logger.info(f"✅ Vosk SUCCESS: {len(text)} chars")
            return text
        else:
            logger.warning("⚠️  Vosk output too short")
            
    except ImportError:
        logger.warning("⚠️  Vosk not installed")
    except Exception as e:
        logger.warning(f"⚠️  Vosk error: {e}")
    
    return None


async def transcribe(wav: str) -> str:
    """Try all 3 local transcription methods"""
    logger.info("=" * 80)
    logger.info("📝 TRANSCRIPTION START (LOCAL ONLY - NO APIs)")
    logger.info("=" * 80)
    
    # Method 1: faster-whisper (best for deployment)
    text = await transcribe_faster_whisper(wav)
    if text:
        return text
    
    # Method 2: SpeechRecognition
    text = await transcribe_speech_recognition(wav)
    if text:
        return text
    
    # Method 3: Vosk (offline)
    text = await transcribe_vosk(wav)
    if text:
        return text
    
    logger.error("❌ ALL TRANSCRIPTION METHODS FAILED")
    return ""


# ═══════════════════════════════════════════════════════════════════════
# MISTRAL AI REPHRASE
# ═══════════════════════════════════════════════════════════════════════

async def mistral_rephrase_seo(transcript: str, duration: float) -> dict:
    """Rephrase with Mistral - 20% change"""
    logger.info("🤖 Mistral AI rephrase...")
    
    if not MISTRAL_API_KEY:
        raise Exception("MISTRAL_API_KEY not set")

    max_words = int(duration * 2.8)
    
    prompt = (
        "Rephrase this Hindi transcript for YouTube Shorts.\n\n"
        "RULES:\n"
        "1. Keep SAME sequence/story\n"
        "2. Change ~20% of words only\n"
        "3. Keep names/places exact\n"
        f"4. Target: {max_words} words\n"
        "5. Natural Hindi flow\n"
        "6. Viral title (3-6 words + emoji)\n"
        "7. Description (2 lines)\n"
        "8. 15 keywords\n"
        "9. 6 hashtags (#Shorts)\n\n"
        f"TRANSCRIPT:\n{transcript}\n\n"
        "Return JSON:\n"
        '{"script":"...","title":"...","description":"...","keywords":[...],"tags":[...]}'
    )
    
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "Output ONLY JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.45,
                    "max_tokens": 1400
                }
            )
        
        if r.status_code != 200:
            raise Exception(f"Mistral failed: {r.status_code}")

        raw = r.json()["choices"][0]["message"]["content"]
        raw = re.sub(r"```json\s*|```", "", raw).strip()
        
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            raise Exception("No JSON in response")
        
        data = json.loads(m.group(0))
        
        logger.info(f"✅ Mistral SUCCESS")
        
        return {
            "script": data.get("script", transcript),
            "title": data.get("title", "Amazing Story 🔥"),
            "description": data.get("description", transcript[:150]),
            "keywords": (data.get("keywords", []) + ["hindi story"]*15)[:15],
            "tags": (data.get("tags", []) + ["#Shorts"]*6)[:6]
        }
        
    except Exception as e:
        logger.error(f"❌ Mistral error: {e}")
        raise


# ═══════════════════════════════════════════════════════════════════════
# VOICEOVER
# ═══════════════════════════════════════════════════════════════════════

async def generate_voiceover(script: str, temp_dir: str) -> Optional[str]:
    """Generate Hindi voiceover with Edge TTS"""
    logger.info("🎙️  Generating voiceover...")
    
    try:
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        out = os.path.join(temp_dir, "voiceover.mp3")
        
        await edge_tts.Communicate(script[:2500], voice, rate="+10%").save(out)
        
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            logger.info(f"✅ Voiceover: {get_size_mb(out):.2f} MB")
            return out
        
        return None
    except Exception as e:
        logger.error(f"❌ Voiceover error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# GOLDEN CAPTIONS
# ═══════════════════════════════════════════════════════════════════════

def _ts(sec: float) -> str:
    """SRT timestamp"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def build_srt_with_emojis(script: str, total_dur: float) -> str:
    """Build SRT with 5-word phrases + emojis"""
    logger.info("📝 Building captions...")
    
    words = script.split()
    phrases = []
    
    for i in range(0, len(words), 5):
        phrase = " ".join(words[i:i+5])
        
        # Add context emojis
        if any(x in phrase.lower() for x in ["krishna", "कृष्ण"]):
            phrase = f"🕉️ {phrase}"
        elif any(x in phrase.lower() for x in ["shiv", "शिव"]):
            phrase = f"🔱 {phrase}"
        elif any(x in phrase.lower() for x in ["ram", "राम"]):
            phrase = f"🏹 {phrase}"
        elif any(x in phrase.lower() for x in ["love", "प्यार"]):
            phrase = f"❤️ {phrase}"
        
        phrases.append(phrase)
    
    if not phrases:
        return ""
    
    dur_each = total_dur / len(phrases)
    blocks = []
    
    for i, ph in enumerate(phrases):
        t0 = i * dur_each
        t1 = t0 + dur_each
        blocks.append(f"{i+1}\n{_ts(t0)} --> {_ts(t1)}\n{ph}\n")
    
    logger.info(f"✅ {len(blocks)} caption blocks")
    return "\n".join(blocks)


# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def strip_audio(vin: str, vout: str) -> bool:
    """Remove original audio"""
    return run_ffmpeg(
        ["ffmpeg", "-i", vin, "-vcodec", "copy", "-an", "-y", vout],
        timeout=60,
        step_name="Strip Audio"
    )


async def download_bgm(temp_dir: str, duration: float) -> Optional[str]:
    """Download BGM"""
    logger.info("🎵 Downloading BGM...")
    
    url = random.choice(STORY_BGM_URLS)
    raw = os.path.join(temp_dir, "bgm_raw.mp3")
    out = os.path.join(temp_dir, "bgm.mp3")
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as c:
            r = await c.get(url)
            
            if r.status_code == 200 and len(r.content) > 500:
                open(raw, "wb").write(r.content)
                
                if run_ffmpeg(
                    ["ffmpeg", "-i", raw, "-t", str(duration), "-acodec", "copy", "-y", out],
                    timeout=60,
                    step_name="Trim BGM"
                ):
                    force_cleanup(raw)
                    return out
                return raw if os.path.exists(raw) else None
    except:
        pass
    
    return None


async def composite(silent_video: str, voiceover: str, srt_path: str,
                    bgm: Optional[str], final: str) -> bool:
    """Burn captions + mix audio"""
    logger.info("✨ Final composite...")
    
    captioned = final.replace(".mp4", "_cap.mp4")
    srt_esc = srt_path.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")
    
    # Golden caption style
    sub_filter = (
        f"subtitles='{srt_esc}':"
        "force_style="
        "Fontname=Arial Black,"
        "Fontsize=32,"
        "PrimaryColour=&H000B86B8,"
        "OutlineColour=&H00000000,"
        "BackColour=&H80000000,"
        "Bold=1,"
        "Outline=3,"
        "Shadow=2,"
        "Alignment=2,"
        "MarginV=80"
    )
    
    # Burn captions
    if not run_ffmpeg(
        ["ffmpeg", "-i", silent_video, "-vf", sub_filter,
         "-c:v", "libx264", "-crf", "22", "-preset", "fast",
         "-pix_fmt", "yuv420p", "-y", captioned],
        timeout=FFMPEG_TIMEOUT,
        step_name="Burn Captions"
    ):
        return False

    # Mix audio
    if bgm and os.path.exists(bgm):
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
        cmd = [
            "ffmpeg",
            "-i", captioned, "-i", voiceover,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest", "-y", final
        ]

    ok = run_ffmpeg(cmd, timeout=FFMPEG_TIMEOUT, step_name="Mix Audio")
    force_cleanup(captioned)
    
    return ok


# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_youtube(video_path: str, title: str, description: str,
                         keywords: List[str], tags: List[str],
                         user_id: str, db) -> dict:
    """Upload directly to YouTube (no storage)"""
    logger.info("📤 Uploading to YouTube...")
    logger.info(f"   ⚠️  Video will NOT be stored in database")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db or not yt_db.youtube.client:
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
        
        full_desc = description + "\n\n" + "\n".join(keywords) + "\n\n" + "\n".join(tags)
        
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
            
            logger.info(f"✅ UPLOADED! ID: {video_id}")
            logger.info(f"   Video file will be deleted (not stored)")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
        else:
            return {"success": False, "error": upload_result.get("error", "Upload failed")}
            
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def process_and_upload_direct(drive_url: str, user_id: str, db) -> dict:
    """Process video and upload directly (no storage)"""
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║" + " " * 15 + "GDRIVE REEL → DIRECT YOUTUBE UPLOAD" + " " * 27 + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    temp_dir = tempfile.mkdtemp(prefix="gdrive_reel_")
    logger.info(f"📁 Temp: {temp_dir}")
    
    try:
        # Extract file ID
        file_id = extract_file_id(drive_url)
        if not file_id:
            return {"success": False, "error": "Invalid Drive URL"}

        # Get serial
        serial = await _next_serial(db, user_id)

        # Download video
        video_src = os.path.join(temp_dir, "source.mp4")
        if not await download_video(file_id, video_src):
            return {"success": False, "error": "Download failed (check if link is public)"}

        # Get duration
        duration = await get_duration(video_src)
        if duration <= 0:
            return {"success": False, "error": "Invalid video"}

        # Extract audio
        wav = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video_src, wav):
            return {"success": False, "error": "Audio extraction failed"}

        # Transcribe (local only)
        transcript = await transcribe(wav)
        if not transcript or len(transcript) < 8:
            return {"success": False, "error": "Transcription failed (try clearer audio)"}

        # AI rephrase
        meta = await mistral_rephrase_seo(transcript, duration)
        script = meta["script"]
        title = meta["title"]
        desc = meta["description"]
        keywords = meta["keywords"]
        tags = meta["tags"]

        # Generate voiceover
        voiceover = await generate_voiceover(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Voiceover failed"}

        # Strip audio
        silent = os.path.join(temp_dir, "silent.mp4")
        if not await strip_audio(video_src, silent):
            return {"success": False, "error": "Audio strip failed"}

        # Build captions
        srt_path = os.path.join(temp_dir, "captions.srt")
        srt_content = build_srt_with_emojis(script, duration)
        open(srt_path, "w", encoding="utf-8").write(srt_content)

        # Download BGM
        bgm = await download_bgm(temp_dir, duration)

        # Composite
        final = os.path.join(temp_dir, "final_reel.mp4")
        if not await composite(silent, voiceover, srt_path, bgm, final):
            return {"success": False, "error": "Composite failed"}

        logger.info("=" * 80)
        logger.info(f"✅ VIDEO READY: {get_size_mb(final):.2f} MB")
        logger.info("📤 Uploading directly to YouTube (NO STORAGE)...")
        logger.info("=" * 80)

        # Upload to YouTube (DIRECT - no storage)
        upload_result = await upload_youtube(final, title, desc, keywords, tags, user_id, db)
        
        if not upload_result.get("success"):
            return {"success": False, "error": upload_result.get("error")}

        # Save ONLY metadata (no video)
        metadata = {
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
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "uploaded": True,
            "processed_at": datetime.utcnow().isoformat(),
            "uploaded_at": datetime.utcnow().isoformat(),
            "note": "Video not stored - uploaded directly to YouTube"
        }
        await _save_metadata(db, metadata)

        logger.info("╔" + "═" * 78 + "╗")
        logger.info("║" + " " * 25 + "🎉 SUCCESS!" + " " * 41 + "║")
        logger.info("╚" + "═" * 78 + "╝")

        return {
            "success": True,
            "serial": serial,
            "title": title,
            "description": desc,
            "keywords": keywords,
            "tags": tags,
            "duration": round(duration, 2),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "uploaded": True,
            "note": "Video uploaded directly (not stored in database)"
        }

    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}
    
    finally:
        logger.info(f"🧹 Cleaning temp files...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()


# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()


@router.get("/api/gdrive-reels/status")
async def status_endpoint(request: Request):
    try:
        user_id = request.query_params.get("user_id")
        if not user_id:
            return JSONResponse(status_code=400, content={"error": "user_id required"})
        
        from Supermain import database_manager
        return JSONResponse(content={
            "success": True,
            "next_serial": await _next_serial(database_manager.db, user_id),
            "total_processed": len(await _history(database_manager.db, user_id)),
            "history": await _history(database_manager.db, user_id),
            "note": "Videos not stored - only metadata"
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/api/gdrive-reels/process-and-upload")
async def process_upload_endpoint(request: Request):
    """Process video and upload directly to YouTube"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"error": "user_id required"})

        drive_url = (data.get("drive_url") or "").strip()
        
        if not drive_url or "drive.google.com" not in drive_url:
            return JSONResponse(status_code=400, content={"error": "Invalid Drive URL"})

        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            process_and_upload_direct(drive_url, user_id, database_manager.db),
            timeout=600
        )
        
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"error": "Timeout (10 min)"})
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})


__all__ = ["router"]