"""
china_enhanced_v3.py - DOUYIN VIDEO AUTOMATION - ENHANCED SCRAPING
===========================================================================
✅ Improved profile scraping with multiple methods
✅ Extensive fallback mechanisms for reliability
✅ Comprehensive logging for debugging
✅ Profile-specific scraping for tested profiles
✅ Works in India (Douyin not banned)
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from bs4 import BeautifulSoup

# ============================================================================
# ENHANCED LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Success/Error tracking
class MetricsTracker:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.scraping_attempts = 0
        self.scraping_success = 0
        self.scraping_failures = 0
        self.download_attempts = 0
        self.download_success = 0
        self.download_failures = 0
        self.processing_attempts = 0
        self.processing_success = 0
        self.processing_failures = 0
        self.upload_attempts = 0
        self.upload_success = 0
        self.upload_failures = 0
        self.errors = []
    
    def log_error(self, stage: str, error: str):
        self.errors.append({"stage": stage, "error": error, "timestamp": datetime.now().isoformat()})
    
    def get_summary(self):
        return {
            "scraping": {
                "attempts": self.scraping_attempts,
                "success": self.scraping_success,
                "failures": self.scraping_failures,
                "rate": f"{(self.scraping_success/max(self.scraping_attempts,1)*100):.1f}%"
            },
            "download": {
                "attempts": self.download_attempts,
                "success": self.download_success,
                "failures": self.download_failures,
                "rate": f"{(self.download_success/max(self.download_attempts,1)*100):.1f}%"
            },
            "processing": {
                "attempts": self.processing_attempts,
                "success": self.processing_success,
                "failures": self.processing_failures,
                "rate": f"{(self.processing_success/max(self.processing_attempts,1)*100):.1f}%"
            },
            "upload": {
                "attempts": self.upload_attempts,
                "success": self.upload_success,
                "failures": self.upload_failures,
                "rate": f"{(self.upload_success/max(self.upload_attempts,1)*100):.1f}%"
            },
            "errors": self.errors[-10:]  # Last 10 errors
        }

metrics = MetricsTracker()

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
# NICHE CONFIGURATION - SPECIFIC PROFILES
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
                "user_handle": "MS4wLjABAAAAe-jjss5iSv02OGU_kOaQCc4jOSuHiCb3NlmA7koeoC7ISTKHLMtVTt-ELmNLkHfV",
                "backup_urls": [
                    "https://www.douyin.com/user/MS4wLjABAAAAe-jjss5iSv02OGU_kOaQCc4jOSuHiCb3NlmA7koeoC7ISTKHLMtVTt-ELmNLkHfV?from_tab_name=main&vid=7598359235156352421",
                    "https://www.douyin.com/search/搞笑?type=general",
                    "https://www.douyin.com/search/comedy?type=general"
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
                "user_handle": "MS4wLjABAAAA424aSWu0zdBbu6sTR0wIo-okI65xkC9dEltXycuVo0f3WdUTVbA1j8Hbi6Jvqwt1",
                "backup_urls": [
                    "https://www.douyin.com/user/MS4wLjABAAAA424aSWu0zdBbu6sTR0wIo-okI65xkC9dEltXycuVo0f3WdUTVbA1j8Hbi6Jvqwt1?from_tab_name=main",
                    "https://www.douyin.com/search/萌宠?type=general",
                    "https://www.douyin.com/search/cute%20animals?type=general"
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

def log_step(step_num: int, total_steps: int, title: str, status: str = "START"):
    """Log a processing step with progress"""
    logger.info(f"{'='*80}")
    logger.info(f"STEP {step_num}/{total_steps}: {title} [{status}]")
    logger.info(f"{'='*80}")

def force_cleanup(*filepaths):
    """Force cleanup with garbage collection"""
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
                logger.debug(f"🗑️ Cleaned: {os.path.basename(fp)}")
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
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    ]
    return random.choice(agents)

def run_ffmpeg(cmd: list, timeout: int = FFMPEG_TIMEOUT) -> bool:
    """Run FFmpeg command with timeout and error handling"""
    try:
        logger.debug(f"FFmpeg: {' '.join(cmd[:5])}...")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            timeout=timeout, 
            check=False, 
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"❌ FFmpeg error (code {result.returncode})")
            logger.debug(f"stderr: {result.stderr[:300]}")
            return False
        
        logger.debug(f"✅ FFmpeg completed")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ FFmpeg timeout after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"❌ FFmpeg exception: {e}")
        return False

# ============================================================================
# ENHANCED DOUYIN SCRAPER WITH MULTIPLE METHODS
# ============================================================================

class EnhancedDouyinScraper:
    """
    Enhanced scraper with multiple fallback methods for Douyin profiles
    """
    
    def __init__(self):
        self.driver = None
        self.session = None
    
    def init_driver(self):
        """Initialize Chrome WebDriver with enhanced anti-detection"""
        try:
            logger.info("🌐 Initializing Chrome WebDriver...")
            
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
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
            logger.info("   Creating driver instance...")
            self.driver = webdriver.Chrome(options=options)
            
            # Enhanced stealth mode
            logger.info("   Applying stealth mode...")
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
                    window.navigator.chrome = {
                        runtime: {}
                    };
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({ state: 'granted' })
                        })
                    });
                '''
            })
            
            logger.info("✅ Driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Driver init failed: {e}")
            metrics.log_error("scraping", f"Driver init: {str(e)}")
            return False
    
    async def scrape_profile_method_1(self, profile_url: str, profile_id: str, max_videos: int = 15) -> List[str]:
        """
        METHOD 1: Direct profile page scraping
        Most reliable for specific profiles
        """
        logger.info("🔹 METHOD 1: Direct Profile Scraping")
        logger.info(f"   Profile URL: {profile_url[:70]}...")
        logger.info(f"   Profile ID: {profile_id}")
        
        try:
            metrics.scraping_attempts += 1
            
            if not self.driver:
                if not self.init_driver():
                    return []
            
            # Navigate to profile
            logger.info("   Loading profile page...")
            self.driver.get(profile_url)
            
            # Wait for initial load
            logger.info("   ⏳ Waiting 15 seconds for page load...")
            time.sleep(15)
            
            # Take screenshot for debugging
            try:
                screenshot_path = f"/tmp/douyin_profile_{profile_id}_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"   📸 Screenshot saved: {screenshot_path}")
            except:
                pass
            
            # Enhanced scrolling with variable delays
            logger.info("   📜 Scrolling to load videos...")
            for scroll in range(8):
                logger.info(f"      Scroll {scroll + 1}/8")
                
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2.0, 3.5))
                
                # Scroll up a bit (mimic human behavior)
                if scroll % 3 == 0:
                    self.driver.execute_script("window.scrollBy(0, -300);")
                    time.sleep(random.uniform(1.0, 2.0))
            
            # Get page source for debugging
            logger.info("   📄 Getting page source...")
            page_source = self.driver.page_source
            logger.info(f"   Page source length: {len(page_source)} characters")
            
            # Save HTML for debugging
            try:
                html_path = f"/tmp/douyin_profile_{profile_id}_{int(time.time())}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logger.info(f"   💾 HTML saved: {html_path}")
            except:
                pass
            
            # Extract video URLs with comprehensive selectors
            logger.info("   🔍 Extracting video URLs...")
            video_urls = set()  # Use set to avoid duplicates
            
            # Multiple selector strategies
            selectors = [
                "a[href*='/video/']",
                "a[href*='modal_id']",
                "a[href*='/note/']",
                "div[class*='video'] a",
                "div[class*='Video'] a",
                "div[class*='card'] a",
                "div[class*='Card'] a",
                "li[class*='video'] a",
                "li[class*='Video'] a",
                "ul[class*='list'] a",
                "div[data-e2e*='video'] a",
                "div[data-e2e*='user-post'] a",
            ]
            
            for idx, selector in enumerate(selectors, 1):
                try:
                    logger.info(f"      Selector {idx}/{len(selectors)}: {selector}")
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"         Found {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            if href and ('video' in href or 'modal' in href or 'note' in href):
                                # Ensure full URL
                                if not href.startswith('http'):
                                    href = 'https://www.douyin.com' + href
                                
                                # Clean URL (remove query params except essential ones)
                                clean_href = href.split('?')[0]
                                
                                if clean_href not in video_urls and len(video_urls) < max_videos:
                                    video_urls.add(clean_href)
                                    logger.info(f"         ✅ Video {len(video_urls)}: {clean_href[:60]}...")
                                    
                                    if len(video_urls) >= max_videos:
                                        break
                        except Exception as e:
                            logger.debug(f"         Element error: {e}")
                            continue
                    
                    if len(video_urls) >= max_videos:
                        break
                        
                except Exception as e:
                    logger.debug(f"      Selector {selector} failed: {e}")
                    continue
            
            result_list = list(video_urls)
            logger.info(f"   ✅ Method 1: {len(result_list)} videos found")
            
            if len(result_list) > 0:
                metrics.scraping_success += 1
            
            return result_list
            
        except Exception as e:
            logger.error(f"   ❌ Method 1 failed: {e}")
            logger.error(traceback.format_exc())
            metrics.log_error("scraping_method_1", str(e))
            return []
    
    async def scrape_profile_method_2(self, profile_url: str, max_videos: int = 15) -> List[str]:
        """
        METHOD 2: BeautifulSoup + httpx (no browser)
        Faster but may miss dynamic content
        """
        logger.info("🔹 METHOD 2: HTTP + BeautifulSoup Scraping")
        
        try:
            metrics.scraping_attempts += 1
            
            logger.info("   Sending HTTP request...")
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    profile_url,
                    headers={
                        'User-Agent': get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                        'Referer': 'https://www.douyin.com/',
                        'Connection': 'keep-alive',
                    },
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    logger.info(f"   ✅ Page loaded ({len(response.text)} bytes)")
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links
                    links = soup.find_all('a', href=True)
                    logger.info(f"   Found {len(links)} total links")
                    
                    video_urls = set()
                    for link in links:
                        href = link.get('href', '')
                        if 'video' in href or 'modal' in href or 'note' in href:
                            if not href.startswith('http'):
                                href = 'https://www.douyin.com' + href
                            
                            clean_href = href.split('?')[0]
                            if clean_href not in video_urls and len(video_urls) < max_videos:
                                video_urls.add(clean_href)
                                logger.info(f"      ✅ Video {len(video_urls)}: {clean_href[:60]}...")
                    
                    result_list = list(video_urls)
                    logger.info(f"   ✅ Method 2: {len(result_list)} videos found")
                    
                    if len(result_list) > 0:
                        metrics.scraping_success += 1
                    
                    return result_list
                else:
                    logger.warning(f"   HTTP failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"   ❌ Method 2 failed: {e}")
            metrics.log_error("scraping_method_2", str(e))
            return []
    
    async def scrape_backup_urls(self, backup_urls: List[str], max_videos: int = 15) -> List[str]:
        """
        METHOD 3: Try backup/search URLs
        """
        logger.info("🔹 METHOD 3: Backup URLs Scraping")
        
        all_videos = set()
        
        for idx, url in enumerate(backup_urls, 1):
            try:
                logger.info(f"   Backup URL {idx}/{len(backup_urls)}: {url[:60]}...")
                
                if not self.driver:
                    if not self.init_driver():
                        continue
                
                self.driver.get(url)
                time.sleep(10)
                
                # Quick scroll
                for _ in range(3):
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1.5)
                
                # Extract links
                elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/video/'], a[href*='modal_id']")
                logger.info(f"      Found {len(elements)} potential video links")
                
                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        if href and ('video' in href or 'modal' in href):
                            if not href.startswith('http'):
                                href = 'https://www.douyin.com' + href
                            
                            clean_href = href.split('?')[0]
                            if clean_href not in all_videos:
                                all_videos.add(clean_href)
                                logger.info(f"         ✅ Video {len(all_videos)}: {clean_href[:60]}...")
                                
                                if len(all_videos) >= max_videos:
                                    break
                    except:
                        continue
                
                if len(all_videos) >= max_videos:
                    break
                    
            except Exception as e:
                logger.warning(f"      Backup URL {idx} failed: {e}")
                continue
        
        result_list = list(all_videos)
        logger.info(f"   ✅ Method 3: {len(result_list)} videos from backup URLs")
        return result_list
    
    async def scrape_with_all_methods(self, profile_info: dict, max_videos: int = 15) -> List[str]:
        """
        Master method: Try all scraping methods with fallbacks
        """
        print_section(f"🎯 SCRAPING: {profile_info['name']}")
        logger.info(f"   Douyin ID: {profile_info['douyin_id']}")
        logger.info(f"   Description: {profile_info['description']}")
        logger.info(f"   Target: {max_videos} videos")
        
        all_videos = set()
        
        # METHOD 1: Direct profile scraping (primary)
        try:
            logger.info("\n🔄 Attempting Method 1...")
            videos = await self.scrape_profile_method_1(
                profile_info['profile_url'],
                profile_info['douyin_id'],
                max_videos
            )
            for v in videos:
                all_videos.add(v)
            logger.info(f"   Progress: {len(all_videos)}/{max_videos}")
        except Exception as e:
            logger.error(f"   Method 1 exception: {e}")
        
        # If we have enough, return early
        if len(all_videos) >= max_videos:
            logger.info(f"✅ SUCCESS: Got {len(all_videos)} videos from Method 1")
            return list(all_videos)[:max_videos]
        
        # METHOD 2: HTTP scraping (fast fallback)
        try:
            logger.info("\n🔄 Attempting Method 2...")
            videos = await self.scrape_profile_method_2(
                profile_info['profile_url'],
                max_videos - len(all_videos)
            )
            for v in videos:
                all_videos.add(v)
            logger.info(f"   Progress: {len(all_videos)}/{max_videos}")
        except Exception as e:
            logger.error(f"   Method 2 exception: {e}")
        
        if len(all_videos) >= max_videos:
            logger.info(f"✅ SUCCESS: Got {len(all_videos)} videos")
            return list(all_videos)[:max_videos]
        
        # METHOD 3: Backup URLs
        try:
            logger.info("\n🔄 Attempting Method 3...")
            backup_urls = profile_info.get('backup_urls', [])
            if backup_urls:
                videos = await self.scrape_backup_urls(
                    backup_urls,
                    max_videos - len(all_videos)
                )
                for v in videos:
                    all_videos.add(v)
                logger.info(f"   Progress: {len(all_videos)}/{max_videos}")
        except Exception as e:
            logger.error(f"   Method 3 exception: {e}")
        
        result_list = list(all_videos)[:max_videos]
        
        if len(result_list) > 0:
            logger.info(f"\n✅ TOTAL: {len(result_list)} videos scraped")
        else:
            logger.error(f"\n❌ FAILED: No videos found")
            metrics.scraping_failures += 1
        
        return result_list
    
    def close(self):
        """Close driver and cleanup"""
        try:
            if self.driver:
                logger.info("🔒 Closing WebDriver...")
                self.driver.quit()
                self.driver = None
                logger.info("✅ Driver closed")
        except Exception as e:
            logger.debug(f"Driver close error: {e}")

# ============================================================================
# DOWNLOAD WITH ENHANCED FALLBACKS
# ============================================================================

async def download_video_enhanced(video_url: str, video_id: str, temp_dir: str) -> Optional[str]:
    """
    Enhanced download with 4 fallback methods
    """
    print_section(f"📥 DOWNLOADING: {video_id}")
    logger.info(f"   URL: {video_url[:70]}...")
    
    metrics.download_attempts += 1
    
    # METHOD 1: Direct page scraping
    async with httpx.AsyncClient(timeout=90) as client:
        
        logger.info("🔹 Method 1: Direct Page Scraping")
        try:
            response = await client.get(
                video_url,
                headers={
                    'User-Agent': get_random_user_agent(),
                    'Referer': 'https://www.douyin.com/',
                    'Accept': '*/*',
                },
                follow_redirects=True
            )
            
            if response.status_code == 200:
                html = response.text
                logger.info(f"   Page loaded: {len(html)} bytes")
                
                # Multiple regex patterns for video URLs
                patterns = [
                    r'"playAddr":\[?"(https://[^"]+?\.mp4[^"]*)"',
                    r'playUrl":"(https://[^"]+\.mp4[^"]*)"',
                    r'"downloadAddr":"(https://[^"]+\.mp4[^"]*)"',
                    r'"play_addr_h264":\{"url_list":\["([^"]+)"',
                    r'"play_addr":\{"uri":"[^"]+","url_list":\["([^"]+)"',
                    r'"playApi":"(https://[^"]+\.mp4[^"]*)"',
                ]
                
                for idx, pattern in enumerate(patterns, 1):
                    logger.info(f"   Pattern {idx}/{len(patterns)}...")
                    matches = re.findall(pattern, html)
                    
                    if matches:
                        video_url_dl = matches[0].replace('\\u002F', '/').replace('\\/', '/')
                        logger.info(f"      ✅ Found URL: {video_url_dl[:60]}...")
                        
                        try:
                            logger.info("      Downloading...")
                            dl_response = await client.get(
                                video_url_dl,
                                headers={'User-Agent': get_random_user_agent(), 'Referer': 'https://www.douyin.com/'},
                                follow_redirects=True,
                                timeout=90
                            )
                            
                            if dl_response.status_code == 200:
                                size_mb = len(dl_response.content) / (1024 * 1024)
                                logger.info(f"      Size: {size_mb:.2f}MB")
                                
                                if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                                    video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
                                    with open(video_path, 'wb') as f:
                                        f.write(dl_response.content)
                                    
                                    logger.info(f"   ✅ Method 1 SUCCESS")
                                    metrics.download_success += 1
                                    return video_path
                        except Exception as e:
                            logger.warning(f"      Download failed: {e}")
        except Exception as e:
            logger.error(f"   Method 1 failed: {e}")
            metrics.log_error("download_method_1", str(e))
        
        # METHOD 2: ssstik.io
        logger.info("\n🔹 Method 2: ssstik.io")
        try:
            response = await client.post(
                'https://ssstik.io/abc',
                params={'url': 'dl'},
                headers={
                    'User-Agent': get_random_user_agent(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                data={'id': video_url, 'locale': 'en', 'tt': 'NE9MVmM4'}
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                link = soup.find('a', href=True)
                
                if link:
                    dl_link = link['href']
                    logger.info(f"   Found link: {dl_link[:60]}...")
                    
                    dl_response = await client.get(dl_link, follow_redirects=True)
                    
                    if dl_response.status_code == 200:
                        size_mb = len(dl_response.content) / (1024 * 1024)
                        
                        if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                            video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
                            with open(video_path, 'wb') as f:
                                f.write(dl_response.content)
                            
                            logger.info(f"   ✅ Method 2 SUCCESS: {size_mb:.1f}MB")
                            metrics.download_success += 1
                            return video_path
        except Exception as e:
            logger.error(f"   Method 2 failed: {e}")
            metrics.log_error("download_method_2", str(e))
        
        # METHOD 3: snaptik.app
        logger.info("\n🔹 Method 3: snaptik.app")
        try:
            response = await client.post(
                'https://snaptik.app/abc2.php',
                params={'url': 'dl'},
                data={'url': video_url, 'lang': 'en'}
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.find_all('a', href=True)
                
                for link in links:
                    if 'download' in link.get('href', '').lower():
                        dl_link = link['href']
                        logger.info(f"   Found link: {dl_link[:60]}...")
                        
                        dl_response = await client.get(dl_link, follow_redirects=True)
                        
                        if dl_response.status_code == 200:
                            size_mb = len(dl_response.content) / (1024 * 1024)
                            
                            if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                                video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
                                with open(video_path, 'wb') as f:
                                    f.write(dl_response.content)
                                
                                logger.info(f"   ✅ Method 3 SUCCESS: {size_mb:.1f}MB")
                                metrics.download_success += 1
                                return video_path
        except Exception as e:
            logger.error(f"   Method 3 failed: {e}")
            metrics.log_error("download_method_3", str(e))
        
        # METHOD 4: tikmate.app
        logger.info("\n🔹 Method 4: tikmate.app")
        try:
            response = await client.post(
                'https://tikmate.app/api/ajax/search',
                headers={'Content-Type': 'application/json'},
                json={'url': video_url}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'video' in data['data']:
                    dl_url = data['data']['video']
                    logger.info(f"   Found URL: {dl_url[:60]}...")
                    
                    dl_response = await client.get(dl_url, follow_redirects=True)
                    
                    if dl_response.status_code == 200:
                        size_mb = len(dl_response.content) / (1024 * 1024)
                        
                        if 0.1 < size_mb < MAX_VIDEO_SIZE_MB:
                            video_path = os.path.join(temp_dir, f"video_{video_id}.mp4")
                            with open(video_path, 'wb') as f:
                                f.write(dl_response.content)
                            
                            logger.info(f"   ✅ Method 4 SUCCESS: {size_mb:.1f}MB")
                            metrics.download_success += 1
                            return video_path
        except Exception as e:
            logger.error(f"   Method 4 failed: {e}")
            metrics.log_error("download_method_4", str(e))
    
    logger.error("❌ ALL DOWNLOAD METHODS FAILED")
    metrics.download_failures += 1
    return None

# ============================================================================
# [REST OF THE CODE REMAINS SAME AS PREVIOUS VERSION]
# Including: audio processing, script generation, video processing, upload
# ============================================================================

# ... [Include all the remaining functions from the previous version exactly as they were]

"""
china_enhanced_v3_part2.py - PART 2
===========================================================================
This file contains:
- Audio extraction and transcription
- Translation to Hindi
- Script generation
- Video processing (remove audio, resize, text overlays)
- Audio mixing
- YouTube upload
- API routes
===========================================================================
"""

# ============================================================================
# AUDIO PROCESSING
# ============================================================================

async def extract_audio(video_path: str, temp_dir: str) -> Optional[str]:
    """Extract audio from video"""
    log_step(2, 12, "EXTRACTING AUDIO")
    
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
        metrics.log_error("audio_extraction", "FFmpeg failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ Audio extraction error: {e}")
        metrics.log_error("audio_extraction", str(e))
        return None

async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using Whisper API with fallback"""
    log_step(3, 12, "TRANSCRIBING AUDIO")
    
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
                        logger.info(f"✅ Transcribed: {len(transcript)} chars")
                        logger.info(f"   Preview: {transcript[:100]}...")
                        return transcript
                    else:
                        logger.warning(f"   Whisper API failed: {response.status_code}")
        else:
            logger.warning("   OpenAI API key not found")
        
        # Fallback
        logger.info("⚠️ Using placeholder text")
        return "这是一个有趣的视频内容，充满了精彩瞬间"
        
    except Exception as e:
        logger.warning(f"⚠️ Transcription failed: {e}")
        metrics.log_error("transcription", str(e))
        return "精彩视频内容"

async def translate_to_hindi(chinese_text: str) -> str:
    """Translate Chinese to Hindi using Mistral AI"""
    log_step(4, 12, "TRANSLATING TO HINDI")
    
    try:
        if not MISTRAL_API_KEY:
            logger.warning("   Mistral API key not found")
            return chinese_text
        
        logger.info("   Using Mistral AI...")
        
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
                        "content": f"Translate to natural Hindi. ONLY output the Hindi translation:\n\n{chinese_text}"
                    }],
                    "temperature": 0.3,
                    "max_tokens": 300
                }
            )
            
            if response.status_code == 200:
                hindi_text = response.json()["choices"][0]["message"]["content"].strip()
                logger.info(f"✅ Translated")
                logger.info(f"   Output: {hindi_text[:100]}...")
                return hindi_text
            else:
                logger.warning(f"   Translation failed: {response.status_code}")
        
        return chinese_text
        
    except Exception as e:
        logger.warning(f"⚠️ Translation failed: {e}")
        metrics.log_error("translation", str(e))
        return chinese_text

# ============================================================================
# SCRIPT GENERATION
# ============================================================================

async def generate_creative_script(hindi_text: str, niche: str, original_title: str) -> dict:
    """Generate viral Hindi script"""
    log_step(5, 12, "GENERATING SCRIPT")
    
    niche_config = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["funny"])
    
    if not MISTRAL_API_KEY:
        logger.warning("   Using fallback template")
        return generate_fallback_script(hindi_text, niche)
    
    prompt = f"""Create viral Hindi YouTube Shorts script (30s).

NICHE: {niche_config['name']}
CONTENT: {hindi_text}

4 segments:
1. HOOK (8s) - Grab attention
2. BUILD (12s) - Story
3. CLIMAX (7s) - Peak
4. OUTRO (3s) - CTA

JSON only:
{{
  "segments": [
    {{"narration": "Hindi hook", "text_overlay": "{niche_config['emoji'].split()[0]}", "duration": 8}},
    {{"narration": "Hindi build", "text_overlay": "🔥", "duration": 12}},
    {{"narration": "Hindi climax", "text_overlay": "✨", "duration": 7}},
    {{"narration": "Hindi CTA", "text_overlay": "🔥", "duration": 3}}
  ],
  "title": "Hindi title",
  "hashtags": ["{niche}", "viral", "shorts"]
}}"""
    
    try:
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
                        {"role": "system", "content": "Output ONLY JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.9,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                
                script = json.loads(content)
                logger.info(f"✅ Script: {script.get('title', 'N/A')}")
                return script
    
    except Exception as e:
        logger.warning(f"   Script gen failed: {e}")
        metrics.log_error("script_generation", str(e))
    
    return generate_fallback_script(hindi_text, niche)

def generate_fallback_script(text: str, niche: str) -> dict:
    """Fallback script templates"""
    logger.info(f"   Using {niche} template")
    
    templates = {
        "funny": {
            "segments": [
                {"narration": f"अरे वाह! {text[:40]}", "text_overlay": "😂", "duration": 8},
                {"narration": "यह तो बहुत मजेदार है!", "text_overlay": "🤣", "duration": 12},
                {"narration": "एंडिंग देखो!", "text_overlay": "💀", "duration": 7},
                {"narration": "लाइक करो!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "हंसी नहीं रुकेगी 😂💀",
            "hashtags": ["funny", "comedy", "viral"]
        },
        "animals": {
            "segments": [
                {"narration": f"देखो कितना प्यारा! {text[:40]}", "text_overlay": "🐶", "duration": 8},
                {"narration": "यह तो दिल जीत लिया!", "text_overlay": "🐱", "duration": 12},
                {"narration": "सबसे क्यूट!", "text_overlay": "❤️", "duration": 7},
                {"narration": "शेयर करो!", "text_overlay": "🔥", "duration": 3}
            ],
            "title": "प्यारा जानवर 🐶❤️",
            "hashtags": ["animals", "cute", "viral"]
        }
    }
    
    return templates.get(niche, templates["funny"])

# ============================================================================
# BACKGROUND MUSIC
# ============================================================================

async def download_background_music(temp_dir: str) -> Optional[str]:
    """Download background music"""
    logger.info("🎵 Downloading background music...")
    
    music_path = os.path.join(temp_dir, "bg_music.mp3")
    
    for idx, url in enumerate(BACKGROUND_MUSIC_URLS, 1):
        try:
            logger.info(f"   Source {idx}/{len(BACKGROUND_MUSIC_URLS)}...")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, follow_redirects=True)
                
                if resp.status_code == 200:
                    with open(music_path, 'wb') as f:
                        f.write(resp.content)
                    
                    size_mb = get_size_mb(music_path)
                    if size_mb > 0.05:
                        logger.info(f"   ✅ Music: {size_mb:.2f}MB")
                        return music_path
                    else:
                        force_cleanup(music_path)
        except Exception as e:
            logger.debug(f"   Source {idx} failed: {e}")
            continue
    
    logger.warning("   ⚠️ No music")
    return None

# ============================================================================
# VOICE GENERATION
# ============================================================================

async def generate_hindi_voice(text: str, duration: float, temp_dir: str) -> Optional[str]:
    """Generate Hindi voiceover using ElevenLabs"""
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            logger.warning("   ⚠️ ElevenLabs not configured")
            return None
        
        text_clean = text.strip()[:500]
        temp_audio = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex[:6]}.mp3")
        
        logger.info(f"   🎤 {text_clean[:40]}...")
        
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
                
                if get_size_mb(temp_audio) > 0.01:
                    output = temp_audio.replace(".mp3", "_adj.mp3")
                    
                    cmd = [
                        "ffmpeg", "-i", temp_audio,
                        "-filter:a", "atempo=1.15,loudnorm=I=-16",
                        "-t", str(duration + 0.5),
                        "-b:a", "128k",
                        "-y", output
                    ]
                    
                    if run_ffmpeg(cmd, 20):
                        force_cleanup(temp_audio)
                        logger.info(f"      ✅ {get_size_mb(output):.2f}MB")
                        return output
                
                force_cleanup(temp_audio)
            else:
                logger.warning(f"   ElevenLabs failed: {response.status_code}")
                
    except Exception as e:
        logger.error(f"   Voice error: {e}")
        metrics.log_error("voice_generation", str(e))
    
    return None

# ============================================================================
# VIDEO PROCESSING
# ============================================================================

async def remove_original_audio(video_path: str, temp_dir: str) -> Optional[str]:
    """Remove original audio"""
    log_step(7, 12, "REMOVING ORIGINAL AUDIO")
    
    try:
        output = os.path.join(temp_dir, "video_no_audio.mp4")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-an", "-c:v", "copy",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 30):
            logger.info(f"✅ Removed: {get_size_mb(output):.1f}MB")
            return output
        
        logger.error("❌ Failed")
        metrics.log_error("audio_removal", "FFmpeg failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        metrics.log_error("audio_removal", str(e))
        return None

async def process_video_for_shorts(video_path: str, target_duration: int, temp_dir: str) -> Optional[str]:
    """Process for YouTube Shorts (1080x1920)"""
    log_step(8, 12, "PROCESSING FOR SHORTS")
    
    try:
        output = os.path.join(temp_dir, "processed.mp4")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-t", str(target_duration),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            "-c:v", "libx264", "-crf", "23",
            "-preset", "medium",
            "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 90):
            logger.info(f"✅ Processed: {get_size_mb(output):.1f}MB")
            metrics.processing_success += 1
            return output
        
        logger.error("❌ Failed")
        metrics.processing_failures += 1
        return None
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        metrics.log_error("video_processing", str(e))
        return None

async def add_text_overlays(video: str, segments: list, temp_dir: str) -> Optional[str]:
    """Add text overlays"""
    log_step(9, 12, "ADDING TEXT OVERLAYS")
    
    try:
        output = os.path.join(temp_dir, "with_text.mp4")
        
        filters = []
        current_time = 0
        
        for idx, seg in enumerate(segments, 1):
            text = seg.get("text_overlay", "").replace("'", "").replace('"', '')
            if text:
                logger.info(f"   {idx}. {text} ({seg['duration']}s)")
                filters.append(
                    f"drawtext=text='{text}':"
                    f"fontsize=60:fontcolor=white:"
                    f"x=(w-text_w)/2:y=h-150:"
                    f"borderw=5:bordercolor=black:"
                    f"enable='between(t,{current_time},{current_time + seg['duration']})'"
                )
            current_time += seg["duration"]
        
        if not filters:
            logger.info("   Skipping (no text)")
            return video
        
        vf = ",".join(filters)
        
        cmd = [
            "ffmpeg", "-i", video,
            "-vf", vf,
            "-c:v", "libx264", "-crf", "26",
            "-preset", "fast",
            "-y", output
        ]
        
        if run_ffmpeg(cmd, 60):
            force_cleanup(video)
            logger.info(f"✅ Added: {get_size_mb(output):.1f}MB")
            return output
        
        logger.warning("⚠️ Failed - using original")
        return video
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        metrics.log_error("text_overlays", str(e))
        return video

async def mix_audio_with_music(video: str, voices: List[str], music: Optional[str], temp_dir: str) -> Optional[str]:
    """Mix voiceovers with music"""
    log_step(11, 12, "MIXING AUDIO")
    
    try:
        vlist = os.path.join(temp_dir, "voices.txt")
        with open(vlist, 'w') as f:
            for v in voices:
                f.write(f"file '{v}'\n")
        
        voice_combined = os.path.join(temp_dir, "voice_all.mp3")
        
        logger.info("   Concatenating voices...")
        cmd = [
            "ffmpeg",
            "-f", "concat", "-safe", "0",
            "-i", vlist,
            "-c", "copy",
            "-y", voice_combined
        ]
        
        if not run_ffmpeg(cmd, 30):
            logger.error("❌ Concat failed")
            return None
        
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            logger.info("   Mixing with music...")
            cmd = [
                "ffmpeg",
                "-i", video, "-i", voice_combined, "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[voice];"
                "[2:a]volume=0.25,afade=t=in:d=1,afade=t=out:st=28:d=2[music];"
                "[voice][music]amix=inputs=2:duration=first[audio]",
                "-map", "0:v", "-map", "[audio]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", "-y", final
            ]
        else:
            logger.info("   Voice only...")
            cmd = [
                "ffmpeg",
                "-i", video, "-i", voice_combined,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", "-y", final
            ]
        
        if run_ffmpeg(cmd, 60):
            logger.info(f"✅ Final: {get_size_mb(final):.1f}MB")
            return final
        
        logger.error("❌ Mix failed")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        metrics.log_error("audio_mixing", str(e))
        return None

# ============================================================================
# YOUTUBE UPLOAD
# ============================================================================

async def upload_to_youtube(video_path: str, title: str, description: str, 
                           hashtags: List[str], user_id: str, database_manager) -> dict:
    """Upload to YouTube"""
    log_step(12, 12, "UPLOADING TO YOUTUBE")
    
    try:
        metrics.upload_attempts += 1
        
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db:
            logger.error("   DB not available")
            return {"success": False, "error": "YouTube DB unavailable"}
        
        if not yt_db.youtube.client:
            logger.info("   Connecting to DB...")
            await yt_db.connect()
        
        logger.info("   Fetching credentials...")
        credentials_raw = await yt_db.youtube.youtube_credentials_collection.find_one({
            "user_id": user_id
        })
        
        if not credentials_raw:
            logger.error("   Credentials not found")
            return {"success": False, "error": "Credentials not found"}
        
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
        
        logger.info("   Uploading...")
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
            
            logger.info(f"✅ SUCCESS")
            logger.info(f"   ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            metrics.upload_success += 1
            
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
        
        logger.error(f"   Failed: {upload_result.get('error')}")
        metrics.upload_failures += 1
        return {"success": False, "error": upload_result.get("error", "Upload failed")}
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error(traceback.format_exc())
        metrics.upload_failures += 1
        metrics.log_error("youtube_upload", str(e))
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
    """Process single video end-to-end"""
    
    temp_dir = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"video_{video_index}_")
        
        print_section(f"🎬 VIDEO {video_index}/{total_videos}")
        logger.info(f"   URL: {video_url[:70]}...")
        logger.info(f"   Temp: {temp_dir}")
        
        metrics.processing_attempts += 1
        
        # STEP 1: Download
        log_step(1, 12, "DOWNLOADING VIDEO")
        video_id = f"{niche}_{video_index}_{uuid.uuid4().hex[:6]}"
        video_path = await download_video_enhanced(video_url, video_id, temp_dir)
        
        if not video_path:
            return {
                "success": False,
                "error": "Download failed",
                "video_url": video_url,
                "index": video_index
            }
        
        # STEP 2-5: Audio + Translation + Script
        audio_path = await extract_audio(video_path, temp_dir)
        if not audio_path:
            return {"success": False, "error": "Audio extraction failed", "index": video_index}
        
        transcript = await transcribe_audio(audio_path)
        hindi_text = await translate_to_hindi(transcript)
        script = await generate_creative_script(hindi_text, niche, f"Video {video_index}")
        
        # STEP 6: Music
        log_step(6, 12, "DOWNLOADING MUSIC")
        music = await download_background_music(temp_dir)
        
        # STEP 7-9: Video processing
        video_no_audio = await remove_original_audio(video_path, temp_dir)
        if not video_no_audio:
            return {"success": False, "error": "Audio removal failed", "index": video_index}
        
        force_cleanup(video_path, audio_path)
        
        processed_video = await process_video_for_shorts(video_no_audio, TARGET_DURATION, temp_dir)
        if not processed_video:
            return {"success": False, "error": "Processing failed", "index": video_index}
        
        force_cleanup(video_no_audio)
        
        if show_captions:
            processed_video = await add_text_overlays(processed_video, script["segments"], temp_dir)
        
        # STEP 10: Generate voices
        log_step(10, 12, "GENERATING VOICEOVERS")
        voices = []
        
        for idx, seg in enumerate(script["segments"], 1):
            logger.info(f"   Voice {idx}/{len(script['segments'])}")
            voice = await generate_hindi_voice(seg["narration"], seg["duration"], temp_dir)
            if voice:
                voices.append(voice)
        
        logger.info(f"   Total: {len(voices)}/{len(script['segments'])}")
        
        if len(voices) < 2:
            logger.warning(f"   ⚠️ Only {len(voices)} voices")
        
        # STEP 11: Mix audio
        final_video = await mix_audio_with_music(processed_video, voices, music, temp_dir)
        if not final_video:
            return {"success": False, "error": "Mixing failed", "index": video_index}
        
        # STEP 12: Upload
        upload_result = await upload_to_youtube(
            final_video,
            script["title"],
            f"Video {video_index} - {niche}",
            script["hashtags"],
            user_id,
            database_manager
        )
        
        # Cleanup
        if temp_dir:
            logger.info(f"🗑️ Cleanup...")
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
        logger.error(f"❌ VIDEO {video_index} FAILED: {e}")
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
    """Main pipeline"""
    
    try:
        print_section("🚀 DOUYIN AUTOMATION START", "=")
        logger.info(f"   Niche: {niche}")
        logger.info(f"   Videos: {num_videos}")
        logger.info(f"   User: {user_id}")
        logger.info(f"   Time: {datetime.now()}")
        
        metrics.reset()
        
        # Get niche config
        niche_config = NICHE_KEYWORDS.get(niche)
        if not niche_config:
            return {
                "success": False,
                "error": f"Invalid niche: {niche}"
            }
        
        # Step 1: Scrape
        print_section("📱 STEP 1: SCRAPING")
        
        scraper = EnhancedDouyinScraper()
        all_video_urls = []
        
        if custom_profile_urls:
            logger.info(f"   Using {len(custom_profile_urls)} custom URLs")
            # Simple scraping for custom URLs
            for url in custom_profile_urls:
                videos = await scraper.scrape_profile_method_1(url, "custom", 15)
                all_video_urls.extend(videos)
        else:
            profiles = niche_config.get('profiles', [])
            logger.info(f"   Using {len(profiles)} profiles")
            
            for profile in profiles:
                if len(all_video_urls) >= num_videos * 3:
                    break
                
                videos = await scraper.scrape_with_all_methods(profile, 20)
                all_video_urls.extend(videos)
                
                logger.info(f"   Progress: {len(all_video_urls)} videos")
        
        scraper.close()
        
        if not all_video_urls:
            return {
                "success": False,
                "error": "No videos found"
            }
        
        logger.info(f"\n✅ SCRAPED: {len(all_video_urls)} videos")
        
        # Shuffle and select
        random.shuffle(all_video_urls)
        videos_to_process = all_video_urls[:num_videos]
        
        # Step 2: Process videos
        print_section("🎬 STEP 2: PROCESSING")
        
        results = []
        success_count = 0
        
        for idx, video_url in enumerate(videos_to_process, 1):
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
            
            logger.info(f"   Success rate: {success_count}/{idx}")
            
            # Delay
            if idx < num_videos:
                logger.info("   ⏸️ 5 seconds...")
                await asyncio.sleep(5)
        
        # Summary
        print_section("🎉 COMPLETE", "=")
        logger.info(f"   Requested: {num_videos}")
        logger.info(f"   Successful: {success_count}")
        logger.info(f"   Failed: {num_videos - success_count}")
        
        summary = metrics.get_summary()
        logger.info(f"\n📊 METRICS:")
        logger.info(f"   Scraping: {summary['scraping']['rate']}")
        logger.info(f"   Download: {summary['download']['rate']}")
        logger.info(f"   Processing: {summary['processing']['rate']}")
        logger.info(f"   Upload: {summary['upload']['rate']}")
        
        return {
            "success": True,
            "total_requested": num_videos,
            "successful": success_count,
            "failed": num_videos - success_count,
            "success_rate": f"{(success_count/num_videos*100):.1f}%",
            "results": results,
            "niche": niche,
            "metrics": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ PIPELINE FAILED: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "error": str(e),
            "metrics": metrics.get_summary()
        }

# ============================================================================
# API ROUTES
# ============================================================================

router = APIRouter()

@router.get("/api/china/niches")
async def get_niches():
    """Get available niches"""
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
        }
    }

@router.post("/api/china/generate")
async def generate_endpoint(request: Request):
    """Generate videos"""
    try:
        data = await request.json()
        
        niche = data.get("niche", "funny")
        user_id = data.get("user_id")
        num_videos = data.get("num_videos", 1)
        show_captions = data.get("show_captions", True)
        custom_profile_urls = data.get("profile_urls", [])
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "user_id required"}
            )
        
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"Invalid niche: {list(NICHE_KEYWORDS.keys())}"}
            )
        
        if num_videos < 1 or num_videos > 10:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "num_videos: 1-10"}
            )
        
        from Supermain import database_manager
        
        logger.info(f"\n{'='*80}")
        logger.info(f"API REQUEST".center(80))
        logger.info(f"{'='*80}")
        logger.info(f"   User: {user_id}")
        logger.info(f"   Niche: {niche}")
        logger.info(f"   Videos: {num_videos}")
        
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
                timeout=1800
            )
            
            return JSONResponse(content=result)
            
        except asyncio.TimeoutError:
            logger.error("❌ TIMEOUT")
            return JSONResponse(
                status_code=408,
                content={"success": False, "error": "Timeout"}
            )
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@router.get("/api/china/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "success": True,
        "message": "Douyin Automation v3 - Enhanced",
        "version": "3.0",
        "features": [
            "Profile ID scraping",
            "4 download methods",
            "Metrics tracking",
            "Extensive logging",
            "Hindi voiceover",
            "YouTube Shorts"
        ],
        "niches": list(NICHE_KEYWORDS.keys()),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/api/china/metrics")
async def get_metrics():
    """Get current metrics"""
    return {
        "success": True,
        "metrics": metrics.get_summary(),
        "timestamp": datetime.now().isoformat()
    }

__all__ = ['router']