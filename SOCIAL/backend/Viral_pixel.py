

# """
# Viral_pixel.py - COMPLETE PRODUCTION VERSION
# ==================================================
# ✅ ElevenLabs Voice ID: nPczCjzI2devNBz1zQrb
# ✅ Horror/Dark/Space Background Music (5-6 retries)
# ✅ Pexels PRIORITY → Pixabay FALLBACK
# ✅ English Suspenseful Titles + Hindi Narration
# ✅ Voice + Music Mixing (Voice 100%, Music 30%)
# ✅ Ultra-fast Processing (720p vertical)
# ✅ Direct YouTube Upload
# ==================================================
# """

# from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
# import asyncio
# import logging
# import os
# import traceback
# import uuid
# import httpx
# import json
# import re
# import random
# import subprocess
# from typing import List, Dict, Optional
# import tempfile
# import shutil
# import gc

# logger = logging.getLogger(__name__)

# # ============================================================================
# # CONFIGURATION & API KEYS
# # ============================================================================

# PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
# PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_346aca9fb63af57816b2f0323b6312b75a65aa852656eeac")

# # ELEVENLABS VOICE ID - CORRECT ONE
# ELEVENLABS_VOICE_ID = "nPczCjzI2devNBz1zQrb"

# # PROCESSING LIMITS
# MAX_VIDEO_SIZE_MB = 40
# FFMPEG_TIMEOUT = 180
# TARGET_DURATION = 30
# CHUNK_SIZE = 65536

# # NICHE KEYWORDS FOR VIDEO SEARCH
# NICHE_KEYWORDS = {
#     "space": ["galaxy", "nebula", "planet", "cosmos", "stars", "universe"],
#     "tech_ai": ["technology", "digital", "cyber", "robot", "ai", "future"],
#     "ocean": ["ocean", "wave", "underwater", "reef", "sea", "marine"],
#     "nature": ["mountain", "forest", "waterfall", "sunset", "river", "landscape"]
# }

# # FALLBACK KEYWORDS FOR VERTICAL VIDEOS
# VERTICAL_FALLBACKS = ["tower", "building", "city", "waterfall"]

# # HORROR/DARK/SPACE BACKGROUND MUSIC URLs (5-6 sources for retry)
# BACKGROUND_MUSIC_URLS = [
#     # Dark Cinematic Ambient
#     "https://freesound.org/data/previews/614/614090_11931419-lq.mp3",
    
#     # Horror Atmosphere
#     "https://freesound.org/data/previews/543/543995_11587873-lq.mp3",
    
#     # Dark Ambient Space
#     "https://freesound.org/data/previews/632/632351_10755880-lq.mp3",
    
#     # Mystery Tension
#     "https://freesound.org/data/previews/558/558262_11587873-lq.mp3",
    
#     # Space Dark Theme
#     "https://freesound.org/data/previews/521/521495_9961799-lq.mp3",
    
#     # Horror Suspense
#     "https://freesound.org/data/previews/477/477718_9497060-lq.mp3"
# ]

# # ============================================================================
# # UTILITY FUNCTIONS
# # ============================================================================

# def force_cleanup(*filepaths):
#     """
#     Force cleanup of files with garbage collection
#     Removes files and frees memory immediately
#     """
#     for fp in filepaths:
#         try:
#             if fp and os.path.exists(fp):
#                 os.remove(fp)
#                 logger.info(f"🗑️ Cleaned: {os.path.basename(fp)}")
#         except Exception as e:
#             logger.warning(f"Cleanup warning: {e}")
#             pass
    
#     # Force garbage collection
#     gc.collect()

# def get_size_mb(fp: str) -> float:
#     """Get file size in megabytes"""
#     try:
#         return os.path.getsize(fp) / (1024 * 1024)
#     except:
#         return 0.0

# def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
#     """
#     Run FFmpeg command with timeout
#     Returns True if successful, False otherwise
#     """
#     try:
#         logger.info(f"Running FFmpeg with {timeout}s timeout...")
#         result = subprocess.run(
#             cmd, 
#             capture_output=True, 
#             timeout=timeout, 
#             check=False, 
#             text=True
#         )
        
#         if result.returncode != 0:
#             logger.error(f"FFmpeg error (code {result.returncode})")
#             logger.error(f"FFmpeg stderr: {result.stderr[:500]}")
#             return False
        
#         return True
        
#     except subprocess.TimeoutExpired:
#         logger.error(f"❌ FFmpeg timeout after {timeout}s")
#         return False
#     except Exception as e:
#         logger.error(f"FFmpeg exception: {e}")
#         return False

# # ============================================================================
# # BACKGROUND MUSIC DOWNLOAD WITH RETRY LOGIC
# # ============================================================================

# async def download_background_music(temp_dir: str) -> Optional[str]:
#     """
#     Download horror/dark/space background music with 5-6 retries
#     Tries each URL sequentially until successful
#     Returns music file path or None if all attempts fail
#     """
#     music_path = os.path.join(temp_dir, "bg_music.mp3")
    
#     logger.info("🎵 Downloading background music (horror/dark/space theme)...")
#     logger.info(f"   Total attempts: {len(BACKGROUND_MUSIC_URLS)}")
    
#     for attempt, url in enumerate(BACKGROUND_MUSIC_URLS, 1):
#         try:
#             logger.info(f"   Attempt {attempt}/{len(BACKGROUND_MUSIC_URLS)}: Trying music source...")
#             logger.info(f"   URL: {url[:60]}...")
            
#             async with httpx.AsyncClient(timeout=30) as client:
#                 resp = await client.get(url, follow_redirects=True)
                
#                 if resp.status_code == 200:
#                     # Write music file
#                     with open(music_path, 'wb') as f:
#                         f.write(resp.content)
                    
#                     size = get_size_mb(music_path)
                    
#                     # Validate file size (at least 50KB)
#                     if size > 0.05:
#                         logger.info(f"   ✅ SUCCESS! Background music downloaded: {size:.2f}MB")
#                         logger.info(f"   Used attempt {attempt} of {len(BACKGROUND_MUSIC_URLS)}")
#                         return music_path
#                     else:
#                         logger.warning(f"   ⚠️ Music file too small: {size:.2f}MB (< 0.05MB)")
#                         force_cleanup(music_path)
#                 else:
#                     logger.warning(f"   ⚠️ HTTP {resp.status_code}")
            
#             # Cleanup failed attempt
#             force_cleanup(music_path)
            
#         except httpx.TimeoutException:
#             logger.warning(f"   ⚠️ Attempt {attempt} timed out (30s)")
#             force_cleanup(music_path)
#         except Exception as e:
#             logger.warning(f"   ⚠️ Attempt {attempt} failed: {str(e)[:100]}")
#             force_cleanup(music_path)
#             continue
    
#     # All attempts failed
#     logger.warning("⚠️ All background music download attempts failed")
#     logger.info("   Will continue without background music")
#     return None

# # ============================================================================
# # SCRIPT GENERATION (ENGLISH TITLE + HINDI NARRATION)
# # ============================================================================

# async def generate_script(niche: str) -> dict:
#     """
#     Generate viral script with:
#     - English suspenseful title
#     - Hindi narration (4 segments: hook, story, climax, outro)
#     - Text overlays with emojis
#     """
    
#     # Suspenseful English title templates
#     title_templates = [
#         "What Scientists Hide About {topic}",
#         "The Dark Truth Behind {topic}",
#         "This Will Change How You See {topic}",
#         "{topic}: The Shocking Reality",
#         "The Secret Of {topic} Revealed",
#         "{topic}: What They Don't Want You To Know"
#     ]
    
#     topic = niche.replace("_", " ").title()
#     english_title = random.choice(title_templates).format(topic=topic)
    
#     # Mistral AI prompt for Hindi narration
#     prompt = f"""Create a VIRAL 30-second Hindi narration for YouTube Shorts about {niche}.

# REQUIREMENTS:
# - Total duration: 30 seconds
# - 4 segments with specific timing
# - Hindi language only for narration
# - Engaging, mysterious, shocking tone

# STRUCTURE:
# 1. HOOK (8 seconds): "Kya aap jaante hain..." - create mystery and shock
# 2. STORY (12 seconds): Present amazing facts, "Scientists ne discover kiya..."
# 3. CLIMAX (7 seconds): "Lekin sabse badi baat..." - build to revelation
# 4. OUTRO (3 seconds): "Comment mein batao!" - call to action

# OUTPUT ONLY THIS JSON:
# {{
#   "segments": [
#     {{"narration": "Hindi hook text here", "text_overlay": "😱", "duration": 8}},
#     {{"narration": "Hindi story text here", "text_overlay": "🔥", "duration": 12}},
#     {{"narration": "Hindi climax text here", "text_overlay": "💡", "duration": 7}},
#     {{"narration": "Hindi outro text here", "text_overlay": "🤔", "duration": 3}}
#   ]
# }}

# Make it VIRAL and ENGAGING!"""
    
#     try:
#         if MISTRAL_API_KEY:
#             logger.info("Calling Mistral AI for script generation...")
            
#             async with httpx.AsyncClient(timeout=30) as client:
#                 resp = await client.post(
#                     "https://api.mistral.ai/v1/chat/completions",
#                     headers={
#                         "Authorization": f"Bearer {MISTRAL_API_KEY}",
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "model": "mistral-large-latest",
#                         "messages": [
#                             {
#                                 "role": "system",
#                                 "content": "You are a viral content creator. Output ONLY valid JSON, no markdown, no explanations."
#                             },
#                             {
#                                 "role": "user",
#                                 "content": prompt
#                             }
#                         ],
#                         "temperature": 0.9,
#                         "max_tokens": 1000
#                     }
#                 )
                
#                 if resp.status_code == 200:
#                     content = resp.json()["choices"][0]["message"]["content"]
                    
#                     # Clean up markdown formatting
#                     content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    
#                     # Extract JSON if wrapped in text
#                     json_match = re.search(r'\{.*\}', content, re.DOTALL)
#                     if json_match:
#                         content = json_match.group(0)
                    
#                     # Parse JSON
#                     script = json.loads(content)
                    
#                     logger.info(f"✅ Script generated successfully")
#                     logger.info(f"   Segments: {len(script.get('segments', []))}")
                    
#                     return {
#                         "title": english_title + " #Shorts",
#                         "description": f"#{niche} #viral #shorts #mystery",
#                         "tags": [niche, "viral", "shorts", "mystery", "facts"],
#                         "segments": script["segments"]
#                     }
#                 else:
#                     logger.warning(f"Mistral API returned status {resp.status_code}")
                    
#     except json.JSONDecodeError as e:
#         logger.warning(f"Mistral JSON parse error: {e}")
#     except Exception as e:
#         logger.warning(f"Mistral API failed: {e}")
    
#     # Fallback script (if Mistral fails)
#     logger.info("Using fallback script template")
    
#     return {
#         "title": english_title + " #Shorts",
#         "description": f"#{niche} #viral #shorts #mystery",
#         "tags": [niche, "viral", "shorts", "mystery"],
#         "segments": [
#             {
#                 "narration": "Kya aap jaante hain yeh shocking rahasya jo duniya se chhupa hai?",
#                 "text_overlay": "😱",
#                 "duration": 8
#             },
#             {
#                 "narration": "Scientists ne discover kiya hai yeh impossible lagta hai lekin sach kuch aur hai! Yeh jaankar aap hairan reh jayenge!",
#                 "text_overlay": "🔥",
#                 "duration": 12
#             },
#             {
#                 "narration": "Lekin sabse badi baat jo aapko pata honi chahiye... yeh duniya badal degi!",
#                 "text_overlay": "💡",
#                 "duration": 7
#             },
#             {
#                 "narration": "Toh kya aap vishwas karte hain? Neeche comment mein zaroor batao!",
#                 "text_overlay": "🤔",
#                 "duration": 3
#             }
#         ]
#     }

# # ============================================================================
# # VOICE GENERATION - ELEVENLABS WITH FALLBACK
# # ============================================================================

# async def generate_voice_elevenlabs(text: str, duration: float, temp_dir: str) -> Optional[str]:
#     """
#     Generate voice using ElevenLabs API with correct voice ID
#     Voice ID: nPczCjzI2devNBz1zQrb
#     Returns path to audio file or None if failed
#     """
#     try:
#         # Validate API key
#         if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
#             logger.warning("   ⚠️ ElevenLabs API key not configured properly")
#             return None
        
#         # Clean and truncate text
#         text_clean = text.strip()[:500]
#         temp_raw = os.path.join(temp_dir, f"eleven_{uuid.uuid4().hex[:4]}.mp3")
        
#         logger.info(f"   📞 Calling ElevenLabs API...")
#         logger.info(f"   Voice ID: {ELEVENLABS_VOICE_ID}")
#         logger.info(f"   Text length: {len(text_clean)} chars")
        
#         async with httpx.AsyncClient(timeout=40) as client:
#             response = await client.post(
#                 f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                 headers={
#                     "xi-api-key": ELEVENLABS_API_KEY,
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "text": text_clean,
#                     "model_id": "eleven_multilingual_v2",
#                     "voice_settings": {
#                         "stability": 0.5,
#                         "similarity_boost": 0.75,
#                         "style": 0.0,
#                         "use_speaker_boost": True
#                     }
#                 }
#             )
            
#             if response.status_code == 200:
#                 # Save raw audio
#                 with open(temp_raw, 'wb') as f:
#                     f.write(response.content)
                
#                 size = get_size_mb(temp_raw)
                
#                 if size > 0.01:
#                     logger.info(f"   ✅ ElevenLabs response: {size:.2f}MB")
                    
#                     # Adjust audio duration and normalize volume
#                     output = temp_raw.replace(".mp3", "_adjusted.mp3")
                    
#                     cmd = [
#                         "ffmpeg",
#                         "-i", temp_raw,
#                         "-filter:a", "atempo=1.1,loudnorm=I=-16",
#                         "-t", str(duration + 0.5),
#                         "-b:a", "128k",
#                         "-y", output
#                     ]
                    
#                     if run_ffmpeg(cmd, 20):
#                         force_cleanup(temp_raw)
#                         logger.info(f"   ✅ ElevenLabs voice processed: {get_size_mb(output):.2f}MB")
#                         return output
#                     else:
#                         force_cleanup(temp_raw, output)
#                 else:
#                     logger.warning(f"   ⚠️ Audio file too small: {size:.2f}MB")
#                     force_cleanup(temp_raw)
                    
#             elif response.status_code == 401:
#                 logger.error("   ❌ ElevenLabs: 401 Unauthorized - Invalid API key")
#             elif response.status_code == 429:
#                 logger.error("   ❌ ElevenLabs: 429 Rate limit exceeded")
#             else:
#                 logger.error(f"   ❌ ElevenLabs: HTTP {response.status_code}")
#                 logger.error(f"   Response: {response.text[:200]}")
                
#     except httpx.TimeoutException:
#         logger.error("   ❌ ElevenLabs: Timeout (40s)")
#     except Exception as e:
#         logger.error(f"   ❌ ElevenLabs error: {e}")
    
#     return None

# async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> Optional[str]:
#     """
#     Generate voice using Edge TTS (fallback)
#     Uses Microsoft's free Text-to-Speech API
#     """
#     try:
#         import edge_tts
        
#         temp = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:4]}.mp3")
#         text_clean = text.strip()[:350]
        
#         logger.info(f"   📞 Using Edge TTS (fallback)...")
#         logger.info(f"   Voice: hi-IN-MadhurNeural")
#         logger.info(f"   Text length: {len(text_clean)} chars")
        
#         # Generate speech
#         communicate = edge_tts.Communicate(
#             text_clean,
#             "hi-IN-MadhurNeural",
#             rate="+10%"
#         )
#         await communicate.save(temp)
        
#         size = get_size_mb(temp)
        
#         if size > 0.01:
#             logger.info(f"   ✅ Edge TTS voice generated: {size:.2f}MB")
#             return temp
        
#         force_cleanup(temp)
#         logger.warning(f"   ⚠️ Edge TTS file too small: {size:.2f}MB")
        
#     except ImportError:
#         logger.error("   ❌ Edge TTS: edge-tts package not installed")
#     except Exception as e:
#         logger.error(f"   ❌ Edge TTS error: {e}")
    
#     return None

# async def generate_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
#     """
#     Generate voice with automatic fallback
#     1. Try ElevenLabs (primary)
#     2. Fallback to Edge TTS if ElevenLabs fails
#     """
#     # Try ElevenLabs first
#     voice = await generate_voice_elevenlabs(text, duration, temp_dir)
#     if voice:
#         return voice
    
#     # Fallback to Edge TTS
#     logger.warning("   ⚠️ ElevenLabs failed, falling back to Edge TTS...")
#     return await generate_voice_edge(text, duration, temp_dir)

# # ============================================================================
# # VIDEO SEARCH - PEXELS PRIORITY, PIXABAY FALLBACK
# # ============================================================================

# def is_vertical_pexels(vdata: dict) -> bool:
#     """Check if Pexels video is vertical (9:16 aspect ratio)"""
#     try:
#         w = vdata.get("width", 0)
#         h = vdata.get("height", 0)
#         return w > 0 and h > 0 and (h / w) >= 1.5
#     except:
#         return False

# def is_vertical_pixabay(vdata: dict) -> bool:
#     """Check if Pixabay video is vertical"""
#     try:
#         videos = vdata.get("videos", {})
#         for size in ["medium", "small", "large"]:
#             sd = videos.get(size, {})
#             w, h = sd.get("width", 0), sd.get("height", 0)
#             if w > 0 and h > 0 and (h / w) >= 1.5:
#                 return True
#         return False
#     except:
#         return False

# async def search_pexels_video(query: str) -> Optional[dict]:
#     """
#     Search Pexels for vertical videos (PRIORITY)
#     Returns video data or None if not found
#     """
#     try:
#         if not PEXELS_API_KEY:
#             logger.warning("⚠️ PEXELS_API_KEY not configured")
#             return None
        
#         # Clean query
#         word = query.split()[0].lower()
#         if not word.isascii():
#             word = random.choice(VERTICAL_FALLBACKS)
        
#         logger.info(f"   Searching Pexels for: '{word}'")
        
#         async with httpx.AsyncClient(timeout=25) as client:
#             # Search with portrait orientation
#             resp = await client.get(
#                 "https://api.pexels.com/videos/search",
#                 headers={"Authorization": PEXELS_API_KEY},
#                 params={
#                     "query": word,
#                     "orientation": "portrait",
#                     "size": "medium",
#                     "per_page": 25
#                 }
#             )
            
#             if resp.status_code == 200:
#                 videos = resp.json().get("videos", [])
#                 vertical = [v for v in videos if is_vertical_pexels(v)]
                
#                 if vertical:
#                     logger.info(f"   ✅ Pexels: Found {len(vertical)} vertical videos for '{word}'")
#                     return {"source": "pexels", "data": vertical[0]}
#                 else:
#                     logger.info(f"   ⚠️ Pexels: No vertical videos for '{word}'")
#             else:
#                 logger.warning(f"   ⚠️ Pexels API: HTTP {resp.status_code}")
            
#             # Try fallback keywords
#             logger.info(f"   Trying Pexels fallback keywords...")
#             for fb in VERTICAL_FALLBACKS:
#                 resp = await client.get(
#                     "https://api.pexels.com/videos/search",
#                     headers={"Authorization": PEXELS_API_KEY},
#                     params={
#                         "query": fb,
#                         "orientation": "portrait",
#                         "size": "medium",
#                         "per_page": 15
#                     }
#                 )
                
#                 if resp.status_code == 200:
#                     videos = resp.json().get("videos", [])
#                     vertical = [v for v in videos if is_vertical_pexels(v)]
                    
#                     if vertical:
#                         logger.info(f"   ✅ Pexels fallback: Found {len(vertical)} videos for '{fb}'")
#                         return {"source": "pexels", "data": vertical[0]}
        
#         logger.info("   ⚠️ Pexels: No vertical videos found")
#         return None
        
#     except Exception as e:
#         logger.error(f"Pexels search error: {e}")
#         return None

# async def search_pixabay_video(query: str) -> Optional[dict]:
#     """
#     Search Pixabay for vertical videos (FALLBACK)
#     Returns video data or None if not found
#     """
#     try:
#         # Clean query
#         word = query.split()[0].lower()
#         if not word.isascii():
#             word = random.choice(VERTICAL_FALLBACKS)
        
#         logger.info(f"   Searching Pixabay for: '{word}'")
        
#         async with httpx.AsyncClient(timeout=25) as client:
#             resp = await client.get(
#                 "https://pixabay.com/api/videos/",
#                 params={
#                     "key": PIXABAY_API_KEY,
#                     "q": word,
#                     "per_page": 40,
#                     "order": "popular"
#                 }
#             )
            
#             if resp.status_code == 200:
#                 videos = resp.json().get("hits", [])
#                 vertical = [v for v in videos if is_vertical_pixabay(v)]
                
#                 if vertical:
#                     logger.info(f"   ✅ Pixabay: Found {len(vertical)} vertical videos for '{word}'")
#                     return {"source": "pixabay", "data": vertical[0]}
#                 else:
#                     logger.info(f"   ⚠️ Pixabay: No vertical videos for '{word}'")
#             else:
#                 logger.warning(f"   ⚠️ Pixabay API: HTTP {resp.status_code}")
            
#             # Try fallback keywords
#             logger.info(f"   Trying Pixabay fallback keywords...")
#             for fb in VERTICAL_FALLBACKS:
#                 resp = await client.get(
#                     "https://pixabay.com/api/videos/",
#                     params={
#                         "key": PIXABAY_API_KEY,
#                         "q": fb,
#                         "per_page": 25
#                     }
#                 )
                
#                 if resp.status_code == 200:
#                     videos = resp.json().get("hits", [])
#                     vertical = [v for v in videos if is_vertical_pixabay(v)]
                    
#                     if vertical:
#                         logger.info(f"   ✅ Pixabay fallback: Found {len(vertical)} videos for '{fb}'")
#                         return {"source": "pixabay", "data": vertical[0]}
        
#         logger.info("   ⚠️ Pixabay: No vertical videos found")
#         return None
        
#     except Exception as e:
#         logger.error(f"Pixabay search error: {e}")
#         return None

# async def search_video(query: str) -> Optional[dict]:
#     """
#     Search for vertical video with priority: Pexels → Pixabay
#     Returns video data or None if not found
#     """
#     logger.info("🔍 Searching for vertical video...")
#     logger.info("   Priority: Pexels (1st) → Pixabay (2nd)")
    
#     # Try Pexels first
#     logger.info("🔍 Step 1: Trying Pexels...")
#     result = await search_pexels_video(query)
    
#     if result:
#         logger.info(f"✅ Video found in Pexels!")
#         return result
    
#     # Fallback to Pixabay
#     logger.info("🔍 Step 2: Pexels not available, trying Pixabay...")
#     result = await search_pixabay_video(query)
    
#     if result:
#         logger.info(f"✅ Video found in Pixabay!")
#         return result
    
#     # No video found
#     logger.error("❌ No vertical video found in Pexels or Pixabay")
#     return None

# # ============================================================================
# # VIDEO DOWNLOAD
# # ============================================================================

# async def download_pexels_video(vdata: dict, output: str) -> bool:
#     """Download video from Pexels"""
#     try:
#         video_files = vdata.get("video_files", [])
        
#         # Filter for HD vertical videos (720p-1920p)
#         hd_files = [f for f in video_files if 720 <= f.get("height", 0) <= 1920]
        
#         if not hd_files:
#             hd_files = video_files
        
#         if not hd_files:
#             logger.error("   No video files available")
#             return False
        
#         # Sort by height (quality) and get best
#         hd_files.sort(key=lambda x: x.get("height", 0), reverse=True)
#         best = hd_files[0]
#         url = best.get("link")
        
#         if not url:
#             logger.error("   No video URL found")
#             return False
        
#         height = best.get("height", 0)
#         logger.info(f"   📥 Downloading Pexels video: {height}p")
#         logger.info(f"   URL: {url[:60]}...")
        
#         async with httpx.AsyncClient(timeout=100) as client:
#             async with client.stream('GET', url) as resp:
#                 if resp.status_code != 200:
#                     logger.error(f"   HTTP {resp.status_code}")
#                     return False
                
#                 with open(output, 'wb') as f:
#                     downloaded = 0
#                     async for chunk in resp.aiter_bytes(CHUNK_SIZE):
#                         f.write(chunk)
#                         downloaded += len(chunk)
                        
#                         # Stop if exceeds limit
#                         if downloaded > MAX_VIDEO_SIZE_MB * 1024 * 1024:
#                             logger.warning(f"   ⚠️ Download stopped: {downloaded/(1024*1024):.1f}MB > {MAX_VIDEO_SIZE_MB}MB")
#                             force_cleanup(output)
#                             return False
                
#                 size = get_size_mb(output)
                
#                 if size < 0.5:
#                     logger.error(f"   Video too small: {size:.2f}MB")
#                     force_cleanup(output)
#                     return False
                
#                 logger.info(f"   ✅ Pexels video downloaded: {size:.1f}MB")
#                 return True
                
#     except Exception as e:
#         logger.error(f"Pexels download error: {e}")
#         force_cleanup(output)
#         return False

# async def download_pixabay_video(vdata: dict, output: str) -> bool:
#     """Download video from Pixabay"""
#     try:
#         videos = vdata.get("videos", {})
        
#         # Priority: medium (720p) > small
#         url = None
#         quality = None
        
#         for size in ["medium", "small"]:
#             if videos.get(size, {}).get("url"):
#                 url = videos[size]["url"]
#                 quality = size
#                 break
        
#         if not url:
#             logger.error("   No video URL found")
#             return False
        
#         logger.info(f"   📥 Downloading Pixabay video: {quality}")
#         logger.info(f"   URL: {url[:60]}...")
        
#         async with httpx.AsyncClient(timeout=100) as client:
#             async with client.stream('GET', url) as resp:
#                 if resp.status_code != 200:
#                     logger.error(f"   HTTP {resp.status_code}")
#                     return False
                
#                 with open(output, 'wb') as f:
#                     downloaded = 0
#                     async for chunk in resp.aiter_bytes(CHUNK_SIZE):
#                         f.write(chunk)
#                         downloaded += len(chunk)
                        
#                         # Stop if exceeds limit
#                         if downloaded > MAX_VIDEO_SIZE_MB * 1024 * 1024:
#                             logger.warning(f"   ⚠️ Download stopped: {downloaded/(1024*1024):.1f}MB > {MAX_VIDEO_SIZE_MB}MB")
#                             force_cleanup(output)
#                             return False
                
#                 size = get_size_mb(output)
                
#                 if size < 0.5:
#                     logger.error(f"   Video too small: {size:.2f}MB")
#                     force_cleanup(output)
#                     return False
                
#                 logger.info(f"   ✅ Pixabay video downloaded: {size:.1f}MB")
#                 return True
                
#     except Exception as e:
#         logger.error(f"Pixabay download error: {e}")
#         force_cleanup(output)
#         return False

# async def download_video(video_result: dict, output: str) -> bool:
#     """Download video from appropriate source"""
#     source = video_result.get("source")
#     vdata = video_result.get("data")
    
#     if source == "pexels":
#         return await download_pexels_video(vdata, output)
#     elif source == "pixabay":
#         return await download_pixabay_video(vdata, output)
    
#     return False

# # ============================================================================
# # VIDEO PROCESSING
# # ============================================================================

# def process_video_fast(source: str, temp_dir: str) -> Optional[str]:
#     """
#     Process video: Loop to 30s, scale to 720p vertical, crop
#     Uses ultrafast preset for speed
#     """
#     try:
#         output = os.path.join(temp_dir, "processed.mp4")
        
#         logger.info("⚙️ Processing video (ultrafast preset)...")
#         logger.info("   - Looping to 30 seconds")
#         logger.info("   - Scaling to 720x1280 (vertical)")
#         logger.info("   - Cropping to fit")
        
#         cmd = [
#             "ffmpeg",
#             "-stream_loop", "-1",  # Loop indefinitely
#             "-i", source,
#             "-t", "30",  # 30 seconds
#             "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
#             "-c:v", "libx264",
#             "-crf", "26",  # Quality (lower = better, 23-28 is good)
#             "-preset", "ultrafast",  # Fastest encoding
#             "-tune", "fastdecode",
#             "-movflags", "+faststart",
#             "-an",  # No audio
#             "-y", output
#         ]
        
#         if run_ffmpeg(cmd, 120):
#             size = get_size_mb(output)
#             logger.info(f"✅ Video processed: {size:.1f}MB")
#             return output
        
#         logger.error("Video processing failed")
#         return None
        
#     except Exception as e:
#         logger.error(f"Processing error: {e}")
#         return None

# def add_text_overlays(video: str, segments: list, temp_dir: str) -> Optional[str]:
#     """Add text overlays at different timestamps"""
#     try:
#         output = os.path.join(temp_dir, "with_text.mp4")
        
#         logger.info("⚙️ Adding text overlays...")
        
#         # Build drawtext filters for all segments
#         filters = []
#         current_time = 0
        
#         for idx, seg in enumerate(segments):
#             text = seg.get("text_overlay", "").replace("'", "").replace('"', '')[:30]
#             if text:
#                 logger.info(f"   Text {idx+1}: '{text}' at {current_time}s")
                
#                 # Create drawtext filter with timing
#                 filters.append(
#                     f"drawtext=text='{text}':"
#                     f"fontsize=55:"
#                     f"fontcolor=white:"
#                     f"x=(w-text_w)/2:"  # Centered horizontally
#                     f"y=h-140:"  # Near bottom
#                     f"borderw=4:"
#                     f"bordercolor=black:"
#                     f"enable='between(t,{current_time},{current_time + seg['duration']})'"
#                 )
            
#             current_time += seg["duration"]
        
#         if not filters:
#             logger.info("   No text overlays to add")
#             return video
        
#         vf = ",".join(filters)
        
#         cmd = [
#             "ffmpeg",
#             "-i", video,
#             "-vf", vf,
#             "-c:v", "libx264",
#             "-crf", "26",
#             "-preset", "ultrafast",
#             "-y", output
#         ]
        
#         if run_ffmpeg(cmd, 90):
#             force_cleanup(video)
#             logger.info(f"✅ Text overlays added: {get_size_mb(output):.1f}MB")
#             return output
        
#         logger.warning("Text overlay failed, using video without text")
#         return video
        
#     except Exception as e:
#         logger.error(f"Text overlay error: {e}")
#         return video

# # ============================================================================
# # AUDIO MIXING
# # ============================================================================

# async def mix_audio_with_music(video: str, voices: List[str], music: Optional[str], temp_dir: str) -> Optional[str]:
#     """
#     Mix voices with background music
#     - Voices: 100% volume
#     - Music: 30% volume with fade in/out
#     """
#     try:
#         logger.info("🎵 Mixing audio...")
        
#         # Step 1: Concatenate all voices
#         logger.info("   Step 1: Concatenating voice segments...")
#         vlist = os.path.join(temp_dir, "voices.txt")
#         with open(vlist, 'w') as f:
#             for v in voices:
#                 f.write(f"file '{v}'\n")
        
#         voice_combined = os.path.join(temp_dir, "voice_all.mp3")
#         cmd = [
#             "ffmpeg",
#             "-f", "concat",
#             "-safe", "0",
#             "-i", vlist,
#             "-c", "copy",
#             "-y", voice_combined
#         ]
        
#         if not run_ffmpeg(cmd, 30):
#             logger.error("Voice concatenation failed")
#             return None
        
#         logger.info(f"   ✅ Voices concatenated: {get_size_mb(voice_combined):.2f}MB")
        
#         # Step 2: Mix with video
#         final = os.path.join(temp_dir, "final.mp4")
        
#         if music and os.path.exists(music):
#             logger.info("   Step 2: Mixing voices + background music...")
#             logger.info("   - Voice: 100% volume")
#             logger.info("   - Music: 30% volume")
#             logger.info("   - Music fade: 1s in, 2s out")
            
#             cmd = [
#                 "ffmpeg",
#                 "-i", video,
#                 "-i", voice_combined,
#                 "-i", music,
#                 "-filter_complex",
#                 "[1:a]volume=1.0[voice];"  # Voice at 100%
#                 "[2:a]volume=0.30,afade=t=in:d=1,afade=t=out:st=28:d=2[music];"  # Music at 30% with fades
#                 "[voice][music]amix=inputs=2:duration=first[audio]",  # Mix both
#                 "-map", "0:v",
#                 "-map", "[audio]",
#                 "-c:v", "copy",
#                 "-c:a", "aac",
#                 "-b:a", "128k",
#                 "-shortest",
#                 "-y", final
#             ]
#         else:
#             logger.info("   Step 2: Mixing voices only (no background music)...")
            
#             cmd = [
#                 "ffmpeg",
#                 "-i", video,
#                 "-i", voice_combined,
#                 "-map", "0:v",
#                 "-map", "1:a",
#                 "-c:v", "copy",
#                 "-c:a", "aac",
#                 "-b:a", "96k",
#                 "-shortest",
#                 "-y", final
#             ]
        
#         if run_ffmpeg(cmd, 60):
#             size = get_size_mb(final)
#             logger.info(f"✅ Final video with audio: {size:.1f}MB")
#             return final
        
#         logger.error("Audio mixing failed")
#         return None
        
#     except Exception as e:
#         logger.error(f"Audio mixing error: {e}")
#         return None

# # ============================================================================
# # YOUTUBE UPLOAD
# # ============================================================================

# async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], 
#                            user_id: str, database_manager) -> dict:
#     """Upload video to YouTube"""
#     try:
#         logger.info("Connecting to YouTube database...")
        
#         from YTdatabase import get_database_manager as get_yt_db
#         yt_db = get_yt_db()
        
#         if not yt_db:
#             return {"success": False, "error": "YouTube database not available"}
        
#         if not yt_db.youtube.client:
#             await yt_db.connect()
        
#         # Get user credentials
#         logger.info(f"Fetching YouTube credentials for user: {user_id}")
        
#         credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
#             "user_id": user_id
#         })
        
#         if not credentials_raw:
#             return {"success": False, "error": "YouTube credentials not found"}
        
#         # Build credentials object
#         credentials = {
#             "access_token": credentials_raw.get("access_token"),
#             "refresh_token": credentials_raw.get("refresh_token"),
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "client_id": credentials_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
#             "client_secret": credentials_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
#             "scopes": [
#                 "https://www.googleapis.com/auth/youtube.upload",
#                 "https://www.googleapis.com/auth/youtube.force-ssl"
#             ]
#         }
        
#         logger.info("Uploading to YouTube...")
        
#         from mainY import youtube_scheduler
        
#         # Combine tags into description
#         full_description = f"{description}\n\n#{' #'.join(tags)}"
        
#         upload_result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             credentials_data=credentials,
#             content_type="shorts",
#             title=title,
#             description=full_description,
#             video_url=video_path
#         )
        
#         if upload_result.get("success"):
#             video_id = upload_result.get("video_id")
#             video_url = f"https://youtube.com/shorts/{video_id}"
            
#             logger.info(f"✅ Video uploaded successfully!")
#             logger.info(f"   Video ID: {video_id}")
#             logger.info(f"   URL: {video_url}")
            
#             return {
#                 "success": True,
#                 "video_id": video_id,
#                 "video_url": video_url
#             }
        
#         return {
#             "success": False,
#             "error": upload_result.get("error", "Upload failed")
#         }
            
#     except Exception as e:
#         logger.error(f"YouTube upload error: {e}")
#         logger.error(traceback.format_exc())
#         return {"success": False, "error": str(e)}

# # ============================================================================
# # MAIN GENERATION PIPELINE
# # ============================================================================

# async def generate_viral_video(
#     niche: str,
#     duration: int,
#     language: str,
#     channel_name: str,
#     show_captions: bool,
#     voice_gender: str,
#     user_id: str,
#     database_manager
# ) -> dict:
#     """
#     Complete viral video generation pipeline
#     Returns success/failure result with video URL
#     """
    
#     temp_dir = None
    
#     try:
#         # Create temporary directory
#         temp_dir = tempfile.mkdtemp(prefix="viral_pixel_")
#         logger.info(f"🎬 Starting generation for niche: {niche}")
#         logger.info(f"   Temp directory: {temp_dir}")
        
#         # ========================================
#         # STEP 1: Generate Script
#         # ========================================
#         logger.info("📝 STEP 1: Generating script...")
#         script = await generate_script(niche)
#         logger.info(f"✅ Script generated")
#         logger.info(f"   Title: {script['title']}")
#         logger.info(f"   Segments: {len(script['segments'])}")
        
#         # ========================================
#         # STEP 2: Download Background Music
#         # ========================================
#         logger.info("🎵 STEP 2: Downloading background music...")
#         music = await download_background_music(temp_dir)
        
#         if music:
#             logger.info(f"✅ Background music ready")
#         else:
#             logger.warning("⚠️ No background music (will continue without)")
        
#         # ========================================
#         # STEP 3: Search & Download Video
#         # ========================================
#         logger.info("📹 STEP 3: Searching and downloading video...")
#         video_result = await search_video(niche)
        
#         if not video_result:
#             return {"success": False, "error": "No suitable vertical video found"}
        
#         video_source = video_result.get("source")
#         logger.info(f"   Video source: {video_source.upper()}")
        
#         source_video = os.path.join(temp_dir, "source.mp4")
        
#         if not await download_video(video_result, source_video):
#             return {"success": False, "error": "Video download failed"}
        
#         logger.info(f"✅ Video downloaded: {get_size_mb(source_video):.1f}MB")
        
#         # ========================================
#         # STEP 4: Process Video
#         # ========================================
#         logger.info("⚙️ STEP 4: Processing video...")
#         processed_video = process_video_fast(source_video, temp_dir)
        
#         # Cleanup source immediately
#         force_cleanup(source_video)
#         gc.collect()
        
#         if not processed_video:
#             return {"success": False, "error": "Video processing failed"}
        
#         # ========================================
#         # STEP 5: Add Text Overlays
#         # ========================================
#         if show_captions:
#             logger.info("📝 STEP 5: Adding text overlays...")
#             processed_video = add_text_overlays(processed_video, script["segments"], temp_dir)
#         else:
#             logger.info("📝 STEP 5: Skipping text overlays (disabled)")
        
#         # ========================================
#         # STEP 6: Generate Voiceovers
#         # ========================================
#         logger.info("🎤 STEP 6: Generating voiceovers...")
#         voices = []
        
#         for idx, seg in enumerate(script["segments"]):
#             logger.info(f"   Generating voice {idx+1}/{len(script['segments'])}...")
#             logger.info(f"   Text: {seg['narration'][:50]}...")
            
#             voice = await generate_voice(seg["narration"], seg["duration"], temp_dir)
            
#             if voice:
#                 voices.append(voice)
#                 logger.info(f"   ✅ Voice {idx+1} generated")
#             else:
#                 logger.warning(f"   ⚠️ Voice {idx+1} failed")
        
#         if len(voices) < 3:
#             return {"success": False, "error": f"Voice generation failed (only {len(voices)}/4 segments)"}
        
#         logger.info(f"✅ {len(voices)} voice segments generated")
        
#         # ========================================
#         # STEP 7: Mix Audio with Video
#         # ========================================
#         logger.info("🎬 STEP 7: Mixing audio with video...")
#         final_video = await mix_audio_with_music(processed_video, voices, music, temp_dir)
        
#         if not final_video:
#             return {"success": False, "error": "Audio mixing failed"}
        
#         final_size = get_size_mb(final_video)
#         logger.info(f"✅ Final video created: {final_size:.1f}MB")
        
#         # ========================================
#         # STEP 8: Upload to YouTube
#         # ========================================
#         logger.info("📤 STEP 8: Uploading to YouTube...")
#         upload_result = await upload_to_youtube(
#             final_video,
#             script["title"],
#             script["description"],
#             script["tags"],
#             user_id,
#             database_manager
#         )
        
#         # ========================================
#         # Cleanup
#         # ========================================
#         logger.info("🧹 Cleaning up temporary files...")
#         if temp_dir:
#             shutil.rmtree(temp_dir, ignore_errors=True)
#         gc.collect()
        
#         # ========================================
#         # Return Result
#         # ========================================
#         if not upload_result.get("success"):
#             return upload_result
        
#         logger.info("🎉 GENERATION COMPLETE!")
        
#         return {
#             "success": True,
#             "video_id": upload_result.get("video_id"),
#             "video_url": upload_result.get("video_url"),
#             "title": script["title"],
#             "description": script["description"],
#             "size_mb": f"{final_size:.1f}MB",
#             "video_source": video_source,
#             "has_music": music is not None,
#             "voice_segments": len(voices)
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Generation failed with error: {e}")
#         logger.error(traceback.format_exc())
        
#         # Cleanup on error
#         if temp_dir:
#             shutil.rmtree(temp_dir, ignore_errors=True)
#         gc.collect()
        
#         return {"success": False, "error": str(e)}

# # ============================================================================
# # API ROUTER
# # ============================================================================

# router = APIRouter()

# @router.get("/api/viral-pixel/niches")
# async def get_niches():
#     """Get available niches for video generation"""
#     return {
#         "success": True,
#         "niches": {
#             k: {"name": k.replace("_", " ").title()} 
#             for k in NICHE_KEYWORDS.keys()
#         }
#     }

# @router.post("/api/viral-pixel/generate")
# async def generate_endpoint(request: Request):
#     """
#     Generate viral video endpoint
#     Accepts niche, user_id, and optional parameters
#     """
#     try:
#         data = await request.json()
#         user_id = data.get("user_id")
        
#         # Validate user_id
#         if not user_id:
#             return JSONResponse(
#                 status_code=401,
#                 content={"success": False, "error": "Authentication required (user_id missing)"}
#             )
        
#         # Validate niche
#         niche = data.get("niche", "space")
#         if niche not in NICHE_KEYWORDS:
#             return JSONResponse(
#                 status_code=400,
#                 content={
#                     "success": False,
#                     "error": f"Invalid niche. Choose from: {list(NICHE_KEYWORDS.keys())}"
#                 }
#             )
        
#         # Import database manager
#         from Supermain import database_manager
        
#         logger.info(f"📨 API Request received")
#         logger.info(f"   User ID: {user_id}")
#         logger.info(f"   Niche: {niche}")
#         logger.info(f"   Show captions: {data.get('show_captions', True)}")
        
#         try:
#             # Generate video with timeout
#             result = await asyncio.wait_for(
#                 generate_viral_video(
#                     niche=niche,
#                     duration=30,
#                     language=data.get("language", "hindi"),
#                     channel_name=data.get("channel_name", ""),
#                     show_captions=data.get("show_captions", True),
#                     voice_gender=data.get("voice_gender", "male"),
#                     user_id=user_id,
#                     database_manager=database_manager
#                 ),
#                 timeout=600  # 10 minute timeout
#             )
            
#             logger.info(f"📤 Sending response: {result.get('success', False)}")
            
#             return JSONResponse(content=result)
            
#         except asyncio.TimeoutError:
#             logger.error("❌ Generation timeout (10 minutes)")
#             return JSONResponse(
#                 status_code=408,
#                 content={"success": False, "error": "Video generation timeout (10 minutes)"}
#             )
        
#     except json.JSONDecodeError:
#         logger.error("❌ Invalid JSON in request")
#         return JSONResponse(
#             status_code=400,
#             content={"success": False, "error": "Invalid JSON in request body"}
#         )
#     except Exception as e:
#         logger.error(f"❌ API endpoint error: {e}")
#         logger.error(traceback.format_exc())
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "error": str(e)}
#         )

# # Export router
# __all__ = ['router']





"""
Viral_pixel.py - PRODUCTION VERSION WITH GOOGLE VERTEX AI
==================================================
✅ Google Vertex AI Text-to-Speech (Chirp 3 HD)
✅ Voice: Orus (Male, Hindi) with 1.1x speed
✅ Horror/Dark/Space Background Music (multiple sources)
✅ Pexels PRIORITY → Pixabay FALLBACK
✅ English Suspenseful Titles + Hindi Narration
✅ Voice + Music Mixing (Voice 100%, Music 30%)
✅ Ultra-fast Processing (720p vertical)
✅ Direct YouTube Upload
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
import base64

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & API KEYS
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# GOOGLE VERTEX AI CONFIGURATION
GOOGLE_API_KEY = os.getenv("GOOGLE_VERTEX_API_KEY", "")  # Your Vertex AI API key
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "socialauto-472509")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")

# VOICE CONFIGURATION
VOICE_SPEED = 1.1  # Narration speed (1.1x faster)
VOICE_NAME = "Orus"  # Male Hindi voice
VOICE_LANGUAGE = "hi-IN"  # Hindi (India)

# PROCESSING LIMITS
MAX_VIDEO_SIZE_MB = 40
FFMPEG_TIMEOUT = 180
TARGET_DURATION = 30
CHUNK_SIZE = 65536

# NICHE KEYWORDS FOR VIDEO SEARCH
NICHE_KEYWORDS = {
    "space": ["galaxy", "nebula", "planet", "cosmos", "stars", "universe"],
    "tech_ai": ["technology", "digital", "cyber", "robot", "ai", "future"],
    "ocean": ["ocean", "wave", "underwater", "reef", "sea", "marine"],
    "nature": ["mountain", "forest", "waterfall", "sunset", "river", "landscape"]
}

# FALLBACK KEYWORDS FOR VERTICAL VIDEOS
VERTICAL_FALLBACKS = ["tower", "building", "city", "waterfall"]

# HORROR/DARK/SPACE BACKGROUND MUSIC URLs (Extended list)
BACKGROUND_MUSIC_URLS = [
    # Dark Cinematic Ambient
    "https://freesound.org/data/previews/614/614090_11931419-lq.mp3",
    
    # Horror Atmosphere
    "https://freesound.org/data/previews/543/543995_11587873-lq.mp3",
    
    # Dark Ambient Space
    "https://freesound.org/data/previews/632/632351_10755880-lq.mp3",
    
    # Mystery Tension
    "https://freesound.org/data/previews/558/558262_11587873-lq.mp3",
    
    # Space Dark Theme
    "https://freesound.org/data/previews/521/521495_9961799-lq.mp3",
    
    # Horror Suspense
    "https://freesound.org/data/previews/477/477718_9497060-lq.mp3",
    
    # Additional Dark Ambient
    "https://freesound.org/data/previews/456/456966_9497060-lq.mp3",
    
    # Eerie Background
    "https://freesound.org/data/previews/398/398787_7517113-lq.mp3"
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def force_cleanup(*filepaths):
    """
    Force cleanup of files with garbage collection
    Removes files and frees memory immediately
    """
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
                logger.info(f"🗑️ Cleaned: {os.path.basename(fp)}")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
            pass
    
    # Force garbage collection
    gc.collect()

def get_size_mb(fp: str) -> float:
    """Get file size in megabytes"""
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0.0

def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """
    Run FFmpeg command with timeout
    Returns True if successful, False otherwise
    """
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
# BACKGROUND MUSIC DOWNLOAD WITH RETRY LOGIC
# ============================================================================

async def download_background_music(temp_dir: str) -> Optional[str]:
    """
    Download horror/dark/space background music with multiple retries
    Tries each URL sequentially until successful
    Returns music file path or None if all attempts fail
    """
    music_path = os.path.join(temp_dir, "bg_music.mp3")
    
    logger.info("🎵 Downloading background music (horror/dark/space theme)...")
    logger.info(f"   Total attempts: {len(BACKGROUND_MUSIC_URLS)}")
    
    for attempt, url in enumerate(BACKGROUND_MUSIC_URLS, 1):
        try:
            logger.info(f"   Attempt {attempt}/{len(BACKGROUND_MUSIC_URLS)}: Trying music source...")
            logger.info(f"   URL: {url[:60]}...")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, follow_redirects=True)
                
                if resp.status_code == 200:
                    # Write music file
                    with open(music_path, 'wb') as f:
                        f.write(resp.content)
                    
                    size = get_size_mb(music_path)
                    
                    # Validate file size (at least 50KB)
                    if size > 0.05:
                        logger.info(f"   ✅ SUCCESS! Background music downloaded: {size:.2f}MB")
                        logger.info(f"   Used attempt {attempt} of {len(BACKGROUND_MUSIC_URLS)}")
                        return music_path
                    else:
                        logger.warning(f"   ⚠️ Music file too small: {size:.2f}MB (< 0.05MB)")
                        force_cleanup(music_path)
                else:
                    logger.warning(f"   ⚠️ HTTP {resp.status_code}")
            
            # Cleanup failed attempt
            force_cleanup(music_path)
            
        except httpx.TimeoutException:
            logger.warning(f"   ⚠️ Attempt {attempt} timed out (30s)")
            force_cleanup(music_path)
        except Exception as e:
            logger.warning(f"   ⚠️ Attempt {attempt} failed: {str(e)[:100]}")
            force_cleanup(music_path)
            continue
    
    # All attempts failed
    logger.warning("⚠️ All background music download attempts failed")
    logger.info("   Will continue without background music")
    return None

# ============================================================================
# SCRIPT GENERATION (ENGLISH TITLE + HINDI NARRATION)
# ============================================================================

async def generate_script(niche: str) -> dict:
    """
    Generate viral script with:
    - English suspenseful title
    - Hindi narration (4 segments: hook, story, climax, outro)
    - Text overlays with emojis
    """
    
    # Suspenseful English title templates
    title_templates = [
        "What Scientists Hide About {topic}",
        "The Dark Truth Behind {topic}",
        "This Will Change How You See {topic}",
        "{topic}: The Shocking Reality",
        "The Secret Of {topic} Revealed",
        "{topic}: What They Don't Want You To Know"
    ]
    
    topic = niche.replace("_", " ").title()
    english_title = random.choice(title_templates).format(topic=topic)
    
    # Mistral AI prompt for Hindi narration
    prompt = f"""Create a VIRAL 30-second Hindi narration for YouTube Shorts about {niche}.

REQUIREMENTS:
- Total duration: 30 seconds
- 4 segments with specific timing
- Hindi language only for narration
- Engaging, mysterious, shocking tone

STRUCTURE:
1. HOOK (8 seconds): "Kya aap jaante hain..." - create mystery and shock
2. STORY (12 seconds): Present amazing facts, "Scientists ne discover kiya..."
3. CLIMAX (7 seconds): "Lekin sabse badi baat..." - build to revelation
4. OUTRO (3 seconds): "Comment mein batao!" - call to action

OUTPUT ONLY THIS JSON:
{{
  "segments": [
    {{"narration": "Hindi hook text here", "text_overlay": "😱", "duration": 8}},
    {{"narration": "Hindi story text here", "text_overlay": "🔥", "duration": 12}},
    {{"narration": "Hindi climax text here", "text_overlay": "💡", "duration": 7}},
    {{"narration": "Hindi outro text here", "text_overlay": "🤔", "duration": 3}}
  ]
}}

Make it VIRAL and ENGAGING!"""
    
    try:
        if MISTRAL_API_KEY:
            logger.info("Calling Mistral AI for script generation...")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
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
                                "content": "You are a viral content creator. Output ONLY valid JSON, no markdown, no explanations."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.9,
                        "max_tokens": 1000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    
                    # Clean up markdown formatting
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    
                    # Extract JSON if wrapped in text
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(0)
                    
                    # Parse JSON
                    script = json.loads(content)
                    
                    logger.info(f"✅ Script generated successfully")
                    logger.info(f"   Segments: {len(script.get('segments', []))}")
                    
                    return {
                        "title": english_title + " #Shorts",
                        "description": f"#{niche} #viral #shorts #mystery",
                        "tags": [niche, "viral", "shorts", "mystery", "facts"],
                        "segments": script["segments"]
                    }
                else:
                    logger.warning(f"Mistral API returned status {resp.status_code}")
                    
    except json.JSONDecodeError as e:
        logger.warning(f"Mistral JSON parse error: {e}")
    except Exception as e:
        logger.warning(f"Mistral API failed: {e}")
    
    # Fallback script (if Mistral fails)
    logger.info("Using fallback script template")
    
    return {
        "title": english_title + " #Shorts",
        "description": f"#{niche} #viral #shorts #mystery",
        "tags": [niche, "viral", "shorts", "mystery"],
        "segments": [
            {
                "narration": "Kya aap jaante hain yeh shocking rahasya jo duniya se chhupa hai?",
                "text_overlay": "😱",
                "duration": 8
            },
            {
                "narration": "Scientists ne discover kiya hai yeh impossible lagta hai lekin sach kuch aur hai! Yeh jaankar aap hairan reh jayenge!",
                "text_overlay": "🔥",
                "duration": 12
            },
            {
                "narration": "Lekin sabse badi baat jo aapko pata honi chahiye... yeh duniya badal degi!",
                "text_overlay": "💡",
                "duration": 7
            },
            {
                "narration": "Toh kya aap vishwas karte hain? Neeche comment mein zaroor batao!",
                "text_overlay": "🤔",
                "duration": 3
            }
        ]
    }

# ============================================================================
# VOICE GENERATION - GOOGLE VERTEX AI
# ============================================================================

async def generate_voice_vertex_ai(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """
    Generate voice using Google Vertex AI Text-to-Speech
    Uses Chirp 3 HD with Orus (Male, Hindi) voice at 1.1x speed
    Returns path to audio file or None if failed
    """
    try:
        # Validate API key
        if not GOOGLE_API_KEY or len(GOOGLE_API_KEY) < 20:
            logger.warning("   ⚠️ Google Vertex AI API key not configured properly")
            return None
        
        # Clean and truncate text
        text_clean = text.strip()[:500]
        temp_raw = os.path.join(temp_dir, f"vertex_{uuid.uuid4().hex[:4]}.mp3")
        
        logger.info(f"   📞 Calling Google Vertex AI...")
        logger.info(f"   Voice: {VOICE_NAME} (Male, Hindi)")
        logger.info(f"   Speed: {VOICE_SPEED}x")
        logger.info(f"   Text length: {len(text_clean)} chars")
        
        # Vertex AI API endpoint
        url = f"https://{GOOGLE_LOCATION}-aiplatform.googleapis.com/v1/projects/{GOOGLE_PROJECT_ID}/locations/{GOOGLE_LOCATION}/publishers/google/models/chirp-3-hd-voices:generateContent"
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {GOOGLE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": text_clean
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "voice": {
                            "name": VOICE_NAME,
                            "languageCode": VOICE_LANGUAGE
                        },
                        "audioEncoding": "LINEAR16",
                        "sampleRateHertz": 22050,
                        "speakingRate": VOICE_SPEED,
                        "volumeGainDb": 0.0
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract audio content from response
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                # Get base64 audio data
                                audio_base64 = part["inlineData"]["data"]
                                audio_bytes = base64.b64decode(audio_base64)
                                
                                # Save raw audio
                                with open(temp_raw, 'wb') as f:
                                    f.write(audio_bytes)
                                
                                size = get_size_mb(temp_raw)
                                
                                if size > 0.01:
                                    logger.info(f"   ✅ Vertex AI response: {size:.2f}MB")
                                    
                                    # Convert to MP3 and adjust duration
                                    output = temp_raw.replace(".mp3", "_adjusted.mp3")
                                    
                                    cmd = [
                                        "ffmpeg",
                                        "-i", temp_raw,
                                        "-filter:a", "loudnorm=I=-16",
                                        "-t", str(duration + 0.5),
                                        "-b:a", "128k",
                                        "-y", output
                                    ]
                                    
                                    if run_ffmpeg(cmd, 20):
                                        force_cleanup(temp_raw)
                                        logger.info(f"   ✅ Vertex AI voice processed: {get_size_mb(output):.2f}MB")
                                        return output
                                    else:
                                        force_cleanup(temp_raw, output)
                                else:
                                    logger.warning(f"   ⚠️ Audio file too small: {size:.2f}MB")
                                    force_cleanup(temp_raw)
                
                logger.error("   ❌ No audio data in Vertex AI response")
                                    
            elif response.status_code == 401:
                logger.error("   ❌ Vertex AI: 401 Unauthorized - Invalid API key")
            elif response.status_code == 429:
                logger.error("   ❌ Vertex AI: 429 Rate limit exceeded")
            else:
                logger.error(f"   ❌ Vertex AI: HTTP {response.status_code}")
                logger.error(f"   Response: {response.text[:200]}")
                
    except httpx.TimeoutException:
        logger.error("   ❌ Vertex AI: Timeout (40s)")
    except Exception as e:
        logger.error(f"   ❌ Vertex AI error: {e}")
        logger.error(traceback.format_exc())
    
    return None

async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """
    Generate voice using Edge TTS (fallback)
    Uses Microsoft's free Text-to-Speech API
    """
    try:
        import edge_tts
        
        temp = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:4]}.mp3")
        text_clean = text.strip()[:350]
        
        logger.info(f"   📞 Using Edge TTS (fallback)...")
        logger.info(f"   Voice: hi-IN-MadhurNeural")
        logger.info(f"   Speed: {VOICE_SPEED}x")
        logger.info(f"   Text length: {len(text_clean)} chars")
        
        # Calculate rate percentage for Edge TTS
        rate_percent = int((VOICE_SPEED - 1.0) * 100)
        rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
        
        # Generate speech
        communicate = edge_tts.Communicate(
            text_clean,
            "hi-IN-MadhurNeural",
            rate=rate_str
        )
        await communicate.save(temp)
        
        size = get_size_mb(temp)
        
        if size > 0.01:
            logger.info(f"   ✅ Edge TTS voice generated: {size:.2f}MB")
            return temp
        
        force_cleanup(temp)
        logger.warning(f"   ⚠️ Edge TTS file too small: {size:.2f}MB")
        
    except ImportError:
        logger.error("   ❌ Edge TTS: edge-tts package not installed")
    except Exception as e:
        logger.error(f"   ❌ Edge TTS error: {e}")
    
    return None

async def generate_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """
    Generate voice with automatic fallback
    1. Try Google Vertex AI (primary)
    2. Fallback to Edge TTS if Vertex AI fails
    """
    # Try Vertex AI first
    voice = await generate_voice_vertex_ai(text, duration, temp_dir)
    if voice:
        return voice
    
    # Fallback to Edge TTS
    logger.warning("   ⚠️ Vertex AI failed, falling back to Edge TTS...")
    return await generate_voice_edge(text, duration, temp_dir)

# ============================================================================
# VIDEO SEARCH - PEXELS PRIORITY, PIXABAY FALLBACK
# ============================================================================

def is_vertical_pexels(vdata: dict) -> bool:
    """Check if Pexels video is vertical (9:16 aspect ratio)"""
    try:
        w = vdata.get("width", 0)
        h = vdata.get("height", 0)
        return w > 0 and h > 0 and (h / w) >= 1.5
    except:
        return False

def is_vertical_pixabay(vdata: dict) -> bool:
    """Check if Pixabay video is vertical"""
    try:
        videos = vdata.get("videos", {})
        for size in ["medium", "small", "large"]:
            sd = videos.get(size, {})
            w, h = sd.get("width", 0), sd.get("height", 0)
            if w > 0 and h > 0 and (h / w) >= 1.5:
                return True
        return False
    except:
        return False

async def search_pexels_video(query: str) -> Optional[dict]:
    """
    Search Pexels for vertical videos (PRIORITY)
    Returns video data or None if not found
    """
    try:
        if not PEXELS_API_KEY:
            logger.warning("⚠️ PEXELS_API_KEY not configured")
            return None
        
        # Clean query
        word = query.split()[0].lower()
        if not word.isascii():
            word = random.choice(VERTICAL_FALLBACKS)
        
        logger.info(f"   Searching Pexels for: '{word}'")
        
        async with httpx.AsyncClient(timeout=25) as client:
            # Search with portrait orientation
            resp = await client.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": word,
                    "orientation": "portrait",
                    "size": "medium",
                    "per_page": 25
                }
            )
            
            if resp.status_code == 200:
                videos = resp.json().get("videos", [])
                vertical = [v for v in videos if is_vertical_pexels(v)]
                
                if vertical:
                    logger.info(f"   ✅ Pexels: Found {len(vertical)} vertical videos for '{word}'")
                    return {"source": "pexels", "data": vertical[0]}
                else:
                    logger.info(f"   ⚠️ Pexels: No vertical videos for '{word}'")
            else:
                logger.warning(f"   ⚠️ Pexels API: HTTP {resp.status_code}")
            
            # Try fallback keywords
            logger.info(f"   Trying Pexels fallback keywords...")
            for fb in VERTICAL_FALLBACKS:
                resp = await client.get(
                    "https://api.pexels.com/videos/search",
                    headers={"Authorization": PEXELS_API_KEY},
                    params={
                        "query": fb,
                        "orientation": "portrait",
                        "size": "medium",
                        "per_page": 15
                    }
                )
                
                if resp.status_code == 200:
                    videos = resp.json().get("videos", [])
                    vertical = [v for v in videos if is_vertical_pexels(v)]
                    
                    if vertical:
                        logger.info(f"   ✅ Pexels fallback: Found {len(vertical)} videos for '{fb}'")
                        return {"source": "pexels", "data": vertical[0]}
        
        logger.info("   ⚠️ Pexels: No vertical videos found")
        return None
        
    except Exception as e:
        logger.error(f"Pexels search error: {e}")
        return None

async def search_pixabay_video(query: str) -> Optional[dict]:
    """
    Search Pixabay for vertical videos (FALLBACK)
    Returns video data or None if not found
    """
    try:
        # Clean query
        word = query.split()[0].lower()
        if not word.isascii():
            word = random.choice(VERTICAL_FALLBACKS)
        
        logger.info(f"   Searching Pixabay for: '{word}'")
        
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": word,
                    "per_page": 40,
                    "order": "popular"
                }
            )
            
            if resp.status_code == 200:
                videos = resp.json().get("hits", [])
                vertical = [v for v in videos if is_vertical_pixabay(v)]
                
                if vertical:
                    logger.info(f"   ✅ Pixabay: Found {len(vertical)} vertical videos for '{word}'")
                    return {"source": "pixabay", "data": vertical[0]}
                else:
                    logger.info(f"   ⚠️ Pixabay: No vertical videos for '{word}'")
            else:
                logger.warning(f"   ⚠️ Pixabay API: HTTP {resp.status_code}")
            
            # Try fallback keywords
            logger.info(f"   Trying Pixabay fallback keywords...")
            for fb in VERTICAL_FALLBACKS:
                resp = await client.get(
                    "https://pixabay.com/api/videos/",
                    params={
                        "key": PIXABAY_API_KEY,
                        "q": fb,
                        "per_page": 25
                    }
                )
                
                if resp.status_code == 200:
                    videos = resp.json().get("hits", [])
                    vertical = [v for v in videos if is_vertical_pixabay(v)]
                    
                    if vertical:
                        logger.info(f"   ✅ Pixabay fallback: Found {len(vertical)} videos for '{fb}'")
                        return {"source": "pixabay", "data": vertical[0]}
        
        logger.info("   ⚠️ Pixabay: No vertical videos found")
        return None
        
    except Exception as e:
        logger.error(f"Pixabay search error: {e}")
        return None

async def search_video(query: str) -> Optional[dict]:
    """
    Search for vertical video with priority: Pexels → Pixabay
    Returns video data or None if not found
    """
    logger.info("🔍 Searching for vertical video...")
    logger.info("   Priority: Pexels (1st) → Pixabay (2nd)")
    
    # Try Pexels first
    logger.info("🔍 Step 1: Trying Pexels...")
    result = await search_pexels_video(query)
    
    if result:
        logger.info(f"✅ Video found in Pexels!")
        return result
    
    # Fallback to Pixabay
    logger.info("🔍 Step 2: Pexels not available, trying Pixabay...")
    result = await search_pixabay_video(query)
    
    if result:
        logger.info(f"✅ Video found in Pixabay!")
        return result
    
    # No video found
    logger.error("❌ No vertical video found in Pexels or Pixabay")
    return None

# ============================================================================
# VIDEO DOWNLOAD
# ============================================================================

async def download_pexels_video(vdata: dict, output: str) -> bool:
    """Download video from Pexels"""
    try:
        video_files = vdata.get("video_files", [])
        
        # Filter for HD vertical videos (720p-1920p)
        hd_files = [f for f in video_files if 720 <= f.get("height", 0) <= 1920]
        
        if not hd_files:
            hd_files = video_files
        
        if not hd_files:
            logger.error("   No video files available")
            return False
        
        # Sort by height (quality) and get best
        hd_files.sort(key=lambda x: x.get("height", 0), reverse=True)
        best = hd_files[0]
        url = best.get("link")
        
        if not url:
            logger.error("   No video URL found")
            return False
        
        height = best.get("height", 0)
        logger.info(f"   📥 Downloading Pexels video: {height}p")
        logger.info(f"   URL: {url[:60]}...")
        
        async with httpx.AsyncClient(timeout=100) as client:
            async with client.stream('GET', url) as resp:
                if resp.status_code != 200:
                    logger.error(f"   HTTP {resp.status_code}")
                    return False
                
                with open(output, 'wb') as f:
                    downloaded = 0
                    async for chunk in resp.aiter_bytes(CHUNK_SIZE):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Stop if exceeds limit
                        if downloaded > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                            logger.warning(f"   ⚠️ Download stopped: {downloaded/(1024*1024):.1f}MB > {MAX_VIDEO_SIZE_MB}MB")
                            force_cleanup(output)
                            return False
                
                size = get_size_mb(output)
                
                if size < 0.5:
                    logger.error(f"   Video too small: {size:.2f}MB")
                    force_cleanup(output)
                    return False
                
                logger.info(f"   ✅ Pexels video downloaded: {size:.1f}MB")
                return True
                
    except Exception as e:
        logger.error(f"Pexels download error: {e}")
        force_cleanup(output)
        return False

async def download_pixabay_video(vdata: dict, output: str) -> bool:
    """Download video from Pixabay"""
    try:
        videos = vdata.get("videos", {})
        
        # Priority: medium (720p) > small
        url = None
        quality = None
        
        for size in ["medium", "small"]:
            if videos.get(size, {}).get("url"):
                url = videos[size]["url"]
                quality = size
                break
        
        if not url:
            logger.error("   No video URL found")
            return False
        
        logger.info(f"   📥 Downloading Pixabay video: {quality}")
        logger.info(f"   URL: {url[:60]}...")
        
        async with httpx.AsyncClient(timeout=100) as client:
            async with client.stream('GET', url) as resp:
                if resp.status_code != 200:
                    logger.error(f"   HTTP {resp.status_code}")
                    return False
                
                with open(output, 'wb') as f:
                    downloaded = 0
                    async for chunk in resp.aiter_bytes(CHUNK_SIZE):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Stop if exceeds limit
                        if downloaded > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                            logger.warning(f"   ⚠️ Download stopped: {downloaded/(1024*1024):.1f}MB > {MAX_VIDEO_SIZE_MB}MB")
                            force_cleanup(output)
                            return False
                
                size = get_size_mb(output)
                
                if size < 0.5:
                    logger.error(f"   Video too small: {size:.2f}MB")
                    force_cleanup(output)
                    return False
                
                logger.info(f"   ✅ Pixabay video downloaded: {size:.1f}MB")
                return True
                
    except Exception as e:
        logger.error(f"Pixabay download error: {e}")
        force_cleanup(output)
        return False

async def download_video(video_result: dict, output: str) -> bool:
    """Download video from appropriate source"""
    source = video_result.get("source")
    vdata = video_result.get("data")
    
    if source == "pexels":
        return await download_pexels_video(vdata, output)
    elif source == "pixabay":
        return await download_pixabay_video(vdata, output)
    
    return False

# ============================================================================
# VIDEO PROCESSING
# ============================================================================

def process_video_fast(source: str, temp_dir: str) -> Optional[str]:
    """
    Process video: Loop to 30s, scale to 720p vertical, crop
    Uses ultrafast preset for speed
    """
    try:
        output = os.path.join(temp_dir, "processed.mp4")
        
        logger.info("⚙️ Processing video (ultrafast preset)...")
        logger.info("   - Looping to 30 seconds")
        logger.info("   - Scaling to 720x1280 (vertical)")
        logger.info("   - Cropping to fit")
        
        cmd = [
            "ffmpeg",
            "-stream_loop", "-1",  # Loop indefinitely
            "-i", source,
            "-t", "30",  # 30 seconds
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-crf", "26",  # Quality (lower = better, 23-28 is good)
            "-preset", "ultrafast",  # Fastest encoding
            "-tune", "fastdecode",
            "-movflags", "+faststart",
            "-an",  # No audio
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 120):
            size = get_size_mb(output)
            logger.info(f"✅ Video processed: {size:.1f}MB")
            return output
        
        logger.error("Video processing failed")
        return None
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return None

def add_text_overlays(video: str, segments: list, temp_dir: str) -> Optional[str]:
    """Add text overlays at different timestamps"""
    try:
        output = os.path.join(temp_dir, "with_text.mp4")
        
        logger.info("⚙️ Adding text overlays...")
        
        # Build drawtext filters for all segments
        filters = []
        current_time = 0
        
        for idx, seg in enumerate(segments):
            text = seg.get("text_overlay", "").replace("'", "").replace('"', '')[:30]
            if text:
                logger.info(f"   Text {idx+1}: '{text}' at {current_time}s")
                
                # Create drawtext filter with timing
                filters.append(
                    f"drawtext=text='{text}':"
                    f"fontsize=55:"
                    f"fontcolor=white:"
                    f"x=(w-text_w)/2:"  # Centered horizontally
                    f"y=h-140:"  # Near bottom
                    f"borderw=4:"
                    f"bordercolor=black:"
                    f"enable='between(t,{current_time},{current_time + seg['duration']})'"
                )
            
            current_time += seg["duration"]
        
        if not filters:
            logger.info("   No text overlays to add")
            return video
        
        vf = ",".join(filters)
        
        cmd = [
            "ffmpeg",
            "-i", video,
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "ultrafast",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 90):
            force_cleanup(video)
            logger.info(f"✅ Text overlays added: {get_size_mb(output):.1f}MB")
            return output
        
        logger.warning("Text overlay failed, using video without text")
        return video
        
    except Exception as e:
        logger.error(f"Text overlay error: {e}")
        return video

# ============================================================================
# AUDIO MIXING
# ============================================================================

async def mix_audio_with_music(video: str, voices: List[str], music: Optional[str], temp_dir: str) -> Optional[str]:
    """
    Mix voices with background music
    - Voices: 100% volume
    - Music: 30% volume with fade in/out
    """
    try:
        logger.info("🎵 Mixing audio...")
        
        # Step 1: Concatenate all voices
        logger.info("   Step 1: Concatenating voice segments...")
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
            logger.error("Voice concatenation failed")
            return None
        
        logger.info(f"   ✅ Voices concatenated: {get_size_mb(voice_combined):.2f}MB")
        
        # Step 2: Mix with video
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            logger.info("   Step 2: Mixing voices + background music...")
            logger.info("   - Voice: 100% volume")
            logger.info("   - Music: 30% volume")
            logger.info("   - Music fade: 1s in, 2s out")
            
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];"  # Voice at 100%
                "[2:a]volume=0.30,afade=t=in:d=1,afade=t=out:st=28:d=2[music];"  # Music at 30% with fades
                "[voice][music]amix=inputs=2:duration=first[audio]",  # Mix both
                "-map", "0:v",
                "-map", "[audio]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", final
            ]
        else:
            logger.info("   Step 2: Mixing voices only (no background music)...")
            
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "96k",
                "-shortest",
                "-y", final
            ]
        
        if run_ffmpeg(cmd, 60):
            size = get_size_mb(final)
            logger.info(f"✅ Final video with audio: {size:.1f}MB")
            return final
        
        logger.error("Audio mixing failed")
        return None
        
    except Exception as e:
        logger.error(f"Audio mixing error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], 
                           user_id: str, database_manager) -> dict:
    """Upload video to YouTube"""
    try:
        logger.info("Connecting to YouTube database...")
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            return {"success": False, "error": "YouTube database not available"}
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        # Get user credentials
        logger.info(f"Fetching YouTube credentials for user: {user_id}")
        
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            return {"success": False, "error": "YouTube credentials not found"}
        
        # Build credentials object
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
        
        logger.info("Uploading to YouTube...")
        
        from mainY import youtube_scheduler
        
        # Combine tags into description
        full_description = f"{description}\n\n#{' #'.join(tags)}"
        
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
        logger.error(f"YouTube upload error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN GENERATION PIPELINE
# ============================================================================

async def generate_viral_video(
    niche: str,
    duration: int,
    language: str,
    channel_name: str,
    show_captions: bool,
    voice_gender: str,
    user_id: str,
    database_manager
) -> dict:
    """
    Complete viral video generation pipeline
    Returns success/failure result with video URL
    """
    
    temp_dir = None
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="viral_pixel_")
        logger.info(f"🎬 Starting generation for niche: {niche}")
        logger.info(f"   Temp directory: {temp_dir}")
        
        # ========================================
        # STEP 1: Generate Script
        # ========================================
        logger.info("📝 STEP 1: Generating script...")
        script = await generate_script(niche)
        logger.info(f"✅ Script generated")
        logger.info(f"   Title: {script['title']}")
        logger.info(f"   Segments: {len(script['segments'])}")
        
        # ========================================
        # STEP 2: Download Background Music
        # ========================================
        logger.info("🎵 STEP 2: Downloading background music...")
        music = await download_background_music(temp_dir)
        
        if music:
            logger.info(f"✅ Background music ready")
        else:
            logger.warning("⚠️ No background music (will continue without)")
        
        # ========================================
        # STEP 3: Search & Download Video
        # ========================================
        logger.info("📹 STEP 3: Searching and downloading video...")
        video_result = await search_video(niche)
        
        if not video_result:
            return {"success": False, "error": "No suitable vertical video found"}
        
        video_source = video_result.get("source")
        logger.info(f"   Video source: {video_source.upper()}")
        
        source_video = os.path.join(temp_dir, "source.mp4")
        
        if not await download_video(video_result, source_video):
            return {"success": False, "error": "Video download failed"}
        
        logger.info(f"✅ Video downloaded: {get_size_mb(source_video):.1f}MB")
        
        # ========================================
        # STEP 4: Process Video
        # ========================================
        logger.info("⚙️ STEP 4: Processing video...")
        processed_video = process_video_fast(source_video, temp_dir)
        
        # Cleanup source immediately
        force_cleanup(source_video)
        gc.collect()
        
        if not processed_video:
            return {"success": False, "error": "Video processing failed"}
        
        # ========================================
        # STEP 5: Add Text Overlays
        # ========================================
        if show_captions:
            logger.info("📝 STEP 5: Adding text overlays...")
            processed_video = add_text_overlays(processed_video, script["segments"], temp_dir)
        else:
            logger.info("📝 STEP 5: Skipping text overlays (disabled)")
        
        # ========================================
        # STEP 6: Generate Voiceovers
        # ========================================
        logger.info("🎤 STEP 6: Generating voiceovers with Google Vertex AI...")
        voices = []
        
        for idx, seg in enumerate(script["segments"]):
            logger.info(f"   Generating voice {idx+1}/{len(script['segments'])}...")
            logger.info(f"   Text: {seg['narration'][:50]}...")
            
            voice = await generate_voice(seg["narration"], seg["duration"], temp_dir)
            
            if voice:
                voices.append(voice)
                logger.info(f"   ✅ Voice {idx+1} generated")
            else:
                logger.warning(f"   ⚠️ Voice {idx+1} failed")
        
        if len(voices) < 3:
            return {"success": False, "error": f"Voice generation failed (only {len(voices)}/4 segments)"}
        
        logger.info(f"✅ {len(voices)} voice segments generated")
        
        # ========================================
        # STEP 7: Mix Audio with Video
        # ========================================
        logger.info("🎬 STEP 7: Mixing audio with video...")
        final_video = await mix_audio_with_music(processed_video, voices, music, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Audio mixing failed"}
        
        final_size = get_size_mb(final_video)
        logger.info(f"✅ Final video created: {final_size:.1f}MB")
        
        # ========================================
        # STEP 8: Upload to YouTube
        # ========================================
        logger.info("📤 STEP 8: Uploading to YouTube...")
        upload_result = await upload_to_youtube(
            final_video,
            script["title"],
            script["description"],
            script["tags"],
            user_id,
            database_manager
        )
        
        # ========================================
        # Cleanup
        # ========================================
        logger.info("🧹 Cleaning up temporary files...")
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        # ========================================
        # Return Result
        # ========================================
        if not upload_result.get("success"):
            return upload_result
        
        logger.info("🎉 GENERATION COMPLETE!")
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script["title"],
            "description": script["description"],
            "size_mb": f"{final_size:.1f}MB",
            "video_source": video_source,
            "has_music": music is not None,
            "voice_segments": len(voices)
        }
        
    except Exception as e:
        logger.error(f"❌ Generation failed with error: {e}")
        logger.error(traceback.format_exc())
        
        # Cleanup on error
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/viral-pixel/niches")
async def get_niches():
    """Get available niches for video generation"""
    return {
        "success": True,
        "niches": {
            k: {"name": k.replace("_", " ").title()} 
            for k in NICHE_KEYWORDS.keys()
        }
    }

@router.post("/api/viral-pixel/generate")
async def generate_endpoint(request: Request):
    """
    Generate viral video endpoint
    Accepts niche, user_id, and optional parameters
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        # Validate user_id
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required (user_id missing)"}
            )
        
        # Validate niche
        niche = data.get("niche", "space")
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Invalid niche. Choose from: {list(NICHE_KEYWORDS.keys())}"
                }
            )
        
        # Import database manager
        from Supermain import database_manager
        
        logger.info(f"📨 API Request received")
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Niche: {niche}")
        logger.info(f"   Show captions: {data.get('show_captions', True)}")
        
        try:
            # Generate video with timeout
            result = await asyncio.wait_for(
                generate_viral_video(
                    niche=niche,
                    duration=30,
                    language=data.get("language", "hindi"),
                    channel_name=data.get("channel_name", ""),
                    show_captions=data.get("show_captions", True),
                    voice_gender=data.get("voice_gender", "male"),
                    user_id=user_id,
                    database_manager=database_manager
                ),
                timeout=600  # 10 minute timeout
            )
            
            logger.info(f"📤 Sending response: {result.get('success', False)}")
            
            return JSONResponse(content=result)
            
        except asyncio.TimeoutError:
            logger.error("❌ Generation timeout (10 minutes)")
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Video generation timeout (10 minutes)"}
            )
        
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in request")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Invalid JSON in request body"}
        )
    except Exception as e:
        logger.error(f"❌ API endpoint error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Export router
__all__ = ['router']