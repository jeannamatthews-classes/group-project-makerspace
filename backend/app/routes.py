from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.models import AccessEvent
from app.utils import normalize_uid, parse_iso_timestamp
from services.checkin_service import process_access_event
from services.registration_service import register_student

routes = Blueprint("routes", __name__)


@routes.post("/api/register")
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    result, status = register_student(
        card_uid=data.get("card_uid"),
        student_id=data.get("student_id"),
        name=data.get("name"),
        email=data.get("email"),
    )
    return jsonify(result), status


@routes.post("/api/access-events")
def create_access_event():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    card_uid = normalize_uid(data.get("card_uid"))
    if not card_uid:
        return jsonify({"error": "card_uid is required"}), 400

    result, status = process_access_event(
        card_uid=card_uid,
        device_id=data.get("device_id"),
        timestamp=data.get("timestamp"),
    )
    return jsonify(result), status


@routes.get("/api/admin/access-events")
def get_access_events():
    query = AccessEvent.query

    student_id = request.args.get("student_id", type=str)
    decision = request.args.get("decision", type=str)
    from_timestamp = request.args.get("from", type=str)
    to_timestamp = request.args.get("to", type=str)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=50, type=int)

    if page < 1:
        return jsonify({"error": "page must be at least 1"}), 400

    if per_page < 1 or per_page > 200:
        return jsonify({"error": "per_page must be between 1 and 200"}), 400

    if student_id:
        query = query.filter(AccessEvent.student_id == student_id.strip())

    if decision:
        normalized_decision = decision.strip().upper()
        if normalized_decision not in {"GRANTED", "DENIED"}:
            return jsonify({"error": "decision must be GRANTED or DENIED"}), 400
        query = query.filter(AccessEvent.decision == normalized_decision)

    if from_timestamp:
        try:
            from_datetime = parse_iso_timestamp(from_timestamp)
            query = query.filter(AccessEvent.timestamp >= from_datetime)
        except ValueError:
            return jsonify({"error": "Invalid format for 'from' timestamp"}), 400

    if to_timestamp:
        try:
            to_datetime = parse_iso_timestamp(to_timestamp)
            query = query.filter(AccessEvent.timestamp <= to_datetime)
        except ValueError:
            return jsonify({"error": "Invalid format for 'to' timestamp"}), 400

    pagination = query.order_by(AccessEvent.timestamp.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    results = []
    for event in pagination.items:
        results.append(
            {
                "id": event.id,
                "student_id": event.student_id,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                "decision": event.decision,
                "reason": event.reason,
                "device_id": event.device_id,
                "export_status": event.export_status,
            }
        )

    return (
        jsonify(
            {
                "items": results,
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )
