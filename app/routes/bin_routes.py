"""
Bin routes - API endpoints for managing deleted notes (bin).
Handles restore and permanent delete operations.
"""
from flask import Blueprint
from app.services import note_service
from app.services.auth_service import login_required, get_current_user_id
from app.utils.helpers import serialize_docs, serialize_doc, success_response, error_response

# Create blueprint with /api prefix
bin_bp = Blueprint('bin', __name__, url_prefix='/api/bin')


@bin_bp.route('', methods=['GET'])
@login_required
def list_deleted_notes():
    """
    List all deleted notes (bin).

    Returns:
        200: List of deleted notes
    """
    user_id = get_current_user_id()
    notes, error = note_service.list_deleted_notes(user_id)

    if error:
        return error_response(error, 500)

    return success_response(serialize_docs(notes))


@bin_bp.route('/<note_id>/restore', methods=['PATCH'])
@login_required
def restore_note(note_id):
    """
    Restore a note from bin.

    Returns:
        200: Note restored successfully
        404: Note not found
    """
    user_id = get_current_user_id()
    note, error = note_service.restore_note(note_id, user_id)

    if error:
        return error_response(error, 404)

    return success_response(
        serialize_doc(note),
        "Note restored successfully"
    )


@bin_bp.route('/<note_id>', methods=['DELETE'])
@login_required
def delete_note_permanently(note_id):
    """
    Permanently delete a note from database.
    This action cannot be undone.

    Returns:
        200: Note deleted permanently
        404: Note not found
    """
    user_id = get_current_user_id()
    success, error = note_service.delete_note_permanently(note_id, user_id)

    if error:
        return error_response(error, 404)

    return success_response(message="Note permanently deleted")

