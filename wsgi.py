"""WSGI entry point for Gunicorn"""
import os
from app import app, db, Admin

# Initialize database on startup
def init_db():
    """Initialize database and create default admin user"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            db.session.commit()
            print("✓ Database tables created")
        except Exception as e:
            db.session.rollback()
            print(f"⚠ Database initialization: {e}")

# Initialize database when module is imported
try:
    init_db()
except Exception as e:
    print(f"⚠ Could not initialize database: {e}")

# Export app for Gunicorn
if __name__ == "__main__":
    app.run()


