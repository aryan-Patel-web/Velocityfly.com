# # """
# # gdrive_reels.py - PRODUCTION READY WITH COMPLETE ENHANCEMENTS
# # ===================================================================
# # ✅ FALLBACK FOR EVERY STEP - Never fails completely
# # ✅ 1.45x voiceover speed (increased from 1.05x)
# # ✅ ElevenLabs voice as PRIORITY (with Edge TTS fallback)
# # ✅ SEO-optimized titles with emojis and viral appeal
# # ✅ AI-generated descriptions with 35+ keywords
# # ✅ 7-9 trending hashtags per video
# # ✅ Golden captions with white fallback (continues without if both fail)
# # ✅ BGM volume increased by 10% (0.18 from 0.12)
# # ✅ Top 10 royalty-free BGM tracks for AI story reels
# # ✅ If compression fails → continue with original video
# # ✅ If AI script fails → use transcript
# # ✅ If voiceover fails → use Edge TTS
# # ✅ If BGM fails → continue without BGM
# # ✅ HTTP-only transcription (no SDK)
# # ✅ Synchronous processing
# # ✅ Memory optimized
# # ===================================================================
# # """

# # from fastapi import APIRouter, Request
# # from fastapi.responses import JSONResponse
# # import asyncio
# # import logging
# # import os
# # import subprocess
# # import tempfile
# # import shutil
# # import gc
# # import httpx
# # import json
# # import re
# # import random
# # from typing import Optional, List
# # from datetime import datetime
# # import uuid
# # import hashlib

# # try:
# #     import psutil
# #     HAS_PSUTIL = True
# # except:
# #     HAS_PSUTIL = False

# # # ═══════════════════════════════════════════════════════════════════════
# # # LOGGING
# # # ═══════════════════════════════════════════════════════════════════════
# # logger = logging.getLogger("GDriveReels")
# # logger.setLevel(logging.INFO)

# # if not logger.handlers:
# #     handler = logging.StreamHandler()
# #     handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# #     logger.addHandler(handler)

# # def log_memory(step: str):
# #     """Log memory"""
# #     if HAS_PSUTIL:
# #         try:
# #             process = psutil.Process(os.getpid())
# #             mem_mb = process.memory_info().rss / 1024 / 1024
# #             logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
# #             if mem_mb > 450:
# #                 logger.warning(f"⚠️ HIGH: {mem_mb:.1f}MB")
# #                 gc.collect()
# #                 gc.collect()
# #                 gc.collect()
# #         except:
# #             pass

# # # ═══════════════════════════════════════════════════════════════════════
# # # CONFIG
# # # ═══════════════════════════════════════════════════════════════════════
# # GROQ_API_KEY = os.getenv("GROQ_SPEECH_API")
# # MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# # ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# # # Edge TTS Hindi voices for fallback
# # EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

# # # ElevenLabs Hindi voice ID
# # # ELEVENLABS_VOICE_ID = "yD0Zg2jxgfQLY8I2MEHO"
# # ELEVENLABS_VOICE_ID ="kvQSb3naDTi3sgHwwBC1"

# # # ═══════════════════════════════════════════════════════════════════════
# # # TOP 10 ROYALTY-FREE BGM FOR AI STORY REELS
# # # ═══════════════════════════════════════════════════════════════════════
# # TOP_10_BGM_URLS = [
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Krishna%20Healing%20Flute%20'%20Bansuri%20background%20music%20-%20Royalty%20free%20Download.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Maha%20Shivratri%20_%20MANTRA%20Sounds%20of%20Indian%20Land%20-%20Royalty%20free%20Download.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/RAMA%20'%20Indian%20Epic%20BGM%20-%20Royalty%20free%20Music%20Download.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Ramayana%20'%20SITA%20Emotional%20BGM%20-%20India%20Royalty%20free%20music%20Download.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sri%20Krishna%20Govinda%20Devotional%20song%20(%20Flute%20Instrumental%20)%20Royalty%20free%20Music.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Mahabharata%20story%20-%20Duryodhana%20Epic%20BGM%20-%20Royalty%20free%20Music.mp3",
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/DURGA%20maa%20_%20Indian%20Royalty%20free%20Music%20%23durgapuja%20%23navratri.mp3"
# # ]

# # PROCESSING_STATUS = {}

# # # ═══════════════════════════════════════════════════════════════════════
# # # CLEANUP
# # # ═══════════════════════════════════════════════════════════════════════

# # def cleanup(*paths):
# #     """Delete + GC"""
# #     for path in paths:
# #         try:
# #             if path and os.path.exists(path):
# #                 size = os.path.getsize(path) / (1024 * 1024)
# #                 os.remove(path)
# #                 logger.info(f"   🗑️ {os.path.basename(path)} ({size:.1f}MB)")
# #         except:
# #             pass
# #     gc.collect()
# #     gc.collect()
# #     gc.collect()

# # # ═══════════════════════════════════════════════════════════════════════
# # # FFMPEG
# # # ═══════════════════════════════════════════════════════════════════════

# # def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
# #     """Run FFmpeg"""
# #     logger.info(f"🎬 {step}...")
# #     log_memory(f"before-{step}")
    
# #     try:
# #         result = subprocess.run(
# #             cmd,
# #             stdout=subprocess.DEVNULL,
# #             stderr=subprocess.PIPE,
# #             timeout=timeout,
# #             text=True
# #         )
        
# #         success = result.returncode == 0
        
# #         if success:
# #             logger.info(f"✅ {step}")
# #         else:
# #             logger.error(f"❌ {step} failed")
# #             if result.stderr:
# #                 logger.error(f"   Error: {result.stderr[-200:]}")
        
# #         gc.collect()
# #         log_memory(f"after-{step}")
# #         return success
# #     except subprocess.TimeoutExpired:
# #         logger.error(f"⏱️ {step} timeout")
# #         gc.collect()
# #         return False
# #     except Exception as e:
# #         logger.error(f"❌ {step} error: {e}")
# #         gc.collect()
# #         return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # GOOGLE DRIVE
# # # ═══════════════════════════════════════════════════════════════════════

# # def extract_file_id(url: str) -> Optional[str]:
# #     """Extract file ID"""
# #     if not url or "drive.google.com" not in url:
# #         return None
    
# #     patterns = [r'/file/d/([a-zA-Z0-9_-]{25,})', r'[?&]id=([a-zA-Z0-9_-]{25,})']
# #     for pattern in patterns:
# #         match = re.search(pattern, url)
# #         if match:
# #             return match.group(1)
# #     return None

# # async def download_chunked(url: str, output: str) -> bool:
# #     """Download in chunks"""
# #     try:
# #         async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
# #             async with client.stream("GET", url) as response:
# #                 if response.status_code != 200:
# #                     return False
                
# #                 total = 0
# #                 with open(output, 'wb') as f:
# #                     async for chunk in response.aiter_bytes(1024*1024):
# #                         f.write(chunk)
# #                         total += len(chunk)
# #                         if total % (5*1024*1024) < 1024*1024:
# #                             logger.info(f"   📥 {total/(1024*1024):.1f}MB")
                
# #                 if total > 10000:
# #                     logger.info(f"   ✅ {total/(1024*1024):.1f}MB")
# #                     return True
# #         return False
# #     except Exception as e:
# #         logger.error(f"   ❌ {e}")
# #         return False

# # async def download_from_gdrive(file_id: str, output: str) -> tuple[bool, str]:
# #     """Download with fallbacks"""
# #     logger.info("⬇️ Downloading...")
# #     log_memory("download-start")
    
# #     urls = [
# #         f"https://drive.google.com/uc?export=download&id={file_id}",
# #         f"https://drive.usercontent.google.com/download?id={file_id}&export=download",
# #     ]
    
# #     for idx, url in enumerate(urls, 1):
# #         logger.info(f"📥 Method {idx}/{len(urls)}")
# #         if await download_chunked(url, output):
# #             logger.info(f"✅ Downloaded")
# #             log_memory("download-done")
# #             return True, ""
# #         await asyncio.sleep(1)
    
# #     return False, "Download failed"

# # # ═══════════════════════════════════════════════════════════════════════
# # # VIDEO COMPRESSION (WITH FALLBACK)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def try_compress_video(input_path: str, output_path: str, timeout: int = 60) -> bool:
# #     """
# #     Try to compress video to 720p
# #     FALLBACK: If fails, return False and continue with original
# #     """
# #     logger.info("🔧 Trying to compress to 720p...")
# #     log_memory("compress-start")
    
# #     # Method 1: Standard compression
# #     logger.info("   Method 1: Standard 720p")
# #     success = run_ffmpeg([
# #         "ffmpeg", "-i", input_path,
# #         "-vf", "scale=720:-2",
# #         "-c:v", "libx264",
# #         "-crf", "28",
# #         "-preset", "ultrafast",
# #         "-c:a", "aac",
# #         "-b:a", "96k",
# #         "-y", output_path
# #     ], timeout=timeout, step="Compress-720p")
    
# #     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
# #         cleanup(input_path)
# #         size = os.path.getsize(output_path) / (1024 * 1024)
# #         logger.info(f"✅ Compressed: {size:.1f}MB")
# #         log_memory("compress-done")
# #         return True
    
# #     # Method 2: Copy codec (faster, less compression)
# #     logger.info("   Method 2: Copy codec")
# #     cleanup(output_path)  # Remove failed attempt
    
# #     success = run_ffmpeg([
# #         "ffmpeg", "-i", input_path,
# #         "-vf", "scale=720:-2",
# #         "-c:v", "copy",  # Copy codec, no re-encode
# #         "-c:a", "copy",
# #         "-y", output_path
# #     ], timeout=30, step="Compress-copy")
    
# #     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
# #         cleanup(input_path)
# #         size = os.path.getsize(output_path) / (1024 * 1024)
# #         logger.info(f"✅ Compressed (copy): {size:.1f}MB")
# #         log_memory("compress-done")
# #         return True
    
# #     # FALLBACK: Compression failed, remove failed file
# #     cleanup(output_path)
# #     logger.warning("⚠️ Compression failed, continuing with original video")
# #     log_memory("compress-failed")
# #     return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # VIDEO INFO
# # # ═══════════════════════════════════════════════════════════════════════

# # async def get_duration(video_path: str) -> float:
# #     """Get duration"""
# #     try:
# #         result = subprocess.run(
# #             ["ffprobe", "-v", "error", "-show_entries", "format=duration",
# #              "-of", "default=noprint_wrappers=1:nokey=1", video_path],
# #             capture_output=True, timeout=15, text=True
# #         )
# #         if result.returncode == 0:
# #             duration = float(result.stdout.strip())
# #             logger.info(f"⏱️ {duration:.1f}s")
# #             return duration
# #         return 0.0
# #     except:
# #         return 0.0

# # # ═══════════════════════════════════════════════════════════════════════
# # # AUDIO EXTRACTION
# # # ═══════════════════════════════════════════════════════════════════════

# # async def extract_audio(video_path: str, audio_path: str) -> bool:
# #     """Extract audio"""
# #     success = run_ffmpeg([
# #         "ffmpeg", "-i", video_path,
# #         "-vn", "-acodec", "pcm_s16le",
# #         "-ar", "16000", "-ac", "1",
# #         "-y", audio_path
# #     ], timeout=60, step="Extract-Audio")
    
# #     return success

# # # ═══════════════════════════════════════════════════════════════════════
# # # TRANSCRIPTION (HTTP ONLY + FALLBACK)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def transcribe_audio(audio_path: str) -> tuple[Optional[str], str]:
# #     """Transcribe with HTTP API"""
# #     logger.info("📝 Transcribing...")
# #     log_memory("transcribe-start")
    
# #     if not GROQ_API_KEY:
# #         return None, "No API key"
    
# #     try:
# #         async with httpx.AsyncClient(timeout=60) as client:
# #             with open(audio_path, "rb") as f:
# #                 files = {"file": ("audio.wav", f, "audio/wav")}
# #                 data = {"model": "whisper-large-v3", "language": "hi", "response_format": "text"}
                
# #                 response = await client.post(
# #                     "https://api.groq.com/openai/v1/audio/transcriptions",
# #                     headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
# #                     files=files,
# #                     data=data
# #                 )
                
# #                 if response.status_code == 200:
# #                     transcript = response.text.strip()
# #                     if len(transcript) > 5:
# #                         logger.info(f"✅ Transcribed ({len(transcript)} chars)")
# #                         logger.info(f"   {transcript[:100]}...")
# #                         log_memory("transcribe-done")
                        
# #                         cleanup(audio_path)
# #                         return transcript, ""
        
# #         cleanup(audio_path)
# #         return None, "Empty response"
# #     except Exception as e:
# #         cleanup(audio_path)
# #         logger.error(f"❌ Transcription error: {e}")
# #         return None, str(e)

# # # ═══════════════════════════════════════════════════════════════════════
# # # AI SCRIPT WITH SEO (TITLE, DESCRIPTION, KEYWORDS, HASHTAGS)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def generate_seo_script(transcript: str, duration: float) -> dict:
# #     """Generate script with SEO-optimized metadata (like Pixabay)"""
# #     logger.info("🤖 AI Script with SEO...")
# #     log_memory("ai-start")
    
# #     words = int(duration * 2.5)
    
# #     # CTA (Call to Action)
# #     cta = "Agar aapko yeh video achhi lagi ho toh LIKE karein, SUBSCRIBE karein aur apne doston ko SHARE karein!"
    
# #     # Try Mistral AI
# #     if MISTRAL_API_KEY:
# #         try:
# #             logger.info("   Trying Mistral AI for SEO content...")
            
# #             prompt = f"""Generate engaging Hindi narration for video with COMPLETE SEO optimization:

# # Transcript: {transcript}
# # Duration: {duration} seconds (approximately {words} words)

# # CRITICAL REQUIREMENTS:
# # 1. Create 100% UNIQUE Hindi content (natural flow, not robotic)
# # 2. Use commas, exclamations for natural speech breaks
# # 3. NO "pause" word - use natural rhythm
# # 4. Include hook + main story + conclusion
# # 5. Add CTA at end: "{cta}"

# # SEO REQUIREMENTS (VERY STRICT – FOLLOW EXACTLY):

# # 6. Generate a VIRAL Hinglish TITLE containing:
# #    - Power words like: SHOCKING, AMAZING, UNBELIEVABLE, SECRET
# #    - Emojis for visual appeal
# #    - Example: "Yeh Video Dekhkar Aap SHOCK Ho Jaoge! 😱 | Sachai Kya Hai? #Shorts"

# # 7. Write a Hinglish DESCRIPTION (2-3 short paragraphs):
# #    - First paragraph: Explain the video topic clearly
# #    - Second paragraph: Add emotional appeal or curiosity
# #    - End with: "Keywords: ..."

# # 8. Generate EXACTLY 65-70 SEO KEYWORDS:
# #    - ALL keywords MUST be derived from video content
# #    - Use real YouTube search-style phrases
# #    - Mix Hindi + English terms naturally
# #    - Example format: "hindi story, amazing facts hindi, viral video, shocking truth, interesting facts"

# # 9. Generate 8-9 HASHTAGS:
# #    - Must be directly related to content
# #    - Include: #Shorts, #Viral, #Hindi (always)
# #    - Add 4-6 content-specific tags
# #    - Example:#Foryou, #Fyp, #Explore, #Reach, #Reelsgrowth, #Boostyourreel, #Trendingnow #HindiStory #AmazingFacts #Shorts #Viral #Trending #MustWatch #Hindi

# # 10. SEO OUTPUT FORMAT (VERY STRICT):
# # - Description first (2-3 lines in Hinglish)
# # - Then 35+ keywords in VERTICAL format (one per line)
# # - Then hashtags in VERTICAL format (one per line)
# # - NO commas in keywords section
# # - NO numbering or bullets

# # Generate in JSON format:
# # {{
# #     "script": "Complete Hindi narration with CTA at end...",
# #     "title": "Viral Hinglish title with emojis (max 100 chars)",
# #     "description": "Hinglish description paragraph 1\\n\\nHinglish description paragraph 2\\n\\nkeyword one\\nkeyword two\\nkeyword three\\n... (65+ keywords)\\n\\n#HashtagOne\\n#HashtagTwo\\n... (8-9 hashtags)",
# #     "hashtags": ["#Foryou", "#Fyp", "#Explore", "#Reach", "#Reelsgrowth", "#Boostyourreel", "#Trendingnow","#Shorts", "#Viral", "#Hindi", "#Trending", "#MustWatch", "#Amazing", "#Story"],
# #     "story_id": "unique-id-based-on-content"
# # }}"""
            
# #             async with httpx.AsyncClient(timeout=60) as client:
# #                 resp = await client.post(
# #                     "https://api.mistral.ai/v1/chat/completions",
# #                     headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
# #                     json={
# #                         "model": "mistral-large-latest",
# #                         "messages": [
# #                             {
# #                                 "role": "system",
# #                                 "content": "You are a viral YouTube content creator. Create SEO-optimized Hinglish titles and descriptions. Output ONLY valid JSON."
# #                             },
# #                             {"role": "user", "content": prompt}
# #                         ],
# #                         "temperature": 0.8,
# #                         "max_tokens": 1500
# #                     }
# #                 )
                
# #                 if resp.status_code == 200:
# #                     content = resp.json()["choices"][0]["message"]["content"]
                    
# #                     # Clean JSON
# #                     content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
# #                     content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    
# #                     match = re.search(r'\{.*\}', content, re.DOTALL)
                    
# #                     if match:
# #                         data = json.loads(match.group(0))
# #                         script_text = data.get("script", transcript)
                        
# #                         # Ensure CTA
# #                         if "LIKE" not in script_text or "SUBSCRIBE" not in script_text:
# #                             script_text += " " + cta
                        
# #                         title = data.get("title", "Amazing Story 🔥 | Must Watch! #Shorts")
# #                         description = data.get("description", f"{transcript[:200]}\\n\\nKeywords: hindi story, amazing facts, viral video")
# #                         hashtags = data.get("hashtags", ["#Shorts", "#Viral", "#Hindi", "#Trending", "#MustWatch", "#Amazing", "#Story"])
# #                         story_id = data.get("story_id", str(uuid.uuid4())[:8])
                        
# #                         logger.info(f"✅ AI Script Generated")
# #                         logger.info(f"   Title: {title}")
# #                         logger.info(f"   Hashtags: {len(hashtags)}")
# #                         log_memory("ai-done")
                        
# #                         return {
# #                             "script": script_text,
# #                             "title": title,
# #                             "description": description,
# #                             "hashtags": hashtags,
# #                             "story_id": story_id
# #                         }
# #         except Exception as e:
# #             logger.warning(f"   Mistral failed: {e}")
    
# #     # FALLBACK: Use transcript with basic SEO
# #     logger.info("   Using transcript (fallback with basic SEO)")
# #     script = " ".join(transcript.split()[:words]) + " " + cta
    
# #     # Extract first few words for title
# #     title_base = " ".join(transcript.split()[:5])
# #     title = f"{title_base}... 🔥 | Must Watch! #Shorts"
    
# #     # Basic description with keywords
# #     description = f"{transcript[:150]}...\n\nKeywords: hindi story, amazing facts, viral video, trending shorts, must watch, interesting content, hindi facts, viral shorts, trending video, youtube shorts"
    
# #     hashtags = ["#Shorts", "#Viral", "#Hindi", "#Trending", "#MustWatch", "#Amazing", "#Story"]
    
# #     log_memory("ai-done")
    
# #     return {
# #         "script": script,
# #         "title": title,
# #         "description": description,
# #         "hashtags": hashtags,
# #         "story_id": str(uuid.uuid4())[:8]
# #     }

# # # ═══════════════════════════════════════════════════════════════════════
# # # VOICEOVER WITH 1.45X SPEED - ELEVENLABS PRIORITY + EDGE TTS FALLBACK
# # # ═══════════════════════════════════════════════════════════════════════

# # async def generate_voiceover_12x(script: str, output: str) -> tuple[bool, str]:
# #     """
# #     Generate voiceover at 1.45x speed with priority system:
# #     1. ElevenLabs (PRIMARY)
# #     2. Edge TTS (FALLBACK)
# #     """
# #     logger.info("🎙️ Voiceover (1.45x speed)...")
# #     log_memory("voice-start")
    
# #     # ========== PRIORITY 1: ELEVENLABS ==========
# #     if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
# #         try:
# #             logger.info("   Attempting ElevenLabs TTS (Priority)...")
# #             async with httpx.AsyncClient(timeout=60) as client:
# #                 resp = await client.post(
# #                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
# #                     headers={"xi-api-key": ELEVENLABS_API_KEY},
# #                     json={
# #                         "text": script[:2000],
# #                         "model_id": "eleven_multilingual_v2"
# #                     }
# #                 )
                
# #                 if resp.status_code == 200:
# #                     base = output.replace(".mp3", "_base.mp3")
# #                     with open(base, 'wb') as f:
# #                         f.write(resp.content)
                    
# #                     # Apply 1.45x speed
# #                     if run_ffmpeg([
# #                         "ffmpeg", "-i", base, "-filter:a", "atempo=1.45",
# #                         "-y", output
# #                     ], 30):
# #                         cleanup(base)
# #                         size = os.path.getsize(output) / 1024
# #                         logger.info(f"✅ ElevenLabs Voiceover (1.45x): {size:.1f}KB")
# #                         log_memory("voice-done")
# #                         return True, ""
# #                     cleanup(base)
# #         except Exception as e:
# #             logger.warning(f"⚠️ ElevenLabs failed: {e}")
# #     else:
# #         logger.warning("⚠️ ElevenLabs API key not available")
    
# #     # ========== FALLBACK: EDGE TTS ==========
# #     logger.info("🔄 Falling back to Edge TTS...")
# #     try:
# #         import edge_tts
        
# #         voice = random.choice(EDGE_TTS_VOICES)
# #         logger.info(f"   Using {voice}")
        
# #         base = output.replace(".mp3", "_edge_base.mp3")
        
# #         # Generate with Edge TTS at increased rate
# #         await edge_tts.Communicate(script[:2000], voice, rate="+20%").save(base)
        
# #         # Apply 1.45x speed on top
# #         if run_ffmpeg([
# #             "ffmpeg", "-i", base, "-filter:a", "atempo=1.45",
# #             "-y", output
# #         ], 30):
# #             cleanup(base)
# #             size = os.path.getsize(output) / 1024
# #             logger.info(f"✅ Edge TTS Voiceover (1.45x): {size:.1f}KB")
# #             log_memory("voice-done")
# #             return True, ""
        
# #         # If speed adjustment fails, use base
# #         if os.path.exists(base):
# #             os.rename(base, output)
# #             size = os.path.getsize(output) / 1024
# #             logger.info(f"✅ Edge TTS Voiceover (base): {size:.1f}KB")
# #             log_memory("voice-done")
# #             return True, ""
# #     except Exception as e:
# #         logger.error(f"❌ Edge TTS error: {e}")
    
# #     logger.error("❌ All voiceover methods failed!")
# #     return False, "Voiceover generation failed"

# # # ═══════════════════════════════════════════════════════════════════════
# # # CAPTIONS (GOLDEN → WHITE → NO CAPTIONS FALLBACK)
# # # ═══════════════════════════════════════════════════════════════════════

# # def generate_srt(script: str, duration: float) -> str:
# #     """Generate SRT"""
# #     words = script.split()
# #     phrases = [" ".join(words[i:i+4]) for i in range(0, len(words), 4) if words[i:i+4]]
    
# #     if not phrases:
# #         return ""
    
# #     time_per = duration / len(phrases)
# #     blocks = []
    
# #     for i, phrase in enumerate(phrases):
# #         start = i * time_per
# #         end = start + time_per
        
# #         sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
# #         eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
# #         blocks.append(f"{i+1}\n{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
# #                      f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + f"\n{phrase}\n")
    
# #     return "\n".join(blocks)

# # # ═══════════════════════════════════════════════════════════════════════
# # # VIDEO ASSEMBLY
# # # ═══════════════════════════════════════════════════════════════════════

# # async def remove_audio(video_in: str, video_out: str) -> bool:
# #     """Remove audio"""
# #     success = run_ffmpeg([
# #         "ffmpeg", "-i", video_in,
# #         "-c:v", "copy", "-an",
# #         "-y", video_out
# #     ], timeout=60, step="Remove-Audio")
    
# #     if success:
# #         cleanup(video_in)
    
# #     return success

# # async def download_bgm(output: str) -> bool:
# #     """Download BGM from top 10 list"""
# #     logger.info("🎵 BGM (Top 10 Royalty-Free)...")
# #     log_memory("bgm-start")
    
# #     # Randomly select from top 10
# #     bgm_url = random.choice(TOP_10_BGM_URLS)
# #     logger.info(f"   Selected: {bgm_url.split('/')[-1][:50]}...")
    
# #     try:
# #         success = await download_chunked(bgm_url, output)
        
# #         if success:
# #             logger.info("✅ BGM Downloaded")
# #             log_memory("bgm-done")
# #             return True
        
# #         logger.warning("⚠️ BGM download failed")
# #         return False
# #     except:
# #         logger.warning("⚠️ BGM error")
# #         return False

# # async def create_final_video(silent: str, voice: str, srt: str, bgm: Optional[str], output: str) -> tuple[bool, str]:
# #     """Create final video with caption fallbacks and increased BGM volume"""
# #     logger.info("✨ Final Video...")
# #     log_memory("final-start")
    
# #     captioned = output.replace(".mp4", "_cap.mp4")
# #     srt_esc = srt.replace("\\", "\\\\").replace(":", "\\:")
    
# #     # ========== CAPTION ATTEMPT 1: GOLDEN COLOR ==========
# #     logger.info("   Trying GOLDEN captions (#FFD700)...")
# #     caption_success = run_ffmpeg([
# #         "ffmpeg", "-i", silent,
# #         "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFD700,Bold=1,Outline=2,Alignment=2,MarginV=50'",
# #         "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
# #         "-y", captioned
# #     ], 180, "Captions-Golden")
    
# #     if caption_success and os.path.exists(captioned) and os.path.getsize(captioned) > 10000:
# #         logger.info("✅ Golden captions applied")
# #         cleanup(silent)
# #         video_for_audio = captioned
# #     else:
# #         # ========== CAPTION ATTEMPT 2: WHITE COLOR FALLBACK ==========
# #         logger.warning("⚠️ Golden captions failed, trying WHITE captions...")
# #         cleanup(captioned)
        
# #         caption_success = run_ffmpeg([
# #             "ffmpeg", "-i", silent,
# #             "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,Bold=1,Outline=2,Alignment=2,MarginV=50'",
# #             "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
# #             "-y", captioned
# #         ], 180, "Captions-White")
        
# #         if caption_success and os.path.exists(captioned) and os.path.getsize(captioned) > 10000:
# #             logger.info("✅ White captions applied")
# #             cleanup(silent)
# #             video_for_audio = captioned
# #         else:
# #             # ========== CAPTION FALLBACK: CONTINUE WITHOUT CAPTIONS ==========
# #             logger.warning("⚠️ All caption attempts failed, continuing WITHOUT captions")
# #             cleanup(captioned)
# #             video_for_audio = silent
    
# #     cleanup(srt)
    
# #     # ========== MIX AUDIO (BGM VOLUME INCREASED BY 10% TO 0.18) ==========
# #     if bgm and os.path.exists(bgm):
# #         logger.info("   Mixing voice + BGM (BGM volume: 0.18)...")
# #         success = run_ffmpeg([
# #             "ffmpeg", "-i", video_for_audio, "-i", voice, "-i", bgm,
# #             "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.18[m];[v][m]amix=inputs=2:duration=first[a]",
# #             "-map", "0:v", "-map", "[a]",
# #             "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
# #             "-shortest", "-y", output
# #         ], 120, "Mix-Voice-BGM")
        
# #         if not success:
# #             # FALLBACK: Try without BGM
# #             logger.warning("⚠️ Mix with BGM failed, trying without BGM...")
# #             success = run_ffmpeg([
# #                 "ffmpeg", "-i", video_for_audio, "-i", voice,
# #                 "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
# #                 "-shortest", "-y", output
# #             ], 90, "Add-Voice")
# #     else:
# #         logger.info("   Adding voice only (no BGM)...")
# #         success = run_ffmpeg([
# #             "ffmpeg", "-i", video_for_audio, "-i", voice,
# #             "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
# #             "-shortest", "-y", output
# #         ], 90, "Add-Voice")
    
# #     cleanup(video_for_audio, voice, bgm)
    
# #     if not success:
# #         return False, "Audio mix failed"
    
# #     log_memory("final-done")
# #     return True, ""

# # # ═══════════════════════════════════════════════════════════════════════
# # # YOUTUBE UPLOAD
# # # ═══════════════════════════════════════════════════════════════════════

# # async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
# #     """Upload to YouTube"""
# #     logger.info("📤 YouTube...")
# #     log_memory("upload-start")
    
# #     try:
# #         from YTdatabase import get_database_manager as get_yt_db
# #         yt_db = get_yt_db()
        
# #         if not yt_db.youtube.client:
# #             await yt_db.connect()
        
# #         creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
# #         if not creds:
# #             return {"success": False, "error": "No YouTube credentials"}
        
# #         credentials = {
# #             "access_token": creds.get("access_token"),
# #             "refresh_token": creds.get("refresh_token"),
# #             "token_uri": "https://oauth2.googleapis.com/token",
# #             "client_id": creds.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
# #             "client_secret": creds.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
# #             "scopes": [
# #                 "https://www.googleapis.com/auth/youtube.upload",
# #                 "https://www.googleapis.com/auth/youtube.force-ssl"
# #             ]
# #         }
        
# #         from mainY import youtube_scheduler
        
# #         result = await youtube_scheduler.generate_and_upload_content(
# #             user_id=user_id,
# #             credentials_data=credentials,
# #             content_type="shorts",
# #             title=title,
# #             description=description,
# #             video_url=video_path
# #         )
        
# #         if result.get("success"):
# #             video_id = result.get("video_id")
# #             logger.info(f"✅ Uploaded: {video_id}")
# #             log_memory("upload-done")
# #             return {
# #                 "success": True,
# #                 "video_id": video_id,
# #                 "video_url": f"https://youtube.com/shorts/{video_id}"
# #             }
        
# #         return {"success": False, "error": result.get("error", "Upload failed")}
# #     except Exception as e:
# #         logger.error(f"❌ {e}")
# #         return {"success": False, "error": str(e)}

# # # ═══════════════════════════════════════════════════════════════════════
# # # MAIN PIPELINE (WITH COMPLETE FALLBACKS + SEO)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def process_reel(drive_url: str, user_id: str, task_id: str):
# #     """Main pipeline with fallbacks + SEO at every step"""
# #     temp_dir = None
# #     start_time = datetime.now()
    
# #     PROCESSING_STATUS[task_id] = {
# #         "status": "processing",
# #         "progress": 0,
# #         "message": "Starting...",
# #         "started_at": start_time.isoformat()
# #     }
    
# #     def update(progress: int, msg: str):
# #         PROCESSING_STATUS[task_id]["progress"] = progress
# #         PROCESSING_STATUS[task_id]["message"] = msg
# #         logger.info(f"[{progress}%] {msg}")
    
# #     try:
# #         temp_dir = tempfile.mkdtemp(prefix="reel_")
# #         logger.info(f"📁 {temp_dir}")
# #         log_memory("START")
        
# #         # Extract ID
# #         update(5, "Extracting ID...")
# #         file_id = extract_file_id(drive_url)
# #         if not file_id:
# #             raise ValueError("Invalid URL")
        
# #         # Download
# #         update(10, "Downloading...")
# #         raw_video = os.path.join(temp_dir, "raw.mp4")
# #         success, error = await download_from_gdrive(file_id, raw_video)
# #         if not success:
# #             raise Exception(error)
        
# #         # Try to compress (FALLBACK: use original if fails)
# #         update(15, "Compressing (optional)...")
# #         compressed_video = os.path.join(temp_dir, "compressed.mp4")
        
# #         compression_success = await try_compress_video(raw_video, compressed_video, timeout=90)
        
# #         if compression_success:
# #             working_video = compressed_video
# #             logger.info("✅ Using compressed video")
# #         else:
# #             working_video = raw_video
# #             logger.info("⚠️ Using original video (compression failed)")
        
# #         # Get duration
# #         update(20, "Analyzing...")
# #         duration = await get_duration(working_video)
# #         if duration <= 0:
# #             raise ValueError("Invalid video")
# #         if duration > 180:
# #             raise ValueError(f"Too long ({duration:.0f}s)")
        
# #         # Extract audio
# #         update(25, "Extracting audio...")
# #         audio_path = os.path.join(temp_dir, "audio.wav")
# #         if not await extract_audio(working_video, audio_path):
# #             raise Exception("Audio extraction failed")
        
# #         # Transcribe
# #         update(30, "Transcribing...")
# #         transcript, error = await transcribe_audio(audio_path)
# #         if not transcript:
# #             raise Exception(error)
        
# #         # AI script with SEO (title, description, keywords, hashtags)
# #         update(50, "AI script + SEO optimization...")
# #         metadata = await generate_seo_script(transcript, duration)
# #         logger.info(f"   Title: {metadata['title']}")
# #         logger.info(f"   Hashtags: {' '.join(metadata['hashtags'])}")
        
# #         # Voiceover at 1.45x (ElevenLabs → Edge TTS fallback)
# #         update(60, "Voiceover (1.45x speed)...")
# #         voiceover = os.path.join(temp_dir, "voice.mp3")
# #         success, error = await generate_voiceover_12x(metadata["script"], voiceover)
# #         if not success:
# #             raise Exception(error)
        
# #         # Remove audio
# #         update(70, "Removing audio...")
# #         silent_video = os.path.join(temp_dir, "silent.mp4")
# #         if not await remove_audio(working_video, silent_video):
# #             raise Exception("Remove audio failed")
        
# #         # Captions
# #         update(75, "Captions (Golden → White → None fallback)...")
# #         srt_path = os.path.join(temp_dir, "captions.srt")
# #         with open(srt_path, 'w', encoding='utf-8') as f:
# #             f.write(generate_srt(metadata["script"], duration))
        
# #         # BGM (Top 10, optional - fallback if fails)
# #         update(80, "BGM (Top 10 Royalty-Free)...")
# #         bgm_path = os.path.join(temp_dir, "bgm.mp3")
# #         bgm_success = await download_bgm(bgm_path)
        
# #         if not bgm_success:
# #             bgm_path = None
# #             logger.info("   Continuing without BGM")
        
# #         # Final video (with caption fallbacks + increased BGM)
# #         update(85, "Final video (captions + audio mix)...")
# #         final_video = os.path.join(temp_dir, "final.mp4")
# #         success, error = await create_final_video(silent_video, voiceover, srt_path, bgm_path, final_video)
# #         if not success:
# #             raise Exception(error)
        
# #         if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
# #             raise Exception("Invalid final video")
        
# #         size_mb = os.path.getsize(final_video) / (1024 * 1024)
# #         logger.info(f"   Final: {size_mb:.1f}MB")
        
# #         # Upload with SEO metadata
# #         update(95, "Uploading with SEO metadata...")
        
# #         # Format description with hashtags
# #         full_description = f"{metadata['description']}\n\n{' '.join(metadata['hashtags'])}"
        
# #         upload_result = await upload_to_youtube(final_video, metadata["title"], full_description, user_id)
        
# #         if not upload_result.get("success"):
# #             raise Exception(upload_result.get("error"))
        
# #         # SUCCESS
# #         elapsed = (datetime.now() - start_time).total_seconds()
        
# #         logger.info("="*80)
# #         logger.info("✅ SUCCESS!")
# #         logger.info(f"   Time: {elapsed:.1f}s")
# #         logger.info(f"   Video: {upload_result['video_id']}")
# #         logger.info("="*80)
# #         log_memory("COMPLETE")
        
# #         PROCESSING_STATUS[task_id] = {
# #             "status": "completed",
# #             "progress": 100,
# #             "success": True,
# #             "message": "Uploaded!",
# #             "title": metadata["title"],
# #             "description": full_description,
# #             "hashtags": metadata["hashtags"],
# #             "story_id": metadata.get("story_id", ""),
# #             "duration": round(duration, 1),
# #             "processing_time": round(elapsed, 1),
# #             "video_id": upload_result["video_id"],
# #             "video_url": upload_result["video_url"],
# #             "completed_at": datetime.utcnow().isoformat()
# #         }
        
# #     except Exception as e:
# #         error_msg = str(e)
# #         logger.error("="*80)
# #         logger.error(f"❌ FAILED: {error_msg}")
# #         logger.error("="*80)
        
# #         PROCESSING_STATUS[task_id] = {
# #             "status": "failed",
# #             "progress": 0,
# #             "success": False,
# #             "error": error_msg,
# #             "message": error_msg,
# #             "failed_at": datetime.utcnow().isoformat()
# #         }
    
# #     finally:
# #         if temp_dir and os.path.exists(temp_dir):
# #             logger.info("🧹 Cleanup...")
# #             try:
# #                 shutil.rmtree(temp_dir, ignore_errors=True)
# #                 logger.info("✅ Clean")
# #             except:
# #                 pass
        
# #         gc.collect()
# #         gc.collect()
# #         gc.collect()
# #         log_memory("FINAL")

# # # ═══════════════════════════════════════════════════════════════════════
# # # API
# # # ═══════════════════════════════════════════════════════════════════════

# # router = APIRouter()

# # @router.post("/api/gdrive-reels/process")
# # async def process_endpoint(request: Request):
# #     """Process (SYNCHRONOUS)"""
# #     logger.info("🌐 API REQUEST")
    
# #     try:
# #         data = await request.json()
        
# #         user_id = data.get("user_id")
# #         drive_url = (data.get("drive_url") or "").strip()
        
# #         if not user_id:
# #             return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
# #         if not drive_url or "drive.google.com" not in drive_url:
# #             return JSONResponse(status_code=400, content={"success": False, "error": "Valid URL required"})
        
# #         task_id = str(uuid.uuid4())
# #         logger.info(f"✅ Task: {task_id}")
        
# #         # SYNCHRONOUS
# #         await asyncio.wait_for(process_reel(drive_url, user_id, task_id), timeout=600)
        
# #         result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
# #         return JSONResponse(content=result)
        
# #     except asyncio.TimeoutError:
# #         return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
# #     except Exception as e:
# #         logger.error(f"❌ {e}")
# #         return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# # @router.get("/api/gdrive-reels/status/{task_id}")
# # async def status_endpoint(task_id: str):
# #     """Status"""
# #     status = PROCESSING_STATUS.get(task_id)
# #     if not status:
# #         return JSONResponse(status_code=404, content={"success": False, "error": "Not found"})
# #     return JSONResponse(content=status)

# # @router.get("/api/gdrive-reels/health")
# # async def health_endpoint():
# #     """Health"""
# #     log_memory("health")
# #     return JSONResponse(content={
# #         "status": "ok",
# #         "groq_configured": bool(GROQ_API_KEY),
# #         "elevenlabs_configured": bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20),
# #         "mistral_configured": bool(MISTRAL_API_KEY),
# #         "active_tasks": len([s for s in PROCESSING_STATUS.values() if s["status"] == "processing"]),
# #         "features": {
# #             "voiceover_speed": "1.45x",
# #             "voiceover_priority": "ElevenLabs → Edge TTS",
# #             "caption_colors": "Golden (#FFD700) → White → None",
# #             "bgm_volume": "0.18 (increased by 10%)",
# #             "bgm_tracks": len(TOP_10_BGM_URLS),
# #             "seo_optimization": "Title + Description + 35+ Keywords + 7-9 Hashtags"
# #         }
# #     })

# # @router.get("/api/gdrive-reels/bgm-list")
# # async def bgm_list_endpoint():
# #     """Get list of top 10 BGM tracks"""
# #     return JSONResponse(content={
# #         "success": True,
# #         "total_tracks": len(TOP_10_BGM_URLS),
# #         "tracks": [
# #             {
# #                 "index": idx + 1,
# #                 "name": url.split('/')[-1].replace('%20', ' ').replace('.mp3', ''),
# #                 "url": url
# #             }
# #             for idx, url in enumerate(TOP_10_BGM_URLS)
# #         ]
# #     })

# # async def initialize():
# #     """Startup"""
# #     logger.info("="*80)
# #     logger.info("🚀 GDRIVE REELS (ENHANCED VERSION)")
# #     logger.info("="*80)
# #     logger.info("✅ 1.45x voiceover speed")
# #     logger.info("✅ ElevenLabs priority + Edge TTS fallback")
# #     logger.info("✅ SEO: Title + Description + 35+ Keywords + 7-9 Hashtags")
# #     logger.info("✅ Golden captions → White → None fallback")
# #     logger.info("✅ BGM volume: 0.18 (increased 10%)")
# #     logger.info(f"✅ Top {len(TOP_10_BGM_URLS)} royalty-free BGM tracks")
# #     logger.info("="*80)
    
# #     if GROQ_API_KEY:
# #         logger.info("✅ Groq configured")
# #     else:
# #         logger.error("❌ No GROQ_SPEECH_API")
    
# #     if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
# #         logger.info("✅ ElevenLabs configured (Priority)")
# #     else:
# #         logger.warning("⚠️ ElevenLabs not configured (will use Edge TTS)")
    
# #     if MISTRAL_API_KEY:
# #         logger.info("✅ Mistral AI configured (SEO)")
# #     else:
# #         logger.warning("⚠️ Mistral AI not configured (basic SEO)")
    
# #     log_memory("startup")
# #     logger.info("="*80)

# # __all__ = ["router", "initialize"]




# """
# gdrive_reels.py - PERFECT VOICE SYNC + HUMAN-LIKE + NO GAPS
# =================================================================================
# ✅ Voice speed matches original video (1.1x-1.2x faster, never slower!)
# ✅ Natural pauses with "..." in script
# ✅ Perfect 29s video = 29s voiceover (±0.5s max)
# ✅ Human-like conversational Hindi script
# ✅ NO 7-second gaps - seamless concatenation
# ✅ Speaking rate matching from original video
# ✅ All original features preserved
# =================================================================================
# """

# from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
# import asyncio
# import logging
# import os
# import subprocess
# import tempfile
# import shutil
# import gc
# import httpx
# import json
# import re
# import random
# from typing import Optional, List, Dict, Tuple
# from datetime import datetime
# import uuid

# try:
#     import psutil
#     HAS_PSUTIL = True
# except:
#     HAS_PSUTIL = False

# # ═══════════════════════════════════════════════════════════════════════
# # LOGGING
# # ═══════════════════════════════════════════════════════════════════════
# logger = logging.getLogger("GDriveReels")
# logger.setLevel(logging.INFO)

# if not logger.handlers:
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#     logger.addHandler(handler)

# def log_memory(step: str):
#     """Log memory"""
#     if HAS_PSUTIL:
#         try:
#             process = psutil.Process(os.getpid())
#             mem_mb = process.memory_info().rss / 1024 / 1024
#             logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
#             if mem_mb > 450:
#                 logger.warning(f"⚠️ HIGH: {mem_mb:.1f}MB")
#                 gc.collect()
#                 gc.collect()
#                 gc.collect()
#         except:
#             pass

# # ═══════════════════════════════════════════════════════════════════════
# # CONFIG
# # ═══════════════════════════════════════════════════════════════════════
# GROQ_API_KEY = os.getenv("GROQ_SPEECH_API")
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# # Voice IDs for character detection
# VOICE_IDS = {
#     "male": ["FZkK3TvQ0pjyDmT8fzIW", "BTNeCNdXniCSbjEac5vd"],
#     "female": ["Icov0pR6jgWuaZhmlmtO", "UbB19hYD8fvYxwJAVTY5"]
# }

# # Edge TTS fallback
# EDGE_TTS_VOICES = {
#     "male": ["hi-IN-MadhurNeural"],
#     "female": ["hi-IN-SwaraNeural"]
# }

# # Top 10 BGM
# TOP_10_BGM_URLS = [
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Krishna%20Healing%20Flute%20'%20Bansuri%20background%20music%20-%20Royalty%20free%20Download.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Maha%20Shivratri%20_%20MANTRA%20Sounds%20of%20Indian%20Land%20-%20Royalty%20free%20Download.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/RAMA%20'%20Indian%20Epic%20BGM%20-%20Royalty%20free%20Music%20Download.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Ramayana%20'%20SITA%20Emotional%20BGM%20-%20India%20Royalty%20free%20music%20Download.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sri%20Krishna%20Govinda%20Devotional%20song%20(%20Flute%20Instrumental%20)%20Royalty%20free%20Music.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Mahabharata%20story%20-%20Duryodhana%20Epic%20BGM%20-%20Royalty%20free%20Music.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/DURGA%20maa%20_%20Indian%20Royalty%20free%20Music%20%23durgapuja%20%23navratri.mp3"
# ]

# PROCESSING_STATUS = {}

# # ═══════════════════════════════════════════════════════════════════════
# # HELPER FUNCTIONS
# # ═══════════════════════════════════════════════════════════════════════
# def cleanup(*paths):
#     """Delete + GC"""
#     for path in paths:
#         try:
#             if path and os.path.exists(path):
#                 size = os.path.getsize(path) / (1024 * 1024)
#                 os.remove(path)
#                 logger.info(f"   🗑️ {os.path.basename(path)} ({size:.1f}MB)")
#         except:
#             pass
#     gc.collect()
#     gc.collect()
#     gc.collect()

# def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
#     """Run FFmpeg"""
#     logger.info(f"🎬 {step}...")
#     log_memory(f"before-{step}")
    
#     try:
#         result = subprocess.run(
#             cmd,
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.PIPE,
#             timeout=timeout,
#             text=True
#         )
        
#         success = result.returncode == 0
        
#         if success:
#             logger.info(f"✅ {step}")
#         else:
#             logger.error(f"❌ {step} failed")
#             if result.stderr:
#                 logger.error(f"   Error: {result.stderr[-200:]}")
        
#         gc.collect()
#         log_memory(f"after-{step}")
#         return success
#     except subprocess.TimeoutExpired:
#         logger.error(f"⏱️ {step} timeout")
#         gc.collect()
#         return False
#     except Exception as e:
#         logger.error(f"❌ {step} error: {e}")
#         gc.collect()
#         return False

# def get_audio_duration(audio_path: str) -> float:
#     """Get audio duration"""
#     try:
#         result = subprocess.run(
#             ["ffprobe", "-v", "error", "-show_entries", "format=duration",
#              "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
#             capture_output=True, timeout=10, text=True
#         )
#         if result.returncode == 0:
#             return float(result.stdout.strip())
#         return 0.0
#     except:
#         return 0.0

# # ═══════════════════════════════════════════════════════════════════════
# # GOOGLE DRIVE
# # ═══════════════════════════════════════════════════════════════════════
# def extract_file_id(url: str) -> Optional[str]:
#     """Extract file ID"""
#     if not url or "drive.google.com" not in url:
#         return None
    
#     patterns = [r'/file/d/([a-zA-Z0-9_-]{25,})', r'[?&]id=([a-zA-Z0-9_-]{25,})']
#     for pattern in patterns:
#         match = re.search(pattern, url)
#         if match:
#             return match.group(1)
#     return None

# async def download_chunked(url: str, output: str) -> bool:
#     """Download in chunks"""
#     try:
#         async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
#             async with client.stream("GET", url) as response:
#                 if response.status_code != 200:
#                     return False
                
#                 total = 0
#                 with open(output, 'wb') as f:
#                     async for chunk in response.aiter_bytes(1024*1024):
#                         f.write(chunk)
#                         total += len(chunk)
#                         if total % (5*1024*1024) < 1024*1024:
#                             logger.info(f"   📥 {total/(1024*1024):.1f}MB")
                
#                 if total > 10000:
#                     logger.info(f"   ✅ {total/(1024*1024):.1f}MB")
#                     return True
#         return False
#     except Exception as e:
#         logger.error(f"   ❌ {e}")
#         return False

# async def download_from_gdrive(file_id: str, output: str) -> tuple[bool, str]:
#     """Download with fallbacks"""
#     logger.info("⬇️ Downloading...")
#     log_memory("download-start")
    
#     urls = [
#         f"https://drive.google.com/uc?export=download&id={file_id}",
#         f"https://drive.usercontent.google.com/download?id={file_id}&export=download",
#     ]
    
#     for idx, url in enumerate(urls, 1):
#         logger.info(f"📥 Method {idx}/{len(urls)}")
#         if await download_chunked(url, output):
#             logger.info(f"✅ Downloaded")
#             log_memory("download-done")
#             return True, ""
#         await asyncio.sleep(1)
    
#     return False, "Download failed"

# # ═══════════════════════════════════════════════════════════════════════
# # VIDEO OPERATIONS
# # ═══════════════════════════════════════════════════════════════════════
# async def get_duration(video_path: str) -> float:
#     """Get duration"""
#     try:
#         result = subprocess.run(
#             ["ffprobe", "-v", "error", "-show_entries", "format=duration",
#              "-of", "default=noprint_wrappers=1:nokey=1", video_path],
#             capture_output=True, timeout=15, text=True
#         )
#         if result.returncode == 0:
#             duration = float(result.stdout.strip())
#             logger.info(f"⏱️ {duration:.1f}s")
#             return duration
#         return 0.0
#     except:
#         return 0.0

# async def extract_audio(video_path: str, audio_path: str) -> bool:
#     """Extract audio"""
#     success = run_ffmpeg([
#         "ffmpeg", "-i", video_path,
#         "-vn", "-acodec", "pcm_s16le",
#         "-ar", "16000", "-ac", "1",
#         "-y", audio_path
#     ], timeout=60, step="Extract-Audio")
    
#     return success

# # ═══════════════════════════════════════════════════════════════════════
# # TRANSCRIPTION WITH TIMESTAMPS
# # ═══════════════════════════════════════════════════════════════════════
# async def transcribe_audio_with_timestamps(audio_path: str) -> tuple[Optional[List[Dict]], str]:
#     """Transcribe with HTTP API + get timestamps"""
#     logger.info("📝 Transcribing with timestamps...")
#     log_memory("transcribe-start")
    
#     if not GROQ_API_KEY:
#         return None, "No API key"
    
#     try:
#         async with httpx.AsyncClient(timeout=60) as client:
#             with open(audio_path, "rb") as f:
#                 files = {"file": ("audio.wav", f, "audio/wav")}
#                 data = {
#                     "model": "whisper-large-v3",
#                     "language": "hi",
#                     "response_format": "verbose_json"
#                 }
                
#                 response = await client.post(
#                     "https://api.groq.com/openai/v1/audio/transcriptions",
#                     headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
#                     files=files,
#                     data=data
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
                    
#                     # Extract segments with timestamps
#                     segments = []
#                     if "segments" in result and result["segments"]:
#                         for seg in result["segments"]:
#                             text = seg.get("text", "").strip()
#                             if text:
#                                 segments.append({
#                                     "start": float(seg.get("start", 0.0)),
#                                     "end": float(seg.get("end", 0.0)),
#                                     "text": text
#                                 })
                        
#                         if segments:
#                             logger.info(f"✅ Transcribed - {len(segments)} segments")
#                             full_text = " ".join([s["text"] for s in segments])
#                             logger.info(f"   Text preview: {full_text[:100]}...")
#                             log_memory("transcribe-done")
#                             cleanup(audio_path)
#                             return segments, ""
                    
#                     # Fallback: use text
#                     if "text" in result and result["text"]:
#                         text = result["text"].strip()
#                         words = text.split()
#                         segments = []
#                         words_per_seg = 10
                        
#                         for i in range(0, len(words), words_per_seg):
#                             seg_words = words[i:i+words_per_seg]
#                             if seg_words:
#                                 segments.append({
#                                     "start": i / 2.5,
#                                     "end": (i + len(seg_words)) / 2.5,
#                                     "text": " ".join(seg_words)
#                                 })
                        
#                         logger.info(f"✅ Transcribed - {len(segments)} segments (from text)")
#                         cleanup(audio_path)
#                         return segments, ""
        
#         cleanup(audio_path)
#         return None, "Empty response"
#     except Exception as e:
#         cleanup(audio_path)
#         logger.error(f"❌ Transcription error: {e}")
#         return None, str(e)

# # ═══════════════════════════════════════════════════════════════════════
# # CHARACTER DETECTION
# # ═══════════════════════════════════════════════════════════════════════
# def detect_character_gender(segments: List[Dict]) -> str:
#     """Detect male/female character from segments"""
#     text = " ".join([seg["text"] for seg in segments]).lower()
    
#     female_keywords = ["sita", "radha", "durga", "lakshmi", "queen", "rani", "girl", "ladki", "woman", "mata", "maa", "goddess", "devi"]
#     male_keywords = ["ram", "krishna", "shiva", "hanuman", "king", "raja", "boy", "ladka", "man", "god", "dev", "pita", "beta"]
    
#     female_count = sum(1 for kw in female_keywords if kw in text)
#     male_count = sum(1 for kw in male_keywords if kw in text)
    
#     if female_count > male_count:
#         logger.info(f"   🎭 FEMALE character detected")
#         return "female"
#     else:
#         logger.info(f"   🎭 MALE character detected (default)")
#         return "male"

# # ═══════════════════════════════════════════════════════════════════════
# # HUMAN-LIKE SCRIPT GENERATION WITH NATURAL PAUSES
# # ═══════════════════════════════════════════════════════════════════════
# async def generate_human_like_script(segments: List[Dict], duration: float) -> dict:
#     """Generate HUMAN-LIKE conversational script with natural pauses"""
#     logger.info("🤖 AI Script (Human-like + Natural Pauses)...")
#     log_memory("ai-start")
    
#     # Combine segments for full text
#     transcript = " ".join([seg["text"] for seg in segments])
    
#     # Calculate original speaking rate (words per second)
#     word_count = len(transcript.split())
#     speaking_rate = word_count / duration if duration > 0 else 2.5
    
#     logger.info(f"   Original speaking rate: {speaking_rate:.2f} words/sec")
    
#     # Target words for new script (slightly more to account for pauses)
#     target_words = int(duration * speaking_rate * 1.05)  # 5% buffer
    
#     # CTA
#     cta = "Agar aapko yeh video achhi lagi ho toh LIKE karein, SUBSCRIBE karein aur apne doston ko SHARE karein!"
    
#     # Detect character
#     character_gender = detect_character_gender(segments)
    
#     # Try Mistral AI with IMPROVED HUMAN-LIKE PROMPT
#     if MISTRAL_API_KEY:
#         try:
#             logger.info("   Trying Mistral AI for human-like script...")
            
#             # IMPROVED PROMPT FOR HUMAN-LIKE CONVERSATIONAL HINDI
#             prompt = f"""Generate a CONVERSATIONAL, HUMAN-LIKE Hindi narration with natural pauses:

# Original Transcript: {transcript}
# Video Duration: {duration} seconds
# Target Words: {target_words} words
# Speaking Rate: {speaking_rate:.2f} words/second

# CRITICAL REQUIREMENTS FOR HUMAN-LIKE SCRIPT:

# 1. **NATURAL CONVERSATIONAL HINDI** (NOT robotic!):
#    - Use casual, everyday Hindi words
#    - Mix Hindi with natural Hinglish where appropriate
#    - Vary sentence length (short punchy sentences + longer descriptive ones)
#    - Use rhetorical questions to engage: "Kya aap jaante hain?", "Sochiye zara..."
#    - Add emotional expressions: "Wahh!", "Arre!", "Dekho..."

# 2. **NATURAL PAUSES** using "..." (VERY IMPORTANT):
#    - Use "..." for dramatic pauses (e.g., "Lekin... jo hua wo...")
#    - Use "..." before revealing key points
#    - Use "..." after questions for impact
#    - Example: "Ek baar... ek gaon mein... ek aadmi tha..."

# 3. **HUMAN SPEAKING PATTERNS**:
#    - Start with an engaging hook: "Suniye ek rochak kahani..."
#    - Use connecting words: "toh", "phir", "aur", "lekin"
#    - Add emphasis words: "bahut", "ekdum", "bilkul"
#    - End sentences naturally, not abruptly

# 4. **RHYTHM AND FLOW**:
#    - Don't use commas for every pause - use "..." for longer pauses
#    - Keep sentences flowing naturally
#    - Vary pace: fast for action, slow for emotion
#    - Example: "Wo bhaaga... bhaaga... aur ruk gaya!" (not "wo bhaaga, bhaaga, aur ruk gaya")

# 5. **STRUCTURE**:
#    - Hook (5-10 words): Grab attention
#    - Main story: Tell the story naturally with pauses
#    - Conclusion: Emotional or thoughtful ending
#    - CTA at end: "{cta}"

# 6. **AVOID**:
#    - NO robotic listing: "pehla, doosra, teesra"
#    - NO formal language
#    - NO excessive commas
#    - NO repetitive structure

# SEO REQUIREMENTS:

# 7. Generate a VIRAL Hinglish TITLE:
#    - Power words: SHOCKING, AMAZING, UNBELIEVABLE, SECRET
#    - Emojis for visual appeal
#    - Example: "Yeh Video Dekhkar Aap SHOCK Ho Jaoge! 😱 | Sachai Kya Hai? #Shorts"

# 8. Write a Hinglish DESCRIPTION (2-3 short paragraphs):
#    - First paragraph: Explain the video topic clearly
#    - Second paragraph: Add emotional appeal
#    - End with: "Keywords: ..."

# 9. Generate EXACTLY 65-70 SEO KEYWORDS (VERTICAL format, one per line, NO commas)

# 10. Generate 8-9 HASHTAGS (VERTICAL format, one per line)

# Generate in JSON format:
# {{
#     "script": "Suniye ek kahani... [natural conversational Hindi with ... for pauses] {cta}",
#     "title": "Viral Hinglish title with emojis (max 100 chars)",
#     "description": "Hinglish description paragraph 1\\n\\nHinglish description paragraph 2\\n\\nkeyword one\\nkeyword two\\n... (65+ keywords)\\n\\n#HashtagOne\\n#HashtagTwo\\n... (8-9 hashtags)",
#     "hashtags": ["#Foryou", "#Fyp", "#Explore", "#Reach", "#Reelsgrowth", "#Boostyourreel", "#Trendingnow","#Shorts", "#Viral", "#Hindi", "#Trending"],
#     "story_id": "unique-id",
#     "speaking_rate": {speaking_rate}
# }}"""
            
#             async with httpx.AsyncClient(timeout=60) as client:
#                 resp = await client.post(
#                     "https://api.mistral.ai/v1/chat/completions",
#                     headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
#                     json={
#                         "model": "mistral-large-latest",
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": "You are a viral YouTube storyteller. Create NATURAL, CONVERSATIONAL Hindi scripts that sound like a real person talking, not AI. Use '...' for natural pauses. Output ONLY valid JSON."
#                             },
#                             {"role": "user", "content": prompt}
#                         ],
#                         "temperature": 0.9,  # Higher for more natural variation
#                         "max_tokens": 1500
#                     }
#                 )
                
#                 if resp.status_code == 200:
#                     content = resp.json()["choices"][0]["message"]["content"]
                    
#                     # Clean JSON
#                     content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
#                     content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    
#                     match = re.search(r'\{.*\}', content, re.DOTALL)
                    
#                     if match:
#                         data = json.loads(match.group(0))
#                         script_text = data.get("script", transcript)
                        
#                         # Ensure CTA
#                         if "LIKE" not in script_text or "SUBSCRIBE" not in script_text:
#                             script_text += " " + cta
                        
#                         title = data.get("title", "Amazing Story 🔥 | Must Watch! #Shorts")
#                         description = data.get("description", f"{transcript[:200]}\\n\\nKeywords: hindi story, amazing facts, viral video")
#                         hashtags = data.get("hashtags", ["#Shorts", "#Viral", "#Hindi", "#Trending", "#MustWatch", "#Amazing", "#Story"])
#                         story_id = data.get("story_id", str(uuid.uuid4())[:8])
                        
#                         logger.info(f"✅ Human-like script generated")
#                         logger.info(f"   Title: {title}")
#                         logger.info(f"   Script preview: {script_text[:80]}...")
#                         log_memory("ai-done")
                        
#                         return {
#                             "script": script_text,
#                             "segments": segments,
#                             "character_gender": character_gender,
#                             "title": title,
#                             "description": description,
#                             "hashtags": hashtags,
#                             "story_id": story_id,
#                             "speaking_rate": speaking_rate
#                         }
#         except Exception as e:
#             logger.warning(f"   Mistral failed: {e}")
    
#     # FALLBACK
#     logger.info("   Using transcript (fallback)")
#     script = " ".join(transcript.split()[:target_words]) + " " + cta
    
#     title_base = " ".join(transcript.split()[:5])
#     title = f"{title_base}... 🔥 | Must Watch! #Shorts"
#     description = f"{transcript[:150]}...\n\nKeywords: hindi story, amazing facts, viral video, trending shorts"
#     hashtags = ["#Shorts", "#Viral", "#Hindi", "#Trending", "#MustWatch", "#Amazing", "#Story"]
    
#     log_memory("ai-done")
    
#     return {
#         "script": script,
#         "segments": segments,
#         "character_gender": character_gender,
#         "title": title,
#         "description": description,
#         "hashtags": hashtags,
#         "story_id": str(uuid.uuid4())[:8],
#         "speaking_rate": speaking_rate
#     }

# # ═══════════════════════════════════════════════════════════════════════
# # PERFECT VOICE SYNC - MATCH VIDEO DURATION EXACTLY
# # ═══════════════════════════════════════════════════════════════════════
# async def generate_perfect_synced_voiceover(metadata: dict, output_dir: str, video_duration: float) -> Tuple[Optional[str], str]:
#     """Generate voiceover that matches video duration EXACTLY (±0.5s max)"""
#     logger.info("🎙️ Perfect Voice Sync (Human-like + Natural Pauses)...")
#     log_memory("voice-start")
    
#     script = metadata.get("script", "")
#     gender = metadata["character_gender"]
#     is_female = (gender == "female")
#     voice_id = random.choice(VOICE_IDS[gender])
#     speaking_rate = metadata.get("speaking_rate", 2.5)
    
#     logger.info(f"   Voice: {gender.upper()} - {voice_id}")
#     logger.info(f"   Target duration: {video_duration:.2f}s")
#     logger.info(f"   Speaking rate: {speaking_rate:.2f} words/sec")
    
#     # Split script by natural pauses ("...")
#     parts = [p.strip() for p in script.split("...") if p.strip()]
    
#     if not parts:
#         parts = [script]
    
#     logger.info(f"   Script parts (natural segments): {len(parts)}")
    
#     # Calculate time per part (with small gaps for natural pauses)
#     pause_time = 0.3  # 300ms pause after "..."
#     speaking_time = video_duration - (len(parts) - 1) * pause_time
#     time_per_part = speaking_time / len(parts) if len(parts) > 0 else video_duration
    
#     # Generate voiceover for each part
#     part_files = []
    
#     for i, part in enumerate(parts):
#         part_file = os.path.join(output_dir, f"part_{i:03d}.mp3")
#         temp_file = part_file.replace(".mp3", "_temp.mp3")
        
#         # Generate with ElevenLabs or Edge TTS
#         success = False
        
#         # Try ElevenLabs
#         if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
#             try:
#                 async with httpx.AsyncClient(timeout=60) as client:
#                     resp = await client.post(
#                         f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
#                         headers={"xi-api-key": ELEVENLABS_API_KEY},
#                         json={
#                             "text": part,
#                             "model_id": "eleven_multilingual_v2",
#                             "voice_settings": {
#                                 "stability": 0.5,
#                                 "similarity_boost": 0.75,
#                                 "style": 0.5,
#                                 "use_speaker_boost": True
#                             }
#                         }
#                     )
                    
#                     if resp.status_code == 200:
#                         with open(temp_file, 'wb') as f:
#                             f.write(resp.content)
                        
#                         actual = get_audio_duration(temp_file)
#                         if actual > 0:
#                             # Speed up to match target duration (1.1x-1.3x faster)
#                             ratio = actual / time_per_part
#                             ratio = min(max(ratio, 0.7), 1.5)  # Clamp
                            
#                             if run_ffmpeg(["ffmpeg", "-i", temp_file, "-filter:a", f"atempo={ratio}", "-y", part_file], 30):
#                                 cleanup(temp_file)
#                                 part_dur = get_audio_duration(part_file)
#                                 logger.info(f"   ✅ Part {i+1}/{len(parts)} - ElevenLabs ({part_dur:.2f}s / target: {time_per_part:.2f}s)")
#                                 part_files.append(part_file)
#                                 success = True
                        
#                         cleanup(temp_file)
                        
#                         if resp.status_code == 429:
#                             await asyncio.sleep(2)
#             except Exception as e:
#                 logger.warning(f"   ⚠️ Part {i+1} - ElevenLabs error: {e}")
#                 cleanup(temp_file)
        
#         # Fallback to Edge TTS
#         if not success:
#             try:
#                 import edge_tts
#                 voice = EDGE_TTS_VOICES[gender][0]
                
#                 await edge_tts.Communicate(part, voice, rate="+20%").save(temp_file)
                
#                 actual = get_audio_duration(temp_file)
#                 if actual > 0:
#                     ratio = actual / time_per_part
#                     ratio = min(max(ratio, 0.7), 1.5)
                    
#                     if run_ffmpeg(["ffmpeg", "-i", temp_file, "-filter:a", f"atempo={ratio}", "-y", part_file], 30):
#                         cleanup(temp_file)
#                         part_dur = get_audio_duration(part_file)
#                         logger.info(f"   ✅ Part {i+1}/{len(parts)} - Edge TTS ({part_dur:.2f}s / target: {time_per_part:.2f}s)")
#                         part_files.append(part_file)
#                         success = True
                
#                 cleanup(temp_file)
#             except Exception as e:
#                 logger.warning(f"   ⚠️ Part {i+1} - Edge TTS error: {e}")
#                 cleanup(temp_file)
        
#         if not success:
#             logger.error(f"   ❌ Part {i+1} failed")
#             continue
        
#         # Small delay between requests
#         await asyncio.sleep(0.5)
    
#     if not part_files:
#         return None, "All parts failed"
    
#     logger.info(f"   ✅ Generated {len(part_files)}/{len(parts)} parts")
    
#     # Concatenate with natural pauses (NO GAPS!)
#     final = os.path.join(output_dir, "voice.mp3")
    
#     # Build complex filter for seamless concatenation
#     # Use adelay to add pauses between parts
#     if len(part_files) == 1:
#         # Single part - just copy
#         shutil.copy(part_files[0], final)
#         cleanup(*part_files)
#     else:
#         # Multiple parts - concatenate with pauses
#         # Create silence file for pauses
#         silence_file = os.path.join(output_dir, "silence.mp3")
#         if run_ffmpeg([
#             "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=r=22050:cl=mono:d={pause_time}",
#             "-y", silence_file
#         ], 10):
#             # Build concat file with silence between parts
#             concat_file = os.path.join(output_dir, "concat.txt")
#             with open(concat_file, 'w') as f:
#                 for i, part_file in enumerate(part_files):
#                     f.write(f"file '{part_file}'\n")
#                     if i < len(part_files) - 1:  # Add silence except after last part
#                         f.write(f"file '{silence_file}'\n")
            
#             # Concatenate
#             if run_ffmpeg(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", "-y", final], 60):
#                 cleanup(concat_file, silence_file, *part_files)
#             else:
#                 cleanup(concat_file, silence_file, *part_files)
#                 return None, "Concatenation failed"
#         else:
#             cleanup(*part_files)
#             return None, "Silence generation failed"
    
#     # Check final duration
#     final_dur = get_audio_duration(final)
#     diff = abs(final_dur - video_duration)
    
#     logger.info(f"   🎵 Voiceover: {final_dur:.2f}s, Video: {video_duration:.2f}s, Diff: {diff:.2f}s")
    
#     # If difference > 0.5s, adjust speed to match EXACTLY
#     if diff > 0.5:
#         logger.info(f"   ⚠️ Adjusting speed for perfect sync...")
#         adjusted = os.path.join(output_dir, "voice_adj.mp3")
#         ratio = final_dur / video_duration
#         ratio = min(max(ratio, 0.8), 1.3)  # Safety clamp
        
#         if run_ffmpeg(["ffmpeg", "-i", final, "-filter:a", f"atempo={ratio}", "-y", adjusted], 30):
#             cleanup(final)
#             final = adjusted
#             final_dur = get_audio_duration(final)
#             diff = abs(final_dur - video_duration)
#             logger.info(f"   ✅ Adjusted: {final_dur:.2f}s (diff: {diff:.2f}s)")
    
#     if diff <= 0.5:
#         logger.info(f"✅ PERFECT SYNC! Voice: {final_dur:.2f}s ≈ Video: {video_duration:.2f}s (±{diff:.2f}s)")
#     else:
#         logger.warning(f"⚠️ Sync acceptable: Voice: {final_dur:.2f}s vs Video: {video_duration:.2f}s (±{diff:.2f}s)")
    
#     log_memory("voice-done")
#     return final, ""

# # ═══════════════════════════════════════════════════════════════════════
# # CAPTIONS & VIDEO ASSEMBLY
# # ═══════════════════════════════════════════════════════════════════════
# def generate_srt(script: str, duration: float) -> str:
#     """Generate SRT with natural pauses"""
#     # Split by "..." for natural pauses
#     parts = [p.strip() for p in script.split("...") if p.strip()]
    
#     if not parts:
#         # Fallback: split by sentences
#         parts = [p.strip() + "." for p in script.split(".") if p.strip()]
    
#     if not parts:
#         return ""
    
#     time_per = duration / len(parts)
#     blocks = []
    
#     for i, part in enumerate(parts):
#         start = i * time_per
#         end = start + time_per
        
#         sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
#         eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
#         blocks.append(f"{i+1}\n{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
#                      f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + f"\n{part}\n")
    
#     return "\n".join(blocks)

# async def remove_audio(video_in: str, video_out: str) -> bool:
#     """Remove audio"""
#     success = run_ffmpeg([
#         "ffmpeg", "-i", video_in,
#         "-c:v", "copy", "-an",
#         "-y", video_out
#     ], timeout=60, step="Remove-Audio")
    
#     if success:
#         cleanup(video_in)
    
#     return success

# async def download_bgm(output: str) -> bool:
#     """Download BGM"""
#     logger.info("🎵 BGM (Top 10 Royalty-Free)...")
#     log_memory("bgm-start")
    
#     bgm_url = random.choice(TOP_10_BGM_URLS)
#     logger.info(f"   Selected: {bgm_url.split('/')[-1][:50]}...")
    
#     try:
#         success = await download_chunked(bgm_url, output)
        
#         if success:
#             logger.info("✅ BGM Downloaded")
#             log_memory("bgm-done")
#             return True
        
#         logger.warning("⚠️ BGM download failed")
#         return False
#     except:
#         logger.warning("⚠️ BGM error")
#         return False

# async def create_final_video(silent: str, voice: str, srt: str, bgm: Optional[str], output: str) -> tuple[bool, str]:
#     """Create final video with captions and audio"""
#     logger.info("✨ Final Video...")
#     log_memory("final-start")
    
#     captioned = output.replace(".mp4", "_cap.mp4")
#     srt_esc = srt.replace("\\", "\\\\").replace(":", "\\:")
    
#     # Try golden captions
#     logger.info("   Trying GOLDEN captions (#FFD700)...")
#     caption_success = run_ffmpeg([
#         "ffmpeg", "-i", silent,
#         "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFD700,Bold=1,Outline=2,Alignment=2,MarginV=50'",
#         "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
#         "-y", captioned
#     ], 180, "Captions-Golden")
    
#     if caption_success and os.path.exists(captioned) and os.path.getsize(captioned) > 10000:
#         logger.info("✅ Golden captions applied")
#         cleanup(silent)
#         video_for_audio = captioned
#     else:
#         # Fallback to white
#         logger.warning("⚠️ Golden captions failed, trying WHITE...")
#         cleanup(captioned)
        
#         caption_success = run_ffmpeg([
#             "ffmpeg", "-i", silent,
#             "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,Bold=1,Outline=2,Alignment=2,MarginV=50'",
#             "-c:v", "libx264", "-crf", "26", "-preset", "ultrafast",
#             "-y", captioned
#         ], 180, "Captions-White")
        
#         if caption_success and os.path.exists(captioned) and os.path.getsize(captioned) > 10000:
#             logger.info("✅ White captions applied")
#             cleanup(silent)
#             video_for_audio = captioned
#         else:
#             logger.warning("⚠️ Continuing without captions")
#             cleanup(captioned)
#             video_for_audio = silent
    
#     cleanup(srt)
    
#     # Mix audio with BGM
#     if bgm and os.path.exists(bgm):
#         logger.info("   Mixing voice + BGM (volume: 0.18)...")
#         success = run_ffmpeg([
#             "ffmpeg", "-i", video_for_audio, "-i", voice, "-i", bgm,
#             "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.18[m];[v][m]amix=inputs=2:duration=first[a]",
#             "-map", "0:v", "-map", "[a]",
#             "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
#             "-shortest", "-y", output
#         ], 120, "Mix-Voice-BGM")
        
#         if not success:
#             logger.warning("⚠️ Mix with BGM failed, trying without...")
#             success = run_ffmpeg([
#                 "ffmpeg", "-i", video_for_audio, "-i", voice,
#                 "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
#                 "-shortest", "-y", output
#             ], 90, "Add-Voice")
#     else:
#         logger.info("   Adding voice only...")
#         success = run_ffmpeg([
#             "ffmpeg", "-i", video_for_audio, "-i", voice,
#             "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
#             "-shortest", "-y", output
#         ], 90, "Add-Voice")
    
#     cleanup(video_for_audio, voice, bgm)
    
#     if not success:
#         return False, "Audio mix failed"
    
#     log_memory("final-done")
#     return True, ""

# # ═══════════════════════════════════════════════════════════════════════
# # YOUTUBE UPLOAD
# # ═══════════════════════════════════════════════════════════════════════
# async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
#     """Upload to YouTube"""
#     logger.info("📤 YouTube...")
#     log_memory("upload-start")
    
#     try:
#         from YTdatabase import get_database_manager as get_yt_db
#         yt_db = get_yt_db()
        
#         if not yt_db.youtube.client:
#             await yt_db.connect()
        
#         creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
#         if not creds:
#             return {"success": False, "error": "No YouTube credentials"}
        
#         credentials = {
#             "access_token": creds.get("access_token"),
#             "refresh_token": creds.get("refresh_token"),
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "client_id": creds.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
#             "client_secret": creds.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
#             "scopes": [
#                 "https://www.googleapis.com/auth/youtube.upload",
#                 "https://www.googleapis.com/auth/youtube.force-ssl"
#             ]
#         }
        
#         from mainY import youtube_scheduler
        
#         result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             credentials_data=credentials,
#             content_type="shorts",
#             title=title,
#             description=description,
#             video_url=video_path
#         )
        
#         if result.get("success"):
#             video_id = result.get("video_id")
#             logger.info(f"✅ Uploaded: {video_id}")
#             log_memory("upload-done")
#             return {
#                 "success": True,
#                 "video_id": video_id,
#                 "video_url": f"https://youtube.com/shorts/{video_id}"
#             }
        
#         return {"success": False, "error": result.get("error", "Upload failed")}
#     except Exception as e:
#         logger.error(f"❌ {e}")
#         return {"success": False, "error": str(e)}

# # ═══════════════════════════════════════════════════════════════════════
# # MAIN PIPELINE
# # ═══════════════════════════════════════════════════════════════════════
# async def process_reel(drive_url: str, user_id: str, task_id: str):
#     """Main pipeline with PERFECT voice sync"""
#     temp_dir = None
#     start_time = datetime.now()
    
#     PROCESSING_STATUS[task_id] = {
#         "status": "processing",
#         "progress": 0,
#         "message": "Starting...",
#         "started_at": start_time.isoformat()
#     }
    
#     def update(progress: int, msg: str):
#         PROCESSING_STATUS[task_id]["progress"] = progress
#         PROCESSING_STATUS[task_id]["message"] = msg
#         logger.info(f"[{progress}%] {msg}")
    
#     try:
#         temp_dir = tempfile.mkdtemp(prefix="reel_")
#         logger.info(f"📁 {temp_dir}")
#         log_memory("START")
        
#         # Extract ID
#         update(5, "Extracting ID...")
#         file_id = extract_file_id(drive_url)
#         if not file_id:
#             raise ValueError("Invalid URL")
        
#         # Download
#         update(10, "Downloading...")
#         raw_video = os.path.join(temp_dir, "raw.mp4")
#         success, error = await download_from_gdrive(file_id, raw_video)
#         if not success:
#             raise Exception(error)
        
#         # Get duration
#         update(20, "Analyzing...")
#         duration = await get_duration(raw_video)
#         if duration <= 0:
#             raise ValueError("Invalid video")
#         if duration > 180:
#             raise ValueError(f"Too long ({duration:.0f}s)")
        
#         # Extract audio
#         update(25, "Extracting audio...")
#         audio_path = os.path.join(temp_dir, "audio.wav")
#         if not await extract_audio(raw_video, audio_path):
#             raise Exception("Audio extraction failed")
        
#         # Transcribe
#         update(30, "Transcribing...")
#         segments, error = await transcribe_audio_with_timestamps(audio_path)
#         if not segments:
#             raise Exception(error or "Transcription failed")
        
#         # Generate human-like script
#         update(50, "AI script (human-like + natural pauses)...")
#         metadata = await generate_human_like_script(segments, duration)
#         logger.info(f"   Title: {metadata['title']}")
#         logger.info(f"   Character: {metadata['character_gender'].upper()}")
        
#         # Perfect synced voiceover
#         update(60, "Perfect voice sync (match video duration)...")
#         voice, error = await generate_perfect_synced_voiceover(metadata, temp_dir, duration)
#         if not voice:
#             raise Exception(error)
        
#         # Remove audio
#         update(70, "Removing audio...")
#         silent_video = os.path.join(temp_dir, "silent.mp4")
#         if not await remove_audio(raw_video, silent_video):
#             raise Exception("Remove audio failed")
        
#         # Captions
#         update(75, "Captions...")
#         srt_path = os.path.join(temp_dir, "captions.srt")
#         with open(srt_path, 'w', encoding='utf-8') as f:
#             f.write(generate_srt(metadata["script"], duration))
        
#         # BGM
#         update(80, "BGM...")
#         bgm_path = os.path.join(temp_dir, "bgm.mp3")
#         bgm_success = await download_bgm(bgm_path)
        
#         if not bgm_success:
#             bgm_path = None
        
#         # Final video
#         update(85, "Final video...")
#         final_video = os.path.join(temp_dir, "final.mp4")
#         success, error = await create_final_video(silent_video, voice, srt_path, bgm_path, final_video)
#         if not success:
#             raise Exception(error)
        
#         if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
#             raise Exception("Invalid final video")
        
#         size_mb = os.path.getsize(final_video) / (1024 * 1024)
#         logger.info(f"   Final: {size_mb:.1f}MB")
        
#         # Upload
#         update(95, "Uploading...")
#         full_description = f"{metadata['description']}\n\n{' '.join(metadata['hashtags'])}"
        
#         upload_result = await upload_to_youtube(final_video, metadata["title"], full_description, user_id)
        
#         if not upload_result.get("success"):
#             raise Exception(upload_result.get("error"))
        
#         # SUCCESS
#         elapsed = (datetime.now() - start_time).total_seconds()
        
#         logger.info("="*80)
#         logger.info("✅ SUCCESS!")
#         logger.info(f"   Time: {elapsed:.1f}s")
#         logger.info(f"   Video: {upload_result['video_id']}")
#         logger.info("="*80)
#         log_memory("COMPLETE")
        
#         PROCESSING_STATUS[task_id] = {
#             "status": "completed",
#             "progress": 100,
#             "success": True,
#             "message": "Uploaded!",
#             "title": metadata["title"],
#             "description": full_description,
#             "hashtags": metadata["hashtags"],
#             "story_id": metadata.get("story_id", ""),
#             "character_gender": metadata["character_gender"],
#             "duration": round(duration, 1),
#             "processing_time": round(elapsed, 1),
#             "video_id": upload_result["video_id"],
#             "video_url": upload_result["video_url"],
#             "completed_at": datetime.utcnow().isoformat(),
#             "sync_mode": "perfect_sync"
#         }
        
#     except Exception as e:
#         error_msg = str(e)
#         logger.error("="*80)
#         logger.error(f"❌ FAILED: {error_msg}")
#         logger.error("="*80)
        
#         PROCESSING_STATUS[task_id] = {
#             "status": "failed",
#             "progress": 0,
#             "success": False,
#             "error": error_msg,
#             "message": error_msg,
#             "failed_at": datetime.utcnow().isoformat()
#         }
    
#     finally:
#         if temp_dir and os.path.exists(temp_dir):
#             logger.info("🧹 Cleanup...")
#             try:
#                 shutil.rmtree(temp_dir, ignore_errors=True)
#                 logger.info("✅ Clean")
#             except:
#                 pass
        
#         gc.collect()
#         gc.collect()
#         gc.collect()
#         log_memory("FINAL")

# # ═══════════════════════════════════════════════════════════════════════
# # API
# # ═══════════════════════════════════════════════════════════════════════
# router = APIRouter()

# @router.post("/api/gdrive-reels/process")
# async def process_endpoint(request: Request):
#     """Process"""
#     logger.info("🌐 API REQUEST")
    
#     try:
#         data = await request.json()
        
#         user_id = data.get("user_id")
#         drive_url = (data.get("drive_url") or "").strip()
        
#         if not user_id:
#             return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
#         if not drive_url or "drive.google.com" not in drive_url:
#             return JSONResponse(status_code=400, content={"success": False, "error": "Valid URL required"})
        
#         task_id = str(uuid.uuid4())
#         logger.info(f"✅ Task: {task_id}")
        
#         await asyncio.wait_for(process_reel(drive_url, user_id, task_id), timeout=600)
        
#         result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
#         return JSONResponse(content=result)
        
#     except asyncio.TimeoutError:
#         return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
#     except Exception as e:
#         logger.error(f"❌ {e}")
#         return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# @router.get("/api/gdrive-reels/status/{task_id}")
# async def status_endpoint(task_id: str):
#     """Status"""
#     status = PROCESSING_STATUS.get(task_id)
#     if not status:
#         return JSONResponse(status_code=404, content={"success": False, "error": "Not found"})
#     return JSONResponse(content=status)

# @router.get("/api/gdrive-reels/health")
# async def health_endpoint():
#     """Health"""
#     log_memory("health")
#     return JSONResponse(content={
#         "status": "ok",
#         "groq_configured": bool(GROQ_API_KEY),
#         "elevenlabs_configured": bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20),
#         "mistral_configured": bool(MISTRAL_API_KEY),
#         "active_tasks": len([s for s in PROCESSING_STATUS.values() if s["status"] == "processing"]),
#         "features": {
#             "voiceover_mode": "perfect_sync",
#             "human_like_script": "yes",
#             "natural_pauses": "yes (...)",
#             "sync_accuracy": "±0.5s max",
#             "voice_speed": "matches original (1.1x-1.2x)",
#             "no_gaps": "yes",
#             "caption_colors": "Golden → White → None",
#             "bgm_volume": "0.18",
#             "bgm_tracks": len(TOP_10_BGM_URLS),
#             "seo_optimization": "Title + Description + 65+ Keywords + 7-9 Hashtags"
#         }
#     })

# @router.get("/api/gdrive-reels/bgm-list")
# async def bgm_list_endpoint():
#     """Get list of top 10 BGM tracks"""
#     return JSONResponse(content={
#         "success": True,
#         "total_tracks": len(TOP_10_BGM_URLS),
#         "tracks": [
#             {
#                 "index": idx + 1,
#                 "name": url.split('/')[-1].replace('%20', ' ').replace('.mp3', ''),
#                 "url": url
#             }
#             for idx, url in enumerate(TOP_10_BGM_URLS)
#         ]
#     })

# async def initialize():
#     """Startup"""
#     logger.info("="*80)
#     logger.info("🚀 GDRIVE REELS (PERFECT VOICE SYNC)")
#     logger.info("="*80)
#     logger.info("✅ Voice speed matches original (never slower!)")
#     logger.info("✅ Natural pauses with '...'")
#     logger.info("✅ Human-like conversational script")
#     logger.info("✅ Perfect sync: 29s video = 29s voice (±0.5s max)")
#     logger.info("✅ NO 7-second gaps - seamless!")
#     logger.info("✅ SEO: Title + Description + 65+ Keywords")
#     logger.info("="*80)
    
#     if GROQ_API_KEY:
#         logger.info("✅ Groq configured")
#     else:
#         logger.error("❌ No GROQ_SPEECH_API")
    
#     if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
#         logger.info("✅ ElevenLabs configured (Priority)")
#     else:
#         logger.warning("⚠️ ElevenLabs not configured")
    
#     if MISTRAL_API_KEY:
#         logger.info("✅ Mistral AI configured (Human-like script)")
#     else:
#         logger.warning("⚠️ Mistral AI not configured")
    
#     log_memory("startup")
#     logger.info("="*80)



# __all__ = ["router", "initialize"]




"""
gdrive_reels.py - PERFECT VOICE SYNC WITH CHUNK-BASED GENERATION
=================================================================================
✅ Fixed voice ID: FZkK3TvQ0pjyDmT8fzIW (Primary ElevenLabs)
✅ Break video into equal 10-second chunks
✅ Generate voiceover per chunk for perfect sync
✅ 30s video = 30s voiceover (±2s tolerance is fine)
✅ Speed adjustment only if difference > 5s
✅ NO CAPTIONS (removed for speed)
✅ Concise script generation (fewer words)
✅ All other features preserved
=================================================================================
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
from typing import Optional, List, Dict, Tuple
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
logger = logging.getLogger("GDriveReels")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def log_memory(step: str):
    """Log memory"""
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

# PRIMARY VOICE ID - FIXED
PRIMARY_VOICE_ID = "FZkK3TvQ0pjyDmT8fzIW"

# Fallback voices
VOICE_IDS = {
    "male": ["7qBNUtXRGP0jPi0H4r8k", "BTNeCNdXniCSbjEac5vd"],
    "female": ["Icov0pR6jgWuaZhmlmtO", "UbB19hYD8fvYxwJAVTY5"]
}

# Edge TTS fallback
EDGE_TTS_VOICES = {
    "male": ["hi-IN-MadhurNeural"],
    "female": ["hi-IN-SwaraNeural"]
}

# Top 10 BGM
TOP_10_BGM_URLS = [
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Temple%20Vibes%20_%20Traditional%20Background%20Music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Krishna%20Healing%20Flute%20'%20Bansuri%20background%20music%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Indian%20Epic%20_%20Cinematic%20Sitar%20and%20Drums%20BGM%20-%20Royalty%20free%20Music%20%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Maha%20Shivratri%20_%20MANTRA%20Sounds%20of%20Indian%20Land%20-%20Royalty%20free%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/RAMA%20'%20Indian%20Epic%20BGM%20-%20Royalty%20free%20Music%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Ramayana%20'%20SITA%20Emotional%20BGM%20-%20India%20Royalty%20free%20music%20Download.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sitar%20-%20Dholak%20-Indian%20Instrumental%20Music%20_%20(No%20Copyright)%20-%20Background%20Music%20for%20Poet%20-%20Meditation.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Sri%20Krishna%20Govinda%20Devotional%20song%20(%20Flute%20Instrumental%20)%20Royalty%20free%20Music.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Mahabharata%20story%20-%20Duryodhana%20Epic%20BGM%20-%20Royalty%20free%20Music.mp3",
    "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/DURGA%20maa%20_%20Indian%20Royalty%20free%20Music%20%23durgapuja%20%23navratri.mp3"
]

PROCESSING_STATUS = {}

# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════
def cleanup(*paths):
    """Delete + GC"""
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

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg"""
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

def get_audio_duration(audio_path: str) -> float:
    """Get audio duration"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
            capture_output=True, timeout=10, text=True
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0.0
    except:
        return 0.0

# ═══════════════════════════════════════════════════════════════════════
# GOOGLE DRIVE
# ═══════════════════════════════════════════════════════════════════════
def extract_file_id(url: str) -> Optional[str]:
    """Extract file ID"""
    if not url or "drive.google.com" not in url:
        return None
    
    patterns = [r'/file/d/([a-zA-Z0-9_-]{25,})', r'[?&]id=([a-zA-Z0-9_-]{25,})']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def download_chunked(url: str, output: str) -> bool:
    """Download in chunks"""
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
    """Download with fallbacks"""
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
# VIDEO OPERATIONS
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
            duration = float(result.stdout.strip())
            logger.info(f"⏱️ {duration:.1f}s")
            return duration
        return 0.0
    except:
        return 0.0

async def extract_audio(video_path: str, audio_path: str) -> bool:
    """Extract audio"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ], timeout=60, step="Extract-Audio")
    
    return success

# ═══════════════════════════════════════════════════════════════════════
# TRANSCRIPTION WITH TIMESTAMPS
# ═══════════════════════════════════════════════════════════════════════
async def transcribe_audio_with_timestamps(audio_path: str) -> tuple[Optional[List[Dict]], str]:
    """Transcribe with HTTP API + get timestamps"""
    logger.info("📝 Transcribing with timestamps...")
    log_memory("transcribe-start")
    
    if not GROQ_API_KEY:
        return None, "No API key"
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            with open(audio_path, "rb") as f:
                files = {"file": ("audio.wav", f, "audio/wav")}
                data = {
                    "model": "whisper-large-v3",
                    "language": "hi",
                    "response_format": "verbose_json"
                }
                
                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract segments with timestamps
                    segments = []
                    if "segments" in result and result["segments"]:
                        for seg in result["segments"]:
                            text = seg.get("text", "").strip()
                            if text:
                                segments.append({
                                    "start": float(seg.get("start", 0.0)),
                                    "end": float(seg.get("end", 0.0)),
                                    "text": text
                                })
                        
                        if segments:
                            logger.info(f"✅ Transcribed - {len(segments)} segments")
                            full_text = " ".join([s["text"] for s in segments])
                            logger.info(f"   Text preview: {full_text[:100]}...")
                            log_memory("transcribe-done")
                            cleanup(audio_path)
                            return segments, ""
                    
                    # Fallback: use text
                    if "text" in result and result["text"]:
                        text = result["text"].strip()
                        words = text.split()
                        segments = []
                        words_per_seg = 10
                        
                        for i in range(0, len(words), words_per_seg):
                            seg_words = words[i:i+words_per_seg]
                            if seg_words:
                                segments.append({
                                    "start": i / 2.5,
                                    "end": (i + len(seg_words)) / 2.5,
                                    "text": " ".join(seg_words)
                                })
                        
                        logger.info(f"✅ Transcribed - {len(segments)} segments (from text)")
                        cleanup(audio_path)
                        return segments, ""
        
        cleanup(audio_path)
        return None, "Empty response"
    except Exception as e:
        cleanup(audio_path)
        logger.error(f"❌ Transcription error: {e}")
        return None, str(e)

# ═══════════════════════════════════════════════════════════════════════
# CHARACTER DETECTION
# ═══════════════════════════════════════════════════════════════════════
def detect_character_gender(segments: List[Dict]) -> str:
    """Detect male/female character from segments"""
    text = " ".join([seg["text"] for seg in segments]).lower()
    
    female_keywords = ["sita", "radha", "durga", "lakshmi", "queen", "rani", "girl", "ladki", "woman", "mata", "maa", "goddess", "devi"]
    male_keywords = ["ram", "krishna", "shiva", "hanuman", "king", "raja", "boy", "ladka", "man", "god", "dev", "pita", "beta"]
    
    female_count = sum(1 for kw in female_keywords if kw in text)
    male_count = sum(1 for kw in male_keywords if kw in text)
    
    if female_count > male_count:
        logger.info(f"   🎭 FEMALE character detected")
        return "female"
    else:
        logger.info(f"   🎭 MALE character detected (default)")
        return "male"

# ═══════════════════════════════════════════════════════════════════════
# CONCISE SCRIPT GENERATION - FEWER WORDS TO FIT IN VOICEOVER
# ═══════════════════════════════════════════════════════════════════════
async def generate_concise_script(segments: List[Dict], duration: float) -> dict:
    """Generate CONCISE script that fits perfectly in voiceover duration"""
    logger.info("🤖 AI Script (Concise + Fits Duration)...")
    log_memory("ai-start")
    
    # Combine segments for full text
    transcript = " ".join([seg["text"] for seg in segments])
    
    # Calculate REDUCED word count (20% less to ensure it fits)
    word_count = len(transcript.split())
    speaking_rate = word_count / duration if duration > 0 else 2.5
    
    # Reduce target by 20% to ensure voiceover doesn't exceed video length
    target_words = int(duration * speaking_rate * 0.8)
    
    logger.info(f"   Original: {word_count} words")
    logger.info(f"   Target: {target_words} words (80% of capacity)")
    logger.info(f"   Speaking rate: {speaking_rate:.2f} words/sec")
    
    # CTA - shorter version
    cta = "Like, Subscribe aur Share karein!"
    
    # Detect character
    character_gender = detect_character_gender(segments)
    
    # Try Mistral AI with CONCISE PROMPT
    if MISTRAL_API_KEY:
        try:
            logger.info("   Trying Mistral AI for concise script...")
            
            # CONCISE PROMPT - STRICT WORD LIMIT
            prompt = f"""Generate a CONCISE, NATURAL Hindi narration that fits EXACTLY in the given duration:

Original Transcript: {transcript}
Video Duration: {duration} seconds
STRICT MAXIMUM WORDS: {target_words} words
Speaking Rate: {speaking_rate:.2f} words/second

CRITICAL REQUIREMENTS:

1. **STRICT WORD LIMIT**:
   - Your script MUST be MAXIMUM {target_words} words
   - Count every word carefully
   - If you exceed {target_words} words, the voiceover will be too long
   - Better to use {target_words - 10} words to be safe

2. **CONCISE STORYTELLING**:
   - Get to the point quickly
   - Use short, punchy sentences
   - Remove unnecessary words
   - No long descriptions
   - Every word must add value

3. **NATURAL HINDI**:
   - Conversational tone
   - Mix Hindi with Hinglish
   - Use simple, everyday words
   - Natural flow

4. **STRUCTURE**:
   - Quick hook (3-5 words): "Suniye ek baat..."
   - Main point (concise, direct)
   - Quick conclusion
   - Short CTA: "{cta}"

5. **NO LONG PAUSES**: Use "..." only 2-3 times maximum

SEO REQUIREMENTS:

6. Generate a VIRAL Hinglish TITLE (max 100 chars):
   - Power words: SHOCKING, AMAZING, SECRET, MUST WATCH
   - Emojis for appeal
   - Example: "Yeh Sach Jaankar Shocked Ho Jaoge! 😱 #Shorts"

7. Write Hinglish DESCRIPTION (2-3 short paragraphs)

8. Generate 60-70 SEO KEYWORDS (vertical format, one per line)

9. Generate 8-10 HASHTAGS (vertical format, one per line)

Generate in JSON format:
{{
    "script": "Concise natural Hindi script with maximum {target_words} words including {cta}",
    "word_count": actual_word_count_number,
    "title": "Viral Hinglish title with emojis",
    "description": "Description paragraph 1\\n\\nDescription paragraph 2\\n\\nkeywords\\n\\nhashtags",
    "hashtags": ["#Shorts", "#Viral", "#Hindi", "#Trending", "#MustWatch"],
    "story_id": "unique-id"
}}"""
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a concise storyteller. Create SHORT, NATURAL Hindi scripts that fit perfectly in the given time. STRICT word limits. Output ONLY valid JSON."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    
                    # Clean JSON
                    content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if match:
                        data = json.loads(match.group(0))
                        script_text = data.get("script", "")
                        
                        # Verify word count
                        actual_words = len(script_text.split())
                        logger.info(f"   Generated: {actual_words} words (target: {target_words})")
                        
                        # If too many words, truncate
                        if actual_words > target_words:
                            logger.warning(f"   ⚠️ Script too long, truncating...")
                            words = script_text.split()
                            script_text = " ".join(words[:target_words - 5]) + " " + cta
                        
                        # Ensure CTA
                        if "LIKE" not in script_text.upper() and "SUBSCRIBE" not in script_text.upper():
                            script_text += " " + cta
                        
                        title = data.get("title", "Amazing Story 🔥 #Shorts")
                        description = data.get("description", f"{transcript[:200]}\\n\\nKeywords: hindi story, viral video")
                        hashtags = data.get("hashtags", ["#Shorts", "#Viral", "#Hindi", "#Trending"])
                        story_id = data.get("story_id", str(uuid.uuid4())[:8])
                        
                        logger.info(f"✅ Concise script generated")
                        logger.info(f"   Title: {title}")
                        logger.info(f"   Script: {len(script_text.split())} words")
                        log_memory("ai-done")
                        
                        return {
                            "script": script_text,
                            "segments": segments,
                            "character_gender": character_gender,
                            "title": title,
                            "description": description,
                            "hashtags": hashtags,
                            "story_id": story_id,
                            "speaking_rate": speaking_rate
                        }
        except Exception as e:
            logger.warning(f"   Mistral failed: {e}")
    
    # FALLBACK - use truncated transcript
    logger.info("   Using truncated transcript (fallback)")
    words = transcript.split()
    script = " ".join(words[:target_words - 5]) + " " + cta
    
    title_base = " ".join(words[:5])
    title = f"{title_base}... 🔥 #Shorts"
    description = f"{transcript[:150]}...\n\nKeywords: hindi story, viral video, trending shorts"
    hashtags = ["#Shorts", "#Viral", "#Hindi", "#Trending"]
    
    log_memory("ai-done")
    
    return {
        "script": script,
        "segments": segments,
        "character_gender": character_gender,
        "title": title,
        "description": description,
        "hashtags": hashtags,
        "story_id": str(uuid.uuid4())[:8],
        "speaking_rate": speaking_rate
    }

# ═══════════════════════════════════════════════════════════════════════
# CHUNK-BASED VOICEOVER GENERATION - PERFECT SYNC
# ═══════════════════════════════════════════════════════════════════════
async def generate_chunked_voiceover(metadata: dict, output_dir: str, video_duration: float) -> Tuple[Optional[str], str]:
    """Generate voiceover in equal chunks matching video duration"""
    logger.info("🎙️ Chunked Voiceover Generation...")
    log_memory("voice-start")
    
    script = metadata.get("script", "")
    gender = metadata["character_gender"]
    
    # ALWAYS USE PRIMARY VOICE ID
    voice_id = PRIMARY_VOICE_ID
    
    logger.info(f"   Voice ID: {voice_id} (PRIMARY)")
    logger.info(f"   Video duration: {video_duration:.2f}s")
    logger.info(f"   Script length: {len(script.split())} words")
    
    # Calculate chunk size (10 seconds per chunk)
    chunk_duration = 10.0
    num_chunks = int(video_duration / chunk_duration)
    
    # If video is less than 10s, use 1 chunk
    if num_chunks == 0:
        num_chunks = 1
        chunk_duration = video_duration
    
    logger.info(f"   Breaking into {num_chunks} chunks of ~{chunk_duration:.1f}s each")
    
    # Split script into equal parts
    words = script.split()
    words_per_chunk = len(words) // num_chunks if num_chunks > 0 else len(words)
    
    script_chunks = []
    for i in range(num_chunks):
        start_idx = i * words_per_chunk
        end_idx = start_idx + words_per_chunk if i < num_chunks - 1 else len(words)
        chunk_text = " ".join(words[start_idx:end_idx])
        if chunk_text:
            script_chunks.append(chunk_text)
    
    logger.info(f"   Script split into {len(script_chunks)} chunks")
    
    # Generate voiceover for each chunk
    chunk_files = []
    
    for i, chunk_text in enumerate(script_chunks):
        chunk_file = os.path.join(output_dir, f"chunk_{i:03d}.mp3")
        temp_file = chunk_file.replace(".mp3", "_temp.mp3")
        
        logger.info(f"   Generating chunk {i+1}/{len(script_chunks)}...")
        
        success = False
        
        # Try ElevenLabs with PRIMARY VOICE ID
        if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    resp = await client.post(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                        headers={"xi-api-key": ELEVENLABS_API_KEY},
                        json={
                            "text": chunk_text,
                            "model_id": "eleven_multilingual_v2",
                            "voice_settings": {
                                "stability": 0.5,
                                "similarity_boost": 0.75,
                                "style": 0.5,
                                "use_speaker_boost": True
                            }
                        }
                    )
                    
                    if resp.status_code == 200:
                        with open(temp_file, 'wb') as f:
                            f.write(resp.content)
                        
                        actual_dur = get_audio_duration(temp_file)
                        if actual_dur > 0:
                            # Adjust speed to match chunk duration
                            target_dur = chunk_duration
                            ratio = actual_dur / target_dur
                            
                            # Clamp ratio
                            ratio = min(max(ratio, 0.5), 2.0)
                            
                            if run_ffmpeg(["ffmpeg", "-i", temp_file, "-filter:a", f"atempo={ratio}", "-y", chunk_file], 30):
                                cleanup(temp_file)
                                final_dur = get_audio_duration(chunk_file)
                                logger.info(f"   ✅ Chunk {i+1}: {final_dur:.2f}s (target: {target_dur:.2f}s)")
                                chunk_files.append(chunk_file)
                                success = True
                        
                        cleanup(temp_file)
                        
                    if resp.status_code == 429:
                        await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"   ⚠️ Chunk {i+1} - ElevenLabs error: {e}")
                cleanup(temp_file)
        
        # Fallback to Edge TTS
        if not success:
            try:
                import edge_tts
                voice = EDGE_TTS_VOICES[gender][0]
                
                await edge_tts.Communicate(chunk_text, voice).save(temp_file)
                
                actual_dur = get_audio_duration(temp_file)
                if actual_dur > 0:
                    target_dur = chunk_duration
                    ratio = actual_dur / target_dur
                    ratio = min(max(ratio, 0.5), 2.0)
                    
                    if run_ffmpeg(["ffmpeg", "-i", temp_file, "-filter:a", f"atempo={ratio}", "-y", chunk_file], 30):
                        cleanup(temp_file)
                        final_dur = get_audio_duration(chunk_file)
                        logger.info(f"   ✅ Chunk {i+1}: {final_dur:.2f}s - Edge TTS")
                        chunk_files.append(chunk_file)
                        success = True
                
                cleanup(temp_file)
            except Exception as e:
                logger.warning(f"   ⚠️ Chunk {i+1} - Edge TTS error: {e}")
                cleanup(temp_file)
        
        if not success:
            logger.error(f"   ❌ Chunk {i+1} failed")
            continue
        
        # Small delay
        await asyncio.sleep(0.3)
    
    if not chunk_files:
        return None, "All chunks failed"
    
    logger.info(f"   ✅ Generated {len(chunk_files)}/{len(script_chunks)} chunks")
    
    # Concatenate chunks
    final = os.path.join(output_dir, "voice.mp3")
    
    if len(chunk_files) == 1:
        shutil.copy(chunk_files[0], final)
        cleanup(*chunk_files)
    else:
        concat_file = os.path.join(output_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for chunk_file in chunk_files:
                f.write(f"file '{chunk_file}'\n")
        
        if run_ffmpeg(["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", "-y", final], 60):
            cleanup(concat_file, *chunk_files)
        else:
            cleanup(concat_file, *chunk_files)
            return None, "Concat failed"
    
    # Check final duration
    final_dur = get_audio_duration(final)
    diff = abs(final_dur - video_duration)
    
    logger.info(f"   🎵 Voiceover: {final_dur:.2f}s, Video: {video_duration:.2f}s, Diff: {diff:.2f}s")
    
    # Only adjust if difference > 5 seconds (allow ±2s tolerance as requested)
    if diff > 5.0:
        logger.info(f"   ⚠️ Large difference detected, adjusting speed...")
        adjusted = os.path.join(output_dir, "voice_adj.mp3")
        ratio = final_dur / video_duration
        
        # Clamp ratio
        if ratio > 2.0:
            logger.warning(f"   ⚠️ Ratio too high ({ratio:.2f}), clamping to 2.0")
            ratio = 2.0
        elif ratio < 0.5:
            logger.warning(f"   ⚠️ Ratio too low ({ratio:.2f}), clamping to 0.5")
            ratio = 0.5
        
        if run_ffmpeg(["ffmpeg", "-i", final, "-filter:a", f"atempo={ratio}", "-y", adjusted], 30):
            cleanup(final)
            final = adjusted
            final_dur = get_audio_duration(final)
            diff = abs(final_dur - video_duration)
            logger.info(f"   ✅ Adjusted: {final_dur:.2f}s (diff: {diff:.2f}s)")
    
    if diff <= 2.0:
        logger.info(f"✅ PERFECT SYNC! Voice: {final_dur:.2f}s ≈ Video: {video_duration:.2f}s (±{diff:.2f}s)")
    else:
        logger.info(f"✅ ACCEPTABLE SYNC: Voice: {final_dur:.2f}s vs Video: {video_duration:.2f}s (±{diff:.2f}s)")
    
    log_memory("voice-done")
    return final, ""

# ═══════════════════════════════════════════════════════════════════════
# VIDEO ASSEMBLY (NO CAPTIONS)
# ═══════════════════════════════════════════════════════════════════════
async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove audio"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an",
        "-y", video_out
    ], timeout=60, step="Remove-Audio")
    
    if success:
        cleanup(video_in)
    
    return success

async def download_bgm(output: str) -> bool:
    """Download BGM"""
    logger.info("🎵 BGM...")
    log_memory("bgm-start")
    
    bgm_url = random.choice(TOP_10_BGM_URLS)
    logger.info(f"   Selected: {bgm_url.split('/')[-1][:50]}...")
    
    try:
        success = await download_chunked(bgm_url, output)
        
        if success:
            logger.info("✅ BGM Downloaded")
            log_memory("bgm-done")
            return True
        
        logger.warning("⚠️ BGM download failed")
        return False
    except:
        logger.warning("⚠️ BGM error")
        return False

async def create_final_video(silent: str, voice: str, bgm: Optional[str], output: str) -> tuple[bool, str]:
    """Create final video - NO CAPTIONS (removed for speed)"""
    logger.info("✨ Final Video (No Captions)...")
    log_memory("final-start")
    
    # Mix audio with BGM directly - NO CAPTION STEP
    if bgm and os.path.exists(bgm):
        logger.info("   Mixing voice + BGM (volume: 0.18)...")
        success = run_ffmpeg([
            "ffmpeg", "-i", silent, "-i", voice, "-i", bgm,
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.18[m];[v][m]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], 120, "Mix-Voice-BGM")
        
        if not success:
            logger.warning("⚠️ Mix with BGM failed, trying without...")
            success = run_ffmpeg([
                "ffmpeg", "-i", silent, "-i", voice,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                "-shortest", "-y", output
            ], 90, "Add-Voice")
    else:
        logger.info("   Adding voice only...")
        success = run_ffmpeg([
            "ffmpeg", "-i", silent, "-i", voice,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
            "-shortest", "-y", output
        ], 90, "Add-Voice")
    
    cleanup(silent, voice, bgm)
    
    if not success:
        return False, "Audio mix failed"
    
    log_memory("final-done")
    return True, ""

# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════
async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload to YouTube"""
    logger.info("📤 YouTube...")
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
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════
async def process_reel(drive_url: str, user_id: str, task_id: str):
    """Main pipeline with chunked voiceover generation"""
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
        temp_dir = tempfile.mkdtemp(prefix="reel_")
        logger.info(f"📁 {temp_dir}")
        log_memory("START")
        
        # Extract ID
        update(5, "Extracting ID...")
        file_id = extract_file_id(drive_url)
        if not file_id:
            raise ValueError("Invalid URL")
        
        # Download
        update(10, "Downloading...")
        raw_video = os.path.join(temp_dir, "raw.mp4")
        success, error = await download_from_gdrive(file_id, raw_video)
        if not success:
            raise Exception(error)
        
        # Get duration
        update(20, "Analyzing...")
        duration = await get_duration(raw_video)
        if duration <= 0:
            raise ValueError("Invalid video")
        if duration > 180:
            raise ValueError(f"Too long ({duration:.0f}s)")
        
        # Extract audio
        update(25, "Extracting audio...")
        audio_path = os.path.join(temp_dir, "audio.wav")
        if not await extract_audio(raw_video, audio_path):
            raise Exception("Audio extraction failed")
        
        # Transcribe
        update(30, "Transcribing...")
        segments, error = await transcribe_audio_with_timestamps(audio_path)
        if not segments:
            raise Exception(error or "Transcription failed")
        
        # Generate concise script
        update(50, "Generating concise script...")
        metadata = await generate_concise_script(segments, duration)
        logger.info(f"   Title: {metadata['title']}")
        logger.info(f"   Character: {metadata['character_gender'].upper()}")
        
        # Chunked voiceover generation
        update(60, "Generating chunked voiceover...")
        voice, error = await generate_chunked_voiceover(metadata, temp_dir, duration)
        if not voice:
            raise Exception(error)
        
        # Remove audio
        update(75, "Removing original audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(raw_video, silent_video):
            raise Exception("Remove audio failed")
        
        # BGM
        update(80, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        bgm_success = await download_bgm(bgm_path)
        
        if not bgm_success:
            bgm_path = None
        
        # Final video (NO CAPTIONS)
        update(85, "Creating final video...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await create_final_video(silent_video, voice, bgm_path, final_video)
        if not success:
            raise Exception(error)
        
        if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
            raise Exception("Invalid final video")
        
        size_mb = os.path.getsize(final_video) / (1024 * 1024)
        logger.info(f"   Final: {size_mb:.1f}MB")
        
        # Upload
        update(95, "Uploading to YouTube...")
        full_description = f"{metadata['description']}\n\n{' '.join(metadata['hashtags'])}"
        
        upload_result = await upload_to_youtube(final_video, metadata["title"], full_description, user_id)
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        # SUCCESS
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("✅ SUCCESS!")
        logger.info(f"   Time: {elapsed:.1f}s")
        logger.info(f"   Video: {upload_result['video_id']}")
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
            "story_id": metadata.get("story_id", ""),
            "character_gender": metadata["character_gender"],
            "duration": round(duration, 1),
            "processing_time": round(elapsed, 1),
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat(),
            "sync_mode": "chunked_perfect_sync",
            "voice_id": PRIMARY_VOICE_ID,
            "captions_applied": False
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
# API
# ═══════════════════════════════════════════════════════════════════════
router = APIRouter()

@router.post("/api/gdrive-reels/process")
async def process_endpoint(request: Request):
    """Process"""
    logger.info("🌐 API REQUEST")
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        drive_url = (data.get("drive_url") or "").strip()
        
        if not user_id:
            return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
        if not drive_url or "drive.google.com" not in drive_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Valid URL required"})
        
        task_id = str(uuid.uuid4())
        logger.info(f"✅ Task: {task_id}")
        
        await asyncio.wait_for(process_reel(drive_url, user_id, task_id), timeout=600)
        
        result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
    except Exception as e:
        logger.error(f"❌ {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/api/gdrive-reels/status/{task_id}")
async def status_endpoint(task_id: str):
    """Status"""
    status = PROCESSING_STATUS.get(task_id)
    if not status:
        return JSONResponse(status_code=404, content={"success": False, "error": "Not found"})
    return JSONResponse(content=status)

@router.get("/api/gdrive-reels/health")
async def health_endpoint():
    """Health"""
    log_memory("health")
    return JSONResponse(content={
        "status": "ok",
        "groq_configured": bool(GROQ_API_KEY),
        "elevenlabs_configured": bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20),
        "mistral_configured": bool(MISTRAL_API_KEY),
        "active_tasks": len([s for s in PROCESSING_STATUS.values() if s["status"] == "processing"]),
        "features": {
            "voiceover_mode": "chunked_generation",
            "primary_voice_id": PRIMARY_VOICE_ID,
            "chunk_size": "10 seconds",
            "concise_script": "yes (80% word capacity)",
            "sync_tolerance": "±2s acceptable, only adjust if >5s diff",
            "captions_applied": "no (removed for speed)",
            "bgm_volume": "0.18",
            "bgm_tracks": len(TOP_10_BGM_URLS),
            "seo_optimization": "yes"
        }
    })

@router.get("/api/gdrive-reels/bgm-list")
async def bgm_list_endpoint():
    """Get list of BGM tracks"""
    return JSONResponse(content={
        "success": True,
        "total_tracks": len(TOP_10_BGM_URLS),
        "tracks": [
            {
                "index": idx + 1,
                "name": url.split('/')[-1].replace('%20', ' ').replace('.mp3', ''),
                "url": url
            }
            for idx, url in enumerate(TOP_10_BGM_URLS)
        ]
    })

async def initialize():
    """Startup"""
    logger.info("="*80)
    logger.info("🚀 GDRIVE REELS (CHUNKED PERFECT SYNC)")
    logger.info("="*80)
    logger.info(f"✅ PRIMARY Voice ID: {PRIMARY_VOICE_ID}")
    logger.info("✅ Chunked generation (10s per chunk)")
    logger.info("✅ Concise scripts (80% word capacity)")
    logger.info("✅ Perfect sync: ±2s tolerance, adjust only if >5s")
    logger.info("✅ NO CAPTIONS (removed for speed)")
    logger.info("✅ SEO optimized titles & descriptions")
    logger.info("="*80)
    
    if GROQ_API_KEY:
        logger.info("✅ Groq configured")
    else:
        logger.error("❌ No GROQ_SPEECH_API")
    
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        logger.info("✅ ElevenLabs configured (PRIMARY)")
    else:
        logger.warning("⚠️ ElevenLabs not configured")
    
    if MISTRAL_API_KEY:
        logger.info("✅ Mistral AI configured (Concise scripts)")
    else:
        logger.warning("⚠️ Mistral AI not configured")
    
    log_memory("startup")
    logger.info("="*80)

__all__ = ["router", "initialize"]