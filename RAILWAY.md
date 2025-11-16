# Railway Deployment Guide

This guide explains how to deploy the Piper TTS Server to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. Railway CLI installed (optional, for local testing)

## Deployment Steps

### Option 1: Deploy via Railway Dashboard

1. **Create a New Project**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo" or "Empty Project"

2. **Connect Your Repository**
   - If using GitHub: Connect your repository and select the `voice-server` directory as the root
   - If using Empty Project: Upload the `voice-server` folder

3. **Configure Environment Variables**
   - Go to your project settings
   - Add these environment variables (optional):
     - `PIPER_BINARY`: Path to piper binary (auto-detected if not set)
     - `PIPER_MODELS_DIR`: Models directory (default: `./models`)
     - `PIPER_DEFAULT_MODEL`: Default model name (default: `en_US-lessac-medium`)
     - `PORT`: Automatically set by Railway (don't override)

4. **Deploy**
   - Railway will automatically detect the Python project
   - It will run the build script to download Piper binary
   - The server will start using the `Procfile` or `railway.toml` configuration

### Option 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Link to existing project (optional)
railway link

# Deploy
railway up
```

## Important Notes

### Model Files

The model files (`en_US-lessac-medium.onnx` and `.onnx.json`) are already included in the repository. Railway will include them in the deployment. However, if you need to add more models:

1. Download model files to `voice-server/models/`
2. Commit and push to your repository
3. Railway will include them in the next deployment

**Note**: Model files are large (~60MB each). Railway has storage limits, so be mindful of how many models you include.

### Piper Binary

The build script (`build.sh`) automatically downloads the appropriate Piper binary for your Railway instance's architecture during the build phase. This happens automatically when Railway builds your project.

### CORS Configuration

The server is configured to allow CORS from any origin. In production, you should update the `allow_origins` in `server.py` to only allow your Next.js app's domain:

```python
allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
```

### Health Check

Railway will use the `/` endpoint as a health check. This endpoint returns the server status and whether Piper and models are available.

## Testing the Deployment

Once deployed, Railway will provide you with a URL (e.g., `https://your-app.railway.app`). Test the endpoints:

1. **Health Check**: `GET https://your-app.railway.app/`
2. **List Models**: `GET https://your-app.railway.app/models`
3. **Generate Speech**: `POST https://your-app.railway.app/speak`

Example with curl:
```bash
curl -X POST https://your-app.railway.app/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Railway!"}' \
  --output speech.wav
```

## Troubleshooting

### Build Fails

- Check Railway build logs for errors
- Ensure `build.sh` has execute permissions (it should be set automatically)
- Verify Python version in `runtime.txt` is supported

### Piper Binary Not Found

- Check build logs to see if `build.sh` ran successfully
- Verify the architecture matches available Piper binaries
- You can manually set `PIPER_BINARY` environment variable to a specific path

### Model Not Found

- Verify model files are in the `models/` directory
- Check that model names match exactly (case-sensitive)
- Review the `/models` endpoint to see what models are available

### CORS Errors

- Update `allow_origins` in `server.py` to include your frontend domain
- Ensure your frontend is making requests to the correct Railway URL

## Updating Your Next.js App

To use the Railway-deployed server, update your Next.js app's `/api/speak/route.ts`:

```typescript
const response = await fetch("https://your-app.railway.app/speak", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text }),
});
```

Or use an environment variable:
```typescript
const VOICE_SERVER_URL = process.env.VOICE_SERVER_URL || "http://localhost:8000";

const response = await fetch(`${VOICE_SERVER_URL}/speak`, {
  // ...
});
```

Then add `VOICE_SERVER_URL=https://your-app.railway.app` to your Next.js `.env.local`.

