Here’s a **complete `README.md`** tailored for your client to run the FastAPI project on **Windows** without Docker. It explains all steps: installing Python & dependencies, activating the virtual environment, running the server, testing, and accessing the JSON output.

````markdown
# Google Maps Review Scraper API

This is a **FastAPI project** that scrapes Google Maps reviews for a given location URL. The API provides a web interface and endpoints to start scraping, monitor job status, and download results in JSON format.

This guide explains **how to run the project on Windows** from scratch.

---

## 1️⃣ Prerequisites

- **Chrome Browser** installed.

- **ChromeDriver** compatible with their Chrome version.  
  Download: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)  

  > Make sure the downloaded `chromedriver.exe` path is set in the `.env` file as:
  > ```
  > CHROMEDRIVER_PATH=E:\Downloads\chromedriver-win64\chromedriver.exe
  > ```

---

## 2️⃣ Clone or Download the Project

Open **Command Prompt** and navigate to your desired folder:

```cmd
cd C:\maps-scraper-api
````

Clone the repository (or copy the project folder):

```cmd
git clone <repository-url> maps-scraper-api
cd maps-scraper-api
```

---

## 3️⃣ Create and Activate Virtual Environment (venv)

Create a new virtual environment (if not already created):

```cmd
python -m venv scraperfastapi
```

Activate the virtual environment:

```cmd
scraperfastapi\Scripts\activate
```

> You should see `(scraperfastapi)` in your terminal.

---

## 4️⃣ Install Required Dependencies

Install Python packages from `requirements.txt`:

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

Check that `fastapi`, `uvicorn`, and `selenium` are installed.

---

## 5️⃣ Verify ChromeDriver

Make sure the path in `.env` is correct, e.g.:

```
CHROMEDRIVER_PATH=E:\Downloads\chromedriver-win64\chromedriver.exe
```

You can also test manually:

```cmd
python tests\test_chromedriver.py
```

It should confirm that ChromeDriver works.

---

## 6️⃣ Run FastAPI Server

Run the API with Uvicorn:

```cmd
uvicorn app.main:app --reload --port 8000
```

* `--reload` enables auto-reload on code changes.
* Port `8000` is used by default.

You should see output like:

```
INFO: Uvicorn running on http://127.0.0.1:8000
🚀 Google Maps Scraper API Started
ChromeDriver Path: E:\Downloads\chromedriver-win64\chromedriver.exe
ChromeDriver Exists: True
```

---

## 7️⃣ Access the Web Interface

Open your browser and go to:

```
http://127.0.0.1:8000
```

You will see the **Google Maps Review Scraper** UI.

* Enter a Google Maps URL (e.g., a restaurant or business).
* Click **Start Scraping**.
* Wait for the job to complete.
* Download the JSON results from the link provided.

---

## 8️⃣ API Endpoints (Optional)

You can also test using **Postman** or **browser**:

1. **Health Check**

```http
GET http://127.0.0.1:8000/health
```

2. **Start Scraping**

```http
POST http://127.0.0.1:8000/scrape
Content-Type: application/json

{
  "maps_url": "https://www.google.com/maps/place/Katz's+Delicatessen/@40.7223063,-73.9877547,17z",
  "async_mode": true
}
```

3. **Check Job Status**

```http
GET http://127.0.0.1:8000/job/<job_id>
```

4. **Download Results**

```http
GET http://127.0.0.1:8000/download/<job_id>
```

All downloaded JSON files are saved in the `output/` folder.

---

## 9️⃣ Output Folder

* The scraper automatically saves results in:

```
maps-scraper-api\output\<job_id>.json
```

* Open these files with any text editor or JSON viewer.

---

## 🔟 Tips & Troubleshooting

1. If scraping fails due to ChromeDriver, ensure the `.env` path matches your ChromeDriver location.
2. Make sure the Google Maps URL is valid and public.
3. For large review pages, scraping may take a few minutes.
4. Stop the server with `CTRL+C` in the terminal.

---

## ✅ Summary

1. Install Python & ChromeDriver.
2. Activate virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run server: `uvicorn app.main:app --reload --port 8000`.
5. Open `http://127.0.0.1:8000` in browser.
6. Start scraping and download JSON from `output/`.

---

Made with ❤️ for scraping Google Maps reviews efficiently.

```