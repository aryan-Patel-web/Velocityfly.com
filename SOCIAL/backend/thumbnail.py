"""
🎙️ VIDEO VOICE TRANSLATOR + THUMBNAIL GENERATOR
Complete single-file Streamlit app

Features:
- Video voice translation (Hindi ↔ English)
- Thumbnail generation (Hindi/Tamil/English)
- Speech-to-text, Translation, Text-to-speech
- CTR-optimized thumbnails

Installation:
    pip install streamlit opencv-python-headless pillow numpy httpx edge-tts
    
    # Install FFmpeg:
    # Ubuntu: sudo apt install ffmpeg
    # Mac: brew install ffmpeg
    # Windows: Download from ffmpeg.org

Usage:
    streamlit run video_translator_complete.py

API Key:
    Get FREE Groq API key from https://console.groq.com/
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import tempfile
import os
import httpx
import asyncio
import subprocess




# At the top of your file, after imports
GROQ_API_KEY = "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"

# In main() function, replace the sidebar input:
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = GROQ_API_KEY  # Use hardcoded key
    st.success("✅ API key configured")
# ============================================================
# CONFIGURATION
# ============================================================

LANGUAGES = {
    'hindi': {'name': '🇮🇳 Hindi (हिंदी)', 'code': 'hi', 'voice': 'hi-IN-SwaraNeural'},
    'english': {'name': '🇺🇸 English', 'code': 'en', 'voice': 'en-US-AriaNeural'},
    'tamil': {'name': '🇮🇳 Tamil (தமிழ்)', 'code': 'ta', 'voice': 'ta-IN-PallaviNeural'}
}

STYLES = [
    {'name': '🔴 Bold Red', 'bg': (255, 50, 50), 'text': (255, 255, 0), 'size': 90, 'stroke': 8},
    {'name': '⚫ High Contrast', 'bg': (0, 0, 0), 'text': (255, 255, 0), 'size': 85, 'stroke': 6},
    {'name': '🟠 Vibrant Orange', 'bg': (255, 140, 0), 'text': (255, 255, 255), 'size': 88, 'stroke': 7}
]

# ============================================================
# VIDEO FUNCTIONS
# ============================================================

def extract_audio(video_path):
    """Extract audio from video"""
    try:
        audio_path = video_path.replace('.mp4', '_audio.wav')
        cmd = ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_path, '-y']
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode == 0:
            st.success(f"✅ Audio extracted: {os.path.getsize(audio_path)/1024:.1f} KB")
            return audio_path
        st.error("❌ Audio extraction failed")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def extract_frames(video_path, num=3):
    """Extract frames from video"""
    try:
        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        st.info(f"📊 Video: {total} frames, {fps:.1f} fps")
        
        start = int(total * 0.1)
        end = int(total * 0.9)
        positions = np.linspace(start, end, num, dtype=int)
        
        frames = []
        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb).resize((1280, 720), Image.LANCZOS)
                frames.append(img)
        
        cap.release()
        return frames
    except Exception as e:
        st.error(f"❌ Frame extraction failed: {e}")
        return []

def combine_video_audio(video_path, audio_path, output_path):
    """Combine video with new audio"""
    try:
        cmd = ['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest', output_path, '-y']
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if result.returncode == 0:
            st.success(f"✅ Video created: {os.path.getsize(output_path)/(1024*1024):.1f} MB")
            return True
        st.error("❌ Video synthesis failed")
        return False
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return False

# ============================================================
# AI FUNCTIONS
# ============================================================

async def transcribe_audio(audio_path, api_key):
    """Speech to text"""
    try:
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        files = {'file': ('audio.wav', audio_data, 'audio/wav')}
        data = {'model': 'whisper-large-v3', 'response_format': 'verbose_json'}
        headers = {'Authorization': f'Bearer {api_key}'}
        
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post('https://api.groq.com/openai/v1/audio/transcriptions', headers=headers, files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                return {'text': result.get('text', ''), 'language': result.get('language', 'en')}
        return None
    except Exception as e:
        st.error(f"❌ Transcription failed: {e}")
        return None

async def translate_text(text, source, target, api_key):
    """Translate text"""
    try:
        if source == target:
            return text
        
        prompt = f"Translate from {LANGUAGES[source]['name']} to {LANGUAGES[target]['name']}. Return only translated text:\n\n{text}"
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'model': 'llama-3.1-70b-versatile', 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.3}
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip().strip('"\'')
        return text
    except Exception as e:
        st.error(f"❌ Translation failed: {e}")
        return text

async def text_to_speech(text, lang, output_path):
    """Text to speech"""
    try:
        voice = LANGUAGES[lang]['voice']
        cmd = ['edge-tts', '--voice', voice, '--text', text, '--write-media', output_path]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode == 0:
            st.success(f"✅ Speech: {os.path.getsize(output_path)/1024:.1f} KB")
            return True
        return False
    except Exception as e:
        st.error(f"❌ TTS failed: {e}")
        return False

# ============================================================
# THUMBNAIL FUNCTIONS
# ============================================================

def add_text_overlay(img, text, style):
    """Add text to image"""
    try:
        draw = ImageDraw.Draw(img)
        text = text[:40]
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", style['size'])
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = (1280 - w) // 2, 720 - h - 80
        
        draw.rectangle([(0, y - 30), (1280, y + h + 30)], fill=style['bg'])
        
        for dx in range(-style['stroke'], style['stroke'] + 1):
            for dy in range(-style['stroke'], style['stroke'] + 1):
                draw.text((x + dx, y + dy), text, fill=(0, 0, 0), font=font)
        
        draw.text((x, y), text, fill=style['text'], font=font)
        return img
    except Exception as e:
        st.error(f"❌ Text overlay failed: {e}")
        return img

def generate_thumbnails(frames, text):
    """Create thumbnails"""
    thumbs = []
    for i, frame in enumerate(frames):
        style = STYLES[i % len(STYLES)]
        thumb = add_text_overlay(frame.copy(), text, style)
        thumbs.append({'image': thumb, 'style': style['name']})
    return thumbs

# ============================================================
# HELPER
# ============================================================

def run_async(coro):
    """Run async function"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ============================================================
# MAIN APP
# ============================================================

def main():
    st.set_page_config(page_title="Video Translator", page_icon="🎙️", layout="wide")
    
    st.title("🎙️ Video Voice Translator + Thumbnail Generator")
    st.markdown("**Upload video → Translate voice → Generate thumbnails**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("Groq API Key", type="password", help="Get FREE key: https://console.groq.com/")
        
        if api_key:
            st.success("✅ API key set")
        else:
            st.warning("⚠️ Enter API key")
        
        st.markdown("---")
        st.markdown("""
        ### 🎯 Features
        - 🎙️ Speech-to-text
        - 🔄 Translation
        - 🗣️ Text-to-speech
        - 🎨 CTR Thumbnails""")

# """)

# Main tabs
tab1, tab2 = st.tabs(["📹 Video Translation", "🎨 Thumbnails"])

# TAB 1: Translation
with tab1:
    st.header("📹 Translate Video")
    
    video_file = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi'])
    
    if video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(video_file.read())
            video_path = tmp.name
        
        st.success(f"✅ Uploaded: {video_file.name}")
        st.video(video_path)
        
        col1, col2 = st.columns(2)
        with col1:
            source = st.selectbox("Original Language", options=['hindi', 'english'], format_func=lambda x: LANGUAGES[x]['name'])
        with col2:
            target = st.selectbox("Target Language", options=['hindi', 'english'], format_func=lambda x: LANGUAGES[x]['name'])
        
        if st.button("🚀 Translate Video", type="primary", disabled=not api_key or source == target):
            with st.spinner("Translating..."):
                progress = st.progress(0)
                
                # Extract audio
                st.info("🎵 Extracting audio...")
                progress.progress(20)
                audio_path = extract_audio(video_path)
                
                if audio_path:
                    # Transcribe
                    st.info("🎙️ Transcribing...")
                    progress.progress(40)
                    transcription = run_async(transcribe_audio(audio_path, api_key))
                    
                    if transcription:
                        original = transcription['text']
                        st.info(f"📝 Original: {original}")
                        
                        # Translate
                        st.info("🔄 Translating...")
                        progress.progress(60)
                        translated = run_async(translate_text(original, source, target, api_key))
                        st.success(f"✅ Translated: {translated}")
                        
                        # TTS
                        st.info("🗣️ Generating speech...")
                        progress.progress(80)
                        new_audio = video_path.replace('.mp4', '_new.mp3')
                        tts_ok = run_async(text_to_speech(translated, target, new_audio))
                        
                        if tts_ok:
                            # Combine
                            st.info("🎬 Creating video...")
                            progress.progress(95)
                            output = video_path.replace('.mp4', '_translated.mp4')
                            
                            if combine_video_audio(video_path, new_audio, output):
                                progress.progress(100)
                                st.balloons()
                                
                                st.markdown("---")
                                st.subheader("📹 Translated Video")
                                st.video(output)
                                
                                with open(output, 'rb') as f:
                                    st.download_button("⬇️ Download", f.read(), file_name=f"translated_{video_file.name}", mime="video/mp4")
                                
                                # Save for thumbnails
                                st.session_state['video'] = output
                                st.session_state['text'] = translated

# TAB 2: Thumbnails
with tab2:
    st.header("🎨 Generate Thumbnails")
    
    # Check if video exists
    video_path = None
    default_text = ''
    
    if 'video' in st.session_state:
        video_path = st.session_state['video']
        default_text = st.session_state.get('text', '')
    elif video_file and 'tmp' in locals():
        video_path = tmp.name
    
    if not video_path:
        st.info("👈 Upload and translate a video first")
    else:
        # Text input
        thumb_text = st.text_input("Thumbnail Text", value=default_text, help="Text to show on thumbnails")
        
        # Language selection
        thumb_lang = st.selectbox("Thumbnail Language", options=['hindi', 'english', 'tamil'], format_func=lambda x: LANGUAGES[x]['name'])
        
        if st.button("🎨 Generate Thumbnails", type="primary", disabled=not thumb_text):
            with st.spinner("Generating thumbnails..."):
                # Extract frames
                st.info("📸 Extracting frames...")
                frames = extract_frames(video_path, 3)
                
                if frames:
                    # Translate text if needed
                    if thumb_lang != 'english' and api_key:
                        st.info(f"🔄 Translating to {LANGUAGES[thumb_lang]['name']}...")
                        thumb_text = run_async(translate_text(thumb_text, 'english', thumb_lang, api_key))
                    
                    # Generate thumbnails
                    st.info("🎨 Creating thumbnails...")
                    thumbnails = generate_thumbnails(frames, thumb_text)
                    
                    st.success("✅ Thumbnails generated!")
                    
                    # Display thumbnails
                    st.markdown("---")
                    for i, thumb in enumerate(thumbnails):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.subheader(f"{thumb['style']}")
                            st.image(thumb['image'], use_container_width=True)
                        
                        with col2:
                            buf = io.BytesIO()
                            thumb['image'].save(buf, format='PNG')
                            st.download_button(
                                f"⬇️ Download",
                                buf.getvalue(),
                                file_name=f"thumbnail_{i+1}.png",
                                mime="image/png",
                                key=f"dl_{i}"
                            )
                        
                        st.markdown("---")