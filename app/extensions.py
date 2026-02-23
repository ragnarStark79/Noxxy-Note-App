"""
Extensions module.
Initializes and exposes MongoDB client and database instances.
"""
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database

# Global MongoDB client and database instances
mongo_client: Optional[MongoClient] = None
db: Optional[Database] = None


def init_db(app):
    """
    Initialize MongoDB connection using Flask app configuration.

    Args:
        app: Flask application instance

    Returns:
        Database instance
    """
    global mongo_client, db

    mongo_uri = app.config['MONGO_URI']
    db_name = app.config['MONGO_DB_NAME']

    # Create MongoDB client
    mongo_client = MongoClient(mongo_uri)

    # Get database instance
    db = mongo_client[db_name]

    # Create indexes for better performance
    _create_indexes()

    app.logger.info(f"Connected to MongoDB database: {db_name}")

    return db


def _create_indexes():
    """Create indexes on collections for optimized queries."""

    # Notes collection indexes
    db.notes.create_index([("is_deleted", 1), ("is_pinned", -1), ("created_at", -1)])
    db.notes.create_index([("folder_id", 1)])

    # Folders collection indexes
    db.folders.create_index([("name", 1)])


def get_db():
    """
    Get the database instance.

    Returns:
        Database instance
    """
    return db


