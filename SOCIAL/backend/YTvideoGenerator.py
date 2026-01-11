"""
YTvideoGenerator.py - Video Generator with URL Overlay
Generates promotional videos with product URL overlays
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoGeneratorWithOverlay:
    """Generate promotional videos with URL overlay"""
    
    def __init__(self):
        self.output_dir = "generated_videos"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def create_promo_video(
        self,
        images: list,
        product_name: str,
        product_url: str,
        price: str = None
    ) -> dict:
        """Create promotional video with URL overlay on first frame"""
        try:
            if len(images) < 1:
                return {"success": False, "error": "Need at least 1 image"}
            
            # Settings
            width, height = 1080, 1920  # 9:16 aspect ratio
            fps = 30
            duration_per_image = 2.0
            
            # Output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"promo_{timestamp}.mp4")
            
            # Video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frames_per_image = int(fps * duration_per_image)
            
            for idx, img_data in enumerate(images):
                # Load image
                if img_data.startswith('data:image'):
                    img_data = img_data.split(',')[1]
                
                img_bytes = base64.b64decode(img_data)
                pil_img = Image.open(io.BytesIO(img_bytes))
                
                # Resize to fit
                pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Add overlay ONLY on first image
                if idx == 0:
                    pil_img = self._add_url_overlay(pil_img, product_url, product_name, price)
                
                # Convert to OpenCV format
                frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                
                # Write frames
                for _ in range(frames_per_image):
                    out.write(frame)
            
            out.release()
            
            logger.info(f"✅ Promo video created: {output_path}")
            
            return {
                "success": True,
                "local_path": output_path,
                "video_url": f"/videos/{os.path.basename(output_path)}"
            }
            
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    def _add_url_overlay(self, img: Image.Image, url: str, title: str, price: str) -> Image.Image:
        """Add promotional overlay with clickable URL"""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Semi-transparent overlay at bottom
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Dark gradient at bottom
        for i in range(400):
            alpha = int(180 * (i / 400))
            overlay_draw.rectangle(
                [(0, height - 400 + i), (width, height - 400 + i + 1)],
                fill=(0, 0, 0, alpha)
            )
        
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img)
        
        # Try to load font
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 45)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw "SHOP NOW" tag
        tag_y = height - 350
        draw.rectangle(
            [(40, tag_y), (240, tag_y + 60)],
            fill=(255, 0, 0),
            outline=(255, 255, 255),
            width=3
        )
        draw.text((140, tag_y + 30), "SHOP NOW", font=font_medium, fill='white', anchor='mm')
        
        # Draw product title
        title_y = height - 270
        if len(title) > 40:
            title = title[:37] + "..."
        draw.text((width // 2, title_y), title, font=font_large, fill='white', anchor='mm', stroke_width=2, stroke_fill='black')
        
        # Draw price
        if price:
            price_y = height - 200
            draw.text((width // 2, price_y), f"₹{price}", font=font_medium, fill='#FFD700', anchor='mm', stroke_width=2, stroke_fill='black')
        
        # Draw URL
        url_y = height - 130
        display_url = url.replace('https://', '').replace('http://', '')
        if len(display_url) > 50:
            display_url = display_url[:47] + "..."
        
        draw.text((width // 2, url_y), display_url, font=font_small, fill='#00D9FF', anchor='mm')
        
        # Draw arrow
        draw.text((width // 2, height - 60), "👆 TAP TO BUY 👆", font=font_medium, fill='white', anchor='mm')
        
        return img.convert('RGB')

# Global instance
_video_gen_instance = None

def get_video_generator():
    global _video_gen_instance
    if _video_gen_instance is None:
        _video_gen_instance = VideoGeneratorWithOverlay()
    return _video_gen_instance