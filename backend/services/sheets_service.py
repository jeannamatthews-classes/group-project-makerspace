import os
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

import gspread
from google.oauth2.service_account import Credentials

from app.db import db
from models.access_event import AccessEvent

logger = logging.getLogger(__name__)

# Configuration
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
if not GOOGLE_CREDENTIALS_FILE:
    raise ValueError("GOOGLE_CREDENTIALS_FILE is not set")

SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
if not SHEET_NAME:
    raise ValueError("GOOGLE_SHEET_NAME is not set")

# Google Sheets scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authenticate
def get_sheet():
    try:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
        )
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets: {e}")
        raise


# Retry wrapper (handles network/API failures)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def append_row(sheet, row):
    sheet.append_row(row)


def export_pending_events():
    """
    Finds unexported successful access events and pushes them to Google Sheets.
    """

    logging.info("Starting export job...")

    # Only export successful (GRANT) events that are still pending
    events = (
        AccessEvent.query
        .filter_by(export_status="PENDING", decision="GRANT")
        .all()
    )

    if not events:
        logging.info("No pending events found.")
        return

    sheet = get_sheet()

    for event in events:
        try:
            # Prepare row data
            row = [
                event.id,              
                event.student_id,
                event.timestamp,
                event.decision,
                event.reason,
                event.device_id
            ]

            # Append to Google Sheet (with retry)
            append_row(sheet, row)

            # Mark as exported
            event.export_status = "EXPORTED"
            db.session.commit()   # Commit immediately

            logging.info(f"Exported event ID {event.id}")

        except Exception as e:
            logging.error(f"Failed to export event ID {event.id}: {e}")
            db.session.rollback()

    # Commit all updates at once
    db.session.commit()

    logging.info("Export job completed.")