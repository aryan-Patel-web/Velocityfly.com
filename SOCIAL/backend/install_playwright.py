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





