"""
Note routes - API endpoints for note management.
Handles HTTP requests and returns JSON responses.
"""
from flask import Blueprint, request
from app.services import note_service
from app.services.auth_service import login_required, get_current_user_id
from app.utils.helpers import serialize_doc, serialize_docs, success_response, error_response

# Create blueprint with /api prefix
note_bp = Blueprint('notes', __name__, url_prefix='/api/notes')


@note_bp.route('', methods=['POST'])
@login_required
def create_note():
    """
    Create a new note.

    Request Body:
        - title (required): Note title
        - content (optional): Note content
        - folder_id (optional): Folder ID

    Returns:
        201: Note created successfully
        400: Validation error
    """
    data = request.get_json()

    if not data:
        return error_response("Request body is required", 400)

    title = data.get('title')
    content = data.get('content', '')
    folder_id = data.get('folder_id')
    user_id = get_current_user_id()

    note, error = note_service.create_note(title, content, folder_id, user_id)

    if error:
        return error_response(error, 400)

    return success_response(
        serialize_doc(note),
        "Note created successfully",
        201
    )


@note_bp.route('/<note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    """
    Get a note by ID.

    Returns:
        200: Note found
        404: Note not found
    """
    user_id = get_current_user_id()
    note, error = note_service.get_note(note_id, user_id)

    if error:
        return error_response(error, 404)

    return success_response(serialize_doc(note))


@note_bp.route('/<note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """
    Update a note.

    Request Body:
        - title (optional): New title
        - content (optional): New content

    Returns:
        200: Note updated successfully
        400: Validation error
        404: Note not found
    """
    data = request.get_json()

    if not data:
        return error_response("Request body is required", 400)

    title = data.get('title')
    content = data.get('content')
    user_id = get_current_user_id()

    # At least one field should be provided
    if title is None and content is None:
        return error_response("At least one field (title or content) is required", 400)

    note, error = note_service.update_note(note_id, title, content, user_id)

    if error:
        status_code = 404 if "not found" in error.lower() else 400
        return error_response(error, status_code)

    return success_response(
        serialize_doc(note),
        "Note updated successfully"
    )


@note_bp.route('/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """
    Soft delete a note (move to bin).

    Returns:
        200: Note deleted successfully
        404: Note not found
    """
    user_id = get_current_user_id()
    success, error = note_service.delete_note(note_id, user_id)

    if error:
        return error_response(error, 404)

    return success_response(message="Note moved to bin successfully")


@note_bp.route('/<note_id>/pin', methods=['PATCH'])
@login_required
def toggle_pin(note_id):
    """
    Toggle pin status of a note.

    Returns:
        200: Pin status toggled
        400: Cannot pin deleted note
        404: Note not found
    """
    user_id = get_current_user_id()
    note, error = note_service.toggle_pin(note_id, user_id)

    if error:
        status_code = 404 if "not found" in error.lower() else 400
        return error_response(error, status_code)

    pin_status = "pinned" if note.get('is_pinned') else "unpinned"

    return success_response(
        serialize_doc(note),
        f"Note {pin_status} successfully"
    )


@note_bp.route('', methods=['GET'])
@login_required
def list_notes():
    """
    List all active notes (excluding deleted).
    Pinned notes appear first.

    Query Parameters:
        - folder_id (optional): Filter by folder

    Returns:
        200: List of notes
    """
    folder_id = request.args.get('folder_id')
    user_id = get_current_user_id()

    notes, error = note_service.list_notes(folder_id, user_id)

    if error:
        return error_response(error, 400)

    return success_response(serialize_docs(notes))

