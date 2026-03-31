from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from services.audit_service import log_event


def register_error_handlers(app):
    """
    Global error handlers.

    Automatically logs ALL API errors.
    """

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """
        Handles known HTTP errors (400, 404, etc.)
        """
        try:
            log_event(
                event_type="API_ERROR",
                message=e.description,
                status="ERROR",
                metadata={
                    "endpoint": request.path,
                    "method": request.method,
                    "code": e.code,
                },
            )
        except Exception:
            pass  # never break API because of logging

        return jsonify({"error": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        """
        Handles unexpected server errors (500).
        """
        try:
            log_event(
                event_type="API_ERROR",
                message=str(e),
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