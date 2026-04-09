from app.db import db
from app.models import AccessEvent, Student
from app.utils import hash_uid, normalize_uid, parse_iso_timestamp
from services.audit_service import log_event
from services.google_sheets_service import export_pending_access_events


def validate_uid(card_uid: str) -> bool:
    """
    Validate that the UID is present after normalization.
    """
    normalized = normalize_uid(card_uid)
    return normalized != ""


def check_optional_policies(student: Student):
    """
    Placeholder for future policy checks.

    Returns:
        tuple[bool, str]
        - bool: whether access is allowed
        - str: machine-readable policy code
    """
    return True, "OK"


def process_access_event(card_uid: str, device_id: str = None, timestamp: str = None):
    """
    Process an RFID tap and return a structured access decision.

    Response fields:
    - decision: GRANTED or DENIED
    - code: machine-readable code for frontend logic
    - reason: human-readable message for UI display
    - student_id: student id if matched, otherwise None
    - timestamp: resolved event timestamp
    """
    normalized_uid = normalize_uid(card_uid)
    student = None
    student_id = None

    # Default response values
    decision = "DENIED"
    code = "UNKNOWN_ERROR"
    reason = "Unknown error"

    # Case 1: card UID is invalid or empty
    if not validate_uid(normalized_uid):
        decision = "DENIED"
        code = "INVALID_UID"
        reason = "Invalid card UID"

    else:
        # Hash the normalized UID and look up the student
        card_uid_hash = hash_uid(normalized_uid)
        student = Student.query.filter_by(card_uid_hash=card_uid_hash).first()

        # Case 2: card is not registered in the student table
        if student is None:
            decision = "DENIED"
            code = "NOT_REGISTERED"
            reason = "Card is not registered"

        else:
            # Student exists; now evaluate policy rules
            student_id = student.student_id
            allowed, policy_code = check_optional_policies(student)

            if allowed:
                decision = "GRANTED"
                code = "ACCESS_GRANTED"
                reason = "Access granted"
            else:
                decision = "DENIED"
                code = policy_code or "POLICY_FAILED"
                reason = "Access denied by policy"

    # Parse timestamp after access decision logic
    try:
        event_timestamp = parse_iso_timestamp(timestamp)
    except ValueError:
        return {"error": "timestamp must be a valid ISO-8601 string"}, 400

    # Store the event in the database first.
    # PostgreSQL remains the source of truth even if Google Sheets export fails.
    try:
        access_event = AccessEvent(
            student_id=student_id,
            timestamp=event_timestamp,
            decision=decision,
            # Store the machine-readable code in the DB reason field
            # so reporting stays stable and consistent.
            reason=code,
            device_id=device_id,
            export_status="PENDING",
        )
        db.session.add(access_event)
        db.session.commit()

        print("Attempting Google Sheets export...")

        # After the local database write succeeds, try exporting pending
        # access events to Google Sheets.
        #
        # If export fails, do NOT fail the API request. The row stays in the
        # database with export_status="PENDING" so it can be retried later.
        try:
            export_pending_access_events(limit=25)
        except Exception as export_exc:
            log_event(
                event_type="EXPORT_ATTEMPT",
                message=f"Google Sheets export trigger failed: {str(export_exc)[:500]}",
                status="ERROR",
                student_id=student_id,
                device_id=device_id,
                metadata={
                    "target": "GOOGLE_SHEETS",
                    "success": False,
                },
            )

    except Exception as exc:
        db.session.rollback()

        log_event(
            event_type="RFID_TAP",
            message=f"Failed to store access event: {str(exc)[:500]}",
            status="ERROR",
            student_id=student_id,
            device_id=device_id,
        )
        return {"error": "Failed to record access event"}, 500

    # Log both code and human-readable reason
    log_event(
        event_type="RFID_TAP",
        message=f"Decision={decision}, Code={code}, Reason={reason}",
        status="SUCCESS" if decision == "GRANTED" else "INFO",
        student_id=student_id,
        device_id=device_id,
        metadata={
            "decision": decision,
            "code": code,
            "reason": reason,
        },
    )

    # Return structured response to frontend
    return {
        "decision": decision,
        "code": code,
        "reason": reason,
        "student_id": student_id,
        "timestamp": event_timestamp.isoformat(),
    }, 200
