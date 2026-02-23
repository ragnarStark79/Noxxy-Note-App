"""
Authentication Routes
Handles user registration, login, logout, and profile management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import (
    register_user,
    login_user,
    logout_user,
    login_required,
    get_current_user,
    get_current_user_id
)
from app.services.user_service import (
    get_user_profile,
    update_user_profile,
    change_user_password
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('frontend.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        profession = request.form.get('profession', '').strip()
        gender = request.form.get('gender', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Register user
        success, message, user = register_user(name, email, profession, gender, password)
        
        if success:
            flash(message, 'success')
            # Auto-login after registration
            login_user(email, password)
            return redirect(url_for('frontend.index'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('frontend.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Authenticate user
        success, message, user = login_user(email, password)
        
        if success:
            flash(message, 'success')
            # Redirect to next page or home
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('frontend.index'))
        else:
            flash(message, 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile settings page"""
    user_id = get_current_user_id()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            profession = request.form.get('profession', '').strip()
            profile_photo_url = request.form.get('profile_photo_url', '').strip()
            
            success, message, updated_user = update_user_profile(
                user_id, name, email, profession, profile_photo_url
            )
            
            if success:
                # Update session data with all updated fields
                session['user_name'] = updated_user['name']
                session['user_email'] = updated_user['email']
                session['user_profession'] = updated_user.get('profession', '')
                session['user_photo_url'] = updated_user.get('profile_photo_url', '')
                flash(message, 'success')
            else:
                flash(message, 'error')
        
        elif action == 'change_password':
            old_password = request.form.get('old_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            success, message = change_user_password(
                user_id, old_password, new_password, confirm_password
            )
            
            flash(message, 'success' if success else 'error')
        
        return redirect(url_for('auth.profile'))
    
    # Get user profile
    profile_data = get_user_profile(user_id)
    
    if not profile_data:
        flash('Profile not found', 'error')
        return redirect(url_for('frontend.index'))
    
    return render_template('profile.html', user=profile_data)
