# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for scientific packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
# Doing this before copying the rest of the code leverages Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variable to recognize the Python path for imports
ENV PYTHONPATH=/app

# By default, run the FastAPI inference server
CMD ["uvicorn", "inference.main:app", "--host", "0.0.0.0", "--port", "8000"]
