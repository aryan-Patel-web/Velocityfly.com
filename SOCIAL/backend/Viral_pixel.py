
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
Viral_pixel.py - ONE VIDEO STRATEGY
✅ Download ONE video (up to 100MB)
✅ Reuse for ALL segments (different timestamps)
✅ FULL engaging script: Hook → Story → Suspense → Outro
✅ 120-150 words per segment for natural pacing
✅ Ultra-fast processing (no re-downloads)
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

# RELAXED LIMITS - ONE VIDEO STRATEGY
MAX_VIDEO_SIZE_MB = 100  # Allow larger video (used for all segments)
MAX_AUDIO_SIZE_MB = 3
VOICE_SPEED = 1.15
MIN_VIDEOS = 1  # Only need 1 video!
MAX_VIDEOS = 1  # Only download 1 video
FFMPEG_TIMEOUT = 90

# ENGLISH KEYWORDS
NICHE_KEYWORDS = {
    "space": ["galaxy", "nebula", "planet", "cosmos", "stars", "universe", "astronomy"],
    "tech_ai": ["technology", "digital", "cyber", "future", "data", "robot", "ai"],
    "ocean": ["ocean", "wave", "underwater", "reef", "beach", "dolphin", "sea"],
    "nature": ["mountain", "forest", "lake", "sunrise", "sunset", "river", "canyon", "desert"]
}

VERTICAL_FALLBACKS = ["tower", "skyscraper", "building", "tree", "lighthouse", "rocket"]

# ============================================================================
# UTILITIES
# ============================================================================

def force_cleanup(*filepaths):
    for filepath in filepaths:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ {os.path.basename(filepath)}")
        except:
            pass
    gc.collect()

def get_file_size_mb(filepath: str) -> float:
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg_safe(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg: {result.stderr[:200]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Timeout {timeout}s")
        return False
    except Exception as e:
        logger.error(f"FFmpeg error: {e}")
        return False

# ============================================================================
# FULL ENGAGING SCRIPT WITH HOOKS & SUSPENSE
# ============================================================================

async def generate_full_script(niche: str) -> dict:
    """Generate FULL engaging script with proper structure"""
    
    niche_info = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    
    prompt = f"""Create a VIRAL 30-second Hindi YouTube Shorts script about {niche}.

STRUCTURE (MUST FOLLOW):
1. HOOK (8 seconds, 120-130 words):
   - Start with curiosity: "Kya aap jaante hain..."
   - Create mystery or shock
   - Use "CAPITAL" words for emphasis
   - End with cliffhanger

2. MAIN STORY (12 seconds, 180-200 words):
   - Tell 2-3 amazing facts
   - Use emotional language
   - Build tension with "lekin...", "par..."
   - Scientific backing: "Scientists kehte hain..."

3. SUSPENSE/TWIST (7 seconds, 120-130 words):
   - Reveal shocking truth: "Lekin sabse badi baat..."
   - Challenge common belief
   - Create urgency

4. OUTRO (3 seconds, 50-60 words):
   - Engaging question
   - Call to action: "Comment mein batao"

REQUIREMENTS:
- Use "..." for dramatic pauses
- CAPITALS for 3-4 key words per segment
- Single ENGLISH word for video_search (like: "galaxy", "ocean", "mountain")
- Emojis in text_overlay

OUTPUT JSON:
{{
  "title": "Mind-Blowing {niche.title()} Secret #Shorts 🔥",
  "description": "This will shock you! #{niche} #viral #shorts #hindi #facts",
  "tags": ["{niche}", "viral", "shorts", "hindi", "facts", "amazing"],
  "segments": [
    {{
      "type": "hook",
      "narration": "Kya aap jaante hain... UNIVERSE mein ek aisi jagah hai... jahan TIME bilkul ruk jaata hai... aur koi bhi wapas nahi aa sakta. Scientists isko BLACK HOLE kehte hain... lekin yeh sirf space mein nahi... yeh humare paas bhi ho sakta hai...",
      "text_overlay": "😱 क्या आप जानते हैं?",
      "video_search": "galaxy",
      "duration": 8
    }},
    {{
      "type": "story",
      "narration": "Jab koi STAR marta hai... toh woh itna compress ho jaata hai ki uski gravity INFINITE ho jaati hai. Light bhi escape nahi kar sakti... time slow ho jaata hai... aur agar aap 1 second black hole ke paas bitaao... toh Earth par 100 SAAL beet jaate hain. Scientists kehte hain... agar aap isme gire... toh aapka body spaghetti jaise stretch ho jaayega...",
      "text_overlay": "🔥 सच्चाई",
      "video_search": "nebula",
      "duration": 12
    }},
    {{
      "type": "suspense",
      "narration": "Lekin sabse SCARY baat... hamare Milky Way ke center mein... ek SUPERMASSIVE black hole hai... jiska naam Sagittarius A* hai. Yeh 4 million suns se zyada bhaari hai... aur ek din... yeh humein nigal sakta hai...",
      "text_overlay": "💡 खतरा",
      "video_search": "cosmos",
      "duration": 7
    }},
    {{
      "type": "outro",
      "narration": "Toh batao... kya aap black hole mein jaana chahoge? Comment mein apni soch share karo!",
      "text_overlay": "🤔 आपकी राय?",
      "video_search": "stars",
      "duration": 3
    }}
  ]
}}

IMPORTANT: Use ONLY single ENGLISH words for video_search!"""
    
    try:
        if MISTRAL_API_KEY:
            async with httpx.AsyncClient(timeout=40) as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "You are a viral YouTube Shorts scriptwriter. Create engaging Hindi scripts with proper hooks, suspense, and emotional storytelling. Output ONLY valid JSON. Use single ENGLISH words for video_search."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.95,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    script = json.loads(content)
                    
                    # Ensure English keywords
                    for seg in script['segments']:
                        words = seg['video_search'].split()
                        seg['video_search'] = words[0] if words[0].isascii() else random.choice(niche_info)
                    
                    logger.info(f"✅ Full script: {len(script['segments'])} segments")
                    return script
    except Exception as e:
        logger.warning(f"Mistral failed: {e}")
    
    return get_fallback_full_script(niche, niche_info)

def get_fallback_full_script(niche: str, keywords: list) -> dict:
    """Detailed fallback script with full structure"""
    
    # Niche-specific scripts
    if niche == "space":
        return {
            "title": "Black Hole का रहस्य जो आपको हिला देगा! 🌌 #Shorts",
            "description": "Mind-blowing space facts! #space #blackhole #universe #viral #shorts #hindi #science",
            "tags": ["space", "blackhole", "universe", "viral", "shorts", "hindi"],
            "segments": [
                {
                    "type": "hook",
                    "narration": "Kya aap jaante hain... UNIVERSE mein ek aisi jagah hai... jahan TIME bilkul ruk jaata hai... aur koi bhi cheez wapas nahi aa sakti. Scientists isko BLACK HOLE kehte hain... lekin yeh sirf space mein nahi... yeh humare galaxy ke center mein bhi hai...",
                    "text_overlay": "😱 ब्लैक होल",
                    "video_search": keywords[0],
                    "duration": 8
                },
                {
                    "type": "story",
                    "narration": "Jab ek MASSIVE star marta hai... toh woh itna collapse ho jaata hai ki uski gravity INFINITE ho jaati hai. Light bhi escape nahi kar sakti isme se... time slow motion mein chalta hai... aur agar aap paas jaao... toh ek second aapka... Earth par 100 SAAL ke barabar ho jaata hai. Scientists kehte hain... agar aap isme gire... toh aapka body spaghetti jaise STRETCH ho jaayega... isko spaghettification kehte hain...",
                    "text_overlay": "🔥 समय रुक जाता है",
                    "video_search": keywords[1] if len(keywords) > 1 else keywords[0],
                    "duration": 12
                },
                {
                    "type": "suspense",
                    "narration": "Lekin sabse SCARY baat yeh hai... hamare Milky Way galaxy ke bilkul center mein... ek SUPERMASSIVE black hole hai... jiska naam Sagittarius A Star hai. Yeh 4 MILLION suns se bhi zyada bhaari hai... aur yeh constantly hamari taraf aa raha hai...",
                    "text_overlay": "💡 खतरे की घंटी",
                    "video_search": keywords[2] if len(keywords) > 2 else keywords[0],
                    "duration": 7
                },
                {
                    "type": "outro",
                    "narration": "Toh batao... kya tum black hole mein jaane ki himmat karoge? Comment mein apni soch batao!",
                    "text_overlay": "🤔 आप क्या सोचते हैं?",
                    "video_search": keywords[0],
                    "duration": 3
                }
            ]
        }
    
    elif niche == "nature":
        return {
            "title": "प्रकृति का सबसे बड़ा रहस्य! 🌿 #Shorts",
            "description": "Nature's biggest secret revealed! #nature #mystery #viral #shorts #hindi #amazing",
            "tags": ["nature", "mystery", "viral", "shorts", "hindi", "amazing"],
            "segments": [
                {
                    "type": "hook",
                    "narration": "Kya aap jaante hain... duniya mein ek aisi JAGAH hai... jahan gravity ULTI kaam karti hai... pani neeche se UPAR badhta hai... aur patthar hawa mein FLOAT karte hain. Scientists isko magnetic hill kehte hain... lekin sach kuch aur hai...",
                    "text_overlay": "😱 गुरुत्वाकर्षण उल्टा",
                    "video_search": keywords[0],
                    "duration": 8
                },
                {
                    "type": "story",
                    "narration": "India ke Ladakh mein... ek aisi road hai jahan car apne aap UPHILL chali jaati hai... bina accelerator dabaye. Local log kehte hain yeh MAGIC hai... lekin scientists ka kehna hai... yeh optical illusion hai jahan road downhill lag rahi hoti hai... par actually UPHILL hoti hai. Lekin phir bhi... pani bhi ulta behta hai... trees bhi tilted hain... aur compass bhi GHOOM jaata hai...",
                    "text_overlay": "🔥 कार अपने आप चलती है",
                    "video_search": keywords[1] if len(keywords) > 1 else keywords[0],
                    "duration": 12
                },
                {
                    "type": "suspense",
                    "narration": "Lekin sabse BADI baat... NASA ke scientists ne pata lagaya... ki yeh jagah electromagnetic radiation se bhara hua hai... aur underground ek MASSIVE magnetic deposit hai... jo gravity ko affect kar raha hai. Kuch kehte hain... yahan aliens ka connection hai...",
                    "text_overlay": "💡 नासा का खुलासा",
                    "video_search": keywords[2] if len(keywords) > 2 else keywords[0],
                    "duration": 7
                },
                {
                    "type": "outro",
                    "narration": "Toh batao... kya tum yahan jaana chahoge? Comment mein batao!",
                    "text_overlay": "🤔 आपकी राय?",
                    "video_search": keywords[0],
                    "duration": 3
                }
            ]
        }
    
    elif niche == "ocean":
        return {
            "title": "समुद्र की सबसे खतरनाक जगह! 🌊 #Shorts",
            "description": "Ocean's deadliest secret! #ocean #mystery #viral #shorts #hindi #scary",
            "tags": ["ocean", "mystery", "viral", "shorts", "hindi", "scary"],
            "segments": [
                {
                    "type": "hook",
                    "narration": "Kya aap jaante hain... ocean ki depth mein... ek aisi DARK jagah hai... jahan koi light nahi pahunchti... temperature FREEZING hai... aur pressure itna hai ki aapka body instantly CRUSH ho jaayega. Scientists isko Mariana Trench kehte hain... lekin yahan kuch aur bhi hai...",
                    "text_overlay": "😱 सबसे गहरी जगह",
                    "video_search": keywords[0],
                    "duration": 8
                },
                {
                    "type": "story",
                    "narration": "Yeh jagah Mount Everest se bhi ZYADA deep hai... 11 KILOMETER neeche... jahan sunlight kabhi nahi pahunchti. James Cameron yahan gaye the submarine mein... aur unhone bataya... yahan bilkul ALIEN world jaisa hai. Strange creatures hain... jo khud GLOW karte hain... kuch ke 100 teeth hain... aur kuch itne bade hain ki unka sirf head aapke room se bhi BADA hai...",
                    "text_overlay": "🔥 11 किमी गहरा",
                    "video_search": keywords[1] if len(keywords) > 1 else keywords[0],
                    "duration": 12
                },
                {
                    "type": "suspense",
                    "narration": "Lekin sabse SCARY baat... scientists ne yahan... microphones lagaye... aur unhone suni... ek ajeeb si AWAAZ... jisko Bloop kehte hain. Yeh kisi bhi known creature se nahi match karti... matlab yahan kuch UNKNOWN hai... jo hum abhi tak nahi jaante...",
                    "text_overlay": "💡 अनजान जीव",
                    "video_search": keywords[2] if len(keywords) > 2 else keywords[0],
                    "duration": 7
                },
                {
                    "type": "outro",
                    "narration": "Toh batao... kya tum yahan jaane ki himmat karoge? Comment mein batao!",
                    "text_overlay": "🤔 हिम्मत है?",
                    "video_search": keywords[0],
                    "duration": 3
                }
            ]
        }
    
    # Default fallback
    return {
        "title": f"SHOCKING {niche.title()} Secret #Shorts 🔥",
        "description": f"Mind-blowing {niche} facts! #{niche} #viral #shorts #hindi",
        "tags": [niche, "viral", "shorts", "hindi", "facts"],
        "segments": [
            {
                "type": "hook",
                "narration": f"Kya aap jaante hain... {niche} ke baare mein yeh SHOCKING fact... jo aapko hila dega!",
                "text_overlay": "😱 सुनो",
                "video_search": keywords[0],
                "duration": 8
            },
            {
                "type": "story",
                "narration": f"Scientists kehte hain... yeh bilkul IMPOSSIBLE hai... lekin sach yeh hai ki... nature ke paas apne SECRET hain!",
                "text_overlay": "🔥 तथ्य",
                "video_search": keywords[1] if len(keywords) > 1 else keywords[0],
                "duration": 12
            },
            {
                "type": "suspense",
                "narration": "Lekin sabse BADI baat... jo aap nahi jaante... woh yeh hai ki...",
                "text_overlay": "💡 रहस्य",
                "video_search": keywords[2] if len(keywords) > 2 else keywords[0],
                "duration": 7
            },
            {
                "type": "outro",
                "narration": "Toh batao... kya aap vishwas karte hain? Comment mein batao!",
                "text_overlay": "🤔 सवाल",
                "video_search": keywords[0],
                "duration": 3
            }
        ]
    }

# ============================================================================
# VOICE
# ============================================================================

async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Edge TTS"""
    try:
        import edge_tts
        
        temp = os.path.join(temp_dir, f"v{uuid.uuid4().hex[:4]}.mp3")
        text_clean = text.replace("...", " ").strip()
        
        # Don't truncate - use full narration
        if len(text_clean) > 500:
            text_clean = text_clean[:500]
        
        communicate = edge_tts.Communicate(text_clean, "hi-IN-MadhurNeural", rate="+20%")
        await communicate.save(temp)
        
        output = temp.replace(".mp3", "_f.mp3")
        cmd = [
            "ffmpeg", "-i", temp,
            "-ar", "44100",
            "-b:a", "128k",
            "-t", str(duration + 1),
            "-y", output
        ]
        
        if run_ffmpeg_safe(cmd, 25):
            force_cleanup(temp)
            if get_file_size_mb(output) <= MAX_AUDIO_SIZE_MB:
                logger.info(f"✅ Voice: {get_file_size_mb(output):.2f}MB")
                return output
        
        force_cleanup(temp, output)
    except Exception as e:
        logger.error(f"Voice error: {e}")
    
    return None

# ============================================================================
# VIDEO - ONE VIDEO STRATEGY
# ============================================================================

def is_vertical_video(video_data: dict) -> bool:
    try:
        videos = video_data.get("videos", {})
        for size_name in ["tiny", "small", "medium", "large"]:
            size_data = videos.get(size_name, {})
            width = size_data.get("width", 0)
            height = size_data.get("height", 0)
            if width > 0 and height > 0 and (height / width) >= 1.5:
                return True
        return False
    except:
        return False

async def search_one_good_video(query: str) -> Optional[dict]:
    """Search for ONE good vertical video"""
    try:
        search_word = query.split()[0].lower()
        if not search_word.isascii():
            search_word = random.choice(VERTICAL_FALLBACKS)
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": search_word,
                    "per_page": 50,
                    "video_type": "film",
                    "order": "popular"
                }
            )
            
            if response.status_code == 200:
                videos = response.json().get("hits", [])
                vertical = [v for v in videos if is_vertical_video(v)]
                
                if vertical:
                    logger.info(f"✅ Found {len(vertical)} vertical videos for '{search_word}'")
                    return vertical[0]  # Return FIRST good video
            
            # Try fallbacks
            for fallback in VERTICAL_FALLBACKS:
                response = await client.get(
                    "https://pixabay.com/api/videos/",
                    params={
                        "key": PIXABAY_API_KEY,
                        "q": fallback,
                        "per_page": 30
                    }
                )
                
                if response.status_code == 200:
                    videos = response.json().get("hits", [])
                    vertical = [v for v in videos if is_vertical_video(v)]
                    
                    if vertical:
                        logger.info(f"✅ Fallback '{fallback}'")
                        return vertical[0]
        
        return None
    except Exception as e:
        logger.error(f"Search error: {e}")
        return None

async def download_one_video(video_data: dict, output: str) -> bool:
    """Download ONE video (up to 100MB)"""
    try:
        videos = video_data.get("videos", {})
        
        # Try to get best quality vertical video
        url = None
        for size in ["medium", "small", "large", "tiny"]:
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
                        
                        # Check if exceeding 100MB
                        if downloaded > MAX_VIDEO_SIZE_MB * 1024 * 1024:
                            logger.warning(f"Video exceeding {MAX_VIDEO_SIZE_MB}MB, stopping")
                            return False
                
                size = get_file_size_mb(output)
                if size < 0.5:  # Too small
                    force_cleanup(output)
                    return False
                
                logger.info(f"✅ Downloaded ONE video: {size:.1f}MB")
                return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        force_cleanup(output)
        return False

# ============================================================================
# PROCESS SEGMENTS FROM ONE VIDEO
# ============================================================================

def extract_segment_from_video(
    source_video: str,
    start_time: float,
    duration: float,
    text: str,
    temp_dir: str
) -> Optional[str]:
    """Extract segment from ONE source video at different timestamps"""
    
    try:
        output = os.path.join(temp_dir, f"seg_{uuid.uuid4().hex[:4]}.mp4")
        
        # Build filter
        filters = ["scale=720:1280:force_original_aspect_ratio=increase", "crop=720:1280"]
        
        if text:
            text_clean = text.replace("'", "").replace('"', '').replace(':', '')[:30]
            filters.append(
                f"drawtext=text='{text_clean}':fontsize=60:fontcolor=white:"
                f"x=(w-text_w)/2:y=h-160:borderw=4:bordercolor=black"
            )
        
        vf = ",".join(filters)
        
        # Extract from specific timestamp
        cmd = [
            "ffmpeg", "-i", source_video,
            "-ss", str(start_time),
            "-t", str(duration),
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "ultrafast",
            "-an",
            "-y", output
        ]
        
        logger.info(f"⚙️ Extracting from {start_time}s (duration: {duration}s)")
        
        if run_ffmpeg_safe(cmd, FFMPEG_TIMEOUT):
            size = get_file_size_mb(output)
            logger.info(f"✅ Segment: {size:.1f}MB")
            return output
        
        force_cleanup(output)
        return None
        
    except Exception as e:
        logger.error(f"Extract error: {e}")
        return None

# ============================================================================
# COMPILATION
# ============================================================================

async def compile_video(clips: List[str], audios: List[str], temp_dir: str) -> Optional[str]:
    try:
        # Concat videos
        vlist = os.path.join(temp_dir, "v.txt")
        with open(vlist, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        vid_all = os.path.join(temp_dir, "vid.mp4")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", vlist, "-c", "copy", "-y", vid_all]
        
        if not run_ffmpeg_safe(cmd, 60):
            return None
        
        # Concat audios
        alist = os.path.join(temp_dir, "a.txt")
        with open(alist, 'w') as f:
            for audio in audios:
                f.write(f"file '{audio}'\n")
        
        aud_all = os.path.join(temp_dir, "aud.mp3")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", alist, "-c", "copy", "-y", aud_all]
        
        if not run_ffmpeg_safe(cmd, 40):
            return None
        
        # Mix
        final = os.path.join(temp_dir, "output.mp4")
        cmd = [
            "ffmpeg",
            "-i", vid_all,
            "-i", aud_all,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            "-y", final
        ]
        
        if run_ffmpeg_safe(cmd, 60):
            logger.info(f"✅ Final: {get_file_size_mb(final):.1f}MB")
            return final
        
        return None
    except Exception as e:
        logger.error(f"Compile error: {e}")
        return None

# ============================================================================
# MAIN - ONE VIDEO STRATEGY
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
    """ONE VIDEO STRATEGY - Download once, reuse for all segments"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_")
        logger.info(f"🎬 ONE VIDEO Strategy: {niche}")
        
        # Step 1: Full engaging script
        script = await generate_full_script(niche)
        logger.info(f"✅ Title: {script['title']}")
        logger.info(f"📝 Segments: {len(script['segments'])}")
        
        # Step 2: Download ONE good video
        logger.info("📥 Searching for ONE perfect video...")
        
        video_data = await search_one_good_video(script["segments"][0]["video_search"])
        
        if not video_data:
            return {"success": False, "error": "No vertical video found"}
        
        source_video = os.path.join(temp_dir, "source.mp4")
        
        if not await download_one_video(video_data, source_video):
            return {"success": False, "error": "Download failed"}
        
        logger.info(f"🎥 ONE video downloaded: {get_file_size_mb(source_video):.1f}MB")
        
        # Step 3: Extract segments from different timestamps
        final_clips = []
        final_audios = []
        
        start_time = 2.0  # Start at 2 seconds
        
        for idx, seg in enumerate(script["segments"]):
            try:
                logger.info(f"\n📹 Processing segment {idx+1}/4: {seg['type']}")
                
                # Extract from source at different timestamp
                segment_clip = extract_segment_from_video(
                    source_video,
                    start_time,
                    seg["duration"],
                    seg["text_overlay"] if show_captions else "",
                    temp_dir
                )
                
                if not segment_clip:
                    logger.warning(f"⚠️ Segment {idx+1} extraction failed")
                    # Try next timestamp
                    start_time += 5
                    continue
                
                final_clips.append(segment_clip)
                
                # Move to next timestamp
                start_time += seg["duration"] + 2
                
                # Generate voice
                logger.info("🎤 Generating voice...")
                voice = await generate_voice_edge(seg["narration"], seg["duration"], temp_dir)
                
                if voice:
                    final_audios.append(voice)
                else:
                    # Silent fallback
                    silent = os.path.join(temp_dir, f"s{idx}.mp3")
                    cmd = ["ffmpeg", "-f", "lavfi", "-i", f"anullsrc=d={seg['duration']}", "-y", silent]
                    if run_ffmpeg_safe(cmd, 15):
                        final_audios.append(silent)
                
                logger.info(f"✅ Segment {idx+1} done!")
                gc.collect()
                
            except Exception as e:
                logger.error(f"Segment {idx+1} error: {e}")
                continue
        
        # Cleanup source video
        force_cleanup(source_video)
        
        # Check success
        if len(final_clips) < 3:
            return {
                "success": False,
                "error": f"Only {len(final_clips)} segments created. Need at least 3."
            }
        
        logger.info(f"\n✅ {len(final_clips)} segments ready! Compiling...")
        
        # Step 4: Compile
        final_video = await compile_video(final_clips, final_audios, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Compilation failed"}
        
        logger.info(f"🎉 SUCCESS! {get_file_size_mb(final_video):.1f}MB")
        
        result = {
            "success": True,
            "video_path": final_video,
            "title": script["title"],
            "description": script["description"],
            "tags": script["tags"],
            "segments": len(final_clips),
            "total_duration": sum([s['duration'] for s in script["segments"]]),
            "size_mb": f"{get_file_size_mb(final_video):.1f}MB",
            "strategy": "ONE_VIDEO_REUSED"
        }
        
        gc.collect()
        return result
        
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
                    duration=int(data.get("duration", 30)),
                    language=data.get("language", "hindi"),
                    channel_name=data.get("channel_name", "My Channel"),
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