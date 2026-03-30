from flask import jsonify, request
from werkzeug.exceptions import HTTPException

# DEPENDS ON: backend/services/audit_logger.py
# If the function name is different there, only adjust this import line.
from services.audit_logger import log_event


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """
        Handles known HTTP errors like 400, 404, 405, etc.
        """
        try:
            log_event(
                event_type="API_ERROR",
                message=e.description,
                status="ERROR",
                metadata={
                    "endpoint": request.path,
                    "method": request.method,
                    "code": e.code
                }
            )
        except Exception:
            # Never let logging failure break the API response
            pass

        return jsonify({
            "error": e.description
        }), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        """
        Handles unexpected server errors.
        """
        try:
            log_event(
                event_type="API_ERROR",
                message=str(e),
                status="ERROR",
                metadata={
                    "endpoint": request.path,
                    "method": request.method,
                    "code": 500
                }
            )
        except Exception:
            pass

        return jsonify({
            "error": "Internal server error"
        }), 500