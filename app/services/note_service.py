"""
Note service - contains business logic for note operations.
Validates input and orchestrates model layer calls.
"""
from typing import Optional, List, Dict, Tuple
from app.models import note_model, folder_model


def create_note(title: str, content: str = "", folder_id: Optional[str] = None, user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Create a new note with validation.

    Args:
        title: Note title
        content: Note content
        folder_id: Optional folder ID
        user_id: User ID (owner of the note)

    Returns:
        Tuple of (note_document, error_message)
    """
    # Validate title
    if not title or not title.strip():
        return None, "Title is required"

    title = title.strip()

    if len(title) > 200:
        return None, "Title must be 200 characters or less"

    # Validate folder if provided
    if folder_id:
        folder = folder_model.get_folder_by_id(folder_id)
        if not folder:
            return None, f"Folder not found: {folder_id}"
        # Ensure folder belongs to user
        if user_id and folder.get('user_id') != user_id:
            return None, "Folder not found"

    # Create note
    try:
        note = note_model.create_note(title, content, folder_id, user_id)
        return note, None
    except Exception as e:
        return None, f"Failed to create note: {str(e)}"


def get_note(note_id: str, user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Get a note by ID.

    Args:
        note_id: Note ID
        user_id: User ID (for access control)

    Returns:
        Tuple of (note_document, error_message)
    """
    note = note_model.get_note_by_id(note_id)

    if not note:
        return None, f"Note not found: {note_id}"
    
    # Check ownership
    if user_id and note.get('user_id') != user_id:
        return None, f"Note not found: {note_id}"

    return note, None


def update_note(note_id: str, title: Optional[str] = None,
                content: Optional[str] = None, user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Update a note with validation.

    Args:
        note_id: Note ID
        title: New title (optional)
        content: New content (optional)
        user_id: User ID (for access control)

    Returns:
        Tuple of (updated_note, error_message)
    """
    # Check if note exists and user owns it
    existing_note = note_model.get_note_by_id(note_id)
    if not existing_note:
        return None, f"Note not found: {note_id}"
    
    if user_id and existing_note.get('user_id') != user_id:
        return None, f"Note not found: {note_id}"

    # Validate title if provided
    if title is not None:
        title = title.strip()
        if not title:
            return None, "Title cannot be empty"
        if len(title) > 200:
            return None, "Title must be 200 characters or less"

    # Update note
    try:
        updated_note = note_model.update_note(note_id, title, content)
        return updated_note, None
    except Exception as e:
        return None, f"Failed to update note: {str(e)}"


def delete_note(note_id: str, user_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Soft delete a note (move to bin).

    Args:
        note_id: Note ID
        user_id: User ID (for access control)

    Returns:
        Tuple of (success, error_message)
    """
    # Check ownership
    existing_note = note_model.get_note_by_id(note_id)
    if not existing_note:
        return False, f"Note not found: {note_id}"
    
    if user_id and existing_note.get('user_id') != user_id:
        return False, f"Note not found: {note_id}"
    
    note = note_model.soft_delete_note(note_id)

    if not note:
        return False, f"Note not found: {note_id}"

    return True, None


def restore_note(note_id: str, user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Restore a note from bin.

    Args:
        note_id: Note ID
        user_id: User ID (for access control)

    Returns:
        Tuple of (restored_note, error_message)
    """
    # Check ownership
    existing_note = note_model.get_note_by_id(note_id)
    if not existing_note:
        return None, f"Note not found: {note_id}"
    
    if user_id and existing_note.get('user_id') != user_id:
        return None, f"Note not found: {note_id}"
    
    note = note_model.restore_note(note_id)

    if not note:
        return None, f"Note not found: {note_id}"

    return note, None


def delete_note_permanently(note_id: str, user_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Permanently delete a note from database.

    Args:
        note_id: Note ID
        user_id: User ID (for access control)

    Returns:
        Tuple of (success, error_message)
    """
    # Check ownership
    existing_note = note_model.get_note_by_id(note_id)
    if not existing_note:
        return False, f"Note not found: {note_id}"
    
    if user_id and existing_note.get('user_id') != user_id:
        return False, f"Note not found: {note_id}"
    
    success = note_model.delete_note_permanently(note_id)

    if not success:
        return False, f"Note not found: {note_id}"

    return True, None


def toggle_pin(note_id: str, user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Toggle pin status of a note.

    Args:
        note_id: Note ID
        user_id: User ID (for access control)

    Returns:
        Tuple of (updated_note, error_message)
    """
    # Get current note
    note = note_model.get_note_by_id(note_id)

    if not note:
        return None, f"Note not found: {note_id}"
    
    # Check ownership
    if user_id and note.get('user_id') != user_id:
        return None, f"Note not found: {note_id}"

    # Cannot pin deleted notes
    if note.get('is_deleted'):
        return None, "Cannot pin deleted notes"

    # Toggle pin status
    new_pin_status = not note.get('is_pinned', False)

    updated_note = note_model.update_note(note_id, is_pinned=new_pin_status)
    return updated_note, None


def list_notes(folder_id: Optional[str] = None, user_id: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
    """
    List all active notes (excluding deleted) for a user.

    Args:
        folder_id: Optional folder ID to filter by
        user_id: User ID (filter by owner)

    Returns:
        Tuple of (notes_list, error_message)
    """
    # Validate folder if provided
    if folder_id:
        folder = folder_model.get_folder_by_id(folder_id)
        if not folder:
            return [], f"Folder not found: {folder_id}"
        # Ensure folder belongs to user
        if user_id and folder.get('user_id') != user_id:
            return [], f"Folder not found: {folder_id}"

    try:
        notes = note_model.list_notes(folder_id=folder_id, include_deleted=False, user_id=user_id)
        return notes, None
    except Exception as e:
        return [], f"Failed to list notes: {str(e)}"


def list_deleted_notes(user_id: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
    """
    List all deleted notes (bin) for a user.

    Args:
        user_id: User ID (filter by owner)

    Returns:
        Tuple of (notes_list, error_message)
    """
    try:
        notes = note_model.list_deleted_notes(user_id=user_id)
        return notes, None
    except Exception as e:
        return [], f"Failed to list deleted notes: {str(e)}"


def assign_to_folder(note_id: str, folder_id: Optional[str], user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Assign a note to a folder or remove from folder.

    Args:
        note_id: Note ID
        folder_id: Folder ID or None to remove from folder
        user_id: User ID (for access control)

    Returns:
        Tuple of (updated_note, error_message)
    """
    # Check if note exists and user owns it
    note = note_model.get_note_by_id(note_id)
    if not note:
        return None, f"Note not found: {note_id}"
    
    if user_id and note.get('user_id') != user_id:
        return None, f"Note not found: {note_id}"

    # Validate folder if provided
    if folder_id:
        folder = folder_model.get_folder_by_id(folder_id)
        if not folder:
            return None, f"Folder not found: {folder_id}"
        # Ensure folder belongs to user
        if user_id and folder.get('user_id') != user_id:
            return None, f"Folder not found: {folder_id}"

    # Assign folder
    try:
        updated_note = note_model.assign_folder(note_id, folder_id)
        return updated_note, None
    except Exception as e:
        return None, f"Failed to assign folder: {str(e)}"

