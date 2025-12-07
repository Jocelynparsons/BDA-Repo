# backend/app/analyzer.py
import os
import re
from collections import Counter
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.corpus import stopwords
from typing import Tuple, List, Dict, Any

DATA_DIR = os.getenv("DATA_DIR", "/app/data")
CSV_FILE = os.path.join(DATA_DIR, "reddit_data.csv")

# Ensure stopwords downloaded (if not present)
try:
    _ = stopwords.words('english')
except Exception:
    nltk.download('stopwords', quiet=True)

def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# --- MAP REDUCE IMPLEMENTATION START ---
def mapper(text: str) -> List[Tuple[str, int]]:
    stop_words = set(stopwords.words('english'))
    words = []
    for word in text.split():
        if word not in stop_words and len(word) > 2:
            words.append((word, 1)) 
    return words

def reducer(mapped_data: List[Tuple[str, int]]) -> Dict[str, int]:
    counts = {}
    for word, count in mapped_data:
        counts[word] = counts.get(word, 0) + count
    return counts

def map_reduce_top_words(texts: List[str], n: int = 15) -> List[Tuple[str, int]]:
    mapped_data = []
    for text in texts:
        mapped_data.extend(mapper(text))
    word_counts = reducer(mapped_data)
    sorted_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
    return sorted_words[:n]
# --- MAP REDUCE IMPLEMENTATION END ---

def sentiment_score(texts: List[str]) -> float:
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(str(text))['compound'] for text in texts if str(text).strip() != ""]
    return sum(scores)/len(scores) if scores else 0.0

def analyze_and_save() -> Dict[str, Any]:
    if not os.path.exists(CSV_FILE):
        return {"error": "CSV not found", "fetched": 0, "analyzed": 0}

    # --- FIX: Handle Empty CSV ---
    try:
        df = pd.read_csv(CSV_FILE)
        if df.empty or 'title' not in df.columns:
            return {"error": "No matching posts found to analyze", "fetched": 0, "analyzed": 0}
    except Exception:
        return {"error": "No data found (CSV empty)", "fetched": 0, "analyzed": 0}
    # -----------------------------

    # combine title + selftext
    df['text'] = df.get('title', '').fillna('') + ' ' + df.get('selftext', '').fillna('')
    df['text_clean'] = df['text'].apply(clean_text)

    texts = df['text_clean'].tolist()
    
    top = map_reduce_top_words(texts, 15)
    avg_sent = sentiment_score(texts)

    # Save top words chart
    top_words_path = None
    if top:
        words, counts = zip(*top)
        plt.figure(figsize=(10,5))
        plt.bar(words, counts)
        plt.xticks(rotation=45)
        plt.title("Top Words in Subreddit (via MapReduce)")
        plt.tight_layout()
        top_words_path = os.path.join(DATA_DIR, "top_words.png")
        plt.savefig(top_words_path)
        plt.close()

    # Posts over time (if created_utc exists)
    posts_by_date_path = None
    if 'created_utc' in df.columns and df['created_utc'].notnull().any():
        df['date_only'] = pd.to_datetime(df['created_utc'], unit='s').dt.date
        counts_by_date = df.groupby('date_only').size()
        plt.figure(figsize=(10,4))
        counts_by_date.plot(kind='bar')
        plt.title("Number of Posts by Date")
        plt.tight_layout()
        posts_by_date_path = os.path.join(DATA_DIR, "posts_by_date.png")
        plt.savefig(posts_by_date_path)
        plt.close()

    # Save sentiment per post CSV
    analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df['text_clean'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    sentiment_csv_path = os.path.join(DATA_DIR, "reddit_data_with_sentiment.csv")
    df.to_csv(sentiment_csv_path, index=False)

    result = {
        "fetched": len(df),
        "analyzed": len(df),
        "avg_sentiment": round(avg_sent, 4),
        "top_words": top,
        "top_words_chart": "top_words.png" if top_words_path else None,
        "posts_by_date_chart": "posts_by_date.png" if posts_by_date_path else None,
        "sentiment_csv": "reddit_data_with_sentiment.csv"
    }
    return result