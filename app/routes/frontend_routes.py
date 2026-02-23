"""
Frontend routes - serves HTML pages for the note-taking application.
Returns rendered Jinja templates.
"""
from flask import Blueprint, render_template
from app.services.auth_service import login_required, get_current_user

# Create blueprint
frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/')
@login_required
def index():
    """
    Home page - displays notes and folders.
    """
    user = get_current_user()
    return render_template('index.html', user=user)


@frontend_bp.route('/bin')
@login_required
def bin_page():
    """
    Bin page - displays deleted notes.
    """
    user = get_current_user()
    return render_template('bin.html', user=user)

