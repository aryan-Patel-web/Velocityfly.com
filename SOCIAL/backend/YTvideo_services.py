"""
Video Generation Service for YouTube Slideshows
Enhanced with comprehensive URL and image handling
"""

import os
import logging
import tempfile
import base64
from typing import List, Optional
import subprocess
import asyncio
import httpx
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoService:
    """Video generation service for slideshows with comprehensive image handling"""
    
    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
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
        """
        Create video slideshow from images (supports URLs, base64, local paths)
        
        Args:
            images: List of image sources (URLs, base64 data, or file paths)
            duration_per_image: Duration each image shows (seconds)
            output_format: Output format (mp4)
            
        Returns:
            Path to generated video file
        """
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg not installed on server")
        
        # ALLOW 1 IMAGE MINIMUM
        if not images or len(images) < 1:
            raise ValueError("Need at least 1 image for slideshow")
        
        # DUPLICATE SINGLE IMAGE
        if len(images) == 1:
            logger.info("⚠️ Only 1 image provided - duplicating for video")
            images = [images[0], images[0]]
        
        temp_dir = tempfile.mkdtemp()
        image_files = []
        
        try:
            # Process each image source
            for i, img_source in enumerate(images):
                img_path = os.path.join(temp_dir, f"img_{i:03d}.jpg")
                
                success = await self._process_image_source(img_source, img_path)
                
                if success:
                    image_files.append(img_path)
                    logger.info(f"✅ Image {i+1}/{len(images)} processed")
                else:
                    logger.warning(f"⚠️ Image {i+1} failed - skipping")
            
            if len(image_files) < 1:
                raise ValueError("No valid images could be processed")
            
            # DUPLICATE IF ONLY ONE SUCCEEDED
            if len(image_files) == 1:
                logger.info("Only 1 valid image - duplicating")
                duplicate_path = os.path.join(temp_dir, f"img_001.jpg")
                import shutil
                shutil.copy(image_files[0], duplicate_path)
                image_files.append(duplicate_path)
            
            # Create video using FFmpeg
            output_path = os.path.join(temp_dir, f"slideshow.{output_format}")
            
            total_duration = len(image_files) * duration_per_image
            
            # FFmpeg command for slideshow
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-framerate', f'1/{duration_per_image}',
                '-pattern_type', 'glob',
                '-i', os.path.join(temp_dir, 'img_*.jpg'),
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'fast',
                '-t', str(total_duration),  # Total duration
                output_path
            ]
            
            logger.info(f"🎬 Creating {total_duration}s video from {len(image_files)} images")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                logger.error(f"FFmpeg error: {error_msg}")
                raise RuntimeError(f"FFmpeg failed: {error_msg}")
            
            # Verify output file exists and has size
            if not os.path.exists(output_path):
                raise RuntimeError("Video file was not created")
            
            file_size = os.path.getsize(output_path)
            if file_size < 1000:  # Less than 1KB
                raise RuntimeError(f"Video file too small ({file_size} bytes)")
            
            logger.info(f"✅ Slideshow created: {output_path} ({file_size} bytes, {total_duration}s)")
            return output_path
            
        except Exception as e:
            logger.error(f"Slideshow creation failed: {e}")
            raise
        finally:
            # Cleanup temp image files (keep output video)
            for img_file in image_files:
                try:
                    os.unlink(img_file)
                except Exception:
                    pass
    
    async def _process_image_source(self, source: str, output_path: str) -> bool:
        """
        Process image from any source (URL, base64, local path)
        
        Args:
            source: Image source (URL, base64 string, or file path)
            output_path: Where to save the processed image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # CASE 1: Base64 encoded image
            if source.startswith('data:image'):
                return await self._process_base64_image(source, output_path)
            
            # CASE 2: HTTP/HTTPS URL
            elif source.startswith(('http://', 'https://')):
                return await self._process_url_image(source, output_path)
            
            # CASE 3: Local file path
            elif os.path.exists(source):
                return await self._process_local_image(source, output_path)
            
            # CASE 4: Unknown format
            else:
                logger.error(f"Unknown image source format: {source[:50]}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process image source: {e}")
            return False
    
    async def _process_base64_image(self, base64_str: str, output_path: str) -> bool:
        """Process base64 encoded image"""
        try:
            # Extract base64 data
            if ',' in base64_str:
                base64_data = base64_str.split(',', 1)[1]
            else:
                base64_data = base64_str
            
            # Decode
            img_bytes = base64.b64decode(base64_data)
            
            # Validate size
            if len(img_bytes) < 100:  # Less than 100 bytes
                logger.error("Base64 image too small")
                return False
            
            if len(img_bytes) > 10 * 1024 * 1024:  # More than 10MB
                logger.error("Base64 image too large")
                return False
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(img_bytes)
            
            logger.info(f"📦 Base64 image decoded ({len(img_bytes)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Base64 decode failed: {e}")
            return False
    
    async def _process_url_image(self, url: str, output_path: str) -> bool:
        """Download and process image from URL"""
        try:
            logger.info(f"🌐 Downloading image from URL...")
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    logger.error(f"URL download failed: HTTP {response.status_code}")
                    return False
                
                img_bytes = response.content
                
                # Validate size
                if len(img_bytes) < 100:
                    logger.error("Downloaded image too small")
                    return False
                
                if len(img_bytes) > 10 * 1024 * 1024:
                    logger.error("Downloaded image too large")
                    return False
                
                # Save to file
                with open(output_path, 'wb') as f:
                    f.write(img_bytes)
                
                logger.info(f"✅ URL image downloaded ({len(img_bytes)} bytes)")
                return True
                
        except httpx.TimeoutException:
            logger.error("Image download timeout")
            return False
        except Exception as e:
            logger.error(f"URL download failed: {e}")
            return False
    
    async def _process_local_image(self, file_path: str, output_path: str) -> bool:
        """Process local image file"""
        try:
            # Validate file
            if not os.path.isfile(file_path):
                logger.error(f"Not a file: {file_path}")
                return False
            
            file_size = os.path.getsize(file_path)
            
            if file_size < 100:
                logger.error("Local image too small")
                return False
            
            if file_size > 10 * 1024 * 1024:
                logger.error("Local image too large")
                return False
            
            # Copy file
            import shutil
            shutil.copy(file_path, output_path)
            
            logger.info(f"📁 Local image copied ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Local file copy failed: {e}")
            return False

# Global instance
_video_service = None

def get_video_service() -> VideoService:
    """Get video service singleton"""
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service