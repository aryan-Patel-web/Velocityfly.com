"""
slideshow_generator.py - FFmpeg-based slideshow creator
100% free implementation using system FFmpeg
"""

import os
import asyncio
import logging
import subprocess
import tempfile
import base64
import io
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import random

logger = logging.getLogger(__name__)

class SlideshowGenerator:
    """Generate video slideshows using FFmpeg (free)"""
    
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"  # System FFmpeg
        self.temp_dir = tempfile.gettempdir()
        
        # Free trending audio tracks (YouTube Audio Library)
        self.free_audio_urls = {
            "upbeat": "https://cdn.jsdelivr.net/gh/username/audio@main/upbeat.mp3",
            "calm": "https://cdn.jsdelivr.net/gh/username/audio@main/calm.mp3",
            "energetic": "https://cdn.jsdelivr.net/gh/username/audio@main/energetic.mp3"
        }
    
    async def generate_slideshow(
        self,
        images: List[str],  # Base64 encoded images
        title: str,
        language: str = "english",
        duration_per_image: float = 2.0,
        transition: str = "fade",
        add_text: bool = True,
        music_style: str = "upbeat",
        aspect_ratio: str = "9:16"  # For YouTube Shorts/Reels
    ) -> Dict[str, Any]:
        """
        Generate slideshow video from images
        
        Args:
            images: List of base64 encoded images (2-6 images)
            title: Video title for text overlay
            language: hindi/english/hinglish
            duration_per_image: 1-3 seconds per image
            transition: fade/slide/zoom
            add_text: Add title overlay
            music_style: upbeat/calm/energetic
            aspect_ratio: 9:16 (Shorts) or 16:9 (regular)
            
        Returns:
            Dict with video_url, duration, thumbnail_url
        """
        try:
            logger.info(f"🎬 Generating slideshow: {len(images)} images, {language}")
            
            # Validate inputs
            if not 2 <= len(images) <= 6:
                return {
                    "success": False,
                    "error": "Please upload 2-6 images"
                }
            
            # Create temp directory for this slideshow
            session_id = f"slideshow_{int(asyncio.get_event_loop().time() * 1000)}"
            work_dir = Path(self.temp_dir) / session_id
            work_dir.mkdir(exist_ok=True)
            
            # Step 1: Decode and save images
            image_paths = await self._save_images(images, work_dir, aspect_ratio)
            
            # Step 2: Add text overlays if requested
            if add_text:
                image_paths = await self._add_text_overlays(
                    image_paths, title, language, work_dir
                )
            
            # Step 3: Generate video with FFmpeg
            video_path = await self._create_video_ffmpeg(
                image_paths,
                duration_per_image,
                transition,
                music_style,
                work_dir
            )
            
            # Step 4: Generate thumbnail
            thumbnail_path = await self._generate_thumbnail(image_paths[0], work_dir)
            
            # Step 5: Return results (in production, upload to cloud)
            video_url = f"/temp/{session_id}/output.mp4"
            thumbnail_url = f"/temp/{session_id}/thumbnail.jpg"
            
            return {
                "success": True,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "duration": len(images) * duration_per_image,
                "image_count": len(images),
                "session_id": session_id,
                "local_path": str(video_path)  # For immediate upload to YouTube
            }
            
        except Exception as e:
            logger.error(f"Slideshow generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _save_images(
        self, 
        images: List[str], 
        work_dir: Path,
        aspect_ratio: str
    ) -> List[Path]:
        """Decode base64 images and resize for aspect ratio"""
        image_paths = []
        target_size = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
        
        for idx, img_b64 in enumerate(images):
            try:
                # Clean the base64 string properly
                if isinstance(img_b64, str):
                    # Remove data:image/jpeg;base64, or data:image/png;base64, prefix
                    if img_b64.startswith('data:image'):
                        img_b64 = img_b64.split(',', 1)[1]
                    
                    # Remove any whitespace/newlines
                    img_b64 = img_b64.strip().replace('\n', '').replace('\r', '')
                
                # Decode base64
                try:
                    img_data = base64.b64decode(img_b64)
                except Exception as decode_error:
                    logger.error(f"Base64 decode failed for image {idx}: {decode_error}")
                    # Try with padding
                    missing_padding = len(img_b64) % 4
                    if missing_padding:
                        img_b64 += '=' * (4 - missing_padding)
                    img_data = base64.b64decode(img_b64)
                
                # Verify it's a valid image
                if len(img_data) < 100:
                    raise ValueError(f"Image data too small: {len(img_data)} bytes")
                
                # Open image
                img_buffer = io.BytesIO(img_data)
                img = Image.open(img_buffer)
                
                # Force load the image to catch any corruption
                img.load()
                
                logger.info(f"✅ Loaded image {idx}: {img.format} {img.size} {img.mode}")
                
                # Resize and pad to target aspect ratio
                img = self._resize_with_padding(img, target_size)
                
                img_path = work_dir / f"img_{idx:03d}.jpg"
                img.save(img_path, "JPEG", quality=95)
                image_paths.append(img_path)
                
                logger.info(f"✅ Saved image {idx + 1}: {img.size}")
                
            except Exception as e:
                logger.error(f"Failed to process image {idx}: {e}")
                logger.error(f"Image data preview: {str(img_b64)[:100] if isinstance(img_b64, str) else 'Not a string'}")
                raise ValueError(f"Image {idx + 1} processing failed: {str(e)}")
        
        return image_paths
    
    def _resize_with_padding(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """Resize image maintaining aspect ratio with padding"""
        # Calculate scaling
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            # Width is limiting factor
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
        else:
            # Height is limiting factor
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create padded image
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
        """Add text overlays to images"""
        overlay_paths = []
        
        # Language-specific fonts (use system fonts)
        font_map = {
            "hindi": "NotoSansDevanagari-Regular.ttf",
            "english": "Arial.ttf",
            "hinglish": "Arial.ttf"
        }
        
        try:
            font_size = 60
            font = ImageFont.truetype(font_map.get(language, "Arial.ttf"), font_size)
        except:
            font = ImageFont.load_default()
        
        for idx, img_path in enumerate(image_paths):
            img = Image.open(img_path)
            draw = ImageDraw.Draw(img)
            
            # Add text at top center
            text = title if idx == 0 else ""  # Only first image gets title
            if text:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (img.width - text_width) // 2
                y = 100
                
                # Add shadow
                draw.text((x+3, y+3), text, fill=(0, 0, 0), font=font)
                # Add main text
                draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            overlay_path = work_dir / f"overlay_{idx:03d}.jpg"
            img.save(overlay_path, "JPEG", quality=95)
            overlay_paths.append(overlay_path)
        
        return overlay_paths
    
    async def _create_video_ffmpeg(
        self,
        image_paths: List[Path],
        duration: float,
        transition: str,
        music_style: str,
        work_dir: Path
    ) -> Path:
        """Generate video using FFmpeg with transitions"""
        output_path = work_dir / "output.mp4"
        
        # Create file list for FFmpeg
        filelist_path = work_dir / "filelist.txt"
        with open(filelist_path, 'w') as f:
            for img_path in image_paths:
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration}\n")
            # Repeat last image
            f.write(f"file '{image_paths[-1]}'\n")
        
        # FFmpeg command with transitions
        transition_filters = {
            "fade": "fade=t=in:st=0:d=0.5,fade=t=out:st={dur-0.5}:d=0.5",
            "slide": "xfade=transition=slideleft:duration=0.5",
            "zoom": "zoompan=z='min(zoom+0.0015,1.5)':d={fps}*{dur}:s=1080x1920"
        }
        
        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-vf", f"fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "23",
            "-y",
            str(output_path)
        ]
        
        logger.info(f"🎥 Running FFmpeg: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg failed: {stderr.decode()}")
            raise Exception(f"Video generation failed: {stderr.decode()[:200]}")
        
        logger.info(f"✅ Video created: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return output_path
    
    async def _generate_thumbnail(self, first_image: Path, work_dir: Path) -> Path:
        """Generate thumbnail from first image"""
        thumb_path = work_dir / "thumbnail.jpg"
        
        img = Image.open(first_image)
        img.thumbnail((1280, 720), Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=85)
        
        return thumb_path


# Global instance
slideshow_generator = SlideshowGenerator()

def get_slideshow_generator():
    return slideshow_generator