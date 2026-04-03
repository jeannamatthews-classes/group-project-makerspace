from flask import Blueprint, request, jsonify
from datetime import datetime
from services.registration_service import register_student
from services.checkin_service import process_access_event
from app.models import AccessEvent

# Blueprint groups all API routes together
routes = Blueprint("routes", __name__)


@routes.route("/api/register", methods=["POST"])
def register():
    """
    Register a new student.
    """
    data = request.get_json()

    # Request body must be JSON
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Extract fields from request body
    card_uid = data.get("card_uid")
    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")

    # Validate required fields
    if not card_uid or not student_id or not name:
        return jsonify({"error": "card_uid, student_id, and name are required"}), 400

    # Delegate business logic to registration service
    result, status = register_student(
        card_uid=card_uid,
        student_id=student_id,
        name=name,
        email=email,
    )

    return jsonify(result), status


@routes.route("/api/access-events", methods=["POST"])
def create_access_event():
    """
    Process an RFID tap event and return the access decision.
    """
    data = request.get_json()

    # Request body must be JSON
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Extract fields from request body
    card_uid = data.get("card_uid")
    device_id = data.get("device_id")
    timestamp = data.get("timestamp")

    # card_uid is required to process an access event
    if not card_uid:
        return jsonify({"error": "card_uid is required"}), 400

    # Delegate business logic to check-in service
    result, status = process_access_event(
        card_uid=card_uid,
        device_id=device_id,
        timestamp=timestamp,
    )

    return jsonify(result), status


@routes.route("/api/admin/access-events", methods=["GET"])
def get_event_logs():
    query = AccessEvent.query

    student_id = request.args.get("student_id")
    decision = request.args.get("decision")
    from_timestamp = request.args.get("from")
    to_timestamp = request.args.get("to")

    if student_id:
        query = query.filter(AccessEvent.student_id == student_id)

    if decision:
        decision = decision.upper()
        if decision not in ["GRANTED", "DENIED"]:
            return jsonify({"error": "decision must be GRANTED or DENIED"}), 400
        query = query.filter(AccessEvent.decision == decision)

    if from_timestamp:
        try:
            from_datetime = datetime.fromisoformat(from_timestamp.replace("Z", "+00:00"))
            query = query.filter(AccessEvent.timestamp >= from_datetime)
        except ValueError:
            return jsonify({"error": "Invalid format for 'from' timestamp"}), 400

    if to_timestamp:
        try:
            to_datetime = datetime.fromisoformat(to_timestamp.replace("Z", "+00:00"))
            query = query.filter(AccessEvent.timestamp <= to_datetime)
        except ValueError:
            return jsonify({"error": "Invalid format for 'to' timestamp"}), 400

    events = query.order_by(AccessEvent.timestamp.desc()).all()

    results = []
    for event in events:
        results.append({
            "id": event.id,
            "student_id": event.student_id,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "decision": event.decision,
            "reason": event.reason,
            "device_id": event.device_id,
            "export_status": event.export_status,
        })

    return jsonify(results), 200