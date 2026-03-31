from app.db import db
from app.models import AuditLog


def log_event(
    event_type: str,
    message: str,
    status: str = "INFO",
    student_id: str = None,
    device_id: str = None,
    metadata: dict = None,
):
    """
    CENTRALIZED LOGGER

    Used across the entire backend.
    """

    try:
        entry = AuditLog(
            event_type=event_type,
            message=message,
            status=status,
            student_id=student_id,
            device_id=device_id,
            metadata_json=metadata,
        )

        db.session.add(entry)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"[Audit Log Error] {e}")