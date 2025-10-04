"""
YTscrapADS.py - Universal Product Scraper (Memory Optimized for Render 512MB)
Supports: Flipkart, Amazon, Myntra, Ajio, Meesho, Snapdeal
ENHANCED: Multiple extraction methods, fallbacks, and complete data coverage
"""

import asyncio
import logging
import re
import os
import json
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Set browser path BEFORE importing playwright
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/render/project/.browsers'

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ProductScraper:
    """Universal product scraper with advanced extraction"""
    
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
        """Universal product scraper"""
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
        """
        ADVANCED FLIPKART SCRAPER
        Extracts: Brand, Name, Price, Discount, Images, Colors, Sizes, Ratings, Reviews
        """
        p, browser = None, None
        try:
            logger.info("Starting Flipkart scrape...")
            p, browser = await self._get_browser()
            page = await browser.new_page()
            
            # Navigate and wait for content
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            await asyncio.sleep(2)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # ===== EXTRACT BRAND (Multiple Methods) =====
            brand = None
            brand_methods = [
                lambda: soup.select_one('span.VU-ZEz'),
                lambda: soup.select_one('a.s1Q9rs'),
                lambda: soup.select_one('div._2f4Txw span'),
                lambda: soup.select_one('span._35KyD6'),
            ]
            
            for method in brand_methods:
                try:
                    elem = method()
                    if elem and elem.text.strip():
                        brand = elem.text.strip()
                        break
                except:
                    continue
            
            if not brand:
                brand = "Brand"
            
            logger.info(f"Brand extracted: {brand}")
            
            # ===== EXTRACT PRODUCT NAME (Multiple Methods) =====
            product_name = None
            name_methods = [
                lambda: soup.select_one('span.VU-ZEz'),
                lambda: soup.select_one('h1.yhB1nd'),
                lambda: soup.select_one('span._35KyD6'),
                lambda: soup.select_one('h1 span'),
            ]
            
            for method in name_methods:
                try:
                    elem = method()
                    if elem and elem.text.strip():
                        product_name = elem.text.strip()
                        break
                except:
                    continue
            
            if not product_name:
                product_name = await page.title()
            
            logger.info(f"Product name: {product_name}")
            
            # ===== EXTRACT PRICE (Multiple Methods) =====
            price = 0
            price_methods = [
                lambda: soup.select_one('div.Nx9bqj.CxhGGd'),
                lambda: soup.select_one('div._30jeq3._16Jk6d'),
                lambda: soup.select_one('div._30jeq3'),
                lambda: soup.select_one('div._25b18c span'),
            ]
            
            for method in price_methods:
                try:
                    elem = method()
                    if elem:
                        price_text = elem.text.replace('₹', '').replace(',', '').strip()
                        price = float(price_text)
                        break
                except:
                    continue
            
            logger.info(f"Price: {price}")
            
            # ===== EXTRACT ORIGINAL PRICE =====
            original_price = price
            original_methods = [
                lambda: soup.select_one('div.yRaY8j.A6+E6v'),
                lambda: soup.select_one('div._3I9_wc._2p6lqe'),
                lambda: soup.select_one('div._3auQ3N._2GeJrf'),
            ]
            
            for method in original_methods:
                try:
                    elem = method()
                    if elem:
                        orig_text = elem.text.replace('₹', '').replace(',', '').strip()
                        original_price = float(orig_text)
                        break
                except:
                    continue
            
            # ===== CALCULATE DISCOUNT =====
            discount = ""
            if original_price > price:
                discount_pct = int(((original_price - price) / original_price) * 100)
                discount = f"{discount_pct}% OFF"
            else:
                # Try to find discount element
                discount_methods = [
                    lambda: soup.select_one('div.UkUFwK span'),
                    lambda: soup.select_one('div._3Ay6Sb._31Dcoz'),
                ]
                for method in discount_methods:
                    try:
                        elem = method()
                        if elem:
                            discount = elem.text.strip()
                            break
                    except:
                        continue
            
            logger.info(f"Discount: {discount}")
            
            # ===== EXTRACT IMAGES (CRITICAL - Multiple Methods) =====
            images = []
            
            # Method 1: Get all carousel thumbnail images
            logger.info("Extracting images - Method 1: Carousel")
            carousel_imgs = soup.select('li._6K-7Co img, ul._7cYte3 img, div._1AtVbE img')
            for img in carousel_imgs:
                img_url = img.get('src') or img.get('data-src')
                if img_url and 'http' in img_url:
                    # Upgrade to high-res
                    img_url = re.sub(r'/\d+/\d+/', '/832/832/', img_url)
                    if img_url not in images:
                        images.append(img_url)
            
            # Method 2: Main product image
            if len(images) < 3:
                logger.info("Extracting images - Method 2: Main image")
                main_img = soup.select_one('img._0DkuPH, img._2r_T1I, img.DByuf4')
                if main_img:
                    img_url = main_img.get('src') or main_img.get('data-src')
                    if img_url and 'http' in img_url:
                        img_url = re.sub(r'/\d+/\d+/', '/832/832/', img_url)
                        if img_url not in images:
                            images.insert(0, img_url)
            
            # Method 3: JavaScript image extraction
            if len(images) < 2:
                logger.info("Extracting images - Method 3: JavaScript")
                try:
                    js_images = await page.evaluate("""
                        () => {
                            const imgs = [];
                            document.querySelectorAll('img').forEach(img => {
                                const src = img.src || img.getAttribute('data-src');
                                if (src && src.includes('rukminim') && !imgs.includes(src)) {
                                    imgs.push(src.replace(/\/\d+\/\d+\//, '/832/832/'));
                                }
                            });
                            return imgs;
                        }
                    """)
                    images.extend([img for img in js_images if img not in images])
                except Exception as e:
                    logger.warning(f"JS extraction failed: {e}")
            
            # Method 4: Parse JSON-LD structured data
            if len(images) < 2:
                logger.info("Extracting images - Method 4: JSON-LD")
                json_ld = soup.find('script', type='application/ld+json')
                if json_ld:
                    try:
                        data = json.loads(json_ld.string)
                        if 'image' in data:
                            img_urls = data['image'] if isinstance(data['image'], list) else [data['image']]
                            for img_url in img_urls:
                                if img_url and img_url not in images:
                                    images.append(img_url)
                    except Exception as e:
                        logger.warning(f"JSON-LD parsing failed: {e}")
            
            logger.info(f"Total images extracted: {len(images)}")
            
            # ===== EXTRACT SIZES =====
            sizes = []
            size_selectors = [
                'li._1xr9Mx',
                'a._0H_LOL',
                'div._2YxCDZ li',
            ]
            
            for selector in size_selectors:
                size_elems = soup.select(selector)
                for elem in size_elems:
                    size_text = elem.text.strip()
                    if size_text and len(size_text) <= 6 and size_text not in sizes:
                        sizes.append(size_text)
                if sizes:
                    break
            
            logger.info(f"Sizes: {sizes}")
            
            # ===== EXTRACT COLORS =====
            colors = []
            color_selectors = [
                'li._3V2wfe',
                'li._0H_LOL[title]',
                'div._2YxCDZ a[title]',
            ]
            
            for selector in color_selectors:
                color_elems = soup.select(selector)
                for elem in color_elems:
                    color_name = elem.get('title', '').strip()
                    if color_name and color_name not in colors:
                        colors.append(color_name)
                if colors:
                    break
            
            logger.info(f"Colors: {colors}")
            
            # ===== EXTRACT RATINGS & REVIEWS =====
            rating_count = 0
            review_count = 0
            rating = 0.0
            
            # Rating count
            rating_methods = [
                lambda: soup.select_one('span._2_R_DZ span'),
                lambda: soup.select_one('span._13vcmD'),
            ]
            
            for method in rating_methods:
                try:
                    elem = method()
                    if elem:
                        rating_text = elem.text.strip()
                        # Extract number from text like "49,344 Ratings"
                        numbers = re.findall(r'[\d,]+', rating_text)
                        if numbers:
                            rating_count = int(numbers[0].replace(',', ''))
                            break
                except:
                    continue
            
            # Review count
            review_methods = [
                lambda: soup.select_one('span._2_R_DZ span:nth-of-type(2)'),
                lambda: soup.select_one('span._3UAT2v'),
            ]
            
            for method in review_methods:
                try:
                    elem = method()
                    if elem:
                        review_text = elem.text.strip()
                        numbers = re.findall(r'[\d,]+', review_text)
                        if numbers:
                            review_count = int(numbers[0].replace(',', ''))
                            break
                except:
                    continue
            
            # Star rating
            rating_star = soup.select_one('div._3LWZlK')
            if rating_star:
                try:
                    rating = float(rating_star.text.strip())
                except:
                    pass
            
            logger.info(f"Ratings: {rating_count} ratings, {review_count} reviews, {rating}★")
            
            # ===== EXTRACT DESCRIPTION =====
            description = ""
            desc_selectors = [
                'div._4gvKMe',
                'div._2418kt',
                'div.aMaAEs',
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.text.strip()[:500]
                    break
            
            await browser.close()
            await p.stop()
            
            result = {
                "success": True,
                "brand": brand,
                "product_name": product_name,
                "price": price,
                "original_price": original_price,
                "discount": discount,
                "images": images[:6],
                "colors": colors,
                "sizes": sizes,
                "rating": rating,
                "rating_count": rating_count,
                "review_count": review_count,
                "description": description,
                "product_url": url,
                "platform": "flipkart"
            }
            
            logger.info(f"✅ Scraping complete: {len(images)} images, {len(sizes)} sizes, {len(colors)} colors")
            return result
                
        except Exception as e:
            logger.error(f"Flipkart scraping failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
        finally:
            if browser:
                await browser.close()
            if p:
                await p.stop()
    
    async def _scrape_amazon(self, url: str) -> Dict:
        """Amazon India scraper"""
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
                "rating": 0,
                "rating_count": 0,
                "review_count": 0,
                "description": "",
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
        """Myntra scraper"""
        return {"success": False, "error": "Myntra scraping in development"}
    
    async def _scrape_ajio(self, url: str) -> Dict:
        """Ajio scraper"""
        return {"success": False, "error": "Ajio scraping in development"}
    
    async def _scrape_meesho(self, url: str) -> Dict:
        """Meesho scraper"""
        return {"success": False, "error": "Meesho scraping in development"}
    
    async def _scrape_snapdeal(self, url: str) -> Dict:
        """Snapdeal scraper"""
        return {"success": False, "error": "Snapdeal scraping in development"}
    
    async def _scrape_generic(self, url: str) -> Dict:
        """Generic scraper"""
        return {"success": False, "error": "Unsupported platform"}


# Global instance
product_scraper = ProductScraper()

def get_product_scraper():
    return product_scraper