"""
Piper TTS Server
A FastAPI server that exposes a /speak endpoint for text-to-speech using Piper TTS.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
import shutil
from pathlib import Path
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Piper TTS Server", version="1.0.0")

# Add CORS middleware for Railway deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PIPER_BINARY = os.getenv("PIPER_BINARY", "piper")
MODELS_DIR = Path(os.getenv("PIPER_MODELS_DIR", "./models"))
DEFAULT_MODEL = os.getenv("PIPER_DEFAULT_MODEL", "en_US-lessac-medium")
DEFAULT_VOICE = os.getenv("PIPER_DEFAULT_VOICE", "en_US-lessac-medium")

# Global model cache
loaded_model: Optional[str] = None

# Path to copied piper binary in /tmp
TMP_PIPER_PATH = "/tmp/piper"


@app.on_event("startup")
async def startup_event():
    """Copy piper binary to /tmp and make it executable at startup.
    This must complete before any TTS operations can run."""
    source_path = Path("/app/bin/piper")
    dest_path = Path(TMP_PIPER_PATH)
    
    try:
        if source_path.exists():
            logger.info(f"Copying piper from {source_path} to {dest_path}")
            shutil.copy2(source_path, dest_path)
            os.chmod(dest_path, 0o755)  # Make executable (rwxr-xr-x)
            
            # Verify the copy was successful
            if not dest_path.exists() or not os.access(dest_path, os.X_OK):
                raise RuntimeError(f"Failed to verify copied binary at {dest_path}")
            
            logger.info(f"Piper binary successfully copied to {dest_path} and made executable")
        else:
            logger.warning(f"Source piper binary not found at {source_path}, skipping copy")
    except Exception as e:
        logger.error(f"Failed to copy piper binary: {e}")
        raise  # Re-raise to prevent server from starting without piper


class SpeakRequest(BaseModel):
    text: str
    model: Optional[str] = None
    voice: Optional[str] = None
    length_scale: Optional[float] = 1.0
    noise_scale: Optional[float] = 0.667
    noise_w: Optional[float] = 0.8


def find_piper_binary() -> Optional[str]:
    """Find the piper binary in PATH or common locations."""
    # Check /tmp/piper first (copied at startup)
    if os.path.exists(TMP_PIPER_PATH) and os.access(TMP_PIPER_PATH, os.X_OK):
        return TMP_PIPER_PATH
    
    # Check environment variable (for Railway)
    if PIPER_BINARY and PIPER_BINARY != "piper":
        if os.path.exists(PIPER_BINARY) and os.access(PIPER_BINARY, os.X_OK):
            return PIPER_BINARY
    
    # Check /app/bin/piper as fallback (should be copied to /tmp at startup)
    app_bin_path = Path("/app/bin/piper")
    if app_bin_path.exists() and os.access(app_bin_path, os.X_OK):
        logger.warning(f"/tmp/piper not found, falling back to {app_bin_path}. Copy may have failed at startup.")
        return str(app_bin_path)
    
    # Check local bin directory (for local development)
    local_bin = Path(__file__).parent / "bin" / "piper"
    if local_bin.exists() and os.access(local_bin, os.X_OK):
        return str(local_bin)
    
    # Check if piper is in PATH
    try:
        result = subprocess.run(
            ["which", "piper"] if os.name != "nt" else ["where", "piper"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    # Check common installation paths
    common_paths = [
        "/usr/local/bin/piper",
        "/usr/bin/piper",
        "C:\\piper\\piper.exe",
        os.path.expanduser("~/.local/bin/piper"),
    ]
    
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None


def find_model_path(model_name: str) -> Optional[Path]:
    """Find the model file path."""
    # Try different possible extensions and locations
    possible_paths = [
        MODELS_DIR / f"{model_name}.onnx",
        MODELS_DIR / f"{model_name}" / f"{model_name}.onnx",
        MODELS_DIR / model_name,
        Path(model_name),  # Absolute path
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def generate_speech(
    text: str,
    model_name: Optional[str] = None,
    voice_name: Optional[str] = None,
    length_scale: float = 1.0,
    noise_scale: float = 0.667,
    noise_w: float = 0.8
) -> bytes:
    """
    Generate speech audio using Piper TTS.
    
    Args:
        text: Text to convert to speech
        model_name: Name of the Piper model to use
        voice_name: Voice name (can be same as model_name)
        length_scale: Speed of speech (1.0 = normal, >1.0 = slower, <1.0 = faster)
        noise_scale: Controls variation in speech
        noise_w: Controls variation in speech
    
    Returns:
        WAV audio data as bytes
    """
    # Find piper binary
    piper_path = find_piper_binary()
    if not piper_path:
        raise HTTPException(
            status_code=500,
            detail="Piper binary not found. Please install Piper TTS or set PIPER_BINARY environment variable."
        )
    
    # Determine model to use
    model = model_name or voice_name or DEFAULT_MODEL
    model_path = find_model_path(model)
    
    if not model_path:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model}' not found. Please ensure the model is downloaded and placed in {MODELS_DIR}"
        )
    
    logger.info(f"Generating speech with model: {model_path}")
    
    try:
        # Build piper command
        cmd = [
            piper_path,
            "--model", str(model_path),
            "--output_file", "-",  # Output to stdout
            "--length_scale", str(length_scale),
            "--noise_scale", str(noise_scale),
            "--noise_w", str(noise_w),
        ]
        
        # Run piper and pipe text to it
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        stdout, stderr = process.communicate(input=text.encode("utf-8"))
        
        if process.returncode != 0:
            error_msg = stderr.decode("utf-8") if stderr else "Unknown error"
            logger.error(f"Piper error: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Piper TTS failed: {error_msg}"
            )
        
        return stdout
    
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Piper TTS process timed out"
        )
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )


@app.get("/")
async def root():
    """Health check endpoint."""
    piper_path = find_piper_binary()
    model_status = "not found"
    
    if find_model_path(DEFAULT_MODEL):
        model_status = "available"
    
    return {
        "status": "running",
        "piper_binary": piper_path is not None,
        "default_model": DEFAULT_MODEL,
        "model_status": model_status,
        "models_dir": str(MODELS_DIR),
    }


@app.get("/models")
async def list_models():
    """List available models in the models directory."""
    models = []
    
    if not MODELS_DIR.exists():
        return {"models": [], "message": f"Models directory {MODELS_DIR} does not exist"}
    
    # Look for .onnx files
    for path in MODELS_DIR.rglob("*.onnx"):
        model_name = path.stem
        models.append({
            "name": model_name,
            "path": str(path),
            "size": path.stat().st_size if path.exists() else 0,
        })
    
    return {"models": models}


@app.post("/speak")
async def speak(request: SpeakRequest):
    """
    Convert text to speech using Piper TTS.
    
    Request body:
    - text: Text to convert (required)
    - model: Model name (optional, uses default if not provided)
    - voice: Voice name (optional, uses model if not provided)
    - length_scale: Speech speed (optional, default: 1.0)
    - noise_scale: Variation control (optional, default: 0.667)
    - noise_w: Variation control (optional, default: 0.8)
    
    Returns:
    - WAV audio stream
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        audio_data = generate_speech(
            text=request.text,
            model_name=request.model,
            voice_name=request.voice,
            length_scale=request.length_scale,
            noise_scale=request.noise_scale,
            noise_w=request.noise_w,
        )
        
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "Content-Length": str(len(audio_data)),
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /speak: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Piper TTS Server on {host}:{port}")
    logger.info(f"Models directory: {MODELS_DIR}")
    logger.info(f"Default model: {DEFAULT_MODEL}")
    
    uvicorn.run(app, host=host, port=port)

