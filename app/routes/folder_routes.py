"""
Folder routes - API endpoints for folder management.
Handles folder CRUD and note assignment operations.
"""
from flask import Blueprint, request
from app.services import folder_service
from app.services.auth_service import login_required, get_current_user_id
from app.utils.helpers import serialize_doc, serialize_docs, success_response, error_response

# Create blueprint with /api prefix
folder_bp = Blueprint('folders', __name__, url_prefix='/api/folders')


@folder_bp.route('', methods=['POST'])
@login_required
def create_folder():
    """
    Create a new folder.

    Request Body:
        - name (required): Folder name

    Returns:
        201: Folder created successfully
        400: Validation error
    """
    data = request.get_json()

    if not data:
        return error_response("Request body is required", 400)

    name = data.get('name')
    user_id = get_current_user_id()

    folder, error = folder_service.create_folder(name, user_id)

    if error:
        return error_response(error, 400)

    return success_response(
        serialize_doc(folder),
        "Folder created successfully",
        201
    )


@folder_bp.route('', methods=['GET'])
@login_required
def list_folders():
    """
    List all folders with note counts.

    Returns:
        200: List of folders
    """
    user_id = get_current_user_id()
    folders, error = folder_service.list_folders(user_id)

    if error:
        return error_response(error, 500)

    return success_response(serialize_docs(folders))


@folder_bp.route('/<folder_id>', methods=['GET'])
@login_required
def get_folder(folder_id):
    """
    Get a folder by ID.

    Returns:
        200: Folder found
        404: Folder not found
    """
    user_id = get_current_user_id()
    folder, error = folder_service.get_folder(folder_id, user_id)

    if error:
        return error_response(error, 404)

    return success_response(serialize_doc(folder))


@folder_bp.route('/<folder_id>', methods=['DELETE'])
@login_required
def delete_folder(folder_id):
    """
    Delete a folder.

    Query Parameters:
        - remove_notes (optional): If true, remove folder from all notes

    Returns:
        200: Folder deleted successfully
        400: Folder contains notes
        404: Folder not found
    """
    remove_notes = request.args.get('remove_notes', 'false').lower() == 'true'
    user_id = get_current_user_id()

    success, error = folder_service.delete_folder(folder_id, remove_notes, user_id)

    if error:
        status_code = 404 if "not found" in error.lower() else 400
        return error_response(error, status_code)

    return success_response(message="Folder deleted successfully")


@folder_bp.route('/<folder_id>/notes/<note_id>', methods=['PATCH'])
@login_required
def add_note_to_folder(folder_id, note_id):
    """
    Add a note to a folder.

    Returns:
        200: Note added to folder
        404: Folder or note not found
    """
    note, error = folder_service.add_note_to_folder(folder_id, note_id)

    if error:
        return error_response(error, 404)

    return success_response(
        serialize_doc(note),
        "Note added to folder successfully"
    )


@folder_bp.route('/<folder_id>/notes/<note_id>', methods=['DELETE'])
@login_required
def remove_note_from_folder(folder_id, note_id):
    """
    Remove a note from a folder.

    Returns:
        200: Note removed from folder
        400: Note not in folder
        404: Note not found
    """
    note, error = folder_service.remove_note_from_folder(folder_id, note_id)

    if error:
        status_code = 404 if "not found" in error.lower() else 400
        return error_response(error, status_code)

    return success_response(
        serialize_doc(note),
        "Note removed from folder successfully"
    )

