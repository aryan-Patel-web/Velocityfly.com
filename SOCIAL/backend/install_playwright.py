#!/usr/bin/env python3.11
import subprocess
import sys

def main():
    # Install Playwright browsers
    # subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"], check=True)
    print("Playwright browsers installed successfully")

if __name__ == "__main__":
    main()