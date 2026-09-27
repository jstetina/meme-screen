#!/bin/bash
# Setup script for meme-screen on Raspberry Pi

set -e

echo "=========================================="
echo "Meme Screen - Raspberry Pi Setup"
echo "=========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /sys/firmware/devicetree/base/model 2>/dev/null; then
    echo "[WARN] This script is designed for Raspberry Pi"
fi

# Update system
echo "[*] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "[*] Installing system dependencies..."
sudo apt-get install --no-install-recommends -y \
    xserver-xorg \
    x11-xserver-utils \
    xinit \
    openbox \
    python3 \
    python3-pip \
    python3-venv \
    podman \
    podman-compose \
    git

# Create necessary directories
echo "[*] Creating directories..."
mkdir -p ~/.config/openbox
mkdir -p ~/meme-screen/pictures

# Setup config file
echo "[*] Setting up configuration..."
if [ ! -f "config.env" ]; then
    cp config.env.example config.env
    echo "[DONE] Created config.env from template"
    echo "[INFO] Please edit config.env with your settings:"
    echo "   - GOOGLE_DRIVE_FOLDER_ID: Your Google Drive folder ID"
    echo "   - GOOGLE_CREDENTIALS_PATH: Path to your credentials.json"
fi

# Setup credentials
if [ ! -f "credentials.json" ]; then
    echo "[WARN] credentials.json not found!"
    echo "[INFO] Please follow these steps:"
    echo "   1. Go to Google Cloud Console: https://console.cloud.google.com"
    echo "   2. Create a new project or select existing one"
    echo "   3. Enable Google Drive API"
    echo "   4. Create a Service Account"
    echo "   5. Create a JSON key for the service account"
    echo "   6. Place the JSON key as 'credentials.json' in this directory"
    echo ""
fi

# Setup xinitrc for display
echo "[*] Setting up X11 configuration..."
cat > ~/.xinitrc << 'EOF'
#!/bin/sh

# Disable screen sleep/saver
xset s off
xset -dpms
xset s noblank

# Start Openbox
openbox-session &

# Launch meme-screen via Podman
exec podman-compose -f ~/meme-screen/podman-compose.yml up
EOF
chmod +x ~/.xinitrc

echo ""
echo "=========================================="
echo "[DONE] Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.env with your Google Drive folder ID and settings"
echo "2. Place your credentials.json in the meme-screen directory"
echo "3. Run: docker-compose build"
echo "4. Run: docker-compose up"
echo ""
echo "To start on boot, add to crontab:"
echo "   @reboot DISPLAY=:0 startx"
echo ""
