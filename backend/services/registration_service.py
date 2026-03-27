from app.db import db
from app.models import Student
from app.utils import hash_uid


def register_student(card_uid: str, student_id: str, name: str, email: str = None):
    """
    Register a new student and bind their RFID card.
    """

    card_uid_hash = hash_uid(card_uid)

    # Check for duplicate UID
    existing = Student.query.filter_by(card_uid_hash=card_uid_hash).first()
    if existing:
        return {"error": "Card already registered"}, 400

    student = Student(
        student_id=student_id,
        name=name,
        email=email,
        card_uid_hash=card_uid_hash
    )

    db.session.add(student)
    db.session.commit()

    #this service may also need an access_event creation in order to pass to the audit_service and log the event

    return {
        "status": "CREATED",
        "student_id": student_id
    }, 201
