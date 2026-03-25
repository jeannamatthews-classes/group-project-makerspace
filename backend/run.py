from app import create_app
from app.db import db
from app.models import Student, AccessEvent

app = create_app()


@app.route("/")
def home():
    return {"status": "ok", "message": "Makerspace backend is running"}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Tables checked/created successfully.")
    app.run(debug=True)