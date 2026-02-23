"""
Services package initialization.
Exposes service modules for easy imports.
"""
from app.services import note_service, folder_service

__all__ = ['note_service', 'folder_service']

