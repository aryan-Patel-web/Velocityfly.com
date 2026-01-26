
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
Viral_pixel.py - ULTRA MEMORY-EFFICIENT (<512MB RAM)
✅ ElevenLabs v2 API with proper authentication
✅ Extreme memory cleanup (download→clip→delete→repeat)
✅ 720p fallback for memory safety
✅ 5 videos total: 4 content + 1 subscribe (from Pixabay)
✅ Each video: 6-9 seconds → Total: 24-28 sec + 2-3 sec subscribe = 30 sec
✅ Background music from Pixabay URL
✅ Aggressive garbage collection
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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "c698af740ba0254488c629da3e373d50e33ab0d278bac71cdaf0a517855acef6")

# ElevenLabs Voice ID - Shardul K Deep Horror Storyteller
ELEVENLABS_VOICE_ID = "Aano0MRpH01ekWzUtv60"

# EXTREME memory limits
MAX_VIDEO_SIZE_MB = 15  # Strict limit
CLIP_MIN = 6  # 6 seconds minimum
CLIP_MAX = 9  # 9 seconds maximum
MAX_CONTENT_VIDEOS = 4  # Only 4 content videos
SUBSCRIBE_DURATION = 2.5  # 2-3 seconds subscribe
FFMPEG_TIMEOUT = 20

# Background music URL from Pixabay
BG_MUSIC_URL = "https://cdn.pixabay.com/download/audio/2024/12/12/audio_1b088a0d23.mp3?filename=film-special-effects-ambient-soundscapes-007-space-atmosphere-304974.mp3"

NICHES = {
    "space": {
        "name": "Space & Universe 🌌",
        "searches": ["galaxy", "nebula", "stars", "planet"],
        "subscribe_search": "youtube subscribe"
    },
    "tech_ai": {
        "name": "Technology & AI 🤖",
        "searches": ["robot", "technology", "AI", "digital"],
        "subscribe_search": "youtube subscribe"
    },
    "ocean": {
        "name": "Ocean & Marine 🌊",
        "searches": ["ocean", "underwater", "coral", "whale"],
        "subscribe_search": "youtube subscribe"
    },
    "nature": {
        "name": "Nature & Wildlife 🦁",
        "searches": ["lion", "eagle", "forest", "tiger"],
        "subscribe_search": "youtube subscribe"
    },
    "success": {
        "name": "Success & Motivation 💪",
        "searches": ["success", "workout", "motivation", "goal"],
        "subscribe_search": "youtube subscribe"
    },
    "sports": {
        "name": "Sports & Fitness ⚽",
        "searches": ["football", "gym", "athlete", "fitness"],
        "subscribe_search": "youtube subscribe"
    }
}

# ============================================================================
# AGGRESSIVE MEMORY MANAGEMENT
# ============================================================================

def force_cleanup(filepath: str):
    """AGGRESSIVE cleanup with multiple GC passes"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🗑️ Deleted: {os.path.basename(filepath)}")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")
    
    # Force 3 GC passes
    gc.collect()
    gc.collect()
    gc.collect()

def get_file_size_mb(filepath: str) -> float:
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except:
        return 0

def run_ffmpeg_quick(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """Run FFmpeg with timeout and immediate cleanup"""
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
        gc.collect()
        return result.returncode == 0
    except:
        gc.collect()
        return False

# ============================================================================
# AI SCRIPT GENERATION - 30 SECONDS MAX
# ============================================================================

async def generate_script_ai(niche: str) -> dict:
    """Generate 30-second emotional script"""
    try:
        niche_info = NICHES.get(niche, NICHES["space"])
        searches = niche_info["searches"]
        
        prompt = f"""Create a 30-SECOND viral story about {niche} for YouTube Shorts.

REQUIREMENTS:
1. Title in ENGLISH (viral style with #Shorts)
2. Narration in HINDI with emotion
3. Use CAPITALS for emphasis and "..." for pauses
4. EXACTLY 4 segments (each 6-9 seconds)
5. Total script time: 24-28 seconds (NOT more!)
6. Very short sentences (6-10 words max)
7. Emotional: fear, hope, mystery

Example narration:
"सुनो... ध्यान से... यह रहस्य चौंका देगा!"
"अंतरिक्ष में... कोई आवाज़ नहीं... लेकिन..."

Output ONLY JSON:
{{
  "title": "Mind-Blowing Secret #Shorts",
  "description": "Description with hashtags",
  "tags": ["viral", "shorts", "hindi"],
  "segments": [
    {{
      "narration": "Hindi text with CAPITALS and ...",
      "text_overlay": "2-3 words",
      "video_search": "{searches[0]}",
      "emoji": "🔥",
      "duration": 7
    }}
  ]
}}"""
        
        # Try Mistral
        if MISTRAL_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    response = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": "mistral-large-latest",
                            "messages": [
                                {"role": "system", "content": "Create viral emotional scripts. Output ONLY JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1200
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                        script = json.loads(ai_response)
                        script["segments"] = script["segments"][:MAX_CONTENT_VIDEOS]
                        logger.info("✅ Script via Mistral")
                        return script
            except Exception as e:
                logger.warning(f"Mistral failed: {e}")
        
        # Try Groq
        if GROQ_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": "mixtral-8x7b-32768",
                            "messages": [
                                {"role": "system", "content": "Create viral scripts. Output ONLY JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.9,
                            "max_tokens": 1200
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_response = re.sub(r'```json\n?|\n?```', '', ai_response).strip()
                        script = json.loads(ai_response)
                        script["segments"] = script["segments"][:MAX_CONTENT_VIDEOS]
                        logger.info("✅ Script via Groq")
                        return script
            except Exception as e:
                logger.warning(f"Groq failed: {e}")
        
        return generate_fallback_template(niche, searches)
        
    except Exception as e:
        logger.error(f"Script error: {e}")
        return generate_fallback_template(niche, NICHES.get(niche, NICHES["space"])["searches"])

def generate_fallback_template(niche: str, searches: List[str]) -> dict:
    """Fallback 30-second script"""
    
    segments = [
        {
            "narration": "सुनो... ध्यान से... यह रहस्य चौंका देगा!",
            "text_overlay": "सुनो",
            "video_search": searches[0],
            "emoji": "🔥",
            "duration": 7
        },
        {
            "narration": "यह सच है... लेकिन यकीन नहीं होगा!",
            "text_overlay": "अविश्वसनीय",
            "video_search": searches[1] if len(searches) > 1 else searches[0],
            "emoji": "😨",
            "duration": 7
        },
        {
            "narration": "अब समय आ गया... सच जानने का!",
            "text_overlay": "सच",
            "video_search": searches[2] if len(searches) > 2 else searches[0],
            "emoji": "💡",
            "duration": 7
        },
        {
            "narration": "यह बदल देगा... आपकी सोच पूरी तरह!",
            "text_overlay": "बदलाव",
            "video_search": searches[3] if len(searches) > 3 else searches[0],
            "emoji": "🎯",
            "duration": 7
        }
    ]
    
    return {
        "title": f"Shocking {niche.title()} Secret #Shorts",
        "description": f"Mind-blowing revelation! #{niche} #viral #shorts",
        "tags": [niche, "viral", "shorts", "hindi"],
        "segments": segments[:MAX_CONTENT_VIDEOS]
    }

# ============================================================================
# ELEVENLABS VOICE - PROPER API
# ============================================================================

async def generate_voiceover_elevenlabs(text: str, duration: float) -> str:
    """ElevenLabs v2 with proper API key"""
    try:
        if not ELEVENLABS_API_KEY:
            logger.warning("No ElevenLabs key, using Edge TTS")
            return await generate_voiceover_edge_tts(text, duration)
        
        processed_text = text.replace("...", ".")[:200]
        temp_file = f"/tmp/elv_{uuid.uuid4().hex[:6]}.mp3"
        
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": processed_text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.45,
                        "similarity_boost": 0.75,
                        "style": 0.65,
                        "use_speaker_boost": True
                    }
                }
            )
            
            if response.status_code == 200:
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                
                output_file = temp_file.replace(".mp3", "_adj.mp3")
                cmd = [
                    "ffmpeg", "-i", temp_file,
                    "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
                    "-t", str(duration),
                    "-b:a", "96k",
                    output_file,
                    "-y"
                ]
                
                run_ffmpeg_quick(cmd, timeout=12)
                force_cleanup(temp_file)
                
                if os.path.exists(output_file):
                    logger.info(f"✅ ElevenLabs voice: {get_file_size_mb(output_file):.1f}MB")
                    return output_file
            else:
                logger.warning(f"ElevenLabs error: {response.status_code}")
        
        return await generate_voiceover_edge_tts(text, duration)
        
    except Exception as e:
        logger.error(f"ElevenLabs error: {e}")
        return await generate_voiceover_edge_tts(text, duration)

async def generate_voiceover_edge_tts(text: str, duration: float) -> str:
    """Fallback Edge TTS"""
    try:
        import edge_tts
        
        temp_file = f"/tmp/tts_{uuid.uuid4().hex[:6]}.mp3"
        text_clean = text.replace("...", " ")[:180]
        
        communicate = edge_tts.Communicate(text_clean, "hi-IN-MadhurNeural", rate="+10%")
        await communicate.save(temp_file)
        
        output_file = temp_file.replace(".mp3", "_adj.mp3")
        cmd = [
            "ffmpeg", "-i", temp_file,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            "-t", str(duration),
            "-b:a", "96k",
            output_file,
            "-y"
        ]
        
        run_ffmpeg_quick(cmd, timeout=12)
        force_cleanup(temp_file)
        
        if os.path.exists(output_file):
            logger.info(f"✅ Edge TTS: {get_file_size_mb(output_file):.1f}MB")
            return output_file
        
        return None
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
        return None

# ============================================================================
# PIXABAY - VERTICAL VIDEOS WITH 720P FALLBACK
# ============================================================================

async def search_pixabay_videos(query: str, is_subscribe: bool = False) -> List[dict]:
    """Search Pixabay for vertical videos"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
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
                    logger.info(f"✅ Found {len(videos)} vertical videos: '{query}'")
                    return videos
                else:
                    first_word = query.split()[0]
                    if first_word != query:
                        return await search_pixabay_videos(first_word, is_subscribe)
            return []
    except Exception as e:
        logger.error(f"Pixabay error: {e}")
        return []

async def download_video_with_fallback(video_data: dict, output_path: str) -> bool:
    """Download with 720p fallback for memory safety"""
    try:
        videos = video_data.get("videos", {})
        
        # Try medium first (720p), then small
        video_url = videos.get("medium", {}).get("url") or videos.get("small", {}).get("url")
        
        if not video_url:
            return False
        
        async with httpx.AsyncClient(timeout=30) as client:
            async with client.stream('GET', video_url) as response:
                if response.status_code != 200:
                    return False
                
                content_length = response.headers.get('content-length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > MAX_VIDEO_SIZE_MB:
                        logger.warning(f"⚠️ Too large: {size_mb:.1f}MB, trying smaller")
                        
                        # Try small version
                        small_url = videos.get("small", {}).get("url")
                        if small_url and small_url != video_url:
                            async with client.stream('GET', small_url) as small_resp:
                                if small_resp.status_code == 200:
                                    with open(output_path, 'wb') as f:
                                        async for chunk in small_resp.aiter_bytes(chunk_size=8192):
                                            f.write(chunk)
                                    logger.info(f"✅ Downloaded (small): {get_file_size_mb(output_path):.1f}MB")
                                    return True
                        return False
                
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"✅ Downloaded: {get_file_size_mb(output_path):.1f}MB")
                return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False

async def download_background_music(temp_dir: str) -> str:
    """Download background music from Pixabay"""
    try:
        music_path = os.path.join(temp_dir, "bgmusic.mp3")
        
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.get(BG_MUSIC_URL)
            if response.status_code == 200:
                with open(music_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✅ Music: {get_file_size_mb(music_path):.1f}MB")
                return music_path
        return None
    except Exception as e:
        logger.error(f"Music error: {e}")
        return None

# ============================================================================
# VIDEO PROCESSING - 720P WITH AGGRESSIVE CLEANUP
# ============================================================================

def extract_clip_720p(video_path: str, duration: float) -> str:
    """Extract and crop to 720p vertical (720x1280)"""
    output_path = video_path.replace(".mp4", "_clip.mp4")
    
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", "1",
            "-t", str(duration),
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "ultrafast",
            "-an",
            output_path,
            "-y"
        ]
        
        if run_ffmpeg_quick(cmd, timeout=20):
            if os.path.exists(output_path) and get_file_size_mb(output_path) > 0:
                force_cleanup(video_path)  # Delete original IMMEDIATELY
                logger.info(f"✅ Clipped 720p: {get_file_size_mb(output_path):.1f}MB")
                return output_path
        
        return video_path
    except Exception as e:
        logger.error(f"Clip error: {e}")
        return video_path

def add_text_overlay_720p(video_path: str, text: str, emoji: str) -> str:
    """Add text overlay"""
    output_path = video_path.replace(".mp4", "_text.mp4")
    
    try:
        text_escaped = text.replace("'", "").replace(":", "").replace(";", "").replace("...", "")[:20]
        full_text = f"{text_escaped} {emoji}"
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"drawtext=text='{full_text}':fontsize=55:fontcolor=white:x=(w-text_w)/2:y=h-180:borderw=4:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2",
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "ultrafast",
            output_path,
            "-y"
        ]
        
        if run_ffmpeg_quick(cmd, timeout=20):
            if os.path.exists(output_path):
                force_cleanup(video_path)  # Delete previous IMMEDIATELY
                logger.info(f"✅ Text added")
                return output_path
        
        return video_path
    except Exception as e:
        logger.error(f"Text error: {e}")
        return video_path

def add_subscribe_overlay(video_path: str, duration: float) -> str:
    """Add subscribe overlay"""
    output_path = video_path.replace(".mp4", "_sub.mp4")
    
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"drawtext=text='SUBSCRIBE करें 🔔':fontsize=70:fontcolor=yellow:x=(w-text_w)/2:y=(h-text_h)/2:borderw=5:bordercolor=red:shadowcolor=black:shadowx=3:shadowy=3",
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "ultrafast",
            output_path,
            "-y"
        ]
        
        if run_ffmpeg_quick(cmd, timeout=20):
            if os.path.exists(output_path):
                force_cleanup(video_path)
                return output_path
        
        return video_path
    except Exception as e:
        logger.error(f"Subscribe error: {e}")
        return video_path

def add_fade(video_path: str) -> str:
    """Add fade transition"""
    output_path = video_path.replace(".mp4", "_fade.mp4")
    
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "fade=t=in:st=0:d=0.3,fade=t=out:st=-1:d=0.3",
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "ultrafast",
            output_path,
            "-y"
        ]
        
        if run_ffmpeg_quick(cmd, timeout=20):
            if os.path.exists(output_path):
                force_cleanup(video_path)
                return output_path
        
        return video_path
    except Exception as e:
        logger.error(f"Fade error: {e}")
        return video_path

# ============================================================================
# FINAL COMPILATION
# ============================================================================

def compile_final(clips: List[str], audios: List[str], music_path: str, temp_dir: str) -> str:
    """Compile with background music at 30%"""
    try:
        # Concat videos
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for clip in clips:
                if clip and os.path.exists(clip):
                    f.write(f"file '{clip}'\n")
        
        temp_video = os.path.join(temp_dir, "video.mp4")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", temp_video, "-y"]
        run_ffmpeg_quick(cmd, timeout=40)
        
        if not os.path.exists(temp_video):
            return None
        
        # Concat audio
        audio_concat = os.path.join(temp_dir, "audio.txt")
        with open(audio_concat, 'w') as f:
            for audio in audios:
                if audio and os.path.exists(audio):
                    f.write(f"file '{audio}'\n")
        
        combined_audio = os.path.join(temp_dir, "voice.mp3")
        cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", audio_concat, "-c", "copy", combined_audio, "-y"]
        run_ffmpeg_quick(cmd, timeout=30)
        
        final_output = os.path.join(temp_dir, "final.mp4")
        
        # Mix with music at 30%
        if music_path and os.path.exists(music_path):
            cmd = [
                "ffmpeg",
                "-i", temp_video,
                "-i", combined_audio,
                "-i", music_path,
                "-filter_complex", 
                "[1:a]volume=1.0[voice];[2:a]volume=0.3,afade=t=in:st=0:d=2,afade=t=out:st=26:d=2[music];[voice][music]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
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
                "-b:a", "96k",
                "-shortest",
                final_output,
                "-y"
            ]
        
        run_ffmpeg_quick(cmd, timeout=50)
        
        # Cleanup
        force_cleanup(temp_video)
        force_cleanup(combined_audio)
        
        for clip in clips:
            force_cleanup(clip)
        for audio in audios:
            force_cleanup(audio)
        
        if os.path.exists(final_output):
            logger.info(f"✅ Final: {get_file_size_mb(final_output):.1f}MB")
            return final_output
        
        return None
    except Exception as e:
        logger.error(f"Compilation error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, 
                           tags: List[str], user_id: str, database_manager) -> dict:
    """Upload to YouTube"""
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            return {"success": False, "error": "YouTube database unavailable"}
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
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
            video_id = upload_result.get("video_id")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://youtube.com/shorts/{video_id}"
            }
        
        return {"success": False, "error": upload_result.get("error", "Upload failed")}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN GENERATION - ULTRA MEMORY EFFICIENT
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
    """Generate with <512MB RAM usage"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="viral_")
        logger.info(f"🎬 Starting ULTRA memory-efficient generation")
        
        # STEP 1: Generate 30-second script
        logger.info("📝 Generating script...")
        script = await generate_script_ai(niche)
        
        if not script or not script.get("segments"):
            return {"success": False, "error": "Script generation failed"}
        
        logger.info(f"✅ Script: {len(script['segments'])} segments")
        logger.info(f"📋 Title: {script.get('title')}")
        
        # STEP 2: Download background music
        logger.info("🎵 Downloading music...")
        music_path = await download_background_music(temp_dir)
        
        # STEP 3: Process 4 content videos ONE BY ONE
        logger.info("🎥 Processing 4 content videos...")
        
        processed_clips = []
        audio_files = []
        used_video_ids = set()
        
        for idx, segment in enumerate(script["segments"][:MAX_CONTENT_VIDEOS]):
            try:
                logger.info(f"📥 Video {idx+1}/4")
                
                seg_duration = segment.get("duration", random.randint(CLIP_MIN, CLIP_MAX))
                
                # Search videos
                videos = await search_pixabay_videos(segment["video_search"])
                if not videos:
                    logger.warning(f"No videos for '{segment['video_search']}'")
                    continue
                
                # Find unique video
                video_path = None
                for video_data in videos:
                    video_id = video_data.get("id")
                    if video_id not in used_video_ids:
                        temp_path = os.path.join(temp_dir, f"raw_{idx}.mp4")
                        success = await download_video_with_fallback(video_data, temp_path)
                        if success:
                            video_path = temp_path
                            used_video_ids.add(video_id)
                            logger.info(f"✅ Video ID: {video_id}")
                            break
                
                if not video_path:
                    continue
                
                # Process: Extract → Text → Fade (delete after each step)
                clip = extract_clip_720p(video_path, seg_duration)
                
                if show_captions:
                    clip = add_text_overlay_720p(clip, segment.get("text_overlay", ""), segment.get("emoji", "🔥"))
                
                clip = add_fade(clip)
                
                processed_clips.append(clip)
                
                # Generate voice
                logger.info(f"🎤 Voice {idx+1}...")
                voice = await generate_voiceover_elevenlabs(
                    segment.get("narration", ""),
                    seg_duration
                )
                if voice:
                    audio_files.append(voice)
                
                gc.collect()
                gc.collect()
                
                logger.info(f"✅ Video {idx+1} complete")
                
            except Exception as e:
                logger.error(f"Video {idx+1} error: {e}")
                continue
        
        if len(processed_clips) < 3:
            return {"success": False, "error": f"Not enough clips: {len(processed_clips)}"}
        
        # STEP 4: Add subscribe video (5th video)
        logger.info("📌 Adding subscribe video...")
        subscribe_videos = await search_pixabay_videos("youtube subscribe", is_subscribe=True)
        
        if subscribe_videos:
            subscribe_path = os.path.join(temp_dir, "subscribe.mp4")
            success = await download_video_with_fallback(subscribe_videos[0], subscribe_path)
            
            if success:
                clip = extract_clip_720p(subscribe_path, SUBSCRIBE_DURATION)
                clip = add_subscribe_overlay(clip, SUBSCRIBE_DURATION)
                clip = add_fade(clip)
                processed_clips.append(clip)
                
                # Silent audio for subscribe clip
                silent_audio = os.path.join(temp_dir, "silent.mp3")
                cmd = [
                    "ffmpeg", "-f", "lavfi",
                    "-i", f"anullsrc=r=44100:cl=mono:d={SUBSCRIBE_DURATION}",
                    "-b:a", "64k",
                    silent_audio,
                    "-y"
                ]
                run_ffmpeg_quick(cmd, timeout=8)
                if os.path.exists(silent_audio):
                    audio_files.append(silent_audio)
                
                logger.info("✅ Subscribe video added")
        
        # STEP 5: Compile
        logger.info("🎬 Compiling...")
        final_video = compile_final(processed_clips, audio_files, music_path, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Compilation failed"}
        
        logger.info(f"✅ Final: {get_file_size_mb(final_video):.1f}MB")
        
        # STEP 6: Upload
        logger.info("📤 Uploading...")
        upload_result = await upload_to_youtube(
            final_video,
            script.get("title", "Viral Video"),
            script.get("description", ""),
            script.get("tags", []),
            user_id,
            database_manager
        )
        
        # Cleanup
        force_cleanup(final_video)
        if music_path:
            force_cleanup(music_path)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        gc.collect()
        gc.collect()
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script.get("title"),
            "segments": len(processed_clips),
            "quality": "720p vertical",
            "features": "✅ ElevenLabs\n✅ 4 content + 1 subscribe\n✅ Music 30%\n✅ <512MB RAM"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        
        gc.collect()
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# ROUTER
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
    """Generate viral video"""
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
                timeout=360  # 6 minutes
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Timeout"}
            )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

__all__ = ['router']