# backend/app/main.py
import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fetcher import fetch_posts
from analyzer import analyze_and_save
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Enable debug mode → shows full errors in docker logs
app = FastAPI(title="Reddit Fetcher & Analyzer", debug=True)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Directory ---
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)

# Serve static files (charts + CSV)
app.mount("/static", StaticFiles(directory=DATA_DIR), name="static")


# --- Request Model ---
class FetchRequest(BaseModel):
    subreddit: str
    keyword: str
    limit: int = 500


# --- Fetch + Analyze Endpoint ---
@app.post("/api/fetch")
def fetch_and_analyze(req: FetchRequest):
    try:
        print("\n===== FETCH STARTED =====")
        print(f"Subreddit: {req.subreddit}, Keyword: {req.keyword}, Limit: {req.limit}")

        df = fetch_posts(req.subreddit, req.keyword, req.limit)
        print(f"Fetcher returned {len(df)} rows.")

    except Exception as e:
        print("\n>>> FETCH ERROR <<<")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Fetch error: {e}")

    # RUN ANALYZER
    try:
        print("\n===== ANALYSIS STARTED =====")
        analysis = analyze_and_save()
        print("Analysis result:", analysis)

    except Exception as e:
        print("\n>>> ANALYSIS ERROR <<<")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis error: {e}")

    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])

    # Build response for frontend
    base = "/static"
    response = {
        "fetched": analysis["fetched"],
        "analyzed": analysis["analyzed"],
        "avg_sentiment": analysis["avg_sentiment"],
        "top_words": analysis["top_words"],
        "computation_method": "MapReduce Algorithm", # <--- Added Badge Info
        "charts": {
            "top_words_chart": f"{base}/{analysis['top_words_chart']}" if analysis['top_words_chart'] else None,
            "posts_by_date_chart": f"{base}/{analysis['posts_by_date_chart']}" if analysis['posts_by_date_chart'] else None
        },
        "sentiment_csv": f"{base}/{analysis['sentiment_csv']}"
    }

    print("\n===== SUCCESS =====")
    return response


# --- FIXED Preview Endpoint ---
@app.get("/api/preview")
def preview(nrows: int = 10):
    import pandas as pd
    import numpy as np

    csv_path = os.path.join(DATA_DIR, "reddit_data_with_sentiment.csv")

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Data not found")

    df = pd.read_csv(csv_path)

    # FIX: JSON-safe values only
    df = df.replace([np.nan, np.inf, -np.inf], 0)

    return {
        "preview": df.head(nrows).to_dict(orient="records")
    }