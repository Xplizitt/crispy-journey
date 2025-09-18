import pytest
from part_lister.app import app as flask_app
from part_lister.database import init_db
import os

@pytest.fixture
def app():
    # Create a temporary database for testing
    db_path = 'test_app_parts.db' # Use a different name to avoid conflicts
    flask_app.config.update({
        "TESTING": True,
        "DATABASE": db_path,
    })

    # Initialize the database within the application context
    with flask_app.app_context():
        # This is a workaround because database.py has a hardcoded path.
        # A more robust solution would involve making the database path in database.py configurable.
        original_db_module_path = 'part_lister.database.DATABASE_PATH'

        # Store original path from the module if it exists
        import part_lister.database
        original_path_val = getattr(part_lister.database, 'DATABASE_PATH', None)

        # Set the path for initialization
        part_lister.database.DATABASE_PATH = db_path

        if os.path.exists(db_path):
            os.remove(db_path)

        init_db()

    yield flask_app

    # Clean up the database
    if os.path.exists(db_path):
        os.remove(db_path)

    # Restore the original path in the module
    if original_path_val:
        part_lister.database.DATABASE_PATH = original_path_val

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_index_loads(client):
    """
    Tests that the index page loads with a 200 OK status code.
    """
    response = client.get('/')
    assert response.status_code == 200
