"""
Quick test to verify ChromeDriver is working
Run: python test_chromedriver.py
"""
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_chromedriver():
    """Test if ChromeDriver can launch Chrome"""
    
    # Try different common paths
    paths_to_try = [
        os.getenv("CHROMEDRIVER_PATH"),
        "chromedriver",
        "/usr/local/bin/chromedriver",
        "/usr/bin/chromedriver",
        "E:\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
    ]
    
    print("🔍 Testing ChromeDriver installation...\n")
    
    for path in paths_to_try:
        if not path:
            continue
            
        print(f"Trying: {path}")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            service = Service(path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Try to load a page
            driver.get("https://www.google.com")
            title = driver.title
            driver.quit()
            
            print(f"✅ SUCCESS! ChromeDriver is working at: {path}")
            print(f"   Loaded page: {title}\n")
            print(f"💡 Add this to your .env file:")
            print(f"   CHROMEDRIVER_PATH={path}\n")
            return path
            
        except FileNotFoundError:
            print(f"   ❌ Not found at this path\n")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}\n")
    
    print("❌ ChromeDriver not found in any common location!")
    print("\n📥 Installation Instructions:")
    print("\nFor Linux/Ubuntu:")
    print("  sudo apt-get update")
    print("  sudo apt-get install -y chromium-browser chromium-chromedriver")
    print("  # Or download from: https://chromedriver.chromium.org/")
    print("\nFor macOS:")
    print("  brew install chromedriver")
    print("\nFor Windows:")
    print("  1. Download from: https://chromedriver.chromium.org/")
    print("  2. Extract to C:\\chromedriver\\")
    print("  3. Add to PATH or create .env file")
    
    return None

if __name__ == "__main__":
    result = test_chromedriver()
    if not result:
        sys.exit(1)