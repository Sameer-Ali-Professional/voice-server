# Railway Deployment Checklist

## Pre-Deployment

- [x] Python dependencies listed in `requirements.txt`
- [x] `Procfile` created for Railway
- [x] `runtime.txt` specifies Python version
- [x] CORS middleware added to server
- [x] Build script (`build.sh`) created for Piper binary download
- [x] Model files in `models/` directory
- [x] Server configured to use `$PORT` environment variable
- [x] Health check endpoint (`/`) available

## Files Created/Updated

### Configuration Files
- ✅ `Procfile` - Railway start command
- ✅ `runtime.txt` - Python version specification
- ✅ `railway.toml` - Railway-specific configuration
- ✅ `nixpacks.toml` - Nixpacks build configuration
- ✅ `.dockerignore` - Files to exclude from build
- ✅ `.gitignore` - Updated to exclude build artifacts

### Server Updates
- ✅ `server.py` - Added CORS middleware, improved binary detection
- ✅ `requirements.txt` - Added `requests` for build script

### Build & Documentation
- ✅ `build.sh` - Downloads Piper binary during Railway build
- ✅ `RAILWAY.md` - Complete deployment guide
- ✅ `DEPLOYMENT_CHECKLIST.md` - This file

## Railway Deployment Steps

1. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Create new project
   - Connect GitHub repo or upload `voice-server` folder

2. **Configure Environment Variables** (Optional)
   - `PIPER_BINARY`: Auto-detected, no need to set
   - `PIPER_MODELS_DIR`: Default `./models` (no need to change)
   - `PIPER_DEFAULT_MODEL`: Default `en_US-lessac-medium` (no need to change)
   - `PORT`: Automatically set by Railway (don't override)

3. **Deploy**
   - Railway will auto-detect Python project
   - Build script will download Piper binary
   - Server will start on Railway's assigned port

4. **Verify Deployment**
   - Check health: `GET https://your-app.railway.app/`
   - List models: `GET https://your-app.railway.app/models`
   - Test TTS: `POST https://your-app.railway.app/speak`

## Post-Deployment

- [ ] Update CORS `allow_origins` in `server.py` with your production domain
- [ ] Test the `/speak` endpoint from your Next.js app
- [ ] Monitor Railway logs for any errors
- [ ] Set up Railway domain (optional)
- [ ] Configure environment variable in Next.js app: `VOICE_SERVER_URL`

## Troubleshooting

If deployment fails:
1. Check Railway build logs
2. Verify `build.sh` has execute permissions
3. Ensure model files are committed to repository
4. Check Python version compatibility

If Piper binary not found:
1. Review build logs for `build.sh` execution
2. Verify architecture matches available binaries
3. Check `bin/` directory exists after build

If models not found:
1. Verify `models/` directory is committed
2. Check model file names match exactly
3. Use `/models` endpoint to list available models

