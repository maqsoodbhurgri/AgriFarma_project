"""
WSGI entry point for production deployment (PythonAnywhere, etc.)
"""
import sys
import os

# Add the project directory to the Python path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask application
from app import app as application

if __name__ == "__main__":
    application.run()
