FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmagic1 \
    gcc \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . /app/worker/

# Create directories
RUN mkdir -p /app/uploads /app/media

CMD ["celery", "-A", "worker.app", "worker", "-l", "info", "-Q", "video_processing,transcription,ai_analysis,maintenance", "-c", "2"]
