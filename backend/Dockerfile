FROM python:3.11-slim

# system deps for matplotlib fonts etc.
RUN apt-get update && apt-get install -y build-essential libpq-dev libfreetype6-dev \
    libjpeg-dev libpng-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy only requirements first for caching
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app code
COPY app /app

# create data dir where CSV & charts will be stored (mounted as volume)
RUN mkdir -p /app/data
ENV DATA_DIR=/app/data

# Ensure NLTK stopwords are available at build time
RUN python -c "import nltk; nltk.download('stopwords', quiet=True)"

# expose
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
