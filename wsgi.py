"""WSGI entry point for Gunicorn"""
import os
import sys
from app import app, db

# Initialize database on startup
def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        try:
            print("🔄 Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully")
        except Exception as e:
            print(f"⚠ Database initialization error: {e}", file=sys.stderr)
            # Don't fail - let the app start anyway

# Initialize database when module is imported
print("🚀 Starting Flask app initialization...")
try:
    init_db()
    print("✓ App initialization complete")
except Exception as e:
    print(f"⚠ Init failed: {e}", file=sys.stderr)

# Export app for Gunicorn
if __name__ == "__main__":
    app.run()





