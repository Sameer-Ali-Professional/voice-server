# Piper TTS Server

A FastAPI server that exposes a `/speak` endpoint for text-to-speech using [Piper TTS](https://github.com/rhasspy/piper).

## Features

- Fast, local neural text-to-speech
- RESTful API with `/speak` endpoint
- Support for multiple Piper models
- Configurable speech parameters (speed, variation)
- Streaming audio response

## Prerequisites

1. **Python 3.8+**
2. **Piper TTS binary** - Download from [Piper releases](https://github.com/rhasspy/piper/releases)
   - For Linux: `piper` binary
   - For Windows: `piper.exe`
   - For macOS: `piper` binary
3. **Piper voice models** - Download from [Piper voices](https://huggingface.co/rhasspy/piper-voices)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Piper TTS:
   - Download the appropriate binary for your OS from the [releases page](https://github.com/rhasspy/piper/releases)
   - Make it executable and place it in your PATH, or set the `PIPER_BINARY` environment variable

3. Download voice models:
   - Visit [Piper voices on Hugging Face](https://huggingface.co/rhasspy/piper-voices)
   - Download a model (e.g., `en_US-lessac-medium.onnx` and `en_US-lessac-medium.onnx.json`)
   - Place them in the `./models` directory (or set `PIPER_MODELS_DIR`)

## Configuration

Set environment variables (optional):

- `PIPER_BINARY`: Path to piper binary (default: looks in PATH)
- `PIPER_MODELS_DIR`: Directory containing model files (default: `./models`)
- `PIPER_DEFAULT_MODEL`: Default model name (default: `en_US-lessac-medium`)
- `PORT`: Server port (default: `8000`)
- `HOST`: Server host (default: `0.0.0.0`)

## Usage

### Start the server:

```bash
python server.py
```

Or with uvicorn directly:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### `GET /`
Health check and server status.

#### `GET /models`
List available models in the models directory.

#### `POST /speak`
Convert text to speech.

**Request body:**
```json
{
  "text": "Hello, this is a test.",
  "model": "en_US-lessac-medium",  // optional
  "voice": "en_US-lessac-medium",   // optional
  "length_scale": 1.0,               // optional, speech speed
  "noise_scale": 0.667,              // optional
  "noise_w": 0.8                     // optional
}
```

**Response:**
- Content-Type: `audio/wav`
- Streaming WAV audio data

**Example with curl:**
```bash
curl -X POST http://localhost:8000/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}' \
  --output speech.wav
```

**Example with Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/speak",
    json={"text": "Hello, world!"}
)

with open("speech.wav", "wb") as f:
    f.write(response.content)
```

## Model Download Example

To download a model manually:

```bash
# Create models directory
mkdir -p models

# Download model files (example for English US Lessac medium)
curl -L https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx -o models/en_US-lessac-medium.onnx
curl -L https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json -o models/en_US-lessac-medium.onnx.json
```

Or use the [piper-download](https://github.com/rhasspy/piper/blob/master/scripts/download-voices.sh) script.

## Integration with Next.js

To use this server with your Next.js app, update `app/api/speak/route.ts` to proxy requests to this server:

```typescript
const response = await fetch("http://localhost:8000/speak", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text }),
});

return new NextResponse(response.body, {
  headers: {
    "Content-Type": "audio/wav",
  },
});
```

## Troubleshooting

- **"Piper binary not found"**: Ensure piper is in your PATH or set `PIPER_BINARY`
- **"Model not found"**: Check that model files are in the `models` directory and match the model name
- **Audio quality issues**: Try adjusting `length_scale`, `noise_scale`, and `noise_w` parameters
- **Port already in use**: Change the port with `PORT=8001 python server.py`

