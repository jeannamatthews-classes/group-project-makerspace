from app import create_app
from app.db import db
from app.models import Student, AccessEvent, AuditLog

# Create Flask app using app factory
app = create_app()


@app.route("/")
def home():
    """
    Simple health check route.
    """
    return {
        "status": "ok",
        "message": "Makerspace backend is running"
    }


if __name__ == "__main__":
    with app.app_context():
        # Create database tables if they do not already exist
        db.create_all()
        print("Tables checked/created successfully.")

    app.run(debug=True)