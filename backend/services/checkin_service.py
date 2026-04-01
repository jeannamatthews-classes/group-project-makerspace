from datetime import datetime

from app.db import db
from app.models import Student, AccessEvent
from app.utils import hash_uid
from services.audit_service import log_event


def validate_uid(card_uid: str):
    """
    Basic UID validation.

    For now:
    - UID must not be None
    - UID must not be empty/whitespace

    This can later be extended to enforce length/format checks.
    """
    return card_uid is not None and card_uid.strip() != ""


def check_optional_policies(student):
    """
    Optional policy hook.

    This function exists so that future rules can be added without
    cluttering the main decision flow.

    Example future checks:
    - safety training completed
    - student account active
    - allowed access hours

    Returns:
        (allowed: bool, reason: str)
    """
    return True, "OK"


def process_access_event(card_uid: str, device_id: str = None, timestamp: str = None):
    """
    Decision + Logging Service (core system flow)

    Responsibilities:
    - validate UID
    - locate student by hashed UID
    - apply optional policy checks
    - return GRANTED or DENIED
    - write access event to DB
    - write audit log entry
    """

    student = None
    student_id = None

    # Step 1: validate raw card UID input
    if not validate_uid(card_uid):
        decision = "DENIED"
        reason = "INVALID_UID"

    else:
        # Step 2: hash UID and look up student
        card_uid_hash = hash_uid(card_uid)
        student = Student.query.filter_by(card_uid_hash=card_uid_hash).first()

        if student is None:
            # No matching registered user
            decision = "DENIED"
            reason = "NOT_REGISTERED"
        else:
            # Step 3: apply optional policies
            allowed, policy_reason = check_optional_policies(student)

            if allowed:
                decision = "GRANTED"
                reason = "OK"
            else:
                decision = "DENIED"
                reason = policy_reason

            student_id = student.student_id

    # Step 4: determine event timestamp
    #
    # If a timestamp was passed in later, this is where parsing logic can go.
    # For now, always use current UTC time.
    event_timestamp = datetime.utcnow()

    try:
        # Step 5: store access event in database
        access_event = AccessEvent(
            student_id=student_id,
            timestamp=event_timestamp,
            decision=decision,
            reason=reason,
            device_id=device_id,
            export_status="PENDING",
        )

        db.session.add(access_event)
        db.session.commit()

    except Exception as e:
        # Roll back failed DB write and also try to log it
        db.session.rollback()

        log_event(
            event_type="RFID_TAP",
            message=f"Failed to store access event: {str(e)}",
            status="ERROR",
            student_id=student_id,
            device_id=device_id,
        )

        return {
            "error": "Failed to record access event"
        }, 500

    # Step 6: store centralized audit log
    log_event(
        event_type="RFID_TAP",
        message=f"Decision={decision}, Reason={reason}",
        status="SUCCESS" if decision == "GRANTED" else "ERROR",
        student_id=student_id,
        device_id=device_id,
    )

    # Step 7: return decision payload
    return {
        "decision": decision,
        "reason": reason,
        "student_id": student_id,
    }, 200