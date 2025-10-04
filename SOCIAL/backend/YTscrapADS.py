"""
YTscrapADS.py - Universal Product Scraper (Memory Optimized for Render 512MB)
Supports: Flipkart, Amazon, Myntra, Ajio, Meesho, Snapdeal
"""

import asyncio
import logging
import re
import os
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Set browser path BEFORE importing playwright
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/render/project/.browsers'

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ProductScraper:
    """Universal product scraper with memory optimization"""
    
    def __init__(self):
        self.browser_args = [
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--single-process',
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-background-networking',
            '--disable-sync',
            '--metrics-recording-only',
            '--disable-default-apps',
            '--mute-audio',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
            '--disable-component-update'
        ]
    
    async def scrape_product(self, url: str) -> Dict:
        """
        Universal product scraper
        
        Returns:
            {
                "success": True/False,
                "product_name": str,
                "brand": str,
                "price": float,
                "original_price": float,
                "discount": str,
                "images": [url1, url2, ...],
                "colors": [],
                "sizes": [],
                "description": str,
                "product_url": str,
                "platform": str
            }
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            if 'flipkart' in domain:
                return await self._scrape_flipkart(url)
            elif 'amazon' in domain:
                return await self._scrape_amazon(url)
            elif 'myntra' in domain:
                return await self._scrape_myntra(url)
            elif 'ajio' in domain:
                return await self._scrape_ajio(url)
            elif 'meesho' in domain:
                return await self._scrape_meesho(url)
            elif 'snapdeal' in domain:
                return await self._scrape_snapdeal(url)
            else:
                return await self._scrape_generic(url)
                
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_browser(self):
        """Get memory-optimized browser instance"""
        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=True,
            args=self.browser_args
        )
        return p, browser
    
    async def _scrape_flipkart(self, url: str) -> Dict:
        """Scrape Flipkart product page"""
        p, browser = None, None
        try:
            p, browser = await self._get_browser()
            page = await browser.new_page()
            
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(1.5)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Product name
            product_name = soup.find('span', class_='VU-ZEz')
            product_name = product_name.text.strip() if product_name else "Product"
            
            # Brand
            brand = soup.find('a', class_='VU-ZEz')
            brand = brand.text.strip() if brand else "Brand"
            
            # Price
            price_elem = soup.find('div', class_='Nx9bqj CxhGGd')
            price = 0
            if price_elem:
                price = float(price_elem.text.strip().replace('₹', '').replace(',', ''))
            
            # Original price
            original_price_elem = soup.find('div', class_='yRaY8j A6+E6v')
            original_price = price
            if original_price_elem:
                original_price = float(original_price_elem.text.strip().replace('₹', '').replace(',', ''))
            
            # Discount
            discount = ""
            if original_price > price:
                discount = f"{int(((original_price - price) / original_price) * 100)}% OFF"
            
            # Images
            images = []
            for img in soup.find_all('img', class_='DByuf4')[:6]:
                img_url = img.get('src') or img.get('data-src')
                if img_url and img_url.startswith('http'):
                    images.append(img_url)
            
            # Colors & Sizes
            colors = [c.get('title', '') for c in soup.find_all('li', class_='_0H_LOL') if c.get('title')]
            sizes = [s.text.strip() for s in soup.find_all('a', class_='_0H_LOL') if len(s.text.strip()) <= 4]
            
            # Description
            desc_elem = soup.find('div', class_='_4gvKMe')
            description = desc_elem.text.strip() if desc_elem else ""
            
            await browser.close()
            await p.stop()
            
            return {
                "success": True,
                "product_name": product_name,
                "brand": brand,
                "price": price,
                "original_price": original_price,
                "discount": discount,
                "images": images,
                "colors": colors,
                "sizes": sizes,
                "description": description,
                "product_url": url,
                "platform": "flipkart"
            }
                
        except Exception as e:
            logger.error(f"Flipkart scraping failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if browser:
                await browser.close()
            if p:
                await p.stop()
    
    async def _scrape_amazon(self, url: str) -> Dict:
        """Scrape Amazon India product page"""
        p, browser = None, None
        try:
            p, browser = await self._get_browser()
            page = await browser.new_page()
            
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Product name
            product_name = soup.find('span', id='productTitle')
            product_name = product_name.text.strip() if product_name else "Product"
            
            # Brand
            brand = soup.find('a', id='bylineInfo')
            brand = brand.text.replace('Visit the', '').replace('Store', '').strip() if brand else "Brand"
            
            # Price
            price_elem = soup.find('span', class_='a-price-whole')
            price = 0
            if price_elem:
                price = float(price_elem.text.replace(',', '').replace('.', ''))
            
            # Images
            images = []
            img_div = soup.find('div', id='altImages')
            if img_div:
                for img in img_div.find_all('img')[:6]:
                    img_url = img.get('src', '').replace('_AC_US40_', '_AC_SY500_')
                    if img_url and 'http' in img_url:
                        images.append(img_url)
            
            # Description
            desc_elem = soup.find('div', id='feature-bullets')
            description = desc_elem.text.strip() if desc_elem else ""
            
            await browser.close()
            await p.stop()
            
            return {
                "success": True,
                "product_name": product_name,
                "brand": brand,
                "price": price,
                "original_price": price,
                "discount": "",
                "images": images,
                "colors": [],
                "sizes": [],
                "description": description[:500],
                "product_url": url,
                "platform": "amazon"
            }
                
        except Exception as e:
            logger.error(f"Amazon scraping failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if browser:
                await browser.close()
            if p:
                await p.stop()
    
    async def _scrape_myntra(self, url: str) -> Dict:
        """Scrape Myntra product page"""
        p, browser = None, None
        try:
            p, browser = await self._get_browser()
            page = await browser.new_page()
            
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Product name
            product_name = soup.find('h1', class_='pdp-title')
            product_name = product_name.text.strip() if product_name else "Product"
            
            # Brand
            brand = soup.find('h1', class_='pdp-name')
            brand = brand.text.strip() if brand else "Brand"
            
            # Price
            price_elem = soup.find('span', class_='pdp-price')
            price = 0
            if price_elem:
                price = float(price_elem.text.replace('₹', '').replace(',', ''))
            
            # Images
            images = []
            for img in soup.find_all('div', class_='image-grid-image')[:6]:
                style = img.get('style', '')
                match = re.search(r'url\((.*?)\)', style)
                if match:
                    images.append(match.group(1))
            
            await browser.close()
            await p.stop()
            
            return {
                "success": True,
                "product_name": product_name,
                "brand": brand,
                "price": price,
                "original_price": price,
                "discount": "",
                "images": images,
                "colors": [],
                "sizes": [],
                "description": "",
                "product_url": url,
                "platform": "myntra"
            }
                
        except Exception as e:
            logger.error(f"Myntra scraping failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if browser:
                await browser.close()
            if p:
                await p.stop()
    
    async def _scrape_ajio(self, url: str) -> Dict:
        """Scrape Ajio product page"""
        # Similar pattern to Myntra
        return {"success": False, "error": "Ajio scraping in development"}
    
    async def _scrape_meesho(self, url: str) -> Dict:
        """Scrape Meesho product page"""
        return {"success": False, "error": "Meesho scraping in development"}
    
    async def _scrape_snapdeal(self, url: str) -> Dict:
        """Scrape Snapdeal product page"""
        return {"success": False, "error": "Snapdeal scraping in development"}
    
    async def _scrape_generic(self, url: str) -> Dict:
        """Generic scraper for unknown sites"""
        p, browser = None, None
        try:
            p, browser = await self._get_browser()
            page = await browser.new_page()
            
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            
            # Get all images
            images = await page.evaluate("""
                () => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    return imgs
                        .map(img => img.src)
                        .filter(src => src && src.startsWith('http'))
                        .slice(0, 6);
                }
            """)
            
            # Get page title as product name
            product_name = await page.title()
            
            await browser.close()
            await p.stop()
            
            return {
                "success": True,
                "product_name": product_name[:100],
                "brand": "Unknown",
                "price": 0,
                "original_price": 0,
                "discount": "",
                "images": images,
                "colors": [],
                "sizes": [],
                "description": "",
                "product_url": url,
                "platform": "generic"
            }
                
        except Exception as e:
            logger.error(f"Generic scraping failed: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if browser:
                await browser.close()
            if p:
                await p.stop()


# Global instance
product_scraper = ProductScraper()

def get_product_scraper():
    return product_scraper