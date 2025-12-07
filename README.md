# Reddit Collector & Analyzer (FastAPI + React + Docker)

## Setup
1. Copy backend/.env.example -> backend/.env and fill:
   - REDDIT_CLIENT_ID
   - REDDIT_CLIENT_SECRET
   - REDDIT_USER_AGENT (your reddit user agent string)

2. Build & start with docker-compose:
   docker-compose up --build

3. Open frontend:
   http://localhost:3000

4. Open backend docs (optional):
   http://localhost:8000/docs

## Where data is stored
- Data (reddit_data.csv, reddit_data_with_sentiment.csv, top_words.png, posts_by_date.png) is stored in a Docker volume `reddit_data` mounted at `/app/data` inside the backend container.

## Downloading files directly from backend
- Charts and CSV are available at:
  - http://localhost:8000/static/top_words.png
  - http://localhost:8000/static/posts_by_date.png
  - http://localhost:8000/static/reddit_data_with_sentiment.csv

## Important
- Rotate your Reddit credentials if they were exposed publicly.
