from dotenv import load_dotenv
import os
load_dotenv()

print("Testing ChromeDriver path...")
path = os.getenv("CHROMEDRIVER_PATH")
print(f"Path: {path}")
print(f"Exists: {os.path.exists(path)}")

if os.path.exists(path):
    print("✅ ChromeDriver found!")
else:
    print("❌ ChromeDriver NOT found - check your .env file!")
