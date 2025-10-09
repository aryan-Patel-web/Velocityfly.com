"""
Jobyaari Engineering Scraper - Complete job details extraction
"""

import asyncio
from pathlib import Path
from datetime import datetime
import re

from playwright.async_api import async_playwright
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "templates"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class JobScraper:
    def __init__(self):
        self.jobs = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def get_job_urls(self, page, url):
        """Get all job URLs from the category page"""
        
        print(f"\n[LOADING] {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        print("[WAIT] Waiting for jobs to load...")
        await asyncio.sleep(5)
        
        # Close any modal that might appear
        try:
            close_button = await page.query_selector('button:has-text("×"), button[aria-label="Close"]')
            if close_button:
                await close_button.click()
                await asyncio.sleep(1)
        except:
            pass
        
        # Scroll to load all jobs
        print("[SCROLL] Loading all jobs...")
        previous_height = 0
        for i in range(15):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
            
            current_height = await page.evaluate('document.body.scrollHeight')
            if current_height == previous_height:
                print(f"  No more content to load (scroll {i+1})")
                break
            previous_height = current_height
            print(f"  Scroll {i+1}")
        
        # Extract job URLs - looking for links that lead to job detail pages
        print("\n[EXTRACT] Finding job detail links...")
        
        job_urls = await page.evaluate("""
            () => {
                const urls = new Set();
                
                // Find all clickable job cards or links
                const links = document.querySelectorAll('a[href]');
                
                links.forEach(link => {
                    const href = link.href;
                    // Look for URLs that contain job IDs (4 digits or more)
                    // Pattern: /jobdetails/XXXX or similar
                    if (href.match(/\/(jobdetails?|job|posting)\/\d{4}/i) || 
                        href.match(/\/\d{4}$/) ||
                        (href.includes('job') && /\d{4}/.test(href))) {
                        urls.add(href);
                    }
                });
                
                return Array.from(urls);
            }
        """)
        
        # If no URLs found with the pattern, try finding all job-related links
        if len(job_urls) == 0:
            print("[INFO] Trying alternative method to find job links...")
            job_urls = await page.evaluate("""
                () => {
                    const urls = new Set();
                    const links = document.querySelectorAll('a[href]');
                    
                    links.forEach(link => {
                        const href = link.href;
                        const text = link.innerText.toLowerCase();
                        
                        // If link contains job-related keywords or numeric ID
                        if ((text.includes('engineer') || 
                             text.includes('officer') || 
                             text.includes('assistant') ||
                             text.includes('manager') ||
                             /\d{4}/.test(href)) && 
                            !href.includes('category') &&
                            !href.includes('login') &&
                            !href.includes('register')) {
                            urls.add(href);
                        }
                    });
                    
                    return Array.from(urls);
                }
            """)
        
        print(f"[RESULT] Found {len(job_urls)} job URLs")
        
        # Save URLs to file for reference
        if job_urls:
            urls_file = OUTPUT_DIR / f"urls_{self.session_id}.txt"
            with open(urls_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(job_urls))
            print(f"[SAVED] URLs to {urls_file}")
        
        return job_urls
    
    async def scrape_job(self, page, url):
        """Scrape individual job detail page"""
        
        try:
            print(f"  [LOADING] {url}")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            await asyncio.sleep(3)
            
            # Close any modal
            try:
                close_button = await page.query_selector('button:has-text("×"), button[aria-label="Close"]')
                if close_button:
                    await close_button.click()
                    await asyncio.sleep(1)
            except:
                pass
            
            # Extract job details
            job_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // Get all text content
                    const bodyText = document.body.innerText;
                    
                    // Helper function to extract field values
                    const extractField = (pattern, defaultValue = '') => {
                        const match = bodyText.match(pattern);
                        return match ? match[1].trim() : defaultValue;
                    };
                    
                    // Extract main headings (organization and job title)
                    const headings = Array.from(document.querySelectorAll('h1, h2, h3'))
                        .map(h => h.innerText.trim())
                        .filter(t => t && 
                            !t.toLowerCase().includes('welcome') && 
                            !t.toLowerCase().includes('job yaari') &&
                            !t.toLowerCase().includes('dream job'));
                    
                    data.job_title = headings[0] || '';
                    data.organization = headings[1] || '';
                    
                    // If first heading seems like organization, swap them
                    if (data.job_title.length > 100 || data.job_title.includes('Limited') || 
                        data.job_title.includes('Corporation') || data.job_title.includes('Institute')) {
                        [data.job_title, data.organization] = [data.organization, data.job_title];
                    }
                    
                    // Extract other fields using various patterns
                    data.salary = extractField(/(?:Salary|Pay Scale)[:\s]*\n?\s*([^\n]+)/i);
                    data.experience = extractField(/(?:Experience)[:\s]*\n?\s*([^\n]+)/i);
                    data.qualification = extractField(/(?:Qualification|Educational Qualification)[:\s]*\n?\s*([^\n]+)/i);
                    data.location = extractField(/(?:Location|Locations|Place)[:\s]*\n?\s*([^\n]+)/i);
                    data.last_date = extractField(/(?:Last Date|Application Deadline)[:\s]*\n?\s*([^\n]+)/i);
                    data.posted_date = extractField(/(?:Posted|Posted on)[:\s]*\n?\s*([^\n]+)/i);
                    data.age_limit = extractField(/(?:Age Limit|Age)[:\s]*\n?\s*([^\n]+)/i);
                    data.job_openings = extractField(/(?:Job Openings|Vacancies|No\\.? of Posts)[:\s]*\n?\s*([^\n]+)/i);
                    data.specialization = extractField(/(?:Specialization|Branch|Stream)[:\s]*\n?\s*([^\n]+)/i);
                    data.walk_in = extractField(/(?:Walk In|Interview Date)[:\s]*\n?\s*([^\n]+)/i);
                    
                    // Try to extract job ID from URL or page
                    const urlMatch = window.location.href.match(/\/(\d{4,})/);
                    data.job_id = urlMatch ? urlMatch[1] : '';
                    
                    // Extract all text for description (can be parsed later)
                    const mainContent = document.querySelector('main, article, .content, .job-details');
                    data.full_description = mainContent ? mainContent.innerText.trim() : bodyText;
                    
                    return data;
                }
            """)
            
            job_data['job_url'] = url
            
            # Extract 4-digit number from URL
            match = re.search(r'/(\d{4,})', url)
            if match:
                job_data['job_id'] = match.group(1)
            
            return job_data
            
        except Exception as e:
            print(f"  [ERROR] Failed to scrape {url}: {e}")
            return None
    
    async def run(self, category_url, max_jobs=None):
        """Main scraping process"""
        async with async_playwright() as p:
            print("[BROWSER] Launching Chromium...")
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()
            
            # Get all job URLs
            job_urls = await self.get_job_urls(page, category_url)
            
            if not job_urls:
                print("\n[WARNING] No job URLs found!")
                print("  Check if the page structure has changed")
                print("  or if JavaScript is required to load jobs.")
                
                # Save page HTML for debugging
                html = await page.content()
                debug_file = OUTPUT_DIR / f"debug_{self.session_id}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"  Saved page HTML to: {debug_file}")
                
                await browser.close()
                return
            
            # Limit number of jobs if specified
            if max_jobs:
                job_urls = job_urls[:max_jobs]
            
            # Scrape each job
            print(f"\n[PROCESSING] Scraping {len(job_urls)} jobs...")
            print("=" * 60)
            
            for i, url in enumerate(job_urls, 1):
                print(f"\n[{i}/{len(job_urls)}]")
                job = await self.scrape_job(page, url)
                
                if job:
                    self.jobs.append(job)
                    print(f"  ✓ {job.get('organization', 'N/A')}")
                    print(f"    Position: {job.get('job_title', 'N/A')}")
                    print(f"    Salary: {job.get('salary', 'N/A')}")
                    print(f"    Last Date: {job.get('last_date', 'N/A')}")
                else:
                    print(f"  ✗ Failed to scrape")
                
                # Be nice to the server
                await asyncio.sleep(2)
            
            await browser.close()
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save scraped data to CSV and JSON"""
        if not self.jobs:
            print("\n[WARNING] No jobs scraped!")
            return
        
        df = pd.DataFrame(self.jobs)
        
        # Save CSV
        csv_file = OUTPUT_DIR / f"jobs_{self.session_id}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n[SAVED] CSV: {csv_file}")
        
        # Save JSON with full details
        json_file = OUTPUT_DIR / f"jobs_{self.session_id}.json"
        df.to_json(json_file, orient='records', indent=2, force_ascii=False)
        print(f"[SAVED] JSON: {json_file}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"Total jobs scraped: {len(df)}")
        print(f"Organizations: {df['organization'].nunique()}")
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"{'='*60}\n")
        
        # Show sample
        print("Sample of scraped data:")
        print(df[['job_title', 'organization', 'salary', 'last_date']].head(10).to_string())


async def main():
    scraper = JobScraper()
    
    # Scrape all engineering jobs
    # Set max_jobs=10 to test with first 10 jobs, or None for all jobs
    await scraper.run(
        category_url="https://www.jobyaari.com/category/engineering",
        max_jobs=None  # Change to a number like 10 for testing
    )

if __name__ == "__main__":
    asyncio.run(main())