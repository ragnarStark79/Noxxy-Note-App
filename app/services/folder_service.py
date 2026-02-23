"""
Folder service - contains business logic for folder operations.
Validates input and orchestrates model layer calls.
"""
from typing import Optional, List, Dict, Tuple
from app.models import folder_model, note_model


def create_folder(name: str, user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Create a new folder with validation.

    Args:
        name: Folder name
        user_id: User ID (owner of the folder)

    Returns:
        Tuple of (folder_document, error_message)
    """
    # Validate name
    if not name or not name.strip():
        return None, "Folder name is required"

    name = name.strip()

    if len(name) > 100:
        return None, "Folder name must be 100 characters or less"

    # Create folder
    try:
        folder = folder_model.create_folder(name, user_id)
        return folder, None
    except Exception as e:
        return None, f"Failed to create folder: {str(e)}"


def get_folder(folder_id: str, user_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Get a folder by ID.

    Args:
        folder_id: Folder ID
        user_id: User ID (for access control)

    Returns:
        Tuple of (folder_document, error_message)
    """
    folder = folder_model.get_folder_by_id(folder_id)

    if not folder:
        return None, f"Folder not found: {folder_id}"
    
    # Check ownership
    if user_id and folder.get('user_id') != user_id:
        return None, f"Folder not found: {folder_id}"

    return folder, None


def list_folders(user_id: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
    """
    List all folders with note counts for a user.

    Args:
        user_id: User ID (filter by owner)

    Returns:
        Tuple of (folders_list, error_message)
    """
    try:
        folders = folder_model.list_folders(user_id)

        # Add note count to each folder
        for folder in folders:
            folder_id = str(folder['_id'])
            folder['note_count'] = folder_model.get_folder_note_count(folder_id, user_id)

        return folders, None
    except Exception as e:
        return [], f"Failed to list folders: {str(e)}"


def delete_folder(folder_id: str, remove_notes: bool = False, user_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Delete a folder.

    Args:
        folder_id: Folder ID
        remove_notes: If True, remove folder from all notes (default: False)
        user_id: User ID (for access control)

    Returns:
        Tuple of (success, error_message)
    """
    # Check if folder exists and user owns it
    folder = folder_model.get_folder_by_id(folder_id)
    if not folder:
        return False, f"Folder not found: {folder_id}"
    
    if user_id and folder.get('user_id') != user_id:
        return False, f"Folder not found: {folder_id}"

    # Check if folder has notes
    note_count = folder_model.get_folder_note_count(folder_id, user_id)

    if note_count > 0 and not remove_notes:
        return False, f"Folder contains {note_count} note(s). Remove notes first or use remove_notes=true"

    # If remove_notes is True, unassign all notes from this folder
    if remove_notes and note_count > 0:
        from app.extensions import get_db
        from bson import ObjectId
        db = get_db()
        query = {"folder_id": ObjectId(folder_id)}
        if user_id:
            query["user_id"] = user_id
        db.notes.update_many(query, {"$set": {"folder_id": None}})

    # Delete folder
    success = folder_model.delete_folder(folder_id)

    if not success:
        return False, "Failed to delete folder"

    return True, None


def add_note_to_folder(folder_id: str, note_id: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Add a note to a folder.

    Args:
        folder_id: Folder ID
        note_id: Note ID

    Returns:
        Tuple of (updated_note, error_message)
    """
    # Validate folder
    folder = folder_model.get_folder_by_id(folder_id)
    if not folder:
        return None, f"Folder not found: {folder_id}"

    # Validate note
    note = note_model.get_note_by_id(note_id)
    if not note:
        return None, f"Note not found: {note_id}"

    # Assign note to folder
    updated_note = note_model.assign_folder(note_id, folder_id)

    if not updated_note:
        return None, "Failed to add note to folder"

    return updated_note, None


def remove_note_from_folder(folder_id: str, note_id: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Remove a note from a folder.

    Args:
        folder_id: Folder ID
        note_id: Note ID

    Returns:
        Tuple of (updated_note, error_message)
    """
    # Validate note
    note = note_model.get_note_by_id(note_id)
    if not note:
        return None, f"Note not found: {note_id}"

    # Check if note is in this folder
    if str(note.get('folder_id')) != folder_id:
        return None, "Note is not in this folder"

    # Remove folder assignment
    updated_note = note_model.assign_folder(note_id, None)

    if not updated_note:
        return None, "Failed to remove note from folder"

    return updated_note, None

