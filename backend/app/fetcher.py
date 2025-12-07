# backend/app/fetcher.py
import os
import pandas as pd
from typing import List, Dict, Any
import praw

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "reddit_keyword_tracker:v1.0")
DATA_DIR = os.getenv("DATA_DIR", "/app/data")

def reddit_instance():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise EnvironmentError("REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not set")
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        check_for_async=False
    )

def fetch_posts(subreddit: str, keyword: str, limit: int = 500) -> pd.DataFrame:
    reddit = reddit_instance()
    subreddit_obj = reddit.subreddit(subreddit)
    posts = []
    # Using .new() to fetch recent posts
    for submission in subreddit_obj.new(limit=limit):
        title = getattr(submission, "title", "") or ""
        selftext = getattr(submission, "selftext", "") or ""
        full_text = (title + " " + selftext).lower()
        if keyword.lower() in full_text:
            posts.append({
                "title": title,
                "selftext": selftext,
                "score": getattr(submission, "score", 0),
                "id": getattr(submission, "id", ""),
                "url": getattr(submission, "url", ""),
                "num_comments": getattr(submission, "num_comments", 0),
                "created_utc": getattr(submission, "created_utc", None)
            })
    df = pd.DataFrame(posts)
    # Save CSV
    csv_path = os.path.join(DATA_DIR, "reddit_data.csv")
    df.to_csv(csv_path, index=False)
    return df
