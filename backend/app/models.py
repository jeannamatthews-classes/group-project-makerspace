from app.db import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=True)
    card_uid_hash = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    access_events = db.relationship(
        "AccessEvent",
        back_populates="student",
        lazy=True,
        primaryjoin="Student.student_id == foreign(AccessEvent.student_id)",
    )


class AccessEvent(db.Model):
    __tablename__ = "access_events"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.String(20),
        db.ForeignKey("students.student_id"),
        nullable=True,
    )
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    decision = db.Column(db.String(10), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    device_id = db.Column(db.Text, nullable=True)
    export_status = db.Column(db.String(10), nullable=False, server_default="PENDING")

    student = db.relationship("Student", back_populates="access_events")

    __table_args__ = (
        db.CheckConstraint(
            "decision IN ('GRANTED', 'DENIED')",
            name="check_decision_granted_or_denied",
        ),
        db.CheckConstraint(
            "export_status IN ('PENDING', 'EXPORTED', 'FAILED')",
            name="check_export_status_valid",
        ),
        db.Index("student_id_index", "student_id"),
        db.Index("timestamp_index", "timestamp"),
    )


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, server_default="INFO")
    student_id = db.Column(db.String(20), nullable=True)
    device_id = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
