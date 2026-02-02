"""
Google Drive Bulk Video Downloader with FastAPI
This script downloads videos from a Google Drive folder and renames them sequentially.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import gdown
import os
from pathlib import Path
from typing import List, Dict
import re

app = FastAPI(title="Google Drive Video Downloader")

# Configuration
DOWNLOAD_DIR = "./downloads"
PREFIX = "aryan"

# Create download directory if it doesn't exist
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)


def extract_folder_id(url: str) -> str:
    """Extract folder ID from Google Drive URL"""
    patterns = [
        r'folders/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Could not extract folder ID from URL")


def download_folder(folder_id: str, output_dir: str) -> List[str]:
    """Download all files from a Google Drive folder"""
    try:
        # Construct the folder URL
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        
        # Download the entire folder
        print(f"Downloading from folder: {folder_url}")
        gdown.download_folder(
            url=folder_url,
            output=output_dir,
            quiet=False,
            use_cookies=False
        )
        
        # Get list of downloaded files
        downloaded_files = []
        for file in os.listdir(output_dir):
            if file.endswith('.mp4'):
                downloaded_files.append(os.path.join(output_dir, file))
        
        return downloaded_files
    
    except Exception as e:
        print(f"Error downloading folder: {str(e)}")
        raise


def rename_files(files: List[str], prefix: str = PREFIX) -> Dict[str, str]:
    """Rename files sequentially"""
    renamed_map = {}
    
    # Sort files to ensure consistent ordering
    files.sort()
    
    for idx, old_path in enumerate(files, start=1):
        directory = os.path.dirname(old_path)
        extension = os.path.splitext(old_path)[1]
        new_name = f"{prefix}{idx}{extension}"
        new_path = os.path.join(directory, new_name)
        
        # Rename the file
        os.rename(old_path, new_path)
        renamed_map[old_path] = new_path
        print(f"Renamed: {os.path.basename(old_path)} -> {new_name}")
    
    return renamed_map


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Google Drive Video Downloader API",
        "endpoints": {
            "/download": "POST - Download and rename videos from Google Drive folder",
            "/status": "GET - Check download directory status"
        }
    }


@app.post("/download")
async def download_and_rename(
    folder_url: str,
    prefix: str = PREFIX,
    clean_dir: bool = False
):
    """
    Download videos from Google Drive folder and rename them sequentially
    
    Args:
        folder_url: Full Google Drive folder URL
        prefix: Prefix for renamed files (default: 'aryan')
        clean_dir: Whether to clean the download directory before downloading
    """
    try:
        # Clean directory if requested
        if clean_dir and os.path.exists(DOWNLOAD_DIR):
            for file in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        # Extract folder ID
        folder_id = extract_folder_id(folder_url)
        print(f"Extracted folder ID: {folder_id}")
        
        # Download files
        print("Starting download...")
        downloaded_files = download_folder(folder_id, DOWNLOAD_DIR)
        
        if not downloaded_files:
            raise HTTPException(
                status_code=404,
                detail="No MP4 files found in the folder"
            )
        
        print(f"Downloaded {len(downloaded_files)} files")
        
        # Rename files
        print("Renaming files...")
        renamed_map = rename_files(downloaded_files, prefix)
        
        return JSONResponse(content={
            "status": "success",
            "total_files": len(renamed_map),
            "download_directory": DOWNLOAD_DIR,
            "files": [os.path.basename(new_path) for new_path in renamed_map.values()]
        })
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/status")
async def get_status():
    """Get current status of download directory"""
    if not os.path.exists(DOWNLOAD_DIR):
        return {"status": "Download directory does not exist"}
    
    files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.mp4')]
    files.sort()
    
    return {
        "download_directory": DOWNLOAD_DIR,
        "total_files": len(files),
        "files": files
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)