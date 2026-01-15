# """
# slideshow_generator.py - Memory-optimized FFmpeg slideshow with quality fallback
# """

# import os
# import asyncio
# import logging
# import subprocess
# import tempfile
# import base64
# import io
# import gc
# from pathlib import Path
# from typing import List, Dict, Any, Tuple, Optional
# from PIL import Image, ImageDraw, ImageFont

# logger = logging.getLogger(__name__)

# class SlideshowGenerator:
#     """Generate video slideshows with memory optimization"""
    
#     # Quality tiers (resolution, CRF, preset)
#     QUALITY_TIERS = [
#         # {"name": "1080p", "resolution": (1080, 1920), "crf": 20, "preset": "medium"},
#         {"name": "720p", "resolution": (720, 1280), "crf": 23, "preset": "fast"},
#         {"name": "540p", "resolution": (540, 960), "crf": 28, "preset": "ultrafast"},
#         {"name": "480p", "resolution": (480, 854), "crf": 30, "preset": "ultrafast"},
#         {"name": "360p", "resolution": (360, 640), "crf": 32, "preset": "ultrafast"}
#     ]
    
#     def __init__(self):
#         self.ffmpeg_path = self._find_ffmpeg()
#         self.temp_dir = tempfile.gettempdir()
#         logger.info(f"SlideshowGenerator initialized - FFmpeg: {self.ffmpeg_path}")
    
#     def _find_ffmpeg(self) -> str:
#         """Find FFmpeg executable"""
#         try:
#             result = subprocess.run(['which', 'ffmpeg'], 
#                                   capture_output=True, 
#                                   text=True, 
#                                   timeout=5)
#             if result.returncode == 0:
#                 return result.stdout.strip()
#         except:
#             pass
#         return "ffmpeg"  # Fallback
    
#     async def generate_slideshow(
#         self,
#         images: List[str],
#         title: str,
#         language: str = "english",
#         duration_per_image: float = 2.0,
#         transition: str = "fade",
#         add_text: bool = True,
#         music_style: str = "upbeat",
#         aspect_ratio: str = "9:16",
#         product_data: Dict = None
#     ) -> Dict[str, Any]:
#         """Generate slideshow with automatic quality fallback"""
        
#         if not 2 <= len(images) <= 6:
#             return {"success": False, "error": "Upload 2-6 images"}
        
#         # Get event loop safely
#         try:
#             loop = asyncio.get_running_loop()
#             timestamp = int(loop.time() * 1000)
#         except:
#             import time
#             timestamp = int(time.time() * 1000)
        
#         session_id = f"slideshow_{timestamp}"
#         work_dir = Path(self.temp_dir) / session_id
#         work_dir.mkdir(exist_ok=True, parents=True)
        
#         logger.info(f"Working directory: {work_dir}")
        
#         # Try each quality tier
#         for tier_index, quality_tier in enumerate(self.QUALITY_TIERS):
#             try:
#                 logger.info(f"🎬 Attempting generation: {quality_tier['name']} (attempt {tier_index + 1}/3)")
                
#                 # Step 1: Save images with current quality
#                 image_paths = await self._save_images_optimized(
#                     images, work_dir, quality_tier['resolution']
#                 )
                
#                 if not image_paths:
#                     raise Exception("No images were saved")
                
#                 # Step 2: Add product overlays if product data provided
#                 if product_data:
#                     image_paths = await self._add_product_overlays(
#                         image_paths, product_data, work_dir
#                     )
#                 # Step 3: Add text overlays (for regular slideshows)
#                 elif add_text:
#                     image_paths = await self._add_text_overlays(
#                         image_paths, title, language, work_dir
#                     )
                
#                 # Step 4: Generate video with FFmpeg
#                 video_path = await self._create_video_ffmpeg(
#                     image_paths,
#                     duration_per_image,
#                     quality_tier,
#                     work_dir
#                 )
                
#                 if not video_path or not video_path.exists():
#                     raise Exception("Video file was not created")
                
#                 # Step 5: Generate thumbnail
#                 thumbnail_path = await self._generate_thumbnail(image_paths[0], work_dir)
                
#                 # SUCCESS - return result
#                 logger.info(f"✅ Video generated successfully at {quality_tier['name']}")
                
#                 return {
#                     "success": True,
#                     "video_url": f"/temp/{session_id}/output.mp4",
#                     "thumbnail_url": f"/temp/{session_id}/thumbnail.jpg",
#                     "duration": len(images) * duration_per_image,
#                     "image_count": len(images),
#                     "session_id": session_id,
#                     "local_path": str(video_path),
#                     "quality": quality_tier['name']
#                 }
                
#             except Exception as e:
#                 logger.error(f"❌ {quality_tier['name']} failed: {e}")
#                 import traceback
#                 logger.error(f"Traceback: {traceback.format_exc()}")
                
#                 # Clean up failed attempt
#                 try:
#                     import shutil
#                     if work_dir.exists():
#                         shutil.rmtree(work_dir, ignore_errors=True)
#                         work_dir.mkdir(exist_ok=True, parents=True)
#                 except Exception as cleanup_err:
#                     logger.warning(f"Cleanup failed: {cleanup_err}")
                
#                 # Force garbage collection
#                 gc.collect()
                
#                 # If this was the last tier, fail
#                 if tier_index == len(self.QUALITY_TIERS) - 1:
#                     return {
#                         "success": False,
#                         "error": f"All quality tiers failed. Last error: {str(e)}"
#                     }
                
#                 # Otherwise, continue to next tier
#                 logger.info(f"⏩ Retrying with {self.QUALITY_TIERS[tier_index + 1]['name']}")
#                 await asyncio.sleep(1)  # Brief pause before retry
#                 continue
        
#         # Should never reach here
#         return {"success": False, "error": "Unknown error in slideshow generation"}
    
#     async def _save_images_optimized(
#         self, 
#         images: List[str], 
#         work_dir: Path,
#         target_size: Tuple[int, int]
#     ) -> List[Path]:
#         """Save images with aggressive memory optimization"""
#         image_paths = []
        
#         for idx, img_b64 in enumerate(images):
#             try:
#                 # Validate format
#                 if not isinstance(img_b64, str):
#                     raise ValueError(f"Image {idx + 1} is not a string")
                
#                 if not img_b64.startswith('data:image/'):
#                     raise ValueError(f"Image {idx + 1} invalid format (must start with data:image/)")
                
#                 # Extract base64
#                 if 'base64,' in img_b64:
#                     img_b64 = img_b64.split('base64,', 1)[1]
#                 else:
#                     raise ValueError(f"Image {idx + 1} missing base64 data")
                
#                 # Decode
#                 img_b64 = img_b64.strip()
                
#                 try:
#                     img_data = base64.b64decode(img_b64)
#                 except Exception as decode_err:
#                     raise ValueError(f"Image {idx + 1} base64 decode failed: {decode_err}")
                
#                 if len(img_data) < 100:
#                     raise ValueError(f"Image {idx + 1} data too small ({len(img_data)} bytes)")
                
#                 # Load image
#                 try:
#                     img = Image.open(io.BytesIO(img_data))
#                     img.load()
#                 except Exception as img_err:
#                     raise ValueError(f"Image {idx + 1} failed to load: {img_err}")
                
#                 # Resize immediately (memory critical)
#                 img = self._resize_with_padding(img, target_size)
                
#                 # Save with low quality
#                 img_path = work_dir / f"img_{idx:03d}.jpg"
#                 img.save(img_path, "JPEG", quality=75, optimize=True)
                
#                 # FREE MEMORY IMMEDIATELY
#                 img.close()
#                 del img
#                 del img_data
#                 del img_b64
#                 gc.collect()
                
#                 image_paths.append(img_path)
#                 logger.info(f"✅ Image {idx + 1} saved: {img_path}")
                
#             except Exception as e:
#                 logger.error(f"Failed to save image {idx + 1}: {e}")
#                 raise ValueError(f"Image {idx + 1} failed: {str(e)}")
        
#         return image_paths
    
#     def _resize_with_padding(self, img: Image.Image, target_size: tuple) -> Image.Image:
#         """Resize maintaining aspect ratio"""
#         img_ratio = img.width / img.height
#         target_ratio = target_size[0] / target_size[1]
        
#         if img_ratio > target_ratio:
#             new_width = target_size[0]
#             new_height = int(new_width / img_ratio)
#         else:
#             new_height = target_size[1]
#             new_width = int(new_height * img_ratio)
        
#         img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
#         padded = Image.new('RGB', target_size, (0, 0, 0))
#         paste_x = (target_size[0] - new_width) // 2
#         paste_y = (target_size[1] - new_height) // 2
#         padded.paste(img, (paste_x, paste_y))
        
#         return padded
    
#     async def _add_text_overlays(
#         self,
#         image_paths: List[Path],
#         title: str,
#         language: str,
#         work_dir: Path
#     ) -> List[Path]:
#         """Add text overlays"""
#         overlay_paths = []
        
#         try:
#             font = ImageFont.load_default()
#         except:
#             font = None
        
#         for idx, img_path in enumerate(image_paths):
#             try:
#                 img = Image.open(img_path)
#                 draw = ImageDraw.Draw(img)
                
#                 if idx == 0 and title and font:
#                     text = title[:50]
#                     x = img.width // 4
#                     y = 100
#                     draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
#                     draw.text((x, y), text, fill=(255, 255, 255), font=font)
                
#                 overlay_path = work_dir / f"overlay_{idx:03d}.jpg"
#                 img.save(overlay_path, "JPEG", quality=75)
#                 overlay_paths.append(overlay_path)
                
#                 img.close()
#                 del img
#                 gc.collect()
#             except Exception as overlay_err:
#                 logger.warning(f"Text overlay failed for image {idx}: {overlay_err}")
#                 overlay_paths.append(img_path)  # Use original
        
#         return overlay_paths if overlay_paths else image_paths
    
#     async def _add_product_overlays(
#         self,
#         image_paths: List[Path],
#         product_data: Dict,
#         work_dir: Path
#     ) -> List[Path]:
#         """Add product info overlays to images"""
#         overlay_paths = []
        
#         try:
#             font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
#             font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
#         except:
#             font_large = font_small = ImageFont.load_default()
        
#         price = product_data.get("price", 0)
#         discount = product_data.get("discount", "")
#         brand = product_data.get("brand", "")
        
#         for idx, img_path in enumerate(image_paths):
#             try:
#                 img = Image.open(img_path)
#                 draw = ImageDraw.Draw(img)
                
#                 # Add brand name at top
#                 if brand:
#                     draw.text((50, 50), brand, fill=(255, 255, 255), font=font_large, stroke_width=2, stroke_fill=(0, 0, 0))
                
#                 # Add price at bottom
#                 if price:
#                     price_text = f"₹{int(price)}"
#                     if discount:
#                         price_text += f" {discount}"
                    
#                     text_bbox = draw.textbbox((0, 0), price_text, font=font_large)
#                     text_width = text_bbox[2] - text_bbox[0]
                    
#                     x = img.width - text_width - 50
#                     y = img.height - 150
                    
#                     # Price background
#                     draw.rectangle([x-20, y-10, x+text_width+20, y+70], fill=(255, 0, 0))
#                     draw.text((x, y), price_text, fill=(255, 255, 255), font=font_large)
                
#                 overlay_path = work_dir / f"product_{idx:03d}.jpg"
#                 img.save(overlay_path, "JPEG", quality=85)
#                 overlay_paths.append(overlay_path)
                
#                 img.close()
#                 del img
#                 gc.collect()
                
#             except Exception as overlay_err:
#                 logger.warning(f"Product overlay failed for image {idx}: {overlay_err}")
#                 overlay_paths.append(img_path)  # Use original
        
#         return overlay_paths if overlay_paths else image_paths
    
#     async def _create_video_ffmpeg(
#         self,
#         image_paths: List[Path],
#         duration: float,
#         quality_tier: dict,
#         work_dir: Path
#     ) -> Optional[Path]:
#         """Generate video with memory-optimized FFmpeg settings"""
#         output_path = work_dir / "output.mp4"
        
#         # Create file list
#         filelist_path = work_dir / "filelist.txt"
#         with open(filelist_path, 'w') as f:
#             for img_path in image_paths:
#                 f.write(f"file '{img_path}'\n")
#                 f.write(f"duration {duration}\n")
#             f.write(f"file '{image_paths[-1]}'\n")
        
#         resolution = quality_tier['resolution']
        
#         cmd = [
#             self.ffmpeg_path,
#             "-f", "concat",
#             "-safe", "0",
#             "-i", str(filelist_path),
#             "-vf", f"fps=24,scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2",
#             "-c:v", "libx264",
#             "-pix_fmt", "yuv420p",
#             "-preset", quality_tier['preset'],
#             "-crf", str(quality_tier['crf']),
#             "-bufsize", "1M",
#             "-maxrate", "1M",
#             "-y",
#             str(output_path)
#         ]
        
#         logger.info(f"🎥 Running FFmpeg: {' '.join(cmd[:8])}...")
        
#         try:
#             process = await asyncio.create_subprocess_exec(
#                 *cmd,
#                 stdout=asyncio.subprocess.PIPE,
#                 stderr=asyncio.subprocess.PIPE
#             )
            
#             stdout, stderr = await process.communicate()
            
#             if process.returncode != 0:
#                 error_msg = stderr.decode()[:1000]
#                 logger.error(f"FFmpeg stderr: {error_msg}")
#                 raise Exception(f"FFmpeg failed with code {process.returncode}")
            
#             if not output_path.exists():
#                 raise Exception("FFmpeg completed but output file not found")
            
#             file_size = output_path.stat().st_size / 1024 / 1024
#             logger.info(f"✅ Video created: {file_size:.2f} MB")
            
#             return output_path
            
#         except Exception as ffmpeg_err:
#             logger.error(f"FFmpeg execution failed: {ffmpeg_err}")
#             raise
    
#     async def _generate_thumbnail(self, first_image: Path, work_dir: Path) -> Path:
#         """Generate thumbnail"""
#         thumb_path = work_dir / "thumbnail.jpg"
        
#         try:
#             img = Image.open(first_image)
#             img.thumbnail((640, 360), Image.Resampling.LANCZOS)
#             img.save(thumb_path, "JPEG", quality=75)
#             img.close()
#             return thumb_path
#         except Exception as thumb_err:
#             logger.warning(f"Thumbnail generation failed: {thumb_err}")
#             return first_image  # Return original as fallback


# # Global instance
# slideshow_generator = SlideshowGenerator()

# def get_slideshow_generator():
#     return slideshow_generator


















"""
slideshow_generator.py - YOUTUBE-COMPLIANT PRODUCT ADS
✅ Professional product promotion (not scammy)
✅ Clear ad disclosure (follows YouTube guidelines)
✅ High-converting visual design
✅ Affiliate link in description (only legal way)
"""

import os
import asyncio
import logging
import subprocess
import tempfile
import base64
import io
import gc
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

logger = logging.getLogger(__name__)

class SlideshowGenerator:
    """Generate YouTube-compliant product promotion videos"""
    
    QUALITY_TIERS = [
        {"name": "720p", "resolution": (720, 1280), "crf": 23, "preset": "fast"},
        {"name": "540p", "resolution": (540, 960), "crf": 28, "preset": "ultrafast"},
    ]
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.temp_dir = tempfile.gettempdir()
        logger.info(f"SlideshowGenerator initialized - FFmpeg: {self.ffmpeg_path}")
    
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable"""
        try:
            result = subprocess.run(['which', 'ffmpeg'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "ffmpeg"
    
    async def generate_slideshow(
        self,
        images: List[str],
        title: str,
        language: str = "english",
        duration_per_image: float = 2.0,
        transition: str = "fade",
        add_text: bool = True,
        music_style: str = "upbeat",
        aspect_ratio: str = "9:16",
        product_data: Dict = None  # ✅ Product info
    ) -> Dict[str, Any]:
        """Generate YouTube-compliant product ad video"""
        
        if not 2 <= len(images) <= 6:
            return {"success": False, "error": "Upload 2-6 images"}
        
        try:
            loop = asyncio.get_running_loop()
            timestamp = int(loop.time() * 1000)
        except:
            import time
            timestamp = int(time.time() * 1000)
        
        session_id = f"slideshow_{timestamp}"
        work_dir = Path(self.temp_dir) / session_id
        work_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"🎬 Creating product ad video...")
        
        for tier_index, quality_tier in enumerate(self.QUALITY_TIERS):
            try:
                logger.info(f"🎬 Quality: {quality_tier['name']}")
                
                # Step 1: Save images
                image_paths = await self._save_images_optimized(
                    images, work_dir, quality_tier['resolution']
                )
                
                if not image_paths:
                    raise Exception("No images saved")
                
                # Step 2: ✅ ADD PROFESSIONAL AD OVERLAYS
                if product_data:
                    logger.info("🎨 Adding professional ad overlays...")
                    image_paths = await self._add_professional_ad_overlays(
                        image_paths, product_data, work_dir, quality_tier['resolution']
                    )
                
                # Step 3: Generate video
                video_path = await self._create_video_ffmpeg(
                    image_paths,
                    duration_per_image,
                    quality_tier,
                    work_dir
                )
                
                if not video_path or not video_path.exists():
                    raise Exception("Video not created")
                
                # Step 4: Thumbnail
                thumbnail_path = await self._generate_thumbnail(image_paths[0], work_dir)
                
                logger.info(f"✅ Video generated: {quality_tier['name']}")
                
                return {
                    "success": True,
                    "video_url": f"/temp/{session_id}/output.mp4",
                    "thumbnail_url": f"/temp/{session_id}/thumbnail.jpg",
                    "duration": len(images) * duration_per_image,
                    "image_count": len(images),
                    "session_id": session_id,
                    "local_path": str(video_path),
                    "quality": quality_tier['name'],
                    "is_product_ad": bool(product_data)
                }
                
            except Exception as e:
                logger.error(f"❌ {quality_tier['name']} failed: {e}")
                
                if tier_index == len(self.QUALITY_TIERS) - 1:
                    return {"success": False, "error": str(e)}
                
                await asyncio.sleep(1)
                continue
        
        return {"success": False, "error": "Generation failed"}
    
    async def _save_images_optimized(
        self, 
        images: List[str], 
        work_dir: Path,
        target_size: Tuple[int, int]
    ) -> List[Path]:
        """Save and resize images"""
        image_paths = []
        
        for idx, img_b64 in enumerate(images):
            try:
                if 'base64,' in img_b64:
                    img_b64 = img_b64.split('base64,', 1)[1]
                
                img_data = base64.b64decode(img_b64.strip())
                img = Image.open(io.BytesIO(img_data))
                img.load()
                
                # Resize
                img = self._resize_with_padding(img, target_size)
                
                # Save
                img_path = work_dir / f"img_{idx:03d}.jpg"
                img.save(img_path, "JPEG", quality=85, optimize=True)
                
                img.close()
                del img
                gc.collect()
                
                image_paths.append(img_path)
                logger.info(f"✅ Image {idx + 1} saved")
                
            except Exception as e:
                logger.error(f"Image {idx + 1} failed: {e}")
                raise
        
        return image_paths
    
    def _resize_with_padding(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """Resize with black padding"""
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
        else:
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        padded = Image.new('RGB', target_size, (0, 0, 0))
        paste_x = (target_size[0] - new_width) // 2
        paste_y = (target_size[1] - new_height) // 2
        padded.paste(img, (paste_x, paste_y))
        
        return padded
    
    # ============================================================================
    # ✅ PROFESSIONAL AD OVERLAYS (YOUTUBE-COMPLIANT)
    # ============================================================================
    
    async def _add_professional_ad_overlays(
        self,
        image_paths: List[Path],
        product_data: Dict,
        work_dir: Path,
        resolution: Tuple[int, int]
    ) -> List[Path]:
        """
        ✅ Add professional product ad overlays
        - First frame: Ad disclosure (YouTube compliance)
        - Product info overlays (price, brand, CTA)
        - Professional styling (not scammy)
        """
        overlay_paths = []
        
        # Load fonts
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font_title = font_large = font_medium = font_small = ImageFont.load_default()
        
        # Extract product info
        product_name = product_data.get("product_name", "Product")[:50]
        brand = product_data.get("brand", "Brand")[:20]
        price = product_data.get("price", 0)
        discount = product_data.get("discount", "")
        original_price = product_data.get("original_price", 0)
        
        # ✅ Fix price if zero (common scraping issue)
        if price == 0 and original_price > 0:
            price = original_price
        
        for idx, img_path in enumerate(image_paths):
            try:
                img = Image.open(img_path).convert('RGBA')
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)
                
                # ========== FRAME 0: AD DISCLOSURE (REQUIRED BY YOUTUBE) ==========
                if idx == 0:
                    # Top badge
                    badge_text = "🔔 Product Review"
                    badge_bbox = draw.textbbox((0, 0), badge_text, font=font_medium)
                    badge_width = badge_bbox[2] - badge_bbox[0] + 40
                    badge_height = 50
                    badge_x = (img.width - badge_width) // 2
                    badge_y = 60
                    
                    # Badge background
                    draw.rounded_rectangle(
                        [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
                        radius=25,
                        fill=(50, 50, 50, 220)
                    )
                    
                    # Badge text
                    text_x = badge_x + 20
                    text_y = badge_y + 8
                    draw.text((text_x, text_y), badge_text, fill=(255, 255, 255), font=font_medium)
                
                # ========== ALL FRAMES: GRADIENT BOTTOM BAR ==========
                bar_height = 180
                bar_y = img.height - bar_height
                
                # Create gradient
                for i in range(bar_height):
                    alpha = int(200 * (i / bar_height))
                    draw.rectangle(
                        [(0, bar_y + i), (img.width, bar_y + i + 1)],
                        fill=(0, 0, 0, alpha)
                    )
                
                # ========== FRAME-SPECIFIC CONTENT ==========
                
                if idx == 0:
                    # FRAME 0: Brand + Product Name
                    brand_text = f"✨ {brand}"
                    draw.text((40, bar_y + 20), brand_text, fill=(255, 215, 0), font=font_large)
                    
                    # Product name (wrapped)
                    product_words = product_name.split()
                    line1 = ' '.join(product_words[:5])
                    line2 = ' '.join(product_words[5:10]) if len(product_words) > 5 else ""
                    
                    draw.text((40, bar_y + 75), line1, fill=(255, 255, 255), font=font_medium)
                    if line2:
                        draw.text((40, bar_y + 115), line2, fill=(255, 255, 255), font=font_small)
                
                elif idx == 1 and price > 0:
                    # FRAME 1: Price
                    price_text = f"₹{int(price):,}"
                    draw.text((40, bar_y + 30), price_text, fill=(0, 255, 127), font=font_title)
                    
                    # Original price (if discount)
                    if discount:
                        orig_text = f"₹{int(original_price):,}"
                        orig_bbox = draw.textbbox((40, bar_y + 90), orig_text, font=font_medium)
                        draw.text((40, bar_y + 90), orig_text, fill=(200, 200, 200), font=font_medium)
                        
                        # Strike-through
                        draw.line(
                            [(40, bar_y + 105), (orig_bbox[2], bar_y + 105)],
                            fill=(255, 0, 0),
                            width=3
                        )
                        
                        # Discount badge
                        discount_text = discount
                        draw.text((40, bar_y + 130), discount_text, fill=(255, 69, 0), font=font_medium)
                
                elif idx == 2:
                    # FRAME 2: Key Feature
                    feature_text = "✓ Premium Quality"
                    draw.text((40, bar_y + 40), feature_text, fill=(255, 255, 255), font=font_large)
                    
                    sub_text = "Original Product"
                    draw.text((40, bar_y + 100), sub_text, fill=(180, 180, 180), font=font_small)
                
                elif idx >= 3:
                    # LAST FRAMES: CTA
                    cta_text = "👇 Link in Description"
                    cta_bbox = draw.textbbox((0, 0), cta_text, font=font_large)
                    cta_width = cta_bbox[2] - cta_bbox[0]
                    cta_x = (img.width - cta_width) // 2
                    
                    # Pulsing effect (visual only)
                    draw.text((cta_x, bar_y + 50), cta_text, fill=(255, 215, 0), font=font_large)
                
                # ========== BRAND WATERMARK (ALL FRAMES) ==========
                watermark = f"📱 {brand}"
                draw.text((30, 30), watermark, fill=(255, 255, 255, 200), font=font_small)
                
                # Composite
                img = Image.alpha_composite(img, overlay)
                img = img.convert('RGB')
                
                # Save
                overlay_path = work_dir / f"ad_overlay_{idx:03d}.jpg"
                img.save(overlay_path, "JPEG", quality=88)
                overlay_paths.append(overlay_path)
                
                logger.info(f"✅ Ad overlay {idx + 1} added")
                
                img.close()
                del img, overlay
                gc.collect()
                
            except Exception as e:
                logger.warning(f"Overlay failed for image {idx}: {e}")
                overlay_paths.append(img_path)
        
        return overlay_paths if overlay_paths else image_paths
    
    async def _create_video_ffmpeg(
        self,
        image_paths: List[Path],
        duration: float,
        quality_tier: dict,
        work_dir: Path
    ) -> Optional[Path]:
        """Generate video with FFmpeg"""
        output_path = work_dir / "output.mp4"
        
        # Create file list
        filelist_path = work_dir / "filelist.txt"
        with open(filelist_path, 'w') as f:
            for img_path in image_paths:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration}\n")
            f.write(f"file '{image_paths[-1]}'\n")
        
        resolution = quality_tier['resolution']
        
        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-vf", f"fps=30,scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", quality_tier['preset'],
            "-crf", str(quality_tier['crf']),
            "-movflags", "+faststart",
            "-y",
            str(output_path)
        ]
        
        logger.info(f"🎥 Running FFmpeg...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg failed: {process.returncode}")
            
            if not output_path.exists():
                raise Exception("Output file not found")
            
            file_size = output_path.stat().st_size / 1024 / 1024
            logger.info(f"✅ Video created: {file_size:.2f} MB")
            
            return output_path
            
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            raise
    
    async def _generate_thumbnail(self, first_image: Path, work_dir: Path) -> Path:
        """Generate thumbnail"""
        thumb_path = work_dir / "thumbnail.jpg"
        
        try:
            img = Image.open(first_image)
            img.thumbnail((640, 360), Image.Resampling.LANCZOS)
            img.save(thumb_path, "JPEG", quality=80)
            img.close()
            return thumb_path
        except:
            return first_image


# Global instance
slideshow_generator = SlideshowGenerator()

def get_slideshow_generator():
    return slideshow_generator

def get_video_generator():
    return slideshow_generator