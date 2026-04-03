import os

from flask import Flask

from app.db import db
from config.config import config_by_name


def create_app():
    app = Flask(__name__)

    env_name = os.getenv("FLASK_ENV", "development").lower()
    config_class = config_by_name.get(env_name, config_by_name["development"])
    app.config.from_object(config_class)

    db.init_app(app)

    from app.routes import routes
    app.register_blueprint(routes)

    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app
