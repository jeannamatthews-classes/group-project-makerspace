import os

from app import create_app

app = create_app()


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Makerspace backend is running",
    }, 200


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
