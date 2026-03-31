from flask import Flask
from app.db import db


def create_app():
    """
    Application factory.

    Responsible for:
    - Creating Flask app
    - Configuring database
    - Initializing extensions
    - Registering routes
    - Registering global error handlers
    """
    app = Flask(__name__)

    # Database configuration (SQLite for now)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///makerspace_test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize SQLAlchemy instance with app
    db.init_app(app)

    # Register API routes (Blueprint)
    from app.routes import routes
    app.register_blueprint(routes)

    # Register centralized error handlers
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app