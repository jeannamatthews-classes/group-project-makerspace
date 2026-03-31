from app.db import db
from sqlalchemy.orm import foreign


class Student(db.Model):
    """
    Stores registered makerspace users.
    """
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    # School student ID
    student_id = db.Column(db.String(20), unique=True, nullable=True)

    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=True)

    # IMPORTANT: hashed UID only (never store raw UID)
    card_uid_hash = db.Column(db.Text, unique=True, nullable=False)

    created_at = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp()
    )

    # Relationship to access events
    access_events = db.relationship(
        "AccessEvent",
        backref="student",
        primaryjoin="Student.student_id == foreign(AccessEvent.student_id)",
        lazy=True,
    )


class AccessEvent(db.Model):
    """
    Stores RFID tap decisions (core system functionality).
    """
    __tablename__ = "access_events"

    id = db.Column(db.Integer, primary_key=True)

    # Links to Student.student_id (NOT primary key id)
    student_id = db.Column(
        db.String(20),
        db.ForeignKey("students.student_id"),
        nullable=True,
    )

    timestamp = db.Column(db.TIMESTAMP, nullable=False)

    # MUST be GRANTED or DENIED
    decision = db.Column(db.String(10), nullable=False)

    reason = db.Column(db.Text, nullable=True)
    device_id = db.Column(db.Text, nullable=True)

    # Used for Google Sheets export tracking
    export_status = db.Column(
        db.String(10),
        nullable=True,
        server_default="PENDING",
    )

    __table_args__ = (
        db.CheckConstraint(
            "decision = 'GRANTED' OR decision = 'DENIED'",
            name="check_decision_granted_or_denied",
        ),
        db.Index("student_id_index", "student_id"),
        db.Index("timestamp_index", "timestamp"),
    )


class AuditLog(db.Model):
    """
    Centralized logging table for:
    - API errors
    - registration events
    - export attempts
    - debugging logs

    This is separate from AccessEvent (which is ONLY for RFID taps)
    """
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    # Example: RFID_TAP, REGISTRATION, API_ERROR, EXPORT_ATTEMPT
    event_type = db.Column(db.String(50), nullable=False)

    message = db.Column(db.Text, nullable=False)

    # INFO / SUCCESS / ERROR
    status = db.Column(db.String(20), nullable=False, server_default="INFO")

    student_id = db.Column(db.String(20), nullable=True)
    device_id = db.Column(db.Text, nullable=True)

    # Stores structured metadata (endpoint, method, etc.)
    metadata_json = db.Column(db.JSON, nullable=True)

    created_at = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp()
    )