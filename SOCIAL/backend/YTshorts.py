import streamlit as st
import yt_dlp
import os
from pathlib import Path
import shutil
import subprocess

# Page configuration
st.set_page_config(
    page_title="YouTube to MP4 Converter",
    page_icon="🎥",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        border: none;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #CC0000;
    }
    .title {
        text-align: center;
        color: #FF0000;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">🎥 YouTube to MP4 Converter</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Download YouTube videos in high quality</div>', unsafe_allow_html=True)

# Create downloads directory
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def find_ffmpeg():
    """Find FFmpeg location on the system"""
    
    # PRIORITY 1: Check the exact WinGet location first
    username = os.environ.get('USERNAME', '')
    if username:
        winget_ffmpeg = rf"C:\Users\{username}\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
        if os.path.isfile(winget_ffmpeg):
            return winget_ffmpeg
    
    # PRIORITY 2: Search all WinGet FFmpeg installations
    try:
        if username:
            winget_base = Path(rf"C:\Users\{username}\AppData\Local\Microsoft\WinGet\Packages")
            if winget_base.exists():
                for folder in winget_base.glob("Gyan.FFmpeg*"):
                    for ffmpeg_exe in folder.rglob("ffmpeg.exe"):
                        if "bin" in str(ffmpeg_exe).lower():
                            return str(ffmpeg_exe.absolute())
    except Exception as e:
        pass
    
    # PRIORITY 3: Try to find ffmpeg using shutil.which
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        ffmpeg_path = os.path.abspath(ffmpeg_path)
        if os.path.isfile(ffmpeg_path):
            return ffmpeg_path
    
    # PRIORITY 4: Check current directory and subdirectories
    current_dir = Path.cwd()
    local_ffmpeg = [
        current_dir / "ffmpeg" / "ffmpeg.exe",
        current_dir / "ffmpeg" / "bin" / "ffmpeg.exe",
        current_dir / "ffmpeg.exe",
    ]
    
    for path in local_ffmpeg:
        if path.exists() and path.is_file():
            return str(path.absolute())
    
    # PRIORITY 5: Common Windows locations
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def get_video_info(url):
    """Get video information without downloading"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        return None

def download_video(url, quality, ffmpeg_location=None):
    """Download video with specified quality"""
    
    # Format selection based on quality
    if quality == "1080p":
        format_string = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
    elif quality == "720p":
        format_string = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
    elif quality == "480p":
        format_string = "bestvideo[height<=480]+bestaudio/best[height<=480]/best"
    elif quality == "360p":
        format_string = "bestvideo[height<=360]+bestaudio/best[height<=360]/best"
    else:
        format_string = "best"
    
    output_path = str(DOWNLOAD_DIR / "%(title)s.%(ext)s")
    
    ydl_opts = {
        'format': format_string,
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    
    # Validate and add FFmpeg location if provided
    if ffmpeg_location:
        # Ensure it's an absolute path to the executable
        if not os.path.isabs(ffmpeg_location):
            ffmpeg_location = os.path.abspath(ffmpeg_location)
        
        # If it's a directory, try to find ffmpeg.exe inside
        if os.path.isdir(ffmpeg_location):
            possible_exe = os.path.join(ffmpeg_location, "ffmpeg.exe")
            if os.path.isfile(possible_exe):
                ffmpeg_location = possible_exe
            else:
                possible_exe = os.path.join(ffmpeg_location, "bin", "ffmpeg.exe")
                if os.path.isfile(possible_exe):
                    ffmpeg_location = possible_exe
        
        # Verify the file exists
        if os.path.isfile(ffmpeg_location):
            ydl_opts['ffmpeg_location'] = ffmpeg_location
            st.info(f"✅ Using FFmpeg: {ffmpeg_location}")
        else:
            st.warning(f"⚠️ FFmpeg path invalid: {ffmpeg_location}")
            st.warning("⚠️ Falling back to basic download mode")
            ydl_opts['format'] = 'best[ext=mp4]/best'
    else:
        st.warning("⚠️ FFmpeg not found - using basic download mode (may have limited quality)")
        # Use format that doesn't require merging
        ydl_opts['format'] = 'best[ext=mp4]/best'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Try to find the downloaded file
            title = info['title']
            base_filename = ydl.prepare_filename(info)
            
            # Check multiple possible extensions
            possible_files = [
                base_filename,
                base_filename.rsplit('.', 1)[0] + '.mp4',
                base_filename.rsplit('.', 1)[0] + '.webm',
                base_filename.rsplit('.', 1)[0] + '.mkv',
            ]
            
            for filename in possible_files:
                if os.path.exists(filename):
                    return filename, title
            
            # If no file found, raise error
            raise Exception("Could not find downloaded file")
            
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

# Check for FFmpeg
ffmpeg_path = find_ffmpeg()

if ffmpeg_path:
    st.success(f"✅ FFmpeg detected at: {ffmpeg_path}")
    # Debug info
    with st.expander("🔍 FFmpeg Debug Info"):
        st.code(f"Path: {ffmpeg_path}")
        st.code(f"Is file: {os.path.isfile(ffmpeg_path)}")
        st.code(f"Is dir: {os.path.isdir(ffmpeg_path)}")
        st.code(f"Exists: {os.path.exists(ffmpeg_path)}")
else:
    st.error("❌ FFmpeg not found in system PATH")
    with st.expander("📖 How to fix this"):
        st.markdown("""
        ### Option 1: Install FFmpeg (Recommended)
        
        **Using Chocolatey (easiest):**
        ```bash
        choco install ffmpeg
        ```
        
        **Manual Installation:**
        1. Download from: https://www.gyan.dev/ffmpeg/builds/
        2. Download "ffmpeg-release-essentials.zip"
        3. Extract to `C:\\ffmpeg`
        4. Add `C:\\ffmpeg\\bin` to System PATH
        5. **Restart your computer**
        6. Restart this app
        
        ### Option 2: Specify FFmpeg location manually
        If you have FFmpeg installed but it's not detected, you can specify the path below.
        """)
    
    # Manual FFmpeg path input
    manual_ffmpeg = st.text_input("🔧 Enter FFmpeg path (optional)", 
                                   placeholder="C:\\ffmpeg\\bin\\ffmpeg.exe")
    if manual_ffmpeg and os.path.exists(manual_ffmpeg):
        ffmpeg_path = manual_ffmpeg
        st.success(f"✅ Using FFmpeg from: {ffmpeg_path}")

# Main interface
col1, col2 = st.columns([3, 1])

with col1:
    url = st.text_input("📎 Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

with col2:
    quality = st.selectbox("Quality", ["1080p", "720p", "480p", "360p"], index=1)

# Info section
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Copy URL**: Go to YouTube and copy the video URL
    2. **Paste URL**: Paste it in the input field above
    3. **Select Quality**: Choose your preferred video quality
    4. **Convert**: Click the convert button and wait
    5. **Download**: Click download button to save the video
    
    **Note**: If FFmpeg is not detected, you'll only be able to download pre-merged formats which may have limited quality options.
    """)

# Convert button
if st.button("🔄 Convert to MP4"):
    if not url:
        st.error("⚠️ Please enter a YouTube URL")
    elif not url.startswith(("https://www.youtube.com", "https://youtube.com", "https://youtu.be", "http://www.youtube.com", "http://youtube.com", "http://youtu.be")):
        st.error("⚠️ Please enter a valid YouTube URL")
    else:
        # Show video info first
        with st.spinner("📋 Fetching video information..."):
            video_info = get_video_info(url)
            
            if video_info:
                st.success("✅ Video found!")
                
                # Display video info
                col1, col2 = st.columns(2)
                with col1:
                    if video_info.get('thumbnail'):
                        st.image(video_info.get('thumbnail'), width=300)
                with col2:
                    st.write(f"**Title:** {video_info.get('title', 'N/A')}")
                    duration = video_info.get('duration', 0)
                    if duration > 0:
                        minutes = duration // 60
                        seconds = duration % 60
                        st.write(f"**Duration:** {minutes}:{seconds:02d}")
                    else:
                        st.write(f"**Duration:** N/A")
                    st.write(f"**Channel:** {video_info.get('uploader', 'N/A')}")
                
                # Download video
                progress_text = f"⬇️ Downloading video in {quality}... This may take a few minutes."
                with st.spinner(progress_text):
                    try:
                        filename, title = download_video(url, quality, ffmpeg_path)
                        st.success("✅ Download completed!")
                        
                        # Provide download button
                        if os.path.exists(filename):
                            with open(filename, 'rb') as file:
                                file_data = file.read()
                                
                                # Clean filename for download
                                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                                download_filename = f"{safe_title}.mp4"
                                
                                st.download_button(
                                    label="📥 Download MP4",
                                    data=file_data,
                                    file_name=download_filename,
                                    mime="video/mp4",
                                    key="download_button"
                                )
                            
                            # Show file size
                            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
                            st.info(f"💡 File size: {file_size_mb:.2f} MB - Click the button above to download.")
                            
                            # Clean up old files to save space
                            try:
                                for old_file in DOWNLOAD_DIR.glob("*"):
                                    if old_file != Path(filename):
                                        old_file.unlink()
                            except:
                                pass
                                
                        else:
                            st.error("❌ File not found after download")
                            
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Error: {error_msg}")
                        
                        if "ffmpeg" in error_msg.lower():
                            st.warning("⚠️ This error is related to FFmpeg. Please install FFmpeg using the instructions above and restart the app.")
                        else:
                            st.info("💡 Try selecting a different quality or check if the video is available in your region.")
            else:
                st.error("❌ Could not fetch video information. Please check the URL.")

# Features section
st.markdown("---")
st.markdown("### ✨ Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🚀 Fast Downloads**")
    st.markdown("Quick and efficient video downloading")

with col2:
    st.markdown("**🎯 High Quality**")
    st.markdown("Download up to 1080p quality")

with col3:
    st.markdown("**🔒 Safe & Secure**")
    st.markdown("No ads, completely safe")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>© 2026 YouTube to MP4 Converter. All rights reserved.</p>
        <p style='font-size: 12px;'>This tool is for personal use only. Respect copyright laws.</p>
    </div>
""", unsafe_allow_html=True)