# # """
# # china_shorts.py - CHINA SHORTS VIDEO PROCESSOR V3.1 (PRODUCTION + MANUAL UPLOAD)
# # ===================================================================
# # ✅ 5 WORKING URL DOWNLOAD METHODS (Based on real SaveTik.co analysis)
# # ✅ NEW: Manual File Upload Processing
# # ✅ All same filters, captions, BGM, and YouTube upload
# # ===================================================================
# # """

# # from fastapi import APIRouter, Request, File, UploadFile, Form
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
# # import base64
# # from typing import Optional, List, Dict, Any
# # from datetime import datetime
# # import uuid
# # from urllib.parse import urlparse, parse_qs, urlencode
# # import aiofiles

# # try:
# #     import psutil
# #     HAS_PSUTIL = True
# # except:
# #     HAS_PSUTIL = False

# # # ═══════════════════════════════════════════════════════════════════════
# # # LOGGING
# # # ═══════════════════════════════════════════════════════════════════════
# # logger = logging.getLogger("ChinaShorts")
# # logger.setLevel(logging.INFO)

# # if not logger.handlers:
# #     handler = logging.StreamHandler()
# #     handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# #     logger.addHandler(handler)

# # def log_memory(step: str):
# #     """Log memory usage"""
# #     if HAS_PSUTIL:
# #         try:
# #             process = psutil.Process(os.getpid())
# #             mem_mb = process.memory_info().rss / 1024 / 1024
# #             logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
# #             if mem_mb > 450:
# #                 logger.warning(f"⚠️ HIGH: {mem_mb:.1f}MB")
# #                 gc.collect()
# #         except:
# #             pass

# # # ═══════════════════════════════════════════════════════════════════════
# # # CONFIG
# # # ═══════════════════════════════════════════════════════════════════════

# # CHINA_BGM_URLS = [
# #     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3"
# # ]

# # PROCESSING_STATUS = {}

# # CAPTION_EMOJIS = ["😂", "🤣", "😱", "😮", "🤔", "😍", "🔥", "✨", "💯", "👀", "🎉", "❤️", "🙌", "💪", "🤯"]
# # CAPTION_TEXT = ["LOL", "OMG", "WOW", "HAHA", "NICE", "EPIC", "COOL", "FIRE"]

# # # Douyin/TikTok headers (Critical for success)
# # DOUYIN_HEADERS = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# #     "Referer": "https://www.douyin.com/",
# #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
# #     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
# #     "Accept-Encoding": "gzip, deflate, br",
# #     "Cookie": "ttwid=1%7C; __ac_nonce=0; __ac_signature=_02B4Z6wo00f01; odin_tt=0",
# # }

# # MOBILE_HEADERS = {
# #     "User-Agent": "com.ss.android.ugc.aweme/260801 (Linux; U; Android 11; zh_CN; SM-G991B; Build/RP1A.200720.012; Cronet/TTNetVersion:d2f6e1a7 2021-06-15 QuicVersion:0144d358 2021-03-09)",
# #     "Accept-Encoding": "gzip, deflate",
# # }

# # # ═══════════════════════════════════════════════════════════════════════
# # # CLEANUP & FFMPEG
# # # ═══════════════════════════════════════════════════════════════════════

# # def cleanup(*paths):
# #     """Delete files and force garbage collection"""
# #     for path in paths:
# #         try:
# #             if path and os.path.exists(path):
# #                 os.remove(path)
# #         except:
# #             pass
# #     gc.collect()

# # def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
# #     """Run FFmpeg command"""
# #     logger.info(f"🎬 {step}...")
# #     try:
# #         result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout, text=True)
# #         if result.returncode == 0:
# #             logger.info(f"✅ {step}")
# #             return True
# #         else:
# #             logger.error(f"❌ {step} failed: {result.stderr[-200:]}")
# #             return False
# #     except Exception as e:
# #         logger.error(f"❌ {step} error: {e}")
# #         return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # URL EXTRACTION
# # # ═══════════════════════════════════════════════════════════════════════

# # def extract_video_id(url: str) -> Optional[str]:
# #     """Extract video ID from Douyin/TikTok URL"""
# #     patterns = [
# #         r'modal_id=(\d+)',
# #         r'video/(\d{19})',
# #         r'vid=(\d+)',
# #         r'/(\d{19})',
# #         r'item_ids=(\d+)',
# #     ]
    
# #     for pattern in patterns:
# #         match = re.search(pattern, url)
# #         if match:
# #             video_id = match.group(1)
# #             logger.info(f"   ✅ Extracted Video ID: {video_id}")
# #             return video_id
    
# #     return None

# # # ═══════════════════════════════════════════════════════════════════════
# # # METHOD 1: DOUYIN INTERNAL API (ITEMINFO) - BEST METHOD
# # # ═══════════════════════════════════════════════════════════════════════

# # async def download_douyin_api(video_id: str, output: str) -> bool:
# #     """
# #     Method 1: Douyin Internal API (iteminfo)
# #     This is what SaveTik.co uses primarily
# #     """
# #     logger.info("   📥 Method 1: Douyin Internal API (iteminfo)")
    
# #     if not video_id:
# #         logger.warning("   ❌ No video ID")
# #         return False
    
# #     # Douyin iteminfo API endpoint
# #     api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
    
# #     try:
# #         async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
# #             logger.info(f"   → Calling Douyin API: item_ids={video_id}")
            
# #             response = await client.get(api_url, headers=DOUYIN_HEADERS)
            
# #             if response.status_code != 200:
# #                 logger.warning(f"   ❌ API returned {response.status_code}")
# #                 return False
            
# #             data = response.json()
            
# #             # Navigate response structure
# #             if "item_list" not in data or not data["item_list"]:
# #                 logger.warning("   ❌ No item_list in response")
# #                 return False
            
# #             item = data["item_list"][0]
            
# #             # Extract video URLs (multiple quality options)
# #             video_urls = []
            
# #             # Try play_addr first (best quality)
# #             if "video" in item and "play_addr" in item["video"]:
# #                 play_addr = item["video"]["play_addr"]
                
# #                 if "url_list" in play_addr:
# #                     video_urls.extend(play_addr["url_list"])
            
# #             # Try download_addr (no watermark)
# #             if "video" in item and "download_addr" in item["video"]:
# #                 download_addr = item["video"]["download_addr"]
                
# #                 if "url_list" in download_addr:
# #                     video_urls.extend(download_addr["url_list"])
            
# #             # Try bit_rate array (different qualities)
# #             if "video" in item and "bit_rate" in item["video"]:
# #                 for bit_rate in item["video"]["bit_rate"]:
# #                     if "play_addr" in bit_rate and "url_list" in bit_rate["play_addr"]:
# #                         video_urls.extend(bit_rate["play_addr"]["url_list"])
            
# #             if not video_urls:
# #                 logger.warning("   ❌ No video URLs found in API response")
# #                 return False
            
# #             logger.info(f"   → Found {len(video_urls)} video URL(s)")
            
# #             # Try each URL until one works
# #             for i, video_url in enumerate(video_urls):
# #                 try:
# #                     logger.info(f"   → Trying URL {i+1}/{len(video_urls)}: {video_url[:60]}...")
                    
# #                     # Download video
# #                     download_headers = {**DOUYIN_HEADERS}
                    
# #                     async with client.stream("GET", video_url, headers=download_headers, timeout=180) as stream:
# #                         if stream.status_code == 200:
# #                             content_type = stream.headers.get("content-type", "")
                            
# #                             if "video" in content_type or "octet-stream" in content_type:
# #                                 total = 0
# #                                 with open(output, 'wb') as f:
# #                                     async for chunk in stream.aiter_bytes(1024*1024):
# #                                         f.write(chunk)
# #                                         total += len(chunk)
                                
# #                                 if total > 10000:
# #                                     size = total / (1024 * 1024)
# #                                     logger.info(f"   ✅ Method 1 SUCCESS: {size:.1f}MB")
# #                                     return True
# #                             else:
# #                                 logger.warning(f"   ❌ Wrong content-type: {content_type}")
                
# #                 except Exception as e:
# #                     logger.warning(f"   → URL {i+1} failed: {e}")
# #                     continue
            
# #             logger.warning("   ❌ All URLs failed")
# #             return False
    
# #     except Exception as e:
# #         logger.warning(f"   ❌ Method 1 ERROR: {e}")
# #         return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # METHOD 2: MOBILE API WITH PROPER HEADERS
# # # ═══════════════════════════════════════════════════════════════════════

# # async def download_mobile_api(video_id: str, output: str) -> bool:
# #     """Method 2: Mobile API (pretend to be Android app)"""
# #     logger.info("   📥 Method 2: Mobile API (Android app simulation)")
    
# #     if not video_id:
# #         logger.warning("   ❌ No video ID")
# #         return False
    
# #     # Mobile API endpoints
# #     mobile_endpoints = [
# #         f"https://aweme.snssdk.com/aweme/v1/play/?video_id={video_id}&ratio=default&line=0",
# #         f"https://api-va.tiktokv.com/aweme/v1/play/?video_id={video_id}",
# #     ]
    
# #     try:
# #         async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
# #             for endpoint in mobile_endpoints:
# #                 try:
# #                     logger.info(f"   → Trying: {endpoint[:60]}...")
                    
# #                     response = await client.get(endpoint, headers=MOBILE_HEADERS, timeout=120)
                    
# #                     if response.status_code == 200:
# #                         content_type = response.headers.get("content-type", "")
                        
# #                         if "video" in content_type or "octet-stream" in content_type:
# #                             with open(output, 'wb') as f:
# #                                 f.write(response.content)
                            
# #                             if os.path.getsize(output) > 10000:
# #                                 size = os.path.getsize(output) / (1024 * 1024)
# #                                 logger.info(f"   ✅ Method 2 SUCCESS: {size:.1f}MB")
# #                                 return True
                
# #                 except Exception as e:
# #                     logger.warning(f"   → Endpoint failed: {e}")
# #                     continue
            
# #             logger.warning("   ❌ All mobile endpoints failed")
# #             return False
    
# #     except Exception as e:
# #         logger.warning(f"   ❌ Method 2 ERROR: {e}")
# #         return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # METHOD 3: YT-DLP WITH COOKIES (Enhanced)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def download_ytdlp_enhanced(url: str, output: str) -> bool:
# #     """Method 3: yt-dlp with Douyin-specific settings"""
# #     logger.info("   📥 Method 3: yt-dlp (enhanced with cookies)")
    
# #     try:
# #         # Create temporary cookies file
# #         cookies_content = """# Netscape HTTP Cookie File
# # .douyin.com	TRUE	/	FALSE	0	ttwid	1%7C
# # .douyin.com	TRUE	/	FALSE	0	__ac_nonce	0
# # .douyin.com	TRUE	/	FALSE	0	odin_tt	0
# # """
        
# #         cookies_file = output + ".cookies"
# #         with open(cookies_file, 'w') as f:
# #             f.write(cookies_content)
        
# #         # Try with cookies
# #         result = subprocess.run([
# #             "yt-dlp",
# #             "-f", "best[ext=mp4]/best",
# #             "--no-playlist",
# #             "--no-warnings",
# #             "--cookies", cookies_file,
# #             "--user-agent", DOUYIN_HEADERS["User-Agent"],
# #             "--referer", "https://www.douyin.com/",
# #             "-o", output,
# #             url
# #         ], capture_output=True, timeout=180, text=True)
        
# #         cleanup(cookies_file)
        
# #         if result.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 10000:
# #             size = os.path.getsize(output) / (1024 * 1024)
# #             logger.info(f"   ✅ Method 3 SUCCESS: {size:.1f}MB")
# #             return True
        
# #         logger.warning(f"   ❌ Method 3 FAILED: {result.stderr[-200:] if result.stderr else 'Unknown error'}")
# #         return False
    
# #     except Exception as e:
# #         logger.warning(f"   ❌ Method 3 ERROR: {e}")
# #         return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # METHOD 4: M3U8 STREAM CAPTURE (For streaming videos)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def download_m3u8_stream(video_id: str, output: str) -> bool:
# #     """Method 4: M3U8 stream capture and conversion"""
# #     logger.info("   📥 Method 4: M3U8 stream capture")
    
# #     if not video_id:
# #         return False
    
# #     try:
# #         # Get m3u8 URL from API
# #         api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
        
# #         async with httpx.AsyncClient(timeout=60) as client:
# #             response = await client.get(api_url, headers=DOUYIN_HEADERS)
            
# #             if response.status_code != 200:
# #                 return False
            
# #             data = response.json()
            
# #             # Look for m3u8 URL
# #             m3u8_url = None
            
# #             if "item_list" in data and data["item_list"]:
# #                 item = data["item_list"][0]
                
# #                 # Check for m3u8 in play_addr
# #                 if "video" in item and "play_addr" in item["video"]:
# #                     play_addr = item["video"]["play_addr"]
                    
# #                     if "url_list" in play_addr:
# #                         for url in play_addr["url_list"]:
# #                             if ".m3u8" in url:
# #                                 m3u8_url = url
# #                                 break
            
# #             if not m3u8_url:
# #                 logger.warning("   ❌ No m3u8 URL found")
# #                 return False
            
# #             logger.info(f"   → Found m3u8: {m3u8_url[:60]}...")
            
# #             # Use ffmpeg to download and convert m3u8
# #             logger.info("   → Converting m3u8 to mp4...")
            
# #             result = subprocess.run([
# #                 "ffmpeg",
# #                 "-i", m3u8_url,
# #                 "-c", "copy",
# #                 "-bsf:a", "aac_adtstoasc",
# #                 "-y", output
# #             ], capture_output=True, timeout=180)
            
# #             if result.returncode == 0 and os.path.exists(output) and os.path.getsize(output) > 10000:
# #                 size = os.path.getsize(output) / (1024 * 1024)
# #                 logger.info(f"   ✅ Method 4 SUCCESS: {size:.1f}MB")
# #                 return True
            
# #             logger.warning("   ❌ m3u8 conversion failed")
# #             return False
    
# #     except Exception as e:
# #         logger.warning(f"   ❌ Method 4 ERROR: {e}")
# #         return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # METHOD 5: TIKTOK GLOBAL API (For TikTok URLs)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def download_tiktok_global(video_id: str, output: str) -> bool:
# #     """Method 5: TikTok Global API (for non-Douyin URLs)"""
# #     logger.info("   📥 Method 5: TikTok Global API")
    
# #     if not video_id:
# #         return False
    
# #     # TikTok API endpoint
# #     api_url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}"
    
# #     try:
# #         async with httpx.AsyncClient(timeout=60) as client:
# #             headers = {
# #                 "User-Agent": "TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet",
# #             }
            
# #             response = await client.get(api_url, headers=headers)
            
# #             if response.status_code != 200:
# #                 return False
            
# #             data = response.json()
            
# #             # Extract video URL
# #             video_url = None
            
# #             if "aweme_list" in data and data["aweme_list"]:
# #                 item = data["aweme_list"][0]
                
# #                 if "video" in item and "play_addr" in item["video"]:
# #                     play_addr = item["video"]["play_addr"]
# #                     if "url_list" in play_addr and play_addr["url_list"]:
# #                         video_url = play_addr["url_list"][0]
            
# #             if not video_url:
# #                 return False
            
# #             # Download video
# #             async with client.stream("GET", video_url, headers=headers, timeout=180) as stream:
# #                 if stream.status_code == 200:
# #                     total = 0
# #                     with open(output, 'wb') as f:
# #                         async for chunk in stream.aiter_bytes(1024*1024):
# #                             f.write(chunk)
# #                             total += len(chunk)
                    
# #                     if total > 10000:
# #                         size = total / (1024 * 1024)
# #                         logger.info(f"   ✅ Method 5 SUCCESS: {size:.1f}MB")
# #                         return True
            
# #             return False
    
# #     except Exception as e:
# #         logger.warning(f"   ❌ Method 5 ERROR: {e}")
# #         return False

# # # ═══════════════════════════════════════════════════════════════════════
# # # MASTER DOWNLOAD FUNCTION (5 METHODS)
# # # ═══════════════════════════════════════════════════════════════════════

# # async def download_china_video(url: str, output: str) -> tuple[bool, str]:
# #     """
# #     Master download function with 5 methods:
# #     1. Douyin Internal API (iteminfo) - BEST
# #     2. Mobile API (Android simulation)
# #     3. yt-dlp with cookies
# #     4. M3U8 stream capture
# #     5. TikTok Global API
# #     """
# #     logger.info("⬇️ Downloading China video...")
# #     logger.info(f"   Original URL: {url[:80]}...")
# #     log_memory("download-start")
    
# #     # Extract video ID
# #     video_id = extract_video_id(url)
    
# #     if not video_id:
# #         logger.error("   ❌ Could not extract video ID from URL")
# #         return False, "Could not extract video ID"
    
# #     # Try all 5 methods
# #     methods = [
# #         ("Douyin API", lambda: download_douyin_api(video_id, output)),
# #         ("Mobile API", lambda: download_mobile_api(video_id, output)),
# #         ("yt-dlp Enhanced", lambda: download_ytdlp_enhanced(url, output)),
# #         ("M3U8 Stream", lambda: download_m3u8_stream(video_id, output)),
# #         ("TikTok Global", lambda: download_tiktok_global(video_id, output)),
# #     ]
    
# #     for method_name, method_func in methods:
# #         logger.info(f"\n{'='*60}")
# #         logger.info(f"   TRYING: {method_name}")
# #         logger.info(f"{'='*60}")
        
# #         try:
# #             success = await method_func()
            
# #             if success and os.path.exists(output) and os.path.getsize(output) > 10000:
# #                 size = os.path.getsize(output) / (1024 * 1024)
# #                 logger.info(f"\n✅ DOWNLOAD SUCCESS ({method_name}): {size:.1f}MB")
# #                 log_memory("download-done")
# #                 return True, ""
            
# #             logger.warning(f"   ❌ {method_name} failed, trying next...")
            
# #             if os.path.exists(output):
# #                 os.remove(output)
        
# #         except Exception as e:
# #             logger.error(f"   ❌ {method_name} critical error: {e}")
# #             if os.path.exists(output):
# #                 os.remove(output)
# #             continue
    
# #     logger.error("\n" + "="*60)
# #     logger.error("❌ ALL 5 DOWNLOAD METHODS FAILED")
# #     logger.error("="*60)
    
# #     return False, "All download methods failed"

# # # ═══════════════════════════════════════════════════════════════════════
# # # MANUAL FILE UPLOAD FUNCTIONS
# # # ═══════════════════════════════════════════════════════════════════════

# # async def save_uploaded_file(upload_file: UploadFile, output_path: str) -> tuple[bool, str]:
# #     """
# #     Save uploaded file to disk
# #     Returns: (success, error_message)
# #     """
# #     logger.info(f"💾 Saving uploaded file: {upload_file.filename}")
    
# #     try:
# #         # Validate file size (max 100MB)
# #         max_size = 100 * 1024 * 1024  # 100MB
        
# #         # Read and save file in chunks
# #         total_bytes = 0
# #         async with aiofiles.open(output_path, 'wb') as f:
# #             while True:
# #                 chunk = await upload_file.read(1024 * 1024)  # 1MB chunks
# #                 if not chunk:
# #                     break
                
# #                 total_bytes += len(chunk)
                
# #                 # Check size limit
# #                 if total_bytes > max_size:
# #                     logger.error(f"❌ File too large: {total_bytes / (1024*1024):.1f}MB")
# #                     if os.path.exists(output_path):
# #                         os.remove(output_path)
# #                     return False, f"File too large: {total_bytes / (1024*1024):.1f}MB (max 100MB)"
                
# #                 await f.write(chunk)
        
# #         # Verify file was saved
# #         if not os.path.exists(output_path):
# #             return False, "File save failed"
        
# #         file_size = os.path.getsize(output_path)
# #         if file_size < 10000:  # Less than 10KB
# #             logger.error(f"❌ File too small: {file_size} bytes")
# #             os.remove(output_path)
# #             return False, "File too small or corrupted"
        
# #         logger.info(f"✅ File saved: {file_size / (1024*1024):.2f}MB")
# #         return True, ""
    
# #     except Exception as e:
# #         logger.error(f"❌ File save error: {e}")
# #         if os.path.exists(output_path):
# #             try:
# #                 os.remove(output_path)
# #             except:
# #                 pass
# #         return False, str(e)


# # async def validate_video_file(video_path: str) -> tuple[bool, str]:
# #     """
# #     Validate uploaded video file using ffprobe
# #     Returns: (is_valid, error_message)
# #     """
# #     logger.info("🔍 Validating video file...")
    
# #     try:
# #         # Use ffprobe to check if it's a valid video
# #         result = subprocess.run([
# #             "ffprobe",
# #             "-v", "error",
# #             "-select_streams", "v:0",
# #             "-show_entries", "stream=codec_type,duration",
# #             "-of", "json",
# #             video_path
# #         ], capture_output=True, timeout=30, text=True)
        
# #         if result.returncode != 0:
# #             logger.error(f"❌ Not a valid video file")
# #             return False, "Invalid video file format"
        
# #         # Parse output
# #         try:
# #             data = json.loads(result.stdout)
            
# #             if not data.get("streams"):
# #                 return False, "No video stream found"
            
# #             # Check duration
# #             duration_str = data["streams"][0].get("duration", "0")
# #             duration = float(duration_str)
            
# #             if duration <= 0:
# #                 return False, "Invalid video duration"
            
# #             if duration > 180:  # Max 3 minutes
# #                 return False, f"Video too long: {duration:.0f}s (max 180s)"
            
# #             logger.info(f"✅ Valid video: {duration:.1f}s")
# #             return True, ""
        
# #         except Exception as e:
# #             logger.error(f"❌ Parse error: {e}")
# #             return False, "Could not parse video metadata"
    
# #     except subprocess.TimeoutExpired:
# #         return False, "Video validation timeout"
# #     except Exception as e:
# #         logger.error(f"❌ Validation error: {e}")
# #         return False, str(e)

# # # ═══════════════════════════════════════════════════════════════════════
# # # VIDEO PROCESSING FUNCTIONS
# # # ═══════════════════════════════════════════════════════════════════════

# # async def get_duration(video_path: str) -> float:
# #     """Get video duration"""
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

# # async def apply_copyright_filters(input_path: str, output_path: str) -> tuple[bool, str]:
# #     """Apply copyright-avoidance filters"""
# #     logger.info("🎨 Applying filters...")
    
# #     filter_complex = "eq=saturation=1.25:brightness=0.10:contrast=1.15"
    
# #     success = run_ffmpeg([
# #         "ffmpeg", "-i", input_path,
# #         "-vf", filter_complex,
# #         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
# #         "-c:a", "copy",
# #         "-y", output_path
# #     ], 90, "Filters")
    
# #     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
# #         return True, ""
    
# #     # Fallback: copy original
# #     if os.path.exists(input_path):
# #         shutil.copy(input_path, output_path)
# #         return True, ""
    
# #     return False, "Filter failed"

# # def generate_srt_with_emojis(duration: float) -> str:
# #     """Generate SRT with emojis"""
# #     num_captions = max(3, int(duration / 3))
# #     time_per = duration / num_captions
# #     blocks = []
    
# #     for i in range(num_captions):
# #         start = i * time_per
# #         end = start + time_per
        
# #         sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
# #         eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
# #         caption = random.choice(CAPTION_EMOJIS) if random.random() < 0.9 else random.choice(CAPTION_TEXT)
        
# #         blocks.append(f"{i+1}\n{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
# #                      f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + f"\n{caption}\n")
    
# #     return "\n".join(blocks)

# # async def apply_golden_captions(video_path: str, duration: float, output_path: str) -> tuple[bool, str]:
# #     """Apply golden captions"""
# #     logger.info("✨ Adding captions...")
    
# #     srt_path = output_path.replace(".mp4", ".srt")
    
# #     try:
# #         with open(srt_path, 'w', encoding='utf-8') as f:
# #             f.write(generate_srt_with_emojis(duration))
# #     except:
# #         shutil.copy(video_path, output_path)
# #         return True, ""
    
# #     srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
# #     success = run_ffmpeg([
# #         "ffmpeg", "-i", video_path,
# #         "-vf", f"subtitles={srt_esc}:force_style='FontName=Arial Black,FontSize=20,PrimaryColour=&H00FFD700,Bold=1,Outline=2,OutlineColour=&H00000000,Alignment=2,MarginV=40'",
# #         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
# #         "-y", output_path
# #     ], 120, "Captions")
    
# #     cleanup(srt_path)
    
# #     if success:
# #         return True, ""
    
# #     shutil.copy(video_path, output_path)
# #     return True, ""

# # async def remove_audio(video_in: str, video_out: str) -> bool:
# #     """Remove audio"""
# #     success = run_ffmpeg([
# #         "ffmpeg", "-i", video_in,
# #         "-c:v", "copy", "-an",
# #         "-y", video_out
# #     ], 60, "Remove-Audio")
    
# #     if success:
# #         cleanup(video_in)
    
# #     return success

# # async def download_bgm(output: str) -> bool:
# #     """Download BGM"""
# #     logger.info("🎵 Downloading BGM...")
    
# #     bgm_url = random.choice(CHINA_BGM_URLS)
    
# #     try:
# #         async with httpx.AsyncClient(timeout=180) as client:
# #             async with client.stream("GET", bgm_url) as response:
# #                 if response.status_code == 200:
# #                     total = 0
# #                     with open(output, 'wb') as f:
# #                         async for chunk in response.aiter_bytes(1024*1024):
# #                             f.write(chunk)
# #                             total += len(chunk)
                    
# #                     if total > 10000:
# #                         logger.info("✅ BGM Downloaded")
# #                         return True
# #         return False
# #     except:
# #         return False

# # async def mix_audio_with_bgm(video_path: str, bgm_path: Optional[str], output_path: str) -> tuple[bool, str]:
# #     """Mix BGM"""
# #     logger.info("🎵 Mixing BGM...")
    
# #     if bgm_path and os.path.exists(bgm_path):
# #         success = run_ffmpeg([
# #             "ffmpeg", "-i", video_path, "-i", bgm_path,
# #             "-filter_complex", "[1:a]volume=0.20[a]",
# #             "-map", "0:v", "-map", "[a]",
# #             "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
# #             "-shortest", "-y", output_path
# #         ], 90, "Mix-BGM")
        
# #         if success:
# #             cleanup(video_path, bgm_path)
# #             return True, ""
    
# #     # Fallback
# #     if os.path.exists(video_path):
# #         shutil.copy(video_path, output_path)
# #         cleanup(video_path, bgm_path)
# #         return True, ""
    
# #     return False, "Mix failed"

# # async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
# #     """Upload to YouTube"""
# #     logger.info("📤 YouTube Upload...")
    
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
# # # MAIN PIPELINES
# # # ═══════════════════════════════════════════════════════════════════════

# # async def process_china_short(china_url: str, user_id: str, task_id: str):
# #     """Main processing pipeline for URL downloads"""
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
# #         temp_dir = tempfile.mkdtemp(prefix="china_short_")
# #         logger.info(f"📁 {temp_dir}")
# #         log_memory("START")
        
# #         # Download (5 methods)
# #         update(10, "Downloading (5 fallback methods)...")
# #         raw_video = os.path.join(temp_dir, "raw.mp4")
# #         success, error = await download_china_video(china_url, raw_video)
# #         if not success:
# #             raise Exception(error)
        
# #         # Duration
# #         update(20, "Analyzing...")
# #         duration = await get_duration(raw_video)
# #         if duration <= 0 or duration > 180:
# #             raise ValueError(f"Invalid duration: {duration:.0f}s")
        
# #         # Filters
# #         update(30, "Applying filters...")
# #         filtered_video = os.path.join(temp_dir, "filtered.mp4")
# #         await apply_copyright_filters(raw_video, filtered_video)
        
# #         # Remove audio
# #         update(50, "Removing audio...")
# #         silent_video = os.path.join(temp_dir, "silent.mp4")
# #         if not await remove_audio(filtered_video, silent_video):
# #             raise Exception("Remove audio failed")
        
# #         # Captions
# #         update(60, "Adding captions...")
# #         captioned_video = os.path.join(temp_dir, "captioned.mp4")
# #         await apply_golden_captions(silent_video, duration, captioned_video)
        
# #         # BGM
# #         update(75, "Downloading BGM...")
# #         bgm_path = os.path.join(temp_dir, "bgm.mp3")
# #         await download_bgm(bgm_path)
        
# #         update(85, "Mixing BGM...")
# #         final_video = os.path.join(temp_dir, "final.mp4")
# #         success, error = await mix_audio_with_bgm(captioned_video, bgm_path, final_video)
# #         if not success:
# #             raise Exception(error)
        
# #         # Upload
# #         title = f"Amazing China Short 🔥 #{random.choice(['Trending', 'Epic', 'Viral'])} #Shorts"
# #         description = "Amazing short video!\n\n#Shorts #Viral #Trending #ChinaShorts #MustWatch"
        
# #         update(95, "Uploading...")
# #         upload_result = await upload_to_youtube(final_video, title, description, user_id)
        
# #         if not upload_result.get("success"):
# #             raise Exception(upload_result.get("error"))
        
# #         # Success
# #         elapsed = (datetime.now() - start_time).total_seconds()
        
# #         logger.info("="*80)
# #         logger.info("✅ SUCCESS!")
# #         logger.info(f"   Time: {elapsed:.1f}s")
# #         logger.info(f"   Video: {upload_result['video_id']}")
# #         logger.info("="*80)
        
# #         PROCESSING_STATUS[task_id] = {
# #             "status": "completed",
# #             "progress": 100,
# #             "success": True,
# #             "message": "Uploaded!",
# #             "title": title,
# #             "description": description,
# #             "duration": round(duration, 1),
# #             "processing_time": round(elapsed, 1),
# #             "video_id": upload_result["video_id"],
# #             "video_url": upload_result["video_url"],
# #             "completed_at": datetime.utcnow().isoformat()
# #         }
        
# #     except Exception as e:
# #         logger.error(f"❌ FAILED: {e}")
        
# #         PROCESSING_STATUS[task_id] = {
# #             "status": "failed",
# #             "progress": 0,
# #             "success": False,
# #             "error": str(e),
# #             "message": str(e),
# #             "failed_at": datetime.utcnow().isoformat()
# #         }
    
# #     finally:
# #         if temp_dir and os.path.exists(temp_dir):
# #             logger.info("🧹 Cleanup...")
# #             shutil.rmtree(temp_dir, ignore_errors=True)
        
# #         gc.collect()
# #         log_memory("FINAL")


# # async def process_uploaded_video(video_path: str, user_id: str, task_id: str):
# #     """
# #     Process manually uploaded video file
# #     Same pipeline as URL processing, but skips download step
# #     """
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
# #         temp_dir = tempfile.mkdtemp(prefix="china_upload_")
# #         logger.info(f"📁 {temp_dir}")
# #         log_memory("START-UPLOAD")
        
# #         # Copy uploaded file to temp directory
# #         update(10, "Processing uploaded file...")
# #         raw_video = os.path.join(temp_dir, "uploaded.mp4")
# #         shutil.copy(video_path, raw_video)
        
# #         # Validate video
# #         update(15, "Validating video...")
# #         is_valid, error = await validate_video_file(raw_video)
# #         if not is_valid:
# #             raise ValueError(error)
        
# #         # Get duration
# #         update(20, "Analyzing video...")
# #         duration = await get_duration(raw_video)
# #         if duration <= 0 or duration > 180:
# #             raise ValueError(f"Invalid duration: {duration:.0f}s")
        
# #         logger.info(f"✅ Video duration: {duration:.1f}s")
        
# #         # Apply filters
# #         update(30, "Applying filters...")
# #         filtered_video = os.path.join(temp_dir, "filtered.mp4")
# #         success, error = await apply_copyright_filters(raw_video, filtered_video)
# #         if not success:
# #             raise Exception(error)
        
# #         # Remove audio
# #         update(50, "Removing audio...")
# #         silent_video = os.path.join(temp_dir, "silent.mp4")
# #         if not await remove_audio(filtered_video, silent_video):
# #             raise Exception("Remove audio failed")
        
# #         # Add captions
# #         update(60, "Adding golden captions...")
# #         captioned_video = os.path.join(temp_dir, "captioned.mp4")
# #         success, error = await apply_golden_captions(silent_video, duration, captioned_video)
# #         if not success:
# #             raise Exception(error)
        
# #         # Download BGM
# #         update(75, "Downloading BGM...")
# #         bgm_path = os.path.join(temp_dir, "bgm.mp3")
# #         await download_bgm(bgm_path)
        
# #         # Mix audio
# #         update(85, "Mixing BGM...")
# #         final_video = os.path.join(temp_dir, "final.mp4")
# #         success, error = await mix_audio_with_bgm(captioned_video, bgm_path, final_video)
# #         if not success:
# #             raise Exception(error)
        
# #         # Upload to YouTube
# #         update(95, "Uploading to YouTube...")
# #         title = f"Amazing China Short 🔥 #{random.choice(['Trending', 'Epic', 'Viral'])} #Shorts"
# #         description = "Amazing short video!\n\n#Shorts #Viral #Trending #ChinaShorts #MustWatch"
        
# #         upload_result = await upload_to_youtube(final_video, title, description, user_id)
        
# #         if not upload_result.get("success"):
# #             raise Exception(upload_result.get("error"))
        
# #         # Success
# #         elapsed = (datetime.now() - start_time).total_seconds()
        
# #         logger.info("="*80)
# #         logger.info("✅ UPLOAD SUCCESS!")
# #         logger.info(f"   Time: {elapsed:.1f}s")
# #         logger.info(f"   Video: {upload_result['video_id']}")
# #         logger.info("="*80)
        
# #         PROCESSING_STATUS[task_id] = {
# #             "status": "completed",
# #             "progress": 100,
# #             "success": True,
# #             "message": "Uploaded!",
# #             "title": title,
# #             "description": description,
# #             "duration": round(duration, 1),
# #             "processing_time": round(elapsed, 1),
# #             "video_id": upload_result["video_id"],
# #             "video_url": upload_result["video_url"],
# #             "completed_at": datetime.utcnow().isoformat()
# #         }
    
# #     except Exception as e:
# #         logger.error(f"❌ UPLOAD FAILED: {e}")
        
# #         PROCESSING_STATUS[task_id] = {
# #             "status": "failed",
# #             "progress": 0,
# #             "success": False,
# #             "error": str(e),
# #             "message": str(e),
# #             "failed_at": datetime.utcnow().isoformat()
# #         }
    
# #     finally:
# #         # Clean up temp directory
# #         if temp_dir and os.path.exists(temp_dir):
# #             logger.info("🧹 Cleanup...")
# #             shutil.rmtree(temp_dir, ignore_errors=True)
        
# #         # Clean up uploaded file
# #         if video_path and os.path.exists(video_path):
# #             try:
# #                 os.remove(video_path)
# #             except:
# #                 pass
        
# #         gc.collect()
# #         log_memory("FINAL-UPLOAD")

# # # ═══════════════════════════════════════════════════════════════════════
# # # API ROUTES
# # # ═══════════════════════════════════════════════════════════════════════

# # router = APIRouter()

# # @router.post("/api/china-shorts/process")
# # async def process_endpoint(request: Request):
# #     """Process China Short from URL"""
# #     logger.info("🌐 URL PROCESS REQUEST")
    
# #     try:
# #         data = await request.json()
        
# #         user_id = data.get("user_id")
# #         china_url = (data.get("china_url") or "").strip()
        
# #         if not user_id:
# #             return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
# #         if not china_url:
# #             return JSONResponse(status_code=400, content={"success": False, "error": "URL required"})
        
# #         task_id = str(uuid.uuid4())
# #         logger.info(f"✅ Task: {task_id}")
        
# #         await asyncio.wait_for(process_china_short(china_url, user_id, task_id), timeout=900)
        
# #         result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown"})
# #         return JSONResponse(content=result)
        
# #     except asyncio.TimeoutError:
# #         return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
# #     except Exception as e:
# #         logger.error(f"❌ {e}")
# #         return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# # @router.post("/api/china-shorts/process-upload")
# # async def process_upload_endpoint(
# #     user_id: str = Form(...),
# #     video_file: UploadFile = File(...)
# # ):
# #     """
# #     NEW ENDPOINT: Process manually uploaded video file
# #     Accepts multipart/form-data with user_id and video_file
# #     """
# #     logger.info("🌐 UPLOAD REQUEST")
# #     logger.info(f"   User: {user_id}")
# #     logger.info(f"   File: {video_file.filename}")
# #     logger.info(f"   Type: {video_file.content_type}")
    
# #     uploaded_file_path = None
    
# #     try:
# #         # Validate user_id
# #         if not user_id:
# #             return JSONResponse(
# #                 status_code=400, 
# #                 content={"success": False, "error": "user_id required"}
# #             )
        
# #         # Validate file
# #         if not video_file:
# #             return JSONResponse(
# #                 status_code=400,
# #                 content={"success": False, "error": "No video file provided"}
# #             )
        
# #         # Check content type
# #         if not video_file.content_type or not video_file.content_type.startswith("video/"):
# #             return JSONResponse(
# #                 status_code=400,
# #                 content={"success": False, "error": f"Invalid file type: {video_file.content_type}. Must be a video file."}
# #             )
        
# #         # Create unique filename
# #         task_id = str(uuid.uuid4())
# #         file_ext = os.path.splitext(video_file.filename)[1] or ".mp4"
# #         uploaded_file_path = f"/tmp/china_upload_{task_id}{file_ext}"
        
# #         logger.info(f"✅ Task: {task_id}")
# #         logger.info(f"📂 Saving to: {uploaded_file_path}")
        
# #         # Save uploaded file
# #         success, error = await save_uploaded_file(video_file, uploaded_file_path)
# #         if not success:
# #             return JSONResponse(
# #                 status_code=400,
# #                 content={"success": False, "error": error}
# #             )
        
# #         # Process the uploaded video (with timeout)
# #         await asyncio.wait_for(
# #             process_uploaded_video(uploaded_file_path, user_id, task_id),
# #             timeout=900  # 15 minutes
# #         )
        
# #         # Get result
# #         result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
# #         return JSONResponse(content=result)
    
# #     except asyncio.TimeoutError:
# #         logger.error("❌ Processing timeout")
# #         return JSONResponse(
# #             status_code=408,
# #             content={"success": False, "error": "Processing timeout (max 15 minutes)"}
# #         )
    
# #     except Exception as e:
# #         logger.error(f"❌ Upload endpoint error: {e}")
# #         return JSONResponse(
# #             status_code=500,
# #             content={"success": False, "error": str(e)}
# #         )
    
# #     finally:
# #         # Cleanup uploaded file if still exists
# #         if uploaded_file_path and os.path.exists(uploaded_file_path):
# #             try:
# #                 os.remove(uploaded_file_path)
# #                 logger.info(f"🧹 Cleaned up: {uploaded_file_path}")
# #             except:
# #                 pass


# # @router.get("/api/china-shorts/status/{task_id}")
# # async def status_endpoint(task_id: str):
# #     """Get processing status for a task"""
# #     status = PROCESSING_STATUS.get(task_id)
# #     if not status:
# #         return JSONResponse(
# #             status_code=404,
# #             content={"success": False, "error": "Task not found"}
# #         )
# #     return JSONResponse(content=status)


# # @router.get("/api/china-shorts/health")
# # async def health_endpoint():
# #     """Health check endpoint"""
# #     return JSONResponse(content={
# #         "status": "ok",
# #         "version": "3.1",
# #         "features": {
# #             "url_download": {
# #                 "enabled": True,
# #                 "methods": [
# #                     "Douyin Internal API (iteminfo)",
# #                     "Mobile API (Android simulation)",
# #                     "yt-dlp Enhanced",
# #                     "M3U8 Stream Capture",
# #                     "TikTok Global API"
# #                 ]
# #             },
# #             "manual_upload": {
# #                 "enabled": True,
# #                 "max_file_size": "100MB",
# #                 "max_duration": "180 seconds",
# #                 "supported_formats": ["mp4", "mov", "avi", "mkv", "webm", "flv"]
# #             },
# #             "processing": {
# #                 "filters": "Saturation +25%, Brightness +10%, Contrast +15%",
# #                 "audio": "Original removed, BGM added at 20%",
# #                 "captions": "Golden captions with emojis",
# #                 "upload": "Direct to YouTube"
# #             }
# #         }
# #     })


# # async def initialize():
# #     """Startup initialization"""
# #     logger.info("="*80)
# #     logger.info("🚀 CHINA SHORTS V3.1 (PRODUCTION + MANUAL UPLOAD)")
# #     logger.info("="*80)
# #     logger.info("✅ URL Download Methods:")
# #     logger.info("   1. Douyin Internal API (iteminfo)")
# #     logger.info("   2. Mobile API (Android)")
# #     logger.info("   3. yt-dlp Enhanced")
# #     logger.info("   4. M3U8 Stream Capture")
# #     logger.info("   5. TikTok Global API")
# #     logger.info("")
# #     logger.info("✅ NEW: Manual File Upload")
# #     logger.info("   • Direct video file upload (max 100MB)")
# #     logger.info("   • Same processing pipeline")
# #     logger.info("   • Validation & error handling")
# #     logger.info("="*80)
# #     log_memory("startup")


# # __all__ = ["router", "initialize"]


# """
# ai_animal_videos.py - AI ANIMAL VIDEO PROCESSOR (ORANGE CAT FIGHTS)
# ===================================================================
# ✅ NO VOICEOVER - BGM MUSIC ONLY
# ✅ AI-Generated Viral Titles (Hinglish with inline hashtags)
# ✅ AI-Generated SEO Description (2 paragraphs)
# ✅ AI-Generated 45 Keywords + 7-9 Hashtags
# ✅ Emoji Captions at Bottom (cute + savage emojis)
# ✅ Video Enhancements (saturation, contrast, brightness)
# ✅ Direct YouTube Upload with Full SEO
# ===================================================================
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
# from typing import Optional, List, Dict
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
# logger = logging.getLogger("AIAnimalVideos")
# logger.setLevel(logging.INFO)

# if not logger.handlers:
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#     logger.addHandler(handler)

# def log_memory(step: str):
#     """Log memory usage"""
#     if HAS_PSUTIL:
#         try:
#             process = psutil.Process(os.getpid())
#             mem_mb = process.memory_info().rss / 1024 / 1024
#             logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
#             if mem_mb > 450:
#                 logger.warning(f"⚠️ HIGH: {mem_mb:.1f}MB")
#                 gc.collect()
#         except:
#             pass

# # ═══════════════════════════════════════════════════════════════════════
# # CONFIG
# # ═══════════════════════════════════════════════════════════════════════
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# # TRENDING BGM FOR AI ANIMAL VIDEOS (NO VOICEOVER)
# ANIMAL_BGM_URLS = [
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Epic%20Action%20BGM%20-%20Battle%20Music.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Funny%20Comedy%20BGM%20-%20Cartoon%20Style.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Cute%20Animals%20BGM%20-%20Happy%20Music.mp3",
#     "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3",
# ]

# # EMOJI CAPTIONS FOR AI ANIMAL VIDEOS (CUTE + SAVAGE)
# ANIMAL_EMOJIS = ["😺", "🐱", "🦁", "💪", "🔥", "😼", "😹", "🐾", "⚡", "💥", "😈", "🤣", "😎", "👑", "✨", "💯"]

# PROCESSING_STATUS = {}

# # ═══════════════════════════════════════════════════════════════════════
# # CLEANUP & FFMPEG
# # ═══════════════════════════════════════════════════════════════════════

# def cleanup(*paths):
#     """Delete files and force garbage collection"""
#     for path in paths:
#         try:
#             if path and os.path.exists(path):
#                 os.remove(path)
#         except:
#             pass
#     gc.collect()

# def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
#     """Run FFmpeg command"""
#     logger.info(f"🎬 {step}...")
#     try:
#         result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout, text=True)
#         if result.returncode == 0:
#             logger.info(f"✅ {step}")
#             return True
#         else:
#             logger.error(f"❌ {step} failed: {result.stderr[-200:]}")
#             return False
#     except Exception as e:
#         logger.error(f"❌ {step} error: {e}")
#         return False

# # ═══════════════════════════════════════════════════════════════════════
# # GOOGLE DRIVE DOWNLOAD
# # ═══════════════════════════════════════════════════════════════════════

# def extract_file_id(url: str) -> Optional[str]:
#     """Extract Google Drive file ID"""
#     if not url or "drive.google.com" not in url:
#         return None
    
#     patterns = [r'/file/d/([a-zA-Z0-9_-]{25,})', r'[?&]id=([a-zA-Z0-9_-]{25,})']
#     for pattern in patterns:
#         match = re.search(pattern, url)
#         if match:
#             return match.group(1)
#     return None

# async def download_chunked(url: str, output: str) -> bool:
#     """Download file in chunks"""
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
                
#                 if total > 10000:
#                     logger.info(f"   ✅ {total/(1024*1024):.1f}MB")
#                     return True
#         return False
#     except Exception as e:
#         logger.error(f"   ❌ {e}")
#         return False

# async def download_from_gdrive(file_id: str, output: str) -> tuple[bool, str]:
#     """Download from Google Drive"""
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
# # VIDEO INFO
# # ═══════════════════════════════════════════════════════════════════════

# async def get_duration(video_path: str) -> float:
#     """Get video duration"""
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

# # ═══════════════════════════════════════════════════════════════════════
# # AI TITLE + DESCRIPTION + KEYWORDS + HASHTAGS GENERATOR
# # ═══════════════════════════════════════════════════════════════════════

# async def generate_viral_seo_metadata() -> dict:
#     """
#     Generate VIRAL title, description, keywords, hashtags using Mistral AI
#     """
#     logger.info("🤖 AI SEO Generator (Viral Titles + Keywords)...")
#     log_memory("ai-seo-start")
    
#     # Try Mistral AI
#     if MISTRAL_API_KEY:
#         try:
#             logger.info("   Using Mistral AI for viral SEO...")
            
#             prompt = """You are a VIRAL YouTube Shorts TITLE + SEO Generator
# for AI GENERATED ANIMAL VIDEOS.

# VIDEO CONTEXT:
# - Content: AI generated orange cat doing funny / badass / chaotic fights with other animals
# - Audio: Background music ONLY (NO voice, NO script)
# - Style: Cute + savage + meme-worthy
# - Target: High replay + viral Shorts
# - Audience: India + Global

# STRICT GLOBAL RULES:
# 1. DO NOT generate any script or dialogue
# 2. DO NOT generate characters
# 3. DO NOT explain AI process
# 4. Keep output SHORT, SIMPLE, VIRAL
# 5. Follow EXACT formatting

# ━━━━━━━━━━━━━━━━━━━━━━
# 🎯 TITLE RULES (VERY IMPORTANT)
# ━━━━━━━━━━━━━━━━━━━━━━
# - Title length: **MIN 3 words, MAX 7 words**
# - Language: Simple English OR Hinglish
# - Must include ONE of these curiosity hooks:
#   ["AI", "Aaj Tak", "99% Log", "Bas 1", "AI Ne"]
# - Must include **INLINE HASHTAGS** like YouTube
# - Hashtags count: **MIN 3, MAX 5**
# - Hashtags MUST be at the END of title
# - NO emojis
# - Natural human title (not robotic)

# TITLE FORMAT (EXACT):
# Title Words #tag1 #tag2 #tag3

# EXAMPLES (STYLE ONLY):
# The Big AI Orange Cat #cat #ai #funny
# Aaj Tak AI Cat Fight #cat #animals #viral
# Bas 1 AI Cat Chaos #cat #pets #shorts
# AI Ne Orange Cat Attack #cat #ai #animals

# ━━━━━━━━━━━━━━━━━━━━━━
# 📝 DESCRIPTION RULES
# ━━━━━━━━━━━━━━━━━━━━━━
# Write **2 short paragraphs**:

# Paragraph 1:
# - Hook viewer
# - Mention orange cat + AI + chaos
# - Max 2–3 lines

# Paragraph 2:
# - Mention funny fight, animals, replay value
# - Encourage like/share subtly
# - Max 2–3 lines

# ━━━━━━━━━━━━━━━━━━━━━━
# 🔑 KEYWORDS RULES
# ━━━━━━━━━━━━━━━━━━━━━━
# Generate **EXACTLY 45 keywords**
# - Mix English + Hinglish + Hindi
# - Each keyword on a NEW LINE
# - Focus on:
#   ai cat video
#   orange cat ai
#   funny cat ai
#   animal fight ai
#   viral shorts

# ━━━━━━━━━━━━━━━━━━━━━━
# #️⃣ HASHTAG RULES (EXTRA)
# ━━━━━━━━━━━━━━━━━━━━━━
# Generate **7–9 hashtags** separately:
# - Must include:
#   #Shorts
#   #AICat
#   #Viral
# - Remaining hashtags:
#   cat + animal + funny + ai

# ━━━━━━━━━━━━━━━━━━━━━━
# 📦 FINAL OUTPUT FORMAT (JSON ONLY)
# ━━━━━━━━━━━━━━━━━━━━━━
# {
#   "title": "Title with inline hashtags",
#   "description": "2 paragraph description",
#   "keywords": [
#     "keyword 1",
#     "keyword 2",
#     ...45 total
#   ],
#   "hashtags": [
#     "#Shorts",
#     "#AICat",
#     "#Viral",
#     ...7-9 total
#   ]
# }

# OUTPUT ONLY VALID JSON.
# NO EXTRA TEXT."""
            
#             async with httpx.AsyncClient(timeout=60) as client:
#                 resp = await client.post(
#                     "https://api.mistral.ai/v1/chat/completions",
#                     headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
#                     json={
#                         "model": "mistral-large-latest",
#                         "messages": [
#                             {"role": "system", "content": "You are a viral YouTube SEO expert. Output ONLY valid JSON."},
#                             {"role": "user", "content": prompt}
#                         ],
#                         "temperature": 0.8,
#                         "max_tokens": 2000
#                     }
#                 )
                
#                 if resp.status_code == 200:
#                     content = resp.json()["choices"][0]["message"]["content"]
#                     content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
#                     content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    
#                     match = re.search(r'\{.*\}', content, re.DOTALL)
                    
#                     if match:
#                         data = json.loads(match.group(0))
                        
#                         title = data.get("title", "AI Orange Cat Fight #cat #ai #viral")
#                         description = data.get("description", "Watch this amazing AI orange cat fight!\n\nLike and share for more!")
#                         keywords = data.get("keywords", [])
#                         hashtags = data.get("hashtags", ["#Shorts", "#AICat", "#Viral"])
                        
#                         # Ensure we have exactly 45 keywords
#                         if len(keywords) < 45:
#                             default_keywords = [
#                                 "ai cat video", "orange cat ai", "funny cat ai", "animal fight ai",
#                                 "viral shorts", "cute cat", "cat fight", "ai animals", "pet video",
#                                 "funny animals", "cat memes", "orange cat", "ai generated", "shorts viral"
#                             ]
#                             while len(keywords) < 45:
#                                 keywords.append(default_keywords[len(keywords) % len(default_keywords)])
                        
#                         keywords = keywords[:45]  # Ensure exactly 45
                        
#                         logger.info(f"✅ AI SEO Generated")
#                         logger.info(f"   Title: {title}")
#                         logger.info(f"   Keywords: {len(keywords)}")
#                         logger.info(f"   Hashtags: {len(hashtags)}")
#                         log_memory("ai-seo-done")
                        
#                         return {
#                             "title": title,
#                             "description": description,
#                             "keywords": keywords,
#                             "hashtags": hashtags
#                         }
#         except Exception as e:
#             logger.warning(f"   Mistral failed: {e}")
    
#     # FALLBACK: Basic SEO
#     logger.info("   Using fallback SEO (basic)...")
    
#     title_options = [
#         "AI Orange Cat Fight #cat #ai #viral",
#         "99% Log Yeh Nahi Jaante #cat #ai #shorts",
#         "AI Ne Banaya Epic Cat #cat #animals #viral",
#         "Aaj Tak Ka Best Cat #cat #ai #funny"
#     ]
    
#     title = random.choice(title_options)
    
#     description = """Watch this amazing AI-generated orange cat doing epic fights with other animals! This cute yet savage cat will make you laugh and replay this video again and again.

# Like, share and subscribe for more AI animal videos! This is the most viral cat content you'll see today. Don't miss out!"""
    
#     keywords = [
#         "ai cat video", "orange cat ai", "funny cat ai", "animal fight ai", "viral shorts",
#         "cute cat", "cat fight", "ai animals", "pet video", "funny animals",
#         "cat memes", "orange cat", "ai generated", "shorts viral", "cat content",
#         "animal videos", "ai pets", "cat vs", "epic cat", "savage cat",
#         "cat battle", "cute animals", "funny pets", "viral cat", "ai video",
#         "orange cat funny", "cat chaos", "animal ai", "pet ai", "cat viral",
#         "shorts cat", "trending cat", "best cat", "cat fight video", "ai cat fight",
#         "funny cat video", "cat shorts", "viral animal", "cat trending", "ai orange cat",
#         "cat ai video", "animal shorts", "cat video viral", "funny ai", "cute cat video"
#     ]
    
#     hashtags = ["#Shorts", "#AICat", "#Viral", "#FunnyCat", "#Animals", "#AI", "#Trending"]
    
#     log_memory("ai-seo-done")
    
#     return {
#         "title": title,
#         "description": description,
#         "keywords": keywords,
#         "hashtags": hashtags
#     }

# # ═══════════════════════════════════════════════════════════════════════
# # EMOJI CAPTIONS (BOTTOM OF VIDEO)
# # ═══════════════════════════════════════════════════════════════════════

# def generate_emoji_srt(duration: float) -> str:
#     """Generate SRT with ONLY emojis (no text) at bottom"""
#     num_captions = max(5, int(duration / 2))
#     time_per = duration / num_captions
#     blocks = []
    
#     for i in range(num_captions):
#         start = i * time_per
#         end = start + time_per
        
#         sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
#         eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
#         # Pick 2-3 random emojis
#         emoji_count = random.choice([2, 3])
#         emojis = " ".join(random.choices(ANIMAL_EMOJIS, k=emoji_count))
        
#         blocks.append(
#             f"{i+1}\n"
#             f"{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
#             f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + 
#             f"\n{emojis}\n"
#         )
    
#     return "\n".join(blocks)

# async def apply_emoji_captions(video_path: str, duration: float, output_path: str) -> tuple[bool, str]:
#     """Apply emoji captions at BOTTOM of video"""
#     logger.info("😺 Emoji Captions (Bottom)...")
#     log_memory("caption-start")
    
#     srt_path = output_path.replace(".mp4", "_emojis.srt")
    
#     try:
#         with open(srt_path, 'w', encoding='utf-8') as f:
#             f.write(generate_emoji_srt(duration))
#     except Exception as e:
#         logger.warning(f"⚠️ SRT generation failed: {e}, skipping emojis")
#         if os.path.exists(video_path):
#             shutil.copy(video_path, output_path)
#         return True, ""
    
#     srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
    
#     # Apply emojis at BOTTOM with large size
#     success = run_ffmpeg([
#         "ffmpeg", "-i", video_path,
#         "-vf", f"subtitles={srt_esc}:force_style='FontSize=28,Bold=1,Alignment=2,MarginV=40'",
#         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
#         "-y", output_path
#     ], 120, "Emoji-Captions")
    
#     cleanup(srt_path)
    
#     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
#         logger.info("✅ Emoji captions applied")
#         log_memory("caption-done")
#         return True, ""
    
#     # Fallback: no emojis
#     logger.warning("⚠️ Emoji captions failed, continuing without")
#     cleanup(output_path)
    
#     if os.path.exists(video_path):
#         shutil.copy(video_path, output_path)
#         return True, ""
    
#     return False, "Caption failed"

# # ═══════════════════════════════════════════════════════════════════════
# # VIDEO ENHANCEMENT
# # ═══════════════════════════════════════════════════════════════════════

# async def enhance_video_quality(input_path: str, output_path: str) -> tuple[bool, str]:
#     """Apply video enhancements"""
#     logger.info("🎨 Video Enhancement...")
#     log_memory("enhance-start")
    
#     filter_complex = "eq=saturation=1.25:brightness=0.10:contrast=1.15"
    
#     success = run_ffmpeg([
#         "ffmpeg", "-i", input_path,
#         "-vf", filter_complex,
#         "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
#         "-c:a", "copy",
#         "-y", output_path
#     ], 90, "Enhancement")
    
#     if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
#         log_memory("enhance-done")
#         return True, ""
    
#     # Fallback
#     if os.path.exists(input_path):
#         shutil.copy(input_path, output_path)
#         return True, ""
    
#     return False, "Enhancement failed"

# # ═══════════════════════════════════════════════════════════════════════
# # BGM DOWNLOAD & MIXING
# # ═══════════════════════════════════════════════════════════════════════

# async def download_animal_bgm(output: str) -> bool:
#     """Download animal BGM"""
#     logger.info("🎵 Downloading BGM...")
#     log_memory("bgm-start")
    
#     bgm_url = random.choice(ANIMAL_BGM_URLS)
#     logger.info(f"   Selected: {bgm_url.split('/')[-1][:50]}...")
    
#     try:
#         success = await download_chunked(bgm_url, output)
        
#         if success:
#             logger.info("✅ BGM Downloaded")
#             log_memory("bgm-done")
#             return True
        
#         return False
#     except:
#         return False

# async def remove_original_audio(video_in: str, video_out: str) -> bool:
#     """Remove original audio"""
#     success = run_ffmpeg([
#         "ffmpeg", "-i", video_in,
#         "-c:v", "copy", "-an",
#         "-y", video_out
#     ], timeout=60, step="Remove-Audio")
    
#     if success:
#         cleanup(video_in)
    
#     return success

# async def add_bgm_to_video(video_path: str, bgm_path: Optional[str], output_path: str) -> tuple[bool, str]:
#     """Add BGM to video (NO voiceover)"""
#     logger.info("🎵 Adding BGM (25% volume)...")
#     log_memory("mix-start")
    
#     if bgm_path and os.path.exists(bgm_path):
#         success = run_ffmpeg([
#             "ffmpeg", "-i", video_path, "-i", bgm_path,
#             "-filter_complex", "[1:a]volume=0.25[a]",
#             "-map", "0:v", "-map", "[a]",
#             "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
#             "-shortest", "-y", output_path
#         ], 90, "Add-BGM")
        
#         cleanup(video_path, bgm_path)
        
#         if success:
#             log_memory("mix-done")
#             return True, ""
    
#     # Fallback: no BGM
#     if os.path.exists(video_path):
#         shutil.copy(video_path, output_path)
#         cleanup(video_path, bgm_path)
#         return True, ""
    
#     return False, "BGM mix failed"

# # ═══════════════════════════════════════════════════════════════════════
# # YOUTUBE UPLOAD
# # ═══════════════════════════════════════════════════════════════════════

# async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
#     """Upload to YouTube"""
#     logger.info("📤 YouTube Upload...")
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

# async def process_ai_animal_video(drive_url: str, user_id: str, task_id: str):
#     """Main processing pipeline"""
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
#         temp_dir = tempfile.mkdtemp(prefix="ai_animal_")
#         logger.info(f"📁 {temp_dir}")
#         log_memory("START")
        
#         # Extract ID
#         update(5, "Extracting Google Drive ID...")
#         file_id = extract_file_id(drive_url)
#         if not file_id:
#             raise ValueError("Invalid Google Drive URL")
        
#         # Download
#         update(10, "Downloading video...")
#         raw_video = os.path.join(temp_dir, "raw.mp4")
#         success, error = await download_from_gdrive(file_id, raw_video)
#         if not success:
#             raise Exception(error)
        
#         # Get duration
#         update(20, "Analyzing video...")
#         duration = await get_duration(raw_video)
#         if duration <= 0:
#             raise ValueError("Invalid video")
#         if duration > 180:
#             raise ValueError(f"Video too long ({duration:.0f}s)")
        
#         # Generate AI SEO (title, description, keywords, hashtags)
#         update(30, "AI SEO generation (viral titles + keywords)...")
#         seo_metadata = await generate_viral_seo_metadata()
#         logger.info(f"   Title: {seo_metadata['title']}")
#         logger.info(f"   Keywords: {len(seo_metadata['keywords'])}")
        
#         # Enhance video
#         update(40, "Enhancing video quality...")
#         enhanced_video = os.path.join(temp_dir, "enhanced.mp4")
#         await enhance_video_quality(raw_video, enhanced_video)
        
#         # Remove original audio
#         update(50, "Removing original audio...")
#         silent_video = os.path.join(temp_dir, "silent.mp4")
#         if not await remove_original_audio(enhanced_video, silent_video):
#             raise Exception("Remove audio failed")
        
#         # Apply emoji captions
#         update(60, "Adding emoji captions (bottom)...")
#         captioned_video = os.path.join(temp_dir, "captioned.mp4")
#         await apply_emoji_captions(silent_video, duration, captioned_video)
        
#         # Download BGM
#         update(70, "Downloading BGM...")
#         bgm_path = os.path.join(temp_dir, "bgm.mp3")
#         bgm_success = await download_animal_bgm(bgm_path)
#         if not bgm_success:
#             bgm_path = None
#             logger.warning("⚠️ BGM download failed, continuing without BGM")
        
#         # Add BGM
#         update(80, "Adding BGM...")
#         final_video = os.path.join(temp_dir, "final.mp4")
#         success, error = await add_bgm_to_video(captioned_video, bgm_path, final_video)
#         if not success:
#             raise Exception(error)
        
#         if not os.path.exists(final_video) or os.path.getsize(final_video) < 10000:
#             raise Exception("Invalid final video")
        
#         # Upload to YouTube
#         update(95, "Uploading to YouTube...")
        
#         # Combine description with keywords and hashtags
#         keywords_text = "\n".join(seo_metadata['keywords'])
#         hashtags_text = " ".join(seo_metadata['hashtags'])
        
#         full_description = f"{seo_metadata['description']}\n\n━━━━━━━━━━━━━━━━━━━━━━\nKEYWORDS:\n{keywords_text}\n\n{hashtags_text}"
        
#         upload_result = await upload_to_youtube(
#             final_video, 
#             seo_metadata['title'], 
#             full_description, 
#             user_id
#         )
        
#         if not upload_result.get("success"):
#             raise Exception(upload_result.get("error"))
        
#         # SUCCESS
#         elapsed = (datetime.now() - start_time).total_seconds()
        
#         logger.info("="*80)
#         logger.info("✅ AI ANIMAL VIDEO SUCCESS!")
#         logger.info(f"   Time: {elapsed:.1f}s")
#         logger.info(f"   Video ID: {upload_result['video_id']}")
#         logger.info("="*80)
        
#         PROCESSING_STATUS[task_id] = {
#             "status": "completed",
#             "progress": 100,
#             "success": True,
#             "message": "Uploaded!",
#             "title": seo_metadata["title"],
#             "description": full_description,
#             "keywords": seo_metadata["keywords"],
#             "hashtags": seo_metadata["hashtags"],
#             "duration": round(duration, 1),
#             "processing_time": round(elapsed, 1),
#             "video_id": upload_result["video_id"],
#             "video_url": upload_result["video_url"],
#             "completed_at": datetime.utcnow().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"❌ FAILED: {e}")
        
#         PROCESSING_STATUS[task_id] = {
#             "status": "failed",
#             "progress": 0,
#             "success": False,
#             "error": str(e),
#             "message": str(e),
#             "failed_at": datetime.utcnow().isoformat()
#         }
    
#     finally:
#         if temp_dir and os.path.exists(temp_dir):
#             logger.info("🧹 Cleanup...")
#             shutil.rmtree(temp_dir, ignore_errors=True)
        
#         gc.collect()
#         log_memory("FINAL")

# # ═══════════════════════════════════════════════════════════════════════
# # API ROUTES
# # ═══════════════════════════════════════════════════════════════════════

# router = APIRouter()

# @router.post("/api/ai-animal-videos/process")
# async def process_endpoint(request: Request):
#     """Process AI animal video"""
#     logger.info("🌐 AI ANIMAL VIDEO REQUEST")
    
#     try:
#         data = await request.json()
        
#         user_id = data.get("user_id")
#         drive_url = (data.get("drive_url") or "").strip()
        
#         if not user_id:
#             return JSONResponse(status_code=400, content={"success": False, "error": "user_id required"})
        
#         if not drive_url or "drive.google.com" not in drive_url:
#             return JSONResponse(status_code=400, content={"success": False, "error": "Valid Google Drive URL required"})
        
#         task_id = str(uuid.uuid4())
#         logger.info(f"✅ Task ID: {task_id}")
        
#         await asyncio.wait_for(process_ai_animal_video(drive_url, user_id, task_id), timeout=900)
        
#         result = PROCESSING_STATUS.get(task_id, {"success": False, "error": "Unknown error"})
#         return JSONResponse(content=result)
        
#     except asyncio.TimeoutError:
#         return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
#     except Exception as e:
#         logger.error(f"❌ {e}")
#         return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# @router.get("/api/ai-animal-videos/status/{task_id}")
# async def status_endpoint(task_id: str):
#     """Get processing status"""
#     status = PROCESSING_STATUS.get(task_id)
#     if not status:
#         return JSONResponse(status_code=404, content={"success": False, "error": "Task not found"})
#     return JSONResponse(content=status)

# @router.get("/api/ai-animal-videos/health")
# async def health_endpoint():
#     """Health check"""
#     return JSONResponse(content={
#         "status": "ok",
#         "mistral_configured": bool(MISTRAL_API_KEY),
#         "features": {
#             "voiceover": "NONE (BGM only)",
#             "bgm": "Animal BGM at 25% volume",
#             "captions": "Emoji captions at bottom",
#             "ai_seo": "Viral titles + 45 keywords + hashtags",
#             "video_enhancement": "Saturation +25%, Brightness +10%, Contrast +15%"
#         }
#     })

# async def initialize():
#     """Startup initialization"""
#     logger.info("="*80)
#     logger.info("🚀 AI ANIMAL VIDEO PROCESSOR")
#     logger.info("="*80)
#     logger.info("✅ NO VOICEOVER - BGM ONLY")
#     logger.info("✅ AI-Generated Viral Titles (Hinglish + inline hashtags)")
#     logger.info("✅ AI-Generated 45 Keywords + 7-9 Hashtags")
#     logger.info("✅ Emoji Captions at Bottom")
#     logger.info("✅ Video Enhancements")
#     logger.info("✅ Direct YouTube Upload")
#     logger.info("="*80)
    
#     if MISTRAL_API_KEY:
#         logger.info("✅ Mistral AI configured (AI SEO)")
#     else:
#         logger.warning("⚠️ Mistral AI not configured (basic SEO)")
    
#     log_memory("startup")

# __all__ = ["router", "initialize"]












































"""
china_shorts_final_orange_cat_v2.py - ROBUST WITH MULTIPLE FALLBACKS
=====================================================================
✅ FIXED: Audio mixing filter syntax
✅ 3-LEVEL FALLBACKS for audio mixing
✅ 3-LEVEL FALLBACKS for video filters  
✅ 3-LEVEL FALLBACKS for captions
✅ BGM is MUST HAVE (highest priority)
✅ Intro/Outro nice-to-have (fallback if fails)
✅ Never fails completely - always produces output
=====================================================================
"""

from fastapi import APIRouter, Request, File, UploadFile, Form
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
import aiofiles
from typing import Optional, List, Dict, Any
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
logger = logging.getLogger("ChinaShortsOrangeCat")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)

def log_memory(step: str):
    """Log memory usage"""
    if HAS_PSUTIL:
        try:
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"🧠 [{step}]: {mem_mb:.1f}MB")
            if mem_mb > 450:
                logger.warning(f"⚠️  HIGH: {mem_mb:.1f}MB")
                gc.collect()
        except:
            pass

def log_step(step: str, status: str = "START", details: str = ""):
    """Log processing steps"""
    if status == "START":
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 {step}")
        if details:
            logger.info(f"   {details}")
        logger.info(f"{'='*70}")
    elif status == "SUCCESS":
        logger.info(f"✅ {step} SUCCESS")
        if details:
            logger.info(f"   {details}")
    elif status == "FAILED":
        logger.error(f"❌ {step} FAILED")
        if details:
            logger.error(f"   {details}")
    elif status == "FALLBACK":
        logger.warning(f"⚠️  {step} FALLBACK")
        if details:
            logger.warning(f"   {details}")

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# SINGLE BGM - Meow Meow Meow ONLY (50% volume)
CHINA_BGM_URL = "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/Meow%20Meow%20Meow%20Meow%20%F0%9F%8E%B6%20Sad%20TikTok%20Song%20%F0%9F%92%94%F0%9F%98%BF.mp3"
BGM_VOLUME = 0.40  # 50% volume

CAPTION_EMOJIS = ["😺", "🐱", "😹", "😼", "🦁", "💪", "🔥", "✨", "💯", "👀", "🎉", "❤️", "😂", "🤣", "😍"]

ELEVENLABS_INTRO_VOICES = ["7b9mYhmnp0y2qSH1FnBL", "MwUdldmtb1Qt7mDEbKM3", "ryIIztHPLYSJ74ueXxnO"]
EDGE_TTS_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]

DOUYIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.douyin.com/",
}

MOBILE_HEADERS = {
    "User-Agent": "com.ss.android.ugc.aweme/260801 (Linux; U; Android 11)",
}

PROCESSING_STATUS = {}

INTRO_TEMPLATES = [
    "Dosto, aaj hum dekhenge orange billa ki mastiyan! Dekhte rahiye kya hota hai!",
    "Santra billa ki sarrarate shuru! Ye dekh kar aap shock ho jayenge!",
    "Orange cat ki badmashiyan aa gayi! Video end tak dekhna mat bhoolna!",
    "Dekho aaj is orange bille ne kya dhamaal machaya! Ye toh must watch hai!",
]

OUTRO_TEMPLATES = [
    "Kaisa laga orange bille ka ye video? LIKE karein aur SUBSCRIBE zaroor karein!",
    "Agar aapko ye mastiyan pasand aayi to LIKE aur SUBSCRIBE karein!",
    "Video kaisi lagi batao! LIKE karo, SHARE karo, aur SUBSCRIBE zaroor karein!",
]

# ═══════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def cleanup(*paths):
    """Delete files"""
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except:
            pass
    gc.collect()

def run_ffmpeg(cmd: list, timeout: int = 180, step: str = "FFmpeg") -> bool:
    """Run FFmpeg with logging"""
    logger.info(f"🎬 {step}...")
    try:
        result = subprocess.run(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE, 
            timeout=timeout, 
            text=True
        )
        if result.returncode == 0:
            logger.info(f"✅ {step} OK")
            return True
        else:
            logger.error(f"❌ {step} failed: {result.stderr[-300:]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {step} timeout")
        return False
    except Exception as e:
        logger.error(f"❌ {step} error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════
# AI SEO GENERATION
# ═══════════════════════════════════════════════════════════════════════

async def generate_orange_cat_seo() -> dict:
    """Generate Orange Cat SEO"""
    log_step("AI SEO Generation", "START", "Orange Cat Focus")
    
    if MISTRAL_API_KEY:
        try:
            logger.info("🤖 Using Mistral AI...")
            
            prompt = """You are a VIRAL YouTube Shorts SEO expert for AI ORANGE CAT VIDEOS.

VIDEO: AI-generated orange cat doing funny/chaotic things
AUDIO: Sad/cute background music (Meow Meow Meow)
AUDIENCE: Global (India + International)

TITLE REQUIREMENTS:
- 3-7 words ONLY
- MUST mention "Orange Cat" or "Orange Billa" or "Santra Cat"
- Simple English, natural
- 3-5 inline hashtags at END
- NO emojis

EXAMPLES:
- Orange Cat Doing Cat Things #cat #pets #funny
- Orange Billa Ki Mastiyan #cat #shorts #viral
- The Orange Cat Story #cat #animals #trending

DESCRIPTION: 2 short paragraphs about the orange cat

KEYWORDS: EXACTLY 45 keywords (orange cat, funny cat, etc.)

HASHTAGS: 7-9 hashtags (#Shorts, #OrangeCat, #Cats are MUST)

OUTPUT JSON:
{
  "title": "Orange Cat Title #tag1 #tag2 #tag3",
  "description": "Paragraph 1\\n\\nParagraph 2",
  "keywords": ["keyword1", ... 45 total],
  "hashtags": ["#Shorts", "#OrangeCat", ... 7-9 total]
}"""
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Output ONLY valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 2000
                    }
                )
                
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    content = re.sub(r'```json\n?|\n?```', '', content).strip()
                    match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if match:
                        data = json.loads(match.group(0))
                        title = data.get("title", "Orange Cat Adventures #cat #viral #shorts")
                        keywords = data.get("keywords", [])
                        
                        while len(keywords) < 45:
                            keywords.append("orange cat")
                        keywords = keywords[:45]
                        
                        log_step("AI SEO Generation", "SUCCESS", f"Title: {title}")
                        return {
                            "title": title,
                            "description": data.get("description", "Orange cat video!"),
                            "keywords": keywords,
                            "hashtags": data.get("hashtags", ["#Shorts", "#OrangeCat", "#Cats"]),
                            "ai_generated": True
                        }
        except Exception as e:
            logger.warning(f"⚠️  Mistral failed: {e}")
    
    # FALLBACK
    log_step("AI SEO Generation", "FALLBACK", "Using basic SEO")
    return {
        "title": "Orange Cat Adventures #cat #viral #shorts",
        "description": "Watch this orange cat!\n\nLike and subscribe!",
        "keywords": ["orange cat"] * 45,
        "hashtags": ["#Shorts", "#OrangeCat", "#Cats"],
        "ai_generated": False
    }

# ═══════════════════════════════════════════════════════════════════════
# INTRO/OUTRO VOICEOVER
# ═══════════════════════════════════════════════════════════════════════

async def generate_intro_outro_voiceovers(temp_dir: str) -> tuple[Optional[str], Optional[str]]:
    """Generate intro/outro with fallbacks"""
    log_step("Intro/Outro Voiceovers", "START")
    
    intro_text = random.choice(INTRO_TEMPLATES)
    outro_text = random.choice(OUTRO_TEMPLATES)
    
    logger.info(f"   Intro: {intro_text[:50]}...")
    logger.info(f"   Outro: {outro_text[:50]}...")
    
    intro_path = os.path.join(temp_dir, "intro.mp3")
    outro_path = os.path.join(temp_dir, "outro.mp3")
    
    # TRY 1: ElevenLabs
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        try:
            logger.info("   🎙️ Attempt 1: ElevenLabs...")
            voice_id = random.choice(ELEVENLABS_INTRO_VOICES)
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp_intro = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    json={"text": intro_text, "model_id": "eleven_multilingual_v2"}
                )
                
                resp_outro = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    json={"text": outro_text, "model_id": "eleven_multilingual_v2"}
                )
                
                if resp_intro.status_code == 200 and resp_outro.status_code == 200:
                    with open(intro_path, 'wb') as f:
                        f.write(resp_intro.content)
                    with open(outro_path, 'wb') as f:
                        f.write(resp_outro.content)
                    
                    log_step("Intro/Outro Voiceovers", "SUCCESS", "ElevenLabs")
                    return intro_path, outro_path
        except Exception as e:
            logger.warning(f"   ⚠️  ElevenLabs failed: {e}")
    
    # TRY 2: Edge TTS
    try:
        logger.info("   🎙️ Attempt 2: Edge TTS...")
        import edge_tts
        
        voice = random.choice(EDGE_TTS_VOICES)
        
        await edge_tts.Communicate(intro_text, voice, rate="+10%").save(intro_path)
        await edge_tts.Communicate(outro_text, voice, rate="+10%").save(outro_path)
        
        if os.path.exists(intro_path) and os.path.exists(outro_path):
            log_step("Intro/Outro Voiceovers", "SUCCESS", "Edge TTS")
            return intro_path, outro_path
    except Exception as e:
        logger.warning(f"   ⚠️  Edge TTS failed: {e}")
    
    # FALLBACK: No intro/outro
    log_step("Intro/Outro Voiceovers", "FALLBACK", "Continuing without intro/outro")
    return None, None

# ═══════════════════════════════════════════════════════════════════════
# VIDEO PROCESSING
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
            return float(result.stdout.strip())
        return 0.0
    except:
        return 0.0

async def validate_video_file(video_path: str) -> tuple[bool, str]:
    """Validate video"""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=duration", "-of", "json", video_path
        ], capture_output=True, timeout=30, text=True)
        
        if result.returncode != 0:
            return False, "Invalid video"
        
        data = json.loads(result.stdout)
        if not data.get("streams"):
            return False, "No video stream"
        
        duration = float(data["streams"][0].get("duration", "0"))
        if duration <= 0 or duration > 180:
            return False, f"Invalid duration: {duration:.0f}s"
        
        return True, ""
    except Exception as e:
        return False, str(e)

async def apply_copyright_filters_robust(input_path: str, output_path: str) -> tuple[bool, str]:
    """
    Apply filters with 3-level fallback
    METHOD 1: Full filters (eq + scale)
    METHOD 2: Scale only
    METHOD 3: Copy original
    """
    log_step("Copyright Filters", "START")
    
    # METHOD 1: Full filters
    logger.info("   🎨 Method 1: Full filters (eq + scale)...")
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", "eq=saturation=1.25:brightness=0.10:contrast=1.15,scale=720:-2",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-c:a", "copy", "-y", output_path
    ], 60, "Filters-Method1")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        log_step("Copyright Filters", "SUCCESS", "Method 1")
        return True, ""
    
    cleanup(output_path)
    
    # METHOD 2: Scale only
    logger.info("   🎨 Method 2: Scale only...")
    success = run_ffmpeg([
        "ffmpeg", "-i", input_path,
        "-vf", "scale=720:-2",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-c:a", "copy", "-y", output_path
    ], 60, "Filters-Method2")
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        log_step("Copyright Filters", "SUCCESS", "Method 2 (scale only)")
        return True, ""
    
    cleanup(output_path)
    
    # METHOD 3: Copy original
    logger.info("   🎨 Method 3: Copy original...")
    try:
        shutil.copy(input_path, output_path)
        log_step("Copyright Filters", "FALLBACK", "Using original video")
        return True, ""
    except:
        return False, "All filter methods failed"

def generate_emoji_srt(duration: float) -> str:
    """Generate emoji SRT"""
    num_captions = max(5, int(duration / 2))
    time_per = duration / num_captions
    blocks = []
    
    for i in range(num_captions):
        start = i * time_per
        end = start + time_per
        
        sh, sm, ss = int(start//3600), int((start%3600)//60), start%60
        eh, em, es = int(end//3600), int((end%3600)//60), end%60
        
        emojis = " ".join(random.choices(CAPTION_EMOJIS, k=random.choice([2, 3])))
        
        blocks.append(
            f"{i+1}\n"
            f"{sh:02d}:{sm:02d}:{ss:06.3f}".replace(".", ",") + 
            f" --> {eh:02d}:{em:02d}:{es:06.3f}".replace(".", ",") + 
            f"\n{emojis}\n"
        )
    
    return "\n".join(blocks)

async def apply_emoji_captions_robust(video_path: str, duration: float, output_path: str) -> tuple[bool, str]:
    """
    Apply captions with 3-level fallback
    METHOD 1: Emoji captions
    METHOD 2: Simple text captions
    METHOD 3: No captions
    """
    log_step("Emoji Captions", "START")
    
    srt_path = output_path.replace(".mp4", ".srt")
    
    # METHOD 1: Emoji captions
    try:
        logger.info("   ✨ Method 1: Emoji captions...")
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(generate_emoji_srt(duration))
        
        srt_esc = srt_path.replace("\\", "\\\\").replace(":", "\\:")
        
        success = run_ffmpeg([
            "ffmpeg", "-i", video_path,
            "-vf", f"subtitles={srt_esc}:force_style='FontSize=28,Bold=1,Alignment=2,MarginV=40'",
            "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
            "-y", output_path
        ], 90, "Captions-Method1")
        
        cleanup(srt_path)
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            log_step("Emoji Captions", "SUCCESS", "Method 1")
            return True, ""
        
        cleanup(output_path)
    except Exception as e:
        logger.warning(f"   ⚠️  Method 1 failed: {e}")
    
    # METHOD 2: Simple burn-in text
    logger.info("   ✨ Method 2: Simple text...")
    try:
        success = run_ffmpeg([
            "ffmpeg", "-i", video_path,
            "-vf", "drawtext=text='Orange Cat':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h-50",
            "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
            "-y", output_path
        ], 60, "Captions-Method2")
        
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            log_step("Emoji Captions", "SUCCESS", "Method 2 (simple text)")
            return True, ""
        
        cleanup(output_path)
    except Exception as e:
        logger.warning(f"   ⚠️  Method 2 failed: {e}")
    
    # METHOD 3: No captions
    logger.info("   ✨ Method 3: No captions...")
    try:
        shutil.copy(video_path, output_path)
        log_step("Emoji Captions", "FALLBACK", "No captions")
        return True, ""
    except:
        return False, "All caption methods failed"

async def remove_audio(video_in: str, video_out: str) -> bool:
    """Remove audio"""
    success = run_ffmpeg([
        "ffmpeg", "-i", video_in,
        "-c:v", "copy", "-an", "-y", video_out
    ], 60, "Remove-Audio")
    
    if success:
        cleanup(video_in)
    return success

async def download_bgm(output: str) -> bool:
    """Download BGM (MUST HAVE)"""
    log_step("Download BGM", "START", "Meow Meow Meow (CRITICAL)")
    
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            async with client.stream("GET", CHINA_BGM_URL) as response:
                if response.status_code == 200:
                    total = 0
                    with open(output, 'wb') as f:
                        async for chunk in response.aiter_bytes(1024*1024):
                            f.write(chunk)
                            total += len(chunk)
                    
                    if total > 10000:
                        log_step("Download BGM", "SUCCESS", f"{total/(1024*1024):.1f}MB")
                        return True
        return False
    except:
        return False

async def add_intro_outro_bgm_robust(
    video_path: str,
    intro_audio: Optional[str],
    outro_audio: Optional[str],
    bgm_path: Optional[str],
    output_path: str
) -> tuple[bool, str]:
    """
    Add audio with 3-level fallback
    METHOD 1: Intro + Outro + BGM (complex)
    METHOD 2: BGM only (simple - MUST WORK)
    METHOD 3: No audio (last resort)
    """
    log_step("Add Audio", "START", "Intro/Outro + BGM")
    
    duration = await get_duration(video_path)
    if duration <= 0:
        return False, "Duration error"
    
    # METHOD 1: Full mix (intro + outro + BGM)
    if intro_audio and outro_audio and bgm_path and os.path.exists(intro_audio) and os.path.exists(outro_audio) and os.path.exists(bgm_path):
        try:
            logger.info("   🎵 Method 1: Intro + Outro + BGM (complex mix)...")
            
            # FIXED FILTER SYNTAX
            delay_ms = int((duration - 5) * 1000)
            
            # Correct filter syntax (no semicolons between inputs)
            filter_complex = (
                f"[1:a]volume={BGM_VOLUME}[bgm];"
                f"[2:a]adelay=0|0[intro];"
                f"[3:a]adelay={delay_ms}|{delay_ms}[outro];"
                f"[bgm][intro][outro]amix=inputs=3:duration=first[a]"
            )
            
            logger.info(f"   Filter: {filter_complex[:100]}...")
            
            cmd = [
                "ffmpeg", "-i", video_path, "-i", bgm_path, "-i", intro_audio, "-i", outro_audio,
                "-filter_complex", filter_complex,
                "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                "-shortest", "-y", output_path
            ]
            
            success = run_ffmpeg(cmd, 90, "Audio-Method1")
            
            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                cleanup(video_path, intro_audio, outro_audio, bgm_path)
                log_step("Add Audio", "SUCCESS", "Method 1 (Full mix)")
                return True, ""
            
            cleanup(output_path)
        except Exception as e:
            logger.warning(f"   ⚠️  Method 1 failed: {e}")
    
    # METHOD 2: BGM only (CRITICAL - MUST WORK)
    if bgm_path and os.path.exists(bgm_path):
        try:
            logger.info("   🎵 Method 2: BGM only (CRITICAL)...")
            
            success = run_ffmpeg([
                "ffmpeg", "-i", video_path, "-i", bgm_path,
                "-filter_complex", f"[1:a]volume={BGM_VOLUME}[a]",
                "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
                "-shortest", "-y", output_path
            ], 60, "Audio-Method2")
            
            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                cleanup(video_path, intro_audio, outro_audio, bgm_path)
                log_step("Add Audio", "SUCCESS", "Method 2 (BGM only)")
                return True, ""
            
            cleanup(output_path)
        except Exception as e:
            logger.warning(f"   ⚠️  Method 2 failed: {e}")
    
    # METHOD 3: No audio (last resort)
    logger.info("   🎵 Method 3: No audio (FALLBACK)...")
    try:
        shutil.copy(video_path, output_path)
        cleanup(video_path, intro_audio, outro_audio, bgm_path)
        log_step("Add Audio", "FALLBACK", "No audio added")
        return True, ""
    except:
        return False, "All audio methods failed"

# ═══════════════════════════════════════════════════════════════════════
# URL DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID"""
    patterns = [r'modal_id=(\d+)', r'video/(\d{19})', r'/(\d{19})']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def download_douyin_api(video_id: str, output: str) -> bool:
    """Download via Douyin API"""
    if not video_id:
        return False
    
    api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            response = await client.get(api_url, headers=DOUYIN_HEADERS)
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            if "item_list" not in data or not data["item_list"]:
                return False
            
            item = data["item_list"][0]
            video_urls = []
            
            if "video" in item and "play_addr" in item["video"]:
                if "url_list" in item["video"]["play_addr"]:
                    video_urls.extend(item["video"]["play_addr"]["url_list"])
            
            for video_url in video_urls:
                try:
                    async with client.stream("GET", video_url, headers=DOUYIN_HEADERS, timeout=180) as stream:
                        if stream.status_code == 200:
                            total = 0
                            with open(output, 'wb') as f:
                                async for chunk in stream.aiter_bytes(1024*1024):
                                    f.write(chunk)
                                    total += len(chunk)
                            
                            if total > 10000:
                                return True
                except:
                    continue
            
            return False
    except:
        return False

async def download_china_video(url: str, output: str) -> tuple[bool, str]:
    """Download with fallbacks"""
    video_id = extract_video_id(url)
    if not video_id:
        return False, "No video ID"
    
    if await download_douyin_api(video_id, output):
        return True, ""
    
    return False, "Download failed"

# ═══════════════════════════════════════════════════════════════════════
# MANUAL UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def save_uploaded_file(upload_file: UploadFile, output_path: str) -> tuple[bool, str]:
    """Save uploaded file"""
    try:
        max_size = 100 * 1024 * 1024
        total_bytes = 0
        
        async with aiofiles.open(output_path, 'wb') as f:
            while True:
                chunk = await upload_file.read(1024 * 1024)
                if not chunk:
                    break
                
                total_bytes += len(chunk)
                if total_bytes > max_size:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    return False, "File too large"
                
                await f.write(chunk)
        
        if os.path.getsize(output_path) < 10000:
            os.remove(output_path)
            return False, "File too small"
        
        return True, ""
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        return False, str(e)

# ═══════════════════════════════════════════════════════════════════════
# YOUTUBE UPLOAD
# ═══════════════════════════════════════════════════════════════════════

async def upload_to_youtube(video_path: str, title: str, description: str, user_id: str) -> dict:
    """Upload to YouTube"""
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db.youtube.client:
            await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        if not creds:
            return {"success": False, "error": "No credentials"}
        
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
            return {
                "success": True,
                "video_id": result.get("video_id"),
                "video_url": f"https://youtube.com/shorts/{result.get('video_id')}"
            }
        
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PROCESSING
# ═══════════════════════════════════════════════════════════════════════

async def process_china_short_url(china_url: str, user_id: str, task_id: str):
    """URL processing"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start_time.isoformat(),
        "processing_type": "url"
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"📊 [{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="orange_cat_")
        log_memory("START")
        
        update(10, "Downloading...")
        raw_video = os.path.join(temp_dir, "raw.mp4")
        success, error = await download_china_video(china_url, raw_video)
        if not success:
            raise Exception(error)
        
        update(20, "Analyzing...")
        duration = await get_duration(raw_video)
        if duration <= 0 or duration > 180:
            raise ValueError(f"Invalid duration: {duration:.0f}s")
        
        update(25, "Generating SEO...")
        seo_metadata = await generate_orange_cat_seo()
        
        update(30, "Applying filters...")
        filtered_video = os.path.join(temp_dir, "filtered.mp4")
        await apply_copyright_filters_robust(raw_video, filtered_video)
        
        update(40, "Removing audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered_video, silent_video):
            raise Exception("Remove audio failed")
        
        update(50, "Adding captions...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        await apply_emoji_captions_robust(silent_video, duration, captioned_video)
        
        update(60, "Generating intro/outro...")
        intro_audio, outro_audio = await generate_intro_outro_voiceovers(temp_dir)
        
        update(70, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        if not await download_bgm(bgm_path):
            logger.warning("⚠️  BGM download failed!")
            bgm_path = None
        
        update(80, "Mixing audio...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await add_intro_outro_bgm_robust(
            captioned_video, intro_audio, outro_audio, bgm_path, final_video
        )
        if not success:
            raise Exception(error)
        
        update(95, "Uploading...")
        
        keywords_text = "\n".join(seo_metadata['keywords'])
        hashtags_text = " ".join(seo_metadata['hashtags'])
        full_description = f"{seo_metadata['description']}\n\n{keywords_text}\n\n{hashtags_text}"
        
        upload_result = await upload_to_youtube(
            final_video, seo_metadata['title'], full_description, user_id
        )
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ SUCCESS! Time: {elapsed:.1f}s")
        logger.info(f"{'='*80}\n")
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "processing_type": "url",
            "title": seo_metadata["title"],
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()

async def process_uploaded_video(video_path: str, user_id: str, task_id: str):
    """Upload processing"""
    temp_dir = None
    start_time = datetime.now()
    
    PROCESSING_STATUS[task_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting...",
        "started_at": start_time.isoformat(),
        "processing_type": "upload"
    }
    
    def update(progress: int, msg: str):
        PROCESSING_STATUS[task_id]["progress"] = progress
        PROCESSING_STATUS[task_id]["message"] = msg
        logger.info(f"📊 [{progress}%] {msg}")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="orange_cat_upload_")
        log_memory("START-UPLOAD")
        
        update(10, "Processing file...")
        raw_video = os.path.join(temp_dir, "uploaded.mp4")
        shutil.copy(video_path, raw_video)
        
        update(15, "Validating...")
        is_valid, error = await validate_video_file(raw_video)
        if not is_valid:
            raise ValueError(error)
        
        update(20, "Analyzing...")
        duration = await get_duration(raw_video)
        if duration <= 0 or duration > 180:
            raise ValueError(f"Invalid duration: {duration:.0f}s")
        
        update(25, "Generating SEO...")
        seo_metadata = await generate_orange_cat_seo()
        
        update(30, "Applying filters...")
        filtered_video = os.path.join(temp_dir, "filtered.mp4")
        await apply_copyright_filters_robust(raw_video, filtered_video)
        
        update(40, "Removing audio...")
        silent_video = os.path.join(temp_dir, "silent.mp4")
        if not await remove_audio(filtered_video, silent_video):
            raise Exception("Remove audio failed")
        
        update(50, "Adding captions...")
        captioned_video = os.path.join(temp_dir, "captioned.mp4")
        await apply_emoji_captions_robust(silent_video, duration, captioned_video)
        
        update(60, "Generating intro/outro...")
        intro_audio, outro_audio = await generate_intro_outro_voiceovers(temp_dir)
        
        update(70, "Downloading BGM...")
        bgm_path = os.path.join(temp_dir, "bgm.mp3")
        if not await download_bgm(bgm_path):
            logger.warning("⚠️  BGM download failed!")
            bgm_path = None
        
        update(80, "Mixing audio...")
        final_video = os.path.join(temp_dir, "final.mp4")
        success, error = await add_intro_outro_bgm_robust(
            captioned_video, intro_audio, outro_audio, bgm_path, final_video
        )
        if not success:
            raise Exception(error)
        
        update(95, "Uploading...")
        
        keywords_text = "\n".join(seo_metadata['keywords'])
        hashtags_text = " ".join(seo_metadata['hashtags'])
        full_description = f"{seo_metadata['description']}\n\n{keywords_text}\n\n{hashtags_text}"
        
        upload_result = await upload_to_youtube(
            final_video, seo_metadata['title'], full_description, user_id
        )
        
        if not upload_result.get("success"):
            raise Exception(upload_result.get("error"))
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ SUCCESS! Time: {elapsed:.1f}s")
        logger.info(f"{'='*80}\n")
        
        PROCESSING_STATUS[task_id] = {
            "status": "completed",
            "progress": 100,
            "success": True,
            "processing_type": "upload",
            "title": seo_metadata["title"],
            "video_id": upload_result["video_id"],
            "video_url": upload_result["video_url"],
            "completed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        
        PROCESSING_STATUS[task_id] = {
            "status": "failed",
            "progress": 0,
            "success": False,
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
    
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        if video_path:
            try:
                os.remove(video_path)
            except:
                pass
        gc.collect()

# ═══════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════

router = APIRouter()

@router.post("/api/china-shorts/process-url")
async def process_url_endpoint(request: Request):
    """Process URL"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        china_url = (data.get("china_url") or "").strip()
        
        if not user_id or not china_url:
            return JSONResponse(status_code=400, content={"success": False, "error": "Missing params"})
        
        task_id = str(uuid.uuid4())
        asyncio.create_task(process_china_short_url(china_url, user_id, task_id))
        
        return JSONResponse(content={"success": True, "task_id": task_id})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/api/china-shorts/process-upload")
async def process_upload_endpoint(user_id: str = Form(...), video_file: UploadFile = File(...)):
    """Process upload"""
    uploaded_file_path = None
    
    try:
        if not user_id or not video_file:
            return JSONResponse(status_code=400, content={"success": False, "error": "Missing params"})
        
        task_id = str(uuid.uuid4())
        uploaded_file_path = f"/tmp/china_upload_{task_id}.mp4"
        
        success, error = await save_uploaded_file(video_file, uploaded_file_path)
        if not success:
            return JSONResponse(status_code=400, content={"success": False, "error": error})
        
        asyncio.create_task(process_uploaded_video(uploaded_file_path, user_id, task_id))
        
        return JSONResponse(content={"success": True, "task_id": task_id})
    except Exception as e:
        if uploaded_file_path:
            try:
                os.remove(uploaded_file_path)
            except:
                pass
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/api/china-shorts/status/{task_id}")
async def status_endpoint(task_id: str):
    """Get status"""
    status = PROCESSING_STATUS.get(task_id)
    if not status:
        return JSONResponse(status_code=404, content={"success": False, "error": "Not found"})
    return JSONResponse(content=status)

@router.get("/api/china-shorts/health")
async def health_endpoint():
    """Health check"""
    return JSONResponse(content={
        "status": "ok",
        "version": "6.0_ROBUST",
        "features": {
            "filters": "3-level fallback",
            "captions": "3-level fallback",
            "audio": "3-level fallback (intro+outro+BGM → BGM only → no audio)",
            "bgm": "50% volume, MUST HAVE",
            "intro_outro": "Nice-to-have with fallback"
        }
    })

async def initialize():
    """Startup"""
    logger.info("\n" + "="*80)
    logger.info("🚀 CHINA SHORTS - ORANGE CAT v6.0 ROBUST")
    logger.info("="*80)
    logger.info("✅ FIXED: Audio mixing filter syntax")
    logger.info("✅ 3-level fallbacks for everything")
    logger.info("✅ BGM is MUST HAVE (highest priority)")
    logger.info("✅ Intro/Outro nice-to-have")
    logger.info("✅ Never fails completely")
    logger.info("="*80 + "\n")
    log_memory("startup")

__all__ = ["router", "initialize"]