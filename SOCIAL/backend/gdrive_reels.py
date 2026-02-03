"""
gdrive_reels.py – Single-URL Drive Re-Voicer + YouTube Uploader
================================================================
User pastes ONE public Google-Drive file URL in the frontend.
This module extracts the file-ID, downloads the video, and runs:

  1. Download video (public /uc?export=download)
  2. ffprobe  → duration
  3. ffmpeg   → extract mono 16 kHz WAV
  4. Whisper (CLI) → transcript   (Google-STT as fallback)
  5. Mistral  → ~20 % rephrase + title / desc / 15 kw / 6 tags
  6. Edge TTS → voiceover  (random Hindi voice)
  7. ffmpeg   → strip original audio
  8. SRT      → build golden captions
  9. Download free BGM, trim to duration
 10. ffmpeg   → burn captions + mix voice + BGM (0.08 vol)
 11. Save record to MongoDB  (serial auto-increments)

A second endpoint lets the frontend upload any saved reel to YouTube.

NO folder listing.  NO Drive API key.  NO ElevenLabs.
YouTube upload credentials copied from working Pixabay code.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio, logging, os, traceback
import httpx, json, re, random, subprocess
from typing import List, Optional
import tempfile, shutil, gc, base64
from datetime import datetime

logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural", "hi-IN-RaviNeural"]

STORY_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Krishna%20Healing%20Flute%20'%20Bansuri%20background%20music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Ramayana%20'%20SITA%20Emotional%20BGM%20-%20India%20Royalty%20free%20music%20Download.mp3",
]

COLLECTION = "gdrive_reels_tracker"
FFMPEG_TIMEOUT  = 300
DOWNLOAD_TIMEOUT = 180

# ──────────────────────────────────────────────────────────────────────────────
# TINY HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def force_cleanup(*paths):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
    gc.collect()


def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if r.returncode != 0:
            logger.warning(f"ffmpeg stderr: {r.stderr.decode(errors='replace')[-500:]}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg timed out")
        return False
    except Exception as e:
        logger.error(f"ffmpeg: {e}")
        return False


def get_size_mb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except Exception:
        return 0.0


# ──────────────────────────────────────────────────────────────────────────────
# EXTRACT FILE-ID FROM PASTED URL
# ──────────────────────────────────────────────────────────────────────────────

def extract_file_id(url: str) -> Optional[str]:
    """
    Handles every shape Google Drive emits:
      /file/d/<ID>/view?usp=…
      /file/d/<ID>/
      /uc?id=<ID>&export=download
      /open?id=<ID>
    """
    if not url:
        return None
    # Pattern A: /file/d/<ID>/…
    m = re.search(r"/file/d/([A-Za-z0-9_-]{15,})", url)
    if m:
        return m.group(1)
    # Pattern B: ?id=<ID> or &id=<ID>
    m = re.search(r"[?&]id=([A-Za-z0-9_-]{15,})", url)
    if m:
        return m.group(1)
    return None


# ──────────────────────────────────────────────────────────────────────────────
# MONGODB
# ──────────────────────────────────────────────────────────────────────────────

async def _next_serial(db, user_id: str) -> int:
    try:
        doc = await db[COLLECTION].find_one({"user_id": user_id}, sort=[("serial", -1)])
        if doc:
            return doc["serial"] + 1
    except Exception as e:
        logger.warning(f"_next_serial: {e}")
    return 1


async def _save(db, record: dict):
    try:
        await db[COLLECTION].insert_one(record)
        logger.info(f"🗄️  Saved serial={record.get('serial')}")
    except Exception as e:
        logger.warning(f"_save: {e}")


async def _history(db, user_id: str) -> list:
    try:
        rows = []
        async for d in db[COLLECTION].find({"user_id": user_id}).sort("serial", -1).limit(50):
            d.pop("_id", None)
            rows.append(d)
        return rows
    except Exception as e:
        logger.warning(f"_history: {e}")
        return []


async def _mark_uploaded(db, user_id: str, serial: int, video_id: str, video_url: str):
    try:
        await db[COLLECTION].update_one(
            {"user_id": user_id, "serial": serial},
            {"$set": {"video_id": video_id, "video_url": video_url,
                      "uploaded": True, "uploaded_at": datetime.utcnow().isoformat()}}
        )
    except Exception as e:
        logger.warning(f"_mark_uploaded: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# DOWNLOAD
# ──────────────────────────────────────────────────────────────────────────────

async def download_video(file_id: str, dest: str) -> bool:
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as c:
            resp = await c.get(url)

            # Google returns a confirm page for files > 100 MB – extract real link
            if resp.status_code == 200 and len(resp.content) < 50000:
                txt = resp.text
                if "<html" in txt.lower()[:500]:
                    m = re.search(r'href="(/uc\?[^"]*&confirm=[^"]*)"', txt)
                    if m:
                        real_url = "https://drive.google.com" + m.group(1).replace("&amp;", "&")
                        resp = await c.get(real_url)

            if resp.status_code == 200 and len(resp.content) > 2048:
                with open(dest, "wb") as f:
                    f.write(resp.content)
                logger.info(f"⬇️  Downloaded {get_size_mb(dest):.2f} MB")
                return True

            logger.warning(f"Download: status={resp.status_code} size={len(resp.content)}")
    except Exception as e:
        logger.error(f"download_video: {e}")
    return False


# ──────────────────────────────────────────────────────────────────────────────
# DURATION
# ──────────────────────────────────────────────────────────────────────────────

async def get_duration(path: str) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, timeout=30
        )
        return float(r.stdout.decode().strip())
    except Exception as e:
        logger.warning(f"get_duration: {e}")
        return 0.0


# ──────────────────────────────────────────────────────────────────────────────
# AUDIO EXTRACTION + TRANSCRIPTION
# ──────────────────────────────────────────────────────────────────────────────

async def extract_audio(video: str, wav: str) -> bool:
    return run_ffmpeg(["ffmpeg", "-i", video, "-vn", "-acodec", "pcm_s16le",
                       "-ar", "16000", "-ac", "1", "-y", wav], timeout=60)


async def transcribe(wav: str) -> str:
    # ── Whisper CLI ────────────────────────────────────────────────────────
    try:
        out_dir = os.path.dirname(wav)
        r = subprocess.run(
            ["whisper", wav, "--language", "hi", "--model", "small",
             "--output_dir", out_dir, "--output_format", "txt"],
            capture_output=True, timeout=300
        )
        if r.returncode == 0:
            txt = wav.rsplit(".", 1)[0] + ".txt"
            if os.path.exists(txt):
                text = open(txt).read().strip()
                if text:
                    logger.info(f"📝 Whisper: {len(text)} chars")
                    return text
    except FileNotFoundError:
        logger.info("whisper CLI not found – trying Google STT")
    except Exception as e:
        logger.warning(f"whisper: {e}")

    # ── Google Cloud STT fallback ──────────────────────────────────────────
    try:
        with open(wav, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        payload = {
            "config": {"encoding": "LINEAR16", "sampleRateHertz": 16000,
                       "languageCodes": ["hi-IN", "en-IN"], "model": "default"},
            "audio": {"content": b64}
        }
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post("https://speech.googleapis.com/v1/speech:recognize", json=payload)
            if r.status_code == 200:
                text = " ".join(
                    alt["transcript"]
                    for res in r.json().get("results", [])
                    for alt in res.get("alternatives", [])[:1]
                )
                if text:
                    logger.info(f"📝 Google STT: {len(text)} chars")
                    return text
    except Exception as e:
        logger.warning(f"STT fallback: {e}")
    return ""


# ──────────────────────────────────────────────────────────────────────────────
# MISTRAL – rephrase + SEO
# ──────────────────────────────────────────────────────────────────────────────

async def mistral_rephrase_seo(transcript: str, duration: float) -> dict:
    if not MISTRAL_API_KEY:
        raise Exception("MISTRAL_API_KEY not set")

    max_words = int(duration * 2.8)
    prompt = (
        "You are a viral YouTube Shorts editor. A Hindi video has been transcribed.\n"
        "TASKS:\n"
        "1. LIGHTLY rephrase (~20 % word changes). Keep EXACT story order + every character name.\n"
        f"   Word count MUST be ≤ {max_words} (fits {duration:.1f} s at Hindi pace).\n"
        "2. Viral Hinglish title (curiosity + power words + 1-2 emojis).\n"
        "3. 2-line Hinglish description.\n"
        "4. EXACTLY 15 SEO keywords (real YouTube search phrases).\n"
        "5. EXACTLY 6 hashtags (include #Shorts).\n\n"
        f"TRANSCRIPT:\n{transcript}\n\n"
        "Return ONLY valid JSON – no markdown fences:\n"
        '{"script":"…","title":"…","description":"…","keywords":[…],"tags":[…]}'
    )

    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={
                "model": "mistral-large-latest",
                "messages": [
                    {"role": "system", "content": "Output ONLY valid JSON. No markdown fences. No extra text."},
                    {"role": "user",   "content": prompt}
                ],
                "temperature": 0.45,
                "max_tokens": 1400
            }
        )
        if r.status_code != 200:
            raise Exception(f"Mistral {r.status_code}: {r.text[:300]}")

        raw = r.json()["choices"][0]["message"]["content"]
        raw = re.sub(r"```json\s*|```", "", raw).strip()
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            raise Exception("No JSON in Mistral response")
        data = json.loads(m.group(0))

    script   = data.get("script", transcript)
    title    = data.get("title", "Amazing Story 🔥")
    desc     = data.get("description", script[:150])
    keywords = data.get("keywords", [])
    tags     = data.get("tags", [])

    while len(keywords) < 15:
        keywords.append(f"hindi story shorts {len(keywords)}")
    while len(tags) < 6:
        tags.append("#Shorts")

    logger.info(f"🤖 Mistral | title={title} | words={len(script.split())}/{max_words}")
    return {"script": script, "title": title, "description": desc,
            "keywords": keywords[:15], "tags": tags[:6]}


# ──────────────────────────────────────────────────────────────────────────────
# EDGE TTS
# ──────────────────────────────────────────────────────────────────────────────

async def generate_voiceover(script: str, temp_dir: str) -> Optional[str]:
    try:
        import edge_tts
        voice = random.choice(EDGE_TTS_VOICES)
        out   = os.path.join(temp_dir, "voiceover.mp3")
        logger.info(f"🎙️  Edge TTS → {voice}")
        await edge_tts.Communicate(script[:2500], voice, rate="+10%").save(out)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            logger.info(f"✅ Voiceover {get_size_mb(out):.2f} MB")
            return out
        logger.error("Edge TTS file empty")
    except Exception as e:
        logger.error(f"Edge TTS: {e}\n{traceback.format_exc()}")
    return None


# ──────────────────────────────────────────────────────────────────────────────
# SRT BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def _ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def build_srt(script: str, total_dur: float) -> str:
    words   = script.split()
    phrases = [" ".join(words[i:i+5]) for i in range(0, len(words), 5)]
    if not phrases:
        return ""
    dur_each = total_dur / len(phrases)
    blocks = []
    for i, ph in enumerate(phrases):
        t0 = i * dur_each
        blocks.append(f"{i+1}\n{_ts(t0)} --> {_ts(t0 + dur_each)}\n{ph}\n")
    return "\n".join(blocks)


# ──────────────────────────────────────────────────────────────────────────────
# FFMPEG PIPELINES
# ──────────────────────────────────────────────────────────────────────────────

async def strip_audio(vin: str, vout: str) -> bool:
    return run_ffmpeg(["ffmpeg", "-i", vin, "-vcodec", "copy", "-an", "-y", vout], timeout=60)


async def download_bgm(temp_dir: str, duration: float) -> Optional[str]:
    url = random.choice(STORY_BGM_URLS)
    raw = os.path.join(temp_dir, "bgm_raw.mp3")
    out = os.path.join(temp_dir, "bgm.mp3")
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as c:
            r = await c.get(url)
            if r.status_code == 200 and len(r.content) > 500:
                open(raw, "wb").write(r.content)
                if run_ffmpeg(["ffmpeg", "-i", raw, "-t", str(duration),
                               "-acodec", "copy", "-y", out], timeout=60):
                    force_cleanup(raw)
                    logger.info(f"🎵 BGM trimmed {duration:.1f}s")
                    return out
    except Exception as e:
        logger.warning(f"BGM: {e}")
    return None


async def composite(silent_video: str, voiceover: str, srt_path: str,
                    bgm: Optional[str], final: str) -> bool:
    """Step A: burn captions.  Step B: mix audio."""
    captioned = final.replace(".mp4", "_cap.mp4")

    # Escape path for ffmpeg subtitles filter
    srt_esc = srt_path.replace("\\", "\\\\").replace("'", "\\'")
    sub_filter = (
        f"subtitles='{srt_esc}':"
        "force_style="
        "Fontname=Arial,"
        "Fontsize=28,"
        "PrimaryColour=&H00D7FF00,"   # BGR → #FFD700
        "OutlineColour=&H00000000,"
        "BackColour=&H80000000,"
        "Bold=1,"
        "Alignment=2,"
        "MarginL=40,"
        "MarginR=40,"
        "MarginV=60"
    )

    if not run_ffmpeg(["ffmpeg", "-i", silent_video, "-vf", sub_filter,
                       "-c:v", "libx264", "-crf", "22", "-preset", "fast",
                       "-pix_fmt", "yuv420p", "-y", captioned], timeout=FFMPEG_TIMEOUT):
        logger.error("Caption burn failed")
        return False

    # Audio mix
    if bgm and os.path.exists(bgm):
        cmd = ["ffmpeg",
               "-i", captioned, "-i", voiceover, "-i", bgm,
               "-filter_complex",
               "[1:a]volume=1.0[v];[2:a]volume=0.08[m];[v][m]amix=inputs=2:duration=first[a]",
               "-map", "0:v", "-map", "[a]",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
               "-shortest", "-y", final]
    else:
        cmd = ["ffmpeg",
               "-i", captioned, "-i", voiceover,
               "-map", "0:v", "-map", "1:a",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
               "-shortest", "-y", final]

    ok = run_ffmpeg(cmd, timeout=FFMPEG_TIMEOUT)
    force_cleanup(captioned)
    if ok:
        logger.info(f"✅ Final video {get_size_mb(final):.2f} MB")
    return ok


# ──────────────────────────────────────────────────────────────────────────────
# YOUTUBE UPLOAD (EXACT PIXABAY WORKING LOGIC)
# ──────────────────────────────────────────────────────────────────────────────

async def upload_youtube(video_path: str, title: str, description: str,
                         keywords: List[str], tags: List[str],
                         user_id: str, db) -> dict:
    """Upload to YouTube using Viral Pixel's exact working logic - COPIED FROM PIXABAY"""
    try:
        logger.info("📤 Connecting to YouTube database...")
        
        # EXACT IMPORT FROM PIXABAY
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            return {"success": False, "error": "YouTube database not available"}
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        logger.info(f"📤 Fetching YouTube credentials for user: {user_id}")
        
        # EXACT CREDENTIAL FETCH FROM PIXABAY
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            return {"success": False, "error": "YouTube credentials not found"}
        
        # EXACT CREDENTIAL STRUCTURE FROM PIXABAY
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
        
        # Build full description with keywords and tags
        full_desc = description + "\n\n" + "\n".join(keywords) + "\n\n" + "\n".join(tags)
        
        logger.info("📤 Uploading to YouTube...")
        
        # EXACT UPLOAD CALL FROM PIXABAY
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
            
            logger.info(f"✅ Video uploaded successfully!")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
        
        return {
            "success": False,
            "error": upload_result.get("error", "Upload failed")
        }
            
    except Exception as e:
        logger.error(f"❌ YouTube upload error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

async def process_video(drive_url: str, user_id: str, db) -> dict:
    """Full pipeline for one pasted Drive URL. Saves to MongoDB. No YT upload."""
    temp_dir = tempfile.mkdtemp(prefix="gdrive_reel_")
    try:
        # 1. Parse file-ID
        file_id = extract_file_id(drive_url)
        if not file_id:
            return {"success": False, "error": "Could not extract file ID. Please paste a valid public Google Drive file link."}
        logger.info(f"📎 File ID: {file_id}")

        # 2. Serial
        serial = await _next_serial(db, user_id)
        logger.info(f"🔢 Serial: {serial}")

        # 3. Download
        video_src = os.path.join(temp_dir, "source.mp4")
        if not await download_video(file_id, video_src):
            return {"success": False, "error": "Download failed. Make sure the link is public (Anyone with link can view)."}

        # 4. Duration
        duration = await get_duration(video_src)
        if duration <= 0:
            return {"success": False, "error": "Could not read video duration (ffprobe)."}
        logger.info(f"⏱️  Duration: {duration:.2f}s")

        # 5. Extract audio
        wav = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video_src, wav):
            return {"success": False, "error": "Audio extraction failed."}

        # 6. Transcribe
        transcript = await transcribe(wav)
        if not transcript or len(transcript.strip()) < 8:
            return {"success": False, "error": "Transcription empty or too short. Video must have audible speech."}
        logger.info(f"📝 Transcript: {len(transcript)} chars")

        # 7. Mistral
        meta = await mistral_rephrase_seo(transcript, duration)
        script, title, desc = meta["script"], meta["title"], meta["description"]
        keywords, tags = meta["keywords"], meta["tags"]

        # 8. Edge TTS
        voiceover = await generate_voiceover(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Edge TTS voiceover generation failed."}

        # 9. Strip audio
        silent = os.path.join(temp_dir, "silent.mp4")
        if not await strip_audio(video_src, silent):
            return {"success": False, "error": "Stripping original audio failed."}

        # 10. SRT
        srt_path = os.path.join(temp_dir, "captions.srt")
        open(srt_path, "w", encoding="utf-8").write(build_srt(script, duration))

        # 11. BGM
        bgm = await download_bgm(temp_dir, duration)

        # 12. Composite
        final = os.path.join(temp_dir, "final_reel.mp4")
        if not await composite(silent, voiceover, srt_path, bgm, final):
            return {"success": False, "error": "Final composite failed."}

        # 13. Save to MongoDB
        record = {
            "user_id": user_id, "serial": serial,
            "drive_url": drive_url, "drive_file_id": file_id,
            "transcript": transcript, "ai_script": script,
            "title": title, "description": desc,
            "keywords": keywords, "tags": tags,
            "duration": round(duration, 2),
            "uploaded": False, "video_id": None, "video_url": None,
            "processed_at": datetime.utcnow().isoformat(),
        }
        await _save(db, record)
        logger.info(f"🎉 Serial #{serial} done")

        return {
            "success": True, "serial": serial,
            "title": title, "description": desc,
            "keywords": keywords, "tags": tags,
            "duration": round(duration, 2),
            "ai_script": script, "transcript": transcript,
            "uploaded": False,
        }
    except Exception as e:
        logger.error(f"❌ process_video: {e}\n{traceback.format_exc()}")
        return {"success": False, "error": str(e)}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()


async def reprocess_and_upload(serial: int, doc: dict, user_id: str, db) -> dict:
    """Re-download + re-process the saved Drive URL, then upload to YouTube."""
    temp_dir = tempfile.mkdtemp(prefix="gdrive_upload_")
    try:
        file_id   = doc["drive_file_id"]
        video_src = os.path.join(temp_dir, "source.mp4")

        if not await download_video(file_id, video_src):
            return {"success": False, "error": "Re-download failed."}

        duration  = await get_duration(video_src)
        script    = doc["ai_script"]
        title     = doc["title"]
        desc      = doc["description"]
        keywords  = doc["keywords"]
        tags      = doc["tags"]

        # voiceover
        voiceover = await generate_voiceover(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Voiceover failed on re-process."}

        # strip + captions + bgm + composite
        silent = os.path.join(temp_dir, "silent.mp4")
        await strip_audio(video_src, silent)

        srt_path = os.path.join(temp_dir, "captions.srt")
        open(srt_path, "w", encoding="utf-8").write(build_srt(script, duration))

        bgm   = await download_bgm(temp_dir, duration)
        final = os.path.join(temp_dir, "final_reel.mp4")
        if not await composite(silent, voiceover, srt_path, bgm, final):
            return {"success": False, "error": "Composite failed on re-process."}

        # Upload (using exact Pixabay credentials logic)
        up = await upload_youtube(final, title, desc, keywords, tags, user_id, db)
        if not up.get("success"):
            return {"success": False, "error": up.get("error", "Upload failed")}

        await _mark_uploaded(db, user_id, serial, up["video_id"], up["video_url"])
        logger.info(f"📤 Serial #{serial} uploaded: {up['video_url']}")
        return {"success": True, "serial": serial,
                "video_id": up["video_id"], "video_url": up["video_url"]}

    except Exception as e:
        logger.error(f"reprocess_and_upload: {e}\n{traceback.format_exc()}")
        return {"success": False, "error": str(e)}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()


# ──────────────────────────────────────────────────────────────────────────────
# API ROUTES
# ──────────────────────────────────────────────────────────────────────────────

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
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request):
    """Body: { user_id, drive_url }  – downloads, processes, saves. No YT upload."""
    try:
        data    = await request.json()
        user_id = data.get("user_id")
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})

        drive_url = (data.get("drive_url") or "").strip()
        if not drive_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "drive_url is required"})
        if "drive.google.com" not in drive_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Must be a Google Drive URL"})

        from Supermain import database_manager
        result = await asyncio.wait_for(
            process_video(drive_url, user_id, database_manager.db),
            timeout=600
        )
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timed out (10 min)"})
    except Exception as e:
        logger.error(f"process_endpoint: {e}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.post("/api/gdrive-reels/upload-to-youtube")
async def upload_endpoint(request: Request):
    """Body: { user_id, serial }  – re-processes the saved reel and uploads."""
    try:
        data    = await request.json()
        user_id = data.get("user_id")
        serial  = data.get("serial")
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})
        if serial is None:
            return JSONResponse(status_code=400, content={"success": False, "error": "serial required"})

        from Supermain import database_manager
        doc = await database_manager.db[COLLECTION].find_one({"user_id": user_id, "serial": serial})
        if not doc:
            return JSONResponse(status_code=404, content={"success": False, "error": f"Serial {serial} not found"})
        if doc.get("uploaded"):
            return JSONResponse(content={"success": True, "message": "Already uploaded",
                                         "video_id": doc.get("video_id"), "video_url": doc.get("video_url")})

        result = await asyncio.wait_for(
            reprocess_and_upload(serial, doc, user_id, database_manager.db),
            timeout=600
        )
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Upload timed out"})
    except Exception as e:
        logger.error(f"upload_endpoint: {e}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


__all__ = ["router"]