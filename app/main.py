import os
import json
import uuid
import platform
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.scraper import GoogleMapsScraper

# ==========================================================
# ✅ Auto-detect ChromeDriver Path
# ==========================================================
def find_chromedriver():
    """Automatically find ChromeDriver"""
    env_path = os.getenv("CHROMEDRIVER_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    system = platform.system()
    paths = []

    if system == "Linux":
        paths = ["/usr/bin/chromedriver", "/usr/local/bin/chromedriver", "/snap/bin/chromium.chromedriver"]
    elif system == "Darwin":
        paths = ["/usr/local/bin/chromedriver", "/opt/homebrew/bin/chromedriver"]
    elif system == "Windows":
        paths = [
            r"E:\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
            "chromedriver.exe"
        ]

    for path in paths:
        if os.path.exists(path):
            return path

    return "chromedriver"

CHROMEDRIVER_PATH = find_chromedriver()

# ==========================================================
# ✅ FastAPI Initialization
# ==========================================================
app = FastAPI(title="Google Maps Review Scraper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# ✅ Job Database
# ==========================================================
jobs_db = {}

# ==========================================================
# ✅ Pydantic Model
# ==========================================================
class ScrapeRequest(BaseModel):
    maps_url: str
    async_mode: bool = True

# ==========================================================
# ✅ Background Task
# ==========================================================
def run_scraper_sync(job_id: str, maps_url: str):
    try:
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["started_at"] = datetime.now().isoformat()
        print(f"🟡 Starting job {job_id} for URL: {maps_url}")

        scraper = GoogleMapsScraper(
            maps_url=maps_url,
            chromedriver_path=CHROMEDRIVER_PATH,
            headless=True
        )

        reviews_data = scraper.scrape()

        if not reviews_data:
            raise ValueError("No reviews were extracted from this location")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{job_id}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(reviews_data, f, indent=4, ensure_ascii=False)

        jobs_db[job_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "total_reviews": len(reviews_data),
            "output_file": str(output_file)
        })
        print(f"✅ Job {job_id} completed: {len(reviews_data)} reviews")

    except FileNotFoundError:
        msg = f"ChromeDriver not found at {CHROMEDRIVER_PATH}"
        jobs_db[job_id].update({"status": "failed", "error": msg, "error_type": "chromedriver_not_found"})
    except ValueError as e:
        jobs_db[job_id].update({"status": "failed", "error": str(e), "error_type": "no_reviews"})
    except Exception as e:
        import traceback
        jobs_db[job_id].update({
            "status": "failed",
            "error": str(e),
            "error_trace": traceback.format_exc(),
            "error_type": "unknown"
        })

# ==========================================================
# ✅ Routes
# ==========================================================
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "chromedriver_path": CHROMEDRIVER_PATH,
        "chromedriver_exists": os.path.exists(CHROMEDRIVER_PATH)
    }

@app.post("/scrape")
async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "maps_url": request.maps_url
    }

    print(f"🆕 New job: {job_id}")
    background_tasks.add_task(run_scraper_sync, job_id, request.maps_url)
    return jobs_db[job_id]

@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

@app.get("/download/{job_id}")
def download_results(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    output_path = job.get("output_file")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"job_id": job_id, "data": data}

# ==========================================================
# ✅ Serve Frontend UI (fixed)
# ==========================================================
UI_DIR = Path(__file__).parent / "ui"

@app.get("/")
def serve_index():
    """Serve the frontend UI"""
    index_path = UI_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

# Serve static files (if your HTML uses assets like JS/CSS)
app.mount("/ui", StaticFiles(directory="app/ui"), name="ui")

# ==========================================================
# ✅ Startup Message
# ==========================================================
@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 60)
    print("🚀 Google Maps Scraper API Started")
    print("=" * 60)
    print(f"ChromeDriver Path: {CHROMEDRIVER_PATH}")
    print(f"ChromeDriver Exists: {os.path.exists(CHROMEDRIVER_PATH)}")
    print("=" * 60 + "\n")

# ==========================================================
# ✅ Run (for local testing)
# ==========================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)






# """
# Minimal fixes to your existing main.py
# Just replace your current main.py with this
# """
# import os
# import json
# import uuid
# import platform
# from datetime import datetime
# from pathlib import Path
# from fastapi import FastAPI, BackgroundTasks, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from app.scraper import GoogleMapsScraper

# # ==========================================================
# # ✅ Auto-detect ChromeDriver Path
# # ==========================================================
# def find_chromedriver():
#     """Automatically find ChromeDriver"""
#     # Check environment variable first
#     env_path = os.getenv("CHROMEDRIVER_PATH")
#     if env_path and os.path.exists(env_path):
#         return env_path
    
#     # Try common paths based on OS
#     system = platform.system()
#     paths = []
    
#     if system == "Linux":
#         paths = [
#             "/usr/bin/chromedriver",
#             "/usr/local/bin/chromedriver",
#             "/snap/bin/chromium.chromedriver"
#         ]
#     elif system == "Darwin":  # macOS
#         paths = [
#             "/usr/local/bin/chromedriver",
#             "/opt/homebrew/bin/chromedriver"
#         ]
#     elif system == "Windows":
#         paths = [
#             r"E:\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",
#             "chromedriver.exe"
#         ]
    
#     for path in paths:
#         if os.path.exists(path):
#             return path
    
#     # Fallback
#     return "chromedriver"

# CHROMEDRIVER_PATH = find_chromedriver()

# # ==========================================================
# # ✅ FastAPI Initialization
# # ==========================================================
# app = FastAPI(title="Google Maps Review Scraper API", version="1.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ==========================================================
# # ✅ Job Database
# # ==========================================================
# jobs_db = {}

# # ==========================================================
# # ✅ Pydantic Models
# # ==========================================================
# class ScrapeRequest(BaseModel):
#     maps_url: str
#     async_mode: bool = True

# # ==========================================================
# # ✅ Background Job Handler (Fixed)
# # ==========================================================
# def run_scraper_sync(job_id: str, maps_url: str):
#     """Runs scraper with better error handling"""
#     try:
#         # Update to processing
#         jobs_db[job_id]["status"] = "processing"
#         jobs_db[job_id]["started_at"] = datetime.now().isoformat()
#         print(f"🟡 Starting job {job_id} for URL: {maps_url}")

#         # Initialize scraper
#         scraper = GoogleMapsScraper(
#             maps_url=maps_url,
#             chromedriver_path=CHROMEDRIVER_PATH,
#             headless=True
#         )

#         # Scrape
#         reviews_data = scraper.scrape()
        
#         # Validate we got data
#         if not reviews_data or len(reviews_data) == 0:
#             raise ValueError("No reviews were extracted from this location")

#         # Save results
#         output_dir = Path("output")
#         output_dir.mkdir(exist_ok=True)
#         output_file = output_dir / f"{job_id}.json"

#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(reviews_data, f, indent=4, ensure_ascii=False)

#         # Update job as completed
#         jobs_db[job_id].update({
#             "status": "completed",
#             "completed_at": datetime.now().isoformat(),
#             "total_reviews": len(reviews_data),
#             "output_file": str(output_file)
#         })

#         print(f"✅ Job {job_id} completed: {len(reviews_data)} reviews")

#     except FileNotFoundError as e:
#         # ChromeDriver not found
#         error_msg = f"ChromeDriver not found at {CHROMEDRIVER_PATH}. Please install ChromeDriver."
#         print(f"❌ Job {job_id} failed: {error_msg}")
#         jobs_db[job_id].update({
#             "status": "failed",
#             "completed_at": datetime.now().isoformat(),
#             "error": error_msg,
#             "error_type": "chromedriver_not_found"
#         })

#     except ValueError as e:
#         # No reviews found
#         error_msg = str(e)
#         print(f"❌ Job {job_id} failed: {error_msg}")
#         jobs_db[job_id].update({
#             "status": "failed",
#             "completed_at": datetime.now().isoformat(),
#             "error": error_msg,
#             "error_type": "no_reviews"
#         })

#     except Exception as e:
#         # Any other error
#         import traceback
#         error_details = traceback.format_exc()
#         error_msg = str(e)
        
#         print(f"❌ Job {job_id} failed:\n{error_details}")
        
#         # Try to categorize error
#         error_type = "unknown"
#         if "timeout" in error_msg.lower():
#             error_type = "timeout"
#         elif "chromedriver" in error_msg.lower():
#             error_type = "chromedriver_not_found"
        
#         jobs_db[job_id].update({
#             "status": "failed",
#             "completed_at": datetime.now().isoformat(),
#             "error": error_msg,
#             "error_type": error_type
#         })

# # ==========================================================
# # ✅ Routes
# # ==========================================================

# @app.get("/health")
# def health_check():
#     """Health check - also shows ChromeDriver status"""
#     return {
#         "status": "ok",
#         "timestamp": datetime.now().isoformat(),
#         "chromedriver_path": CHROMEDRIVER_PATH,
#         "chromedriver_exists": os.path.exists(CHROMEDRIVER_PATH)
#     }

# @app.post("/scrape")
# async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
#     """Start scraping job"""
#     job_id = str(uuid.uuid4())
#     jobs_db[job_id] = {
#         "job_id": job_id,
#         "status": "queued",
#         "created_at": datetime.now().isoformat(),
#         "maps_url": request.maps_url
#     }

#     print(f"🆕 New job: {job_id}")
#     background_tasks.add_task(run_scraper_sync, job_id, request.maps_url)

#     return jobs_db[job_id]

# @app.get("/job/{job_id}")
# def get_job_status(job_id: str):
#     """Get job status"""
#     if job_id not in jobs_db:
#         raise HTTPException(status_code=404, detail="Job not found")
#     return jobs_db[job_id]

# @app.get("/download/{job_id}")
# def download_results(job_id: str):
#     """Download results JSON"""
#     if job_id not in jobs_db:
#         raise HTTPException(status_code=404, detail="Job not found")

#     job = jobs_db[job_id]
#     if job["status"] != "completed":
#         raise HTTPException(status_code=400, detail="Job not completed yet")

#     output_path = job.get("output_file")
#     if not output_path or not os.path.exists(output_path):
#         raise HTTPException(status_code=404, detail="Output file not found")

#     with open(output_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     return {"job_id": job_id, "data": data}

# # ==========================================================
# # ✅ Serve UI
# # ==========================================================
# app.mount("/", StaticFiles(directory="app/ui", html=True), name="ui")

# # ==========================================================
# # ✅ Startup
# # ==========================================================
# @app.on_event("startup")
# async def startup_event():
#     """Print configuration on startup"""
#     print("\n" + "="*60)
#     print("🚀 Google Maps Scraper API Started")
#     print("="*60)
#     print(f"ChromeDriver Path: {CHROMEDRIVER_PATH}")
#     print(f"ChromeDriver Exists: {os.path.exists(CHROMEDRIVER_PATH)}")
#     print("="*60 + "\n")
    
#     if not os.path.exists(CHROMEDRIVER_PATH):
#         print("⚠️  WARNING: ChromeDriver not found!")
#         print("   Install ChromeDriver or scraping will fail.")
#         print("   Run: python test_chromedriver.py\n")

# # ==========================================================
# # ✅ Run
# # ==========================================================
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)