#!/usr/bin/env python3

import os
import sys
import time
import logging
import threading
import subprocess
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import GoogleAPIError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoogleDriveManager:
    """Manages interactions with Google Drive API."""

    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive using service account credentials."""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Successfully authenticated with Google Drive")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive: {e}")
            raise

    def get_files_in_folder(self, folder_id: str) -> List[dict]:
        """
        Retrieve all image files from a Google Drive folder.
        Returns list of dicts with 'id', 'name', and 'mimeType'.
        """
        try:
            query = (
                f"'{folder_id}' in parents and trashed=false and "
                "(mimeType='image/jpeg' or mimeType='image/png' or "
                "mimeType='image/gif' or mimeType='image/webp')"
            )
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime)',
                pageSize=100
            ).execute()
            files = results.get('files', [])
            logger.info(f"Found {len(files)} image files in Google Drive folder")
            return files
        except GoogleAPIError as e:
            logger.error(f"Error querying Google Drive: {e}")
            return []

    def download_file(self, file_id: str, filename: str, destination: Path) -> bool:
        """Download a file from Google Drive to local disk."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_path = destination / filename

            with open(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()

            logger.info(f"Downloaded: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            return False


class SlideShowManager:
    """Manages the slideshow display using feh."""

    def __init__(self, pictures_dir: Path, interval: int):
        self.pictures_dir = pictures_dir
        self.interval = interval
        self.running = True
        self._feh_proc = None

    def get_image_files(self) -> List[Path]:
        """Get sorted list of image files in the pictures directory."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        images = sorted(
            f for f in self.pictures_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        )
        logger.info(f"Found {len(images)} images to display")
        return images

    def _launch_feh(self, images: List[Path]):
        """Kill any existing feh and start a new slideshow."""
        if self._feh_proc and self._feh_proc.poll() is None:
            self._feh_proc.terminate()
            try:
                self._feh_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._feh_proc.kill()

        cmd = [
            'feh',
            '--fullscreen',
            '--auto-zoom',
            '--hide-pointer',
            '--slideshow-delay', str(self.interval),
            '--quiet',
        ] + [str(f) for f in images]

        self._feh_proc = subprocess.Popen(cmd)
        logger.info(f"feh started with {len(images)} images (PID {self._feh_proc.pid})")

    def start(self):
        """Start the slideshow, blocking until stop() is called."""
        images = self.get_image_files()
        if images:
            self._launch_feh(images)
        else:
            logger.warning("No images yet; will retry")

        logger.info("Slideshow started")

        while self.running:
            time.sleep(1)
            if self._feh_proc and self._feh_proc.poll() is not None:
                logger.warning(f"feh exited (code {self._feh_proc.returncode}), restarting")
                images = self.get_image_files()
                if images:
                    self._launch_feh(images)

    def refresh(self):
        """Restart feh with the current image list (call after a sync)."""
        images = self.get_image_files()
        if images:
            self._launch_feh(images)

    def stop(self):
        """Stop the slideshow."""
        self.running = False
        if self._feh_proc and self._feh_proc.poll() is None:
            self._feh_proc.terminate()
        logger.info("Slideshow stopped")


class MemeScreen:
    """Main application orchestrating Google Drive sync and slideshow."""

    def __init__(self):
        load_dotenv()

        self.google_creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        self.slideshow_interval = int(os.getenv('SLIDESHOW_INTERVAL_SECONDS', '10'))
        self.download_interval = int(os.getenv('DOWNLOAD_CHECK_INTERVAL_MINUTES', '10'))
        self.pictures_dir = Path(os.getenv('PICTURES_DIRECTORY', '/tmp/meme-screen/pictures'))

        log_level = os.getenv('LOG_LEVEL', 'INFO')
        logger.setLevel(log_level)

        self.pictures_dir.mkdir(parents=True, exist_ok=True)

        self.drive_manager = GoogleDriveManager(self.google_creds_path)
        self.slideshow_manager = SlideShowManager(self.pictures_dir, self.slideshow_interval)

    def sync_files_from_drive(self):
        """Download new files from Google Drive and clean up deleted ones."""
        logger.info("Starting sync with Google Drive...")

        try:
            remote_files = self.drive_manager.get_files_in_folder(self.drive_folder_id)
            remote_file_names = {f['name']: f['id'] for f in remote_files}

            # Download new or updated files
            for filename, file_id in remote_file_names.items():
                file_path = self.pictures_dir / filename

                if not file_path.exists():
                    self.drive_manager.download_file(file_id, filename, self.pictures_dir)

            # Delete files that were removed from remote
            remote_names = set(remote_file_names.keys())
            local_names = {f.name for f in self.pictures_dir.iterdir() if f.is_file()}
            files_to_delete = local_names - remote_names

            for filename in files_to_delete:
                try:
                    (self.pictures_dir / filename).unlink()
                    logger.info(f"Deleted local file no longer in remote: {filename}")
                except Exception as e:
                    logger.error(f"Failed to delete {filename}: {e}")

            logger.info("Sync completed successfully")

        except Exception as e:
            logger.error(f"Sync failed: {e}")

    def periodic_sync(self):
        """Periodically sync files from Google Drive and refresh display."""
        while True:
            time.sleep(self.download_interval * 60)
            self.sync_files_from_drive()
            self.slideshow_manager.refresh()

    def run(self):
        """Run the main application."""
        logger.info("Starting Meme Screen application")

        # Initial sync
        self.sync_files_from_drive()

        # Start background sync thread
        sync_thread = threading.Thread(target=self.periodic_sync, daemon=True)
        sync_thread.start()

        # Start slideshow (blocking)
        try:
            self.slideshow_manager.start()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down")
        except Exception as e:
            logger.error(f"Slideshow error: {e}")
            raise


if __name__ == '__main__':
    try:
        app = MemeScreen()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
