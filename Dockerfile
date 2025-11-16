# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY build.sh .

# Make build script executable
RUN chmod +x build.sh

# Download Piper binary and model during build
RUN ./build.sh

# Ensure Piper binary is executable
RUN chmod +x /app/bin/piper

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Health check (uses default port, Railway will override PORT env var)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the server
CMD ["python", "server.py"]

