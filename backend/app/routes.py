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