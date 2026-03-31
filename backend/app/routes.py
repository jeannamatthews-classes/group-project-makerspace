from flask import Blueprint, request, jsonify
from services.registration_service import register_student
from services.checkin_service import process_access_event

# Blueprint for grouping all API routes
routes = Blueprint("routes", __name__)

# Student Registration Route
@routes.route("/api/register", methods=["POST"])
def register():
    # Parse JSON body from request
    data = request.get_json()

    # Validate request format
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Extract required and optional fields
    card_uid = data.get("card_uid")
    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")

    # Validate required fields
    if not card_uid or not student_id or not name:
        return jsonify({"error": "card_uid, student_id, and name are required"}), 400

    # Call service layer to handle registration logic
    result, status = register_student(
        card_uid=card_uid,
        student_id=student_id,
        name=name,
        email=email
    )

    # Return response from service
    return jsonify(result), status

# Create Access Event Route
@routes.route("/api/access-events", methods=["POST"])
def create_access_event():
    # Parse JSON body from request
    data = request.get_json()

    # Validate request format
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Extract fields from request
    card_uid = data.get("card_uid")
    device_id = data.get("device_id")
    timestamp = data.get("timestamp")

    # card_uid is required for processing access event
    if not card_uid:
        return jsonify({"error": "card_uid is required"}), 400

    # Call service layer to process access logic (GRANT / DENY + logging)
    result = process_access_event(
        card_uid=card_uid,
        device_id=device_id,
        timestamp=timestamp
    )

    # Return result (typically includes decision + message)
    return jsonify(result), 200
