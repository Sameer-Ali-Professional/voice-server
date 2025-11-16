#!/bin/bash
# Build script for Railway deployment
# Downloads Piper TTS model files

set -e

echo "Downloading Piper TTS model..."

# Make sure models directory exists
mkdir -p models

# Download English model if not already present
MODEL_NAME="en_US-lessac-medium"
MODEL_ONNX="models/${MODEL_NAME}.onnx"
MODEL_JSON="models/${MODEL_NAME}.onnx.json"

if [ ! -f "$MODEL_ONNX" ]; then
    echo "Downloading Piper model: $MODEL_NAME"
    
    # Download model files from Hugging Face
    MODEL_BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium"
    
    echo "Downloading model ONNX file..."
    curl -L -o "$MODEL_ONNX" "${MODEL_BASE_URL}/${MODEL_NAME}.onnx"
    
    echo "Downloading model JSON file..."
    curl -L -o "$MODEL_JSON" "${MODEL_BASE_URL}/${MODEL_NAME}.onnx.json"
    
    echo "Model downloaded successfully!"
else
    echo "Model $MODEL_NAME already exists, skipping download."
fi

echo "Build complete! Piper binary is in ./bin/$PIPER_BIN"
echo "Model files are in ./models/"

