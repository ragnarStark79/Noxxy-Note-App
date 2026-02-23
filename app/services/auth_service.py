"""
Authentication Service
Handles user authentication, session management, and access control
"""

from flask import session, redirect, url_for, flash
from functools import wraps
from app.models.user_model import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_password
)


def register_user(name, email, profession, gender, password):
    """
    Register a new user
    
    Args:
        name (str): User's full name
        email (str): User's email
        profession (str): User's profession
        gender (str): "he" or "she"
        password (str): User's password
    
    Returns:
        tuple: (success: bool, message: str, user: dict or None)
    """
    # Validate inputs
    if not all([name, email, profession, gender, password]):
        return False, "All fields are required", None
    
    if gender not in ["he", "she"]:
        return False, "Invalid gender selection", None
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters", None
    
    # Create user
    user = create_user(name, email, profession, gender, password)
    
    if not user:
        return False, "Email already exists", None
    
    return True, "Registration successful", user


def login_user(email, password):
    """
    Authenticate user and create session
    
    Args:
        email (str): User's email
        password (str): User's password
    
    Returns:
        tuple: (success: bool, message: str, user: dict or None)
    """
    # Get user by email
    user = get_user_by_email(email)
    
    if not user:
        return False, "Invalid email or password", None
    
    # Verify password
    if not verify_password(user, password):
        return False, "Invalid email or password", None
    
    # Create session
    session['user_id'] = str(user['_id'])
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['user_uid'] = user['user_uid']
    session.permanent = True
    
    return True, "Login successful", user


def logout_user():
    """
    Clear user session and logout
    """
    session.clear()


def get_current_user():
    """
    Get currently logged in user from session
    
    Returns:
        dict: User document or None
    """
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    return get_user_by_id(user_id)


def is_authenticated():
    """
    Check if user is logged in
    
    Returns:
        bool: True if user is authenticated
    """
    return 'user_id' in session


def login_required(f):
    """
    Decorator to protect routes that require authentication
    Redirects to login page if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id():
    """
    Get current user's MongoDB ObjectId from session
    
    Returns:
        str: User ID or None
    """
    return session.get('user_id')
