"""
Utility helper functions.
Contains common utilities for JSON serialization and response formatting.
"""
from datetime import datetime
from typing import Any, Dict, List
from bson import ObjectId
from flask import jsonify


def serialize_doc(doc: Dict) -> Dict:
    """
    Serialize a MongoDB document to JSON-compatible format.
    Converts ObjectId to string and datetime to ISO format.

    Args:
        doc: MongoDB document

    Returns:
        JSON-compatible dictionary
    """
    if doc is None:
        return None

    serialized = {}

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value

    # Convert _id to id for cleaner API
    if '_id' in serialized:
        serialized['id'] = serialized.pop('_id')

    # Convert folder_id to string if present
    if 'folder_id' in serialized and serialized['folder_id']:
        serialized['folder_id'] = str(serialized['folder_id'])

    return serialized


def serialize_docs(docs: List[Dict]) -> List[Dict]:
    """
    Serialize a list of MongoDB documents.

    Args:
        docs: List of MongoDB documents

    Returns:
        List of JSON-compatible dictionaries
    """
    return [serialize_doc(doc) for doc in docs]


def success_response(data: Any = None, message: str = None, status_code: int = 200):
    """
    Create a successful JSON response.

    Args:
        data: Response data
        message: Success message (optional)
        status_code: HTTP status code (default: 200)

    Returns:
        Flask JSON response
    """
    response = {
        "success": True
    }

    if message:
        response["message"] = message

    if data is not None:
        response["data"] = data

    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400):
    """
    Create an error JSON response.

    Args:
        message: Error message
        status_code: HTTP status code (default: 400)

    Returns:
        Flask JSON response
    """
    response = {
        "success": False,
        "error": message
    }

    return jsonify(response), status_code

