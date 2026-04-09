import os
from typing import List

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.db import db
from app.models import AccessEvent
from services.export_logger import log_export_attempt

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def sheets_enabled() -> bool:
    """
    Return True if Google Sheets export is enabled.
    """
    return os.getenv("GOOGLE_SHEETS_ENABLED", "false").lower() == "true"


def get_sheets_client():
    """
    Build an authenticated Google Sheets API client using a service account.
    """
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not service_account_file:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is not set")

    credentials = Credentials.from_service_account_file(
        service_account_file,
        scopes=SCOPES,
    )

    return build("sheets", "v4", credentials=credentials)


def get_spreadsheet_config():
    """
    Read Google Sheets target settings from environment variables.
    """
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    worksheet_name = os.getenv("GOOGLE_SHEETS_WORKSHEET_NAME", "AccessEvents")

    if not spreadsheet_id:
        raise RuntimeError("GOOGLE_SHEETS_SPREADSHEET_ID is not set")

    return spreadsheet_id, worksheet_name


def serialize_event(event: AccessEvent) -> List[str]:
    """
    Convert one AccessEvent database row into a Google Sheets row.
    """
    return [
        str(event.id),
        event.student_id or "",
        event.timestamp.isoformat() if event.timestamp else "",
        event.decision or "",
        event.reason or "",
        event.device_id or "",
        event.export_status or "",
    ]


def export_pending_access_events(limit: int = 100) -> int:
    """
    Export pending access events from PostgreSQL to Google Sheets.

    Flow:
    - find rows marked PENDING
    - mark each row EXPORTED before serializing so the sheet also gets EXPORTED
    - append the row to Google Sheets
    - commit the DB change only after the append succeeds
    - if append fails, roll back and leave the row as PENDING

    Returns:
        Number of rows successfully exported.
    """
    if not sheets_enabled():
        return 0

    service = get_sheets_client()
    spreadsheet_id, worksheet_name = get_spreadsheet_config()
    append_range = f"{worksheet_name}!A:G"

    pending_events = (
        AccessEvent.query
        .filter(AccessEvent.export_status == "PENDING")
        .order_by(AccessEvent.timestamp.asc())
        .limit(limit)
        .all()
    )

    if not pending_events:
        return 0

    exported_count = 0

    for event in pending_events:
        try:
            # Set EXPORTED before serializing so the sheet row also shows EXPORTED
            event.export_status = "EXPORTED"
            row_values = [serialize_event(event)]

            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=append_range,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": row_values},
            ).execute()

            # Persist EXPORTED in PostgreSQL only after append succeeds
            db.session.commit()
            exported_count += 1

            print(f"Exported access event {event.id} to Google Sheets")

            log_export_attempt(
                student_id=event.student_id,
                device_id=event.device_id,
                success=True,
                details=f"Exported access event {event.id} to Google Sheets",
            )

        except Exception as exc:
            db.session.rollback()

            print(f" Failed to export access event {event.id}: {str(exc)}")

            log_export_attempt(
                student_id=event.student_id,
                device_id=event.device_id,
                success=False,
                details=f"Failed to export access event {event.id}: {str(exc)[:500]}",
            )

    return exported_count
