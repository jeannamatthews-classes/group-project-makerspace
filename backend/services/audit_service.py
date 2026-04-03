from app.db import db
from app.models import AuditLog


ALLOWED_STATUSES = {"INFO", "SUCCESS", "ERROR"}


def log_event(
    event_type: str,
    message: str,
    status: str = "INFO",
    student_id: str = None,
    device_id: str = None,
    metadata: dict = None,
):
    try:
        normalized_status = str(status).upper().strip()
        if normalized_status not in ALLOWED_STATUSES:
            normalized_status = "INFO"

        entry = AuditLog(
            event_type=str(event_type).strip(),
            message=str(message).strip(),
            status=normalized_status,
            student_id=student_id,
            device_id=device_id,
            metadata_json=metadata,
        )

        db.session.add(entry)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        print(f"[Audit Log Error] {exc}")
