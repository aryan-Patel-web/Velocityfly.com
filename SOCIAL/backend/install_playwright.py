# #!/usr/bin/env python3.11
# import subprocess
# import sys
# import os

# # Force browser install to project directory (persistent on Render)
# browser_path = '/opt/render/project/.browsers'
# os.makedirs(browser_path, exist_ok=True)
# os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_path

# print(f"Installing Playwright browsers to: {browser_path}")

# result = subprocess.run(
#     [sys.executable, "-m", "playwright", "install", "chromium"],
#     check=True,
#     env=dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=browser_path)
# )

# print("Browser installation complete")







#!/usr/bin/env python3.11
"""
install_playwright.py - FIXED VERSION
Uses consistent path: /opt/render/project/.playwright (matches mainY.py)
Includes retry logic and IPv4 support
"""
import subprocess
import sys
import os
import time

# ✅ CRITICAL: Use SAME path as mainY.py
BROWSER_PATH = '/opt/render/project/.playwright'

def install_playwright_with_retry(max_retries=3):
    """Install Playwright browsers with IPv4 forcing and retry logic"""
    
    print("=" * 60)
    print("🎭 Installing Playwright Chromium Browser")
    print(f"📁 Browser path: {BROWSER_PATH}")
    print("=" * 60)
    
    # Create browser directory
    os.makedirs(BROWSER_PATH, exist_ok=True)
    
    # ✅ FIX 1: Force IPv4 only (disable IPv6)
    env = os.environ.copy()
    env['PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS'] = '1'
    env['PLAYWRIGHT_BROWSERS_PATH'] = BROWSER_PATH
    
    # ✅ FIX 2: Force IPv4 by preferring IPv4 addresses
    env['NODE_OPTIONS'] = '--dns-result-order=ipv4first'
    
    install_command = [
        sys.executable,
        '-m', 'playwright',
        'install',
        'chromium'
    ]
    
    for attempt in range(1, max_retries + 1):
        print(f"\n📥 Attempt {attempt}/{max_retries}: Installing Chromium...")
        
        try:
            result = subprocess.run(
                install_command,
                env=env,
                check=True,
                capture_output=True,
                text=True,
                timeout=60  # 5 minute timeout
            )
            
            print("✅ Chromium installed successfully!")
            print(f"✅ Browser location: {BROWSER_PATH}")
            if result.stdout:
                print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Attempt {attempt} failed:")
            print(f"Exit code: {e.returncode}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            
            if attempt < max_retries:
                wait_time = attempt * 5  # Exponential backoff
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"\n❌ All {max_retries} attempts failed")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Attempt {attempt} timed out after 5 minutes")
            if attempt < max_retries:
                print("⏳ Retrying...")
                time.sleep(5)
            else:
                print(f"\n❌ All {max_retries} attempts timed out")
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return False

def check_playwright_installation():
    """Check if Chromium is already installed"""
    try:
        chromium_path = os.path.join(BROWSER_PATH, 'chromium-*')
        if os.path.exists(BROWSER_PATH):
            dirs = os.listdir(BROWSER_PATH)
            if any('chromium' in d for d in dirs):
                print(f"✅ Chromium found in {BROWSER_PATH}")
                return True
        return False
    except Exception as e:
        print(f"⚠️ Could not check installation status: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 Checking Playwright installation status...")
    print(f"📁 Browser path: {BROWSER_PATH}")
    
    if check_playwright_installation():
        print("✅ No installation needed - Chromium already present")
        sys.exit(0)
    
    print("\n📦 Chromium not found - starting installation...")
    
    success = install_playwright_with_retry(max_retries=3)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ PLAYWRIGHT INSTALLATION COMPLETED")
        print(f"✅ Browser location: {BROWSER_PATH}")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("⚠️ PLAYWRIGHT INSTALLATION FAILED")
        print("Continuing deployment - slideshow generation will be disabled")
        print("=" * 60)
        # ✅ Don't fail the build - just warn
        sys.exit(0)  # Exit 0 to continue deployment