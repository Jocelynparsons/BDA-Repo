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

def top_words(texts: List[str], n: int = 15) -> List[Tuple[str, int]]:
    stop_words = set(stopwords.words('english'))
    counter = Counter()
    for text in texts:
        for word in text.split():
            if word not in stop_words and len(word) > 2:
                counter[word] += 1
    return counter.most_common(n)

def sentiment_score(texts: List[str]) -> float:
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(str(text))['compound'] for text in texts if str(text).strip() != ""]
    return sum(scores)/len(scores) if scores else 0.0

def analyze_and_save() -> Dict[str, Any]:
    if not os.path.exists(CSV_FILE):
        return {"error": "CSV not found", "fetched": 0, "analyzed": 0}

    df = pd.read_csv(CSV_FILE)
    # combine title + selftext
    df['text'] = df.get('title', '').fillna('') + ' ' + df.get('selftext', '').fillna('')
    df['text_clean'] = df['text'].apply(clean_text)

    texts = df['text_clean'].tolist()
    top = top_words(texts, 15)
    avg_sent = sentiment_score(texts)

    # Save top words chart
    if top:
        words, counts = zip(*top)
        plt.figure(figsize=(10,5))
        plt.bar(words, counts)
        plt.xticks(rotation=45)
        plt.title("Top Words in Subreddit")
        plt.tight_layout()
        top_words_path = os.path.join(DATA_DIR, "top_words.png")
        plt.savefig(top_words_path)
        plt.close()
    else:
        top_words_path = None

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
