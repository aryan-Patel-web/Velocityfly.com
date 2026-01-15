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
slideshow_generator.py - DEBUGGING VERSION + BACKGROUND MUSIC
✅ Saves intermediate files for debugging
✅ Detailed logging at every step
✅ Background music support (royalty-free) - 9 categories with 5 tracks each
✅ Simple, foolproof overlay approach
"""

import os
import asyncio
import logging
import subprocess
import tempfile
import base64
import io
import gc
import urllib.request
import random  # ← NEW: Import random
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class SlideshowGenerator:
    """Generate product ad videos with overlays and music"""
    
    # ✅ UPDATED: 9 music categories with 5 tracks each (45 total tracks)
    BACKGROUND_MUSIC = {
        "upbeat": [
            "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
            "https://www.bensound.com/bensound-music/bensound-happyrock.mp3",
            "https://www.bensound.com/bensound-music/bensound-energy.mp3",
            "https://www.bensound.com/bensound-music/bensound-clearday.mp3",
            "https://www.bensound.com/bensound-music/bensound-funkyelement.mp3",
        ],
        "energetic": [
            "https://www.bensound.com/bensound-music/bensound-dance.mp3",
            "https://www.bensound.com/bensound-music/bensound-actionable.mp3",
            "https://www.bensound.com/bensound-music/bensound-epic.mp3",
            "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
            "https://www.bensound.com/bensound-music/bensound-instinct.mp3",
        ],
        "cinematic": [
            "https://www.bensound.com/bensound-music/bensound-november.mp3",
            "https://www.bensound.com/bensound-music/bensound-slowmotion.mp3",
            "https://www.bensound.com/bensound-music/bensound-tomorrow.mp3",
            "https://www.bensound.com/bensound-music/bensound-memories.mp3",
            "https://www.bensound.com/bensound-music/bensound-epic.mp3",
        ],
        "relaxing": [
            "https://www.bensound.com/bensound-music/bensound-relaxing.mp3",
            "https://www.bensound.com/bensound-music/bensound-tenderness.mp3",
            "https://www.bensound.com/bensound-music/bensound-slowmotion.mp3",
            "https://www.bensound.com/bensound-music/bensound-onceagain.mp3",
            "https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3",
        ],
        "sad": [
            "https://www.bensound.com/bensound-music/bensound-sadness.mp3",
            "https://www.bensound.com/bensound-music/bensound-memories.mp3",
            "https://www.bensound.com/bensound-music/bensound-tomorrow.mp3",
            "https://www.bensound.com/bensound-music/bensound-november.mp3",
            "https://www.bensound.com/bensound-music/bensound-thejazzpiano.mp3",
        ],
        "dark": [
            "https://www.bensound.com/bensound-music/bensound-instinct.mp3",
            "https://www.bensound.com/bensound-music/bensound-theduel.mp3",
            "https://www.bensound.com/bensound-music/bensound-epic.mp3",
            "https://www.bensound.com/bensound-music/bensound-dangerous.mp3",
            "https://www.bensound.com/bensound-music/bensound-sci-fi.mp3",
        ],
        "lofi": [
            "https://www.bensound.com/bensound-music/bensound-acousticbreeze.mp3",
            "https://www.bensound.com/bensound-music/bensound-november.mp3",
            "https://www.bensound.com/bensound-music/bensound-slowmotion.mp3",
            "https://www.bensound.com/bensound-music/bensound-onceagain.mp3",
            "https://www.bensound.com/bensound-music/bensound-tenderness.mp3",
        ],
        "happy": [
            "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
            "https://www.bensound.com/bensound-music/bensound-happyrock.mp3",
            "https://www.bensound.com/bensound-music/bensound-sunny.mp3",
            "https://www.bensound.com/bensound-music/bensound-clearday.mp3",
            "https://www.bensound.com/bensound-music/bensound-funkyelement.mp3",
        ],
        "motivational": [
            "https://www.bensound.com/bensound-music/bensound-inspire.mp3",
            "https://www.bensound.com/bensound-music/bensound-epic.mp3",
            "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
            "https://www.bensound.com/bensound-music/bensound-actionable.mp3",
            "https://www.bensound.com/bensound-music/bensound-instinct.mp3",
        ],
    }
    
    QUALITY_TIERS = [
        {"name": "720p", "resolution": (720, 1280), "crf": 23, "preset": "fast"},
        {"name": "540p", "resolution": (540, 960), "crf": 28, "preset": "ultrafast"},
    ]
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.temp_dir = tempfile.gettempdir()
        logger.info(f"✅ SlideshowGenerator initialized - FFmpeg: {self.ffmpeg_path}")
    
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable"""
        try:
            result = subprocess.run(['which', 'ffmpeg'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                ffmpeg_path = result.stdout.strip()
                logger.info(f"✅ FFmpeg found: {ffmpeg_path}")
                return ffmpeg_path
        except Exception as e:
            logger.warning(f"⚠️  FFmpeg search failed: {e}")
        
        logger.warning("⚠️  Using default 'ffmpeg' command")
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
        product_data: Dict = None,
        add_music: bool = True  # Enable background music
    ) -> Dict[str, Any]:
        """Generate slideshow with debugging and music"""
        
        logger.info("=" * 70)
        logger.info("🎬 STARTING SLIDESHOW GENERATION")
        logger.info("=" * 70)
        logger.info(f"📊 Input: {len(images)} images")
        logger.info(f"📦 Product data: {product_data is not None}")
        logger.info(f"🎵 Music style: {music_style}")
        logger.info(f"🎵 Add music: {add_music}")
        
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
        
        logger.info(f"📁 Work directory: {work_dir}")
        
        for tier_index, quality_tier in enumerate(self.QUALITY_TIERS):
            try:
                logger.info(f"\n{'='*70}")
                logger.info(f"🎬 Attempting quality: {quality_tier['name']}")
                logger.info(f"{'='*70}\n")
                
                # STEP 1: Decode and save images
                logger.info("📥 STEP 1: Decoding and saving base images...")
                base_paths = await self._decode_and_save_images(
                    images, work_dir, quality_tier['resolution']
                )
                logger.info(f"✅ STEP 1 COMPLETE: {len(base_paths)} base images saved")
                for i, p in enumerate(base_paths):
                    logger.info(f"   → {i+1}. {p} ({p.stat().st_size / 1024:.1f} KB)")
                
                # STEP 2: Add overlays (CRITICAL STEP)
                if product_data:
                    logger.info("\n🎨 STEP 2: Adding text overlays to images...")
                    logger.info(f"   Product: {product_data.get('brand')} - {product_data.get('product_name', '')[:30]}")
                    logger.info(f"   Price: Rs.{product_data.get('price', 0)}")
                    
                    overlaid_paths = await self._add_overlays_with_pil(
                        base_paths, product_data, work_dir
                    )
                    logger.info(f"✅ STEP 2 COMPLETE: {len(overlaid_paths)} overlaid images created")
                    for i, p in enumerate(overlaid_paths):
                        logger.info(f"   → {i+1}. {p} ({p.stat().st_size / 1024:.1f} KB)")
                else:
                    logger.warning("⚠️  STEP 2 SKIPPED: No product_data provided!")
                    overlaid_paths = base_paths
                
                # STEP 3: Download background music (if enabled)
                music_path = None
                if add_music:
                    logger.info("\n🎵 STEP 3: Downloading background music...")
                    music_path = await self._download_music(work_dir, music_style)
                    if music_path:
                        logger.info(f"✅ STEP 3 COMPLETE: Music downloaded to {music_path}")
                    else:
                        logger.warning("⚠️  STEP 3 FAILED: Could not download music, continuing without")
                else:
                    logger.info("\n⚠️  STEP 3 SKIPPED: Music disabled")
                
                # STEP 4: Create video
                logger.info("\n🎥 STEP 4: Creating video with FFmpeg...")
                video_path = await self._create_video_with_ffmpeg(
                    overlaid_paths,
                    duration_per_image,
                    quality_tier,
                    work_dir,
                    music_path  # Pass music path
                )
                
                if not video_path or not video_path.exists():
                    raise Exception("Video file not created!")
                
                file_size = video_path.stat().st_size / 1024 / 1024
                logger.info(f"✅ STEP 4 COMPLETE: Video created ({file_size:.2f} MB)")
                
                # STEP 5: Generate thumbnail
                logger.info("\n📸 STEP 5: Creating thumbnail...")
                thumbnail_path = await self._generate_thumbnail(overlaid_paths[0], work_dir)
                logger.info(f"✅ STEP 5 COMPLETE: Thumbnail created")
                
                logger.info("\n" + "=" * 70)
                logger.info("✅✅✅ SUCCESS! ALL STEPS COMPLETED")
                logger.info("=" * 70)
                logger.info(f"📁 Debug files location: {work_dir}")
                logger.info(f"   - base_*.jpg (original images)")
                logger.info(f"   - overlaid_*.jpg (with text overlays)")
                logger.info(f"   - output.mp4 (final video)")
                logger.info("=" * 70 + "\n")
                
                return {
                    "success": True,
                    "video_url": f"/temp/{session_id}/output.mp4",
                    "thumbnail_url": f"/temp/{session_id}/thumbnail.jpg",
                    "duration": len(images) * duration_per_image,
                    "image_count": len(images),
                    "session_id": session_id,
                    "local_path": str(video_path),
                    "quality": quality_tier['name'],
                    "has_overlays": bool(product_data),
                    "has_music": music_path is not None,
                    "music_style": music_style,
                    "debug_dir": str(work_dir)
                }
                
            except Exception as e:
                logger.error(f"\n❌❌❌ TIER {quality_tier['name']} FAILED ❌❌❌")
                logger.error(f"Error: {e}")
                import traceback
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                
                if tier_index == len(self.QUALITY_TIERS) - 1:
                    return {"success": False, "error": str(e)}
                
                logger.info(f"⏭️  Trying next quality tier...")
                await asyncio.sleep(1)
        
        return {"success": False, "error": "All quality tiers failed"}
    
    async def _decode_and_save_images(
        self,
        images: List[str],
        work_dir: Path,
        target_size: Tuple[int, int]
    ) -> List[Path]:
        """Decode base64 images and save as JPG files"""
        saved_paths = []
        
        for idx, img_b64 in enumerate(images):
            try:
                logger.info(f"   Processing image {idx+1}/{len(images)}...")
                
                # Remove data URI prefix if present
                if 'base64,' in img_b64:
                    img_b64 = img_b64.split('base64,', 1)[1]
                
                # Decode base64
                img_data = base64.b64decode(img_b64.strip())
                logger.info(f"      Decoded: {len(img_data)} bytes")
                
                # Open image
                img = Image.open(io.BytesIO(img_data))
                img = img.convert('RGB')
                logger.info(f"      Original size: {img.size}")
                
                # Resize
                img = self._resize_to_target(img, target_size)
                logger.info(f"      Resized to: {img.size}")
                
                # Save
                save_path = work_dir / f"base_{idx:03d}.jpg"
                img.save(save_path, "JPEG", quality=95)
                saved_paths.append(save_path)
                
                logger.info(f"      ✅ Saved: {save_path.name}")
                
                img.close()
                del img
                gc.collect()
                
            except Exception as e:
                logger.error(f"      ❌ Image {idx+1} failed: {e}")
                raise
        
        return saved_paths
    
    def _resize_to_target(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize image to exact target size with padding"""
        target_w, target_h = target_size
        
        # Calculate scaling
        img_ratio = img.width / img.height
        target_ratio = target_w / target_h
        
        if img_ratio > target_ratio:
            new_w = target_w
            new_h = int(target_w / img_ratio)
        else:
            new_h = target_h
            new_w = int(target_h * img_ratio)
        
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Add black padding
        canvas = Image.new('RGB', target_size, (0, 0, 0))
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        canvas.paste(img, (paste_x, paste_y))
        
        return canvas
    
    async def _add_overlays_with_pil(
        self,
        base_paths: List[Path],
        product_data: Dict,
        work_dir: Path
    ) -> List[Path]:
        """Add text overlays using PIL"""
        overlaid_paths = []
        
        # Load fonts
        logger.info("   Loading fonts...")
        try:
            font_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
            logger.info("   ✅ System fonts loaded")
        except Exception as e:
            logger.warning(f"   ⚠️  Font loading failed: {e}, using default")
            font_xl = font_large = font_medium = ImageFont.load_default()
        
        # Extract product info
        brand = str(product_data.get("brand", "Brand"))[:20]
        product_name = str(product_data.get("product_name", "Product"))[:40]
        price = product_data.get("price", 0)
        discount = str(product_data.get("discount", ""))
        
        logger.info(f"   Product info: {brand} | {product_name[:25]} | Rs.{price}")
        
        # Text configurations for each image
        text_configs = [
            {"line1": f"🔥 {brand}", "line2": product_name, "color": (255, 215, 0)},
            {"line1": f"Rs.{int(price):,}" if price > 0 else "Best Deal", "line2": discount or "Special Price", "color": (0, 255, 127)},
            {"line1": "Premium Quality", "line2": "100% Original", "color": (255, 105, 180)},
            {"line1": "👇 Click Link Below", "line2": "Buy Now", "color": (255, 69, 0)},
        ]
        
        # Process each image
        for idx, base_path in enumerate(base_paths):
            try:
                logger.info(f"   Adding overlay to image {idx+1}...")
                
                img = Image.open(base_path)
                w, h = img.size
                logger.info(f"      Image size: {w}x{h}")
                
                draw = ImageDraw.Draw(img)
                config = text_configs[idx % len(text_configs)]
                
                text_area_height = int(h * 0.20)
                text_y_start = h - text_area_height - 50
                
                logger.info(f"      Text area: y={text_y_start} to y={h-50}")
                
                # Draw background
                bg_y = text_y_start - 20
                draw.rectangle([(0, bg_y), (w, h - 40)], fill=(0, 0, 0, 200))
                logger.info(f"      ✅ Background drawn")
                
                # Draw line 1
                line1 = config["line1"]
                bbox1 = draw.textbbox((0, 0), line1, font=font_xl)
                text1_w = bbox1[2] - bbox1[0]
                x1 = (w - text1_w) // 2
                
                draw.text((x1+3, text_y_start+3), line1, fill=(0, 0, 0), font=font_xl)
                draw.text((x1, text_y_start), line1, fill=config["color"], font=font_xl)
                logger.info(f"      ✅ Line 1: '{line1[:20]}...'")
                
                # Draw line 2
                line2 = config["line2"]
                bbox2 = draw.textbbox((0, 0), line2, font=font_large)
                text2_w = bbox2[2] - bbox2[0]
                x2 = (w - text2_w) // 2
                
                draw.text((x2+2, text_y_start+72), line2, fill=(0, 0, 0), font=font_large)
                draw.text((x2, text_y_start+70), line2, fill=(255, 255, 255), font=font_large)
                logger.info(f"      ✅ Line 2: '{line2[:20]}...'")
                
                # Brand watermark
                draw.text((20, 20), f"📱 {brand}", fill=(255, 255, 255), font=font_medium)
                
                # Save
                overlaid_path = work_dir / f"overlaid_{idx:03d}.jpg"
                img.save(overlaid_path, "JPEG", quality=95)
                overlaid_paths.append(overlaid_path)
                
                logger.info(f"      ✅ Saved: {overlaid_path.name} ({overlaid_path.stat().st_size / 1024:.1f} KB)")
                
                img.close()
                del img, draw
                gc.collect()
                
            except Exception as e:
                logger.error(f"      ❌ Overlay {idx+1} failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
                overlaid_paths.append(base_path)
        
        return overlaid_paths
    
    # ✅ UPDATED FUNCTION - Randomly picks from category
    async def _download_music(self, work_dir: Path, style: str) -> Optional[Path]:
        """Download background music (royalty-free) - randomly picks from category"""
        try:
            # Get list of tracks for selected style
            music_list = self.BACKGROUND_MUSIC.get(
                style,
                self.BACKGROUND_MUSIC["upbeat"]  # Fallback to upbeat
            )
            
            # Randomly select one track from the list
            music_url = random.choice(music_list)
            music_path = work_dir / "background_music.mp3"
            
            logger.info(f"   🎵 Selected style: {style}")
            logger.info(f"   🎵 Random track: {music_url}")
            
            # Download with timeout
            urllib.request.urlretrieve(music_url, music_path)
            
            if music_path.exists():
                logger.info(f"   ✅ Music downloaded: {music_path.stat().st_size / 1024:.1f} KB")
                return music_path
            
        except Exception as e:
            logger.warning(f"   ⚠️  Music download failed: {e}")
        
        return None
    
    async def _create_video_with_ffmpeg(
        self,
        image_paths: List[Path],
        duration: float,
        quality_tier: dict,
        work_dir: Path,
        music_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Create video with FFmpeg + optional background music"""
        
        output_path = work_dir / "output.mp4"
        resolution = quality_tier['resolution']
        
        # Create concat file
        concat_file = work_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for img_path in image_paths:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration}\n")
            f.write(f"file '{image_paths[-1]}'\n")
        
        logger.info(f"   Concat file: {concat_file}")
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
        ]
        
        # Add music input if available
        if music_path and music_path.exists():
            logger.info(f"   🎵 Adding background music: {music_path}")
            cmd.extend(["-i", str(music_path)])
            audio_filter = [
                "-filter_complex", "[1:a]volume=0.3[a]",  # Lower music volume to 30%
                "-map", "0:v",  # Video from input 0
                "-map", "[a]",  # Audio from filter
                "-shortest",  # Stop when shortest input ends
            ]
        else:
            logger.info("   ⚠️  No music added")
            audio_filter = []
        
        # Video encoding options
        cmd.extend([
            "-vf", f"fps=30,scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2",
            *audio_filter,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", quality_tier['preset'],
            "-crf", str(quality_tier['crf']),
            "-c:a", "aac",  # Audio codec
            "-b:a", "128k",  # Audio bitrate
            "-movflags", "+faststart",
            "-y",
            str(output_path)
        ])
        
        logger.info(f"   Running FFmpeg...")
        logger.info(f"   Command: {' '.join(cmd[:10])}...")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"   ❌ FFmpeg failed (exit code {process.returncode})")
                logger.error(f"   FFmpeg stderr: {stderr.decode()[:500]}")
                raise Exception(f"FFmpeg failed: {process.returncode}")
            
            if not output_path.exists():
                raise Exception("Output video not found")
            
            logger.info(f"   ✅ FFmpeg completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"   ❌ FFmpeg error: {e}")
            raise
    
    async def _generate_thumbnail(self, first_image: Path, work_dir: Path) -> Path:
        """Generate thumbnail"""
        thumb_path = work_dir / "thumbnail.jpg"
        try:
            img = Image.open(first_image)
            img.thumbnail((640, 360), Image.Resampling.LANCZOS)
            img.save(thumb_path, "JPEG", quality=85)
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