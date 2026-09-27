# meme-screen

Raspberry Pi slideshow that syncs images from a Google Drive folder and displays them fullscreen via feh and X11.

Two Podman containers run as user systemd services: one handles the slideshow, one handles periodic Drive sync.

## Requirements

- Raspberry Pi (3B+ or newer) running Raspberry Pi OS
- Podman
- A Google Cloud service account with Drive API access

## Setup

**One-time host setup** (installs X11 wrapper and enables linger):
```
make setup
```

**Credentials** — place in `~/meme-screen/`:
- `credentials.json` — Google service account JSON key
- `config.env` — copy from `config.env.example` and fill in your folder ID

**Build and start:**
```
make deploy
```

## Google Drive

1. Create a project in Google Cloud Console
2. Enable the Drive API
3. Create a service account and download its JSON key as `credentials.json`
4. Share your Drive folder with the service account email

## Configuration

See `config.env.example` for all options. Key variables:

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_DRIVE_FOLDER_ID` | — | ID of the Drive folder containing images |
| `SLIDESHOW_INTERVAL_SECONDS` | 10 | Seconds each image is shown |
| `DOWNLOAD_CHECK_INTERVAL_MINUTES` | 10 | How often to sync from Drive |

## Commands

```
make setup       # one-time host setup
make deploy      # build image and start services
make logs        # follow slideshow logs
make logs-sync   # follow sync logs
make shell       # shell in slideshow container
make clean       # stop services and remove image
```

## Structure

```
meme-screen/
├── src/
│   ├── sync.py          # Google Drive sync loop
│   └── entrypoint.sh    # slideshow entrypoint
├── quadlet/
│   ├── meme-screen.container
│   └── meme-screen-sync.container
├── Dockerfile
├── Makefile
├── requirements.txt
└── config.env.example
```
