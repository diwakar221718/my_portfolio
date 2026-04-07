"""WSGI entry point for Gunicorn"""
import os
import sys
from app import app

# Export app for Gunicorn
if __name__ == "__main__":
    app.run()






