"""
Routes package initialization.
Exposes route blueprints for easy imports.
"""
from app.routes.note_routes import note_bp
from app.routes.bin_routes import bin_bp
from app.routes.folder_routes import folder_bp
from app.routes.frontend_routes import frontend_bp

__all__ = ['note_bp', 'bin_bp', 'folder_bp', 'frontend_bp']

