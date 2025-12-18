import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import time
from urllib.parse import quote
import random

# Page config
st.set_page_config(page_title="YouTube Thumbnail Generator", page_icon="🎬", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(to right, #ff0000, #ff4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff0000;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎬 YouTube Thumbnail Generator</h1>', unsafe_allow_html=True)

# Initialize session state
if 'generated_images' not in st.session_state:
    st.session_state['generated_images'] = {}

# Sidebar
with st.sidebar:
    st.header("⚡ Generation Mode")
    
    generation_mode = st.radio(
        "Choose Speed",
        ["🚀 Ultra Fast (3-5s)", 
         "⚡ Fast (5-8s)",
         "🎨 Quality (10-15s)",
         "🔥 All Modes (Compare)"],
        help="Faster = quicker results, Quality = better images"
    )
    
    st.divider()
    
    st.header("🎨 Style Presets")
    style_preset = st.selectbox(
        "Choose Style",
        ["Gaming (Cinematic)", "Tech/Tutorial", "Vlog Style", "Professional", "Anime/Cartoon", "Cyberpunk", "Minimalist", "Custom"]
    )
    
    if style_preset == "Custom":
        custom_style = st.text_area("Custom Style", placeholder="e.g., cyberpunk, neon, futuristic")
    
    st.divider()
    
    st.header("📐 Settings")
    
    width = st.slider("Width", 640, 1920, 1280, 64)
    height = st.slider("Height", 360, 1080, 720, 36)
    
    add_text_overlay_option = st.checkbox("Add Title Overlay", value=True)
    enhance_colors = st.checkbox("Enhance Colors", value=True)
    sharpen_image = st.checkbox("Fix Blur (Sharpen)", value=True)
    
    st.divider()
    st.success("✅ No API Keys Required!")

# Style mappings
style_keywords = {
    "Gaming (Cinematic)": "epic cinematic gaming setup, dramatic volumetric lighting, RGB gaming PC with vibrant neon lights, photorealistic, ultra detailed, 8k quality, professional photography, dynamic composition",
    "Tech/Tutorial": "clean professional tech workspace, modern minimalist design, bright studio lighting, sharp focus, high resolution, youtube thumbnail style, crisp and clear",
    "Vlog Style": "warm inviting lifestyle aesthetic, natural lighting, cozy personal space, bright cheerful atmosphere, high quality photograph, friendly vibe",
    "Professional": "corporate professional environment, clean modern design, perfect studio lighting, business aesthetic, ultra sharp, premium quality, sleek design",
    "Anime/Cartoon": "vibrant anime art style, manga aesthetic, bold vivid colors, digital illustration, high detail anime artwork, expressive characters",
    "Cyberpunk": "cyberpunk neon aesthetic, futuristic technology, synthwave purple and blue colors, dramatic lighting, sci-fi atmosphere, glowing elements",
    "Minimalist": "clean minimalist design, simple elegant composition, modern aesthetic, professional lighting, clear focus, sophisticated style",
}

def generate_prompt(title, description, style, additional_keywords=""):
    """Generate optimized prompt"""
    if style == "Custom":
        style_desc = st.session_state.get('custom_style', custom_style if 'custom_style' in locals() else "")
    else:
        style_desc = style_keywords.get(style, "")
    
    prompt = f"""YouTube thumbnail: {title}. {description}. 
    {style_desc}. {additional_keywords}. 
    professional, eye-catching, vibrant colors, high quality, sharp focus, detailed"""
    
    return ' '.join(prompt.split())

# Multiple API endpoints (all free, no keys)
def try_pollinations_v1(prompt, width, height):
    """Pollinations API v1 - Fast"""
    try:
        encoded = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&enhance=true"
        response = requests.get(url, timeout=10)
        return response.content if response.status_code == 200 else None
    except:
        return None

def try_pollinations_v2(prompt, width, height):
    """Pollinations API v2 - Alternative endpoint"""
    try:
        encoded = quote(prompt)
        url = f"https://pollinations.ai/p/{encoded}?width={width}&height={height}&nologo=1&enhance=1"
        response = requests.get(url, timeout=15)
        return response.content if response.status_code == 200 else None
    except:
        return None

def try_craiyon(prompt):
    """Craiyon API - Free, no key needed"""
    try:
        url = "https://api.craiyon.com/v3"
        data = {"prompt": prompt, "version": "35s5hfwn9n78gb06", "negative_prompt": "blurry, low quality"}
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'images' in result and len(result['images']) > 0:
                import base64
                image_data = base64.b64decode(result['images'][0])
                return image_data
        return None
    except:
        return None

def try_imagine_api(prompt, width, height):
    """Imagine API - Free alternative"""
    try:
        encoded = quote(prompt)
        url = f"https://api.vyro.ai/v1/imagine/api/generations?prompt={encoded}&width={width}&height={height}"
        response = requests.get(url, timeout=20)
        return response.content if response.status_code == 200 else None
    except:
        return None

def try_prodia(prompt, width, height):
    """Prodia API - Free, fast"""
    try:
        url = "https://api.prodia.com/generate"
        data = {
            "prompt": prompt,
            "model": "dreamshaper_8.safetensors",
            "negative_prompt": "blurry, bad quality, watermark",
            "steps": 20,
            "cfg_scale": 7,
            "width": min(width, 1024),
            "height": min(height, 1024),
            "sampler": "DPM++ 2M Karras"
        }
        response = requests.post(url, json=data, timeout=25)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job')
            
            # Poll for result
            for _ in range(10):
                time.sleep(2)
                check_url = f"https://api.prodia.com/job/{job_id}"
                check_response = requests.get(check_url, timeout=10)
                
                if check_response.status_code == 200:
                    job_data = check_response.json()
                    if job_data.get('status') == 'succeeded':
                        image_url = job_data.get('imageUrl')
                        img_response = requests.get(image_url, timeout=10)
                        return img_response.content
        return None
    except:
        return None

def smart_generate(prompt, width, height, mode):
    """Smart generation with fallback"""
    apis_by_mode = {
        "Ultra Fast": [try_pollinations_v1],
        "Fast": [try_pollinations_v1, try_pollinations_v2],
        "Quality": [try_pollinations_v2, try_pollinations_v1, try_imagine_api],
    }
    
    apis_to_try = apis_by_mode.get(mode, [try_pollinations_v1, try_pollinations_v2])
    
    for api_func in apis_to_try:
        try:
            result = api_func(prompt, width, height)
            if result:
                return result, api_func.__name__.replace('try_', '').replace('_', ' ').title()
        except:
            continue
    
    return None, "Failed"

def enhance_image_quality(image_bytes):
    """Enhance image quality"""
    img = Image.open(io.BytesIO(image_bytes))
    
    if sharpen_image:
        img = img.filter(ImageFilter.UnsharpMask(radius=2.5, percent=180, threshold=3))
    
    if enhance_colors:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.35)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.25)
        
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
    
    if sharpen_image:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.4)
    
    buf = io.BytesIO()
    img.save(buf, format='PNG', quality=98)
    return buf.getvalue()

def add_professional_overlay(image_bytes, title):
    """Add text overlay"""
    img = Image.open(io.BytesIO(image_bytes))
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    try:
        font_size = min(int(img.height / 9), 90)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        title_font = ImageFont.load_default()
    
    max_chars = 35
    if len(title) > max_chars:
        words = title.split()
        line1, line2 = "", ""
        for word in words:
            if len(line1) < max_chars:
                line1 += word + " "
            else:
                line2 += word + " "
        lines = [line1.strip(), line2.strip()]
    else:
        lines = [title]
    
    bar_height = 220 if len(lines) > 1 else 170
    bar_y = img.height - bar_height - 20
    draw.rectangle([(0, bar_y), (img.width, img.height)], fill=(0, 0, 0, 160))
    
    y_position = img.height - 180 if len(lines) > 1 else img.height - 130
    
    for i, line in enumerate(lines):
        if not line:
            continue
        text_position = (50, y_position + (i * (font_size + 10)))
        
        # Shadow
        for offset in range(-6, 7, 2):
            draw.text(
                (text_position[0] + offset, text_position[1] + offset),
                line, font=title_font, fill=(0, 0, 0, 255)
            )
        
        # Main text
        draw.text(text_position, line, font=title_font, fill=(255, 255, 255, 255))
    
    # Red accent bar
    bar_y = img.height - 35
    draw.rectangle([(40, bar_y), (min(600, img.width - 40), bar_y + 12)], fill=(255, 0, 0, 255))
    
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    return img.convert('RGB')

# Main UI
st.subheader("📝 Video Information")

col1, col2 = st.columns([1, 1])

with col1:
    video_title = st.text_input(
        "Video Title *",
        value="Build Your Dream Workstation in 2024 - Complete Setup Guide",
        placeholder="Enter your YouTube video title"
    )
    
    video_description = st.text_area(
        "Video Description",
        value="Step-by-step guide to building the perfect productivity workstation. Monitor setup, cable management, and lighting optimization.",
        height=100
    )

with col2:
    additional_prompt = st.text_input(
        "Additional Keywords",
        value="dual monitors, clean desk, modern workspace, LED strips, minimalist"
    )
    
    negative_prompt = st.text_input(
        "Exclude",
        value="blurry, low quality, distorted, watermark"
    )

# Generate button
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("🚀 GENERATE THUMBNAIL", type="primary")

if generate_button:
    if not video_title:
        st.error("⚠️ Please enter a video title!")
    else:
        full_prompt = generate_prompt(video_title, video_description, style_preset, additional_prompt)
        
        if negative_prompt:
            full_prompt += f". Negative: {negative_prompt}"
        
        st.info(f"**🎨 Prompt:** {full_prompt[:180]}...")
        
        st.session_state['generated_images'] = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        modes_to_try = []
        if "Ultra Fast" in generation_mode:
            modes_to_try = [("Ultra Fast", 0.3)]
        elif "Fast" in generation_mode:
            modes_to_try = [("Fast", 0.5)]
        elif "Quality" in generation_mode:
            modes_to_try = [("Quality", 0.7)]
        elif "All" in generation_mode:
            modes_to_try = [("Ultra Fast", 0.3), ("Fast", 0.5), ("Quality", 0.7)]
        
        for mode, progress_weight in modes_to_try:
            status_text.text(f"⚡ Generating {mode} version...")
            progress_bar.progress(int(progress_weight * 40))
            
            start_time = time.time()
            image_bytes, api_used = smart_generate(full_prompt, width, height, mode)
            elapsed = time.time() - start_time
            
            if image_bytes:
                progress_bar.progress(int(progress_weight * 60))
                status_text.text(f"🎨 Enhancing {mode} quality...")
                
                try:
                    image_bytes = enhance_image_quality(image_bytes)
                    
                    progress_bar.progress(int(progress_weight * 80))
                    
                    if add_text_overlay_option:
                        final_image = add_professional_overlay(image_bytes, video_title)
                    else:
                        final_image = Image.open(io.BytesIO(image_bytes))
                    
                    final_image = final_image.resize((width, height), Image.Resampling.LANCZOS)
                    
                    st.session_state['generated_images'][mode] = {
                        'image': final_image,
                        'time': elapsed,
                        'api': api_used
                    }
                    
                    status_text.text(f"✅ {mode} ready in {elapsed:.1f}s!")
                    progress_bar.progress(int(progress_weight * 100))
                except Exception as e:
                    status_text.text(f"⚠️ {mode} enhancement failed, trying next...")
            else:
                status_text.text(f"⚠️ {mode} generation failed, trying next...")
        
        progress_bar.progress(100)
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        if not st.session_state['generated_images']:
            st.error("❌ Generation failed. Please try again or check your internet connection.")
            st.info("💡 Tip: Try selecting a different generation mode or simplify your prompt.")

# Display results
if st.session_state['generated_images']:
    st.divider()
    st.header("📸 Generated Thumbnails")
    
    if len(st.session_state['generated_images']) == 1:
        mode = list(st.session_state['generated_images'].keys())[0]
        data = st.session_state['generated_images'][mode]
        
        st.subheader(f"🎨 {mode} Mode - {data['time']:.1f}s")
        st.caption(f"Generated using: {data['api']}")
        st.image(data['image'], use_column_width=True)
        
        buf = io.BytesIO()
        data['image'].save(buf, format='PNG', quality=98)
        st.download_button(
            label="📥 Download Thumbnail",
            data=buf.getvalue(),
            file_name=f"thumbnail_{video_title[:30].replace(' ', '_')}.png",
            mime="image/png"
        )
    else:
        cols = st.columns(len(st.session_state['generated_images']))
        
        for idx, (mode, data) in enumerate(st.session_state['generated_images'].items()):
            with cols[idx]:
                st.subheader(f"🎨 {mode}")
                st.caption(f"⏱️ {data['time']:.1f}s | {data['api']}")
                st.image(data['image'], use_column_width=True)
                
                buf = io.BytesIO()
                data['image'].save(buf, format='PNG', quality=98)
                st.download_button(
                    label="📥 Download",
                    data=buf.getvalue(),
                    file_name=f"thumbnail_{mode.replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"download_{mode}"
                )

# Tips
st.divider()
st.header("💡 Generation Tips")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **⚡ Speed Options:**
    - Ultra Fast: 3-5s
    - Fast: 5-8s
    - Quality: 10-15s
    - All Modes: Compare all
    """)

with col2:
    st.markdown("""
    **🎨 Quality Tips:**
    - Enable "Fix Blur" always
    - Use Quality mode for final
    - Add specific keywords
    - Try different styles
    """)

with col3:
    st.markdown("""
    **🎯 Best Practices:**
    - Clear, specific titles
    - Descriptive keywords
    - Test multiple modes
    - Download best result
    """)

st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
<p><strong>✅ 100% Free - No API Keys Required!</strong></p>
<p>Smart fallback system tries multiple APIs automatically for best results</p>
</div>
""", unsafe_allow_html=True)