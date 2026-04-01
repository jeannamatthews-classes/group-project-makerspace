from app import create_app

# Create Flask app using application factory
app = create_app()


@app.route("/")
def home():
    """
    Simple health check route.

    Useful for quickly checking whether the backend is up.
    """
    return {
        "status": "ok",
        "message": "Makerspace backend is running"
    }


if __name__ == "__main__":
    # IMPORTANT:
    # We do NOT call db.create_all() here because the project already uses
    # schema.sql as the source of truth for database structure.
    #
    # Tables should be created by running:
    # psql -U postgres -d makerspace_db -f backend/database/schema.sql
    #
    # Keeping schema creation out of runtime avoids schema drift between
    # SQLAlchemy models and the actual PostgreSQL schema.
    app.run(debug=True)