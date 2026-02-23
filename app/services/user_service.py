"""
User Service
Handles user profile management and updates
"""

from app.models.user_model import (
    get_user_by_id,
    update_user,
    update_password
)


def get_user_profile(user_id):
    """
    Get user profile information
    
    Args:
        user_id (str): User's ID
    
    Returns:
        dict: User profile data (excluding password)
    """
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    # Remove sensitive data
    profile = {
        "_id": str(user["_id"]),
        "user_uid": user["user_uid"],
        "name": user["name"],
        "email": user["email"],
        "profession": user["profession"],
        "gender": user["gender"],
        "profile_photo_url": user["profile_photo_url"],
        "created_at": user["created_at"],
        "updated_at": user.get("updated_at", user["created_at"])
    }
    
    return profile


def update_user_profile(user_id, name=None, email=None, profession=None, profile_photo_url=None):
    """
    Update user profile information
    
    Args:
        user_id (str): User's ID
        name (str, optional): New name
        email (str, optional): New email
        profession (str, optional): New profession
        profile_photo_url (str, optional): New profile photo URL
    
    Returns:
        tuple: (success: bool, message: str, user: dict or None)
    """
    update_data = {}
    
    if name:
        update_data["name"] = name
    if email:
        update_data["email"] = email
    if profession:
        update_data["profession"] = profession
    
    # Handle profile photo URL (allow empty string to clear photo)
    if profile_photo_url is not None:
        update_data["profile_photo_url"] = profile_photo_url
    
    if not update_data:
        return False, "No fields to update", None
    
    updated_user = update_user(user_id, update_data)
    
    if not updated_user:
        return False, "Failed to update profile", None
    
    return True, "Profile updated successfully", updated_user


def change_user_password(user_id, old_password, new_password, confirm_password):
    """
    Change user's password
    
    Args:
        user_id (str): User's ID
        old_password (str): Current password
        new_password (str): New password
        confirm_password (str): Confirm new password
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate inputs
    if not all([old_password, new_password, confirm_password]):
        return False, "All password fields are required"
    
    if new_password != confirm_password:
        return False, "New passwords do not match"
    
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters"
    
    if old_password == new_password:
        return False, "New password must be different from old password"
    
    # Update password
    success = update_password(user_id, old_password, new_password)
    
    if not success:
        return False, "Current password is incorrect"
    
    return True, "Password changed successfully"
