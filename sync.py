#!/usr/bin/env python3
import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import GoogleAPIError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    load_dotenv()

    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    if not credentials_path:
        logger.error("GOOGLE_CREDENTIALS_PATH not set")
        sys.exit(1)

    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    interval_minutes = int(os.getenv('DOWNLOAD_CHECK_INTERVAL_MINUTES', '10'))
    pictures_dir = Path(os.getenv('PICTURES_DIRECTORY', '/tmp/meme-screen/pictures'))
    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

    pictures_dir.mkdir(parents=True, exist_ok=True)

    creds = Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    service = build('drive', 'v3', credentials=creds)
    logger.info("Authenticated with Google Drive")

    def sync():
        logger.info("Syncing with Google Drive...")
        try:
            query = (
                f"'{folder_id}' in parents and trashed=false and "
                "(mimeType='image/jpeg' or mimeType='image/png' or "
                "mimeType='image/gif' or mimeType='image/webp')"
            )
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=100
            ).execute()
            remote = {f['name']: f['id'] for f in results.get('files', [])}
            logger.info(f"Found {len(remote)} images in Google Drive")

            changed = False
            for name, file_id in remote.items():
                if not (pictures_dir / name).exists():
                    try:
                        request = service.files().get_media(fileId=file_id)
                        tmp = pictures_dir / (name + '.tmp')
                        with open(tmp, 'wb') as f:
                            dl = MediaIoBaseDownload(f, request)
                            done = False
                            while not done:
                                _, done = dl.next_chunk()
                        tmp.rename(pictures_dir / name)
                        logger.info(f"Downloaded: {name}")
                        changed = True
                    except Exception as e:
                        logger.error(f"Failed to download {name}: {e}")
                        (pictures_dir / (name + '.tmp')).unlink(missing_ok=True)

            for local in pictures_dir.iterdir():
                if local.is_file() and local.name not in remote:
                    local.unlink()
                    logger.info(f"Removed: {local.name}")
                    changed = True

            if changed:
                (pictures_dir / '.reload').touch()

            logger.info("Sync complete")
        except Exception as e:
            logger.error(f"Sync failed: {e}")

    sync()
    while True:
        time.sleep(interval_minutes * 60)
        sync()


if __name__ == '__main__':
    main()
