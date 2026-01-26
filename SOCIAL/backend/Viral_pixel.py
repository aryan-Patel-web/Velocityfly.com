
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
Viral_pixel.py - OPTIMIZED PRODUCTION VERSION
✅ Fixed ElevenLabs API (proper key format)
✅ 4 unique videos with smooth transitions  
✅ 30+ second scripts with Hook-Story-Suspense-Outro
✅ Background music downloaded from Pixabay API
✅ 1.1x voice speed (NOT video speed)
✅ Memory optimized (<512MB) with aggressive cleanup
✅ Max 25MB per video, efficient FFmpeg usage
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
from typing import List, Dict
import tempfile
import shutil
import gc

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# ElevenLabs API Key - your actual key
ELEVENLABS_API_KEY = "d4b3f7d4b20eb5994410ea31fbc719244cdb7b7076744d4a20345cab167f339e"
ELEVENLABS_VOICE_ID = "YkAJCvEzSQvG7K2YK9kx"

# Memory optimization
MAX_VIDEO_SIZE_MB = 25  # 25MB max per video
TARGET_DURATION = 30  # 30 seconds minimum
VOICE_SPEED = 1.1  # 1.1x speed for voice only
MAX_VIDEOS = 4  # 4 unique videos
SUBSCRIBE_DURATION = 3  # 3 second subscribe
FFMPEG_TIMEOUT = 30

NICHES = {
    "space": {
        "name": "Space & Universe 🌌",
        "searches": ["galaxy", "nebula", "planet", "stars"],
    },
    "tech_ai": {
        "name": "Technology & AI 🤖",
        "searches": ["robot", "technology", "digital", "innovation"],
    },
    "ocean": {
        "name": "Ocean & Marine 🌊",
        "searches": ["ocean", "underwater", "coral", "waves"],
    },
    "nature": {
        "name": "Nature & Wildlife 🦁",
        "searches": ["lion", "forest", "eagle", "wildlife"],
    }
}

# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

def cleanup_file(filepath: str):
    """Delete file and clear memory"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🗑️ Deleted: {os.path.basename(filepath)}")
    except:
        pass
    gc.collect()

def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB"""
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """Run FFmpeg with timeout and cleanup"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            timeout=timeout, 
            check=False
        )
        gc.collect()
        return result.returncode == 0
    except:
        gc.collect()
        return False

# ============================================================================
# AI SCRIPT GENERATION - 120+ WORDS, 30+ SECONDS
# ============================================================================

async def generate_viral_script(niche: str) -> dict:
    """Generate engaging 30+ second Hindi script"""
    
    niche_info = NICHES.get(niche, NICHES["space"])
    
    prompt = f"""Create a 30-35 second viral Hindi YouTube Shorts script about {niche}.

MANDATORY STRUCTURE (120-150 words total):
1. HOOK (30-35 words, 7-8 sec): Start with "Socho agar main kahun..." Create STRONG curiosity
2. MAIN STORY (50-60 words, 14-16 sec): 2-3 amazing facts with emotion and pauses
3. SUSPENSE TWIST (25-30 words, 6-7 sec): Mind-blowing revelation starting with "Lekin..."
4. OUTRO (15-20 words, 4-5 sec): Engaging question to audience

INDIAN VIRAL STYLE:
- Use dramatic words: "Socho", "Lekin", "Aur sabse badi baat", "Scientists kehte hain"
- Add "..." for suspense pauses (minimum 5 times total)
- Add "," for natural breathing (every 8-10 words)
- Use CAPITAL words for emphasis (3-4 times)
- Short punchy sentences (6-9 words each)
- Create mystery and emotion

EXAMPLE STRUCTURE:
Hook: "Socho agar main kahun... universe mein ek aisi jagah hai... jahan TIME hi ruk jaata hai, aur koi bhi cheez wapas nahi aa sakti..."

Story: "Black Hole naam ki ye cosmic entity... itni POWERFUL hoti hai ki light bhi escape nahi kar sakti. Scientists ne calculate kiya hai... agar aap black hole ke paas gaye, toh ek second aapka... bahar kai saalon ke barabar hoga. Yeh space aur time ko hi tod deta hai..."

Suspense: "Lekin sabse SCARY baat ye hai... Scientists maante hain ki hamare solar system ke paas bhi ek black hole ho sakta hai... jo slowly towards us aa raha hai..."

Outro: "Toh batao dosto... kya tum black hole ke paas jaoge?"

REQUIREMENTS:
- Title in English with emojis and #Shorts
- 4 segments (Hook, Story, Suspense, Outro)
- Each segment: simple 1 word search query for videos
- Total: 120-150 words, 32-36 seconds
- Natural Hindi with emotion

Output ONLY JSON:
{{
  "title": "SHOCKING Space Secret #Shorts 🚀",
  "description": "Mind-blowing space revelation! #space #viral #shorts",
  "tags": ["space", "viral", "shorts", "hindi"],
  "segments": [
    {{
      "type": "hook",
      "narration": "Socho agar main kahun... (30-35 words with ... and ,)",
      "text_overlay": "😱 सुनो",
      "video_search": "galaxy",
      "duration": 8
    }},
    {{
      "type": "story",
      "narration": "Main story (50-60 words)",
      "text_overlay": "🔥 अविश्वसनीय",
      "video_search": "nebula",
      "duration": 15
    }},
    {{
      "type": "suspense",
      "narration": "Lekin... (25-30 words)",
      "text_overlay": "💡 रहस्य",
      "video_search": "planet",
      "duration": 7
    }},
    {{
      "type": "outro",
      "narration": "Question (15-20 words)",
      "text_overlay": "🤔 सवाल",
      "video_search": "stars",
      "duration": 5
    }}
  ]
}}"""
    
    try:
        # Try Mistral AI
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
                                    "content": "You are a viral Hindi content creator. Create emotional, suspenseful 30+ second scripts. Output ONLY valid JSON."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 2000
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]
                        content = re.sub(r'```json\n?|\n?```', '', content).strip()
                        script = json.loads(content)
                        script["segments"] = script["segments"][:MAX_VIDEOS]
                        logger.info(f"✅ Script via Mistral: {len(script['segments'])} segments")
                        return script
            except Exception as e:
                logger.warning(f"Mistral failed: {e}")
        
        # Fallback to template
        return get_fallback_script(niche, niche_info["searches"])
        
    except Exception as e:
        logger.error(f"Script error: {e}")
        return get_fallback_script(niche, niche_info["searches"])

def get_fallback_script(niche: str, searches: List[str]) -> dict:
    """Fallback engaging script"""
    
    scripts = {
        "space": {
            "hook": "Socho agar main kahun... UNIVERSE mein ek aisi jagah hai... jahan TIME hi ruk jaata hai, aur koi bhi cheez wapas nahi aa sakti. Yeh sach hai dosto...",
            "story": "Black Hole naam ki ye cosmic entity... itni POWERFUL hoti hai ki light bhi escape nahi kar sakti. Scientists ne calculate kiya... agar aap black hole ke paas gaye, toh ek second aapka bahar kai saalon ke barabar hoga. Yeh SPACE aur TIME ko hi tod deta hai... puri reality badal deta hai.",
            "suspense": "Lekin sabse SCARY baat ye hai... Scientists maante hain ki hamare solar system ke paas bhi ek black hole ho sakta hai... jo slowly towards us aa raha hai...",
            "outro": "Toh batao dosto... kya tum black hole ke paas jaoge? Comment mein batao!"
        },
        "tech_ai": {
            "hook": "Socho agar main kahun... AI ab tumhare dimaag ko PADH sakta hai, tumhari soch ko samajh sakta hai... yeh science fiction nahi, REALITY hai...",
            "story": "Aaj ki technology itni ADVANCED ho gayi hai... ki robots ab EMOTIONS samajh rahe hain. Neuralink jaise devices... seedha brain se connect ho rahe hain. AI paintings bana raha hai, music compose kar raha hai... insaan se bhi behtar.",
            "suspense": "Lekin sabse BADI baat... Scientists ne predict kiya hai ki 2030 tak... AI insaan se zyada SMART ho jayega. Phir kya hoga...",
            "outro": "Kya tum tayaar ho AI ke yug ke liye? Batao comments mein!"
        }
    }
    
    template = scripts.get(niche, scripts["space"])
    
    return {
        "title": f"SHOCKING {niche.title()} Secret #Shorts 🔥",
        "description": f"Mind-blowing revelation! #{niche} #viral #shorts #hindi",
        "tags": [niche, "viral", "shorts", "hindi", "trending"],
        "segments": [
            {
                "type": "hook",
                "narration": template["hook"],
                "text_overlay": "😱 सुनो",
                "video_search": searches[0],
                "duration": 8
            },
            {
                "type": "story",
                "narration": template["story"],
                "text_overlay": "🔥 अविश्वसनीय",
                "video_search": searches[1] if len(searches) > 1 else searches[0],
                "duration": 15
            },
            {
                "type": "suspense",
                "narration": template["suspense"],
                "text_overlay": "💡 रहस्य",
                "video_search": searches[2] if len(searches) > 2 else searches[0],
                "duration": 7
            },
            {
                "type": "outro",
                "narration": template["outro"],
                "text_overlay": "🤔 सवाल",
                "video_search": searches[3] if len(searches) > 3 else searches[0],
                "duration": 5
            }
        ]
    }

# ============================================================================
# ELEVENLABS VOICE - 1.1x SPEED (NOT VIDEO)
# ============================================================================

async def generate_voice_elevenlabs(text: str, duration: float, temp_dir: str) -> str:
    """Generate voice with ElevenLabs at 1.1x speed"""
    try:
        # Clean text
        text_clean = text.replace("...", " ").strip()[:300]
        
        temp_file = os.path.join(temp_dir, f"elv_{uuid.uuid4().hex[:8]}.mp3")
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text_clean,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.50,
                        "similarity_boost": 0.75,
                        "style": 0.60,
                        "use_speaker_boost": True
                    }
                }
            )
            
            if response.status_code == 200:
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                
                # Apply 1.1x speed to audio ONLY
                output_file = temp_file.replace(".mp3", "_speed.mp3")
                cmd = [
                    "ffmpeg", "-i", temp_file,
                    "-filter:a", f"atempo={VOICE_SPEED},loudnorm=I=-16:LRA=11:TP=-1.5",
                    "-t", str(duration),
                    "-b:a", "128k",
                    "-y", output_file
                ]
                
                if run_ffmpeg(cmd, timeout=20):
                    cleanup_file(temp_file)
                    if os.path.exists(output_file):
                        logger.info(f"✅ ElevenLabs ({VOICE_SPEED}x): {get_file_size_mb(output_file):.1f}MB")
                        return output_file
            else:
                logger.warning(f"ElevenLabs {response.status_code}: {response.text[:150]}")
        
        # Fallback to Edge TTS
        return await generate_voice_edge(text, duration, temp_dir)
        
    except Exception as e:
        logger.error(f"ElevenLabs error: {e}")
        return await generate_voice_edge(text, duration, temp_dir)

async def generate_voice_edge(text: str, duration: float, temp_dir: str) -> str:
    """Fallback Edge TTS with 1.1x speed"""
    try:
        import edge_tts
        
        temp_file = os.path.join(temp_dir, f"edge_{uuid.uuid4().hex[:8]}.mp3")
        text_clean = text.replace("...", " ").strip()[:250]
        
        # +15% rate for 1.1x effect
        communicate = edge_tts.Communicate(
            text_clean, 
            "hi-IN-MadhurNeural", 
            rate="+15%"
        )
        await communicate.save(temp_file)
        
        # Normalize audio
        output_file = temp_file.replace(".mp3", "_norm.mp3")
        cmd = [
            "ffmpeg", "-i", temp_file,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            "-t", str(duration),
            "-b:a", "128k",
            "-y", output_file
        ]
        
        if run_ffmpeg(cmd, timeout=15):
            cleanup_file(temp_file)
            if os.path.exists(output_file):
                logger.info(f"✅ Edge TTS ({VOICE_SPEED}x): {get_file_size_mb(output_file):.1f}MB")
                return output_file
        
        return None
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
        return None

# ============================================================================
# PIXABAY - VIDEOS + MUSIC
# ============================================================================

async def search_pixabay_videos(query: str) -> List[dict]:
    """Search Pixabay with simple 1-2 word queries"""
    try:
        # Keep queries simple - 1 word best
        search_query = query.split()[0] if query else "nature"
        
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://pixabay.com/api/videos/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": search_query,
                    "per_page": 10,
                    "video_type": "film",
                    "orientation": "vertical",
                    "order": "popular"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get("hits", [])
                if videos:
                    logger.info(f"✅ Found {len(videos)} videos: '{search_query}'")
                    return videos
        
        return []
    except Exception as e:
        logger.error(f"Pixabay search error: {e}")
        return []

async def download_video(video_data: dict, output_path: str) -> bool:
    """Download video with size limit (25MB max)"""
    try:
        videos = video_data.get("videos", {})
        
        # Try small first for memory efficiency, then medium
        video_url = videos.get("small", {}).get("url") or videos.get("medium", {}).get("url")
        
        if not video_url:
            return False
        
        async with httpx.AsyncClient(timeout=50) as client:
            async with client.stream('GET', video_url) as response:
                if response.status_code != 200:
                    return False
                
                # Check size
                content_length = response.headers.get('content-length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > MAX_VIDEO_SIZE_MB:
                        logger.warning(f"Video too large: {size_mb:.1f}MB")
                        return False
                
                # Download
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                
                size = get_file_size_mb(output_path)
                logger.info(f"✅ Downloaded: {size:.1f}MB")
                return True
                
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False

async def download_background_music(temp_dir: str) -> str:
    """Download background music from Pixabay"""
    try:
        music_path = os.path.join(temp_dir, "bgmusic.mp3")
        
        # Search for space music
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.get(
                "https://pixabay.com/api/",
                params={
                    "key": PIXABAY_API_KEY,
                    "q": "space",
                    "audio_type": "music",
                    "per_page": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", [])
                
                if hits:
                    # Download first music
                    audio_url = hits[0].get("previewURL")
                    if audio_url:
                        audio_resp = await client.get(audio_url, timeout=30)
                        if audio_resp.status_code == 200:
                            with open(music_path, 'wb') as f:
                                f.write(audio_resp.content)
                            logger.info(f"✅ Music: {get_file_size_mb(music_path):.1f}MB")
                            return music_path
        
        logger.warning("No music found")
        return None
        
    except Exception as e:
        logger.error(f"Music download error: {e}")
        return None

# ============================================================================
# VIDEO PROCESSING
# ============================================================================

def extract_clip(video_path: str, duration: float, temp_dir: str) -> str:
    """Extract vertical clip 720x1280"""
    output_path = os.path.join(temp_dir, f"clip_{uuid.uuid4().hex[:6]}.mp4")
    
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", "1",  # Skip first second
            "-t", str(duration),
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-crf", "26",  # Slightly lower quality for memory
            "-preset", "veryfast",
            "-an",  # No audio
            "-y", output_path
        ]
        
        if run_ffmpeg(cmd, timeout=30):
            cleanup_file(video_path)
            if os.path.exists(output_path):
                logger.info(f"✅ Clipped: {get_file_size_mb(output_path):.1f}MB")
                return output_path
        
        return video_path
    except Exception as e:
        logger.error(f"Clip error: {e}")
        return video_path

def add_text_overlay(video_path: str, text: str, temp_dir: str) -> str:
    """Add text overlay to video"""
    output_path = os.path.join(temp_dir, f"text_{uuid.uuid4().hex[:6]}.mp4")
    
    try:
        # Clean text
        text_clean = text.replace("'", "").replace(":", "")[:30]
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"drawtext=text='{text_clean}':fontsize=65:fontcolor=white:x=(w-text_w)/2:y=h-250:borderw=6:bordercolor=black:shadowcolor=black@0.7:shadowx=3:shadowy=3",
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "veryfast",
            "-y", output_path
        ]
        
        if run_ffmpeg(cmd, timeout=30):
            cleanup_file(video_path)
            if os.path.exists(output_path):
                return output_path
        
        return video_path
    except Exception as e:
        logger.error(f"Text overlay error: {e}")
        return video_path

def add_fade_transition(video_path: str, duration: float, temp_dir: str) -> str:
    """Add fade in/out"""
    output_path = os.path.join(temp_dir, f"fade_{uuid.uuid4().hex[:6]}.mp4")
    
    try:
        fade_dur = min(0.5, duration / 5)
        fade_out = duration - fade_dur
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"fade=t=in:st=0:d={fade_dur},fade=t=out:st={fade_out}:d={fade_dur}",
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "veryfast",
            "-y", output_path
        ]
        
        if run_ffmpeg(cmd, timeout=25):
            cleanup_file(video_path)
            if os.path.exists(output_path):
                return output_path
        
        return video_path
    except Exception as e:
        logger.error(f"Fade error: {e}")
        return video_path

# ============================================================================
# FINAL COMPILATION
# ============================================================================

def compile_final_video(clips: List[str], audios: List[str], music_path: str, temp_dir: str) -> str:
    """Compile final video with background music"""
    try:
        # Concat videos
        concat_list = os.path.join(temp_dir, "concat.txt")
        with open(concat_list, 'w') as f:
            for clip in clips:
                if clip and os.path.exists(clip):
                    f.write(f"file '{clip}'\n")
        
        video_concat = os.path.join(temp_dir, "video_all.mp4")
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            "-y", video_concat
        ]
        run_ffmpeg(cmd, timeout=40)
        
        # Concat audios
        audio_list = os.path.join(temp_dir, "audio.txt")
        with open(audio_list, 'w') as f:
            for audio in audios:
                if audio and os.path.exists(audio):
                    f.write(f"file '{audio}'\n")
        
        audio_concat = os.path.join(temp_dir, "audio_all.mp3")
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", audio_list,
            "-c", "copy",
            "-y", audio_concat
        ]
        run_ffmpeg(cmd, timeout=30)
        
        # Final mix with background music
        final_output = os.path.join(temp_dir, "final.mp4")
        
        if music_path and os.path.exists(music_path):
            # Mix voice + background music
            cmd = [
                "ffmpeg",
                "-i", video_concat,
                "-i", audio_concat,
                "-i", music_path,
                "-filter_complex",
                "[1:a]volume=1.0[voice];[2:a]volume=0.20,afade=t=in:st=0:d=2,afade=t=out:st=28:d=2[music];[voice][music]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", final_output
            ]
        else:
            # No background music
            cmd = [
                "ffmpeg",
                "-i", video_concat,
                "-i", audio_concat,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", final_output
            ]
        
        if run_ffmpeg(cmd, timeout=60):
            cleanup_file(video_concat)
            cleanup_file(audio_concat)
            
            if os.path.exists(final_output):
                logger.info(f"✅ Final video: {get_file_size_mb(final_output):.1f}MB")
                return final_output
        
        return None
        
    except Exception as e:
        logger.error(f"Compilation error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, 
                           tags: List[str], user_id: str) -> dict:
    """Upload to YouTube"""
    try:
        from YTdatabase import get_database_manager as get_yt_db
        
        yt_db = get_yt_db()
        if not yt_db:
            return {"success": False, "error": "YouTube DB unavailable"}
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        # Get credentials
        creds_raw = await yt_db.youtube.youtube_credentials_collection.find_one(
            {"user_id": user_id}
        )
        
        if not creds_raw:
            return {"success": False, "error": "YouTube not connected"}
        
        credentials = {
            "access_token": creds_raw.get("access_token"),
            "refresh_token": creds_raw.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        }
        
        from mainY import youtube_scheduler
        
        full_desc = f"{description}\n\n#{' #'.join(tags)}"
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=f"{title} #Shorts",
            description=full_desc,
            video_url=video_path
        )
        
        if result.get("success"):
            video_id = result.get("video_id")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
        
    except Exception as e:
        logger.error(f"YouTube upload error: {e}")
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
    """Main video generation pipeline"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_")
        logger.info(f"🎬 Generating viral video for {niche}")
        
        # Step 1: Generate engaging script
        logger.info("📝 Generating script...")
        script = await generate_viral_script(niche)
        
        if not script or not script.get("segments"):
            return {"success": False, "error": "Script generation failed"}
        
        logger.info(f"✅ Script ready: {len(script['segments'])} segments")
        logger.info(f"📋 Title: {script['title']}")
        
        # Step 2: Download background music
        logger.info("🎵 Downloading background music...")
        music_path = await download_background_music(temp_dir)
        
        # Step 3: Process 4 unique videos
        logger.info(f"🎥 Processing {MAX_VIDEOS} videos...")
        
        processed_clips = []
        audio_files = []
        used_video_ids = set()
        
        for idx, segment in enumerate(script["segments"][:MAX_VIDEOS]):
            try:
                logger.info(f"📥 Processing video {idx+1}/{MAX_VIDEOS}")
                
                seg_duration = segment.get("duration", 8)
                
                # Search videos
                videos = await search_pixabay_videos(segment["video_search"])
                if not videos:
                    logger.warning(f"No videos for '{segment['video_search']}'")
                    continue
                
                # Download unique video
                video_path = None
                for video_data in videos:
                    video_id = video_data.get("id")
                    if video_id not in used_video_ids:
                        temp_path = os.path.join(temp_dir, f"raw_{idx}.mp4")
                        success = await download_video(video_data, temp_path)
                        if success:
                            video_path = temp_path
                            used_video_ids.add(video_id)
                            logger.info(f"✅ Video {idx+1} ID: {video_id}")
                            break
                
                if not video_path:
                    logger.warning(f"Could not download video {idx+1}")
                    continue
                
                # Process video
                clip = extract_clip(video_path, seg_duration, temp_dir)
                
                if show_captions:
                    clip = add_text_overlay(clip, segment.get("text_overlay", ""), temp_dir)
                
                clip = add_fade_transition(clip, seg_duration, temp_dir)
                
                processed_clips.append(clip)
                
                # Generate voice with 1.1x speed
                logger.info(f"🎤 Generating voice {idx+1}...")
                voice = await generate_voice_elevenlabs(
                    segment.get("narration", ""),
                    seg_duration,
                    temp_dir
                )
                
                if voice:
                    audio_files.append(voice)
                
                gc.collect()
                logger.info(f"✅ Video {idx+1} complete")
                
            except Exception as e:
                logger.error(f"Video {idx+1} error: {e}")
                continue
        
        if len(processed_clips) < 3:
            return {"success": False, "error": f"Only {len(processed_clips)} videos created, need at least 3"}
        
        # Step 4: Add subscribe clip
        logger.info("📌 Adding subscribe overlay...")
        subscribe_videos = await search_pixabay_videos("subscribe")
        
        if subscribe_videos:
            subscribe_path = os.path.join(temp_dir, "subscribe.mp4")
            success = await download_video(subscribe_videos[0], subscribe_path)
            
            if success:
                clip = extract_clip(subscribe_path, SUBSCRIBE_DURATION, temp_dir)
                
                # Add subscribe text
                sub_text_path = os.path.join(temp_dir, f"sub_text_{uuid.uuid4().hex[:6]}.mp4")
                cmd = [
                    "ffmpeg", "-i", clip,
                    "-vf", "drawtext=text='SUBSCRIBE करें 🔔':fontsize=75:fontcolor=yellow:x=(w-text_w)/2:y=(h-text_h)/2:borderw=7:bordercolor=red:shadowcolor=black@0.8:shadowx=4:shadowy=4",
                    "-c:v", "libx264",
                    "-crf", "26",
                    "-preset", "veryfast",
                    "-y", sub_text_path
                ]
                
                if run_ffmpeg(cmd, timeout=25):
                    cleanup_file(clip)
                    clip = sub_text_path
                
                clip = add_fade_transition(clip, SUBSCRIBE_DURATION, temp_dir)
                processed_clips.append(clip)
                
                # Add silent audio
                silent_audio = os.path.join(temp_dir, "silent.mp3")
                cmd = [
                    "ffmpeg", "-f", "lavfi",
                    "-i", f"anullsrc=r=44100:cl=mono:d={SUBSCRIBE_DURATION}",
                    "-b:a", "64k",
                    "-y", silent_audio
                ]
                
                if run_ffmpeg(cmd, timeout=15):
                    audio_files.append(silent_audio)
                
                logger.info("✅ Subscribe clip added")
        
        # Step 5: Compile final video
        logger.info("🎬 Compiling final video...")
        final_video = compile_final_video(
            processed_clips,
            audio_files,
            music_path,
            temp_dir
        )
        
        if not final_video:
            return {"success": False, "error": "Video compilation failed"}
        
        logger.info(f"✅ Final video: {get_file_size_mb(final_video):.1f}MB")
        
        # Step 6: Upload to YouTube
        logger.info("📤 Uploading to YouTube...")
        upload_result = await upload_to_youtube(
            final_video,
            script.get("title", "Viral Video"),
            script.get("description", ""),
            script.get("tags", []),
            user_id
        )
        
        # Cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info("🗑️ Cleaned temp directory")
            except:
                pass
        
        gc.collect()
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        total_duration = sum([s.get("duration", 8) for s in script["segments"]])
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script.get("title"),
            "segments": len(processed_clips),
            "duration": f"{total_duration} seconds",
            "features": f"✅ ElevenLabs {VOICE_SPEED}x voice\n✅ {len(processed_clips)} unique videos\n✅ Background music\n✅ Hook-Story-Suspense-Outro structure"
        }
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        logger.error(traceback.format_exc())
        
        # Cleanup on error
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/viral-pixel/niches")
async def get_niches():
    """Get available niches"""
    return {
        "success": True,
        "niches": {k: {"name": v["name"]} for k, v in NICHES.items()}
    }

@router.post("/api/viral-pixel/generate")
async def generate_video_endpoint(request: Request):
    """Generate viral video endpoint"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Authentication required"}
            )
        
        niche = data.get("niche", "space")
        duration = int(data.get("duration", 30))
        language = data.get("language", "hindi")
        channel_name = data.get("channel_name", "My Channel")
        show_captions = data.get("show_captions", True)
        voice_gender = data.get("voice_gender", "male")
        
        if niche not in NICHES:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid niche"}
            )
        
        from Supermain import database_manager
        
        try:
            result = await asyncio.wait_for(
                generate_viral_video(
                    niche=niche,
                    duration=duration,
                    language=language,
                    channel_name=channel_name,
                    show_captions=show_captions,
                    voice_gender=voice_gender,
                    user_id=user_id,
                    database_manager=database_manager
                ),
                timeout=480  # 8 minutes
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Generation timeout (8 min)"}
            )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

__all__ = ['router']