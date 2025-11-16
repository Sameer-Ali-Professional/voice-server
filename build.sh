#!/bin/bash
# Build script for Railway deployment
# Downloads Piper TTS binary and sets it up

set -e

echo "Building Piper TTS Server for Railway..."

# Create bin directory for Piper binary
mkdir -p bin

# Detect architecture
ARCH=$(uname -m)
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

echo "Detected OS: $OS, Architecture: $ARCH"

# Download Piper binary based on architecture
if [ "$OS" = "linux" ]; then
    if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"
        PIPER_BIN="piper"
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz"
        PIPER_BIN="piper"
    else
        echo "Unsupported architecture: $ARCH"
        exit 1
    fi
else
    echo "Unsupported OS: $OS"
    exit 1
fi

echo "Downloading Piper from: $PIPER_URL"

# Download and extract Piper
cd bin
curl -L -o piper.tar.gz "$PIPER_URL"
tar -xzf piper.tar.gz
chmod +x "$PIPER_BIN"
rm piper.tar.gz
cd ..

# Make sure models directory exists
mkdir -p models

echo "Build complete! Piper binary is in ./bin/$PIPER_BIN"

