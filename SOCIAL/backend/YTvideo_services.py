"""
Video Generation Service for YouTube Slideshows
"""

import os
import logging
import tempfile
import base64
from typing import List, Optional
import subprocess
import asyncio

logger = logging.getLogger(__name__)

class VideoService:
    """Video generation service for slideshows"""
    
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
        """
        Create video slideshow from images
        
        Args:
            images: List of base64 image data or file paths
            duration_per_image: Duration each image shows (seconds)
            output_format: Output format (mp4)
            
        Returns:
            Path to generated video file
        """
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg not installed on server")
        
        if len(images) < 2:
            raise ValueError("Need at least 2 images for slideshow")
        
        temp_dir = tempfile.mkdtemp()
        image_files = []
        
        try:
            # Save images to temp files
            for i, img_data in enumerate(images):
                img_path = os.path.join(temp_dir, f"img_{i:03d}.jpg")
                
                if img_data.startswith('data:image'):
                    # Decode base64
                    base64_data = img_data.split(',')[1]
                    img_bytes = base64.b64decode(base64_data)
                    with open(img_path, 'wb') as f:
                        f.write(img_bytes)
                else:
                    # Copy file
                    import shutil
                    shutil.copy(img_data, img_path)
                
                image_files.append(img_path)
            
            # Create video using FFmpeg
            output_path = os.path.join(temp_dir, f"slideshow.{output_format}")
            
            # FFmpeg command for slideshow
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-framerate', f'1/{duration_per_image}',  # Frame rate
                '-pattern_type', 'glob',
                '-i', os.path.join(temp_dir, 'img_*.jpg'),
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',  # Shorts format
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'fast',
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                raise RuntimeError(f"FFmpeg failed: {error_msg}")
            
            logger.info(f"✅ Slideshow created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Slideshow creation failed: {e}")
            raise
        finally:
            # Cleanup temp image files (but keep output video)
            for img_file in image_files:
                try:
                    os.unlink(img_file)
                except Exception:
                    pass

# Global instance
_video_service = None

def get_video_service() -> VideoService:
    """Get video service singleton"""
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service