"""
WSGI entry point for WoW Flask application.
Used by production servers like Gunicorn.
"""
from app import create_app

# Create the application instance
application = create_app()
app = application  # Alias for compatibility

if __name__ == "__main__":
    app.run()