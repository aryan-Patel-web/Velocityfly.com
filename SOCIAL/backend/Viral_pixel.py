
# """
# Viral_pixel.py - MEMORY-OPTIMIZED VIRAL VIDEO GENERATOR
# ✅ Reduced to 6 segments (from 8)
# ✅ Lower resolution downloads (SD instead of HD)
# ✅ Stream processing (download → extract → delete immediately)
# ✅ Parallel processing disabled to save memory
# ✅ 720p output instead of 1080p
# ✅ Aggressive cleanup after each step
# """

# from fastapi import APIRouter, HTTPException, Request
# from fastapi.responses import JSONResponse
# import asyncio
# import logging
# import os
# import sys
# import traceback
# import uuid
# import httpx
# import json
# import re
# import random
# import subprocess
# from datetime import datetime
# from typing import Optional, List, Dict
# import tempfile
# import shutil
# import gc  # Garbage collection

# # Setup logging
# logger = logging.getLogger(__name__)

# # ============================================================================
# # CONFIGURATION & CONSTANTS
# # ============================================================================

# PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "zGWMX93EDxCbRYoJyMw0ADQcbPNmjJ5jvGW5GmahCavl42Nb4Hj")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# # Memory limits
# MAX_VIDEO_SIZE_MB = 15  # Skip videos larger than this
# MAX_TOTAL_MEMORY_MB = 300  # Total memory budget
# SEGMENT_COUNT = 6  # Reduced from 8
# CLIP_DURATION = 5  # Seconds per clip

# # Free background music library
# FREE_MUSIC_LIBRARY = {
#     "upbeat": "https://www.bensound.com/bensound-music/bensound-happyrock.mp3",
#     "calm": "https://www.bensound.com/bensound-music/bensound-slowmotion.mp3",
#     "epic": "https://www.bensound.com/bensound-music/bensound-epic.mp3",
#     "cinematic": "https://www.bensound.com/bensound-music/bensound-inspire.mp3"
# }

# # Niche configurations
# NICHES = {
#     "space": {
#         "name": "Space & Universe 🌌",
#         "search_terms": ["galaxy", "nebula", "planets", "stars", "black hole", "universe"],
#         "cpm": "$4-8",
#         "viral_potential": "Very High"
#     },
#     "tech_ai": {
#         "name": "Technology & AI 🤖",
#         "search_terms": ["artificial intelligence", "robot", "hologram", "futuristic", "circuits"],
#         "cpm": "$6-12",
#         "viral_potential": "Very High"
#     },
#     "ocean": {
#         "name": "Ocean & Marine Life 🌊",
#         "search_terms": ["ocean", "underwater", "coral reef", "dolphins", "sharks"],
#         "cpm": "$3-7",
#         "viral_potential": "High"
#     },
#     "nature": {
#         "name": "Nature & Wildlife 🦁",
#         "search_terms": ["lions", "eagles", "wolves", "forests", "mountains"],
#         "cpm": "$3-6",
#         "viral_potential": "High"
#     },
#     "success": {
#         "name": "Success & Motivation 💪",
#         "search_terms": ["success", "business", "workout", "sunrise", "meditation"],
#         "cpm": "$4-10",
#         "viral_potential": "Very High"
#     },
#     "sports": {
#         "name": "Sports & Fitness ⚽",
#         "search_terms": ["football", "basketball", "gym workout", "athlete", "running"],
#         "cpm": "$3-7",
#         "viral_potential": "High"
#     }
# }

# # ============================================================================
# # MEMORY MANAGEMENT HELPERS
# # ============================================================================

# def cleanup_file(filepath: str):
#     """Immediately delete file and free memory"""
#     try:
#         if filepath and os.path.exists(filepath):
#             os.remove(filepath)
#             logger.info(f"🗑️ Deleted: {os.path.basename(filepath)}")
#     except Exception as e:
#         logger.warning(f"Cleanup failed for {filepath}: {e}")
    
#     # Force garbage collection
#     gc.collect()


# def get_file_size_mb(filepath: str) -> float:
#     """Get file size in MB"""
#     try:
#         return os.path.getsize(filepath) / (1024 * 1024)
#     except:
#         return 0


# # ============================================================================
# # AI SCRIPT GENERATION
# # ============================================================================

# async def generate_ai_script(niche: str, duration: int) -> dict:
#     """Generate viral video script using Groq/Mistral"""
#     try:
#         num_segments = SEGMENT_COUNT  # Fixed to 6
        
#         niche_info = NICHES.get(niche, NICHES["space"])
#         search_terms = niche_info["search_terms"]
        
#         prompt = f"""
# Create a viral {duration}-second video script for {niche_info['name']} niche.

# Requirements:
# - EXACTLY {num_segments} segments (5 seconds each)
# - Hook viewers in first 2 seconds
# - Each segment needs:
#   * narration: 12-15 words max
#   * text_overlay: 3-4 words MAX
#   * video_search: 2 words from: {', '.join(search_terms)}
#   * emoji: One emoji
#   * effect: zoom_in or zoom_out only
#   * saturation: 1.2 to 1.4

# Output ONLY valid JSON:
# {{
#   "title": "Title #Shorts",
#   "description": "Description",
#   "tags": ["tag1", "tag2", "tag3"],
#   "segments": [
#     {{
#       "narration": "Short punchy sentence",
#       "text_overlay": "BIG TEXT",
#       "video_search": "space stars",
#       "emoji": "🌌",
#       "effect": "zoom_in",
#       "saturation": 1.3
#     }}
#   ]
# }}
# """
        
#         # Try Mistral first
#         if MISTRAL_API_KEY:
#             try:
#                 async with httpx.AsyncClient(timeout=20) as client:
#                     response = await client.post(
#                         "https://api.mistral.ai/v1/chat/completions",
#                         headers={
#                             "Authorization": f"Bearer {MISTRAL_API_KEY}",
#                             "Content-Type": "application/json"
#                         },
#                         json={
#                             "model": "mistral-large-latest",
#                             "messages": [
#                                 {"role": "system", "content": "Output ONLY valid JSON."},
#                                 {"role": "user", "content": prompt}
#                             ],
#                             "temperature": 0.8,
#                             "max_tokens": 1000
#                         }
#                     )
                    
#                     if response.status_code == 200:
#                         result = response.json()
#                         ai_response = result["choices"][0]["message"]["content"]
#                         ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
#                         script = json.loads(ai_response)
                        
#                         # Ensure exactly 6 segments
#                         script["segments"] = script["segments"][:SEGMENT_COUNT]
                        
#                         logger.info("✅ Script generated via Mistral")
#                         return script
#             except Exception as e:
#                 logger.warning(f"Mistral failed: {e}")
        
#         # Fallback to Groq
#         if GROQ_API_KEY:
#             try:
#                 async with httpx.AsyncClient(timeout=20) as client:
#                     response = await client.post(
#                         "https://api.groq.com/openai/v1/chat/completions",
#                         headers={
#                             "Authorization": f"Bearer {GROQ_API_KEY}",
#                             "Content-Type": "application/json"
#                         },
#                         json={
#                             "model": "mixtral-8x7b-32768",
#                             "messages": [
#                                 {"role": "system", "content": "Output ONLY valid JSON."},
#                                 {"role": "user", "content": prompt}
#                             ],
#                             "temperature": 0.8,
#                             "max_tokens": 1000
#                         }
#                     )
                    
#                     if response.status_code == 200:
#                         result = response.json()
#                         ai_response = result["choices"][0]["message"]["content"]
#                         ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
#                         script = json.loads(ai_response)
                        
#                         script["segments"] = script["segments"][:SEGMENT_COUNT]
                        
#                         logger.info("✅ Script generated via Groq")
#                         return script
#             except Exception as e:
#                 logger.warning(f"Groq failed: {e}")
        
#         # Fallback template
#         return generate_template_script(niche)
        
#     except Exception as e:
#         logger.error(f"Script generation failed: {e}")
#         return generate_template_script(niche)


# def generate_template_script(niche: str) -> dict:
#     """Fallback template script"""
#     niche_info = NICHES.get(niche, NICHES["space"])
#     search_terms = niche_info["search_terms"]
    
#     segments = []
#     for i in range(SEGMENT_COUNT):
#         segments.append({
#             "narration": f"Amazing {niche} fact number {i+1} will shock you",
#             "text_overlay": f"FACT #{i+1}",
#             "video_search": random.choice(search_terms),
#             "emoji": "🤯",
#             "effect": random.choice(["zoom_in", "zoom_out"]),
#             "saturation": round(random.uniform(1.2, 1.4), 1)
#         })
    
#     return {
#         "title": f"{niche_info['name']} Facts #Shorts",
#         "description": f"Amazing {niche} facts!",
#         "tags": [niche, "facts", "viral"],
#         "segments": segments
#     }


# # ============================================================================
# # PEXELS VIDEO SEARCH & DOWNLOAD (MEMORY OPTIMIZED)
# # ============================================================================

# async def search_pexels_videos_low_res(query: str) -> List[dict]:
#     """Search Pexels for SMALL videos only"""
#     try:
#         async with httpx.AsyncClient(timeout=20) as client:
#             response = await client.get(
#                 "https://api.pexels.com/videos/search",
#                 headers={"Authorization": PEXELS_API_KEY},
#                 params={
#                     "query": query,
#                     "per_page": 3,  # Reduced from 5
#                     "orientation": "portrait",
#                     "size": "small"  # Changed from medium to small
#                 }
#             )
            
#             if response.status_code == 200:
#                 data = response.json()
#                 videos = data.get("videos", [])
                
#                 if videos:
#                     logger.info(f"✅ Found {len(videos)} videos for '{query}'")
#                     return videos
#                 else:
#                     # Try first word
#                     return await search_pexels_videos_low_res(query.split()[0])
#             else:
#                 logger.error(f"Pexels error: {response.status_code}")
#                 return []
                
#     except Exception as e:
#         logger.error(f"Pexels search failed: {e}")
#         return []


# async def download_video_streaming(video_url: str, output_path: str) -> bool:
#     """Download video with size check and streaming"""
#     try:
#         async with httpx.AsyncClient(timeout=30) as client:
#             # Stream download
#             async with client.stream('GET', video_url) as response:
#                 if response.status_code != 200:
#                     return False
                
#                 # Check content length
#                 content_length = response.headers.get('content-length')
#                 if content_length:
#                     size_mb = int(content_length) / (1024 * 1024)
#                     if size_mb > MAX_VIDEO_SIZE_MB:
#                         logger.warning(f"⚠️ Video too large ({size_mb:.1f}MB), skipping")
#                         return False
                
#                 # Stream to file
#                 with open(output_path, 'wb') as f:
#                     async for chunk in response.aiter_bytes(chunk_size=8192):
#                         f.write(chunk)
                
#                 file_size = get_file_size_mb(output_path)
#                 logger.info(f"✅ Downloaded: {file_size:.1f}MB")
#                 return True
                
#     except Exception as e:
#         logger.error(f"Download error: {e}")
#         return False


# # ============================================================================
# # VIDEO PROCESSING (STREAM OPTIMIZED)
# # ============================================================================

# def extract_clip_quick(video_path: str, duration: int = CLIP_DURATION) -> str:
#     """Quick clip extraction from middle"""
#     try:
#         output_path = video_path.replace(".mp4", "_clip.mp4")
        
#         # Extract from middle with lower quality
#         cmd = [
#             "ffmpeg", "-i", video_path,
#             "-ss", "3",  # Start at 3 seconds
#             "-t", str(duration),
#             "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
#             "-c:v", "libx264",
#             "-crf", "28",  # Higher CRF = lower quality = smaller file
#             "-preset", "ultrafast",
#             "-an",  # No audio yet
#             output_path,
#             "-y"
#         ]
        
#         subprocess.run(cmd, capture_output=True, timeout=30)
        
#         if os.path.exists(output_path):
#             size = get_file_size_mb(output_path)
#             logger.info(f"✅ Extracted clip: {size:.1f}MB")
            
#             # Delete original immediately
#             cleanup_file(video_path)
            
#             return output_path
#         else:
#             return video_path
            
#     except Exception as e:
#         logger.error(f"Extract error: {e}")
#         return video_path


# def apply_simple_effect(video_path: str, effect: str, saturation: float) -> str:
#     """Apply simple effects - NO ZOOMPAN to avoid timeout"""
#     try:
#         output_path = video_path.replace(".mp4", "_fx.mp4")
        
#         # SIMPLIFIED: Only scale + saturation (no zoompan - it's too slow)
#         vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=saturation={saturation}"
        
#         cmd = [
#             "ffmpeg", "-i", video_path,
#             "-vf", vf,
#             "-c:v", "libx264",
#             "-crf", "28",
#             "-preset", "ultrafast",
#             output_path,
#             "-y"
#         ]
        
#         subprocess.run(cmd, capture_output=True, timeout=20)
        
#         if os.path.exists(output_path):
#             cleanup_file(video_path)
#             return output_path
#         return video_path
            
#     except Exception as e:
#         logger.error(f"Effect error: {e}")
#         return video_path


# def add_text_simple(video_path: str, text: str, emoji: str) -> str:
#     """Add text overlay - FAST"""
#     try:
#         output_path = video_path.replace(".mp4", "_text.mp4")
        
#         # Simplified text (no emoji if it causes issues)
#         text_escaped = text.replace("'", "'\\''").replace(":", "\\:")
        
#         # Simpler drawtext
#         drawtext = (
#             f"drawtext=text='{text_escaped}':"
#             "fontsize=50:"
#             "fontcolor=white:"
#             "borderw=3:"
#             "bordercolor=black:"
#             "x=(w-text_w)/2:"
#             "y=h-180"
#         )
        
#         cmd = [
#             "ffmpeg", "-i", video_path,
#             "-vf", drawtext,
#             "-c:v", "libx264",
#             "-crf", "28",
#             "-preset", "ultrafast",
#             output_path,
#             "-y"
#         ]
        
#         subprocess.run(cmd, capture_output=True, timeout=20)
        
#         if os.path.exists(output_path):
#             cleanup_file(video_path)
#             return output_path
#         return video_path
            
#     except Exception as e:
#         logger.error(f"Text error: {e}")
#         return video_path


# # ============================================================================
# # VOICEOVER (LIGHTWEIGHT)
# # ============================================================================

# def generate_voiceover_simple(text: str, duration: float) -> str:
#     """Generate simple voiceover"""
#     try:
#         from gtts import gTTS
        
#         temp_file = f"/tmp/voice_{uuid.uuid4().hex[:8]}.mp3"
        
#         tts = gTTS(text=text, lang='en', slow=False)
#         tts.save(temp_file)
        
#         # Stretch to duration using FFmpeg
#         output_file = temp_file.replace(".mp3", "_adj.mp3")
#         cmd = [
#             "ffmpeg", "-i", temp_file,
#             "-filter:a", f"atempo=1.0",
#             "-t", str(duration),
#             output_file,
#             "-y"
#         ]
#         subprocess.run(cmd, capture_output=True, timeout=15)
        
#         cleanup_file(temp_file)
        
#         if os.path.exists(output_file):
#             return output_file
#         return temp_file
        
#     except Exception as e:
#         logger.error(f"Voice error: {e}")
#         return create_silent_audio(duration)


# def create_silent_audio(duration: float) -> str:
#     """Create silent audio"""
#     try:
#         output = f"/tmp/silent_{uuid.uuid4().hex[:8]}.mp3"
#         cmd = [
#             "ffmpeg",
#             "-f", "lavfi",
#             "-i", f"anullsrc=r=44100:cl=mono:d={duration}",
#             "-acodec", "libmp3lame",
#             "-ab", "64k",
#             output,
#             "-y"
#         ]
#         subprocess.run(cmd, capture_output=True, timeout=10)
#         return output
#     except:
#         return None


# # ============================================================================
# # FINAL COMPILATION (OPTIMIZED)
# # ============================================================================

# def compile_video_efficient(clips: List[str], audio_files: List[str], bg_music_path: str = None) -> str:
#     """Compile video efficiently"""
#     try:
#         # Concat video
#         concat_file = f"/tmp/concat_{uuid.uuid4().hex[:8]}.txt"
#         with open(concat_file, 'w') as f:
#             for clip in clips:
#                 f.write(f"file '{clip}'\n")
        
#         temp_video = f"/tmp/video_{uuid.uuid4().hex[:8]}.mp4"
#         cmd = [
#             "ffmpeg", "-f", "concat", "-safe", "0",
#             "-i", concat_file,
#             "-c", "copy",
#             temp_video,
#             "-y"
#         ]
#         subprocess.run(cmd, capture_output=True, timeout=60)
        
#         # Concat audio
#         audio_concat = f"/tmp/audio_concat_{uuid.uuid4().hex[:8]}.txt"
#         with open(audio_concat, 'w') as f:
#             for audio in audio_files:
#                 if audio and os.path.exists(audio):
#                     f.write(f"file '{audio}'\n")
        
#         combined_audio = f"/tmp/audio_{uuid.uuid4().hex[:8]}.mp3"
#         cmd = [
#             "ffmpeg", "-f", "concat", "-safe", "0",
#             "-i", audio_concat,
#             "-c", "copy",
#             combined_audio,
#             "-y"
#         ]
#         subprocess.run(cmd, capture_output=True, timeout=30)
        
#         # Mix
#         final_output = f"/tmp/final_{uuid.uuid4().hex[:8]}.mp4"
        
#         cmd = [
#             "ffmpeg",
#             "-i", temp_video,
#             "-i", combined_audio,
#             "-c:v", "copy",
#             "-c:a", "aac",
#             "-b:a", "96k",
#             "-shortest",
#             final_output,
#             "-y"
#         ]
        
#         subprocess.run(cmd, capture_output=True, timeout=60)
        
#         # Cleanup temps
#         cleanup_file(temp_video)
#         cleanup_file(combined_audio)
#         cleanup_file(concat_file)
#         cleanup_file(audio_concat)
        
#         for clip in clips:
#             cleanup_file(clip)
#         for audio in audio_files:
#             cleanup_file(audio)
        
#         if os.path.exists(final_output):
#             size = get_file_size_mb(final_output)
#             logger.info(f"✅ Final video: {size:.1f}MB")
#             return final_output
        
#         return None
            
#     except Exception as e:
#         logger.error(f"Compilation error: {e}")
#         return None


# # ============================================================================
# # YOUTUBE UPLOAD
# # ============================================================================

# async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], 
#                            user_id: str, database_manager) -> dict:
#     """Upload to YouTube"""
#     try:
#         from YTdatabase import get_database_manager as get_yt_db
#         yt_db = get_yt_db()
        
#         if not yt_db:
#             return {"success": False, "error": "YouTube database not available"}
        
#         if not yt_db.youtube.client:
#             await yt_db.connect()
        
#         credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
#             "user_id": user_id
#         })
        
#         if not credentials_raw:
#             return {"success": False, "error": "YouTube not connected"}
        
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
        
#         from mainY import youtube_scheduler
        
#         # FIXED: Combine tags into description instead of separate parameter
#         full_description = f"{description}\n\n#{' #'.join(tags)}"
        
#         upload_result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             credentials_data=credentials,
#             content_type="shorts",
#             title=f"{title} #Shorts",
#             description=full_description,
#             video_url=video_path
#             # Removed: tags parameter (not supported)
#         )
        
#         if upload_result.get("success"):
#             video_id = upload_result.get("video_id")
#             return {
#                 "success": True,
#                 "video_id": video_id,
#                 "video_url": f"https://youtube.com/shorts/{video_id}"
#             }
        
#         return {
#             "success": False,
#             "error": upload_result.get("error", "Upload failed")
#         }
            
#     except Exception as e:
#         logger.error(f"Upload error: {e}")
#         return {"success": False, "error": str(e)}


# # ============================================================================
# # MAIN GENERATION (OPTIMIZED WORKFLOW)
# # ============================================================================

# async def generate_viral_video(
#     niche: str,
#     duration: int,
#     voice_style: str,
#     bg_music_option: str,
#     custom_music_url: str,
#     user_id: str,
#     database_manager
# ) -> dict:
#     """MEMORY-OPTIMIZED video generation"""
    
#     temp_dir = None
    
#     try:
#         temp_dir = tempfile.mkdtemp(prefix="viral_")
#         logger.info(f"🎬 Starting OPTIMIZED generation")
        
#         # STEP 1: Generate script (6 segments only)
#         logger.info("📝 Step 1: AI Script")
#         script = await generate_ai_script(niche, 30)  # Fixed 30 seconds
        
#         if not script or not script.get("segments"):
#             return {"success": False, "error": "Script failed"}
        
#         logger.info(f"✅ Script: {len(script['segments'])} segments")
        
#         # STEP 2-4: STREAM PROCESSING (one video at a time)
#         logger.info("🎥 Step 2-4: Stream Processing")
        
#         processed_clips = []
#         audio_files = []
        
#         for idx, segment in enumerate(script["segments"]):
#             try:
#                 logger.info(f"Processing segment {idx+1}/6...")
                
#                 # Search
#                 videos = await search_pexels_videos_low_res(segment["video_search"])
#                 if not videos:
#                     logger.warning(f"No video for segment {idx+1}")
#                     continue
                
#                 # Get smallest video
#                 video_files = videos[0]["video_files"]
#                 small_video = min(video_files, key=lambda x: x.get("width", 9999))
                
#                 # Download
#                 video_path = os.path.join(temp_dir, f"v{idx}.mp4")
#                 success = await download_video_streaming(small_video["link"], video_path)
                
#                 if not success:
#                     continue
                
#                 # Extract clip (deletes original)
#                 clip = extract_clip_quick(video_path, CLIP_DURATION)
                
#                 # Apply effect (deletes input)
#                 fx_clip = apply_simple_effect(clip, segment.get("effect", "zoom_in"), segment.get("saturation", 1.3))
                
#                 # Add text (deletes input)
#                 final_clip = add_text_simple(fx_clip, segment.get("text_overlay", ""), segment.get("emoji", ""))
                
#                 processed_clips.append(final_clip)
                
#                 # Generate voice
#                 voice = generate_voiceover_simple(segment.get("narration", ""), CLIP_DURATION)
#                 audio_files.append(voice)
                
#                 # Force cleanup
#                 gc.collect()
                
#             except Exception as e:
#                 logger.error(f"Segment {idx+1} error: {e}")
#                 continue
        
#         if len(processed_clips) < 3:
#             return {"success": False, "error": "Not enough clips"}
        
#         logger.info(f"✅ Processed {len(processed_clips)} clips")
        
#         # STEP 5: Compile
#         logger.info("🎬 Step 5: Compile")
#         final_video = compile_video_efficient(processed_clips, audio_files, None)
        
#         if not final_video:
#             return {"success": False, "error": "Compilation failed"}
        
#         # STEP 6: Upload
#         logger.info("📤 Step 6: Upload")
#         upload_result = await upload_to_youtube(
#             final_video,
#             script.get("title", "Viral Video"),
#             script.get("description", ""),
#             script.get("tags", []),
#             user_id,
#             database_manager
#         )
        
#         # Final cleanup
#         cleanup_file(final_video)
#         if temp_dir and os.path.exists(temp_dir):
#             shutil.rmtree(temp_dir)
        
#         gc.collect()
        
#         if not upload_result.get("success"):
#             return upload_result
        
#         return {
#             "success": True,
#             "video_id": upload_result.get("video_id"),
#             "video_url": upload_result.get("video_url"),
#             "title": script.get("title"),
#             "segments": len(processed_clips)
#         }
        
#     except Exception as e:
#         logger.error(f"Generation failed: {e}")
#         logger.error(traceback.format_exc())
        
#         if temp_dir and os.path.exists(temp_dir):
#             try:
#                 shutil.rmtree(temp_dir)
#             except:
#                 pass
        
#         gc.collect()
        
#         return {"success": False, "error": str(e)}


# # ============================================================================
# # FASTAPI ROUTER
# # ============================================================================

# router = APIRouter()

# @router.get("/api/viral-pixel/niches")
# async def get_niches():
#     """Get available niches"""
#     return {
#         "success": True,
#         "niches": NICHES
#     }


# @router.post("/api/viral-pixel/generate")
# async def generate_video(request: Request):
#     """Generate viral video"""
#     try:
#         data = await request.json()
#         user_id = data.get("user_id")
        
#         if not user_id:
#             return JSONResponse(
#                 status_code=401,
#                 content={"success": False, "error": "Authentication required"}
#             )
        
#         niche = data.get("niche", "space")
#         voice_style = data.get("voice_style", "male")
#         bg_music_option = data.get("bg_music_option", "none")
#         custom_music_url = data.get("custom_music_url")
        
#         if niche not in NICHES:
#             return JSONResponse(
#                 status_code=400,
#                 content={"success": False, "error": "Invalid niche"}
#             )
        
#         from Supermain import database_manager
        
#         result = await generate_viral_video(
#             niche=niche,
#             duration=30,  # Fixed 30 seconds
#             voice_style=voice_style,
#             bg_music_option=bg_music_option,
#             custom_music_url=custom_music_url,
#             user_id=user_id,
#             database_manager=database_manager
#         )
        
#         return JSONResponse(content=result)
        
#     except Exception as e:
#         logger.error(f"Endpoint error: {e}")
#         logger.error(traceback.format_exc())
#         return JSONResponse(
#             status_code=500,
#             content={"success": False, "error": str(e)}
#         )


# __all__ = ['router']











"""
Viral_pixel.py - COMPLETE PRODUCTION VERSION
✅ ONE HD video (LOOP 30 seconds)
✅ Freesound background music (30% volume)
✅ ElevenLabs voice (fallback: Edge TTS)
✅ Full engaging script with hooks
✅ YouTube upload (YOUR credentials method)
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
# CONFIGURATION
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_346aca9fb63af57816b2f0323b6312b75a65aa852656eeac")

# LIMITS
MAX_VIDEO_SIZE_MB = 100
FFMPEG_TIMEOUT = 120
TARGET_DURATION = 30  # 30 seconds total

# KEYWORDS
NICHE_KEYWORDS = {
    "space": ["galaxy", "nebula", "planet", "cosmos", "stars"],
    "tech_ai": ["technology", "digital", "cyber", "robot"],
    "ocean": ["ocean", "wave", "underwater", "reef"],
    "nature": ["mountain", "forest", "waterfall", "sunset", "river"]
}

VERTICAL_FALLBACKS = ["tower", "skyscraper", "tree", "lighthouse"]

# FREESOUND MUSIC URLs (Cinematic/Dark/Ambient)
FREESOUND_MUSIC_URLS = [
    "https://freesound.org/data/previews/614/614090_11931419-lq.mp3",
    "https://freesound.org/data/previews/543/543995_11587873-lq.mp3",
    "https://freesound.org/data/previews/506/506052_9961799-lq.mp3",
    "https://freesound.org/data/previews/477/477718_9497060-lq.mp3"
]

# ============================================================================
# UTILITIES
# ============================================================================

def force_cleanup(*filepaths):
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
                logger.info(f"🗑️ {os.path.basename(fp)}")
        except:
            pass
    gc.collect()

def get_size_mb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg: {result.stderr[:200]}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Timeout {timeout}s")
        return False
    except Exception as e:
        logger.error(f"FFmpeg error: {e}")
        return False

# ============================================================================
# SCRIPT GENERATION
# ============================================================================

async def generate_script(niche: str) -> dict:
    """Generate engaging script"""
    keywords = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    
    prompt = f"""Create VIRAL 30-second Hindi YouTube Shorts script about {niche}.

STRUCTURE:
1. HOOK (8s): "Kya aap jaante hain..." - mystery, shock
2. STORY (12s): Amazing facts, "Scientists kehte hain..."
3. SUSPENSE (7s): "Lekin sabse badi baat..."
4. OUTRO (3s): Question + "Comment mein batao"

OUTPUT JSON:
{{
  "title": "{niche.title()} का रहस्य! #Shorts 🔥",
  "description": "#{niche} #viral #shorts #hindi",
  "tags": ["{niche}", "viral", "shorts"],
  "segments": [
    {{"narration": "...", "text_overlay": "😱 सुनो", "duration": 8}},
    {{"narration": "...", "text_overlay": "🔥 तथ्य", "duration": 12}},
    {{"narration": "...", "text_overlay": "💡 रहस्य", "duration": 7}},
    {{"narration": "...", "text_overlay": "🤔 सवाल", "duration": 3}}
  ]
}}"""
    
    try:
        if MISTRAL_API_KEY:
            async with httpx.AsyncClient(timeout=40) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Create viral Hindi scripts. Output ONLY JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.95,
                        "max_tokens": 2000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    script = json.loads(content)
                    logger.info(f"✅ Script: {len(script['segments'])} segments")
                    return script
    except Exception as e:
        logger.warning(f"Mistral failed: {e}")
    
    # Fallback
    return {
        "title": f"{niche.title()} का रहस्य! #Shorts 🔥",
        "description": f"#{niche} #viral #shorts #hindi",
        "tags": [niche, "viral", "shorts"],
        "segments": [
            {"narration": "Kya aap jaante hain... yeh SHOCKING rahasya!", "text_overlay": "😱 सुनो", "duration": 8},
            {"narration": "Scientists kehte hain... yeh IMPOSSIBLE hai lekin sach kuch aur hai!", "text_overlay": "🔥 तथ्य", "duration": 12},
            {"narration": "Lekin sabse BADI baat... jo aap nahi jaante...", "text_overlay": "💡 रहस्य", "duration": 7},
            {"narration": "Toh batao... kya aap vishwas karte hain? Comment mein batao!", "text_overlay": "🤔 सवाल", "duration": 3}
        ]
    }

# ============================================================================
# ELEVENLABS VOICE (WITH FALLBACK)
# ============================================================================

async def generate_voice_elevenlabs(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """ElevenLabs voice with your API key"""
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            return None
        
        text_clean = text.replace("...", " ").strip()[:500]
        temp_raw = os.path.join(temp_dir, f"eleven_{uuid.uuid4().hex[:4]}.mp3")
        
        # Use Hindi multilingual voice
        voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam (multilingual)
        
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text_clean,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                        "style": 0.0,
                        "use_speaker_boost": True
                    }
                }
            )
            
            if response.status_code == 200:
                with open(temp_raw, 'wb') as f:
                    f.write(response.content)
                
                if get_size_mb(temp_raw) < 0.01:
                    force_cleanup(temp_raw)
                    return None
                
                # Adjust duration
                output = temp_raw.replace(".mp3", "_adj.mp3")
                cmd = [
                    "ffmpeg", "-i", temp_raw,
                    "-filter:a", "atempo=1.15,loudnorm=I=-16",
                    "-t", str(duration + 0.5),
                    "-b:a", "128k",
                    "-y", output
                ]
                
                if run_ffmpeg(cmd, 25):
                    force_cleanup(temp_raw)
                    logger.info(f"✅ ElevenLabs voice: {get_size_mb(output):.2f}MB")
                    return output
                
                force_cleanup(temp_raw, output)
    except Exception as e:
        logger.error(f"ElevenLabs error: {e}")
    
    return None

async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Edge TTS fallback"""
    try:
        import edge_tts
        
        temp = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:4]}.mp3")
        text_clean = text.replace("...", " ").strip()[:400]
        
        communicate = edge_tts.Communicate(text_clean, "hi-IN-MadhurNeural", rate="+20%")
        await communicate.save(temp)
        
        output = temp.replace(".mp3", "_adj.mp3")
        cmd = [
            "ffmpeg", "-i", temp,
            "-af", "loudnorm=I=-16",
            "-t", str(duration + 0.5),
            "-b:a", "128k",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 20):
            force_cleanup(temp)
            logger.info(f"✅ Edge TTS: {get_size_mb(output):.2f}MB")
            return output
        
        force_cleanup(temp, output)
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
    
    return None

async def generate_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Try ElevenLabs first, fallback to Edge TTS"""
    voice = await generate_voice_elevenlabs(text, duration, temp_dir)
    if voice:
        return voice
    
    logger.info("Falling back to Edge TTS")
    return await generate_voice_edge(text, duration, temp_dir)

# ============================================================================
# VIDEO SEARCH & DOWNLOAD
# ============================================================================

def is_vertical(vdata: dict) -> bool:
    try:
        videos = vdata.get("videos", {})
        for size in ["tiny", "small", "medium", "large"]:
            sd = videos.get(size, {})
            w, h = sd.get("width", 0), sd.get("height", 0)
            if w > 0 and h > 0 and (h / w) >= 1.5:
                return True
        return False
    except:
        return False

async def search_hd_video(query: str) -> Optional[dict]:
    """Search ONE HD vertical video"""
    try:
        word = query.split()[0].lower()
        if not word.isascii():
            word = random.choice(VERTICAL_FALLBACKS)
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://pixabay.com/api/videos/",
                params={"key": PIXABAY_API_KEY, "q": word, "per_page": 50, "order": "popular"}
            )
            
            if resp.status_code == 200:
                videos = resp.json().get("hits", [])
                vertical = [v for v in videos if is_vertical(v)]
                if vertical:
                    logger.info(f"✅ Found {len(vertical)} vertical for '{word}'")
                    return vertical[0]
            
            # Fallback
            for fb in VERTICAL_FALLBACKS:
                resp = await client.get(
                    "https://pixabay.com/api/videos/",
                    params={"key": PIXABAY_API_KEY, "q": fb, "per_page": 30}
                )
                if resp.status_code == 200:
                    videos = resp.json().get("hits", [])
                    vertical = [v for v in videos if is_vertical(v)]
                    if vertical:
                        logger.info(f"✅ Fallback '{fb}'")
                        return vertical[0]
        
        return None
    except Exception as e:
        logger.error(f"Search error: {e}")
        return None

async def download_hd_video(vdata: dict, output: str) -> bool:
    """Download HD video"""
    try:
        videos = vdata.get("videos", {})
        # Get best quality: large > medium > small
        url = None
        for size in ["large", "medium", "small"]:
            if videos.get(size, {}).get("url"):
                url = videos[size]["url"]
                break
        
        if not url:
            return False
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream('GET', url) as resp:
                if resp.status_code != 200:
                    return False
                
                with open(output, 'wb') as f:
                    downloaded = 0
                    async for chunk in resp.aiter_bytes(65536):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if downloaded > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                            return False
                
                size = get_size_mb(output)
                if size < 0.5:
                    force_cleanup(output)
                    return False
                
                logger.info(f"✅ HD video: {size:.1f}MB")
                return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        force_cleanup(output)
        return False

# ============================================================================
# BACKGROUND MUSIC FROM FREESOUND
# ============================================================================

async def download_freesound_music(temp_dir: str) -> Optional[str]:
    """Download background music from Freesound"""
    try:
        music_url = random.choice(FREESOUND_MUSIC_URLS)
        music_path = os.path.join(temp_dir, "bg_music.mp3")
        
        async with httpx.AsyncClient(timeout=40) as client:
            resp = await client.get(music_url, follow_redirects=True)
            
            if resp.status_code == 200:
                with open(music_path, 'wb') as f:
                    f.write(resp.content)
                
                if get_size_mb(music_path) > 0.1:
                    logger.info(f"✅ Freesound music: {get_size_mb(music_path):.2f}MB")
                    return music_path
        
        return None
    except Exception as e:
        logger.error(f"Music error: {e}")
        return None

# ============================================================================
# VIDEO LOOP FOR 30 SECONDS
# ============================================================================

def loop_video_30sec(source: str, temp_dir: str) -> Optional[str]:
    """Loop HD video to exactly 30 seconds"""
    try:
        output = os.path.join(temp_dir, "looped.mp4")
        
        # Loop video to 30 seconds
        cmd = [
            "ffmpeg", "-stream_loop", "-1", "-i", source,
            "-t", "30",
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-an",
            "-y", output
        ]
        
        logger.info("⚙️ Looping video to 30 seconds...")
        
        if run_ffmpeg(cmd, 60):
            logger.info(f"✅ Looped video: {get_size_mb(output):.1f}MB")
            return output
        
        return None
    except Exception as e:
        logger.error(f"Loop error: {e}")
        return None

# ============================================================================
# ADD TEXT OVERLAYS TO VIDEO
# ============================================================================

def add_text_overlays(video: str, segments: list, temp_dir: str) -> Optional[str]:
    """Add text overlays at different timestamps"""
    try:
        output = os.path.join(temp_dir, "with_text.mp4")
        
        # Build drawtext filters for all segments
        filters = []
        current_time = 0
        
        for seg in segments:
            text = seg.get("text_overlay", "").replace("'", "").replace('"', '')[:30]
            if text:
                # Show text for segment duration
                filters.append(
                    f"drawtext=text='{text}':fontsize=65:fontcolor=white:"
                    f"x=(w-text_w)/2:y=h-180:borderw=5:bordercolor=black:"
                    f"enable='between(t,{current_time},{current_time + seg['duration']})'"
                )
            current_time += seg["duration"]
        
        if not filters:
            return video
        
        vf = ",".join(filters)
        
        cmd = [
            "ffmpeg", "-i", video,
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-y", output
        ]
        
        logger.info("⚙️ Adding text overlays...")
        
        if run_ffmpeg(cmd, 90):
            force_cleanup(video)
            logger.info(f"✅ With text: {get_size_mb(output):.1f}MB")
            return output
        
        return video
    except Exception as e:
        logger.error(f"Text error: {e}")
        return video

# ============================================================================
# FINAL MIXING: BG MUSIC (30%) + VOICE (100%)
# ============================================================================

async def mix_audio_final(video: str, voices: List[str], music: Optional[str], temp_dir: str) -> Optional[str]:
    """Mix: Background music 30% + Voice 100%"""
    try:
        # Concat voices
        vlist = os.path.join(temp_dir, "voices.txt")
        with open(vlist, 'w') as f:
            for v in voices:
                f.write(f"file '{v}'\n")
        
        voice_all = os.path.join(temp_dir, "voice_all.mp3")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", vlist, "-c", "copy", "-y", voice_all]
        
        if not run_ffmpeg(cmd, 40):
            return None
        
        # Final mix
        final = os.path.join(temp_dir, "final_output.mp4")
        
        if music and os.path.exists(music):
            # BG music 30%, voice 100%
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_all,
                "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];[2:a]volume=0.3,afade=t=in:d=1,afade=t=out:st=28:d=2[bg];[voice][bg]amix=inputs=2:duration=first[audio]",
                "-map", "0:v",
                "-map", "[audio]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-y", final
            ]
        else:
            # Just voice
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_all,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", final
            ]
        
        logger.info("⚙️ Final mixing...")
        
        if run_ffmpeg(cmd, 90):
            logger.info(f"✅ Final video: {get_size_mb(final):.1f}MB")
            return final
        
        return None
    except Exception as e:
        logger.error(f"Mix error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD (FROM YOUR COMMENTED CODE)
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], 
                           user_id: str, database_manager) -> dict:
    """Upload to YouTube using YOUR credentials method"""
    try:
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
            return {"success": False, "error": "YouTube not connected"}
        
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
        
        # Combine tags into description
        full_description = f"{description}\n\n#{' #'.join(tags)}"
        
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=f"{title} #Shorts",
            description=full_description,
            video_url=video_path
        )
        
        if upload_result.get("success"):
            video_id = upload_result.get("video_id")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {
            "success": False,
            "error": upload_result.get("error", "Upload failed")
        }
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN GENERATION
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
    """COMPLETE: HD video loop + BG music + Voice + YouTube upload"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_")
        logger.info(f"🎬 Starting: {niche}")
        
        # Step 1: Script
        script = await generate_script(niche)
        logger.info(f"✅ Title: {script['title']}")
        
        # Step 2: Download Freesound music
        logger.info("🎵 Downloading music...")
        music = await download_freesound_music(temp_dir)
        
        # Step 3: Search & download ONE HD video
        logger.info("📥 Searching HD video...")
        vdata = await search_hd_video(niche)
        
        if not vdata:
            return {"success": False, "error": "No HD video found"}
        
        source = os.path.join(temp_dir, "source.mp4")
        
        if not await download_hd_video(vdata, source):
            return {"success": False, "error": "Download failed"}
        
        # Step 4: Loop video to 30 seconds
        looped = loop_video_30sec(source, temp_dir)
        force_cleanup(source)
        
        if not looped:
            return {"success": False, "error": "Loop failed"}
        
        # Step 5: Add text overlays
        if show_captions:
            with_text = add_text_overlays(looped, script["segments"], temp_dir)
            if with_text:
                looped = with_text
        
        # Step 6: Generate voices for all segments
        logger.info("🎤 Generating voices...")
        voices = []
        
        for idx, seg in enumerate(script["segments"]):
            logger.info(f"Voice {idx+1}/4...")
            voice = await generate_voice(seg["narration"], seg["duration"], temp_dir)
            
            if voice:
                voices.append(voice)
            else:
                # Silent fallback
                silent = os.path.join(temp_dir, f"silent{idx}.mp3")
                cmd = ["ffmpeg", "-f", "lavfi", "-i", f"anullsrc=d={seg['duration']}", "-y", silent]
                if run_ffmpeg(cmd, 15):
                    voices.append(silent)
        
        if len(voices) < 3:
            return {"success": False, "error": "Voice generation failed"}
        
        # Step 7: Final mix (BG music 30% + Voice 100%)
        logger.info("🎬 Final mixing...")
        final = await mix_audio_final(looped, voices, music, temp_dir)
        
        if not final:
            return {"success": False, "error": "Mix failed"}
        
        logger.info(f"🎉 SUCCESS! {get_size_mb(final):.1f}MB")
        
        # Step 8: Upload to YouTube
        logger.info("📤 Uploading to YouTube...")
        upload_result = await upload_to_youtube(
            final,
            script["title"],
            script["description"],
            script["tags"],
            user_id,
            database_manager
        )
        
        # Cleanup
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script["title"],
            "description": script["description"],
            "size_mb": f"{get_size_mb(final):.1f}MB"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}\n{traceback.format_exc()}")
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
    return {
        "success": True,
        "niches": {k: {"name": k.replace("_", " ").title()} for k in NICHE_KEYWORDS.keys()}
    }

@router.post("/api/viral-pixel/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "Auth required"})
        
        niche = data.get("niche", "space")
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(status_code=400, content={"success": False, "error": "Invalid niche"})
        
        from Supermain import database_manager
        
        try:
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
                timeout=600
            )
            
            return JSONResponse(content=result)
            
        except asyncio.TimeoutError:
            return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
        
    except Exception as e:
        logger.error(f"❌ Endpoint error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']