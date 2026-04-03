import re

from sqlalchemy.exc import IntegrityError

from app.db import db
from app.models import Student
from app.utils import hash_uid, normalize_uid
from services.audit_service import log_event


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _clean_text(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def register_student(card_uid: str, student_id: str, name: str, email: str = None):
    normalized_uid = normalize_uid(card_uid)
    normalized_student_id = _clean_text(student_id)
    normalized_name = _clean_text(name)
    normalized_email = _clean_text(email)

    if not normalized_uid:
        return {"error": "card_uid is required"}, 400

    if not normalized_student_id:
        return {"error": "student_id is required"}, 400

    if not normalized_name:
        return {"error": "name is required"}, 400

    if normalized_email and not EMAIL_REGEX.match(normalized_email):
        return {"error": "email must be a valid email address"}, 400

    card_uid_hash = hash_uid(normalized_uid)

    student = Student(
        student_id=normalized_student_id,
        name=normalized_name,
        email=normalized_email,
        card_uid_hash=card_uid_hash,
    )

    try:
        db.session.add(student)
        db.session.commit()

        log_event(
            event_type="REGISTRATION",
            message="Student registered successfully",
            status="SUCCESS",
            student_id=normalized_student_id,
        )

        return {
            "status": "CREATED",
            "student_id": normalized_student_id,
        }, 201

    except IntegrityError:
        db.session.rollback()

        log_event(
            event_type="REGISTRATION",
            message="Duplicate registration attempt",
            status="ERROR",
            student_id=normalized_student_id,
        )

        return {
            "error": "Student already exists or card is already registered"
        }, 409

    except Exception as exc:
        db.session.rollback()

        log_event(
            event_type="REGISTRATION",
            message=f"Unexpected registration failure: {str(exc)[:500]}",
            status="ERROR",
            student_id=normalized_student_id,
        )

        return {"error": "Failed to register student"}, 500
