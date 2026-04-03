from flask import jsonify, request
from werkzeug.exceptions import HTTPException

from services.audit_service import log_event


SENSITIVE_ERROR_TYPES = {"password", "token", "secret"}


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        try:
            log_event(
                event_type="API_ERROR",
                message=error.description,
                status="ERROR",
                metadata={
                    "endpoint": request.path,
                    "method": request.method,
                    "code": error.code,
                },
            )
        except Exception:
            pass

        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        try:
            error_text = str(error)
            lowered = error_text.lower()
            if any(word in lowered for word in SENSITIVE_ERROR_TYPES):
                safe_message = "Unexpected internal error"
            else:
                safe_message = error_text[:500]

            log_event(
                event_type="API_ERROR",
                message=safe_message,
                status="ERROR",
                metadata={
                    "endpoint": request.path,
                    "method": request.method,
                    "code": 500,
                },
            )
        except Exception:
            pass

        return jsonify({"error": "Internal server error"}), 500
