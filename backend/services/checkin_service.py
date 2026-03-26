from datetime import datetime
from app.db import db
from app.models import Student, AccessEvent
from app.utils import hash_uid
from services.audit_service import log_event


def process_access_event(card_uid: str, device_id: str = None, timestamp: str = None) -> dict:
    """
    Process an RFID tap attempt for POST /api/access-events.
    """
    card_uid_hash = hash_uid(card_uid)
    student = Student.query.filter_by(card_uid_hash=card_uid_hash).first() # returns the first match 

    if student != None:
        decision = "GRANT"
        reason = "OK"
        student_id = student.student_id
    else:
        decision = "DENY"
        reason = "NOT_REGISTERED"
        student_id = None

    if timestamp != None:
        try:
            event_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00")) # convert timestamp to python datetime obj.
        except ValueError: # date is badly formatted
            event_timestamp = datetime.utcnow() # use current time
    else:
        event_timestamp = datetime.utcnow() # if no timestamp exist, use current time

    access_event = AccessEvent( # create a new access event record to log this tap attempt

        student_id=student_id,
        timestamp=event_timestamp,
        decision=decision,
        reason=reason,
        device_id=device_id,
        export_status="PENDING"
    )

    log_event(access_event)

    response = { # response dictionary that will be returned to the Flask route
        "decision": decision,
        "reason": reason
    }

    if student_id: # if a student ID exists, send back final dictionary with that student_id
        response["student_id"] = student_id

    return response 
