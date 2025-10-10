import streamlit as st
import requests
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import io
import threading
import uvicorn
import textwrap
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from rembg import remove
import cv2
import numpy as np
import yt_dlp
import tempfile
import os
from typing import Dict, Any

# --- Part 1: FastAPI Application ---

app = FastAPI(title="Advanced Thumbnail Generator API")

# --- Style Presets for "Auto" Mode ---
STYLE_PRESETS = {
    "Cinematic Punch": {
        "background_zoom": 1.2,
        "background_brightness": 0.8,
        "background_saturation": 1.1,
        "background_blur": 3,
        "vignette_effect": True,
        "title_font_size": 130,
        "subtitle_font_size": 60,
        "text_glow_color": "#FF8C00",
        "text_glow_radius": 5,
        "main_subject_pos_x": 600,
        "main_subject_pos_y": 80,
        "main_subject_size": 650,
        "secondary_subject_pos_x": 40,
        "secondary_subject_pos_y": 400,
        "secondary_subject_size": 300,
    },
    "Clean & Modern": {
        "background_zoom": 1.0,
        "background_brightness": 1.0,
        "background_saturation": 1.0,
        "background_blur": 1,
        "vignette_effect": False,
        "title_font_size": 120,
        "subtitle_font_size": 55,
        "text_glow_color": "#000000",
        "text_glow_radius": 0,
        "main_subject_pos_x": 680,
        "main_subject_pos_y": 120,
        "main_subject_size": 580,
        "secondary_subject_pos_x": 70,
        "secondary_subject_pos_y": 380,
        "secondary_subject_size": 320,
    },
    "Dynamic Action": {
        "background_zoom": 1.1,
        "background_brightness": 0.9,
        "background_saturation": 1.2,
        "background_blur": 2,
        "vignette_effect": True,
        "title_font_size": 125,
        "subtitle_font_size": 65,
        "text_glow_color": "#00FFFF",
        "text_glow_radius": 4,
        "main_subject_pos_x": 50,
        "main_subject_pos_y": 300,
        "main_subject_size": 450,
        "secondary_subject_pos_x": 550,
        "secondary_subject_pos_y": 100,
        "secondary_subject_size": 700,
    }
}


# --- Helper Functions for Image Processing ---

def remove_background_real(image_bytes):
    try:
        output_bytes = remove(image_bytes)
        return Image.open(io.BytesIO(output_bytes)).convert("RGBA")
    except Exception as e:
        print(f"Error in remove_background_real: {e}")
        return Image.open(io.BytesIO(image_bytes)).convert("RGBA")

def get_frame_sharpness(frame):
    if frame is None:
        return 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def add_text_with_effects(draw, text, font, position, fill_color, outline_color, shadow_color, 
                            outline_width=3, shadow_offset=(5, 5), wrap_width=25, 
                            glow_color=None, glow_radius=0):
    x, y = position
    lines = textwrap.wrap(text, width=wrap_width)
    
    try:
        line_height = font.getbbox("A")[3] + font.getmetrics()[1] * 0.2
    except AttributeError:
        line_height = font.getsize("A")[1]

    current_y = y
    for line in lines:
        if glow_color and glow_radius > 0:
            text_img = Image.new('RGBA', draw.im.size, (0,0,0,0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((x, current_y), line, font=font, fill=glow_color)
            blurred_text_img = text_img.filter(ImageFilter.GaussianBlur(radius=glow_radius))
            draw.im.paste(blurred_text_img, (0,0), blurred_text_img)

        shadow_pos = (x + shadow_offset[0], current_y + shadow_offset[1])
        draw.text(shadow_pos, line, font=font, fill=shadow_color)
        
        # Changed to a square outline as requested
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    outline_pos = (x + dx, current_y + dy)
                    draw.text(outline_pos, line, font=font, fill=outline_color)
                    
        draw.text((x, current_y), line, font=font, fill=fill_color)
        current_y += line_height

def apply_vignette(image, strength=0.3):
    width, height = image.size
    gradient_base = Image.new('RGBA', (width, height), (0, 0, 0, 255))
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    for i in range(min(width, height) // 2):
        alpha = int(255 * (i / (min(width, height) // 2))**2 * strength)
        draw.ellipse((i, i, width - i, height - i), fill=255 - alpha)
    vignette_overlay = Image.composite(Image.new('RGBA', (width, height), (0,0,0,0)), gradient_base, mask)
    return Image.alpha_composite(image, vignette_overlay)

def create_subject_shadow(subject_img_rgba, shadow_color=(0, 0, 0, 150), blur_radius=5, offset=(5, 5)):
    if subject_img_rgba is None or subject_img_rgba.mode != 'RGBA':
        return None
    alpha_channel = subject_img_rgba.split()[-1]
    shadow_base = Image.new('RGBA', subject_img_rgba.size, shadow_color)
    shadow_base.putalpha(alpha_channel)
    shadow_blurred = shadow_base.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    shadow_img = Image.new('RGBA', (subject_img_rgba.width + abs(offset[0]) + blur_radius*2, 
                                    subject_img_rgba.height + abs(offset[1]) + blur_radius*2), (0,0,0,0))
    shadow_img.paste(shadow_blurred, (offset[0] + blur_radius, offset[1] + blur_radius), shadow_blurred)
    return shadow_img


def create_single_thumbnail(base_elements: Dict[str, Any], style_params: Dict[str, Any]) -> Image:
    """Core logic to generate one thumbnail based on a set of style parameters."""
    thumbnail_width, thumbnail_height = 1280, 720
    
    # --- 1. Process Background ---
    background = base_elements['background'].copy()

    if style_params['background_zoom'] != 1.0:
        original_width, original_height = background.size
        cropped_width = int(original_width / style_params['background_zoom'])
        cropped_height = int(original_height / style_params['background_zoom'])
        if cropped_width > 0 and cropped_height > 0:
            left, top = (original_width - cropped_width) // 2, (original_height - cropped_height) // 2
            background = background.crop((left, top, left + cropped_width, top + cropped_height))

    background = background.resize((thumbnail_width, thumbnail_height), Image.LANCZOS)

    if style_params['background_brightness'] != 1.0 or style_params['background_saturation'] != 1.0:
        background_hsv = background.convert("HSV")
        h, s, v = background_hsv.split()
        s_array = np.array(s, dtype=np.float32) * style_params['background_saturation']
        s = Image.fromarray(np.uint8(np.clip(s_array, 0, 255)))
        v_array = np.array(v, dtype=np.float32) * style_params['background_brightness']
        v = Image.fromarray(np.uint8(np.clip(v_array, 0, 255)))
        background = Image.merge("HSV", (h, s, v)).convert("RGB")

    if style_params['background_blur'] > 0:
        background = background.filter(ImageFilter.GaussianBlur(radius=style_params['background_blur']))
    
    final_image = background.convert("RGBA")

    # --- 2. Place Subjects ---
    subjects_data = [
        (base_elements.get('main_subject'), style_params['main_subject_size'], style_params['main_subject_pos_x'], style_params['main_subject_pos_y']),
        (base_elements.get('secondary_subject'), style_params['secondary_subject_size'], style_params['secondary_subject_pos_x'], style_params['secondary_subject_pos_y'])
    ]

    for subject_img, size, pos_x, pos_y in subjects_data:
        if subject_img:
            if subject_img.width > 0:
                aspect_ratio = subject_img.height / subject_img.width
                new_height = int(size * aspect_ratio) if aspect_ratio > 0 else size
                resized_subject = subject_img.resize((size, new_height), Image.LANCZOS)
                
                shadow_offset = (int(size * 0.02), int(size * 0.02))
                shadow_blur = int(size * 0.01)
                subject_shadow = create_subject_shadow(resized_subject, offset=shadow_offset, blur_radius=shadow_blur)
                
                if subject_shadow:
                    shadow_paste_x = pos_x - shadow_offset[0] - shadow_blur
                    shadow_paste_y = pos_y - shadow_offset[1] - shadow_blur
                    final_image.paste(subject_shadow, (shadow_paste_x, shadow_paste_y), subject_shadow)

                final_image.paste(resized_subject, (pos_x, pos_y), resized_subject)

    # --- 3. Place Text ---
    text_overlay_image = Image.new('RGBA', final_image.size, (0,0,0,0))
    draw_text_overlay = ImageDraw.Draw(text_overlay_image)
    
    title_font = ImageFont.truetype("arial.ttf", style_params['title_font_size'])
    subtitle_font = ImageFont.truetype("arial.ttf", style_params['subtitle_font_size'])

    if base_elements['title_text']:
        add_text_with_effects(draw_text_overlay, base_elements['title_text'], title_font, (50, 50), 
                              base_elements['title_color'], base_elements['outline_color'], base_elements['shadow_color'], 
                              wrap_width=base_elements['title_wrap_width'], 
                              glow_color=style_params['text_glow_color'], glow_radius=style_params['text_glow_radius'])
    if base_elements['subtitle_text']:
        add_text_with_effects(draw_text_overlay, base_elements['subtitle_text'], subtitle_font, (50, 200),
                              base_elements['subtitle_color'], base_elements['outline_color'], base_elements['shadow_color'], 
                              wrap_width=base_elements['subtitle_wrap_width'],
                              glow_color=style_params['text_glow_color'], glow_radius=style_params['text_glow_radius'])
    
    final_image = Image.alpha_composite(final_image, text_overlay_image)

    # --- 4. Final Effects ---
    if style_params['vignette_effect']:
        final_image = apply_vignette(final_image)

    return final_image


# --- API Endpoint Definition ---

@app.post("/generate-thumbnail/", tags=["Thumbnail Generation"])
async def generate_thumbnail(
    # --- Mode ---
    generation_mode: str = Form("auto"),
    # --- Base Inputs ---
    background_file: UploadFile = File(None),
    video_file: UploadFile = File(None),
    youtube_url: str = Form(None),
    main_subject_file: UploadFile = File(None),
    secondary_subject_file: UploadFile = File(None),
    title_text: str = Form("Your Title Here"),
    subtitle_text: str = Form("A compelling subtitle"),
    # --- Manual Inputs (used only if generation_mode is 'manual') ---
    frame_search_start_percent: int = Form(45), background_zoom: float = Form(1.0), 
    background_brightness: float = Form(1.0), background_saturation: float = Form(1.0),
    title_font_size: int = Form(110), subtitle_font_size: int = Form(55),
    title_color: str = Form("#FFFFFF"), subtitle_color: str = Form("#DDDDDD"),
    outline_color: str = Form("#000000"), shadow_color: str = Form("#222222"),
    text_glow_color: str = Form("#FFD700"), text_glow_radius: int = Form(0),
    background_blur: int = Form(2), vignette_effect: bool = Form(True),
    title_wrap_width: int = Form(20), subtitle_wrap_width: int = Form(35),
    main_subject_pos_x: int = Form(650), main_subject_pos_y: int = Form(100), main_subject_size: int = Form(600),
    secondary_subject_pos_x: int = Form(50), secondary_subject_pos_y: int = Form(350), secondary_subject_size: int = Form(350)
):
    thumbnail_width, thumbnail_height = 1280, 720
    background = None
    cap = None

    # --- 1. Prepare Base Elements (run once) ---
    if background_file:
        background = Image.open(io.BytesIO(await background_file.read())).convert("RGB")
    elif youtube_url:
        try:
            ydl_opts = {'format': 'best[ext=mp4]', 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                cap = cv2.VideoCapture(info['url'])
        except Exception as e:
            print(f"Error fetching YouTube URL: {e}")
    elif video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await video_file.read())
            tmp_path = tmp.name
        cap = cv2.VideoCapture(tmp_path)
    else:
        background = Image.new('RGB', (thumbnail_width, thumbnail_height), '#1E293B')

    if cap and cap.isOpened():
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames > 0:
            best_frame, max_sharpness = None, -1
            start_frame = int(total_frames * (frame_search_start_percent / 100.0))
            end_frame = min(start_frame + 90, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            current_frame_pos = start_frame
            while current_frame_pos < end_frame:
                ret, frame = cap.read()
                if not ret: break
                sharpness = get_frame_sharpness(frame)
                if sharpness > max_sharpness:
                    max_sharpness, best_frame = sharpness, frame
                current_frame_pos += 1
            if best_frame is not None:
                background = Image.fromarray(cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB))
        cap.release()
        if 'tmp_path' in locals() and os.path.exists(tmp_path): os.unlink(tmp_path)

    if background is None: background = Image.new('RGB', (thumbnail_width, thumbnail_height), 'red')

    base_elements = {
        "background": background,
        "main_subject": remove_background_real(await main_subject_file.read()) if main_subject_file else None,
        "secondary_subject": remove_background_real(await secondary_subject_file.read()) if secondary_subject_file else None,
        "title_text": title_text, "subtitle_text": subtitle_text,
        "title_color": title_color, "subtitle_color": subtitle_color,
        "outline_color": outline_color, "shadow_color": shadow_color,
        "title_wrap_width": title_wrap_width, "subtitle_wrap_width": subtitle_wrap_width
    }
    
    # --- 2. Generate Thumbnails ---
    thumbnails = []
    if generation_mode == "auto":
        for style_name, params in STYLE_PRESETS.items():
            try:
                thumb = create_single_thumbnail(base_elements, params)
                thumbnails.append(thumb)
            except Exception as e:
                print(f"Error generating style '{style_name}': {e}")
    else: # Manual mode
        manual_params = {k: locals()[k] for k in STYLE_PRESETS["Clean & Modern"].keys()}
        thumb = create_single_thumbnail(base_elements, manual_params)
        thumbnails.append(thumb)

    # --- 3. Combine and Return ---
    if not thumbnails: return StreamingResponse(status_code=500, content=b"Failed to generate any thumbnails.")
    
    if len(thumbnails) > 1:
        # Create a vertical strip for the 3 options
        combined_image = Image.new('RGB', (thumbnail_width, thumbnail_height * len(thumbnails)))
        for i, thumb in enumerate(thumbnails):
            combined_image.paste(thumb, (0, i * thumbnail_height))
    else:
        combined_image = thumbnails[0]
        
    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/png")


# --- Function to run Uvicorn server in a thread ---
def run_fastapi_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

fastapi_thread = threading.Thread(target=run_fastapi_server, daemon=True)
fastapi_thread.start()

# --- Part 2: Streamlit Frontend ---
FASTAPI_URL = "http://127.0.0.1:8000/generate-thumbnail/"
st.set_page_config(page_title="Pro Thumbnail Generator", layout="wide")

st.title("🚀 AI-Assisted Thumbnail Generator")
st.markdown("Generate multiple professional styles automatically, or switch to manual mode for full control.")

# --- UI Layout with Tabs ---
auto_tab, manual_tab = st.tabs(["🤖 Auto Magic", "🎛️ Manual Studio"])

# --- Auto Magic Tab ---
with auto_tab:
    st.header("1. Upload Your Assets")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Background Source")
        background_file_auto = st.file_uploader("Image", type=["png", "jpg"], key="bg_auto")
        video_file_auto = st.file_uploader("Video", type=["mp4", "mov"], key="vid_auto")
        youtube_url_auto = st.text_input("YouTube URL", key="url_auto")
    with col2:
        st.subheader("Subject Layers")
        main_subject_file_auto = st.file_uploader("Main Subject", type=["png", "jpg"], key="main_auto")
        secondary_subject_file_auto = st.file_uploader("Secondary Subject", type=["png", "jpg"], key="sec_auto")

    st.header("2. Add Your Text")
    title_text_auto = st.text_input("Title Text", "IMPOSSIBLE!", key="title_auto")
    subtitle_text_auto = st.text_input("Subtitle Text", "This changes everything", key="subtitle_auto")

    st.header("3. Generate!")
    generate_auto_button = st.button("✨ Generate 3 AI-Styled Variations", use_container_width=True, type="primary")
    
    if generate_auto_button:
        form_data = { "generation_mode": "auto", 'title_text': title_text_auto, 'subtitle_text': subtitle_text_auto }
        files_to_upload = {}
        if background_file_auto: files_to_upload['background_file'] = background_file_auto.getvalue()
        if video_file_auto: files_to_upload['video_file'] = video_file_auto.getvalue()
        if main_subject_file_auto: files_to_upload['main_subject_file'] = main_subject_file_auto.getvalue()
        if secondary_subject_file_auto: files_to_upload['secondary_subject_file'] = secondary_subject_file_auto.getvalue()
        if youtube_url_auto: form_data['youtube_url'] = youtube_url_auto

        with st.spinner("Generating 3 professional styles for you..."):
            try:
                response = requests.post(FASTAPI_URL, data=form_data, files=files_to_upload, timeout=180)
                if response.status_code == 200:
                    st.session_state.image = Image.open(io.BytesIO(response.content))
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- Manual Studio Tab ---
with manual_tab:
    with st.sidebar:
        st.header("Manual Controls")
        st.header("🎨 1. Background Source")
        background_file = st.file_uploader("Upload an image", type=["png", "jpg"], key="bg_manual")
        video_file = st.file_uploader("Upload a video", type=["mp4", "mov"], key="vid_manual")
        youtube_url = st.text_input("Or paste a YouTube URL", key="url_manual")
        frame_search_start_percent = st.slider("Frame search start (%)", 0, 100, 45)

        with st.expander("Background Adjustments"):
            background_zoom = st.slider("Zoom", 1.0, 3.0, 1.0, 0.1)
            background_brightness = st.slider("Brightness", 0.1, 2.0, 1.0, 0.1)
            background_saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
            background_blur = st.slider("Blur", 0, 20, 2)
            vignette_effect = st.checkbox("Vignette", True)

        st.header("🎭 2. Subject Layers")
        main_subject_file = st.file_uploader("Main subject", type=["png", "jpg"], key="main_manual")
        secondary_subject_file = st.file_uploader("Secondary subject", type=["png", "jpg"], key="sec_manual")
        
        st.header("✍️ 3. Text Layers")
        title_text = st.text_input("Title Text", "IMPOSSIBLE!", key="title_manual")
        subtitle_text = st.text_input("Subtitle Text", "This changes everything", key="subtitle_manual")

        with st.expander("Text Styling"):
            c1, c2 = st.columns(2)
            title_font_size = c1.slider("Title Size", 10, 250, 110)
            title_color = c1.color_picker("Title Color", "#FFFFFF")
            outline_color = c1.color_picker("Outline Color", "#000000")
            title_wrap_width = c1.number_input("Title Wrap", 1, 100, 20)
            subtitle_font_size = c2.slider("Subtitle Size", 10, 200, 55)
            subtitle_color = c2.color_picker("Subtitle Color", "#DDDDDD")
            shadow_color = c2.color_picker("Shadow Color", "#222222")
            subtitle_wrap_width = c2.number_input("Subtitle Wrap", 1, 100, 35)
            text_glow_color = st.color_picker("Glow Color", "#FFD700")
            text_glow_radius = st.slider("Glow Radius", 0, 20, 0)

        with st.expander("Position & Size"):
            st.markdown("##### Main Subject")
            c1,c2,c3 = st.columns(3)
            main_subject_pos_x, main_subject_pos_y, main_subject_size = c1.slider("X",-200,1280,650), c2.slider("Y",-200,720,100), c3.slider("Size",50,1500,600)
            st.markdown("##### Secondary Subject")
            c1,c2,c3 = st.columns(3)
            secondary_subject_pos_x, secondary_subject_pos_y, secondary_subject_size = c1.slider("X",-200,1280,50), c2.slider("Y",-200,720,350), c3.slider("Size",50,1000,350)

    generate_manual_button = st.button("🔧 Generate Thumbnail", use_container_width=True)
    if generate_manual_button:
        form_data = locals()
        form_data["generation_mode"] = "manual"
        files_to_upload = {}
        if background_file: files_to_upload['background_file'] = background_file.getvalue()
        if video_file: files_to_upload['video_file'] = video_file.getvalue()
        if main_subject_file: files_to_upload['main_subject_file'] = main_subject_file.getvalue()
        if secondary_subject_file: files_to_upload['secondary_subject_file'] = secondary_subject_file.getvalue()
        
        with st.spinner("Building your custom thumbnail..."):
            try:
                response = requests.post(FASTAPI_URL, data=form_data, files=files_to_upload, timeout=180)
                if response.status_code == 200:
                    st.session_state.image = Image.open(io.BytesIO(response.content))
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")


# --- Main Content Area for Image Display ---
if 'image' not in st.session_state: st.session_state.image = None

image_placeholder = st.empty()
if st.session_state.image:
    st.success("Generation complete! Here are your results.")
    image_placeholder.image(st.session_state.image, use_column_width=True)
else:
    image_placeholder.info("Your generated thumbnails will appear here. Start by uploading assets in one of the tabs.")
