"""
Routes package initialization.
"""
from agrifarma.routes.main import main_bp
from agrifarma.routes.auth import auth_bp
from agrifarma.routes.admin import admin_bp

__all__ = ['main_bp', 'auth_bp', 'admin_bp']
