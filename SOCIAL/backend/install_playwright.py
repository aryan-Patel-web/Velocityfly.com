#!/usr/bin/env python3.11
import subprocess
import sys
import os

# Force browser install to project directory (persistent on Render)
browser_path = '/opt/render/project/.browsers'
os.makedirs(browser_path, exist_ok=True)
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_path

print(f"Installing Playwright browsers to: {browser_path}")

result = subprocess.run(
    [sys.executable, "-m", "playwright", "install", "chromium"],
    check=True,
    env=dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=browser_path)
)

print("Browser installation complete")





# #!/usr/bin/env python3.11
# """
# install_playwright.py - FINAL WORKING VERSION
# Uses system-installed Chromium - NO DOWNLOAD NEEDED
# 100% reliable - works every time
# """
# import subprocess
# import sys
# import os

# print("=" * 70)
# print("🎭 Playwright Setup")
# print("=" * 70)

# # ✅ CRITICAL: Skip browser download entirely
# os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'

# # ✅ Tell Playwright to use system Chromium
# chromium_paths = [
#     '/usr/bin/chromium-browser',
#     '/usr/bin/chromium',
#     '/usr/bin/google-chrome',
#     '/usr/bin/chrome'
# ]

# chromium_found = None
# for path in chromium_paths:
#     if os.path.exists(path):
#         chromium_found = path
#         break

# if chromium_found:
#     os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'] = chromium_found
#     print(f"✅ Found system Chromium: {chromium_found}")
#     print("✅ Playwright configured successfully")
#     print("⏩ No download needed - using pre-installed browser")
# else:
#     print("⚠️ System Chromium not found")
#     print("⚠️ Slideshow features will be disabled")
#     print("💡 To enable: Add 'chromium-browser' to build command")

# print("=" * 70)
# sys.exit(0)