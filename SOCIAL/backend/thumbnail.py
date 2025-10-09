"""
Dynamic Static Thumbnails - Looks Animated But YouTube-Compatible
Creates single static image with motion effects
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import math
import numpy as np

def draw_speed_lines(canvas: Image.Image, direction: str = "right"):
    """Draw speed lines to suggest motion"""
    
    draw = ImageDraw.Draw(canvas, 'RGBA')
    width, height = canvas.size
    
    for i in range(50):
        # Random line positions
        y = int(height * (i / 50))
        
        # Speed line characteristics
        line_length = 100 + (i % 10) * 50
        alpha = 100 - (i % 5) * 20
        thickness = 2 + (i % 3)
        
        if direction == "right":
            start = (0, y)
            end = (line_length, y + 20)
        else:
            start = (width - line_length, y)
            end = (width, y - 20)
        
        draw.line([start, end], fill=(255, 255, 255, alpha), width=thickness)

def create_motion_trail(face_image: Image.Image, num_copies: int = 5) -> Image.Image:
    """Create motion trail effect with face"""
    
    # Create transparent canvas
    width = 1920
    height = 1080
    canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Face size
    face_size = 600
    face_resized = face_image.resize((face_size, face_size), Image.Resampling.LANCZOS)
    
    # Create motion trail (multiple copies with decreasing opacity)
    for i in range(num_copies):
        # Position (moves from left to right)
        progress = i / (num_copies - 1)
        x = int(200 + progress * 700)
        y = int(200 + math.sin(progress * math.pi) * 100)
        
        # Opacity (decreases for older positions)
        opacity = int(255 * (0.3 + 0.7 * progress))
        
        # Create copy
        face_copy = face_resized.copy()
        
        # Apply blur to older positions
        blur_amount = int((1 - progress) * 5)
        if blur_amount > 0:
            face_copy = face_copy.filter(ImageFilter.GaussianBlur(blur_amount))
        
        # Adjust opacity
        if face_copy.mode != 'RGBA':
            face_copy = face_copy.convert('RGBA')
        
        alpha = face_copy.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 255)
        face_copy.putalpha(alpha)
        
        # Paste on canvas
        canvas.paste(face_copy, (x, y), face_copy)
    
    return canvas

def create_dynamic_thumbnail(
    face_image: Image.Image,
    title: str,
    effect: str = "motion_trail"
) -> Image.Image:
    """
    Create single static thumbnail that LOOKS animated
    
    Effects:
    - motion_trail: Face moving with trail
    - triple: 3 faces side-by-side
    - explosion: Energetic burst effect
    """
    
    # Create background with gradient
    background = Image.new('RGB', (1920, 1080))
    
    # Gradient background
    for y in range(1080):
        ratio = y / 1080
        r = int(180 * (1 - ratio) + 255 * ratio)
        g = int(0 * (1 - ratio) + 69 * ratio)
        b = int(0 * (1 - ratio) + 0 * ratio)
        
        ImageDraw.Draw(background).line([(0, y), (1920, y)], fill=(r, g, b))
    
    if effect == "motion_trail":
        # Draw speed lines
        draw_speed_lines(background, "right")
        
        # Create motion trail
        motion_layer = create_motion_trail(face_image, num_copies=5)
        
        # Composite
        background = background.convert('RGBA')
        background = Image.alpha_composite(background, motion_layer)
        background = background.convert('RGB')
    
    elif effect == "triple":
        # Show 3 versions side-by-side
        face_positions = [300, 810, 1320]
        
        for i, x in enumerate(face_positions):
            face_sized = face_image.resize((500, 500), Image.Resampling.LANCZOS)
            
            # Apply different color tints
            if i == 0:
                # Red tint (shocked)
                array = np.array(face_sized)
                array[:,:,0] = np.clip(array[:,:,0] * 1.3, 0, 255)
                face_sized = Image.fromarray(array.astype(np.uint8))
            elif i == 1:
                # Yellow tint (excited)
                array = np.array(face_sized)
                array[:,:,0] = np.clip(array[:,:,0] * 1.2, 0, 255)
                array[:,:,1] = np.clip(array[:,:,1] * 1.2, 0, 255)
                face_sized = Image.fromarray(array.astype(np.uint8))
            
            # Paste
            background.paste(face_sized, (x - 250, 290))
            
            # Add arrow between faces
            if i < 2:
                draw = ImageDraw.Draw(background)
                arrow_x = x + 250
                arrow_y = 540
                draw.polygon(
                    [(arrow_x, arrow_y - 50), (arrow_x, arrow_y + 50), (arrow_x + 60, arrow_y)],
                    fill=(255, 255, 255)
                )
    
    elif effect == "explosion":
        # Draw explosion rays from center
        draw = ImageDraw.Draw(background, 'RGBA')
        center_x, center_y = 960, 540
        
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            end_x = int(center_x + math.cos(rad) * 1000)
            end_y = int(center_y + math.sin(rad) * 1000)
            
            alpha = 150 if angle % 30 == 0 else 80
            draw.line(
                [(center_x, center_y), (end_x, end_y)],
                fill=(255, 215, 0, alpha),
                width=5
            )
        
        # Add face in center with glow
        face_sized = face_image.resize((700, 700), Image.Resampling.LANCZOS)
        
        # Create glow
        glow = Image.new('RGBA', (750, 750), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        
        for i in range(50):
            alpha = int(200 * (1 - i / 50))
            glow_draw.ellipse([i, i, 750-i, 750-i], fill=(255, 255, 0, alpha))
        
        # Composite
        background_rgba = background.convert('RGBA')
        background_rgba.paste(glow, (960 - 375, 540 - 375), glow)
        background_rgba.paste(face_sized, (960 - 350, 540 - 350), face_sized if face_sized.mode == 'RGBA' else None)
        background = background_rgba.convert('RGB')
    
    # Add text
    background = add_dynamic_text(background, title)
    
    # Enhance
    enhancer = ImageEnhance.Contrast(background)
    background = enhancer.enhance(1.3)
    
    enhancer = ImageEnhance.Color(background)
    background = enhancer.enhance(1.4)
    
    return background

def add_dynamic_text(image: Image.Image, text: str) -> Image.Image:
    """Add text with dynamic effects"""
    
    draw = ImageDraw.Draw(image)
    
    # Try to load font
    try:
        font = ImageFont.truetype("C:\\Windows\\Fonts\\impact.ttf", 150)
    except:
        font = ImageFont.load_default()
    
    # Extract keywords
    words = text.upper().split()[:4]
    text_display = " ".join(words)
    
    # Position
    x, y = 100, 100
    
    # Shadow
    for offset in range(8):
        draw.text((x + offset + 5, y + offset + 5), text_display, font=font, fill=(0, 0, 0))
    
    # Outline
    for dx in range(-12, 13, 3):
        for dy in range(-12, 13, 3):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text_display, font=font, fill=(0, 0, 0))
    
    # Glow
    for dx in range(-6, 7, 2):
        for dy in range(-6, 7, 2):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text_display, font=font, fill=(255, 215, 0))
    
    # Main text
    draw.text((x, y), text_display, font=font, fill=(255, 255, 255))
    
    return image

# =============================================================================
# STREAMLIT UI
# =============================================================================

def main():
    st.set_page_config(page_title="Dynamic Static Thumbnails", page_icon="⚡")
    
    st.title("⚡ Dynamic Static Thumbnail Generator")
    st.markdown("Creates **STATIC** images that **LOOK** animated (YouTube-compatible!)")
    
    st.info("💡 **Important:** YouTube doesn't support animated GIFs. These thumbnails LOOK dynamic but are single static images.")
    
    # Upload face
    st.header("📸 Upload Your Face Photo")
    uploaded = st.file_uploader("Choose photo", type=['jpg', 'png', 'jpeg'])
    
    if uploaded:
        face_image = Image.open(uploaded)
        st.image(face_image, caption="Your Photo", width=300)
        
        # Title input
        st.header("📝 Enter Video Title")
        title = st.text_input("Title", placeholder="Amazing Tech Review!")
        
        # Effect selection
        st.header("🎨 Choose Effect")
        effect = st.radio(
            "Select dynamic effect:",
            ["motion_trail", "triple", "explosion"],
            format_func=lambda x: {
                "motion_trail": "⚡ Motion Trail (face moving fast)",
                "triple": "🎭 Triple Expression (3 reactions)",
                "explosion": "💥 Explosion (high energy)"
            }[x]
        )
        
        if st.button("🚀 Generate Dynamic Thumbnail", type="primary"):
            if title:
                with st.spinner("Creating dynamic thumbnail..."):
                    thumbnail = create_dynamic_thumbnail(face_image, title, effect)
                
                st.success("✅ Generated!")
                st.image(thumbnail, use_column_width=True)
                
                # Download
                buf = io.BytesIO()
                thumbnail.save(buf, format='PNG', quality=95)
                buf.seek(0)
                
                st.download_button(
                    "⬇️ Download Thumbnail (PNG - YouTube Compatible)",
                    data=buf,
                    file_name=f"dynamic_thumbnail_{effect}.png",
                    mime="image/png"
                )
                
                st.info("✅ This is a **STATIC PNG** that YouTube will accept. It just LOOKS dynamic!")
            else:
                st.warning("⚠️ Please enter a title")

if __name__ == "__main__":
    main()