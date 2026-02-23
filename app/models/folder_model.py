"""
Folder model - handles all database interactions for folders.
Uses PyMongo to interact with MongoDB folders collection.
"""
from datetime import datetime
from typing import Optional, List, Dict
from bson import ObjectId
from bson.errors import InvalidId
from app.extensions import get_db


def create_folder(name: str, user_id: Optional[str] = None) -> Dict:
    """
    Create a new folder in the database.

    Args:
        name: Folder name
        user_id: User ID (owner of the folder)

    Returns:
        Created folder document
    """
    db = get_db()

    folder_doc = {
        "name": name,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }

    result = db.folders.insert_one(folder_doc)
    folder_doc['_id'] = result.inserted_id

    return folder_doc


def get_folder_by_id(folder_id: str) -> Optional[Dict]:
    """
    Get a single folder by ID.

    Args:
        folder_id: Folder ID as string

    Returns:
        Folder document or None if not found
    """
    db = get_db()

    try:
        object_id = ObjectId(folder_id)
    except InvalidId:
        return None

    folder = db.folders.find_one({"_id": object_id})
    return folder


def list_folders(user_id: Optional[str] = None) -> List[Dict]:
    """
    List all folders, sorted by name.

    Args:
        user_id: Filter by user ID (optional)

    Returns:
        List of folder documents
    """
    db = get_db()

    query = {}
    if user_id:
        query["user_id"] = user_id

    folders = list(db.folders.find(query).sort("name", 1))
    return folders


def delete_folder(folder_id: str) -> bool:
    """
    Delete a folder from database.
    Note: This does NOT delete notes in the folder.

    Args:
        folder_id: Folder ID as string

    Returns:
        True if deleted, False otherwise
    """
    db = get_db()

    try:
        object_id = ObjectId(folder_id)
    except InvalidId:
        return False

    result = db.folders.delete_one({"_id": object_id})
    return result.deleted_count > 0


def get_folder_note_count(folder_id: str, user_id: Optional[str] = None) -> int:
    """
    Get the count of notes in a folder.

    Args:
        folder_id: Folder ID as string
        user_id: Filter by user ID (optional)

    Returns:
        Number of notes in folder
    """
    db = get_db()

    try:
        object_id = ObjectId(folder_id)
    except InvalidId:
        return 0

    query = {
        "folder_id": object_id,
        "is_deleted": False
    }
    if user_id:
        query["user_id"] = user_id

    count = db.notes.count_documents(query)

    return count

