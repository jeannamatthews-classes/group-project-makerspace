from sqlalchemy.exc import IntegrityError

from app.db import db
from app.models import Student
from app.utils import hash_uid
from services.audit_service import log_event


def register_student(card_uid: str, student_id: str, name: str, email: str = None):
    """
    Handles student registration.

    Responsibilities:
    - Hash the raw RFID UID
    - Create a Student record
    - Handle duplicate/constraint errors safely
    - Log successful and failed registration attempts
    """

    # Hash raw UID before storage
    card_uid_hash = hash_uid(card_uid)

    # Prepare new student record
    student = Student(
        student_id=student_id,
        name=name,
        email=email,
        card_uid_hash=card_uid_hash,
    )

    try:
        # Save student to database
        db.session.add(student)
        db.session.commit()

        # Log successful registration
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

    except IntegrityError:
        # This usually means duplicate student_id, email, or card UID hash
        db.session.rollback()

        log_event(
            event_type="REGISTRATION",
            message="Duplicate registration attempt",
            status="ERROR",
            student_id=student_id,
        )

        return {
            "error": "Student already exists or card is already registered"
        }, 409

    except Exception as e:
        # Catch unexpected errors to prevent partial/dirty DB state
        db.session.rollback()

        log_event(
            event_type="REGISTRATION",
            message=f"Unexpected registration failure: {str(e)}",
            status="ERROR",
            student_id=student_id,
        )

        return {
            "error": "Failed to register student"
        }, 500