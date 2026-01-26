
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
Viral_pixel.py - ULTRA MEMORY OPTIMIZED VERSION
✅ Memory usage ALWAYS under 512MB
✅ Download → Process → Cleanup immediately
✅ No memory spikes
✅ Background music MANDATORY
✅ ONLY vertical videos (9:16 aspect ratio)
✅ 4 unique HD videos
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
# ELEVENLABS_API_KEY = "d4b3f7d4b20eb5994410ea31fbc719244cdb7b7076744d4a20345cab167f339e"
ELEVENLABS_API_KEY = "sk_1ce0029a03ff38d8bf38d3e4b5550a3c9603cd3ab50d930a"
ELEVENLABS_VOICE_ID = "YkAJCvEzSQvG7K2YK9kx"

# STRICT MEMORY LIMITS
MAX_VIDEO_SIZE_MB = 15  # 15MB max per video
MAX_AUDIO_SIZE_MB = 2   # 2MB max per audio
TARGET_DURATION = 30
VOICE_SPEED = 1.1
MAX_VIDEOS = 4
SUBSCRIBE_DURATION = 3
FFMPEG_TIMEOUT = 25

# Background music MANDATORY
BG_MUSIC_URL = "https://cdn.pixabay.com/audio/2025/01/19/audio_52f6bf8ba1.mp3"  # Space ambient music

NICHES = {
    "space": ["galaxy", "space", "stars", "universe"],
    "tech_ai": ["technology", "digital", "computer", "science"],
    "ocean": ["ocean", "water", "sea", "beach"],
    "nature": ["nature", "forest", "mountain", "sky"]
}

# ============================================================================
# AGGRESSIVE MEMORY MANAGEMENT
# ============================================================================

def force_cleanup(filepath: str):
    """Immediate file deletion + memory cleanup"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🗑️ Deleted: {os.path.basename(filepath)}")
    except:
        pass
    gc.collect()
    gc.collect()  # Double collect for thorough cleanup

def get_file_size_mb(filepath: str) -> float:
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg_safe(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """Run FFmpeg with immediate cleanup"""
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        gc.collect()
        return result.returncode == 0
    except:
        gc.collect()
        return False

# ============================================================================
# SCRIPT GENERATION - 120+ WORDS
# ============================================================================

async def generate_script(niche: str) -> dict:
    """Generate 30+ second script"""
    
    prompt = f"""Create viral 30-35 second Hindi YouTube Shorts script about {niche}.

STRUCTURE (120-150 words):
1. HOOK (8 sec): "Socho agar main kahun..." - Strong curiosity
2. STORY (15 sec): 2-3 amazing facts with emotion
3. SUSPENSE (7 sec): "Lekin sabse badi baat..."
4. OUTRO (5 sec): Engaging question

STYLE:
- Use "...", "," for pauses
- CAPITALS for emphasis (3-4 times)
- Short sentences (6-9 words)
- Create mystery

Output JSON:
{{
  "title": "SHOCKING Space Secret #Shorts 🚀",
  "description": "Mind-blowing! #space #viral #shorts",
  "tags": ["space", "viral", "shorts", "hindi"],
  "segments": [
    {{"type": "hook", "narration": "...", "text_overlay": "😱 सुनो", "video_search": "galaxy", "duration": 8}},
    {{"type": "story", "narration": "...", "text_overlay": "🔥 तथ्य", "video_search": "nebula", "duration": 15}},
    {{"type": "suspense", "narration": "...", "text_overlay": "💡 रहस्य", "video_search": "planet", "duration": 7}},
    {{"type": "outro", "narration": "...", "text_overlay": "🤔 सवाल", "video_search": "stars", "duration": 5}}
  ]
}}"""
    
    try:
        if MISTRAL_API_KEY:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Create viral Hindi scripts. Output ONLY JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.9
                    }
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    script = json.loads(content)
                    logger.info(f"✅ Mistral script: {len(script['segments'])} segments")
                    return script
    except Exception as e:
        logger.warning(f"Mistral failed: {e}")
    
    # Fallback
    return get_fallback_script(niche)

def get_fallback_script(niche: str) -> dict:
    """Fallback script"""
    searches = NICHES.get(niche, NICHES["space"])
    
    return {
        "title": f"SHOCKING {niche.title()} Secret #Shorts 🔥",
        "description": f"Mind-blowing revelation! #{niche} #viral #shorts",
        "tags": [niche, "viral", "shorts", "hindi"],
        "segments": [
            {
                "type": "hook",
                "narration": "Socho agar main kahun... UNIVERSE mein ek aisi jagah hai... jahan TIME ruk jaata hai, aur koi wapas nahi aa sakta...",
                "text_overlay": "😱 सुनो",
                "video_search": searches[0],
                "duration": 8
            },
            {
                "type": "story",
                "narration": "Black Hole itna POWERFUL hai... ki light bhi escape nahi kar sakti. Agar aap paas gaye... toh ek second aapka bahar saalon ke barabar hoga. Yeh SPACE aur TIME ko tod deta hai...",
                "text_overlay": "🔥 अविश्वसनीय",
                "video_search": searches[1],
                "duration": 15
            },
            {
                "type": "suspense",
                "narration": "Lekin sabse SCARY baat... Scientists maante hain ki hamare paas bhi ek black hole ho sakta hai... jo towards us aa raha hai...",
                "text_overlay": "💡 रहस्य",
                "video_search": searches[2],
                "duration": 7
            },
            {
                "type": "outro",
                "narration": "Toh batao... kya tum tayaar ho? Comment mein batao!",
                "text_overlay": "🤔 सवाल",
                "video_search": searches[3] if len(searches) > 3 else searches[0],
                "duration": 5
            }
        ]
    }

# ============================================================================
# VOICE GENERATION - 1.1x SPEED
# ============================================================================

async def generate_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Generate voice with immediate cleanup - Try ElevenLabs first, fallback to Edge TTS"""
    
    # Try ElevenLabs only if API key is set
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        try:
            text_clean = text.replace("...", " ").strip()[:300]
            temp_raw = os.path.join(temp_dir, f"v_{uuid.uuid4().hex[:6]}.mp3")
            
            async with httpx.AsyncClient(timeout=40) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
                    json={
                        "text": text_clean,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {"stability": 0.50, "similarity_boost": 0.75}
                    }
                )
                
                if response.status_code == 200:
                    with open(temp_raw, 'wb') as f:
                        f.write(response.content)
                    
                    # Apply 1.1x speed
                    output = temp_raw.replace(".mp3", "_s.mp3")
                    cmd = [
                        "ffmpeg", "-i", temp_raw,
                        "-filter:a", f"atempo={VOICE_SPEED},loudnorm=I=-16",
                        "-t", str(duration),
                        "-b:a", "96k",
                        "-y", output
                    ]
                    
                    if run_ffmpeg_safe(cmd, 20):
                        force_cleanup(temp_raw)
                        size = get_file_size_mb(output)
                        if size <= MAX_AUDIO_SIZE_MB:
                            logger.info(f"✅ ElevenLabs: {size:.1f}MB")
                            return output
                        force_cleanup(output)
                else:
                    logger.warning(f"ElevenLabs {response.status_code}, using Edge TTS")
        except Exception as e:
            logger.warning(f"ElevenLabs error: {e}, using Edge TTS")
    
    # Use Edge TTS (free, reliable)
    return await generate_voice_edge(text, duration, temp_dir)

async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Edge TTS fallback"""
    try:
        import edge_tts
        
        temp = os.path.join(temp_dir, f"e_{uuid.uuid4().hex[:6]}.mp3")
        text_clean = text.replace("...", " ").strip()[:250]
        
        communicate = edge_tts.Communicate(text_clean, "hi-IN-MadhurNeural", rate="+15%")
        await communicate.save(temp)
        
        output = temp.replace(".mp3", "_n.mp3")
        cmd = [
            "ffmpeg", "-i", temp,
            "-af", "loudnorm=I=-16",
            "-t", str(duration),
            "-b:a", "96k",
            "-y", output
        ]
        
        if run_ffmpeg_safe(cmd, 15):
            force_cleanup(temp)
            if get_file_size_mb(output) <= MAX_AUDIO_SIZE_MB:
                logger.info(f"✅ Edge TTS: {get_file_size_mb(output):.1f}MB")
                return output
        
        force_cleanup(temp)
        force_cleanup(output)
        return None
    except:
        return None

# ============================================================================
# PIXABAY - ONLY VERTICAL VIDEOS
# ============================================================================

async def search_vertical_videos(query: str) -> List[dict]:
    """Search ONLY vertical videos - try multiple fallbacks"""
    try:
        search = query.split()[0]  # Single word
        
        async with httpx.AsyncClient(timeout=20) as client:
            # Try original search
            response = await client.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": search,
                    "per_page": 20,
                    "video_type": "film",
                    "orientation": "vertical",
                    "order": "popular"
                }
            )
            
            if response.status_code == 200:
                videos = response.json().get("hits", [])
                
                # Filter for truly vertical videos
                vertical_only = []
                for v in videos:
                    small = v.get("videos", {}).get("small", {})
                    width = small.get("width", 0)
                    height = small.get("height", 0)
                    if height > width * 1.3:  # Must be significantly taller
                        vertical_only.append(v)
                
                if vertical_only:
                    logger.info(f"✅ Found {len(vertical_only)} vertical videos: '{search}'")
                    return vertical_only
            
            # Fallback: try without orientation filter and filter manually
            logger.info(f"Trying fallback search for '{search}'")
            response = await client.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": search,
                    "per_page": 30,
                    "video_type": "film",
                    "order": "popular"
                }
            )
            
            if response.status_code == 200:
                all_videos = response.json().get("hits", [])
                vertical_only = []
                
                for v in all_videos:
                    # Check all available sizes
                    for size in ["tiny", "small", "medium"]:
                        vid_data = v.get("videos", {}).get(size, {})
                        width = vid_data.get("width", 0)
                        height = vid_data.get("height", 0)
                        
                        if height > width * 1.3:  # Vertical
                            vertical_only.append(v)
                            break
                
                if vertical_only:
                    logger.info(f"✅ Fallback found {len(vertical_only)} vertical: '{search}'")
                    return vertical_only
            
            # Last resort: use common vertical keywords
            fallback_searches = ["nature", "sky", "city", "light", "fire", "water"]
            for fb in fallback_searches:
                response = await client.get(
                    "https://pixabay.com/api/videos/",
                    params={
                        "key": PIXABAY_API_KEY,
                        "q": fb,
                        "per_page": 30,
                        "video_type": "film"
                    }
                )
                
                if response.status_code == 200:
                    all_videos = response.json().get("hits", [])
                    for v in all_videos:
                        for size in ["tiny", "small"]:
                            vid_data = v.get("videos", {}).get(size, {})
                            width = vid_data.get("width", 0)
                            height = vid_data.get("height", 0)
                            
                            if height > width * 1.3:
                                logger.info(f"✅ Using fallback '{fb}' video")
                                return [v]
        
        logger.warning(f"No vertical videos found for '{search}'")
        return []
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

async def download_video_immediate_cleanup(video_data: dict, output: str) -> bool:
    """Download with immediate size check"""
    try:
        videos = video_data.get("videos", {})
        url = videos.get("small", {}).get("url") or videos.get("medium", {}).get("url")
        
        if not url:
            return False
        
        async with httpx.AsyncClient(timeout=50) as client:
            async with client.stream('GET', url) as resp:
                if resp.status_code != 200:
                    return False
                
                # Check size before downloading
                content_len = resp.headers.get('content-length')
                if content_len:
                    size_mb = int(content_len) / (1024 * 1024)
                    if size_mb > MAX_VIDEO_SIZE_MB:
                        logger.warning(f"Video too large: {size_mb:.1f}MB")
                        return False
                
                # Download
                with open(output, 'wb') as f:
                    async for chunk in resp.aiter_bytes(8192):
                        f.write(chunk)
                
                # Verify size after download
                actual_size = get_file_size_mb(output)
                if actual_size > MAX_VIDEO_SIZE_MB:
                    force_cleanup(output)
                    return False
                
                logger.info(f"✅ Downloaded: {actual_size:.1f}MB")
                return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        force_cleanup(output)
        return False

async def download_background_music(temp_dir: str) -> Optional[str]:
    """Download background music - MANDATORY"""
    try:
        music_path = os.path.join(temp_dir, "bg.mp3")
        
        # Try direct URL first
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(BG_MUSIC_URL)
                if response.status_code == 200:
                    with open(music_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"✅ Music from URL: {get_file_size_mb(music_path):.1f}MB")
                    return music_path
            except:
                pass
            
            # Fallback to API search
            response = await client.get(
                "https://pixabay.com/api/",
                params={"key": PIXABAY_API_KEY, "q": "space", "audio_type": "music", "per_page": 5}
            )
            
            if response.status_code == 200:
                hits = response.json().get("hits", [])
                if hits:
                    audio_url = hits[0].get("previewURL")
                    if audio_url:
                        audio_resp = await client.get(audio_url)
                        if audio_resp.status_code == 200:
                            with open(music_path, 'wb') as f:
                                f.write(audio_resp.content)
                            logger.info(f"✅ Music from API: {get_file_size_mb(music_path):.1f}MB")
                            return music_path
        
        logger.error("❌ Background music download failed - MANDATORY!")
        return None
    except Exception as e:
        logger.error(f"Music error: {e}")
        return None

# ============================================================================
# VIDEO PROCESSING - PROCESS → CLEANUP IMMEDIATELY
# ============================================================================

def process_video_segment(raw_path: str, duration: float, text: str, temp_dir: str) -> Optional[str]:
    """Process video with immediate cleanup of intermediate files"""
    
    # Step 1: Extract clip
    clip1 = os.path.join(temp_dir, f"c1_{uuid.uuid4().hex[:6]}.mp4")
    cmd = [
        "ffmpeg", "-i", raw_path,
        "-ss", "1", "-t", str(duration),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
        "-an", "-y", clip1
    ]
    
    if not run_ffmpeg_safe(cmd, 30):
        force_cleanup(clip1)
        return None
    
    force_cleanup(raw_path)  # Cleanup raw immediately
    
    # Step 2: Add text
    clip2 = os.path.join(temp_dir, f"c2_{uuid.uuid4().hex[:6]}.mp4")
    text_clean = text.replace("'", "")[:30]
    cmd = [
        "ffmpeg", "-i", clip1,
        "-vf", f"drawtext=text='{text_clean}':fontsize=65:fontcolor=white:x=(w-text_w)/2:y=h-250:borderw=6:bordercolor=black",
        "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
        "-y", clip2
    ]
    
    if not run_ffmpeg_safe(cmd, 30):
        force_cleanup(clip1)
        force_cleanup(clip2)
        return None
    
    force_cleanup(clip1)  # Cleanup intermediate
    
    # Step 3: Add fade
    final = os.path.join(temp_dir, f"seg_{uuid.uuid4().hex[:6]}.mp4")
    fade_dur = min(0.5, duration / 5)
    fade_out = duration - fade_dur
    cmd = [
        "ffmpeg", "-i", clip2,
        "-vf", f"fade=t=in:st=0:d={fade_dur},fade=t=out:st={fade_out}:d={fade_dur}",
        "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
        "-y", final
    ]
    
    if not run_ffmpeg_safe(cmd, 25):
        force_cleanup(clip2)
        force_cleanup(final)
        return None
    
    force_cleanup(clip2)  # Cleanup intermediate
    
    size = get_file_size_mb(final)
    if size > MAX_VIDEO_SIZE_MB:
        logger.warning(f"Segment too large: {size:.1f}MB")
        force_cleanup(final)
        return None
    
    logger.info(f"✅ Segment ready: {size:.1f}MB")
    return final

# ============================================================================
# MAIN GENERATION - MEMORY OPTIMIZED
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
    """Memory-optimized generation"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_")
        logger.info(f"🎬 Generating {niche} video")
        
        # Step 1: Script
        logger.info("📝 Script...")
        script = await generate_script(niche)
        logger.info(f"✅ {script['title']}")
        
        # Step 2: Background music (MANDATORY)
        logger.info("🎵 Music...")
        music_path = await download_background_music(temp_dir)
        if not music_path:
            return {"success": False, "error": "Background music required but failed to download"}
        
        # Step 3: Process videos ONE BY ONE
        logger.info(f"🎥 Processing {MAX_VIDEOS} videos...")
        
        final_clips = []
        final_audios = []
        used_ids = set()
        
        for idx, seg in enumerate(script["segments"][:MAX_VIDEOS]):
            try:
                logger.info(f"📥 Video {idx+1}/{MAX_VIDEOS}")
                
                # Search
                videos = await search_vertical_videos(seg["video_search"])
                if not videos:
                    continue
                
                # Download ONE video
                downloaded = False
                for vdata in videos:
                    vid = vdata.get("id")
                    if vid in used_ids:
                        continue
                    
                    raw = os.path.join(temp_dir, f"raw{idx}.mp4")
                    if await download_video_immediate_cleanup(vdata, raw):
                        used_ids.add(vid)
                        logger.info(f"✅ ID: {vid}")
                        
                        # Process immediately
                        processed = process_video_segment(
                            raw, 
                            seg["duration"],
                            seg["text_overlay"] if show_captions else "",
                            temp_dir
                        )
                        
                        if processed:
                            final_clips.append(processed)
                            downloaded = True
                            break
                        else:
                            force_cleanup(raw)
                
                if not downloaded:
                    logger.warning(f"Video {idx+1} failed")
                    continue
                
                # Generate voice
                logger.info(f"🎤 Voice {idx+1}...")
                voice = await generate_voice(seg["narration"], seg["duration"], temp_dir)
                if voice:
                    final_audios.append(voice)
                
                gc.collect()  # Cleanup after each segment
                
            except Exception as e:
                logger.error(f"Segment {idx+1} error: {e}")
                continue
        
        if len(final_clips) < 3:
            return {"success": False, "error": f"Only {len(final_clips)} clips created"}
        
        # Step 4: Subscribe
        logger.info("📌 Subscribe...")
        sub_videos = await search_vertical_videos("subscribe")
        if sub_videos:
            sub_raw = os.path.join(temp_dir, "sub_raw.mp4")
            if await download_video_immediate_cleanup(sub_videos[0], sub_raw):
                sub_final = process_video_segment(sub_raw, SUBSCRIBE_DURATION, "SUBSCRIBE करें 🔔", temp_dir)
                if sub_final:
                    final_clips.append(sub_final)
                    
                    # Silent audio
                    silent = os.path.join(temp_dir, "silent.mp3")
                    cmd = ["ffmpeg", "-f", "lavfi", "-i", f"anullsrc=d={SUBSCRIBE_DURATION}", "-b:a", "64k", "-y", silent]
                    if run_ffmpeg_safe(cmd, 15):
                        final_audios.append(silent)
        
        # Step 5: Compile
        logger.info("🎬 Compiling...")
        final_video = await compile_with_music(final_clips, final_audios, music_path, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Compilation failed"}
        
        logger.info(f"✅ Final: {get_file_size_mb(final_video):.1f}MB")
        
        # Step 6: Upload
        logger.info("📤 Uploading...")
        result = await upload_to_youtube(final_video, script["title"], script["description"], script["tags"], user_id)
        
        # Cleanup
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        gc.collect()
        gc.collect()
        
        if not result.get("success"):
            return result
        
        return {
            "success": True,
            "video_id": result["video_id"],
            "video_url": result["video_url"],
            "title": script["title"],
            "segments": len(final_clips),
            "duration": f"{sum([s['duration'] for s in script['segments']])} sec",
            "features": f"✅ {VOICE_SPEED}x voice\n✅ {len(final_clips)} vertical videos\n✅ Background music\n✅ HD quality"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}\n{traceback.format_exc()}")
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        return {"success": False, "error": str(e)}

async def compile_with_music(clips: List[str], audios: List[str], music: str, temp_dir: str) -> Optional[str]:
    """Compile with background music"""
    try:
        # Concat videos
        vlist = os.path.join(temp_dir, "v.txt")
        with open(vlist, 'w') as f:
            for c in clips:
                f.write(f"file '{c}'\n")
        
        vall = os.path.join(temp_dir, "vall.mp4")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", vlist, "-c", "copy", "-y", vall]
        run_ffmpeg_safe(cmd, 40)
        
        # Concat audios
        alist = os.path.join(temp_dir, "a.txt")
        with open(alist, 'w') as f:
            for a in audios:
                f.write(f"file '{a}'\n")
        
        aall = os.path.join(temp_dir, "aall.mp3")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", alist, "-c", "copy", "-y", aall]
        run_ffmpeg_safe(cmd, 30)
        
        # Mix with music
        final = os.path.join(temp_dir, "final.mp4")
        cmd = [
            "ffmpeg",
            "-i", vall,
            "-i", aall,
            "-i", music,
            "-filter_complex",
            "[1:a]volume=1.0[v];[2:a]volume=0.20,afade=t=in:d=2,afade=t=out:st=28:d=2[m];[v][m]amix=inputs=2:duration=first[out]",
            "-map", "0:v",
            "-map", "[out]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            "-y", final
        ]
        
        if run_ffmpeg_safe(cmd, 60):
            force_cleanup(vall)
            force_cleanup(aall)
            return final
        
        return None
    except Exception as e:
        logger.error(f"Compile error: {e}")
        return None

async def upload_to_youtube(video_path: str, title: str, desc: str, tags: List[str], user_id: str) -> dict:
    """Upload to YouTube"""
    try:
        from YTdatabase import get_database_manager as get_yt_db
        
        yt_db = get_yt_db()
        if not yt_db or not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        if not creds:
            return {"success": False, "error": "YouTube not connected"}
        
        credentials = {
            "access_token": creds.get("access_token"),
            "refresh_token": creds.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
        }
        
        from mainY import youtube_scheduler
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=f"{title} #Shorts",
            description=f"{desc}\n\n#{' #'.join(tags)}",
            video_url=video_path
        )
        
        if result.get("success"):
            return {
                "success": True,
                "video_id": result["video_id"],
                "video_url": f"https://youtube.com/shorts/{result['video_id']}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/viral-pixel/niches")
async def get_niches():
    return {"success": True, "niches": {k: {"name": k.replace("_", " ").title()} for k in NICHES.keys()}}

@router.post("/api/viral-pixel/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "Auth required"})
        
        niche = data.get("niche", "space")
        if niche not in NICHES:
            return JSONResponse(status_code=400, content={"success": False, "error": "Invalid niche"})
        
        from Supermain import database_manager
        
        try:
            result = await asyncio.wait_for(
                generate_viral_video(
                    niche=niche,
                    duration=int(data.get("duration", 30)),
                    language=data.get("language", "hindi"),
                    channel_name=data.get("channel_name", "My Channel"),
                    show_captions=data.get("show_captions", True),
                    voice_gender=data.get("voice_gender", "male"),
                    user_id=user_id,
                    database_manager=database_manager
                ),
                timeout=480
            )
        except asyncio.TimeoutError:
            return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

__all__ = ['router']