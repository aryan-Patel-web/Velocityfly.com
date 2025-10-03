"""
YTscrapADS.py - Product scraper for e-commerce sites
Supports: Flipkart, Amazon, custom product pages
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ProductScraper:
    """Scrape product details from e-commerce URLs"""
    
    def __init__(self):
        self.supported_sites = ['flipkart.com', 'amazon.in', 'myntra.com']
    
    async def scrape_product(self, url: str) -> Dict:
        """
        Scrape product from URL
        
        Returns:
            {
                "success": True/False,
                "product_name": str,
                "brand": str,
                "price": float,
                "original_price": float,
                "discount": str,
                "images": [url1, url2, ...],
                "colors": ["Red", "Blue"],
                "sizes": ["S", "M", "L"],
                "description": str,
                "specifications": {},
                "product_url": str,
                "platform": "flipkart/amazon/etc"
            }
        """
        try:
            domain = urlparse(url).netloc
            
            if 'flipkart' in domain:
                return await self._scrape_flipkart(url)
            elif 'amazon' in domain:
                return await self._scrape_amazon(url)
            else:
                return {
                    "success": False,
                    "error": "Unsupported website. Only Flipkart and Amazon are supported."
                }
                
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _scrape_flipkart(self, url: str) -> Dict:
        """Scrape Flipkart product page"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, wait_until='networkidle')
                await asyncio.sleep(2)  # Wait for dynamic content
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract product name
                product_name = soup.find('span', class_='VU-ZEz')
                product_name = product_name.text.strip() if product_name else "Unknown Product"
                
                # Extract brand
                brand_elem = soup.find('a', class_='VU-ZEz')
                brand = brand_elem.text.strip() if brand_elem else "Unknown Brand"
                
                # Extract price
                price_elem = soup.find('div', class_='Nx9bqj CxhGGd')
                price = 0
                if price_elem:
                    price_text = price_elem.text.strip().replace('₹', '').replace(',', '')
                    price = float(price_text)
                
                # Extract original price
                original_price_elem = soup.find('div', class_='yRaY8j A6+E6v')
                original_price = price
                if original_price_elem:
                    orig_text = original_price_elem.text.strip().replace('₹', '').replace(',', '')
                    original_price = float(orig_text)
                
                # Calculate discount
                discount = ""
                if original_price > price:
                    discount_pct = ((original_price - price) / original_price) * 100
                    discount = f"{int(discount_pct)}% OFF"
                
                # Extract images
                images = []
                img_containers = soup.find_all('img', class_='DByuf4')
                for img in img_containers[:5]:  # Get first 5 images
                    img_url = img.get('src') or img.get('data-src')
                    if img_url and img_url.startswith('http'):
                        images.append(img_url)
                
                # Extract colors
                colors = []
                color_divs = soup.find_all('li', class_='_0H_LOL')
                for color_div in color_divs:
                    color_text = color_div.get('title', '')
                    if color_text:
                        colors.append(color_text)
                
                # Extract sizes
                sizes = []
                size_divs = soup.find_all('a', class_='_0H_LOL')
                for size_div in size_divs:
                    size_text = size_div.text.strip()
                    if size_text and len(size_text) <= 4:  # S, M, L, XL, XXL
                        sizes.append(size_text)
                
                # Extract description
                desc_elem = soup.find('div', class_='_4gvKMe')
                description = desc_elem.text.strip() if desc_elem else ""
                
                await browser.close()
                
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
    
    async def _scrape_amazon(self, url: str) -> Dict:
        """Scrape Amazon product page"""
        # Similar implementation for Amazon
        # Amazon has different HTML structure
        return {
            "success": False,
            "error": "Amazon scraping coming soon"
        }


# Global instance
product_scraper = ProductScraper()

def get_product_scraper():
    return product_scraper