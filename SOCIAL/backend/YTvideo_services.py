"""
Video Generation Service for YouTube Slideshows
Fixed: Proper image format conversion to prevent FFmpeg errors
"""

import os
import logging
import tempfile
import base64
from typing import List
import subprocess
import asyncio
import httpx
from PIL import Image
import io

logger = logging.getLogger(__name__)

class VideoService:
    """Video generation service with proper image format handling"""
    
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
        logger.info(f"VideoService initialized - FFmpeg: {self.ffmpeg_available}")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed"""
        try:
            import shutil
            return shutil.which('ffmpeg') is not None
        except Exception:
            return False
    
    async def create_slideshow(
        self,
        images: List[str],
        duration_per_image: float = 2.0,
        output_format: str = 'mp4'
    ) -> str:
        """Create video slideshow from images with proper format conversion"""
        
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg not installed on server")
        
        if not images or len(images) < 1:
            raise ValueError("Need at least 1 image for slideshow")
        
        if len(images) == 1:
            logger.info("Only 1 image - duplicating for video")
            images = [images[0], images[0]]
        
        temp_dir = tempfile.mkdtemp()
        image_files = []
        
        try:
            # Process and convert each image
            for i, img_source in enumerate(images):
                img_path = os.path.join(temp_dir, f"img_{i:03d}.jpg")
                
                success = await self._process_and_convert_image(img_source, img_path)
                
                if success:
                    image_files.append(img_path)
                    logger.info(f"✅ Image {i+1}/{len(images)} processed")
                else:
                    logger.warning(f"⚠️ Image {i+1} failed - skipping")
            
            if len(image_files) < 1:
                raise ValueError("No valid images could be processed")
            
            if len(image_files) == 1:
                logger.info("Only 1 valid image - duplicating")
                duplicate_path = os.path.join(temp_dir, f"img_001.jpg")
                import shutil
                shutil.copy(image_files[0], duplicate_path)
                image_files.append(duplicate_path)
            
            # Create filelist for FFmpeg
            filelist_path = os.path.join(temp_dir, 'filelist.txt')
            with open(filelist_path, 'w') as f:
                for img_file in image_files:
                    f.write(f"file '{os.path.basename(img_file)}'\n")
                    f.write(f"duration {duration_per_image}\n")
                # Repeat last image
                f.write(f"file '{os.path.basename(image_files[-1])}'\n")
            
            output_path = os.path.join(temp_dir, f"slideshow.{output_format}")
            total_duration = len(image_files) * duration_per_image
            
            # FFmpeg command using concat demuxer
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', filelist_path,
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-y',
                output_path
            ]
            
            logger.info(f"🎬 Creating {total_duration}s video from {len(image_files)} images")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                logger.error(f"FFmpeg error: {error_msg[:500]}")
                raise RuntimeError(f"FFmpeg failed: {error_msg[:200]}")
            
            if not os.path.exists(output_path):
                raise RuntimeError("Video file was not created")
            
            file_size = os.path.getsize(output_path)
            if file_size < 1000:
                raise RuntimeError(f"Video file too small ({file_size} bytes)")
            
            logger.info(f"✅ Slideshow created: {output_path} ({file_size} bytes, {total_duration}s)")
            return output_path
            
        except Exception as e:
            logger.error(f"Slideshow creation failed: {e}")
            raise
    
    async def _process_and_convert_image(self, source: str, output_path: str) -> bool:
        """
        Process image from any source and convert to proper JPEG format
        Handles: Base64, URLs, local files, GIF, PNG, WebP, JPEG
        """
        try:
            # Get raw image bytes
            img_bytes = await self._get_image_bytes(source)
            
            if not img_bytes:
                return False
            
            # Convert to proper JPEG using PIL
            return await self._convert_to_jpeg(img_bytes, output_path)
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return False
    
    async def _get_image_bytes(self, source: str) -> bytes:
        """Get image bytes from any source"""
        try:
            # Base64 encoded image
            if source.startswith('data:image'):
                base64_data = source.split(',', 1)[1] if ',' in source else source
                img_bytes = base64.b64decode(base64_data)
                logger.info(f"📦 Base64 decoded ({len(img_bytes)} bytes)")
                return img_bytes
            
            # HTTP/HTTPS URL
            elif source.startswith(('http://', 'https://')):
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(source)
                    if response.status_code == 200:
                        logger.info(f"🌐 URL downloaded ({len(response.content)} bytes)")
                        return response.content
                    else:
                        logger.error(f"URL failed: HTTP {response.status_code}")
                        return None
            
            # Local file path
            elif os.path.exists(source):
                with open(source, 'rb') as f:
                    img_bytes = f.read()
                logger.info(f"📁 Local file read ({len(img_bytes)} bytes)")
                return img_bytes
            
            else:
                logger.error(f"Unknown source format: {source[:50]}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get image bytes: {e}")
            return None
    
    async def _convert_to_jpeg(self, img_bytes: bytes, output_path: str) -> bool:
        """
        Convert any image format to proper JPEG
        Handles: GIF, PNG, WebP, JPEG, transparency, etc.
        """
        try:
            # Validate size
            if len(img_bytes) < 100:
                logger.error("Image too small")
                return False
            
            if len(img_bytes) > 10 * 1024 * 1024:
                logger.error("Image too large")
                return False
            
            # Open with PIL
            img = Image.open(io.BytesIO(img_bytes))
            
            # Convert to RGB (removes alpha channel, handles all formats)
            if img.mode in ('RGBA', 'LA', 'P', 'PA'):
                # Create white background for transparency
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                
                # Handle palette images
                if img.mode == 'P':
                    img = img.convert('RGBA')
                
                # Paste with alpha mask
                if img.mode in ('RGBA', 'LA', 'PA'):
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                
                img = rgb_img
            
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if needed
            max_width, max_height = 1920, 1080
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized to {img.width}x{img.height}")
            
            # Ensure minimum size
            if img.width < 400 or img.height < 400:
                new_width = max(img.width, 400)
                new_height = max(img.height, 400)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as high-quality JPEG
            img.save(output_path, 'JPEG', quality=95, optimize=True)
            
            logger.info(f"✅ Converted to JPEG: {img.width}x{img.height}")
            return True
            
        except Exception as e:
            logger.error(f"JPEG conversion failed: {e}")
            return False


# Global instance
_video_service = None

def get_video_service() -> VideoService:
    """Get video service singleton"""
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service