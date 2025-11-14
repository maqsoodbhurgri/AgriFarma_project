"""
AgriFarma Application Factory
Creates and configures the Flask application instance.
"""
import os
from flask import Flask
from config import config
from agrifarma.extensions import db  # re-exported for tests


def create_app(config_name='development'):
    """
    Application factory function.
    
    Args:
        config_name: Configuration environment (development, production, testing)
        
    Returns:
        Configured Flask application instance
    """
    # Set template and static folders to the root level
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Set ASSETS_ROOT for templates
    app.config['ASSETS_ROOT'] = '/static'
    
    # Initialize extensions
    from agrifarma.extensions import db, migrate, login_manager, bcrypt, csrf
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from agrifarma.routes.main import main_bp
    from agrifarma.routes.auth import auth_bp
    from agrifarma.routes.admin import admin_bp
    from agrifarma.routes.forum import forum_bp
    from agrifarma.routes.blog import blog_bp
    from agrifarma.routes.consultancy import consultancy_bp
    from agrifarma.routes.marketplace import marketplace_bp
    from agrifarma.routes.analytics import analytics_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(forum_bp, url_prefix='/forum')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(consultancy_bp, url_prefix='/consultancy')
    app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
    app.register_blueprint(analytics_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Create upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app

# Re-export commonly used objects for tests/importers
__all__ = [
    'create_app',
    'db',
]


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/error_403.html'), 403
    
    @app.errorhandler(404)
    def page_not_found(error):
        from flask import render_template
        return render_template('errors/error_404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        from agrifarma.extensions import db
        db.session.rollback()
        
        # Log the actual error in debug mode
        if app.debug:
            import traceback
            print("\n" + "="*60)
            print("500 ERROR DETAILS:")
            print("="*60)
            print(f"Error: {error}")
            print(f"Type: {type(error)}")
            traceback.print_exc()
            print("="*60 + "\n")
        
        return render_template('errors/error_500.html'), 500


def register_template_filters(app):
    """Register custom template filters."""
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format a datetime object."""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('date')
    def format_date(value, format='%Y-%m-%d'):
        """Format a date object."""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('nl2br')
    def nl2br_filter(value):
        """Convert newlines to <br> tags."""
        if value is None:
            return ""
        from markupsafe import Markup
        import re
        return Markup(re.sub(r'\n', '<br>\n', str(value)))
