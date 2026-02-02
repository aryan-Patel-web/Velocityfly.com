"""
🎬 YouTube Video Downloader - Streamlit App
=============================================
✅ Max quality download (no watermark)
✅ 8 fallback methods with retry logic
✅ Beautiful UI with progress tracking
✅ Download history
✅ Error handling & logging
=============================================
"""

import streamlit as st
import asyncio
import httpx
import subprocess
import os
import tempfile
import shutil
import json
import re
import random
import time
from datetime import datetime
from pathlib import Path
import base64
from typing import Optional, Dict, List, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

# User agents for bot detection bypass
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

INVIDIOUS_INSTANCES = [
    "https://invidious.fdn.fr",
    "https://inv.nadeko.net",
    "https://invidious.privacyredirect.com",
    "https://inv.riverside.rocks",
]

# Session state initialization
if 'download_history' not in st.session_state:
    st.session_state.download_history = []
if 'current_download' not in st.session_state:
    st.session_state.current_download = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_random_headers() -> Dict[str, str]:
    """Generate random headers to bypass bot detection"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_video_info(file_path: str) -> Dict:
    """Get video duration and resolution using ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-show_entries", "format=duration",
            "-of", "json",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=10, check=False)
        
        if result.returncode == 0:
            data = json.loads(result.stdout.decode())
            stream = data.get('streams', [{}])[0]
            format_data = data.get('format', {})
            
            return {
                'width': stream.get('width', 0),
                'height': stream.get('height', 0),
                'duration': float(format_data.get('duration', 0)),
                'resolution': f"{stream.get('width', 0)}x{stream.get('height', 0)}"
            }
    except:
        pass
    
    return {'width': 0, 'height': 0, 'duration': 0, 'resolution': 'Unknown'}

# ============================================================================
# DOWNLOAD METHOD 1: COBALT API
# ============================================================================

async def download_with_cobalt(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """Cobalt API - Most reliable, no watermark"""
    try:
        if progress_callback:
            progress_callback("🔷 Trying Cobalt API (Professional Service)...")
        
        cobalt_instances = [
            "https://api.cobalt.tools",
            "https://co.wuk.sh",
        ]
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            for instance in cobalt_instances:
                try:
                    if progress_callback:
                        progress_callback(f"   Requesting from {instance}...")
                    
                    # Request download link
                    response = await client.post(
                        f"{instance}/api/json",
                        json={
                            "url": url,
                            "vCodec": "h264",
                            "vQuality": "max",  # Maximum quality
                            "aFormat": "mp3",
                            "isAudioOnly": False,
                            "isNoTTWatermark": True,  # No watermark!
                            "isTTFullAudio": False,
                            "isAudioMuted": False,
                        },
                        headers={"Accept": "application/json", "Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        download_url = data.get("url")
                        
                        if download_url:
                            if progress_callback:
                                progress_callback(f"   Downloading video...")
                            
                            # Download video
                            video_response = await client.get(download_url, headers=get_random_headers())
                            
                            if video_response.status_code == 200:
                                with open(output_path, 'wb') as f:
                                    f.write(video_response.content)
                                
                                if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
                                    size = format_file_size(os.path.getsize(output_path))
                                    return True, f"✅ Cobalt API: {size}"
                
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"   ⚠️ {instance} failed")
                    continue
        
        return False, "❌ Cobalt API failed"
    
    except Exception as e:
        return False, f"❌ Cobalt error: {str(e)}"

# ============================================================================
# DOWNLOAD METHOD 2: YT-DLP (MAX QUALITY)
# ============================================================================

async def download_with_ytdlp(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """yt-dlp with maximum quality settings"""
    strategies = [
        {
            "name": "Best quality (bestvideo+bestaudio)",
            "cmd": [
                "yt-dlp",
                "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--merge-output-format", "mp4",
                "--no-warnings",
                "--no-check-certificate",
                "--geo-bypass",
                "--user-agent", random.choice(USER_AGENTS),
                "-o", output_path,
                url
            ]
        },
        {
            "name": "Android client (max quality)",
            "cmd": [
                "yt-dlp",
                "--extractor-args", "youtube:player_client=android",
                "--format", "best[height>=1080]/best",
                "--no-check-certificate",
                "--geo-bypass",
                "-o", output_path,
                url
            ]
        },
        {
            "name": "iOS client (max quality)",
            "cmd": [
                "yt-dlp",
                "--extractor-args", "youtube:player_client=ios",
                "--format", "best",
                "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
                "-o", output_path,
                url
            ]
        },
        {
            "name": "TV embedded (fallback)",
            "cmd": [
                "yt-dlp",
                "--extractor-args", "youtube:player_client=tv_embedded",
                "--format", "best",
                "-o", output_path,
                url
            ]
        }
    ]
    
    for strategy in strategies:
        try:
            if progress_callback:
                progress_callback(f"🔷 Trying yt-dlp: {strategy['name']}...")
            
            process = await asyncio.create_subprocess_exec(
                *strategy["cmd"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode == 0 and os.path.exists(output_path):
                if os.path.getsize(output_path) > 100000:
                    size = format_file_size(os.path.getsize(output_path))
                    return True, f"✅ yt-dlp ({strategy['name']}): {size}"
        
        except asyncio.TimeoutError:
            if progress_callback:
                progress_callback(f"   ⏱️ Timeout")
            continue
        except Exception as e:
            if progress_callback:
                progress_callback(f"   ⚠️ Failed")
            continue
    
    return False, "❌ yt-dlp failed"

# ============================================================================
# DOWNLOAD METHOD 3: INVIDIOUS API
# ============================================================================

async def download_with_invidious(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """Invidious API with quality selection"""
    try:
        if progress_callback:
            progress_callback("🔷 Trying Invidious API...")
        
        video_id = extract_video_id(url)
        if not video_id:
            return False, "❌ Invalid video ID"
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            for instance in INVIDIOUS_INSTANCES:
                try:
                    if progress_callback:
                        progress_callback(f"   Checking {instance}...")
                    
                    api_url = f"{instance}/api/v1/videos/{video_id}"
                    response = await client.get(api_url, headers=get_random_headers())
                    
                    if response.status_code == 200:
                        data = response.json()
                        formats = data.get('formatStreams', [])
                        
                        if formats:
                            # Get highest quality format
                            best_format = max(formats, key=lambda x: (
                                x.get('size', 0),
                                x.get('resolution', '').replace('p', '0')
                            ))
                            
                            video_url = best_format.get('url')
                            
                            if video_url:
                                if progress_callback:
                                    progress_callback(f"   Downloading {best_format.get('resolution', 'Unknown')}...")
                                
                                video_response = await client.get(video_url, headers=get_random_headers())
                                
                                if video_response.status_code == 200:
                                    with open(output_path, 'wb') as f:
                                        f.write(video_response.content)
                                    
                                    if os.path.getsize(output_path) > 100000:
                                        size = format_file_size(os.path.getsize(output_path))
                                        return True, f"✅ Invidious ({best_format.get('resolution')}): {size}"
                
                except Exception as e:
                    continue
        
        return False, "❌ Invidious failed"
    
    except Exception as e:
        return False, f"❌ Invidious error: {str(e)}"

# ============================================================================
# DOWNLOAD METHOD 4: Y2MATE SIMULATION
# ============================================================================

async def download_with_y2mate(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """Y2Mate API simulation"""
    try:
        if progress_callback:
            progress_callback("🔷 Trying Y2Mate simulation...")
        
        video_id = extract_video_id(url)
        if not video_id:
            return False, "❌ Invalid video ID"
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            # Step 1: Analyze video
            response = await client.post(
                "https://www.y2mate.com/mates/analyzeV2/ajax",
                data={
                    "k_query": f"https://www.youtube.com/watch?v={video_id}",
                    "k_page": "home",
                    "hl": "en",
                    "q_auto": "1"
                },
                headers={
                    **get_random_headers(),
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                links = data.get('links', {}).get('mp4', {})
                
                # Try qualities in order: 1080p, 720p, 480p, 360p
                for quality in ['1080', '720', '480', '360']:
                    if quality in links:
                        k_value = links[quality].get('k')
                        
                        if k_value:
                            if progress_callback:
                                progress_callback(f"   Converting {quality}p...")
                            
                            # Step 2: Convert
                            convert_response = await client.post(
                                "https://www.y2mate.com/mates/convertV2/index",
                                data={"vid": video_id, "k": k_value},
                                headers={
                                    **get_random_headers(),
                                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                                }
                            )
                            
                            if convert_response.status_code == 200:
                                convert_data = convert_response.json()
                                download_url = convert_data.get('dlink')
                                
                                if download_url:
                                    if progress_callback:
                                        progress_callback(f"   Downloading {quality}p...")
                                    
                                    video_response = await client.get(download_url, headers=get_random_headers())
                                    
                                    if video_response.status_code == 200:
                                        with open(output_path, 'wb') as f:
                                            f.write(video_response.content)
                                        
                                        if os.path.getsize(output_path) > 100000:
                                            size = format_file_size(os.path.getsize(output_path))
                                            return True, f"✅ Y2Mate ({quality}p): {size}"
        
        return False, "❌ Y2Mate failed"
    
    except Exception as e:
        return False, f"❌ Y2Mate error: {str(e)}"

# ============================================================================
# DOWNLOAD METHOD 5: SAVEFROM.NET SIMULATION
# ============================================================================

async def download_with_savefrom(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """SaveFrom.net simulation"""
    try:
        if progress_callback:
            progress_callback("🔷 Trying SaveFrom.net simulation...")
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            response = await client.get(
                "https://api.savefrom.net/info",
                params={"url": url},
                headers={
                    **get_random_headers(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Extract download URLs
                url_pattern = r'url":"(https?://[^"]+)"'
                urls = re.findall(url_pattern, content)
                
                for download_url in urls:
                    try:
                        download_url = download_url.replace('\\/', '/')
                        
                        if progress_callback:
                            progress_callback(f"   Downloading...")
                        
                        video_response = await client.get(download_url, headers=get_random_headers())
                        
                        if video_response.status_code == 200:
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            if os.path.getsize(output_path) > 100000:
                                size = format_file_size(os.path.getsize(output_path))
                                return True, f"✅ SaveFrom: {size}"
                    except:
                        continue
        
        return False, "❌ SaveFrom failed"
    
    except Exception as e:
        return False, f"❌ SaveFrom error: {str(e)}"

# ============================================================================
# DOWNLOAD METHOD 6: DIRECT STREAM EXTRACTION
# ============================================================================

async def download_with_direct_stream(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """Direct stream URL extraction"""
    try:
        if progress_callback:
            progress_callback("🔷 Trying direct stream extraction...")
        
        video_id = extract_video_id(url)
        if not video_id:
            return False, "❌ Invalid video ID"
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            page_url = f"https://www.youtube.com/watch?v={video_id}"
            response = await client.get(page_url, headers=get_random_headers())
            
            if response.status_code == 200:
                html = response.text
                
                # Extract player response
                pattern = r'var ytInitialPlayerResponse = ({.+?});'
                match = re.search(pattern, html)
                
                if match:
                    player_data = json.loads(match.group(1))
                    streaming_data = player_data.get('streamingData', {})
                    formats = streaming_data.get('formats', []) + streaming_data.get('adaptiveFormats', [])
                    
                    # Get highest quality video
                    video_formats = [f for f in formats if f.get('mimeType', '').startswith('video/mp4')]
                    video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
                    
                    for fmt in video_formats[:3]:
                        stream_url = fmt.get('url')
                        
                        if stream_url:
                            if progress_callback:
                                height = fmt.get('height', 0)
                                progress_callback(f"   Downloading {height}p...")
                            
                            video_response = await client.get(stream_url, headers=get_random_headers())
                            
                            if video_response.status_code == 200:
                                with open(output_path, 'wb') as f:
                                    f.write(video_response.content)
                                
                                if os.path.getsize(output_path) > 100000:
                                    size = format_file_size(os.path.getsize(output_path))
                                    return True, f"✅ Direct stream ({fmt.get('height')}p): {size}"
        
        return False, "❌ Direct stream failed"
    
    except Exception as e:
        return False, f"❌ Direct stream error: {str(e)}"

# ============================================================================
# DOWNLOAD METHOD 7: PYTUBEFIX
# ============================================================================

async def download_with_pytubefix(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """PyTubeFix - modern pytube fork"""
    try:
        if progress_callback:
            progress_callback("🔷 Trying PyTubeFix...")
        
        from pytubefix import YouTube
        
        yt = YouTube(url)
        
        # Get highest resolution progressive stream (video+audio)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            # Fallback: Get highest resolution video-only
            stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        
        if stream:
            if progress_callback:
                progress_callback(f"   Downloading {stream.resolution}...")
            
            temp = output_path.replace('.mp4', '_temp.mp4')
            stream.download(filename=temp)
            shutil.move(temp, output_path)
            
            size = format_file_size(os.path.getsize(output_path))
            return True, f"✅ PyTubeFix ({stream.resolution}): {size}"
        
        return False, "❌ PyTubeFix: No stream found"
    
    except ImportError:
        return False, "❌ PyTubeFix not installed"
    except Exception as e:
        return False, f"❌ PyTubeFix error: {str(e)}"

# ============================================================================
# DOWNLOAD METHOD 8: CLOUDFLARE BYPASS
# ============================================================================

async def download_with_cf_bypass(url: str, output_path: str, progress_callback=None) -> Tuple[bool, str]:
    """Cloudflare bypass using cloudscraper"""
    try:
        if progress_callback:
            progress_callback("🔷 Trying Cloudflare bypass...")
        
        import cloudscraper
        
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        
        video_id = extract_video_id(url)
        if not video_id:
            return False, "❌ Invalid video ID"
        
        # Try loader.to service
        service_url = f"https://loader.to/api/button/?url=https://www.youtube.com/watch?v={video_id}"
        
        response = scraper.get(service_url)
        
        if response.status_code == 200:
            data = response.json()
            download_url = data.get('url') or data.get('dlink')
            
            if download_url:
                if progress_callback:
                    progress_callback(f"   Downloading...")
                
                video_response = scraper.get(download_url)
                
                if video_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    if os.path.getsize(output_path) > 100000:
                        size = format_file_size(os.path.getsize(output_path))
                        return True, f"✅ CF Bypass: {size}"
        
        return False, "❌ CF Bypass failed"
    
    except ImportError:
        return False, "❌ cloudscraper not installed"
    except Exception as e:
        return False, f"❌ CF Bypass error: {str(e)}"

# ============================================================================
# MAIN DOWNLOAD ORCHESTRATOR WITH RETRY LOGIC
# ============================================================================

async def download_youtube_video(
    url: str,
    output_path: str,
    max_retries: int = 3,
    progress_callback=None,
    quality_criteria: str = "max"
) -> Tuple[bool, str, Dict]:
    """
    Download YouTube video with advanced retry logic
    
    Args:
        url: YouTube video URL
        output_path: Where to save the video
        max_retries: Max retry attempts per method
        progress_callback: Function to call with progress updates
        quality_criteria: 'max', 'high', 'medium', 'low'
    
    Returns:
        (success, message, info_dict)
    """
    
    # All download methods in priority order
    methods = [
        ("Cobalt API", download_with_cobalt),
        ("yt-dlp", download_with_ytdlp),
        ("Invidious", download_with_invidious),
        ("Y2Mate", download_with_y2mate),
        ("SaveFrom", download_with_savefrom),
        ("Direct Stream", download_with_direct_stream),
        ("PyTubeFix", download_with_pytubefix),
        ("CF Bypass", download_with_cf_bypass),
    ]
    
    total_attempts = 0
    
    for method_name, method_func in methods:
        for retry in range(max_retries):
            try:
                total_attempts += 1
                
                if progress_callback:
                    retry_text = f" (Retry {retry + 1}/{max_retries})" if retry > 0 else ""
                    progress_callback(f"📥 Method {methods.index((method_name, method_func)) + 1}/{len(methods)}: {method_name}{retry_text}")
                
                # Try download
                success, message = await method_func(url, output_path, progress_callback)
                
                if success:
                    # Validate download based on criteria
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        
                        # Get video info
                        video_info = get_video_info(output_path)
                        
                        # Check quality criteria
                        meets_criteria = True
                        
                        if quality_criteria == "max":
                            # Accept any successful download for max quality
                            meets_criteria = file_size > 1_000_000  # At least 1MB
                        elif quality_criteria == "high":
                            meets_criteria = video_info['height'] >= 720
                        elif quality_criteria == "medium":
                            meets_criteria = video_info['height'] >= 480
                        
                        if meets_criteria:
                            if progress_callback:
                                progress_callback(f"✅ SUCCESS! {message}")
                            
                            return True, message, {
                                'method': method_name,
                                'attempts': total_attempts,
                                'file_size': file_size,
                                'file_size_str': format_file_size(file_size),
                                **video_info
                            }
                        else:
                            if progress_callback:
                                progress_callback(f"⚠️ Quality criteria not met, trying next method...")
                            # Delete low quality file
                            os.remove(output_path)
                            continue
                
                # Method failed, try next retry
                if retry < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"   ⏳ Waiting before retry...")
                    await asyncio.sleep(2)  # Wait before retry
            
            except Exception as e:
                if progress_callback:
                    progress_callback(f"   ❌ Error: {str(e)}")
                
                if retry < max_retries - 1:
                    await asyncio.sleep(2)
                continue
        
        # Small delay between methods
        await asyncio.sleep(0.5)
    
    return False, f"❌ All methods failed after {total_attempts} attempts", {}

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    st.set_page_config(
        page_title="YouTube Video Downloader",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🎬 YouTube Video Downloader")
    st.markdown("### Download YouTube videos in maximum quality without watermarks")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        quality_criteria = st.selectbox(
            "Quality Criteria",
            ["max", "high (720p+)", "medium (480p+)", "low (any)"],
            help="Minimum quality requirement"
        ).split()[0]
        
        max_retries = st.slider(
            "Max Retries per Method",
            min_value=1,
            max_value=5,
            value=3,
            help="Number of retry attempts for each download method"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Download Methods")
        st.markdown("""
        1. 🔷 Cobalt API (No watermark)
        2. 🔧 yt-dlp (Max quality)
        3. 🌐 Invidious (Privacy-focused)
        4. 🎨 Y2Mate (Popular)
        5. 💾 SaveFrom (Reliable)
        6. 🔓 Direct Stream
        7. 📱 PyTubeFix
        8. 🛡️ Cloudflare Bypass
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ Features")
        st.markdown("""
        ✅ Max quality download  
        ✅ No watermarks  
        ✅ 8 fallback methods  
        ✅ Automatic retry  
        ✅ Progress tracking  
        ✅ Download history  
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input
        url = st.text_input(
            "🔗 YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any YouTube video URL (regular, shorts, or embedded)"
        )
        
        # Download button
        download_btn = st.button("📥 Download Video", type="primary", use_container_width=True)
    
    with col2:
        st.info("📌 **Tip**: Works with shorts, regular videos, and embedded links!")
    
    # Download logic
    if download_btn:
        if not url:
            st.error("❌ Please enter a YouTube URL")
            return
        
        # Validate URL
        video_id = extract_video_id(url)
        if not video_id:
            st.error("❌ Invalid YouTube URL")
            return
        
        # Create progress containers
        progress_text = st.empty()
        progress_bar = st.progress(0)
        status_container = st.empty()
        log_container = st.expander("📋 Download Log", expanded=True)
        
        logs = []
        
        def update_progress(message: str):
            logs.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
            with log_container:
                st.text("\n".join(logs[-20:]))  # Show last 20 logs
        
        # Start download
        with st.spinner("🚀 Starting download..."):
            try:
                # Create temp file
                temp_dir = tempfile.mkdtemp()
                output_path = os.path.join(temp_dir, f"{video_id}.mp4")
                
                # Run download
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                success, message, info = loop.run_until_complete(
                    download_youtube_video(
                        url=url,
                        output_path=output_path,
                        max_retries=max_retries,
                        progress_callback=update_progress,
                        quality_criteria=quality_criteria
                    )
                )
                
                loop.close()
                
                if success:
                    progress_bar.progress(100)
                    
                    # Success message
                    with status_container:
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Download Successful!</h3>
                            <p><strong>Method:</strong> {info.get('method', 'Unknown')}</p>
                            <p><strong>File Size:</strong> {info.get('file_size_str', 'Unknown')}</p>
                            <p><strong>Resolution:</strong> {info.get('resolution', 'Unknown')}</p>
                            <p><strong>Duration:</strong> {info.get('duration', 0):.1f}s</p>
                            <p><strong>Attempts:</strong> {info.get('attempts', 0)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Provide download button
                    with open(output_path, 'rb') as f:
                        video_data = f.read()
                    
                    st.download_button(
                        label="💾 Download Video File",
                        data=video_data,
                        file_name=f"video_{video_id}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
                    # Add to history
                    st.session_state.download_history.insert(0, {
                        'url': url,
                        'video_id': video_id,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'method': info.get('method'),
                        'size': info.get('file_size_str'),
                        'resolution': info.get('resolution')
                    })
                    
                    # Cleanup
                    shutil.rmtree(temp_dir, ignore_errors=True)
                
                else:
                    progress_bar.progress(0)
                    with status_container:
                        st.markdown(f"""
                        <div class="error-box">
                            <h3>❌ Download Failed</h3>
                            <p>{message}</p>
                            <p><strong>Suggestions:</strong></p>
                            <ul>
                                <li>Check if the video is public</li>
                                <li>Try a different video URL</li>
                                <li>Increase max retries</li>
                                <li>Lower quality criteria</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Cleanup
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
    
    # Download history
    if st.session_state.download_history:
        st.markdown("---")
        st.subheader("📜 Download History")
        
        for idx, item in enumerate(st.session_state.download_history[:10]):
            with st.expander(f"📹 {item['video_id']} - {item['timestamp']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Method:** {item['method']}")
                with col2:
                    st.write(f"**Size:** {item['size']}")
                with col3:
                    st.write(f"**Resolution:** {item['resolution']}")
                
                st.code(item['url'], language=None)

if __name__ == "__main__":
    main()