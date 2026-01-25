
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
Viral_pixel.py - PIXABAY HD VIRAL VIDEO GENERATOR
✅ Pixabay API (HD videos + sound effects)
✅ Hindi/English voice with human-like narration
✅ Creative storytelling with hooks
✅ HD quality (720p/1080p) with memory optimization
✅ Animated transitions between clips
✅ Sound effects + background music
✅ Custom intro/outro with channel branding
✅ 2-3 second clips for engagement
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import uuid
import httpx
import json
import re
import random
import subprocess
from typing import List, Dict
import tempfile
import shutil
import gc

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

SEGMENT_COUNT = 10  # More clips, shorter duration each
CLIP_DURATION = 3  # 2-3 seconds per clip
MAX_VIDEO_SIZE_MB = 20

# Niches with creative hooks
NICHES = {
    "space": {
        "name": "Space & Universe",
        "search_terms": ["galaxy", "nebula", "planet", "star", "astronaut", "cosmos"],
        "sound_effects": ["space atmosphere", "cosmic sounds", "sci-fi"],
        "hook_style": "mysterious_discovery"
    },
    "tech_ai": {
        "name": "Technology & AI",
        "search_terms": ["artificial intelligence", "robot", "technology", "futuristic", "digital"],
        "sound_effects": ["technology", "futuristic", "digital"],
        "hook_style": "mind_blowing"
    },
    "ocean": {
        "name": "Ocean & Marine",
        "search_terms": ["ocean", "underwater", "coral", "dolphin", "whale"],
        "sound_effects": ["ocean", "underwater", "waves"],
        "hook_style": "nature_wonder"
    },
    "nature": {
        "name": "Nature & Wildlife",
        "search_terms": ["lion", "eagle", "forest", "mountain", "wildlife"],
        "sound_effects": ["nature", "forest", "wildlife"],
        "hook_style": "survival"
    },
    "success": {
        "name": "Success & Motivation",
        "search_terms": ["success", "business", "workout", "meditation", "motivation"],
        "sound_effects": ["inspirational", "motivational", "uplifting"],
        "hook_style": "inspirational"
    }
}

# Hindi/English voice mapping
VOICE_LANGUAGES = {
    "hindi": {"lang": "hi", "name": "Hindi"},
    "english_us": {"lang": "en", "name": "English (US)"},
    "english_uk": {"lang": "en-uk", "name": "English (UK)"},
    "english_in": {"lang": "en-in", "name": "English (India)"}
}

# ============================================================================
# AI SCRIPT GENERATION (CREATIVE STORYTELLING)
# ============================================================================

async def generate_creative_script(niche: str, language: str, duration: int) -> dict:
    """Generate creative, human-like script with hooks"""
    try:
        niche_info = NICHES.get(niche, NICHES["space"])
        
        prompt = f"""
You are a viral YouTube Shorts scriptwriter. Create an ENGAGING {duration}-second video script.

NICHE: {niche_info['name']}
LANGUAGE: {language}
STYLE: Human narrator explaining fascinating facts (like Veritasium, Vsauce)

REQUIREMENTS:
1. START WITH A HOOK (first 2 seconds must grab attention)
   - Use question, shocking statement, or "Did you know?"
   - Example: "What if I told you this galaxy is older than time itself?"

2. Create {SEGMENT_COUNT} segments (3 seconds each):
   - Each segment tells ONE fascinating fact
   - Use conversational, human language (not robotic AI)
   - Build suspense and curiosity
   - End with a cliffhanger or call-to-action

3. Each segment needs:
   - narration: Natural human speech (15-20 words, conversational)
   - text_overlay: 2-3 WORDS in {language} (catchy, dramatic)
   - video_search: 1-2 keywords from {niche_info['search_terms']}
   - sound_effect: Keyword from {niche_info['sound_effects']}
   - transition: fade/slide/zoom

OUTPUT ONLY VALID JSON:
{{
  "title": "SEO-optimized title with keywords #Shorts",
  "description": "Detailed description with keywords",
  "tags": ["viral", "shorts", "{niche}"],
  "segments": [
    {{
      "narration": "Human-like conversational narration here",
      "text_overlay": "CATCHY TEXT",
      "video_search": "space galaxy",
      "sound_effect": "cosmic sounds",
      "transition": "fade"
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
                        headers={
                            "Authorization": f"Bearer {MISTRAL_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {"role": "system", "content": "You are a viral content expert. Output ONLY valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 2000
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                        script = json.loads(ai_response)
                        script["segments"] = script["segments"][:SEGMENT_COUNT]
                        logger.info("✅ Creative script via Mistral")
                        return script
            except Exception as e:
                logger.warning(f"Mistral failed: {e}")
        
        # Fallback template
        return generate_fallback_script(niche, language)
        
    except Exception as e:
        logger.error(f"Script error: {e}")
        return generate_fallback_script(niche, language)


def generate_fallback_script(niche: str, language: str) -> dict:
    """Creative fallback script"""
    niche_info = NICHES.get(niche, NICHES["space"])
    
    hooks = [
        "Kya aapko pata hai?",  # Hindi
        "Did you know?",
        "Yeh vishwas nahi hoga!",
        "This will blow your mind!"
    ]
    
    segments = []
    for i in range(SEGMENT_COUNT):
        segments.append({
            "narration": f"{random.choice(hooks)} Yeh {niche} ke baare mein ek adbhut rahasya hai jo aapko hairaan kar dega!",
            "text_overlay": f"FACT #{i+1}",
            "video_search": random.choice(niche_info["search_terms"]),
            "sound_effect": random.choice(niche_info["sound_effects"]),
            "transition": random.choice(["fade", "slide", "zoom"])
        })
    
    return {
        "title": f"Amazing {niche_info['name']} Facts You Never Knew! #Shorts",
        "description": f"Discover mind-blowing {niche} facts!",
        "tags": [niche, "facts", "viral", "shorts"],
        "segments": segments
    }


# ============================================================================
# PIXABAY API (HD VIDEOS + SOUND EFFECTS)
# ============================================================================

async def search_pixabay_videos(query: str, hd_quality: bool = True) -> List[dict]:
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
                logger.info(f"✅ Pixabay: {len(videos)} videos for '{query}'")
                return videos
            else:
                logger.error(f"Pixabay error: {response.status_code}")
                return []
                
    except Exception as e:
        logger.error(f"Pixabay search failed: {e}")
        return []


async def search_pixabay_sound_effects(query: str) -> str:
    """Search Pixabay for sound effects"""
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://pixabay.com/api/",  # Audio endpoint
                params={
                    "key": PIXABAY_API_KEY,
                    "q": query,
                    "audio_type": "sound_effect",
                    "per_page": 3
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                sounds = data.get("hits", [])
                if sounds:
                    # Return first sound effect URL
                    return sounds[0].get("previewURL", "")
                
    except Exception as e:
        logger.warning(f"Sound effect search failed: {e}")
    
    return None


async def download_video_hd(video_data: dict, output_path: str, hd_quality: bool) -> bool:
    """Download HD video from Pixabay"""
    try:
        # Get best quality available
        videos = video_data.get("videos", {})
        
        if hd_quality:
            # Try HD first, fallback to medium
            video_url = (videos.get("large", {}).get("url") or 
                        videos.get("medium", {}).get("url") or 
                        videos.get("small", {}).get("url"))
        else:
            # Medium quality for memory efficiency
            video_url = (videos.get("medium", {}).get("url") or 
                        videos.get("small", {}).get("url"))
        
        if not video_url:
            return False
        
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream('GET', video_url) as response:
                if response.status_code != 200:
                    return False
                
                # Check size
                content_length = response.headers.get('content-length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > MAX_VIDEO_SIZE_MB:
                        logger.warning(f"⚠️ Video too large ({size_mb:.1f}MB)")
                        return False
                
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"✅ Downloaded HD video: {os.path.getsize(output_path)/(1024*1024):.1f}MB")
                return True
                
    except Exception as e:
        logger.error(f"HD download error: {e}")
        return False


# ============================================================================
# VIDEO PROCESSING (HD + ANIMATIONS)
# ============================================================================

def extract_best_clip_hd(video_path: str, duration: int = CLIP_DURATION) -> str:
    """Extract best 2-3 second clip from video"""
    try:
        output_path = video_path.replace(".mp4", "_clip.mp4")
        
        # Get middle section (usually most interesting)
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", "2",  # Skip first 2 seconds
            "-t", str(duration),
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-crf", "23",  # Better quality than 28
            "-preset", "fast",
            "-an",
            output_path,
            "-y"
        ]
        
        subprocess.run(cmd, capture_output=True, timeout=25)
        
        if os.path.exists(output_path):
            logger.info(f"✅ Extracted {duration}s clip")
            os.remove(video_path)
            return output_path
        
        return video_path
            
    except Exception as e:
        logger.error(f"Extract error: {e}")
        return video_path


def add_transition_animation(video_path: str, transition_type: str) -> str:
    """Add smooth transitions"""
    try:
        output_path = video_path.replace(".mp4", "_trans.mp4")
        
        # Add fade or slide effect
        if transition_type == "fade":
            vf = "fade=in:0:15,fade=out:st=2.7:d=0.3"
        elif transition_type == "zoom":
            vf = "zoompan=z='min(zoom+0.002,1.1)':d=75:s=720x1280"
        else:  # slide
            vf = "fade=in:0:15,fade=out:st=2.7:d=0.3"
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            output_path,
            "-y"
        ]
        
        subprocess.run(cmd, capture_output=True, timeout=15)
        
        if os.path.exists(output_path):
            os.remove(video_path)
            return output_path
        
        return video_path
            
    except Exception as e:
        logger.error(f"Transition error: {e}")
        return video_path


def add_hindi_caption(video_path: str, text: str, show_captions: bool) -> str:
    """Add Hindi/English captions with golden style"""
    if not show_captions:
        return video_path
    
    try:
        output_path = video_path.replace(".mp4", "_caption.mp4")
        
        # Escape text for FFmpeg
        text_escaped = text.replace("'", "'\\''").replace(":", "\\:")
        
        # Golden yellow captions with shadow
        drawtext = (
            f"drawtext=text='{text_escaped}':"
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            "fontsize=55:"
            "fontcolor=#FFD700:"  # Golden
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
        
        subprocess.run(cmd, capture_output=True, timeout=15)
        
        if os.path.exists(output_path):
            os.remove(video_path)
            return output_path
        
        return video_path
            
    except Exception as e:
        logger.error(f"Caption error: {e}")
        return video_path


# ============================================================================
# HINDI VOICE GENERATION
# ============================================================================

def generate_hindi_voice(text: str, language: str, duration: float) -> str:
    """Generate Hindi/English voice"""
    try:
        from gtts import gTTS
        
        lang_code = VOICE_LANGUAGES.get(language, {}).get("lang", "hi")
        
        temp_file = f"/tmp/voice_{uuid.uuid4().hex[:8]}.mp3"
        
        # Generate TTS
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(temp_file)
        
        logger.info(f"✅ Generated {language} voice")
        return temp_file
        
    except Exception as e:
        logger.error(f"Voice error: {e}")
        # Return silent audio
        return create_silent_audio(duration)


def create_silent_audio(duration: float) -> str:
    """Silent fallback"""
    try:
        output = f"/tmp/silent_{uuid.uuid4().hex[:8]}.mp3"
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=mono:d={duration}",
            "-acodec", "libmp3lame",
            "-ab", "64k",
            output,
            "-y"
        ]
        subprocess.run(cmd, capture_output=True, timeout=10)
        return output
    except:
        return None


# ============================================================================
# INTRO/OUTRO WITH BRANDING
# ============================================================================

def create_intro_outro(channel_name: str, temp_dir: str) -> tuple:
    """Create intro and outro clips"""
    try:
        intro_path = os.path.join(temp_dir, "intro.mp4")
        outro_path = os.path.join(temp_dir, "outro.mp4")
        
        # Intro: 1.5 seconds
        intro_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "color=c=black:s=720x1280:d=1.5",
            "-vf", 
            f"drawtext=text='{channel_name}':"
            "fontsize=70:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-100,"
            "drawtext=text='🔔 SUBSCRIBE':"
            "fontsize=40:fontcolor=#FFD700:x=(w-text_w)/2:y=(h-text_h)/2+50",
            "-c:v", "libx264",
            "-t", "1.5",
            intro_path,
            "-y"
        ]
        
        # Outro: 1.5 seconds
        outro_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "color=c=black:s=720x1280:d=1.5",
            "-vf",
            "drawtext=text='👍 LIKE':"
            "fontsize=45:fontcolor=#FFD700:x=(w-text_w)/2:y=(h-text_h)/2-80,"
            "drawtext=text='💬 COMMENT':"
            "fontsize=45:fontcolor=#FFD700:x=(w-text_w)/2:y=(h-text_h)/2,"
            "drawtext=text='🔔 SUBSCRIBE':"
            "fontsize=45:fontcolor=#FFD700:x=(w-text_w)/2:y=(h-text_h)/2+80",
            "-c:v", "libx264",
            "-t", "1.5",
            outro_path,
            "-y"
        ]
        
        subprocess.run(intro_cmd, capture_output=True, timeout=10)
        subprocess.run(outro_cmd, capture_output=True, timeout=10)
        
        return intro_path, outro_path
        
    except Exception as e:
        logger.error(f"Intro/outro error: {e}")
        return None, None


# ============================================================================
# FINAL COMPILATION
# ============================================================================

def compile_final_video(clips: List[str], audio_files: List[str], bg_music: str, intro: str, outro: str) -> str:
    """Compile everything into final video"""
    try:
        # Add intro and outro to clips
        all_clips = []
        if intro and os.path.exists(intro):
            all_clips.append(intro)
        all_clips.extend(clips)
        if outro and os.path.exists(outro):
            all_clips.append(outro)
        
        # Create concat file
        concat_file = f"/tmp/concat_{uuid.uuid4().hex[:8]}.txt"
        with open(concat_file, 'w') as f:
            for clip in all_clips:
                f.write(f"file '{clip}'\n")
        
        temp_video = f"/tmp/video_{uuid.uuid4().hex[:8]}.mp4"
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            temp_video,
            "-y"
        ]
        subprocess.run(cmd, capture_output=True, timeout=60)
        
        # Concat audio
        audio_concat = f"/tmp/audio_concat_{uuid.uuid4().hex[:8]}.txt"
        with open(audio_concat, 'w') as f:
            for audio in audio_files:
                if audio and os.path.exists(audio):
                    f.write(f"file '{audio}'\n")
        
        combined_audio = f"/tmp/audio_{uuid.uuid4().hex[:8]}.mp3"
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", audio_concat,
            "-c", "copy",
            combined_audio,
            "-y"
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)
        
        # Final mix with background music
        final_output = f"/tmp/final_{uuid.uuid4().hex[:8]}.mp4"
        
        if bg_music and os.path.exists(bg_music):
            cmd = [
                "ffmpeg",
                "-i", temp_video,
                "-i", combined_audio,
                "-i", bg_music,
                "-filter_complex",
                "[1:a]volume=1.0[v1];[2:a]volume=0.35[v2];[v1][v2]amix=inputs=2:duration=shortest[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                final_output,
                "-y"
            ]
        else:
            cmd = [
                "ffmpeg",
                "-i", temp_video,
                "-i", combined_audio,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                final_output,
                "-y"
            ]
        
        subprocess.run(cmd, capture_output=True, timeout=60)
        
        # Cleanup
        for clip in all_clips:
            try:
                os.remove(clip)
            except:
                pass
        for audio in audio_files:
            try:
                os.remove(audio)
            except:
                pass
        
        os.remove(temp_video)
        os.remove(combined_audio)
        os.remove(concat_file)
        os.remove(audio_concat)
        
        if os.path.exists(final_output):
            logger.info(f"✅ Final: {os.path.getsize(final_output)/(1024*1024):.1f}MB")
            return final_output
        
        return None
            
    except Exception as e:
        logger.error(f"Compile error: {e}")
        return None


# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, tags: List[str], 
                           user_id: str, database_manager) -> dict:
    """Upload to YouTube"""
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db or not yt_db.youtube.client:
            return {"success": False, "error": "YouTube not available"}
        
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        
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
            return {
                "success": True,
                "video_id": upload_result.get("video_id"),
                "video_url": f"https://youtube.com/shorts/{upload_result.get('video_id')}"
            }
        
        return {"success": False, "error": upload_result.get("error", "Upload failed")}
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# MAIN GENERATION
# ============================================================================

async def generate_viral_video(
    niche: str,
    language: str,
    hd_quality: bool,
    show_captions: bool,
    channel_name: str,
    user_id: str,
    database_manager
) -> dict:
    """Generate complete viral video"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_")
        logger.info(f"🎬 Starting Pixabay HD generation")
        
        # STEP 1: Creative script
        logger.info("📝 Creative AI script")
        script = await generate_creative_script(niche, language, 30)
        
        logger.info(f"✅ Script: {len(script['segments'])} segments")
        
        # STEP 2: Download videos + sound effects
        logger.info("📥 Pixabay HD videos")
        
        processed_clips = []
        audio_files = []
        
        for idx, segment in enumerate(script["segments"]):
            try:
                logger.info(f"Segment {idx+1}/{len(script['segments'])}")
                
                # Search Pixabay
                videos = await search_pixabay_videos(segment["video_search"], hd_quality)
                if not videos:
                    continue
                
                # Download best video
                video_path = os.path.join(temp_dir, f"v{idx}.mp4")
                success = await download_video_hd(videos[0], video_path, hd_quality)
                
                if not success:
                    continue
                
                # Extract 2-3 sec clip
                clip = extract_best_clip_hd(video_path, CLIP_DURATION)
                
                # Add transition
                trans_clip = add_transition_animation(clip, segment.get("transition", "fade"))
                
                # Add caption
                final_clip = add_hindi_caption(trans_clip, segment.get("text_overlay", ""), show_captions)
                
                processed_clips.append(final_clip)
                
                # Voice
                voice = generate_hindi_voice(segment.get("narration", ""), language, CLIP_DURATION)
                audio_files.append(voice)
                
                gc.collect()
                
            except Exception as e:
                logger.error(f"Segment {idx+1} error: {e}")
                continue
        
        if len(processed_clips) < 5:
            return {"success": False, "error": "Not enough clips generated"}
        
        logger.info(f"✅ {len(processed_clips)} clips ready")
        
        # STEP 3: Intro/Outro
        logger.info("🎬 Creating intro/outro")
        intro, outro = create_intro_outro(channel_name, temp_dir)
        
        # STEP 4: Background music (search Pixabay)
        bg_music = None  # TODO: Implement Pixabay music search
        
        # STEP 5: Compile
        logger.info("🎬 Final compilation")
        final_video = compile_final_video(processed_clips, audio_files, bg_music, intro, outro)
        
        if not final_video:
            return {"success": False, "error": "Compilation failed"}
        
        # STEP 6: Upload
        logger.info("📤 Uploading to YouTube")
        upload_result = await upload_to_youtube(
            final_video,
            script.get("title"),
            script.get("description"),
            script.get("tags"),
            user_id,
            database_manager
        )
        
        # Cleanup
        os.remove(final_video)
        shutil.rmtree(temp_dir)
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script.get("title"),
            "segments": len(processed_clips)
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
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
    """Get available niches"""
    return {
        "success": True,
        "niches": NICHES,
        "languages": VOICE_LANGUAGES
    }


@router.post("/api/viral-pixel/generate")
async def generate_video(request: Request):
    """Generate viral video with Pixabay"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        niche = data.get("niche", "space")
        language = data.get("language", "hindi")
        hd_quality = data.get("hd_quality", True)
        show_captions = data.get("show_captions", True)
        channel_name = data.get("channel_name", "My Channel")
        
        if niche not in NICHES:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid niche"}
            )
        
        if language not in VOICE_LANGUAGES:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid language"}
            )
        
        from Supermain import database_manager
        
        result = await generate_viral_video(
            niche=niche,
            language=language,
            hd_quality=hd_quality,
            show_captions=show_captions,
            channel_name=channel_name,
            user_id=user_id,
            database_manager=database_manager
        )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


__all__ = ['router']