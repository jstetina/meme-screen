# Testing Meme Screen on Desktop

You can test the meme-screen application on a regular desktop (Linux with X11 or Wayland) without needing a Raspberry Pi.

## Prerequisites

1. **Python 3.8+** installed
2. **X11 or Wayland display server** (standard on most Linux desktops)
3. **Python dependencies** installed
4. **Google Drive credentials** set up
5. **Images in your Google Drive folder**

## Option 1: Direct Python Testing (Recommended)

### Setup

```bash
cd ~/meme-screen

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure
cp config.env.example config.env
# Edit config.env with your settings
nano config.env
```

### Test with test_desktop.py

Run individual tests:

```bash
# Show system diagnostics
python test_desktop.py --diagnostics

# Test Google Drive connection
python test_desktop.py --test-drive

# Download one sample image
python test_desktop.py --download-sample

# Test slideshow display
python test_desktop.py --test-slideshow

# Run full sync
python test_desktop.py --full-sync

# Run all tests
python test_desktop.py --all
```

### Run the Full App

```bash
python meme_screen.py
```

## Option 2: Docker Testing

If you want to test with Docker on desktop:

```bash
# Build the image
docker-compose build

# Run with display forwarding
docker-compose up
```

**Note**: On desktop Linux, Docker needs access to the X11 socket. The compose file already handles this via volume mounting.

## Troubleshooting

### "DISPLAY not set" Error

Your display server isn't available. Set it manually:

```bash
# Find your display
echo $DISPLAY

# If empty, try
export DISPLAY=:0

# Or for Wayland
export DISPLAY=:1
```

### "cannot connect to X server" Error

```bash
# Check if X server is running
ps aux | grep X

# Check X server socket
ls -la /tmp/.X11-unix/

# If you don't have X11, you can use Xvfb (virtual X server)
sudo apt install xvfb
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

### Module Import Errors

Make sure virtual environment is activated:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Google Drive Connection Issues

1. Verify credentials.json exists in project directory
2. Check config.env has correct GOOGLE_DRIVE_FOLDER_ID
3. Ensure service account has access to the shared folder:
   ```bash
   # Get service account email from credentials.json
   cat credentials.json | grep client_email
   
   # Share your Drive folder with that email
   ```

## Testing Workflow

### 1. Test Authentication
```bash
python test_desktop.py --test-drive
```

### 2. Download Sample Images
```bash
python test_desktop.py --download-sample
```

### 3. Test Slideshow
```bash
python test_desktop.py --test-slideshow
```

### 4. Test Full Application
```bash
python meme_screen.py
```

## Running Without X11 (Headless)

If you don't have a display but want to test the sync logic:

```python
from meme_screen import MemeScreen

app = MemeScreen()
app.sync_files_from_drive()
print(f"Downloaded {len(list(app.pictures_dir.glob('*')))} images")
```

## Performance Notes

On desktop, you might want to:

1. **Reduce image interval for testing**:
   ```bash
   SLIDESHOW_INTERVAL_SECONDS=3 python meme_screen.py
   ```

2. **Lower resolution for faster rendering**:
   ```bash
   RESOLUTION_WIDTH=1280 RESOLUTION_HEIGHT=720 python meme_screen.py
   ```

3. **Disable automatic syncing** during testing:
   - Modify `MemeScreen.__init__()` to not start the sync thread

## Testing with Multiple Monitors

Set resolution to match one monitor:

```bash
# Get monitor info
xrandr

# Run with specific resolution
RESOLUTION_WIDTH=2560 RESOLUTION_HEIGHT=1440 python meme_screen.py
```

## Debugging

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python meme_screen.py
```

Or in test script:

```bash
LOG_LEVEL=DEBUG python test_desktop.py --all
```

## Continuous Testing

Run the full app and watch logs:

```bash
python meme_screen.py 2>&1 | tee meme-screen.log
```

Monitor sync in real-time:

```bash
# In another terminal
tail -f meme-screen.log | grep "Sync"
```

## Integration Testing

To test the actual Pi setup before deploying:

```bash
# Build Docker image (test arm32v7 image)
docker build -f Dockerfile -t meme-screen:test .

# Run it with display forwarding
docker run -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/config.env:/app/.env:ro \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  meme-screen:test
```

## Next Steps

After successful desktop testing:

1. Copy project to Raspberry Pi
2. Run setup.sh on Pi
3. Test with Docker on Pi
4. Set up systemd service or cron for auto-start
