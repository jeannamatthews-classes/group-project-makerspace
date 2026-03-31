from app.db import db
from app.models import Student
from app.utils import hash_uid
from services.audit_service import log_event


def register_student(card_uid: str, student_id: str, name: str, email: str = None):
    """
    Handles student registration.
    """

    card_uid_hash = hash_uid(card_uid)

    # create student
    student = Student(
        student_id=student_id,
        name=name,
        email=email,
        card_uid_hash=card_uid_hash,
    )

    db.session.add(student)
    db.session.commit()

    # log registration
    log_event(
        event_type="REGISTRATION",
        message="Student registered successfully",
        status="SUCCESS",
        student_id=student_id,
    )

    return {
        "status": "CREATED",
        "student_id": student_id,
    }, 201