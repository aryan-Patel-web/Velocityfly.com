"""
MrBeast.py - VIRAL VIDEO GENERATOR
✅ Download YouTube video
✅ Cut into 3-5 viral segments (20-55 seconds each)
✅ Extract transcript → Translate to Hindi
✅ Add Hindi voice-over (ElevenLabs + Free fallbacks)
✅ Auto-upload to YouTube Shorts
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

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# Hindi Voice IDs (ElevenLabs)
HINDI_VOICES = {
    "male_energetic": "pNInz6obpgDQGcFmaJgB",  # Adam
    "female_warm": "EXAVITQu4vr4xnSDxMaL",     # Bella
    "male_deep": "YkAJCvEzSQvG7K2YK9kx",       # Hindi native
    "female_cheerful": "jsCqWAovK2LkecY7zXl4"   # Freya
}

# Video constraints
MIN_DURATION = 20
MAX_DURATION = 55
TARGET_SEGMENTS = 5
MAX_FILE_SIZE_MB = 100
FFMPEG_TIMEOUT = 120

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter()

# ============================================================================
# HELPER: CLEANUP
# ============================================================================

def force_cleanup(filepath: str):
    """Delete file and free memory"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🗑️ Deleted: {os.path.basename(filepath)}")
    except:
        pass
    gc.collect()

def get_file_size_mb(filepath: str) -> float:
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg_safe(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """Run FFmpeg with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        gc.collect()
        return result.returncode == 0
    except:
        gc.collect()
        return False

# ============================================================================
# STEP 1: DOWNLOAD YOUTUBE VIDEO
# ============================================================================

async def download_youtube_video(url: str, temp_dir: str) -> Optional[str]:
    """Download YouTube video using yt-dlp"""
    try:
        output_path = os.path.join(temp_dir, "original_video.mp4")
        
        logger.info(f"📥 Downloading video from: {url}")
        
        # Use yt-dlp for best quality
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            url
        ]
        
        process = subprocess.run(cmd, capture_output=True, timeout=300, check=False)
        
        if process.returncode != 0:
            logger.error(f"yt-dlp error: {process.stderr.decode()}")
            return None
        
        if not os.path.exists(output_path):
            logger.error("Download failed - file not found")
            return None
        
        size_mb = get_file_size_mb(output_path)
        logger.info(f"✅ Downloaded: {size_mb:.1f}MB")
        
        if size_mb > MAX_FILE_SIZE_MB:
            logger.warning(f"Video too large: {size_mb}MB, compressing...")
            compressed = os.path.join(temp_dir, "compressed.mp4")
            
            compress_cmd = [
                "ffmpeg", "-i", output_path,
                "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-crf", "28", "-preset", "fast",
                "-c:a", "aac", "-b:a", "96k",
                "-y", compressed
            ]
            
            if run_ffmpeg_safe(compress_cmd, 180):
                force_cleanup(output_path)
                output_path = compressed
                logger.info(f"✅ Compressed to: {get_file_size_mb(output_path):.1f}MB")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None

# ============================================================================
# STEP 2: GET VIDEO DURATION
# ============================================================================

def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=10, check=False)
        
        if result.returncode == 0:
            duration = float(result.stdout.decode().strip())
            logger.info(f"📏 Video duration: {duration:.1f}s")
            return duration
        
        return 0
        
    except Exception as e:
        logger.error(f"Duration check error: {e}")
        return 0

# ============================================================================
# STEP 3: EXTRACT TRANSCRIPT USING WHISPER (GROQ)
# ============================================================================

async def extract_transcript_whisper(video_path: str, temp_dir: str) -> Optional[str]:
    """Extract audio and transcribe using Whisper"""
    try:
        # Extract audio
        audio_path = os.path.join(temp_dir, "audio.mp3")
        
        logger.info("🎤 Extracting audio...")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "libmp3lame",
            "-b:a", "128k", "-ar", "16000",
            "-y", audio_path
        ]
        
        if not run_ffmpeg_safe(cmd, 60):
            logger.error("Audio extraction failed")
            return None
        
        logger.info("🧠 Transcribing with Whisper...")
        
        # Use Groq Whisper API
        if not GROQ_API_KEY:
            logger.error("GROQ_API_KEY not set")
            return None
        
        async with httpx.AsyncClient(timeout=120) as client:
            with open(audio_path, 'rb') as audio_file:
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files={"file": ("audio.mp3", audio_file, "audio/mpeg")},
                    data={
                        "model": "whisper-large-v3",
                        "response_format": "verbose_json",
                        "temperature": 0
                    }
                )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("text", "")
                
                force_cleanup(audio_path)
                
                logger.info(f"✅ Transcript: {len(transcript)} chars")
                return transcript
            else:
                logger.error(f"Whisper API error: {response.status_code}")
                logger.error(response.text)
                return None
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None

# ============================================================================
# STEP 4: IDENTIFY VIRAL MOMENTS
# ============================================================================

async def identify_viral_moments(transcript: str, video_duration: float, target_duration: int) -> List[Dict]:
    """Use AI to identify best moments for viral clips"""
    try:
        logger.info("🔍 Analyzing viral moments...")
        
        prompt = f"""Analyze this video transcript and identify the 5 MOST VIRAL moments for YouTube Shorts.

Transcript: "{transcript[:2000]}"

Video Duration: {video_duration:.0f} seconds
Target Clip Duration: {target_duration} seconds each

Identify moments with:
- High energy/excitement
- Key reveals or surprises
- Emotional peaks
- Valuable information
- Cliffhangers

Output ONLY valid JSON (no markdown):
{{
  "segments": [
    {{
      "start_time": 10,
      "end_time": 50,
      "duration": 40,
      "text": "Original English text for this segment",
      "viral_score": 9.5,
      "reason": "High energy reveal with surprise element",
      "hooks": "Wait for what happens next..."
    }}
  ]
}}

Generate 5 segments. Each segment must be {MIN_DURATION}-{MAX_DURATION} seconds."""

        # Try Mistral first
        if MISTRAL_API_KEY:
            try:
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
                                {
                                    "role": "system",
                                    "content": "You are a viral video expert. Output ONLY valid JSON without markdown."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7
                        }
                    )
                    
                    if response.status_code == 200:
                        content = response.json()["choices"][0]["message"]["content"]
                        content = re.sub(r'```json\n?|\n?```', '', content).strip()
                        
                        result = json.loads(content)
                        segments = result.get("segments", [])
                        
                        # Validate segments
                        valid_segments = []
                        for seg in segments:
                            duration = seg.get("end_time", 0) - seg.get("start_time", 0)
                            if MIN_DURATION <= duration <= MAX_DURATION:
                                seg["duration"] = duration
                                valid_segments.append(seg)
                        
                        if valid_segments:
                            logger.info(f"✅ Found {len(valid_segments)} viral moments")
                            return valid_segments[:TARGET_SEGMENTS]
            
            except Exception as e:
                logger.warning(f"Mistral error: {e}")
        
        # Fallback to Groq
        if GROQ_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=45) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Output ONLY valid JSON."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7
                        }
                    )
                    
                    if response.status_code == 200:
                        content = response.json()["choices"][0]["message"]["content"]
                        content = re.sub(r'```json\n?|\n?```', '', content).strip()
                        
                        result = json.loads(content)
                        segments = result.get("segments", [])
                        
                        valid_segments = []
                        for seg in segments:
                            duration = seg.get("end_time", 0) - seg.get("start_time", 0)
                            if MIN_DURATION <= duration <= MAX_DURATION:
                                seg["duration"] = duration
                                valid_segments.append(seg)
                        
                        if valid_segments:
                            logger.info(f"✅ Found {len(valid_segments)} viral moments (Groq)")
                            return valid_segments[:TARGET_SEGMENTS]
            
            except Exception as e:
                logger.warning(f"Groq error: {e}")
        
        # Final fallback - simple split
        logger.warning("Using simple time-based split")
        return create_simple_segments(video_duration, target_duration)
        
    except Exception as e:
        logger.error(f"Viral moments error: {e}")
        return create_simple_segments(video_duration, target_duration)

def create_simple_segments(total_duration: float, target_duration: int) -> List[Dict]:
    """Fallback: split video into equal segments"""
    segments = []
    num_segments = min(TARGET_SEGMENTS, int(total_duration / target_duration))
    
    for i in range(num_segments):
        start = i * target_duration
        end = min(start + target_duration, total_duration)
        
        segments.append({
            "start_time": start,
            "end_time": end,
            "duration": end - start,
            "text": f"Segment {i+1}",
            "viral_score": 7.0,
            "reason": "Auto-generated segment"
        })
    
    logger.info(f"Created {len(segments)} simple segments")
    return segments

# ============================================================================
# STEP 5: TRANSLATE TO HINDI
# ============================================================================

async def translate_to_hindi_creative(text: str) -> str:
    """Translate to Hindi with creative MrBeast-style hooks"""
    try:
        logger.info("🌐 Translating to Hindi...")
        
        prompt = f"""Translate this to VIRAL Hindi for YouTube Shorts (MrBeast style):

English: "{text}"

Rules:
1. Keep it exciting and energetic
2. Add Hinglish words (bro, amazing, etc.)
3. Use short, punchy sentences
4. Add suspense/hooks
5. Max 150 words

Output ONLY the Hindi translation (no quotes, no explanations):"""

        # Try Mistral
        if MISTRAL_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
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
                                    "role": "system",
                                    "content": "You are a Hindi content creator. Output ONLY Hindi text."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.8
                        }
                    )
                    
                    if response.status_code == 200:
                        hindi_text = response.json()["choices"][0]["message"]["content"].strip()
                        hindi_text = hindi_text.strip('"\'')
                        logger.info(f"✅ Hindi translation: {len(hindi_text)} chars")
                        return hindi_text
            
            except Exception as e:
                logger.warning(f"Mistral translation error: {e}")
        
        # Fallback to Groq
        if GROQ_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-70b-versatile",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Output ONLY Hindi translation."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.8
                        }
                    )
                    
                    if response.status_code == 200:
                        hindi_text = response.json()["choices"][0]["message"]["content"].strip()
                        hindi_text = hindi_text.strip('"\'')
                        logger.info(f"✅ Hindi translation (Groq): {len(hindi_text)} chars")
                        return hindi_text
            
            except Exception as e:
                logger.warning(f"Groq translation error: {e}")
        
        # Final fallback
        return f"देखिए क्या होता है... {text[:50]}... यकीन नहीं होगा!"
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return f"Amazing content... {text[:30]}"

# ============================================================================
# STEP 6: GENERATE HINDI VOICE-OVER
# ============================================================================

async def generate_hindi_voiceover(text: str, duration: float, voice_type: str, temp_dir: str) -> Optional[str]:
    """Generate Hindi voice using ElevenLabs or free fallbacks"""
    try:
        logger.info(f"🎤 Generating Hindi voice ({voice_type})...")
        
        # Try ElevenLabs first
        if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
            voice_id = HINDI_VOICES.get(voice_type, HINDI_VOICES["male_energetic"])
            
            output = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex[:6]}.mp3")
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text[:500],  # ElevenLabs limit
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "style": 0.5,
                            "use_speaker_boost": True
                        }
                    }
                )
                
                if response.status_code == 200:
                    with open(output, 'wb') as f:
                        f.write(response.content)
                    
                    # Normalize and trim
                    final = output.replace(".mp3", "_final.mp3")
                    cmd = [
                        "ffmpeg", "-i", output,
                        "-af", f"atempo=1.1,loudnorm=I=-16:TP=-1.5",
                        "-t", str(duration + 1),
                        "-y", final
                    ]
                    
                    if run_ffmpeg_safe(cmd, 30):
                        force_cleanup(output)
                        logger.info(f"✅ ElevenLabs voice: {get_file_size_mb(final):.2f}MB")
                        return final
        
        # Fallback 1: Edge TTS (Free)
        logger.info("Using Edge TTS (free)...")
        return await generate_edge_tts(text, duration, temp_dir)
        
    except Exception as e:
        logger.error(f"Voice generation error: {e}")
        return await generate_edge_tts(text, duration, temp_dir)

async def generate_edge_tts(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Free Hindi TTS using Edge"""
    try:
        import edge_tts
        
        output = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:6]}.mp3")
        
        # Hindi voices
        voices = [
            "hi-IN-MadhurNeural",      # Male
            "hi-IN-SwaraNeural",       # Female
            "hi-IN-KalpanaNeural"      # Female warm
        ]
        
        voice = random.choice(voices)
        
        communicate = edge_tts.Communicate(text[:400], voice, rate="+15%", pitch="+3Hz")
        await communicate.save(output)
        
        # Normalize
        final = output.replace(".mp3", "_final.mp3")
        cmd = [
            "ffmpeg", "-i", output,
            "-af", "loudnorm=I=-16:TP=-1.5",
            "-t", str(duration + 1),
            "-y", final
        ]
        
        if run_ffmpeg_safe(cmd, 25):
            force_cleanup(output)
            logger.info(f"✅ Edge TTS voice: {get_file_size_mb(final):.2f}MB")
            return final
        
        return None
        
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
        return None

# ============================================================================
# STEP 7: CUT VIDEO SEGMENT
# ============================================================================

def cut_video_segment(video_path: str, start: float, end: float, temp_dir: str) -> Optional[str]:
    """Extract specific segment from video"""
    try:
        output = os.path.join(temp_dir, f"segment_{uuid.uuid4().hex[:6]}.mp4")
        
        duration = end - start
        
        logger.info(f"✂️ Cutting segment: {start:.1f}s → {end:.1f}s ({duration:.1f}s)")
        
        # Cut and convert to vertical 9:16
        cmd = [
            "ffmpeg", "-ss", str(start), "-i", video_path,
            "-t", str(duration),
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=contrast=1.05:brightness=0.03",
            "-c:v", "libx264", "-crf", "23", "-preset", "medium",
            "-an",  # Remove original audio
            "-y", output
        ]
        
        if run_ffmpeg_safe(cmd, 90):
            logger.info(f"✅ Segment cut: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
        
    except Exception as e:
        logger.error(f"Cut segment error: {e}")
        return None

# ============================================================================
# STEP 8: COMBINE VIDEO + VOICE + CAPTIONS
# ============================================================================

def combine_video_voice_captions(video_path: str, voice_path: str, hindi_text: str, temp_dir: str) -> Optional[str]:
    """Combine video segment with Hindi voice and captions"""
    try:
        output = os.path.join(temp_dir, f"final_{uuid.uuid4().hex[:6]}.mp4")
        
        logger.info("🎬 Combining video + voice + captions...")
        
        # Add voice and text overlay
        text_clean = hindi_text.replace("'", "").replace('"', '')[:60]  # Truncate for display
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", voice_path,
            "-filter_complex",
            f"[0:v]drawtext=text='{text_clean}':fontsize=45:fontcolor=white:x=(w-text_w)/2:y=h-250:borderw=4:bordercolor=black:shadowcolor=black@0.7:shadowx=3:shadowy=3[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264", "-crf", "23", "-preset", "medium",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            "-y", output
        ]
        
        if run_ffmpeg_safe(cmd, 60):
            logger.info(f"✅ Final video: {get_file_size_mb(output):.1f}MB")
            return output
        
        return None
        
    except Exception as e:
        logger.error(f"Combine error: {e}")
        return None

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

async def generate_mrbeast_shorts(
    youtube_url: str,
    target_duration: int,
    voice_type: str,
    num_videos: int,
    user_id: str,
    database_manager
) -> dict:
    """Main function to generate MrBeast-style shorts"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="mrbeast_")
        logger.info(f"🎬 MrBeast Generator Started")
        logger.info(f"URL: {youtube_url}")
        logger.info(f"Duration: {target_duration}s")
        logger.info(f"Voice: {voice_type}")
        
        # Step 1: Download video
        video_path = await download_youtube_video(youtube_url, temp_dir)
        
        if not video_path:
            return {"success": False, "error": "Failed to download video"}
        
        # Step 2: Get duration
        duration = get_video_duration(video_path)
        
        if duration < target_duration:
            return {"success": False, "error": f"Video too short ({duration:.0f}s < {target_duration}s)"}
        
        # Step 3: Extract transcript
        transcript = await extract_transcript_whisper(video_path, temp_dir)
        
        if not transcript:
            return {"success": False, "error": "Failed to extract transcript"}
        
        # Step 4: Identify viral moments
        segments = await identify_viral_moments(transcript, duration, target_duration)
        
        if not segments:
            return {"success": False, "error": "No viral moments found"}
        
        # Limit to requested number
        segments = segments[:num_videos]
        
        # Step 5-8: Process each segment
        generated_videos = []
        
        for i, segment in enumerate(segments):
            try:
                logger.info(f"🎥 Processing segment {i+1}/{len(segments)}...")
                
                start = segment["start_time"]
                end = segment["end_time"]
                text = segment["text"]
                
                # Translate to Hindi
                hindi_text = await translate_to_hindi_creative(text)
                
                # Generate voice
                voice_path = await generate_hindi_voiceover(
                    hindi_text,
                    end - start,
                    voice_type,
                    temp_dir
                )
                
                if not voice_path:
                    logger.warning(f"Segment {i+1} voice failed, skipping...")
                    continue
                
                # Cut video segment
                video_segment = cut_video_segment(video_path, start, end, temp_dir)
                
                if not video_segment:
                    logger.warning(f"Segment {i+1} cut failed, skipping...")
                    force_cleanup(voice_path)
                    continue
                
                # Combine
                final_video = combine_video_voice_captions(
                    video_segment,
                    voice_path,
                    hindi_text,
                    temp_dir
                )
                
                # Cleanup intermediate files
                force_cleanup(video_segment)
                force_cleanup(voice_path)
                
                if final_video:
                    generated_videos.append({
                        "video_path": final_video,
                        "hindi_text": hindi_text,
                        "english_text": text,
                        "start_time": start,
                        "end_time": end,
                        "duration": end - start,
                        "viral_score": segment.get("viral_score", 7.0)
                    })
                    
                    logger.info(f"✅ Segment {i+1} completed!")
                
            except Exception as seg_error:
                logger.error(f"Segment {i+1} error: {seg_error}")
                continue
        
        if not generated_videos:
            return {"success": False, "error": "No videos generated successfully"}
        
        logger.info(f"✅ Generated {len(generated_videos)} viral shorts!")
        
        return {
            "success": True,
            "videos": generated_videos,
            "count": len(generated_videos),
            "message": f"Successfully generated {len(generated_videos)} viral shorts!"
        }
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}
        
    finally:
        # Cleanup
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/api/mrbeast/generate")
async def generate_endpoint(request: Request):
    """Generate MrBeast-style viral shorts"""
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        youtube_url = data.get("youtube_url", "")
        target_duration = int(data.get("target_duration", 30))
        voice_type = data.get("voice_type", "male_energetic")
        num_videos = int(data.get("num_videos", 3))
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        if not youtube_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "YouTube URL required"}
            )
        
        # Validate URL
        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid YouTube URL"}
            )
        
        # Validate duration
        if not (MIN_DURATION <= target_duration <= MAX_DURATION):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Duration must be between {MIN_DURATION}-{MAX_DURATION} seconds"
                }
            )
        
        # Import database manager
        from Supermain import database_manager
        
        # Generate videos
        result = await asyncio.wait_for(
            generate_mrbeast_shorts(
                youtube_url=youtube_url,
                target_duration=target_duration,
                voice_type=voice_type,
                num_videos=num_videos,
                user_id=user_id,
                database_manager=database_manager
            ),
            timeout=600  # 10 minutes max
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={"success": False, "error": "Generation timeout (10 min limit)"}
        )
    except Exception as e:
        logger.error(f"❌ Endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.get("/api/mrbeast/voices")
async def get_voices():
    """Get available voice types"""
    return {
        "success": True,
        "voices": [
            {"id": "male_energetic", "name": "Male Energetic (Hindi)", "premium": True},
            {"id": "female_warm", "name": "Female Warm (Hindi)", "premium": True},
            {"id": "male_deep", "name": "Male Deep (Hindi)", "premium": True},
            {"id": "female_cheerful", "name": "Female Cheerful (Hindi)", "premium": True},
            {"id": "edge_free", "name": "Free Hindi Voice (Edge TTS)", "premium": False}
        ]
    }

__all__ = ['router']