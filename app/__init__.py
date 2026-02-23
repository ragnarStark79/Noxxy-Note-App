"""
Application factory module.
Creates and configures the Flask application using the app factory pattern.
"""
from flask import Flask
from flask_cors import CORS
from app.config import get_config
from app.extensions import init_db
from datetime import timedelta


def create_app():
    """
    Create and configure Flask application.

    Returns:
        Configured Flask app instance
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(get_config())
    
    # Configure session
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.secret_key = app.config.get('SECRET_KEY', 'noxxy-secret-key-change-in-production')

    # Enable CORS for all routes
    CORS(app)

    # Initialize extensions
    init_db(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Add health check endpoint
    @app.route('/health')
    def health():
        return {"status": "healthy"}

    # Add API info endpoint
    @app.route('/api')
    def api_info():
        return {
            "name": "Noxxy API",
            "version": "1.0.0",
            "description": "Note-taking application API",
            "endpoints": {
                "notes": "/notes",
                "bin": "/bin",
                "folders": "/folders"
            }
        }

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.note_routes import note_bp
    from app.routes.bin_routes import bin_bp
    from app.routes.folder_routes import folder_bp
    from app.routes.frontend_routes import frontend_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(note_bp)
    app.register_blueprint(bin_bp)
    app.register_blueprint(folder_bp)
    app.register_blueprint(frontend_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_error_handlers(app):
    """Register error handlers for common HTTP errors."""

    @app.errorhandler(404)
    def not_found(error):
        return {
            "success": False,
            "error": "Resource not found"
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {
            "success": False,
            "error": "Internal server error"
        }, 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            "success": False,
            "error": "Method not allowed"
        }, 405

