"""
Note model - handles all database interactions for notes.
Uses PyMongo to interact with MongoDB notes collection.
"""
from datetime import datetime
from typing import Optional, List, Dict
from bson import ObjectId
from bson.errors import InvalidId
from app.extensions import get_db


def create_note(title: str, content: str = "", folder_id: Optional[str] = None, user_id: Optional[str] = None) -> Dict:
    """
    Create a new note in the database.

    Args:
        title: Note title
        content: Note content (optional)
        folder_id: Folder ID to assign note to (optional)
        user_id: User ID (owner of the note)

    Returns:
        Created note document
    """
    db = get_db()

    note_doc = {
        "title": title,
        "content": content,
        "is_pinned": False,
        "is_deleted": False,
        "folder_id": ObjectId(folder_id) if folder_id else None,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = db.notes.insert_one(note_doc)
    note_doc['_id'] = result.inserted_id

    return note_doc


def get_note_by_id(note_id: str) -> Optional[Dict]:
    """
    Get a single note by ID.

    Args:
        note_id: Note ID as string

    Returns:
        Note document or None if not found
    """
    db = get_db()

    try:
        object_id = ObjectId(note_id)
    except InvalidId:
        return None

    note = db.notes.find_one({"_id": object_id})
    return note


def update_note(note_id: str, title: Optional[str] = None,
                content: Optional[str] = None,
                is_pinned: Optional[bool] = None) -> Optional[Dict]:
    """
    Update a note's fields.

    Args:
        note_id: Note ID as string
        title: New title (optional)
        content: New content (optional)
        is_pinned: Pin status (optional)

    Returns:
        Updated note document or None if not found
    """
    db = get_db()

    try:
        object_id = ObjectId(note_id)
    except InvalidId:
        return None

    # Build update document with only provided fields
    update_doc = {"updated_at": datetime.utcnow()}

    if title is not None:
        update_doc["title"] = title
    if content is not None:
        update_doc["content"] = content
    if is_pinned is not None:
        update_doc["is_pinned"] = is_pinned

    result = db.notes.find_one_and_update(
        {"_id": object_id},
        {"$set": update_doc},
        return_document=True
    )

    return result


def soft_delete_note(note_id: str) -> Optional[Dict]:
    """
    Soft delete a note (move to bin).

    Args:
        note_id: Note ID as string

    Returns:
        Updated note document or None if not found
    """
    db = get_db()

    try:
        object_id = ObjectId(note_id)
    except InvalidId:
        return None

    result = db.notes.find_one_and_update(
        {"_id": object_id},
        {"$set": {
            "is_deleted": True,
            "is_pinned": False,  # Unpin when deleting
            "updated_at": datetime.utcnow()
        }},
        return_document=True
    )

    return result


def restore_note(note_id: str) -> Optional[Dict]:
    """
    Restore a note from bin.

    Args:
        note_id: Note ID as string

    Returns:
        Restored note document or None if not found
    """
    db = get_db()

    try:
        object_id = ObjectId(note_id)
    except InvalidId:
        return None

    result = db.notes.find_one_and_update(
        {"_id": object_id},
        {"$set": {
            "is_deleted": False,
            "updated_at": datetime.utcnow()
        }},
        return_document=True
    )

    return result


def delete_note_permanently(note_id: str) -> bool:
    """
    Permanently delete a note from database.

    Args:
        note_id: Note ID as string

    Returns:
        True if deleted, False otherwise
    """
    db = get_db()

    try:
        object_id = ObjectId(note_id)
    except InvalidId:
        return False

    result = db.notes.delete_one({"_id": object_id})
    return result.deleted_count > 0


def list_notes(folder_id: Optional[str] = None, include_deleted: bool = False, user_id: Optional[str] = None) -> List[Dict]:
    """
    List all notes, sorted by pinned status and creation date.
    Pinned notes appear first.

    Args:
        folder_id: Filter by folder ID (optional)
        include_deleted: Include deleted notes (default: False)
        user_id: Filter by user ID (optional)

    Returns:
        List of note documents
    """
    db = get_db()

    # Build query filter
    query = {}

    if not include_deleted:
        query["is_deleted"] = False
    
    if user_id:
        query["user_id"] = user_id

    if folder_id:
        try:
            query["folder_id"] = ObjectId(folder_id)
        except InvalidId:
            return []

    # Sort: pinned first (descending), then by created_at (newest first)
    notes = list(db.notes.find(query).sort([
        ("is_pinned", -1),
        ("created_at", -1)
    ]))

    return notes


def list_deleted_notes(user_id: Optional[str] = None) -> List[Dict]:
    """
    List all deleted notes (bin).

    Args:
        user_id: Filter by user ID (optional)

    Returns:
        List of deleted note documents
    """
    db = get_db()

    query = {"is_deleted": True}
    if user_id:
        query["user_id"] = user_id

    notes = list(db.notes.find(query).sort("updated_at", -1))
    return notes


def assign_folder(note_id: str, folder_id: Optional[str]) -> Optional[Dict]:
    """
    Assign a note to a folder or remove from folder.

    Args:
        note_id: Note ID as string
        folder_id: Folder ID as string or None to remove from folder

    Returns:
        Updated note document or None if not found
    """
    db = get_db()

    try:
        object_id = ObjectId(note_id)
        folder_object_id = ObjectId(folder_id) if folder_id else None
    except InvalidId:
        return None

    result = db.notes.find_one_and_update(
        {"_id": object_id},
        {"$set": {
            "folder_id": folder_object_id,
            "updated_at": datetime.utcnow()
        }},
        return_document=True
    )

    return result

