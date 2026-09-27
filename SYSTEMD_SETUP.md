# Systemd Setup with Podman Quadlet

This sets up automatic X11 and meme-screen startup on boot using systemd and Podman Quadlet.

## Installation

### 1. Create Quadlet Directory

```bash
mkdir -p ~/.config/containers/systemd
```

### 2. Copy Files

```bash
cp ~/meme-screen/meme-screen.container ~/.config/containers/systemd/
cp ~/meme-screen/meme-screen-xserver.service ~/.config/systemd/user/
```

### 3. Generate Systemd Units from Quadlet

```bash
podman-compose up -d --build
podman quadlet -dryrun
```

Or let systemd auto-generate them:

```bash
systemctl --user daemon-reload
```

### 4. Enable and Start

```bash
# Enable X server service
systemctl --user enable meme-screen-xserver.service

# Enable container service (generated from quadlet)
systemctl --user enable meme-screen.service

# Start everything
systemctl --user start meme-screen-xserver.service
systemctl --user start meme-screen.service
```

### 5. Check Status

```bash
systemctl --user status meme-screen-xserver.service
systemctl --user status meme-screen.service
journalctl --user -u meme-screen -f
```

## Auto-start on Boot

To auto-start when the system boots (not just when the user logs in), you need to enable user services to start at boot:

```bash
sudo loginctl enable-linger kuba
```

## Troubleshooting

### Services don't start

Check logs:
```bash
journalctl --user -u meme-screen -f
journalctl --user -u meme-screen-xserver -f
```

### X11 not connecting

Make sure:
1. Display is connected to HDMI
2. .Xauthority exists: `ls -la ~/.Xauthority`
3. /tmp/.X11-unix socket exists after X starts: `ls -la /tmp/.X11-unix`

### Manual Testing

Before enabling on boot, test manually:

```bash
# Terminal 1: Start X server
systemctl --user start meme-screen-xserver.service

# Terminal 2: Wait a few seconds, then start container
sleep 5
systemctl --user start meme-screen.service

# Watch logs
journalctl --user -u meme-screen -f
```

## Files

- `meme-screen.container` - Podman Quadlet definition for container
- `meme-screen-xserver.service` - Systemd service for X11 startup

## Notes

- Uses Podman Quadlet for declarative container management
- X server starts first, then container depends on it
- Logs accessible via journalctl
- Restart policy handles failures
- User-scoped services (can run without root)
