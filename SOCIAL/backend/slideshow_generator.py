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
slideshow_generator.py - YOUTUBE-PROOF OVERLAYS
✅ FFmpeg drawtext filter (burns overlays permanently)
✅ Bottom-center positioning with safe margins
✅ Different gradient colors for each image
✅ Survives YouTube processing/compression
✅ Professional animations and shadows
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
from PIL import Image
import random

logger = logging.getLogger(__name__)

class SlideshowGenerator:
    """Generate product ad videos with FFmpeg-burned overlays"""
    
    # Colorful gradient backgrounds for overlays (changes per image)
    GRADIENT_COLORS = [
        {"bg": "0x1a1a1aCC", "text": "0xFFD700", "accent": "0xFF6B6B"},  # Gold text, red accent
        {"bg": "0x0a0a2eCC", "text": "0x00FFF7", "accent": "0xFF3CAC"},  # Cyan text, pink accent
        {"bg": "0x1a4d2eCC", "text": "0xFFE66D", "accent": "0x4ECDC4"},  # Yellow text, teal accent
        {"bg": "0x2d1b4eCC", "text": "0xFF6BCB", "accent": "0xFFA500"},  # Pink text, orange accent
        {"bg": "0x4a0e0eCC", "text": "0xFFFFAA", "accent": "0x00FF00"},  # Light yellow, green accent
    ]
    
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
        product_data: Dict = None
    ) -> Dict[str, Any]:
        """Generate slideshow with FFmpeg-burned overlays"""
        
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
        
        logger.info(f"🎬 Creating product ad video with FFmpeg overlays...")
        
        for tier_index, quality_tier in enumerate(self.QUALITY_TIERS):
            try:
                logger.info(f"🎬 Quality: {quality_tier['name']}")
                
                # Step 1: Save and resize images
                image_paths = await self._save_images_optimized(
                    images, work_dir, quality_tier['resolution']
                )
                
                if not image_paths:
                    raise Exception("No images saved")
                
                # Step 2: Generate video with FFmpeg text overlays
                video_path = await self._create_video_with_ffmpeg_overlays(
                    image_paths,
                    duration_per_image,
                    quality_tier,
                    work_dir,
                    product_data
                )
                
                if not video_path or not video_path.exists():
                    raise Exception("Video not created")
                
                # Step 3: Thumbnail
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
                
                # Resize with padding
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
    
    async def _create_video_with_ffmpeg_overlays(
        self,
        image_paths: List[Path],
        duration: float,
        quality_tier: dict,
        work_dir: Path,
        product_data: Optional[Dict]
    ) -> Optional[Path]:
        """
        ✅ Generate video with FFmpeg drawtext overlays
        Overlays are BURNED into video frames (permanent)
        """
        output_path = work_dir / "output.mp4"
        resolution = quality_tier['resolution']
        width, height = resolution
        
        # Create concat file
        filelist_path = work_dir / "filelist.txt"
        with open(filelist_path, 'w') as f:
            for img_path in image_paths:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration}\n")
            f.write(f"file '{image_paths[-1]}'\n")
        
        # Build FFmpeg command with drawtext overlays
        video_filters = [
            f"fps=30",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        ]
        
        # ✅ ADD OVERLAYS if product data exists
        if product_data:
            overlay_filters = self._build_ffmpeg_overlay_filters(
                product_data, 
                len(image_paths), 
                duration,
                width,
                height
            )
            video_filters.extend(overlay_filters)
        
        # Combine all filters
        vf_string = ",".join(video_filters)
        
        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-vf", vf_string,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", quality_tier['preset'],
            "-crf", str(quality_tier['crf']),
            "-movflags", "+faststart",
            "-y",
            str(output_path)
        ]
        
        logger.info(f"🎥 Running FFmpeg with overlays...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg stderr: {stderr.decode()}")
                raise Exception(f"FFmpeg failed: {process.returncode}")
            
            if not output_path.exists():
                raise Exception("Output file not found")
            
            file_size = output_path.stat().st_size / 1024 / 1024
            logger.info(f"✅ Video created: {file_size:.2f} MB")
            
            return output_path
            
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            raise
    
    def _build_ffmpeg_overlay_filters(
        self,
        product_data: Dict,
        num_images: int,
        duration: float,
        width: int,
        height: int
    ) -> List[str]:
        """
        ✅ Build FFmpeg drawtext filters for bottom-center overlays
        Each image gets different colored gradient background
        """
        filters = []
        
        # Extract product info
        product_name = product_data.get("product_name", "Product")[:40]
        brand = product_data.get("brand", "Brand")[:20]
        price = product_data.get("price", 0)
        discount = product_data.get("discount", "")
        original_price = product_data.get("original_price", 0)
        
        # Fix price if zero
        if price == 0 and original_price > 0:
            price = original_price
        
        # ✅ BOTTOM-CENTER POSITIONING (YouTube-safe margins)
        # Bottom margin: 150px from bottom (safe zone)
        # Center horizontally
        box_y = height - 150
        
        # Create overlay for each image
        for idx in range(num_images):
            start_time = idx * duration
            end_time = (idx + 1) * duration
            
            # Get gradient color for this image
            color_scheme = self.GRADIENT_COLORS[idx % len(self.GRADIENT_COLORS)]
            
            # ========== FRAME-SPECIFIC TEXT ==========
            if idx == 0:
                # Frame 0: Brand + Product Name
                main_text = f"{brand}"
                sub_text = product_name[:30]
                
            elif idx == 1 and price > 0:
                # Frame 1: Price
                main_text = f"Rs.{int(price):,}"
                if discount:
                    sub_text = f"{discount} OFF"
                else:
                    sub_text = "Special Price"
                
            elif idx == 2:
                # Frame 2: Feature
                main_text = "Premium Quality"
                sub_text = "Original Product"
                
            else:
                # Last frames: CTA
                main_text = "Link in Description"
                sub_text = "Click to Buy"
            
            # ========== GRADIENT BACKGROUND BOX (BOTTOM-CENTER) ==========
            # Create semi-transparent gradient box
            box_filter = (
                f"drawbox="
                f"x=0:y={box_y}:w={width}:h=150:"
                f"color={color_scheme['bg']}:t=fill:"
                f"enable='between(t,{start_time},{end_time})'"
            )
            filters.append(box_filter)
            
            # ========== MAIN TEXT (LARGE, CENTERED) ==========
            # Escape special characters for FFmpeg
            main_text_escaped = main_text.replace("'", "\\'").replace(":", "\\:")
            
            main_text_filter = (
                f"drawtext="
                f"text='{main_text_escaped}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=48:"
                f"fontcolor={color_scheme['text']}:"
                f"x=(w-text_w)/2:"  # Center horizontally
                f"y={box_y + 30}:"  # 30px from box top
                f"shadowcolor=black@0.8:shadowx=2:shadowy=2:"
                f"enable='between(t,{start_time},{end_time})'"
            )
            filters.append(main_text_filter)
            
            # ========== SUB TEXT (SMALLER, CENTERED) ==========
            sub_text_escaped = sub_text.replace("'", "\\'").replace(":", "\\:")
            
            sub_text_filter = (
                f"drawtext="
                f"text='{sub_text_escaped}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                f"fontsize=32:"
                f"fontcolor=white:"
                f"x=(w-text_w)/2:"  # Center horizontally
                f"y={box_y + 90}:"  # Below main text
                f"shadowcolor=black@0.8:shadowx=2:shadowy=2:"
                f"enable='between(t,{start_time},{end_time})'"
            )
            filters.append(sub_text_filter)
            
            # ========== BRAND WATERMARK (TOP-LEFT) ==========
            watermark_filter = (
                f"drawtext="
                f"text='{brand[:15]}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=24:"
                f"fontcolor=white@0.7:"
                f"x=30:y=30:"
                f"shadowcolor=black@0.8:shadowx=1:shadowy=1:"
                f"enable='between(t,{start_time},{end_time})'"
            )
            filters.append(watermark_filter)
        
        logger.info(f"✅ Built {len(filters)} FFmpeg overlay filters")
        return filters
    
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