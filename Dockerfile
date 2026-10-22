FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for OpenCV)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings sqlalchemy psycopg2-binary python-multipart scikit-learn numpy opencv-python reportlab requests

# Copy backend code
COPY backend/ ./backend/
COPY models/ ./models/
COPY data/ ./data/

# Create uploads directory
RUN mkdir -p uploads/audio

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
