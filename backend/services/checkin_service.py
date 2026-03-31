from datetime import datetime
from app.db import db
from app.models import Student, AccessEvent
from app.utils import hash_uid
from services.audit_service import log_event


def validate_uid(card_uid: str):
    return card_uid is not None and card_uid.strip() != ""


def check_optional_policies(student):
    return True, "OK"


def process_access_event(card_uid: str, device_id: str = None, timestamp: str = None):
    """
    Decision + Logging Service (core system flow)
    """

    if not validate_uid(card_uid):
        decision = "DENIED"
        reason = "INVALID_UID"
        student_id = None
    else:
        card_uid_hash = hash_uid(card_uid)
        student = Student.query.filter_by(card_uid_hash=card_uid_hash).first()

        if student is None:
            decision = "DENIED"
            reason = "NOT_REGISTERED"
            student_id = None
        else:
            decision = "GRANTED"
            reason = "OK"
            student_id = student.student_id

    # timestamp handling
    event_timestamp = datetime.utcnow()

    # store main event
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

    # log audit entry
    log_event(
        event_type="RFID_TAP",
        message=f"Decision={decision}, Reason={reason}",
        status="SUCCESS" if decision == "GRANTED" else "ERROR",
        student_id=student_id,
        device_id=device_id,
    )

    return {
        "decision": decision,
        "reason": reason,
        "student_id": student_id,
    }