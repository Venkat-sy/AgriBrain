# ------------------------------------------------------------
# Dockerfile for AgriSim FastAPI backend
# ------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any are needed for pandas, geopandas, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends 
    build-essential 
    gcc 
    g++ 
    libgomp1 
    libatlas-base-dev 
    libproj-dev 
    proj-data 
    proj-bin 
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/ ./

# Copy model artifacts (they are ignored by .gitignore but needed at runtime)
COPY models/ ./models/
COPY ml/ ./ml/
COPY training_data/ ./training_data/

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
