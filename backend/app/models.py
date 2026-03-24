from app.db import db
from sqlalchemy.orm import foreign

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=True)
    card_uid_hash = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    access_events = db.relationship(
        "AccessEvent",
        backref="student",
        primaryjoin="Student.student_id == foreign(AccessEvent.student_id)",
        lazy=True,
    )


class AccessEvent(db.Model):
    __tablename__ = "access_events"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.String(20),
        db.ForeignKey("students.student_id"),
        nullable=True,
    )
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    decision = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    device_id = db.Column(db.Text, nullable=True)
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