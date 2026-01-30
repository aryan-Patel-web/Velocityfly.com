"""
china_enhanced.py - DOUYIN VIDEO AUTOMATION WITH PROFILE ID SCRAPING
===========================================================================
✅ Profile ID-based scraping (more reliable)
✅ Multiple fallback methods for each step
✅ Extensive logging for debugging
✅ Works in India (Douyin not banned)
✅ Complete A-Z pipeline: scrape → download → edit → upload
===========================================================================

TESTED PROFILES:
1. FUNNY/COMEDY:
   - Profile: "Escape and beating the meal"
   - ID: 56007218020
   - URL: https://www.douyin.com/user/MS4wLjABAAAAe-jjss5iSv02OGU_kOaQCc4jOSuHiCb3NlmA7koeoC7ISTKHLMtVTt-ELmNLkHfV

2. CUTE ANIMALS:
   - Profile: Cat Stories
   - ID: 78632067601
   - URL: https://www.douyin.com/user/MS4wLjABAAAA424aSWu0zdBbu6sTR0wIo-okI65xkC9dEltXycuVo0f3WdUTVbA1j8Hbi6Jvqwt1
===========================================================================
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import traceback
import uuid
import httpx
import json
import re
import random
import subprocess
from typing import List, Dict, Optional
import tempfile
import shutil
import gc
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_346aca9fb63af57816b2f0323b6312b75a65aa852656eeac")
ELEVENLABS_VOICE_ID = "nPczCjzI2devNBz1zQrb"

MAX_VIDEO_SIZE_MB = 50
FFMPEG_TIMEOUT = 360
TARGET_DURATION = 50
DOWNLOAD_TIMEOUT = 120

# ============================================================================
# NICHE CONFIGURATION - PROFILE ID BASED
# ============================================================================

NICHE_KEYWORDS = {
    "funny": {
        "name": "Funny / Comedy / Memes",
        "icon": "😂",
        "emoji": "😂🤣💀",
        "profiles": [
            {
                "name": "Escape and beating the meal",
                "douyin_id": "56007218020",
                "profile_url": "https://www.douyin.com/user/MS4wLjABAAAAe-jjss5iSv02OGU_kOaQCc4jOSuHiCb3NlmA7koeoC7ISTKHLMtVTt-ELmNLkHfV",
                "description": "401 fans, 236.2K likes",
                "search_urls": [
                    "https://www.douyin.com/user/MS4wLjABAAAAe-jjss5iSv02OGU_kOaQCc4jOSuHiCb3NlmA7koeoC7ISTKHLMtVTt-ELmNLkHfV?from_tab_name=main",
                    "https://www.douyin.com/search/搞笑",
                    "https://www.douyin.com/search/comedy"
                ]
            }
        ]
    },
    "animals": {
        "name": "Cute Animals / Pets",
        "icon": "🐶",
        "emoji": "🐶🐱❤️",
        "profiles": [
            {
                "name": "Cat Stories (Using cats to tell true stories)",
                "douyin_id": "78632067601",
                "profile_url": "https://www.douyin.com/user/MS4wLjABAAAA424aSWu0zdBbu6sTR0wIo-okI65xkC9dEltXycuVo0f3WdUTVbA1j8Hbi6Jvqwt1",
                "description": "69 fans, 1406 likes, Guangdong",
                "search_urls": [
                    "https://www.douyin.com/user/MS4wLjABAAAA424aSWu0zdBbu6sTR0wIo-okI65xkC9dEltXycuVo0f3WdUTVbA1j8Hbi6Jvqwt1?from_tab_name=main",
                    "https://www.douyin.com/search/萌宠",
                    "https://www.douyin.com/search/cute%20animals"
                ]
            }
        ]
    }
}

BACKGROUND_MUSIC_URLS = [
    "https://freesound.org/data/previews/456/456966_5121236-lq.mp3",
    "https://freesound.org/data/previews/391/391660_7181322-lq.mp3",
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_section(title: str, char: str = "="):
    """Print formatted section header"""
    line = char * 80
    logger.info(f"\n{line}")
    logger.info(f"{title.center(80)}")
    logger.info(f"{line}\n")

def force_cleanup(*filepaths):
    """Force cleanup with garbage collection"""
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
                logger.info(f"🗑️ Cleaned: {os.path.basename(fp)}")
        except Exception as e:
            logger.debug(f"Cleanup failed for {fp}: {e}")
    gc.collect()

def get_size_mb(fp: str) -> float:
    """Get file size in MB"""
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0.0

def get_random_user_agent():
    """Generate random user agent"""
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(agents)

def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """Run FFmpeg command with timeout and error handling"""
    try:
        logger.info(f"🎬 Running FFmpeg command...")
        logger.debug(f"   Command: {' '.join(cmd[:5])}...")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            timeout=timeout, 
            check=False, 
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ FFmpeg error (code {result.returncode})")
            logger.debug(f"   stderr: {result.stderr[:200]}")
            return False
        
        logger.info(f"✅ FFmpeg completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ FFmpeg timeout after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"❌ FFmpeg exception: {e}")
        return False

# ============================================================================
# DOUYIN SCRAPER CLASS - PROFILE ID BASED
# ============================================================================

class DouyinScraper:
    """
    Scrapes Douyin profiles using profile IDs and URLs
    Multiple fallback methods for reliability
    """
    
    def __init__(self):
        self.driver = None
        self.current_method = "selenium"
    
    def init_driver(self):
        """Initialize Chrome WebDriver with anti-detection"""
        try:
            print_section("🌐 INITIALIZING CHROME DRIVER")
            
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(f"user-agent={get_random_user_agent()}")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Additional anti-detection
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--start-maximized")
            
            logger.info("📦 Creating Chrome driver instance...")
            self.driver = webdriver.Chrome(options=options)
            
            # Stealth mode scripts
            logger.info("🥷 Applying stealth mode...")
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en', 'zh-CN', 'zh']
                    });
                '''
            })
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Driver initialization failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def scrape_profile_page(self, profile_url: str, profile_id: str, max_videos: int = 10) -> List[str]:
        """
        Method 1: Scrape profile page directly using profile URL
        This is the most reliable method
        """
        try:
            print_section(f"📱 METHOD 1: PROFILE PAGE SCRAPING")
            logger.info(f"   Profile ID: {profile_id}")
            logger.info(f"   URL: {profile_url[:70]}...")
            
            if not self.driver:
                logger.info("   Initializing driver...")
                if not self.init_driver():
                    return []
            
            # Navigate to profile
            logger.info("   Loading profile page...")
            self.driver.get(profile_url)
            
            # Wait for page load
            logger.info("   ⏳ Waiting 12 seconds for page to load...")
            time.sleep(12)
            
            # Scroll to load videos
            logger.info("   📜 Scrolling to load more videos...")
            for scroll in range(6):
                logger.info(f"      Scroll {scroll + 1}/6")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2.5)
            
            # Extract video URLs
            logger.info("   🔍 Extracting video URLs...")
            video_urls = []
            
            # Try multiple CSS selectors
            selectors = [
                "a[href*='/video/']",
                "a[href*='modal_id']",
                "div[class*='video'] a",
                "div[class*='card'] a",
                "li[class*='video'] a",
                "ul[class*='list'] a",
            ]
            
            for idx, selector in enumerate(selectors, 1):
                try:
                    logger.info(f"      Trying selector {idx}/{len(selectors)}: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"         Found {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            if href and ('video' in href or 'modal' in href):
                                # Ensure full URL
                                if not href.startswith('http'):
                                    href = 'https://www.douyin.com' + href
                                
                                if href not in video_urls:
                                    video_urls.append(href)
                                    logger.info(f"         ✅ Video {len(video_urls)}: {href[:60]}...")
                                    
                                    if len(video_urls) >= max_videos:
                                        logger.info(f"      🎯 Reached target of {max_videos} videos")
                                        break
                        except Exception as e:
                            logger.debug(f"         Element parse error: {e}")
                            continue
                    
                    if len(video_urls) >= max_videos:
                        break
                        
                except Exception as e:
                    logger.debug(f"      Selector {selector} failed: {e}")
                    continue
            
            logger.info(f"\n   ✅ Method 1 Result: {len(video_urls)} videos found")
            return video_urls[:max_videos]
            
        except Exception as e:
            logger.error(f"   ❌ Profile page scraping failed: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def scrape_search_page(self, search_url: str, max_videos: int = 10) -> List[str]:
        """
        Method 2: Scrape search results page (fallback)
        """
        try:
            print_section(f"📱 METHOD 2: SEARCH PAGE SCRAPING (FALLBACK)")
            logger.info(f"   URL: {search_url[:70]}...")
            
            if not self.driver:
                if not self.init_driver():
                    return []
            
            logger.info("   Loading search page...")
            self.driver.get(search_url)
            
            logger.info("   ⏳ Waiting 10 seconds...")
            time.sleep(10)
            
            logger.info("   📜 Scrolling...")
            for scroll in range(5):
                logger.info(f"      Scroll {scroll + 1}/5")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            logger.info("   🔍 Extracting URLs...")
            video_urls = []
            
            selectors = [
                "a[href*='/video/']",
                "a[href*='modal_id']",
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"      Selector {selector}: {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            if href and ('video' in href or 'modal' in href):
                                if not href.startswith('http'):
                                    href = 'https://www.douyin.com' + href
                                
                                if href not in video_urls:
                                    video_urls.append(href)
                                    logger.info(f"         ✅ Video {len(video_urls)}: {href[:60]}...")
                                    
                                    if len(video_urls) >= max_videos:
                                        break
                        except:
                            continue
                    
                    if len(video_urls) >= max_videos:
                        break
                        
                except Exception as e:
                    logger.debug(f"      Selector failed: {e}")
                    continue
            
            logger.info(f"\n   ✅ Method 2 Result: {len(video_urls)} videos found")
            return video_urls[:max_videos]
            
        except Exception as e:
            logger.error(f"   ❌ Search page scraping failed: {e}")
            return []
    
    def scrape_api_fallback(self, profile_id: str, max_videos: int = 10) -> List[str]:
        """
        Method 3: Try API-based scraping (experimental fallback)
        """
        try:
            print_section(f"📱 METHOD 3: API SCRAPING (EXPERIMENTAL)")
            logger.info(f"   Profile ID: {profile_id}")
            logger.info("   ⚠️ This method is experimental and may not work")
            
            # This is a placeholder for potential API methods
            # Douyin's API is not publicly documented
            logger.warning("   API method not implemented - skipping")
            return []
            
        except Exception as e:
            logger.error(f"   ❌ API scraping failed: {e}")
            return []
    
    def scrape_with_fallbacks(self, profile_info: dict, max_videos: int = 10) -> List[str]:
        """
        Master scraping method with multiple fallbacks
        """
        print_section(f"🎯 SCRAPING PROFILE: {profile_info['name']}")
        logger.info(f"   Douyin ID: {profile_info['douyin_id']}")
        logger.info(f"   Description: {profile_info['description']}")
        logger.info(f"   Target: {max_videos} videos")
        
        all_videos = []
        
        # Method 1: Profile page (primary)
        logger.info("\n🔄 Attempting Method 1: Profile Page")
        videos = self.scrape_profile_page(
            profile_info['profile_url'],
            profile_info['douyin_id'],
            max_videos
        )
        all_videos.extend(videos)
        logger.info(f"   Progress: {len(all_videos)}/{max_videos} videos")
        
        if len(all_videos) >= max_videos:
            logger.info(f"✅ SUCCESS: Got {len(all_videos)} videos from Method 1")
            return all_videos[:max_videos]
        
        # Method 2: Search URLs (fallback)
        logger.info("\n🔄 Attempting Method 2: Search Pages")
        for search_url in profile_info.get('search_urls', []):
            if len(all_videos) >= max_videos:
                break
            
            logger.info(f"\n   Trying search URL: {search_url[:60]}...")
            videos = self.scrape_search_page(search_url, max_videos - len(all_videos))
            
            # Add only unique videos
            for video in videos:
                if video not in all_videos:
                    all_videos.append(video)
            
            logger.info(f"   Progress: {len(all_videos)}/{max_videos} videos")
        
        if len(all_videos) > 0:
            logger.info(f"\n✅ TOTAL SCRAPED: {len(all_videos)} videos")
            return all_videos[:max_videos]
        else:
            logger.error("\n❌ FAILED: No videos found with any method")
            return []
    
    def close(self):
        """Close the driver"""
        try:
            if self.driver:
                logger.info("🔒 Closing Chrome driver...")
                self.driver.quit()
                self.driver = None
                logger.info("✅ Driver closed")
        except Exception as e:
            logger.debug(f"Driver close error: {e}")

# ============================================================================
# VIDEO DOWNLOAD - WITH FALLBACKS
# ============================================================================

async def download_video_from_url(video_url: str, video_id: str, temp_dir: str) -> Optional[str]:
    """
    Download video from Douyin URL with multiple fallback methods
    """
    print_section(f"📥 DOWNLOADING VIDEO: {video_id}")
    logger.info(f"   Source URL: {video_url[:70]}...")
    
    async with httpx.AsyncClient(timeout=60) as client:
        
        # Method 1: Direct page scraping
        logger.info("\n🔄 Method 1: Direct Page Scraping")
        try:
            logger.info("   Fetching page HTML...")
            response = await client.get(
                video_url,
                headers={
                    'User-Agent': get_random_user_agent(),
                    'Referer': 'https://www.douyin.com/',
                    'Accept': 'text/html,application/xhtml+xml',
                },
                follow_redirects=True
            )
            
            if response.status_code == 200:
                logger.info(f"   ✅ Page loaded ({len(response.text)} bytes)")
                html = response.text
                
                # Extract video URL patterns
                patterns = [
                    r'"playAddr":\[?"(https://[^"]+?\.mp4[^"]*)"',
                    r'playUrl":"(https://[^"]+\.mp4[^"]*)"',
                    r'"downloadAddr":"(https://[^"]+\.mp4[^"]*)"',
                    r'"play_addr_h264":\{"url_list":\["([^"]+)"',
                    r'"play_addr":\{"uri":"[^"]+","url_list":\["([^"]+)"',
                ]
                
                for idx, pattern in enumerate(patterns, 1):
                    logger.info(f"   Trying pattern {idx}/{len(patterns)}...")
                    matches = re.findall(pattern, html)
                    
                    if matches:
                        logger.info(f"      ✅ Found {len(matches)} matches")
                        video_download_url = matches[0]
                        video_download_url = video_download_url.replace('\\u002F', '/').replace('\\/', '/')
                        logger.info(f"      Video URL: {video_download_url[:60]}...")
                        
                        # Download video
                        logger.info("      Downloading video content...")
                        video_response = await client.get(
                            video_download_url,
                            headers={
                                'User-Agent': get_random_user_agent(),
                                'Referer': 'https://www.douyin.com/'
                            },
                            follow_redirects=True,
                            timeout=90
                        )
                        
                        if video_response.status_code == 200:
                            content = video_response.content
                            size_mb = len(content) / (1024 * 1024)
                            logger.info(f"      Downloaded: {size_mb:.2f}MB")
                            
                            if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                                video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
                                with open(video_path, 'wb') as f:
                                    f.write(content)
                                logger.info(f"   ✅ Method 1 SUCCESS: {size_mb:.1f}MB saved")
                                return video_path
                            else:
                                logger.warning(f"      Invalid size: {size_mb:.2f}MB")
                        else:
                            logger.warning(f"      Download failed: {video_response.status_code}")
            else:
                logger.warning(f"   Page load failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Method 1 failed: {e}")
        
        # Method 2: ssstik.io fallback
        logger.info("\n🔄 Method 2: ssstik.io Downloader")
        try:
            logger.info("   Sending request to ssstik.io...")
            response = await client.post(
                'https://ssstik.io/abc',
                params={'url': 'dl'},
                headers={
                    'User-Agent': get_random_user_agent(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                data={'id': video_url, 'locale': 'en', 'tt': 'NE9MVmM4'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("   ✅ Response received, parsing HTML...")
                soup = BeautifulSoup(response.text, "html.parser")
                link = soup.find('a')
                
                if link and 'href' in link.attrs:
                    download_link = link['href']
                    logger.info(f"   Found download link: {download_link[:60]}...")
                    logger.info("   Downloading video...")
                    
                    video_response = await client.get(download_link, follow_redirects=True, timeout=90)
                    
                    if video_response.status_code == 200:
                        content = video_response.content
                        size_mb = len(content) / (1024 * 1024)
                        logger.info(f"   Downloaded: {size_mb:.2f}MB")
                        
                        if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                            video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
                            with open(video_path, 'wb') as f:
                                f.write(content)
                            logger.info(f"   ✅ Method 2 SUCCESS: {size_mb:.1f}MB saved")
                            return video_path
                        else:
                            logger.warning(f"   Invalid size: {size_mb:.2f}MB")
                    else:
                        logger.warning(f"   Download failed: {video_response.status_code}")
                else:
                    logger.warning("   No download link found in response")
            else:
                logger.warning(f"   ssstik.io failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Method 2 failed: {e}")
        
        # Method 3: snaptik.app fallback
        logger.info("\n🔄 Method 3: snaptik.app Downloader")
        try:
            logger.info("   Sending request to snaptik.app...")
            response = await client.post(
                'https://snaptik.app/abc2.php',
                params={'url': 'dl'},
                headers={
                    'User-Agent': get_random_user_agent(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                data={'url': video_url, 'lang': 'en'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("   ✅ Response received, parsing...")
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.find_all('a', href=True)
                
                for link in links:
                    if 'download' in link.get('href', '').lower():
                        download_link = link['href']
                        logger.info(f"   Found download link: {download_link[:60]}...")
                        logger.info("   Downloading video...")
                        
                        video_response = await client.get(download_link, follow_redirects=True, timeout=90)
                        
                        if video_response.status_code == 200:
                            content = video_response.content
                            size_mb = len(content) / (1024 * 1024)
                            logger.info(f"   Downloaded: {size_mb:.2f}MB")
                            
                            if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                                video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
                                with open(video_path, 'wb') as f:
                                    f.write(content)
                                logger.info(f"   ✅ Method 3 SUCCESS: {size_mb:.1f}MB saved")
                                return video_path
            else:
                logger.warning(f"   snaptik.app failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"   ❌ Method 3 failed: {e}")
        
        logger.error("\n❌ ALL DOWNLOAD METHODS FAILED")
        return None

# ============================================================================
# AUDIO PROCESSING
# ============================================================================

async def extract_audio(video_path: str, temp_dir: str) -> Optional[str]:
    """Extract audio from video with fallback"""
    print_section("🎵 EXTRACTING AUDIO")
    logger.info(f"   Input: {os.path.basename(video_path)}")
    
    audio_path = os.path.join(temp_dir, "original_audio.mp3")
    
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "libmp3lame",
            "-b:a", "128k",
            "-y", audio_path
        ]
        
        if run_ffmpeg(cmd, 30):
            if os.path.exists(audio_path) and get_size_mb(audio_path) > 0.01:
                logger.info(f"✅ Audio extracted: {get_size_mb(audio_path):.2f}MB")
                return audio_path
        
        logger.error("❌ Audio extraction failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ Audio extraction error: {e}")
        return None

async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Whisper API with fallback"""
    print_section("🎤 TRANSCRIBING AUDIO")
    
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key:
            logger.info("   Using OpenAI Whisper API...")
            
            async with httpx.AsyncClient(timeout=120) as client:
                with open(audio_path, 'rb') as audio_file:
                    files = {'file': ('audio.mp3', audio_file, 'audio/mpeg')}
                    data = {'model': 'whisper-1', 'language': 'zh'}
                    
                    response = await client.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {openai_key}"},
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        transcript = response.json().get('text', '').strip()
                        logger.info(f"✅ Transcribed: {len(transcript)} characters")
                        logger.info(f"   Preview: {transcript[:100]}...")
                        return transcript
                    else:
                        logger.warning(f"   Whisper API failed: {response.status_code}")
        else:
            logger.warning("   OpenAI API key not found")
        
        # Fallback
        logger.info("⚠️ Using placeholder text (fallback)")
        return "这是一个有趣的视频内容，充满了精彩瞬间"
        
    except Exception as e:
        logger.warning(f"⚠️ Transcription failed: {e}")
        return "精彩视频内容"

async def translate_to_hindi(chinese_text: str) -> str:
    """Translate Chinese to Hindi using Mistral AI with fallback"""
    print_section("🌏 TRANSLATING TO HINDI")
    logger.info(f"   Input: {chinese_text[:100]}...")
    
    try:
        if not MISTRAL_API_KEY:
            logger.warning("   Mistral API key not found")
            return chinese_text
        
        logger.info("   Using Mistral AI for translation...")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-large-latest",
                    "messages": [{
                        "role": "user",
                        "content": f"Translate this Chinese text to natural, conversational Hindi. Provide ONLY the Hindi translation, nothing else:\n\n{chinese_text}"
                    }],
                    "temperature": 0.3,
                    "max_tokens": 300
                }
            )
            
            if response.status_code == 200:
                hindi_text = response.json()["choices"][0]["message"]["content"].strip()
                logger.info(f"✅ Translated successfully")
                logger.info(f"   Output: {hindi_text[:100]}...")
                return hindi_text
            else:
                logger.warning(f"   Translation failed: {response.status_code}")
        
        return chinese_text
        
    except Exception as e:
        logger.warning(f"⚠️ Translation failed: {e}")
        return chinese_text

# ============================================================================
# SCRIPT GENERATION
# ============================================================================

async def generate_creative_script(hindi_text: str, niche: str, original_title: str) -> dict:
    """Generate viral Hindi script for YouTube Shorts with fallback"""
    print_section("🤖 GENERATING CREATIVE SCRIPT")
    
    niche_config = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["funny"])
    logger.info(f"   Niche: {niche_config['name']}")
    logger.info(f"   Content length: {len(hindi_text)} characters")
    
    if not MISTRAL_API_KEY:
        logger.warning("   Mistral API key not found - using fallback")
        return generate_fallback_script(hindi_text, niche)
    
    prompt = f"""Create a viral Hindi YouTube Shorts script (30 seconds total).

NICHE: {niche_config['name']}
EMOJI THEME: {niche_config['emoji']}
ORIGINAL CONTENT: {hindi_text}

Create exactly 4 segments with precise timing:
1. HOOK (8 seconds) - Attention-grabbing opening
2. BUILD (12 seconds) - Story development
3. CLIMAX (7 seconds) - Peak moment
4. OUTRO (3 seconds) - Call to action

OUTPUT MUST BE VALID JSON ONLY (no markdown, no explanations):
{{
  "segments": [
    {{"narration": "Hindi hook text", "text_overlay": "{niche_config['emoji'].split()[0]}", "duration": 8}},
    {{"narration": "Hindi build text", "text_overlay": "{niche_config['emoji'].split()[1] if len(niche_config['emoji'].split()) > 1 else '🔥'}", "duration": 12}},
    {{"narration": "Hindi climax text", "text_overlay": "{niche_config['emoji'].split()[2] if len(niche_config['emoji'].split()) > 2 else '✨'}", "duration": 7}},
    {{"narration": "Hindi CTA", "text_overlay": "🔥", "duration": 3}}
  ],
  "title": "Viral Hindi title (under 70 characters)",
  "hashtags": ["{niche}", "viral", "shorts"]
}}"""
    
    try:
        logger.info("   Calling Mistral AI...")
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "You are a JSON generator. Output ONLY valid JSON, no markdown, no explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.9,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Remove markdown code blocks if present
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                
                script = json.loads(content)
                logger.info("✅ Script generated successfully")
                logger.info(f"   Title: {script.get('title', 'N/A')}")
                logger.info(f"   Segments: {len(script.get('segments', []))}")
                return script
            else:
                logger.warning(f"   Mistral API failed: {response.status_code}")
    
    except json.JSONDecodeError as e:
        logger.error(f"   JSON parse error: {e}")
    except Exception as e:
        logger.warning(f"   Script generation failed: {e}")
    
    logger.info("   Using fallback script template")
    return generate_fallback_script(hindi_text, niche)

def generate_fallback_script(text: str, niche: str) -> dict:
    """Fallback script templates for each niche"""
    logger.info(f"🔄 Generating fallback script for: {niche}")
    
    templates = {
        "funny": {
            "segments": [
                {"narration": f"अरे वाह! {text[:40]}", "text_overlay": "😂", "duration": 8},
                {"narration": "यह तो बहुत ही मजेदार है!", "text_overlay": "🤣", "duration": 12},
                {"narration": "एंडिंग देखो! माजा आ गया!", "text_overlay": "💀", "duration": 7},
                {"narration": "लाइक करो दोस्तों!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "इस वीडियो पर हंसी नहीं रुकेगी 😂💀",
            "hashtags": ["funny", "comedy", "viral", "hindi"]
        },
        "animals": {
            "segments": [
                {"narration": f"देखो कितना प्यारा! {text[:40]}", "text_overlay": "🐶", "duration": 8},
                {"narration": "यह तो दिल जीत लिया!", "text_overlay": "🐱", "duration": 12},
                {"narration": "सबसे क्यूट जानवर!", "text_overlay": "❤️", "duration": 7},
                {"narration": "शेयर करो!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "सबसे प्यारा जानवर वीडियो 🐶❤️",
            "hashtags": ["animals", "cute", "pets", "viral"]
        }
    }
    
    return templates.get(niche, templates["funny"])

# ============================================================================
# BACKGROUND MUSIC
# ============================================================================

async def download_background_music(temp_dir: str) -> Optional[str]:
    """Download background music with fallback URLs"""
    print_section("🎵 DOWNLOADING BACKGROUND MUSIC")
    
    music_path = os.path.join(temp_dir, "bg_music.mp3")
    
    for idx, url in enumerate(BACKGROUND_MUSIC_URLS, 1):
        try:
            logger.info(f"   Trying source {idx}/{len(BACKGROUND_MUSIC_URLS)}...")
            logger.info(f"   URL: {url[:60]}...")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, follow_redirects=True)
                
                if resp.status_code == 200:
                    with open(music_path, 'wb') as f:
                        f.write(resp.content)
                    
                    size_mb = get_size_mb(music_path)
                    if size_mb > 0.05:
                        logger.info(f"✅ Music downloaded: {size_mb:.2f}MB")
                        return music_path
                    else:
                        logger.warning(f"   File too small: {size_mb:.2f}MB")
                        force_cleanup(music_path)
                else:
                    logger.warning(f"   Download failed: {resp.status_code}")
        except Exception as e:
            logger.warning(f"   Source {idx} failed: {e}")
            continue
    
    logger.warning("⚠️ No background music available")
    return None

# ============================================================================
# VOICE GENERATION
# ============================================================================

async def generate_hindi_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Generate Hindi voiceover using ElevenLabs with fallback"""
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            logger.warning("   ⚠️ ElevenLabs API key not configured")
            return None
        
        text_clean = text.strip()[:500]
        temp_audio = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex[:6]}.mp3")
        
        logger.info(f"   🎤 Text: {text_clean[:50]}...")
        logger.info(f"   Duration: {duration}s")
        
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text_clean,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.4,
                        "similarity_boost": 0.8,
                        "style": 0.3,
                        "use_speaker_boost": True
                    }
                }
            )
            
            if response.status_code == 200:
                with open(temp_audio, 'wb') as f:
                    f.write(response.content)
                
                size_mb = get_size_mb(temp_audio)
                logger.info(f"      Generated: {size_mb:.2f}MB")
                
                if size_mb > 0.01:
                    # Adjust speed and normalize
                    output = temp_audio.replace(".mp3", "_adj.mp3")
                    
                    cmd = [
                        "ffmpeg",
                        "-i", temp_audio,
                        "-filter:a", "atempo=1.15,loudnorm=I=-16",
                        "-t", str(duration + 0.5),
                        "-b:a", "128k",
                        "-y", output
                    ]
                    
                    if run_ffmpeg(cmd, 20):
                        force_cleanup(temp_audio)
                        logger.info(f"   ✅ Voice ready: {get_size_mb(output):.2f}MB")
                        return output
                
                force_cleanup(temp_audio)
            else:
                logger.warning(f"   ElevenLabs failed: {response.status_code}")
                
    except Exception as e:
        logger.error(f"   Voice generation error: {e}")
    
    return None

# ============================================================================
# VIDEO PROCESSING
# ============================================================================

async def remove_original_audio(video_path: str, temp_dir: str) -> Optional[str]:
    """Remove original audio from video"""
    print_section("🔇 REMOVING ORIGINAL AUDIO")
    
    try:
        output = os.path.join(temp_dir, "video_no_audio.mp4")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-an",
            "-c:v", "copy",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 30):
            size_mb = get_size_mb(output)
            logger.info(f"✅ Audio removed: {size_mb:.1f}MB")
            return output
        
        logger.error("❌ Audio removal failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ Audio removal error: {e}")
        return None

async def process_video_for_shorts(video_path: str, target_duration: int, temp_dir: str) -> Optional[str]:
    """Process video for YouTube Shorts (1080x1920, 9:16)"""
    print_section(f"⚙️ PROCESSING FOR SHORTS")
    logger.info(f"   Target: {target_duration}s, 1080x1920 (9:16)")
    
    try:
        output = os.path.join(temp_dir, "processed.mp4")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-t", str(target_duration),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 90):
            size_mb = get_size_mb(output)
            logger.info(f"✅ Video processed: {size_mb:.1f}MB")
            return output
        
        logger.error("❌ Video processing failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ Processing error: {e}")
        return None

async def add_text_overlays(video: str, segments: list, temp_dir: str) -> Optional[str]:
    """Add text overlays to video"""
    print_section("📝 ADDING TEXT OVERLAYS")
    
    try:
        output = os.path.join(temp_dir, "with_text.mp4")
        
        filters = []
        current_time = 0
        
        for idx, seg in enumerate(segments, 1):
            text = seg.get("text_overlay", "").replace("'", "").replace('"', '')
            if text:
                logger.info(f"   Segment {idx}: {text} ({seg['duration']}s)")
                filters.append(
                    f"drawtext=text='{text}':"
                    f"fontsize=60:"
                    f"fontcolor=white:"
                    f"x=(w-text_w)/2:"
                    f"y=h-150:"
                    f"borderw=5:"
                    f"bordercolor=black:"
                    f"enable='between(t,{current_time},{current_time + seg['duration']})'"
                )
            
            current_time += seg["duration"]
        
        if not filters:
            logger.info("   No text overlays - skipping")
            return video
        
        vf = ",".join(filters)
        
        cmd = [
            "ffmpeg",
            "-i", video,
            "-vf", vf,
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "fast",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 60):
            force_cleanup(video)
            logger.info(f"✅ Text added: {get_size_mb(output):.1f}MB")
            return output
        
        logger.warning("⚠️ Text overlay failed - using original")
        return video
        
    except Exception as e:
        logger.error(f"❌ Text overlay error: {e}")
        return video

async def mix_audio_with_music(video: str, voices: List[str], music: Optional[str], temp_dir: str) -> Optional[str]:
    """Mix voiceovers with background music"""
    print_section("🎬 MIXING AUDIO")
    logger.info(f"   Voices: {len(voices)}")
    logger.info(f"   Music: {'Yes' if music else 'No'}")
    
    try:
        # Concatenate voices
        vlist = os.path.join(temp_dir, "voices.txt")
        with open(vlist, 'w') as f:
            for v in voices:
                f.write(f"file '{v}'\n")
        
        voice_combined = os.path.join(temp_dir, "voice_all.mp3")
        
        logger.info("   Concatenating voices...")
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", vlist,
            "-c", "copy",
            "-y", voice_combined
        ]
        
        if not run_ffmpeg(cmd, 30):
            logger.error("❌ Voice concatenation failed")
            return None
        
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            logger.info("   Mixing with background music...")
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];"
                "[2:a]volume=0.25,afade=t=in:d=1,afade=t=out:st=28:d=2[music];"
                "[voice][music]amix=inputs=2:duration=first[audio]",
                "-map", "0:v",
                "-map", "[audio]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", final
            ]
        else:
            logger.info("   Adding voice only (no music)...")
            cmd = [
                "ffmpeg",
                "-i", video,
                "-i", voice_combined,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                "-y", final
            ]
        
        if run_ffmpeg(cmd, 60):
            logger.info(f"✅ Final video: {get_size_mb(final):.1f}MB")
            return final
        
        logger.error("❌ Audio mixing failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ Mixing error: {e}")
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, 
                           hashtags: List[str], user_id: str, database_manager) -> dict:
    """Upload video to YouTube"""
    print_section("📤 UPLOADING TO YOUTUBE")
    logger.info(f"   Title: {title}")
    logger.info(f"   File: {os.path.basename(video_path)}")
    logger.info(f"   Size: {get_size_mb(video_path):.1f}MB")
    
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            logger.error("   YouTube database not available")
            return {"success": False, "error": "YouTube database not available"}
        
        if not yt_db.youtube.client:
            logger.info("   Connecting to database...")
            await yt_db.connect()
        
        logger.info("   Fetching credentials...")
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            logger.error("   YouTube credentials not found")
            return {"success": False, "error": "YouTube credentials not found"}
        
        credentials = {
            "access_token": credentials_raw.get("access_token"),
            "refresh_token": credentials_raw.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": credentials_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": credentials_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
        }
        
        from mainY import youtube_scheduler
        
        full_description = f"{description}\n\n#{' #'.join(hashtags)}"
        
        logger.info("   Uploading to YouTube...")
        upload_result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type="shorts",
            title=title,
            description=full_description,
            video_url=video_path
        )
        
        if upload_result.get("success"):
            video_id = upload_result.get("video_id")
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            logger.info(f"✅ UPLOAD SUCCESS")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
        
        logger.error(f"   Upload failed: {upload_result.get('error', 'Unknown error')}")
        return {"success": False, "error": upload_result.get("error", "Upload failed")}
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN PROCESSING PIPELINE
# ============================================================================

async def process_single_video(
    video_url: str,
    niche: str,
    user_id: str,
    show_captions: bool,
    database_manager,
    video_index: int,
    total_videos: int
) -> dict:
    """
    Process single video: download → edit → upload
    Sequential processing to avoid resource issues
    """
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"video_{video_index}_")
        
        print_section(f"🎬 VIDEO {video_index}/{total_videos}")
        logger.info(f"   Source: {video_url[:70]}...")
        logger.info(f"   Temp dir: {temp_dir}")
        
        # STEP 1: Download
        video_id = f"{niche}_{video_index}_{uuid.uuid4().hex[:6]}"
        video_path = await download_video_from_url(video_url, video_id, temp_dir)
        
        if not video_path:
            return {
                "success": False,
                "error": "Download failed - all methods exhausted",
                "video_url": video_url,
                "index": video_index
            }
        
        # STEP 2: Extract audio
        audio_path = await extract_audio(video_path, temp_dir)
        if not audio_path:
            return {"success": False, "error": "Audio extraction failed", "index": video_index}
        
        # STEP 3: Transcribe
        transcript = await transcribe_audio(audio_path)
        
        # STEP 4: Translate
        hindi_text = await translate_to_hindi(transcript)
        
        # STEP 5: Generate script
        script = await generate_creative_script(hindi_text, niche, f"Video {video_index}")
        
        # STEP 6: Download music
        music = await download_background_music(temp_dir)
        
        # STEP 7: Remove original audio
        video_no_audio = await remove_original_audio(video_path, temp_dir)
        if not video_no_audio:
            return {"success": False, "error": "Audio removal failed", "index": video_index}
        
        force_cleanup(video_path, audio_path)
        
        # STEP 8: Process for Shorts
        processed_video = await process_video_for_shorts(video_no_audio, TARGET_DURATION, temp_dir)
        if not processed_video:
            return {"success": False, "error": "Video processing failed", "index": video_index}
        
        force_cleanup(video_no_audio)
        
        # STEP 9: Add text overlays
        if show_captions:
            processed_video = await add_text_overlays(processed_video, script["segments"], temp_dir)
        
        # STEP 10: Generate voiceovers
        print_section("🎤 GENERATING VOICEOVERS")
        voices = []
        
        for idx, seg in enumerate(script["segments"], 1):
            logger.info(f"\n   Voice {idx}/{len(script['segments'])}")
            voice = await generate_hindi_voice(seg["narration"], seg["duration"], temp_dir)
            if voice:
                voices.append(voice)
        
        logger.info(f"\n   Total voices generated: {len(voices)}/{len(script['segments'])}")
        
        if len(voices) < 2:
            logger.warning(f"⚠️ Only {len(voices)} voices generated - video may have issues")
        
        # STEP 11: Mix audio
        final_video = await mix_audio_with_music(processed_video, voices, music, temp_dir)
        if not final_video:
            return {"success": False, "error": "Audio mixing failed", "index": video_index}
        
        # STEP 12: Upload to YouTube
        upload_result = await upload_to_youtube(
            final_video,
            script["title"],
            f"Video {video_index} - {niche} content with Hindi voiceover",
            script["hashtags"],
            user_id,
            database_manager
        )
        
        # Cleanup
        if temp_dir:
            logger.info(f"🗑️ Cleaning temp directory...")
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if not upload_result.get("success"):
            return {**upload_result, "index": video_index}
        
        print_section(f"✅ VIDEO {video_index} COMPLETE", "=")
        
        return {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script["title"],
            "source_url": video_url,
            "index": video_index
        }
        
    except Exception as e:
        logger.error(f"❌ VIDEO {video_index} FAILED")
        logger.error(f"   Error: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e), "index": video_index}

async def process_niche_videos(
    niche: str,
    num_videos: int,
    user_id: str,
    show_captions: bool,
    database_manager,
    custom_profile_urls: List[str] = None
) -> dict:
    """
    Main pipeline: Scrape Douyin profiles → Process videos sequentially
    """
    
    try:
        print_section("🚀 DOUYIN AUTOMATION PIPELINE START", "=")
        logger.info(f"   Niche: {niche}")
        logger.info(f"   Videos to generate: {num_videos}")
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Show captions: {show_captions}")
        logger.info(f"   Timestamp: {datetime.now()}")
        
        # Get niche config
        niche_config = NICHE_KEYWORDS.get(niche)
        if not niche_config:
            return {
                "success": False,
                "error": f"Invalid niche: {niche}. Available: {list(NICHE_KEYWORDS.keys())}"
            }
        
        logger.info(f"\n   Niche details: {niche_config['name']} {niche_config['icon']}")
        
        # Step 1: Scrape Douyin profiles
        print_section("📱 STEP 1: SCRAPING DOUYIN PROFILES")
        
        scraper = DouyinScraper()
        all_video_urls = []
        
        # Use custom URLs or profile defaults
        if custom_profile_urls:
            logger.info(f"   Using {len(custom_profile_urls)} custom URLs")
            for url in custom_profile_urls:
                logger.info(f"      • {url[:70]}...")
                videos = scraper.scrape_search_page(url, max_videos=15)
                all_video_urls.extend(videos)
        else:
            # Use configured profiles
            profiles = niche_config.get('profiles', [])
            logger.info(f"   Using {len(profiles)} configured profiles")
            
            for profile in profiles:
                if len(all_video_urls) >= num_videos * 3:  # Get 3x target for safety
                    break
                
                videos = scraper.scrape_with_fallbacks(profile, max_videos=20)
                all_video_urls.extend(videos)
                
                logger.info(f"\n   Progress: {len(all_video_urls)} total videos scraped")
        
        scraper.close()
        
        if not all_video_urls:
            return {
                "success": False,
                "error": "No videos found. Scraping failed for all methods."
            }
        
        logger.info(f"\n✅ SCRAPING COMPLETE: {len(all_video_urls)} videos found")
        
        # Shuffle and limit
        random.shuffle(all_video_urls)
        videos_to_process = all_video_urls[:num_videos]
        
        logger.info(f"   Selected {len(videos_to_process)} videos for processing")
        
        # Step 2: Process videos sequentially
        print_section("🎬 STEP 2: PROCESSING VIDEOS")
        
        results = []
        success_count = 0
        
        for idx, video_url in enumerate(videos_to_process, 1):
            print_section(f"PROCESSING VIDEO {idx}/{num_videos}", "=")
            
            result = await process_single_video(
                video_url=video_url,
                niche=niche,
                user_id=user_id,
                show_captions=show_captions,
                database_manager=database_manager,
                video_index=idx,
                total_videos=num_videos
            )
            
            results.append(result)
            
            if result.get("success"):
                success_count += 1
                logger.info(f"✅ Success rate: {success_count}/{idx}")
            else:
                logger.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            # Delay between videos
            if idx < num_videos:
                logger.info("\n⏸️ Waiting 5 seconds before next video...")
                await asyncio.sleep(5)
        
        # Final summary
        print_section("🎉 PIPELINE COMPLETE", "=")
        logger.info(f"   Total requested: {num_videos}")
        logger.info(f"   Successful: {success_count}")
        logger.info(f"   Failed: {num_videos - success_count}")
        logger.info(f"   Success rate: {(success_count/num_videos*100):.1f}%")
        
        return {
            "success": True,
            "total_requested": num_videos,
            "successful": success_count,
            "failed": num_videos - success_count,
            "success_rate": f"{(success_count/num_videos*100):.1f}%",
            "results": results,
            "niche": niche,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ PIPELINE FAILED")
        logger.error(f"   Error: {e}")
        logger.error(traceback.format_exc())
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter()

@router.get("/api/china/niches")
async def get_niches():
    """Get available niches with profile information"""
    return {
        "success": True,
        "niches": {
            key: {
                "name": config["name"],
                "icon": config["icon"],
                "emoji": config["emoji"],
                "profiles": [
                    {
                        "name": p["name"],
                        "douyin_id": p["douyin_id"],
                        "description": p["description"]
                    }
                    for p in config["profiles"]
                ]
            }
            for key, config in NICHE_KEYWORDS.items()
        },
        "note": "Currently supporting: funny, animals. More niches will be added."
    }

@router.post("/api/china/generate")
async def generate_endpoint(request: Request):
    """Generate videos from Douyin profiles"""
    try:
        data = await request.json()
        
        niche = data.get("niche", "funny")
        user_id = data.get("user_id")
        num_videos = data.get("num_videos", 1)
        show_captions = data.get("show_captions", True)
        custom_profile_urls = data.get("profile_urls", [])
        
        # Validation
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "user_id required"}
            )
        
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Invalid niche. Choose from: {list(NICHE_KEYWORDS.keys())}"
                }
            )
        
        if num_videos < 1 or num_videos > 10:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "num_videos must be between 1 and 10"}
            )
        
        from Supermain import database_manager
        
        logger.info(f"\n{'='*80}")
        logger.info(f"API REQUEST RECEIVED".center(80))
        logger.info(f"{'='*80}")
        logger.info(f"   User: {user_id}")
        logger.info(f"   Niche: {niche}")
        logger.info(f"   Videos: {num_videos}")
        logger.info(f"   Captions: {show_captions}")
        logger.info(f"   Custom URLs: {len(custom_profile_urls)}")
        
        try:
            result = await asyncio.wait_for(
                process_niche_videos(
                    niche=niche,
                    num_videos=num_videos,
                    user_id=user_id,
                    show_captions=show_captions,
                    database_manager=database_manager,
                    custom_profile_urls=custom_profile_urls
                ),
                timeout=1800  # 30 minutes
            )
            
            return JSONResponse(content=result)
            
        except asyncio.TimeoutError:
            logger.error("❌ REQUEST TIMEOUT (30 minutes)")
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Processing timeout (30 minutes)"}
            )
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.get("/api/china/test")
async def test_endpoint():
    """Test endpoint to verify service is running"""
    return {
        "success": True,
        "message": "Douyin Video Automation - Profile ID Based Scraping",
        "version": "2.0",
        "features": [
            "Profile ID-based scraping",
            "Multiple fallback methods",
            "Extensive logging",
            "Works in India",
            "Hindi translation & voiceover",
            "YouTube Shorts upload (1080x1920)"
        ],
        "niches": list(NICHE_KEYWORDS.keys()),
        "profiles_configured": sum(len(c["profiles"]) for c in NICHE_KEYWORDS.values()),
        "timestamp": datetime.now().isoformat()
    }

__all__ = ['router']