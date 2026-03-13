from flask import request, jsonify
from services.registration_service import register_student
from app import app


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    card_uid = data.get("card_uid")
    student_id = data.get("student_id")
    name = data.get("name")
    email = data.get("email")

    if not card_uid or not student_id or not name:
        return jsonify({"error": "card_uid, student_id, and name are required"}), 400

    result, status = register_student(
        card_uid=card_uid,
        student_id=student_id,
        name=name,
        email=email
    )

    return jsonify(result), status
from flask import Flask, request, jsonify
from services.checkin_service import process_access_event

app = Flask(__name__)

@app.route("/api/access-events", methods=["POST"]) # post requests sent to /api/access-events
def create_access_event():
    data = request.get_json() # get the json body from the incoming request
    if not data: # if no json body, error
        return jsonify({"error": "Request body must be JSON"}), 400

    # extract fields 
    card_uid = data.get("card_uid")
    device_id = data.get("device_id")
    timestamp = data.get("timestamp")

    # card_uid is required
    if not card_uid:
        return jsonify({"error": "card_uid is required"}), 400

    result = process_access_event(
        card_uid=card_uid,
        device_id=device_id,
        timestamp=timestamp
    )
    # return the result as a json response with 'OK' http status
    return jsonify(result), 200
