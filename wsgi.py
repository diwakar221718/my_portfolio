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
            
            # Create default admin user if it doesn't exist
            admin_exists = Admin.query.filter_by(username='admin').first()
            if not admin_exists:
                admin = Admin(username='admin', email='admin@portfolio.com')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Default admin user created: admin / admin123")
            else:
                print("✓ Admin user already exists")
        except Exception as e:
            print(f"✗ Database initialization error: {e}")
            db.session.rollback()

# Initialize database when module is imported
init_db()

# Export app for Gunicorn
if __name__ == "__main__":
    app.run()
