# Use lightweight but flexible Python base
FROM python:3.10-slim

# Environment setup
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_RETRIES=10

# Set working directory
WORKDIR /app

# Install required system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libsoxr-dev \
    libasound2 \
    libgl1 \
    build-essential \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y

# Copy application code
COPY . .

# Expose app port (adjust if needed)
EXPOSE 8080

# Default run command (adjust if needed)
CMD ["python", "main.py"]
