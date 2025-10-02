"""
slideshow_generator.py - Memory-optimized FFmpeg slideshow with quality fallback
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
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class SlideshowGenerator:
    """Generate video slideshows with memory optimization"""
    
    # Quality tiers (resolution, CRF, preset)
    QUALITY_TIERS = [
        {"name": "540p", "resolution": (540, 960), "crf": 28, "preset": "ultrafast"},
        {"name": "480p", "resolution": (480, 854), "crf": 30, "preset": "ultrafast"},
        {"name": "360p", "resolution": (360, 640), "crf": 32, "preset": "ultrafast"}
    ]
    
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"
        self.temp_dir = tempfile.gettempdir()
    
    async def generate_slideshow(
        self,
        images: List[str],
        title: str,
        language: str = "english",
        duration_per_image: float = 2.0,
        transition: str = "fade",
        add_text: bool = True,
        music_style: str = "upbeat",
        aspect_ratio: str = "9:16"
    ) -> Dict[str, Any]:
        """Generate slideshow with automatic quality fallback"""
        
        if not 2 <= len(images) <= 6:
            return {"success": False, "error": "Upload 2-6 images"}
        
        session_id = f"slideshow_{int(asyncio.get_event_loop().time() * 1000)}"
        work_dir = Path(self.temp_dir) / session_id
        work_dir.mkdir(exist_ok=True)
        
        # Try each quality tier
        for tier_index, quality_tier in enumerate(self.QUALITY_TIERS):
            try:
                logger.info(f"🎬 Attempting generation: {quality_tier['name']} (attempt {tier_index + 1}/3)")
                
                # Step 1: Save images with current quality
                image_paths = await self._save_images_optimized(
                    images, work_dir, quality_tier['resolution']
                )
                
                # Step 2: Add text overlays
                if add_text:
                    image_paths = await self._add_text_overlays(
                        image_paths, title, language, work_dir
                    )
                
                # Step 3: Generate video with FFmpeg
                video_path = await self._create_video_ffmpeg(
                    image_paths,
                    duration_per_image,
                    quality_tier,
                    work_dir
                )
                
                # Step 4: Generate thumbnail
                thumbnail_path = await self._generate_thumbnail(image_paths[0], work_dir)
                
                # SUCCESS - return result
                logger.info(f"✅ Video generated successfully at {quality_tier['name']}")
                
                return {
                    "success": True,
                    "video_url": f"/temp/{session_id}/output.mp4",
                    "thumbnail_url": f"/temp/{session_id}/thumbnail.jpg",
                    "duration": len(images) * duration_per_image,
                    "image_count": len(images),
                    "session_id": session_id,
                    "local_path": str(video_path),
                    "quality": quality_tier['name']
                }
                
            except Exception as e:
                logger.warning(f"❌ {quality_tier['name']} failed: {e}")
                
                # Clean up failed attempt
                try:
                    import shutil
                    shutil.rmtree(work_dir, ignore_errors=True)
                    work_dir.mkdir(exist_ok=True)
                except:
                    pass
                
                # Force garbage collection
                gc.collect()
                
                # If this was the last tier, fail
                if tier_index == len(self.QUALITY_TIERS) - 1:
                    return {
                        "success": False,
                        "error": f"All quality tiers failed. Last error: {str(e)}"
                    }
                
                # Otherwise, continue to next tier
                logger.info(f"⏩ Retrying with {self.QUALITY_TIERS[tier_index + 1]['name']}")
                continue
    
    async def _save_images_optimized(
        self, 
        images: List[str], 
        work_dir: Path,
        target_size: Tuple[int, int]
    ) -> List[Path]:
        """Save images with aggressive memory optimization"""
        image_paths = []
        
        for idx, img_b64 in enumerate(images):
            try:
                # Validate format
                if not isinstance(img_b64, str) or not img_b64.startswith('data:image/'):
                    raise ValueError(f"Image {idx + 1} invalid format")
                
                # Extract base64
                if 'base64,' in img_b64:
                    img_b64 = img_b64.split('base64,', 1)[1]
                else:
                    raise ValueError(f"Image {idx + 1} missing base64 data")
                
                # Decode
                img_b64 = img_b64.strip()
                img_data = base64.b64decode(img_b64)
                
                if len(img_data) < 100:
                    raise ValueError(f"Image {idx + 1} data too small")
                
                # Load image
                img = Image.open(io.BytesIO(img_data))
                img.load()
                
                # Resize immediately (memory critical)
                img = self._resize_with_padding(img, target_size)
                
                # Save with low quality
                img_path = work_dir / f"img_{idx:03d}.jpg"
                img.save(img_path, "JPEG", quality=75, optimize=True)
                
                # FREE MEMORY IMMEDIATELY
                img.close()
                del img
                del img_data
                del img_b64
                gc.collect()
                
                image_paths.append(img_path)
                logger.info(f"✅ Image {idx + 1} saved")
                
            except Exception as e:
                raise ValueError(f"Image {idx + 1} failed: {str(e)}")
        
        return image_paths
    
    def _resize_with_padding(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """Resize maintaining aspect ratio"""
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
    
    async def _add_text_overlays(
        self,
        image_paths: List[Path],
        title: str,
        language: str,
        work_dir: Path
    ) -> List[Path]:
        """Add text overlays"""
        overlay_paths = []
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        for idx, img_path in enumerate(image_paths):
            img = Image.open(img_path)
            draw = ImageDraw.Draw(img)
            
            if idx == 0 and title and font:  # Only first image
                text = title[:50]  # Limit length
                
                # Simple centered text
                x = img.width // 4
                y = 100
                
                # Shadow
                draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
                # Main text
                draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            overlay_path = work_dir / f"overlay_{idx:03d}.jpg"
            img.save(overlay_path, "JPEG", quality=75)
            overlay_paths.append(overlay_path)
            
            img.close()
            del img
            gc.collect()
        
        return overlay_paths
    
    async def _create_video_ffmpeg(
        self,
        image_paths: List[Path],
        duration: float,
        quality_tier: dict,
        work_dir: Path
    ) -> Path:
        """Generate video with memory-optimized FFmpeg settings"""
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
            "-vf", f"fps=24,scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,pad={resolution[0]}:{resolution[1]}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", quality_tier['preset'],
            "-crf", str(quality_tier['crf']),
            "-bufsize", "1M",
            "-maxrate", "1M",
            "-y",
            str(output_path)
        ]
        
        logger.info(f"🎥 FFmpeg command: {' '.join(cmd[:8])}...")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()[:500]
            raise Exception(f"FFmpeg failed: {error_msg}")
        
        file_size = output_path.stat().st_size / 1024 / 1024
        logger.info(f"✅ Video: {file_size:.2f} MB")
        
        return output_path
    
    async def _generate_thumbnail(self, first_image: Path, work_dir: Path) -> Path:
        """Generate thumbnail"""
        thumb_path = work_dir / "thumbnail.jpg"
        
        img = Image.open(first_image)
        img.thumbnail((640, 360), Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=75)
        img.close()
        
        return thumb_path


# Global instance
slideshow_generator = SlideshowGenerator()

def get_slideshow_generator():
    return slideshow_generator