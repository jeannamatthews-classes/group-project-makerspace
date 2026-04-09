from services.audit_service import log_event


def log_export_attempt(
    student_id: str = None,
    device_id: str = None,
    success: bool = True,
    details: str = None,
):
    """
    Log Google Sheets export attempts through the central audit logger.
    """
    log_event(
        event_type="EXPORT_ATTEMPT",
        message=details or "Google Sheets export attempt recorded",
        status="SUCCESS" if success else "ERROR",
        student_id=student_id,
        device_id=device_id,
        metadata={
            "target": "GOOGLE_SHEETS",
            "success": success,
        },
    )
