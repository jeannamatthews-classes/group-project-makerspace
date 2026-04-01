from flask import Blueprint, request, jsonify
from services.registration_service import register_student
from services.checkin_service import process_access_event

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
    result = process_access_event(
        card_uid=card_uid,
        device_id=device_id,
        timestamp=timestamp,
    )

    return jsonify(result), 200