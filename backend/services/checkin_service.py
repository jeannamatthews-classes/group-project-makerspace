from app.db import db
from app.models import AccessEvent, Student
from app.utils import hash_uid, normalize_uid, parse_iso_timestamp
from services.audit_service import log_event


def validate_uid(card_uid: str) -> bool:
    normalized = normalize_uid(card_uid)
    return normalized != ""


def check_optional_policies(student: Student):
    return True, "OK"


def process_access_event(card_uid: str, device_id: str = None, timestamp: str = None):
    normalized_uid = normalize_uid(card_uid)
    student = None
    student_id = None

    if not validate_uid(normalized_uid):
        decision = "DENIED"
        reason = "INVALID_UID"
    else:
        card_uid_hash = hash_uid(normalized_uid)
        student = Student.query.filter_by(card_uid_hash=card_uid_hash).first()

        if student is None:
            decision = "DENIED"
            reason = "NOT_REGISTERED"
        else:
            allowed, policy_reason = check_optional_policies(student)
            student_id = student.student_id

            if allowed:
                decision = "GRANTED"
                reason = "OK"
            else:
                decision = "DENIED"
                reason = policy_reason or "POLICY_FAILED"

    try:
        event_timestamp = parse_iso_timestamp(timestamp)
    except ValueError:
        return {"error": "timestamp must be a valid ISO-8601 string"}, 400

    try:
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

    log_event(
        event_type="RFID_TAP",
        message=f"Decision={decision}, Reason={reason}",
        status="SUCCESS" if decision == "GRANTED" else "INFO",
        student_id=student_id,
        device_id=device_id,
        metadata={
            "decision": decision,
            "reason": reason,
        },
    )

    return {
        "decision": decision,
        "reason": reason,
        "student_id": student_id,
        "timestamp": event_timestamp.isoformat(),
    }, 200
