import os
from pathlib import Path
from dotenv import load_dotenv

# Get backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:makerspace2026@localhost:5432/makerspace_db",
    )


class DevelopmentConfig(Config):
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}