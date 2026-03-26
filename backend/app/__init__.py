import os
from flask import Flask
from dotenv import load_dotenv
from .db import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    # PostgreSQL connection string
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/rfid_db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # initialize database
    db.init_app(app)

    return app