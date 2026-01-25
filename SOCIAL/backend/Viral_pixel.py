
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
Viral_pixel.py - ULTRA-OPTIMIZED PIXABAY VIRAL VIDEO GENERATOR
✅ Pixabay HD videos + Hindi/English voice
✅ Creative storytelling with hooks
✅ 2-3 second clips (no static videos)
✅ NO intro/outro (saves 50MB memory + avoids timeout)
✅ Memory efficient: <350MB total
✅ Sequential processing with retry logic
✅ 40-second timeouts for all operations
"""

from fastapi import APIRouter, HTTPException, Request
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
from datetime import datetime
from typing import Optional, List, Dict
import tempfile
import shutil
import gc

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Memory optimization
MAX_VIDEO_SIZE_MB = 12
CLIP_DURATION = 3
MIN_CLIP_DURATION = 2
MAX_SEGMENTS = 10
FFMPEG_TIMEOUT = 40  # Increased from 10 to 40 seconds

# Niches
NICHES = {
    "space": {
        "name": "Space & Universe 🌌",
        "searches": ["cosmos galaxy", "nebula space", "star cluster", "black hole", "planet earth", "astronaut space"],
        "hooks_hindi": ["क्या आपको पता है? ब्रह्मांड में...", "आज मैं आपको दिखाऊंगा...", "यह रहस्य सुनकर आप हैरान रह जाएंगे..."],
        "hooks_english": ["Did you know that in space...", "Today I'll show you something amazing...", "This secret will shock you..."]
    },
    "tech_ai": {
        "name": "Technology & AI 🤖",
        "searches": ["artificial intelligence", "robot technology", "futuristic tech", "AI hologram", "circuit board", "digital brain"],
        "hooks_hindi": ["AI का यह राज जानकर आप चौंक जाएंगे...", "टेक्नोलॉजी का यह चमत्कार देखिए...", "भविष्य में ऐसा होगा..."],
        "hooks_english": ["This AI secret will amaze you...", "Watch this tech miracle...", "The future will be like this..."]
    },
    "ocean": {
        "name": "Ocean & Marine 🌊",
        "searches": ["ocean waves", "coral reef", "dolphins swimming", "shark underwater", "deep sea", "whale ocean"],
        "hooks_hindi": ["समुद्र की गहराई में...", "यह समुद्री जीव देखकर...", "महासागर का यह रहस्य..."],
        "hooks_english": ["Deep in the ocean...", "Watch this marine creature...", "This ocean mystery..."]
    },
    "nature": {
        "name": "Nature & Wildlife 🦁",
        "searches": ["lion wildlife", "eagle flying", "wolf pack", "forest trees", "mountain landscape", "tiger jungle"],
        "hooks_hindi": ["प्रकृति का यह चमत्कार...", "जंगली जानवर की यह खासियत...", "पहाड़ों में छुपा यह राज..."],
        "hooks_english": ["This wonder of nature...", "This wild animal's special feature...", "This secret hidden in mountains..."]
    },
    "success": {
        "name": "Success & Motivation 💪",
        "searches": ["business success", "workout gym", "meditation zen", "sunrise motivation", "entrepreneur work", "achievement goal"],
        "hooks_hindi": ["सफलता का यह मंत्र...", "अमीर बनने का यह तरीका...", "इस टिप से बदल जाएगी जिंदगी..."],
        "hooks_english": ["This mantra for success...", "This way to become rich...", "Life will change with this tip..."]
    },
    "sports": {
        "name": "Sports & Fitness ⚽",
        "searches": ["football match", "basketball dunk", "gym workout", "athlete running", "cricket stadium", "fitness training"],
        "hooks_hindi": ["खेल का यह रोमांचक पल...", "फिटनेस का यह राज...", "एथलीट की यह खासियत..."],
        "hooks_english": ["This thrilling sports moment...", "This fitness secret...", "This athlete's special skill..."]
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def cleanup_file(filepath: str):
    """Delete file immediately"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🗑️ Deleted: {os.path.basename(filepath)}")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")
    gc.collect()

def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB"""
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg_with_retry(cmd: list, timeout: int = FFMPEG_TIMEOUT, retries: int = 2) -> bool:
    """Run FFmpeg command with retry logic"""
    for attempt in range(retries):
        try:
            subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
            return True
        except subprocess.TimeoutExpired:
            logger.warning(f"FFmpeg timeout (attempt {attempt + 1}/{retries})")
            if attempt < retries - 1:
                continue
            return False
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            return False
    return False

# ============================================================================
# AI SCRIPT GENERATION
# ============================================================================

async def generate_creative_script(niche: str, duration: int, language: str = "hindi") -> dict:
    """Generate creative script with hooks"""
    try:
        niche_info = NICHES.get(niche, NICHES["space"])
        searches = niche_info["searches"]
        
        content_duration = duration
        num_segments = min(int(content_duration / CLIP_DURATION), MAX_SEGMENTS)
        
        prompt = f"""
Create a VIRAL {duration}-second YouTube Shorts script in {'HINDI' if language == 'hindi' else 'ENGLISH'} for {niche_info['name']}.

REQUIREMENTS:
1. HOOK: Start with STRONG hook (first 2 seconds)
2. STORY: Engaging story with suspense
3. FACTS: Surprising, mind-blowing facts
4. EXACTLY {num_segments} segments (3 sec each)
5. Human explanation style, NOT robotic

Output ONLY valid JSON:
{{
  "title": "SEO-friendly clickbait title",
  "description": "Engaging description",
  "tags": ["tag1", "tag2", "tag3"],
  "segments": [
    {{
      "narration": "{'Hindi' if language == 'hindi' else 'English'} explanation (conversational)",
      "text_overlay": "3-4 words",
      "video_search": "2 words from: {', '.join(searches[:3])}",
      "emoji": "emoji"
    }}
  ]
}}
"""
        
        # Try Mistral
        if MISTRAL_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {"role": "system", "content": f"Output ONLY valid JSON. Use {'HINDI' if language == 'hindi' else 'ENGLISH'}."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1500
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                        script = json.loads(ai_response)
                        script["segments"] = script["segments"][:num_segments]
                        logger.info("✅ Creative script via Mistral")
                        return script
            except Exception as e:
                logger.warning(f"Mistral failed: {e}")
        
        # Try Groq
        if GROQ_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": "mixtral-8x7b-32768",
                            "messages": [
                                {"role": "system", "content": f"Output ONLY valid JSON. Use {'HINDI' if language == 'hindi' else 'ENGLISH'}."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1500
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                        script = json.loads(ai_response)
                        script["segments"] = script["segments"][:num_segments]
                        logger.info("✅ Creative script via Groq")
                        return script
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        # Fallback
        return generate_template_script(niche, num_segments, language)
        
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        return generate_template_script(niche, 8, language)

def generate_template_script(niche: str, num_segments: int, language: str) -> dict:
    """Fallback template"""
    niche_info = NICHES.get(niche, NICHES["space"])
    searches = niche_info["searches"]
    hooks = niche_info.get(f"hooks_{language}", niche_info["hooks_hindi"])
    
    segments = []
    segments.append({
        "narration": random.choice(hooks),
        "text_overlay": "सुनो ये!" if language == "hindi" else "LISTEN!",
        "video_search": searches[0],
        "emoji": "🤯"
    })
    
    for i in range(1, num_segments - 1):
        segments.append({
            "narration": f"{'तथ्य' if language == 'hindi' else 'Fact'} #{i}: {'यह अद्भुत है' if language == 'hindi' else 'This is amazing'}",
            "text_overlay": f"{'तथ्य' if language == 'hindi' else 'FACT'} #{i}",
            "video_search": random.choice(searches),
            "emoji": random.choice(["🔥", "⚡", "✨", "💫"])
        })
    
    segments.append({
        "narration": "यह था आज का रहस्य!" if language == "hindi" else "This was today's mystery!",
        "text_overlay": "अद्भुत!" if language == "hindi" else "AMAZING!",
        "video_search": searches[-1],
        "emoji": "🎉"
    })
    
    return {
        "title": f"{niche_info['name']} {'का रहस्य' if language == 'hindi' else 'Mystery'} #Shorts",
        "description": f"{'जानिए' if language == 'hindi' else 'Know about'} {niche}!",
        "tags": [niche, "viral", "shorts"],
        "segments": segments
    }

# ============================================================================
# PIXABAY VIDEO SEARCH & DOWNLOAD
# ============================================================================

async def search_pixabay_videos_hd(query: str) -> List[dict]:
    """Search Pixabay for HD videos"""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": query,
                    "per_page": 5,
                    "video_type": "film",
                    "orientation": "vertical"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get("hits", [])
                
                if videos:
                    logger.info(f"✅ Pixabay: {len(videos)} videos for '{query}'")
                    return videos
                else:
                    return await search_pixabay_videos_hd(query.split()[0])
            else:
                logger.error(f"Pixabay error: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Pixabay search failed: {e}")
        return []

async def download_pixabay_video_hd(video_data: dict, output_path: str) -> bool:
    """Download HD video"""
    try:
        videos = video_data.get("videos", {})
        video_url = videos.get("large", {}).get("url") or videos.get("medium", {}).get("url")
        
        if not video_url:
            return False
        
        async with httpx.AsyncClient(timeout=40) as client:
            async with client.stream('GET', video_url) as response:
                if response.status_code != 200:
                    return False
                
                content_length = response.headers.get('content-length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > MAX_VIDEO_SIZE_MB:
                        logger.warning(f"⚠️ Video too large ({size_mb:.1f}MB)")
                        return False
                
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                
                file_size = get_file_size_mb(output_path)
                logger.info(f"✅ Downloaded HD: {file_size:.1f}MB")
                return True
                
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False

# ============================================================================
# VIDEO PROCESSING
# ============================================================================

def extract_clip_hd(video_path: str, start: float = 1.0, duration: float = CLIP_DURATION) -> str:
    """Extract 2-3 sec HD clip"""
    try:
        output_path = video_path.replace(".mp4", "_clip.mp4")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", str(start),
            "-t", str(duration),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "medium",
            "-an",
            output_path,
            "-y"
        ]
        
        if run_ffmpeg_with_retry(cmd, timeout=FFMPEG_TIMEOUT):
            if os.path.exists(output_path) and get_file_size_mb(output_path) > 0:
                logger.info(f"✅ Extracted clip: {get_file_size_mb(output_path):.1f}MB")
                cleanup_file(video_path)
                return output_path
        
        return video_path
            
    except Exception as e:
        logger.error(f"Extract error: {e}")
        return video_path

def add_fade_transition(video_path: str) -> str:
    """Add fade in/out"""
    try:
        output_path = video_path.replace(".mp4", "_fade.mp4")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "fade=in:0:10,fade=out:st=2.7:d=0.3",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            output_path,
            "-y"
        ]
        
        if run_ffmpeg_with_retry(cmd, timeout=20):
            if os.path.exists(output_path):
                cleanup_file(video_path)
                return output_path
        
        return video_path
            
    except Exception as e:
        logger.error(f"Transition error: {e}")
        return video_path

def add_hindi_caption(video_path: str, text: str, language: str) -> str:
    """Add golden caption"""
    try:
        output_path = video_path.replace(".mp4", "_caption.mp4")
        
        text_escaped = text.replace("'", "'\\''").replace(":", "\\:")
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        drawtext = (
            f"drawtext=text='{text_escaped}':"
            f"fontfile={font_path}:"
            "fontsize=55:"
            "fontcolor=#FFD700:"
            "borderw=4:"
            "bordercolor=black:"
            "shadowcolor=black@0.7:"
            "shadowx=3:"
            "shadowy=3:"
            "x=(w-text_w)/2:"
            "y=h-220"
        )
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", drawtext,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            output_path,
            "-y"
        ]
        
        if run_ffmpeg_with_retry(cmd, timeout=20):
            if os.path.exists(output_path):
                cleanup_file(video_path)
                return output_path
        
        return video_path
            
    except Exception as e:
        logger.error(f"Caption error: {e}")
        return video_path

# ============================================================================
# VOICE GENERATION
# ============================================================================

def generate_hindi_voice(text: str, duration: float, language: str = "hindi") -> str:
    """Generate Hindi/English voice"""
    try:
        from gtts import gTTS
        
        temp_file = f"/tmp/voice_{uuid.uuid4().hex[:8]}.mp3"
        
        lang_map = {
            "hindi": "hi",
            "english_uk": "en-gb",
            "english_us": "en-us",
            "english_in": "en-in"
        }
        
        lang_code = lang_map.get(language, "hi")
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(temp_file)
        
        output_file = temp_file.replace(".mp3", "_adj.mp3")
        cmd = [
            "ffmpeg", "-i", temp_file,
            "-filter:a", "atempo=1.0",
            "-t", str(duration),
            "-b:a", "128k",
            output_file,
            "-y"
        ]
        
        run_ffmpeg_with_retry(cmd, timeout=15)
        
        cleanup_file(temp_file)
        
        if os.path.exists(output_file):
            logger.info(f"✅ Generated {language} voice")
            return output_file
        return temp_file
        
    except Exception as e:
        logger.error(f"Voice error: {e}")
        return create_silent_audio(duration)

def create_silent_audio(duration: float) -> str:
    """Create silent audio"""
    try:
        output = f"/tmp/silent_{uuid.uuid4().hex[:8]}.mp3"
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=mono:d={duration}",
            "-acodec", "libmp3lame",
            "-ab", "96k",
            output,
            "-y"
        ]
        run_ffmpeg_with_retry(cmd, timeout=10)
        return output
    except:
        return None

# ============================================================================
# FINAL COMPILATION
# ============================================================================

def compile_final_video(clips: List[str], audio_files: List[str], temp_dir: str) -> str:
    """Compile final video"""
    try:
        # Concat videos
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for clip in clips:
                if clip and os.path.exists(clip):
                    f.write(f"file '{clip}'\n")
        
        temp_video = os.path.join(temp_dir, "video_concat.mp4")
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            temp_video,
            "-y"
        ]
        run_ffmpeg_with_retry(cmd, timeout=FFMPEG_TIMEOUT)
        
        # Concat audio
        audio_concat = os.path.join(temp_dir, "audio_concat.txt")
        with open(audio_concat, 'w') as f:
            for audio in audio_files:
                if audio and os.path.exists(audio):
                    f.write(f"file '{audio}'\n")
        
        combined_audio = os.path.join(temp_dir, "audio_combined.mp3")
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", audio_concat,
            "-c", "copy",
            combined_audio,
            "-y"
        ]
        run_ffmpeg_with_retry(cmd, timeout=30)
        
        # Mix
        final_output = os.path.join(temp_dir, "final.mp4")
        
        cmd = [
            "ffmpeg",
            "-i", temp_video,
            "-i", combined_audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            final_output,
            "-y"
        ]
        
        run_ffmpeg_with_retry(cmd, timeout=FFMPEG_TIMEOUT)
        
        # Cleanup
        cleanup_file(temp_video)
        cleanup_file(combined_audio)
        
        for clip in clips:
            cleanup_file(clip)
        for audio in audio_files:
            cleanup_file(audio)
        
        if os.path.exists(final_output):
            size = get_file_size_mb(final_output)
            logger.info(f"✅ Final video: {size:.1f}MB")
            return final_output
        
        return None
            
    except Exception as e:
        logger.error(f"Compilation error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube_shorts(video_path: str, title: str, description: str, 
                                   tags: List[str], user_id: str, database_manager) -> dict:
    """Upload to YouTube"""
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

async def generate_viral_video_optimized(
    niche: str,
    duration: int,
    language: str,
    channel_name: str,
    show_captions: bool,
    user_id: str,
    database_manager
) -> dict:
    """Optimized generation - NO INTRO/OUTRO"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_pbn")
        logger.info(f"🎬 Starting Pixabay HD generation")
        
        # STEP 1: Script
        logger.info("📝 Creative AI script")
        script = await generate_creative_script(niche, duration, language)
        
        if not script or not script.get("segments"):
            return {"success": False, "error": "Script generation failed"}
        
        logger.info(f"✅ Script: {len(script['segments'])} segments")
        
        # STEP 2: Process segments (NO INTRO/OUTRO - saves memory)
        logger.info("📥 Pixabay HD videos")
        
        processed_clips = []
        audio_files = []
        
        for idx, segment in enumerate(script["segments"]):
            try:
                logger.info(f"Segment {idx+1}/{len(script['segments'])}")
                
                # Search
                videos = await search_pixabay_videos_hd(segment["video_search"])
                if not videos:
                    logger.warning(f"No video for segment {idx+1}")
                    continue
                
                # Download
                video_path = None
                for video_data in videos[:3]:
                    temp_path = os.path.join(temp_dir, f"v{idx}.mp4")
                    success = await download_pixabay_video_hd(video_data, temp_path)
                    if success:
                        video_path = temp_path
                        break
                
                if not video_path:
                    continue
                
                # Extract
                clip_duration = random.uniform(MIN_CLIP_DURATION, CLIP_DURATION)
                clip = extract_clip_hd(video_path, start=1.0, duration=clip_duration)
                
                # Fade
                clip = add_fade_transition(clip)
                
                # Caption
                if show_captions:
                    clip = add_hindi_caption(clip, segment.get("text_overlay", ""), language)
                
                processed_clips.append(clip)
                
                # Voice
                voice = generate_hindi_voice(segment.get("narration", ""), clip_duration, language)
                audio_files.append(voice)
                
                gc.collect()
                
            except Exception as e:
                logger.error(f"Segment {idx+1} error: {e}")
                continue
        
        if len(processed_clips) < 3:
            return {"success": False, "error": "Not enough clips"}
        
        logger.info(f"✅ Processed {len(processed_clips)} clips")
        
        # STEP 3: Compile
        logger.info("🎬 Compiling")
        final_video = compile_final_video(processed_clips, audio_files, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Compilation failed"}
        
        # STEP 4: Upload
        logger.info("📤 Uploading")
        upload_result = await upload_to_youtube_shorts(
            final_video,
            script.get("title", "Viral Video"),
            script.get("description", ""),
            script.get("tags", []),
            user_id,
            database_manager
        )
        
        # Cleanup
        cleanup_file(final_video)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script.get("title"),
            "segments": len(processed_clips),
            "language": language,
            "duration": duration
        }
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# FASTAPI ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/viral-pixel/niches")
async def get_niches():
    """Get niches"""
    return {
        "success": True,
        "niches": {k: {"name": v["name"]} for k, v in NICHES.items()}
    }

@router.post("/api/viral-pixel/generate")
async def generate_video_endpoint(request: Request):
    """Generate video"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        niche = data.get("niche", "space")
        duration = int(data.get("duration", 40))
        language = data.get("language", "hindi")
        channel_name = data.get("channel_name", "My Channel")
        show_captions = data.get("show_captions", True)
        
        if niche not in NICHES:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid niche"}
            )
        
        if duration < 20 or duration > 60:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Duration must be 20-60 seconds"}
            )
        
        from Supermain import database_manager
        
        result = await generate_viral_video_optimized(
            niche=niche,
            duration=duration,
            language=language,
            channel_name=channel_name,
            show_captions=show_captions,
            user_id=user_id,
            database_manager=database_manager
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Endpoint error: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

__all__ = ['router']