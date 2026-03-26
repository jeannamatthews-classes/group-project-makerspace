from datetime import datetime
from app.db import db
from app.models import Student, AccessEvent
from app.utils import hash_uid


def validate_uid(card_uid: str):
    """
    Basic validation to make sure the UID exists and is not blank.
    """
    return card_uid is not None and card_uid.strip() != ""


def check_optional_policies(student):
    """
    Placeholder for future policy checks.

    Right now, any registered student passes.
    Later this could check things like "training status".
    """
    return True, "OK"


def process_access_event(card_uid: str, device_id: str = None, timestamp: str = None):
    """
    Process an RFID tap attempt for POST /api/access-events.
    """

    if not validate_uid(card_uid): # ensure UID exist before doing anything else
        decision = "DENY"
        reason = "INVALID_UID"
        student_id = None
    else:
        card_uid_hash = hash_uid(card_uid) 
        student = Student.query.filter_by(card_uid_hash=card_uid_hash).first() # look for a matching registered student

        if student is None:
            decision = "DENY"
            reason = "NOT_REGISTERED"
            student_id = None
        else:
            allowed, policy_reason = check_optional_policies(student) # run extra policy checks here 
            if allowed:
                decision = "GRANT"
                reason = "OK"
            else:
                decision = "DENY"
                reason = policy_reason

            student_id = student.student_id

    # use the provided timestamp if valid; else use current UTC time
    if timestamp is not None:
        try:
            event_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            event_timestamp = datetime.utcnow()
    else:
        event_timestamp = datetime.utcnow()

    # log the tap attempt in the database
    access_event = AccessEvent(
        student_id=student_id,
        timestamp=event_timestamp,
        decision=decision,
        reason=reason,
        device_id=device_id,
        export_status="PENDING"
    )

    db.session.add(access_event)
    db.session.commit()

    # build the response returned to the route
    response = {
        "decision": decision,
        "reason": reason
    }

    if student_id is not None:
        response["student_id"] = student_id

    return response