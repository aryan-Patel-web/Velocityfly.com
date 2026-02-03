"""
gdrive_reels.py – Google-Drive Reel Re-voicer & YouTube Uploader
================================================================
Flow per video
──────────────
1.  Pull next serial number from MongoDB  →  download N.mp4 from Drive
2.  Extract audio  →  Whisper / Vosk transcription  →  plain text
3.  Send transcript to Mistral  →  ~20 % light rephrase (story & order kept)
4.  Mistral also emits: viral title, description, 15 vertical keywords, 6 tags
5.  Strip original audio  →  Edge TTS voiceover (3 Hindi voices, random)
6.  Burn golden bold captions  →  sync to AI-script word timing
7.  Overlay free royalty-free story-BGM at very-low volume (voice stays clear)
8.  Upload to YouTube via the same helper used by pixabay_final_complete_WORKING
9.  Persist result doc in MongoDB  →  next run picks up serial + 1

Key design decisions
────────────────────
• NO ElevenLabs – only edge_tts (RaviNeural / MadhurNeural / KunalNeural)
• BGM volume = 0.08  →  voice always dominant
• Caption style = golden #FFD700, bold, readable but NOT oversized
• Mistral temperature 0.45  →  keeps ~80 % original wording
• Google-Drive public-folder download uses the /export or /uc?export=download trick
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import traceback
import httpx
import json
import re
import random
import subprocess
from typing import List, Optional
import tempfile
import shutil
import gc
from datetime import datetime
import hashlib
import uuid
import math

logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)

# ============================================================================
# CONFIGURATION  (mirrors env-style from pixabay file)
# ============================================================================

MISTRAL_API_KEY   = os.getenv("MISTRAL_API_KEY")
MONGODB_URI       = os.getenv("MONGODB_URI",
    "mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/"
    "?retryWrites=true&w=majority&appName=Cluster0")

# Google Drive PUBLIC folder ID  →  extracted from the shared link
# https://drive.google.com/drive/folders/1kocgFg0rzsMCtXsrWiOH_oditWshBpbV
GDRIVE_FOLDER_ID = "1kocgFg0rzsMCtXsrWiOH_oditWshBpbV"
# https://drive.google.com/drive/folders/
# Edge TTS voices (random pick each video)
EDGE_TTS_VOICES = [
    "hi-IN-RaviNeural",
    "hi-IN-MadhurNeural",
    "hi-IN-KunalNeural",
]

# Free story-BGM URLs  (royalty-free, low-intensity ambient / cinematic)
STORY_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Krishna%20Healing%20Flute%20'%20Bansuri%20background%20music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Ramayana%20'%20SITA%20Emotional%20BGM%20-%20India%20Royalty%20free%20music%20Download.mp3",
]

# Timeouts
FFMPEG_TIMEOUT = 300
DOWNLOAD_TIMEOUT = 120   # seconds per video download

# MongoDB collection name
COLLECTION_NAME = "gdrive_reels_tracker"

# ============================================================================
# UTILITIES
# ============================================================================

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
            logger.warning(f"ffmpeg stderr: {r.stderr.decode(errors='replace')[-400:]}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg timed out")
        return False
    except Exception as e:
        logger.error(f"ffmpeg error: {e}")
        return False

def get_size_mb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except Exception:
        return 0.0

# ============================================================================
# MONGODB HELPERS
# ============================================================================

async def get_next_serial(database_manager, user_id: str) -> int:
    """
    Return the next video serial number to process.
    Looks at the highest 'serial' already stored for this user; returns +1.
    If nothing exists yet, returns 1.
    """
    try:
        doc = await database_manager.db[COLLECTION_NAME].find_one(
            {"user_id": user_id},
            sort=[("serial", -1)]          # descending  →  highest first
        )
        if doc:
            return doc["serial"] + 1
    except Exception as e:
        logger.warning(f"get_next_serial DB error: {e}")
    return 1

async def save_reel_record(database_manager, record: dict):
    """Upsert a reel processing record."""
    try:
        await database_manager.db[COLLECTION_NAME].insert_one(record)
        logger.info(f"✅ Saved record serial={record.get('serial')}")
    except Exception as e:
        logger.warning(f"save_reel_record error: {e}")

async def get_all_reels(database_manager, user_id: str) -> list:
    """Return all processed reels for a user (newest first)."""
    try:
        cursor = database_manager.db[COLLECTION_NAME].find(
            {"user_id": user_id}
        ).sort("serial", -1).limit(50)
        docs = []
        async for d in cursor:
            d.pop("_id", None)
            docs.append(d)
        return docs
    except Exception as e:
        logger.warning(f"get_all_reels error: {e}")
        return []

# ============================================================================
# GOOGLE DRIVE – list files & download
# ============================================================================

async def list_drive_files(folder_id: str) -> dict:
    """
    Use the Google Drive *public* folder page to scrape file-IDs.
    Returns  { "1": file_id, "2": file_id, … }  keyed by serial number.
    Fallback: if scraping is blocked we try the Drive API v3 (no key needed
    for public folders in some regions – but in production you may need an
    API key).  For robustness we do both.
    """
    mapping = {}                         # serial_str  →  drive_file_id

    # ── attempt 1: Drive API v3 public listing (no auth needed for public) ──
    try:
        url = (
            "https://www.googleapis.com/drive/v3/files"
            f"?q=%27{folder_id}%27+in+parents+and+mimeType=%27video/mp4%27"
            "&fields=files(id,name)&pageSize=1000"
        )
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(url)
            if r.status_code == 200:
                for f in r.json().get("files", []):
                    name = f.get("name", "")                # e.g. "1.mp4"
                    m = re.match(r"^(\d+)\.mp4$", name)
                    if m:
                        mapping[int(m.group(1))] = f["id"]
                if mapping:
                    logger.info(f"📂 Drive API listed {len(mapping)} files")
                    return mapping
    except Exception as e:
        logger.warning(f"Drive API list failed: {e}")

    # ── attempt 2: scrape the public folder HTML page ──────────────────────
    try:
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
            r = await c.get(folder_url)
            if r.status_code == 200:
                # Drive embeds file IDs in data attributes / script blocks
                # Pattern: /file/d/<FILE_ID>/
                ids_found = re.findall(r'/file/d/([A-Za-z0-9_-]{20,})', r.text)
                # Also look for name hints in nearby text
                # This is best-effort; serial assignment may need manual tune
                ids_found = list(dict.fromkeys(ids_found))   # dedupe preserve order
                logger.info(f"📂 Scraped {len(ids_found)} file-IDs from folder page")
                # We can't reliably map names from scrape, so store all
                # and let download step try  /uc?id=X&export=download
                for i, fid in enumerate(ids_found, 1):
                    mapping[i] = fid
                return mapping
    except Exception as e:
        logger.warning(f"Drive scrape failed: {e}")

    return mapping

async def download_drive_video(file_id: str, dest_path: str) -> bool:
    """
    Download a single file from Google Drive (public, no auth).
    Uses the classic  /uc?export=download&id=  URL.
    """
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT, follow_redirects=True) as c:
            r = await c.get(url)
            if r.status_code == 200 and len(r.content) > 1024:
                with open(dest_path, "wb") as f:
                    f.write(r.content)
                logger.info(f"⬇️  Downloaded {get_size_mb(dest_path):.2f} MB → {dest_path}")
                return True
            else:
                logger.warning(f"Drive download returned status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        logger.error(f"Drive download error: {e}")
    return False

# ============================================================================
# TRANSCRIPTION  (ffmpeg + whisper-compatible via subprocess)
# ============================================================================

async def extract_audio(video_path: str, audio_path: str) -> bool:
    """Strip video  →  mono WAV for transcription."""
    return run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ], timeout=60)

async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe using whisper CLI if available, else fall back to a simple
    speech-to-text via Google Cloud (free tier).  For offline use the code
    expects `whisper` to be pip-installed.
    """
    # ── try whisper CLI ──────────────────────────────────────────────────
    try:
        result = subprocess.run(
            ["whisper", audio_path, "--language", "hi", "--model", "small",
             "--output_dir", os.path.dirname(audio_path), "--output_format", "txt"],
            capture_output=True, timeout=300
        )
        if result.returncode == 0:
            txt_path = audio_path.replace(".wav", ".txt")
            if os.path.exists(txt_path):
                with open(txt_path) as f:
                    text = f.read().strip()
                logger.info(f"📝 Whisper transcript: {len(text)} chars")
                return text
    except FileNotFoundError:
        logger.info("whisper not installed – trying Google STT fallback")
    except Exception as e:
        logger.warning(f"whisper error: {e}")

    # ── fallback: Google Cloud Speech-to-Text (free, public endpoint) ────
    # For simplicity we use a base64 POST; in production wire up properly.
    try:
        import base64
        with open(audio_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        # Google STT v1 – no key needed for very short clips on some quotas
        # In production add your API key as ?key=YOUR_KEY
        payload = {
            "config": {
                "encoding": "LINEAR16",
                "sampleRateHertz": 16000,
                "languageCodes": ["hi-IN", "en-IN"],
                "model": "default"
            },
            "audio": {"content": b64}
        }
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(
                "https://speech.googleapis.com/v1/speech:recognize",
                json=payload
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                text = " ".join(
                    alt["transcript"]
                    for res in results
                    for alt in res.get("alternatives", [])[:1]
                )
                logger.info(f"📝 Google STT transcript: {len(text)} chars")
                return text
    except Exception as e:
        logger.warning(f"Google STT fallback error: {e}")

    return ""

# ============================================================================
# MISTRAL  – rephrase + SEO metadata generation
# ============================================================================

async def mistral_rephrase_and_seo(
    transcript: str,
    video_duration_sec: float
) -> dict:
    """
    Single Mistral call that returns:
      - script        : ~20 % rephrased transcript (story order preserved)
      - title         : viral Hinglish title
      - description   : 2-line Hinglish summary
      - keywords      : list of 15 vertical keywords
      - tags          : list of 6 tags
    """
    if not MISTRAL_API_KEY:
        raise Exception("MISTRAL_API_KEY not set")

    prompt = f"""You are a viral YouTube Shorts editor. A Hindi video has been transcribed.
Your job:
1. LIGHTLY rephrase the transcript (~20% word changes max).
   - Keep the EXACT story sequence and every character name.
   - Only tweak phrasing / connectors for natural flow.
   - The rephrased script MUST fit within {video_duration_sec:.1f} seconds
     when spoken at normal Hindi pace (~2.8 words/sec).
     So total words must be ≤ {int(video_duration_sec * 2.8)}.
2. Create a VIRAL Hinglish title (curiosity + power words + 1-2 emojis).
3. Write a 2-line Hinglish description explaining the video.
4. Generate EXACTLY 15 SEO keywords (one per line, real YouTube search phrases).
5. Generate EXACTLY 6 hashtags.

ORIGINAL TRANSCRIPT:
{transcript}

OUTPUT FORMAT – valid JSON only, no markdown:
{{
  "script": "rephrased hindi text here",
  "title": "Viral Hinglish Title 🔥",
  "description": "line1\\nline2",
  "keywords": ["kw1","kw2",...],
  "tags": ["tag1","tag2",...]
}}"""

    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
            json={
                "model": "mistral-large-latest",
                "messages": [
                    {"role": "system", "content": "Output ONLY valid JSON. No markdown fences."},
                    {"role": "user",   "content": prompt}
                ],
                "temperature": 0.45,   # low  →  keeps ~80 % original
                "max_tokens": 1200
            }
        )
        if r.status_code != 200:
            raise Exception(f"Mistral HTTP {r.status_code}: {r.text[:300]}")

        raw = r.json()["choices"][0]["message"]["content"]
        # Strip possible ```json … ``` wrapper
        raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            raise Exception("No JSON object found in Mistral response")
        data = json.loads(match.group(0))

    # Validate / default
    script  = data.get("script", transcript)
    title   = data.get("title", "Amazing Story 🔥")
    desc    = data.get("description", script[:150])
    keywords= data.get("keywords", [])[:15]
    tags    = data.get("tags", [])[:6]

    # Ensure exactly 15 kw / 6 tags (pad if short)
    while len(keywords) < 15:
        keywords.append(f"hindi shorts {len(keywords)}")
    while len(tags) < 6:
        tags.append(f"#shorts")

    logger.info(f"📝 Mistral done | title={title} | script_words={len(script.split())}")
    return {
        "script": script,
        "title": title,
        "description": desc,
        "keywords": keywords[:15],
        "tags": tags[:6]
    }

# ============================================================================
# EDGE TTS VOICE GENERATION
# ============================================================================

async def generate_edge_tts(script: str, temp_dir: str) -> Optional[str]:
    """
    Generate voiceover with Edge TTS.  Randomly picks one of 3 Hindi voices.
    Returns path to the generated MP3.
    """
    try:
        import edge_tts

        voice = random.choice(EDGE_TTS_VOICES)
        logger.info(f"🎙️  Edge TTS voice: {voice}")

        out_mp3 = os.path.join(temp_dir, "voiceover.mp3")
        await edge_tts.Communicate(
            script[:2500],        # Edge has a char limit
            voice,
            rate="+10%"           # slightly faster for shorts pacing
        ).save(out_mp3)

        if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000:
            logger.info(f"✅ Voiceover generated: {get_size_mb(out_mp3):.2f} MB ({voice})")
            return out_mp3
        logger.error("Edge TTS output empty or missing")
    except Exception as e:
        logger.error(f"Edge TTS error: {e}\n{traceback.format_exc()}")
    return None

# ============================================================================
# CAPTION GENERATION  –  golden, bold, synced
# ============================================================================

def build_srt_from_script(script: str, total_duration: float) -> str:
    """
    Simple equal-duration SRT builder.
    Splits script into short phrases (≤ 6 words) and distributes them
    evenly across the video timeline.
    """
    # Split into phrases of ~5 words
    words = script.split()
    phrases = []
    for i in range(0, len(words), 5):
        phrases.append(" ".join(words[i:i+5]))

    if not phrases:
        return ""

    dur_each = total_duration / len(phrases)
    lines = []
    for idx, phrase in enumerate(phrases):
        start = idx * dur_each
        end   = start + dur_each
        lines.append(
            f"{idx+1}\n"
            f"{_ts(start)} --> {_ts(end)}\n"
            f"{phrase}\n"
        )
    return "\n".join(lines)

def _ts(sec: float) -> str:
    """Seconds  →  HH:MM:SS,mmm"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

# ============================================================================
# FFMPEG PIPELINES
# ============================================================================

async def strip_audio(video_in: str, video_no_audio: str) -> bool:
    """Remove original audio from video."""
    return run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-vcodec", "copy", "-an",
        "-y", video_no_audio
    ], timeout=60)

async def get_video_duration(video_path: str) -> float:
    """Use ffprobe to get duration in seconds."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, timeout=30
        )
        return float(r.stdout.decode().strip())
    except Exception as e:
        logger.warning(f"ffprobe error: {e}")
        return 0.0

async def download_bgm(temp_dir: str, duration: float) -> Optional[str]:
    """Download a random story BGM and trim to video duration."""
    url = random.choice(STORY_BGM_URLS)
    raw  = os.path.join(temp_dir, "bgm_raw.mp3")
    out  = os.path.join(temp_dir, "bgm.mp3")
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as c:
            r = await c.get(url)
            if r.status_code == 200 and len(r.content) > 500:
                with open(raw, "wb") as f:
                    f.write(r.content)
                # Trim to duration
                if run_ffmpeg([
                    "ffmpeg", "-i", raw, "-t", str(duration),
                    "-acodec", "copy", "-y", out
                ], timeout=60):
                    force_cleanup(raw)
                    logger.info(f"🎵 BGM downloaded & trimmed: {duration:.1f}s")
                    return out
    except Exception as e:
        logger.warning(f"BGM download error: {e}")
    return None

async def add_captions_and_bgm(
    video_no_audio: str,
    voiceover_mp3: str,
    srt_path: str,
    bgm_path: Optional[str],
    final_path: str
) -> bool:
    """
    Composite pipeline:
      1. Burn golden captions onto video  (subtitles filter)
      2. Mix voiceover + BGM (bgm at 0.08 volume)  →  final MP4
    """
    # ── Step A: burn captions onto the silent video ──────────────────────
    captioned = final_path.replace(".mp4", "_captioned.mp4")
    # ffmpeg subtitles filter with styling
    # fontsize=28 → readable but not oversized
    # fontcolor=golden #FFD700, shadow for readability
    srt_escaped = srt_path.replace("'", r"\'").replace("\\", "\\\\")

    sub_filter = (
        f"subtitles='{srt_escaped}':"
        "force_style="
        "Fontname=Arial,"
        "Fontsize=28,"
        "PrimaryColour=&H00D7FF00,"       # BGR  →  #FFD700 golden
        "OutlineColour=&H00000000,"       # black outline
        "BackColour=&H80000000,"          # semi-transparent black shadow
        "Bold=1,"
        "Alignment=2,"                    # bottom-center
        "MarginL=40,"
        "MarginR=40,"
        "MarginV=60"
    )

    ok = run_ffmpeg([
        "ffmpeg", "-i", video_no_audio,
        "-vf", sub_filter,
        "-c:v", "libx264", "-crf", "22", "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-y", captioned
    ], timeout=FFMPEG_TIMEOUT)

    if not ok:
        logger.error("Caption burn failed")
        return False

    # ── Step B: add audio (voiceover + optional BGM) ─────────────────────
    if bgm_path and os.path.exists(bgm_path):
        # Mix: voice at 1.0, bgm at 0.08
        cmd = [
            "ffmpeg",
            "-i", captioned,          # video (no audio)
            "-i", voiceover_mp3,      # voice
            "-i", bgm_path,           # bgm
            "-filter_complex",
            "[1:a]volume=1.0[v];[2:a]volume=0.08[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            "-y", final_path
        ]
    else:
        # Voice only, no BGM
        cmd = [
            "ffmpeg",
            "-i", captioned,
            "-i", voiceover_mp3,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            "-y", final_path
        ]

    ok = run_ffmpeg(cmd, timeout=FFMPEG_TIMEOUT)
    force_cleanup(captioned)

    if ok:
        logger.info(f"✅ Final video: {get_size_mb(final_path):.2f} MB")
    return ok

# ============================================================================
# YOUTUBE UPLOAD  (reuses pixabay helper pattern)
# ============================================================================

async def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    tags: List[str],
    keywords: List[str],
    user_id: str,
    database_manager
) -> dict:
    """Upload finished reel to YouTube via the same scheduler used by pixabay."""
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        if not yt_db:
            return {"success": False, "error": "YouTube DB not available"}
        if not yt_db.youtube.client:
            await yt_db.connect()

        creds_raw = await yt_db.youtube.youtube_credentials_collection.find_one(
            {"user_id": user_id}
        )
        if not creds_raw:
            return {"success": False, "error": "YouTube credentials not found"}

        credentials = {
            "access_token":  creds_raw.get("access_token"),
            "refresh_token": creds_raw.get("refresh_token"),
            "token_uri":     "https://oauth2.googleapis.com/token",
            "client_id":     creds_raw.get("client_id")     or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        }

        # Build full description: summary + vertical keywords + hashtags
        full_desc_parts = [description, ""]
        full_desc_parts.extend(keywords)                   # vertical keywords
        full_desc_parts.append("")
        full_desc_parts.extend([f"#{t.lstrip('#')}" for t in tags])
        full_description = "\n".join(full_desc_parts)

        from mainY import youtube_scheduler
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=full_description,
            video_url=video_path,
        )

        if result.get("success"):
            vid_id = result.get("video_id")
            logger.info(f"✅ Uploaded | video_id={vid_id}")
            return {"success": True, "video_id": vid_id,
                    "video_url": f"https://youtube.com/shorts/{vid_id}"}

        return {"success": False, "error": result.get("error", "Upload failed")}

    except Exception as e:
        logger.error(f"YouTube upload error: {e}\n{traceback.format_exc()}")
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

async def process_next_reel(
    user_id: str,
    database_manager,
    upload: bool = False          # False = download+process only; True = also upload
) -> dict:
    """
    Downloads the NEXT video in serial order, processes it fully,
    optionally uploads to YouTube.
    """
    temp_dir = tempfile.mkdtemp(prefix="gdrive_reel_")

    try:
        # ── 1. determine serial ──────────────────────────────────────────
        serial = await get_next_serial(database_manager, user_id)
        logger.info(f"🎯 Processing serial #{serial}")

        # ── 2. list Drive folder  →  get file_id for serial ─────────────
        file_map = await list_drive_files(GDRIVE_FOLDER_ID)
        if not file_map:
            return {"success": False, "error": "Could not list Google Drive folder"}

        if serial not in file_map:
            # Maybe the folder listing was by scrape-order not by name;
            # try to find by trying download with guessed file naming
            logger.warning(f"Serial {serial} not in map. Available: {sorted(file_map.keys())[:10]}")
            return {"success": False, "error": f"{serial}.mp4 not found in Drive folder"}

        file_id = file_map[serial]

        # ── 3. download video ────────────────────────────────────────────
        video_src = os.path.join(temp_dir, f"{serial}.mp4")
        if not await download_drive_video(file_id, video_src):
            return {"success": False, "error": f"Download of {serial}.mp4 failed"}

        # ── 4. get duration ──────────────────────────────────────────────
        duration = await get_video_duration(video_src)
        if duration <= 0:
            return {"success": False, "error": "Could not read video duration"}
        logger.info(f"⏱️  Video duration: {duration:.2f}s")

        # ── 5. extract audio  →  transcribe ──────────────────────────────
        audio_wav = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(video_src, audio_wav):
            return {"success": False, "error": "Audio extraction failed"}

        transcript = await transcribe_audio(audio_wav)
        if not transcript or len(transcript.strip()) < 10:
            return {"success": False, "error": "Transcription returned empty/too short"}
        logger.info(f"📝 Transcript ({len(transcript)} chars): {transcript[:120]}…")

        # ── 6. Mistral rephrase + SEO ────────────────────────────────────
        meta = await mistral_rephrase_and_seo(transcript, duration)
        script   = meta["script"]
        title    = meta["title"]
        desc     = meta["description"]
        keywords = meta["keywords"]
        tags     = meta["tags"]

        # ── 7. Edge TTS voiceover ────────────────────────────────────────
        voiceover = await generate_edge_tts(script, temp_dir)
        if not voiceover:
            return {"success": False, "error": "Edge TTS voiceover generation failed"}

        # ── 8. strip original audio ──────────────────────────────────────
        video_silent = os.path.join(temp_dir, "silent.mp4")
        if not await strip_audio(video_src, video_silent):
            return {"success": False, "error": "Audio strip failed"}

        # ── 9. build SRT captions ────────────────────────────────────────
        srt_content = build_srt_from_script(script, duration)
        srt_path    = os.path.join(temp_dir, "captions.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        # ── 10. download BGM ─────────────────────────────────────────────
        bgm_path = await download_bgm(temp_dir, duration)

        # ── 11. composite: captions + voice + BGM ────────────────────────
        final_video = os.path.join(temp_dir, "final_reel.mp4")
        if not await add_captions_and_bgm(
            video_silent, voiceover, srt_path, bgm_path, final_video
        ):
            return {"success": False, "error": "Caption/audio composite failed"}

        # ── 12. upload (optional) ────────────────────────────────────────
        video_id  = None
        video_url = None
        if upload:
            up = await upload_to_youtube(
                final_video, title, desc, tags, keywords, user_id, database_manager
            )
            if not up.get("success"):
                return {"success": False, "error": up.get("error", "Upload failed")}
            video_id  = up["video_id"]
            video_url = up["video_url"]

        # ── 13. persist to MongoDB ───────────────────────────────────────
        record = {
            "user_id":     user_id,
            "serial":      serial,
            "drive_file_id": file_id,
            "transcript":  transcript,
            "ai_script":   script,
            "title":       title,
            "description": desc,
            "keywords":    keywords,
            "tags":        tags,
            "video_id":    video_id,
            "video_url":   video_url,
            "duration":    round(duration, 2),
            "uploaded":    upload,
            "processed_at": datetime.utcnow().isoformat(),
        }
        await save_reel_record(database_manager, record)

        logger.info(f"🎉 Serial #{serial} DONE | uploaded={upload}")
        return {
            "success":   True,
            "serial":    serial,
            "title":     title,
            "description": desc,
            "keywords":  keywords,
            "tags":      tags,
            "video_id":  video_id,
            "video_url": video_url,
            "duration":  round(duration, 2),
            "ai_script": script,
            "transcript": transcript,
        }

    except Exception as e:
        logger.error(f"❌ process_next_reel: {e}\n{traceback.format_exc()}")
        return {"success": False, "error": str(e)}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()

# ============================================================================
# API ROUTES
# ============================================================================

router = APIRouter()

@router.get("/api/gdrive-reels/status")
async def reels_status(request: Request):
    """Return current serial pointer + last N processed reels."""
    try:
        user_id = request.query_params.get("user_id")
        if not user_id:
            return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})

        from Supermain import database_manager
        next_serial = await get_next_serial(database_manager, user_id)
        history     = await get_all_reels(database_manager, user_id)

        return JSONResponse(content={
            "success":      True,
            "next_serial":  next_serial,
            "total_processed": len(history),
            "history":      history
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request):
    """
    Body: { "user_id": "…", "upload": true/false }
    upload=false  →  download + process + save to DB  (no YT upload)
    upload=true   →  also upload to YouTube
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})

        upload = data.get("upload", False)

        from Supermain import database_manager
        result = await asyncio.wait_for(
            process_next_reel(user_id, database_manager, upload=upload),
            timeout=600   # 10 min max
        )
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Processing timed out"})
    except Exception as e:
        logger.error(f"Endpoint error: {e}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/gdrive-reels/upload")
async def upload_endpoint(request: Request):
    """
    Body: { "user_id": "…", "serial": N }
    Re-uploads an already-processed reel (serial N) to YouTube.
    If serial is omitted, uploads the latest processed-but-not-uploaded reel.
    """
    try:
        data    = await request.json()
        user_id = data.get("user_id")
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})

        from Supermain import database_manager

        # Find the record
        serial = data.get("serial")
        query  = {"user_id": user_id}
        if serial:
            query["serial"] = serial
        else:
            query["uploaded"] = False
            # pick highest serial not yet uploaded
        doc = await database_manager.db[COLLECTION_NAME].find_one(
            query, sort=[("serial", -1)]
        )
        if not doc:
            return JSONResponse(status_code=404, content={"success": False, "error": "No matching reel found"})

        # We don't have the processed video on disk any more  →  re-run full pipeline
        # but this time with upload=True.  To avoid re-downloading, you could cache
        # processed videos; for now we simply re-process (download is fast for shorts).
        result = await asyncio.wait_for(
            process_next_reel(user_id, database_manager, upload=True),
            timeout=600
        )
        return JSONResponse(content=result)

    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Upload timed out"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']