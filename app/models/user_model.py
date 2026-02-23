"""
User Model - MongoDB Schema and Operations
Handles user data, authentication, and profile management
"""

from app.extensions import get_db
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random


def generate_unique_user_uid():
    """
    Generate a unique 6-digit user ID
    Ensures no collision with existing users
    """
    db = get_db()
    while True:
        # Generate random 6-digit number
        user_uid = random.randint(100000, 999999)
        
        # Check if it already exists
        existing = db.users.find_one({"user_uid": user_uid})
        if not existing:
            return user_uid


def create_user(name, email, profession, gender, password, profile_photo_url=None):
    """
    Create a new user with hashed password and unique ID
    
    Args:
        name (str): User's full name
        email (str): User's email (must be unique)
        profession (str): User's profession
        gender (str): "he" or "she"
        password (str): Plain text password (will be hashed)
        profile_photo_url (str, optional): URL to profile photo
    
    Returns:
        dict: Created user document or None if email exists
    """
    db = get_db()
    
    # Check if email already exists
    existing_user = db.users.find_one({"email": email.lower()})
    if existing_user:
        return None
    
    # Set default profile photo based on gender
    if not profile_photo_url:
        if gender == "he":
            profile_photo_url = "/static/images/default-male-avatar.png"
        elif gender == "she":
            profile_photo_url = "/static/images/default-female-avatar.png"
        else:
            profile_photo_url = "/static/images/default-avatar.png"
    
    # Generate unique user ID
    user_uid = generate_unique_user_uid()
    
    # Create user document
    user_doc = {
        "user_uid": user_uid,
        "name": name,
        "email": email.lower(),
        "profession": profession,
        "gender": gender,
        "password": generate_password_hash(password),
        "profile_photo_url": profile_photo_url,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert into database
    result = db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    return user_doc


def get_user_by_email(email):
    """
    Get user by email address
    
    Args:
        email (str): User's email
    
    Returns:
        dict: User document or None
    """
    db = get_db()
    return db.users.find_one({"email": email.lower()})


def get_user_by_id(user_id):
    """
    Get user by MongoDB ObjectId
    
    Args:
        user_id (str or ObjectId): User's ID
    
    Returns:
        dict: User document or None
    """
    db = get_db()
    
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return None
    
    return db.users.find_one({"_id": user_id})


def get_user_by_uid(user_uid):
    """
    Get user by unique 6-digit user ID
    
    Args:
        user_uid (int): 6-digit user ID
    
    Returns:
        dict: User document or None
    """
    db = get_db()
    return db.users.find_one({"user_uid": user_uid})


def verify_password(user, password):
    """
    Verify user's password
    
    Args:
        user (dict): User document
        password (str): Plain text password to verify
    
    Returns:
        bool: True if password matches
    """
    if not user or "password" not in user:
        return False
    
    return check_password_hash(user["password"], password)


def update_user(user_id, update_data):
    """
    Update user profile information
    
    Args:
        user_id (str or ObjectId): User's ID
        update_data (dict): Fields to update
    
    Returns:
        dict: Updated user document or None
    """
    db = get_db()
    
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return None
    
    # Fields that can be updated
    allowed_fields = ["name", "email", "profession", "profile_photo_url"]
    
    # Build update document
    update_doc = {}
    for field in allowed_fields:
        if field in update_data:
            if field == "email":
                update_doc[field] = update_data[field].lower()
            else:
                update_doc[field] = update_data[field]
    
    # Add updated timestamp
    update_doc["updated_at"] = datetime.utcnow()
    
    # Update database
    result = db.users.update_one(
        {"_id": user_id},
        {"$set": update_doc}
    )
    
    if result.modified_count > 0:
        return get_user_by_id(user_id)
    
    return None


def update_password(user_id, old_password, new_password):
    """
    Update user's password (requires old password verification)
    
    Args:
        user_id (str or ObjectId): User's ID
        old_password (str): Current password
        new_password (str): New password
    
    Returns:
        bool: True if password updated successfully
    """
    db = get_db()
    
    user = get_user_by_id(user_id)
    if not user:
        return False
    
    # Verify old password
    if not verify_password(user, old_password):
        return False
    
    # Update password
    new_password_hash = generate_password_hash(new_password)
    result = db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password": new_password_hash,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return result.modified_count > 0


def delete_user(user_id):
    """
    Delete a user (soft delete by marking as inactive)
    
    Args:
        user_id (str or ObjectId): User's ID
    
    Returns:
        bool: True if deleted successfully
    """
    db = get_db()
    
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return False
    
    result = db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "is_active": False,
                "deleted_at": datetime.utcnow()
            }
        }
    )
    
    return result.modified_count > 0
