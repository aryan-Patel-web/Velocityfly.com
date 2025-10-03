import subprocess
import sys

def install_browsers():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Playwright browsers installed")
    except Exception as e:
        print(f"❌ Failed to install browsers: {e}")

if __name__ == "__main__":
    install_browsers()