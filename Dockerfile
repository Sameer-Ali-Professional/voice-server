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

# Download Piper binary based on architecture
RUN mkdir -p /app/bin && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then \
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    cd /app/bin && \
    curl -L -o piper.tar.gz "$PIPER_URL" && \
    tar -xzf piper.tar.gz && \
    rm piper.tar.gz && \
    chmod +x /app/bin/piper

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

# Download model files during build
RUN ./build.sh

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Health check (uses default port, Railway will override PORT env var)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the server
CMD ["python", "server.py"]

