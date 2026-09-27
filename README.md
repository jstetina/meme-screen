# Meme Screen

A Raspberry Pi application that displays a slideshow of images from a Google Drive folder using Xserver and OpenBox.

## Features

- 📸 Automatic slideshow of images from Google Drive
- 🔄 Periodic sync to download new images and remove deleted ones
- 🐳 Fully containerized with Docker and Docker Compose
- ⚙️ Highly configurable via environment variables
- 🔐 Secure credential management
- 📺 Optimized for Raspberry Pi with minimal dependencies

## System Requirements

- Raspberry Pi (3B+ or newer recommended)
- Raspberry Pi OS (Lite or Desktop)
- Docker and Docker Compose
- 2GB RAM minimum, 4GB recommended
- X11-compatible display (HDMI)

## Installation

### 1. Clone and Setup

```bash
git clone <repository-url> ~/meme-screen
cd ~/meme-screen
chmod +x setup.sh
./setup.sh
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the **Google Drive API**
4. Create a **Service Account**:
   - Go to "Service Accounts"
   - Create a new service account
   - Create a JSON key
5. Share your Google Drive folder with the service account email address
6. Save the JSON key as `credentials.json` in the project directory

### 3. Configuration

1. Copy configuration template:
   ```bash
   cp config.env.example config.env
   ```

2. Edit `config.env`:
   ```env
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
   SLIDESHOW_INTERVAL_SECONDS=10
   DOWNLOAD_CHECK_INTERVAL_MINUTES=30
   PICTURES_DIRECTORY=/tmp/meme-screen/pictures
   RESOLUTION_WIDTH=1920
   RESOLUTION_HEIGHT=1080
   ```

### 4. Build and Run

```bash
cd ~/meme-screen
podman-compose build
podman-compose up -d
```

## Configuration Options

### Google Drive
- `GOOGLE_DRIVE_FOLDER_ID`: ID of the folder containing your images
- `GOOGLE_CREDENTIALS_PATH`: Path to service account credentials JSON

### Slideshow
- `SLIDESHOW_INTERVAL_SECONDS`: How long each image displays (default: 10)
- `IMAGE_DISPLAY_TIMEOUT_SECONDS`: Max time to wait for image load (default: 15)

### Sync
- `DOWNLOAD_CHECK_INTERVAL_MINUTES`: How often to check for new images (default: 30)
- `PICTURES_DIRECTORY`: Local directory to store downloaded images

### Display
- `RESOLUTION_WIDTH`: Display width in pixels (default: 1920)
- `RESOLUTION_HEIGHT`: Display height in pixels (default: 1080)
- `DISPLAY_MONITOR`: Monitor output (default: HDMI-1)
- `DISPLAY`: X11 display (default: :0)

### Logging
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, ERROR)

## System Dependencies (if not using Docker)

If you prefer to run without Docker, install these packages on the Raspberry Pi:

```bash
sudo apt-get install --no-install-recommends \
    xserver-xorg \
    x11-xserver-utils \
    xinit \
    openbox \
    python3 \
    python3-pip \
    python3-venv
```

Then install Python dependencies:

```bash
pip3 install -r requirements.txt
```

## Running on Boot

To start the slideshow automatically on boot:

### Option 1: Using systemd (Recommended)

Create `/etc/systemd/system/meme-screen.service`:

```ini
[Unit]
Description=Meme Screen Slideshow
After=network.target podman.service
Wants=podman.service

[Service]
Type=simple
User=meme
WorkingDirectory=/home/meme/meme-screen
Environment="DISPLAY=:0"
ExecStart=/usr/bin/podman-compose up
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable meme-screen.service
sudo systemctl start meme-screen.service
```

### Option 2: Using xinit

Add to your `~/.bashrc` or login shell:

```bash
if [ -z "$DISPLAY" ] && [ "$XDG_VTNR" -eq 1 ]; then
    exec startx
fi
```

And ensure `~/.xinitrc` is configured to run the slideshow.

## Usage

### Start the slideshow

```bash
podman-compose up
```

### Stop the slideshow

```bash
podman-compose down
```

### View logs

```bash
podman-compose logs -f meme-screen
```

### Rebuild after code changes

```bash
podman-compose down
podman-compose build --no-cache
podman-compose up
```

## Keyboard Controls

- **ESC**: Exit slideshow
- **Ctrl+C**: Stop application (if running in foreground)

## Troubleshooting

### X11 Connection Error

If you see `cannot connect to X server :0`, ensure:
1. X server is running: `ps aux | grep X`
2. DISPLAY is set correctly: `echo $DISPLAY`
3. X server socket is accessible in Docker volume

### Images not downloading

Check logs for authentication errors:
```bash
podman-compose logs meme-screen
```

Verify:
- Service account has access to the Drive folder
- Credentials JSON is valid
- Folder ID is correct

### Slideshow stutters or lags

- Reduce `SLIDESHOW_INTERVAL_SECONDS`
- Reduce image resolution (convert to smaller sizes)
- Check Raspberry Pi temperature: `vcgencmd measure_temp`
- Ensure adequate power supply (5V 3A minimum)
- Monitor Podman resources: `podman stats`

## Architecture

```
meme-screen/
├── meme_screen.py         # Main application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Container orchestration
├── xinitrc                # X11 initialization script
├── config.env.example     # Configuration template
├── credentials.json       # Google service account (create this)
└── README.md
```

## Performance Tips

1. **Use SSD**: SD cards are slow; consider USB SSD or NFS
2. **Optimize images**: Pre-resize large images before uploading
3. **Reduce polling**: Increase `DOWNLOAD_CHECK_INTERVAL_MINUTES`
4. **Monitor resources**: Use `htop` or `docker stats`
5. **Enable GPU**: Use hardware acceleration if available

## License

MIT

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
