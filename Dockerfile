# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set work directory
WORKDIR /app

# Copy application
COPY ./ragoo ./ragoo

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "ragoo.main:app", "--host", "0.0.0.0", "--port", "8000"]